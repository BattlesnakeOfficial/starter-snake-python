from board import Board
import collision_avoidance
import moves
import random
import flood_fill
import constants
import util


def snake_behaviour(data):
    board = Board(data)
    curr_pos = board.me.head

    possible_moves = moves.get_moves(curr_pos)
    possible_moves = collision_avoidance.avoid_obstacles(board, curr_pos)

    #possible_moves = flood_fill.compare_moves(board, curr_pos, possible_moves)

    move = None
    if len(possible_moves) > 0:
        move = random.choice(list(possible_moves.keys()))

    # follow your own tail if necessary
    if len(possible_moves) == 0:
        possible_moves = collision_avoidance.safe_moves(
            board, curr_pos, ignored=[constants.MY_TAIL])
    # follow enemy tail if no other options exist
    if len(possible_moves) == 0:
        possible_moves = collision_avoidance.safe_moves(
            board, curr_pos, ignored=[constants.ENEMY_TAIL])
    if move == None:
        move = random.choice(moves.all_moves())
    return move
