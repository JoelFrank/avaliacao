import numpy as np
import random

# Parâmetros do ambiente
GRID_SIZE = 4
ACTIONS = ['up', 'down', 'left', 'right']
ACTION_IDX = {a: i for i, a in enumerate(ACTIONS)}

# Mundo do Wumpus
class WumpusWorld:
    def __init__(self):
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        self.has_gold = False
        self.is_done = False

        # Configuração do mapa (poços, wumpus e ouro)
        self.wumpus = (1, 2)
        self.gold = (2, 3)
        self.pits = [(3, 0), (3, 3), (1, 3)]
        
        return tuple(self.agent_pos)

    def step(self, action):
        if self.is_done:
            return tuple(self.agent_pos), 0, True

        x, y = self.agent_pos
        if action == 'up':
            nx, ny = x - 1, y
        elif action == 'down':
            nx, ny = x + 1, y
        elif action == 'left':
            nx, ny = x, y - 1
        elif action == 'right':
            nx, ny = x, y + 1
        else:
            nx, ny = x, y

        # Checar se bate na parede
        if nx < 0 or ny < 0 or nx >= GRID_SIZE or ny >= GRID_SIZE:
            reward = -5  # Penalidade por bater na parede
            next_state = tuple(self.agent_pos)
            return next_state, reward, False

        # Atualiza posição
        self.agent_pos = [nx, ny]
        pos = (nx, ny)

        # Checa eventos
        if pos in self.pits:
            reward = -1000
            self.is_done = True
        elif pos == self.wumpus:
            reward = -1000
            self.is_done = True
        elif pos == self.gold:
            reward = 1000
            self.has_gold = True
            self.is_done = True
        else:
            reward = -1  # Custo de movimento

        return pos, reward, self.is_done


# Agente Q-learning
class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = np.zeros((GRID_SIZE, GRID_SIZE, len(ACTIONS)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(ACTIONS)
        else:
            x, y = state
            return ACTIONS[np.argmax(self.q_table[x, y])]

    def learn(self, state, action, reward, next_state):
        x, y = state
        nx, ny = next_state
        action_index = ACTION_IDX[action]

        predict = self.q_table[x, y, action_index]
        target = reward + self.gamma * np.max(self.q_table[nx, ny])

        self.q_table[x, y, action_index] += self.alpha * (target - predict)


# Loop de treinamento
env = WumpusWorld()
agent = QLearningAgent()

EPISODES = 1000

for episode in range(EPISODES):
    state = env.reset()
    total_reward = 0

    while True:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)

        agent.learn(state, action, reward, next_state)

        state = next_state
        total_reward += reward

        if done:
            break

    if (episode + 1) % 100 == 0:
        print(f'Episódio {episode+1}: Recompensa total = {total_reward}')


# Testando agente treinado
print("\nTestando agente treinado:")
state = env.reset()
env.is_done = False
steps = 0
total_reward = 0  # <-- Adiciona acumulador

while not env.is_done:
    action = agent.choose_action(state)
    next_state, reward, done = env.step(action)
    total_reward += reward  # <-- Acumula recompensa

    print(f'Posição: {state} -> Ação: {action} -> Próxima: {next_state} | Recompensa: {reward}')
    state = next_state
    steps += 1

    if done or steps > 20:
        break

print(f"\nRecompensa total no teste: {total_reward}")
