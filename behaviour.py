from board import Board
import collision_avoidance
import moves
import random

def snake_behaviour(data):
    board = Board(data)
    curr_pos = board.me.head
    
    move = collision_avoidance.avoid_obstacles(board, curr_pos)

    if move == None:
      move = random.choice(moves.all_moves())
    return move
    