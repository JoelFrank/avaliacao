using System;
using System.Collections.Generic;

namespace WumpusWorld
{
    enum FieldType
    {
        Start,
        Wumpus,
        Pit,
        Gold,
        Empty
    }

    enum Action 
    { 
        Up, 
        Down, 
        Left, 
        Right, 
        Grab, 
        Shoot, 
        Exit 
    }

    class Ambient
    {
        public FieldType[,] Fields;

        public Ambient(int wumpusCount, int pitCount, int goldCount)
        {
            Fields = new FieldType[4, 4];
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++)
                    Fields[i, j] = FieldType.Empty;

            Fields[0, 0] = FieldType.Start;

            if (wumpusCount + pitCount + goldCount > 15)
                throw new ArgumentOutOfRangeException();

            PlaceRandomly(wumpusCount, FieldType.Wumpus);
            PlaceRandomly(pitCount, FieldType.Pit);
            PlaceRandomly(goldCount, FieldType.Gold);
        }

        private Ambient(Ambient other)
        {
            Fields = (FieldType[,])other.Fields.Clone();
        }

        public Ambient Clone() => new Ambient(this);

        private void PlaceRandomly(int count, FieldType type)
        {
            var rnd = new Random();
            int placed = 0;
            while (placed < count)
            {
                int x = rnd.Next(0, 4);
                int y = rnd.Next(0, 4);
                if (Fields[x, y] == FieldType.Empty)
                {
                    Fields[x, y] = type;
                    placed++;
                }
            }
        }
    }

    class State
    {
        public int X, Y;
        public bool HasGold, WumpusAlive;
        public State(int x, int y, bool hasGold, bool wumpusAlive)
        {
            X = x; Y = y; HasGold = hasGold; WumpusAlive = wumpusAlive;
        }
        public override bool Equals(object obj)
            => obj is State s && X == s.X && Y == s.Y && HasGold == s.HasGold && WumpusAlive == s.WumpusAlive;
        public override int GetHashCode()
            => (X, Y, HasGold, WumpusAlive).GetHashCode();
    }

    class QLearningAgent
    {
        private readonly Ambient _baseEnv;
        private readonly Random _rnd = new Random();
        private readonly Dictionary<(State, Action), double> _Q = new();
        private readonly double _alpha = 0.1, _gamma = 0.9, _epsilon = 0.2;

        public QLearningAgent(Ambient env) => _baseEnv = env;

        private double GetQ(State s, Action a) => _Q.TryGetValue((s, a), out var v) ? v : 0.0;

        private Action ChooseAction(State s)
        {
            if (_rnd.NextDouble() < _epsilon)
                return (Action)_rnd.Next(Enum.GetValues(typeof(Action)).Length);

            double best = double.NegativeInfinity;
            Action bestAction = Action.Up;
            foreach (Action a in Enum.GetValues(typeof(Action)))
            {
                double q = GetQ(s, a);
                if (q > best)
                {
                    best = q;
                    bestAction = a;
                }
            }
            return bestAction;
        }

        public void Train(int episodes = 5000)
        {
            int successCount = 0;
            double totalRewardSum = 0;

            for (int ep = 1; ep <= episodes; ep++)
            {
                var env = _baseEnv.Clone();
                var state = new State(0, 0, false, true);
                bool done = false;
                double epReward = 0;
                double lastReward = 0;

                while (!done)
                {
                    var action = ChooseAction(state);
                    Step(env, state, action, out var nextState, out var reward, out done, out _);
                    epReward += reward;
                    lastReward = reward;

                    double maxNextQ = double.NegativeInfinity;
                    foreach (Action a2 in Enum.GetValues(typeof(Action)))
                        maxNextQ = Math.Max(maxNextQ, GetQ(nextState, a2));

                    double currentQ = GetQ(state, action);
                    double target = reward + (done ? 0 : _gamma * maxNextQ);
                    _Q[(state, action)] = currentQ + _alpha * (target - currentQ);

                    state = nextState;
                }

                totalRewardSum += epReward;
                if (lastReward > 0) successCount++;

                if (ep % 1000 == 0)
                    Console.WriteLine($"Ep {ep}: recomp_reward={epReward}, succ_rate={(double)successCount / ep:P1}");
            }

            Console.WriteLine($"\nTreinamento concluído em {episodes} eps.");
            Console.WriteLine($"Taxa de sucesso: {successCount}/{episodes} ({(double)successCount / episodes:P2})");
            Console.WriteLine($"Recompensa média por episódio: {totalRewardSum / episodes:F2}\n");
        }

        public void RunGreedy()
        {
            var env = _baseEnv.Clone();
            var state = new State(0, 0, false, true);
            bool done = false;
            bool won = false;
            int steps = 0;
            double reward = 0;

            while (!done)
            {
                var action = ChooseAction(state);
                Step(env, state, action, out state, out reward, out done, out won);
                steps++;
                Console.WriteLine($"Step {steps}: ação={action}, posição=[{state.X},{state.Y}], hasGold={state.HasGold}");
            }

            Console.WriteLine($"\nPassos={steps};Pontuação={reward};Venceu={won}\n");
        }

        private void Step(Ambient env, State state, Action action,
                          out State nextState, out double reward, out bool terminal, out bool won)
        {
            int x = state.X, y = state.Y;
            bool hasG = state.HasGold, wAlive = state.WumpusAlive;
            reward = -1;
            terminal = false;
            won = false;

            switch (action)
            {
                case Action.Up: x--; break;
                case Action.Down: x++; break;
                case Action.Left: y--; break;
                case Action.Right: y++; break;
                case Action.Grab:
                    if (env.Fields[x, y] == FieldType.Gold) { hasG = true; env.Fields[x, y] = FieldType.Empty; reward = 100; }
                    else reward = -10;
                    break;
                case Action.Shoot:
                    bool hit = false;
                    foreach (var (dx, dy) in new (int, int)[] { (-1, 0), (1, 0), (0, -1), (0, 1) })
                    {
                        int nx = x + dx, ny = y + dy;
                        if (wAlive && nx >= 0 && nx < 4 && ny >= 0 && ny < 4 && env.Fields[nx, ny] == FieldType.Wumpus)
                        { 
                            wAlive = false; 
                            env.Fields[nx, ny] = FieldType.Empty; 
                            hit = true; 
                            break; 
                        }
                    }
                    reward = hit ? 50 : -5;
                    break;
                case Action.Exit:
                    if (x == 0 && y == 0 && hasG) 
                    { 
                        reward = 100; 
                        terminal = true;
                        won = true;
                    }
                    else reward = -10;
                    break;
            }

            if (action == Action.Up || action == Action.Down || action == Action.Left || action == Action.Right)
            {
                if (x < 0 || x >= 4 || y < 0 || y >= 4)
                {
                    x = state.X; y = state.Y; reward = -5;
                }
                else if (env.Fields[x, y] == FieldType.Pit || (env.Fields[x, y] == FieldType.Wumpus && wAlive))
                {
                    reward = -100; 
                    terminal = true;
                }
            }

            nextState = new State(x, y, hasG, wAlive);
        }
    }

    internal class Program
    {
        static void Main(string[] args)
        {
            var baseAmb = new Ambient(1, 3, 1);
            var agent = new QLearningAgent(baseAmb);

            Console.WriteLine("Treinando Q-Learning...");
            agent.Train();
            Console.WriteLine("Executando após learning 10 vezes...");
            for (int i = 0; i < 10; i++) agent.RunGreedy();
            Console.WriteLine("Executando encerrada.");
        }
    }
}
