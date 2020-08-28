
from util import get_pos

class Snake:
    def __init__(self, data, is_you=False, is_alive=True):
        self.snake_id = data['id']
        self.name = data['name']
        self.health = data['health']
        
        self.head = get_pos(data['head'])#create_point(head, contents=ENEMY_SNAKE_HEAD, parent_object=self)
        self.body = []
        for pos in data['body']:
            self.body.append(get_pos(pos))
        self.tail = get_pos(data['body'][-1])
        self.length = data['length']
        self.shout = data['shout']
        self.is_you = is_you
        self.is_alive = is_alive
        
        self.move_hist = []
    
    def __str__(self):
        return self.name
    
    def __len__(self):
        return len(body)
    def __eq__(self, other):
        if self.snake_id == other.snake_id:
            return True
        else:
            return False
    def me(self):
        return self.is_you
    def alive(self):
        return self.is_alive