import random as rd
import numpy as np

matriz = np.empty((4, 4), dtype=object)
for i in range(4):
    for j in range(4):
        matriz[i][j] = []

dx_dy = [(-1, 0), (0, 1), (1, 0), (0, -1)]
acoes = [0, 1, 2, 3]

alpha = 0.1
gamma = 0.9
epsilon = 0.2
episodios = 2000
max_passos = 50

Q = {}

ocupado = set()
def posiciona():
    while True:
        x, y = rd.randint(0, 3), rd.randint(0, 3)
        if (x, y) not in ocupado and (x, y) != (0, 0):
            ocupado.add((x, y))
            return x, y

ouro_x, ouro_y = posiciona()
matriz[ouro_x][ouro_y].append("Ouro")

x, y = posiciona()
matriz[x][y].append("Wumpus")

for _ in range(3):
    x, y = posiciona()
    matriz[x][y].append("Buraco")

for i in range(4):
    for j in range(4):
        if "Wumpus" in matriz[i][j]:
            for dx, dy in dx_dy:
                ni, nj = i + dx, j + dy
                if 0 <= ni < 4 and 0 <= nj < 4:
                    matriz[ni][nj].append("Cheiro ruim")
        if "Buraco" in matriz[i][j]:
            for dx, dy in dx_dy:
                ni, nj = i + dx, j + dy
                if 0 <= ni < 4 and 0 <= nj < 4:
                    matriz[ni][nj].append("Brisa")

def recompensa(l, c, pegou):
    if not (0 <= l < 4 and 0 <= c < 4):
        return -5
    if "Buraco" in matriz[l][c] or "Wumpus" in matriz[l][c]:
        return -100
    if "Ouro" in matriz[l][c] and not pegou:
        return 100
    if (l, c) == (0, 0) and pegou:
        return 200
    return -1

def mover(l, c, acao):
    dx, dy = dx_dy[acao]
    return l + dx, c + dy

for ep in range(episodios):
    l, c = 0, 0
    pegou = False
    for _ in range(max_passos):
        estado = (l, c, pegou)
        if estado not in Q:
            Q[estado] = {a: 0 for a in acoes}
        if rd.random() < epsilon:
            acao = rd.choice(acoes)
        else:
            acao = max(Q[estado], key=Q[estado].get)

        nl, nc = mover(l, c, acao)
        novo_pegou = pegou or (0 <= nl < 4 and 0 <= nc < 4 and "Ouro" in matriz[nl][nc])
        prox_estado = (nl, nc, novo_pegou)
        r = recompensa(nl, nc, pegou)

        if prox_estado not in Q:
            Q[prox_estado] = {a: 0 for a in acoes}

        Q[estado][acao] += alpha * (r + gamma * max(Q[prox_estado].values()) - Q[estado][acao])

        if r == 200 or r == -100:
            break

        l, c = nl, nc
        pegou = novo_pegou

def politica_q():
    caminho = []
    l, c, pegou = 0, 0, False
    for _ in range(100):
        estado = (l, c, pegou)
        if estado not in Q:
            break
        acao = max(Q[estado], key=Q[estado].get)
        caminho.append(((l, c), acao))
        l, c = mover(l, c, acao)
        if "Ouro" in matriz[l][c]:
            pegou = True
        if (l, c) == (0, 0) and pegou:
            caminho.append(((l, c), None))
            break
    return caminho

trajetoria = politica_q()

print("\nMatriz com elementos:")
for i in range(4):
    for j in range(4):
        conteudo = ', '.join(matriz[i][j]) or 'Livre'
        print(f"({i},{j}): {conteudo:<15}", end=' | ')
    print()

print("\nTrajetória do agente:")
for (pos, acao) in trajetoria:
    i, j = pos
    print(f"Posição: ({i},{j})", end='')
    if acao is not None:
        direcao = ['↑', '→', '↓', '←'][acao]
        print(f" - Ação: {direcao}")
    else:
        print(" - Fim (voltou ao início)")


###FONTE: ChatGPT, slides de aula