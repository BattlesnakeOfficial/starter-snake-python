# Reference: https://github.com/graeme-hill/snakebot/
# Example input:
#
# [
#     "_ _ _ _ _ _ _ _",
#     "_ _ _ d _ _ _ _",
#     "_ _ _ > v _ _ _",
#     "_ _ _ _ 0 _ _ _",
#     "_ * _ _ _ _ _ _",
#     "_ _ _ _ _ _ _ _",
#     "_ _ _ v < < l _",
#     "_ _ _ 1 _ _ _ _"
# ]
#
# Each part of the snake is represented by '<', 'v', '>', or '^' pointing
# in the direction of the next part belonging to the same snake. The head
# is a number between 0 and 9 that uniquely identifies that snake. The tail
# is 'u', 'd', 'l', 'r' that points to the next part of the snake. This
# weirdness is necessary to make it possible to identify each part's owner
# with only a single character.
#
# Whitespace is ignored so the spaces are not required.
#
# Supports up to ten snakes (same as game limit) so that they will fit in
# one char each. Snake 0 is "my" snake (which is actually called "you" in the
# world json object that the game sends).
#

import sys
import math
from timeit import default_timer as timer
import visualizer
sys.path.append("E:/BattleSnake/MYSNAKE/Battlesnake-2020/app/")
import localizer
import logic

def make_board(s):
    BOARD = {}
    BOARD["height"] = len(s)
    BOARD["width"] = len(s[0].split())
    BOARD["obstacles"] = set()
    BOARD["food"] = []
    BOARD["heads"] = []  # [(x,y)] snake heads
    BOARD["weights"] = {}  # {(x,y): w}
    BOARD["our_snake"] = {"health": 10, "body": []}
    BOARD["snakes"] = []

    visited = [[False for i in range(len(s))]
            for j in range(len(s[0].split()))]

    # split s into 2d array
    grid = []
    for i in range(len(s)):
        row = s[i].split()
        grid.append(row)

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if is_food(grid[i][j]):
                BOARD["food"].append((j, i))

            if is_tail(grid[i][j]) and not visited[i][j]:
                snake_body, you = find_snake(grid, visited, i, j, BOARD["width"], BOARD["height"])

                # add to BOARD
                # head
                BOARD["heads"].append((snake_body[0]['x'], snake_body[0]['y']))

                # body
                for index in range(len(snake_body)):
                    (a,b) = (snake_body[index]['x'], snake_body[index]['y'])
                    BOARD['obstacles'].add((a,b))
                    
                BOARD['snakes'].append({"health": 100, "body": snake_body})

                if you:
                    BOARD['our_snake']['body'] = snake_body

    # init board weight
    # board boders
    for row in range(BOARD["height"]):
        BOARD['weights'][(0, row)] = localizer.BORDERS
        BOARD['weights'][(BOARD['width']-1, row)] = localizer.BORDERS
    for col in range(BOARD['width']):
        BOARD['weights'][(col, 0)] = localizer.BORDERS
        BOARD['weights'][(col, BOARD['height']-1)] = localizer.BORDERS

    # heads
    for snake in BOARD["snakes"]:
        head = (snake['body'][0]['x'], snake['body'][0]['y'])
        if len(snake['body']) >= len(BOARD["our_snake"]['body']):
            BOARD['weights'][head] = localizer.LONGER_SNAKE_HEAD
        else:
            BOARD['weights'][head] = localizer.SHORTER_SNAKE_HEAD

    # remove tail
    # our_tail = (BOARD['our_snake']['body'][-1]['x'], BOARD['our_snake']['body'][-1]['y'])
    # BOARD["obstacles"].remove(our_tail)

    # bodies
    for snake_bodies in BOARD["obstacles"]:
        BOARD['weights'][snake_bodies] = localizer.SNAKE_BODIES

    return BOARD

# find snake parts
def find_snake(grid, visited, i, j, width, height):
    # append tail
    snake_body = []
    x, y = j, i
    snake_body.append({"x": x, "y": y})
    visited[y][x] = True
    if grid[y][x] == 'r':
        x, y = x + 1, y
    elif grid[y][x] == 'd':
        x, y = x, y + 1
    elif grid[y][x] == 'l':
        x, y = x - 1, y
    elif grid[y][x] == 'u':
        x, y = x, y - 1

    # append other snake parts
    you = False
    while 0 <= x < width and 0 <= y < height and is_snake(grid[y][x]) and not is_head(grid[y][x]) and not visited[y][x]:
        snake_body.append({"x": x, "y": y})
        visited[y][x] = True
        if grid[y][x] == '>':
            x, y = x + 1, y
        elif grid[y][x] == 'v':
            x, y = x, y + 1
        elif grid[y][x] == '<':
            x, y = x - 1, y
        elif grid[y][x] == '^':
            x, y = x, y - 1
    if is_head(grid[y][x]):
        snake_body.append({"x": x, "y": y})
        visited[y][x] = True
    snake_body.reverse()

    # our snake
    if grid[y][x] == '0':
        you = True

    return snake_body, you

def is_tail(char):
    return char == 'u' or char == 'd' or char == 'l' or char == 'r'
        
def is_head(char):
    return char in [str(x) for x in range(10)]


def is_snake(char):
    return char == '>' or char == 'v' or char == '<' or char == '^'


def is_food(char):
    return char == '*'

# ======================== MY TEST BOARD =======================
class Board:
    '''Simple class to represent the board'''

    def __init__(self, board):
        self.width = board['width']
        self.height = board['height']
        self.obstacles = board['obstacles']  # snake heads and bodies
        self.food = board['food']
        self.heads = board['heads']  # [(x,y)] snake heads
        self.weights = board['weights']  # {(x,y): w}
        self.our_snake = board['our_snake']
        self.snakes = board['snakes']

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        return id not in self.obstacles

    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return list(results)

    def cost(self, from_node, to_node):
        return self.weights.get(to_node, 1)

# ================================ LOGIC ==========================================
def make_a_move(board):
    # board = Board(data)
    health = board.our_snake['health']
    snake_body = board.our_snake['body']
    head = (snake_body[0]['x'], snake_body[0]['y'])
    tail = (snake_body[-1]['x'], snake_body[-1]['y'])

    # the longer the less food threshold
    FOOD_SEARCH_THRESHOLD = max(50, 95 - len(snake_body))

    # # FIXME: test function, will develop later
    # if len(snake_body) < 3 or health < FOOD_SEARCH_THRESHOLD or not is_longest(board.snakes, len(snake_body)):
    #     return get_food(board)
    # return chase_tail(board, head, tail)
    return logic.get_food(board)

    # TODO: below
    # if there are more than 2 snakes, we need to make ourself long enough
    # if len(snakes) > 2:
    #     if is_second_longest(snakes, len(snake_body)):
    #         return kill_others(head, tail, len(snake_body), board, snakes)
    #     return get_food(board, head, tail, board.food, board.heads)
    # else:
    #     if not is_longest(snakes, len(snake_body)):
    #         return get_food(board, head, tail, board.food, board.heads)
    #     return kill_others(head, tail, len(snake_body), board, snakes)

# =============================== TEST =======================================
def test_result(s):
    b = make_board(s)
    board = Board(b)
    visualizer.visualize_board(board.weights, board.width, board.height)
    direction = make_a_move(board)
    print(direction)

def test_chase_tail():
    s = [
    "_ _ _ _ _ _ _ _",
    "_ _ _ _ _ _ _ _",
    "_ _ _ _ v l _ _",
    "_ _ _ _ 0 _ _ _",
    "_ * _ _ _ _ _ *",
    "_ _ _ _ _ _ _ _",
    "_ _ _ v < < l _",
    "_ _ _ 1 _ _ _ _"
    ]
    test_result(s)

def test_why_hit_wall():
    s =[
        "_ _ _ 0 _",
        "_ * _ ^ _",
        "* _ _ ^ _",
        "_ _ _ u _",
        "_ * _ _ _"
    ]
    test_result(s)

def test_choose_food():
    s =[
        "* _ _ _ _ 1",
        "_ > > > > ^",
        "_ ^ < l _ _",
        "_ 0 _ _ _ _",
        "_ ^ < l _ _",
        "_ _ _ _ _ _",
        "_ _ _ _ * _",
    ]
    test_result(s)

def eat_tail():
    s =[
        "_ _ _ _ * _",
        "_ _ 0 _ _ _",
        "_ r ^ _ _ _",
        "_ _ _ _ _ _",
        "_ _ _ _ _ _",
        "_ _ _ * * *",
        "_ * _ _ _ _",
    ]
    test_result(s)

test_why_hit_wall()


# http://www.graemehill.ca/battle-snake/
# https://github.com/nicktsan/battlesnake-python
# https://github.com/rdbrck/battlesnake-python/tree/master/app
# https://github.com/Wyllan/battlesnake-python/tree/master/app
# https://github.com/colosnake2019/Fine-snake
# https://github.com/battlesnakeio/engine
# https://github.com/graeme-hill/snakebot/blob/21059e4b5e3153ada5e74ba2e1331c10b5142b2f/util/helpers.js#L26
