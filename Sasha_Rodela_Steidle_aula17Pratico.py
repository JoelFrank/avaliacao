# Sasha Rodela Steidle
# RA: 169233
# Bibliografia utilizada:
#   - Documentação do Python:
#         https://docs.python.org/3/
#   - https://medium.com/codex/temporal-difference-learning-sarsa-vs-q-learning-c367934b8bc
#   - https://www.geeksforgeeks.org/q-learning-in-python/

## A "parte importante" está a partir da linha 328 ##

from random import Random, randint
from time import time, perf_counter, sleep
from enum import Enum, auto
from dataclasses import dataclass
from typing import Iterable, Callable, Self, Generator
from abc import ABC, abstractmethod
from collections import namedtuple
from pprint import pprint
import sys
from scipy.sparse import dok_array as sparse_array
import numpy as np
from sys import argv


class Sentido(Enum):
    CHEIRO_RUIM = auto()
    BRISA = auto()
    GRITO = auto()
    BRILHO = auto()
    ATAQUE_WUMPUS = auto()
    PAREDE = auto()
    QUEDA_BURACO = auto()
    ESCALADA = auto()


class Compartimento(Enum):
    VAZIO = auto()
    WUMPUS = auto()
    WUMPUS_MORTO = auto()
    BURACO = auto()
    PAREDE = auto()
    OURO = auto()


def _debug_set_compartimento(x: set[Compartimento]) -> str:
    '''Retorna uma representação visual concisa de um conjunto de compartimentos.'''
    cs = [
        [Compartimento.VAZIO, 'V'],
        [Compartimento.WUMPUS, 'W'],
        [Compartimento.WUMPUS_MORTO, 'X'],
        [Compartimento.BURACO, 'B'],
        [Compartimento.PAREDE, 'P'],
        [Compartimento.OURO, 'O']
    ]
    retorno = []
    for c, s in cs:
        if c in x:
            retorno.append(s)
        else:
            retorno.append(' ')
    return ''.join(retorno)


@dataclass(frozen=True, eq=True)
class Ponto:
    '''Tupla de inteiros (x, y) com algumas funcionalidades extras para conveniência.'''
    x: int
    y: int

    def eh_adjacente_a(self, outro: Self) -> bool:
        '''Verifica se o ponto está ortogonalmente adjacente a outro.'''
        dx = abs(self.x - outro.x)
        dy = abs(self.y - outro.y)
        return dx + dy == 1

    def esta_na_matriz(self, tamanho_matriz: int) -> bool:
        '''
        Verifica se o ponto está dentro de uma matriz NxN, isto é, se
        ambas as coordenadas X e Y do ponto são não-negativas e menores que N.
        Argumentos:
        tamanho_matriz -- tamanho N da matriz quadrada.
        Retorna True se o ponto está na matriz.
        '''
        x_valido = self.x >= 0 and self.x < tamanho_matriz
        y_valido = self.y >= 0 and self.y < tamanho_matriz
        return x_valido and y_valido

    def __getitem__(self, idx) -> int:
        if idx:
            return self.y
        return self.x

    def __str__(self):
        return f'{self.x} {self.y}'

    def __add__(self, other):
        return Ponto(self.x + other.x, self.y + other.y)


class Matriz2D:
    '''
    Lista bidimensional que pode ser acessada usando tuplas ou instâncias de Ponto.
    Exemplo:
        matriz[i, j] = v  # Define como v o valor na linha j, coluna i.
        matriz[Ponto(i, j)]  # Equivalente
    '''
    def __init__(self, linhas: int, colunas: int, valor_inicial, funcao_repr=str):
        self._elementos = [valor_inicial for _ in range(linhas*colunas)]
        self._linhas = linhas
        self._colunas = colunas
        self._funcao_repr = funcao_repr

    def __getitem__(self, idx: tuple[int, int] | Ponto):
        return self._elementos[idx[0] + idx[1] * self._colunas]

    def __setitem__(self, idx: tuple[int, int] | Ponto, valor):
        self._elementos[idx[0] + idx[1] * self._colunas] = valor

    def __str__(self) -> str:
        r = []
        for linha in range(self._linhas):
            r.append('\t'.join(self._funcao_repr(self[linha, coluna]) for coluna in range(self._colunas)))
        return '\n'.join(r) + '\n'
    
    def copy(self):
        m = Matriz2D(self._linhas, self._colunas, None)
        for i in range(self._linhas):
            for j in range(self._colunas):
                m[i, j] = self[i, j]
        return m


class Caverna:
    def __init__(self, tamanho: int, rng: Random):
        self.tamanho = tamanho + 2
        self.compartimentos = Matriz2D(
            linhas=self.tamanho,
            colunas=self.tamanho,
            valor_inicial=Compartimento.VAZIO,
        )
        for x in range(self.tamanho):
            self.compartimentos[x, 0] = Compartimento.PAREDE
            self.compartimentos[x, self.tamanho - 1] = Compartimento.PAREDE
        for y in range(self.tamanho):
            self.compartimentos[0, y] = Compartimento.PAREDE
            self.compartimentos[self.tamanho - 1, y] = Compartimento.PAREDE

        self._colocar_em_ponto_aleatorio(Compartimento.WUMPUS, rng)
        self._colocar_em_ponto_aleatorio(Compartimento.OURO, rng)
        quantidade_buracos_paredes = tamanho*tamanho//8
        for _ in range(quantidade_buracos_paredes):
            self._colocar_em_ponto_aleatorio(Compartimento.BURACO, rng)
            self._colocar_em_ponto_aleatorio(Compartimento.PAREDE, rng)

    def _colocar_em_ponto_aleatorio(self, compart: Compartimento, rng: Random):
        '''Coloca um compartimento `compart` em um local aleatório da caverna que esteja vazio.'''

        while 1:
            posicao_inicial = Ponto(1, 1)
            x = rng.randrange(0, self.tamanho)
            y = rng.randrange(0, self.tamanho)
            p = Ponto(x, y)
            if p != posicao_inicial and self.compartimentos[p] == Compartimento.VAZIO:
                self.compartimentos[p] = compart
                break

    def ler_sentidos(self, posicao: Ponto) -> set[Sentido]:
        '''Retorna o conjunto dos sentidos que são percebidos por um agente localizado no ponto `posicao`.'''

        res = set()
        if self.compartimentos[posicao] == Compartimento.OURO:
            res.add(Sentido.BRILHO)
        for pt in offsets_validos(posicao, self.tamanho):
            comp = self.compartimentos[pt]
            if comp in [Compartimento.WUMPUS, Compartimento.WUMPUS_MORTO]:
                res.add(Sentido.CHEIRO_RUIM)
            elif comp == Compartimento.BURACO:
                res.add(Sentido.BRISA)
        return res


class Jogo:
    '''Caverna + o restante do estado do jogo, como flechas, pontuação, posição do agente e se o ouro foi pego.'''

    def __init__(self, tamanho_caverna: int, rng: Random):
        self.caverna = Caverna(tamanho_caverna, rng)
        for i in range(self.caverna.tamanho):
            for j in range(self.caverna.tamanho):
                if self.caverna.compartimentos[i, j] == Compartimento.OURO:
                    self.pos_ouro = Ponto(i, j)
        self.reset()
    
    def reset(self):
        self.posicao_agente = Ponto(1, 1)
        self.flechas = 1
        self.pontuacao = 0
        self.acabou = False
        self.pegou_ouro = False
        self.caverna.compartimentos[self.pos_ouro] = Compartimento.OURO
        for i in range(self.caverna.tamanho):
            for j in range(self.caverna.tamanho):
                if self.caverna.compartimentos[i, j] == Compartimento.WUMPUS_MORTO:
                    self.caverna.compartimentos[i, j] = Compartimento.WUMPUS

    def acao_mover(self, nova_pos: Ponto) -> tuple[set[Sentido], bool]:
        '''
        Processa uma ação de movimento para a posição `nova_pos`.
        Então, retorna o conjunto dos sentidos percebidos pelo agente após a ação e
        um valor booleano verdadeiro se a ação foi executada corretamente e falso caso contrário.
        '''

        if not nova_pos.eh_adjacente_a(self.posicao_agente):
            return set(), False

        cp = self.caverna.compartimentos[nova_pos]
        res = self.caverna.ler_sentidos(nova_pos)
        self.pontuacao -= 1
        ok = True

        if cp == Compartimento.BURACO:
            res.add(Sentido.QUEDA_BURACO)
            self.pontuacao -= 100
            self.acabou = True
        elif cp == Compartimento.PAREDE:
            res.add(Sentido.PAREDE)
            ok = False
        elif cp == Compartimento.WUMPUS:
            res.add(Sentido.ATAQUE_WUMPUS)
            self.pontuacao -= 100
            self.acabou = True
        else:
            self.posicao_agente = nova_pos

        return res, ok

    def acao_atirar(self, pos_ataque: Ponto) -> tuple[set[Sentido], bool]:
        '''
        Processa uma ação de atirar na posição `pos_ataque`.
        Então, retorna o conjunto dos sentidos percebidos pelo agente após a ação e
        um valor booleano verdadeiro se a ação foi executada corretamente e falso caso contrário.
        '''

        if self.flechas <= 0:
            return set(), False
        if not pos_ataque.eh_adjacente_a(self.posicao_agente):
            return set(), False
        self.pontuacao -= 1
        self.flechas -= 1
        res = self.caverna.ler_sentidos(self.posicao_agente)
        if self.caverna.compartimentos[pos_ataque] == Compartimento.WUMPUS:
            res.add(Sentido.GRITO)
            self.caverna.compartimentos[pos_ataque] = Compartimento.WUMPUS_MORTO
            self.pontuacao += 50
        return res, True

    def acao_pegar_ouro(self) -> tuple[set[Sentido], bool]:
        '''
        Processa a ação de pegar ouro na posição atual do agente.
        Então, retorna o conjunto dos sentidos percebidos pelo agente após a ação e
        um valor booleano verdadeiro se a ação foi executada corretamente e falso caso contrário.
        '''
        self.pontuacao -= 1
        res = self.caverna.ler_sentidos(self.posicao_agente)
        if self.caverna.compartimentos[self.posicao_agente] == Compartimento.OURO:
            self.pegou_ouro = True
            self.caverna.compartimentos[self.posicao_agente] = Compartimento.VAZIO
            return res, True
        return res, False

    def acao_escalar(self) -> tuple[set[Sentido], bool]:
        '''
        Processa a ação de escalar (i.e. sair da caverna).
        Então, retorna o conjunto dos sentidos percebidos pelo agente após a ação e
        um valor booleano verdadeiro se a ação foi executada corretamente e falso caso contrário.
        '''
        self.pontuacao -= 1
        if self.posicao_agente == Ponto(1, 1):
            if self.pegou_ouro:
                self.pontuacao += 50
            self.acabou = True
            return {Sentido.ESCALADA}, True
        return self.caverna.ler_sentidos(self.posicao_agente), False


class TipoAcao(Enum):
    MOVER = auto()
    ATIRAR = auto()
    PEGAR_OURO = auto()
    ESCALAR = auto()
    FINALIZAR_JOGO = auto()


@dataclass(frozen=True)
class Acao:
    tipo: TipoAcao
    direcao: str

    def __lt__(self, outro: 'Acao') -> bool:
        return False


class Agente(ABC):
    '''Tipo abstrato para agentes.'''

    @abstractmethod
    def inicializar(self, tamanho_caverna: int) -> None:
        '''Inicializa o agente para um dado tamanho da caverna (quadrada).'''
        return NotImplemented

    @abstractmethod
    def agir(self, sentidos: set[Sentido], pontuacao: int) -> Generator[Acao, tuple[int, set[Sentido], bool], None]:
        '''
        Recebe o conjunto dos sentidos percebidos pelo agente e a pontuação atual.
        Então, retorna um gerador que produz a ação a ser feita e espera que sejam
        enviados a nova pontuação após a ação, o conjunto de sentidos após a ação e
        um valor verdadeiro se a ação foi válida, e falso se ela não pôde ser executada.

        Embora essa solução não seja muito elegante, ela garante totalmente que o agente
        não tem acesso às informações internas do jogo.
        '''
        return NotImplemented


Estado = namedtuple('Estado', ['posicao', 'flechas', 'pegou_ouro', 'sentidos', 'matou_wumpus', 'memorias'])


class AgenteQLearning(Agente):  # <-- Implementação do agente aqui!
    '''
    Esse agente aprende a jogar conforme joga o jogo do Wumpus. A Q-tabela
    é inicializada com zeros ao instanciar o objeto, e persiste entre jogos,
    desde que o tamanho das cavernas seja o mesmo.
    '''

    def resetar_qtabela(self, tamanho_caverna: int):
        estados = 2 * 2 * 2 * 2  # sentindo cheiro ruim, brisa, parede e brilho
        estados *= tamanho_caverna * tamanho_caverna
        estados *= 2  # possui ou não a flecha
        estados *= 2  # pegou ou não o ouro
        estados *= 2  # matou o wumpus
        estados *= tamanho_caverna * tamanho_caverna * 2 * 2  # memórias

        acoes = 2  # escalar e pegar ouro
        acoes += 4  # 4 direções de movimento
        acoes += 4  # 4 direções para atirar

        self.estados = estados
        self.acoes = acoes
        self.qtabela = np.zeros((acoes, estados), dtype=np.float64) #sparse_array((estados, acoes), dtype=int)

    def indice_estado(self, estado: Estado) -> int:
        '''Mapeia cada estado possível a um índice na Q-tabela.'''
        sentidos = 0
        t2 = self.tamanho_ambiente * self.tamanho_ambiente
        for i, sentido in enumerate([Sentido.CHEIRO_RUIM, Sentido.BRISA, Sentido.PAREDE, Sentido.BRILHO]):
            if sentido in estado.sentidos:
                sentidos |= 1 << i
        posicao = estado.posicao.x + estado.posicao.y * self.tamanho_ambiente
        flechas = 1 if estado.flechas else 0
        pegou_ouro = 1 if estado.pegou_ouro else 0
        matou_wumpus = 1 if estado.matou_wumpus else 0
        memorias = posicao * 4
        mem = estado.memorias[estado.posicao]
        if Sentido.CHEIRO_RUIM in mem:
            memorias += 1
        if Sentido.BRISA in mem:
            memorias += 2
        return sentidos + posicao*16 + flechas*16*t2 + pegou_ouro*16*t2*2 + memorias*16*t2*2*2 + matou_wumpus*16*t2*2*2*t2*4

    def __init__(self, tamanho_caverna: int, epsilon: float, taxa_aprendizado: float, desconto: float):
        self.epsilon = epsilon
        self.taxa_aprendizado = taxa_aprendizado
        self.desconto = desconto
        self.resetar_qtabela(tamanho_caverna)
        self.tamanho_ambiente = tamanho_caverna
        self.rng = Random()
        self.estado_atual = None
        super().__init__()

    def inicializar(self, tamanho_caverna: int) -> None:
        if self.tamanho_ambiente != tamanho_caverna:
            self.tamanho_ambiente = tamanho_caverna
            self.resetar_qtabela(tamanho_caverna)
        memoria_vazia = Matriz2D(tamanho_caverna, tamanho_caverna, set())
        self.estado_atual = Estado(Ponto(1, 1), 1, False, set(), False, memoria_vazia)

    def indice_acao(self, acao: Acao) -> int:
        '''Mapeia cada ação a um índice na Q-tabela.'''
        if acao.tipo == TipoAcao.ESCALAR:
            return 0
        elif acao.tipo == TipoAcao.PEGAR_OURO:
            return 1
        elif acao.tipo == TipoAcao.MOVER:
            g = 2 + {Ponto(0, 1): 0, Ponto(0, -1): 1, Ponto(1, 0): 2, Ponto(-1, 0): 3}[acao.direcao]
            print(g)
            return g
        elif acao.tipo == TipoAcao.ATIRAR:
            g = 6 + {Ponto(0, 1): 0, Ponto(0, -1): 1, Ponto(1, 0): 2, Ponto(-1, 0): 3}[acao.direcao]
            print(g)
            return g
        raise ValueError

    def agir(self, sentidos: set[Sentido], pontuacao: int):
        if Sentido.QUEDA_BURACO in sentidos or Sentido.ATAQUE_WUMPUS in sentidos or Sentido.ESCALADA in sentidos:
            yield Acao(TipoAcao.FINALIZAR_JOGO, None)
            yield
            return

        estado_atual = Estado(self.estado_atual.posicao, self.estado_atual.flechas, self.estado_atual.pegou_ouro, sentidos, self.estado_atual.matou_wumpus, self.estado_atual.memorias)
        estado_idx = self.indice_estado(estado_atual)

        if np.random.rand() < self.epsilon:
            acao_idx = self.rng.randrange(0, self.acoes)
        else:
            acao_idx = np.argmax(self.qtabela[:, estado_idx])

        if acao_idx == 0:
            ac = Acao(TipoAcao.ESCALAR, None)
            novo_estado = estado_atual
        elif acao_idx == 1:
            ac = Acao(TipoAcao.PEGAR_OURO, None)
            novo_estado = Estado(estado_atual.posicao, estado_atual.flechas, True, sentidos, estado_atual.matou_wumpus, estado_atual.memorias)
        elif acao_idx < 6:
            ac = Acao(TipoAcao.MOVER, [Ponto(0, -1), Ponto(0, 1), Ponto(1, 0), Ponto(-1, 0)][acao_idx - 2])
            novo_estado = Estado(estado_atual.posicao + ac.direcao, estado_atual.flechas, estado_atual.pegou_ouro, sentidos, estado_atual.matou_wumpus, estado_atual.memorias)
        else:
            ac = Acao(TipoAcao.ATIRAR, [Ponto(0, -1), Ponto(0, 1), Ponto(1, 0), Ponto(-1, 0)][acao_idx - 6])
            novo_estado = Estado(estado_atual.posicao, estado_atual.flechas - 1, estado_atual.pegou_ouro, sentidos, estado_atual.matou_wumpus, estado_atual.memorias)

        pontuacao_nova, novos_sentidos, ok = yield ac

        recompensa = pontuacao_nova - pontuacao - 1  # -1 pois o movimento em si causa uma pequena penalidade
        if Sentido.GRITO in novos_sentidos:
            novo_estado = Estado(novo_estado.posicao, novo_estado.flechas, novo_estado.pegou_ouro, novo_estado.sentidos, True, novo_estado.memorias)

        # Colocar penalidades altas para ações ilegais
        if ac.tipo == TipoAcao.ESCALAR and estado_atual.posicao != Ponto(1, 1):
            recompensa -= 1000
        elif ac.tipo == TipoAcao.PEGAR_OURO and Sentido.BRILHO not in sentidos:
            recompensa -= 1000
        elif ac.tipo == TipoAcao.MOVER and (
            novo_estado.posicao.x < 1
            or novo_estado.posicao.x >= self.tamanho_ambiente - 1
            or novo_estado.posicao.y < 1
            or novo_estado.posicao.y >= self.tamanho_ambiente - 1):
            recompensa -= 1000

        if ok:  # atualizar o estado somente se a ação foi, de fato, executada
            self.estado_atual = Estado(novo_estado.posicao, novo_estado.flechas, novo_estado.pegou_ouro, novos_sentidos, novo_estado.matou_wumpus, novo_estado.memorias.copy())
            self.estado_atual.memorias[self.estado_atual.posicao] = novos_sentidos

        # Equação padrão do Q-learning
        novo_estado_idx = self.indice_estado(self.estado_atual)
        valor_proximo = np.max(self.qtabela[:, novo_estado_idx])
        valor_atual = self.qtabela[acao_idx, estado_idx]
        self.qtabela[acao_idx, estado_idx] = valor_atual + self.taxa_aprendizado * (recompensa + self.desconto * valor_proximo - valor_atual)
        yield


def offsets_validos(origem: Ponto, tamanho_matriz: int) -> Iterable[Ponto]:
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
        pt = Ponto(dx + origem.x, dy + origem.y)
        if pt.esta_na_matriz(tamanho_matriz):
            yield pt


def jogar(agente: Agente, jogo: Jogo, limite=float('inf')):
    '''
    Faz um agente jogar um jogo até que ele acabe.
    Parâmetro limite: Máximo de jogadas a serem feitas,
    a fim de evitar loops infinitos.
    '''
    agente.inicializar(jogo.caverna.tamanho)
    sentidos = jogo.caverna.ler_sentidos(jogo.posicao_agente)
    acao_ok = True
    tabela_chamadas = {
        TipoAcao.MOVER: jogo.acao_mover,
        TipoAcao.ATIRAR: jogo.acao_atirar,
        TipoAcao.PEGAR_OURO: lambda _: jogo.acao_pegar_ouro(),
        TipoAcao.ESCALAR: lambda _: jogo.acao_escalar(),
        TipoAcao.FINALIZAR_JOGO: lambda: print(
            "Erro: o agente tentou finalizar o jogo, " +
            "mas o jogo deve continuar."
        ),
    }
    c = 0
    while not jogo.acabou:
        gen = agente.agir(sentidos, jogo.pontuacao)
        ac = next(gen)
        soma = Ponto(0, 0) if ac.direcao is None else ac.direcao
        sentidos, acao_ok = tabela_chamadas[ac.tipo](jogo.posicao_agente + soma)
        gen.send((jogo.pontuacao, sentidos, acao_ok))
        try:
            next(gen)
            raise RuntimeError('esperava StopIteration')
        except StopIteration:
            pass
        limite -= 1
        if limite <= 0:
            return None, None
        c += 1

    gen = agente.agir(sentidos, jogo.pontuacao)
    for _ in gen:
        pass
    return jogo.pontuacao, c


def main() -> None:
    rng = Random()
    try:
        agente = AgenteQLearning(6 + 2, .05, .1, .85)
        i = 10**6 + rng.randint(1000, 99999)
        ultimos = [0] * 1500
        #jogo = Jogo(6, rng)  # melhor com 10**6: média: 79
        while 1:
            agente.epsilon = np.exp(-i/10**5.5) * .75
            jogo = Jogo(6, rng)  # melhor com 10**7: média: -10.72   melhor com 10**4.75: média: -1
            jogo.reset()
            pontuacao_final, lances = jogar(agente, jogo)
            if pontuacao_final is None:
                print('Jogo muito longo')
            else:
                ultimos = [pontuacao_final] + ultimos[:-1]
                print(f'{i} pontos: {str(pontuacao_final).zfill(3)}\t\tmédia: {sum(ultimos)/len(ultimos):.2f}\t\tepsilon: {agente.epsilon}')
            sys.stdout.flush()
            i += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
