import random

class Move():

    def __init__(self):

        self.is_move_safe = {"up": {"is_safe": True}, 
                             "down": {"is_safe": True}, 
                             "left": {"is_safe": True}, 
                             "right": {"is_safe": True}}

    def not_backward(self, game_state):

        # We've included code to prevent your Battlesnake from moving backwards
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

        if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
            self.is_move_safe["left"]["is_safe"] = False

        elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
            self.is_move_safe["right"]["is_safe"] = False

        elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
            self.is_move_safe["down"]["is_safe"] = False

        elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
            self.is_move_safe["up"]["is_safe"] = False  

    def choose_move(self, game_state):

        self.not_backward(game_state)
        
        # Are there any safe moves left?
        safe_moves = []
        for move , data in self.is_move_safe.items():

            if data["is_safe"] == True:

                safe_moves.append(move)  

        if len(safe_moves) == 0:
            print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
            return {"move": "down"}
        
        # Choose a random move from the safe ones 
        next_move = random.choice(safe_moves)
            
        return {"move": next_move}

# TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
# board_width = game_state['board']['width']
# board_height = game_state['board']['height']
    
# TODO: Step 2 - Prevent your Battlesnake from colliding with itself
# my_body = game_state['you']['body']

# TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
# opponents = game_state['board']['snakes']

# TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
# food = game_state['board']['food']