from random import randint
from retro.game import Game
from .catcher import Catcher
from .manager import FruitManager
import json

WIDTH = 27
HEIGHT = 30

def play():
    agents = [
        Catcher((11, 28)),
        FruitManager(),
    ]
    state = {'score': 0, 'lives': 5, 'slices': 3}
    game = Game(agents, state, board_size=(WIDTH, HEIGHT), framerate=24, color="white_on_indigo", dump_state="result.json", log_file="game.log")
    game.play()
