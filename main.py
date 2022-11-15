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


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
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
# Welcome to
# __________         __    __  .__                               __
# \______   \_____ /  |_/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  /\_  \\   __\   __\  | _/ __ \ /  __//    \\_  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  __/ \__ \|   |  \/ __ \|    <\  ___/
#  |_______/(____/_|  |_| |__/\___>____>_|_(_____/_|_\\____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com
import random
import typing
# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")
    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
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
def move(game_state: typing.Dict) -> typing.Dict:
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    next_moves = [ [1]* board_width for i in range(board_height)]
    # mark my snake body as invalid next moves
    for body in game_state["you"]["body"]:
        next_moves[body["x"]][body["y"]] = 0
    # mark other snake bodies as invalid next moves
    opponents = game_state['board']['snakes']
    for snake in opponents:
        for body in snake["body"]:
            next_moves[body["x"]][body["y"]] = 0
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    left = my_head["x"] - 1
    right = my_head["x"] + 1
    up = my_head["y"] + 1
    down = my_head["y"] - 1
    # Prevent your Battlesnake from moving out of bounds or colliding into existing snakes (including itself)
    if left < 0 or next_moves[left][my_head["y"]] == 0:
        is_move_safe["left"] = False
    if right > board_width - 1 or next_moves[right][my_head["y"]] == 0:
        is_move_safe["right"] = False
    if up > board_height - 1 or next_moves[my_head["x"]][up] == 0:
        is_move_safe["up"] = False
    if down < 0 or next_moves[my_head["x"]][down] == 0:
        is_move_safe["down"] = False
    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)
    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    # food = game_state['board']['food']
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
