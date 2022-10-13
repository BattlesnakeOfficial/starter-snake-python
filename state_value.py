import random
import typing

def state_value(game_state: typing.Dict) -> typing.Dict:
    state_value += death_value(game_state)
    state_value += head_collision_value(game_state)
    return state_value




def death_value(game_state: typing.Dict):
    value = 0
    # subtract 100 if death by hunger
    if game_state['you']['health'] == 0:
        value -= 100

    # subtract 100 if death by collision with a wall
    my_head = (game_state['you']['head']['x'], game_state['you']['head']['y'])
    hazards = [(x,y) for x,y in game_state['board']['hazards'].items()]
    if my_head in hazards:
        value -= 100

    # subtract 100 if death by collision with a snake body
    snake_bodies = []
    for snake in game_state['board']['snakes']:
        snake_bodies.append([(x,y) for x,y in snake['body'].items()[1:]])
    if my_head in snake_bodies:
        value -= 100
    
    return value

def head_collision_value(game_state: typing.Dict):
    value = 0
    my_head = (game_state['you']['head']['x'], game_state['you']['head']['y'])
    my_length = game_state['you']['length']
    for snake in game_state['board']['snakes']:
        if snake["id"] != game_state['you']['id']:
            snake_head = (snake['head']['x'], snake['head']['y'])
            if (snake_head) == my_head:
                # collision with a bigger snake head
                if snake['length'] >= my_length:
                    value -= 100
                # collision with a smaller snake head
                else:
                    value += 50
    return value


