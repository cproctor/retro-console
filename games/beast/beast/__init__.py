from retro.game import Game
from beast.board import Board

WIDTH = 40
HEIGHT = 20
NUM_BEASTS = 10

def main():
    board = Board(WIDTH, HEIGHT, num_beasts=NUM_BEASTS)
    state = {"score": 0, "level": 1}
    game = Game(board.get_agents(), state, board_size=(WIDTH, HEIGHT), dump_state="result.json")
    game.num_beasts = NUM_BEASTS
    game.play()

if __name__ == '__main__':
    main()
