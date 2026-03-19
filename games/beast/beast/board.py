from random import shuffle
from beast.helpers import distance
from beast.agents.player import Player
from beast.agents.beast import Beast
from beast.agents.block import Block

MIN_PLAYER_DISTANCE = 5


class Board:
    """Creates agents and assigns them positions. Owned by the Manager."""

    def __init__(self, width, height, block_density=0.3):
        self.width = width
        self.height = height
        self.num_blocks = round(width * height * block_density)

    def get_layout(self, num_beasts, color, beast_params):
        """Returns (player, beasts, blocks) with player placed safely away from beasts."""
        positions = self._shuffled_positions()
        beast_positions = positions[:num_beasts]
        block_positions = positions[num_beasts:num_beasts + self.num_blocks]
        remaining = positions[num_beasts + self.num_blocks:]

        safe = [p for p in remaining
                if all(distance(p, bp) >= MIN_PLAYER_DISTANCE for bp in beast_positions)]
        player_pos = safe[0] if safe else remaining[0]

        player = Player(player_pos)
        beasts = [Beast(pos, **beast_params) for pos in beast_positions]
        blocks = [Block(pos, color=color) for pos in block_positions]
        return player, beasts, blocks

    def find_safe_spawn(self, beast_positions, occupied_positions):
        """Find a safe respawn position: far from beasts and not occupied."""
        positions = self._shuffled_positions(exclude=occupied_positions)
        for pos in positions:
            if all(distance(pos, bp) >= MIN_PLAYER_DISTANCE for bp in beast_positions):
                return pos
        return positions[0] if positions else None

    def _shuffled_positions(self, exclude=None):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        if exclude:
            positions = [p for p in positions if p not in exclude]
        shuffle(positions)
        return positions
