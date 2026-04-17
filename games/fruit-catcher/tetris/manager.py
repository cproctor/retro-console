from piece import Piece, PIECE_DEFINITIONS
from random import choice
from retro.errors import AgentNotFoundByName

class Manager:
    """The Manager takes care of stuff that isn't anyone else's responsibility:
    - Create a Piece whenever none exists.
    - Clear full rows of Blocks (and move other Blocks down).
    - End the game when the Blocks pile up all the way.
    """
    display = False

    def play_turn(self, game):
        try:
            game.get_agent_by_name("piece")
        except AgentNotFoundByName:
            self.create_piece(game)

    def create_piece(self, game):
        width, height = game.board_size
        piece = Piece((width//2, 2), game, choice(PIECE_DEFINITIONS))
        game.add_agent(piece)


