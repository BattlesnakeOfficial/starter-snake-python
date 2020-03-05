import json
import os
import random

import bottle
from bottle import HTTPResponse


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    print("START:", json.dumps(data))

    response = {"color": "#000000", "headType": "dead", "tailType": "small-rattle"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json

    print("MOVE:", json.dumps(data))

    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    move = random.choice(directions)

    converted_data = json.loads(json.dumps(data))
    game_id = converted_data["game"]["id"]
    turn = converted_data["turn"]
    print("Game ID: " + game_id)
    print("Turn: " + str(turn))

    board_width = converted_data["board"]["width"]
    board_height = converted_data["board"]["height"]

    game_board = [['_' for x in range(board_width)] for y in range(board_height)]

    for a in converted_data["board"]["food"]:
        game_board[a["y"]][a["x"]] = "F"



    for a in converted_data["board"]["snakes"]:
        t = 0
        for b in a["body"]:
            game_board[b["y"]][b["x"]] = "s"
            t = t+1
        game_board[a["body"][0]["y"]][a["body"][0]["x"]] = "S"
        game_board[a["body"][t-1]["y"]][a["body"][t-1]["x"]] = "t"

    for x in game_board:
        for y in x:
            print(y, end=' ')
        print()
    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.

    shout = "I am a python snake!"
    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
