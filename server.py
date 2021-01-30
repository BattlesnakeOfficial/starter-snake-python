import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python and was based on the starter snake from battlesnake official
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
class Board(object):
    def __init__(self, maxx, maxy):
      self.board=[[{"visited":False,"snake":False} for i in range(maxx)] for j in range(maxy)]
      self.maxx=maxx
      self.maxy=maxy
      return
    def snake(self,snake_piece):
      self.board[snake_piece["x"]][snake_piece["y"]]["snake"]=True
      
      return

    def check(self,move,head,length):
      moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
      to_visite=[{"x":(moves_ressult.get(move)["x"]+head["x"]),"y":(moves_ressult.get(move)["y"]+head["y"])}]
    
      self.board[to_visite[0]["x"]][to_visite[0]["y"]]["visited"]= False
      visited_stack=[]
      while len(visited_stack)<=length:
        if len(to_visite)==0:
          return {"wontTrap":False,"visited":len(visited_stack), "move":move}
        tempPlace=to_visite.pop(0)
        visited_stack.append(tempPlace)
        if (tempPlace["y"]+1)<self.maxy:
          if not self.board[tempPlace["x"]][tempPlace["y"]+1]["visited"] and not self.board[tempPlace["x"]][tempPlace["y"]+1]["snake"]:
            self.board[tempPlace["x"]][tempPlace["y"]+1]["visited"]= True
            to_visite.append({"x":tempPlace["x"],"y":tempPlace["y"]+1})
        if (tempPlace["y"]-1)>=0:
          if not self.board[tempPlace["x"]][tempPlace["y"]-1]["visited"] and not self.board[tempPlace["x"]][tempPlace["y"]-1]["snake"]:
            self.board[tempPlace["x"]][tempPlace["y"]-1]["visited"]= True
            to_visite.append({"x":tempPlace["x"],"y":tempPlace["y"]-1})
        if (tempPlace["x"]+1)<self.maxx:
          if not self.board[tempPlace["x"]+1][tempPlace["y"]]["visited"] and not self.board[tempPlace["x"]+1][tempPlace["y"]]["snake"]:
            self.board[tempPlace["x"]+1][tempPlace["y"]]["visited"]= True
            to_visite.append({"x":tempPlace["x"]+1,"y":tempPlace["y"]})
        if (tempPlace["x"]-1)>=0:
          if not self.board[tempPlace["x"]-1][tempPlace["y"]]["visited"] and not self.board[tempPlace["x"]-1][tempPlace["y"]]["snake"]:
            self.board[tempPlace["x"]-1][tempPlace["y"]]["visited"]= True
            to_visite.append({"x":tempPlace["x"]-1,"y":tempPlace["y"]})
      return {"wontTrap":True,"visited":0, "move":move}


    def printboard(self):
      print(self.board)
      return

class Battlesnake(object):
    board= Board(0,0)
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "bobfrit",  
            "color": "#80c1ff", 
            "head": "silly",  
            "tail": "bolt", 
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json
        head = data["you"]["head"]
        self.board = Board(data["board"]["width"],data["board"]["height"])
        possible_moves = ["up", "down", "left", "right"]
        tryMoves=possible_moves
        board_sanke_death_move=self.clashWithHead(head)
        remove_move=self.outOfBoardMove()+self.crashIntoSnake(head)
        remove_move.extend(board_sanke_death_move)
        #self.board.printboard()
        tryMoves=[temp for temp in possible_moves if temp not in remove_move]
        try :
          print("???")
          print(tryMoves)
          if len(tryMoves)==0:
            tryMoves.extend(board_sanke_death_move)
          if len(tryMoves)==1 and len(board_sanke_death_move)==0:
            move= tryMoves[0]
          else:
            tryMovesNearest = self.nearest_food(tryMoves,head,data["board"]["food"])
            move = random.choice(tryMovesNearest)

            trapMove=[]
            trapMove.append(self.board.check(move,data["you"]["head"],data["you"]["length"]))
            print(trapMove)
            if not trapMove[-1]["wontTrap"]:
              tryMovesNearest.remove(move)
              if len(tryMovesNearest) == 1:
                testmove=tryMovesNearest[0]
                trapMove.append(self.board.check(testmove,data["you"]["head"],data["you"]["length"]))
                move=testmove
                print("!!!")
              print(".")
              print(trapMove)
              if not trapMove[-1]["wontTrap"]:
                print(tryMoves)
                tryMoves.remove(move)
                print(tryMoves)
                if len(tryMoves)==0:
                  trapMove.sort(key=lambda x:x["visited"])
                  move=trapMove[-1]["move"]
                  print("..")
                  print(trapMove)
                  

                else:
                  testmove=tryMoves[0]
                  trapMove.append(self.board.check(testmove,data["you"]["head"],data["you"]["length"]))
                  if not trapMove[-1]["wontTrap"]:
                    tryMoves.remove(testmove)
                    if len(tryMoves)==0:
                      trapMove.sort(key=lambda x:x["visited"])
                      move=trapMove[-1]["move"]
                      
                    else:
                      testmove=tryMoves[0]
                      trapMove.append(self.board.check(testmove,data["you"]["head"],data["you"]["length"]))
                      if trapMove[-1]["wontTrap"]:
                        move = trapMove[-1]["move"]
                      else:
                        trapMove.sort(key=lambda x:x["visited"])
                        move=trapMove[-1]["move"]
                  else:
                    move=trapMove[-1]["move"]
              else:
                move=trapMove[-1]["move"]
          
            
            
        except IndexError as e:
          print(e)
          ("random")

          move = random.choice(possible_moves)
        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"
        

    #return a list of moves that would kill the snake by crashing into and other snake
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def crashIntoSnake(self,head):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        #head = data["you"]["head"]
        snake_block=[]
        #for peice in  data["you"]["body"]:
         # snake_block.append(peice)
        for snake in data["board"]["snakes"]:
          for peice in snake["body"]:
            snake_block.append(peice)
            self.board.snake(peice)
          snake_block.pop()#TODO check if the other snake will eat
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp in snake_block:
            move_return.append(pos_move)
        return move_return

    #return list of moves that will be out of the board
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def outOfBoardMove(self):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        max_y=data["board"]["height"]
        max_x=data["board"]["width"]
        head = data["you"]["head"]
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp["x"]>=max_x or temp["y"]>=max_y or temp["x"]<0 or temp["y"]<0:
            move_return.append(pos_move)
        return move_return
    
    #reutn move that could crash with an other head that would kill
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def clashWithHead(self,head):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        #head = data["you"]["head"]
        length = data["you"]["length"]
        snake_head=[]
        snake_prediction=[]
        for snake in data["board"]["snakes"]:
          if length <= snake["length"] and snake["head"] != head:
            snake_head.append(snake["head"])
        for snakehead in snake_head:
          for pos_move in moves_ressult:
            snake_prediction.append({"x":(moves_ressult.get(pos_move)["x"]+snakehead["x"]),"y":(moves_ressult.get(pos_move)["y"]+snakehead["y"])})
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp in snake_prediction:
            move_return.append(pos_move)
        #print(move_return)
        return move_return

    #return the move that would bring you closes to a food node
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def nearest_food(self, move, head, food):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return =[]

        if len(food) >0:
          food.sort(key=lambda x:abs(x["x"]-head["x"])+abs(x["y"]-head["y"]))
          nearestFood=food[0]
          #closest
          #print(nearestFood)
          for pos_move in move:
            tempDistance=abs(nearestFood["x"]-head["x"]-moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]-moves_ressult.get(pos_move)["y"])
            tempDistanceOpissite=abs(nearestFood["x"]-head["x"]+moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]+moves_ressult.get(pos_move)["y"])
            if tempDistanceOpissite>tempDistance:
              move_return.append(pos_move)
          
          if len(move_return)>0:
            #print(move_return)
            return move_return

          else:
            return move
        return move


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)