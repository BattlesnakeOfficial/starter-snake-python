import json

from board import Board
from collision_avoidance import avoid_obstacles
import behaviour
import util
from goto import find_food
import moves

def test_food_behaviour(board):
    my_head = board.me.head
    enemy_head = board.get_snakes()[1].head
    
    head = enemy_head
    food = board.food
    
    print("\n\nTesting Food")
    print(head)
    print("Food", board.food)
    for pos in board.food:
        print(util.distance(head, pos))
    
    board.food.sort(key=lambda food: util.distance(head, food))
    
    print("Food after sort:", board.food)
    for pos in board.food:
        print(util.distance(head, pos))
    print("\n\nTesting find_food()")
    print("Find food", find_food(board, enemy_head, moves.all_moves()))
    

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
    
    print(board.me.body)
    print(board.me.last_move)
    print(board.on_edge(11,11))
    
    test_food_behaviour(board)
    
    