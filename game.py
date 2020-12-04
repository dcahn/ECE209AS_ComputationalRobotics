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
		self.pursers = [Pursuer(1, 3, self.map)] * npursuers

	def step(self):
		# Call evader policy
		# Take evader action

		for purser in self.pursers:
			# remove prev position
			x, y = purser.getPos()
			self.map.clearmap(x, y)

			# Call pursuer policy
			a = purser.policy()

			# Take pursuer action
			purser.action(a)

			#set new position
			x, y = purser.getPos()
			self.map.setmap(x, y, 'p')
		
		# Update board
		pass

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
