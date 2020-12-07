from map import Map
from evader import Evader, board_distance
from pursuer import Pursuer
from MDP import MDP
from pursuer_shortest_path import ShortestPathPursuer
import os
import time
import random

class Game():
	def __init__(self, nrows=31, ncols=16, nevaders=1, npursuers=4):
		map = Map(nrows,ncols,"""
		||||||||||||||||
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|.........||||||
		|.........||||||
		|.........||||||
		|.........||||||
		|.........||||||
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		||||||||||||||||
		""")

		while map.add_wall_obstacle(extend=True):
			pass
		self.board = map.makeBoard()
		self.board_str = ""
		self.MDP = MDP(nevaders, npursuers)

		evader_pursuer_locs_valid = False
		while not evader_pursuer_locs_valid:
			self.evader = Evader(random.randint(1, nrows-2), random.randint(1, ncols-2), self.board)
			
			# self.pursers = [ShortestPathPursuer(random.randint(1, nrows-2), random.randint(1, ncols-2), self.board) for i in range(npursuers)]
			self.pursers = [Pursuer(random.randint(1, nrows-1), random.randint(1, ncols-1), self.board) for i in range(npursuers)]
			evader_pursuer_locs_valid = True
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
				if board_distance(self.evader.getPos(), self.pursers[i].getPos(), self.board) is None:
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
		policy = self.MDP.Policy(self.board)
		for purser in self.pursers:
			# Call pursuer policy
			# a = purser.Policy(self.evader.getPos())
			# a = purser.Policy(self.board)
			# Take pursuer action
			x, y = purser.getPos()
			purser.action(policy[x][y])
		
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


if __name__ == "__main__":
	game = Game()
	game.print()
	time.sleep(5)
