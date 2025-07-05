import random

class mundoWumpus:
  def __init__(self, tamanho=4):
    self.tamanho = tamanho
    self.agente_pos = [0, 0]
    self.vivo = True
    self.ouro = [2, 1]
    self.ouro_pego = False #ouro nao foi pego ainda
    self.wumpus = [2, 0]
    self.wumpus_vivo = True
    self.abismo = [[3, 3], [2, 2], [0, 2]]
    self.pontuacao = 0
    self.brisa = False
    self.fedor = False
    self.flecha = True
    self.reset()

  def atirar_flecha(self, direcao):
    if self.flecha:
      self.flecha = False
      if direcao == 0: #atirar embaixo
        if [self.agente_pos[0], self.agente_pos[1] - 1] == self.wumpus: #encontrou wumpus
          self.pontuacao += 50
          self.wumpus_vivo = False
          #print("O Wumpus é morto e solta um grito. Você recebeu 50 pontos!")
          return 10 #recompensa
      elif direcao == 1: #atirar esquerda
        if [self.agente_pos[0] - 1, self.agente_pos[1]] == self.wumpus: #encontrou wumpus
          self.pontuacao += 50
          self.wumpus_vivo = False
          #print("O Wumpus é morto e solta um grito. Você recebeu 50 pontos!")
          return 10 #recompensa
      elif direcao == 2: #atirar em cima
        if [self.agente_pos[0], self.agente_pos[1] + 1] == self.wumpus: #encontrou wumpus
          self.pontuacao += 50
          self.wumpus_vivo = False
          #print("O Wumpus é morto e solta um grito. Você recebeu 50 pontos!")
          return 10 #recompensa
      elif direcao == 3: #atirar direita
        if [self.agente_pos[0] + 1, self.agente_pos[1]] == self.wumpus: #encontrou wumpus
          self.pontuacao += 50
          self.wumpus_vivo = False
          #print("O Wumpus é morto e solta um grito. Você recebeu 50 pontos!")
          return 10 #recompensa
      return -10 #penalidade
    return -10 #penalidade por atirar sem flecha
  
  def reset(self):
    self.agente_pos = [0, 0]
    self.vivo = True
    self.ouro_pego = False
    self.wumpus_vivo = True
    ultima_pontuacao = self.pontuacao
    self.pontuacao = 0
    self.flecha = True
    self.brisa = False
    self.fedor = False
    return ultima_pontuacao

  def movimento_agente(self, direcao):
    self.pontuacao -= 1
    if direcao == 0: #embaixo
      y_novo = self.agente_pos[1] - 1
      if y_novo >= 0:
        self.agente_pos[1] = y_novo
      else:
        return tuple(self.agente_pos), -20 #penalidade por andar na parede
    elif direcao == 1: #esquerda
      x_novo = self.agente_pos[0] - 1
      if x_novo >= 0:
        self.agente_pos[0] = x_novo
      else:
        return tuple(self.agente_pos), -20 #penalidade por andar na parede
    elif direcao == 2: #cima
      y_novo = self.agente_pos[1] + 1
      if y_novo <= 3:
        self.agente_pos[1] = y_novo
      else:
        return tuple(self.agente_pos), -20 #penalidade por andar na parede
    elif direcao == 3: #direita
      x_novo = self.agente_pos[0] + 1
      if x_novo <= 3:
        self.agente_pos[0] = x_novo
      else:
        return tuple(self.agente_pos), -20 #penalidade por andar na parede
    
    #se nao for parede:
    if self.agente_pos == self.ouro:
      #print("Você pegou o ouro")
      self.ouro_pego = True
      return self.agente_pos, 10 #recompensa

    elif self.agente_pos == self.wumpus or self.agente_pos == self.abismo[0] or self.agente_pos == self.abismo[1] or self.agente_pos == self.abismo[2]:
      self.vivo = False
      self.pontuacao -= 100
      #print("Você morreu. Menos 100 pontos")
      return self.agente_pos, -10 #penalidade
    
    for i in range(3):
      if [self.agente_pos[0] - 1, self.agente_pos[1]] == self.abismo[i] or [self.agente_pos[0] + 1, self.agente_pos[1]] == self.abismo[i] or [self.agente_pos[0], self.agente_pos[1] - 1] == self.abismo[i] or [self.agente_pos[0], self.agente_pos[1] + 1] == self.abismo[i]:
        self.brisa = True

    if [self.agente_pos[0] - 1, self.agente_pos[1]] == self.wumpus or [self.agente_pos[0] + 1, self.agente_pos[1]] == self.wumpus or [self.agente_pos[0], self.agente_pos[1] - 1] == self.wumpus or [self.agente_pos[0], self.agente_pos[1] + 1] == self.wumpus:
      self.fedor = True
    return self.agente_pos, 0 #recompensa normal



tabuleiro = mundoWumpus()


class qLearningAgente:
  def __init__(self, alpha=1, gamma=0.99, epsilon=1):
    self.q = {}
    self.alpha = alpha
    self.gamma = gamma
    self.epsilon = epsilon
    self.record=list()

  def get_q(self,estado,acao):
    return self.q.get((estado, acao), 0.0)
  
  def escolha_acao(self, estado):
    if self.epsilon > random.random(): #acao aleatoria
      return random.choice(range(8))
    else: #acao com base na tabela Q
      lista_q = [self.get_q(estado, a) for a in range(8)]
      max_q = max(lista_q)
      best = [a for a, q in enumerate(lista_q) if q == max_q]
      return random.choice(best)

  def atualizar(self, estado, acao, recompensa, prox_estado):
    max_q_next = max([self.get_q(prox_estado, a) for a in range(8)])
    self.q[(estado, acao)] = self.get_q(estado, acao) + self.alpha * (recompensa + self.gamma * max_q_next - self.get_q(estado, acao))

def treino(agente, tabuleiro, episodios=1000): #1000 EPISODIOS
  for ep in range(episodios):
    agente.epsilon = max(0.1, agente.epsilon * 0.995)  # decaimento
    while tabuleiro.vivo and not tabuleiro.ouro_pego:
      estado = (
        tabuleiro.agente_pos[0],
        tabuleiro.agente_pos[1],
        int(tabuleiro.wumpus_vivo),
        int(tabuleiro.ouro_pego),
        int(tabuleiro.flecha)
      )
      acao = agente.escolha_acao(estado)

      if acao < 4: #movimento
        prox_estado, recompensa = tabuleiro.movimento_agente(acao)
      else: #atira flecha
        recompensa = tabuleiro.atirar_flecha(acao-4)
      prox_estado = (
        tabuleiro.agente_pos[0],
        tabuleiro.agente_pos[1],
        int(tabuleiro.wumpus_vivo),
        int(tabuleiro.ouro_pego),
        int(tabuleiro.flecha)
      )
      agente.atualizar(estado, acao, recompensa, prox_estado)
    tabuleiro.reset()


'''
Após o treinamento, o agente pode usar a tabela Q para determinar a
política ótima, ou seja, a melhor ação a ser tomada em cada estado.
• A política ótima é geralmente determinada selecionando a ação com o
maior valor Q em cada estado.
'''

def imprimir_caminho_numerado(tabuleiro, caminho_acoes):
    grid = [["" for _ in range(tabuleiro.tamanho)] for _ in range(tabuleiro.tamanho)]

    for passo, (x, y) in enumerate(caminho_acoes):
        if grid[x][y] == "":
            grid[x][y] = str(passo)
        else:
            grid[x][y] += f",{passo}"  # empilha os passos, ex: "3,6"

    # Marcar elementos do mundo se a célula ainda está vazia
    ox, oy = tabuleiro.ouro
    if grid[ox][oy] == "":
        grid[ox][oy] = "O"
    
    if tabuleiro.wumpus_vivo:
        wx, wy = tabuleiro.wumpus
        if grid[wx][wy] == "":
            grid[wx][wy] = "W"

    for ax, ay in tabuleiro.abismo:
        if grid[ax][ay] == "":
            grid[ax][ay] = "A"

    print("\nTabuleiro (caminho da política final):")
    for linha in reversed(grid):
        print(" ".join(cell.rjust(4) if cell else "   ." for cell in linha))


def executar_politica_final(agente, tabuleiro):
    agente.epsilon = 0  # Exploração desligada
    tabuleiro.reset()
    caminho = [tuple(tabuleiro.agente_pos)]

    while tabuleiro.vivo and not tabuleiro.ouro_pego:
        estado = (
            tabuleiro.agente_pos[0],
            tabuleiro.agente_pos[1],
            int(tabuleiro.wumpus_vivo),
            int(tabuleiro.ouro_pego),
            int(tabuleiro.flecha)
        )
        acao = agente.escolha_acao(estado)

        if acao < 4:
            prox_estado, _ = tabuleiro.movimento_agente(acao)
        else:
            _ = tabuleiro.atirar_flecha(acao - 4)
            prox_estado = tuple(tabuleiro.agente_pos)

        if tuple(tabuleiro.agente_pos) != caminho[-1]:
            caminho.append(tuple(tabuleiro.agente_pos))

    imprimir_caminho_numerado(tabuleiro, caminho)



if __name__ == '__main__':
  tabuleiro = mundoWumpus()
  agente = qLearningAgente()
  treino(agente, tabuleiro)
  executar_politica_final(agente, tabuleiro)