import pygame
import json
from network import Network
import sys
pygame.font.init()


ALPHA_BETA_KI_PATH = r"C:\Users\ylang\Downloads\turm_waechter_ai\turm_waechter_ai"
sys.path.insert(0, ALPHA_BETA_KI_PATH)

from alpha_beta_ki import choose_best_move

def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    while run:
        clock.tick(60)
        try:
            #try to send get as a json to server over network, rest is error handling
            game = n.send(json.dumps("get"))
            if game is None:
                raise ValueError("Game data is None")
        except:
            run = False
            print("Couldn't get game")
            break

        #response is also a json, json.loads transforms into a python dictionary
        #dictionary consists of board string, a variable turn which is r or b depending whos turn it is, 
        #bothConnected which is True if both players are connected, time which is the left time and end which is False as long as the game isn't finished
        game = json.loads(game)

        #allow input just when both players are in
        if game["bothConnected"]:

            #allow to only give input, when it is your turn
            if player == 0 and game["turn"] == "r":
                #printing not necessary, game["board"] is the way to get the board string
                print("New Board: " + game["board"])
                print("New Time: " + str(game["time"]))

                #change to any input you like. This one is just console input. Change it here to respond with your Ai's answer. 
                #Answer must have format: start-end-height like E7-F7-1
                i, allocated = choose_best_move(game["board"])

                #json.dumps(i) transforms the input into a json. You can print it, if you want to see the difference
                data = json.dumps(i)

                #send data via network
                n.send(data)
            elif player == 1 and game["turn"] == "b":
                print("New Board: " + game["board"])
                print("New Time: " + str(game["time"]))

                #Please also change your Input here to respond with your Ai's answer
                #i = input()
                i, allocated = choose_best_move(game["board"])
                data = json.dumps(i)
                n.send(data)

while True:
    main()