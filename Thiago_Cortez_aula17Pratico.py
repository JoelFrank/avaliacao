from abc import ABC, abstractmethod
import random
from numpy import argmax
from typing import TypedDict, Set, Tuple, List


class pos(TypedDict):
    x: int
    y: int

    def __eq__(self, other):
        return self["x"] == other["x"] and self["y"] == other["y"]

class Creature(ABC):
    @abstractmethod
    def hit(self) -> Tuple[int, str]: 
        pass

    @abstractmethod
    def nearby(self) -> str: 
        pass

    @abstractmethod
    def get_hit(self) -> Tuple[str, bool]: 
        pass

class Gold(Creature):
    
    def __init__(self):
        super().__init__()
        self.__taken = False

    def __str__(self): 
        return "_Gold_"
    
    def hit(self) -> Tuple[int, str]: 
        if not self.__taken:
            self.__taken = True
            return (500, "gold")
        else: 
            return (-1, "empty")
    
    def nearby(self) -> str: 
        return ""
    
    def get_hit(self) -> Tuple[str, bool]: 
        return ("", False)

class Hole(Creature):
    def __str__(self): return "_Hole_"
    def hit(self) -> Tuple[int, str]: 
        return (-1000, "hole")
    
    def nearby(self) -> str: 
        return "Você sente uma brisa suave..."
    
    def get_hit(self) -> Tuple[str, bool]: 
        return ("", False)
    
class Wumpus(Creature):
    def __init__(self):
        super().__init__()
        self.__alive: bool = True

    def __str__(self): 
        return "Wumpus"
    
    @property
    def is_alive(self): 
        return self.__alive
    
    def hit(self) -> Tuple[int, str]:
        if self.__alive: 
            return (-1000, "wumpus")
        else: 
            return (0, "dead_wumpus")
        
    def nearby(self) -> str: 
        return "Você sente um cheiro insuportável"
    
    def get_hit(self) -> Tuple[str, bool]:
        if self.__alive:
            self.__alive = False
            return ("scream", True)
        
        return ("", False)

class Empty(Creature):
    def __str__(self): 
        return "______"
    
    def hit(self) -> Tuple[int, str]: 
        return (-1, "empty")
    
    def nearby(self) -> str: 
        return ""
    
    def get_hit(self) -> Tuple[str, bool]: 
        return ("", False)

class Square():
    
    def __init__(self, type: Creature):
        self.__type: Creature = type
        self.__scents: Set[str] = set()

    def __repr__(self): 
        return str(self.__type)
    
    def add_side_effect(self, scent: str):
        if scent: 
            self.__scents.add(scent)

    def send_side_effect(self) -> str: 
        return self.__type.nearby()
    
    def stepped_on(self) -> Tuple[int, str, Set[str]]:
        pontos, event = self.__type.hit()
        return pontos, event, self.__scents
    
    def get_hit(self) -> Tuple[str, bool]: 
        return self.__type.get_hit()
    
    @property
    def type(self): 
        return self.__type

class Game():
    
    def __init__(self, size: int = 4):
        self.__size = size
        self.action_map = {
            0: ("mover", "cima"), 1: ("mover", "direita"),
            2: ("mover", "baixo"), 3: ("mover", "esquerda"),
            4: ("atirar", "cima"), 5: ("atirar", "direita"),
            6: ("atirar", "baixo"), 7: ("atirar", "esquerda"),
            8: ("sair", "")
        }
        self.reset()

    def __create_board(self) -> list[list[Square]]:
        
        positions = list(range(self.__size))
        
        safe_zone = [(self.__size - 1, 0), (self.__size - 1, 1), (self.__size - 2, 0)]
        
        possible_coords = [pos(x=x, y=y) for x in range(self.__size) for y in range(self.__size) if (x,y) not in safe_zone]
        random.shuffle(possible_coords)

        monster_pos = possible_coords.pop()
        
        treasure_pos = possible_coords.pop()

        num_holes = (self.__size**2 - 1) // 5
        holes_pos = []
        for _ in range(num_holes):
            if not possible_coords: break
            holes_pos.append(possible_coords.pop())
            
        board = []
        for r in range(self.__size):
            row = []
            for c in range(self.__size):
                current_pos = pos(x=r, y=c)
                if current_pos == monster_pos:
                    row.append(Square(Wumpus()))
                elif current_pos == treasure_pos:
                    row.append(Square(Gold()))
                elif current_pos in holes_pos:
                    row.append(Square(Hole()))
                else:
                    row.append(Square(Empty()))
            board.append(row)
        return board

    def __set_effects(self):
        for r in range(self.__size):
            for c in range(self.__size):
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.__size and 0 <= nc < self.__size:
                        scent = self.__board[nr][nc].send_side_effect()
                        self.__board[r][c].add_side_effect(scent)

    def reset(self, render: bool = False):
        self.__board = self.__create_board()
        self.__set_effects()
        self.__player_pos = pos(x=self.__size - 1, y=0)
        self.__has_arrow = True
        self.__has_gold = False
        self.__score = 0
        self.__plays = 0
        self.__gone = False
        self.__wumpus_alive = True
        
        _, _, scents = self.__board[self.__player_pos['x']][self.__player_pos['y']].stepped_on()

        if render: self.render(False)
        
        return self.get_state(), {"scents": scents}

    def get_state(self):
         return (self.__player_pos['x'], self.__player_pos['y'])

    def step(self, action: int):
        option, direction = self.action_map[action]
        reward = 0
        done = False
        info = {"scream": False, "gold": False, "shot": False, "wumpus": False, "hole": False}

        if option == "mover":
            self.__plays += 1
            px, py = self.__player_pos['x'], self.__player_pos['y']
            
            if direction == "cima": self.__player_pos['x'] -= 1
            elif direction == "direita": self.__player_pos['y'] += 1
            elif direction == "baixo": self.__player_pos['x'] += 1
            elif direction == "esquerda": self.__player_pos['y'] -= 1

            if not (0 <= self.__player_pos['x'] < self.__size and 0 <= self.__player_pos['y'] < self.__size):
                self.__player_pos = pos(x=px, y=py)
                reward -= 100
            
            points, event, scents = self.__board[self.__player_pos['x']][self.__player_pos['y']].stepped_on()
            reward += points
            if len(scents) > 0:
                info["scents"] = scents
            if "Você sente uma brisa suave..." in scents:
                info["hole"] = True
            if "Você sente um cheiro insuportável" in scents:
                info["wumpus"] = True

            if event == "gold": 
                self.__has_gold = True
                info["gold"] = True

            if event in {"wumpus", "hole"}:
                done = True

        elif option == "atirar":
            reward -= 1
            # self.__plays += 1
            if self.__has_arrow:
                self.__has_arrow = False
                info["shot"] = True
                px, py = self.__player_pos['x'], self.__player_pos['y']
                
                if direction == "cima" and px > 0: target_pos = (px - 1, py)
                elif direction == "direita" and py < self.__size - 1: target_pos = (px, py + 1)
                elif direction == "baixo" and px < self.__size - 1: target_pos = (px + 1, py)
                elif direction == "esquerda" and py > 0: target_pos = (px, py - 1)
                else: target_pos = None

                if target_pos:
                    _, hit = self.__board[target_pos[0]][target_pos[1]].get_hit()
                    if hit:
                        info["scream"] = True
                        reward += 4000
                        self.__wumpus_alive = False
                        # self.__set_effects()
            else:
                reward -= 1000
                self.__plays += 1

        elif option == "sair":
            if self.__player_pos == pos(x=self.__size - 1, y=0):
                if self.__has_gold:
                    reward += 4000
                else:
                    if self.__wumpus_alive == True:
                        reward -= 1000
                done = True
                self.__gone = True
            else:
                reward -= 100000
                self.__plays += 1

        if self.__plays >= 50:
            reward -= 1000
            done = True
        
        next_state = self.get_state()
        return next_state, reward, done, info

    def render(self, score: bool = True):
        for r in range(self.__size):
            row_str = []
            for c in range(self.__size):
                if self.__player_pos['x'] == r and self.__player_pos['y'] == c:
                    row_str.append("PLAYER")
                else:
                    row_str.append(str(self.__board[r][c]))
            print(" | ".join(row_str))
        
        if score:
            if not self.__wumpus_alive:
                self.__score += 50

            if self.__has_gold and self.__gone:
                self.__score += 100

            self.__score -= self.__plays

            if not self.__gone:
                self.__score -= 100
            
            print(f"Score: {self.__score}")


class QLearningAgent():
    def __init__(self, actions: List[int], alpha: float = 0.1, gamma: float = 0.99, epsilon: float = 1.0):
        self.__q_table = {}
        self.__actions = actions
        self.__alpha = alpha
        self.__gamma = gamma
        self.epsilon = epsilon
        self.__show = False
        self.__i = 0

    def get_q_value(self, state: Tuple, action: int) -> float:
        return self.__q_table.get((state, action), 0.0)

    def choose_action(self, state: Tuple) -> int:
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.__actions)
        else:
            q_values = [self.get_q_value(state, a) for a in self.__actions]
            action = self.__actions[argmax(q_values)]
            if self.__show:
                print(state)
                print(q_values)
                print(action)
            return action

    def learn(self, state: Tuple, action: int, reward: float, next_state: Tuple, done: bool):
        old_value = self.get_q_value(state, action)
        
        if done:
            next_max = 0
        else:
            next_q_values = [self.get_q_value(next_state, a) for a in self.__actions]
            next_max = max(next_q_values)
        
        new_value = old_value + self.__alpha * (reward + self.__gamma * next_max - old_value)
        self.__q_table[(state, action)] = new_value
        # if isclose(new_value, old_value, rel_tol=1e-9):
        #     print(state)
        #     print(next_state)
        #     print(f"old_value={old_value}, reward={reward}, next_max={next_max}, alpha={self.__alpha}, gamma={self.__gamma}")
        #     sys.exit(0)
        # if not isclose(new_value, old_value, rel_tol=1e-9) and state == (3, 0, False, False, True):
        #     self.__i += 1
        #     if not self.__i%1000:
        #         print(f"UPDATE: {state}, {action} -> {new_value:.4f}")

    def get_q_table(self):
        return self.__q_table
    
    def show(self, op: bool = True):
        self.__show = op


def train_agent():
    env = Game(size=4)
    agent = QLearningAgent(actions=list(range(9)))

    episodes = 200000
    epsilon_decay = 0.99999
    min_epsilon = 0.05

    print("Iniciando treinamento...")
    for episode in range(episodes):
        
        agent_has_gold = False
        agent_wumpus_killed = False
        agent_has_arrow = True
        near_wumpus = False
        near_hole =  False
        play = 0
        
        state_pos, info = env.reset()
        state = state_pos + (agent_has_gold, agent_wumpus_killed, agent_has_arrow, near_wumpus, near_hole, play)
        done = False
        
        while not done:
            action = agent.choose_action(state)
            next_state_pos, reward, done, info = env.step(action)
            
            if info.get("gold"):
                agent_has_gold = True
            if info.get("scream"):
                agent_wumpus_killed = True
            if info.get("shot"):
                agent_has_arrow = False
            if info.get("wumpus"):
                near_wumpus = True
            else:
                near_wumpus = False
            if info.get("hole"):
                near_hole = True
            else:
                near_hole = False
            play += 1
            
            next_state = next_state_pos + (agent_has_gold, agent_wumpus_killed, agent_has_arrow, near_wumpus, near_hole, play)
            
            if reward != 0: agent.learn(state, action, reward, next_state, done)
            state = next_state

        agent.epsilon = max(min_epsilon, agent.epsilon * epsilon_decay)
        
        if (episode + 1) % 2000 == 0:
            print(f"Episódio {episode + 1}/{episodes} - Epsilon: {agent.epsilon:.4f}")
            
    print("Treinamento concluído.")
    return agent

def solve_with_agent(agent: QLearningAgent):
    print("\n--- Resolvendo o jogo com o agente treinado ---")
    agent.epsilon = 0.05
    env = Game(size=4)
    for _ in range(4):

        agent_has_gold = False
        agent_wumpus_killed = False
        agent_has_arrow = True
        near_wumpus = False
        near_hole =  False
        play = 0
        
        state_pos, info = env.reset(True)
        state = state_pos + (agent_has_gold, agent_wumpus_killed, agent_has_arrow, near_wumpus, near_hole, play)
        done = False
        
        path = [state_pos]
        
        # env.render()
        print("-" * 20)

        while not done:
            action = agent.choose_action(state)
            action_desc = env.action_map[action]
            
            next_state_pos, reward, done, info = env.step(action)
            
            if info.get("gold"):
                agent_has_gold = True
            if info.get("scream"):
                agent_wumpus_killed = True
            if info.get("shot"):
                agent_has_arrow = False
            if info.get("wumpus"):
                near_wumpus = True
            else:
                near_wumpus = False
            if info.get("hole"):
                near_hole = True
            else:
                near_hole = False
            play += 1

            state = next_state_pos + (agent_has_gold, agent_wumpus_killed, agent_has_arrow, near_wumpus, near_hole, play)
            path.append(next_state_pos)
            
            print(f"Ação: {action_desc} -> Posição: {next_state_pos}")
            print(f"Percepções: {info.get('scents', '')}")
            if info.get("scream"): print(">>> OUVIU UM GRITO! <<<")
            if agent_has_gold: print(">>> PEGOU O OURO! <<<")
            print("-" * 20)
            
            if done:
                print("Jogo concluído!")
                break
        
        env.render()
        print(f"\nCaminho percorrido: {path}")


if __name__ == "__main__":
    bot = train_agent()
    # bot.show()
    solve_with_agent(bot)
    # print(bot.get_q_table())
