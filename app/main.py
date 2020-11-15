import json
import os
import random
import bottle
from api import ping_response, start_response, move_response, end_response
from timeit import default_timer as timer
import logic

@bottle.route('/')
def index():
    return '''
	Battlesnake documentation can be found at
	   <a href="https://docs.battlesnake.com">https://docs.battlesnake.com</a>.
	'''

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json
    return{
        "name": "snake",
        "color": "#ff3769",
        "headType": "bendr",
        "tailType": "curled",
    }

@bottle.post('/move')
def move():
    start = timer()
    data = bottle.request.json
    direction = logic.make_a_move(data)
    print("direction: ", direction)  # DEBUG
    end = timer()
    print("TOTAL RESPONSE TIME: %.1f" % ((end - start) * 1000))
    return {
        'move': direction,
        'taunt': 'python!'
    }

@bottle.post('/end')
def end():
    data = bottle.request.json
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
