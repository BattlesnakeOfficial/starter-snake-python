from state_reward import state_reward
from state_value import state_value_deterministic
from state_generator import next_state_for_action


def sample_best_minmax_action(game_state, rewards):
    # returns 
    # for the current game state
    actions = ['up', 'down', 'left', 'right']
    action_values = {}
    # my actions
    for action in actions:
        state_values = []
        next_state = next_state_for_action(game_state, 0, action)
        for snake_index in range(1, len(game_state['snake_heads'])):
            for opponent_action in actions:
                next_state = next_state_for_action(
                    next_state, snake_index, opponent_action)
                state_values.append(state_value_deterministic(next_state, rewards))
        action_values[action] = min(state_values)
    return action_values