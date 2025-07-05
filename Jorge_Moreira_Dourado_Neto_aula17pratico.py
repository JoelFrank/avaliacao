import numpy as np
import random

# Parâmetros do ambiente
GRID_SIZE = 4
ACTIONS = ['up', 'down', 'left', 'right']
ALPHA = 0.1      # taxa de aprendizado
GAMMA = 0.9      # fator de desconto
EPSILON = 0.2    # política epsilon-greedy
EPISODES = 5000

# Recompensas
REWARD_GOLD = 100
REWARD_WUMPUS = -100
REWARD_PIT = -100
REWARD_STEP = -1

# Ambiente do mundo do Wumpus
class WumpusWorld:
    def __init__(self):
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        self.gold_pos = [3, 3]
        self.pits = [[1, 2], [2, 2]]
        self.wumpus = [1, 1]
        self.done = False
        return self._get_state()

    def _get_state(self):
        return tuple(self.agent_pos)

    def _in_bounds(self, pos):
        return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE

    def step(self, action):
        if self.done:
            return self._get_state(), 0, True

        delta = {'up': [-1, 0], 'down': [1, 0], 'left': [0, -1], 'right': [0, 1]}
        new_pos = [self.agent_pos[0] + delta[action][0], self.agent_pos[1] + delta[action][1]]

        if self._in_bounds(new_pos):
            self.agent_pos = new_pos

        reward = REWARD_STEP
        if self.agent_pos == self.gold_pos:
            reward = REWARD_GOLD
            self.done = True
        elif self.agent_pos in self.pits or self.agent_pos == self.wumpus:
            reward = REWARD_PIT
            self.done = True

        return self._get_state(), reward, self.done

# Q-Learning agente
class QLearningAgent:
    def __init__(self):
        self.q_table = {}
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                self.q_table[(x, y)] = {a: 0 for a in ACTIONS}

    def choose_action(self, state):
        if random.uniform(0, 1) < EPSILON:
            return random.choice(ACTIONS)
        else:
            return max(self.q_table[state], key=self.q_table[state].get)

    def update(self, state, action, reward, next_state):
        max_q = max(self.q_table[next_state].values())
        self.q_table[state][action] += ALPHA * (reward + GAMMA * max_q - self.q_table[state][action])

# Treinamento
env = WumpusWorld()
agent = QLearningAgent()

for episode in range(EPISODES):
    state = env.reset()
    done = False

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, next_state)
        state = next_state

# Exemplo de execução após treinamento
print("Execução após treinamento:")

state = env.reset()
done = False
steps = 0
while not done:
    action = agent.choose_action(state)
    print(f"Estado: {state} -> Ação: {action}")
    state, reward, done = env.step(action)
    steps += 1

print(f"Recompensa final: {reward}, em {steps} passos.")