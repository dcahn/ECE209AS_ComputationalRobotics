from map import Map
from evader import Evader
from pursuer import Pursuer
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

		self.evader = Evader(random.randint(1, nrows-1), random.randint(1, ncols-1), self.board)
        
		self.pursers = [ShortestPathPursuer(random.randint(1, nrows-1), random.randint(1, ncols-1), self.board) for i in range(npursuers)]
		# self.pursers = [Pursuer(random.randint(1, nrows-1), random.randint(1, ncols-1), self.board) for i in range(npursuers)]
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

		for purser in self.pursers:
			# Call pursuer policy
			a = purser.Policy(self.evader.getPos())
			# a = purser.Policy(self.board)
			# Take pursuer action
			purser.action(a)

		# Update board
		self.clearBoard()
		self.updateBoard()
		pass
	
	# Update board using pursuer and evader position
	def updateBoard(self):
		for purser in self.pursers:
			x, y = purser.getPos()
			self.board[x][y] = 'p'
		
		x, y = self.evader.getPos()
		self.board[x][y] = 'e'

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
		#for purser in self.pursers:
		#	if self.evader.getPos() == purser.getPos():
		#		return True
		for i in range(len(self.board)):
			for j in range(len(self.board[0])):
				if self.board[i][j] == '.':
					return False
		return True


if __name__ == "__main__":
	game = Game()
	game.print()
	time.sleep(5)
