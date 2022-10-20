import random
import typing


def state_reward(game_state: typing.Dict, rewards: typing.Dict) -> typing.Dict:
    state_reward = 0
    state_reward += death_reward(game_state, rewards)
    state_reward += head_collision_reward(game_state, rewards)
    state_reward += food_reward(game_state, rewards)
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


def food_reward(game_state, rewards):
    reward = 0
    nearest_food = bfs_nearest_food(game_state)
    if nearest_food is None:
        return 0
    # if hungry
    if game_state['you']['health'] < 20:
        reward += nearest_food * rewards['distance_to_food_when_hungry']
    # if not bigger than the biggest opponent
    biggest_opponent = 0
    for snake in game_state['board']['snakes']:
        if snake['id'] != game_state['you']['id']:
            if snake['length'] > biggest_opponent:
                biggest_opponent = snake['length']
    if game_state['you']['length'] <= biggest_opponent:
        reward += nearest_food * rewards['distance_to_food_when_small']
    return reward


def bfs_nearest_food(game_state):
    hazards = []
    for hazard in game_state['board']['hazards']:
        hazards.append((hazard['x'], hazard['y']))
    snakes = []
    for snake in game_state['board']['snakes']:
        for body in snake['body']:
            snakes.append((body['x'], body['y']))
    food = []
    for f in game_state['board']['food']:
        food.append((f['x'], f['y']))
    my_head = (game_state['you']['head']['x'], game_state['you']['head']['y'])
    visited = set()
    queue = []
    queue.append((my_head, 0))
    visited.add(my_head)
    while queue:
        current_node, distance = queue.pop(0)
        if current_node in food:
            return distance
        for neighbor in get_neighbors(current_node, game_state, hazards, snakes):
            if neighbor not in visited:
                queue.append((neighbor, distance + 1))
                visited.add(neighbor)
    return None


def get_neighbors(current_node, game_state, hazards, snakes):
    potential_neighbors = []
    neighbors = []
    height = game_state['board']['height']
    width = game_state['board']['width']
    x, y = current_node
    potential_neighbors.append(((x + 1) % width, y))
    potential_neighbors.append(((x - 1) % width, y))
    potential_neighbors.append((x, (y + 1) % height))
    potential_neighbors.append((x, (y - 1) % height))
    for neighbor in potential_neighbors:
        if neighbor not in hazards and neighbor not in snakes:
            neighbors.append(neighbor)
    return neighbors
