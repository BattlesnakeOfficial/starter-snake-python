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
            "color": "#0CDED8",
            "head": "bwc-rudolph",
            "tail": "round-bum"
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.

        data = cherrypy.request.json
        
        print("START")
        
        # Constants pertaining to u/cbinners implementation of the gym
        self.layers = 17
        self.width = 23
        self.height = 23
        
        # Make our policy from previous weights
        self.policy = make_policy(self.layers, self.width, self.height, "weights/weights-200iter-aggressive.pt")
        self.policy.eval()
        
        # Try using symmetry
        # self.generator = GameGenerator(self.layers, self.width, self.height)
        self.generator = GameGenerator(self.layers, self.width, self.height, True)

        print("Made policy and game generator")
        
        # Trackers
        self.deaths = 0
        self.total_moves = 0
        self.ups = 0
        self.downs = 0
        self.rights = 0
        self.lefts = 0
        
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. 
        # It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        
        start = time.time() # Start timer
        
        data = cherrypy.request.json # Get game JSON
        
        self.total_moves += 1
        actions = [0, 1, 2, 3]
        possible_moves = ["up", "down", "left", "right"]
        
        # Convert the JSON to a format needed by agent/policy
        obs = self.generator.make_input(data)
        converted_input = torch.tensor(obs, dtype=torch.float32)
    
        # Get action from our model
        with torch.no_grad():
            action_index, value = self.policy.predict(converted_input, deterministic=True)
            
        # Convert
        action_index = self.generator.get_action(data, action_index.item())
        
        # Check model action with heuristics
        heuristics = Heuristics(data)
        certain_death_actions, head_to_head_actions = heuristics.run()
        
        legal_actions = [a for a in actions if a not in certain_death_actions]
        
        print("Model action: {}".format(possible_moves[action_index]))
        print("Certain death actions: ", 
              [possible_moves[a] for a in list(certain_death_actions)]
        )
        
        # If our model tried to kill us, print it 
        # and choose a new action
        if action_index in certain_death_actions:
            move = possible_moves[action_index]
            log_message = certain_death_actions[action_index]
            print("Potential bad move: {}, {}".format(move, log_message))
            
            self.deaths += 1
            if move == 'up':
                self.ups += 1
            elif move == 'down':
                self.downs += 1
            elif move == 'right':
                self.rights += 1
            elif move == 'left':
                self.lefts += 1
            
            # Choose a different legal action, maybe go head-to-head
            # if legal_actions:
            #     action_index = random.choice(legal_actions)
            # elif head_to_head_actions:
            #     action_index = random.choice(list(head_to_head_actions))
                
        end = time.time()
         
        # Get string name corresponding to action
        action = possible_moves[action_index]
        
        # Print logs
        print("Step {}, Move: {}, Dur: {:.3f}s, Move value: {:.3f}".format(
            data['turn'], 
            action,
            end-start,
            value[0].item()
        ))
        
        return {"move": action}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        
        if data["you"] not in data["board"]["snakes"]:
            print("You lost :(")
        else:
            print("You won :D")
            
        print("You chose a dying move {} out of {} times".format(self.deaths, self.total_moves))
        print("Ups: ", self.ups)
        print("Downs: ", self.downs)
        print("Rights: ", self.rights)
        print("Lefts: ", self.lefts)
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
