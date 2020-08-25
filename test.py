import json

from board import Board
from collision_avoidance import avoid_obstacles
import behaviour

if __name__ == "__main__":
  with open("example_move.json") as file:
    data = json.load(file)
    board = Board(data)
    print(board.board)
    print(board.hazards)
    print(board.snakes)
    print(board.is_safe(0,0))
    
    print(avoid_obstacles(board, 0, 0))
    print(behaviour.snake_behaviour(data))