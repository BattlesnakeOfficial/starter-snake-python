import numpy as np
import random

class MyBattlesnakeHeuristics:
    '''
    The BattlesnakeHeuristics class allows you to define handcrafted rules of the snake.
    '''
    
    FOOD_INDEX = 0
    def __init__(self, json):
        self.height = json["board"]["height"]
        self.width = json["board"]["width"]
        self.foods = json["board"]["food"]
        self.snakes = json["board"]["snakes"]
        self.me = json["you"]
        self.my_health = json["you"]["health"]
        self.my_body = json["you"]["body"]
        self.my_head = json["you"]["head"]
        self.my_length = json["you"]["length"]
    
    
    def go_to_food_if_close(self):
        '''
        Example heuristic to move towards food if it's close to you.
        '''
        
        food_direction = None
        
        # Get the position of the snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
        
        # Check if we are surrounded by food
        if {'x': i_head-1, 'y': j_head} in self.foods:
            food_direction = LEFT
        if {'x': i_head+1, 'y': j_head} in self.foods:
            food_direction = RIGHT
        if {'x': i_head, 'y': j_head-1} in self.foods:
            food_direction = DOWN
        if {'x': i_head, 'y': j_head+1} in self.foods:
            food_direction = UP
        
        return food_direction
    
    def did_try_to_kill_self(self, action):
        
        # Return if our body is smol (1 piece only)
        if len(self.my_body) == 1:
            return False
        
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        # Get the position of the second piece (body)
        i_body, j_body = self.my_body[1]["x"], self.my_body[1]["y"]

        # Calculate the facing direction with the head and the next location
        diff_horiz, diff_vert = i_head - i_body, j_head - j_body
        UP, DOWN, LEFT, RIGHT = 0, 1, 2 ,3
        
        if diff_horiz == -1 and diff_vert == 0: # Left
            if action == RIGHT:
                return True
        elif diff_horiz == 1 and diff_vert == 0: # Right
            if action == LEFT:
                return True 
        elif diff_horiz == 0 and diff_vert == 1: # Up
            if action == DOWN:
                return True
        elif diff_horiz == 0 and diff_vert == -1: # Down
            if action == UP:
                return True
            
        return False

    def did_try_to_escape(self, action):

        # Get the position of snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]

        # Get dimensions
        height_min, width_min, height_max, width_max = 0, 0, self.height-1, self.width-1

        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

        # Top, bottom, left, right layer respectively
        if j_head == height_min and action == DOWN \
            or j_head == height_max and action == UP \
            or i_head == width_min and action == LEFT \
            or i_head == width_max and action == RIGHT:
            return True

        return False
    
    def did_try_to_hit_snake(self, action):
        # Get the position of snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        # Compute the next location of snake head with action
        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
        if action == UP:
        	j_head += 1
       	elif action == DOWN:
       		j_head -= 1
       	elif action == LEFT:
       		i_head -= 1
       	elif action == RIGHT:
       		i_head += 1
         
        # Loop through snakes to see if we're about to collide
        i = 0
        for snake in self.snakes:
            for piece in snake["body"]:
                x, y = piece["x"], piece["y"]
                if x == i_head and y == j_head: # Exact match
                    return True

        return False
    
    def run(self):
        
        log_string = ""
        
        # Check to see which actions kill us
        action_names = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        actions = [0, 1, 2, 3]
        bad_actions = []
        log_strings = []
        
        for action in actions:
            
            # Don't do a forbidden move
            if self.did_try_to_kill_self(action):
                bad_actions.append(action)
                log_strings.append("{} is forbidden".format(action_names[action]))

            # Don't exit the map
            if self.did_try_to_escape(action):
                bad_actions.append(action)
                log_strings.append("{} tries to escape".format(action_names[action]))

            # Don't hit another snake
            if self.did_try_to_hit_snake(action):
                bad_actions.append(action)
                log_strings.append("{} tries to hit a snake".format(action_names[action]))

        legal_actions = [a for a in actions if a not in bad_actions]
        
        # Now choose random action
        if len(legal_actions) > 0:
            action = random.choice(legal_actions)
        else:
            action = 0 # Just go die!
            log_strings.append("Guess I'll just die!")
        
        # Overwrite action if there's food that we are close to
        # This will never kill us based on current heuristics
        if self.my_health < 30:
            food_direction = self.go_to_food_if_close()
            if food_direction:
                action = food_direction
                log_strings.append("Went {} to food if close".format(action_names[action]))


        assert action in [0, 1, 2, 3], "{} is not a valid action.".format(action)
        
        return action, log_strings
