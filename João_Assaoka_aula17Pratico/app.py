# app.py
import streamlit as st
import regras  # módulo com a lógica do jogo
import agente_bfs  # módulo com o agente de busca em largura
import agente_qlearning

st.set_page_config(page_title="Mundo de Wumpus", layout="wide")

# ---------- Sidebar – parâmetros de jogo ----------
with st.sidebar.expander("⚙️ Configuração do Jogo", expanded=True):
    st.number_input("Número de Quadrantes (N x N)",
                    min_value=3, max_value=10, value=3, step=1,
                    key="num_quadrantes")
    st.number_input("Número de Flechas",
                    min_value=1, max_value=10, value=1, step=1,
                    key="num_flechas")
    st.number_input("Quantidade de Ouro",
                    min_value=1, max_value=10, value=1, step=1,
                    key="num_ouro")
    st.number_input("Quantidade de Buracos",
                    min_value=1, max_value=10, value=1, step=1,
                    key="num_buracos")

    # validação básica
    total_itens = st.session_state.num_ouro + st.session_state.num_buracos + 1
    max_casas = st.session_state.num_quadrantes ** 2
    if total_itens > max_casas:
        st.error("A soma de Ouro, Buracos e o Wumpus não pode exceder o número de quadrantes.")
        st.stop()

# ---------- Sidebar – informações do jogo ----------
with st.sidebar.expander("🤖 Agentes"):
    st.button("Agente BFS", on_click=agente_bfs.executar_agente, use_container_width=True)
    st.button("Agente Q-learning", on_click=agente_qlearning.executar_agente_qlearning, use_container_width=True)

# ---------- Reinício ou primeira execução ----------
if (
    "tabuleiro" not in st.session_state or
    st.session_state.num_quadrantes != len(st.session_state.tabuleiro) or
    st.sidebar.button("🔄 Reiniciar Jogo", use_container_width=True)    
):
    regras.criar_tabuleiro()
    st.session_state.atual = (0, 0)
    st.session_state.sentidos = ""
    st.session_state.flechas = st.session_state.num_flechas
    st.session_state.ouro_coletado = False
    st.session_state.wumpus_vivo = True
    st.session_state.pontuacao = 0
    # revela casa inicial
    regras.sentidos(0, 0)

# ---------- Renderização do tabuleiro ----------
N = st.session_state.num_quadrantes
cols = st.columns(N + 1)  # última coluna = painel de ações

for i in range(N):
    for j in range(N):
        cell = st.session_state.tabuleiro[i][j]
        # imagem
        if (i, j) == st.session_state.atual:
            cols[j].image("atual.png", use_container_width=True)
        elif cell[regras.VISITADO]:
            cols[j].image("visitado.png", use_container_width=True)
        else:
            cols[j].image("segredo.png", use_container_width=True)

        # miniexpander debug‑friendly (pode ocultar se preferir)
        _ = ''' with cols[j].expander(f"{i}, {j}", expanded=False):
            st.write(f"""
Visitado: {cell[regras.VISITADO]}
Buraco: {cell[regras.BURACO]}
Vento: {cell[regras.VENTO]}
Ouro: {cell[regras.OURO]}
Wumpus Vivo: {cell[regras.WUMPUS_VIVO]}
Fedor: {cell[regras.FEDOR]}
Wumpus Morto: {cell[regras.WUMPUS_MORTO]}
""")'''

# ---------- Painel de ações (última coluna) ----------
with cols[-1]:
    st.checkbox("Atirar", value=False, key="atirar")

    st.button("Mover ↑", on_click=regras.mover_cima, use_container_width=True)
    st.button("Mover ↓", on_click=regras.mover_baixo, use_container_width=True)
    st.button("Mover ←", on_click=regras.mover_esquerda, use_container_width=True)
    st.button("Mover →", on_click=regras.mover_direita, use_container_width=True)

    st.divider()
    st.button("🏆 Pegar Ouro", on_click=regras.pegar_ouro, use_container_width=True)
    st.button("🧗 Escalar (sair)", on_click=regras.escalar_caverna, use_container_width=True)

    st.divider()
    st.markdown(f"**Flechas restantes:** {st.session_state.flechas}")
    st.markdown(f"**Pontuação:** {st.session_state.pontuacao}")

# ---------- Painel de feedback / sentidos ----------
with st.sidebar.expander("🗣️ Sentidos do Agente", expanded=True):
    st.markdown(st.session_state.sentidos) 