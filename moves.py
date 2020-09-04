import util
import random

class Move:
    def __init__(self, x, y=None):
        self.x, self.y = util.get_pos(x, y)

# return all move names
def all_moves():
    return ["up", "down", "left", "right"]

# get all reasonable {"name": value} dictionary pairs for moves: {"move name": position}
def get_moves(x, y=None):
    x, y = util.get_pos(x, y)
    moves = dict()
    
    up_move = move_up(x, y)
    down_move = move_down(x, y)
    left_move = move_left(x, y)
    right_move = move_right(x, y)
    
    if up_move >= 0:
        moves[up()] = up_move
    if down_move >= 0:
        moves[down()] = down_move
    if left_move >= 0:
        moves[left()] = left_move
    if right_move >= 0:
        moves[right()] = right_move
       
    return moves

def up():
    return "up"
def down():
    return "down"
def left():
    return "left"
def right():
    return "right"

def move_up(x, y):
    x, y = util.get_pos(x, y)
    return x, y+1
def move_down(x, y):
    return x, y-1
def move_left(x, y):
    return x-1, y
def move_right(x, y):
    return x+1, y


def pick_move(possible_moves):
    if type(possible_moves) == type(dict()):
        return random.choice(list(possible_moves.keys()))
    else:
        return random.choice(list(possible_moves))

if __name__ == "__main__":
    print(get_moves({"x": 0, "y": 0}))
    print(get_moves((0,0)))