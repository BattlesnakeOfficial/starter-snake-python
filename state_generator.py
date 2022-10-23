import copy


def next_state_for_action(game_state, snake_index, action):

    game_state = copy.deepcopy(game_state)
    head = game_state['snake_heads'][snake_index]
    food = game_state['food']
    # move the head
    if action == 'up':
        next_position = (head[0], (head[1] + 1) % game_state['height'])
    if action == 'down':
        next_position = (head[0], (head[1] - 1) % game_state['height'])
    if action == 'left':
        next_position = ((head[0] - 1) % game_state['width'], head[1])
    if action == 'right':
        next_position = ((head[0] + 1) % game_state['width'], head[1])

    ate_food = False
    if next_position in food:
        ate_food = True
        game_state['snake_lengths'][snake_index] += 1
        # TODO: check rules for health
        game_state['snake_healths'][snake_index] = 100

    # add head to body
    game_state['snake_bodies'][snake_index].insert(0, head)
    # move head to the next position
    game_state['snake_heads'][snake_index] = next_position
    # remove the tail if the snake did not eat food
    if not ate_food:
        game_state['snake_bodies'][snake_index].pop(-1)

    #dead = False
    #snake_bodies = []
    #for snake in range(len(game_state['snake_heads'])):
    #    snake_bodies += game_state['snake_bodies'][snake]
    #
    #if next_position in game_state['hazards'] or next_position in snake_bodies:
    #    dead = True
    #
    #for opponent in range(len(game_state['snake_heads'])):
    #    if opponent != snake_index:
    #        if next_position == game_state['snake_heads'][opponent] and game_state['snake_lengths'][snake_index] <= game_state['snake_lengths'][opponent]:
    #            dead = True
#
    ## check if the snake died
    #if dead:
    #    # erase snake from the board
    #    game_state['snake_heads'].pop(snake_index)
    #    game_state['snake_bodies'].pop(snake_index)
    #    game_state['snake_lengths'].pop(snake_index)
    #    game_state['snake_healths'].pop(snake_index)


    return game_state


def transform_state(game_state):
    # transform game state to a flatter format
    transformed_state = {}
    transformed_state['height'] = game_state['board']['height']
    transformed_state['width'] = game_state['board']['width']
    transformed_state['food'] = set()
    for food in game_state['board']['food']:
        transformed_state['food'].add((food['x'], food['y']))
    transformed_state['hazards'] = set()
    for hazard in game_state['board']['hazards']:
        transformed_state['hazards'].add((hazard['x'], hazard['y']))
    transformed_state['snake_heads'] = []
    transformed_state['snake_bodies'] = []
    transformed_state['snake_lengths'] = []
    transformed_state['snake_healths'] = []
    # I am always the snake at index 0
    transformed_state['snake_heads'].append(
        (game_state['you']['head']['x'], game_state['you']['head']['y']))
    transformed_state['snake_bodies'].append([])
    # do not append head to body
    for body in game_state['you']['body'][1:]:
        transformed_state['snake_bodies'][0].append((body['x'], body['y']))
    transformed_state['snake_lengths'].append(game_state['you']['length'])
    transformed_state['snake_healths'].append(game_state['you']['health'])
    # Other snakes
    for snake in game_state['board']['snakes']:
        if snake['id'] != game_state['you']['id']:
            transformed_state['snake_heads'].append(
                (snake['head']['x'], snake['head']['y']))
            transformed_state['snake_bodies'].append([])
            # do not append head to body
            for body in snake['body'][1:]:
                transformed_state['snake_bodies'][-1].append(
                    (body['x'], body['y']))
            transformed_state['snake_lengths'].append(snake['length'])
            transformed_state['snake_healths'].append(snake['health'])
    return transformed_state

