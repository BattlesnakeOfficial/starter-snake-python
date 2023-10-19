import copy
import itertools
import logging
import operator
import os
import numpy as np
import sys
import time
from collections import Counter
from networkx_tree import hierarchy_pos
from matplotlib import colors, image as mpimg, pyplot as plt

tree_tracker = {4: [], 3: [], 2: [], 1: [], 0: []}
tree_edges = []
tree_nodes = []
tree_node_counter = 1


class Battlesnake:
    def __init__(self, game_state, debugging=False):
        # General game data
        self.turn = game_state["turn"]
        self.board_width = game_state["board"]["width"]
        self.board_height = game_state["board"]["height"]
        self.food = game_state["board"]["food"]
        self.hazards = game_state["board"]["hazards"]
        self.board = np.full((self.board_width, self.board_height), " ")

        # Our snake's data
        self.my_id = game_state["you"]["id"]
        self.my_head = game_state["you"]["head"]
        self.my_neck = game_state["you"]["body"][1]
        self.my_body = game_state["you"]["body"]
        self.my_length = game_state["you"]["length"]
        self.my_health = game_state["you"]["health"]

        # Read snake positions as a dictionary of dictionaries (easier to access than list of dicts)
        self.all_snakes_dict = {}
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
            if ("name" in game_state["you"] and game_state["you"]["name"] != "Nightwing"
                    and snake["name"] == "Nightwing"):
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
        self.minimax_search_depth = 4
        self.peripheral_dim = 3
        self.debugging = debugging
        logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
        if not self.debugging:
            logging.disable(logging.INFO)

    def __copy__(self):
        """Making a deep copy of the game_state dictionary takes too much time, so let's manually build it from
        scratch. That way, we can modify a copied instance of the class without affecting the original instance."""
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
        """Fill in the board with the locations of all snakes. Our snake will be displayed like "oo£" where "o"
        represents the body and "£" represents the head. Opponents will be displayed as "xx£" in the same manner"""
        self.board = np.full((self.board_width, self.board_height), " ")
        for num, my_square in enumerate(self.my_body):
            self.board[my_square["x"], my_square["y"]] = "£" if num == 0 else "O"
        for opponent in self.opponents.values():
            snake_body = opponent["body"]
            for num, snake_sq in enumerate(snake_body):
                self.board[snake_sq["x"], snake_sq["y"]] = "$" if num == 0 else "X"

    def display_board(self, board=None, return_string=False):
        """Print out a nicely formatted board for convenient debugging"""
        render_board = board if board is not None else self.board
        for j in range(1, len(render_board[0]) + 1):
            display_row = ""
            for i in range(0, len(render_board)):
                display_row += f"{render_board[i][-j]}| "
            logging.info(display_row)

        # Do you want to return the board as a string instead of printing it out?
        if return_string:
            board_str = ""
            for j in range(1, len(render_board[0]) + 1):
                display_row = ""
                for i in range(0, len(render_board)):
                    display_row += f"{render_board[i][-j]}| "
                board_str += display_row + "\n"
            return board_str

    @staticmethod
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

    @staticmethod
    def manhattan_distance(start, end):
        """Return the Manhattan distance for two positions"""
        start = (start["x"], start["y"])
        end = (end["x"], end["y"])
        return sum(abs(value1 - value2) for value1, value2 in zip(start, end))

    def our_direction(self, snake_id):
        head = self.all_snakes_dict[snake_id]["head"]
        neck = self.all_snakes_dict[snake_id]["neck"]
        if neck["x"] < head["x"]:
            direction = "right"
        elif neck["x"] > head["x"]:
            direction = "left"
        elif neck["y"] < head["y"]:
            direction = "up"
        elif neck["y"] > head["y"]:
            direction = "down"
        else:
            direction = None
        return direction

    def peripheral_vision(self, snake_id, direction):
        """Return [x1, x2] and [y1, y2] of a portion of the board that functions as 'peripheral vision' for the snake"""
        # Our peripheral field of vision when scanning for moves
        head = self.all_snakes_dict[snake_id]["head"].copy()
        neck = self.all_snakes_dict[snake_id]["neck"].copy()
        dim = self.peripheral_dim

        if direction == "auto":  # Got to figure out the direction ourselves
            direction = self.our_direction(snake_id)
            head = neck.copy()  # Roll back our head location

        if direction == "right":  # Neck is left of head, don't move left
            peripheral_box_x = head["x"] + 1, min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = 0, head["y"] - peripheral_box_y[0]
        elif direction == "left":  # Neck is right of head, don't move right
            peripheral_box_x = max(head["x"] - dim, 0), head["x"]
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = max(head["x"] - peripheral_box_x[0] - 1, 0), head["y"] - peripheral_box_y[0]
        elif direction == "up":  # Neck is below head, don't move down
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = head["y"] + 1, min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], 0
        elif direction == "down":  # Neck is above head, don't move up
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), head["y"]
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], max(head["y"] - peripheral_box_y[0] - 1, 0)
        else:  # Centred around our snake's head
            peripheral_box_x = max(head["x"] - dim, 0), min(head["x"] + dim + 1, self.board_width)
            peripheral_box_y = max(head["y"] - dim, 0), min(head["y"] + dim + 1, self.board_height)
            head["x"], head["y"] = head["x"] - peripheral_box_x[0], head["y"] - peripheral_box_y[0]

        return peripheral_box_x, peripheral_box_y, head

    def get_obvious_moves(self, snake_id, risk_averse=True, sort_by_dist_to=None, sort_by_peripheral=False):
        """Return a list of valid moves for any hypothetical snake. If risk_averse is True, avoid any moves that may
        potentially cause a collision (but only if the snake is shorter)

        Use cases:
        - self.get_obvious_moves(snake_id) will return moves for any opponent snake for the current board
        - self.get_obvious_moves(risk_averse=True) will return possible moves that avoid death-inducing collisions with
        our snake. Set False to assume our opponents are out to get us (paranoid minimax)
        - self.get_obvious_moves(sort_by_dist_to=snake["id"]) will return all possible moves, but sorted by the distance
        from our snake post-move to the head of the snake whose ID is given as the parameter input
        - self.get_obvious_moves(sort_by_peripheral=True) will return all possible moves, but sorted by the amount of
        space that each move is estimated to give us in our "peripheral vision"
        """
        risky_moves = []  # Initialise a set of possible risky moves
        possible_moves = {"up", "down", "left", "right"}  # Initialise a set of possible moves

        head = self.all_snakes_dict[snake_id]["head"]
        neck = self.all_snakes_dict[snake_id]["neck"]
        length = self.all_snakes_dict[snake_id]["length"]

        clock_in = time.time_ns()
        if neck["x"] < head["x"]:  # Neck is left of head, don't move left
            possible_moves.discard("left")
        elif neck["x"] > head["x"]:  # Neck is right of head, don't move right
            possible_moves.discard("right")
        elif neck["y"] < head["y"]:  # Neck is below head, don't move down
            possible_moves.discard("down")
        elif neck["y"] > head["y"]:  # Neck is above head, don't move up
            possible_moves.discard("up")

        # Prevent snake from moving out of bounds
        if head["x"] == 0:
            possible_moves.discard("left")
        if head["x"] + 1 == self.board_height:
            possible_moves.discard("right")
        if head["y"] == 0:
            possible_moves.discard("down")
        if head["y"] + 1 == self.board_width:
            possible_moves.discard("up")

        # Prevent snake from colliding with other snakes
        for opp_snake_id, opp_snake in self.all_snakes_dict.items():
            for move in possible_moves.copy():  # Remaining moves
                possible_hit = self.look_ahead(head, move)
                # If the potential move hits a snake's body, it's invalid (exclude the tail since it moves forward)
                if snake_id == self.my_id and possible_hit in opp_snake["body"][:-1]:
                    possible_moves.discard(move)
                elif snake_id != self.my_id and possible_hit != self.my_head and (
                        (possible_hit in opp_snake["body"][:-1] and opp_snake_id != self.my_id)
                        or (possible_hit in opp_snake["body"] and opp_snake_id == self.my_id)):
                    possible_moves.discard(move)
                # If the snake is risk-averse, avoid any chance of head-on collisions only if our snake is shorter
                elif snake_id != opp_snake_id and length <= opp_snake["length"] \
                        and self.manhattan_distance(possible_hit, opp_snake["head"]) <= 1:
                    # Allow opponents to be suicidal (so our snakes are the same size)
                    if not (snake_id != self.my_id and opp_snake_id == self.my_id and length == opp_snake["length"]):
                        risky_moves.append(move)
                    if risk_averse:
                        possible_moves.discard(move)

        if sort_by_dist_to is not None:
            head2 = self.all_snakes_dict[sort_by_dist_to]["head"]
            possible_moves = sorted(possible_moves,  # This converts a set to a list anyway
                                    key=lambda move2: self.manhattan_distance(head2, self.look_ahead(head, move2)))
        elif sort_by_peripheral:
            possible_moves = sorted(possible_moves,  # This converts a set to a list anyway
                                    key=lambda move2: self.flood_fill(snake_id, confined_area=move2),
                                    reverse=True)
        else:
            possible_moves = list(possible_moves)

        # De-prioritise any risky moves and send them to the back
        if len(risky_moves) > 0:
            for risky in risky_moves:
                if risky in possible_moves:
                    possible_moves.append(possible_moves.pop(possible_moves.index(risky)))

        logging.info(f"Identified obvious moves {list(possible_moves)} in "
                     f"{round((time.time_ns() - clock_in) / 1000000, 3)} ms")
        return possible_moves

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
            G.add_edges_from(tree_edges)
            pos = hierarchy_pos(G, 0)
            edge_colours = [G[u][v]["colour"] for u, v in G.edges()]
            edge_widths = [G[u][v]["width"] for u, v in G.edges()]

            fig = plt.figure(figsize=(50, 25))
            nx.draw(G, pos=pos, node_color=["white"] * G.number_of_nodes(), edge_color=edge_colours, width=edge_widths,
                    labels=node_labels, with_labels=True, node_size=40000, font_size=20)
            plt.savefig("minimax_tree.png", bbox_inches="tight", pad_inches=0)

        return best_move

    def is_game_over(self, for_snake_id=None, depth=None):
        """Return True if the game ended for our snake, False otherwise. Use for_snake_id to return a boolean for a
        specific snake's status (can be one or multiple)."""
        snake_monitor = {}  # A dictionary for each snake showing whether they're alive
        for snake_id, snake in self.all_snakes_dict.items():
            snake_monitor[snake_id] = True

            head = snake["head"]
            # Prevent snake from moving out of bounds
            if head["x"] < 0 or head["x"] >= self.board_height:
                snake_monitor[snake_id] = False
            if head["y"] < 0 or head["y"] >= self.board_width:
                snake_monitor[snake_id] = False

            # Skip this if we're at the beginning of the game when all snakes are still coiled up
            if not (snake["length"] == 3 and snake["body"][-2] == snake["body"][-1]):
                # Prevent snake from colliding with any other snakes
                for opp_snake_id, opp_snake in self.all_snakes_dict.items():
                    # Depending on the depth, exclude the tail if the turn technically isn't over (all players need to
                    # have made a move)
                    check_body = opp_snake["body"][1:-1] if depth % 2 == 1 else opp_snake["body"][1:]

                    # If the potential move hits a snake's body, it's invalid
                    if head in check_body:
                        snake_monitor[snake_id] = False
                    # If the potential move hits a snake's head, it's invalid only if our snake is shorter
                    if snake_id != opp_snake_id:
                        if head == opp_snake["head"] and snake["length"] <= opp_snake["length"]:
                            snake_monitor[snake_id] = False

        # Game is over if there's only one snake remaining or if our snake died
        game_over = True if (sum(snake_monitor.values()) == 1 or not snake_monitor[self.my_id]) else False

        # See if a specific snake is alive or not
        if isinstance(for_snake_id, (list, tuple)):
            snake_still_alive = [snake_monitor[snake_id] for snake_id in for_snake_id]
        else:
            snake_still_alive = snake_monitor[self.my_id] if for_snake_id is None else snake_monitor[for_snake_id]

        return game_over, snake_still_alive

    def edge_kill_detection(self):
        if 0 < self.my_head["x"] < self.board_width and 0 < self.my_head["y"] < self.board_height:
            return False

        possible_moves = self.get_obvious_moves(self.my_id, risk_averse=True)
        direction = self.our_direction(self.my_id)
        if self.my_head["x"] == 0:
            if "right" not in possible_moves:
                suspect = [opp_id for opp_id, opp in self.opponents.items()
                           if opp["head"]["x"] == self.my_head["x"] + 1 and (
                                   (direction == "up" and opp["head"]["y"] >= self.my_head["y"])
                                   or (direction == "down" and opp["head"]["y"] <= self.my_head["y"])
                           )]
                if len(suspect) > 0:
                    diff_y = min([self.manhattan_distance(self.my_head, self.opponents[opp_id]["head"]) - 1 for opp_id in suspect])
                    gaps = [self.opponents[snake_id]["body"][-diff_y:] for snake_id in suspect]  # Would leave space for us to move to
                    if self.look_ahead(self.my_head, "right") not in list(itertools.chain(*gaps)):
                        return True
        if self.my_head["x"] == self.board_width - 1:
            if "left" not in possible_moves:
                suspect = [opp_id for opp_id, opp in self.opponents.items()
                           if opp["head"]["x"] == self.my_head["x"] - 1 and (
                                   (direction == "up" and opp["head"]["y"] >= self.my_head["y"])
                                   or (direction == "down" and opp["head"]["y"] <= self.my_head["y"])
                           )]
                if len(suspect) > 0:
                    diff_y = min([self.manhattan_distance(self.my_head, self.opponents[opp_id]["head"]) - 1 for opp_id in suspect])
                    gaps = [self.opponents[snake_id]["body"][-diff_y:] for snake_id in suspect]  # Would leave space for us to move to
                    if self.look_ahead(self.my_head, "right") not in list(itertools.chain(*gaps)):
                        return True
        if self.my_head["y"] == 0:
            if "up" not in possible_moves:
                return True
        if self.my_head["y"] == self.board_height - 1:
            if "down" not in possible_moves:
                return True
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
        if available_space < 4:
            space_penalty = -200
        else:
            space_penalty = 0

        # ARE WE TRAPPED???
        trap_space = None
        if available_space <= 10:
            trap_space = available_space - self.flood_fill(self.my_id, estimate_moves=available_space)
        # Shoot we're trapped
        if trap_space == 0:
            space_penalty = -1e7  # We'd prefer getting killed than getting trapped, so penalise this more

        # ARE WE GOING TO GET EDGE-KILLED???
        possible_edged = self.edge_kill_detection()
        if possible_edged:
            space_penalty = -1e5

        # Estimate the space we have in our peripheral vision
        available_peripheral = self.flood_fill(self.my_id, confined_area="auto")

        # # We want to minimise available space for our opponents via flood fill (but only when there are fewer snakes in
        # # our vicinity)
        # if len(self.opponents) <= 3:
        #         # and sum([dist < (self.board_width // 2) for dist in self.dist_from_enemies()]) <= 3 \
        #         # and len(self.opponents) == sum([self.my_length > s["length"] for s in self.opponents.values()]):
        #     self.peripheral_dim = 4
        #     available_enemy_space = self.flood_fill(self.closest_enemy(), confined_area="General")
        # else:
        #     available_enemy_space = 0

        # Get closer to enemy snakes if we're longer by 3
        if 2 >= len(self.opponents) == sum([self.my_length > s["length"] + 3 for s in self.opponents.values()]):
            dist_to_enemy = self.dist_from_enemies()[0]
        else:
            dist_to_enemy = 0

        # If we're getting too close to enemy snakes that are longer, RETREAT
        threats = [self.manhattan_distance(self.my_head, opp["head"]) for opp in self.opponents.values() if opp["length"] >= self.my_length]
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
        # logging.info(f"Available enemy space: {available_enemy_space}")
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
            aggression_weight / (dist_to_enemy + 1)
# (enemy_restriction_weight / (available_enemy_space + 1)) + \

        return h, {"Heur": round(h, 2),
                   "Space": available_space,
                   "Penalty": space_penalty,
                   "Periph": available_peripheral,
                   "Food Dist": dist_food,
                   "Enemy Dist": dist_to_enemy,
                   "Threats": num_threats,
                   "Length": self.my_length}

    def flood_fill(self, snake_id, confined_area=None, risk_averse=False, estimate_moves=0):
        """Recursive function to get the total area of the current fill selection. Basically, count how many £ symbols
        we can fill while avoiding any $, O, and X symbols (obstacles). Confined_area tells the function to do flood
        fill only on one side of the snake (should be either left/right/up/down)."""
        head = self.all_snakes_dict[snake_id]["head"]

        # Assume we're doing flood fill for our snake
        if snake_id == self.my_id:
            board = copy.deepcopy(self.board)
            # Let's simulate entrapment
            if estimate_moves > 0:
                for snake in self.all_snakes_dict.values():
                    tail_removed = snake["body"][-estimate_moves:]
                    for remove in tail_removed:
                        board[remove["x"]][remove["y"]] = " "
            # Let's try to avoid any squares that our enemy can go to
            if risk_averse:
                threats = [other["head"] for other in self.opponents.values() if other["length"] >= self.my_length]
                for threat in threats:
                    x, y = threat["x"], threat["y"]
                    avoid_sq = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    for n in avoid_sq:
                        if not (n[0] == head["x"] and n[1] == head["y"]) and \
                                (0 <= n[0] < self.board_width and 0 <= n[1] < self.board_height):
                            board[n[0]][n[1]] = "X"
        # Otherwise, generate a new board and pretend the opponent snake is our snake (in order to compute flood fill)
        else:
            board = np.full((self.board_width, self.board_height), " ")
            for num, square in enumerate(self.all_snakes_dict[snake_id]["body"]):
                board[square["x"], square["y"]] = "£" if num == 0 else "O"
            for other_id, other_snake in self.all_snakes_dict.items():
                if other_id != snake_id:
                    for num, other_square in enumerate(other_snake["body"]):
                        board[other_square["x"], other_square["y"]] = "$" if num == 0 else "X"

        if confined_area is not None:
            xs, ys, head = self.peripheral_vision(snake_id, confined_area)
            board = board[xs[0]:xs[1], ys[0]:ys[1]]
            # if -1 == head["x"]:
            #     self.peripheral_vision(snake_id, confined_area)

        def fill(x, y, board, initial_square):
            if board[x][y] in ["X", "$"]:  # Snakes or hazards
                return
            if board[x][y] in ["O"]:  # Us
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
        return filled - 1 if filled > 0 else filled  # Exclude the head, but cannot ever be negative

    def dist_to_nearest_food(self):
        """Return the Manhattan distance to the nearest food for our snake"""
        best_dist = np.inf
        for food in self.food:
            dist = self.manhattan_distance(food, self.my_head)
            dist_enemy = min([self.manhattan_distance(food, snake["head"]) for snake in self.opponents.values()])
            if dist < best_dist and ((dist_enemy >= 4 and dist <= dist_enemy * 2) or (4 > dist_enemy >= dist)):
                best_dist = dist
        return best_dist

    def dist_from_enemies(self):
        """To gauge how in danger we are, return a list of Manhattan distances to all snakes"""
        return sorted([self.manhattan_distance(self.my_head, opp["head"]) for opp in self.opponents.values()])

    def closest_enemy(self):
        """Return the nearest enemy snake"""
        return sorted(self.opponents.keys(),
                      key=lambda opp_id: self.manhattan_distance(self.my_head, self.opponents[opp_id]["head"]))[0]

    def simulate_move(self, move, snake_id, evaluate_deaths=False):
        """Create a new Battlesnake instance with a simulated move for a given snake"""
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

        # Keep track if food was consumed - this elongates the snake from the tail and restores health
        if new_head in self.food:
            new_game.all_snakes_dict[snake_id]["food_eaten"] = new_head

        # Check if any snakes died from this simulated move and remove them from the game
        if evaluate_deaths:
            # Update snake lengths from any food eaten
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

            # Did any snakes die from collisions?
            all_heads = [(snake["head"]["x"], snake["head"]["y"]) for snake in new_game.all_snakes_dict.values()]
            count_heads = Counter(all_heads)
            butt_heads = [k for k, v in count_heads.items() if v > 1]
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
                    if len(indices_largest_snakes) > 1:
                        winner_id = None
                    else:
                        winner_id = overlapping_snakes[:, 0][indices_largest_snakes[0]]

                    for rm_id in overlapping_snakes[:, 0]:
                        if rm_id != winner_id:
                            new_game.all_snakes_dict.pop(rm_id)

        new_game.update_board()
        # logging.info(f"Done with simulation in {round((time.time_ns() - clock_in) / 1000000, 3)} ms")
        return new_game

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
        """Implement the minimax algorithm with alpha-beta pruning

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

            global tree_edges
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
                dist_opp_to_us = self.manhattan_distance(self.my_head, opp_snake["head"])
                if dist_opp_to_us <= search_within:
                    opps_moves[opp_id] = opp_move  # Put all of their moves
                    opps_nearby += 1
                else:
                    if len(self.opponents) <= 5:
                        opps_moves[opp_id] = [opp_move[0]]

            sorted_opps_by_dists = sorted(self.opponents.keys(), key=lambda opp_id: self.manhattan_distance(self.my_head, self.opponents[opp_id]["head"]))
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

#     def a_star_search(self, food_loc):
#         """
#         Implement the A* search algorithm to find the shortest path to food
#         """
#         head_loc = self.my_head.copy()
#         open_list = [Node(head_loc)]  # Contains the nodes that have been generated but have not been yet examined till yet
#         closed_list = []  # Contains the nodes which are examined
#         timer = 0
#
#         while len(open_list) > 0:
#             if timer > 300:
#                 return None, None
#
#             current_node = min(open_list, key=lambda node: node.f)  # The node with the smallest f value
#             open_list.remove(current_node)  # Remove from open list
#
#             if current_node.location == food_loc:  # Found the food! Stop search
#                 traceback = [food_loc]
#                 pointer = current_node
#                 while pointer.parent is not None:
#                     traceback.append(pointer.parent.location)
#                     pointer = pointer.parent
#                 return traceback, current_node.g
#
#             # Identify all possible nodes to move to
#             neighbour_nodes = []
#             possible_moves = self.get_obvious_moves(self.my_id, risk_averse=True)
#
#             for possible_move in possible_moves:
#                 possible_node = Node(self.look_ahead(current_node.location, possible_move), parent=current_node)
#                 neighbour_nodes.append(possible_node)
#
#             for possible_node in neighbour_nodes:  # For each possible new node
#                 if possible_node.location in closed_list:  # Skip if the node is in the closed list
#                     continue
#
#                 # Compute f value for the neighbour node
#                 possible_node.g = current_node.g + 1
#                 possible_node.h = self.manhattan_distance(current_node.location, food_loc)
#                 possible_node.f = possible_node.g + possible_node.h
#
#                 # If the node's location is also in the open list but has a worse g value, ignore since we can do better
#                 for open_node in open_list:
#                     if possible_node.location == open_node.location and possible_node.g > open_node.g:
#                         break
#
#                 # Otherwise, this is the best we can do so far - add to open list
#                 open_list.append(possible_node)
#
#             closed_list.append(current_node.location)  # Add to closed list since we've looked at all neighbours
#             timer += 1
#
#         return None, None
#
#
class Node:
    def __init__(self, location, parent=None, f=0, g=0, h=0):
        self.location = location
        self.neighbour_nodes = []
        self.parent = parent
        self.f = f  # The cost from the start node to the goal node
        self.g = g  # The cost from the start node to the current node
        self.h = h  # The cost from the current node to the goal node using a heuristic

    def __repr__(self):
        return str(self.location)