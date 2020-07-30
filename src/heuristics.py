import numpy as np
import random
import math

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

class Heuristics:
    
    '''
    The BattlesnakeHeuristics class defines handcrafted rules for the snake.
    '''
    
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
    
    # ------------------------------------------------------------------------
    
    # Helper function to update coordinates
    
    def update_coords(self, i, j, action):
        
        if action == UP:
            j += 1
        elif action == DOWN:
            j -= 1
        elif action == LEFT:
            i -= 1
        elif action == RIGHT:
            i += 1
        
        return i, j
    
    # ------------------------------------------------------------------------
    
    # Check if food is one or two blocks next to our head
    
    def go_to_food_if_close(self):
        '''
        Example heuristic to move towards food if it's close to you.
        '''
        
        food_direction = None
        
        # Get the position of the snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        # Check if we are surrounded by food
        if {'x': i_head-1, 'y': j_head} in self.foods or {'x': i_head-2, 'y': j_head} in self.foods:
            food_direction = LEFT
        if {'x': i_head+1, 'y': j_head} in self.foods or {'x': i_head+2, 'y': j_head} in self.foods:
            food_direction = RIGHT
        if {'x': i_head, 'y': j_head-1} in self.foods or {'x': i_head, 'y': j_head-2} in self.foods:
            food_direction = DOWN
        if {'x': i_head, 'y': j_head+1} in self.foods or {'x': i_head, 'y': j_head+2} in self.foods:
            food_direction = UP
        
        return food_direction
    
    
    # ------------------------------------------------------------------------
    
    # Check if surrounding block to our head (after action) is 
    # surrounded by any enemy heads

    def about_to_go_head_to_head(self, action):
        
        i_head, j_head = self.my_head["x"], self.my_head["y"]

        # Get new coordinate of where head will be if we move there
        i_head, j_head = self.update_coords(i_head, j_head, action)
            
        # Loop through snakes to see if there's potential to collide
        action_names = ['up', 'down', 'left', 'right']
        for a in [UP, DOWN, LEFT, RIGHT]:
            # Get new coordinate of where head would be //on turn after next// if we move there
            i_new, j_new = self.update_coords(i_head, j_head, a)
            for snake in self.snakes:
                head = snake["head"]
                if head != self.my_head: # Skip our own head (or else it would return True each time)
                    x, y = head["x"], head["y"]
                    if (x == i_new and y == j_new) and (snake["health"] >= self.my_health):
                        return True
                    # else:
                    #     print('Moving {} {} does not hit snake {}'.format(action_names[action], action_names[a], snake["name"]))
                    #     print('My health: ', self.my_health)
                    #     print('{}''s health: {}'.format(snake["name"], snake["health"]))
        return False
        

    # ------------------------------------------------------------------------
    
    # Check for a forbidden move (e.g. going right, move left)
    
    # Deprecated by did_try_to_hit_snake
    
    # def did_try_to_kill_self(self, action):
        
    #     # Return if our body is smol (1 piece only)
    #     if len(self.my_body) == 1:
    #         return False
        
    #     i_head, j_head = self.my_head["x"], self.my_head["y"]
        
    #     # Get the position of the second piece (body)
    #     i_body, j_body = self.my_body[1]["x"], self.my_body[1]["y"]

    #     # Calculate the facing direction with the head and the next location
    #     diff_horiz, diff_vert = i_head - i_body, j_head - j_body
        
    #     if diff_horiz == -1 and diff_vert == 0: # Left
    #         if action == RIGHT:
    #             return True
    #     elif diff_horiz == 1 and diff_vert == 0: # Right
    #         if action == LEFT:
    #             return True 
    #     elif diff_horiz == 0 and diff_vert == 1: # Up
    #         if action == DOWN:
    #             return True
    #     elif diff_horiz == 0 and diff_vert == -1: # Down
    #         if action == UP:
    #             return True
            
    #     return False
    
    # ------------------------------------------------------------------------
    
    # Check if we're leaving the map

    def did_try_to_escape(self, action):
        
        # Get head
        i_head, j_head = self.my_head["x"], self.my_head["y"]

        # Get dimensions
        height_min, width_min, height_max, width_max = 0, 0, self.height-1, self.width-1

        # Top, bottom, left, right layer respectively
        if j_head == height_min and action == DOWN \
            or j_head == height_max and action == UP \
            or i_head == width_min and action == LEFT \
            or i_head == width_max and action == RIGHT:
            return True

        return False
    
    # ------------------------------------------------------------------------
    
    # Check if we're about to hit another snake
    
    def did_try_to_hit_snake(self, action):
        
        # Get the position of snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        # Compute the next location of snake head with action
        i_head, j_head = self.update_coords(i_head, j_head, action)

        # Loop through snakes to see if we're about to collide
        for snake in self.snakes:
            for piece in snake["body"]:
                x, y = piece["x"], piece["y"]
                if x == i_head and y == j_head: # Exact match
                    return True
        return False

    # ------------------------------------------------------------------------
    
    # Check if we die on the next, next move (two move look-ahead)
    def will_die_on_next_move(self, action):
        
        # Helper function to see if we're dead
        def dies(i, j, a):
            # Duplicate code to see if we're about to escape // TODO: Avoid duplicate code
            if j == height_min and a == DOWN \
                or j == height_max and a == UP \
                or i == width_min and a == LEFT \
                or i == width_max and a == RIGHT:
                return True
                
            # Don't hit another snake
            # Loop through snakes to see if we're about to collide // TODO: Avoid duplicate code
            for snake in self.snakes:
                # TODO: NEED TO ADD NEW LOCATION OF HEAD OF OWN SNAKE
                for piece in snake["body"]:
                    x, y = piece["x"], piece["y"]
                    if x == i and y == j: # Exact match
                        return True
            return False
            
        # Get the position of snake head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        # Compute the next location of snake head with action
        i_head, j_head = self.update_coords(i_head, j_head, action)
        
        # Counter
        bad_moves = 0
        
         # Get dimensions
        height_min, width_min, height_max, width_max = 0, 0, self.height-1, self.width-1
        
        for a in [UP, DOWN, LEFT, RIGHT]: # Note to self: don't confuse 'action' with 'a' and CHANGE VARIABLE NAMES
            
            i_new, j_new = self.update_coords(i_head, j_head, a)
            
            if dies(i_new, j_new, a):
                bad_moves += 1
        
        return bad_moves == 4
    
    # ------------------------------------------------------------------------
    
    # Choose the action which has the smallest distance 
    
    def get_action_based_on_dist(self, legal_actions):
        
        # To get the action corresponding to smallest dist.
        smallest_dist = 10000
        best_action = None

        # Head
        i_head, j_head = self.my_head["x"], self.my_head["y"]
        
        center_x, center_y = self.height/2, self.width/2
        
        def calculate_dist(i, j):
            return math.sqrt((center_x - i)**2 + (center_y - j)**2)
            
        for a in legal_actions:
            
            # Update head
            i_new, j_new = self.update_coords(i_head, j_head, a)
            
            # Check dist
            dist = calculate_dist(i_new, j_new)
            
            if dist < smallest_dist:
                smallest_dist = dist
                best_action = a
        
        return best_action

    # ------------------------------------------------------------------------

    def run(self):
        
        log_strings = []
        action_names = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        actions = [0, 1, 2, 3]
        certain_death_actions = {}
        head_to_head_actions = {}
        
        # See if we can eat food
        # food_direction = None
        # if self.my_health < 50:
        #     food_direction = self.go_to_food_if_close()
        
        # Check to see which actions kill us
        for action in [UP, DOWN, LEFT, RIGHT]:
            
            # Don't hit another snake (including self)
            if self.did_try_to_hit_snake(action):
                certain_death_actions[action] = "tried to hit a snake/self"
                continue

            # Don't exit the map
            if self.did_try_to_escape(action):
                certain_death_actions[action] = "tried to escape"
                continue
            
            # Don't die two moves later
            # if self.will_die_on_next_move(action):
            #     certain_death_actions[action] = "will die two moves later"
            #     continue
            
            # Don't (potentially) lose a head-to-head
            if self.about_to_go_head_to_head(action):
                certain_death_actions[action] = "might lose head to head"
                head_to_head_actions[action] = "might lose head to head"

        return certain_death_actions, head_to_head_actions