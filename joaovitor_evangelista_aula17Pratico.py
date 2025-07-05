import random
import numpy as np

class Environment:
    def __init__(self, board_layout, rewards_map):
        self.board = board_layout
        self.rows, self.cols = len(board_layout), len(board_layout[0])
        self.rewards = rewards_map
        self.start_pos = (0, 0)

    def step(self, state, action):
        row, col = state

        if action == 'up':
            row -= 1
        elif action == 'down':
            row += 1
        elif action == 'left':
            col -= 1
        elif action == 'right':
            col += 1

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols: #evitar sair do tabuleiro
            return state, -1.0, False 
        
        next_state = (row, col)
        cell = self.board[row][col]
        reward = self.rewards[cell]
        done = cell in ['P', 'W', 'G'] 
        
        return next_state, reward, done

    def reset(self):
        return self.start_pos

class QLearningAgent:
    def __init__(self, actions, rows, cols, alpha=0.1, gamma=0.9):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = np.zeros((rows, cols, len(actions)))

    def choose_action(self, state, epsilon):
        row, col = state
        if random.uniform(0, 1) < epsilon:
            return random.choice(range(len(self.actions)))
        else:
            return np.argmax(self.q_table[row, col])

    def update(self, state, action_idx, reward, next_state):
        row, col = state
        next_row, next_col = next_state
        
        future_optimal_value = np.max(self.q_table[next_row, next_col])
        
        current_q = self.q_table[row, col, action_idx]

        new_q = current_q + self.alpha * (reward + self.gamma * future_optimal_value - current_q)
        self.q_table[row, col, action_idx] = new_q


def train(episodes=10000):
    board = [
        ['S', '.', 'P', 'G'],
        ['.', 'W', '.', '.'],
        ['.', '.', '.', '.'],
        ['P', '.', 'P', '.']
    ]

    rewards = {'S': -0.1, '.': -0.1, 'P': -100, 'W': -100, 'G': 100}
    actions = ['up', 'down', 'left', 'right']

    env = Environment(board_layout=board, rewards_map=rewards)
    agent = QLearningAgent(actions=actions, rows=env.rows, cols=env.cols, alpha=0.1, gamma=0.9)

    epsilon = 1.0  # Começa explorando 100% aleatório
    min_epsilon = 0.01
    epsilon_decay_rate = 0.9995 #valor para decair mais lentamente ao longo dos episódios

    for ep in range(episodes):
        state = env.reset()
        done = False

        while not done:
            action_idx = agent.choose_action(state, epsilon)
            action = actions[action_idx]
            
            next_state, reward, done = env.step(state, action)
            
            agent.update(state, action_idx, reward, next_state)
            
            state = next_state
        
        if epsilon > min_epsilon:
            epsilon *= epsilon_decay_rate
        
        if (ep + 1) % 1000 == 0:
            print(f"Episódio {ep+1}/{episodes} concluído. Epsilon atual: {epsilon:.4f}")

    print("\nTreinamento Concluído!")
    return agent, env

def show_policy(agent, env):
    action_symbols = {'up': '^', 'down': 'v', 'left': '<', 'right': '>'}
    
    print("\nPolítica Aprendida (Melhor Ação por Célula):")
    policy_grid = []
    for i in range(env.rows):
        row = []
        for j in range(env.cols):
            cell_content = env.board[i][j]
            if cell_content in ['P', 'W', 'G']:
                row.append(f" {cell_content} ")
            else:
                best_action_idx = np.argmax(agent.q_table[i, j])
                action = agent.actions[best_action_idx]
                row.append(f" {action_symbols[action]} ")
        policy_grid.append(row)
    
    for r in policy_grid:
        print("".join(r))

trained_agent, game_env = train(20000) 
show_policy(trained_agent, game_env)