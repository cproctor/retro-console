from random import shuffle
from beast.agents.player import Player
from beast.agents.beast import Beast
from beast.agents.block import Block


class Board:
    """Creates agents and assigns them positions. Owned by the Manager."""

    def __init__(self, width, height, block_density=0.3):
        self.width = width
        self.height = height
        self.num_blocks = round(width * height * block_density)

    def get_initial_agents(self, num_beasts, color, beast_params):
        """Returns (player, beasts, blocks) for the first level."""
        positions = self._shuffled_positions()
        player = Player(positions[0])
        beasts = [Beast(pos, **beast_params) for pos in positions[1:num_beasts + 1]]
        blocks = [Block(pos, color=color) for pos in positions[num_beasts + 1:num_beasts + 1 + self.num_blocks]]
        return player, beasts, blocks

    def get_level_agents(self, num_beasts, color, beast_params, exclude_positions):
        """Returns (beasts, blocks) for a level transition, avoiding exclude_positions."""
        positions = self._shuffled_positions(exclude=exclude_positions)
        beasts = [Beast(pos, **beast_params) for pos in positions[:num_beasts]]
        blocks = [Block(pos, color=color) for pos in positions[num_beasts:num_beasts + self.num_blocks]]
        return beasts, blocks

    def _shuffled_positions(self, exclude=None):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        if exclude:
            positions = [p for p in positions if p not in exclude]
        shuffle(positions)
        return positions
