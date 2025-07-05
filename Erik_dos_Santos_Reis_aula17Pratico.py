import numpy as np
import random

def CriarTabuleiro():
    tabuleiro = np.full((4, 4), "----", dtype=object) 

    tabuleiro[2, 2] = "Wumpus"
    tabuleiro[3, 2] = "Buraco"
    tabuleiro[0, 2] = "Buraco"
    tabuleiro[3, 0] = "Buraco"
    tabuleiro[3, 3] = "Ouro"

    posicoes = [(0,1), (1,0), (-1,0), (0,-1)]

    for dx, dy in posicoes:
        x, y = 2 + dx, 2 + dy
        if 0 <= x < 4 and 0 <= y < 4 and tabuleiro[x, y] == "----":
            tabuleiro[x, y] = "Cheiro Ruim"

    buracos = [(3,2), (0,2), (3,0)]
    for bx, by in buracos:
        for dx, dy in posicoes:
            x, y = bx + dx, by + dy
            if 0 <= x < 4 and 0 <= y < 4 and tabuleiro[x, y] == "----":
                tabuleiro[x, y] = "Brisa"

    return tabuleiro

def TabuleiroSimplificado():
    tabuleiroSimplificado = np.full((4, 4), "-", dtype=object) 

    tabuleiroSimplificado[2, 2] = "W"
    tabuleiroSimplificado[3, 2] = "B"
    tabuleiroSimplificado[0, 2] = "B"
    tabuleiroSimplificado[3, 0] = "B"
    tabuleiroSimplificado[3, 3] = "O"

    return tabuleiroSimplificado

def EscolherCaminho(posicao, acao):
    if acao == "cima":
        return (posicao[0] - 1, posicao[1])
    elif acao == "baixo":
        return (posicao[0] + 1, posicao[1])
    elif acao == "direita":
        return (posicao[0], posicao[1] + 1)
    elif acao == "esquerda":
        return (posicao[0], posicao[1] - 1)

def TreinarQLearning(episodios=1000):
    Q = {}
    acoes = ["cima", "baixo", "direita", "esquerda"]
    alpha = 0.1
    gamma = 0.9
    epsilon = 1.0

    tabuleiro = CriarTabuleiro()

    for episodio in range(episodios):
        estado = (0, 0)

        while estado != (3, 3):
            if estado not in Q:
                Q[estado] = [0, 0, 0, 0]

            if random.random() < epsilon:
                acao = random.choice(acoes)
            else:
                max_valor = max(Q[estado])
                indice = Q[estado].index(max_valor)
                acao = acoes[indice]

            prox_estado = EscolherCaminho(estado, acao)

            if not (0 <= prox_estado[0] < 4 and 0 <= prox_estado[1] < 4):
                recompensa = -5
                prox_estado = estado
            else:
                conteudo = tabuleiro[prox_estado]
                if conteudo == "Buraco" or conteudo == "Wumpus":
                    recompensa = -100
                elif conteudo == "Ouro":
                    recompensa = 1000
                else:
                    recompensa = -1

            if prox_estado not in Q:
                Q[prox_estado] = [0, 0, 0, 0]

            indice_acao = acoes.index(acao)
            Q[estado][indice_acao] += alpha * (
                recompensa + gamma * max(Q[prox_estado]) - Q[estado][indice_acao]
            )

            estado = prox_estado

    return Q, tabuleiro


def MelhorCaminho(Q):
    estado = (0, 0)
    acoes = ["cima", "baixo", "direita", "esquerda"]
    caminho = [estado]

    while estado != (3, 3):

        indice = Q[estado].index(max(Q[estado]))
        acao = acoes[indice]
        estado = EscolherCaminho(estado, acao)
        caminho.append(estado)

    print("Caminho encontrado")
    for pos in caminho:
        print(pos)

def PrintMatrizQ(Q):
    print("Matriz Q-learning -- cima, baixo, direita, esquerda")
    for posicao, lista in Q.items():
        print(f"{posicao}: {lista}")

Q, tabuleiro = TreinarQLearning()
print("\nTabuleiro:")
print(tabuleiro)
print("\nTabuleiro Simplificado:")
print(TabuleiroSimplificado())
PrintMatrizQ(Q)
MelhorCaminho(Q)
