from queue import Queue
import itertools
from evader import board_distance, distance

class PursuersBFS:
    # Pursuer policy that performs BFS to find optimal policy for all pursuers
    def __init__(self, num_pursuers, board):
        self.board = board
        self.num_pursuers = num_pursuers
        
    def compute_transition(self, pursuer_positions, evader_position, pursuer_actions):
        pursuer_newpositions = []
        # If we've already won, keep the state the same (i.e. pursuers and evader do not move)
        game_won = self.check_win(pursuer_positions, evader_position)
        if game_won:
            return pursuer_positions, evader_position, True
        for pursuer_index, pursuer_action in enumerate(pursuer_actions):
            pursuer_newposition = self.pursuer_try_action(pursuer_positions[pursuer_index], pursuer_action)
            pursuer_newpositions.append(pursuer_newposition)
        # If we win after pursuers move, the evader cannot move anymore so return the new pursuers' positions 
        # and evader's old position
        game_won = self.check_win(pursuer_newpositions, evader_position)
        if game_won:
            return pursuer_newpositions, evader_position, True
        evader_newposition = self.evader_move(evader_position, pursuer_newpositions)
        # Check for win after evader moves (as evader has to move in one of the four directions, if evader is 
        # surrounded by pursuers, it's forced to move for a loss)
        game_won = self.check_win(pursuer_newpositions, evader_newposition)
        if game_won:
            return pursuer_newpositions, evader_position, True
        return pursuer_newpositions, evader_newposition, False
        
    def check_win(self, pursuer_positions, evader_position):
        for pursuer_position in pursuer_positions:
            if pursuer_position == evader_position:
                return True
        return False
        
    def bfs(self, pursuer_positions, evader_position):
        pursuer_positions_tuple = tuple(pursuer_positions)
        bfs_queue = Queue()
        seen_set = set()
        bfs_queue.put((pursuer_positions, evader_position, []))
        seen_set.add((pursuer_positions_tuple, evader_position))
        while not bfs_queue.empty():
            pursuer_positions, evader_position, pursuer_actions_list = bfs_queue.get()
            if self.check_win(pursuer_positions, evader_position):
                return pursuer_actions_list
            pursuer_actions_iter = itertools.product(range(1, 5), repeat=self.num_pursuers)
            for action_index, pursuer_actions in enumerate(pursuer_actions_iter):
                pursuer_newpositions, evader_newposition, _ = self.compute_transition(pursuer_positions, evader_position, pursuer_actions)
                if (tuple(pursuer_newpositions), evader_newposition) in seen_set:
                    continue
                pursuer_actions_newlist = pursuer_actions_list.copy()
                pursuer_actions_newlist.append(pursuer_actions)
                bfs_queue.put((pursuer_newpositions, evader_newposition, pursuer_actions_newlist))
                seen_set.add((tuple(pursuer_newpositions), evader_newposition))
        return None
        
    # return dx, dy corresponding to action
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

    # try action for a pursuer but don't actually update the pursuer's position
    def pursuer_try_action(self, pursuer_position, a):
        dx, dy = self.move(a)
        x, y = pursuer_position
        if (self.board[x + dx][y + dy] != '|'):
            x += dx
            y += dy
        return x, y

    # policy
    # The evader takes the action that would maximizes the distance 
    # to the closest pursuer
    def evader_move(self, evader_position, pursuer_positions):
        max_distance = None
        max_distance_action = None
        x_afteraction = None
        y_afteraction = None
        for a in range(1, 5):
            # Try each action
            x, y = evader_position
            dx, dy = self.move(a)
            if (self.board[x + dx][y + dy] != '|'):
                x += dx
                y += dy
            min_pursuer_distance = None
            # Compute distance to closest pursuer after taking the action
            for pursuer_position in pursuer_positions:
                dist_pursuer = distance(pursuer_position, (x, y))
                # dist_pursuer = board_distance(pursuer_position, (x, y), self.board)
                if min_pursuer_distance is None or dist_pursuer < min_pursuer_distance:
                    min_pursuer_distance = dist_pursuer
            # Update maximum distance to closest pursuer and corresponding action
            if max_distance is None or min_pursuer_distance > max_distance:
                max_distance = min_pursuer_distance
                max_distance_action = a
                x_afteraction = x
                y_afteraction = y
        return x_afteraction, y_afteraction
            
            
        
        
