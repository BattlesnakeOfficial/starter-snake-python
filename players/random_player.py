import random
from state_generator import StateGeneraror
from state_reward import state_reward


class RandomPlayer():

  def __init__(self):
    self.rewards = {}

  def info(self):
    return {
      "apiversion": "1",
      "author": "Barbora",
      "color": "#FF33FC",
      "head": "default",  # TODO: Choose head
      "tail": "default",  # TODO: Choose tail
    }

def move(self, game_state):

  is_move_safe = {"up": True, "down": True, "left": True, "right": True}

  # prevent Battlesnake from moving backwards
  my_head = game_state["you"]["body"][0]  # Coordinates of your head
  my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

  if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
    is_move_safe["left"] = False

  elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
    is_move_safe["right"] = False

  elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
    is_move_safe["down"] = False

  elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
    is_move_safe["up"] = False

  # Are there any safe moves left?
  safe_moves = []
  for move, isSafe in is_move_safe.items():
    if isSafe:
      safe_moves.append(move)

  if len(safe_moves) == 0:
    print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
    return {"move": "down"}

  # Choose a random move from the safe ones
  next_move = random.choice(safe_moves)

  print(f"MOVE {game_state['turn']}: {next_move}")
  return {"move": next_move}
