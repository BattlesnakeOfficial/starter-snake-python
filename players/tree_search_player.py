import random
from tree_search import sample_best_minmax_action
from state_generator import next_state_for_action, transform_state
from state_reward import state_reward


class TreeSearchPlayer():

  def __init__(self):
    self.rewards = {
      'death': -1000,
      'death_by_head_collision': -700,
      'opponent_death': 100,
      'distance_to_food_when_hungry': -5,
      'distance_to_food_when_small': -1,
      'board_domination': 2
    }

  def info(self):
    return {
      "apiversion": "1",
      "author": "Barbora",
      "color": "#3352FF",
      "head": "default",  # TODO: Choose head
      "tail": "default",  # TODO: Choose tail
    }

  def move(self, game_state):
    # move is called on every turn and returns your next move
    # Valid moves are "up", "down", "left", or "right"

    print('turn ', game_state['turn'])
    game_state = transform_state(game_state)
    print(game_state)
    action_values = sample_best_minmax_action(game_state, self.rewards)

    next_move = sorted(action_values, key=action_values.get, reverse=True)[0]
    #print(action_values, next_move)

    return {"move": next_move}
