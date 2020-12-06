import random
import copy
from evader import board_distance

class ShortestPathPursuer:
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

    # try action but don't actually update the pursuer's position
    def try_action(self, a):
        dx, dy = self.move(a)
        x = self.x
        y = self.y
        if (self.board[self.x + dx][self.y + dy] != '|'):
            x += dx
            y += dy
        return x, y

    # return postion of the pursuer
    def getPos(self):
        return self.x, self.y

    # print current position
    def print(self):
        print(self.x, self.y)
    
    # policy
    # The pursuer takes the action that minimizes the distance to the 
    # evader
    def Policy(self, evader_position):
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        min_distance = None
        min_distance_action = None
        for a in range(1, 5):
            # Try each action
            x, y = self.try_action(a)
            dist_evader = board_distance(evader_position, (x, y), self.board)
            if min_distance is None or dist_evader < min_distance:
                min_distance = dist_evader
                min_distance_action = a
        return min_distance_action

if __name__ == "__main__":
    # test
    print()