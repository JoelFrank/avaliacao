import random
import copy
from collections import defaultdict
import numpy as np

# Parâmetros
TAMANHO = 4
AÇÕES = ["andar", "girar_direita", "girar_esquerda", "atirar", "pegar_ouro", "escalar"]
direcoes = ["norte", "leste", "sul", "oeste"]

# Tabela Q para armazenar os valores de estado-ação
Q = defaultdict(float)

# Parâmetros do Q-Learning
alpha = 0.1      # Taxa de aprendizado
gamma = 0.99     # Fator de desconto
epsilon = 1.0    # Chance de exploração (ação aleatória)
epsilon_min = 0.05 # Mínimo de exploração
decay_rate = 0.9995 # Decaimento do epsilon por episódio
episodios = 5000

RECOMPENSAS = {
    "vitoria": 1000,      # Escapar com o ouro
    "ouro": 100,          # Pegar o ouro
    "morte": -1000,       # Cair no poço ou ser pego pelo Wumpus
    "matar_wumpus": 10,   # Bônus por matar o Wumpus
    "passo": -1,          # Custo de cada ação
    "flecha_perdida": -10 # Penalidade por atirar e errar
}

def resetar_ambiente():
    """ Gera um novo ambiente aleatório para um episódio. """
    matriz = [["" for _ in range(TAMANHO)] for _ in range(TAMANHO)]
    posicoes_ocupadas = set()
    posicoes_ocupadas.add((0, 0))

    def gerar_posicao():
        while True:
            x, y = random.randint(0, TAMANHO - 1), random.randint(0, TAMANHO - 1)
            if (x, y) not in posicoes_ocupadas:
                posicoes_ocupadas.add((x, y))
                return [x, y]

    pos_ouro = gerar_posicao()
    matriz[pos_ouro[0]][pos_ouro[1]] += "O"
    pos_wumpus = gerar_posicao()
    matriz[pos_wumpus[0]][pos_wumpus[1]] += "W"
    num_pocos = random.randint(1, 3)
    for _ in range(num_pocos):
        x, y = gerar_posicao()
        matriz[x][y] += "P"

    return {
        "matriz": matriz,
        "agente": [0, 0],
        "direcao": "leste",
        "pegou_ouro": False,
        "flecha": True,
        "wumpus_vivo": True,
        "ouro": pos_ouro,
        "wumpus": pos_wumpus,
        "fim": False
    }

def obter_percepcoes(env):
    x, y = env["agente"]
    tem_brisa = False
    tem_fedor = False
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < TAMANHO and 0 <= ny < TAMANHO:
            if "P" in env["matriz"][nx][ny]:
                tem_brisa = True
            if "W" in env["matriz"][nx][ny]:
                tem_fedor = True
    return tem_fedor, tem_brisa

def codificar_estado(env):
    tem_fedor, tem_brisa = obter_percepcoes(env)
    return (
        tuple(env["agente"]),
        env["direcao"],
        env["pegou_ouro"],
        env["wumpus_vivo"],
        tem_fedor,
        tem_brisa
    )

def escolher_acao(estado):
    if random.uniform(0, 1) < epsilon:
        return random.choice(AÇÕES)
    else:
        q_vals = [Q[(estado, a)] for a in AÇÕES]
        max_q = max(q_vals)
        melhores_acoes = [a for a, q in zip(AÇÕES, q_vals) if q == max_q]
        return random.choice(melhores_acoes)

def aplicar_acao(env, acao):
    recompensa = RECOMPENSAS["passo"]
    x, y = env["agente"]
    direcao = env["direcao"]

    if acao == "andar":
        dx, dy = 0, 0
        if direcao == "norte": dx = -1
        elif direcao == "sul": dx = 1
        elif direcao == "leste": dy = 1
        elif direcao == "oeste": dy = -1
        nx, ny = x + dx, y + dy
        if 0 <= nx < TAMANHO and 0 <= ny < TAMANHO:
            env["agente"] = [nx, ny]
    elif acao == "girar_direita":
        idx = (direcoes.index(direcao) + 1) % 4
        env["direcao"] = direcoes[idx]
    elif acao == "girar_esquerda":
        idx = (direcoes.index(direcao) - 1) % 4
        env["direcao"] = direcoes[idx]
    elif acao == "atirar":
        if env["flecha"]:
            env["flecha"] = False
            dx, dy = 0, 0
            if direcao == "norte": dx = -1
            elif direcao == "sul": dx = 1
            elif direcao == "leste": dy = 1
            elif direcao == "oeste": dy = -1
            acertou = False
            ax, ay = x + dx, y + dy
            while 0 <= ax < TAMANHO and 0 <= ay < TAMANHO:
                if [ax, ay] == env["wumpus"] and env["wumpus_vivo"]:
                    recompensa += RECOMPENSAS["matar_wumpus"]
                    env["wumpus_vivo"] = False
                    acertou = True
                    break
                ax += dx
                ay += dy
            if not acertou:
                recompensa += RECOMPENSAS["flecha_perdida"]
    elif acao == "pegar_ouro":
        if env["agente"] == env["ouro"] and not env["pegou_ouro"]:
            recompensa += RECOMPENSAS["ouro"]
            env["pegou_ouro"] = True
    elif acao == "escalar":
        if env["agente"] == [0, 0]:
            if env["pegou_ouro"]:
                recompensa += RECOMPENSAS["vitoria"]
                env["fim"] = True
            else:
                recompensa += RECOMPENSAS["morte"] / 20
                env["fim"] = True
    
    novo_x, novo_y = env["agente"]
    celula_atual = env["matriz"][novo_x][novo_y]
    if "P" in celula_atual or ("W" in celula_atual and env["wumpus_vivo"]):
        recompensa += RECOMPENSAS["morte"]
        env["fim"] = True

    return recompensa, codificar_estado(env), env["fim"]

ambiente_real = resetar_ambiente()

print("Mapa Fixo Gerado para Treinamento e Avaliação:")
for linha in ambiente_real["matriz"]:
    print(f"  {linha}")
print(f"Posição Ouro: {ambiente_real['ouro']}, Posição Wumpus: {ambiente_real['wumpus']}\n")

print(f"Iniciando treinamento por {episodios} episódios no mapa fixo...")

for ep in range(episodios):
    env = copy.deepcopy(ambiente_real)
    estado = codificar_estado(env)
    passos = 0

    while not env["fim"] and passos < 100:
        acao = escolher_acao(estado)
        recompensa, novo_estado, fim = aplicar_acao(env, acao)
        
        melhor_q_proximo = max([Q[(novo_estado, a)] for a in AÇÕES])
        q_antigo = Q[(estado, acao)]
        novo_q = q_antigo + alpha * (recompensa + gamma * melhor_q_proximo - q_antigo)
        Q[(estado, acao)] = novo_q

        estado = novo_estado
        passos += 1

    epsilon = max(epsilon_min, epsilon * decay_rate)


print("Treinamento concluído!")

print("Iniciando avaliação no mesmo mapa em que foi treinado...")
epsilon = 0

env_final = copy.deepcopy(ambiente_real)
estado = codificar_estado(env_final)
trajetoria = [(estado, None)]
recompensa_final = 0

passos = 0
while not env_final["fim"] and passos < 50:
    acao = escolher_acao(estado)
    recompensa, novo_estado, fim = aplicar_acao(env_final, acao)
    
    trajetoria.append((novo_estado, acao))
    estado = novo_estado
    recompensa_final += recompensa
    passos += 1

print("\nTrajetória executada pelo agente treinado:")
for i, (est, ac) in enumerate(trajetoria):
    if ac:
      print(f"Passo {i}: Estado = {trajetoria[i-1][0]}")
      print(f"       -> Ação: {ac} -> Novo Estado: {est}")

print(f"Fim da execução. Recompensa total: {recompensa_final}")
if env_final["pegou_ouro"] and env_final["agente"] == [0,0]:
    print("Resultado: SUCESSO! O agente memorizou o caminho e escapou com o ouro.")
elif not env_final["fim"]:
     print("Resultado: FALHA. O agente não encontrou a saída a tempo.")
else:
    print("Resultado: FALHA. O agente morreu.")

    #referências: gemini e slides da aula de IA