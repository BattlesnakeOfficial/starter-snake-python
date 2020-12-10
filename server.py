import os
import random

import cherrypy
"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
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
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    def willCollideWithSelf(self, data, direction):
        head = data['you']['head']

        if direction == "up" and {
                'x': head['x'],
                'y': head['y'] + 1
        } in data['you']['body']:
            return True
        elif direction == "down" and {
                'x': head['x'],
                'y': head['y'] - 1
        } in data['you']['body']:
            return True
        elif direction == "right" and {
                'x': head['x'] + 1,
                'y': head['y']
        } in data['you']['body']:
            return True
        elif direction == "left" and {
                'x': head['x'] - 1,
                'y': head['y']
        } in data['you']['body']:
            return True

        return False

    def willGoOutOfBounds(self, data, direction):
        head = data['you']['head']

        if direction == "up" and head['y'] == data['board']['height'] - 1:
            return True
        elif direction == "down" and head['y'] == 0:
            return True
        elif direction == "right" and head['x'] == data['board']['width'] - 1:
            return True
        elif direction == "left" and head['x'] == 0:
            return True

        return False

    def headToHeadCollision(self, data, direction):
        your_head = data['you']['head']
        for snake in data['board']['snakes']:
            oponent_head = snake['head']
            if direction == 'up' and your_head['x'] == oponent_head[
                    'x'] and your_head['y'] + 1 == oponent_head['y']:
                return True
            elif direction == 'down' and your_head['x'] == oponent_head[
                    'x'] and your_head['y'] - 1 == oponent_head['y']:
                return True
            elif direction == 'right' and your_head['x'] + 1 == oponent_head[
                    'x'] and your_head['y'] == oponent_head['y']:
                return True
            elif direction == 'left' and your_head['x'] - 1 == oponent_head[
                    'x'] and your_head['y'] == oponent_head['y']:
                return True
        return False

    def willHitAnotherSnake(self, data, direction):
        head = data['you']['head']
        for snake in data['board']['snakes']:
            oponent_body = snake['body']
            if direction == "up" and {
                    'x': head['x'],
                    'y': head['y'] + 1
            } in oponent_body:
                return True
            elif direction == "down" and {
                    'x': head['x'],
                    'y': head['y'] - 1
            } in oponent_body:
                return True
            elif direction == "right" and {
                    'x': head['x'] + 1,
                    'y': head['y']
            } in oponent_body:
                return True
            elif direction == "left" and {
                    'x': head['x'] - 1,
                    'y': head['y']
            } in oponent_body:
                return True

        return False

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]

        # print("head:")
        # print(data['you']['head'])
        # print(data)

        move = random.choice(possible_moves)
        print("Random choice: ", move)
        for possible_move in possible_moves:
            # print(possible_move)
            will_hit_another_snake = self.willHitAnotherSnake(
                data, possible_move)
            will_go_out_of_bounds = self.willGoOutOfBounds(
                data, possible_move)
            is_head_to_head_collision = self.headToHeadCollision(
                data, possible_move)
            if not will_hit_another_snake and not will_go_out_of_bounds and not is_head_to_head_collision:
                move = possible_move
                break

        # move = random.choice(possible_moves)

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update({
        "server.socket_port":
        int(os.environ.get("PORT", "8080")),
    })
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
