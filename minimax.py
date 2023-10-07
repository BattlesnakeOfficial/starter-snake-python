import itertools
import numpy as np
import time
from helper_functions import look_ahead, simulate_move, calc_manhattan_distance, flood_fill

global counter
counter = 0


class Battlesnake:
    def __init__(self, game_state):
        self.game_state = game_state
        self.board_width = game_state["board"]["width"]
        self.board_height = game_state["board"]["height"]
        self.all_snakes = game_state["board"]["snakes"]
        self.food = game_state["board"]["food"]
        self.hazards = game_state["board"]["hazards"]
        self.board = np.empty((self.board_width, self.board_height), dtype="<U10")
        # Our snake's data
        self.my_id = game_state["you"]["id"]
        self.my_head = game_state["you"]["head"]
        self.my_neck = game_state["you"]["body"][1]
        self.my_body = game_state["you"]["body"]
        self.my_length = game_state["you"]["length"]
        self.my_health = game_state["you"]["health"]
        # Opponent snakes
        self.opponents = []
        for opponent in game_state["board"]["snakes"]:
            if opponent["id"] == self.my_id:  # Ignore yourself
                continue
            self.opponents.append(opponent)

        self.initialise_board()

    def initialise_board(self, risk_averse=True):
        """Fill in the board with the locations of all snakes. Our snake will be displayed like "oo£" where "o"
        represents the body and "£" represents the head. Opponents will be displayed as "xx£" in the same manner"""
        self.board.fill(".")
        for num, my_square in enumerate(self.my_body):
            self.board[my_square["x"], my_square["y"]] = "£" if num == 0 else "o"
        for opponent in self.opponents:
            snake_body = opponent["body"]
            for num, snake_sq in enumerate(snake_body):
                self.board[snake_sq["x"], snake_sq["y"]] = "$" if num == 0 else "x"
            # To avoid head-to-head collisions, mark off any potential squares the opponents can move to
            # Only if the opponent snake is longer though
            if risk_averse and self.my_length < opponent["length"]:
                opponent_head = opponent["head"]
                opponent_moves = [look_ahead(opponent_head, move) for move in ["up", "down", "left", "right"]]
                for m in opponent_moves:
                    if (0 <= m["x"] < self.board_width and 0 <= m["y"] < self.board_height
                            and self.board[m["x"], m["y"]] not in ["o", "x", "£", "$"]):  # Set empty squares
                        self.board[m["x"], m["y"]] = "?"

    def display_board(self):
        """Print out a nicely formatted board for convenient debugging"""
        for j in range(1, self.board_height + 1):
            for i in range(0, self.board_height):
                print('{}|'.format(self.board[i][-j]), end=" ")
            print()
        print()

    def get_obvious_moves(self, game_state=None, snake_id=None, head=None, neck=None, risk_averse=True,
                          allow_suicide=False):
        """Return a list of valid moves for a hypothetical position. If risk_averse is True, avoid any moves that may
        potentially cause a collision (but only if our snake is shorter)

        Use cases:
        - self.get_obvious_moves() will return moves for your own snake for the current board
        - self.get_obvious_moves(game_state) will return moves for your own snake for a custom board position
        - self.get_obvious_moves(game_state, snake_id) will return moves for any opponent snake
        - self.get_obvious_moves(game_state, head, neck) will return moves for a hypothetical snake
        - self.get_obvious_moves(risk_averse=True) will return possible moves that avoid death-inducing collisions
        - self.get_obvious_moves(allow_suicide=True) will return all possible moves, even ones that end up in death
        """
        clock_in = time.time_ns()
        # Just if you want to simulate moves for a different game state
        input_game = game_state if game_state is not None else self.game_state
        if snake_id is None:
            snake_id = input_game["you"]["id"]
        if head is None:
            head = [snake for snake in self.all_snakes if snake["id"] == snake_id][0]["head"]
        if neck is None:
            neck = [snake for snake in self.all_snakes if snake["id"] == snake_id][0]["body"][1]

        # Initialise a set of possible moves
        possible_moves = {"up", "down", "left", "right"}

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
        if not allow_suicide:  # Unless the snake is willing to die
            for opp_snake in self.all_snakes:
                for move in possible_moves.copy():  # Remaining moves
                    # If the potential move hits a snake's body, it's invalid (but not the tail since it moves forward)
                    if look_ahead(head, move) in opp_snake["body"][:-1]:
                        possible_moves.discard(move)
                    # Avoid possible collisions with any future moves an opponent snake can make
                    if risk_averse:
                        snake_length = [snake for snake in self.all_snakes if snake["id"] == snake_id][0]["length"]
                        # Only if the snake in question is shorter
                        if opp_snake["id"] != snake_id and snake_length < opp_snake["length"]:
                            opp_moves = [look_ahead(opp_snake["head"], move2) for move2 in ["up", "down", "left", "right"]]
                            if look_ahead(head, move) in opp_moves:
                                possible_moves.discard(move)

        print(f"Identified obvious moves {list(possible_moves)} in {(time.time_ns() - clock_in) // 1000000} ms")
        return list(possible_moves)

    def minimax_move(self, risk_averse=True):
        # Compute the best score of each move using the minimax algorithm with alpha-beta pruning
        minimax_score, best_move = self.minimax(self.game_state, depth=3, alpha=-np.inf, beta=np.inf, maximising_snake=True)
        return best_move

    def is_game_over(self, game_state=None, maximising_snake=True):
        """Return True if our snake won or lost, False otherwise"""
        # Just if you want to simulate moves for a different game state
        input_game = game_state if game_state is not None else self.game_state
        all_snakes = input_game["board"]["snakes"]
        if maximising_snake:  # This means it's our turn
            snake_heads = [input_game["you"]["head"]]
            snake_lengths = [input_game["you"]["length"]]
            snake_ids = [self.my_id]
        else:  # Opponent's turn
            snake_heads = [snake["head"] for snake in all_snakes if snake["id"] != self.my_id]
            snake_lengths = [snake["length"] for snake in all_snakes if snake["id"] != self.my_id]
            snake_ids = [snake["id"] for snake in all_snakes if snake["id"] != self.my_id]

        snakes_alive = [True] * len(snake_heads)  # Initialise a boolean list for each snake
        for i in range(len(snake_heads)):
            coords = snake_heads[i]
            # Prevent snake from moving out of bounds
            if coords["x"] < 0 or coords["x"] >= self.board_height:
                snakes_alive[i] = False
            if coords["y"] < 0 or coords["y"] >= self.board_width:
                snakes_alive[i] = False

            # Prevent snake from colliding with other snakes
            for opp_snake in all_snakes:
                if opp_snake["id"] != snake_ids[i]:
                    # If the potential move hits a snake's body, it's invalid
                    if coords in opp_snake["body"][1:]:
                        snakes_alive[i] = False
                    # If the potential move hits a snake's head, it's invalid only if it's shorter
                    if coords == opp_snake["body"][0] and snake_lengths[i] <= opp_snake["length"]:
                        snakes_alive[i] = False

        return True if sum(snakes_alive) == 0 else False

    def heuristic(self, game_state):
        return flood_fill(game_state, risk_averse=True)

    def store_board_positions(self, game_state):
        """Things get confusing when we're simulating snake positions over and over. Making shallow copies of game_state
        variables to simulate a new position causes a loss of information in the original board, and making deep copies
        adds too much to the runtime.

        Solution: this function can keep a temporary copy of all the positions of all snakes and can be re-inserted into
        the game_state variable at any point to "restore" the original board."""
        # Grab our position
        copy_our_pos = game_state["you"]["body"].copy()

        # Grab opponents' positions
        # We need the index of each opponent snake in the game_state's "snakes" field for later use
        num_snakes = len(game_state["board"]["snakes"])
        copy_opps_bodies = [game_state["board"]["snakes"][index]["body"] for index in range(num_snakes)]
        copy_opps_pos = {index: copy_opps_bodies[index] for index in range(num_snakes)}
        return {"you": copy_our_pos, "snakes": copy_opps_pos}

    @staticmethod
    def restore_board_positions(game_state, snake_position_dict):
        """Goes hand-in-hand with the store_board_position function"""
        # Restore our positions
        copy_our_pos = snake_position_dict["you"]
        game_state["you"]["body"] = copy_our_pos
        game_state["you"]["head"] = copy_our_pos[0]
        game_state["you"]["length"] = len(copy_our_pos)

        # Replace all other snakes' positions
        copy_opps_pos = snake_position_dict["snakes"]
        for index, body in copy_opps_pos.items():
            game_state["board"]["snakes"][index]["body"] = copy_opps_pos[index]
            game_state["board"]["snakes"][index]["head"] = copy_opps_pos[index][0]
            game_state["board"]["snakes"][index]["length"] = len(copy_opps_pos[index])
        return game_state

    def minimax(self, game_state, depth, alpha, beta, maximising_snake):
        """Implement the minimax algorithm with alpha-beta pruning

        :param game_state: A fresh copy of the game state dictionary (not from self.game_state in case we need to
        simulate different situations)
        :param depth:
        :param alpha:
        :param beta:
        :param maximising_snake:
        :return:
        """
        global counter
        counter += 1

        # At the bottom of the decision tree or if we won/lost the game
        if self.is_game_over(game_state, maximising_snake):
            print("=" * 50)
            print(f"Heuristic = -100 at terminal node of depth = {depth}")
            return -100, None
        if depth == 0:
            heur = self.heuristic(game_state)
            print("=" * 50)
            print(f"Heuristic = {heur} at terminal node of depth = {depth}")
            return heur, None

        # Our snake's turn
        if maximising_snake:
            clock_in = time.time_ns()
            print("=" * 50)
            print(f"DEPTH == {depth} OUR SNAKE")
            possible_moves = self.get_obvious_moves(game_state, risk_averse=False)
            best_val, best_move = -np.inf, None

            # Store the positions of all snakes before making any board simulations
            stored_snake_positions = self.store_board_positions(game_state)

            for num, move in enumerate(possible_moves):
                # Restore game state after the first simulation
                if num > 0:
                    game_state = self.restore_board_positions(game_state, stored_snake_positions)

                sim_game_state = simulate_move(game_state, move, self.my_id)
                clock_in2 = time.time_ns()
                print(f"Running Minimax for OUR SNAKE'S move {move} at depth = {depth} at counter = {counter}")
                node_val, node_move = self.minimax(sim_game_state, depth - 1, alpha, beta, False)

                # Update best score and best move
                if np.argmax([best_val, node_val]) == 1:
                    best_move = node_move if node_move is not None else move  # None when it's a terminal node
                best_val = max(best_val, node_val)

                print("=" * 50)
                print(f"BACK AT DEPTH = {depth}")
                print(f"Heuristic = {best_val} and best move = {best_move} at our node at depth = {depth - 1} in {(time.time_ns() - clock_in2) // 1000000} ms")

                # Check to see if we can prune
                alpha = max(alpha, best_val)
                if alpha >= beta:
                    print("PRUNED!!!")
                    break

            print(f"Minimax on our snake in {(time.time_ns() - clock_in) // 1000000} ms")
            return best_val, best_move

        # Opponent snakes' turns
        else:
            clock_in = time.time_ns()
            print("=" * 50)
            print(f"DEPTH == {depth} OPPONENT SNAKES")

            # Grab possible moves for all opponent snakes
            all_opps_ids = []
            all_opps_moves = []  # Going to be a list of lists
            for opp_snake in self.opponents:
                opp_id = opp_snake["id"]
                # But only within a reasonable distance of our own snake
                if calc_manhattan_distance(self.my_head, opp_snake["head"]) < self.board_width // 2:
                    all_opps_moves.append(self.get_obvious_moves(game_state, snake_id=opp_id, allow_suicide=True))
                    all_opps_ids.append(opp_id)
            print(f"{len(all_opps_ids)} OPPONENT SNAKES within {self.board_width // 2} of us in {(time.time_ns() - clock_in) // 1000000} ms")

            # Store the positions of all snakes before making any board simulations
            stored_snake_positions = self.store_board_positions(game_state)

            clock_in = time.time_ns()
            possible_sim_states = []
            possible_movesets = []
            # Get all possible boards by simulating moves for each opponent snake, one at a time
            all_opp_combos = list(itertools.product(*all_opps_moves))
            for num, move_combo in enumerate(all_opp_combos):
                # Restore game state after the first simulation
                if num > 0:
                    game_state = self.restore_board_positions(game_state, stored_snake_positions)

                sim_game_state = game_state.copy()
                for snake_num, move in enumerate(move_combo):
                    sim_game_state = simulate_move(sim_game_state, move, all_opps_ids[snake_num])
                possible_sim_states.append(self.store_board_positions(sim_game_state))
                possible_movesets.append(move_combo)
            print(f"{len(possible_sim_states)} POSSIBLE SIMULATED BOARDS OF OPPONENT MOVES in {(time.time_ns() - clock_in) // 1000000} ms")

            best_val, best_move = np.inf, None
            game_state = self.restore_board_positions(game_state, stored_snake_positions)
            for num, stored_sim in enumerate(possible_sim_states):
                clock_in2 = time.time_ns()
                sim_state = self.restore_board_positions(game_state, stored_sim)
                print(f"TESTING {possible_movesets[num]}")
                Battlesnake(sim_state).display_board()
                print(f"Running Minimax for OPPONENT SNAKES' moves at depth = {depth} at counter = {counter}")
                node_val, node_move = self.minimax(sim_state, depth - 1, alpha, beta, True)

                # Update best score and best move
                best_val = min(best_val, node_val)
                if np.argmin([best_val, node_val]) == 1:
                    best_move = node_move if node_move is not None else possible_movesets[num]

                print("=" * 50)
                print(f"BACK AT DEPTH = {depth}")
                print(f"Heuristic = {best_val} and best move = {best_move} at opponents' node at depth = {depth - 1} in {(time.time_ns() - clock_in2) // 1000000} ms")

                # Check to see if we can prune
                beta = min(beta, best_val)
                if beta <= alpha:
                    print("PRUNED!!!")
                    break

            print(f"Minimax on opponents took {(time.time_ns() - clock_in) // 1000000} ms")
            return best_val, best_move