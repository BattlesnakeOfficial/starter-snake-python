import bottle
import os
import random

from api import *


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data
    print(json.dumps(data))

    return StartResponse("#00ff00")


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    print(json.dumps(data))
    
    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)

    return MoveResponse(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Any cleanup that needs to be done.
    print json.dumps(data)


@bottle.post('/ping')
def ping():
    return "Alive"


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
