from map import Map
#from evader import Evader
from pursuer import Pursuer
import os
import time

class Game():
	def __init__(self, nrows=31, ncols=16, nevaders=1, npursuers=4):
		self.map = Map(nrows,ncols,"""
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

		while self.map.add_wall_obstacle(extend=True):
			pass
		self.board = self.map.makeBoard()

		#self.evader = Evader()
		self.pursers = [Pursuer(1, i+1, self.board) for i in range(npursuers)]

	def step(self):
		# Call evader policy
		# Take evader action

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
		for purser in self.pursers:
			x, y = purser.getPos()
			self.board[x][y] = 'p'
	
	# Remove previous pursuer and evader in board
	def clearBoard(self):
		for x in range(len(self.board)):
			for y in range(len(self.board[x])):
				if self.board[x][y] == 'p' or self.board[x][y] == 'c':
					self.board[x][y] = '.'

	def print(self):
		print(self.map)

	def done(self):
        # if evader is caught:
        #   return True
		for i in range(len(self.board)):
			for j in range(len(self.board[0])):
				if self.board[i][j] == '.':
					return False
		return True


if __name__ == "__main__":
	game = Game()
	game.print()
	time.sleep(5)
	os.system('cls' if os.name == 'nt' else 'clear')
