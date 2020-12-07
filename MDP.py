import copy

class MDP:
    def __init__(self, nevaders=1, npursuers=4):
        self.nevaders = nevaders
        self.npursuers = npursuers

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

        return self.policy

    # initial value, reward, and policy for all states
    def init_MDP(self, board):
        self.value = copy.deepcopy(board)
        self.reward = copy.deepcopy(board)
        self.policy = copy.deepcopy(board)

        # set reward and value
        eva_x, eva_y = 0, 0
        for x in range(len(self.value)):
            for y in range(len(self.value[x])):
                if self.value[x][y] == '.' or self.value[x][y] == ' ' or self.value[x][y] == 'p':
                    self.value[x][y] = 0
                    self.reward[x][y] = 0

                elif self.value[x][y] == 'e':
                    self.value[x][y] = 500
                    self.reward[x][y] = 0
                    eva_x, eva_y = x, y

        # set the reward for 4 position of evader
        for i in range(1,5):
            x, y = eva_x, eva_y

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
                self.value[x][y] += 100     # up, down
            else:
                self.value[x][y] += 250     # left, right

        #self.board_to_string(self.value)
        #self.print()


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

    def board_to_string(self, board):
        self.board_str = ""
        for row in board:
            temp = ""
            for col in row:
                if isinstance(col, int):
                    temp += str(col)
                else:
                    temp += col
            self.board_str += temp + "\n"

    def print(self):
        print(self.board_str)