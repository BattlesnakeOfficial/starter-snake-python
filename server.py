import logging
import os
import typing

from flask import Flask
from flask import request


def run_server(handlers: typing.Dict):
    """Starts a Flask server with the specified handlers.

    Args:
        handlers (typing.Dict): A dictionary of handlers that will be used by the server.


    Returns:
        type: The type of the Flask server.
    """
    app = Flask("Battlesnake")

    @app.get("/")
    def on_info():
        """Calls the "info" handler function.


        Returns:
                type: The type of the "info" handler function's return value.

        """
        return handlers["info"]()

    @app.post("/start")
    def on_start():
        """ Calls the "start" handler function and returns "ok".

        Returns:
                type: The type of the "start" handler function's return value.

        """
        game_state = request.get_json()
        handlers["start"](game_state)
        return "ok"

    @app.post("/move")
    def on_move():
        """  Calls the "move" handler function with the current game state and returns its return value.


        Returns:
                type: The type of the "move" handler function's return value.

        """
        game_state = request.get_json()
        return handlers["move"](game_state)

    @app.post("/end")
    def on_end():
        """ Calls the "end" handler function and returns "ok".


        Returns:
                type: The type of the "end" handler function's return value.

        """
        game_state = request.get_json()
        handlers["end"](game_state)
        return "ok"

    @app.after_request
    def identify_server(response):
        """ Sets the "server" header of the specified response object and returns it.


        Args:
            response (type): The response object to modify.


        Returns:
        type: The modified response object.
        """
        response.headers.set(
            "server", "battlesnake/github/starter-snake-python"
        )
        return response

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print(f"\nRunning Battlesnake at http://{host}:{port}")
    app.run(host=host, port=port)

