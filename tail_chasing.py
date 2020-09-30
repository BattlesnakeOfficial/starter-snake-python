"""
Code for implementing tail chasing

"""
import flood_fill
import behaviour
import moves

def tail_chase(board, me, ignored=[]):
    curr_pos = me.head
    returned_moves = dict()

    #if me.health < 10:
    #    hunt_food = True # change this back to true later
    
    possible_moves = behaviour.search_for_moves(board, curr_pos, ignored)
    # change health threshold back to 30 later
    if me.is_full_length and (me.health >= 10 or len(possible_moves)==0): #me.health < 100:
        possible_moves = moves.get_moves(curr_pos)
        for name, move in possible_moves.items():
            if move == me.tail:
                return name
    space_per_direction, surroundings_per_direction, available_spaces_per_direction = flood_fill.compare_moves(board, curr_pos, possible_moves, ignored)

    if should_follow_tail(board, curr_pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
        for name, space in space_per_direction.items():
            my_tail = board.me.tail
            if my_tail in surroundings_per_direction[name] or my_tail in available_spaces_per_direction[name]:
                returned_moves[name] = possible_moves[name]
                continue


# return True if the snake should follow its own tail,
# False otherwise
def should_follow_tail(board, pos, space_per_direction, surroundings_per_direction, available_spaces_per_direction, possible_moves, ignored):
    return True