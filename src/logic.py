import random
import re
from turtle import pos
from typing import List, Dict

"""
This file can be a nice home for your Battlesnake's logic and helper functions.

We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""

def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization

    TIP: If you open your Battlesnake URL in browser you should see this data.
    """
    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Personalize
        "head": "default",  # TODO: Personalize
        "tail": "default",  # TODO: Personalize
    }


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_snake = data["you"]      # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates like {"x": 0, "y": 0}
    my_body = my_snake["body"]  # A list of coordinate dictionaries like [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]

    # Uncomment the lines below to see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnake this turn is: {my_snake}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]

    # Step 0: Don't allow your Battlesnake to move back on it's own neck.
    possible_moves = _avoid_my_neck(my_body, possible_moves)

    # TODO: Step 1 - Don't hit walls.
    # Use information from `data` and `my_head` to not move beyond the game board.
    board = data['board']
    
    possible_moves = _avoid_walls(board, possible_moves)

    # TODO: Step 2 - Don't hit yourself. TODO: Step 3 - Don't collide with others.
    # Use information from `my_body` to avoid moves that would collide with yourself.
    # Use information from `data` to prevent your Battlesnake from colliding with others.
    snakes = data["snakes"]
    
    possible_moves = _avoid_snakes(my_head, snakes, possible_moves)

    # TODO: Step 4 - Find food.
    # Use information in `data` to seek out and find food.
    # food = data['board']['food']

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = _find_food(my_head, data["food"], possible_moves)
    if (move == "none"):
        move = random.choice(possible_moves)
    # TODO: Explore new strategies for picking a move that are better than random

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move


def _avoid_my_neck(my_body: dict, possible_moves: List[str]) -> List[str]:
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_head = my_body[0]  # The first body coordinate is always the head
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves

def _avoid_walls(my_head: dict, board: dict, possible_moves: List[str]) -> List[str]:
    board_height = board["height"]
    board_width = board["width"]

    if my_head["x"] == (board_width - 1):
        possible_moves.remove("right")
    elif my_head["x"] == 0:
        possible_moves.remove("left")
        
    if my_head["y"] == (board_height - 1):
        possible_moves.remove("up")
    elif my_head["y"] == 0:
        possible_moves.remove("down")
        
    return possible_moves
        
def _avoid_snakes(my_head: dict, snakes: dict, possible_moves: List[str]) -> List[str]:
    for snake in snakes:
        for coord in snake["body"]:
            if coord["x"] == my_head["x"]:
                if coord["y"] > my_head["y"]:
                    possible_moves.remove("up")
                else:
                    possible_moves.remove("down")
            elif coord["y"] == my_head["y"]:
                if coord["x"] > my_head["x"]:
                    possible_moves.remove("right")
                else:
                    possible_moves.remove("left")
    
    return possible_moves

def _find_food(my_head: dict, food: list, possible_moves: List[str]) -> str:
    if food.len() == 0:
        return "none"
    
    currLow: int = 21
    closestCoord: dict = {"x":11, "y":11}
    
    for coord in food:
        distX = abs(coord["x"] - my_head["x"])
        distY = abs(coord["y"] - my_head["y"])
        
        curr = distX + distY
        
        if (curr < currLow):
            currLow = curr
            closestCoord = coord
            
    currX: str
    currY: str
    
    if closestCoord["x"] > my_head["x"]:
        currX = "right"
    elif closestCoord["x"] < my_head["x"]:
        currX =  "left"

    if closestCoord["y"] > my_head["y"]:
        currY = "up"
    elif closestCoord["y"] < my_head["y"]:
        currY = "down"
        
    if (possible_moves.index(currX)):
        return currX
    elif(possible_moves.index(currY)):
        return currY
    else:
        return "none"