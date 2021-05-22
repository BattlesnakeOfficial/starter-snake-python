import os
import random
import json
import numpy
import cherrypy
from termcolor import colored
import pathfind
import calculations

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "Lawrence Zhang",
            "color": "#00FF74",
            "head": "evil", 
            "tail": "curled",  
        }
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json
        global xSize
        global ySize
        xSize = data['board']['height']
        ySize = data['board']['width']
        global boardData
        boardData = [ [0] * xSize for _ in range(ySize)]
        print(numpy.matrix(boardData))
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        global xHead
        global yHead
        global head
        global Food
        Food = []
            

        #----------------------
        #Board Generation Data
        boardData = [ [0] * xSize for _ in range(ySize)]
        data = cherrypy.request.json
        snakeList = data['board']['snakes']

        for i in data['board']['food']:
            boardData[xSize - 1 - i['y']][i['x']] = 0
            Food.append((xSize - 1 - i['y'],i['x']))



        for x in snakeList:
            body = x['body']
            head = x['head']

            
            for y in body:
                boardData[xSize - 1 - y['y']][y['x']] = 1
            boardData[xSize - 1 - head['y']][head['x']] = 1
            xHead = head['x']
            yHead = xSize - 1 - head['y']
            
        print("-----------\nSTATE UPDATED:")
        print(numpy.matrix(boardData))
        print("-----------")
        #---------------------


        # Choose a random direction to move in
        path = pathfind.astar(boardData, (yHead,xHead), calculations.distanceSort(xHead,yHead,Food)[0])
        print(colored("Path is: ","cyan"))
        print(colored(path,'yellow'))
        print("head: " + str(xHead) + " " + str(yHead))
        print(colored("TARGET MOVE:","cyan"))
        print(path[1])
        moves = []
        print(colored("MOVES LIST: ","cyan"))
        target = path[1]
        if target[1] > xHead:
            print(colored("right","yellow"))
            moves.append('right')
        if target[1] < xHead:
            print(colored("left","yellow"))
            moves.append('left')
        if target[0] > yHead:
            print(colored("down","yellow"))
            moves.append('down')
        if target[0] < yHead:
            print(colored("up","yellow"))
            moves.append('up')





        for action in moves:
            if action == 'left':
                if boardData[yHead][xHead - 1] == 1 or xHead - 1 < 0:
                    print(colored("Illegal move: LEFT removed","red"))
                    moves.remove('left')
            elif action == 'right':
                if boardData[yHead][xHead + 1] == 1 or xHead + 1 > xSize:
                    print(colored("Illegal move: RIGHT removed","red"))
                    moves.remove('right')
            elif action == 'up':
                if boardData[yHead - 1][xHead] == 1 or yHead - 1 < 0:
                    print(colored("Illegal move: UP removed","red"))
                    moves.remove('up')
            elif action == 'down':
                if boardData[yHead + 1][xHead] == 1 or yHead + 1 > ySize:
                    print(colored("Illegal move: DOWN removed","red"))
                    moves.remove('down')



        return {"move": moves[0]}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
    #    data = cherrypy.request.json
    #    print(data)
        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
