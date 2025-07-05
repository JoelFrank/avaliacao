"""
## Mundo de Wumpus - Agente com Aprendizado por Reforço

- Este projeto implementa um agente autônomo para o Mundo de Wumpus usando o algoritmo Q-Learning de aprendizado por reforço.


#Funcionalidades:
- Ambiente 4x4 com Wumpus, ouro e poços
- Sistema de recompensas (+1000 ouro, -1000 perigos, -1 movimento)
- Treinamento por 1000 episódios
- Visualização do progresso e testes
- Gráficos de performance

Autor: Shogo Miyazaki
Disciplina: Inteligência Artificial
"""

import numpy as np
import random
import matplotlib.pyplot as plt
from collections import defaultdict

class WumpusWorld:
    def __init__(self, size=4):
        self.size = size
        self.reset()
        
    def reset(self):
        self.agent_pos = [0, 0]
        self.wumpus_pos = [1, 2]
        self.gold_pos = [2, 3]
        self.pits = [[1, 1], [2, 1], [3, 2]]
        self.has_gold = False
        self.is_alive = True
        self.game_over = False
        return self.get_state()
    
    def get_state(self):
        return tuple(self.agent_pos + [int(self.has_gold)])
    
    def get_valid_actions(self):
        actions = []
        x, y = self.agent_pos
        if x > 0: actions.append(0)
        if x < self.size - 1: actions.append(1)
        if y > 0: actions.append(2)
        if y < self.size - 1: actions.append(3)
        return actions
    
    def step(self, action):
        if self.game_over:
            return self.get_state(), 0, True
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if action in self.get_valid_actions():
            dx, dy = moves[action]
            self.agent_pos[0] += dx
            self.agent_pos[1] += dy
        reward = self.calculate_reward()
        if not self.is_alive or (self.has_gold and self.agent_pos == [0, 0]):
            self.game_over = True
        return self.get_state(), reward, self.game_over
    
    def calculate_reward(self):
        reward = -1
        if self.agent_pos == self.gold_pos and not self.has_gold:
            self.has_gold = True
            reward += 1000
        if self.has_gold and self.agent_pos == [0, 0]:
            reward += 1000
        if self.agent_pos in self.pits:
            self.is_alive = False
            reward -= 1000
        if self.agent_pos == self.wumpus_pos:
            self.is_alive = False
            reward -= 1000
        return reward
    
    def get_percepts(self):
        x, y = self.agent_pos
        breeze = False
        stench = False
        for px, py in self.pits:
            if abs(x - px) + abs(y - py) == 1:
                breeze = True
                break
        wx, wy = self.wumpus_pos
        if abs(x - wx) + abs(y - wy) == 1:
            stench = True
        return breeze, stench
    
    def render(self):
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        for px, py in self.pits:
            grid[py][px] = 'P'
        wx, wy = self.wumpus_pos
        grid[wy][wx] = 'W'
        if not self.has_gold:
            gx, gy = self.gold_pos
            grid[gy][gx] = 'G'
        ax, ay = self.agent_pos
        if self.is_alive:
            grid[ay][ax] = 'A' if not self.has_gold else 'A*'
        else:
            grid[ay][ax] = 'X'
        print("\n" + "="*20)
        for row in reversed(grid):
            print(" ".join(row))
        print("="*20)
        breeze, stench = self.get_percepts()
        print(f"Percepções: Brisa={breeze}, Fedor={stench}")
        print(f"Tem ouro: {self.has_gold}, Vivo: {self.is_alive}")

class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
    
    def get_action(self, state, valid_actions):
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            q_values = [self.q_table[state][action] for action in valid_actions]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(valid_actions, q_values) if q == max_q]
            return random.choice(best_actions)
    
    def update_q_value(self, state, action, reward, next_state, valid_next_actions):
        current_q = self.q_table[state][action]
        if valid_next_actions:
            max_next_q = max([self.q_table[next_state][a] for a in valid_next_actions])
        else:
            max_next_q = 0
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

def train_agent(episodes=1000, render_interval=100):
    env = WumpusWorld()
    agent = QLearningAgent()
    scores = []
    success_rate = []
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 100
        while not env.game_over and steps < max_steps:
            valid_actions = env.get_valid_actions()
            action = agent.get_action(state, valid_actions)
            next_state, reward, done = env.step(action)
            next_valid_actions = env.get_valid_actions() if not done else []
            agent.update_q_value(state, action, reward, next_state, next_valid_actions)
            state = next_state
            total_reward += reward
            steps += 1
            if episode % render_interval == 0 and episode > 0:
                if steps == 1:
                    print(f"\nEpisódio {episode}")
                    env.render()
        scores.append(total_reward)
        if episode >= 99:
            recent_episodes = scores[-100:]
            successes = sum(1 for score in recent_episodes if score > 0)
            success_rate.append(successes / 100)
        agent.decay_epsilon()
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores)
            print(f"Episódio {episode}, Score médio: {avg_score:.2f}, Epsilon: {agent.epsilon:.3f}")
    return agent, scores, success_rate

def test_agent(agent, episodes=10):
    env = WumpusWorld()
    successes = 0
    print("\n" + "="*50)
    print("TESTANDO AGENTE TREINADO")
    print("="*50)
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 50
        print(f"\n--- Teste {episode + 1} ---")
        env.render()
        while not env.game_over and steps < max_steps:
            valid_actions = env.get_valid_actions()
            q_values = [agent.q_table[state][action] for action in valid_actions]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(valid_actions, q_values) if q == max_q]
            action = random.choice(best_actions)
            print(f"Ação escolhida: {['Esquerda', 'Direita', 'Baixo', 'Cima'][action]}")
            next_state, reward, done = env.step(action)
            state = next_state
            total_reward += reward
            steps += 1
            env.render()
            if done:
                break
        if env.has_gold and env.agent_pos == [0, 0]:
            successes += 1
            print("✓ SUCESSO! Agente coletou o ouro e escapou!")
        else:
            print("✗ Falhou...")
        print(f"Recompensa total: {total_reward}")
    print(f"\nTaxa de sucesso: {successes}/{episodes} ({successes/episodes*100:.1f}%)")

def plot_training_progress(scores, success_rate):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    window = 100
    moving_avg = [np.mean(scores[max(0, i-window):i+1]) for i in range(len(scores))]
    ax1.plot(scores, alpha=0.3, color='blue', label='Score por episódio')
    ax1.plot(moving_avg, color='red', label=f'Média móvel ({window} episódios)')
    ax1.set_xlabel('Episódio')
    ax1.set_ylabel('Score')
    ax1.set_title('Progresso do Treinamento')
    ax1.legend()
    ax1.grid(True)
    if success_rate:
        ax2.plot(range(99, 99 + len(success_rate)), success_rate, color='green')
        ax2.set_xlabel('Episódio')
        ax2.set_ylabel('Taxa de Sucesso (%)')
        ax2.set_title('Taxa de Sucesso (últimos 100 episódios)')
        ax2.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Iniciando treinamento do agente Q-learning no Mundo do Wumpus...")
    print("\nLegenda:")
    print("A = Agente, A* = Agente com ouro")
    print("W = Wumpus, P = Poço, G = Ouro")
    print("X = Agente morto")
    trained_agent, training_scores, success_rates = train_agent(episodes=1000, render_interval=200)
    plot_training_progress(training_scores, success_rates)
    test_agent(trained_agent, episodes=5)
    print(f"\nEstatísticas finais:")
    print(f"Score médio (últimos 100 episódios): {np.mean(training_scores[-100:]):.2f}")
    print(f"Epsilon final: {trained_agent.epsilon:.3f}")
    print(f"Tamanho da Q-table: {len(trained_agent.q_table)} estados")