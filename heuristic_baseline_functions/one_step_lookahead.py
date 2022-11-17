import itertools
import copy
from state_reward import state_reward
from state_value import state_value_deterministic
from state_generator import next_state_for_action


def sample_best_minmax_action(game_state, rewards):
  actions = ['up', 'down', 'left', 'right']
  action_values = {}
  for action in actions:
    possible_states = generate_possible_states(game_state, action, rewards)
    action_values[action] = min(possible_states)

  return action_values

def generate_possible_states(game_state, my_action, rewards):
  actions = ['up', 'down', 'left', 'right']
  possible_states = []
  move_combinations = itertools.combinations_with_replacement(
    actions,
    len(game_state['snake_heads'])-1)
  my_next_state = next_state_for_action(game_state, 0, my_action)
  for move_combination in move_combinations:
      next_state = my_next_state
      for snake_index, move in enumerate(
          move_combination):
        next_state = next_state_for_action(next_state, snake_index+1,
                                           move)
      possible_states.append(state_value_deterministic(next_state, rewards))
  return possible_states