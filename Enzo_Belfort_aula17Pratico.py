import random
import os
import time
import numpy as np
import pickle
from collections import deque, defaultdict

def limpar_tela():
    """Limpa a tela do console para melhor visualização"""
    # Comando para Windows
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def criar_mapa():
    """Cria o mapa do jogo com Wumpus, buracos e ouro posicionados aleatoriamente"""
    mapa = [['.' for _ in range(4)] for _ in range(4)]
    
    # Posiciona o agente na entrada (canto superior esquerdo)
    mapa[0][0] = "A"  
    
    # Posiciona o Wumpus aleatoriamente (evitando a posição do agente)
    linha_wumpus = random.randint(0, 3)
    coluna_wumpus = random.randint(0, 3)
    while linha_wumpus == 0 and coluna_wumpus == 0:
        linha_wumpus = random.randint(0, 3)
        coluna_wumpus = random.randint(0, 3)
    mapa[linha_wumpus][coluna_wumpus] = "W"  
    
    # Posiciona 3 buracos aleatoriamente (evitando o agente e o Wumpus)
    for _ in range(3):
        linha_buraco = random.randint(0, 3)
        coluna_buraco = random.randint(0, 3)
        while (linha_buraco == 0 and coluna_buraco == 0) or \
              mapa[linha_buraco][coluna_buraco] != '.':
            linha_buraco = random.randint(0, 3)
            coluna_buraco = random.randint(0, 3)
        mapa[linha_buraco][coluna_buraco] = "B"  
    
    # Posiciona o ouro aleatoriamente (evitando o agente, o Wumpus e os buracos)
    linha_ouro = random.randint(0, 3)
    coluna_ouro = random.randint(0, 3)
    while (linha_ouro == 0 and coluna_ouro == 0) or \
          mapa[linha_ouro][coluna_ouro] != '.':
        linha_ouro = random.randint(0, 3)
        coluna_ouro = random.randint(0, 3)
    mapa[linha_ouro][coluna_ouro] = "O" 
    
    return mapa

def marcar_percepcoes(mapa):
    """Marca as percepções em cada célula baseada nos elementos do mapa"""
    percepcoes = [[[] for _ in range(4)] for _ in range(4)]
    
    # Direções adjacentes (norte, leste, sul, oeste)
    direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    for i in range(4):
        for j in range(4):
            # Se for Wumpus, marca fedor nas células adjacentes
            if mapa[i][j] == "W":
                for di, dj in direcoes:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4:
                        if "fedor" not in percepcoes[ni][nj]:
                            percepcoes[ni][nj].append("fedor")
            
            # Se for buraco, marca brisa nas células adjacentes
            elif mapa[i][j] == "B":
                for di, dj in direcoes:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4:
                         if "brisa" not in percepcoes[ni][nj]:
                            percepcoes[ni][nj].append("brisa")
            
            # Se for ouro, marca brilho na mesma célula
            elif mapa[i][j] == "O":
                 if "brilho" not in percepcoes[i][j]:
                    percepcoes[i][j].append("brilho")
    
    return percepcoes

def exibir_mapa_debug(mapa):
    """Exibe o mapa completo para debug (todas as posições visíveis)"""
    print("\n----- MAPA DEBUG -----")
    print("  1 2 3 4")  # Adiciona numeração de colunas
    for i, linha in enumerate(mapa):
        print(f"{i+1} {' '.join(linha)}")
    print("---------------------\n")

def exibir_mapa_jogador(mapa, percepcoes, pos_jogador, visitadas):
    """Exibe o mapa como o jogador vê - apenas células visitadas"""
    print("\n----- MAPA VISÍVEL -----")
    print("  1 2 3 4")  # Adiciona numeração de colunas
    for i in range(4):
        linha = []
        linha.append(f"{i+1}")  # Adiciona numeração de linhas
        for j in range(4):
            if (i, j) in visitadas:
                if (i, j) == pos_jogador:
                    # Mostra o agente com uma seta indicando a direção
                    linha.append('A')
                else:
                    celula = mapa[i][j]
                    # Não mostra os perigos nas células visitadas, apenas passagens seguras ou ouro
                    if celula == 'W' or celula == 'B':
                        linha.append('.')
                    else:
                        linha.append(celula)
            else:
                linha.append('?')
        print(' '.join(linha))
    print("------------------------\n")

def exibir_ajuda():
    """Exibe instruções detalhadas de como jogar"""
    print("\n===== AJUDA - MUNDO DE WUMPUS =====")
    print("Comandos disponíveis:")
    print("- 'cima': move uma casa na direção que está olhando")
    print("- 'dir': vira 90 graus à direita")
    print("- 'esq': vira 90 graus à esquerda")
    print("- 'atirar': atira a flecha na direção que está olhando")
    print("- 'pegar': pega o ouro se estiver na mesma casa")
    print("- 'escalar': sai da caverna na posição [1,1] (apenas com o ouro)")
    print("- 'mapa': mostra o mapa visível")
    print("- 'ajuda': mostra esta mensagem de ajuda")
    print("- 'sair': encerra o jogo")
    print("\nObjetivo: Encontrar o ouro e retornar à posição [1,1] para escapar")
    print("Perigos: Evite o Wumpus (você percebe fedor nas casas adjacentes)")
    print("         Evite buracos (você percebe brisa nas casas adjacentes)")
    print("==================================\n")

def obter_direcao_simbolo(direcao):
    """Retorna um símbolo para representar a direção em que o agente está olhando"""
    if direcao == 'norte':
        return '↑'
    elif direcao == 'leste':
        return '→'
    elif direcao == 'sul':
        return '↓'
    elif direcao == 'oeste':
        return '←'

def obter_proxima_posicao(pos_atual, direcao):
    """Calcula a próxima posição com base na posição atual e direção"""
    i, j = pos_atual
    if direcao == 'norte' and i > 0:
        return (i-1, j)
    elif direcao == 'sul' and i < 3:
        return (i+1, j)
    elif direcao == 'leste' and j < 3:
        return (i, j+1)
    elif direcao == 'oeste' and j > 0:
        return (i, j-1)
    return None  # Retorna None se a próxima posição seria fora do mapa

def virar_direcao(direcao_atual, para_onde):
    """Retorna a nova direção após virar para esquerda ou direita"""
    direcoes = ['norte', 'leste', 'sul', 'oeste']
    idx = direcoes.index(direcao_atual)
    
    if para_onde == 'dir':
        return direcoes[(idx + 1) % 4]
    elif para_onde == 'esq':
        return direcoes[(idx - 1) % 4]
    return direcao_atual

def calcular_direcao(pos_atual, pos_destino):
    """Calcula a direção para ir da posição atual para a posição destino"""
    i_atual, j_atual = pos_atual
    i_destino, j_destino = pos_destino
    
    if i_atual > i_destino:
        return 'norte'
    elif i_atual < i_destino:
        return 'sul'
    elif j_atual > j_destino:
        return 'oeste'
    elif j_atual < j_destino:
        return 'leste'
    return None

def virar_para_direcao(direcao_atual, direcao_desejada):
    """Retorna uma sequência de comandos para virar da direção atual para a desejada"""
    direcoes = ['norte', 'leste', 'sul', 'oeste']
    idx_atual = direcoes.index(direcao_atual)
    idx_desejada = direcoes.index(direcao_desejada)
    
    # Calcula o número de viradas necessárias (0, 1, 2 ou 3)
    diff = (idx_desejada - idx_atual) % 4
    
    if diff == 0:
        return []  # Já está na direção desejada
    elif diff == 1:
        return ['dir']  # Uma virada à direita
    elif diff == 2:
        return ['dir', 'dir']  # Duas viradas (180 graus)
    else:  # diff == 3
        return ['esq']  # Uma virada à esquerda
    
class AgenteInteligente:
    """Classe que implementa um agente inteligente para o Mundo de Wumpus"""
    
    def __init__(self, mapa, percepcoes):
        self.conhecimento = [[None for _ in range(4)] for _ in range(4)]  # Conhecimento do agente sobre o mapa
        self.seguras = set()  # Células que o agente sabe que são seguras
        self.perigosas = set()  # Células que o agente sabe que são perigosas (Wumpus ou buraco)
        self.fedores = set()  # Células onde o agente sentiu fedor
        self.brisas = set()  # Células onde o agente sentiu brisa
        self.visitadas = {(0, 0)}  # Células que o agente já visitou
        self.pos_wumpus = None  # Posição do Wumpus, se descoberta
        self.wumpus_vivo = True  # Estado do Wumpus
        self.ouro_encontrado = False  # Se o ouro foi encontrado
        self.ouro_coletado = False  # Se o ouro foi coletado
        self.pos_ouro = None  # Posição do ouro, se descoberta
        self.caminho_atual = []  # Caminho atual para seguir
        self.fronteira = set()  # Células na fronteira de exploração
        self.pos_atual = (0, 0)  # Posição atual do agente
        self.direcao_atual = 'leste'  # Direção atual do agente
        self.tem_flecha = True  # Se o agente ainda tem a flecha
        self.mapa_real = mapa  # O mapa real (usado para debug)
        self.percepcoes_reais = percepcoes  # As percepções reais (usado para simulação)
        
        # Inicializa a célula inicial como segura
        self.conhecimento[0][0] = '.'
        self.seguras.add((0, 0))
        self.atualizar_fronteira()
        
    def atualizar_fronteira(self):
        """Atualiza o conjunto de células de fronteira (células adjacentes às visitadas)"""
        direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for i, j in self.visitadas:
            for di, dj in direcoes:
                ni, nj = i + di, j + dj
                if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) not in self.visitadas:
                    self.fronteira.add((ni, nj))
    
    def inferir_celulas_seguras(self):
        """Infere células seguras baseado nas percepções"""
        # Se uma célula visitada não tem fedor nem brisa, todas as células adjacentes são seguras
        direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for i, j in self.visitadas:
            if (i, j) not in self.fedores and (i, j) not in self.brisas:
                for di, dj in direcoes:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4:
                        self.seguras.add((ni, nj))
                        if self.conhecimento[ni][nj] is None:
                            self.conhecimento[ni][nj] = '.'
        
        # Remove células seguras da lista de perigosas
        self.perigosas -= self.seguras
    
    def inferir_celulas_perigosas(self):
        """Infere células perigosas baseado nas percepções"""
        # Se uma célula tem fedor ou brisa, células adjacentes não visitadas são potencialmente perigosas
        direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # A partir dos fedores
        for i, j in self.fedores:
            for di, dj in direcoes:
                ni, nj = i + di, j + dj
                if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) not in self.visitadas:
                    self.perigosas.add((ni, nj))
        
        # A partir das brisas
        for i, j in self.brisas:
            for di, dj in direcoes:
                ni, nj = i + di, j + dj
                if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) not in self.visitadas:
                    self.perigosas.add((ni, nj))
        
        # Remove células seguras da lista de perigosas
        self.perigosas -= self.seguras
    
    def localizar_wumpus(self):
        """Tenta localizar o Wumpus baseado nos fedores"""
        if self.pos_wumpus or not self.wumpus_vivo:
            return
        
        direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        candidatos_wumpus = set()
        
        # Para cada célula com fedor, adicione as células adjacentes como possíveis localizações do Wumpus
        for fedor_i, fedor_j in self.fedores:
            if not candidatos_wumpus:  # Primeiro fedor, todas as células adjacentes são candidatas
                for di, dj in direcoes:
                    ni, nj = fedor_i + di, fedor_j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) not in self.visitadas:
                        candidatos_wumpus.add((ni, nj))
            else:  # Intersecção com candidatos anteriores
                candidatos_atuais = set()
                for di, dj in direcoes:
                    ni, nj = fedor_i + di, fedor_j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) not in self.visitadas:
                        candidatos_atuais.add((ni, nj))
                
                candidatos_wumpus &= candidatos_atuais
                
        # Se sobrar apenas um candidato, o Wumpus está localizado
        if len(candidatos_wumpus) == 1:
            self.pos_wumpus = list(candidatos_wumpus)[0]
            return True
        
        return False
    
    def deve_atirar(self):
        """Decide se o agente deve atirar baseado na localização do Wumpus e no estado da flecha"""
        if not self.tem_flecha or not self.wumpus_vivo or not self.pos_wumpus:
            return False
        
        # Verifica se o Wumpus está na mesma linha ou coluna que o agente
        i, j = self.pos_atual
        wi, wj = self.pos_wumpus
        
        if i == wi:  # Mesma linha
            if j < wj and self.direcao_atual == 'leste':
                return True
            elif j > wj and self.direcao_atual == 'oeste':
                return True
        elif j == wj:  # Mesma coluna
            if i < wi and self.direcao_atual == 'sul':
                return True
            elif i > wi and self.direcao_atual == 'norte':
                return True
        
        return False
    
    def encontrar_caminho_seguro(self, destino):
        """Encontra um caminho seguro da posição atual até o destino usando BFS"""
        if destino == self.pos_atual:
            return []
        
        fila = deque([(self.pos_atual, [])])  # (posição, caminho)
        visitados = {self.pos_atual}
        
        while fila:
            pos, caminho = fila.popleft()
            
            if pos == destino:
                return caminho
            
            # Explora os vizinhos
            for di, dj in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                ni, nj = pos[0] + di, pos[1] + dj
                nova_pos = (ni, nj)
                
                if (0 <= ni < 4 and 0 <= nj < 4 and 
                    nova_pos not in visitados and 
                    (nova_pos in self.seguras or nova_pos == destino)):
                    novo_caminho = caminho + [nova_pos]
                    visitados.add(nova_pos)
                    fila.append((nova_pos, novo_caminho))
        
        return None  # Não há caminho seguro
    
    def encontrar_celula_segura_nao_visitada(self):
        """Encontra uma célula segura não visitada para explorar"""
        for i in range(4):
            for j in range(4):
                if (i, j) in self.seguras and (i, j) not in self.visitadas:
                    return (i, j)
        return None
    
    def decidir_proxima_acao(self):
        """Decide a próxima ação do agente baseado no conhecimento atual"""
        # 1. Se tiver ouro na posição atual, pegue-o
        if self.pos_ouro == self.pos_atual and not self.ouro_coletado:
            return "pegar"
        
        # 2. Se tiver o ouro e estiver na posição inicial, saia
        if self.ouro_coletado and self.pos_atual == (0, 0):
            return "escalar"
        
        # 3. Se souber onde está o Wumpus e puder atirar, atire
        if self.deve_atirar():
            return "atirar"
        
        # 4. Se tiver um caminho atual a seguir, siga-o
        if self.caminho_atual:
            prox_pos = self.caminho_atual[0]
            direcao_desejada = calcular_direcao(self.pos_atual, prox_pos)
            
            if direcao_desejada != self.direcao_atual:
                # Precisa virar antes de mover
                comandos_virar = virar_para_direcao(self.direcao_atual, direcao_desejada)
                if comandos_virar:
                    return comandos_virar[0]  # 'dir' ou 'esq'
            else:
                # Já está na direção certa, pode mover
                self.caminho_atual.pop(0)  # Remove a primeira posição do caminho
                return "cima"
        
        # 5. Se tiver o ouro, encontre caminho de volta para a entrada
        if self.ouro_coletado:
            caminho = self.encontrar_caminho_seguro((0, 0))
            if caminho:
                self.caminho_atual = caminho
                return self.decidir_proxima_acao()
        
        # 6. Se não tiver o ouro e souber onde está, vá buscá-lo
        if self.pos_ouro and not self.ouro_coletado:
            caminho = self.encontrar_caminho_seguro(self.pos_ouro)
            if caminho:
                self.caminho_atual = caminho
                return self.decidir_proxima_acao()
        
        # 7. Explorar uma célula segura não visitada
        proxima_celula = self.encontrar_celula_segura_nao_visitada()
        if proxima_celula:
            caminho = self.encontrar_caminho_seguro(proxima_celula)
            if caminho:
                self.caminho_atual = caminho
                return self.decidir_proxima_acao()
        
        # 8. Se estiver cercado por células perigosas ou não tiver mais células seguras para explorar
        # tente encontrar uma célula menos perigosa para explorar (heurística)
        if (not proxima_celula) and self.fronteira:
            # Escolhe a célula da fronteira com menos percepções de perigo adjacentes
            menor_perigo = float('inf')
            melhor_celula = None
            
            for celula in self.fronteira:
                if celula in self.perigosas:
                    continue
                
                i, j = celula
                perigo = 0
                
                # Verifica percepções nas células adjacentes que já foram visitadas
                for di, dj in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4 and (ni, nj) in self.visitadas:
                        if (ni, nj) in self.fedores:
                            perigo += 1
                        if (ni, nj) in self.brisas:
                            perigo += 1
                
                if perigo < menor_perigo:
                    menor_perigo = perigo
                    melhor_celula = celula
            
            if melhor_celula:
                caminho = self.encontrar_caminho_seguro(melhor_celula)
                if caminho:
                    self.caminho_atual = caminho
                    return self.decidir_proxima_acao()
        
        # 9. Se não encontrou nenhuma ação útil, volte para a entrada
        if self.pos_atual != (0, 0):
            caminho = self.encontrar_caminho_seguro((0, 0))
            if caminho:
                self.caminho_atual = caminho
                return self.decidir_proxima_acao()
        
        # 10. Sem mais ações possíveis
        return "sem_acao"
    
    def atualizar_conhecimento(self, percepcoes_atuais):
        """Atualiza o conhecimento do agente baseado nas percepções atuais"""
        i, j = self.pos_atual
        
        # Atualiza o conhecimento sobre a célula atual
        self.conhecimento[i][j] = '.'
        self.seguras.add((i, j))
        self.visitadas.add((i, j))
        
        # Remove da fronteira
        if (i, j) in self.fronteira:
            self.fronteira.remove((i, j))
        
        # Atualiza percepções
        if "fedor" in percepcoes_atuais:
            self.fedores.add((i, j))
        
        if "brisa" in percepcoes_atuais:
            self.brisas.add((i, j))
        
        if "brilho" in percepcoes_atuais:
            self.pos_ouro = (i, j)
            self.ouro_encontrado = True
        
        # Infere células seguras e perigosas
        self.inferir_celulas_seguras()
        self.inferir_celulas_perigosas()
        
        # Atualiza a fronteira
        self.atualizar_fronteira()
        
        # Tenta localizar o Wumpus
        self.localizar_wumpus()
    
    def exibir_conhecimento(self):
        """Exibe o conhecimento atual do agente (para debug)"""
        print("\n----- CONHECIMENTO DO AGENTE -----")
        print("  1 2 3 4")
        for i in range(4):
            linha = [f"{i+1}"]
            for j in range(4):
                if (i, j) == self.pos_atual:
                    linha.append('A')
                elif self.conhecimento[i][j] is not None:
                    linha.append(self.conhecimento[i][j])
                elif (i, j) in self.perigosas:
                    linha.append('P')
                elif (i, j) in self.seguras:
                    linha.append('S')
                else:
                    linha.append('?')
            print(' '.join(linha))
        
        print(f"Seguras: {self.seguras}")
        print(f"Perigosas: {self.perigosas}")
        print(f"Fedores: {self.fedores}")
        print(f"Brisas: {self.brisas}")
        print(f"Wumpus: {self.pos_wumpus}")
        print(f"Ouro: {self.pos_ouro}")
        print(f"Fronteira: {self.fronteira}")
        print("----------------------------------\n")

def modo_agente(mapa, percepcoes, delay=1):
    """Função principal para o modo agente automático"""
    # Estado do jogo
    pos_jogador = (0, 0)
    direcao_jogador = 'leste'
    flecha = True
    ouro_coletado = False
    pontuacao = 0
    movimento_count = 0
    wumpus_vivo = True
    jogo_ativo = True
    visitadas = {pos_jogador}
    
    # Cria o agente inteligente
    agente = AgenteInteligente(mapa, percepcoes)
    
    limpar_tela()
    print("=" * 50)
    print("    Mundo de Wumpus - Modo Agente Automático")
    print("=" * 50)
    
    print("\nO agente inteligente está explorando a caverna...")
    print("Pressione Enter para cada passo ou digite 'auto' para execução automática.")
    modo_execucao = input("Modo (passo a passo/auto): ").strip().lower()
    
    automatico = (modo_execucao == 'auto')
    
    # Ciclo principal do jogo
    while jogo_ativo:
        i, j = pos_jogador
        percepcoes_atuais = percepcoes[i][j]
        
        # Exibe informações atuais
        print(f"\nPasso {movimento_count}:")
        print(f"O agente está na posição [{i+1},{j+1}] olhando para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}")
        
        # Exibe percepções na casa atual
        if percepcoes_atuais:
            print(f"O agente percebe: {', '.join(percepcoes_atuais)}")
        else:
            print("O agente não percebe nada especial.")
        
        # Exibe o mapa visível
        exibir_mapa_jogador(mapa, percepcoes, pos_jogador, visitadas)
        
        # Atualiza o conhecimento do agente
        agente.pos_atual = pos_jogador
        agente.direcao_atual = direcao_jogador
        agente.atualizar_conhecimento(percepcoes_atuais)
        agente.exibir_conhecimento()  # Debug
        
        # Verifica condições de fim de jogo
        if mapa[i][j] == "W" and wumpus_vivo:
            print("\n!! O AGENTE FOI DEVORADO PELO WUMPUS !!")
            print("Fim de jogo.")
            pontuacao -= 100
            jogo_ativo = False
            break
        
        if mapa[i][j] == "B":
            print("\n!! O AGENTE CAIU EM UM BURACO !!")
            print("Fim de jogo.")
            pontuacao -= 100
            jogo_ativo = False
            break
        
        # O agente decide a próxima ação
        acao = agente.decidir_proxima_acao()
        print(f"Ação escolhida pelo agente: {acao}")
        
        if acao == "sem_acao":
            print("\nO agente não consegue encontrar uma ação segura. Saindo da caverna...")
            jogo_ativo = False
            break
        
        # Não incrementa o contador para comandos que não são ações
        movimento_count += 1
        
        # Processamento dos comandos
        if acao == "pegar":
            if "brilho" in percepcoes[i][j]:
                print("\nO agente encontrou o ouro e o guardou na bolsa!")
                percepcoes[i][j].remove("brilho") # Remove o brilho
                ouro_coletado = True
                agente.ouro_coletado = True
            else:
                print("Não há nada para pegar aqui.")
                movimento_count -= 1  # Não conta como movimento
        
        elif acao == "escalar":
            if pos_jogador == (0, 0):
                if ouro_coletado:
                    print("\n*** SUCESSO! ***")
                    print("O agente escapou da caverna com o ouro!")
                    pontuacao += 1000  # Pontos por escapar com o ouro
                    pontuacao -= (movimento_count - 1)  # Perda de pontos por número de movimentos
                    jogo_ativo = False
                else:
                    print("O agente precisa pegar o ouro antes de escapar!")
                    movimento_count -= 1  # Não conta como movimento
            else:
                print("O agente só pode escalar na entrada da caverna [1,1].")
                movimento_count -= 1  # Não conta como movimento
        
        elif acao == "atirar":
            if flecha and wumpus_vivo:
                acertou = False
                pos_wumpus = None
                for r in range(4):
                    for c in range(4):
                        if mapa[r][c] == 'W':
                            pos_wumpus = (r, c)
                            break
                
                if pos_wumpus:
                    wi, wj = pos_wumpus
                    if direcao_jogador == 'norte' and j == wj and i > wi: acertou = True
                    elif direcao_jogador == 'sul' and j == wj and i < wi: acertou = True
                    elif direcao_jogador == 'leste' and i == wi and j < wj: acertou = True
                    elif direcao_jogador == 'oeste' and i == wi and j > wj: acertou = True
                
                flecha = False
                agente.tem_flecha = False
                print("\nO agente atira a flecha zumbindo pelo corredor...")
                if acertou:
                    print("Ouve-se um grito horrível! O Wumpus foi morto!")
                    print("O agente recebeu 500 pontos!")
                    wumpus_vivo = False
                    agente.wumpus_vivo = False
                    mapa[pos_wumpus[0]][pos_wumpus[1]] = '.' # Remove Wumpus do mapa
                    # Remove fedor das casas adjacentes
                    percepcoes = marcar_percepcoes(mapa) 
                    pontuacao += 500
                else:
                    print("A flecha não acertou nada e desapareceu na escuridão.")
            else:
                if not flecha:
                    print("O agente já usou sua única flecha!")
                else:
                    print("O Wumpus já está morto!")
                movimento_count -= 1  # Não conta como movimento
        
        elif acao == "cima":
            nova_pos = obter_proxima_posicao(pos_jogador, direcao_jogador)
                
            if nova_pos:
                pos_jogador = nova_pos
                visitadas.add(pos_jogador)
                print(f"O agente move para [{pos_jogador[0]+1},{pos_jogador[1]+1}]")
            else:
                print("O agente bateu na parede!")
                movimento_count -= 1  # Não conta como movimento
        
        elif acao == "dir":
            direcao_jogador = virar_direcao(direcao_jogador, 'dir')
            print(f"O agente virou para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}.")
            
        elif acao == "esq":
            direcao_jogador = virar_direcao(direcao_jogador, 'esq')
            print(f"O agente virou para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}.")
        
        # Pausa entre as ações no modo passo a passo
        if not automatico:
            input("\nPressione Enter para continuar...")
        else:
            time.sleep(delay)  # Pausa para visualização em modo automático
    
    # Exibe pontuação final
    print(f"\nPontuação final: {pontuacao}")
    
    # Mostra o mapa completo no final do jogo
    print("\nMapa completo da caverna:")
    exibir_mapa_debug(mapa)

def modo_jogador(mapa, percepcoes):
    """Função principal para o modo jogador humano"""
    # Estado do jogo
    pos_jogador = (0, 0)
    direcao_jogador = 'leste'
    flecha = True
    ouro_coletado = False
    pontuacao = 0
    movimento_count = 0
    wumpus_vivo = True
    jogo_ativo = True
    visitadas = {pos_jogador}
    
    mapa_original = [linha[:] for linha in mapa]

    limpar_tela()
    print("=" * 50)
    print("    Bem-vindo ao Mundo de Wumpus!")
    print("=" * 50)
    print("Digite 'ajuda' para ver as instruções do jogo.")
    print("Seu objetivo é encontrar o ouro e retornar à entrada.")
    print("Cuidado com o Wumpus e os buracos!")
    
    # Ciclo principal do jogo
    while jogo_ativo:
        i, j = pos_jogador
        
        # As percepções devem ser lidas do mapa de percepções original, não do mapa do jogo que pode ser modificado
        percepcoes_atuais = percepcoes[i][j]
        
        # Informa a posição atual e as percepções
        print(f"\nVocê está na posição [{i+1},{j+1}] olhando para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}")
        
        # Exibe percepções na casa atual
        if percepcoes_atuais:
            print(f"Você percebe: {', '.join(percepcoes_atuais)}")
        else:
            print("Você não percebe nada especial.")
        
        # Verifica condições de fim de jogo
        if mapa_original[i][j] == "W" and wumpus_vivo:
            print("\n!! VOCÊ FOI DEVORADO PELO WUMPUS !!")
            print("Fim de jogo.")
            pontuacao -= 1000
            jogo_ativo = False
            break
        
        if mapa_original[i][j] == "B":
            print("\n!! VOCÊ CAIU EM UM BURACO !!")
            print("Fim de jogo.")
            pontuacao -= 1000
            jogo_ativo = False
            break
        
        # Interface com o jogador
        print("\nO que você quer fazer? (digite 'ajuda' para ver os comandos)")
        movimento = input("> ").strip().lower()
        
        # Não incrementa o contador para comandos que não são ações
        if movimento not in ['mapa', 'ajuda', 'sair']:
            pontuacao -=1
            movimento_count += 1
        
        # Processamento dos comandos
        if movimento == "sair":
            print("Jogo encerrado.")
            jogo_ativo = False
        
        elif movimento == "ajuda":
            exibir_ajuda()
            
        elif movimento == "mapa":
            exibir_mapa_jogador(mapa, percepcoes, pos_jogador, visitadas)
        
        elif movimento == "cima":
            nova_pos = obter_proxima_posicao(pos_jogador, direcao_jogador)
                
            if nova_pos:
                pos_jogador = nova_pos
                visitadas.add(pos_jogador)
                exibir_mapa_jogador(mapa, percepcoes, pos_jogador, visitadas)
            else:
                print("Você bateu na parede! Tente mudar de direção.")
                pontuacao += 1 # Anula a penalidade
                movimento_count -= 1  # Não conta como movimento
        
        elif movimento == "dir":
            direcao_jogador = virar_direcao(direcao_jogador, 'dir')
            print(f"Virou para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}.")
            
        elif movimento == "esq":
            direcao_jogador = virar_direcao(direcao_jogador, 'esq')
            print(f"Virou para {direcao_jogador} {obter_direcao_simbolo(direcao_jogador)}.")
            
        elif movimento == "atirar":
            pontuacao -= 10 # Custo para atirar
            if flecha and wumpus_vivo:
                acertou = False
                pos_wumpus = None
                for r in range(4):
                    for c in range(4):
                        if mapa_original[r][c] == 'W':
                            pos_wumpus = (r, c)
                            break
                
                if pos_wumpus:
                    wi, wj = pos_wumpus
                    if direcao_jogador == 'norte' and j == wj and i > wi: acertou = True
                    elif direcao_jogador == 'sul' and j == wj and i < wi: acertou = True
                    elif direcao_jogador == 'leste' and i == wi and j < wj: acertou = True
                    elif direcao_jogador == 'oeste' and i == wi and j > wj: acertou = True
                
                flecha = False
                print("\nVocê atira a flecha zumbindo pelo corredor...")
                if acertou:
                    print("Você ouve um grito horrível! O Wumpus foi morto!")
                    wumpus_vivo = False
                    # Atualiza o mapa de percepções sem o fedor
                    percepcoes = marcar_percepcoes(mapa_original)
                else:
                    print("A flecha não acertou nada e desapareceu na escuridão.")
            else:
                if not flecha:
                    print("Você já usou sua única flecha!")
                else:
                    print("O Wumpus já está morto!")
                pontuacao += 10 # Devolve o custo
                movimento_count -= 1
                    
        elif movimento == "pegar":
            if mapa_original[i][j] == "O":
                print("\nVocê encontrou o ouro e o guardou na sua bolsa!")
                mapa[i][j] = "." # Atualiza o mapa visível
                ouro_coletado = True
            else:
                print("Não há nada para pegar aqui.")
                pontuacao += 1
                movimento_count -= 1
                
        elif movimento == "escalar":
            if pos_jogador == (0, 0):
                if ouro_coletado:
                    print("\n*** PARABÉNS! ***")
                    print("Você escapou da caverna com o ouro!")
                    pontuacao += 1000
                    jogo_ativo = False
                else:
                    print("Você precisa pegar o ouro antes de escapar!")
                    pontuacao += 1
                    movimento_count -= 1
            else:
                print("Você só pode escalar na entrada da caverna [1,1].")
                pontuacao += 1
                movimento_count -= 1
                
        else:
            print("Comando não reconhecido. Digite 'ajuda' para ver os comandos disponíveis.")
            pontuacao += 1
            movimento_count -= 1
    
    # Exibe pontuação final
    print(f"\nPontuação final: {pontuacao}")
    
    # Mostra o mapa completo no final do jogo
    print("\nMapa completo da caverna:")
    exibir_mapa_debug(mapa_original)

class QLearningAgent:
    """Agente que usa Q-learning para aprender a jogar o Mundo de Wumpus"""
    
    def __init__(self, alpha=0.3, gamma=0.95, epsilon=1.0, epsilon_decay=0.9997, min_epsilon=0.05):
        # Parâmetros otimizados
        self.alpha = alpha  # Taxa de aprendizado aumentada
        self.gamma = gamma  # Fator de desconto mantido alto
        self.epsilon = epsilon  # Exploração inicial total
        self.epsilon_decay = epsilon_decay  # Decaimento mais lento
        self.min_epsilon = min_epsilon  # Mínimo de exploração
        
        # Q-table: estado -> (ação -> valor Q)
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Ações possíveis
        self.actions = ['cima', 'dir', 'esq', 'atirar', 'pegar']
        
        # Histórico para detectar ciclos e comportamentos repetitivos
        self.acoes_recentes = []
        self.max_historico = 10
        self.posicoes_recentes = []
        
        # SISTEMA DE RECOMPENSAS REEQUILIBRADO
        self.rewards = {
            'ouro_coletado': 1000,      # Mantido alto
            'saiu_com_ouro': 5000,      # AUMENTADO SIGNIFICATIVAMENTE
            'wumpus_morto': 500,        # Mantido
            'movimento': -1,            # Penalidade base por movimento
            'explorar': 20,             # AUMENTADO: maior incentivo à exploração
            'virar': -2,                # REDUZIDO: menos penalidade para virar
            'virar_repetido': -50,      # AUMENTADO: penalidade maior para virar em ciclos
            'bateu_parede': -10,        # Ajustado
            'morreu_wumpus': -1000,     # Mantido
            'caiu_buraco': -1000,       # Mantido
            'acao_invalida': -15,       # Ajustado
            'acao_repetida': -30,       # Mantido
            'ciclo_detectado': -100,    # AUMENTADO: penalidade mais severa
            'atirar_sem_flecha': -15,   # Mantido
            'atirar_errado': -20,       # Mantido
            'pegar_invalido': -25,      # Mantido
            'aproximar_ouro': 15,       # NOVO: recompensa por se aproximar do ouro
            'aproximar_saida': 10       # NOVO: recompensa por se aproximar da saída com ouro
        }
        
        # Rastreamento de progresso
        self.visitadas_episodio = set()
        self.pos_ouro = None  # Posição do ouro quando descoberta
        self.distancia_anterior_ouro = float('inf')
        self.distancia_anterior_saida = float('inf')
    
    def get_estado(self, pos, direcao, percepcoes, tem_flecha, tem_ouro):
        """Estado simplificado para melhor generalização"""
        # Reduz o espaço de estados incluindo apenas percepções cruciais
        percepcoes_relevantes = []
        if 'fedor' in percepcoes:
            percepcoes_relevantes.append('fedor')
        if 'brisa' in percepcoes:
            percepcoes_relevantes.append('brisa')
        if 'brilho' in percepcoes:
            percepcoes_relevantes.append('brilho')
            
        percepcoes_tuple = tuple(sorted(percepcoes_relevantes))
        
        # Incluir apenas informações essenciais no estado
        return (pos, direcao, percepcoes_tuple, tem_flecha, tem_ouro)
    
    def detectar_ciclo(self):
        """Detecção de ciclos melhorada"""
        # Verifica padrões de ações repetitivas
        if len(self.acoes_recentes) >= 8:  # Expandido para capturar ciclos maiores
            # Ciclos de tamanho 2 (dir, esq, dir, esq...)
            if self.acoes_recentes[-2:] * 4 == self.acoes_recentes[-8:]:
                return True
                
            # Ciclos de tamanho 3
            if len(self.acoes_recentes) >= 9 and self.acoes_recentes[-3:] * 3 == self.acoes_recentes[-9:]:
                return True
                
            # Ciclos de tamanho 4
            if len(self.acoes_recentes) >= 12 and self.acoes_recentes[-4:] * 3 == self.acoes_recentes[-12:]:
                return True
        
        # Verifica repetição de posições
        if len(self.posicoes_recentes) >= 8:
            # Conta posições únicas nos últimos 8 movimentos
            posicoes_unicas = len(set(self.posicoes_recentes[-8:]))
            # Se houver 3 ou menos posições únicas em 8 movimentos, é um ciclo
            if posicoes_unicas <= 3:
                return True
                
        return False
    
    def escolher_acao(self, estado, percepcoes):
        """Política de seleção de ação inteligente"""
        # Atualiza histórico de posições
        self.posicoes_recentes.append(estado[0])
        if len(self.posicoes_recentes) > self.max_historico:
            self.posicoes_recentes.pop(0)
        
        # EXPLORAÇÃO INTELIGENTE
        if random.random() < self.epsilon:
            acoes_prioritarias = []
            pos, direcao, percepcoes_estado, tem_flecha, tem_ouro = estado
            
            # Ações de alta prioridade baseadas no contexto
            if 'brilho' in percepcoes and not tem_ouro:
                # Prioridade absoluta: pegar o ouro se estiver na mesma célula
                return 'pegar'
                
            if tem_ouro and pos == (0, 0):
                # Se tiver o ouro e estiver na entrada, prioridade é sair
                # (esta condição é mais para treino, já que o jogo acaba neste ponto)
                return 'escalar'
            
            # Se tem ouro, prioriza voltar para a entrada
            if tem_ouro:
                # Tenta mover em direção à entrada (0,0)
                if self._deve_ir_para_norte(pos):
                    if direcao == 'norte':
                        acoes_prioritarias.append('cima')
                    elif direcao == 'leste':
                        acoes_prioritarias.append('esq')
                    elif direcao == 'oeste':
                        acoes_prioritarias.append('dir')
                    else:  # sul
                        acoes_prioritarias.extend(['dir', 'dir'])
                elif self._deve_ir_para_oeste(pos):
                    if direcao == 'oeste':
                        acoes_prioritarias.append('cima')
                    elif direcao == 'norte':
                        acoes_prioritarias.append('esq')
                    elif direcao == 'sul':
                        acoes_prioritarias.append('dir')
                    else:  # leste
                        acoes_prioritarias.extend(['dir', 'dir'])
            
            # Se sente fedor e tem flecha, considera atirar
            if 'fedor' in percepcoes and tem_flecha:
                acoes_prioritarias.append('atirar')
            
            # Prioriza movimento para frente, mas evita paredes
            acoes_prioritarias.append('cima')
            
            # Randomiza um pouco para evitar ciclos previsíveis
            random.shuffle(acoes_prioritarias)
            
            # Seleciona uma ação prioritária com 80% de chance
            if acoes_prioritarias and random.random() < 0.8:
                return acoes_prioritarias[0]
            
            # Caso contrário, ação completamente aleatória
            return random.choice(self.actions)
        
        # EXPLORAÇÃO - MELHOR AÇÃO CONHECIDA
        q_values = self.q_table[estado]
        
        if not q_values:
            return random.choice(self.actions)
        
        max_q = max(q_values.values())
        best_actions = [a for a, q in q_values.items() if q == max_q]
        
        # ANTI-CICLO: Evita repetir a última ação, especialmente se for virar
        if len(best_actions) > 1 and self.acoes_recentes:
            ultima_acao = self.acoes_recentes[-1] if self.acoes_recentes else None
            
            # Se está virando repetidamente, evita
            if ultima_acao in ['dir', 'esq'] and ultima_acao in best_actions:
                best_actions.remove(ultima_acao)
                
            # Se detectar ciclo, evita ações recentes completamente
            if self.detectar_ciclo() and len(best_actions) > 1:
                for acao in self.acoes_recentes[-4:]:
                    if acao in best_actions and len(best_actions) > 1:
                        best_actions.remove(acao)
        
        escolhida = random.choice(best_actions)
        
        # Atualiza histórico de ações
        self.acoes_recentes.append(escolhida)
        if len(self.acoes_recentes) > self.max_historico:
            self.acoes_recentes.pop(0)
        
        return escolhida
    
    def _deve_ir_para_norte(self, pos):
        """Helper para determinar se deve ir para o norte para chegar à entrada"""
        return pos[0] > 0
    
    def _deve_ir_para_oeste(self, pos):
        """Helper para determinar se deve ir para o oeste para chegar à entrada"""
        return pos[1] > 0
    
    def atualizar_q_table(self, estado, acao, recompensa, proximo_estado):
        """Atualização da Q-table com penalidades para comportamentos não desejados"""
        # ANTI-CICLO: Penalidade severa para padrões cíclicos
        if self.detectar_ciclo():
            recompensa += self.rewards['ciclo_detectado']
        
        # Penalidade para ações repetitivas
        if len(self.acoes_recentes) >= 3:
            # Se as últimas 3 ações foram iguais
            if all(a == acao for a in self.acoes_recentes[-3:]):
                recompensa += self.rewards['acao_repetida']
            
            # Penalidade para alternar entre virar esquerda e direita
            if len(self.acoes_recentes) >= 4:
                ultimas_acoes = self.acoes_recentes[-4:]
                if (all(a in ['dir', 'esq'] for a in ultimas_acoes) and
                    ultimas_acoes[0] != ultimas_acoes[1] and
                    ultimas_acoes[1] != ultimas_acoes[2] and
                    ultimas_acoes[2] != ultimas_acoes[3]):
                    recompensa += self.rewards['virar_repetido']
        
        # APRENDIZADO PROFUNDO: Aumenta alpha quando detecta ciclos para quebrar padrões
        learning_rate = self.alpha
        if self.detectar_ciclo():
            learning_rate = min(0.9, self.alpha * 2)  # Aumenta a taxa de aprendizado, mas no máximo 0.9
        
        # Equação Q-Learning padrão com learning rate adaptativo
        max_q_proximo = max(self.q_table[proximo_estado].values()) if self.q_table[proximo_estado] else 0.0
        current_q = self.q_table[estado][acao]
        new_q = current_q + learning_rate * (recompensa + self.gamma * max_q_proximo - current_q)
        self.q_table[estado][acao] = new_q
    
    def treinar_episodio(self, mapa_original, percepcoes_original):
        """Executa um episódio completo com rastreamento de progresso melhorado"""
        # Cria cópias do mapa e percepções
        mapa = [linha[:] for linha in mapa_original]
        percepcoes = [[celula[:] for celula in linha] for linha in percepcoes_original]
        
        # Reset do estado
        pos = (0, 0)
        direcao = 'leste'
        tem_flecha = True
        tem_ouro = False
        wumpus_vivo = True
        self.acoes_recentes = []
        self.posicoes_recentes = []
        self.visitadas_episodio = {(0, 0)}
        self.pos_ouro = None
        self.distancia_anterior_ouro = float('inf')
        self.distancia_anterior_saida = float('inf')
        
        # Encontra a posição do ouro para calcular distâncias
        for i in range(4):
            for j in range(4):
                if mapa[i][j] == 'O':
                    self.pos_ouro = (i, j)
                    self.distancia_anterior_ouro = self._calcular_distancia(pos, self.pos_ouro)
                    break
        
        max_passos = 100  # Limite para evitar episódios muito longos
        
        for _ in range(max_passos):
            # Obter estado e percepções atuais
            percepcoes_atuais = percepcoes[pos[0]][pos[1]]
            estado_atual = self.get_estado(pos, direcao, percepcoes_atuais, tem_flecha, tem_ouro)
            
            # Escolher ação
            acao = self.escolher_acao(estado_atual, percepcoes_atuais)
            
            # Executar ação
            nova_pos, nova_direcao, novo_tem_flecha, novo_tem_ouro, novo_wumpus_vivo, recompensa, fim_de_jogo = \
                self.executar_acao(acao, pos, direcao, tem_flecha, tem_ouro, wumpus_vivo, mapa, percepcoes)
            
            # RECOMPENSAS ADICIONAIS POR PROGRESSO
            
            # Recompensa por explorar novas áreas
            if nova_pos not in self.visitadas_episodio:
                recompensa += self.rewards['explorar']
                self.visitadas_episodio.add(nova_pos)
            
            # Recompensa por aproximação do ouro (se não tiver coletado ainda)
            if not tem_ouro and self.pos_ouro:
                nova_distancia = self._calcular_distancia(nova_pos, self.pos_ouro)
                if nova_distancia < self.distancia_anterior_ouro:
                    recompensa += self.rewards['aproximar_ouro']
                self.distancia_anterior_ouro = nova_distancia
            
            # Recompensa por aproximação da saída (se tiver o ouro)
            if novo_tem_ouro:
                nova_distancia_saida = self._calcular_distancia(nova_pos, (0, 0))
                if nova_distancia_saida < self.distancia_anterior_saida:
                    recompensa += self.rewards['aproximar_saida']
                self.distancia_anterior_saida = nova_distancia_saida
            
            # Obter novo estado
            novas_percepcoes = percepcoes[nova_pos[0]][nova_pos[1]]
            proximo_estado = self.get_estado(nova_pos, nova_direcao, novas_percepcoes, novo_tem_flecha, novo_tem_ouro)
            
            # Atualizar Q-Table
            self.atualizar_q_table(estado_atual, acao, recompensa, proximo_estado)
            
            # Atualizar estado
            pos, direcao = nova_pos, nova_direcao
            tem_flecha, tem_ouro, wumpus_vivo = novo_tem_flecha, novo_tem_ouro, novo_wumpus_vivo
            
            # Verificar fim de episódio
            if fim_de_jogo:
                return recompensa > 0  # Sucesso se recompensa for positiva
        
        # Decai epsilon
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
        
        return False
    
    def salvar_q_table(self, filename):
     with open(filename, 'wb') as f:
        pickle.dump(dict(self.q_table), f)

    def carregar_q_table(self, filename):
        try:
            with open(filename, 'rb') as f:
                q_dict = pickle.load(f)
                # Converte de volta para defaultdict
                self.q_table = defaultdict(lambda: defaultdict(float))
                for estado, acoes in q_dict.items():
                    self.q_table[estado] = defaultdict(float, acoes)
            return True
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado. Iniciando com Q-table vazia.")
            return False

    def _calcular_distancia(self, pos1, pos2):
        """Calcula a distância Manhattan entre duas posições"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def executar_acao(self, acao, pos, direcao, tem_flecha, tem_ouro, wumpus_vivo, mapa, percepcoes):
        """Executa uma ação e retorna o resultado"""
        i, j = pos
        recompensa = self.rewards['movimento']  # Recompensa base
        fim_de_jogo = False
        
        # Implementação das ações - mantendo o código existente
        if acao == 'cima':
            nova_pos = obter_proxima_posicao(pos, direcao)
            if nova_pos:
                pos = nova_pos
            else:
                recompensa = self.rewards['bateu_parede']
        
        elif acao == 'dir' or acao == 'esq':
            direcao = virar_direcao(direcao, acao)
            recompensa = self.rewards['virar']
        
        elif acao == 'pegar':
            if 'brilho' in percepcoes[i][j] and not tem_ouro:
                tem_ouro = True
                percepcoes[i][j].remove('brilho')
                recompensa = self.rewards['ouro_coletado']
            else:
                recompensa = self.rewards['pegar_invalido']
        
        elif acao == 'atirar':
            if not tem_flecha:
                recompensa = self.rewards['atirar_sem_flecha']
            elif wumpus_vivo:
                tem_flecha = False
                acertou = False
                
                # Encontra posição do Wumpus
                pos_wumpus = next(((r, c) for r in range(4) for c in range(4) if mapa[r][c] == 'W'), None)
                
                if pos_wumpus:
                    wi, wj = pos_wumpus
                    # Verifica se acertou o Wumpus
                    if (direcao == 'norte' and j == wj and i > wi) or \
                       (direcao == 'sul'   and j == wj and i < wi) or \
                       (direcao == 'leste'  and i == wi and j < wj) or \
                       (direcao == 'oeste'  and i == wi and j > wj):
                        acertou = True
                
                if acertou:
                    wumpus_vivo = False
                    recompensa = self.rewards['wumpus_morto']
                    # Atualiza mapa e percepções
                    mapa[pos_wumpus[0]][pos_wumpus[1]] = '.'
                    for linha in range(4):
                        for coluna in range(4):
                            if 'fedor' in percepcoes[linha][coluna]:
                                percepcoes[linha][coluna].remove('fedor')
                else:
                    recompensa = self.rewards['atirar_errado']
            else:
                recompensa = self.rewards['acao_invalida']
        
        # Verificações pós-ação
        ni, nj = pos
        
        # Verifica condições de fim de jogo
        if mapa[ni][nj] == 'W' and wumpus_vivo:
            recompensa = self.rewards['morreu_wumpus']
            fim_de_jogo = True
        elif mapa[ni][nj] == 'B':
            recompensa = self.rewards['caiu_buraco']
            fim_de_jogo = True
        
        # Verifica vitória
        if tem_ouro and pos == (0, 0):
            recompensa = self.rewards['saiu_com_ouro']
            fim_de_jogo = True
        
        return pos, direcao, tem_flecha, tem_ouro, wumpus_vivo, recompensa, fim_de_jogo
    
    

def treinar_agente_qlearning(num_episodios=10000):
    """Treina o agente Q-learning com configurações otimizadas"""
    agente = QLearningAgent(
        alpha=0.3,          # Taxa de aprendizado aumentada
        gamma=0.95,         # Fator de desconto alto
        epsilon=1.0,        # Começa com exploração total
        epsilon_decay=0.9997, # Decaimento mais lento para explorar mais
        min_epsilon=0.05    # Mínimo de exploração
    )
    
    # Opção para resetar Q-table
    if agente.carregar_q_table('q_table_wumpus.pkl'):
        print("Q-table existente carregada. Continuando treinamento...")
        resposta = input("Deseja apagar a Q-table existente e começar do zero? (s/n): ").strip().lower()
        if resposta == 's':
            agente.q_table = defaultdict(lambda: defaultdict(float))
            print("Q-table resetada.")
    
    # Estatísticas de treinamento
    sucessos_recentes = 0
    total_sucessos = 0
    historico_sucessos = []
    
    print(f"Iniciando treinamento com {num_episodios} episódios...")
    
    for episodio in range(1, num_episodios + 1):
        # Cria novo mapa para cada episódio
        mapa = criar_mapa()
        percepcoes = marcar_percepcoes(mapa)
        
        # Treina um episódio
        if agente.treinar_episodio(mapa, percepcoes):
            sucessos_recentes += 1
            total_sucessos += 1
        
        # Mostra progresso
        if episodio % 100 == 0:
            taxa_sucesso = sucessos_recentes / 100
            historico_sucessos.append(taxa_sucesso)
            print(f"Episódio {episodio}: Taxa de sucesso (últimos 100): {taxa_sucesso:.2%}, " +
                  f"Epsilon: {agente.epsilon:.4f}, Total de sucessos: {total_sucessos}")
            sucessos_recentes = 0
            
            # Salva periodicamente
            if episodio % 1000 == 0:
                agente.salvar_q_table('q_table_wumpus.pkl')
                print(f"Q-table salva em 'q_table_wumpus.pkl' (Episódio {episodio})")
    
    # Salva a Q-table final
    agente.salvar_q_table('q_table_wumpus.pkl')
    print(f"\nTreinamento concluído! Total: {total_sucessos}/{num_episodios} ({total_sucessos/num_episodios:.2%})")
    print("Q-table salva em 'q_table_wumpus.pkl'")

def modo_agente_qlearning(mapa, percepcoes, delay=0.5):
    """Modo onde o agente Q-learning joga usando a Q-table treinada."""
    agente = QLearningAgent()
    if not agente.carregar_q_table('q_table_wumpus.pkl'):
        print("Nenhum agente treinado encontrado. Execute o treinamento primeiro (opção 4).")
        return
    
    # Desativa a exploração para o modo de jogo
    agente.epsilon = 0
    
    # Estado inicial do jogo
    pos = (0, 0)
    direcao = 'leste'
    tem_flecha = True
    tem_ouro = False
    wumpus_vivo = True
    pontuacao = 0
    passos = 0
    visitadas = {pos}
    
    # Reset dos históricos para o modo de jogo
    agente.acoes_recentes = []
    agente.posicoes_recentes = []
    
    limpar_tela()
    print("=" * 50)
    print("    Mundo de Wumpus - Agente Q-Learning")
    print("=" * 50)
    
    print("\nO agente Q-Learning está jogando...")
    print("Pressione Enter para cada passo ou digite 'auto' para execução automática.")
    modo_execucao = input("Modo (passo a passo/auto): ").strip().lower()
    automatico = (modo_execucao == 'auto')
    
    jogo_ativo = True
    while jogo_ativo and passos < 100:  # Limite para evitar loops infinitos
        i, j = pos
        percepcoes_atuais = percepcoes[i][j]
        
        # Exibir informações
        print(f"\nPasso {passos}: Pontuação: {pontuacao}")
        print(f"Agente em [{i+1},{j+1}], olhando para {direcao} {obter_direcao_simbolo(direcao)}")
        if percepcoes_atuais: 
            print(f"Percebe: {', '.join(percepcoes_atuais)}")
        else: 
            print("Não percebe nada de especial.")
        
        exibir_mapa_jogador(mapa, percepcoes, pos, visitadas)
        
        # Verificar condições de fim de jogo
        if mapa[i][j] == "W" and wumpus_vivo:
            print("\n!! O AGENTE FOI DEVORADO PELO WUMPUS !!")
            pontuacao += agente.rewards['morreu_wumpus']
            break
            
        if mapa[i][j] == "B":
            print("\n!! O AGENTE CAIU EM UM BURACO !!")
            pontuacao += agente.rewards['caiu_buraco']
            break
            
        if tem_ouro and pos == (0, 0):
            print("\n*** SUCESSO! O AGENTE ESCAPOU COM O OURO! ***")
            pontuacao += agente.rewards['saiu_com_ouro']
            break

        # Verifica se está em um ciclo e avisa
        if agente.detectar_ciclo():
            print("\n⚠️ ALERTA: O agente parece estar em um padrão cíclico!")
            
            # Se ficar preso por muito tempo no mesmo lugar, encerra
            if passos > 20 and all(p == agente.posicoes_recentes[0] for p in agente.posicoes_recentes[-5:]):
                print("O agente está preso em um ciclo. Encerrando simulação.")
                break

        # O agente escolhe e executa a ação
        estado_atual = agente.get_estado(pos, direcao, percepcoes_atuais, tem_flecha, tem_ouro)
        acao = agente.escolher_acao(estado_atual, percepcoes_atuais)
        print(f"Ação escolhida pelo agente: {acao.upper()}")

        # Executar ação
        resultado = agente.executar_acao(acao, pos, direcao, tem_flecha, tem_ouro, wumpus_vivo, mapa, percepcoes)
        pos, direcao, tem_flecha, tem_ouro, wumpus_vivo, recompensa, _ = resultado
        
        pontuacao += recompensa
        passos += 1
        visitadas.add(pos)
        
        # Pausa entre as ações
        if not automatico:
            input("Pressione Enter para continuar...")
        else:
            time.sleep(delay)
    
    print(f"\nFim de jogo! Pontuação final: {pontuacao} em {passos} passos")
    print("\nMapa completo da caverna:")
    exibir_mapa_debug(mapa)

def iniciar_jogo():
    """Inicia o jogo e permite escolher entre modo jogador e modo agente"""
    
    limpar_tela()
    print("=" * 50)
    print("    Mundo de Wumpus")
    print("=" * 50)
    print("\nEscolha o modo de jogo:")
    print("1 - Modo Jogador (você controla as ações)")
    print("2 - Modo Agente com Lógica (IA baseada em regras)")
    print("3 - Jogar com Agente Q-Learning (IA treinada)")
    print("4 - Treinar Agente Q-Learning")
    
    modo_valido = False
    while not modo_valido:
        modo = input("\nDigite o número do modo: ").strip()
        if modo in ['1', '2', '3']:
            mapa = criar_mapa()
            percepcoes = marcar_percepcoes(mapa)
            if modo == '1':
                modo_jogador(mapa, percepcoes)
            elif modo == '2':
                modo_agente(mapa, percepcoes)
            elif modo == '3':
                modo_agente_qlearning(mapa, percepcoes)
            modo_valido = True
        elif modo == '4':
            num_eps_str = input("Número de episódios de treinamento (padrão 10000): ").strip()
            try:
                num_eps = int(num_eps_str) if num_eps_str else 10000
            except ValueError:
                num_eps = 10000
            treinar_agente_qlearning(num_eps)
            modo_valido = True
        else:
            print("Modo inválido! Digite 1, 2, 3 ou 4.")

def main():
    """Função principal do programa"""
    jogando = True
    
    while jogando:
        iniciar_jogo()
        
        resposta = input("\nDeseja jogar novamente ou voltar ao menu? (s/n): ").strip().lower()
        if resposta != 's':
            print("\nObrigado por jogar o Mundo de Wumpus!")
            jogando = False

if __name__ == "__main__":
    main()