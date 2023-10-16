# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#

import typing

from minimax import Battlesnake


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


def end(game_state: typing.Dict):
    """end is called when your Battlesnake finishes a game"""
    print("GAME OVER\n")


def move(game_state: typing.Dict) -> typing.Dict:
    """
    move is called on every turn and returns your next move
    Valid moves are "up", "down", "left", or "right"
    See https://docs.battlesnake.com/api/example-move for available data
    """
    game = Battlesnake(game_state)
    # Find the safe moves from current position
    optimal_move = game.minimax_move()
    print(f"MOVE {game_state['turn']}: {optimal_move}")
    return {"move": optimal_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
