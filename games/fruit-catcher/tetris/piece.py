from block import Block

PIECE_DEFINITIONS = [
    [(-1, 0), (0, 0), (1, 0), (2, 0)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
]

class Piece:
    """A Piece is a group of blocks which are 'alive': 
    They fall and the player can rotate or move them.
    A Piece is created with a position, the game, and a list of block_offsets, 
    each of which represents the location of one of the Piece's 
    Blocks relative to the Piece position.
    """
    name = "piece"
    display = False

    def __init__(self, position, game, block_offsets):
        self.position = position
        self.blocks = {}
        for offset in block_offsets:
            self.create_block(game, offset)

    def handle_keystroke(self, keystroke, game):
        x, y = self.position
        if keystroke.name == "KEY_LEFT":
            new_position = (x - 1, y)
            if self.can_move_to(new_position, game):
                self.move_to(new_position)
        elif keystroke.name == "KEY_RIGHT": 
            new_position = (x + 1, y)
            if self.can_move_to(new_position, game):
                self.move_to(new_position)

    def play_turn(self, game):
        if self.should_fall(game):
            self.fall(game)

    def should_fall(self, game):
        """Determines whether the piece should fall.
        Currently, the Piece falls every third turn. 
        In the future, the Piece should fall slowly at first, and 
        then should fall faster at higher levels.
        """
        return game.turn_number % 3 == 0

    def fall(self, game):
        x, y = self.position
        falling_position = (x, y + 1)
        if self.can_move_to(falling_position, game):
            self.move_to(falling_position)
        else:
            self.destroy(game)

    def can_move_to(self, new_position, game):
        """Checks whether the Piece can move to a new position.
        For every one of the Piece's Blocks, finds where that block
        would be after the move, and checks whether there are any dead agents
        already there (live agents would be Blocks which are part of this Piece, 
        not a problem since they'll be moving too).
        """
        x, y = new_position
        agents_by_position = game.get_agents_by_position()
        for offset in self.blocks.keys():
            ox, oy = offset
            new_block_position = (x+ox, y+oy)
            if not game.on_board(new_block_position):
                return False
            for agent in agents_by_position[new_block_position]:
                if not agent.alive:
                    return False
        return True

    def move_to(self, position):
        """Move to position and updates positions of Blocks.
        """
        x, y = position
        self.position = position
        for offset, block in self.blocks.items():
            ox, oy = offset
            block.position = (x + ox, y + oy)

    def create_block(self, game, offset):
        x, y = self.position
        ox, oy = offset
        block = Block((x + ox, y + oy))
        self.blocks[offset] = block
        game.add_agent(block)

    def destroy(self, game):
        """Causes the Piece to destroy itself. 
        All the Blocks are set to dead.
        """
        for block in self.blocks.values():
            block.alive = False
        game.remove_agent(self)
        

        

