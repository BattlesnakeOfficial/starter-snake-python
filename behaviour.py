from board import Board
import collision_avoidance

def snake_behaviour(data):
    board = Board(data)
    curr_pos = board.me.head
    
    move = collision_avoidance.avoid_obstacles(board, curr_pos)
    return move
    