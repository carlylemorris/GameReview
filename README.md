# GameReview
A tool for analyzing chess games with stockfish.

## Usage
python3 gameReview.py [w/b] '[pgn game text]'  

## Installation 
Running in WSL is recommended but not necessary (wslview will just fail)  
Clone this repo  
Pip install chess and matplotlib  
Download chess engine of choice (uses UCI communication protocol)  
Change ENGINE global variable to the path of the chess engine executable (currently ./tools/stockfish)
