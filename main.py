# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing

debug = True
status = True
# board variables
SPACE = 0
KILL_ZONE = 1
FOOD = 2
#MY_HEAD = 3
DANGER = 3
SNAKE_BODY = 4
ENEMY_HEAD = 5
#WALL = 7
directions = ['up', 'left', 'down', 'right']
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
# general variables
game_id = ''
board_width = 0
board_height = 0
# my snake variables
direction = 0
health = 100
turn = 0
survival_min = 50
my_id = ''
INITIAL_FEEDING = 3
state = None
grid = None

# the cell class for storing a* search information
class Cell:
    global board_height, board_width
    def __init__(self, x, y):
        self.f = 0
        self.g = 0
        self.h = 0
        self.x = x
        self.y = y
        self.state = 0;
        self.neighbors = []
        self.previous = None
        if self.x < board_width - 1:
            self.neighbors.append([self.x + 1, self.y])
        if self.x > 0:
            self.neighbors.append([self.x - 1, self.y])
        if self.y < board_height - 1:
            self.neighbors.append([self.x, self.y + 1])
        if self.y > 0:
            self.neighbors.append([self.x, self.y - 1])

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#003333",  # TODO: Choose color
        "head": "tiger-king",  # TODO: Choose head
        "tail": "coffee",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    global direction, directions, board_height, board_width, game_id, health, turn, my_id, state, grid
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    my_id = game_state['you']['id']
    health = game_state['you']['health']
    turn = game_state['turn']
    state = game_state
    survival_min = set_health_min(game_state)
    # if health is below set threshold
    grid = build_map()
    if health < survival_min:
        direction = hungry()
    # if not the biggest snake
    elif not biggest():
        direction = hungry()
    # # if all is well
    else:
        direction = kill_time()
    # print data for debugging
    # if status:
    #     print('REMAINING HEALTH IS ' + str(health) + ' ON TURN ' + str(turn) + '.')
    #     print('SENDING MOVE: ' + str(directions[direction]))
    # end_time = time.time()
    # print('Time for move was ' + str((end_time - start_time) * 1000.0) + 'ms')
    # return next move
    return {
        'move': directions[direction],
    }

# will return the minimum health required to keep alive
# TODO: Consider other ways to determine the bottom line
def set_health_min():
    health_board = max(board_height, board_width) * 2
    health_length = state['you']['length']
    if health_length > health_board:
        return health_length
    return health_board

# return move towards the closest food
def hungry():
    close_food = closest_food()
    move = astar(close_food)
    return move

# follow own tail to kill time
def kill_time():
    if status: print('COOL. KILLING TIME.')
    tail = get_tail()
    move = astar(tail)
    return move

def build_map():
    global my_id, board_height, board_width
    my_length = state['you']['length']
    # create map and fill with SPACEs
    grid = [ [SPACE for col in range(state['board']['height'])] for row in range(state['board']['width'])]
    # fill in food locations
    for food in state['board']['food']:
        grid[food['x']][food['y']] = FOOD
    # fill in snake locations
    for snake in state['board']['snakes']:
        for segment in snake['body']:
            # get each segment from game_state {snakes, game_state, body, game_state}
            grid[segment['x']][segment['y']] = SNAKE_BODY
        # mark snake head locations
        #if debug: print('Snake id = ' + str(snake['id']))
        #if debug: print('My id = ' + str(my_id))
        # mark tails as empty spaces only after turn 3
        # if debug:
        #     if snake['id'] == my_id:
        #         print('-1 body seg: ' + str(snake['body']['data'][-1]['x']) + ',' + str(snake['body']['data'][-1]['y']))
        #         print('-2 body seg: ' + str(snake['body']['data'][-2]['x']) + ',' + str(snake['body']['data'][-2]['y']))
        #if turn > 3:
        # open space from snake's tail
        if snake['body'][-1] != snake['body'][-2]:
            tempX = snake['body'][-1]['x']
            tempY = snake['body'][-1]['y']
            grid[tempX][tempY] = SPACE
        # dont mark own head or own danger zones
        if snake['id'] == my_id: continue
        head = get_coords(snake['head'])
        grid[head[0]][head[1]] = ENEMY_HEAD
        # mark danger locations around enemy head
        head_zone = DANGER
        if snake['length'] < my_length:
            head_zone = KILL_ZONE
        # check up from head    
        if (head[1] + 1 <= board_height - 1):
            if grid[head[0]][head[1] + 1] < head_zone:
                grid[head[0]][head[1] + 1] = head_zone
        # check down from head
        if (head[1] - 1 >= 0):
            if grid[head[0]][head[1] - 1] < head_zone:
                grid[head[0]][head[1] - 1] = head_zone
        # check left from head
        if (head[0] - 1 >= 0):
            if grid[head[0] - 1][head[1]] < head_zone:
                grid[head[0] - 1][head[1]] = head_zone
        # check right from head
        if (head[0] + 1 <= board_width - 1):
            if grid[head[0] + 1][head[1]] < head_zone:
                grid[head[0] + 1][head[1]] = head_zone
    # mark my head location
    #grid[data['you']['body']['data'][0]['x']][data['you']['body']['data'][0]['y']] = 1
    #if debug: print_map(grid)
    return grid
    

# convert object yx to tuple yx
def get_coords (o):
    return (o['x'], o['y'])

# returns if you are not the biggest snake
def biggest():
    my_id = state['you']['id']
    my_length = state['you']['length']
    for snake in state['board']['snakes']:
        if my_id != snake['id']:
            if snake['length'] > my_length:
                return False
    return True

# return coords of closest food to head, using grid
def closest_food():
    my_location = get_coords(state['you']['head'])
    close_food = None
    close_distance = 9999
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == FOOD:
                food = [i, j]
                distance = get_distance(my_location, food)
                if distance < close_distance:
                    close_food = food
                    close_distance = distance
    if (close_food is None):
      return get_tail()
    else:
      return close_food

# return manhattan distance between a and b
def get_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]))

# return coords to own tail
def get_tail():
    body = state['you']['body']
    tail = get_coords(body[-1]) 
    return tail

# astar search, returns move that moves closest to destination
def astar(destination):
    #destination = get_coords(destination)
    search_scores = build_astar_grid()
    open_set = []
    closed_set = []
    # set start location to current head location
    start = get_coords(state['you']['head'])
    # on first 3 moves, point to closest food
    if state['turn'] < INITIAL_FEEDING:
        destination = closest_food()
    open_set.append(start)
    # while openset is NOT empty keep searching
    while open_set:
        lowest_cell = [9999, 9999] # x, y
        lowest_f = 9999
        # find cell with lowest f score
        for cell in open_set:
            if search_scores[cell[0]][cell[1]].f < lowest_f: # CONSIDER CHANGING TO <= AND THEN ALSO COMPARING G SCORES
                lowest_f = search_scores[cell[0]][cell[1]].f
                lowest_cell = cell
        # found path to destination
        
        if lowest_cell[0] == destination[0] and lowest_cell[1] == destination[1]:
            # if status: print('FOUND A PATH!')
            # if debug:
            #     print("astar grid after search success:")
            #     print_f_scores(search_scores)
            # retrace path back to origin to find optimal next move
            temp = lowest_cell
            # if debug:
            #     print('astar start pos: ' + str(start))
            while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                temp = search_scores[temp[0]][temp[1]].previous
            # get direction of next optimal move
            # if debug: print('astar next move: ' + str(temp))
            next_move = calculate_direction(start, temp)
            return next_move
        # else continue searching
        current = lowest_cell
        current_cell = search_scores[current[0]][current[1]]
        # update sets
        open_set.remove(lowest_cell)
        closed_set.append(current)
        # check every viable neighbor to current cell
        for neighbor in search_scores[current[0]][current[1]].neighbors:
            neighbor_cell = search_scores[neighbor[0]][neighbor[1]]
            if neighbor[0] == destination[0] and neighbor[1] == destination[1]:
                if status: print('FOUND A PATH! (neighbor)')
                neighbor_cell.previous = current
                if debug:
                    print("astar grid after search success:")
                    # print_f_scores(search_scores)
                # retrace path back to origin to find optimal next move
                temp = neighbor
                if debug:
                    print('astar start pos: ' + str(start))
                while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                    temp = search_scores[temp[0]][temp[1]].previous
                # get direction of next optimal move
                if debug: print('astar next move: ' + str(temp))
                next_move = calculate_direction(start, temp)
                return best_move(next_move)
            # check if neighbor can be moved to
            if neighbor_cell.state < SNAKE_BODY:
                # check if neighbor has already been evaluated
                if neighbor not in closed_set:# and grid[neighbor[0]][neighbor[1]] <= FOOD:
                    temp_g = current_cell.g + 1
                    shorter = True
                    # check if already evaluated with lower g score
                    if neighbor in open_set:
                        if temp_g > neighbor_cell.g: # CHANGE TO >= ??
                            shorter = False
                    # if not in either set, add to open set
                    else:
                        #if debug: print('neighbor: ' + str(grid[neighbor[0]][neighbor[1]]))
                        open_set.append(neighbor)
                    # this is the current best path, record it
                    if shorter:
                        neighbor_cell.g = temp_g
                        neighbor_cell.h = get_distance(neighbor, destination)
                        neighbor_cell.f = neighbor_cell.g + neighbor_cell.h
                        neighbor_cell.previous = current
        # inside for neighbor
    # inside while open_set
    # if reach this point and open set is empty, no path
    if not open_set:
        # if status: print('COULD NOT FIND PATH!')
        if debug:
            print("astar grid after search failure:")
            # print_f_scores(search_scores)

        move = 2
        # if mode == 'food':
        #     tail = get_tail(game_state)
        #     move = astar(game_state, grid, tail)
        
        return best_move(move)

# return grid of empty Cells for astar search game_state
def build_astar_grid():
    w = state['board']['width']
    h = state['board']['height']
    astar_grid = [ [Cell(row, col) for col in range(h)] for row in range(w)]
    for i in range(w):
        for j in range(h):
            astar_grid[i][j].state = grid[i][j]
    return astar_grid

# return direction from a to b
def calculate_direction(a, b):
    # if status: print('CALCULATING NEXT MOVE...')
    x = a[0] - b[0]
    y = a[1] - b[1]
    direction = 0
    # directions = ['up', 'left', 'down', 'right']
    if x < 0:
        direction = RIGHT
    elif x > 0:
        direction = LEFT
    elif y < 0:
        direction = UP
    count = 0
    if not valid_move(direction):
        if count == 3:
            if status:
                print('DEAD END, NO VALID MOVE REMAINING!')
                print('GAME OVER')
            return direction
        count += 1
        direction += 1
        if direction == 4:
            direction = 0
    return direction

# check if move in direction will kill you
# return True if valid
# return False if it will kill you
def valid_move(d):
    global board_height, board_width
    current = get_coords(state['you']['head'])
    # if status: print('CHECKING IF MOVE IS VALID!')
    # directions = ['up', 'left', 'down', 'right']
    # check up direction
    if d == DOWN:
        if current[1] - 1 < 0:
            if debug: print('Down move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] - 1] < DANGER:
            if debug: print('Down move is VALID.')
            return True
        else:
            if debug: print('Down move is FATAL!')
            return False
    #check left direction
    if d == LEFT:
        if current[0] - 1 < 0:
            if debug: print('Left move is OFF THE MAP!')
            return False
        if grid[current[0] - 1][current[1]] < DANGER:
            if debug: print('Left move is VALID.')
            return True
        else:
            if debug: print('Left move is FATAL!')
            return False
    # check up direction
    if d == UP:
        if current[1] + 1 > board_height - 1:
            if debug: print('Up move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] + 1] < DANGER:
            if debug: print('Up move is VALID.')
            return True
        else:
            if debug: print('Up move is FATAL!')
            return False
    # check right direction
    if d == RIGHT:
        if current[0] + 1 > board_width - 1:
            if debug: print('Right move is OFF THE MAP!')
            return False
        if grid[current[0] + 1][current[1]] < DANGER:
            if debug: print('Right move is VALID.')
            return True
        else:
            if debug: print('Right move is FATAL!')
            return False
    # failsafe
    if d > 3 and status: print('valid_move FAILED! direction IS NOT ONE OF FOUR POSSIBLE MOVES!')
    return True

def best_move(recommended_move):
    global board_height, board_width
    if status: print('CHECKING FOR BEST MOVE...')

    reg_moves = []
    danger_moves = []
    kill_moves = []
    current = get_coords(state['you']['head'])
    best_move = []
    # check DOWN move
    if current[1] - 1 >= 0 and grid[current[0]][current[1] - 1] <= DANGER:
        if debug: print('move DOWN is viable')
        reg_moves.append(DOWN)
    # check UP move
    if current[1] + 1 < board_height and grid[current[0]][current[1] + 1] <= DANGER:
        if debug: print('move UP is viable')
        reg_moves.append(UP)
    # check LEFT move
    if current[0] - 1 >= 0 and grid[current[0] - 1][current[1]] <= DANGER:
        if debug: print('move LEFT is viable')
        reg_moves.append(LEFT)
    # check RIGHT move
    if current[0] + 1 < board_width and grid[current[0] + 1][current[1]] <= DANGER:
        if debug: print('move RIGHT is viable')
        reg_moves.append(RIGHT)
    # check viable moves for a move better than DANGER
    if reg_moves:
        for move in reg_moves:
            # DOWN
            if move == DOWN:
                if grid[current[0]][current[1] - 1] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0]][current[1] - 1] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # UP
            elif move == UP:
                if grid[current[0]][current[1] + 1] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0]][current[1] + 1] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # LEFT
            elif move == LEFT:
                if grid[current[0] - 1][current[1]] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0] - 1][current[1]] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # RIGHT
            elif move == RIGHT:
                if grid[current[0] + 1][current[1]] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0] + 1][current[1]] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
    else: # NO MOVE AT ALL
        if status:
            print('DEAD END, NO VALID MOVE REMAINING! (none at all)')
            print('GAME OVER')
        return recommended_move # suicide

    # if a kill move exists, pick the best one
    if kill_moves:
        # if all moves are kill moves, take reccommended move
        if len(kill_moves) >= 3 and recommended_move in kill_moves:
            if debug: print('ALL MOVES ARE KILL MOVES, TAKING RECCOMMENDED MOVE!')
            return recommended_move
        # otherwise calculate best kill move
        if status: print('KILL move exists!')
        best_move = recommended_move
        # best_area = 0
        # check recommended_move first
        if valid_move(recommended_move):
            best_move = recommended_move
            # best_area = look_ahead(recommended_move, grid, data)
        best_move = kill_moves[0]
        # check every other kill move
        # for move in kill_moves:
        #     # if the move contains your tail, its probably a pretty good move
        #     if move_contains_tail(move, grid, data):
        #         return move
        #     # check available area of move
        #     new_area = look_ahead(move, grid, data)
        #     if new_area > best_area:
        #         best_area = new_area
        #         best_move = move
        return best_move
    # if a non-DANGER move exists, calculate the best one
    elif reg_moves:
        # if ALL moves are reg, take reccommended move
        if status: print(str(len(reg_moves)) + ' VIABLE move(s) exist!')
        if len(reg_moves) >= 3 and recommended_move in reg_moves:
            if debug: print('ALL MOVES VALID, TAKING RECCOMMENDED MOVE!')
            return recommended_move
        # otherwise calulate the best reg move
        best_move = recommended_move
        best_area = 0
        # check reccommended move first
        if valid_move(recommended_move):
            best_move = recommended_move
            best_area = look_ahead(recommended_move)
        # check every other reg move
        for move in reg_moves:
            # if the move contains your tail, its probably a pretty good move
            #if move_contains_tail(move, grid, data):
                #return move
            # check available area of move
            new_area = look_ahead(move)
            if new_area > best_area:
                best_area = new_area
                best_move = move
        return best_move

    # if only DANGER moves exist, calculate best one
    elif danger_moves:
        # if ALL moves are DANGER, take recommended_move
        if len(danger_moves) >= 3: return recommended_move
        if status: print('No VIABLE move, only DANGER moves exist!')
        best_move = recommended_move
        best_area = 0
        # check reccommended move first
        if valid_move(recommended_move):
            best_move = recommended_move
            best_area = look_ahead(recommended_move)
        for move in danger_moves:
            # check available area of move
            new_area = look_ahead(move)
            if new_area > best_area:
                best_area = new_area
                best_move = move
        return best_move
    else: # NO MOVE AT ALL
        if status:
            print('DEAD END, NO VALID MOVE REMAINING! (bottom)')
            print('GAME OVER')
        return recommended_move # suicide

def look_ahead(move):
    area = 0
    current = get_coords(state['you']['head'])
    # get move coords
    given_move_coords = current
    if move == UP:
        given_move_coords = [current[0], current[1] + 1]
    elif move == DOWN:
        given_move_coords = [current[0], current[1] - 1]
    elif move == LEFT:
        given_move_coords = [current[0] - 1, current[1]]
    elif move == RIGHT:
        given_move_coords = [current[0] + 1, current[1]]
    move_queue = []
    checked_moves = []
    # start with given move
    move_queue.append(given_move_coords)
    # mark current as checked
    checked_moves.append(current)
    # iterate over all possible moves given initial move
    while move_queue:
        for next_move in move_queue:
            # next move is assessed
            area += 1
            #if debug: test_grid[next_move[0]][next_move[1]] = 7 #<##
            move_queue.remove(next_move)
            checked_moves.append(next_move)
            # check neighbors
            # check UP move
            neighbor_up = [next_move[0], next_move[1] + 1]
            # if not already checked, or queued to be checked
            if neighbor_up != current and neighbor_up not in checked_moves and neighbor_up not in move_queue:
                # if move on board
                if neighbor_up[1] < board_height:
                    # if move is valid
                        if grid[neighbor_up[0]][neighbor_up[1]] <= DANGER:
                            move_queue.append(neighbor_up)
            # check DOWN move
            neighbor_down = [next_move[0], next_move[1] - 1]
            # if not already checked, or queued to be checked
            if neighbor_down != current and neighbor_down not in checked_moves and neighbor_down not in move_queue:
                # if move on board
                if neighbor_down[1] >= 0:
                    # if move is valid
                        if grid[neighbor_down[0]][neighbor_down[1]] <= DANGER:
                            move_queue.append(neighbor_down)
            # check LEFT move
            neighbor_left = [next_move[0] - 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_left != current and neighbor_left not in checked_moves and neighbor_left not in move_queue:
                # if move on board
                if neighbor_left[0] >= 0:
                    # if move is valid
                        if grid[neighbor_left[0]][neighbor_left[1]] <= DANGER:
                            move_queue.append(neighbor_left)
            # check RIGHT move
            neighbor_right = [next_move[0] + 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_right != current and neighbor_right not in checked_moves and neighbor_right not in move_queue:
                # if move on board
                if neighbor_right[0] < board_width:
                    # if move is valid
                        if grid[neighbor_right[0]][neighbor_right[1]] <= DANGER: # <<<<<<<< failing
                            move_queue.append(neighbor_right)
    # if debug:
    #     print('test grid after traversal:')
    #     print_map(test_grid)
    return area

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
