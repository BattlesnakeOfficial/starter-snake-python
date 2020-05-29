

import numpy as np
import random

class MyBattlesnakeHeuristics:
    '''
    The BattlesnakeHeuristics class allows you to define handcrafted rules of the snake.
    '''
    FOOD_INDEX = 0
    def __init__(self):
        pass
    
    def go_to_food_if_close(self, state, json):
        '''
        Example heuristic to move towards food if it's close to you.
        '''
        # Get the position of the snake head
        your_snake_body = json["you"]["body"]
        i, j = your_snake_body[0]["y"], your_snake_body[0]["x"]
        
        # Set food_direction towards food
        food = state[:, :, self.FOOD_INDEX]
        
        # Note that there is a -1 border around state so i = i + 1, j = j + 1
        if -1 in state:
            i, j = i+1, j+1
        
        food_direction = None
        if food[i-1, j] == 1:
            food_direction = 0 # up
        if food[i+1, j] == 1:
            food_direction = 1 # down
        if food[i, j-1] == 1:
            food_direction = 2 # left
        if food[i, j+1] == 1:
            food_direction = 3 # right
        return food_direction
    
    def did_try_to_kill_self(self, json, best_action):
        
        # Get the position of the snake head
        your_snake_body = json["you"]["body"]
        
        # Return if our body is smol (1 piece only)
        if len(your_snake_body) == 1:
            return False
        
        i_head, j_head = your_snake_body[0]["y"], your_snake_body[0]["x"]
        
        # Get the position of the second piece (body)
        i_body, j_body = your_snake_body[1]["y"], your_snake_body[1]["x"]

        # Calculate the facing direction with the head and the next location
        difference = (i_head - i_body, j_head - j_body)
        
        if difference[0] == -1 and difference[1] == 0: # Up
            if best_action == 1: # Down = death
                return True
        elif difference[0] == 1 and difference[1] == 0: # Down
            if best_action == 0: # Up = death
                return True 
        elif difference[0] == 0 and difference[1] == -1: # Left
            if best_action == 3: # Right = death
                return True
        elif difference[0] == 0 and difference[1] == 1: # Right
            if best_action == 2: # Left = death
                return True
            
        return False

    def did_try_to_escape(self, json, state, best_action):

        # Get the position of snake head
        your_snake_body = json["you"]["body"]
        i_head, j_head = your_snake_body[0]["y"], your_snake_body[0]["x"]

        # Get map size
        height_min = 0
        width_min = 0
        height_max, width_max = json["board"]["height"], json["board"]["width"]

        # Adjust if padded
        if -1 in state:
            i_head += 1
            j_head += 1
            height_min += 1
            width_min += 1
            height_max += 1
            width_max += 1

        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

        # Top layer 
        if i_head == height_min and best_action == UP:
            return True
        elif i_head == height_max and best_action == DOWN:
            return True
        elif j_head == width_min and best_action == LEFT:
            return True
        elif j_head == width_max and best_action == RIGHT:
            return True
        
        # Old code that determines if head went outside map
        # if 0 <= j_head < self.map_size[1]:
        #     if 0 <= i_head < self.map_size[0]:
        #         return False

        return False

    def did_try_to_hit_snake(self, json, state, best_action):

    	# Get the position of snake head
        your_snake_body = json["you"]["body"]
        i_head, j_head = your_snake_body[0]["y"], your_snake_body[0]["x"]

        # Adjust if padded
        if -1 in state:
            i_head += 1
            j_head += 1

        # Compute the next location of snake head with best_action
        UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
        if best_action == UP: # UP
        	i_head -= 1
       	elif best_action == DOWN:
       		i_head += 1
       	elif best_action == LEFT:
       		j_head -= 1
       	elif best_action == RIGHT:
       		j_head += 1

        # Loop through snakes to see if we're about to collide
        snakes = json["board"]["snakes"]
        for snake in snakes:
        	for piece in snake["body"]:
        		x, y = piece["x"], piece["y"]
        		if -1 in state:
        			x += 1
        			y += 1

        		if x == i_head or y == j_head:
        			return True

        return False
    
    def run(self, state, snake_id, turn_count, health, json, action):
        '''
        The main function of the heuristics.
        
        Parameters:
        -----------
        `state`: np.array of size (map_size[0]+2, map_size[1]+2, 1+number_of_snakes)
        Provides the current observation of the gym.
        Your target snake is state[:, :, snake_id+1]
    
        `snake_id`: int
        Indicates the id where id \in [0...number_of_snakes]
    
        `turn_count`: int
        Indicates the number of elapsed turns
    
        `health`: dict
        Indicates the health of all snakes in the form of {int: snake_id: int:health}
        
        `json`: dict
        Provides the same information as above, in the same format as the battlesnake engine.

        `action`: np.array of size 4
        The qvalues of the actions calculated. The 4 values correspond to [up, down, left, right]
        '''
        log_string = ""
        
        # The default `best_action` to take is the one that provides has the largest Q value.
        # If you think of something else, you can edit how `best_action` is calculated
        best_action = int(np.argmax(action))

        num_redirected = 2 # If we ignore max q value, choose second highest and continue decrementing.
                
        # Example heuristics to eat food that you are close to.
        if health[snake_id] < 30:
            food_direction = self.go_to_food_if_close(state, json)
            if food_direction:
                best_action = food_direction
                log_string = "Went to food if close."
        
        # Don't do a forbidden move
        if self.did_try_to_kill_self(json, best_action):
            
            old_action = best_action # For logging
            
            # Pick one lower q-value instead
            sort = np.argsort(action)[0]
            best_action = sort[-num_redirected]

            num_redirected -= 1
            
            log_string = "Forbidden. Changed {} to {}".format(old_action, best_action)

        # Don't exit the map
        if self.did_try_to_escape(json, state, best_action):

            old_action = best_action # For logging
            
            # Pick one lower q-value instead
            sort = np.argsort(action)[0]
            best_action = sort[-num_redirected]

            num_redirected -= 1
            
            log_string = "Tried to escape. Changed {} to {}".format(old_action, best_action)

        # Don't hit another snake
        if self.did_try_to_hit_snake(json, state, best_action):

        	old_action = best_action

        	# Pick one lower q-value instead
            sort = np.argsort(action)[0]
            best_action = sort[-num_redirected]

            num_redirected -= 1
            
            log_string = "About to hit a snake. Changed {} to {}".format(old_action, best_action)

        # Somehow, every action is bad! Pick the highest q-value and die lmao
        if best_action not in [0, 1, 2, 3]:
        	best_action = int(np.argmax(action))
        	log_string = "Guess I'll die!"

        assert best_action in [0, 1, 2, 3], "{} is not a valid action.".format(best_action)
        return best_action, log_string

# JSON

# {'board': {'height': 11, 'width': 11, 'food': [{'x': 1, 'y': 8}], 'snakes': [{'health': 100, 'body': [{'x': 10, 'y': 2}], 'id': 0, 'name': 'Snake 0'}, {'health': 100, 'body': [{'x': 3, 'y': 2}], 'id': 1, 'name': 'Snake 1'}, {'health': 100, 'body': [{'x': 7, 'y': 6}], 'id': 2, 'name': 'Snake 2'}, {'health': 100, 'body': [{'x': 4, 'y': 2}], 'id': 3, 'name': 'Snake 3'}, {'health': 100, 'body': [{'x': 3, 'y': 1}], 'id': 4, 'name': 'Snake 4'}]}, 'you': {'health': 100, 'body': [{'x': 10, 'y': 2}], 'id': 0, 'name': 'Snake 0'}}
