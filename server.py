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
            "color": "#ff8f00", # Princeton orange bih
            "head": "bendr",
            "tail": "freckled",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        
        data = cherrypy.request.json
        
        actions = [0, 1, 2, 3]
        possible_moves = ["up", "down", "left", "right"]

        # Grab constants
        NUM_LAYERS = 17
        WIDTH, HEIGHT = data["board"]["width"], data["board"]["height"]
        
        # Make our policy from previous weights
        policy = make_policy(17, WIDTH, HEIGHT, "weights/battlesnakeWeights.pt")
        
        # Convert the json to a format needed by agent/policy
        generator = GameGenerator(17, WIDTH, HEIGHT)
        converted_input = torch.tensor(generator.make_input(data), dtype=torch.float32)
    
        # Get action from our model
        start = time.time()
        with torch.no_grad():
            action_index, value = policy.predict(converted_input, deterministic=True)
            action_index = action_index.item()
        
        # Check model action with heuristics
        heuristics = Heuristics(data)
        certain_death_actions, might_die_actions = heuristics.run()
        legal_actions = [a for a in actions if a not in certain_death_actions]
        
        # If our model tried to kill us, print and choose a new action
        if action_index in certain_death_actions:
            print("Oh no! Our model tried to kill us by going {}".format(possible_moves[action_index]))
            
            if legal_actions:
                action_index = random.choice(legal_actions)
            elif might_die_actions:
                action_index = random.choice(might_die_actions)
            else:
                action_index = 0 # Just go and die then!
                
        end = time.time()
         
        # Get string name corresponding to action
        action = possible_moves[action_index]
        
        # Print move
        print("Step {}... Move: {}".format(data['turn'], action))
        print("Duration: {}".format(end-start))
        print("Value: {}".format(value[0].item()))
        
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
            
        return "ok"

    # ----------------------
    
    # Some unit testing
    def test(self):
        
        # Dummy json
        with open('src/data.json') as json_file:
            data = json.load(json_file)
        
        possible_moves = ["up", "down", "left", "right"]

        # Choose an action through our ML model
        NUM_LAYERS = 17
        WIDTH, HEIGHT = 12, 12
        
        policy = make_policy(17, WIDTH, HEIGHT, "weights/battlesnakeWeights.pt")
        gen = GameGenerator(17, WIDTH, HEIGHT)
        
        # Convert the json to format needed by agent/policy
        import numpy as np
        converted_input = torch.tensor(gen.make_input(data), dtype=torch.float32).to(torch.device('cpu'))
    
        # Get action
        start = time.time()
        with torch.no_grad():
            action_index, value = policy.predict(converted_input, deterministic=True)
        end = time.time()
        
        action = possible_moves[action_index.item()]
        
        return action
        

if __name__ == "__main__":
    server = Battlesnake()
    
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
