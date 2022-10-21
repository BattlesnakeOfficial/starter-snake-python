import random
import typing

from players.heuristic_player import HeuristicPlayer
from players.random_player import RandomPlayer
from players.self_preserving_player import SelfPreservingPlayer


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    player = HeuristicPlayer()

    run_server({
        "info": player.info,
        "start": start,
        "move": player.move,
        "end": end
    })
