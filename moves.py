import util
class Move:
    def __init__(x, y=None):
        self.x, self.y = get_pos(x, y)

def all_moves():
    return ["up", "down", "left", "right"]

def get_moves(x, y=None):
    x, y = util.get_pos(x, y)
    moves = dict()
    
    moves[up()] = move_up(x, y)
    moves[down()] = move_down(x, y)
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

if __name__ == "__main__":
    print(get_moves({"x": 0, "y": 0}))
    print(get_moves((0,0)))