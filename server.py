import os
import random
import cherrypy

from heuristics import Heuristics
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
            "head": "beluga",
            "tail": "fat-rattle",
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

        json = cherrypy.request.json

        possible_moves = ["up", "down", "left", "right"]

        # Choose an action through heuristics
        heuristics = Heuristics(json)
        action_index, log_strings = heuristics.run()
        
        action = possible_moves[action_index]
        
        # Print move
        print("Step {}... Move: {}".format(json['turn'], action))
        
        # Check logs
        if len(log_strings) > 0:
            for msg in log_strings: 
                print(msg)
        
        return {"move": action}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        
        print('FINAL DATA: ', data)
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
