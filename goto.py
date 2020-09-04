from util import get_pos, distance, directions
import board

# find food you can get to before anyone else can:
def find_food(board, pos, possible_moves):
    print(pos)
    x, y = get_pos(pos)
    return goto_nearest_target(board, x, y, possible_moves, board.food)

# goto the nearest target in a list of targets
def goto_nearest_target(board, x, y, possible_moves, targets):
    my_head = board.me.head
    target_distances = [] # the distances from your head to each target
    
    for target in targets:
        target_distances.append(distance(my_head, target))
    
    target_distances.sort()
    targets.sort(key=lambda target: distance(my_head, target))
    
    while len(targets) > 0:
        my_distance = target_distances[0]
        target = targets[0]
        if not is_closer_snake(board, my_distance, target):
            moves_to_food = directions(my_head, target)
            for move in moves_to_food:
                if move in possible_moves:
                    return move
        del targets[0]
        del target_distances[0]
            
    return ""
    


"""
Is another snake closer to the target (i.e., a piece of food) than you
(don't bother going for it in that case)
"""
def is_closer_snake(board, my_dist, target):
    
    for head in board.get_enemy_heads():
        print(head)
        if head == board.me.head:
            continue
        dist = distance(head, target)
        print(dist, my_dist)
        if dist < my_dist: # another snake could get there sooner
            print("closer snake")
            return True
        elif dist == my_dist:
            if snake.length >= my_snake.length:
                return True
            
    return False
