from map import Map
from evader import Evader
from pursuer import Pursuer
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

		self.evader = Evader(random.randint(0, nrows), random.randint(0, ncols), self.board)
		self.pursers = [Pursuer(random.randint(0, nrows), random.randint(0, ncols), self.board) for i in range(npursuers)]
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
			a = purser.policy()
			# Take pursuer action
			purser.action(a)

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
				if self.board[x][y] == 'e':
					self.board[x][y] == '.'

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
