import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import matplotlib
import random

# Используем TkAgg для стабильной работы окна на Linux/Windows
matplotlib.use('TkAgg')


class EternalMemory:
    """Память Вселенной: хранит отпечатки чувств и путей."""

    def __init__(self):
        self.records = deque(maxlen=10)
        self.canvas = []

    def save(self, path, color, role, mood_at_death):
        if len(path) > 10:
            # Визуализация наследия: чем выше было настроение, тем ярче след
            brightness = np.clip(0.5 + mood_at_death * 0.5, 0.1, 1.0)
            alpha = (0.3 if role == 'soul' else 0.1) * brightness
            lw = 1.2 if role == 'soul' else 0.6

            if role == 'judge':  # Судьи оставляют ледяной след
                alpha, lw, color = 0.4, 1.5, np.array([1, 1, 1])

            self.canvas.append({'d': np.array(path), 'c': color, 'a': alpha, 'lw': lw})
            if len(self.canvas) > 250: self.canvas.pop(0)


class Agent:
    def __init__(self, mem, id, role_dist):
        self.mem = mem
        self.id = id
        self.role_dist = role_dist
        self.path = deque(maxlen=50)
        self.reset()

    def reset(self):
        """Рождение: инициализация плоти и духа."""
        # 1. Физическая оболочка (Аттрактор Лоренца)
        self.s, self.r, self.b = 10.0, 28.0, 2.666
        self.state = np.random.uniform(-15, 15, 3)
        self.coupled_with = None

        # 2. Роль и Социальный статус
        rand = np.random.random()
        if rand < self.role_dist['judge']:
            self.role = 'judge'
            self.color = np.array([1.0, 1.0, 1.0])
            self.energy = 10.0
        elif rand < self.role_dist['judge'] + self.role_dist['parasite']:
            self.role = 'parasite'
            self.color = np.array([0.2, 0.0, 0.0])
            self.energy = 4.0
        else:
            self.role = 'soul'
            self.color = np.random.uniform(0.4, 0.9, 3)
            self.energy = np.random.uniform(3.0, 6.0)

        # 3. Внутреннее "Я" (Эмоции и Цели)
        self.mood = np.random.uniform(-0.2, 0.2)
        self.fear = 0.0
        self.current_goal = 'explore'

    def perceive_and_decide(self, others):
        """Анализ окружения и выбор стратегии поведения."""
        nearby_souls = 0
        nearby_threats = 0

        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            if dist < 12.0:
                if other.role == 'soul': nearby_souls += 1
                if other.role in ['parasite', 'judge']: nearby_threats += 1

        # Динамика настроения
        self.mood = np.clip(self.mood + (nearby_souls * 0.01 - nearby_threats * 0.02), -1.0, 1.0)
        self.fear = np.clip(self.fear + (nearby_threats * 0.05 - nearby_souls * 0.01), 0.0, 1.0)
        self.fear *= 0.98  # Страх затихает со временем

        # Выбор цели
        if self.fear > 0.5:
            self.current_goal = 'avoid_danger'
        elif self.role == 'parasite':
            self.current_goal = 'hunt'
        elif self.role == 'soul' and self.mood > 0:
            self.current_goal = 'seek_love'
        else:
            self.current_goal = 'explore'

    def step(self, others):
        """Один миг жизни: движение, взаимодействие, метаморфоза."""
        x, y, z = self.state
        dt = 0.006

        # Физика Хаоса
        dx = self.s * (y - x)
        dy = x * (self.r - z) - y
        dz = x * y - self.b * z
        velocity = np.array([dx, dy, dz])

        # Интеллектуальные силы
        self.perceive_and_decide(others)
        force = np.zeros(3)
        self.coupled_with = None

        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            vec = other.state - self.state

            if self.role == 'soul':
                if self.current_goal == 'seek_love' and other.role == 'soul' and dist < 7.0:
                    force += vec * 1.5
                    self.color = self.color * 0.99 + other.color * 0.01
                    self.coupled_with = other
                elif dist < 10.0 and (other.role == 'parasite' or other.role == 'judge'):
                    force -= vec * 2.5  # Бегство

            elif self.role == 'parasite':
                if other.role == 'soul' and dist < 15.0:
                    force += vec * 1.2  # Преследование
                    if dist < 2.0:  # Контакт
                        self.energy += 0.1
                        other.energy -= 0.2
                        self.color = np.clip(self.color + [0.05, 0, 0], 0, 1)
                        other.mood -= 0.2

            elif self.role == 'judge':
                if dist < 6.0:
                    force -= vec * 10.0  # Очищение пространства
                    other.energy -= 0.05

        # Применение воли и физики
        self.state += (velocity + force) * dt
        self.path.append(self.state.copy())

        # Расход жизни (счастливые тратят меньше)
        self.energy -= 0.006 * (1.2 - self.mood * 0.3)

        # МЕТАМОРФОЗА (Пропасть исчезает здесь)
        if self.role == 'soul' and self.mood < -0.8 and self.energy < 1.0:
            self.role = 'parasite'
            self.color = np.array([0.3, 0.0, 0.0])
            print(f"[{self.id}] Душа сломлена. Перерождение в Паразита.")

        if self.energy <= 0 or np.linalg.norm(self.state) > 100:
            self.mem.save(list(self.path), self.color, self.role, self.mood)
            self.reset()


def run_universe():
    mem = EternalMemory()
    # Конфигурация мира: Судьи (5%), Паразиты (20%), Души (75%)
    role_dist = {'judge': 0.05, 'parasite': 0.20}
    agents = [Agent(mem, i, role_dist) for i in range(12)]

    plt.ion()
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111, projection='3d')

    steps = 0
    try:
        while True:
            steps += 1
            for a in agents: a.step(agents)

            if steps % 6 == 0:
                ax.clear()
                ax.set_facecolor('black')
                ax.set_axis_off()

                # Прошлое
                for t in mem.canvas:
                    ax.plot(t['d'][:, 0], t['d'][:, 1], t['d'][:, 2], color=t['c'], alpha=t['a'], lw=t['lw'])

                # Настоящее
                for a in agents:
                    if len(a.path) > 1:
                        d = np.array(a.path)
                        color = a.color
                        if a.role == 'judge':
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color='white', lw=2, alpha=0.9)
                            ax.scatter(d[-1, 0], d[-1, 1], d[-1, 2], color='white', s=80, marker='*')
                        elif a.role == 'parasite':
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=color, lw=1, alpha=0.7, ls=':')
                        else:
                            lw = 3.0 if a.coupled_with else 1.2
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=color, lw=lw, alpha=0.9)
                            # Индикатор настроения (размер точки)
                            size = np.clip(20 + a.mood * 40, 5, 80)
                            ax.scatter(d[-1, 0], d[-1, 1], d[-1, 2], color=color, s=size, edgecolors='white',
                                       linewidth=0.5)

                ax.set_xlim(-50, 50);
                ax.set_ylim(-50, 50);
                ax.set_zlim(0, 70)
                ax.view_init(20, steps * 0.1)
                plt.draw()
                plt.pause(0.001)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_universe()