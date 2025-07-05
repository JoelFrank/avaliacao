import numpy as np
import random

class WumpusWorld:
    def __init__(self, grid_size=4, max_steps=100):
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        
        self.gold_pos = [random.randint(0, 3), random.randint(0, 3)]
        while self.gold_pos == [0, 0]:
            self.gold_pos = [random.randint(0, 3), random.randint(0, 3)]
        
        self.wumpus_pos = [random.randint(0, 3), random.randint(0, 3)]
        while self.wumpus_pos == [0, 0] or self.wumpus_pos == self.gold_pos:
            self.wumpus_pos = [random.randint(0, 3), random.randint(0, 3)]
        
        self.pits = []
        for _ in range(3):
            pit = [random.randint(0, 3), random.randint(0, 3)]
            while (pit == [0, 0] or 
                   pit == self.gold_pos or 
                   pit == self.wumpus_pos or 
                   pit in self.pits):
                pit = [random.randint(0, 3), random.randint(0, 3)]
            self.pits.append(pit)

        self.exit_pos = [random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)]
        while (self.exit_pos == [0, 0] or 
               self.exit_pos == self.gold_pos or 
               self.exit_pos == self.wumpus_pos or 
               self.exit_pos in self.pits):
            self.exit_pos = [random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)]
        
        self.has_gold = False
        self.has_arrow = True
        self.wumpus_alive = True
        self.done = False
        self.current_step = 0
        
        return self._get_state()

    def step(self, action):
        reward = -1
        old_pos = self.agent_pos.copy()
        x, y = old_pos

    def step(self, action):
        reward = -1
        old_pos = self.agent_pos.copy()
        x, y = old_pos

        if action == 0:   # up
            new_pos = [x, min(y + 1, self.grid_size - 1)]
        elif action == 1: # down
            new_pos = [x, max(y - 1, 0)]
        elif action == 2: # left
            new_pos = [max(x - 1, 0), y]
        elif action == 3: # right
            new_pos = [min(x + 1, self.grid_size - 1), y]
        elif action == 4: # grab
            if (not self.has_gold and 
                self.agent_pos == self.gold_pos):
                self.has_gold = True
                reward += 1000
        elif action == 5 and self.has_arrow:  # shoot
            self.has_arrow = False
            reward -= 10
            if self.wumpus_alive and (
               x == self.wumpus_pos[0] or y == self.wumpus_pos[1]):
                self.wumpus_alive = False
                reward += 50
        else:
            new_pos = old_pos

        if new_pos == old_pos and action in [0,1,2,3]:
            reward -= 5       # total −6 for a wall-bump
        else:
            self.agent_pos = new_pos

        if self.agent_pos in self.pits:
            reward -= 1000;   self.done = True
        elif self.wumpus_alive and self.agent_pos == self.wumpus_pos:
            reward -= 1000;   self.done = True
        elif self.agent_pos == self.exit_pos and self.has_gold:  
            reward += 1000;    self.done = True

        if self.current_step >= self.max_steps and not self.done:
            self.done = True
            reward -= 1000

        return self._get_state(), reward, self.done, self._check_perception()

    def _get_state(self):
        return (self.agent_pos[0],
                self.agent_pos[1],
                int(self.has_gold),
                int(self.wumpus_alive),
                int(self.has_arrow))

    def _check_perception(self):
        x, y = self.agent_pos
        breeze  = any(abs(x-px)+abs(y-py)==1 for px,py in self.pits)
        stench  = self.wumpus_alive and any(abs(x-wx)+abs(y-wy)==1
                                            for wx,wy in [self.wumpus_pos])
        glitter = (self.agent_pos == self.gold_pos and not self.has_gold)
        return {'breeze':breeze, 'stench':stench, 'glitter':glitter}

    
    
    def step(self, action):
        # Ações: 0=cima, 1=baixo, 2=esquerda, 3=direita, 4=pegar, 5=atirar
        reward = -1  # Custo padrão por movimento
        x, y = self.agent_pos
        
        if action == 0:  # Cima
            self.agent_pos = [x, min(y + 1, self.grid_size - 1)]
        elif action == 1:  # Baixo
            self.agent_pos = [x, max(y - 1, 0)]
        elif action == 2:  # Esquerda
            self.agent_pos = [max(x - 1, 0), y]
        elif action == 3:  # Direita
            self.agent_pos = [min(x + 1, self.grid_size - 1), y]
        elif action == 4:  # Pegar ouro
            if not self.has_gold and self.agent_pos == self.gold_pos:
                self.has_gold = True
                reward = 1000  # Recompensa por pegar o ouro
        elif action == 5 and self.has_arrow:  # Atirar
            self.has_arrow = False
            reward = -10  # Custo por atirar
            # Matar Wumpus se estiver na mesma linha/coluna
            if self.wumpus_alive and (
                self.agent_pos[0] == self.wumpus_pos[0] or 
                self.agent_pos[1] == self.wumpus_pos[1]
            ):
                self.wumpus_alive = False
                reward = 50  # Recompensa por matar o Wumpus

        if self.agent_pos in self.pits:
            reward = -1000  # Cair em poço
            self.done = True
        elif self.wumpus_alive and self.agent_pos == self.wumpus_pos:
            reward = -1000  # Ser morto pelo Wumpus
            self.done = True
        elif self.agent_pos == [0, 0] and self.has_gold:
            reward = 1000  # Sair com o ouro
            self.done = True
            
        next_state = self._get_state()
        return next_state, reward, self.done, self._check_perception()

class QLearningAgent:
    def __init__(self, learning_rate=0.2, discount_factor=0.9, exploration_rate=1.0):
        self.lr            = learning_rate
        self.gamma         = discount_factor
        self.epsilon       = exploration_rate
        self.epsilon_decay = 0.999995    
        self.epsilon_min   = 0.1      
        self.q_table       = {}
        self.actions       = 6  

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)
    
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.actions - 1)
        else:
            q_values = [self.get_q_value(state, a) for a in range(self.actions)]
            max_q = max(q_values)
            best_actions = [a for a, q in enumerate(q_values) if q == max_q]
            return random.choice(best_actions)

    def update(self, state, action, reward, next_state):
        old_q       = self.get_q_value(state, action)
        max_next_q  = max(self.get_q_value(next_state, a) for a in range(self.actions))
        new_q       = old_q + self.lr * (reward + self.gamma * max_next_q - old_q)
        self.q_table[(state, action)] = new_q
        
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

env = WumpusWorld()
agent = QLearningAgent()
episodes = 50000

for episode in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        action = agent.choose_action(state)
        next_state, reward, done, _ = env.step(action)
        agent.update(state, action, reward, next_state)
        state = next_state
        total_reward += reward
    
    if (episode + 1) % 500 == 0:
        print(f"Episódio: {episode+1}, Recompensa Total: {total_reward}, Epsilon: {agent.epsilon:.4f}")

test_episodes = 10
for episode in range(test_episodes):
    state = env.reset()
    done = False
    path = [env.agent_pos.copy()]
    
    while not done:
        action = agent.choose_action(state)
        state, _, done, _ = env.step(action)
        path.append(env.agent_pos.copy())
    
    print(f"\nTeste {episode+1}:")
    print(f"Local da saída: {env.exit_pos}")
    print(f"Posições visitadas: {path}")
    print("Resultado:", "Sucesso" if env.has_gold and env.agent_pos == env.exit_pos else "Falha")