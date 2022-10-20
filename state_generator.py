import copy


class StateGeneraror():

    def next_state_for_action(self, game_state, snake_id, action):
        height = game_state['board']['height']
        width = game_state['board']['width']
        game_state = copy.deepcopy(game_state)
        for all_snakes in game_state['board']['snakes']:
            if all_snakes['id'] == snake_id:
                snake = all_snakes
                break
        head = snake['head']
        food = game_state['board']['food']

        # move the head
        if action == 'up':
            next_position = {'x': head['x'], 'y': (head['y'] + 1) % height}
        if action == 'down':
            next_position = {'x': head['x'], 'y': (head['y'] - 1) % height}
        if action == 'left':
            next_position = {'x': (head['x'] - 1) % width, 'y': head['y']}
        if action == 'right':
            next_position = {'x': (head['x'] + 1) % width, 'y': head['y']}

        ate_food = False
        for index in range(len(food)):
            if (food[index]['x'], food[index]['y']) == (next_position['x'], next_position['y']):
                food.pop(index)
                snake['length'] += 1
                ate_food = True
                break

        # move head to the next position
        snake['body'].insert(0, next_position)
        snake['head'] = next_position

        # remove the tail if the snake did not eat food
        if not ate_food:
            snake['body'].pop(-1)

        # if I am the snake
        if snake_id == game_state['you']['id']:
            me = game_state['you']
            me['body'].insert(0, next_position)
            me['head'] = next_position
            if not ate_food:
                me['body'].pop(-1)

        return game_state
