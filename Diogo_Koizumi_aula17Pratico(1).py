import pygame
from pygame.locals import *
from sys import exit
import random as rd
import numpy as np

# Inicialização
pygame.init()
largura, altura = 600, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Mundo do Wumpus - Q-Learning')
fonte = pygame.font.SysFont('Rubik', 25)
clock = pygame.time.Clock()

# Cores
branco = (54, 54, 54)
verde = (50, 205, 50)

# Ambiente 4x4
matriz = np.empty((4, 4), dtype=object)
for i in range(4):
    for j in range(4):
        matriz[i][j] = []

# Direções (cima, direita, baixo, esquerda)
dx_dy = [(-1, 0), (0, 1), (1, 0), (0, -1)]
acoes = [0, 1, 2, 3]
Q = {}
alpha, gamma, epsilon = 0.1, 0.9, 0.2

# Posicionamento de itens
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

# Percepções
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

# Q-learning
recompensa_final = {}
def recompensa(l, c, pegou):
    if not (0 <= l < 4 and 0 <= c < 4): return -5
    if "Buraco" in matriz[l][c] or "Wumpus" in matriz[l][c]: return -100
    if "Ouro" in matriz[l][c] and not pegou: return 100
    if (l, c) == (0, 0) and pegou: return 200
    return -1

def mover(l, c, acao):
    dx, dy = dx_dy[acao]
    return l + dx, c + dy

for ep in range(2000):
    l, c = 0, 0
    pegou = False
    for _ in range(50):
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

# Política
def politica_q():
    caminho = []
    l, c, pegou = 0, 0, False
    for _ in range(100):
        estado = (l, c, pegou)
        if estado not in Q:
            break
        acao = max(Q[estado], key=Q[estado].get)
        caminho.append((l, c))
        l, c = mover(l, c, acao)
        if "Ouro" in matriz[l][c]:
            pegou = True
        if (l, c) == (0, 0) and pegou:
            caminho.append((l, c))
            break
    return caminho

trajetoria = politica_q()
passo = 0
linha_ag, col_ag = 0, 0
pegou_ouro = False

# Execução visual
while True:
    clock.tick(2)
    tela.fill((0, 0, 0))

    for i in range(5):
        pygame.draw.rect(tela, branco, (100 + i * 100, 100, 5, 400))
        pygame.draw.rect(tela, branco, (100, 100 + i * 100, 400, 5))

    pygame.draw.circle(tela, verde, (col_ag * 100 + 150, linha_ag * 100 + 150), 20)

    celula = matriz[linha_ag][col_ag]
    percepcoes = []
    if "Cheiro ruim" in celula: percepcoes.append("um cheiro ruim")
    if "Brisa" in celula: percepcoes.append("uma brisa")
    if "Ouro" in celula and not pegou_ouro: percepcoes.append("brilho")
    txt = "Voce sente " + " e ".join(percepcoes) + "!" if percepcoes else "Nao sente nada."
    tela.blit(fonte.render(txt, True, (255, 255, 255)), (20, 20))

    if passo < len(trajetoria):
        linha_ag, col_ag = trajetoria[passo]
        if "Ouro" in matriz[linha_ag][col_ag]: pegou_ouro = True
        passo += 1

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
