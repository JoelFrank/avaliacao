import numpy as np
import random
from collections import defaultdict

ACTIONS_LIST = ['move_up', 'move_down', 'move_left', 'move_right', 'grab', 'climb', 'shoot_up', 'shoot_down', 'shoot_left', 'shoot_right']

REWARDS = {
    'move': -1,
    'fall_pit': -100,
    'grab_gold': 100,
    'shoot_wumpus': 50,
    'death_wumpus': -100,
    'miss_shot': -10,
    'no_gold_grab': -1,
    'climb_out_success': 100,
    'climb_out_fail': -100,
    'invalid_move': -10,
}

class WumpusEnv:
    def __init__(self, size=4):
        self.size = size
        self.reset()

    def reset(self):
        self.world = [[{'content': None, 'visited': False, 'senses': []} for _ in range(self.size)] for _ in range(self.size)]
        self.agent_pos = (0, 0)
        self.world[0][0]['visited'] = True
        self.gold_collected = False
        self.wumpus_killed = False
        self.has_arrow = True
        self.score = 100
        self.path = [self.agent_pos]
        self.place_fixed_items()
        self.add_senses()
        return self.get_state()

    def place_fixed_items(self):
        self.wumpus_pos = (0, 2)
        self.gold_pos = (2, 3)
        self.pits = [(1, 1), (3, 2)]
        self.world[self.wumpus_pos[0]][self.wumpus_pos[1]]['content'] = 'W'
        self.world[self.gold_pos[0]][self.gold_pos[1]]['content'] = 'G'
        for pit in self.pits:
            self.world[pit[0]][pit[1]]['content'] = 'P'

    def add_senses(self):
        for i in range(self.size):
            for j in range(self.size):
                self.world[i][j]['senses'] = []
        def around(x, y):
            return [(x+dx, y+dy) for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)] if 0<=x+dx<self.size and 0<=y+dy<self.size]
        wx, wy = self.wumpus_pos
        for x, y in around(wx, wy):
            self.world[x][y]['senses'].append('Stench')
        for px, py in self.pits:
            for x, y in around(px, py):
                self.world[x][y]['senses'].append('Breeze')
        gx, gy = self.gold_pos
        self.world[gx][gy]['senses'].append('Glitter')

    def get_state(self):
        x, y = self.agent_pos
        senses = self.world[x][y]['senses']
        return (x, y, 'Glitter' in senses, 'Stench' in senses, 'Breeze' in senses, self.gold_collected, self.wumpus_killed, self.has_arrow)

    def step(self, action):
        reward = 0
        done = False
        x, y = self.agent_pos
        self.world[x][y]['visited'] = True

        if action.startswith('move'):
            dx, dy = {'move_up': (-1,0), 'move_down': (1,0), 'move_left': (0,-1), 'move_right': (0,1)}[action]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self.agent_pos = (nx, ny)
                self.path.append(self.agent_pos)
                cell = self.world[nx][ny]
                if cell['content'] == 'P':
                    reward = REWARDS['fall_pit']
                    done = True
                elif cell['content'] == 'W' and not self.wumpus_killed:
                    reward = REWARDS['death_wumpus']
                    done = True
                else:
                    reward = REWARDS['move']
            else:
                reward = REWARDS['invalid_move']

        elif action == 'grab':
            if self.agent_pos == self.gold_pos and not self.gold_collected:
                self.gold_collected = True
                reward = REWARDS['grab_gold']
                self.world[self.gold_pos[0]][self.gold_pos[1]]['content'] = None
            else:
                reward = REWARDS['no_gold_grab']

        elif action == 'climb':
            if self.agent_pos == (0,0):
                if self.gold_collected:
                    reward = REWARDS['climb_out_success']
                else:
                    reward = REWARDS['climb_out_fail']
                done = True
            else:
                reward = REWARDS['invalid_move']

        elif action.startswith('shoot') and self.has_arrow:
            self.has_arrow = False
            dx, dy = {'shoot_up': (-1,0), 'shoot_down': (1,0), 'shoot_left': (0,-1), 'shoot_right': (0,1)}[action]
            tx, ty = x + dx, y + dy
            if 0 <= tx < self.size and 0 <= ty < self.size:
                if (tx, ty) == self.wumpus_pos and self.world[tx][ty]['content'] == 'W':
                    reward = REWARDS['shoot_wumpus']
                    self.wumpus_killed = True
                    self.world[tx][ty]['content'] = None
                    self.add_senses()
                else:
                    reward = REWARDS['miss_shot']
            else:
                reward = REWARDS['invalid_move']
        else:
            reward = REWARDS['invalid_move']

        self.score += reward
        if self.score <= 0:
            done = True
        return self.get_state(), reward, done, {}

    def render(self):
        print("\nMapa Atual:")
        for i in range(self.size):
            for j in range(self.size):
                cell = self.world[i][j]
                if (i, j) == self.agent_pos:
                    print(f"\033[32m[A]\033[0m", end=' ')
                elif cell['content'] == 'G':
                    print(f"\033[33m[G]\033[0m", end=' ')
                elif cell['content'] == 'W':
                    print(f"\033[31m[W]\033[0m", end=' ')
                elif cell['content'] == 'P':
                    print(f"\033[34m[P]\033[0m", end=' ')
                else:
                    if cell['visited']:
                        print("[.]", end=' ')
                    else:
                        print("[?]", end=' ')
            print()
        print(f"Gold: {self.gold_collected}, Wumpus Killed: {self.wumpus_killed}, Score: {self.score}")

class QLearningAgent:
    def __init__(self, env, lr=0.1, gamma=0.99, epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.0005):
        self.env = env
        self.q_table = defaultdict(lambda: np.zeros(len(ACTIONS_LIST)))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS_LIST)
        else:
            return ACTIONS_LIST[np.argmax(self.q_table[state])]

    def update_q_table(self, state, action, reward, next_state, done):
        idx = ACTIONS_LIST.index(action)
        max_next = np.max(self.q_table[next_state]) if not done else 0
        self.q_table[state][idx] += self.lr * (reward + self.gamma * max_next - self.q_table[state][idx])

    def decay_epsilon(self, episode):
        self.epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * np.exp(-self.epsilon_decay * episode)

def train(episodes=5000):
    env = WumpusEnv()
    agent = QLearningAgent(env)
    rewards_per_episode = []

    for ep in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0
        steps = 0
        env.path = []
        while not done and steps < 100:
            action = agent.get_action(state)

            # Restringe atirar só se sentir fedor e tiver flecha
            if action.startswith('shoot') and (not state[3] or not state[7]):
                action = random.choice(['move_up', 'move_down', 'move_left', 'move_right', 'grab', 'climb'])

            next_state, reward, done, _ = env.step(action)
            agent.update_q_table(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            steps +=1
        agent.decay_epsilon(ep)
        rewards_per_episode.append(total_reward)
        if (ep+1) % 500 == 0:
            avg = np.mean(rewards_per_episode[-500:])
            print(f"Episódio {ep+1} - Média recompensa últimos 500 episódios: {avg:.2f}")
    return agent, env, rewards_per_episode




def test(agent, env, runs=3):
    agent.epsilon = 0
    for t in range(runs):
        state = env.reset()
        done = False
        print(f"\n--- Teste {t+1} ---")
        step = 0
        while not done and step < 50:
            env.render()
            action = agent.get_action(state)

            if action.startswith('shoot') and (not state[3] or not state[7]):
                action = random.choice(['move_up','move_down','move_left','move_right','grab','climb'])
                print(f"Corrigido: ação inválida de tiro sem flecha/fedor. Nova ação: {action}")

            print(f"Ação escolhida: {action}")

            next_state, reward, done, _ = env.step(action)
            state = next_state
            step += 1
        print(f"Caminho percorrido: {env.path}")

if __name__ == "__main__":
    agent, env, rewards = train()
    test(agent, env, runs=3)
