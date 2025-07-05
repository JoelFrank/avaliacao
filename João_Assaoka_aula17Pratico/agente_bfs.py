import streamlit as st
import regras
from collections import deque

# ---- Utilidades ----------------------------------------------------------------

Movimento = str  # 'cima' | 'baixo' | 'esquerda' | 'direita'
Coordenada = tuple[int, int]  # (x, y)
DIRECOES: dict[Movimento, tuple[int, int]] = {
    'cima': (-1, 0),
    'baixo': (1, 0),
    'esquerda': (0, -1),
    'direita': (0, 1),
}

def dentro_limites(x: int, y: int, n: int) -> bool:
    """Verifica se (x, y) está dentro do tabuleiro n×n."""
    return 0 <= x < n and 0 <= y < n

def busca_em_largura(inicio: Coordenada, objetivos: set[Coordenada], bloqueados: set[Coordenada], n: int) -> list[Movimento]:
    """Encontra o menor caminho (BFS) de *inicio* até qualquer destino em *objetivos*.

    Evita casas em *bloqueados*. Retorna None se não houver caminho.
    """
    fila = deque([inicio])
    pais: dict[Coordenada, Coordenada] = {inicio: inicio}
    while fila:
        x, y = fila.popleft()
        if (x, y) in objetivos:
            # Reconstrói o caminho
            caminho: list[Movimento] = []
            while (x, y) != inicio:
                px, py = pais[(x, y)]
                dx, dy = x - px, y - py
                for mov, (ddx, ddy) in DIRECOES.items():
                    if (ddx, ddy) == (dx, dy):
                        caminho.append(mov)
                        break
                x, y = px, py
            caminho.reverse()
            return caminho
        for mov, (ddx, ddy) in DIRECOES.items():
            nx, ny = x + ddx, y + ddy
            if not dentro_limites(nx, ny, n) or (nx, ny) in bloqueados or (nx, ny) in pais:
                continue
            pais[(nx, ny)] = (x, y)
            fila.append((nx, ny))
    return None

def direcao(origem: Coordenada, destino: Coordenada) -> Movimento:
    """Determina a direção que leva *origem* → *destino*."""
    ox, oy = origem
    dx, dy = destino
    delta_x, delta_y = dx - ox, dy - oy
    for mov, (ddx, ddy) in DIRECOES.items():
        if (ddx, ddy) == (delta_x, delta_y):
            return mov
    raise ValueError("Células não adjacentes")

def executar_movimento(mov: Movimento) -> None:
    """Executa o movimento chamando a função correspondente em regras.py."""
    if mov == 'cima':
        regras.mover_cima()
    elif mov == 'baixo':
        regras.mover_baixo()
    elif mov == 'esquerda':
        regras.mover_esquerda()
    elif mov == 'direita':
        regras.mover_direita()
    else:
        raise ValueError(mov)

def executar_caminho(caminho: list[Movimento]) -> None:
    """Executa uma sequência de movimentos."""
    for mov in caminho:
        executar_movimento(mov)

# ---- Planejamento ----------------------------------------------------------------

def celulas_adjacentes(coord: Coordenada, n: int) -> list[Coordenada]:
    """Retorna as células adjacentes válidas."""
    x, y = coord
    adjacentes = []
    for dx, dy in DIRECOES.values():
        nx, ny = x + dx, y + dy
        if dentro_limites(nx, ny, n):
            adjacentes.append((nx, ny))
    return adjacentes

def encontrar_posicoes(flag: int) -> list[Coordenada]:
    """Encontra todas as posições no tabuleiro com a flag especificada."""
    tabuleiro = st.session_state.tabuleiro
    n = len(tabuleiro)
    posicoes = []
    for i in range(n):
        for j in range(n):
            if tabuleiro[i][j][flag]:
                posicoes.append((i, j))
    return posicoes

# ---- Rotina Principal -----------------------------------------------------------

def executar_agente() -> None:
    """Planeja e executa o plano completo do agente."""
    # Coleta informações do tabuleiro
    tabuleiro = st.session_state.tabuleiro
    n = len(tabuleiro)

    inicio = st.session_state.atual
    buracos: set[Coordenada] = {
        (i, j) for i in range(n) for j in range(n) if tabuleiro[i][j][regras.BURACO]
    }
    pos_wumpus_vivo = encontrar_posicoes(regras.WUMPUS_VIVO)
    pos_ouro = encontrar_posicoes(regras.OURO)

    # Eliminar o Wumpus
    if pos_wumpus_vivo:
        wumpus = pos_wumpus_vivo[0]  # Existe apenas um Wumpus
        adjacentes_seguras = {
            c for c in celulas_adjacentes(wumpus, n) if c not in buracos
        }
        caminho_ate_adjacente = busca_em_largura(inicio, adjacentes_seguras, buracos | {wumpus}, n)
        if caminho_ate_adjacente is None:
            st.session_state.sentidos += "🤖 **Agente falhou**: não há caminho até posição de tiro no Wumpus.\n\n"
            return
        executar_caminho(caminho_ate_adjacente)

        # Determinar direção para atirar
        atual = st.session_state.atual
        direcao_tiro = direcao(atual, wumpus)
        st.session_state.atirar = True  # Marca checkbox interna
        executar_movimento(direcao_tiro)  # Dispara + entra na casa do Wumpus

        # Atualiza referência
        inicio = st.session_state.atual

    # Coletar ouro
    pos_ouro = encontrar_posicoes(regras.OURO)  # Atualiza lista (talvez ouro na casa do Wumpus)
    for ouro in pos_ouro:
        caminho = busca_em_largura(inicio, {ouro}, buracos, n)
        if caminho is None:
            continue  # Ignora se ouro inacessível
        executar_caminho(caminho)
        regras.pegar_ouro()
        inicio = st.session_state.atual

    if not st.session_state.ouro_coletado:
        st.session_state.sentidos += "😕 **Agente falhou**: não conseguiu coletar ouro.\n\n"
        return

    # Voltar para a saída
    caminho_para_saida = busca_em_largura(inicio, {(0, 0)}, buracos, n)
    if caminho_para_saida is None:
        st.session_state.sentidos += "😕 **Agente falhou**: não há caminho de volta à saída.\n\n"
        return
    executar_caminho(caminho_para_saida)
    regras.escalar_caverna()
