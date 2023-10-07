# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#

import numpy as np
import random
import time
import typing

from helper_battlesnake import a_star_search
from helper_battlesnake import fill_search
from helper_battlesnake import flood_fill
from helper_battlesnake import look_ahead
from helper_battlesnake import obvious_moves
from helper_battlesnake import order_food
from helper_battlesnake import snake_compass


global board_log

def info() -> typing.Dict:
    """
    info is called when you create your Battlesnake on play.battlesnake.com
    and controls your Battlesnake's appearance
    TIP: If you open your Battlesnake URL in a browser you should see this data
    """
    print("INFO")

    return {
        "apiversion": "1",
        "author": "G",
        "color": "#3333ff",
        "head": "ski",
        "tail": "mystic-moon",
    }


def start(game_state: typing.Dict):
    """start is called when your Battlesnake begins a game"""
    print("GAME START")
    global board_log
    board_log = open("board_log.txt", "w")


def end(game_state: typing.Dict):
    """end is called when your Battlesnake finishes a game"""
    print("GAME OVER\n")


def move(game_state: typing.Dict, log=True, timer_log=True) -> typing.Dict:
    """
    move is called on every turn and returns your next move
    Valid moves are "up", "down", "left", or "right"
    See https://docs.battlesnake.com/api/example-move for available data
    """
    clock_in = time.time_ns()
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_length = game_state["you"]["length"]  # Length of your snake

    # Find the safe moves from current position
    safe_moves = obvious_moves(game_state, my_head)
    if timer_log:
        print(f"Found safe moves in {(time.time_ns() - clock_in) // 1000000} ms")
    if log:
        print(f"Safe moves: {safe_moves}")

    if len(safe_moves) == 0:
        risky_moves = obvious_moves(game_state, my_head, risk_averse=False)
        if len(risky_moves) == 1:
            return {"move": risky_moves[0]}
        elif len(risky_moves) == 0:
            print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
            return {"move": "down"}
        else:
            safe_moves = risky_moves

    # Move towards food instead of random, to regain health and survive longer
    food_dist = []
    food_moves = []
    food_fill = []
    food_heur = []
    # Big idea: loop through the most convenient food and find the shortest path using A* search
    sorted_food_list = order_food(game_state, my_head)
    if log:
        print(f"Narrowed down {len(sorted_food_list)} food options: {sorted_food_list}")
    for food_loc in sorted_food_list:
        clock_in = time.time_ns()
        best_path, best_dist = a_star_search(game_state, my_head, food_loc)
        if timer_log:
            if best_path is None:
                print(f"Failed A* search in {(time.time_ns() - clock_in) // 1000000} ms")
            else:
                print(f"Ran A* search successfully in {(time.time_ns() - clock_in) // 1000000} ms")

        # Grab the output if A* search ran to completion AND run flood fill just in case
        if best_path is not None:
            clock_in = time.time_ns()
            # Grab the shortest distance to the food
            food_dist.append(best_dist)
            way_to_food = snake_compass(my_head, best_path[-2])
            # Grab the direction to the food
            food_moves.append(way_to_food)
            f = flood_fill(game_state, look_ahead(my_head, way_to_food))
            food_fill.append(f)
            # Grab the heuristic computed for the food
            heuristic = best_dist * 11 * 11 / f ** 2.25
            food_heur.append(heuristic)

            if timer_log:
                print(f"Ran flood fill and computed heuristic in {(time.time_ns() - clock_in) // 1000000} ms")
            if log:
                print(f"Distance: {best_dist}, Fill: {f}, Heuristic: {round(heuristic, 5)}")

    # Kinda annoying, but A* sometimes fails because of time complexity. Condition on whether A* ran or not...
    food_risk_too_high = False
    if len(food_dist) > 0 and my_length <= 25:  # If there's food and we're not chilling
        next_fill = min(food_fill)
        # Probably going to get trapped if we go here
        if next_fill < 25:
            food_risk_too_high = True
            if log:
                print(f"If we eat, the fill is {next_fill} so skip")

        if not food_risk_too_high:
            next_move = food_moves[np.argmin(food_heur)]
            # This bug shouldn't happen
            if next_move not in safe_moves:
                raise ValueError
            if log:
                best_food_loc = sorted_food_list[np.argmin(food_heur)]
                print(f"Best A* search is {best_food_loc}")
                print(f"Going {next_move} which is {min(food_dist)} away from {my_head}")
            print(f"MOVE {game_state['turn']}: {next_move}")
            print("=" * 10)
            return {"move": next_move}

    best_fill = -1
    next_move = safe_moves[0]
    for safe_move in safe_moves:
        end_square = look_ahead(my_head, safe_move)
        max_fill = flood_fill(game_state, next_square=end_square)
        if max_fill > best_fill:
            next_move = safe_move
            best_fill = max_fill


    # Optimise based on flood fill
    next_move = fill_search(game_state, my_head, safe_moves, log)

    if best_fill < 5:
        risky_moves = obvious_moves(game_state, my_head, risk_averse=False)
        print(f"Risk-averse may cause death with fill = {best_fill}")
        next_move = fill_search(game_state, my_head, risky_moves, log)
        print(f"Changing to risky with fill = {best_fill}")
    if log:
        print(f"No A    * but best flood fill: {next_move}")

    print(f"MOVE {game_state['turn']}: {next_move}")
    print("=" * 10)
    # board_log.write(f"MOVE {game_state['turn']}\n")
    # board_log.write(str(game_state))
    # board_log.write("\n" + "=" * 100)
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
