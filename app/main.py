import bottle
import json


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return json.dumps({
        'color': '#00ff00',
        'head': head_url
    })


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data

    return json.dumps({
        'taunt': 'battlesnake-python!'
    })


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data

    return json.dumps({
        'move': 'north',
        'taunt': 'battlesnake-python!'
    })


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return json.dumps({
        'taunt': 'battlesnake-python!'
    })


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host='127.0.0.1', port=8080)
