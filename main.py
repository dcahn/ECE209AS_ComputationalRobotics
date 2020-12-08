from game import Game
import argparse
import os
import time
import random

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--rows", help="Number of rows in board", default=8, type=int)
	parser.add_argument("-c", "--cols", help="Number of columns in board", default=14, type=int)
	parser.add_argument("-e", "--evaders", help="Number of Evaders in board", default=1, type=int)
	parser.add_argument("-p", "--pursuers", help="Number of Pursuers in board", default=4, type=int)
    parser.add_argument("-s", "--seed", help="Random seed", default=0, type=int)
	args = parser.parse_args()

	random.seed(args.seed)
	game = Game(args.rows, args.cols, args.evaders, args.pursuers, args.seed)
	game.print()
	while not game.done():
		game.step()
		game.print()
		time.sleep(0.1)
