LEVEL_COLORS = ["green4", "cyan", "yellow", "magenta", "red", "white"]
BASE_BEASTS = 10
BEASTS_PER_LEVEL = 3
BASE_TURNS_BETWEEN_MOVES = 33  # Level 1: move on average every 33 turns
MIN_TURNS_BETWEEN_MOVES = 4   # Level 11+: move on average every 4 turns
BASE_PROB_RANDOM = 0.2
MIN_PROB_RANDOM = 0.02


class Manager:
    """Manages level setup and progression. Not rendered on the board."""
    display = False
    name = "manager"

    def __init__(self, board):
        self.board = board
        self.blocks = []
        self.beasts = []

    def _beast_params(self, level):
        """Returns beast difficulty parameters for the given level.
        Beasts move more frequently and more purposefully as levels increase."""
        t = min(1.0, (level - 1) / 10)  # Reaches max difficulty at level 11
        avg_turns = BASE_TURNS_BETWEEN_MOVES + t * (MIN_TURNS_BETWEEN_MOVES - BASE_TURNS_BETWEEN_MOVES)
        prob_random = BASE_PROB_RANDOM + t * (MIN_PROB_RANDOM - BASE_PROB_RANDOM)
        return {"average_turns_between_moves": avg_turns, "probability_of_random_move": prob_random}

    def setup_level(self, game):
        """Sets up agents for the current level. On level 1 this includes the
        player; on subsequent levels it replaces beasts and blocks in place."""
        level = game.state["level"]
        color = LEVEL_COLORS[(level - 1) % len(LEVEL_COLORS)]
        num_beasts = BASE_BEASTS + (level - 1) * BEASTS_PER_LEVEL
        beast_params = self._beast_params(level)

        if level == 1:
            player, beasts, blocks = self.board.get_initial_agents(num_beasts, color, beast_params)
            for agent in [player] + beasts + blocks:
                game.add_agent(agent)
        else:
            # Remove existing blocks (beasts are already removed when killed)
            for block in self.blocks:
                game.remove_agent(block)
            player = game.get_agent_by_name("player")
            beasts, blocks = self.board.get_level_agents(
                num_beasts, color, beast_params, exclude_positions=[player.position]
            )
            for agent in beasts + blocks:
                game.add_agent(agent)

        self.beasts = beasts
        self.blocks = blocks

    def check_level_complete(self, game):
        """Called by a Beast when it dies. Advances to the next level if all
        beasts have been cleared."""
        self.beasts = [b for b in self.beasts if b in game.agents]
        if not self.beasts:
            game.state["level"] += 1
            game.state["message"] = f"Level {game.state['level']}!"
            self.setup_level(game)
