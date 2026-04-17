from random import randint
from .fruit import FruitPiece

class SliceEffectPiece:
    character = "-"
    color = "yellow_on_indigo"
    z = 2
    def __init__(self, position):
        self.position = position

class SliceEffect:
    display = False

    def __init__(self, game):
        self.pieces = []
        self.turns_remaining = 8
        width, height = game.board_size
        for y in range(height - 3, height):
            for x in range(width):
                piece = SliceEffectPiece((x, y))
                self.pieces.append(piece)
                game.add_agent(piece)

    def play_turn(self, game):
        self.turns_remaining -= 1
        if self.turns_remaining <= 0:
            for piece in self.pieces:
                game.remove_agent(piece)
            game.remove_agent(self)

class CatcherPiece:
    character = "-"
    color = "white_on_indigo"
    z = 1
    def __init__(self, position):
        self.position = position

class Catcher:
    width = 6
    display = False
    pieces = []
    name = "catcher"
    color = "white_on_indigo"

    def __init__(self, position):
        self.position = position

    def play_turn(self, game):
        if not self.pieces:
            self.create_pieces(game)

    def handle_keystroke(self, keystroke, game):
        x, y = self.position
        width, height = game.board_size
        if keystroke.name == "KEY_LEFT":
            new_x = max(0, x - 3)
            self.position = (new_x, y)
            self.update_piece_positions()
            self.check_fruit_collisions(game)
        if keystroke.name == "KEY_RIGHT":
            new_x = min(width - self.width, x + 3)
            self.position = (new_x, y)
            self.update_piece_positions()
            self.check_fruit_collisions(game)
        if str(keystroke) == 'z' and game.state['slices'] > 0:
            game.log("play success_medium")
            game.state['slices'] -= 1
            game.add_agent(SliceEffect(game))
            self._slice_fruits(game)

    def check_fruit_collisions(self, game):
        agents_by_pos = game.get_agents_by_position()
        seen = set()
        for piece in self.pieces:
            for agent in agents_by_pos.get(piece.position, []):
                if isinstance(agent, FruitPiece) and agent.parent.alive and id(agent.parent) not in seen:
                    seen.add(id(agent.parent))
                    agent.parent.check_catcher_collision(game)

    def _slice_fruits(self, game):
        _, height = game.board_size
        slice_rows = set(range(height - 3, height))
        manager = game.get_agent_by_name("fruit_manager")
        for fruit in list(manager.active_fruits):
            if not fruit.alive:
                continue
            for piece in fruit.pieces.values():
                if piece.position[1] in slice_rows:
                    game.state['score'] += 1
                    for p in fruit.pieces.values():
                        game.remove_agent(p)
                    game.remove_agent(fruit)
                    fruit.alive = False
                    break

    def create_pieces(self, game):
        x, y = self.position
        self.pieces = []
        for i in range(self.width):
            piece = CatcherPiece((x + i, y))
            self.pieces.append(piece)
            game.add_agent(piece)

    def update_piece_positions(self):
        x, y = self.position
        for i, piece in enumerate(self.pieces):
            piece.position = (x + i, y)

    def can_move(self, position, game):
        on_board = game.on_board(position)
        empty = game.is_empty(position)
