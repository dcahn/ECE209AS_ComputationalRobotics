import random
import copy

class Pursuer:
    def __init__(self, x, y, board):
        self.x = x
        self.y = y
        self.board = board

    # decode action
    def move(self, a):
        if a == 1:
            return -1, 0    # left
        elif a == 2:
            return 1, 0     # right
        elif a == 3:
            return 0, -1    # down
        elif a == 4:
            return 0, 1     # up

        return 0, 0         # invalid action

    # action
    def action(self, a):
        dx, dy = self.move(a)
        if (self.board[self.x + dx][self.y + dy] != '|'):
            self.x += dx
            self.y += dy

    # return postion of the pursuer
    def getPos(self):
        return self.x, self.y

    # print current position
    def print(self):
        print(self.x, self.y)
    
    # policy (random action for now)
    def Policy(self, b):
        self.board = copy.deepcopy(b)
        self.init_MDP()
        
        # run value iteration for 50 times
        for i in range(50):
            self.value = self.VI()

        return self.policy[self.x][self.y]


    # initial value, reward, and policy for all states
    def init_MDP(self):
        self.value = copy.deepcopy(self.board)
        self.reward = copy.deepcopy(self.board)
        self.policy = copy.deepcopy(self.board)

        # set reward and value
        for x in range(len(self.value)):
            for y in range(len(self.value[x])):
                if self.value[x][y] == '.' or self.value[x][y] == ' ' or self.value[x][y] == 'p':
                    self.value[x][y] = 0
                    self.reward[x][y] = 0

                elif self.value[x][y] == 'e':
                    self.value[x][y] = 100
                    self.reward[x][y] = 0
    
    # value iteration
    def VI(self):
        value_temp = copy.deepcopy(self.value)

        # loop entire array
        for x in range(len(self.value)):
            for y in range(len(self.value[x])):

                # skip if the cell are walls or or final position
                if isinstance(self.value[x][y], str) or self.board[x][y] == 'e':
                    continue
                else:
                    # loop 4 actions and calculate each Q(s,a)
                    v_lst = []
                    for i in range(4):
                        dx, dy = self.move(i+1)
                        v = self.value[x+dx][y+dy]
                        r = self.reward[x+dx][y+dy]

                        # if the action will hit the wall, stay in current position
                        if isinstance(v, str) or isinstance(r, str):
                            v = self.value[x][y]
                            r = self.reward[x][y]

                        # Q(s,a)
                        v_lst.append(self.Bellman_Backup(r, v, 0.8))
                    
                    # choose Q_max(s,a) for value and policy
                    value_temp[x][y] = max(v_lst)
                    self.policy[x][y] = v_lst.index(max(v_lst)) + 1

        return value_temp

    # Bellman Backup
    def Bellman_Backup(self, r, v, df):
        return r + df*v


        



if __name__ == "__main__":
    # test
    print()