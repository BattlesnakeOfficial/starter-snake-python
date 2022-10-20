class StateGeneraror():
    def __init__(self, game_state):
        self.game_state = game_state

    def next_state_for_action(self, snake_id, action):
        snake = self.game_state['board']['snakes']['snake_id']
        head = snake['head']
        food = self.game_state['board']['food']

        # move the head
        if action == 'up':
            next_position = {'x': head['x'], 'y': head['y'] + 1}
        if action == 'down':
            next_position = {'x': head['x'], 'y': head['y'] - 1}
        if action == 'left':
            next_position = {'x': head['x'] - 1, 'y': head['y']}
        if action == 'right':
            next_position = {'x': head['x'] + 1, 'y': head['y']}

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
        if snake_id == self.game_state['you']['id']:
            me = self.game_state['you']
            me['body'].insert(0, next_position)
            me['head'] = next_position
            if not ate_food:
                me['body'].pop(-1)

        return self.game_state
