import os
import random
import cherrypy
import torch
import time

from src.heuristics import Heuristics
from src.my_model import make_policy
from src.generator import GameGenerator

import json

class Battlesnake(object):
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "jpulmano",
            "color": "#800000",
            "head": "shac-gamer",
            "tail": "shac-coffee"
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json
        
        print("START")
        
        # Constants pertaining to u/cbinners implementation of the gym
        self.layers = 17
        self.width = 23
        self.height = 23
        
        # Make our policy from previous weights
        self.policy = make_policy(self.layers, self.width, self.height, "weights/weights-50iter.pt")
        self.policy.eval()
        
        self.generator = GameGenerator(self.layers, self.width, self.height)

        print("Made policy and generator!")
        
        # Trackers
        self.deaths = 0
        self.total_moves = 0
        
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        
        start = time.time() # Start timer
        
        data = cherrypy.request.json # Get game JSON
        
        self.total_moves += 1 # Increment
        
        actions = [0, 1, 2, 3]
        possible_moves = ["up", "down", "left", "right"]
        
        # Convert the JSON to a format needed by agent/policy
        converted_input = torch.tensor(self.generator.make_input(data), dtype=torch.float32)
    
        # Get action from our model
        with torch.no_grad():
            action_index, value = self.policy.predict(converted_input, deterministic=True)
        
        # Get the name of the action
        action = self.generator.get_action(data, possible_moves[action_index[0]])
        
        # Return to the index
        action_index = possible_moves.index(action)
        
        # Check model action with heuristics
        heuristics = Heuristics(data)
        certain_death_actions, might_die_actions = heuristics.run()
        legal_actions = [a for a in actions if a not in certain_death_actions]
        
        # If our model tried to kill us, print and choose a new action
        if action_index in certain_death_actions:
            print("MODEL TRIED TO KILL US BY GOING {}".format(possible_moves[action_index]))
            self.deaths += 1
            
            if legal_actions:
                print("Choosing another legal action")
                action_index = random.choice(legal_actions)
            elif might_die_actions:
                print("Choosing an action where we might die")
                action_index = random.choice(might_die_actions)
            else:
                print("Just going to die now!")
                action_index = 0 # Just go and die then!
                
        end = time.time()
         
        # Get string name corresponding to action
        action = possible_moves[action_index]
        
        # Print move
        print("Step {}... Move: {}".format(data['turn'], action))
        print("Duration: {:.2f}s".format(end-start))
        print("Value: {:.2f}".format(value[0].item()))
        
        return {"move": action}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        
        if data["you"] not in data["board"]["snakes"]:
            print("you lost bruh")
        else:
            print("you won bruh!")
            
        print("You chose a dying move {} out of {} times".format(self.deaths, self.total_moves))
        print("That's {:.2f}!".format(self.deaths/self.total_moves))
        
        return "ok"
        

if __name__ == "__main__":
    server = Battlesnake()
    
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
