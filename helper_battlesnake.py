import numpy as np
import typing


def look_ahead(head, move):
    """Given a possible move, return the snake's new coordinates if it were headed that way"""
    snake_head = head.copy()
    if move == "up":
        snake_head["y"] += 1
    if move == "down":
        snake_head["y"] -= 1
    if move == "left":
        snake_head["x"] -= 1
    if move == "right":
        snake_head["x"] += 1
    return snake_head


def snake_compass(head_loc: typing.Dict, next_loc: typing.Dict):
    """
    Given the snake's head and an adjacent square, return either left/right/up/down
    """
    if head_loc["x"] + 1 == next_loc["x"] and head_loc["y"] == next_loc["y"]:
        return "right"
    if head_loc["x"] - 1 == next_loc["x"] and head_loc["y"] == next_loc["y"]:
        return "left"
    if head_loc["x"] == next_loc["x"] and head_loc["y"] + 1 == next_loc["y"]:
        return "up"
    if head_loc["x"] == next_loc["x"] and head_loc["y"] - 1 == next_loc["y"]:
        return "down"

def manhattan_distance(start: typing.Dict, end: typing.Dict):
    """
    Return the Manhattan distance for two positions
    """
    start = (start["x"], start["y"])
    end = (end["x"], end["y"])
    return sum(abs(value1 - value2) for value1, value2 in zip(start, end))


def refresh_safe_moves(move_dict):
    """
    Return any remaining safe moves
    """
    safe_moves = []
    for move, isSafe in move_dict.items():
        if isSafe:
            safe_moves.append(move)
    return safe_moves


def obvious_moves(game_state: typing.Dict, my_head: typing.Dict, my_neck=None, risk_averse=True):
    """
    Update the move dictionary and mark unsafe directions as False
    """
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    my_length = game_state["you"]["length"]
    if my_neck is None:
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
    # print(f"Head location: {str(my_head)}")

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False
        # print("Neck is left of head, don't move left")
    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False
        # print("Neck is right of head, don't move right")
    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False
        # print("Neck is below head, don't move down")
    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False
        # print("Neck is above head, don't move up")

    # Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head["x"] == 0:
        is_move_safe["left"] = False
        # print("Out of bounds, can't move left")
    if my_head["x"] + 1 == board_height:
        is_move_safe["right"] = False
        # print("Out of bounds, can't move right")
    if my_head["y"] == 0:
        is_move_safe["down"] = False
        # print("Out of bounds, can't move down")
    if my_head["y"] + 1 == board_width:
        is_move_safe["up"] = False
        # print("Out of bounds, can't move up")

    # Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    for direction in refresh_safe_moves(is_move_safe):
        possible_move = look_ahead(my_head, direction)
        if possible_move in my_body:
            is_move_safe[direction] = False
            # print(f"Body in the way, can't move {direction}")
            # print(f"Headed towards: {str(possible_move)}")
            # print(f"Body: {str(my_body)}")

    # Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']
    for opponent in opponents:
        if opponent["id"] == game_state['you']["id"]:  # Ignore yourself
            continue

        opponent_locs = opponent["body"]
        opponent_head = opponent_locs[0]
        for direction in ["up", "down", "left", "right"]:
            possible_move = look_ahead(my_head, direction)
            # Avoid any possible encounters with any future opponent move
            if risk_averse and my_length < opponent["length"]:
                opponent_moves = [look_ahead(opponent_head, direction) for direction in ["up", "down", "left", "right"]]
                if possible_move in opponent_moves:
                    is_move_safe[direction] = False
            # Avoid running into the opponent snake
            if possible_move in opponent_locs:
                is_move_safe[direction] = False
                # print(f"Opponent snake in the way, can't move {direction}")
                # print(f"Headed towards: {str(possible_move)}")
                # print(f"Opponent: {str(opponent_locs)}")

    return refresh_safe_moves(is_move_safe)


class Node:
    def __init__(self, location, parent=None, f=0, g=0, h=0):
        self.location = location
        self.neighbour_nodes = []
        self.parent = parent
        self.f = f  # The cost from the start node to the goal node
        self.g = g  # The cost from the start node to the current node
        self.h = h  # The cost from the current node to the goal node using a heuristic

    def __repr__(self):
        return str(self.location)


def a_star_search(game_state, my_head, food_loc):
    """
    Implement the A* search algorithm to find the shortest path to food
    """
    head_loc = my_head.copy()
    open_list = [Node(head_loc)]  # Contains the nodes that have been generated but have not been yet examined till yet
    closed_list = []  # Contains the nodes which are examined
    timer = 0

    while len(open_list) > 0:
        if timer > 300:
            return None, None

        current_node = min(open_list, key = lambda node: node.f)  # The node with the smallest f value
        open_list.remove(current_node)  # Remove from open list

        if current_node.location == food_loc:  # Found the food! Stop search
            traceback = [food_loc]
            pointer = current_node
            while pointer.parent is not None:
                traceback.append(pointer.parent.location)
                pointer = pointer.parent
            return traceback, current_node.g

        # Identify all possible nodes to move to
        neighbour_nodes = []
        possible_moves = obvious_moves(
            game_state,
            my_head=current_node.location,
            my_neck=current_node.parent.location if current_node.parent is not None else None,
            risk_averse=True
        )

        for possible_move in possible_moves:
            possible_node = Node(look_ahead(current_node.location, possible_move), parent=current_node)
            neighbour_nodes.append(possible_node)

        for possible_node in neighbour_nodes:  # For each possible new node
            if possible_node.location in closed_list:  # Skip if the node is in the closed list
                continue

            # Compute f value for the neighbour node
            possible_node.g = current_node.g + 1
            possible_node.h = manhattan_distance(current_node.location, food_loc)
            possible_node.f = possible_node.g + possible_node.h

            # If the node's location is also in the open list but has a worse g value, ignore since we can do better
            for open_node in open_list:
                if possible_node.location == open_node.location and possible_node.g > open_node.g:
                    break

            # Otherwise, this is the best we can do so far - add to open list
            open_list.append(possible_node)

        closed_list.append(current_node.location)  # Add to closed list since we've looked at all neighbours
        timer += 1

    return None, None

def flood_fill(game_state, next_square, risk_averse=True):
    """
    Recursive function to get the total area of the current fill selection
    """
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    my_length = game_state["you"]["length"]

    # Make an (l x w) array and simulate the board
    board = np.zeros((board_width, board_height))
    for snake in game_state["board"]["snakes"]:
        body_pixels = snake["body"]
        for pixel in body_pixels:
            board[pixel["x"], pixel["y"]] = 1

        if snake["id"] == game_state['you']["id"]:  # Ignore yourself
            continue
        elif risk_averse and my_length < snake["length"]:
            opponent_head = body_pixels[0]
            opponent_moves = [look_ahead(opponent_head, direction) for direction in ["up", "down", "left", "right"]]
            for m in opponent_moves:
                if 0 <= m["x"] < board_width and 0 <= m["y"] < board_height:
                    board[m["x"], m["y"]] = 1

    def fill(x, y):
        if board[x][y] == 1:  # Snakes or hazards
            return
        if board[x][y] == 2:  # Fill
            return
        board[x][y] = 2
        neighbours = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
        for n in neighbours:
            if 0 <= n[0] < board_width and 0 <= n[1] < board_height:
                fill(n[0], n[1])

    fill(next_square["x"], next_square["y"])
    return sum((row == 2).sum() for row in board)


def fill_search(game_state, my_head, safe_moves, log):
    best_fill = -1
    next_move = safe_moves[0]
    for safe_move in safe_moves:
        end_square = look_ahead(my_head, safe_move)
        max_fill = flood_fill(game_state, next_square=end_square)
        if max_fill > best_fill:
            next_move = safe_move
            best_fill = max_fill
        if log:
            print(f"Flood fill on {safe_move} and got {max_fill}")
    return next_move

def order_food(game_state, head_loc):
    """
    Return a sorted list of food options by distance to the snake. Also decide a cut-off based on health
    """
    menu = game_state["board"]["food"]
    health = game_state["you"]["health"]
    # For each food item, grab the Manhattan distance to the snake
    food_costs = []
    for food in menu:
        cost_to_item = manhattan_distance(head_loc, food)
        food_costs.append(cost_to_item)

    def helper_food_filter(menu, food_costs, cutoff):
        menu_indices = np.where(np.array(food_costs) <= cutoff)
        filt_menu = menu[menu_indices]
        return

    # Sort the food by the distances and apply discretionary filters based on how hungry you are
    sorted_menu = sorted(menu, key=lambda x: food_costs[menu.index(x)])
    sorted_food_costs = sorted(food_costs)
    if len(menu) == 0:
        new_menu = []
    elif health >= 45:  # Big chilling
        new_menu = [x for x in sorted_menu if sorted_food_costs[sorted_menu.index(x)] <= 5]
    elif health <= min(food_costs) * 3:  # Pretty desperate
        new_menu = [x for x in sorted_menu if sorted_food_costs[sorted_menu.index(x)] <= 15]
    else:
        new_menu = [x for x in sorted_menu if sorted_food_costs[sorted_menu.index(x)] <= 10]

    return new_menu
