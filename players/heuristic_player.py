import random
from battlesnake.state_generator import StateGeneraror
from battlesnake.state_reward import state_reward


class HeuristicPlayer():
    def __init__(self):
        self.rewards = {
            'death': -100,
            'opponent_death': 50
        }
    
    def info(self):
        return {
            "apiversion": "1",
            "author": "Barbora",
            "color": "#3352FF",
            "head": "default",  # TODO: Choose head
            "tail": "default",  # TODO: Choose tail
        }

    def get_move_values(self, game_state):
        # value is the immedtae reward for a move
        # does not take other opponents' moves into account
        state_generator = StateGeneraror(game_state)
        moves = ["up", "down", "left", "right"]
        move_value = {}
        for move in moves:
            move_value[move] = state_reward(state_generator.next_state_for_aciton(move), self.rewards)
        
        return move_value

    def move(self, game_state):
        # move is called on every turn and returns your next move
        # Valid moves are "up", "down", "left", or "right"

        move_values = self.get_move_values(game_state)
        best_value = max(move_values.values())
        best_moves = []
        for move, value in move_values.items():
            if value == best_value:
                best_moves.append(move)

        # Choose a random move from the safe ones
        next_move = random.choice(best_moves)

        print(f"MOVE {game_state['turn']}: {next_move}")
        return {"move": next_move}
