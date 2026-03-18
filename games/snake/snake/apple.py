from random import randint

class Apple:
    """An agent representing the Apple. 
    Note how Apple doesn't have ``play_turn`` or 
    ``handle_keystroke`` methods: the Apple doesn't need to do 
    anything in this game. It just sits there waiting to get 
    eaten.

    Attributes:
        name: "Apple"
        character: '@'
        color: "red_on_black" (`Here's documentation on how colors 
            work <https://blessed.readthedocs.io/en/latest/colors.html>`_
        position: (0, 0). The Apple will choose a random position 
            as soon as the game starts, but it needs an initial 
            position to be assigned.

    """
    name = "Apple"
    character = '@'
    color = "red_on_black"
    position = (0, 0)

    def relocate(self, game):
        """Sets position to a random empty position. This method is 
        called whenever the snake's head touches the apple. 

        Arguments: 
            game (Game): The current game.
        """
        self.position = self.random_empty_position(game)

    def random_empty_position(self, game):
        """Returns a randomly-selected empty position. Uses a very 
        simple algorithm: Get the game's board size, choose a 
        random x-value between 0 and the board width, and choose 
        a random y-value between 0 and the board height. Now use 
        the game to check whether any Agents are occupying this 
        position. If so, keep randomly choosing a new position 
        until the position is empty.
        """
        bw, bh = game.board_size
        occupied_positions = game.get_agents_by_position()
        while True:
            position = (randint(0, bw-1), randint(0, bh-1))
            if position not in occupied_positions:
                return position

