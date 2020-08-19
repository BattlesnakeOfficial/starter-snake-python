<<<<<<< HEAD
import json
import numpy as np 

from constants import FREE_SPACE, FOOD, SAFE_SPACE, HAZARD

class Board:
  def __init__(self, data):

    self.width = data['board']['width']
    self.height = data['board']['height']

    self.board = np.zeros((self.width, self.height), dtype=np.int16)
    self.hazards = np.zeros((self.width, self.height), dtype=np.int16)
    self.load_hazards(data)

  def __getitem__(self, index):
    return self.board[index]
  def process_board(self, data):
    for food in data['board']['food']:
      self.board[self.load_coordinates(food)] = FOOD
  def load_hazards(self, data):
    for hazard in data['board']['hazards']:
      x, y = self.load_coardinates(hazard)
      self.hazards[x, y] = HAZARD
  
  def load_coordinates(self, pos):
    x = pos['x']
    y = pos['y']
    return x, y
  def get_coordinates(self, x, y=None):
    if type(x) == type(tuple()):
      x, y = x
    return x, y

  def in_bounds(self, x, y=None):
    x, y = self.get_coordinates(x, y)
    if x in range(self.width) and y in range(self.height):
      return True
    else:
      return False

  def is_safe(self, x, y=None):
    x, y = self.get_coordinates(x, y)
    if self.in_bounds(x, y) and self[x, y] <= SAFE_SPACE:
      return True
    else:
      return False
  

  def is_food(self, x, y=None):
    x, y = self.get_coordinates(x, y)
    if self[x, y] == FOOD:
      return True
    else:
      return False
  
  def is_hazard(self, x, y=None):
    x, y = self.get_coordinates(x, y)
    if self[x, y] == HAZARD:
      return True
    else:
      return False


if __name__ == "__main__":
  with open("example_move.json") as file:
    data = json.load(file)
    board = Board(data)
    print(board.hazards)
=======
"""
Game Board logic
"""

class Board:
  def __init__(self, data):
    pass
>>>>>>> origin/master
