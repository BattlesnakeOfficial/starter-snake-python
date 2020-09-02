from board import Board
import collision_avoidance
import moves
import random
import flood_fill
import constants
import util

# define the snake's behaviour
def snake_behaviour(data):
    board = Board(data)
    curr_pos = board.me.head

    possible_moves = search_for_moves(board, curr_pos)

    
    # follow enemy tail if no other options exist
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(board, 
            curr_pos, ignored=[constants.ENEMY_TAIL])
    
    # move into possible enemy next move if necessary
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(board, 
            curr_pos, ignored=[constants.ENEMY_NEXT_MOVE])
    
    move = None
    if len(possible_moves) > 0:
        move = moves.pick_move(possible_moves)
    
    if move == None:
        move = random.choice(moves.all_moves())
    return move

# find possible moves to make from your current position
def search_for_moves(board, curr_pos, ignored=[]):
    possible_moves = board.safe_moves(curr_pos, ignored=ignored)
    
    if len(possible_moves) > 1:
        possible_moves = flood_fill.compare_moves(board, curr_pos, possible_moves, ignored=ignored)
    
    return possible_moves
