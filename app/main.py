import bottle
import json


@bottle.get('/')
def index():
    return json.dumps({
        'name': 'battlesnake-python',
        'color': '#00ff00',
        'head': 'http://battlesnake-python.herokuapp.com'
    })


@bottle.post('/start')
def start():
    data = bottle.request.json

    return json.dumps({
        'taunt': 'battlesnake-python!'
    })


@bottle.post('/move')
def move():
    data = bottle.request.json

    return json.dumps({
        'move': 'west',
        'taunt': 'battlesnake-python!'
    })


@bottle.post('/end')
def end():
    data = bottle.request.json

    return json.dumps({
        'taunt': 'battlesnake-python!'
    })


# Expose WSGI app
application = bottle.default_app()
