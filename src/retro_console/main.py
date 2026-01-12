"""Main entry point for the retro console."""

import os
import sys

from blessed import Terminal

from retro_console import settings
from retro_console.models import init_db, get_session, Game
from retro_console.input_handler import InputHandler
from retro_console.game_manager import discover_games, register_games
from retro_console.screens import SplashScreen, GameSelectScreen, HighScoreScreen


class SetupError(Exception):
    """Error during setup."""
    pass


class RetroConsoleApp:
    """Main application class."""

    def __init__(self):
        self.terminal = Terminal()
        self.input_handler = InputHandler(self.terminal)
        self.session = None
        self.games = []
        self.validation_results = []
        self.pending_high_score = None
        self.debug_mode = False

    def check_terminal_size(self):
        """Check if terminal is large enough."""
        if self.terminal.width < settings.SCREEN_WIDTH:
            raise SetupError(
                f"Terminal width ({self.terminal.width}) is less than "
                f"required ({settings.SCREEN_WIDTH})"
            )
        if self.terminal.height < settings.SCREEN_HEIGHT:
            raise SetupError(
                f"Terminal height ({self.terminal.height}) is less than "
                f"required ({settings.SCREEN_HEIGHT})"
            )

    def setup(self):
        """Run setup and return True if successful."""
        errors = []

        # Initialize database
        try:
            init_db()
            self.session = get_session()
        except Exception as e:
            errors.append(f"Database initialization failed: {e}")

        # Check terminal size
        try:
            self.check_terminal_size()
        except SetupError as e:
            errors.append(str(e))

        # Discover and validate games
        print("Discovering games...")
        valid_games, self.validation_results = discover_games()

        if valid_games:
            print(f"Found {len(valid_games)} valid game(s)")
            self.games = register_games(valid_games, self.session)
        else:
            print("No valid games found")

        # Check for debug key during setup
        print(f"Press {settings.DEBUG_KEY} within 2 seconds to enter debug mode...")
        raw_key, _ = self.input_handler.read_key(timeout=2)
        if raw_key and self.input_handler.is_debug_key(raw_key):
            self.debug_mode = True

        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            self.debug_mode = True

        return not errors

    def refresh_games(self):
        """Refresh game data from database."""
        self.session.expire_all()
        self.games = self.session.query(Game).all()

    def run_debug_mode(self):
        """Run debug mode."""
        print("\n" + "=" * 60)
        print("DEBUG MODE")
        print("=" * 60)

        print(f"\nGames directory: {settings.GAMES_DIR}")
        print(f"Database path: {settings.DATABASE_PATH}")
        print(f"Screen size: {settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT}")
        print(f"Terminal size: {self.terminal.width}x{self.terminal.height}")

        print("\n--- Validation Results ---")
        if self.validation_results:
            for result in self.validation_results:
                status = "VALID" if result.valid else "INVALID"
                print(f"\n{result.path.name}: {status}")
                if result.valid:
                    print(f"  Name: {result.name}")
                    print(f"  Author: {result.author}")
                else:
                    for error in result.errors:
                        print(f"  ERROR: {error}")
        else:
            print("No game packages found")

        print("\n--- Registered Games ---")
        if self.games:
            for game in self.games:
                print(f"  {game.name} (plays: {game.play_count})")
        else:
            print("  No games registered")

        print("\n" + "=" * 60)
        print("Entering shell. Type 'exit' to quit.")
        print("=" * 60 + "\n")

        # Drop to shell
        shell = os.environ.get("SHELL", "/bin/sh")
        os.system(shell)

    def run(self):
        """Run the main application loop."""
        with self.terminal.fullscreen(), self.terminal.hidden_cursor():
            # Run setup
            self.setup()

            # Enter debug mode if requested
            if self.debug_mode:
                self.run_debug_mode()
                return

            # Main screen loop
            current_screen = "splash"

            while True:
                if current_screen == "splash":
                    screen = SplashScreen(self)
                elif current_screen == "game_select":
                    screen = GameSelectScreen(self)
                elif current_screen == "high_score":
                    screen = HighScoreScreen(self)
                else:
                    break

                next_screen = screen.run()
                if next_screen:
                    current_screen = next_screen


def main():
    """Main entry point."""
    app = RetroConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
