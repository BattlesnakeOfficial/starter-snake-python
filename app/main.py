import pprint
import bottle
import json


@bottle.get('/')
def index():
    return """
        <a href="https://github.com/sendwithus/battlesnake-python">
            battlesnake-python
        </a>
    """


@bottle.post('/start')
def start():
    data = bottle.request.json
    pprint.pprint(data)

    return json.dumps({
        'name': 'battlesnake-python',
        'color': '#00ff00',
        'head_url': 'http://battlesnake-python.herokuapp.com',
        'taunt': 'battlesnake-python!'
    })


@bottle.post('/move')
def move():
    data = bottle.request.json
    pprint.pprint(data)
    return json.dumps({
        'move': 'left',
    })


@bottle.post('/end')
def end():
    data = bottle.request.json
    pprint.pprint(data)
    return json.dumps({})


# Expose WSGI app
application = bottle.default_app()

if __name__ == "__main__":
    bottle.run(host='0.0.0.0', port=8080, debug=True)
