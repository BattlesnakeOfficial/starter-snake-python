"""
Code for implementing tail chasing

"""
import flood_fill
import behaviour
import moves

def tail_chase(board, curr_pos, possible_moves, 
            space_per_direction, 
            surroundings_per_direction,available_spaces_per_direction, 
            ignored=[]):
    me = board.me
    curr_pos = me.head
    returned_moves = dict()
    
    possible_moves = behaviour.search_for_moves(board, curr_pos, ignored)

    if should_follow_tail(board, curr_pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
        for name, space in space_per_direction.items():
            my_tail = board.me.tail
            if my_tail in surroundings_per_direction[name] or my_tail in available_spaces_per_direction[name]:
                returned_moves[name] = possible_moves[name]
                continue
    if me.is_full_length: 
        for name, move in moves.get_moves(curr_pos).items():
            if move == me.tail:
                returned_moves[name] = move
    return returned_moves


# return True if the snake should follow its own tail,
# False otherwise
def should_follow_tail(board, pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
    return True