import os
import sys
import chess.pgn
import chess.engine
from io import StringIO
from matplotlib import pyplot as plt
from math import log
import requests
import datetime
#Chess.com username for automated retrival of previous game.
USERNAME = "Croc0dileL"

ENGINE = "./tools/stockfish"
ENGINE_DEPTH = 22 # engine analysis depth, go lower if you dont like waiting
CHART_DPI = 600 # crips charts only
MATE_SCORE = 100000

def getLastGame(user: str):
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        resp = requests.get(f"https://api.chess.com/pub/player/{user}/games/{current_year}/{current_month}",headers={"User-Agent":"carlylemorris@gmail.com"})
        game = resp.json()["games"][-1]
        return game["pgn"], game["white"]["username"].lower() == user.lower()


def scale(x):
    return x/(500 + abs(x))

def main():
    if USERNAME == "":
        if len(sys.argv) > 3:
            print("\nUsage: python3 gameReview.py [w/b] '[game]'\nMake sure expored game is quoted\n")
            quit()

        elif len(sys.argv) == 3:
            uicolor = sys.argv[1]
            sanGame = sys.argv[2]

        else:
            uicolor = input("Enter Your Color [w/b]: ")
            sanGame = ""
            temp = input("Enter PGN Game: ")
            while(len(sanGame) < 3 or sanGame[-3:] != "\n\n\n"):
                sanGame += temp + "\n"
                temp = input()

            color = uicolor != "b"
    else:
        sanGame,color = getLastGame(USERNAME)
    
    pgn = StringIO(sanGame)
    game = chess.pgn.read_game(pgn)
     
    headers = sanGame.split("\n\n")[0].split("\n")
    fname = "_".join([h.split('"')[1] for h in [headers[2], headers[4], headers[5]]])

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE)
    
    i = 0
    wmoves = list()
    bmoves = list()
    print("\nengine is thinking",end="")
    for move in game.mainline():
        print(".",end="")
        sys.stdout.flush()
        board = move.board()
    
        info = engine.analyse(board,chess.engine.Limit(depth=ENGINE_DEPTH))
        
        (wmoves if i%2 == 0 else bmoves).append(info["score"].pov(color).score(mate_score=MATE_SCORE))
        i += 1


    #Analize mistakes

    if color:
        premoves = bmoves
        postmoves = wmoves[1:]
        md = 2
    else:
        premoves = wmoves
        postmoves = bmoves
        md = 1

    deltas = [post-pre for pre,post in zip(premoves,postmoves)]

    numDeltas = [(i,delta) for i,delta in enumerate(deltas)]
    numDeltas.sort(key=lambda x:-1*x[1])

    print("Mistakes: ")
    for moveNum,delta in numDeltas:
        print(f"Move {moveNum+md:3} {delta:10} ({premoves[moveNum]} to {postmoves[moveNum]})")
    
    #Generate eval line graph
    moves = list() 
    
    for wm,bm in zip(wmoves,bmoves):
        for m in [wm,bm]:
            moves.append(scale(m))


    plt.plot([1+i/2 for i in range(len(moves))],
            moves,
            color="tab:orange")
    
    #Generate bar chart
    barDeltas = [scale(m) for m in deltas]
   
    plt.bar([1+i+color for i in range(len(deltas))],
            barDeltas,
            align="edge",
            width=0.5,
            color="tab:blue",
            )

    plt.title(fname)

    #Save and view chart
    os.system("mkdir ./games/"+fname)
    plt.savefig("./games/"+fname+"/chart.png",dpi = CHART_DPI)
    print(sanGame,file=open("./games/"+fname+"/game.pgn","w"))
    os.system("wslview ./games/"+fname+"/chart.png")
    quit()
    
if __name__ == "__main__":
    main()
