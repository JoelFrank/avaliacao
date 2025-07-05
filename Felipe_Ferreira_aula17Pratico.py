import random
import os


class SARSA:
    def __init__(self):
        self.REscapedGold = +100.0
        self.REscapedGoldKilledWumpus = +200.0
        self.RKillWum = +20.0
        self.RFoundGold = +20.0
        self.RDeath = -100.0
        self.RMissWum = -5.0
        self.RMove = -0.5

        self.Qtable = []
        self.QtableGold = []
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilonDecay = 0.9

        self.lastChoice = -1
        self.lastPosition = [-1, -1]
        self.currentPosition = [-1, -1]
        self.nextChoice = -1
        self.hasGold = 0
        self.arrows = 1
        self.wumpusAlive = 1
        self.test = []
        self.row = 4
        self.col = 4
        
    def buildQtable(self):
        for i in range(self.row):
            row = []
            for j in range(self.col):
                action = []
                list1 = []
                list2 = []
                if i != 0:
                    list1.append(0)
                    list1.append(0)
                    list2.append(0)
                    list2.append(0)
                if i != self.row-1:
                    list1.append(0)
                    list1.append(0)
                    list2.append(0)
                    list2.append(0)
                if j != 0:
                    list1.append(0)
                    list1.append(0)
                    list2.append(0)
                    list2.append(0)
                if j != self.col-1:
                    list1.append(0)
                    list1.append(0)
                    list2.append(0)
                    list2.append(0)
                action.append(list1)
                action.append(list2)
                row.append(action)
            self.Qtable.append(row)

    def findR(self, i, j, map, start):
        if map[i][j][1] == "W" or map[i][j][2] == "P":
            return self.RDeath
        if map[i][j][3] == "G":
            self.hasGold = 1
            return self.RFoundGold
        if i == start[0] and j == start[1] and self.hasGold == 1:
            if self.wumpusAlive == 1:
                return self.REscapedGold
            else:
                return self.REscapedGoldKilledWumpus
        return self.RMove
        
    def updateQtable(self, position, map, start):
        retSTR = ""
        i = position[0]
        j = position[1]
        g = self.hasGold

        action = self.Qtable[position[0]][position[1]][self.hasGold]
        half = len(action)//2

        if self.nextChoice > half-1 and self.wumpusAlive == 0 and self.arrows == 0:
            r = self.RKillWum
        else:
            r = self.findR(i, j, map, start)
        retSTR = self.policy(position)

        l = self.lastPosition[0]
        m = self.lastPosition[1]
        k2 = self.nextChoice
        k = self.lastChoice
        g2 = self.hasGold


        self.Qtable[l][m][g][k] = self.Qtable[l][m][g][k] + self.alpha * (r + self.gamma*(self.Qtable[i][j][g2][k2]) - self.Qtable[l][m][g][k])
        
        if k > half-1:
            if g == 0:
                self.Qtable[l][m][1][k] = self.Qtable[l][m][0][k]
            else:
                self.Qtable[l][m][0][k] = self.Qtable[l][m][1][k]
        
        return retSTR
     
    def policy(self, position):
        retSTR = "move"
        action = self.Qtable[position[0]][position[1]][self.hasGold]
        half = len(action)//2
        if self.arrows == 0:
            tam = half-1
            lista = action[:half]
        else:
            tam = len(action)-1
            lista = action


        if random.random() < self.epsilon:
            choice = random.randint(0,tam)
        else:
            choice = lista.index(max(lista))

        self.lastPosition[0] = self.currentPosition[0]
        self.lastPosition[1] = self.currentPosition[1]
        self.currentPosition[0] = position[0]
        self.currentPosition[1] = position[1]

        self.lastChoice = self.nextChoice
        self.nextChoice = choice
        if choice > half-1:
            retSTR = "shoot"
            self.test.append(self.arrows)
        return retSTR        

class Player:
    def __init__(self,narrow,start):
        self.score = 0
        self.currentScore = 0
        self.arrow = narrow
        self.position = [start[0],start[1]]
        self.gold = 0

    def move(self, map, choice, movecost, diecost):
        map[self.position[0]][self.position[1]][0] = "N"

        if choice == "up":
            self.position[0] -= 1
        if choice == "down":
            self.position[0] += 1
        if choice == "left":
            self.position[1] -= 1
        if choice == "right":
            self.position[1] += 1 

        map[self.position[0]][self.position[1]][0] = "H"
        map[self.position[0]][self.position[1]][4] = "V"

        self.score -= movecost
        self.currentScore -= movecost

        if map[self.position[0]][self.position[1]][1] == "W":
            self.score -= diecost
            self.currentScore -=diecost
            return "wumpus"

        if map[self.position[0]][self.position[1]][2] == "P":
            self.score -= diecost
            self.currentScore -= diecost
            return "pit"
        
        return "nothing"

    def shoot(self, map, choice, killscore):
        self.arrow -= 1
        a = 0
        b = 0

        if choice == "up":
            a = -1
        if choice == "down":
            a = 1
        if choice == "left":
            b = -1
        if choice == "right":
            b = 1

        if map[self.position[0]+a][self.position[1]+b][1] == "W":
            map[self.position[0]+a][self.position[1]+b][1] = "X"
            self.score += killscore
            self.currentScore += killscore
            return "hit"
        
        return "missed"

class Game:
    def __init__(self):
        self.map = []
        self.row = 4
        self.col = 4
        self.nwumpus = 1
        self.npit = 3
        self.ngold = 1
        self.narrow = 1
        self.killscore = 50
        self.goldscore = 50
        self.movecost = 1
        self.diecost = 100
        self.start = [self.row-1,0]
        self.player = Player(self.narrow,self.start)
        self.first = 1
        self.choice = ""
        self.ff = 1
        self.agent2 = SARSA()
        self.agent2.buildQtable()

    def printline(self):
        print(end="  ")
        for i in range(self.col):
            print("----------", end="")
        print("-")

    def printmap(self):
        os.system('cls')
        
        print("Arrow:", self.player.arrow, end=" ")
        print("Current Score:", self.player.currentScore, end=" ")
        print("Total Score:", self.player.score)

        self.printline()

        for i in range(self.row):
            print(self.row-i, end=" ")
            for j in range(self.col):
                print("|", end=" ")
                for k in range(4):
                    if self.map[i][j][4] == "V":
                        print(self.map[i][j][k], end=" ")
                    else:
                        print("?", end=" ")
            print("|")
            self.printline()

        print(end="  ")
        for j in range(self.col):
            print("    ",j+1, end="    ")
        print(" ")
        print()
            
    def validrandom(self):
        nrow = self.start[0]
        ncol = self.start[1]
        while self.map[nrow][ncol][0] == "H" or self.map[nrow][ncol][1] == "W" or self.map[nrow][ncol][2] == "P" or self.map[nrow][ncol][3] == "G":
            nrow = random.randint(0,self.row-1)
            ncol = random.randint(0,self.col-1)
        return [nrow,ncol]
    
    def adjinsert(self,nrow,ncol,mainc,adjc,layer):
        self.map[nrow][ncol][layer] = mainc
        if nrow != 0 and self.map[nrow-1][ncol][layer] != mainc:
            self.map[nrow-1][ncol][layer] = adjc
        if nrow != self.row-1 and self.map[nrow+1][ncol][layer] != mainc:
            self.map[nrow+1][ncol][layer] = adjc
        if ncol != 0 and self.map[nrow][ncol-1][layer] != mainc:
            self.map[nrow][ncol-1][layer] = adjc
        if ncol != self.col-1 and self.map[nrow][ncol+1][layer] != mainc:
            self.map[nrow][ncol+1][layer] = adjc
        
    def setup(self,first):
        rn = []

        if first == 1:
            for i in range(self.row):
                row = []
                for j in range(self.col):
                    layers = ["N","N","N","N","U"]
                    row.append(layers)
                self.map.append(row)  
        else:
            self.agent2.wumpusAlive = 1
            self.agent2.hasGold = 0
            self.agent2.lastChoice = -1
            self.agent2.nextChoice = -1
            self.agent2.lastPosition[0] = -1
            self.agent2.lastPosition[1] = -1
            self.agent2.currentPosition[0] = -1
            self.agent2.currentPosition[1] = -1
            self.player.position = [self.start[0],self.start[1]]
            self.player.currentScore = 0

            for i in range(self.row):
                for j in range(self.col):
                    self.map[i][j][4] = "U"
                    if self.map[i][j][3] == "X":
                        self.map[i][j][3] = "G"
                    if self.map[i][j][1] == "X":
                        self.map[i][j][1] = "W"
                    if self.map[i][j][0] == "H":
                        self.map[i][j][0] = "N"

        self.agent2.arrows = self.narrow
        self.player.arrow = self.narrow

        self.map[self.start[0]][self.start[1]][0] = "H"

        if first == 1:
            for i in range(self.nwumpus):
                rn = self.validrandom()
                self.adjinsert(rn[0],rn[1],"W","S",1)

            for i in range(self.npit):
                rn = self.validrandom()
                self.adjinsert(rn[0],rn[1],"P","B",2)

            for i in range(self.ngold):
                rn = self.validrandom()
                self.map[rn[0]][rn[1]][3] = "G"

        self.map[self.start[0]][self.start[1]][4] = "V"
        
    def printoptions(self,list):
        for i in list:
            if list[i] == 1:
                print(i, end=" ")
        print()
    
    def optionsList(self, list):
        retList = []
        for i in list:
            if list[i] == 1:
                retList.append(i)
        return retList
    
    def validinput(self,list,choice = ""):
        choice = input()
        while choice not in list or list[choice] != 1:
            print("invalid input")
            choice = input()
        return choice
    
    def checklist(self,actionlist,directionlist):
        if self.player.position[0] != 0:
            directionlist["up"] = 1
        if self.player.position[0] != self.row-1:
            directionlist["down"] = 1

        if self.player.position[1] != 0:
            directionlist["left"] = 1
        if self.player.position[1] != self.col-1:
            directionlist["right"] = 1

        if self.player.arrow > 0:
            actionlist["shoot"] = 1
        
        if self.map[self.player.position[0]][self.player.position[1]][3] == "G":
            actionlist["loot"] = 1

        if self.player.position[0] == self.start[0] and self.player.position[1] == self.start[1]:
            actionlist["escape"] = 1

    def makelist(self, directionlist):
        retlist = []

        if directionlist["up"] == 1:
            retlist.append("up")
        if directionlist["down"] == 1:
            retlist.append("down")
        if directionlist["left"] == 1:
            retlist.append("left")
        if directionlist["right"] == 1:
            retlist.append("right")

        if directionlist["up"] == 1:
            retlist.append("up")
        if directionlist["down"] == 1:
            retlist.append("down")
        if directionlist["left"] == 1:
            retlist.append("left")
        if directionlist["right"] == 1:
            retlist.append("right")

        return retlist

    def menuplayer(self):
        actionlist = {"move": 1,"shoot": 0,"loot": 0,"escape": 0}
        directionlist = {"up": 0, "down": 0, "left": 0,"right": 0}

        self.checklist(actionlist,directionlist)       
        dlist = self.makelist(directionlist)

        print("Action:", end=" ")
        self.printoptions(actionlist)
        

        if self.first == 1:
            self.choice = self.agent2.policy(self.player.position)
            self.first += 1
        choice = self.choice
        if self.map[self.player.position[0]][self.player.position[1]][3] == "G":
            choice = "loot"
        elif self.player.position[0] == self.start[0] and self.player.position[1] == self.start[1] and self.agent2.hasGold == 1:
            choice = "escape"
        print("Choice: ", choice)

      
        if choice == "move":
            print("Direction:", end=" ")
            self.printoptions(directionlist)

            choice = dlist[self.agent2.nextChoice]
            print("Choice: ", choice)

            if self.ff == 0:
                input("...")

            result = self.player.move(self.map,choice,self.movecost,self.diecost)
            self.printmap()
            if result == "wumpus":
                self.printmap()
                print("Game Over")
                print("Killed by Wumpus")
                print("Final Score:", self.player.score)
                if self.ff == 0:
                    input("...")
            if result == "pit":
                self.printmap()
                print("Game Over")
                print("Fell into a Pit")
                print("Final Score:", self.player.score)
                if self.ff == 0:
                    input("...")

        elif choice == "shoot":
            self.agent2.arrows -= 1
            print("Direction:", end=" ")
            self.printoptions(directionlist)

            choice = dlist[self.agent2.nextChoice]
            print("Choice: ", choice)
            if self.ff == 0:
                input("...")

            result = self.player.shoot(self.map,choice,self.killscore)
            if result == "hit":
                self.printmap()
                self.agent2.wumpusAlive = 0
                print("Wumpus killed")
                if self.ff == 0:
                    input("...")
            if result == "missed":
                self.printmap()
                print("Arrow missed")
                if self.ff == 0:
                    input("...")

        elif choice == "loot":
            result = "looted"
            self.map[self.player.position[0]][self.player.position[1]][3] = "X"
            self.player.gold += 1
            self.printmap()
            print("Looted the Gold")
            if self.ff == 0:
                input("...")

        elif choice == "escape":
            result = "escaped"
            self.player.score += self.player.gold*self.goldscore
            self.player.currentScore += self.player.gold*self.goldscore
            self.player.gold = 0
            self.printmap()
            print("Escaped the cave")
            if self.ff == 0:
                input("...")

       
        if choice != "loot":
            self.choice = self.agent2.updateQtable(self.player.position, self.map, self.start)

        return result
    
    
    def gameloop(self, n):
        loop = 1

        self.printmap()
        if self.ff == 0:
            input("...")
        while loop >= 1:

            result = self.menuplayer()

            if result == "wumpus":
                loop = 0
            if result == "pit":
                loop = 0
            if result == "escaped":
                loop = 0
            
            if loop == 0:
                n += 1
                self.agent2.epsilon *= self.agent2.epsilonDecay
                
                if self.ff == 0:
                    input("...")

                self.setup(0)
                self.printmap()
                loop = 1
                self.first = 1
                
            if n == 50:
                loop = 2
                self.ff = 0
            if n == 55:
                loop = 0

                
newGame = Game()
newGame.setup(1)
newGame.gameloop(0)