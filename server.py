import os

import cherrypy

import server_logic

class BattlesnakeServer(object):
    """
    This is a simple Battlesnake server written in Python using the CherryPy Web Framework.
    For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
    """

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """
        This function is called when you register your Battlesnake on play.battlesnake.com
        See https://docs.battlesnake.com/guides/getting-started#step-4-register-your-battlesnake

        It controls your Battlesnake appearance and author permissions.
        For customization options, see https://docs.battlesnake.com/references/personalization
        
        TIP: If you open your Battlesnake URL in browser you should see this data.
        """
        print("INFO")
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#888888",  # TODO: Personalize
            "head": "default",  # TODO: Personalize
            "tail": "default",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        """
        This function is called everytime your snake is entered into a game.
        cherrypy.request.json contains information about the game that's about to be played.
        """
        data = cherrypy.request.json
        
        print(f"{data['game']['id']} START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        """
        This function is called on every turn of a game. It's how your snake decides where to move.
        Valid moves are "up", "down", "left", or "right".
        """
        data = cherrypy.request.json

        # TODO - look at the server_logic.py file to see how we decide what move to return!
        move = server_logic.choose_move(data)

        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        """
        This function is called when a game your snake was in ends.
        It's purely for informational purposes, you don't have to make any decisions here.
        """
        data = cherrypy.request.json
        
        print(f"{data['game']['id']} END")
        return "ok"


if __name__ == "__main__":
    server = BattlesnakeServer()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
