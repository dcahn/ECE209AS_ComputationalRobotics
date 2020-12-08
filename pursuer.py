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
            return -1, 0    # up
        elif a == 2:
            return 1, 0     # down
        elif a == 3:
            return 0, -1    # left
        elif a == 4:
            return 0, 1     # right

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
    
   

if __name__ == "__main__":
    # test
    print()