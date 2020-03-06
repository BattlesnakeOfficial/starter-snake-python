import json
import os
import random
import math
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

    response = {"color": "#ee0606", "headType": "fang", "tailType": "hook"}
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
    distanceTonearestFood = 1000
    myHealth = resp_dict['you']['health']
    maxHeight = resp_dict['board']['height']
    snakeHeadX = resp_dict['you']['body'][0]['x']
    snakeHeadY = resp_dict['you']['body'][0]['y']
    snakeHeadXY = snakeHeadX, snakeHeadY
    currentNearestFood = nearestFood(snakeHeadX, snakeHeadY, getFoodSpaces(resp_dict))
    distanceTonearestFood = calculateDistance(snakeHeadX, currentNearestFood[0],snakeHeadY, currentNearestFood[1])
    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    shout = "I am spaghetti!"
    print("My Health: ", myHealth)
    print("Snake - Head Coordinates: ", snakeHeadXY)
    print("All Snake Spaces: ", getAllSnakeSpaces(resp_dict))
    print("All Food Spaces: ", getFoodSpaces(resp_dict))
    print("Nearest Food Space: ", currentNearestFood, " with a Distance: ", distanceTonearestFood)
    print("isUpFree: ", isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)))
    print("isLeftFree: ", isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)))
    print("isDownFree: ", isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)))
    print("isRightFree: ", isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)))
    isCloserToFood_RIGHT = isCloserToFood(snakeHeadX + 1, snakeHeadY, currentNearestFood, distanceTonearestFood ) 
    isCloserToFood_LEFT =  isCloserToFood(snakeHeadX - 1,  snakeHeadY, currentNearestFood, distanceTonearestFood)
    isCloserToFood_UP =  isCloserToFood(snakeHeadX, snakeHeadY-1, currentNearestFood, distanceTonearestFood)
    isCloserToFood_DOWN =  isCloserToFood(snakeHeadX, snakeHeadY+1, currentNearestFood, distanceTonearestFood)
    print("LEFTFOOD:", isCloserToFood_LEFT,"UPFOOD:", isCloserToFood_UP,"DOWNFOOD:", isCloserToFood_DOWN,"RIGHTFOOD:", isCloserToFood_RIGHT,)
    print("isFoodLeft: ", isFoodLeft(snakeHeadXY,currentNearestFood))
    print("isFoodRight: ", isFoodRight(snakeHeadXY,currentNearestFood))
    print("isFoodUp: ", isFoodUp(snakeHeadXY,currentNearestFood))
    print("isFoodDown: ", isFoodDown(snakeHeadXY,currentNearestFood))

    if isFoodUp(snakeHeadXY,getFoodSpaces(resp_dict)):
        response = {"move": "up", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isFoodLeft(snakeHeadXY,getFoodSpaces(resp_dict)):
        response = {"move": "left", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isFoodRight(snakeHeadXY,getFoodSpaces(resp_dict)):
        response = {"move": "right", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif isFoodDown(snakeHeadXY,getFoodSpaces(resp_dict)):
        response = {"move": "down", "shout": shout}
        return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
        )
    elif myHealth >= 80:
        print("Healthy")
        if isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
            print("Healthy UP")
            response = {"move": "up", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
            print("Healthy Left")
            response = {"move": "left", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
            print("Healthy Down")
            response = {"move": "down", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
            print("Healthy RIGHT")
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
    elif myHealth < 80:
        print("Hungry")
        if (isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)) and isCloserToFood_DOWN):
            print("Hungry DOWN")           
            response = {"move": "down", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif (isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)) and isCloserToFood_RIGHT) : 
            print("Hungry RIGHT")
            response = {"move": "right", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif (isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)) and isCloserToFood_UP):
            print("Hungry UP")
            response = {"move": "up", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        elif (isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)) and isCloserToFood_LEFT):
            print("Hungry LEFT")
            response = {"move": "left", "shout": shout}
            return HTTPResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(response),
            )
        else:
            move = ""   
            while move == "":
                proposedMove = random.choice(directions)
                if (proposedMove == "up"):
                    if isUpFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
                        move = "up"
                        print("move has been set to up", move)
                    else:
                        proposedMove = random.choice(directions) 
                elif (proposedMove == "left"):
                    if isLeftFree(snakeHeadX, snakeHeadY, getAllSnakeSpaces(resp_dict)):
                        move = "left"
                        print("move has been set to left", move)
                    else:
                        proposedMove = random.choice(directions) 
                elif (proposedMove == "right"):
                    if isRightFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
                        move = "right"
                        print("move has been set to right", move)
                    else:
                        proposedMove = random.choice(directions) 
                elif (proposedMove == "down"):
                    if isDownFree(snakeHeadX, snakeHeadY, maxHeight, getAllSnakeSpaces(resp_dict)):
                        move = "down"
                        print("move has been set to down", move)
                    else:
                        proposedMove = random.choice(directions)  

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
        return False
    elif upCoordinate in totalSnakeSpaces.values():  #Represents the up Space containing a snake
        return False
    return True

def isDownFree(currentX, currentY, maxHeight, totalSnakeSpaces):
    downSpace = currentY + 1
    downCoordinate = currentX, downSpace
    if downSpace == maxHeight: #Bottom of board Wall
        return False
    elif downCoordinate in totalSnakeSpaces.values():  # Represents the up Space containing a snake
        return False
    return True

def isLeftFree(currentX, currentY, totalSnakeSpaces):
    leftSpace = currentX - 1
    leftCoordinate = leftSpace, currentY
    if leftSpace == -1: #Left of board Wall
        return False
    elif leftCoordinate in totalSnakeSpaces.values():  # BROKEN -  Represents the up Space containing a snake
        return False
    return True

def isRightFree(currentX, currentY, maxWidth, totalSnakeSpaces):
    rightSpace = currentX + 1
    rightCoordinate = rightSpace, currentY
    if rightSpace == maxWidth: #Right of board Wall
        return False
    elif rightCoordinate in totalSnakeSpaces.values():  # BROKEN - Represents the up Space containing a snake
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

def isFoodLeft(snakeHead, nearestFood):
    print("SnakeHeadLeft: ", (snakeHead[0]-1,snakeHead[1]))
    print((snakeHead[0]-1,snakeHead[1]) in nearestFood)
    if (snakeHead[0]-1,snakeHead[1]) in nearestFood:
        return True
    return False
def isFoodRight(snakeHead, nearestFood):
    print("SnakeHeadRight: ", (snakeHead[0]+1,snakeHead[1]))
    print((snakeHead[0]+1,snakeHead[1]) in nearestFood)
    if (snakeHead[0]+1,snakeHead[1]) in nearestFood:
        return True
    return False

def isFoodUp(snakeHead, nearestFood):
    print("SnakeHeadUp: ", (snakeHead[0], snakeHead[1]-1))
    print((snakeHead[0], snakeHead[1]-1) in nearestFood)
    if (snakeHead[0], snakeHead[1]-1) in nearestFood:
        return True
    return False

def isFoodDown(snakeHead, nearestFood):
    print("SnakeHeadDown: ", (snakeHead[0], snakeHead[1]+1))
    print((snakeHead[0], snakeHead[1]+1) in nearestFood)
    if (snakeHead[0], snakeHead[1]+1) in nearestFood:
        return True
    return False
    

def getFoodSpaces(boardData):
    allFoodSpaces = {}
    for food in range(len(boardData['board']['food'])):
        currentX = boardData['board']['food'][food]['x']
        currentY = boardData['board']['food'][food]['y']
        allFoodSpaces[food] = currentX, currentY
    return allFoodSpaces

def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist  

def nearestFood(currentX, currentY, foodSpaces):
    nearestFoodCoord = (0,0)
    shortestDistance = 1000
    currentSnakeHead = currentX, currentY
    for foodSpace in range(len(foodSpaces)):
        thisDistance = calculateDistance(currentX,foodSpaces[foodSpace][0],currentY, foodSpaces[foodSpace][1])
        if thisDistance < shortestDistance:
            shortestDistance = thisDistance
            nearestFoodCoord = foodSpaces[foodSpace][0], foodSpaces[foodSpace][1]
        foodSpace = foodSpace + 1
    return nearestFoodCoord

def isCloserToFood(currentX, currentY, closestFood, distance):
    currentDistance = distance
    nextDistance = calculateDistance(currentX, closestFood[0], currentY, closestFood[1])
    if nextDistance < currentDistance:
        return True
    return False
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
