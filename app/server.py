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

    response = {"color": "#00FF00", "headType": "regular", "tailType": "regular"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


def against_wall(data, pos):
    """ Get a list of the directions of walls that the snake is adjacent to. """
    width = data['board']['width']
    height = data['board']['height']

    adjacent = []
    if pos['x'] == 0:
        adjacent.append("left")
    if pos['x'] == width - 1:
        adjacent.append("right")
    if pos['y'] == 0:
        adjacent.append("up")
    if pos['y'] == height - 1:
        adjacent.append("down")
    return adjacent


def unoccupied_adjacent(data, pos):
    """ Get a list of unoccupied positions adjacent to position pos.
    Does not give information about the walls. """
    adjacent = []
    snakes = data['board']['snakes']

    # print("POS: {}".format(pos))
    # [[x,y],[x,y],...]
    # [{'x' : x, 'y' : y}, {...]
    # s['body'] is a dict with keys x and y
    occupied_positions = list()
    print("SNAKE BODY: {}".format(snakes[0]['body']))
    for s in snakes:
        occupied_positions += s['body']

    print("SNAKES: {}".format(snakes))
    print("OCCUPIED POSITIONS: {}".format(occupied_positions))

    # Check position to the left of pos
    if {'x': pos['x'] - 1, 'y': pos['y']} not in occupied_positions:
        # print("LEFT: {}, checking against: {}".format([pos['x'] - 1, pos['y']], occupied_positions))
        # adjacent_pos.append([pos['x'] - 1, pos['y']])
        adjacent.append("left")

    # Check position to the right of pos
    if {'x': pos['x'] + 1, 'y': pos['y']} not in occupied_positions:
        # adjacent_pos.append([pos['x'] + 1, pos['y']])
        adjacent.append("right")

    # Check position above pos
    if {'x': pos['x'], 'y': pos['y'] - 1} not in occupied_positions:
        # print("LEFT: {}, checking against: {}".format([pos['x'], pos['y'] - 1], occupied_positions))
        # adjacent_pos.append([pos['x'], pos['y'] + 1])
        adjacent.append("up")

    # Check position below pos
    if {'x': pos['x'], 'y': pos['y'] + 1} not in occupied_positions:
        # adjacent_pos.append([pos['x'], pos['y'] - 1])
        adjacent.append("down")

    return adjacent


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json
    print("MOVE:", json.dumps(data))

    # Store board data for easier access
    width = data['board']['width']
    height = data['board']['height']
    snakes = data['board']['snakes']

    # Choose a random direction to move in
    # directions = ["up", "down", "left", "right"]
    you = data['you']
    unoccupied = unoccupied_adjacent(data, you['body'][0])
    adjacent_walls = against_wall(data, you['body'][0])
    print("HEAD POS: {}".format(you['body'][0]))
    print("ADJACENT WALLS: {}".format(adjacent_walls))
    print("UNOCCUPIED POSITIONS: {}".format(unoccupied))
    temp = [i for i in unoccupied if i not in adjacent_walls]
    # for i in unoccupied:
    #     for j in adjacent_walls:
    #         if i is not j:
    #             temp.append(i)

    move = random.choice(temp)  # random.choice([i for i in unoccupied not in adjacent_walls])

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
