from retro.game import Game
from snake.apple import Apple
from snake.snake import SnakeHead

def main():
    head = SnakeHead()
    apple = Apple()
    game = Game([head, apple], {'score': 0}, board_size=(32, 16), framerate=12, dump_state="result.json")
    apple.relocate(game)
    game.play()

if __name__ == '__main__':
    main()
