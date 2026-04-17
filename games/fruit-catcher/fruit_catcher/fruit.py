from random import randint, choice

FRUIT_TYPES = [
    {'shape': [(0, 0)],                              'color': 'green_on_indigo'},
    {'shape': [(0, 0), (1, 0)],                      'color': 'yellow_on_indigo'},
    {'shape': [(0, 0), (1, 0), (2, 0)],              'color': 'red_on_indigo'},
    {'shape': [(0, 0), (0, 1)],                      'color': 'cyan_on_indigo'},
    {'shape': [(0, 0), (1, 0), (0, 1), (1, 1)],      'color': 'magenta_on_indigo'},
    {'shape': [(0, 0), (1, 1), (2, 0)],              'color': 'white_on_indigo'},
]

class FruitPiece:
    character = "@"
    display = True

    def __init__(self, position, color, z):
        self.position = position
        self.color = color
        self.z = z
        self.parent = None

class Fruit:
    display = False
    character = "@"

    def __init__(self, position, game, shape_offsets, color, dx, speed, start_z):
        self.position = position
        self.pieces = {}
        self.color = color
        self.dx = dx
        self.speed = speed
        self.alive = True
        for i, offset in enumerate(shape_offsets):
            self.create_shape(game, offset, start_z + i)

    def play_turn(self, game):
        if game.turn_number % self.speed == 0:
            self.move(game)

    def move(self, game):
        x, y = self.position
        width, height = game.board_size
        offsets = list(self.pieces.keys())
        max_ox = max(ox for ox, oy in offsets)
        min_ox = min(ox for ox, oy in offsets)
        max_oy = max(oy for ox, oy in offsets)

        new_x = x + self.dx
        if new_x + min_ox < 0 or new_x + max_ox >= width:
            self.dx = -self.dx
            new_x = x + self.dx

        new_y = y + 1
        if new_y + max_oy >= height:
            for piece in self.pieces.values():
                game.remove_agent(piece)
            game.remove_agent(self)
            self.alive = False
            game.state['lives'] -= 1
            if game.state['lives'] <= 0:
                game.log("play lose_a_life")
                game.end()
            else:
                game.log("play hit_small")
        else:
            self.position = (new_x, new_y)
            self.update_piece_positions()
            self.check_catcher_collision(game)

    def create_shape(self, game, offset, z):
        x, y = self.position
        ox, oy = offset
        piece = FruitPiece((x + ox, y + oy), self.color, z)
        piece.parent = self
        self.pieces[offset] = piece
        game.add_agent(piece)

    def update_piece_positions(self):
        x, y = self.position
        for offset, piece in self.pieces.items():
            ox, oy = offset
            piece.position = (x + ox, y + oy)

    def check_catcher_collision(self, game):
        catcher = game.get_agent_by_name("catcher")
        catcher_positions = {p.position for p in catcher.pieces}
        for piece in self.pieces.values():
            if piece.position in catcher_positions:
                game.log("play success_small")
                game.state['score'] += 1
                for p in self.pieces.values():
                    game.remove_agent(p)
                game.remove_agent(self)
                self.alive = False
                return
