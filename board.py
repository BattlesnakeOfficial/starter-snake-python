import json
import numpy as np
import predict
import moves
from snake import Snake
from util import get_pos, distance, directions
from constants import FREE_SPACE, FOOD, SAFE_SPACE, HAZARD, MY_HEAD, MY_BODY, MY_TAIL, ENEMY_HEAD, ENEMY_TAIL, ENEMY_BODY, ENEMY_NEXT_MOVE


class Board:
    def __init__(self, data):

        self.data = data

        self.width = data['board']['width']
        self.height = data['board']['height']

        self.food = []

        self.board = np.zeros((self.width, self.height), dtype=np.int16)
        self.hazards = np.zeros((self.width, self.height), dtype=np.int16)
        self.healthmatrix = np.zeros((self.width, self.height), dtype=np.int16)
        self.lengthmatrix = np.zeros((self.width, self.height), dtype=np.int16)

        self.snakematrix = np.zeros((self.width, self.height), dtype=object)

        self.me = Snake(data['you'], is_you=True)
        self.snakes = dict()
        for snake in data['board']['snakes']:
            snk = Snake(snake)
            if snk == self.me:
                self.snakes[snake['id']] = self.me
            else:
                self.snakes[snake['id']] = snk

        self.process_board(data)

    def __getitem__(self, index):
        return self.board[index]

    def process_board(self, data):
        # load hazards
        self.load_hazards(data)

        # load food data
        for food in data['board']['food']:
            food_pos = get_pos(food)
            self.board[food_pos] = FOOD
            self.food.append(food_pos)

        # load enemy snakes
        for snake in self.snakes.values():
            if snake == self.me:
                self.load_me(snake)  # load yourself
                continue
            on_same_team = self.me.on_my_team(snake)
            if not on_same_team:
                for pos in snake.body:
                    x, y = get_pos(pos)
                    self.board[x, y] = ENEMY_BODY
                    self.healthmatrix[x, y] = snake.health
                    self.lengthmatrix[x, y] = snake.length
                    self.snakematrix[x, y] = snake
                tail = get_pos(snake.tail)
                #todo: double check this
                if distance(self.me.head, tail) < 2:
                    self.board[tail] = ENEMY_TAIL

            head = get_pos(snake.head)
            self.board[head] = ENEMY_HEAD
            if snake.length >= self.me.length or on_same_team or distance(self.me.head, snake.head) > 2: # todo: double check this condition
                other_snake_moves = self.safe_moves(head)
                for move in other_snake_moves.values():
                    self.board[move] = ENEMY_NEXT_MOVE
                predict.predict_moves(self, snake)

    # load yourself
    def load_me(self, snake):
        for pos in snake.body:
            x, y = get_pos(pos)
            self.board[x, y] = MY_BODY
            self.healthmatrix[x, y] = snake.health
            self.lengthmatrix[x, y] = snake.length
            self.snakematrix[x, y] = snake

        head = get_pos(snake.head)
        tail = get_pos(snake.tail)

        self.snakematrix[head] = snake
        self.snakematrix[tail] = snake
        self.board[head] = MY_HEAD

        if len(snake.body
               ) == snake.length and snake.length > 3 and snake.health < 100:
            return
        else:
            if self.board[tail] == FREE_SPACE:
                self.board[tail] = MY_TAIL

    def load_hazards(self, data):
        for hazard in data['board']['hazards']:
            x, y = get_pos(hazard)
            self.hazards[x, y] = HAZARD

    def safe_moves(self, x, y=None, ignored=[]):
        x, y = get_pos(x, y)
        possible_moves = moves.get_moves(x, y)
        returned_moves = dict()

        for name, move in possible_moves.items():
            if self.is_safe(move, ignored=ignored):
                returned_moves[name] = move
            else:
                continue
        return returned_moves

    def in_bounds(self, x, y=None):
        x, y = get_pos(x, y)
        if x in range(self.width) and y in range(self.height):
            return True
        else:
            return False

    def is_safe(self, x, y=None, ignored=[]):
        x, y = get_pos(x, y)

        if self.in_bounds(x, y):
            contents = self[x, y]
            if contents <= SAFE_SPACE or contents in ignored:
                return True
            else:
                return False
        else:
            return False

    def is_food(self, x, y=None):
        x, y = get_pos(x, y)
        if self[x, y] == FOOD:
            return True
        else:
            return False

    def is_hazard(self, x, y=None):
        x, y = get_pos(x, y)
        if self[x, y] == HAZARD:
            return True
        else:
            return False

    """
    Return the snake at x, y
    """

    def get_snake_at(self, x, y=None):
        x, y = get_pos(x, y)
        return self.snakematrix[x, y]

    """ Is there a snake at (x, y) ? """

    def is_snake_at(self, x, y=None):
        x, y = get_pos(x, y)
        if type(self.get_snake_at(x, y)) == type(Snake(self.data['you'])):
            return True
        else:
            return False

    # return the position of every enemy snake head on the board
    def get_enemy_heads(self):
        heads = []
        for snake in self.snakes.values():
            if snake == self.me:
                continue
            heads.append(snake.head)
        return heads

    # return a list of all snakes on the board
    def get_snakes(self):
        return list(self.snakes.values())

    # return all enemy snakes on the board
    # TODO: ignore squadmates
    def get_enemy_snakes(self):
        snakes = self.get_snakes()
        returned_snakes = []
        for snake in snakes:
            if snake != self.me:
                returned_snakes.append(snake)

    # Is this position on the edge of the board?
    def on_edge(self, x, y=None):
        x, y = get_pos(x, y)
        if 0 in (x, y):
            return True
        elif x == self.width - 1:
            return True
        elif y == self.height - 1:
            return True
        else:
            return False

    def copy(self):
        return Board(self.data)

if __name__ == "__main__":
    with open("example_move.json") as file:
        data = json.load(file)
        board = Board(data)
        print(board.board)
        print(board.hazards)
        print(board.snakes)
        print(board.is_safe(0, 0))
        print(board.snakematrix)
        print(board.is_snake_at(0, 0))
