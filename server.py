import json

import cherrypy


class Battlesnake(object):
    @cherrypy.expose
    def index(self):
        return "Your Battlesnake is alive!"

    @cherrypy.expose
    def ping(self):
        return "pong"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        data = cherrypy.request.json
        print(data)
        response = {"color": "#888888", "headType": "regular", "tailType": "regular"}
        return json.dumps(response)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json
        print(data)
        response = {"move": "up"}  # can also be "down", "left", or "right"
        return json.dumps(response)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        data = cherrypy.request.json
        print(data)
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.quickstart(server)
