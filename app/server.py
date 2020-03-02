#imports
import json
import os
import math
import random
import bottle
from bottle import HTTPResponse

#global variables
board_width = board_height = 0
segments = [] #list of x and y positions of snake
fruits = [] #list of x and y positions of fruit
rivals = [] #list of x and y positions of segments of rivals
directions = ['up','down','left','right']
weights = [0,0,0,0] #weighted numbers from (-5,5) corresponding to directions
health = 100

caution = 0 #used in survive() -> avoid_self()
hysteria = 0 #used in thrive() -> find_fruit(), move_to_fruits()

@bottle.route("/")
def index():
	return "Battlesnake is alive"
	
@bottle.post("/ping")
def ping():
	"""
	Used by the Battlesnake Engine to make sure your snake is still working.
	"""
	return HTTPResponse(status=200)
	
@bottle.post("/start")
def start():
	"""
	Called every time a new Battlesnake game starts and your snake is in it.
	Your response will control how your snake is displayed on the board.
	"""
	data = bottle.request.json
	
	#get width and height of board
	global board_width, board_height
	board_width = data["board"]["width"]
	board_height = data["board"]["height"]
	
	#send snake customization
	response = {
		"color": "#CC9900",
		"headType": "safe",
		"tailType": "bolt"
		}
		
	return HTTPResponse(
		status=200,
		headers={"Content-Type": "application/json"},
		body=json.dumps(response),
	)
	
@bottle.post("/move")
def move():
	"""
	Called when the Battlesnake Engine needs to know your next move.
	The data parameter will contain information about the board.
	Your response must include your move of up, down, left, or right.
	"""
	data = bottle.request.json
	
	#update values
	global weights, directions, segments, fruits, id, health
	segments.clear()
	fruits.clear()
	rivals.clear()
	health = data["you"]["health"]
	#segments
	for s in data["you"]["body"]:
		current = [s['x'],s['y']]
		segments.append(current)
	#fruits
	for f in data["board"]["food"]:
		current = [f['x'],f['y']]
		fruits.append(current)
	#rivals
	for r in data["board"]["snakes"]:
		cur_r = []
		if r["id"] != data["you"]["id"]: #don't add yourself to the rivals list
			for c in r["body"]:
				cur_s = [c['x'],c['y']]
				cur_r.append(cur_s)
		if cur_r != []: #don't add empty rivals
			rivals.append(cur_r)
	#reset weights
	weights = [0,0,0,0]
	
	'''telemetry'''
	print("turn:",data["turn"],"with snake",data["you"]["name"])
	print("health:",health)
	
	#print("segments:",segments)
	#print("fruits:",fruits)
	#print("rivals:",rivals)
	
	
	survive()
	thrive()
	
	i = weights.index(max(weights))
	move = directions[i]
	
	shout = "I'm a python snake!"
	
	response = {"move": move, "shout": shout}
	return HTTPResponse(
		status=200,
		headers={"Content-Type": "application/json"},
		body=json.dumps(response),
	)

@bottle.post("/end")
def end():
	"""
	Called every time a game with your snake in it ends.
	"""
	data = bottle.request.json
	
	print("final size",len(segments))
	
	#print("END:", json.dumps(data))
	return HTTPResponse(status=200)

	
	
	
	
	
	
	
	
'''#####HELPER FUNCTIONS#####'''	
def survive():
	"""
	Defense/discouragement function.
	Discourages the snake from making decisions that will:
		- cause death by wall collision
		- cause death by body collision
		- cause death by rival collision
	Does not stop death by starvation.
	"""
	print("SURVIVAL:")
	global caution, weights
	
	avoid_walls(1)
	avoid_rival(1)
	if (caution):
		avoid_walls(2)
		avoid_rival(2)
		
	avoid_self(1,caution)
	if (len(segments) >= 4): avoid_self(2,caution)
	if (len(segments) >= 9): avoid_self(3,caution)
	if (len(segments) >= 2*board_width) or (len(segments) >= 2*board_height):
		caution = 1
		avoid_self(4,caution)
	
	print(weights)
	print("END SURVIVAL")
		

def avoid_walls(n):
	"""
	heavily discourage hitting walls.
	n is a radius around which to check for wall collision.
	it also serves as a way to minimize penalty for walls that are far away and vice versa.
	"""
	penalty = 9 - 3.5*n #penalty function
	
	global segments, weights
	head_x = segments[0][0]
	head_y = segments[0][1]
	
	if (head_x-n == -1):			#going left
		weights[2] -= penalty
		print(n,"moves away from wall on left, lowering left to",weights[2],"by",penalty)
	elif (head_x+n == board_width): #going right
		weights[3] -= penalty
		print(n,"moves away from wall on right, lowering right to",weights[3],"by",penalty)
	if (head_y-n == -1):			#going up
		weights[0] -= penalty
		print(n,"moves away from wall on up, lowering up to",weights[0],"by",penalty)
	elif (head_y+n == board_height):#going down
		weights[1] -= penalty
		print(n,"moves away from wall on down, lowering down to",weights[1],"by",penalty)
	
def avoid_self(n,c):
	"""
	discourage running into own snake.
	n is a radius around which to check for collision.
	c is 'caution', when activated 
	"""
	penalty = (4 + 2*c) - n	#penalty function
	
	global segments, weights
	head_x = segments[0][0]
	head_y = segments[0][1]
	
	for s in segments[:len(segments)-1]:	#check every segment of body
		if (head_y == s[1]):			#if head is on the same y-axis
			if (head_x-n == s[0]):		#going left
				weights[2] -= penalty
				print(n,"moves away from segment on left, lowering left to",weights[2],"by",penalty)
			elif (head_x+n == s[0]): 	#going right
				weights[3] -= penalty
				print(n,"moves away from segment on right, lowering right to",weights[3],"by",penalty)
		elif (head_x == s[0]):			#if head is on the same x-axis
			if (head_y-n == s[1]):		#going up
				weights[0] -= penalty
				print(n,"moves away from segment on up, lowering up to",weights[0],"by",penalty)
			elif (head_y+n == s[1]):	#going down
				weights[1] -= penalty
				print(n,"moves away from segment on down, lowering down to",weights[1],"by",penalty)
			
def avoid_rival(n):
	"""
	heavily discourage running into rival segments (except for their heads)
	n is a radius around which to check for collision
	"""
	penalty = 7 - 4*n	#penalty function
	
	global segments, weights, rivals
	head_x = segments[0][0]
	head_y = segments[0][1]
	
	for rival in rivals:
		if len(rival) > len(segments):
			scared = 1
		else:
			scared = 0
		for s in rival[scared:len(rival)-1]:
			if (head_y == s[1]):			#if head is on the same y-axis
				if (head_x-n == s[0]):		#going left
					weights[2] -= penalty
					print(n,"moves away from enemy segment on left, lowering left to",weights[2],"by",penalty)
				elif (head_x+n == s[0]): 	#going right
					weights[3] -= penalty
					print(n,"moves away from enemy segment on right, lowering right to",weights[3],"by",penalty)
			elif (head_x == s[0]):			#if head is on the same x-axis
				if (head_y-n == s[1]):		#going up
					weights[0] -= penalty
					print(n,"moves away from enemy segment on up, lowering up to",weights[0],"by",penalty)
				elif (head_y+n == s[1]):	#going down
					weights[1] -= penalty
					print(n,"moves away from enemy segment on down, lowering down to",weights[1],"by",penalty)
	
def thrive():
	"""
	Offensive/encouragement function.
	Encourages the snake to make decisions that:
		- Lead it closer to the closest fruit
		- Lead it closer to larger concentrations of fruit
		- Lead it closer to vulnerable snakes' heads
	"""
	print("THRIVE:")
	global hysteria, health, weights
	
	if (health < 75 and health > 50): move_to_fruits()
	if (health < 50): find_fruit()
	
	
	
	#attack()
	
	print(weights)
	print("END THRIVE")
	
def find_fruit():
	"""
	heavily encourages finding closest fruit to the head.
	"""
	award = 3.1		#award function
	global segments, weights, fruits
	head_x = segments[0][0]
	head_y = segments[0][1]
	
	#find closest fruit
	min = fruits[0][0]+fruits[0][1];
	index = 0;
	for f in fruits[1:]:
		close_x = abs(head_x - f[0])
		close_y = abs(head_y - f[1])
		i = close_x + close_y
		if (i < min):
			min = i;
			index = fruits.index([f[0],f[1]])
	
	#encourage movement towards closest fruit
	dist_x = head_x - fruits[index][0]
	dist_y = head_y - fruits[index][1]
	if dist_x > 0:
		weights[2] += award
		print("need to get to food, raising left to",weights[2],"by",award)
	elif dist_x < 0:
		weights[3] += award
		print("need to get to food, raising right to",weights[3],"by",award)
	if dist_y > 0:
		weights[0] += award
		print("need to get to food, raising up to",weights[0],"by",award)
	elif dist_y < 0:
		weights [1] += award
		print("need to get to food, raising down to",weights[2],"by",award)
			
def move_to_fruits():
	"""
	encourages moving towards larger concentrations of fruit.
	n is the radius around which to search
	"""
	global weights, segments, fruits
	award = round(2*(1/len(fruits)),2)	#award function
	head_x = segments[0][0]
	head_y = segments[0][1]
	
	f_left, f_right, f_up, f_down = 0,0,0,0
	
	for f in fruits:
		if f[0] > (board_width/2):
			f_right += 1
		else:
			f_left += 1
		if f[1] > (board_height/2):
			f_down += 1
		else:
			f_up += 1
			
	if (f_left > f_right):
		weights[2] += award
		weights[3] -= award
		print("smell food, raising left to",weights[2],"by",award)
	else:
		weights[3] += award
		weights[2] -= award
		print("smell food, raising right to",weights[3],"by",award)
	if (f_up > f_down):
		weights[0] += award
		weights[1] -= award
		print("smell food, raising up to",weights[0],"by",award)
	else:
		weights[1] += award
		weights[0] -= award
		print("smell food, raising down to",weights[1],"by",award)
	
def main():
	bottle.run(
		application,
		host=os.getenv("IP", "0.0.0.0"),
		port=os.getenv("PORT", "8080"),
		debug=os.getenv("DEBUG", True),
	)


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
	main()
