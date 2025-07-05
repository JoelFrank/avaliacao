import numpy as np
import random
import matplotlib.pyplot as plt
import time

class WumpusWorldAgent:
    """
    Implementação de um agente autônomo que usa Q-learning para resolver o Mundo de Wumpus.
    """
    def __init__(self, grid_size=4, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.9995, min_epsilon=0.01):
        # --- Configuração do Ambiente ---
        self.grid_size = grid_size
        self.wumpus_pos = (1, 2)
        self.gold_pos = (2, 2)
        # Posições dos poços (Pits)
        self.pit_pos = [(2, 0), (3, 3)]
        self.start_pos = (0, 0)
        
        # --- Parâmetros do Q-learning ---
        self.actions = ['up', 'down', 'left', 'right']
        # Q-Table: (grid_size * grid_size) estados, 4 ações
        self.q_table = np.zeros((grid_size * grid_size, len(self.actions)))
        self.alpha = alpha       # Taxa de aprendizagem
        self.gamma = gamma       # Fator de desconto
        self.epsilon = epsilon   # Taxa de exploração inicial
        self.epsilon_decay = epsilon_decay # Fator de decaimento do epsilon
        self.min_epsilon = min_epsilon     # Epsilon mínimo para garantir exploração

    def _get_state_index(self, pos):
        """Converte a posição (linha, coluna) para um índice de estado único."""
        return pos[0] * self.grid_size + pos[1]

    def _get_reward_and_done(self, pos):
        """Calcula a recompensa para entrar em uma determinada posição."""
        if pos == self.gold_pos:
            return 1000, True  # Recompensa alta por encontrar o ouro
        if pos == self.wumpus_pos or pos in self.pit_pos:
            return -1000, True # Penalidade alta por morrer
        return -1, False # Penalidade pequena por cada movimento

    def choose_action(self, state_index):
        """Escolhe uma ação usando a política Epsilon-Greedy."""
        if random.uniform(0, 1) < self.epsilon:
            # Ação aleatória (Exploração)
            return random.choice(range(len(self.actions)))
        else:
            # Melhor ação conhecida (Explotação)
            return np.argmax(self.q_table[state_index])

    def step(self, state_pos, action_index):
        """Executa a ação e retorna o próximo estado, recompensa e se o episódio terminou."""
        action = self.actions[action_index]
        next_pos = list(state_pos)

        if action == 'up':
            next_pos[0] = max(0, state_pos[0] - 1)
        elif action == 'down':
            next_pos[0] = min(self.grid_size - 1, state_pos[0] + 1)
        elif action == 'left':
            next_pos[1] = max(0, state_pos[1] - 1)
        elif action == 'right':
            next_pos[1] = min(self.grid_size - 1, state_pos[1] + 1)
        
        next_pos = tuple(next_pos)
        reward, done = self._get_reward_and_done(next_pos)
        return next_pos, reward, done

    def train(self, num_episodes):
        """Executa o loop de treinamento do Q-learning."""
        rewards_per_episode = []
        print("--- Iniciando Treinamento ---")
        start_time = time.time()
        
        for episode in range(num_episodes):
            state_pos = self.start_pos
            done = False
            total_reward = 0
            steps = 0

            while not done and steps < 100: # Limite de passos para evitar loops infinitos
                state_index = self._get_state_index(state_pos)
                action_index = self.choose_action(state_index)
                
                next_state_pos, reward, done = self.step(state_pos, action_index)
                total_reward += reward
                
                # --- Atualização da Q-Table ---
                old_q_value = self.q_table[state_index, action_index]
                next_state_index = self._get_state_index(next_state_pos)
                next_max_q = np.max(self.q_table[next_state_index])
                
                # Fórmula do Q-learning
                new_q_value = old_q_value + self.alpha * (reward + self.gamma * next_max_q - old_q_value)
                self.q_table[state_index, action_index] = new_q_value
                
                state_pos = next_state_pos
                steps += 1
            
            # Decaimento do Epsilon
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay
            
            rewards_per_episode.append(total_reward)
            if (episode + 1) % 500 == 0:
                print(f"Episódio {episode + 1}/{num_episodes}: Recompensa Média (últimos 100) = {np.mean(rewards_per_episode[-100:]):.2f}")

        end_time = time.time()
        print(f"--- Treinamento Concluído em {end_time - start_time:.2f} segundos ---")
        return rewards_per_episode

    def run_trained_agent(self):
        """Executa um episódio com o agente treinado (sem exploração)."""
        print("\n--- Executando Agente Treinado (Política Ótima) ---")
        state_pos = self.start_pos
        done = False
        path = [state_pos]
        total_reward = 0
        
        while not done:
            state_index = self._get_state_index(state_pos)
            action_index = np.argmax(self.q_table[state_index]) # Apenas a melhor ação
            action = self.actions[action_index]
            
            print(f"Estado: {state_pos}, Ação: {action}")
            state_pos, reward, done = self.step(state_pos, action_index)
            path.append(state_pos)
            total_reward += reward

        print("\n--- Resultado Final ---")
        if reward == 1000:
            print("✨ Ouro encontrado! ✨")
        else:
            print("☠️ Agente morreu! ☠️")
            
        print(f"Caminho percorrido: {path}")
        print(f"Recompensa Total: {total_reward}")

    def plot_rewards(self, rewards):
        """Plota as recompensas por episódio."""
        plt.figure(figsize=(12, 6))
        plt.plot(rewards, alpha=0.6, label='Recompensa por Episódio')
        # Média móvel para visualizar a tendência
        moving_avg = np.convolve(rewards, np.ones(100)/100, mode='valid')
        plt.plot(moving_avg, color='red', label='Média Móvel (100 episódios)')
        plt.title('Recompensa por Episódio Durante o Treinamento')
        plt.xlabel('Episódio')
        plt.ylabel('Recompensa Total')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    # Cria e treina o agente
    agent = WumpusWorldAgent()
    rewards_history = agent.train(num_episodes=3000)
    
    # Executa o agente treinado e mostra o resultado
    agent.run_trained_agent()

    # Mostra a Q-Table final
    print("\n--- Q-Table Final (Valores arredondados) ---")
    print("Ações: [Cima, Baixo, Esquerda, Direita]")
    for i in range(agent.grid_size * agent.grid_size):
        pos = (i // agent.grid_size, i % agent.grid_size)
        print(f"Estado {i} {pos}: {np.round(agent.q_table[i], 2)}")
        
    # Plota o gráfico de recompensas
    agent.plot_rewards(rewards_history)