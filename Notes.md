# Project Notes

MOVE: up
172.18.0.1 - - [02/Oct/2020:20:07:13] "POST /move HTTP/1.1" 200 14 "" "BattlesnakeEngine/unknown"
MOVE: right
172.18.0.1 - - [02/Oct/2020:20:07:14] "POST /move HTTP/1.1" 200 17 "" "BattlesnakeEngine/unknown"
[02/Oct/2020:20:07:14] HTTP 
Traceback (most recent call last):
  File "/opt/virtualenvs/python3/lib/python3.8/site-packages/cherrypy/_cprequest.py", line 638, in respond
    self._do_respond(path_info)
  File "/opt/virtualenvs/python3/lib/python3.8/site-packages/cherrypy/_cprequest.py", line 697, in _do_respond
    response.body = self.handler()
  File "/opt/virtualenvs/python3/lib/python3.8/site-packages/cherrypy/lib/encoding.py", line 219, in __call__
    self.body = self.oldhandler(*args, **kwargs)
  File "/opt/virtualenvs/python3/lib/python3.8/site-packages/cherrypy/lib/jsontools.py", line 59, in json_handler
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
  File "/opt/virtualenvs/python3/lib/python3.8/site-packages/cherrypy/_cpdispatch.py", line 54, in __call__
    return self.callable(*self.args, **self.kwargs)
  File "server.py", line 53, in move
    move = behaviour.snake_behaviour(data)
  File "/home/runner/SpaceX-Ninja/behaviour.py", line 29, in snake_behaviour
    if snake.is_full_length: #len(snake.body) == snake.length and
AttributeError: 'numpy.ndarray' object has no attribute 'is_full_length'
[02/Oct/2020:20:07:14] HTTP 
Request Headers:
  Remote-Addr: 172.18.0.1
  HOST: SpaceX-Ninja.mdhexdrive.repl.co
  USER-AGENT: BattlesnakeEngine/unknown
  ACCEPT-ENCODING: gzip
  X-FORWARDED-FOR: 35.191.3.105
  X-REPLIT-USER-ID: 
  X-REPLIT-USER-NAME: 
  X-REPLIT-USER-ROLES: 
  Content-Type: application/json
  Content-Length: 1531
172.18.0.1 - - [02/Oct/2020:20:07:14] "POST /move HTTP/1.1" 500 1947 "" "BattlesnakeEngine/unknown"
END
## Game mode specific notes

### Squad Game mode


### Royale
