import collections
import heapq
import localizer


class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        self.width = data['board']['width']
        self.height = data['board']['height']
        self.obstacles = set()  # snake heads and bodies
        self.food = []
        self.heads = []  # [(x,y)] snake heads
        self.weights = {}  # {(x,y): w}
        self.our_snake = data['you']
        self.snakes = data['board']['snakes']

        # init board
        for snake in self.snakes:
            head = snake['body'][0]
            self.heads.append((head['x'], head['y']))

            for point in snake['body']:
                self.obstacles.add((point['x'], point['y']))

        for food in data['board']['food']:
            self.food.append((food['x'], food['y']))

        # init board weight
        # board boders
        for row in range(self.height):
            self.weights[(0, row)] = localizer.BORDERS
            self.weights[(self.width-1, row)] = localizer.BORDERS
        for col in range(self.width):
            self.weights[(col, 0)] = localizer.BORDERS
            self.weights[(col, self.height-1)] = localizer.BORDERS

        # heads
        for snake in self.snakes:
            head = (snake['body'][0]['x'], snake['body'][0]['y'])
            if len(snake['body']) >= len(self.our_snake['body']):
                self.weights[head] = localizer.LONGER_SNAKE_HEAD
            else:
                self.weights[head] = localizer.SHORTER_SNAKE_HEAD

        # remove our tail from obstacles
        # our_tail = (data['you']['body'][-1]['x'], data['you']['body'][-1]['y'])
        # self.obstacles.remove(our_tail)

        # bodies
        for snake_bodies in self.obstacles:
            self.weights[snake_bodies] = localizer.SNAKE_BODIES

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        return id not in self.obstacles

    # possible neighbors around a point
    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return list(results)

    def cost(self, from_node, to_node):
        return self.weights.get(to_node, 1)