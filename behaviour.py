from board import Board
import collision_avoidance
import moves
import random
import flood_fill
import constants
import util
import goto


# define the snake's behaviour
def snake_behaviour(data):
    board = Board(data)
    curr_pos = board.me.head

    possible_moves = search_for_moves(board, curr_pos)

    # follow enemy tail if no other options exist
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(
            board, curr_pos, ignored=[constants.ENEMY_TAIL])

    # move into possible enemy next move if necessary
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(
            board, curr_pos, ignored=[constants.ENEMY_NEXT_MOVE])

    move = None
    # if only one move if possible, return it
    if len(possible_moves.keys()) == 1:
        move = moves.pick_move(possible_moves)
        return move
    # look for food, if I should do that now
    if len(possible_moves) > 0 and eat_food(board, possible_moves):
        move = goto.find_food(board, curr_pos, possible_moves)
    # pick a random safe move
    if len(possible_moves) > 0 and move == None:
        move = moves.pick_move(possible_moves)
    # if no safe moves are possible, pick a random move to avoid errors
    if move == None:
        move = random.choice(moves.all_moves())
    return move


# find possible moves to make from your current position
def search_for_moves(board, curr_pos, ignored=[]):
    possible_moves = board.safe_moves(curr_pos, ignored=ignored)

    if len(possible_moves) > 1:
        possible_moves = flood_fill.compare_moves(
            board, curr_pos, possible_moves, ignored=ignored)

    return possible_moves


# Should I eat Food?
def eat_food(board, possible_moves):
    return True
