import random

from board import Board
import constants
import util
import moves


def avoid_obstacles(board, x, y=None, ignored=[]):
    x, y = util.get_pos(x, y)
    possible_moves = board.safe_moves(x, y, ignored)
    return possible_moves
