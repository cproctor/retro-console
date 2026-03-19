from beast.helpers import add, distance, get_occupant
from random import uniform, choice


class Beast:
    """Represents a beast, coming after the player.
    """
    character = "H"
    color = "red"
    deadly = True

    def __init__(self, position, average_turns_between_moves=33, probability_of_random_move=0.2):
        self.position = position
        self.average_turns_between_moves = average_turns_between_moves
        self.probability_of_random_move = probability_of_random_move
        self.energy = 0.0

    def handle_push(self, vector, game):
        future_position = add(self.position, vector)
        on_board = game.on_board(future_position)
        obstacle = get_occupant(game, future_position)
        if obstacle and isinstance(obstacle, Beast):
            return False
        if obstacle or not on_board:
            self.die(game)
            return True
        return False

    def play_turn(self, game):
        self.energy += uniform(0, 2 / self.average_turns_between_moves)
        if self.energy >= 1.0:
            self.energy -= 1.0
            player = game.get_agent_by_name("player")
            possible_moves = [
                pos for pos in self.get_adjacent_positions()
                if pos == player.position or (game.is_empty(pos) and game.on_board(pos))
            ]
            if possible_moves:
                if uniform(0, 1) < self.probability_of_random_move:
                    self.position = choice(possible_moves)
                else:
                    self.position = self.choose_best_move(possible_moves, game)
            if player.position == self.position:
                player.die(game)

    def get_adjacent_positions(self):
        """Returns a list of all adjacent positions, including diagonals."""
        return [
            add(self.position, (i, j))
            for i in [-1, 0, 1]
            for j in [-1, 0, 1]
            if i or j
        ]

    def choose_best_move(self, possible_moves, game):
        player = game.get_agent_by_name("player")
        move_distances = [[distance(player.position, move), move] for move in possible_moves]
        _, best_move = sorted(move_distances)[0]
        return best_move

    def die(self, game):
        game.remove_agent(self)
        game.state["score"] += game.state["level"]
        manager = game.get_agent_by_name("manager")
        manager.check_level_complete(game)
