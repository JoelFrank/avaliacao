import tkinter as tk
import random
import time
from collections import defaultdict

# --- Parâmetros do Jogo e do Agente ---
GRID_SIZE = 5
CELL_SIZE = 100
ACTIONS = ['up', 'down', 'left', 'right']

START_POS = (0, 0)
GOLD_POS = (GRID_SIZE - 1, GRID_SIZE - 1)
WUMPUS_POS = (1, 2)
PITS_POS = [(2, 1), (3, 3), (0, 4)]

# Parâmetros do Q-Learning
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.9995
MIN_EPSILON = 0.05
MAX_EPISODES_TRAINING = 2500

VISUALIZATION_INTERVAL = 250

class WumpusWorld:
    """
    Define o ambiente do Mundo de Wumpus.
    Gerencia o estado, ações e recompensas.
    """
    def __init__(self, size, start, gold, wumpus, pits):
        self.size = size
        self.start_pos = start
        self.gold_pos = gold
        self.wumpus_pos = wumpus
        self.pits_pos = pits
        self.agent_pos = self.start_pos
        self.agent_has_gold = False

    def reset(self):
        """Reseta a posição do agente e o status do ouro."""
        self.agent_pos = self.start_pos
        self.agent_has_gold = False
        return self.get_state()

    def get_state(self):
        """O estado agora inclui a posição e se o agente tem o ouro."""
        return (self.agent_pos, self.agent_has_gold)

    def step(self, action_str):
        """
        Executa uma ação e retorna o novo estado, recompensa e se o episódio terminou.
        """
        x, y = self.agent_pos
        
        if action_str == 'up': y -= 1
        elif action_str == 'down': y += 1
        elif action_str == 'left': x -= 1
        elif action_str == 'right': x += 1

        reward = -1
        done = False

        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            reward = -5
        else:
            self.agent_pos = (x, y)

        if self.agent_pos == self.wumpus_pos or self.agent_pos in self.pits_pos:
            reward = -100
            done = True
        elif self.agent_pos == self.gold_pos and not self.agent_has_gold:
            self.agent_has_gold = True
            reward = 50
            done = False
        elif self.agent_pos == self.start_pos and self.agent_has_gold:
            reward = 100
            done = True

        new_state = self.get_state()
        return new_state, reward, done


class QLearningAgent:
    def __init__(self, actions, alpha, gamma, epsilon):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.q_table.get(state, {})
            if not q_values:
                return random.choice(self.actions)
            return max(q_values, key=q_values.get)

    def learn(self, state, action, reward, next_state):
        future_q_values = self.q_table.get(next_state, {})
        max_future_q = max(future_q_values.values()) if future_q_values else 0.0
        current_q = self.q_table[state][action]
        new_q = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)
        self.q_table[state][action] = new_q


class WumpusGUI(tk.Frame):
    """
    GUI com a lógica de visualização periódica no treinamento.
    """
    def __init__(self, master, env, agent):
        super().__init__(master)
        self.master = master
        self.env = env
        self.agent = agent
        self.cell_size = CELL_SIZE
        
        self.is_training = False
        self.episode_count = 0
        self.total_reward = 0
        
        self.pack()
        self._create_widgets()
        self.draw_grid()
        self.draw_elements()

    def _create_widgets(self):
        canvas_width = self.env.size * self.cell_size
        canvas_height = self.env.size * self.cell_size
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg='white')
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.start_button = tk.Button(control_frame, text="Iniciar Treinamento", command=self.start_training)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(control_frame, text="Parar Treinamento", command=self.stop_training, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.run_once_button = tk.Button(control_frame, text="Executar 1 Episódio (Treinado)", command=self.run_single_trained_episode)
        self.run_once_button.pack(side=tk.LEFT, padx=5)
        info_frame = tk.Frame(self)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.episode_label = tk.Label(info_frame, text=f"Episódio: {self.episode_count}")
        self.episode_label.pack(side=tk.LEFT)
        self.reward_label = tk.Label(info_frame, text=f"Recompensa Acumulada: {self.total_reward}")
        self.reward_label.pack(side=tk.LEFT, padx=10)
        self.epsilon_label = tk.Label(info_frame, text=f"Epsilon: {self.agent.epsilon:.3f}")
        self.epsilon_label.pack(side=tk.LEFT, padx=10)

    def draw_grid(self):
        for i in range(self.env.size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.env.size * self.cell_size)
            self.canvas.create_line(0, i * self.cell_size, self.env.size * self.cell_size, i * self.cell_size)

    def draw_elements(self):
        x, y = self.env.start_pos
        self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill='lightgreen', outline='black')
        self.canvas.create_text((x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size, text='Início/Escape')
        x, y = self.env.gold_pos
        self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill='gold', outline='black')
        self.canvas.create_text((x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size, text='Ouro')
        x, y = self.env.wumpus_pos
        self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill='purple', outline='black')
        self.canvas.create_text((x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size, text='Wumpus', fill='white')
        for x, y in self.env.pits_pos:
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill='black', outline='black')
            self.canvas.create_text((x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size, text='Poço', fill='white')
        x, y = self.env.agent_pos
        self.agent_oval = self.canvas.create_oval(x * self.cell_size + 10, y * self.cell_size + 10, (x + 1) * self.cell_size - 10, (y + 1) * self.cell_size - 10, fill='red', outline='darkred')
    
    def update_display(self, delay=100, is_final_move=False):
        x, y = self.env.agent_pos
        self.canvas.coords(self.agent_oval, x * self.cell_size + 10, y * self.cell_size + 10, (x + 1) * self.cell_size - 10, (y + 1) * self.cell_size - 10)
        
        agent_color = 'red'
        if self.env.agent_has_gold:
            agent_color = 'orange'
        
        if is_final_move:
             if self.env.agent_pos == self.env.start_pos and self.env.agent_has_gold:
                 agent_color = 'blue'
             else:
                 agent_color = 'black'
        
        self.canvas.itemconfig(self.agent_oval, fill=agent_color)

        self.episode_label.config(text=f"Episódio: {self.episode_count}")
        self.reward_label.config(text=f"Recompensa Acumulada: {self.total_reward}")
        self.epsilon_label.config(text=f"Epsilon: {self.agent.epsilon:.3f}")
        
        # Apenas atualiza o canvas se houver um delay
        if delay > 0:
            self.master.update()
            time.sleep(delay / 1000)

    def run_episode(self, is_training=True, delay=0):
        state = self.env.reset()
        self.update_display(delay=delay)
        done = False
        episode_reward = 0
        
        while not done:
            if not self.is_training and is_training:
                break
            action = self.agent.choose_action(state)
            next_state, reward, done = self.env.step(action)
            episode_reward += reward
            if is_training:
                self.agent.learn(state, action, reward, next_state)
            state = next_state
            self.update_display(delay=delay, is_final_move=done)
        
        self.total_reward += episode_reward
        self.episode_count += 1
        
        if is_training and self.agent.epsilon > MIN_EPSILON:
            self.agent.epsilon *= EPSILON_DECAY

    def start_training(self):
        self.is_training = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.run_once_button.config(state=tk.DISABLED)
        
        def training_loop():
            if self.is_training and self.episode_count < MAX_EPISODES_TRAINING:
                
                if self.episode_count % VISUALIZATION_INTERVAL == 0:
                    print(f"--- Visualizando Episódio de Treinamento Nº {self.episode_count} ---")

                    self.run_episode(is_training=True, delay=150)
                else:

                    self.run_episode(is_training=True, delay=0)
                
                self.episode_label.config(text=f"Episódio: {self.episode_count}")
                self.epsilon_label.config(text=f"Epsilon: {self.agent.epsilon:.3f}")
                self.master.update() 

                self.master.after(1, training_loop)
            else:
                if self.episode_count >= MAX_EPISODES_TRAINING:
                    print(f"\nTreinamento parado automaticamente ao atingir {self.episode_count} episódios.")
                self.stop_training()

        training_loop()

    def stop_training(self):
        self.is_training = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.run_once_button.config(state=tk.NORMAL)
        print("\n--- Q-Table (Top 20 entradas por valor) ---")
        sorted_q = sorted(
            ((s, a, v) for s, actions in self.agent.q_table.items() for a, v in actions.items()),
            key=lambda item: item[2],
            reverse=True
        )
        for state, action, value in sorted_q[:20]:
            pos, has_gold = state
            print(f"Estado (Pos:{pos}, Ouro:{has_gold}), Ação {action}: Q-valor {value:.2f}")

    def run_single_trained_episode(self):
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0
        self.run_episode(is_training=False, delay=200)
        self.agent.epsilon = original_epsilon

if __name__ == '__main__':
    wumpus_env = WumpusWorld(GRID_SIZE, START_POS, GOLD_POS, WUMPUS_POS, PITS_POS)
    rl_agent = QLearningAgent(actions=ACTIONS, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON)
    root = tk.Tk()
    root.title("Agente RL no Mundo de Wumpus - Visualização Periódica")
    root.resizable(False, False)
    app = WumpusGUI(master=root, env=wumpus_env, agent=rl_agent)
    root.mainloop()


    #Referencias:
    ## aulas da professora lilian e gemini