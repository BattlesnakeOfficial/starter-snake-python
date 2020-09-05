import util
import random

class Move:
    def __init__(self, x, y=None):
        self.x, self.y = util.get_pos(x, y)

# return all move names
def all_moves():
    return ["up", "down", "left", "right"]

# get all reasonable {"name": value} dictionary pairs for moves:
# {"move name": position}
def get_moves(x, y=None):
    x, y = util.get_pos(x, y)
    moves = dict()
    
    # I do not want negative indexing!:
    if x < 0 or y < 0:
        return moves
    
    moves[up()]  = move_up(x, y)
    if y > 0:
        moves[down()] = move_down(x, y)
    if x > 0:
        moves[left()] = move_left(x, y)
    moves[right()] = move_right(x, y)
    
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