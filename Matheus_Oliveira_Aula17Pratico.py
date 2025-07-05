import numpy as np
import random
import time
import os

#codigo feito com a ajuda do ChatGPT/copilot
TAXA_APRENDIZADO = 0.2      
FATOR_DESCONTO = 0.9
EPISODIOS = 20000         
DECAIMENTO_EPSILON = 0.9995 
EPSILON_MIN = 0.05
EPSILON = 1.0 
ACOES = {0: 'Cima', 1: 'Baixo', 2: 'Esquerda', 3: 'Direita', 4: 'Atirar'}

class WumpusMundo:
   
    def __init__(self, tamanho=4, num_buracos=3):
        self.tamanho = tamanho
        self.num_buracos = num_buracos
        self.reset()
        
    def reset(self):
        
        posicoes_disponiveis = [(i, j) for i in range(self.tamanho) for j in range(self.tamanho)]
        posicoes_iniciais_seguras = [(0,0), (0,1), (1,0)]
        for pos in posicoes_iniciais_seguras:
            if pos in posicoes_disponiveis: posicoes_disponiveis.remove(pos)
        self.pos_player = [0, 0]
        pos_ouro = random.choice(posicoes_disponiveis)
        posicoes_disponiveis.append((0,1)); posicoes_disponiveis.append((1,0))
        posicoes_disponiveis.remove(pos_ouro)
        self.pos_ouro = list(pos_ouro)
        pos_wumpus = random.choice(posicoes_disponiveis)
        posicoes_disponiveis.remove(pos_wumpus)
        self.pos_wumpus = list(pos_wumpus)
        self.pos_buracos = [list(pos) for pos in random.sample(posicoes_disponiveis, self.num_buracos)]
        self.fim_de_jogo = False; self.wumpus_vivo = True; self.tem_flecha = True
        self._gerar_percepcoes()
        return self.get_estado()

    def _gerar_percepcoes(self):
        
        self.percepcoes = {'brisa': np.zeros((self.tamanho, self.tamanho), dtype=bool),
                           'fedor': np.zeros((self.tamanho, self.tamanho), dtype=bool)}
        if self.wumpus_vivo:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if abs(i) + abs(j) == 1:
                        y, x = self.pos_wumpus[0] + i, self.pos_wumpus[1] + j
                        if 0 <= y < self.tamanho and 0 <= x < self.tamanho: self.percepcoes['fedor'][y, x] = True
        for buraco in self.pos_buracos:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if abs(i) + abs(j) == 1:
                        y, x = buraco[0] + i, buraco[1] + j
                        if 0 <= y < self.tamanho and 0 <= x < self.tamanho: self.percepcoes['brisa'][y, x] = True
                        
    def get_estado(self):
        
        y, x = self.pos_player
        fedor = self.percepcoes['fedor'][y, x]
        brisa = self.percepcoes['brisa'][y, x]
        pos_id = y * self.tamanho + x
        percep_id = (1 if fedor else 0) * 2 + (1 if brisa else 0)
        return pos_id * 4 + percep_id

    
    def step(self, acao, historico_set):
        
        if self.fim_de_jogo: return self.get_estado(), 0, True
        if acao == 4:
            if not self.tem_flecha: return self.get_estado(), -10, False
            self.tem_flecha = False
            if self.pos_player[0] == self.pos_wumpus[0] or self.pos_player[1] == self.pos_wumpus[1]:
                self.wumpus_vivo = False; self._gerar_percepcoes(); return self.get_estado(), 50, False
            else: return self.get_estado(), -10, False
        pos_anterior = list(self.pos_player)
        if   acao == 0 and self.pos_player[0] > 0: self.pos_player[0] -= 1
        elif acao == 1 and self.pos_player[0] < self.tamanho - 1: self.pos_player[0] += 1
        elif acao == 2 and self.pos_player[1] > 0: self.pos_player[1] -= 1
        elif acao == 3 and self.pos_player[1] < self.tamanho - 1: self.pos_player[1] += 1
        
        if self.pos_player == self.pos_ouro: recompensa = 1000; self.fim_de_jogo = True
        elif self.wumpus_vivo and self.pos_player == self.pos_wumpus: recompensa = -1000; self.fim_de_jogo = True
        elif self.pos_player in self.pos_buracos: recompensa = -1000; self.fim_de_jogo = True
        elif self.pos_player == pos_anterior: recompensa = -5
        else: recompensa = -1

        
        if tuple(self.pos_player) in historico_set:
             recompensa -= 2

        return self.get_estado(), recompensa, self.fim_de_jogo
    
    def render(self, titulo=""):
        
        os.system('cls' if os.name == 'nt' else 'clear'); print(f"=== {titulo} ===")
        y_p, x_p = self.pos_player
        print(f"Posição: [{y_p}, {x_p}] | Flecha: {'Sim' if self.tem_flecha else 'Não'} | Wumpus: {'Vivo' if self.wumpus_vivo else 'Morto'}")
        percepcoes_str = []
        if self.percepcoes['fedor'][y_p, x_p]: percepcoes_str.append('Fedor')
        if self.percepcoes['brisa'][y_p, x_p]: percepcoes_str.append('Brisa')
        print(f"Percepções: {' e '.join(percepcoes_str) if percepcoes_str else 'Nada'}")
        grid = [['.' for _ in range(self.tamanho)] for _ in range(self.tamanho)]
        for br in self.pos_buracos: grid[br[0]][br[1]] = 'B'
        if self.wumpus_vivo: grid[self.pos_wumpus[0]][self.pos_wumpus[1]] = 'W'
        grid[self.pos_ouro[0]][self.pos_ouro[1]] = 'O'
        grid[self.pos_player[0]][self.pos_player[1]] = 'P'
        print("\n--- Visão do Jogo (Debug) ---")
        for linha in grid: print(" ".join(linha))

class AgenteSARSA:
    def __init__(self, tamanho_ambiente=4, num_acoes=5):
        self.tamanho_estado = tamanho_ambiente * tamanho_ambiente * 4
        self.num_acoes = num_acoes
        self.q_table = np.zeros((self.tamanho_estado, self.num_acoes))
        self.epsilon = EPSILON

    def escolher_acao(self, estado):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.num_acoes - 1)
        else:
            return np.argmax(self.q_table[estado])

    def treinar(self, ambiente):
       
        recompensas_por_episodio = []
        
        for episodio in range(EPISODIOS):
            estado = ambiente.reset()
            
           
            historico_set = {tuple(ambiente.pos_player)}

            acao = self.escolher_acao(estado)
            fim_de_jogo = False
            
            while not fim_de_jogo:
                proximo_estado, recompensa, fim_de_jogo = ambiente.step(acao, historico_set)
                historico_set.add(tuple(ambiente.pos_player))

                proxima_acao = self.escolher_acao(proximo_estado)
                
                valor_antigo = self.q_table[estado, acao]
                valor_futuro = self.q_table[proximo_estado, proxima_acao]
                novo_valor = valor_antigo + TAXA_APRENDIZADO * (recompensa + FATOR_DESCONTO * valor_futuro - valor_antigo)
                self.q_table[estado, acao] = novo_valor
                
                estado, acao = proximo_estado, proxima_acao

            if self.epsilon > EPSILON_MIN: self.epsilon *= DECAIMENTO_EPSILON
            if (episodio + 1) % 2000 == 0:
                print(f"Episódio {episodio + 1}/{EPISODIOS} - Epsilon: {self.epsilon:.4f}")

    def executar(self):
        
        if np.sum(self.q_table) == 0:
            print("\nERRO: A Q-Table está vazia. Treine o agente primeiro."); return
        print("\n--- Executando Agente Treinado ---")
        ambiente = WumpusMundo()
        estado = ambiente.reset()
        fim_de_jogo = False
        while not fim_de_jogo:
            ambiente.render(titulo="Execução")
            acao = np.argmax(self.q_table[estado])
            print(f"\nEstado: {estado}, Ação Escolhida: {ACOES[acao]}")
            time.sleep(0.3)
            estado, _, fim_de_jogo = ambiente.step(acao, set())
            if ambiente.pos_player == ambiente.pos_ouro or (ambiente.wumpus_vivo and ambiente.pos_player == ambiente.pos_wumpus) or (ambiente.pos_player in ambiente.pos_buracos):
                fim_de_jogo = True
        ambiente.render(titulo="Resultado Final")

def menu():
    agente = AgenteSARSA(num_acoes=5)
    ambiente_de_treino = WumpusMundo() 
    while True:
        print("\n=== MUNDO DE WUMPUS COMPLETO - AGENTE SARSA (Otimizado) ===")
        print("1. Treinar o Agente")
        print("2. Executar Agente Treinado")
        print("3. Sair")
        opcao = input("Escolha: ")
        if opcao == "1": agente.treinar(ambiente_de_treino)
        elif opcao == "2": agente.executar()
        elif opcao == "3": break
        else: print("Opção inválida.")

if __name__ == "__main__":
    menu()