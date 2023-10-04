# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
import numpy as np


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "G",  # TODO: Your Battlesnake Username
        "color": "#3333ff",  # TODO: Choose color
        "head": "ski",  # TODO: Choose head
        "tail": "mystic-moon",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict, log=False) -> typing.Dict:

    from helper_battlesnake import look_ahead
    from helper_battlesnake import a_star_search
    from helper_battlesnake import obvious_moves
    from helper_battlesnake import snake_compass
    from helper_battlesnake import flood_fill

    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_length = game_state["you"]["length"]
    safe_moves = obvious_moves(game_state, my_head)
    if log:
        print("=" * 25)
        print(f"Safe moves: {safe_moves}")

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Step 4 - Move towards food instead of random, to regain health and survive longer
    food = game_state['board']['food']
    food_dist = []
    food_moves = []
    food_fill = []
    # Big idea: loop through all food and find the shortest path using A* search
    for food_loc in food:
        best_path, best_dist = a_star_search(game_state, my_head.copy(), food_loc)
        if best_path is not None:
            food_dist.append(best_dist)
            way_to_food = snake_compass(my_head, best_path[-2])
            food_moves.append(way_to_food)
            f = flood_fill(game_state, look_ahead(my_head, way_to_food))
            food_fill.append(best_dist * 11 * 11 / f ** 2.25)

    # Kinda annoying, but A* sometimes fails because of time complexity. Condition on whether A* ran or not...
    if len(food_dist) > 0 and my_length <= 45:
        best_dist_to_food = min(food_fill)
        best_way_to_food = food_moves[np.argmin(food_fill)]
        next_move = best_way_to_food if best_way_to_food in safe_moves else safe_moves[0]
        if log:
            print("Ran A*")
            print(f"Going {next_move} which is {best_dist_to_food} away from {my_head}")
    else:
        best_fill = -1
        next_move = safe_moves[0]
        for safe_move in safe_moves:
            end_square = look_ahead(my_head, safe_move)
            max_fill = flood_fill(game_state, next_square=end_square)
            if max_fill > best_fill:
                next_move = safe_move
                best_fill = max_fill
        print(f"A* failed doing flood fill: {safe_moves}")

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
