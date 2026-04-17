from retro.game import Game
from manager import Manager

agents = [Manager()]
state = {'level': 1}
game = Game(agents, state, board_size=(20, 20), debug=True)
game.play()
