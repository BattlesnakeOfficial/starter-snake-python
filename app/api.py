import json
from bottle import HTTPResponse


class MoveResponse(HTTPResponse):
    def __init__(self, move):
        assert move in ['up', 'down', 'left', 'right'], \
            "Move must be one of [up, down, left, right]"

        self.move = move

        super(HTTPResponse, self).__init__(
            status=200,
            body=json.dumps({"move": self.move}),
            headers={"Content-Type": "application/json"}
        )


class StartResponse(HTTPResponse):
    def __init__(self, color):
        assert type(color) is str, "Color value must be string"
        self.color = color

        super(HTTPResponse, self).__init__(
            status=200,
            body=json.dumps({"color": self.color}),
            headers={"Content-Type": "application/json"}
        )
