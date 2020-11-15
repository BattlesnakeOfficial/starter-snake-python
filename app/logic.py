import sys, os
import math
import localizer
import a_star
import breadth_first_search as bfs
import predict_future
import Classes

# DEBUG
sys.path.append(os.path.join(os.path.dirname(__file__), 'test'))
import visualizer
# ================================ FOOD ===========================================
# return the move to food
def get_food(board):
    head = (board.our_snake['body'][0]['x'], board.our_snake['body'][0]['y'])
    target_food_path = find_food_path(board)
    return move_direction(head, target_food_path[1])
    # return target_food_path

# return the path to food
def find_food_path(board):
    head = (board.our_snake['body'][0]['x'], board.our_snake['body'][0]['y'])
    us_to_food = []
    for f in board.food:
        us_to_food.append((distance(f, head), f))
    us_to_food.sort(key=lambda x: x[0]) # sort food by distance from our head to food increasingly
    best_food_path = find_best_food_path(board, us_to_food)
    return best_food_path

# check future of us getting each food, and find longest safe path in radius = our length
# longest safe path is a path containing empty cells
# ideally, longest safe path should equal our length + 1
# return the path to the best food
def find_best_food_path(board, us_to_food):
    count = 0
    our_head = (board.our_snake['body'][0]['x'], board.our_snake['body'][0]['y'])
    possible_food = []
    for food_obj in us_to_food:

        # find distance of closest snake to food
        dist_to_food = sys.maxsize
        for i, head in enumerate(board.heads):
            if head != our_head:
                dist_to_food = min(distance(food_obj[1], head), dist_to_food)

        # if dist(other snakes' heads, food) > dist(our head, food), add to possible_food
        if dist_to_food > food_obj[0]:
            possible_food.append(food_obj[1]) # TODO: if a_star is too slow, use distance food_obj[0] as step to food instead

    # check future of each possible food
    future_path = check_future(board, our_head, possible_food)

    # TODO: fix down here
    # consider future
    if future_path != None:
        print("find_best_food_path: FUTURE PATH")  # DEBUG
        return future_path

    # TODO: no path, chase tail
    print("find_best_food_path: CHASE TAIL")  # DEBUG
    return chase_tail(board, our_head, (board.our_snake['body'][-1]['x'], board.our_snake['body'][-1]['y']))

# predict future of getting each food
# in future heatmap, if there exists safe path (do BFS) which longer than our length, go for that food
def check_future(board, start, goals):
    steps_to_goals = []
    goal_paths = {} # {food: path}
    # good_food = {} # food we need to see future
    for food in goals:
        path = a_star.a_star_search(board, start, food)
        goal_paths[food] = path
        steps_to_goals.append(len(path)-1)
    food_weight = predict_future.predict_heatmap(board, start, goals, steps_to_goals)

    backup_weight = board.weights
    backup_obstacles = board.obstacles

    # update obstacles
    for k, v in food_weight.items():
        future_obstacles = set()
        for coord, value in v.items():
            if value != localizer.BORDERS and value != 0:
                future_obstacles.add(coord)
        board.obstacles = future_obstacles
        board.weights = v

        # for each food_weight heatmap, do a_star again on each food and see if the number of steps to get there still equals the previous calculation
        future_path = a_star.a_star_search(board, start, k)
        if len(future_path) == len(goal_paths[k]):
            # good_food[food] = future_path

            # update our snake location in the future
            update_snake_location(future_path, board)
            visualizer.visualize_board(board.weights, board.width, board.height) # DEBUG
            # check if exists safe path
            is_save = predict_future.check_safe_location(board, k, board.weights) # FIXME:

            # TODO: 
            if is_save:
                # reset board
                board.weights = backup_weight
                board.obstacles = backup_obstacles
                return future_path # FIXME:


    # for each of heatmap, check the longest empty cell path within x radius
    # if len(path) == 1:
    #     return sys.maxsize, None
    # is_save = predict_future.check_safe_location(board, food, board.weight)
    return None

def update_snake_location(future_path, board):
    weight = board.weights

    # add head
    for i in range(1, len(future_path)):
        weight[future_path[i]] = localizer.SNAKE_BODIES

    # remove tail
    count = len(future_path)
    us = board.our_snake['body']
    for i in range(len(us)-1, -1, -1):
        if count == 0:
            break
        tail = (us[i]['x'], us[i]['y'])
        weight[tail] = 0
        count -= 1
    for x in range(1, count):
        weight[future_path[x]] = 0

    board.weights = weight

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# ================================ MOVE ==========================================
def move_direction(start, goal):
    if(start[0] == goal[0] - 1):
        return 'right'
    if(start[0] == goal[0] + 1):
        return 'left'
    if(start[1] == goal[1] + 1):
        return 'up'
    if(start[1] == goal[1] - 1):
        return 'down'
    return 'up'


def chase_tail(board, head, tail):
    neigbors = board.neighbors(tail)
    if len(neigbors) == 0:
        move = bfs.bfs_safe_move(head, board)
        print("chase_tail: NO NEIGHBOUR = DIE")  # DEBUG
        return move_direction(head, move)
    path_to_tail = a_star.a_star_search(board, head, neigbors[0])
    if len(path_to_tail) == 1:  # no path
        print("chase_tail: BFS")  # DEBUG
        move = bfs.bfs_safe_move(head, board)
        path_to_tail.append(move)
    print("chase_tail: A STAR")  # DEBUG
    return path_to_tail
    # return move_direction(head, path_to_tail[1])

# ================================ LOGIC ==========================================


def make_a_move(data):
    board = Classes.Board(data)
    health = data['you']['health']
    snake_body = data['you']['body']
    head = (snake_body[0]['x'], snake_body[0]['y'])
    tail = (snake_body[-1]['x'], snake_body[-1]['y'])

    # the longer the less food threshold
    FOOD_SEARCH_THRESHOLD = max(50, 95 - len(snake_body))

    # FIXME: test function, will develop later
    if len(snake_body) < 4 or health < FOOD_SEARCH_THRESHOLD or not is_longest(data['board']['snakes'], len(snake_body)):
        return get_food(board)
    return chase_tail(board, head, tail)

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


def is_longest(snakes, our_snake_length):
    count = 0
    for other in snakes:
        if len(other['body']) > our_snake_length:
            count += 1
    return True if count == 0 else False