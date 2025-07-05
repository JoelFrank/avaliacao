import numpy as np
import random

# Parâmetros do ambiente
n_linhas, n_colunas = 4, 4
actions = ['cima', 'baixo', 'esquerda', 'direita']
action_map = {
    'cima': (-1, 0),
    'baixo': (1, 0),
    'esquerda': (0, -1),
    'direita': (0, 1)
}

# Tabuleiro fixo (G = gold, P = pit, W = wumpus, S = start)
# S está em (3, 0)
board = [
    ['.', '.', '.', '.'],
    ['.', '.', 'P', '.'],
    ['.', 'W', 'G', '.'],
    ['S', '.', 'P', '.']
]

# Recompensas
def get_reward(state):
    x, y = state
    cell = board[x][y]
    if cell == 'G':
        return 100
    elif cell == 'P' or cell == 'W':
        return -100
    else:
        return -1  # Custo por andar

# Verifica se o estado é terminal
def is_terminal(state):
    x, y = state
    return board[x][y] in ['G', 'P', 'W']

# Movimento do agente
def move(state, action):
    dx, dy = action_map[action]
    new_x = min(max(state[0] + dx, 0), n_linhas - 1)
    new_y = min(max(state[1] + dy, 0), n_colunas - 1)
    return (new_x, new_y)

# Inicialização da Q-table
Q = {}
for i in range(n_linhas):
    for j in range(n_colunas):
        Q[(i, j)] = {a: 0.0 for a in actions}

# Hiperparâmetros
alpha = 0.1      # taxa de aprendizado
gamma = 0.9      # fator de desconto
epsilon = 0.2    # exploração

# Treinamento
num_episodios = 1000
for episodio in range(num_episodios):
    state = (3, 0)  # posição inicial
    while not is_terminal(state):
        # Política ε-greedy
        if random.random() < epsilon:
            action = random.choice(actions)
        else:
            action = max(Q[state], key=Q[state].get)

        next_state = move(state, action)
        reward = get_reward(next_state)
        
        # Atualização da Q-table
        next_max = max(Q[next_state].values())
        Q[state][action] += alpha * (reward + gamma * next_max - Q[state][action])
        
        state = next_state

# Política final aprendida
for i in range(n_linhas):
    row = ""
    for j in range(n_colunas):
        if board[i][j] == '.':
            best_action = max(Q[(i, j)], key=Q[(i, j)].get)
            row += f"{best_action[0]} "  # mostra só a inicial da ação
        else:
            row += f"{board[i][j]}  "
    print(row)
