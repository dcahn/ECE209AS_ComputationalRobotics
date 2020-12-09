from map import Map
from evader import Evader, board_distance
from pursuer import Pursuer
from MDP import MDP
from pursuer_shortest_path import ShortestPathPursuer
from pursuers_value_iteration import PursuersValueIteration
from pursuers_bfs import PursuersBFS
import os
import time
import random
import numpy as np

class Game():
	def __init__(self, nrows=20, ncols=10, nevaders=1, npursuers=4, seed=0, bfs=False):
		map_string = ""
		center_obstacle_rows = range(nrows // 2 - int(np.ceil(nrows / 8)), nrows // 2 + int(np.ceil(nrows / 8)))
		center_obstacle_cols = range(ncols - (ncols // 2 - 1), ncols)
		for row in range(nrows):
			if row == 0 or row == nrows - 1:
				map_string += '|' * ncols
			else:
				if row in center_obstacle_rows:
					for col in range(ncols):
						if col == 0 or col in center_obstacle_cols:
							map_string += '|'
						else:
							map_string += '.'
				else:
					map_string += ('|' + '.' * (ncols - 1))
			map_string += '\n'
		map = Map(nrows,ncols,map_string)

		while map.add_wall_obstacle(extend=True):
			pass
		self.board = map.makeBoard()
		self.board_str = ""
		# self.MDP = MDP(nevaders, npursuers)
		self.bfs = bfs
		if not bfs:
			self.VI = PursuersValueIteration(npursuers, self.board, seed)
		else:
			self.BFS = PursuersBFS(npursuers, self.board)
		self.policy = None
		self.num_moves = 0

		evader_pursuer_locs_valid = False
		while not evader_pursuer_locs_valid:
			self.evader = Evader(np.random.randint(1, nrows-1), np.random.randint(1, ncols-1), self.board)
			
			# self.pursers = [ShortestPathPursuer(random.randint(1, nrows-2), random.randint(1, ncols-2), self.board) for i in range(npursuers)]
			self.pursers = [Pursuer(np.random.randint(1, nrows-1), np.random.randint(1, ncols-1), self.board) for i in range(npursuers)]
			evader_pursuer_locs_valid = True
			# Check that evader and pursuers do not spawn where there should be walls
			x, y = self.evader.getPos()
			if self.board[x][y] == '|':
				evader_pursuer_locs_valid = False
			for i in range(npursuers):
				x, y = self.pursers[i].getPos()
				if self.board[x][y] == '|':
					evader_pursuer_locs_valid = False
			if not evader_pursuer_locs_valid:
				continue
			# Make sure evader does not spawn in a location with three walls / pursuers around it as in this case, the evader 
			# often does nothing as its only move may be for it to move closer to the pursuers
			num_evader_moves = 0
			for a in range(1, 5):
				evader_cannot_move = False
				x, y = self.evader.try_action(a)
				for i in range(npursuers):
					if self.evader.getPos() == (x, y) or self.pursers[i].getPos() == (x, y):
						evader_cannot_move = True
				if not evader_cannot_move:
					num_evader_moves += 1
			if num_evader_moves <= 1:
				evader_pursuer_locs_valid = False
				continue
			# Make sure evaders and pursuers all spawn at different locations and that pursuers can actually 
			# reach evader
			evader_pursuer_positions = set()
			evader_pursuer_positions.add(self.evader.getPos())
			for i in range(npursuers):
				if self.pursers[i].getPos() in evader_pursuer_positions:
					evader_pursuer_locs_valid = False
				pursuer_evader_dist = board_distance(self.evader.getPos(), self.pursers[i].getPos(), self.board)
				if pursuer_evader_dist is None or pursuer_evader_dist < 10:
					evader_pursuer_locs_valid = False
				evader_pursuer_positions.add(self.pursers[i].getPos())
				
		self.updateBoard()

	def board_to_string(self):
		self.board_str = ""
		for row in self.board:
			temp = ""
			for col in row:
				temp += col
			self.board_str += temp + "\n"

	def step(self):
		# Call evader policy
		# Take evader action
		pursuer_positions = []
		for purser in self.pursers:
			pursuer_positions.append(purser.getPos())
		a = self.evader.policy(pursuer_positions)
		self.evader.action(a)

		# new policy from MDP.py
		'''
		policy = self.MDP.Policy(self.board)
		pur_lst = []
		for purser in self.pursers:
			# Call pursuer policy
			# a = purser.Policy(self.evader.getPos())
			# a = purser.Policy(self.board)

			# Take pursuer action
			x, y = purser.getPos()
			dx, dy = self.move(policy[x][y])

			# avoid pursuers to occupy the same spot
			if [x+dx, y+dy] in pur_lst:
				purser.action(5)
				pur_lst.append([x,y])

			else:
				purser.action(policy[x][y])
				pur_lst.append([x+dx, y+dy])
		'''
		# Maybe add a win check here to match the VI? Anyways pursuers don't need to move if 
		# game is over
		if not self.bfs:
			policy = self.VI.Policy(pursuer_positions, self.evader.getPos())
		else:
			if self.policy is None:
				self.policy = self.BFS.bfs(pursuer_positions, self.evader.getPos())
			policy = self.policy[self.num_moves]
		for i, pursuer in enumerate(self.pursers):
			pursuer.action(policy[i])
		self.num_moves += 1
		# Update board
		self.clearBoard()
		self.updateBoard()
		pass
	
	# Update board using pursuer and evader position
	def updateBoard(self):
		x, y = self.evader.getPos()
		self.board[x][y] = 'e'
		for purser in self.pursers:
			x, y = purser.getPos()
			self.board[x][y] = 'p'

		self.board_to_string()
	
	# Remove previous pursuer and evader in board
	def clearBoard(self):
		for x in range(len(self.board)):
			for y in range(len(self.board[x])):
				if self.board[x][y] == 'p':
					self.board[x][y] = '.'
				elif self.board[x][y] == 'e':
					self.board[x][y] = ' '


	def print(self):
		print(self.board_str)

	def done(self):
		for purser in self.pursers:
			if self.evader.getPos() == purser.getPos():
				return True
		# for i in range(len(self.board)):
		# 	for j in range(len(self.board[0])):
		# 		if self.board[i][j] == '.':
		# 			return False
		return False

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


if __name__ == "__main__":
	game = Game()
	game.print()
	time.sleep(5)
