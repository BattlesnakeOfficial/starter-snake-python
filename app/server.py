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
    snakeHeadXY = snakeHeadX, snakeHeadY
    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    shout = "I am spaghetti!"
    #move = random.choice(directions)
    #conditionally move in a certain direction
    print("My Spaces: ", getMySpaces(resp_dict))
    print("All Snake Spaces: ", getAllSnakeSpaces(resp_dict))
    print("All Food Spaces: ", getFoodSpaces(resp_dict))
    print("Snakehead Coordinates: ", snakeHeadXY)
    print("is upSpace Free: ",isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)))
    print("is leftSpace Free: ", isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)))
    print("is rightSpace Free: ", isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)))
    print("is downSpace Free: ", isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)))

    #Needs some sort of shuffling behavior or the snake just goes in circles until starvation
    if isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
        response = {"move": "up", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
        response = {"move": "left", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
        response = {"move": "down", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
        response = {"move": "right", "shout": shout}
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

def isUpFree(currentX, currentY, totalSnakeSpaces):
    upSpace = currentY - 1
    upCoordinate = currentX, upSpace
    if upSpace == -1: #Top of board Wall
        print("upspace is a wall")
        return False
    elif upCoordinate in totalSnakeSpaces.values():  #Represents the up Space containing a snake
        print("upSpace is a snake")
        return False
    return True

def isDownFree(currentX, currentY, maxHeight, totalSnakeSpaces):
    downSpace = currentY + 1
    downCoordinate = currentX, downSpace
    if downSpace == maxHeight: #Bottom of board Wall
        print("downspace is a wall")
        return False
    elif downCoordinate in totalSnakeSpaces.values():  # Represents the up Space containing a snake
        print("downspace is a snake")
        return False
    return True

def isLeftFree(currentX, currentY, totalSnakeSpaces):
    leftSpace = currentX - 1
    leftCoordinate = leftSpace, currentY
    if leftSpace == -1: #Left of board Wall
        print("leftspace is a wall")
        return False
    elif leftCoordinate in totalSnakeSpaces.values():  # BROKEN -  Represents the up Space containing a snake
        print("leftspace is a snake")
        return False
    return True

def isRightFree(currentX, currentY, maxWidth, totalSnakeSpaces):
    rightSpace = currentX + 1
    rightCoordinate = rightSpace, currentY
    if rightSpace == maxWidth: #Right of board Wall
        print("rightspace is a wall")
        return False
    elif rightCoordinate in totalSnakeSpaces.values():  # BROKEN - Represents the up Space containing a snake
        print("rightSpace is a snake")
        return False
    return True

def getMySpaces(boardData):
    occupiedSpaces = {}
    for mySpace in range(len(boardData['you']['body'])): 
        currentXvalue = boardData['you']['body'][mySpace]['x']
        occupiedSpaces[mySpace] = boardData['you']['body'][mySpace]['x'], boardData['you']['body'][mySpace]['y']
    return occupiedSpaces

def getAllSnakeSpaces(boardData):
    allSnakeSpaces = {}
    totalSnakeSpaces = 0
    for snake in range(len(boardData['board']['snakes'])):
        for snakeSpace in range(len(boardData['board']['snakes'][snake]['body'])):
            currentTotalSnakeSpacespace = {}
            currentXvalue = boardData['board']['snakes'][snake]['body'][snakeSpace]['x']
            currentYvalue = boardData['board']['snakes'][snake]['body'][snakeSpace]['y']
            snakeSpace = snakeSpace + 1
            allSnakeSpaces[totalSnakeSpaces] = currentXvalue, currentYvalue
            totalSnakeSpaces = totalSnakeSpaces + 1
        snake = snake + 1
    return allSnakeSpaces

def getFoodSpaces(boardData):
    allFoodSpaces = {}
    for food in range(len(boardData['board']['food'])):
        currentX = boardData['board']['food'][food]['x']
        currentY = boardData['board']['food'][food]['y']
        allFoodSpaces[food] = currentX, currentY
    return allFoodSpaces

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
