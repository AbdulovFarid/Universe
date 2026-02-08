import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import matplotlib
import time

matplotlib.use('TkAgg')


class EternalMemory:
    def __init__(self):
        self.records = deque(maxlen=5)
        self.canvas = []

    def save(self, path, color, was_coupled):
        if len(path) > 10:
            # Если агент любил, его след в истории ярче и толще
            alpha = 0.4 if was_coupled else 0.1
            lw = 1.0 if was_coupled else 0.4
            self.canvas.append({'d': np.array(path), 'c': color, 'a': alpha, 'lw': lw})
            if len(self.canvas) > 250: self.canvas.pop(0)


class Agent:
    def __init__(self, mem, id):
        self.mem = mem
        self.id = id
        self.path = deque(maxlen=40)
        self.coupled_with = None  # Текущая "родственная душа"
        self.reset()

    def reset(self):
        best = self.mem.records[0] if self.mem.records else None
        if best and np.random.random() < 0.7:
            self.s, self.r, self.b = best['g'] + np.random.normal(0, 0.05, 3)
            self.color = np.array(best['c'])
        else:
            self.s, self.r, self.b = np.random.uniform(10, 15), np.random.uniform(20, 35), 2.666
            self.color = np.random.random(3)

        self.state = np.random.uniform(-5, 5, 3)
        self.energy = np.random.uniform(1.5, 3.0)
        self.coupled_with = None

    def step(self, others):
        x, y, z = self.state
        # Базовая физика
        force = np.array([self.s * (y - x), x * (self.r - z) - y, x * y - self.b * z])

        # Поиск близости
        self.coupled_with = None
        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            if dist < 5.0:  # Порог узнавания "своего"
                self.coupled_with = other
                # Притяжение к душе: 10% влияния на траекторию
                force += (other.state - self.state) * 0.5
                # Слияние цветов (взаимное влияние)
                self.color = self.color * 0.99 + other.color * 0.01
                break

        self.state += force * 0.005
        self.path.append(self.state.copy())
        self.energy -= 0.004

        if self.energy <= 0:
            self.mem.save(list(self.path), self.color, self.coupled_with is not None)
            self.mem.records.append({'g': [self.s, self.r, self.b], 'c': self.color})
            self.path.clear()
            self.reset()


def run_universe():
    mem = EternalMemory()
    agents = [Agent(mem, i) for i in range(6)]
    plt.ion()
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111, projection='3d')

    steps = 0
    try:
        while True:
            steps += 1
            for a in agents: a.step(agents)

            if steps % 20 == 0:
                ax.clear()
                ax.set_facecolor('black')
                ax.set_axis_off()

                # Прошлое: Послания любви и одиночества
                for t in mem.canvas:
                    ax.plot(t['d'][:, 0], t['d'][:, 1], t['d'][:, 2], color=t['c'], alpha=t['a'], lw=t['lw'])

                # Настоящее
                for a in agents:
                    if len(a.path) > 1:
                        d = np.array(a.path)
                        # Если агент в паре, его нить светится белым по краям
                        color = a.color if not a.coupled_with else (a.color + [1, 1, 1]) / 2
                        ax.plot(d[:, 0], d[:, 1], d[:, 2], color=color, lw=2.5 if a.coupled_with else 1.5)

                ax.set_xlim(-30, 30);
                ax.set_ylim(-30, 30);
                ax.set_zlim(0, 50)
                ax.view_init(25, steps * 0.15)
                plt.draw()
                plt.pause(0.001)
    except KeyboardInterrupt:
        pass
    finally:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    run_universe()