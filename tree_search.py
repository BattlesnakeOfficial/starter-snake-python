import itertools
import copy
from state_reward import state_reward
from state_value import state_value_deterministic
from state_generator import next_state_for_action


def sample_best_minmax_action(game_state, rewards):
  # for the current game state
  actions = ['up', 'down', 'left', 'right']
  action_values = {}
  # my actions
  for action in actions:
    state_values = []
    my_next_state = next_state_for_action(game_state, 0, action)
    opponent_move_combinations = itertools.combinations(
      actions,
      len(game_state['snake_heads']) - 1)
    for opponent_move_combination in opponent_move_combinations:
      next_state = copy.deepcopy(my_next_state)
      for opponent_index, opponent_move in enumerate(
          opponent_move_combination):
        next_state = next_state_for_action(next_state, opponent_index+1,
                                           opponent_move)
      state_values.append(state_value_deterministic(next_state, rewards))

    action_values[action] = min(state_values)
  return action_values
