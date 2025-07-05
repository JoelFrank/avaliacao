import random
import numpy as np

# parametros Q-learning
alpha = 0.1
gamma = 0.9
epsilon = 1.0
epsilon_decay = 0.99
epsilon_min = 0.1
episodios = 1000


tamanho = 4
acoes = ['cima', 'baixo', 'esquerda', 'direita']
q_table = np.zeros((tamanho, tamanho, len(acoes)))


tabuleiro = [['' for _ in range(tamanho)] for _ in range(tamanho)]
tabuleiro[1][1] = 'buraco'
tabuleiro[2][3] = 'buraco'
tabuleiro[0][3] = 'buraco'
tabuleiro[1][3] = 'wumpus'
tabuleiro[0][0] = 'ouro'

def recompensar(pos):
    x, y = pos
    if tabuleiro[x][y] == 'ouro':
        return 100
    elif tabuleiro[x][y] == 'buraco' or tabuleiro[x][y] == 'wumpus':
        return -100
    else:
        return -1

def mover(pos, acao):
    x, y = pos
    if acao == 'cima' and x > 0:
        x -= 1
    elif acao == 'baixo' and x < tamanho - 1:
        x += 1
    elif acao == 'esquerda' and y > 0:
        y -= 1
    elif acao == 'direita' and y < tamanho - 1:
        y += 1
    return (x, y)


for ep in range(1, episodios + 1):
    estado = (3, 0)
    terminado = False
    trajeto = [(estado, None)]  

    while not terminado:
        if random.uniform(0, 1) < epsilon:
            acao_idx = random.randint(0, len(acoes) - 1)
        else:
            acao_idx = np.argmax(q_table[estado[0], estado[1]])

        acao = acoes[acao_idx]
        novo_estado = mover(estado, acao)
        recompensa = recompensar(novo_estado)

        
        old_value = q_table[estado[0], estado[1], acao_idx]
        next_max = np.max(q_table[novo_estado[0], novo_estado[1]])
        q_table[estado[0], estado[1], acao_idx] = old_value + alpha * (
            recompensa + gamma * next_max - old_value
        )

        trajeto.append((novo_estado, acao))
        estado = novo_estado

        if recompensa == 100 or recompensa == -100:
            terminado = True

    
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    
    if recompensa == 100:
        print(f"\n Episódio {ep}: AGENTE VENCEU!")
        print("Caminho até o ouro:")
        for i, (s, a) in enumerate(trajeto):
            if a:
                print(f"{i}. Posição: {s}, Ação tomada: {a}")
            else:
                print(f"{i}. Posição inicial: {s}")
        break