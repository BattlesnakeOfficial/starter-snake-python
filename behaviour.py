from board import Board
import collision_avoidance
import moves
import random
import flood_fill
import constants
import util
import goto
import tail_chasing

# define the snake's behaviour
def snake_behaviour(data):
    hunt_food = True # change this back to true later
    board = Board(data)
    me = board.me
    curr_pos = board.me.head
    
    
    
    
    possible_moves = search_for_moves(board, curr_pos)
    
    # follow enemy tail if no other options exist
    if len(possible_moves) == 0:
        returned_moves = search_for_moves(
            board, curr_pos, ignored=[constants.MY_TAIL,constants.ENEMY_TAIL])
        for name, move in returned_moves.values():
            snake = board.get_snake_at(move)
            if snake.is_full_length: #len(snake.body) == snake.length and 
                possible_moves[name] = move

    # move into possible enemy next move if necessary
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(
            board, curr_pos, ignored=[constants.ENEMY_MOVE_2])
        hunt_food = False # don't hunt for food in this situation
    # move into possible enemy next move if necessary
    if len(possible_moves) == 0:
        possible_moves = search_for_moves(
            board, curr_pos, ignored=[constants.ENEMY_NEXT_MOVE, constants.ENEMY_MOVE_2])
        hunt_food = False # don't hunt for food in this situation

    move = None
    # if only one move if possible, return it
    if len(possible_moves) == 1:
        move = moves.pick_move(possible_moves)
        return move
    # look for food, if I should do that now
    if hunt_food and len(possible_moves) > 0 and eat_food(board, possible_moves):
        move = goto.find_food(board, curr_pos, possible_moves)
    # pick a random safe move
    if len(possible_moves) > 0 and move == None:
        move = moves.pick_move(possible_moves)
    # if no safe moves are possible, pick a random move to avoid errors
    if move == None:
        move = random.choice(moves.all_moves())
    return move


# find possible moves to make from your current position
def search_for_moves(board, curr_pos, ignored=[]):
    possible_moves = board.safe_moves(curr_pos, ignored=ignored)

    space_per_direction, surroundings_per_direction, available_spaces_per_direction = flood_fill.compare_moves(board, curr_pos, possible_moves, ignored)
    
    returned_moves = tail_chasing.tail_chase(board, curr_pos, possible_moves, 
            space_per_direction, 
            surroundings_per_direction,available_spaces_per_direction, 
            ignored=ignored)
    if len(returned_moves) > 0:
        return returned_moves

    if len(possible_moves) > 1:
        possible_moves = flood_fill.select_roomiest_moves(
            board, curr_pos, possible_moves, 
            space_per_direction, 
            surroundings_per_direction,available_spaces_per_direction, 
            ignored=ignored)

    return possible_moves


# Should I eat Food?
def eat_food(board, possible_moves):
    return True
