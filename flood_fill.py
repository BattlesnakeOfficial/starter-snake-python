from board import Board
import numpy as np

import moves
import util
import constants

def compare_moves(board, pos, possible_moves, ignored=[]):

    returned_moves = dict()
    space_per_direction = dict()
    surroundings_per_direction = dict()
    available_spaces_per_direction = dict()
    for name, move in possible_moves.items():
        free_space, available_spaces, surroundings = flood_fill(board, move, ignored)

        space_per_direction[name] = free_space
        surroundings_per_direction[name] = surroundings
        available_spaces_per_direction[name] = available_spaces
    most_free_space = max(space_per_direction.values())

    if should_follow_tail(board, pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
        for name, space in space_per_direction.items():
            my_tail = board.me.tail
            if my_tail in surroundings_per_direction[name] or my_tail in available_spaces_per_direction[name]:
                returned_moves[name] = possible_moves[name]
                continue
    if len(returned_moves) == 0:
        for name, space in space_per_direction.items():
            if space == most_free_space:
                returned_moves[name] = possible_moves[name]
                continue
        

    return returned_moves, space_per_direction

# return True if the snake should follow its own tail
# False otherwise
def should_follow_tail(board, pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
    return True
def flood_fill(board, pos, ignored=[]):
    free_space = 0
    #board_copy = board.board.copy()
    available_spaces = []

    queue = [pos]
    surroundings = []
    if not board.is_safe(pos, ignored):
        return free_space, available_spaces, surroundings
    while len(queue) > 0:
        pos = queue.pop()
        potential_moves = moves.get_moves(pos)

        for move in potential_moves.values():
            x, y = util.get_pos(move)
            if move not in available_spaces and board.is_safe(
                    x, y, ignored=ignored):
                available_spaces.append(move)
                queue.append(move)
                free_space += 1
            elif move not in surroundings:
                surroundings.append(move)
    return free_space, available_spaces, surroundings

def flood_fill_look_ahead(board, pos, possible_moves, ignored=[]):
    prediction_board = board.copy()

    max_free_space, _, _ = flood_fill(prediction_board, pos, ignored)
    possible_moves, space_per_direction = compare_moves(board, pos, possible_moves, ignored)
    print(possible_moves)
    if len(possible_moves) == 1:
        return possible_moves
    returned_moves = dict()
    for name, move in possible_moves.items():
        current_contents = prediction_board.board[move]
        prediction_board.board[move] = constants.MY_HEAD
        possible_movesN, space_per_directionN = compare_moves(board, move, moves.get_moves(x=move[0], y=move[1]), ignored)

        for move_name in possible_movesN:
            if space_per_directionN[move_name] < max_free_space-1:
                continue
            else:
                returned_moves[name] = move
                break
        prediction_board.board[move] = current_contents
    
    return returned_moves