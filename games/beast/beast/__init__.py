from retro.game import Game
from beast.board import Board
from beast.agents.manager import Manager

WIDTH = 40
HEIGHT = 20

def main():
    board = Board(WIDTH, HEIGHT)
    manager = Manager(board)
    state = {"score": 0, "level": 1}
    game = Game([manager], state, board_size=(WIDTH, HEIGHT), dump_state="result.json")
    manager.setup_level(game)
    game.play()

if __name__ == '__main__':
    main()
