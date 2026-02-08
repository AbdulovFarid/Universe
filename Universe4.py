import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import matplotlib
import random

# Пытаемся автоматически выбрать бэкенд для Linux
try:
    matplotlib.use('TkAgg')
except:
    pass


class EternalMemory:
    def __init__(self):
        self.canvas = []

    def save(self, path, color, role, mood_at_death):
        if len(path) > 10:
            brightness = np.clip(0.5 + mood_at_death * 0.5, 0.1, 1.0)
            alpha = (0.3 if role == 'soul' else 0.1) * brightness
            lw = 1.2 if role == 'soul' else 0.6
            if role == 'judge':
                alpha, lw, color = 0.4, 1.8, np.array([1, 1, 1])
            self.canvas.append({'d': np.array(path), 'c': color, 'a': alpha, 'lw': lw})
            if len(self.canvas) > 200: self.canvas.pop(0)


class Agent:
    def __init__(self, mem, id, role_dist):
        self.mem = mem
        self.id = id
        self.role_dist = role_dist
        self.path = deque(maxlen=40)
        self.reset()

    def reset(self):
        self.s, self.r, self.b = 10.0, 28.0, 2.666
        self.state = np.random.uniform(-15, 15, 3)
        self.coupled_with = None
        rand = np.random.random()
        if rand < self.role_dist['judge']:
            self.role, self.color, self.energy = 'judge', np.array([1.0, 1.0, 1.0]), 10.0
        elif rand < self.role_dist['judge'] + self.role_dist['parasite']:
            self.role, self.color, self.energy = 'parasite', np.array([0.2, 0.0, 0.0]), 4.0
        else:
            self.role, self.color, self.energy = 'soul', np.random.uniform(0.4, 0.9, 3), np.random.uniform(4.0, 7.0)
        self.mood, self.fear = np.random.uniform(-0.1, 0.1), 0.0
        self.vision_range = 35.0

    def step(self, others, global_mood, global_fear):
        x, y, z = self.state
        dt = 0.006
        dx = self.s * (y - x)
        dy = x * (self.r - z) - y
        dz = x * y - self.b * z
        velocity = np.array([dx, dy, dz])

        # Слух и Шум
        self.mood = np.clip(self.mood + (global_mood * 0.05) + np.random.normal(0, 0.02), -1.0, 1.0)
        self.fear = np.clip(self.fear + (global_fear * 0.05), 0.0, 1.0)
        self.fear *= 0.95

        force = np.random.normal(0, 0.03, 3)
        self.coupled_with = None
        target = None

        # Зрение и поиск цели
        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            if dist < self.vision_range and other.role == 'soul':
                target = other
                break

        # Взаимодействие
        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            vec = other.state - self.state
            if self.role == 'soul':
                if target == other: force += vec * 1.2
                if dist < 5.0 and other.role == 'soul': self.coupled_with = other
                if dist < 10.0 and other.role != 'soul': force -= vec * 3.0
            elif self.role == 'parasite':
                if target == other: force += vec * 1.5
                if dist < 2.5 and other.role == 'soul':
                    self.energy += 0.15
                    other.energy -= 0.2
                    other.mood -= 0.3
            elif self.role == 'judge' and dist < 8.0:
                force -= vec * 15.0
                other.energy -= 0.1

        self.state += (velocity + force) * dt
        self.path.append(self.state.copy())
        self.energy -= 0.007 * (1.1 - self.mood * 0.2)

        if self.role == 'soul' and self.mood < -0.8 and self.energy < 1.0:
            self.role, self.color = 'parasite', np.array([0.4, 0.0, 0.0])

        if self.energy <= 0 or np.linalg.norm(self.state) > 120:
            self.mem.save(list(self.path), self.color, self.role, self.mood)
            self.reset()


def run_universe():
    mem = EternalMemory()
    agents = [Agent(mem, i, {'judge': 0.05, 'parasite': 0.20}) for i in range(15)]
    plt.ion()
    fig = plt.figure(figsize=(10, 7))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111, projection='3d')
    steps = 0
    try:
        while True:
            steps += 1
            g_m = np.mean([a.mood for a in agents])
            g_f = np.mean([a.fear for a in agents])
            for a in agents: a.step(agents, g_m, g_f)
            if steps % 6 == 0:
                ax.clear()
                ax.set_facecolor('black')
                ax.set_axis_off()
                for t in mem.canvas:
                    ax.plot(t['d'][:, 0], t['d'][:, 1], t['d'][:, 2], color=t['c'], alpha=t['a'], lw=t['lw'])
                for a in agents:
                    if len(a.path) > 1:
                        d = np.array(a.path)
                        if a.role == 'judge':
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color='white', lw=2)
                        elif a.role == 'parasite':
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=a.color, lw=1, ls=':')
                        else:
                            ax.plot(d[:, 0], d[:, 1], d[:, 2], color=a.color, lw=(2.5 if a.coupled_with else 1.0))
                            ax.scatter(d[-1, 0], d[-1, 1], d[-1, 2], color=a.color,
                                       s=np.clip(25 + a.mood * 50, 10, 100))
                ax.set_xlim(-60, 60);
                ax.set_ylim(-60, 60);
                ax.set_zlim(0, 80)
                ax.view_init(25, steps * 0.1)
                plt.pause(0.001)
    except KeyboardInterrupt:
        pass
    finally:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    run_universe()