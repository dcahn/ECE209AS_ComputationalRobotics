import copy
import math

class MDP:
    def __init__(self, nevaders=1, npursuers=4):
        self.nevaders = nevaders
        self.npursuers = npursuers
        self.reward_count = []

    def move(self, a):
        if a == 1:
            return -1, 0    # up
        elif a == 2:
            return 1, 0     # down
        elif a == 3:
            return 0, -1    # left
        elif a == 4:
            return 0, 1     # right

        return 0, 0         # invalid action

    # simply MDP
    def Policy(self, board):
        self.init_MDP(board)
        
        # run value iteration for 50 times
        for i in range(50):
            self.value = self.VI(board)
            #self.board_to_string(self.value)
            #self.print()
        return self.policy

    # initial value, reward, and policy for all states
    def init_MDP(self, board):
        self.value = copy.deepcopy(board)
        self.reward = copy.deepcopy(board)
        self.policy = copy.deepcopy(board)

        # set reward and value
        eva_pos = []
        pur_pos = []
        for x in range(len(self.value)):
            for y in range(len(self.value[x])):
                if self.value[x][y] == '.' or self.value[x][y] == ' ':
                    self.value[x][y] = 0
                    self.reward[x][y] = 0

                elif self.value[x][y] == 'e':
                    self.value[x][y] = 400
                    self.reward[x][y] = 0
                    eva_pos = [x, y]

                elif self.value[x][y] == 'p':
                    self.value[x][y] = 0
                    self.reward[x][y] = 0
                    pur_pos.append([x, y])

        # set the reward for 4 position of evader
        for i in range(1,5):
            x, y = eva_pos[0], eva_pos[1]

            # reward sets max of 8 distances away form position of evader
            for k in range(8):  
                dx, dy = self.move(i)
                x += dx
                y += dy

                # break if their is a wall
                if isinstance(self.value[x][y], str):
                    x -= dx
                    y -= dy
                    break

            if i <= 2:
                self.value[x][y] += 300     # up, down
            else:
                self.value[x][y] += 300     # left, right
            
        # negative reward if pursuers are in same line
        for i in range(len(pur_pos)):
            for j in range(i, len(pur_pos)):
                # skip comparing itself
                if i == j:
                    continue
                # check if the pursuers are in same line
                elif self.same_line(pur_pos[i], pur_pos[j], eva_pos):
                    # find the mid position of the pursuers
                    x = (pur_pos[i][0] + pur_pos[j][0])//2
                    y = (pur_pos[i][1] + pur_pos[j][1])//2

                    # special condition that two pursuer are next to each other (no mid position)
                    if (x == pur_pos[i][0] and y == pur_pos[i][1]) or (x == pur_pos[j][0] and y == pur_pos[j][1]):
                        x1, y1 = pur_pos[i][0], pur_pos[i][1]
                        x2, y2 = pur_pos[j][0], pur_pos[j][1]
                        self.reward_count.append([x1, y1, 8])
                        self.reward_count.append([x2, y2, 8])
                    else:
                        self.reward_count.append([x, y, 8])
            
        self.reward_count_down()

    # adding counter for the negative reward for t time steps
    def reward_count_down(self):
        c = 0
        while c < len(self.reward_count):
            x, y, t = self.reward_count[c][0], self.reward_count[c][1], self.reward_count[c][2]
            if t > 0:
                self.reward[x][y] -= 5000
                self.reward_count[c][2] -= 1
            else:
                del self.reward_count[c]
                c -= 1
            c += 1

            
        

    # value iteration
    def VI(self, board):
        value_temp = copy.deepcopy(self.value)

        # loop entire array
        for x in range(len(self.value)):
            for y in range(len(self.value[x])):

                # skip if the cell are walls or or final position
                if isinstance(self.value[x][y], str) or board[x][y] == 'e':
                    continue
                else:
                    # loop 4 actions and calculate each Q(s,a)
                    v_lst = []
                    for i in range(1,5):
                        dx, dy = self.move(i)
                        v = self.value[x+dx][y+dy]
                        r = self.reward[x+dx][y+dy]

                        # if the action will hit the wall, stay in current position
                        if isinstance(v, str) or isinstance(r, str):
                            v = self.value[x][y]
                            r = self.reward[x][y]

                        # Q(s,a)
                        v_lst.append(self.Bellman_Backup(r, v, 0.95))
                    
                    # choose Q_max(s,a) for value and policy
                    value_temp[x][y] = max(v_lst)
                    self.policy[x][y] = v_lst.index(max(v_lst)) + 1

        return value_temp

    # Bellman Backup
    def Bellman_Backup(self, r, v, df):
        return r + df*v

    # check if the position of pursuers is in same line
    def same_line(self, pos1, pos2, eva_pos):
        dx = abs(pos2[0] - pos1[0])
        dy = abs(pos2[1] - pos1[1])

        if dx == 0:
            y = min(pos2[1], pos1[1])
            if y < eva_pos[1] < max(pos2[1], pos1[1]):
                return False

            for i in range(dy):
                if isinstance(self.value[pos1[0]][y + i], str):
                    return False
            return True

        elif dy == 0:
            x = min(pos2[0], pos1[0])
            if x < eva_pos[0] < max(pos2[0], pos1[0]):
                return False
            
            for i in range(dx):
                if isinstance(self.value[x + i][pos1[1]], str):
                    return False
            return True

        return False


    def board_to_string(self, board):
        self.board_str = ""
        for row in board:
            temp = ""
            for col in row:
                temp += str(col)
            self.board_str += temp + "\n"

    def print(self):
        print(self.board_str)