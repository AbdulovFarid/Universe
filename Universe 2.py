import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import matplotlib

# Используем TkAgg для стабильного рендеринга окна
matplotlib.use('TkAgg')


class EternalMemory:
    """Память Вселенной: хранит следы тех, кто ушел."""

    def __init__(self):
        self.records = deque(maxlen=8)  # Храним последние 8 "смертей"
        self.canvas = []

    def save(self, path, color, role):
        if len(path) > 10:
            # След зависит от роли:
            # Души оставляют яркий, но прозрачный след
            # Паразиты - темный и рваный
            # Судьи - ослепительно белый, но тонкий
            alpha = 0.3 if role == 'soul' else (0.5 if role == 'judge' else 0.1)
            lw = 1.2 if role == 'soul' else (2.0 if role == 'judge' else 0.8)

            self.canvas.append({'d': np.array(path), 'c': color, 'a': alpha, 'lw': lw})
            if len(self.canvas) > 300: self.canvas.pop(0)


class Agent:
    def __init__(self, mem, id, role_distribution):
        self.mem = mem
        self.id = id
        self.role_dist = role_distribution
        self.path = deque(maxlen=50)  # Длина хвоста
        self.reset()

    def reset(self):
        # Определение роли при рождении
        rand = np.random.random()
        if rand < self.role_dist['judge']:
            self.role = 'judge'
            self.color = np.array([1.0, 1.0, 1.0])  # Белый свет
            self.energy = 5.0  # Судьи живут долго
        elif rand < self.role_dist['judge'] + self.role_dist['parasite']:
            self.role = 'parasite'
            self.color = np.array([0.1, 0.0, 0.0])  # Почти черный с красным отливом
            self.energy = 2.0
        else:
            self.role = 'soul'
            self.color = np.random.uniform(0.3, 1.0, 3)  # Яркие цвета
            self.energy = np.random.uniform(2.0, 3.5)

        # Параметры хаоса (Лоренц)
        self.s, self.r, self.b = 10.0, 28.0, 2.666
        # Случайная стартовая позиция
        self.state = np.random.uniform(-10, 10, 3)
        self.coupled_with = None

    def step(self, others):
        x, y, z = self.state
        dt = 0.006

        # 1. Базовая физика (Аттрактор Лоренца)
        dx = self.s * (y - x)
        dy = x * (self.r - z) - y
        dz = x * y - self.b * z
        velocity = np.array([dx, dy, dz])

        # 2. Воля (Взаимодействие)
        force = np.zeros(3)
        self.coupled_with = None

        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            vec = other.state - self.state  # Вектор к другому

            # --- ЛОГИКА ДУШИ ---
            if self.role == 'soul':
                if other.role == 'soul' and dist < 6.0:
                    # Любовь: притяжение и синхронизация
                    force += vec * 0.8
                    self.color = self.color * 0.98 + other.color * 0.02  # Смешивание душ
                    self.coupled_with = other
                elif other.role == 'parasite' and dist < 8.0:
                    # Страх: попытка убежать
                    force -= vec * 1.5
                elif other.role == 'judge' and dist < 5.0:
                    # Трепет: подчинение силе
                    force += np.cross(vec, np.array([0, 0, 1])) * 2.0  # Движение по орбите вокруг Судьи

            # --- ЛОГИКА ПАРАЗИТА ---
            elif self.role == 'parasite':
                if other.role == 'soul' and dist < 15.0:
                    # Охота: преследование жертвы
                    force += vec * 1.2
                    if dist < 2.0:
                        # Вампиризм
                        self.energy += 0.05
                        other.energy -= 0.08
                        self.color = np.clip(self.color + [0.05, 0, 0], 0, 1)  # Краснеет от крови
                elif other.role == 'judge' and dist < 10.0:
                    # Ужас: паразиты боятся Судей
                    force -= vec * 3.0

            # --- ЛОГИКА СУДЬИ ---
            elif self.role == 'judge':
                # Судья патрулирует хаос. Ему никто не нужен.
                # Он разгоняет толпу, чтобы не было стагнации.
                if dist < 6.0:
                    force -= vec * 5.0  # Мощное отталкивание (Гравитационный удар)
                    other.energy -= 0.01  # Наказание за приближение

        # Применение сил
        self.state += (velocity + force) * dt
        self.path.append(self.state.copy())

        # Энтропия жизни
        loss_rate = 0.005 if self.role == 'soul' else (0.008 if self.role == 'parasite' else 0.002)
        self.energy -= loss_rate

        # Смерть и перерождение
        if self.energy <= 0 or np.linalg.norm(self.state) > 60:  # Или если улетел в бездну
            self.mem.save(list(self.path), self.color, self.role)
            self.reset()


def run_universe():
    mem = EternalMemory()
    # Баланс сил: 1 Судья, 2 Паразита, 7 Душ
    role_dist = {'judge': 0.1, 'parasite': 0.2}
    agents = [Agent(mem, i, role_dist) for i in range(10)]

    plt.ion()
    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111, projection='3d')

    steps = 0
    try:
        while True:
            steps += 1
            for a in agents: a.step(agents)

            if steps % 5 == 0:  # Рендер каждые 5 шагов для скорости
                ax.clear()
                ax.set_facecolor('black')
                ax.set_axis_off()

                # Рисуем память (мертвые линии)
                for t in mem.canvas:
                    ax.plot(t['d'][:, 0], t['d'][:, 1], t['d'][:, 2],
                            color=t['c'], alpha=t['a'], lw=t['lw'])

                # Рисуем живых
                for a in agents:
                    if len(a.path) > 1:
                        d = np.array(a.path)
                        # Особый стиль для каждой роли
                        if a.role == 'judge':
                            # Судья сияет
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color='white', lw=3, alpha=0.9)
                            ax.scatter(d[-1, 0], d[-1, 1], d[-1, 2], color='white', s=100, marker='*')
                        elif a.role == 'parasite':
                            # Паразит темный и острый
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=a.color, lw=1.5, alpha=0.8, linestyle='--')
                        else:
                            # Души плавные
                            glow = 2.5 if a.coupled_with else 1.5
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=a.color, lw=glow, alpha=0.8)

                ax.set_xlim(-40, 40);
                ax.set_ylim(-40, 40);
                ax.set_zlim(0, 60)

                # Медленное вращение камеры
                ax.view_init(elev=20, azim=steps * 0.2)

                title = f"VANGUARD SIMULATION | Steps: {steps} | Souls: {len([a for a in agents if a.role == 'soul'])}"
                ax.text2D(0.05, 0.95, title, transform=ax.transAxes, color='white', fontsize=10)

                plt.draw()
                plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nSimulation Halted by Architect.")
    finally:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    run_universe()