import moves
from util import get_pos


class Snake:
    def __init__(self, data, is_you=False, is_alive=True):
        self.snake_id = data['id']
        self.name = data['name']
        self.health = data['health']

        self.head = get_pos(data['head'])
        self.body = []
        for pos in data['body']:
            self.body.append(get_pos(pos))
        self.tail = get_pos(data['body'][-1])
        self.length = data['length']
        self.shout = data['shout']
        self.is_you = is_you
        self.is_alive = is_alive

        self.squad = ""
        self.is_squad_game = False
        if "squad" in data:
            self.squad = data['squad']
            if self.squad != "":
                self.is_squad_game = True
        self.move_hist = []

        # TODO: maybe make this more situation specific?
        # i.e., eliminate moves this snake can't possibly make,
        self.possible_moves = moves.get_moves(self.head)

        self.last_move = ""  # the last move this snake made
        self.last_pos = self.body[1]
        for name, move in moves.get_moves(self.last_pos).items():
            if move == self.head:
                self.last_move = name
        
        self.is_full_length = True
        self.bodySet = set(self.body)
        if len(self.bodySet) != len(self.body):
            self.is_full_length = False

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.body)

    def __eq__(self, other):
        if self.snake_id == other.snake_id:
            return True
        else:
            return False

    def me(self):
        return self.is_you

    def alive(self):
        return self.is_alive

    def on_my_team(self, snake):
        if not self.is_squad_game:
            return False
        if snake.squad == self.squad:
            return True
        else:
            return False
