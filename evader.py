import math
from queue import Queue

# Spatial distance between two positions
def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Shortest path distance (BFS) between two positions on the board
def board_distance(pos1, pos2, board):
    bfs_queue = Queue()
    seen_set = set()
    bfs_queue.put((pos1, 0))
    seen_set.add(pos1)

    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while not bfs_queue.empty():
        curr_pos, dist = bfs_queue.get()
        if curr_pos == pos2:
            return dist
        for action in actions:
            dx, dy = action
            x, y = curr_pos
            # Note that here, we assume that pursuers can move to any 
            # non-obstacle space (i.e. that multiple pursuers can be at 
            # the same location)
            next_pos = (x + dx, y + dy)
            if next_pos not in seen_set and (board[x + dx][y + dy] != '|'):
                bfs_queue.put((next_pos, dist + 1))
                seen_set.add(next_pos)
    return None    

class Evader:
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

    # try action but don't actually update the evader's position
    def try_action(self, a):
        dx, dy = self.move(a)
        x = self.x
        y = self.y
        if (self.board[self.x + dx][self.y + dy] != '|'):
            x += dx
            y += dy
        return x, y
    
    # policy
    # The evader takes the action that would maximizes the distance 
    # to the closest pursuer
    def policy(self, pursuer_positions):
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        max_distance = None
        max_distance_action = None
        for a in range(1, 5):
            # Try each action
            x, y = self.try_action(a)
            min_pursuer_distance = None
            # Compute distance to closest pursuer after taking the action
            for pursuer_position in pursuer_positions:
                # dist_pursuer = distance(pursuer_position, (x, y))
                dist_pursuer = board_distance(pursuer_position, (x, y), self.board)
                if min_pursuer_distance is None or dist_pursuer < min_pursuer_distance:
                    min_pursuer_distance = dist_pursuer
            # Update maximum distance to closest pursuer and corresponding action
            if max_distance is None or min_pursuer_distance > max_distance:
                max_distance = min_pursuer_distance
                max_distance_action = a
        return max_distance_action
    
    # return postion of the evader
    def getPos(self):
        return self.x, self.y

    # print current position
    def print(self):
        print(self.x, self.y)


