# agente_qlearning.py
import streamlit as st
import numpy as np
import random
import regras
import time
import pandas as pd

# Ações possíveis para o agente, incluindo atirar
ACTIONS = ['cima', 'baixo', 'esquerda', 'direita',
           'atirar_cima', 'atirar_baixo', 'atirar_esquerda', 'atirar_direita']

def get_state():
    """ Constrói o estado atual a partir das variáveis de sessão do Streamlit. """
    x, y = st.session_state.atual
    ouro = st.session_state.ouro_coletado
    wumpus = st.session_state.wumpus_vivo
    return (x, y, ouro, wumpus)

def get_reward(old_score):
    """ Calcula a recompensa com base na variação da pontuação. """
    return st.session_state.pontuacao - old_score

def perform_action(action):
    """ Executa a ação escolhida no ambiente, lidando com movimento e tiro. """
    if action.startswith('atirar_'):
        direction = action.split('_')[1]
        st.session_state.atirar = True  # Prepara para atirar
        if direction == 'cima':
            regras.mover_cima()
        elif direction == 'baixo':
            regras.mover_baixo()
        elif direction == 'esquerda':
            regras.mover_esquerda()
        elif direction == 'direita':
            regras.mover_direita()
    else:
        # Movimento normal
        if action == 'cima':
            regras.mover_cima()
        elif action == 'baixo':
            regras.mover_baixo()
        elif action == 'esquerda':
            regras.mover_esquerda()
        elif action == 'direita':
            regras.mover_direita()

def display_policy_table(agent):
    """ Exibe a política ótima aprendida em duas tabelas simples. """
    st.markdown("### Política Ótima Aprendida pelo Agente")

    n = agent.n
    # Mapeia a ação para um símbolo mais legível
    action_map = {
        'cima': '↑ Mover', 'baixo': '↓ Mover', 'esquerda': '← Mover', 'direita': '→ Mover',
        'atirar_cima': '↑ Atirar', 'atirar_baixo': '↓ Atirar',
        'atirar_esquerda': '← Atirar', 'atirar_direita': '→ Atirar'
    }

    # Tabela 1: Buscando o ouro (estado: sem ouro, wumpus vivo)
    policy_data_ida = []
    for x in range(n):
        for y in range(n):
            state = (x, y, False, True)
            q_values = [agent.get_q_value(state, a) for a in ACTIONS]
            best_action = "N/A (Não explorado)"
            if any(q != 0.0 for q in q_values):
                best_action_key = ACTIONS[np.argmax(q_values)]
                best_action = action_map.get(best_action_key, best_action_key)
            policy_data_ida.append([f"({x}, {y})", best_action])

    df_ida = pd.DataFrame(policy_data_ida, columns=['Posição', 'Melhor Ação'])
    st.markdown("**Objetivo 1: Pegar o Ouro**")
    st.table(df_ida)

    # Tabela 2: Voltando para a saída (estado: com ouro, wumpus vivo)
    policy_data_volta = []
    for x in range(n):
        for y in range(n):
            state = (x, y, True, True)
            q_values = [agent.get_q_value(state, a) for a in ACTIONS]
            best_action = "N/A (Não explorado)"
            if any(q != 0.0 for q in q_values):
                best_action_key = ACTIONS[np.argmax(q_values)]
                best_action = action_map.get(best_action_key, best_action_key)
            policy_data_volta.append([f"({x}, {y})", best_action])

    df_volta = pd.DataFrame(policy_data_volta, columns=['Posição', 'Melhor Ação'])
    st.markdown("**Objetivo 2: Voltar para (0,0) com Ouro**")
    st.table(df_volta)


class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.3):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.n = st.session_state.num_quadrantes

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(ACTIONS)
        else:
            q_values = [self.get_q_value(state, a) for a in ACTIONS]
            max_q = max(q_values)
            best_actions = [a for a, q in zip(ACTIONS, q_values) if q == max_q]
            return random.choice(best_actions)

    def update_q_table(self, state, action, reward, next_state):
        old_q_value = self.get_q_value(state, action)
        next_max_q = max([self.get_q_value(next_state, a) for a in ACTIONS])
        new_q_value = old_q_value + self.alpha * (reward + self.gamma * next_max_q - old_q_value)
        self.q_table[(state, action)] = new_q_value
        
    def train(self, episodes=2000): # Aumentei um pouco os episódios devido à complexidade
        progress_bar = st.progress(0, text="Treinando o Agente Q-Learning...")
        
        for i in range(episodes):
            regras.criar_tabuleiro()
            st.session_state.atual = (0, 0)
            st.session_state.sentidos = ""
            st.session_state.flechas = st.session_state.num_flechas
            st.session_state.ouro_coletado = False
            st.session_state.wumpus_vivo = True
            st.session_state.pontuacao = 0
            regras.sentidos(0, 0)

            state = get_state()
            done = False
            max_steps = self.n ** 2 # Limite de passos por episódio
            
            for _ in range(max_steps):
                action = self.choose_action(state)
                old_score = st.session_state.pontuacao
                perform_action(action)
                
                x, y = st.session_state.atual
                if st.session_state.tabuleiro[x][y][regras.OURO] and not st.session_state.ouro_coletado:
                    regras.pegar_ouro()
                
                if st.session_state.ouro_coletado and st.session_state.atual == (0,0):
                    regras.escalar_caverna()

                reward = get_reward(old_score)
                next_state = get_state()
                
                if "Você morreu" in st.session_state.sentidos or "Você escapou" in st.session_state.sentidos:
                    done = True

                self.update_q_table(state, action, reward, next_state)
                state = next_state

                if done:
                    break

            progress_bar.progress((i + 1) / episodes, text=f"Treinando... Episódio {i+1}/{episodes}")

        st.success("Treinamento concluído!")
        st.session_state.sentidos = "🤖 **Agente treinado!** Veja a política aprendida abaixo. Use o botão na barra lateral para executar a melhor rota.\n\n"
        
    def run_best_policy(self):
        st.session_state.sentidos = "Executando a melhor política aprendida...\n\n"
        regras.criar_tabuleiro()
        st.session_state.atual = (0, 0)
        st.session_state.flechas = st.session_state.num_flechas
        st.session_state.ouro_coletado = False
        st.session_state.wumpus_vivo = True
        st.session_state.pontuacao = 0
        regras.sentidos(0, 0)

        done = False
        max_steps = self.n ** 2 * 2
        steps = 0

        while not done and steps < max_steps:
            state = get_state()
            q_values = [self.get_q_value(state, a) for a in ACTIONS]
            action = ACTIONS[np.argmax(q_values)]

            perform_action(action)
            
            x, y = st.session_state.atual
            if st.session_state.tabuleiro[x][y][regras.OURO] and not st.session_state.ouro_coletado:
                regras.pegar_ouro()
            
            if st.session_state.ouro_coletado and st.session_state.atual == (0,0):
                regras.escalar_caverna()
                
            if "Você morreu" in st.session_state.sentidos or "Você escapou" in st.session_state.sentidos:
                done = True
            
            steps += 1
            st.rerun()
            time.sleep(0.5)
        
        if not done:
            st.session_state.sentidos += "\n⚠️ O agente não conseguiu concluir o objetivo e pode ter entrado em um loop."


def treinar_agente():
    agent = QLearningAgent()
    agent.train()
    st.session_state.trained_agent = agent
    display_policy_table(agent)

def executar_politica_otima():
    if 'trained_agent' in st.session_state:
        agent = st.session_state.trained_agent
        agent.run_best_policy()
    else:
        st.error("Você precisa treinar o agente primeiro!")

def executar_agente_qlearning():
    # Treina o agente se ainda não foi treinado
    treinar_agente()
    
    # Executa a política ótima aprendida
    executar_politica_otima()