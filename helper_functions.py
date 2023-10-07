import copy
import time
import numpy as np
import typing


def look_ahead(head, move):
    """Given a possible move, return the snake's new coordinates if it were headed that way"""
    snake_head = head.copy()
    if move == "up":
        snake_head["y"] += 1
    if move == "down":
        snake_head["y"] -= 1
    if move == "left":
        snake_head["x"] -= 1
    if move == "right":
        snake_head["x"] += 1
    return snake_head

def simulate_move(game_state, move, snake_id):
    """Given a game_state variable, simulate a board with a given move for a given snake"""
    game_state2 = game_state
    all_snakes = game_state2["board"]["snakes"]
    head = [snake for snake in all_snakes if snake["id"] == snake_id][0]["head"]
    new_head = look_ahead(head, move)

    snake_index = [snake["id"] for snake in all_snakes].index(snake_id)
    game_state2["board"]["snakes"][snake_index]["body"] = [new_head] + game_state2["board"]["snakes"][snake_index]["body"][:-1]  # Remove tail
    if snake_id == game_state2["you"]["id"]:
        game_state2["you"]["body"] = [new_head] + game_state2["you"]["body"][:-1]  # Remove tail
        game_state2["you"]["head"] =  new_head
    return game_state2

def calc_manhattan_distance(start, end):
    """Return the Manhattan distance for two positions"""
    start = (start["x"], start["y"])
    end = (end["x"], end["y"])
    return sum(abs(value1 - value2) for value1, value2 in zip(start, end))

def flood_fill(game_state, risk_averse=True):
    """Recursive function to get the total area of the current fill selection"""
    clock_in = time.time_ns()
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    my_head = game_state["you"]["head"]
    my_length = game_state["you"]["length"]

    # Make an (l x w) array and simulate the board
    board = np.empty((board_width, board_height), dtype="<U10")
    board.fill(".")
    for opponent in game_state["board"]["snakes"]:
        snake_body = opponent["body"]
        for snake_sq in snake_body:
            board[snake_sq["x"], snake_sq["y"]] = "x"
            if opponent["id"] == game_state["you"]["id"]:  # Ignore yourself
                board[snake_sq["x"], snake_sq["y"]] = "o"
            elif risk_averse and my_length < opponent["length"]:
                opponent_head = opponent["head"]
                opponent_moves = [look_ahead(opponent_head, move) for move in ["up", "down", "left", "right"]]
                for m in opponent_moves:
                    if 0 <= m["x"] < board_width and 0 <= m["y"] < board_height:
                        board[m["x"], m["y"]] = "x"

    def fill(x, y, board, first_sq):
        if board[x][y] == "x" and not first_sq:  # Snakes or hazards
            return
        if board[x][y] == "o" and not first_sq:  # Us
            return
        if board[x][y] == "£":  # Already filled
            return
        board[x][y] = "£"
        neighbours = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
        for n in neighbours:
            if 0 <= n[0] < board_width and 0 <= n[1] < board_height:
                fill(n[0], n[1], board, first_sq=False)

    fill(my_head["x"], my_head["y"], board, first_sq=True)
    # print(f"Performed flood fill in {(time.time_ns() - clock_in) // 1000000} ms")
    return sum((row == "£").sum() for row in board)
