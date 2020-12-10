from game import Game
import argparse
import os
import time
import random
import numpy as np
from shutil import rmtree
from PIL import Image, ImageDraw

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
	parser.add_argument("--video", help="Save game states as images for video", action="store_true", default=False)
	args = parser.parse_args()

	random.seed(args.seed)
	np.random.seed(args.numpy_seed)
	game = Game(args.rows, args.cols, args.evaders, args.pursuers, args.seed, args.bfs, args.empty, args.vi_irrational, args.vi_noirrational, args.pursuer_range)
	game.print()
	num_steps = 0
	if args.video:
		board_img = Image.new('RGB', (100, 230), (255, 255, 255))
		d = ImageDraw.Draw(board_img)
		d.text((0, 0), game.board_str, fill=(0, 0, 0))
		dir_str = 'video_npursuers_%d_seed_%d_npseed_%d_nrows_%d_ncols_%d_empty_%s_viirrational_%s_vinoirrational_%s_pursuerrange_%d' % \
			(args.pursuers, args.seed, args.numpy_seed, args.rows, args.cols, args.empty, args.vi_irrational, args.vi_noirrational, args.pursuer_range)
		if os.path.exists(dir_str):
			rmtree(dir_str)
		os.makedirs(dir_str)
		board_img.save(os.path.join(dir_str, '%02d.png' % num_steps))
	while not game.done():
		game.step()
		game.print()
		num_steps += 1
		if args.video:
			board_img = Image.new('RGB', (100, 230), (255, 255, 255))
			d = ImageDraw.Draw(board_img)
			d.text((0, 0), game.board_str, fill=(0, 0, 0))
			board_img.save(os.path.join(dir_str, '%02d.png' % num_steps))
		time.sleep(0.1)
	print(num_steps)
