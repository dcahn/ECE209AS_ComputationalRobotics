import random
import copy
import os
import operator as op
import scipy
import pickle
from functools import reduce
import itertools
import time
from evader import board_distance, distance
from pursuers_value_iteration import PursuersValueIteration
from pursuer_limitedrange import PursuerLimitedRange
from mdptoolbox.mdp import ValueIteration
import multiprocessing as mp

class PursuersVIIrrational(PursuersValueIteration):
    # Pursuer policy that performs value iteration to find a policy for the pursuers 
    # given that one of the pursuers follows an irrational policy. We assume the irrational 
    # pursuer is the first pursuer.
    def __init__(self, num_pursuers, board, seed, pursuer_range, use_bfs=False):
        self.pursuer_range = pursuer_range
        self.irrational_pursuer = PursuerLimitedRange(num_pursuers, board, pursuer_range, seed, use_bfs)
        super().__init__(num_pursuers, board, seed)
    
    def compute_transition(self, pursuer_positions, evader_position, pursuer_actions):
        pursuer_newpositions = []
        # If we've already won, keep the state the same (i.e. pursuers and evader do not move)
        game_won = self.check_win(pursuer_positions, evader_position)
        if game_won:
            pursuer_newpositions = [[pursuer_positions[0]]] + pursuer_positions[1:]
            return pursuer_newpositions, evader_position, [True]
        irrational_pursuer_positions = []
        if distance(pursuer_positions[0], evader_position) > self.pursuer_range:
            for pursuer_action in range(1, 5):
                irrational_pursuer_newposition = self.pursuer_try_action(pursuer_positions[0], pursuer_action)
                irrational_pursuer_positions.append(irrational_pursuer_newposition)
        else:
            irrational_pursuer_newposition = self.irrational_pursuer.Policy(pursuer_positions, evader_position, 0)
            irrational_pursuer_positions.append(irrational_pursuer_newposition)
        pursuer_newpositions.append(irrational_pursuer_positions)
        for pursuer_index, pursuer_action in enumerate(pursuer_actions):
            pursuer_newposition = self.pursuer_try_action(pursuer_positions[pursuer_index + 1], pursuer_action)
            pursuer_newpositions.append(pursuer_newposition)
        # If we win after pursuers move, the evader cannot move anymore so return the new pursuers' positions 
        # and evader's old position
        game_won_list = []
        evader_newpositions = []
        for irrational_pursuer_newposition in pursuer_newpositions[0]:
            pursuer_newpositions_poss = [irrational_pursuer_newposition] + pursuer_newpositions[1:]
            game_won = self.check_win(pursuer_newpositions_poss, evader_position)
            if game_won:
                game_won_list.append(True)
                evader_newpositions.append(evader_position)
                continue
            evader_newposition = self.evader_move(evader_position, pursuer_newpositions_poss)
            evader_newpositions.append(evader_newposition)
            # Check for win after evader moves (as evader has to move in one of the four directions, if evader is 
            # surrounded by pursuers, it's forced to move for a loss)
            game_won = self.check_win(pursuer_newpositions_poss, evader_newposition)
            if game_won:
                game_won_list.append(True)
            else:
                game_won_list.append(False)
        return pursuer_newpositions, evader_newpositions, game_won_list

    def parallelize(self, iteration):
        start = time.time()
        action_index, pursuer_actions = iteration
        transitions_filename = 'transitions_action_%d_npursuers_%d_seed_%d_irrationalpursuer.npz' % (action_index, self.num_pursuers, self.seed)
        rewards_filename = 'rewards_action_%d_npursuers_%d_seed_%d_irrationalpursuer.npz' % (action_index, self.num_pursuers, self.seed)
        if os.path.exists(transitions_filename) and os.path.exists(rewards_filename):
            return scipy.sparse.load_npz(transitions_filename), scipy.sparse.load_npz(rewards_filename)
        # print(pursuer_actions)
        transition_row_indices = []
        transition_col_indices = []
        transition_probs = []
        reward_row_indices = []
        reward_col_indices = []
        rewards_action = []
        for state_index in range(self.num_state_indices):
            if state_index % 1000 == 0:
                print(state_index, time.time() - start)
                # print(time.time() - start)
            # print(state_index)
            pursuer_positions, evader_position = self.compute_pursuer_evader_positions(state_index)
            # print(pursuer_positions)
            # print("Old: ", state_index, pursuer_positions, evader_position, pursuer_actions)
            pursuer_positions_list, evader_positions_list, game_won_list = self.compute_transition(pursuer_positions, evader_position, pursuer_actions)
            new_state_num_seen = {}
            for pos_index, irrational_pursuer_position in enumerate(pursuer_positions_list[0]):
                pursuer_positions = [irrational_pursuer_position] + pursuer_positions_list[1:]
                evader_position = evader_positions_list[pos_index]
                game_won = game_won_list[pos_index]
                new_state_index = self.compute_state_index(pursuer_positions, evader_position)
                # print("New: ", new_state_index, pursuer_positions, evader_position)
                # if new_state_index < 0:
                #     print(self.board_to_string())
                assert(new_state_index >= 0)
                if new_state_index not in new_state_num_seen:
                    new_state_num_seen[new_state_index] = 1
                    if game_won:
                        reward_row_indices.append(state_index)
                        reward_col_indices.append(new_state_index)
                        rewards_action.append(100.0)
                else:
                    new_state_num_seen[new_state_index] += 1
            for new_state_index, num_seen in new_state_num_seen.items():
                transition_row_indices.append(state_index)
                transition_col_indices.append(new_state_index)
                transition_prob = 1.0 if len(pursuer_positions_list[0]) == 1 else 0.25 * num_seen
                transition_probs.append(transition_prob)
                
            # print("new state:", new_state_index)
        transition = scipy.sparse.csr_matrix((transition_probs, (transition_row_indices, transition_col_indices)), shape=(self.num_state_indices, self.num_state_indices))
        reward = scipy.sparse.csr_matrix((rewards_action, (reward_row_indices, reward_col_indices)), shape=(self.num_state_indices, self.num_state_indices))
        #scipy.sparse.save_npz('transitions_action_%d_npursuers_%d_seed_%d.npz' % (action_index, self.num_pursuers, self.seed), transition)
        #scipy.sparse.save_npz('rewards_action_%d_npursuers_%d_seed_%d.npz' % (action_index, self.num_pursuers, self.seed), reward)
        return transition, reward

    def compute_alltransitions_reward(self):
        pursuer_actions_iter = itertools.product(range(1, 5), repeat=self.num_pursuers - 1)
        self.num_state_indices = self.num_pos_indices ** (self.num_pursuers + 1)
        print(self.num_state_indices)
        transitions = []
        rewards = []
        pool = mp.Pool(16)
        transitions, rewards = zip(*pool.map(self.parallelize, enumerate(pursuer_actions_iter)))
        return transitions, rewards   

    def valueIteration(self):
        policy_filename = 'policy_npursuers_%d_seed_%d_irrationalpursuer.pkl' % (self.num_pursuers, self.seed)
        if os.path.exists(policy_filename):
            with open(policy_filename, 'rb') as policy_file:
                policy = pickle.load(policy_file)
            return policy
        transitions, rewards = self.compute_alltransitions_reward()
        valueIterationMDP = ValueIteration(transitions, rewards, 0.99, skip_check=True)
        valueIterationMDP.run()
        with open(policy_filename, 'wb') as policy_file:
            pickle.dump(valueIterationMDP.policy, policy_file)
        return valueIterationMDP.policy

    def Policy(self, pursuer_positions, evader_position):
        if self.policy is None:
            self.policy = self.valueIteration()
        state_index = self.compute_state_index(pursuer_positions, evader_position)
        action_index = self.policy[state_index]
        pursuer_actions = []
        for i in range(self.num_pursuers - 1):
            pursuer_actions.append(action_index % 4 + 1)
            action_index = action_index // 4
        pursuer_actions.reverse()
        return pursuer_actions
