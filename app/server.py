import json
import os
import random

import bottle
from bottle import HTTPResponse


@bottle.route("/")
def index():
    return "Your Battlesnake is alive! Hello Abe and Ayushi"


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


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json
    print("MOVE:", json.dumps(data))
    resp_dict = json.loads(json.dumps(data))
    maxHeight = resp_dict['board']['height']
    snakeHeadX = resp_dict['you']['body'][0]['x']
    snakeHeadY = resp_dict['you']['body'][0]['y']
    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    shout = "I am a spaghetti!"
    #move = random.choice(directions)
    #conditionally move in a certain direction
    occupiedSpaces = {}
    for i in range(len(resp_dict['you']['body'])):
        currentOccupiedX = resp_dict['you']['body'][i]['x']
        occupiedSpaces[currentOccupiedX] = resp_dict['you']['body'][i]['y']
    print("Occupied Spaces: ", occupiedSpaces)



    if isWallUp(snakeHeadY) and not isOccupiedUp(snakeHeadX, snakeHeadY, occupiedSpaces) :
        print("isWallUp is: ", isWallUp(snakeHeadY))
        response = {"move": "up", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
)
    elif isWallRight(snakeHeadX, maxHeight):
        print("isWallRight is: ", isWallRight(snakeHeadX, maxHeight))
        response = {"move": "right", "shout": shout}
        return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
        )
    
    elif isWallDown(snakeHeadY, maxHeight):
        print("isWallDown is: ", isWallDown(snakeHeadY, maxHeight))
        move = "down"
        response = {"move": "down", "shout": shout}
        return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
        )

    else:   
        move = random.choice(directions)
    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
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

#Helper functions 

def isWallUp(currentY):
    print("isWallUp-","currentY: ", currentY)
    return currentY-1 >= 0

def isWallDown(currentY, maxHeight):
    print("isWallDown-","currentY: ", currentY,  "maxHeight: ", maxHeight)
    return currentY+1 < maxHeight-1

def isWallRight(currentX, maxWidth):
    print("isWallRight-","currentX: ", currentX, "maxWidth: ", maxWidth)
    return currentX+1 < maxWidth-1

def isWallLeft(currentX):
    print("isWallLeft-","currentX: ", currentX)
    return currentX-1 >= 0

def isOccupiedUp(currentX, currentY, snakes):
    return currentX, currentY in snakes.items()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
