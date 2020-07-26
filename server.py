import os
import random
import cherrypy
import torch
import time

from src.heuristics import Heuristics
from src.my_model import make_agent
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
        
        possible_moves = ["up", "down", "left", "right"]


        # Choose an action through our ML model
        agent, policy = make_agent()
        gen = GameGenerator(17, json["board"]["width"], json["board"]["height"])
        
        converted_input = torch.tensor(agent.gen.make_input(data), dtype=torch.float32)
    
        # Get action
        start = time.time()
        with torch.no_grad():
            action_index, value = policy.predict(converted_input, deterministic=True)
        end = time.time()
        

        # Check action with heuristics
        # heuristics = Heuristics(json)
        # action_index, log_strings = heuristics.run()
        
        action = possible_moves[action_index]
        
        # Print move
        print("Step {}... Move: {}".format(json['turn'], action))
        print("Duration: {}".format(end-start))
        
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
    
    # Testing
    def test(self):
        agent, policy = make_agent()
        print(agent)
        print(policy)
        print("good!")
        

if __name__ == "__main__":
    server = Battlesnake()
    
    # Added unit test
    server.test()
    
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
