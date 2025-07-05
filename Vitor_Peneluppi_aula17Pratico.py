#O Mundo de Wumpus

from typing import List
import random
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
import pandas as pd

def Header():
        #Para referência
        """
        OURO = 0
        WUMPUS = 1
        BURACO = 2
        FEDOR = 3
        BRISA = 4
        INDICE TABELA = 5
        """
        
class Jogador:
    def __init__(self):
        self.flecha = 1
        self.ouro = 0
        self.pos = [3,0] #Equivalente a (0,0) do exemplo no PDF

def PrintTab(Tab):
      for linha in Tab:
           print(linha)
            
def ColocaBuracos(Tab, tam: int, dif: int):
    for i in range(dif):
        item = 2 #Buraco
        conflito = True
        posx = random.randrange(tam)
        posy = random.randrange(tam)

        while posx == tam-1 and posy == 0:
            posx = random.randrange(tam)
            posy = random.randrange(tam)

        while(conflito):
            if Tab[posx][posy][item] != 1:
                Tab[posx][posy][item] = 1
                conflito = False
            else:
                posx = random.randrange(tam)
                posy = random.randrange(tam)

        item = 4 #Brisa

        if posx > 0:
            Tab[posx-1][posy][item] = 1
        if posx < tam-1:
            Tab[posx+1][posy][item] = 1
        if posy > 0:
            Tab[posx][posy-1][item] = 1
        if posy < tam-1:
            Tab[posx][posy+1][item] = 1

def ColocaWumpus(Tab, tam: int):
        item = 1 #Wumpus
        conflito = True
        posx = random.randrange(tam)
        posy = random.randrange(tam)

        while posx == tam-1 and posy == 0:
            posx = random.randrange(tam)
            posy = random.randrange(tam)

        while(conflito):
            if Tab[posx][posy][2] != 1:
                Tab[posx][posy][item] = 1
                conflito = False
            else:
                posx = random.randrange(tam)
                posy = random.randrange(tam)

        item = 3 #Fedor

        if posx > 0:
            Tab[posx-1][posy][item] = 1
        if posx < tam-1:
            Tab[posx+1][posy][item] = 1
        if posy > 0:
            Tab[posx][posy-1][item] = 1
        if posy < tam-1:
            Tab[posx][posy+1][item] = 1

def ColocaOuro(Tab, tam: int):
    item = 0 #Ouro
    conflito = True
    posx = random.randrange(tam)
    posy = random.randrange(tam)

    while(conflito):
        if Tab[posx][posy][2] != 1 and Tab[posx][posy][1] != 1:
            Tab[posx][posy][item] = 1
            conflito = False
        else:
            posx = random.randrange(tam)
            posy = random.randrange(tam)

    return (posx, posy, Tab[posx][posy][5])

def Jogo_Q_learning(Tab, tam: int, jog, goal):
    n_states = tam * tam
    n_actions = 8
    learning_rate = 0.8
    discount_factor = 0.95
    exploration_prob = 0.2
    epochs = 1000
    Q_table = np.zeros((n_states, n_actions))
    
    # Guarda a posição original do Wumpus para reiniciá-lo
    wumpus_pos = None
    for i in range(tam):
        for j in range(tam):
            if Tab[i][j][1] == 1:
                wumpus_pos = (i, j)
                break
        if wumpus_pos:
            break

    Actions = {
        0: (-1, 0),  # move cima
        1: (1, 0),   # move baixo
        2: (0, -1),  # move esquerda
        3: (0, 1),   # move direita
        4: (-1, 0),  # atira cima
        5: (1, 0),   # atira baixo
        6: (0, -1),  # atira esquerda
        7: (0, 1)    # atira direita
    }

    for epoch in range(epochs):
        current_Tab = [row[:] for row in Tab]
        
        pos = [tam - 1, 0]
        current_state = current_Tab[pos[0]][pos[1]][5]
        ouro_pego = False
        flecha = 1
        wumpus_vivo = True
        points = 0
        highscore = [0, 0]
        done = False

        while not done:
            if np.random.rand() < exploration_prob:
                action = np.random.randint(0, n_actions)
            else:
                action = np.argmax(Q_table[current_state])

            reward = -1  # penalidade de movimento

            if action in range(0, 4):
                dx, dy = Actions[action]
                new_x, new_y = pos[0] + dx, pos[1] + dy

                if 0 <= new_x < tam and 0 <= new_y < tam:
                    next_pos = [new_x, new_y]
                else:
                    next_pos = pos

                next_state = current_Tab[next_pos[0]][next_pos[1]][5]

                if current_Tab[next_pos[0]][next_pos[1]][2] == 1:  # Buraco
                    reward = -100
                    done = True
                elif current_Tab[next_pos[0]][next_pos[1]][1] == 1 and wumpus_vivo:  # Wumpus vivo
                    reward = -100
                    done = True
                elif current_Tab[next_pos[0]][next_pos[1]][0] == 1 and not ouro_pego:  # Ouro
                    reward = 50
                    ouro_pego = True
                elif ouro_pego and next_pos == [tam - 1, 0]:  # Vitória
                    reward = 100
                    done = True

                points += reward
                Q_table[current_state, action] += learning_rate * (
                    reward + discount_factor * np.max(Q_table[next_state]) - Q_table[current_state, action])
                pos = next_pos
                current_state = next_state

            elif action in range(4, 8) and flecha == 1:  # Atirar
                dx, dy = Actions[action]
                shoot_x, shoot_y = pos[0] + dx, pos[1] + dy
                flecha = 0

                if 0 <= shoot_x < tam and 0 <= shoot_y < tam:
                    if current_Tab[shoot_x][shoot_y][1] == 1:  
                        current_Tab[shoot_x][shoot_y][1] = 0
                        wumpus_vivo = False
                        reward = 50
                    else:
                        reward = -5
                else:
                    reward = -10

                points += reward
                Q_table[current_state, action] += learning_rate * (reward - Q_table[current_state, action])

            else:  # Sem flechas
                reward = -10
                points += reward
                Q_table[current_state, action] += learning_rate * (reward - Q_table[current_state, action])
    
        print(f"Tentativa {epoch+1}, pontuação: {points}")
        if points >= highscore[1]:
            highscore = [epoch, points]
    
    print(f"\nMelhor tentativa: {highscore[0]} com {highscore[1]} pontos\n\nTabuleiro:\n")
    print("Legenda:", Header.__doc__)
    PrintTab(Tab)
    Mostrar_QTable(Q_table)

def Mostrar_QTable(Q_table):
    action_labels = [0, 1, 2, 3, 4, 5, 6, 7]

    tam = int(np.sqrt(Q_table.shape[0]))
    q_values_grid = np.max(Q_table, axis=1).reshape((tam, tam))

    plt.figure(figsize=(6, 6))
    plt.imshow(q_values_grid, cmap='coolwarm', interpolation='nearest')
    plt.colorbar(label='Q-value')
    plt.title('Valores Q máximos por estado')
    plt.xticks(np.arange(tam), [str(i) for i in range(tam)])
    plt.yticks(np.arange(tam), [str(i) for i in range(tam)])
    plt.gca().invert_yaxis()
    plt.grid(True)

    for i in range(tam):
        for j in range(tam):
            plt.text(j, i, f'{q_values_grid[i, j]:.2f}', ha='center', va='center', color='black')

    plt.show()

    df_qtable = pd.DataFrame(Q_table, columns=action_labels)
    print("\nQ-table:\n")
    print(df_qtable.round(2))


def main():
    Jog = Jogador()
    Tab = []
    Tam_tab = 4
    Dificuldade = 1
    num = 0
    for i in range(Tam_tab):

        linha = []

        for j in range(Tam_tab):

            val = [0,0,0,0,0,num]
            linha.append(val)
            num += 1
        Tab.append(linha)
     
    ColocaBuracos(Tab, Tam_tab, Dificuldade+1)
    ColocaWumpus(Tab, Tam_tab)
    pos_ouro = ColocaOuro(Tab, Tam_tab)
    Jogo_Q_learning(Tab, Tam_tab, Jog, pos_ouro)

main()

#   Fontes:
#        https://www-geeksforgeeks-org.translate.goog/q-learning-in-python/?_x_tr_sl=en&_x_tr_tl=pt&_x_tr_hl=pt&_x_tr_pto=tc
#        https://matplotlib.org/stable/tutorials/pyplot.html
#        Slides da aula