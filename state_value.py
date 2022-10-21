from state_reward import state_reward


def state_value_deterministic(state, rewards):
    # state_value is the expected reward for a state
    # just return the expected reward for the current state (no lookahead)
    return state_reward(state, rewards)