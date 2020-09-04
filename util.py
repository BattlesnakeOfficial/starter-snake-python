"""
Useful Utility Functions for Battlesnake
"""
import math
import constants
"""
convert a pair of board coordinates into the tuple (x, y)
(used to make sure you are always using the same board cooardinate format)
"""
def get_pos(x, y=None):
    if type(x) == type(tuple()):
      x, y = x
    elif type(x) == type(dict()):
        x, y = x['x'], x['y']
    return x, y

"""
get the Manhattan distance between points A and B,
Special thanks to one of the Victoria 2019 bounty snakes for this adjustment from Pythagorean distance
"""
def distance(A, B):
    xA, yA = get_pos(A)
    xB, yB = get_pos(B)
    # get the Pythagorean distance between points A and B
    #dist = math.sqrt(((xB-xA) ** 2) + ((yB-yA) ** 2))

    # get the Manhattan distance between points A and B:
    dist = abs(xB-xA) + abs(yB-yA)
    return dist

"""
get the direction(s) you have to go to get from point A to point B
"""
def directions(A, B):
    x1, y1 = get_pos(A)
    x2, y2 = get_pos(B)
    
    moves = []
    
    if x1 > x2:
        moves.append("left")
    elif x1 < x2:
        moves.append("right")
    
    if y1 > y2:
        moves.append("down")
    elif y1 < y2:
        moves.append("up")
    
    return moves


if __name__ == "__main__":
    print(directions((1, 11), (1, 11)))
    