import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import matplotlib
import random

# Backend setup
try:
    matplotlib.use('TkAgg')
except:
    pass


class NeuralMind:
    """The brain: A simple MLP with backpropagation."""

    def __init__(self, input_size, output_size, hidden_size=8):
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        self.b2 = np.zeros((1, output_size))
        self.lr = 0.01

    def forward(self, inputs):
        self.h = np.dot(inputs, self.W1) + self.b1
        self.h_act = np.maximum(0, self.h)
        self.out = np.dot(self.h_act, self.W2) + self.b2
        return self.out

    def train(self, inputs, target):
        inputs = inputs.reshape(1, -1)
        target = target.reshape(1, -1)
        out = self.forward(inputs)
        error = out - target
        dW2 = np.dot(self.h_act.T, error)
        db2 = error
        dh = np.dot(error, self.W2.T)
        dh[self.h <= 0] = 0
        dW1 = np.dot(inputs.T, dh)
        db1 = dh
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2

    def get_weights(self):
        return {'W1': self.W1.copy(), 'b1': self.b1.copy(), 'W2': self.W2.copy(), 'b2': self.b2.copy()}

    def set_weights(self, weights):
        self.W1, self.b1, self.W2, self.b2 = weights['W1'], weights['b1'], weights['W2'], weights['b2']


class EternalMemory:
    def __init__(self):
        self.canvas = []
        self.best_weights = None
        self.top_score = -np.inf
        self.total_deaths = 0
        self.legendary_lives = 0

    def save(self, path, color, role, mood, weights=None):
        self.total_deaths += 1
        if len(path) > 10:
            brightness = np.clip(0.5 + mood * 0.5, 0.1, 1.0)
            self.canvas.append({'d': np.array(path), 'c': color, 'a': 0.2 * brightness})
            if len(self.canvas) > 150: self.canvas.pop(0)

            if role == 'soul' and weights:
                score = len(path) * (1 + mood)
                if score > 100: self.legendary_lives += 1
                if score > self.top_score:
                    self.top_score = score
                    self.best_weights = weights


class Agent:
    def __init__(self, mem, id, role_dist):
        self.mem, self.id, self.role_dist = mem, id, role_dist
        self.path = deque(maxlen=40)
        self.brain = NeuralMind(input_size=10, output_size=5)
        self.reset()

    def reset(self):
        self.s, self.r, self.b = 10.0, 28.0, 2.666
        self.state = np.random.uniform(-15, 15, 3)
        self.energy = np.random.uniform(6, 12)
        self.mood, self.fear = 0.0, 0.0
        rand = random.random()
        if rand < self.role_dist['judge']:
            self.role, self.color, self.energy = 'judge', np.array([1, 1, 1]), 20.0
        elif rand < self.role_dist['judge'] + self.role_dist['parasite']:
            self.role, self.color = 'parasite', np.array([0.4, 0, 0])
        else:
            self.role, self.color = 'soul', np.random.uniform(0.4, 0.9, 3)
            if self.mem.best_weights and random.random() < 0.7:
                self.brain.set_weights(self.mem.best_weights)

    def step(self, others, gm, gf):
        dt = 0.006
        x, y, z = self.state
        velocity = np.array([self.s * (y - x), x * (self.r - z) - y, x * y - self.b * z])
        threat_dist, soul_dist, target = 100.0, 100.0, None
        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            if dist < 40.0:
                if other.role == 'soul' and dist < soul_dist:
                    soul_dist, target = dist, other
                elif other.role in ['parasite', 'judge'] and dist < threat_dist:
                    threat_dist = dist

        inputs = np.array([x, y, z, self.mood, self.fear, self.energy, threat_dist, soul_dist, gm, gf])
        decision = self.brain.forward(inputs.reshape(1, -1))[0]
        force = decision[0:3] * 0.4 + np.random.normal(0, 0.02, 3)
        self.coupled = False

        for other in others:
            if other == self: continue
            dist = np.linalg.norm(self.state - other.state)
            vec = (other.state - self.state)
            if self.role == 'soul':
                if target == other: force += vec * decision[3]
                if dist < 5.0 and other.role == 'soul': self.coupled, self.mood = True, min(1.0, self.mood + 0.02)
                if dist < 12.0 and other.role != 'soul': force -= vec * decision[4]; self.fear = 0.8
            elif self.role == 'parasite' and target == other:
                force += vec * 1.5
                if dist < 2.5: self.energy += 0.25; other.energy -= 0.4; self.mood += 0.1

        self.state += (velocity + force) * dt
        self.path.append(self.state.copy())
        self.energy -= 0.009 * (1.1 - self.mood * 0.3)

        target_out = np.zeros(5)
        if self.coupled: target_out[3] = 1.0
        if threat_dist < 10.0: target_out[4] = 1.0
        self.brain.train(inputs, target_out)

        if self.energy <= 0 or np.linalg.norm(self.state) > 170:
            self.mem.save(list(self.path), self.color, self.role, self.mood, self.brain.get_weights())
            self.reset()


def run_universe():
    mem = EternalMemory()
    agents = [Agent(mem, i, {'judge': 0.05, 'parasite': 0.25}) for i in range(16)]
    plt.ion()
    fig = plt.figure(figsize=(12, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    steps = 0

    print("--- ARCHITECT: UNIVERSE INITIALIZED ---")
    while True:
        steps += 1
        gm = np.mean([a.mood for a in agents])
        gf = np.mean([a.fear for a in agents])
        for a in agents: a.step(agents, gm, gf)

        # COSMIC JOURNAL: Reporting every 1000 steps
        if steps % 1000 == 0:
            avg_energy = np.mean([a.energy for a in agents])
            souls_alive = len([a for a in agents if a.role == 'soul'])
            print(f"\n[COSMIC JOURNAL - STEP {steps}]")
            print(f" > Collective Consciousness: {'Stable' if gm > 0 else 'Suffering'}")
            print(f" > Global Mood: {gm:.2f} | Global Fear: {gf:.2f}")
            print(f" > Population: {souls_alive} Souls | {len(agents) - souls_alive} Predators/Laws")
            print(f" > Legacy Score: {mem.top_score:.1f} | Legendary Lives: {mem.legendary_lives}")
            print(f" > Total Cycle Rebirths: {mem.total_deaths}")
            if gm < -0.3:
                print(" ! WARNING: World is descending into entropy.")
            elif gm > 0.3:
                print(" * NOTICE: World is experiencing an Era of Harmony.")

        if steps % 8 == 0:
            ax.clear();
            ax.set_axis_off()
            for t in mem.canvas:
                ax.plot(t['d'][:, 0], t['d'][:, 1], t['d'][:, 2], color=t['c'], alpha=0.2, lw=0.7)
            for a in agents:
                if len(a.path) > 1:
                    d = np.array(a.path)
                    ax.plot(d[:, 0], d[:, 1], d[:, 2], color=a.color, lw=2 if getattr(a, 'coupled', False) else 1)
            ax.set_xlim(-70, 70);
            ax.set_ylim(-70, 70);
            ax.set_zlim(0, 90)
            plt.pause(0.001)


if __name__ == "__main__":
    run_universe()