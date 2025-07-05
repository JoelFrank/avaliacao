import numpy as np
import random
from dataclasses import dataclass

# Fontes:
# https://www.datacamp.com/pt/tutorial/introduction-q-learning-beginner-tutorial
# https://www.geeksforgeeks.org/q-learning-in-python/
# https://www.youtube.com/watch?v=tz8phEIqKAM

M = 4

@dataclass
class Jogador:
    pontos: int = 0
    ouro: bool = False
    flecha: bool = True
    posi: tuple = (0, 0)

def gerar_mapa():
    return np.full((M, M), 0)

def add_object(matriz, valor):
    vazios = [(i, j) for i in range(M) for j in range(M) if matriz[i, j] == 0]
    if vazios:
        i, j = random.choice(vazios)
        matriz[i, j] = valor

def gerar_estruturas():
    matriz = gerar_mapa()
    matriz[0, 0] = 1
    add_object(matriz, 2) # wumpus
    add_object(matriz, 3) # ouro
    add_object(matriz, 4) # buraco
    add_object(matriz, 4)
    add_object(matriz, 4)
    return matriz

def pos_to_index(pos):
    i, j = pos
    return i * M + j

def movimentar(novo_i, novo_j, mapa, jogador, wumpus_alive):

    if novo_i < 0 or novo_j < 0 or novo_i >= M or novo_j >= M:  # bateu na parede
        recompensa = -5
        return recompensa, wumpus_alive, False, False
    
    jogador.posi = (novo_i, novo_j)
    valor = mapa[novo_i, novo_j]

    if valor == 2 and wumpus_alive:   # morte por wumpus 
        jogador.pontos -= 100
        recompensa = -100
        return recompensa, wumpus_alive, False, True
    
    if valor == 4:   # morte por buraco
        jogador.pontos -= 100
        recompensa = -100
        return recompensa, wumpus_alive, False, True

    if valor == 3 and not jogador.ouro: # achou o ouro
        jogador.pontos += 50
        mapa[novo_i, novo_j] = 0
        jogador.ouro = True
        recompensa = 100
        return recompensa, wumpus_alive, True, False
    
    if valor == 1 and jogador.ouro == True: # voltou com o ouro
        jogador.pontos += 50
        recompensa = 100
        return recompensa, wumpus_alive, False, True
    
    return -1, wumpus_alive, True, False
    
def atirar(i, j, mapa, jogador, wumpus_alive):
    if not jogador.flecha or not wumpus_alive:
        return 0, wumpus_alive
    
    jogador.flecha = False

    if i < 0 or i >= M or j < 0 or j >= M:
        recompensa = -50
        return recompensa, wumpus_alive
    
    valor = mapa[i, j]
    if valor == 2 and wumpus_alive:
        wumpus_alive = False
        mapa[i, j] = 0
        jogador.pontos += 50
        recompensa = 200    # recompensa maior para incentivar o agente
        return recompensa, wumpus_alive
    
    return -50, wumpus_alive

n_states = M * M * 2 * 2 * 2  
n_actions = 8
# 8 acoes, 4 de andar e 4 de atirar
Q_table = np.full((n_states, n_actions), 0)


learning_rate = 0.2
discount_factor = 0.99
epsilon_start = 1.0
epsilon_min = 0.01
epsilon_decay = 0.995
epochs = 5000

def state_to_index(i, j, ouro, flecha, wumpus_alive):
    return (i * M * 8) + (j * 8) + (ouro * 4) + (flecha * 2) + wumpus_alive

def choose_action(state, epsilon):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, n_actions - 1)
    return np.argmax(Q_table[state, :])

matriz = gerar_estruturas()

epsilon = epsilon_start
melhor_pontuacao = -float('inf')

for epoch in range(epochs):
    jogador = Jogador()
    mapa = np.copy(matriz)
    i, j = 0, 0 
    wumpus_alive = True
    done = False
    valid = False
    ouro = 0
    flecha = 0
    state = state_to_index(i, j, ouro, flecha, int(wumpus_alive))

    for step in range(5000):
        
        acao = choose_action(state, epsilon)

        novo_i, novo_j = i, j
        if acao == 0:   # cima
            novo_i = i-1
            recompensa, wumpus_alive, valid, done = movimentar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 1:   # baixo
            novo_i = i+1
            recompensa, wumpus_alive, valid, done = movimentar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 2:   # direita
            novo_j = j+1
            recompensa, wumpus_alive, valid, done = movimentar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 3:   # esquerda
            novo_j = j-1
            recompensa, wumpus_alive, valid, done = movimentar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if valid:  
            i, j = novo_i, novo_j

        if acao == 4:   # atirar/cima
            novo_i = i-1
            recompensa, wumpus_alive = atirar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 5:   # atirar/baixo
            novo_i = i+1
            recompensa, wumpus_alive = atirar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 6:   # atirar/direita
            novo_j = j+1
            recompensa, wumpus_alive = atirar(novo_i, novo_j, mapa, jogador, wumpus_alive)

        if acao == 7:   # atirar/esquerda
            novo_j = j-1
            recompensa, wumpus_alive = atirar(novo_i, novo_j, mapa, jogador, wumpus_alive)
        
        ouro = int(jogador.ouro)
        flecha = int(jogador.flecha)
        next_state = state_to_index(i, j, ouro, flecha, int(wumpus_alive))

        futuro_max = np.max(Q_table[next_state])
        Q_table[state, acao] = Q_table[state, acao] + learning_rate * (recompensa + discount_factor * futuro_max - Q_table[state, acao])

        state = next_state
        jogador.pontos -= 1

        if done:
            if jogador.pontos > melhor_pontuacao:
                melhor_pontuacao = jogador.pontos
            break

    epsilon = max(epsilon_min, epsilon * epsilon_decay)


    print(f"Epoch {epoch+1}, Pontos: {jogador.pontos}")

print(f"Melhor pontuação alcançada: {melhor_pontuacao}")

print(Q_table)
print("____________")
print(matriz)
print("____________")

# i = linha j = coluna