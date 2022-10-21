import random
import typing


def state_reward(game_state, rewards):
  # a list of all snake bodies
  snakes = []
  for snake in game_state['snake_bodies']:
    snakes += snake
  snakes += game_state['snake_heads']

  state_reward = 0
  state_reward += death_reward(game_state, rewards)
  state_reward += head_collision_reward(game_state, rewards)
  state_reward += food_reward(game_state, rewards, snakes)
  state_reward += domination_reward(game_state, rewards, snakes)
  return state_reward


def death_reward(game_state, rewards):
  dead = False
  # death by hunger
  if game_state['snake_healths'][0] <= 0:
    dead = True

  # death by collision with a wall
  if game_state['snake_heads'][0] in game_state['hazards']:
    dead = True

  # death by collision with a snake body
  for snake_body in game_state['snake_bodies']:
    # if my head is in a snake body
    if game_state['snake_heads'][0] in snake_body:
      dead = True

  if dead:
    return rewards['death']
  else:
    return 0


def head_collision_reward(game_state, rewards):
  reward = 0

  for snake_index in range(1, len(game_state['snake_heads'])):
    # if my head is in an opponent's head
    if game_state['snake_heads'][0] == game_state['snake_heads'][snake_index]:
      # collision with a bigger snake head
      if game_state['snake_lengths'][0] <= game_state['snake_lengths'][
          snake_index]:
        reward += rewards['death']
      # collision with a smaller snake head
      else:
        reward += rewards['opponent_death']
  return reward


def food_reward(game_state, rewards, snakes):
  reward = 0
  nearest_food = bfs_nearest_food(game_state, snakes)
  if nearest_food is None:
    return 0
  # if hungry
  if game_state['snake_healths'][0] < 30:
    reward += nearest_food * rewards['distance_to_food_when_hungry']
  # if not bigger than the biggest opponent
  elif game_state['snake_lengths'][0] < max(game_state['snake_lengths'][1:]):
    reward += nearest_food * rewards['distance_to_food_when_small']
  return reward


def domination_reward(game_state, rewards, snakes):
  reward = 0
  board_domination = bfs_board_domination(game_state, snakes)
  reward = board_domination[0] * rewards['board_domination']
  return reward


def bfs_nearest_food(game_state, snakes):

  my_head = game_state['snake_heads'][0]
  visited = set()
  queue = []
  queue.append((my_head, 0))
  visited.add(my_head)
  while queue:
    current_node, distance = queue.pop(0)
    if current_node in game_state['food']:
      return distance
    for neighbor in get_neighbors(current_node, game_state, snakes):
      if neighbor not in visited:
        queue.append((neighbor, distance + 1))
        visited.add(neighbor)
  return None


def get_neighbors(current_node, game_state, snakes):
  potential_neighbors = []
  neighbors = []
  height = game_state['height']
  width = game_state['width']
  x, y = current_node
  potential_neighbors.append(((x + 1) % width, y))
  potential_neighbors.append(((x - 1) % width, y))
  potential_neighbors.append((x, (y + 1) % height))
  potential_neighbors.append((x, (y - 1) % height))
  for neighbor in potential_neighbors:
    if neighbor not in game_state['hazards'] and neighbor not in snakes:
      neighbors.append(neighbor)
  return neighbors


def bfs_board_domination(game_state, snakes):

  snake_domination = {}
  snake_queues = {}
  visited = set()
  # sort snakes by length and put me last if it's a tie
  snake_indices_by_length = sorted(
    range(len(game_state['snake_lengths'])),
    key=(lambda k: game_state['snake_lengths'][k], lambda k: 0 if k==0 else 1),
    reverse=True)
  for snake_index in snake_indices_by_length:
    snake_head = game_state['snake_heads'][snake_index]
    snake_domination[snake_index] = 0
    snake_queues[snake_index] = []
    snake_queues[snake_index].append((snake_head, 0))
    visited.add(snake_head)

  while non_empty(snake_queues):
    for snake_index, queue in snake_queues.items():
      if queue:
        current_node, domination = queue.pop(0)
        for neighbor in get_neighbors(current_node, game_state, snakes):
          if neighbor not in visited:
            snake_queues[snake_index].append((neighbor, 0))
            visited.add(neighbor)
            snake_domination[snake_index] += 1
  return snake_domination


def non_empty(snake_queues):
  for queue in snake_queues.values():
    if queue:
      return True
  return False
