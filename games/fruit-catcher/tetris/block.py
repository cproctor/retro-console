class Block:
    """A Block represents a single square on the Tetris board. 
    Blocks are part of a Piece while they are 'alive'.
    """
    character = "X"
    color = "blue"
    alive = True

    def __init__(self, position):
        self.position = position
