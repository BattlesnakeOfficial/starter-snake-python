import random
import typing


def state_reward(game_state: typing.Dict, rewards: typing.Dict) -> typing.Dict:
    state_reward = 0
    state_reward += death_reward(game_state, rewards)
    state_reward += head_collision_reward(game_state, rewards)
    return state_reward


def death_reward(game_state: typing.Dict, rewards: typing.Dict):
    dead = False
    # death by hunger
    if game_state['you']['health'] == 0:
        dead = True

    # death by collision with a wall
    my_head = (game_state['you']['head']['x'], game_state['you']['head']['y'])
    hazards = []
    for hazard in game_state['board']['hazards']:
        hazards.append((hazard['x'], hazard['y']))
    if my_head in hazards:
        dead = True

    # death by collision with a snake body
    snake_bodies = {}
    for snake in game_state['board']['snakes']:
        snake_bodies[snake['id']] = []
        for body in snake['body']:
            snake_bodies[snake['id']].append((body['x'], body['y']))
        # pop the heads
        snake_bodies[snake['id']].pop(0)
    
    for snake_id, snake_body in snake_bodies.items():
        if my_head in snake_body:
            dead = True

    if dead:
        return rewards['death']
    else:
        return 0


def head_collision_reward(game_state: typing.Dict, rewards: typing.Dict):
    reward = 0
    my_head = (game_state['you']['head']['x'], game_state['you']['head']['y'])
    my_length = game_state['you']['length']
    for snake in game_state['board']['snakes']:
        if snake["id"] != game_state['you']['id']:
            snake_head = (snake['head']['x'], snake['head']['y'])
            if (snake_head) == my_head:
                # collision with a bigger snake head
                if snake['length'] >= my_length:
                    reward += rewards['death']
                # collision with a smaller snake head
                else:
                    reward += rewards['opponent_death']
    return reward
