import random

from board import Board
import constants
import util
import moves


def avoid_obstacles(board, x, y=None, ignored=[]):
    x, y = util.get_pos(x, y)
    possible_moves = safe_moves(board, x, y, ignored)    
    return possible_moves

def safe_moves(board, x, y=None, ignored=[]):
    x, y = util.get_pos(x, y)
    possible_moves = moves.get_moves(x, y)
    returned_moves = dict()
    
    for name, move in possible_moves.items():
        if board.is_safe(move, ignored=ignored):
            returned_moves[name] = move
        else:
            continue
    return returned_moves

