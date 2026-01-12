"""
Star Catcher - A simple game using the retro-games library.

In this game, you control a basket at the bottom of the screen.
Stars fall from the sky, and you need to catch them!
Each star you catch is worth 10 points.
If you miss 3 stars, the game is over.

This game demonstrates how to create Agents in the retro-games framework:
- Basket: The player-controlled agent
- Star: Falling objects to catch
- StarSpawner: An invisible agent that creates new stars
"""

import json
from pathlib import Path
from random import randint

from retro.game import Game

# Game board dimensions
WIDTH = 40
HEIGHT = 20

# How many stars can you miss before game over?
MAX_MISSES = 3


class Basket:
    """
    The player's basket that catches falling stars.

    The player moves the basket left and right using the arrow keys.
    The basket is displayed as [___] at the bottom of the screen.
    """

    # Give this agent a name so other agents can find it
    name = "basket"

    # The basket is shown as an underscore (the "middle" of the basket)
    character = "_"

    # Start at the bottom center of the screen
    position = (WIDTH // 2, HEIGHT - 1)

    # Make the basket green
    color = "green"

    def handle_keystroke(self, keystroke, game):
        """
        Move the basket when the player presses left or right arrow keys.

        This method is called automatically whenever a key is pressed.
        """
        # Get the current x and y position
        x, y = self.position

        # Check which key was pressed
        if keystroke.name == "KEY_LEFT":
            # Move left (decrease x by 1)
            new_x = x - 1
            # Make sure we don't go off the left edge
            if new_x >= 0:
                self.position = (new_x, y)

        elif keystroke.name == "KEY_RIGHT":
            # Move right (increase x by 1)
            new_x = x + 1
            # Make sure we don't go off the right edge
            if new_x < WIDTH:
                self.position = (new_x, y)


class Star:
    """
    A falling star that the player tries to catch.

    Stars fall from the top of the screen to the bottom.
    If a star reaches the basket's row, we check if it was caught.
    """

    # Stars are shown as asterisks
    character = "*"

    # Stars are yellow/gold colored
    color = "yellow"

    def __init__(self, x_position):
        """
        Create a new star at the top of the screen.

        Args:
            x_position: The horizontal position where the star appears
        """
        # Stars start at the top (y = 0)
        self.position = (x_position, 0)

    def play_turn(self, game):
        """
        Move the star down one space each turn.

        This method is called automatically each turn of the game.
        When a star reaches the bottom, check if it was caught.
        """
        # Only move on every other turn (so stars don't fall too fast)
        if game.turn_number % 2 != 0:
            return

        # Get current position
        x, y = self.position

        # Check if we've reached the bottom row (where the basket is)
        if y >= HEIGHT - 1:
            # Get the basket's position
            basket = game.get_agent_by_name("basket")
            basket_x, basket_y = basket.position

            # Check if the star is close enough to the basket to be caught
            # The basket can catch stars within 1 space of its center
            if abs(x - basket_x) <= 1:
                # Caught! Add points
                game.state["score"] += 10
            else:
                # Missed! Add to miss counter
                game.state["misses"] += 1

                # Check if game is over
                if game.state["misses"] >= MAX_MISSES:
                    game.end()

            # Remove this star from the game
            game.remove_agent(self)
        else:
            # Move down one space
            self.position = (x, y + 1)


class StarSpawner:
    """
    An invisible agent that spawns new stars.

    This agent doesn't appear on the screen (display = False).
    Its only job is to create new Star agents at random times.
    """

    # Don't show this agent on the screen
    display = False

    def play_turn(self, game):
        """
        Maybe spawn a new star each turn.

        The chance of spawning increases as the game goes on,
        making the game progressively harder.
        """
        # Decide whether to spawn a star this turn
        if self.should_spawn_star(game.turn_number):
            # Pick a random x position for the new star
            x_position = randint(0, WIDTH - 1)

            # Create the star and add it to the game
            new_star = Star(x_position)
            game.add_agent(new_star)

    def should_spawn_star(self, turn_number):
        """
        Decide whether to spawn a star.

        Early in the game, stars spawn rarely.
        As turns increase, stars spawn more frequently.
        """
        # Random number between 0 and 500
        random_number = randint(0, 500)

        # Compare to turn number - higher turns = more likely to spawn
        # This makes the game get harder over time
        return random_number < turn_number


def main():
    """
    Start the Star Catcher game.

    This function:
    1. Creates all the agents
    2. Sets up the initial game state
    3. Runs the game
    4. Saves the final score to a file
    """
    # Create our agents
    basket = Basket()
    spawner = StarSpawner()

    # Set up the initial game state
    # This dictionary tracks score and misses throughout the game
    initial_state = {
        "score": 0,
        "misses": 0,
    }

    # Create and run the game
    game = Game(
        agents=[basket, spawner],
        state=initial_state,
        board_size=(WIDTH, HEIGHT),
    )

    # Play the game (this blocks until the game ends)
    game.play()

    # After the game ends, save the score to a file
    # The retro-console reads this file to record high scores
    final_score = game.state["score"]

    result_path = Path(__file__).parent.parent.parent / "result.json"
    with open(result_path, "w") as f:
        json.dump({"score": final_score}, f)


# This runs when you execute the file directly
if __name__ == "__main__":
    main()
