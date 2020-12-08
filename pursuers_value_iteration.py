import random
import copy
import operator as op
import scipy
import pickle
from functools import reduce
import itertools
import time
from evader import board_distance
from mdptoolbox.mdp import ValueIteration

def board_to_indices(board):
    # Make a grid of indices, where the index at each valid board location 
    # corresponds to a position index
    # Also return a list of board locations corresponding to the position indices
    pos_indices = []
    pos_index = 0
    pos_indices_to_loc = []
    for x in range(len(board)):
        pos_indices.append([])
        for y in range(len(board[x])):
            if board[x][y] == '|':
                pos_indices[x].append(-1)
            else:
                pos_indices[x].append(pos_index)
                pos_indices_to_loc.append((x, y))
                pos_index += 1
    return pos_indices, pos_index, pos_indices_to_loc

class PursuersValueIteration:
    # Pursuer policy that performs value iteration to find a policy for the pursuers.
    def __init__(self, num_pursuers, board, seed):
        self.board = board
        self.num_pursuers = num_pursuers
        self.pos_indices, self.num_pos_indices, self.pos_indices_to_loc = board_to_indices(self.board)
        self.policy = None
        self.seed = seed

    def pursuer_positions_to_index(self, pursuer_positions):
        # Convert pursuer positions to an index by first converting the pursuer's individual positions to 
        # indices. We then convert the position indices to an index (note that this index conversion process 
        # cares about the order of the positions).
        pursuer_pos_indices = [self.pos_indices[x][y] for x, y in pursuer_positions]
        overall_index = 0
        for pursuer_pos_index in pursuer_pos_indices:
            overall_index *= self.num_pos_indices
            overall_index += pursuer_pos_index
        return overall_index

    def index_to_pursuer_positions(self, pursuer_index):
        # Convert the index of the pursuers' positions to the individual positions of the pursuers.
        pursuer_positions = []
        for i in range(self.num_pursuers):
            pursuer_positions.append(pursuer_index % self.num_pos_indices)
            pursuer_index = pursuer_index // self.num_pos_indices
        pursuer_positions.reverse()
        return [self.pos_indices_to_loc[index] for index in pursuer_positions]

    def compute_state_index(self, pursuer_positions, evader_position):
        # Convert pursuers' positions + evader position to a state index
        evader_index = self.pos_indices[evader_position[0]][evader_position[1]]
        pursuer_index = self.pursuer_positions_to_index(pursuer_positions)
        return pursuer_index * self.num_pos_indices + evader_index

    def compute_pursuer_evader_positions(self, state_index):
        # Convert state index to pursuers' positions + evader position
        evader_index = state_index % self.num_pos_indices
        pursuer_index = state_index // self.num_pos_indices
        evader_position = self.pos_indices_to_loc[evader_index]
        pursuer_positions = self.index_to_pursuer_positions(pursuer_index)
        return pursuer_positions, evader_position

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
    
    def compute_alltransitions_reward(self):
        start = time.time()
        pursuer_actions_iter = itertools.product(range(1, 5), repeat=self.num_pursuers)
        num_state_indices = self.num_pos_indices ** (self.num_pursuers + 1)
        print(num_state_indices)
        transitions = []
        rewards = []
        for action_index, pursuer_actions in enumerate(pursuer_actions_iter):
            # print(pursuer_actions)
            transition_row_indices = range(num_state_indices)
            transition_col_indices = []
            transition_probs = [1.0] * num_state_indices
            reward_row_indices = []
            reward_col_indices = []
            rewards_action = []
            for state_index in range(num_state_indices):
                if state_index % 1000 == 0:
                    print(state_index, time.time() - start)
                    # print(time.time() - start)
                # print(state_index)
                pursuer_positions, evader_position = self.compute_pursuer_evader_positions(state_index)
                # print(pursuer_positions)
                pursuer_positions, evader_position, game_won = self.compute_transition(pursuer_positions, evader_position, pursuer_actions)
                new_state_index = self.compute_state_index(pursuer_positions, evader_position)
                transition_col_indices.append(new_state_index)
                if game_won:
                    reward_row_indices.append(state_index)
                    reward_col_indices.append(new_state_index)
                    rewards_action.append(100.0)
                # print("new state:", new_state_index)
            transitions.append(scipy.sparse.csr_matrix((transition_probs, (transition_row_indices, transition_col_indices)), shape=(num_state_indices, num_state_indices)))
            rewards.append(scipy.sparse.csr_matrix((rewards_action, (reward_row_indices, reward_col_indices)), shape=(num_state_indices, num_state_indices)))
            scipy.sparse.save_npz('transitions_action_%d_seed_%d.npz' % (action_index, self.seed) transitions[-1])
            scipy.sparse.save_npz('rewards_action_%d_seed_%d.npz' % (action_index, self.seed) rewards[-1])
        return transitions, rewards   

    def valueIteration(self):
        transitions, rewards = self.compute_alltransitions_reward()
        valueIterationMDP = ValueIteration(transitions, rewards, 0.99)
        valueIterationMDP.run()
        pickle.dump(valueIterationMDP.policy, 'policy_seed_%d.pkl' % self.seed)
        return valueIterationMDP.policy

    def Policy(self, pursuer_positions, evader_position):
        if self.policy is None:
            self.policy = self.valueIteration()
        state_index = self.compute_state_index(pursuer_positions, evader_position)
        action_index = self.policy[state_index]
        pursuer_actions = []
        for i in range(self.num_pursuers):
            pursuer_actions.append(action_index % 4 + 1)
            action_index = action_index // 4
        pursuer_actions.reverse()
        return pursuer_actions

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
                # dist_pursuer = distance(pursuer_position, (x, y))
                dist_pursuer = board_distance(pursuer_position, (x, y), self.board)
                if min_pursuer_distance is None or dist_pursuer < min_pursuer_distance:
                    min_pursuer_distance = dist_pursuer
            # Update maximum distance to closest pursuer and corresponding action
            if max_distance is None or min_pursuer_distance > max_distance:
                max_distance = min_pursuer_distance
                max_distance_action = a
                x_afteraction = x
                y_afteraction = y
        return x_afteraction, y_afteraction

    def check_win(self, pursuer_positions, evader_position):
        for pursuer_position in pursuer_positions:
            if pursuer_position == evader_position:
                return True
        return False


    
    
