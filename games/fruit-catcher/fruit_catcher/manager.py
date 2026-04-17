from .fruit import Fruit, FRUIT_TYPES
from random import choice, randint

class FruitManager:

    display = False
    name = "fruit_manager"

    def __init__(self):
        self.active_fruits = []
        self.last_spawn_turn = 0
        self.next_z = 0

    def play_turn(self, game):
        self.active_fruits = [f for f in self.active_fruits if f.alive]
        spawn_interval = max(12, 72 - game.turn_number // 10)
        if game.turn_number - self.last_spawn_turn >= spawn_interval:
            self.create_piece(game)
            self.last_spawn_turn = game.turn_number

    def create_piece(self, game):
        width, _ = game.board_size
        fruit_type = choice(FRUIT_TYPES)
        shape = fruit_type['shape']
        max_ox = max(ox for ox, oy in shape)
        x = randint(0, width - 1 - max_ox)
        dx = choice([-1, 0, 0, 1])
        speed = randint(2, 5)
        fruit = Fruit((x, 1), game, shape, fruit_type['color'], dx, speed, self.next_z)
        self.next_z += len(shape)
        game.add_agent(fruit)
        self.active_fruits.append(fruit)
