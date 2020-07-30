import numpy as np
import os
import yaml
import gym
import torch

# Game generator file provided by cbinners (https://github.com/cbinners/)
class GameGenerator():
    
    def __init__(self, layers, width, height, use_symmetry=False):
        self.NUM_LAYERS = layers
        self.LAYER_WIDTH = width
        self.LAYER_HEIGHT = height
        self.use_symmetry = use_symmetry
        
    
    def get_action(self, data, action):
        """
        Takes the json and the action returned by the agent/policy 
        and corrects the action if necessary - i.e. if symmetry
        was used to train
        
        data: the json returned by the game
        action: the action (in number form)
        
        returns action
        """
        
        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
        if self.use_symmetry == False:
            return action
        player_snake = data['you']
        head = player_snake['body'][0]
        neck = player_snake['body'][1]
        flip_y = False
        transpose = False
        transpose_rotate = False
        diff_x = head['x'] - neck['x']
        diff_y = head['y'] - neck['y']
        if self.use_symmetry:
            if diff_x == 0:
                if diff_y == 1:
                    flip_y = True
            else:
                if diff_x == 1:
                    transpose_rotate = True
                if diff_x == -1:
                    transpose = True
                    
        print("flip_y: {}, transpose: {}, transpose_rotate: {}".format(
            flip_y, transpose, transpose_rotate
        ))
        
        if transpose:
            if action == LEFT:
                return DOWN # ORIGINALLY UP
            if action == RIGHT:
                return UP # ORIGINALLY DOWN
            if action == UP: 
                return LEFT
            if action == DOWN:
                return RIGHT
        if transpose_rotate:
            if action == LEFT:
                return DOWN # ORIGINALLY UP
            if action == RIGHT:
                return UP # ORIGINALLY DOWN
            if action == UP:
                return RIGHT
            if action == DOWN:
                return LEFT
        # if flip_y:
        #     return action
            # if action == LEFT:
            #     return LEFT
            # if action == RIGHT:
            #     return RIGHT
            # if action == UP:
            #     return DOWN
            # if action == DOWN:
            #     return UP
        
        # Added conversion
        if action == UP:
            return DOWN
        elif action == DOWN:
            return UP
        
        return action
    
    def get_x(self, head, flip_y, transpose, transpose_rotate, x, y):
        s_x = x - head['x']
        s_y = y - head['y']
        s_x += self.LAYER_WIDTH // 2
        s_y += self.LAYER_HEIGHT // 2
        if transpose:
            return s_y
        if transpose_rotate:
            return s_y
        return s_x
    
    def get_y(self, head, flip_y, transpose, transpose_rotate, x, y):
        s_x = x - head['x']
        s_y = y - head['y']
        s_x += self.LAYER_WIDTH // 2
        s_y += self.LAYER_HEIGHT // 2
        if transpose:
            return s_x
        if transpose_rotate:
            return self.LAYER_WIDTH - s_x - 1
        if flip_y:
            return self.LAYER_HEIGHT - s_y - 1
        return s_y
    
    def assign(self, obs, head, neck, x, y, l, v, params):
        flip_y = params['flip_y']
        transpose = params['transpose']
        transpose_rotate = params['transpose_rotate']
        s_x = self.get_x(head, flip_y, transpose, transpose_rotate, x, y)
        s_y = self.get_y(head, flip_y, transpose, transpose_rotate, x, y)
        if s_x >= 0 and s_x < self.LAYER_WIDTH and s_y >= 0 and s_y < self.LAYER_HEIGHT:
            obs[l*self.LAYER_WIDTH*self.LAYER_HEIGHT + s_x * self.LAYER_HEIGHT + s_y] += v
            
    def make_input(self, data):
        """ Method to transform the starter snake input into the correct format for our trained model """
        obs = np.zeros((self.LAYER_WIDTH * self.LAYER_HEIGHT * self.NUM_LAYERS), dtype=np.uint8)
        player_snake = data['you']
        head = player_snake['body'][0]
        neck = player_snake['body'][1]
        params = {}
        
        flip_y = False
        transpose = False
        transpose_rotate = False
        
        diff_x = head['x'] - neck['x']
        diff_y = head['y'] - neck['y']
        if self.use_symmetry:
            if diff_x == 0:
                if diff_y == 1:
                    flip_y = True
            else:
                if diff_x == 1:
                    transpose_rotate = True
                if diff_x == -1:
                    transpose = True
        
        params['flip_y'] = flip_y
        params['transpose'] = transpose
        params['transpose_rotate'] = transpose_rotate
        # Assign the head for the player
        self.assign(obs, head, neck, player_snake['body'][0]['x'], player_snake['body'][0]['y'], 6, 1, params)
        for snake in data['board']['snakes']:
            self.assign(obs, head, neck, snake['body'][0]['x'], snake['body'][0]['y'], 0, snake['health'], params)
            i = 1
            for segment in reversed(snake['body']):
                self.assign(obs, head, neck, segment['x'], segment['y'], 1, 1, params)
                self.assign(obs, head, neck, segment['x'], segment['y'], 2, min(i, 255), params)
                i += 1
                if snake['id'] != player_snake['id']:
                    len_enemy = len(snake['body'])
                    len_player = len(player_snake['body'])
                    if len_enemy >= len_player:
                        self.assign(obs, head, neck, segment['x'], segment['y'], 8, 1 + len_enemy - len_player, params)
                    else:
                        self.assign(obs, head, neck, segment['x'], segment['y'], 9, len_player - len_enemy, params)
            # Check for matching tails
            tail_1 = snake['body'][-1]
            tail_2 = snake['body'][-2]
            if tail_1['x'] == tail_2['x'] and tail_1['y'] == tail_2['y']:
                # Mark the doubled tail
                self.assign(obs, head, neck, tail_1['x'], tail_1['y'], 7, 1, params)
            if snake['id'] != player_snake['id']:
                is_bigger = 0
                if len(snake['body']) >= len(player_snake['body']):
                    is_bigger = 1
                snake_head = snake['body'][0]
                self.assign(obs, head, neck, snake_head['x'], snake_head['y'], 3, is_bigger, params)
        n_enemy_idx = len(data['board']['snakes']) - 2
        for food in data['board']['food']:
            self.assign(obs, head, neck, food['x'], food['y'], 4, 1, params)
        for x in range(data['board']['width']):
            for y in range(data['board']['height']):
                self.assign(obs, head, neck, x, y, 5, 1, params)
                self.assign(obs, head, neck, x, y, n_enemy_idx + 10, 1, params)
        inp = obs.reshape(1, self.NUM_LAYERS, self.LAYER_WIDTH, self.LAYER_HEIGHT)
        return inp