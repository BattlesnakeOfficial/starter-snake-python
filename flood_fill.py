import board
import numpy as np

def compare_moves(board, pos, possible_moves, ignored=[]):

def flood_fill(board, pos, ignored=[]):
    free_space = 0
    board_copy = board.copy()
    available_spaces = []

    queue = [pos]

    while len(queue) > 0:
        