from retro.game import Game
from beast.board import Board

WIDTH = 40
HEIGHT = 20
NUM_BEASTS = 10

def play():
    board = Board(WIDTH, HEIGHT, num_beasts=NUM_BEASTS)
    state = {"score": 0}
    game = Game(board.get_agents(), state, board_size=(WIDTH, HEIGHT))
    game.num_beasts = NUM_BEASTS
    game.play()
    with open("result.json") as fh:
        json.dump(game.state, fh)

if __name__ == '__main__':
    play()
