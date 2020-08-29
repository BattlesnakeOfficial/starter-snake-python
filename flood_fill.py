from board import Board
import numpy as np

import moves
import util

def compare_moves(board, pos, possible_moves, ignored=[]):
    
    returned_moves = dict()
    space_per_direction = dict()
    for name, move in possible_moves.items():
        free_space, board_copy, surroundings = flood_fill(board, move, ignored)
        space_per_direction[name] = free_space
    most_free_space = max(space_per_direction.values())
    
    for name, space in space_per_direction.items():
        if space == most_free_space:
            returned_moves[name] = possible_moves[name]
    
    return returned_moves




def flood_fill(board, pos, ignored=[]):
    free_space = 0
    #board_copy = board.board.copy()
    available_spaces = []

    queue = [pos]
    surroundings = []
    while len(queue) > 0:
        pos = queue.pop()
        potential_moves = moves.get_moves(pos)

        for move in potential_moves.values():
            x, y = util.get_pos(move)
            if move not in available_spaces and board.is_safe(x, y, ignored=ignored):
                available_spaces.append(move)
                queue.append(move)
                free_space += 1
            elif move not in surroundings:
                surroundings.append(move)
    return free_space, available_spaces, surroundings
    

