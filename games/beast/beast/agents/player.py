import os
from beast.helpers import add, get_occupant

direction_vectors = {
    os.environ.get("RETRO_KEY_RIGHT", "KEY_RIGHT"): (1, 0),
    os.environ.get("RETRO_KEY_UP", "KEY_UP"): (0, -1),
    os.environ.get("RETRO_KEY_LEFT", "KEY_LEFT"): (-1, 0),
    os.environ.get("RETRO_KEY_DOWN", "KEY_DOWN"): (0, 1),
}

class Player:
    character = "*"
    color = "white"
    name = "player"

    def __init__(self, position):
        self.position = position

    def handle_keystroke(self, keystroke, game):
        key = keystroke.name or str(keystroke)
        if key in direction_vectors:
            vector = direction_vectors[key]
            self.try_to_move(vector, game)

    def try_to_move(self, vector, game):
        """Tries to move the player in the direction of vector.
        If the space is empty and it's on the board, then the move succeeds. 
        If the space is occupied, then if the occupant can be pushed, it gets
        pushed and the move succeeds. Otherwise, the move fails. 
        """
        future_position = add(self.position, vector)
        on_board = game.on_board(future_position)
        obstacle = get_occupant(game, future_position)
        if obstacle:
            if obstacle.deadly:
                self.die(game)
            elif obstacle.handle_push(vector, game):
                game.log("play light_hit")
                self.position = future_position
        elif on_board:
            game.log("play move")
            self.position = future_position

    def die(self, game):
        manager = game.get_agent_by_name("manager")
        manager.respawn_player(game)

