import util
class Move:
    def __init__(x, y=None):
        self.x, self.y = get_pos(x, y)

def all_moves():
    return {"up", "down", "left", "right"}

def get_moves(x, y=None):
    x, y = util.get_pos(x, y)
    moves = dict()
    
    moves["up"] = x, y+1
    moves["down"] = x, y-1
    moves["left"] = x-1, y
    moves["right"] = x+1, y
       
    return moves

if __name__ == "__main__":
    print(get_moves({"x": 0, "y": 0}))
    print(get_moves((0,0)))