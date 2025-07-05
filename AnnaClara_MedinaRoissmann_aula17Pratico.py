# fontes:
# https://github.com/parham1998/Wumpus_Q-Learning/blob/main/Wumpus(python)/main.py
# https://github.com/Ceoxinia/Q-Learning-Wumpus-World/blob/main/Q-wumpus.ipynb

import numpy as np
import random
from collections import defaultdict

# Parâmetros do Q-Learning
alpha = 0.1  # taxa de aprendizado
gamma = 0.9  # fator de desconto
epsilon = 0.1  # taxa de exploração

tamanho = 4  # tabuleiro 4x4
acoes = ['cima', 'baixo', 'esquerda', 'direita']

# Recompensas
R_OURO = 100
R_MORTE = -100
R_BURACO = -10
R_GANHO_FINAL = 50

# Inicializa a tabela Q
Q = defaultdict(lambda: {a: 0.0 for a in acoes})

def estado_para_str(estado):
    return f"{estado[0]}-{estado[1]}-{int(estado[2])}-{int(estado[3])}"

def escolher_acao(estado):
    if np.random.rand() < epsilon:
        return random.choice(acoes)
    else:
        estado_str = estado_para_str(estado)
        return max(Q[estado_str], key=Q[estado_str].get)

def atualizar_q(estado, acao, recompensa, proximo_estado):
    estado_str = estado_para_str(estado)
    prox_str = estado_para_str(proximo_estado)
    melhor_futuro = max(Q[prox_str].values())
    Q[estado_str][acao] += alpha * (recompensa + gamma * melhor_futuro - Q[estado_str][acao])

def inicializar_mundo():
    tabuleiro = [['' for _ in range(tamanho)] for _ in range(tamanho)]
    ouro = (np.random.randint(tamanho), np.random.randint(tamanho))
    while ouro == (0, 0):
        ouro = (np.random.randint(tamanho), np.random.randint(tamanho))
    tabuleiro[ouro[0]][ouro[1]] = 'O'

    wumpus = (np.random.randint(tamanho), np.random.randint(tamanho))
    while wumpus == (0, 0) or wumpus == ouro:
        wumpus = (np.random.randint(tamanho), np.random.randint(tamanho))
    tabuleiro[wumpus[0]][wumpus[1]] = 'W'

    buracos = set()
    while len(buracos) < 3:
        b = (np.random.randint(tamanho), np.random.randint(tamanho))
        if b != (0, 0) and b != ouro and b != wumpus:
            buracos.add(b)
            tabuleiro[b[0]][b[1]] = 'B'

    return tabuleiro, ouro, wumpus, buracos

def mover(pos, acao):
    i, j = pos
    if acao == 'cima': return (max(i - 1, 0), j)
    if acao == 'baixo': return (min(i + 1, tamanho - 1), j)
    if acao == 'esquerda': return (i, max(j - 1, 0))
    if acao == 'direita': return (i, min(j + 1, tamanho - 1))
    return pos

def executar_episodio():
    tabuleiro, ouro, wumpus, buracos = inicializar_mundo()
    pos = (0, 0)
    ouro_pego = False
    wumpus_vivo = True
    total_recompensa = 0

    for passo in range(100):
        estado = (pos[0], pos[1], ouro_pego, wumpus_vivo)
        acao = escolher_acao(estado)
        nova_pos = mover(pos, acao)

        recompensa = R_BURACO
        fim = False

        conteudo = tabuleiro[nova_pos[0]][nova_pos[1]]
        if conteudo == 'O' and not ouro_pego:
            ouro_pego = True
            recompensa += R_OURO
        elif conteudo == 'W' and wumpus_vivo:
            recompensa += R_MORTE
            fim = True
        elif conteudo == 'B':
            recompensa += R_MORTE
            fim = True

        if ouro_pego and wumpus_vivo == False and nova_pos == (0, 0):
            recompensa += R_GANHO_FINAL
            fim = True

        novo_estado = (nova_pos[0], nova_pos[1], ouro_pego, wumpus_vivo)
        atualizar_q(estado, acao, recompensa, novo_estado)
        total_recompensa += recompensa

        pos = nova_pos

        if fim:
            break

    return total_recompensa

# Treinamento
for episodio in range(10000):
    recompensa = executar_episodio()
    if (episodio + 1) % 100 == 0:
        print(f"Episódio {episodio+1}: recompensa total = {recompensa:.2f}")

print("Treinamento finalizado.")

print("\nQ-table final:")
for estado_str, acoes_dict in Q.items():
    print(f"Estado {estado_str}:")
    for acao, valor in acoes_dict.items():
        print(f"  Ação '{acao}': {valor:.2f}")