import numpy as np
import random

# Definições do ambiente
ACTIONS = ['cima', 'baixo', 'esquerda', 'direita']
NUM_EPISODIOS = 10000
ALPHA = 0.1  # Taxa de aprendizado
GAMMA = 0.99 # Fator de desconto

# Epsilon (exploração) com decaimento
epsilon_inicial = 1.0
epsilon_min = 0.01
taxa_decaimento = 0.0005

# --- FUNÇÃO MODIFICADA PARA CRIAR UM TABULEIRO FIXO ---
def criar_caverna_fixa():
    """
    Cria sempre a mesma caverna para que o treinamento seja consistente.
    """
    caverna = np.zeros((4,4), dtype=int)
    # Valores: 0:Vazio, 2:Fedor, 3:Wumpus, 4:Brisa, 5:Buraco, 10:Ouro

    # --- Posições Fixas ---
    pos_wumpus = (1, 2)
    pos_ouro = (3, 3)
    pos_buracos = [(0, 2), (2, 1), (2, 3)]
    
    # Adiciona Buracos e Brisa ao redor deles
    for b in pos_buracos:
        caverna[b] = 5 # Buraco
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = b[0]+di, b[1]+dj
            if 0 <= ni < 4 and 0 <= nj < 4 and caverna[ni,nj]==0:
                caverna[ni,nj] = 4 # Brisa
                
    # Adiciona Wumpus e Fedor ao redor
    caverna[pos_wumpus] = 3 # Wumpus
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = pos_wumpus[0]+di, pos_wumpus[1]+dj
        if 0 <= ni < 4 and 0 <= nj < 4 and caverna[ni,nj]==0:
            caverna[ni,nj] = 2 # Fedor
            
    # Adiciona Ouro
    caverna[pos_ouro] = 10 # Ouro
    return caverna

# Movimentação
def mover(pos, acao):
    i,j = pos
    if acao == 'cima' and i>0: return (i-1,j)
    if acao == 'baixo' and i<3: return (i+1,j)
    if acao == 'esquerda' and j>0: return (i,j-1)
    if acao == 'direita' and j<3: return (i,j+1)
    return pos  # Bateu na parede, fica no mesmo lugar

# Recompensa
def recompensa(caverna, pos):
    celula = caverna[pos]
    if celula == 10: return 50, True, "IA encontrou o ouro!"
    if celula == 3: return -100, True, "IA foi devorada pelo Wumpus!"
    if celula == 5: return -100, True, "IA caiu no buraco!"
    return -1, False, "" # Custo de -1 por movimento para incentivar caminhos curtos

# Inicialização da Tabela-Q
Q = {}
for i in range(4):
    for j in range(4):
        Q[(i,j)] = {a: 0.0 for a in ACTIONS}

# --- TREINAMENTO ---
print("Iniciando treinamento da IA no tabuleiro fixo...")
epsilon = epsilon_inicial
for episodio in range(NUM_EPISODIOS):
    # Usa a função que cria a caverna fixa em todos os episódios
    caverna = criar_caverna_fixa()
    pos = (0,0)
    fim = False
    
    while not fim:
        # Escolha da ação (Epsilon-Greedy)
        if random.uniform(0,1) < epsilon:
            acao = random.choice(ACTIONS)
        else:
            acao = max(Q[pos], key=Q[pos].get)
        
        nova_pos = mover(pos, acao)
        r, fim, aviso = recompensa(caverna, nova_pos)
        
        # ATUALIZAÇÃO DO Q-LEARNING
        if fim:
            maxQ_next = 0
        else:
            maxQ_next = max(Q[nova_pos].values())
        
        Q[pos][acao] += ALPHA * (r + GAMMA * maxQ_next - Q[pos][acao])
        
        pos = nova_pos

    # Decaimento do Epsilon
    epsilon = epsilon_min + (epsilon_inicial - epsilon_min) * np.exp(-taxa_decaimento*episodio)

print("Treinamento concluído!")

# --- TESTE PÓS-TREINAMENTO ---
print("\n--- Executando episódio de teste com a IA treinada no tabuleiro fixo ---")
caverna_teste = criar_caverna_fixa()
pos = (0,0)
fim = False
passos = 0

while not fim and passos < 20: # Limite de 20 passos
    acao = max(Q[pos], key=Q[pos].get)
    nova_pos = mover(pos, acao)
    
    r, fim, aviso = recompensa(caverna_teste, nova_pos)
    
    celula = caverna_teste[nova_pos]
    percepcoes = []
    if celula == 2: percepcoes.append("Sentiu um fedor!")
    if celula == 4: percepcoes.append("Sentiu uma brisa!")
    
    print(f"Passo {passos+1}: Posição: {pos} -> Ação: {acao} -> Nova Posição: {nova_pos}, Recompensa: {r}")
    for percep in percepcoes:
        print(f"  > {percep}")
    if aviso:
        print(f"  > {aviso}")
        
    pos = nova_pos
    passos += 1

if not fim:
    print("\nA IA não atingiu um objetivo em 20 passos.")

# Berton, L. (s.d.). *Aula 17 - Aprendizado por reforço* [Apresentação de slides]. UNIFESP.

# https://numpy.org/devdocs/user/quickstart.html
# https://panda.ime.usp.br/cc110/static/cc110/12-matrizes.html
# https://www.dio.me/articles/gerar-numero-int-aleatorio-python
# aula de algoritmos e bioinformatica prof martini
# chat gpt