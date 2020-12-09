import random
from evader import distance
from pursuers_value_iteration import PursuersValueIteration
from pursuers_bfs import PursuersBFS

class PursuerLimitedRange:
    # Pursuer that behaves optimally when evader is within a certain spatial distance 
    # and otherwise moves at random
    def __init__(self, num_pursuers, board, pursuer_range, seed=0, use_bfs=False):
        self.num_pursuers = num_pursuers
        self.board = board
        self.pursuer_range = pursuer_range
        self.use_bfs = use_bfs
        if not self.use_bfs:
            self.VI = PursuersValueIteration(num_pursuers, board, seed)
        else:
            self.BFS = PursuersBFS(num_pursuers, board)

    def Policy(self, pursuer_positions, evader_position, pursuer_index):
        if distance(pursuer_positions[pursuer_index], evader_position) > self.pursuer_range:
            return random.randint(1, 4)
        if not self.bfs:
            return self.VI.Policy(pursuer_positions, evader_position)[pursuer_index]
        return self.BFS.bfs(pursuer_positions, evader_position)[0][pursuer_index]

    

    


    
    
