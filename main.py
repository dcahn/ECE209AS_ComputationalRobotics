from game import Game
import argparse
import os
import time
import random
import numpy as np

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--rows", help="Number of rows in board", default=20, type=int)
	parser.add_argument("-c", "--cols", help="Number of columns in board", default=16, type=int)
	parser.add_argument("-e", "--evaders", help="Number of Evaders in board", default=1, type=int)
	parser.add_argument("-p", "--pursuers", help="Number of Pursuers in board", default=4, type=int)
	parser.add_argument("-s", "--seed", help="Random seed for board", default=0, type=int)
	parser.add_argument("-ns", "--numpy_seed", help="Random seed for starting positions", default=1, type=int)
	parser.add_argument("--bfs", help="Use BFS to compute optimal pursuer actions", action='store_true', default=False)
	parser.add_argument("--empty", help="Use empty board", action="store_true", default=False)
	parser.add_argument("--vi-irrational", help="Use VI accounting for irrational pursuer", action="store_true", default=False)
	parser.add_argument("--vi-noirrational", help="Use VI not accounting for irrational pursuer", action="store_true", default=False)
	parser.add_argument("--pursuer-range", help="Range for irrational pursuer", default=4, type=float)
	args = parser.parse_args()

	random.seed(args.seed)
	np.random.seed(args.numpy_seed)
	game = Game(args.rows, args.cols, args.evaders, args.pursuers, args.seed, args.bfs, args.empty, args.vi_irrational, args.vi_noirrational, args.pursuer_range)
	game.print()
	while not game.done():
		game.step()
		game.print()
		time.sleep(0.1)
