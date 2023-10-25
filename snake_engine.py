from __future__ import annotations
import copy
import itertools
import logging
import networkx as nx
import numpy as np
import sys
import time
from collections import Counter
from matplotlib import colors, image as mpimg, pyplot as plt
from networkx_tree import hierarchy_pos
from typing import Optional

my_name = "Nightwing"
# Use these global variables to add data for visualising the minimax decision tree
tree_tracker = {4: [], 3: [], 2: [], 1: [], 0: []}
tree_edges = []
tree_nodes = []
tree_node_counter = 1


class Battlesnake:
    def __init__(self, game_state: dict, debugging: Optional[bool] = False):
        """
        Represents our Battlesnake in any given game state and includes all our decision-making methods

        :param game_state: The move API request (https://docs.battlesnake.com/api/example-move#move-api-response)
        :param debugging: Set to True if you want to view a log of what's happening behind the minimax algorithm
        """
        # General game data
        self.turn = game_state["turn"]
        self.board_width = game_state["board"]["width"]
        self.board_height = game_state["board"]["height"]
        self.food = game_state["board"]["food"]
        self.hazards = game_state["board"]["hazards"]
        self.board = None  # Generated later with update_board()
        self.graph = None  # Generated later with update_board()

        # Our snake's data
        self.my_id = game_state["you"]["id"]
        self.my_head = game_state["you"]["head"]
        self.my_neck = game_state["you"]["body"][1]
        self.my_body = game_state["you"]["body"]
        self.my_length = game_state["you"]["length"]
        self.my_health = game_state["you"]["health"]

        # Read snake positions as a dictionary of dictionaries (easier to access than list of dicts)
        self.all_snakes_dict: dict[str, dict] = {}
        for snake in game_state["board"]["snakes"]:
            self.all_snakes_dict[snake["id"]] = {
                "head": snake["head"],
                "neck": snake["body"][1],
                "body": snake["body"],
                "length": snake["length"],
                "health": snake["health"],
                "food_eaten": snake["food_eaten"] if "food_eaten" in snake.keys() else []
            }
            # Weird cases when running locally where the "you" snake is not our actual snake or is empty
            if "name" in game_state["you"] and game_state["you"]["name"] != my_name and snake["name"] == my_name:
                self.my_id = snake["id"]
                self.my_head = snake["head"]
                self.my_neck = snake["body"][1]
                self.my_body = snake["body"]
                self.my_length = snake["length"]
                self.my_health = snake["health"]
        # Another weird edge case when running locally where our snake is not actually in the "snakes" field
        if self.my_id not in self.all_snakes_dict.keys():
            self.all_snakes_dict[self.my_id] = {
                "head": self.my_head,
                "neck": self.my_neck,
                "body": self.my_body,
                "length": self.my_length,
                "health": self.my_health
            }

        # Opponent snakes
        self.opponents = self.all_snakes_dict.copy()
        self.opponents.pop(self.my_id)

        # Finish up our constructor
        self.update_board()
        self.minimax_search_depth = 4  # Depth for minimax algorithm
        self.peripheral_size = 3  # Length of our snake's "peripheral vision"
        self.debugging = debugging
        logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
        if not self.debugging:
            logging.disable(logging.INFO)

    def __copy__(self) -> Battlesnake:
        """
        Making a deep copy of the game_state dictionary takes too much time, so let's manually build it from
        scratch. That way, we can modify a copied instance of the class without affecting the original instance.

        :return: A new instance of our Battlesnake class
        """
        all_snakes = []
        for snake_id, snake in self.all_snakes_dict.items():
            all_snakes.append({
                "id": snake_id,
                "head": snake["head"],
                "body": snake["body"].copy(),
                "length": snake["length"],
                "health": snake["health"],
                "food_eaten": snake["food_eaten"] if "food_eaten" in snake.keys() else []
            })
        board = {
            "height": self.board_height,
            "width": self.board_width,
            "food": self.food.copy(),
            "hazards": self.hazards.copy(),
            "snakes": all_snakes
        }
        you = {
            "id": self.my_id,
            "health": self.my_health,
            "body": self.my_body.copy(),
            "head": self.my_head,
            "length": self.my_length
        }
        new_game_state = {"turn": self.turn, "board": board, "you": you}
        return Battlesnake(new_game_state, debugging=self.debugging)

    def update_board(self):
        """
        Fill in the board with the locations of all snakes. Our snake will be displayed like "oo£" where "o"
        represents the body and "£" represents the head. Opponents will be displayed as "xx£" in the same manner.
        """
        self.board = np.full((self.board_width, self.board_height), " ")
        self.graph = nx.grid_2d_graph(self.board_width, self.board_height)
        for num, my_square in enumerate(self.my_body):
            self.board[my_square["x"], my_square["y"]] = "£" if num == 0 else "o"
            if num > 0:
                self.graph.remove_nodes_from([(my_square["x"], my_square["y"])])
        for opponent in self.opponents.values():
            snake_body = opponent["body"]
            for num, snake_sq in enumerate(snake_body):
                self.board[snake_sq["x"], snake_sq["y"]] = "$" if num == 0 else "x"
                self.graph.remove_nodes_from([(snake_sq["x"], snake_sq["y"])])

    def display_board(self, board: Optional[np.array] = None, return_string: Optional[bool] = False):
        """
        Print out a nicely formatted board for convenient debugging e.g.

         |  |  |  |  |  |  |  |  |  |  |
         |  |  |  |  |  |  |  |  |  |  |
         |  |  |  |  | o| o| o| o| o| o|
         |  |  |  |  | o| o|  |  |  | o|
        x| x|  |  |  |  |  |  |  |  | o|
        x|  |  |  |  |  |  |  |  |  | o|
        x|  |  |  |  |  |  |  |  |  | o|
        x|  |  |  | £| o| o| o| o| o| o|
        x|  |  | $| x| x| x|  |  |  |  |
        x| x| x| x| x| x| x|  |  |  |  |
         |  |  |  |  |  |  |  |  |  |  |

        :param board: Calling display_board() will print out the current board, but for debugging purposes, you can feed
            in a different board variable to display
        :param return_string: You can optionally choose to return the board as a string for you to print later
        """
        render_board = board if board is not None else self.board
        for j in range(1, len(render_board[0]) + 1):
            display_row = ""
            for i in range(0, len(render_board)):
                display_row += f"{render_board[i][-j]}| "
            if self.debugging:
                logging.info(display_row)
            else:
                print(display_row)

        # Return the board as a string instead of printing it out
        if return_string:
            board_str = ""
            for j in range(1, len(render_board[0]) + 1):
                display_row = ""
                for i in range(0, len(render_board)):
                    if render_board[i][-j] == " ":  # Adjust for difference in sizes between spaces and x/o's
                        display_row += f"  | "
                    else:
                        display_row += f"{render_board[i][-j]}| "
                board_str += display_row + "\n"
            return board_str

    @staticmethod
    def look_ahead(head: dict, move: str) -> dict:
        """
        Given a possible move, return the snake's new coordinates if it were headed that way

        :param head: The location of the snake's head as a dictionary e.g. {"x": 5, "y": 10}
        :param move: Either "left", "right", "up", or "down"

        :return: The new location of the snake's head if it were to move in said direction e.g. {"x": 4, "y": 10}
        """
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

    @staticmethod
    def manhattan_distance(start: dict, end: dict) -> int:
        """
        Return the Manhattan distance between two positions

        :param start: A location on the board as a dictionary e.g. {"x": 5, "y": 10}
        :param end: A different location on the board

        :return: The Manhattan distance between the start and end inputs
        """
        start = (start["x"], start["y"])
        end = (end["x"], end["y"])
        return sum(abs(value1 - value2) for value1, value2 in zip(start, end))

    def dijkstra_shortest_path(self, start: dict, end: dict) -> int:
        """
        Return the shortest path between two positions using Dijkstra's algorithm implemented in networkx

        :param start: A location on the board as a dictionary e.g. {"x": 5, "y": 10}
        :param end: A different location on the board

        :return: The shortest distance between the start and end inputs. 1e6 if no path could be found
        """
        start = (start["x"], start["y"])
        end = (end["x"], end["y"])

        # If the desired location is on a hazard or snake, then it's absent from the graph - add it in but remove later
        temp_start_node = False
        temp_end_node = False
        if start not in self.graph.nodes():
            self.graph.add_node(start)
            temp_start_node = True
        if end not in self.graph.nodes():
            self.graph.add_node(end)
            temp_end_node = True

        # Run networkx's Dijkstra method (it'll error out if no path is possible)
        try:
            self.display_board()
            path = nx.shortest_path(self.graph, start, end)
            shortest = len(path)
        except nx.exception.NetworkXNoPath:
            shortest =  1e6

        # Remove any nodes that were temporarily added in
        if temp_start_node:
            self.graph.remove_node(start)
        if temp_end_node:
            self.graph.remove_node(end)
        return shortest

    @staticmethod
    def snake_compass(head: dict, neck: dict) -> str:
        """
        Return the direction a snake is facing in the current board

        :param head: The location of the snake's head as a dictionary e.g. {"x": 5, "y": 10}
        :param neck: The location of the snake's neck as a dictionary e.g. {"x": 6, "y": 10}

        :return: Either "left", "right", "up", or "down" e.g. "right" for the above inputs
        """
        if neck["x"] < head["x"]:
            direction = "right"
        elif neck["x"] > head["x"]:
            direction = "left"
        elif neck["y"] < head["y"]:
            direction = "up"
        elif neck["y"] > head["y"]:
            direction = "down"
        else:
            direction = "none"  # At the beginning of the game when snakes are coiled
        return direction

    def peripheral_vision(self, snake_id: str, direction: str) -> tuple[tuple, tuple, dict]:
        """
        Calculate our snake's peripheral vision aka the portion of the board that is closest to our snake in a certain
        direction. E.g. the space bounded by [x1, x2] and [y1, y2] in the following example board. Notice that the space
        extends 3 squares above, below, and to the left of the snake, assuming we specified direction="left". Also
        notice that the head of the snake doesn't actually enter the 3x7 peripheral field - the hypothetical new head is
        returned as an output for convenience.

         |  |  |
         |  |  |
         |  |  |
         |  |  | £|
         |  | $|
         | x| x|
         |  |  |

        :param snake_id: The ID of the desired snake we want to find the peripheral field for
        :param direction: The direction you'd like to point the snake towards (either "left", "right", "up", or "down",
            but use "auto" if you want to just use the direction the snake is facing in the current board)

        :return:
            [x1, x2] of a portion of the board that functions as the snake's peripheral vision
            [y1, y2] of the same portion
            The position of the snake's head if it hypothetically moved into its peripheral field (used to perform
                flood-fill on the peripheral field)
        """
        # Our peripheral field of vision when scanning for moves
        head = self.all_snakes_dict[snake_id]["head"].copy()
        neck = self.all_snakes_dict[snake_id]["neck"].copy()
        dim = self.peripheral_size

        # Got to figure out the direction ourselves
        if direction == "auto":
            direction = self.snake_compass(head, neck)
            head = neck.copy()  # Roll back our head location

        # Construct the bounds of the peripheral field depending on the requested direction
        if direction == "right":
            peripheral_box_x = head["x"] + 1, min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = 0, head["y"] - peripheral_box_y[0]
        elif direction == "left":
            peripheral_box_x = max(head["x"] - dim, 0), head["x"]
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = max(head["x"] - peripheral_box_x[0] - 1, 0), head["y"] - peripheral_box_y[0]
        elif direction == "up":
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = head["y"] + 1, min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], 0
        elif direction == "down":
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), head["y"]
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], max(head["y"] - peripheral_box_y[0] - 1, 0)
        else:  # Centre it around our snake's head
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], head["y"] - peripheral_box_y[0]

        return peripheral_box_x, peripheral_box_y, head

    def is_move_safe(
            self,
            move: dict,
            snake_id: str,
            turn: Optional[str] = "done"
    ) -> tuple[bool, bool]:
        """
        Determine if a location on the board is safe (e.g. if it's out-of-bounds or hits a different snake) or risky
        (e.g. if there's a chance of a head-to-head collision). Can be used in the middle of running the minimax
        algorithm (but make sure to specify the "turn_over" parameter).

        :param move: The location of the snake's hypothetical head as a dictionary e.g. {"x": 5, "y": 10}
        :param snake_id: The ID of the desired snake we're evaluating a move for
        :param turn: Either "ours", "opponents", or "done". Addresses nuances with running this function during the
            minimax algorithm or outside of it. If "ours", this means we're at a depth where our snake has to make a
            move. If "opponents", then we're at a depth where we've made a move but the opponent snakes haven't. If
            "done", then both our snake and the opponent snakes have made moves (and one complete turn
            has been completed).

        :return:
            True if the square is safe, False otherwise
            True if the square is risky, False otherwise
        """
        # Prevent snake from moving out of bounds
        if move["x"] < 0 or move["x"] >= self.board_width:
            return False, True
        if move["y"] < 0 or move["y"] >= self.board_height:
            return False, True

        # Prevent snake from colliding with other snakes
        length = self.all_snakes_dict[snake_id]["length"]
        risky_flag = False
        for opp_id, opp_snake in self.all_snakes_dict.items():

            # Different rules apply during the middle of running minimax, depending on whose turn it is since our snake
            # makes moves separately from opponent snakes
            if turn == "ours":
                # We can run into the tail of any snake since it will have to move forward
                if move in opp_snake["body"][:-1] and snake_id != opp_id:
                    return False, True
                # We cannot hit our own head
                elif move in opp_snake["body"][1:-1] and snake_id == opp_id:
                    return False, True
                # Flag a move as risky if it could lead to a losing head-to-head collision
                elif (snake_id != opp_id  # Skip the same snake we're evaluating
                      and length <= opp_snake["length"]  # Only if the other snake is the same length or longer
                      and self.manhattan_distance(move, opp_snake["head"]) == 1):  # Only if we're collision-bound
                    risky_flag = True

            elif turn == "opponents":
                if opp_id == self.my_id:
                    # Our snake's tail is off-limits since we will already have moved
                    if move in opp_snake["body"][1:]:
                        return False, True
                    # Avoid losing head-to-head collisions with our snake, but suicidal collisions are fine if our snake
                    # is the same length and also dies
                    elif move == opp_snake["head"] and length < opp_snake["length"]:
                        return False, True
                else:
                    # Tail is fine against other opponents
                    if move in opp_snake["body"][:-1]:
                        return False, True
                    # Flag a move as risky if it could lead to a losing head-to-head collision
                    elif (snake_id != opp_id  # Skip the same snake we're evaluating
                          and length <= opp_snake["length"]  # Only if the other snake is the same length or longer
                          and self.manhattan_distance(move, opp_snake["head"]) == 1):  # Only if we're collision-bound
                        risky_flag = True

            elif turn == "done":
                # Move is invalid if it collides with the body of a snake
                if move in opp_snake["body"][1:]:
                    return False, True
                # Move is invalid if it collides with the head of a snake that is the same length or longer
                elif snake_id != opp_id and move == opp_snake["head"] and length <= opp_snake["length"]:
                    return False, True

            elif turn == "flood_fill":
                if move in opp_snake["body"]:
                    return False, True

        return True, risky_flag

    def get_obvious_moves(
            self,
            snake_id: str,
            risk_averse: Optional[bool] = True,
            sort_by_dist_to: Optional[str] = None,
            sort_by_peripheral: Optional[bool] = False
    ) -> list:
        """
        Return a list of valid moves for any hypothetical snake.

        :param snake_id: The ID of the desired snake we want to find moves for (can also be any opponent snake).
        :param risk_averse: Return possible moves that avoid death-inducing collisions (essentially we're assuming our
            opponents are out to get us, but only if we're shorter). Set False to include any risky moves towards other
            snakes that might kill us.
        :param sort_by_dist_to: Input any snake ID here. This will return all possible moves, but sort the moves by the
            distance from our snake (after making the move) to the head of the snake whose ID was inputted. Very useful
            for discerning which moves are more threatening/bring us closer to a different snake.
        :param sort_by_peripheral: If True, return all possible moves, but sort the moves by the amount of space that
            each move will give us in our "peripheral vision". Very useful for discerning which moves allow us more
            immediate space.

        :return: A list of possible moves for the given snake
        """
        # Loop through possible moves and remove from consideration if it's invalid
        possible_moves = ["up", "down", "left", "right"]
        risky_moves = []
        head = self.all_snakes_dict[snake_id]["head"]
        for move in possible_moves.copy():
            is_safe, is_risky = self.is_move_safe(
                self.look_ahead(head, move),
                snake_id,
                turn="ours" if snake_id == self.my_id else "opponents"
            )
            if not is_safe or (risk_averse and is_risky):
                possible_moves.remove(move)
            if is_risky:
                risky_moves.append(move)

        if sort_by_dist_to is not None:
            head2 = self.all_snakes_dict[sort_by_dist_to]["head"]
            possible_moves = sorted(possible_moves,
                                    key=lambda move2: self.dijkstra_shortest_path(head2, self.look_ahead(head, move2)))
        if sort_by_peripheral:
            possible_moves = sorted(possible_moves,
                                    key=lambda move2: self.flood_fill(snake_id, confined_area=move2),
                                    reverse=True)
        # De-prioritise any risky moves and send them to the back
        if len(risky_moves) > 0:
            for risky in risky_moves:
                if risky in possible_moves:
                    possible_moves.append(possible_moves.pop(possible_moves.index(risky)))

        logging.info(f"Found obvious moves {possible_moves}")
        return possible_moves

    def is_game_over(self, for_snake_id: str | list, depth: Optional[int] = None) -> tuple[bool, bool]:
        """
        Determine if the game ended for certain snakes or not. Mostly use to know whether our snake died, but can
        optionally be used to determine any number of opponent snakes' statuses.

        :param for_snake_id: The ID of the desired snake we want to know died or not
        :param depth: During minimax, things get complicated when we call this function right after making a move for
            our snake but before the opponent snakes have made moves. We only want to return True when a complete turn
            is done (e.g. our snake made a move and our opponents did as well). Thus, we need the current depth that
            minimax is on to determine this.

        :return:
            True if the overall game has a winner or if our snake is dead, False otherwise
            True if the snake associated with the input snake ID is alive, False otherwise
        """
        # Skip if we're at the beginning of the game when all snakes are still coiled up
        if self.turn == 0:
            return False, True

        snake_monitor = {}  # A dictionary for each snake showing whether they're alive
        for snake_id, snake in self.all_snakes_dict.items():
            # Check if each snake's head is in a safe square, depending on if we're at a depth where only we made a move
            is_safe, _ = self.is_move_safe(snake["head"], snake_id, turn="done" if depth % 2 == 0 else "ours")
            snake_monitor[snake_id] = is_safe

        # Game is over if there's only one snake remaining or if our snake died
        game_over = True if (sum(snake_monitor.values()) == 1 or not snake_monitor[self.my_id]) else False
        # See if a specific snake is alive or not
        if isinstance(for_snake_id, (list, tuple)):
            snake_still_alive = [snake_monitor[snake_id] for snake_id in for_snake_id]
        else:
            snake_still_alive = snake_monitor[self.my_id] if for_snake_id is None else snake_monitor[for_snake_id]

        return game_over, snake_still_alive

    def simulate_move(self, move: str, snake_id: str, evaluate_deaths: Optional[bool] = False) -> Battlesnake:
        """
        Create a new Battlesnake instance that simulates a move for a given snake

        :param move: The direction you'd like the snake to move towards (either "left", "right", "up", or "down")
        :param snake_id: The ID of the desired snake we want to simulate a move for
        :param evaluate_deaths: If True, remove any snakes that died as a result of the simulated move (exclusively via
            head-to-head collisions)

        :return: A Battlesnake instance incorporating the simulated move in a new game state
        """
        # clock_in = time.time_ns()
        new_game = self.__copy__()

        # Simulate the new head position
        old_head = self.all_snakes_dict[snake_id]["head"]
        new_head = self.look_ahead(old_head, move)

        # Insert the simulated snake position into the new instance
        new_game.all_snakes_dict[snake_id]["body"] = [new_head] + new_game.all_snakes_dict[snake_id]["body"][:-1]
        new_game.all_snakes_dict[snake_id]["head"] = new_head
        new_game.all_snakes_dict[snake_id]["health"] -= 1
        # Repeat for our snake's specific attributes
        if snake_id == self.my_id:
            new_game.my_body = [new_head] + new_game.my_body[:-1]
            new_game.my_head = new_head
            new_game.my_health -= 1

        # Track if food was consumed - this elongates the snake from the tail and restores health
        if new_head in self.food:
            new_game.all_snakes_dict[snake_id]["food_eaten"] = new_head

        # Check if any snakes died from this simulated move and remove them from the game
        if evaluate_deaths:
            # First update snake lengths from any food eaten
            for update_id, snake in new_game.all_snakes_dict.items():
                if len(snake["food_eaten"]) > 0:
                    new_game.all_snakes_dict[update_id]["length"] += 1
                    new_game.all_snakes_dict[update_id]["health"] = 100
                    new_game.all_snakes_dict[update_id]["body"] += [new_game.all_snakes_dict[update_id]["body"][-1]]
                    new_game.food = [food for food in self.food  # Remove the food from the board
                                     if not (food["x"] == snake["food_eaten"]["x"]
                                             and food["y"] == snake["food_eaten"]["y"])]
                    if update_id == self.my_id:
                        new_game.my_length += 1
                        new_game.my_health = 100
                        new_game.my_body += [new_game.my_body[-1]]
                    # Reset the food tracker
                    new_game.all_snakes_dict[update_id]["food_eaten"] = []

            # Did any snakes die from head-to-head collisions?
            all_heads = [(snake["head"]["x"], snake["head"]["y"]) for snake in new_game.all_snakes_dict.values()]
            count_heads = Counter(all_heads)
            butt_heads = [k for k, v in count_heads.items() if v > 1]  # Any square where > 1 heads collided
            for butt_head in butt_heads:
                overlapping_snakes = np.array([
                    (rm_id, snake["length"]) for rm_id, snake in new_game.all_snakes_dict.items()
                    if (snake["head"]["x"] == butt_head[0] and snake["head"]["y"] == butt_head[1])
                ])
                lengths = overlapping_snakes[:, 1].astype(int)
                # Special cases where the snake committed suicide and also killed our snake => don't remove
                if not (self.my_id in overlapping_snakes[:, 0]
                        and np.count_nonzero(lengths == new_game.my_length) > 1):
                    indices_largest_snakes = np.argwhere(lengths == lengths.max()).flatten().tolist()
                    if len(indices_largest_snakes) > 1:  # No winner if the snakes are the same length
                        winner_id = None
                    else:
                        winner_id = overlapping_snakes[:, 0][indices_largest_snakes[0]]
                    # Remove any dead snakes
                    for rm_id in overlapping_snakes[:, 0]:
                        if rm_id != winner_id:
                            new_game.all_snakes_dict.pop(rm_id)

        new_game.update_board()
        # logging.info(f"Done with simulation in {round((time.time_ns() - clock_in) / 1000000, 3)} ms")
        return new_game

    def flood_fill(
            self,
            snake_id: str,
            confined_area: Optional[str] = None,
            risk_averse: Optional[bool] = False,
            fast_forward: Optional[int] = 0
    ) -> int:
        """
        Recursive function to get the total available space for a given snake. Basically, count how many £ symbols
        we can fill while avoiding any $, o, and x symbols (obstacles).

        :param snake_id: The ID of the desired snake we want to do flood fill for
        :param confined_area: Tells the function to do flood fill for only on one side of the snake (either "left",
            "right", "up", or "down") to represent its peripheral vision
        :param risk_averse: If True, flood fill will avoid any squares that directly border an opponent's head
        :param fast_forward: Hypothetical scenarios where we want to see how much space we still have after moving
            X turns ahead. E.g. if we set it to 5, then we remove 5 squares from all snake's tails before doing flood
            fill - this is only useful when we suspect we'll be trapped by an opponent snake.

        :return: The total area of the flood fill selection
        """
        head = self.all_snakes_dict[snake_id]["head"]

        if snake_id == self.my_id:  # Assume we're doing flood fill for our snake
            board = copy.deepcopy(self.board)
            # See how flood fill changes when all snakes fast-forward X turns
            if fast_forward > 0:
                for snake in self.all_snakes_dict.values():
                    tail_removed = snake["body"][-fast_forward:]
                    for remove in tail_removed:
                        board[remove["x"]][remove["y"]] = " "
            # Try to avoid any squares that our enemy can go to
            if risk_averse:
                threats = [other["head"] for other in self.opponents.values() if other["length"] >= self.my_length]
                for threat in threats:
                    x, y = threat["x"], threat["y"]
                    avoid_sq = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    for n in avoid_sq:
                        if not (n[0] == head["x"] and n[1] == head["y"]) and \
                                (0 <= n[0] < self.board_width and 0 <= n[1] < self.board_height):
                            board[n[0]][n[1]] = "x"
        else:  # Otherwise, generate a new board and pretend the opponent snake is our snake
            board = np.full((self.board_width, self.board_height), " ")
            for num, square in enumerate(self.all_snakes_dict[snake_id]["body"]):
                board[square["x"], square["y"]] = "£" if num == 0 else "o"
            for other_id, other_snake in self.all_snakes_dict.items():
                if other_id != snake_id:
                    for num, other_square in enumerate(other_snake["body"]):
                        board[other_square["x"], other_square["y"]] = "$" if num == 0 else "x"

        # Narrow down a portion of the board that represents the snake's peripheral vision
        if confined_area is not None:
            xs, ys, head = self.peripheral_vision(snake_id, confined_area)
            board = board[xs[0]:xs[1], ys[0]:ys[1]]

        def fill(x, y, board, initial_square):
            if board[x][y] in ["x", "$"]:  # Snakes or hazards
                return
            if board[x][y] in ["o"]:  # Our snake
                return
            if board[x][y] == "£" and not initial_square:  # Already filled
                return
            board[x][y] = "£"
            neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for n in neighbours:
                if 0 <= n[0] < len(board) and 0 <= n[1] < len(board[0]):
                    fill(n[0], n[1], board, initial_square=False)

        fill(head["x"], head["y"], board, initial_square=True)
        filled = sum((row == "£").sum() for row in board)
        return filled - 1 if filled > 0 else filled  # Exclude the head from the count, but cannot ever be negative

    def dist_to_nearest_food(self) -> int:
        """
        Return the shortest distance to food for our snake, but only if we're closer to it than an opponent snake
        """
        best_dist = np.inf
        for food in self.food:
            dist = self.dijkstra_shortest_path(food, self.my_head)
            # If an enemy snake is longer than ours, and we're both 2 squares away from food, then they're technically
            # closer to it since they'd win the head-to-head battle.
            dist_enemy = min([self.dijkstra_shortest_path(food, snake["head"]) if snake["length"] < self.my_length
                              else self.dijkstra_shortest_path(food, snake["head"]) - 1
                              for snake in self.opponents.values()])
            if dist < best_dist and dist_enemy >= dist:
                best_dist = dist
        return best_dist

    def edge_kill_detection(self):
        """
        Determine if our snake is in a position where it can get edge-killed
        """
        # Ignore if we're not on the edge of the board
        if 0 < self.my_head["x"] < self.board_width - 1 and 0 < self.my_head["y"] < self.board_height - 1:
            return False

        # possible_moves = self.get_obvious_moves(self.my_id, risk_averse=True)
        # direction = self.snake_compass(self.my_head, self.my_neck)
        # dir_dict = {
        #     "vertical": {
        #         "bounds": [0, self.board_width],
        #         "escape_dirs": ["left", "right"],
        #         "axis": "x",
        #         "axis_dir": "y",
        #         "scan_dir": +1 if direction == "up" else -1
        #     },
        #     "horizontal": {
        #         "bounds": [0, self.board_height],
        #         "escape_dirs": ["down", "up"],
        #         "axis": "y",
        #         "axis_dir": "x",
        #         "scan_dir": +1 if direction == "right" else -1
        #     },
        # }
        # dir_data = dir_dict["horizontal"] if direction in ["left", "right"] else dir_dict["vertical"]
        # bounds = dir_data["bounds"]
        # escape_dirs = dir_data["escape_dirs"]
        # ax = dir_data["axis"]
        # ax_dir = dir_data["axis_dir"]
        # scan_dir = dir_data["scan_dir"]
        #
        # # If we can't escape (e.g. we're heading right, but can't move up or down)
        # if len(set(escape_dirs).intersection(possible_moves)) == 0:
        #     trapped_sides = [False, False]
        #     for num, escape_dir in enumerate(escape_dirs):
        #         look = -1 if num == 0 else +1
        #         # Scan the column/row to each side of us in ascending order
        #         if escape_dir in ["left", "right"]:
        #             esc_attempt = self.my_head[ax] + look
        #             if 0 <= esc_attempt < self.board_width:
        #                 strip = self.board[esc_attempt, self.my_head[ax_dir]:]
        #                 # Check if there's free space ahead of us, we're trapped if there's none
        #                 if np.count_nonzero(strip != " ") == 0:
        #                     trapped_sides[num] = True
        #
        #             threats = [opp_id for opp_id, opp in self.opponents.items()
        #                        if (opp["head"][ax] == esc_attempt)
        #                        and (opp["head"][ax_dir] >= self.my_head[ax_dir] if look == 1
        #                             else opp["head"][ax_dir] <= self.my_head[ax_dir]
        #                             )]
        #
        #     # # Find snakes that can possibly edge-kill us
        #     # suspects = [opp_id for opp_id, opp in self.opponents.items()
        #     #             if opp["head"][ax] == self.my_head[ax] + dir_data["adj_col"] and (
        #     #                     opp["head"][dir_data["axis_dir"]] >= self.my_head[dir_data["axis_dir"]] if dir_data["scan_dir"] == 1
        #     #                     else opp["head"][dir_data["axis_dir"]] <= self.my_head[dir_data["axis_dir"]])
        #     #             ]
        #     # if len(suspects) > 0:
        #     #     diff_y = min([self.manhattan_distance(self.my_head, self.opponents[opp_id]["head"]) - 1 for opp_id in suspects])
        #     #     if diff_y == 0:
        #     #         return True
        #     #     gaps = [self.opponents[opp_id]["body"][-diff_y:] for opp_id in suspects]  # Would leave space for us to move to
        #     #     if self.look_ahead(self.my_head, "right") not in list(itertools.chain(*gaps)):
        #     #         return True
        return False

    def heuristic(self, depth_number):
        """Let's figure out a way to evaluate the current board for our snake :)

        Should be a function of:
        - Maximising available space for our snake (flood fill)
        - Minimising available space for enemy snakes
        - Distance to food
        - How far down our game tree we went in our minimax search
        """
        # Determine how many layers deep in the game tree we are
        layers_deep = self.minimax_search_depth - depth_number

        # If an opponent snake dies :)
        opponents_left = len(self.opponents)

        # Determine available space via flood fill
        available_space = self.flood_fill(self.my_id, risk_averse=True)
        available_space_ra = self.flood_fill(self.my_id, risk_averse=False)
        if available_space_ra < 4:
            space_penalty = -500
        elif available_space < 4:
            space_penalty = -200
        else:
            space_penalty = 0

        # ARE WE TRAPPED???
        trap_space = None
        if available_space <= 10:
            trap_space = available_space - self.flood_fill(self.my_id, fast_forward=available_space)
        # Shoot we're trapped
        if trap_space == 0:
            space_penalty = -1e7  # We'd prefer getting killed than getting trapped, so penalise this more

        # ARE WE GOING TO GET EDGE-KILLED???
        possible_edged = self.edge_kill_detection()
        if possible_edged:
            space_penalty = -1e5
            self.edge_kill_detection()

        # Estimate the space we have in our peripheral vision
        available_peripheral = self.flood_fill(self.my_id, confined_area="auto")

        # We want to minimise available space for our opponents via flood fill (but only when there are fewer snakes in
        # our vicinity)
        if len(self.opponents) <= 3:
                # and sum([dist < (self.board_width // 2) for dist in self.dist_from_enemies()]) <= 3 \
                # and len(self.opponents) == sum([self.my_length > s["length"] for s in self.opponents.values()]):
            self.peripheral_size = 4
            closest_enemy = sorted(self.opponents.keys(), key=lambda opp_id: self.dijkstra_shortest_path(self.my_head, self.opponents[opp_id]["head"]))[0]
            available_enemy_space = self.flood_fill(closest_enemy, confined_area="General")
            if available_enemy_space < 4:
                kill_bonus = 1000
            else:
                kill_bonus = 0
        else:
            available_enemy_space = 0
            kill_bonus = 0

        # Get closer to enemy snakes if we're longer by 3
        if 2 >= len(self.opponents) == sum([self.my_length > s["length"] + 3 for s in self.opponents.values()]):
            dist_from_enemies = sorted([self.dijkstra_shortest_path(self.my_head, opp["head"]) for opp in self.opponents.values()])
            dist_to_enemy = dist_from_enemies[0]
        else:
            dist_to_enemy = 0

        # If we're getting too close to enemy snakes that are longer, RETREAT
        threats = [self.dijkstra_shortest_path(self.my_head, opp["head"]) for opp in self.opponents.values() if opp["length"] >= self.my_length]
        num_threats = (np.count_nonzero(np.array(threats) <= 2) * 2
                       + np.count_nonzero(np.array(threats) == 3) * 1)

        # Determine the closest safe distance to food
        dist_food = self.dist_to_nearest_food()
        health_flag = True if self.my_health < 40 else False
        shortest_flag = True if sum([self.my_length <= snake["length"] for snake in self.opponents.values()]) >= min([2, len(self.opponents)]) else False
        longest_flag = True if sum([self.my_length > snake["length"] for snake in self.opponents.values()]) == len(self.opponents) else False

        # Are we in the centre of the board? Maximise control
        centre = range(self.board_width // 2 - 2, self.board_width // 2 + 3)
        in_centre = (self.my_head["x"] in centre and self.my_head["x"] in centre) and (len(self.opponents) <= 2)

        # Heuristic formula
        space_weight = 1
        peripheral_weight = 2
        enemy_left_weight = 1000
        enemy_restriction_weight = 75 if len(self.opponents) > 2 else 200
        food_weight = 250 if health_flag else 175 if shortest_flag else 25 if longest_flag else 50
        depth_weight = 25
        length_weight = 300
        centre_control_weight = 10
        aggression_weight = 250 if dist_to_enemy > 0 else 0
        threat_proximity_weight = -25

        logging.info(f"Available space: {available_space}")
        logging.info(f"Available peripheral: {available_peripheral}")
        logging.info(f"Enemies left: {opponents_left}")
        logging.info(f"Threats within 3 squares of us: {num_threats}")
        logging.info(f"Distance to nearest enemy: {dist_to_enemy}")
        logging.info(f"Distance to nearest food: {dist_food}")
        logging.info(f"Layers deep in search tree: {layers_deep}")
        logging.info(f"Available enemy space: {available_enemy_space}")
        logging.info(f"Kill bonus: {kill_bonus}")
        logging.info(f"In centre: {in_centre}")
        logging.info(f"Length: {self.my_length}")

        h = (available_space * space_weight) + space_penalty + \
            (peripheral_weight * available_peripheral) + \
            (enemy_left_weight / (opponents_left + 1)) + \
            (threat_proximity_weight * num_threats) + \
            (food_weight / (dist_food + 1)) + \
            (layers_deep * depth_weight) + \
            (self.my_length * length_weight) + \
            in_centre * centre_control_weight + \
            aggression_weight / (dist_to_enemy + 1) + \
            (enemy_restriction_weight / (available_enemy_space + 1)) + kill_bonus


        return h, {"Heur": round(h, 2),
                   "Space": available_space,
                   "Penalty": space_penalty,
                   "Periph": available_peripheral,
                   "Food Dist": dist_food,
                   "Enemy Dist": dist_to_enemy,
                   "Enemy Kill": available_enemy_space + kill_bonus,
                   "Threats": num_threats,
                   "Length": self.my_length}

    @staticmethod
    def update_tree_visualisation(depth, add_edges=False, add_nodes=False, node_data=None, insert_index=None):
        global tree_node_counter
        global tree_tracker
        if add_edges:
            # Add the node that we'll be creating the edge to
            tree_tracker[depth].append(tree_node_counter)
            # Tuple of (node_1, node_2, node_attributes) where the edge is created between node_1 and node_2
            global tree_edges
            tree_edges.append((tree_tracker[depth + 1][-1], tree_tracker[depth][-1], {"colour": "k", "width": 1}))
            # Now we're going to be on the next node
            tree_node_counter += 1
            return len(tree_edges) - 1

        if add_nodes:
            global tree_nodes
            if insert_index is not None:
                node_move = tree_nodes[insert_index][1]
                formatted_dict = str(node_data).replace(", ", "\n").replace("{", "").replace("}", "").replace("'", "")
                tree_nodes[insert_index] = (tree_tracker[depth][-1], node_move + "\n" + formatted_dict)
            else:
                tree_nodes.append((tree_tracker[depth][-1], str(node_data).replace("'", "")))
            return len(tree_nodes) - 1

    def minimax(self, depth, alpha, beta, maximising_snake):
        """
        Implement the minimax algorithm with alpha-beta pruning

        :param depth:
        :param alpha:
        :param beta:
        :param maximising_snake:

        :return:
        """
        if depth != self.minimax_search_depth:
            # Check if our snake died
            game_over, still_alive = self.is_game_over(for_snake_id=self.my_id, depth=depth)
            if not still_alive:
                logging.info("Our snake died...")
                heuristic = -1e6 + (self.minimax_search_depth - depth)  # Reward slower deaths
                return heuristic, None, {"Heur": heuristic}
            # Otherwise, if our snake is ALIVE and is the winner :)
            elif game_over:
                logging.info("OUR SNAKE WON")
                heuristic = 1e6 + depth  # Reward faster kills
                return heuristic, None, heuristic

        # At the bottom of the decision tree or if we won/lost the game
        if depth == 0:
            logging.info("=" * 50)
            logging.info(f"DEPTH = {depth}")
            heuristic, heuristic_data = self.heuristic(depth_number=depth)
            logging.info(f"Heuristic = {heuristic} at terminal node")
            return heuristic, None, heuristic_data

        global tree_edges
        # Our snake's turn
        if maximising_snake:
            logging.info("=" * 50)
            logging.info(f"DEPTH = {depth} OUR SNAKE")
            logging.info(f"ALPHA = {alpha} | beta = {beta}")

            clock_in = time.time_ns()
            possible_moves = self.get_obvious_moves(  # If > 6 opponents, we'll do depth = 2 and risk_averse = True
                self.my_id, risk_averse=(len(self.opponents) > 6), sort_by_peripheral=True)
            if len(possible_moves) == 0 and len(self.opponents) > 6:  # Try again, but do any risky move
                possible_moves = self.get_obvious_moves(self.my_id, risk_averse=False, sort_by_peripheral=True)
            if len(possible_moves) == 0:  # RIP
                possible_moves = ["down"]

            best_val, best_move = -np.inf, None
            best_node_data, best_edge = None, None
            for num, move in enumerate(possible_moves):
                SIMULATED_BOARD_INSTANCE = self.simulate_move(move, self.my_id)

                logging.info(f"{len(possible_moves)} CHILD NODES: VISITING {num + 1} OF {len(possible_moves)}")
                logging.info(f"Running minimax for OUR SNAKE moving {move}")
                if self.debugging:
                    SIMULATED_BOARD_INSTANCE.display_board()

                clock_in2 = time.time_ns()
                edge_added = self.update_tree_visualisation(add_edges=True, depth=depth - 1)
                node_added = self.update_tree_visualisation(add_nodes=True, depth=depth - 1, node_data=move)
                node_val, node_move, node_data = SIMULATED_BOARD_INSTANCE.minimax(depth - 1, alpha, beta, False)
                self.update_tree_visualisation(add_nodes=True, depth=depth - 1, node_data=node_data, insert_index=node_added)

                logging.info("=" * 50)
                logging.info(f"BACK AT DEPTH = {depth} OUR SNAKE")
                logging.info(f"ALPHA = {alpha} | beta = {beta}")

                # Update best score and best move
                if np.argmax([best_val, node_val]) == 1:
                    best_move = move
                    best_node_data, best_edge = node_data, edge_added
                best_val = max(best_val, node_val)
                old_alpha = alpha
                alpha = max(alpha, best_val)

                logging.info(f"Updated ALPHA from {old_alpha} to {alpha}")
                logging.info(f"Identified best move so far = {best_move} in {round((time.time_ns() - clock_in2) / 1000000, 3)} ms")

                # Check to see if we can prune
                if alpha >= beta:
                    logging.info(f"PRUNED!!! Alpha = {alpha} >= Beta = {beta}")
                    break

            tree_edges[best_edge][2]["colour"] = "r"
            tree_edges[best_edge][2]["width"] = 4
            logging.info(f"FINISHED MINIMAX LAYER on our snake in {round((time.time_ns() - clock_in) / 1000000, 3)} ms")
            return best_val, best_move, best_node_data

        # Opponents' turns
        else:
            logging.info("=" * 50)
            logging.info(f"DEPTH = {depth} OPPONENT SNAKES")
            logging.info(f"BETA = {beta} | alpha = {alpha}")

            clock_in = time.time_ns()
            # If there are multiple opponent snakes, search only for those within a reasonable distance of ours
            if len(self.opponents) == 1:
                search_within = self.board_width * self.board_height
            elif len(self.opponents) <= 3:
                search_within = self.board_width
            elif len(self.opponents) <= 5:
                search_within = self.board_width // 2 + 1
            else:
                search_within = self.board_width // 2

            # Grab possible moves for all opponent snakes
            opps_nearby = 0  # Counter for opponents in our vicinity
            opps_moves = {}  # Store possible moves for each snake id
            for opp_id, opp_snake in self.opponents.items():
                opp_move = self.get_obvious_moves(opp_id, risk_averse=False, sort_by_dist_to=self.my_id)
                if len(opp_move) == 0:  # If the snake has no legal moves, move down and die
                    opp_move = ["down"]

                # Save time by only searching for snakes within close range
                dist_opp_to_us = self.dijkstra_shortest_path(self.my_head, opp_snake["head"])
                if dist_opp_to_us <= search_within:
                    opps_moves[opp_id] = opp_move  # Put all of their moves
                    opps_nearby += 1
                else:
                    if len(self.opponents) <= 5:
                        opps_moves[opp_id] = [opp_move[0]]

            sorted_opps_by_dists = sorted(self.opponents.keys(), key=lambda opp_id: self.dijkstra_shortest_path(self.my_head, self.opponents[opp_id]["head"]))
            opps_moves = dict(sorted(opps_moves.items(), key=lambda pair: sorted_opps_by_dists.index(pair[0])))

            logging.info(f"Found {opps_nearby} of {len(self.opponents)} OPPONENT SNAKES within {search_within} "
                         f"squares of us in {round((time.time_ns() - clock_in) / 1000000, 3)} ms")

            clock_in = time.time_ns()
            # If >= 3 board simulations, then randomly sample 3 of them based on how threatening the position is to our
            # snake to cut down on runtime
            all_opp_combos = list(itertools.product(*opps_moves.values()))
            if len(all_opp_combos) > 2 and len(self.opponents) > 2:
                logging.info(f"FOUND {len(all_opp_combos)} BOARDS BUT CUTTING DOWN TO 2")
                cutoff = 3
            elif len(all_opp_combos) > 3:
                logging.info(f"FOUND {len(all_opp_combos)} BOARDS BUT CUTTING DOWN TO 3")
                cutoff = 3
            else:
                cutoff = 3

            if len(opps_moves) > 0 and len(all_opp_combos) > cutoff:
                covered_ids = [list(opps_moves.keys())[0]]
                all_opp_combos2 = []
                while len(all_opp_combos2) < cutoff:
                    combo_counter = 1
                    for s_id, s in opps_moves.items():
                        if s_id not in covered_ids:
                            combo_counter = combo_counter * len(s)
                    index_getter = np.arange(len(covered_ids) - 1, len(all_opp_combos), combo_counter)
                    getter = [all_opp_combos[i] for i in index_getter]
                    all_opp_combos2.extend(getter)

                all_opp_combos = all_opp_combos2[:cutoff]

            possible_movesets = []
            possible_sims = []
            # Get all possible boards by simulating moves for each opponent snake, one at a time
            for move_combo in all_opp_combos:
                SIMULATED_BOARD_INSTANCE = self.__copy__()
                for num, move in enumerate(move_combo):
                    evaluate_flag = (num + 1 == len(move_combo))
                    SIMULATED_BOARD_INSTANCE = SIMULATED_BOARD_INSTANCE.simulate_move(
                        move, list(opps_moves.keys())[num], evaluate_deaths=evaluate_flag)
                possible_sims.append(SIMULATED_BOARD_INSTANCE.__copy__())
                possible_movesets.append(move_combo)

            logging.info(f"SIMULATED {len(possible_sims)} POSSIBLE BOARDS OF OPPONENT MOVE COMBOS in "
                         f"{round((time.time_ns() - clock_in) / 1000000, 3)} ms")

            clock_in = time.time_ns()
            best_val, best_move = np.inf, None
            best_node_data, best_edge = None, None
            for num, SIMULATED_BOARD_INSTANCE in enumerate(possible_sims):
                logging.info(f"{len(possible_sims)} CHILD NODES: VISITING {num + 1} OF {len(possible_sims)}")
                logging.info(f"Running minimax for OPPONENT SNAKES moving {possible_movesets[num]}")
                if self.debugging:
                    SIMULATED_BOARD_INSTANCE.display_board()
                clock_in2 = time.time_ns()
                edge_added = self.update_tree_visualisation(add_edges=True, depth=depth - 1)
                node_added = self.update_tree_visualisation(add_nodes=True, depth=depth - 1, node_data=str(possible_movesets[num]))
                node_val, node_move, node_data = SIMULATED_BOARD_INSTANCE.minimax(depth - 1, alpha, beta, True)
                self.update_tree_visualisation(add_nodes=True, depth=depth - 1, node_data=node_data,
                                               insert_index=node_added)

                logging.info("=" * 50)
                logging.info(f"BACK AT DEPTH = {depth} OPPONENT SNAKES")
                logging.info(f"BETA = {beta} | alpha = {alpha}")

                # Update best score and best move
                if np.argmin([best_val, node_val]) == 1:
                    best_move = possible_movesets[num]
                    best_node_data, best_edge = node_data, edge_added
                best_val = min(best_val, node_val)
                old_beta = beta
                beta = min(beta, best_val)

                logging.info(f"Updated BETA from {old_beta} to {beta}")
                logging.info(f"Identified best move so far = {best_move} in {round((time.time_ns() - clock_in2) / 1000000, 3)} ms")

                # Check to see if we can prune
                if beta <= alpha:
                    logging.info(f"PRUNED!!! Beta = {beta} <= Alpha = {alpha}")
                    break

            tree_edges[best_edge][2]["colour"] = "r"
            tree_edges[best_edge][2]["width"] = 4
            logging.info(f"FINISHED MINIMAX LAYER on opponents in {(time.time_ns() - clock_in) // 1000000} ms")
            return best_val, best_move, best_node_data

    def optimal_move(self):
        """Let's run the minimax algorithm with alpha-beta pruning!"""
        # Compute the best score of each move using the minimax algorithm with alpha-beta pruning
        if self.turn < 3:  # Our first 3 moves are super self-explanatory tbh
            search_depth = 1
        elif len(self.opponents) > 6:
            search_depth = 2  # TODO should be risk-averse
        elif len(self.opponents) >= 4:
            search_depth = 4
        else:
            search_depth = self.minimax_search_depth

        tree_tracker[search_depth].append(0)
        _, best_move, _ = self.minimax(depth=search_depth, alpha=-np.inf, beta=np.inf, maximising_snake=True)

        # Output a visualisation of the minimax decision tree for debugging
        if self.debugging:
            import networkx as nx
            G = nx.Graph()
            node_labels = {}
            for node in tree_nodes:
                G.add_node(node[0])
                node_labels[node[0]] = node[1]
            G.add_node(0)
            node_labels[0] = self.display_board(return_string=True)
            G.add_edges_from(tree_edges)
            pos = hierarchy_pos(G, 0)
            edge_colours = [G[u][v]["colour"] for u, v in G.edges()]
            edge_widths = [G[u][v]["width"] for u, v in G.edges()]

            fig = plt.figure(figsize=(50, 25))
            nx.draw(G, pos=pos, node_color=["white"] * G.number_of_nodes(), edge_color=edge_colours, width=edge_widths,
                    labels=node_labels, with_labels=True, node_size=40000, font_size=20)
            plt.savefig("minimax_tree.png", bbox_inches="tight", pad_inches=0)

        return best_move