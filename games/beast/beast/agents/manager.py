LEVEL_COLORS = ["green4", "cyan", "yellow", "magenta", "red", "white"]
BASE_BEASTS = 10
BEASTS_PER_LEVEL = 3
BASE_TURNS_BETWEEN_MOVES = 33  # Level 1: move on average every 33 turns
MIN_TURNS_BETWEEN_MOVES = 4   # Level 11+: move on average every 4 turns
BASE_PROB_RANDOM = 0.2
MIN_PROB_RANDOM = 0.02


class Manager:
    """Manages level setup, progression, and player lives. Not rendered on the board."""
    display = False
    name = "manager"

    def __init__(self, board):
        self.board = board
        self.blocks = []
        self.beasts = []
        self._setup_pending = False

    def _beast_params(self, level):
        t = min(1.0, (level - 1) / 10)
        avg_turns = BASE_TURNS_BETWEEN_MOVES + t * (MIN_TURNS_BETWEEN_MOVES - BASE_TURNS_BETWEEN_MOVES)
        prob_random = BASE_PROB_RANDOM + t * (MIN_PROB_RANDOM - BASE_PROB_RANDOM)
        return {"average_turns_between_moves": avg_turns, "probability_of_random_move": prob_random}

    def play_turn(self, game):
        """Execute any pending level setup at the start of a frame, before beasts move."""
        if self._setup_pending:
            self._setup_pending = False
            self._do_setup_level(game)

    def setup_level(self, game):
        """Direct entry point for initial level setup (called before the game loop)."""
        self._do_setup_level(game)

    def _do_setup_level(self, game):
        """Remove all agents and build a fresh layout for the current level."""
        level = game.state["level"]
        color = LEVEL_COLORS[(level - 1) % len(LEVEL_COLORS)]
        num_beasts = BASE_BEASTS + (level - 1) * BEASTS_PER_LEVEL
        beast_params = self._beast_params(level)

        for agent in list(game.agents):
            if agent is not self:
                game.remove_agent(agent)

        player, beasts, blocks = self.board.get_layout(num_beasts, color, beast_params)
        for agent in [player] + beasts + blocks:
            game.add_agent(agent)

        self.beasts = beasts
        self.blocks = blocks

    def check_level_complete(self, game):
        """Called by a Beast when it dies. Schedules next level if all beasts are gone."""
        self.beasts = [b for b in self.beasts if b in game.agents]
        if not self.beasts:
            game.state["level"] += 1
            game.state["message"] = f"Level {game.state['level']}!"
            self._setup_pending = True

    def respawn_player(self, game):
        """Decrement lives. End the game if none remain, otherwise move player to safety."""
        game.state["lives"] -= 1
        if game.state["lives"] <= 0:
            game.state["message"] = "Game over!"
            game.end()
            return
        player = game.get_agent_by_name("player")
        player.color = "white"
        beast_positions = [b.position for b in self.beasts if b in game.agents]
        occupied = {a.position for a in game.agents
                    if getattr(a, "display", True) and a is not player}
        safe_pos = self.board.find_safe_spawn(beast_positions, occupied)
        if safe_pos:
            player.position = safe_pos
        game.state["message"] = f"Lives: {game.state['lives']}"
