"""Main entry point for the retro console."""

import os
import subprocess
import sys

from blessed import Terminal

from retro_console import settings
from retro_console.logging_setup import configure_logging, get_logger
from retro_console.models import init_db, get_session, Game, purge_banned_high_scores
from retro_console.input_handler import InputHandler
from retro_console.game_manager import discover_games, register_games
from retro_console.screens import SplashScreen, GameSelectScreen, HighScoreScreen
from retro_console.sound_manager import SoundManager


class SetupError(Exception):
    """Error during setup."""
    pass


class RetroConsoleApp:
    """Main application class."""

    def __init__(self):
        configure_logging(settings.LOG_FILE)
        self.log = get_logger(__name__)
        self.terminal = Terminal()
        self.input_handler = InputHandler(self.terminal)
        self.sound_manager = SoundManager()
        self.session = None
        self.games = []
        self.validation_results = []
        self.pending_high_score = None
        self.debug_mode = False

    def _status(self, msg: str, **log_kw) -> None:
        """Print a setup status line to the terminal and log it to file."""
        print(msg)
        self.log.info(msg, **log_kw)

    def pull_latest(self):
        """Pull latest changes from git repository."""
        self._status("Pulling latest changes...")
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self._status(f"Git pull: {result.stdout.strip()}")
            else:
                self._status(f"Git pull failed: {result.stderr.strip()}")
                self.log.warning("git_pull_failed", stderr=result.stderr.strip())
        except subprocess.TimeoutExpired:
            self._status("Git pull timed out")
            self.log.warning("git_pull_timeout")
        except Exception as e:
            self._status(f"Git pull error: {e}")
            self.log.error("git_pull_error", error=str(e))

        try:
            result = subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive", "--remote"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                self._status("Submodules updated")
            else:
                self._status(f"Submodule update failed: {result.stderr.strip()}")
                self.log.warning("git_submodule_update_failed", stderr=result.stderr.strip())
        except subprocess.TimeoutExpired:
            self._status("Submodule update timed out")
            self.log.warning("git_submodule_update_timeout")
        except Exception as e:
            self._status(f"Submodule update error: {e}")
            self.log.error("git_submodule_update_error", error=str(e))

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
            purge_banned_high_scores(self.session, settings.get_forbidden_words())
        except Exception as e:
            errors.append(f"Database initialization failed: {e}")

        # Check terminal size
        try:
            self.check_terminal_size()
        except SetupError as e:
            errors.append(str(e))

        # Pull latest changes before discovering games
        self.pull_latest()

        # Discover and validate games
        self._status("Discovering games...")
        valid_games, self.validation_results = discover_games()

        if valid_games:
            self._status(f"Found {len(valid_games)} valid game(s)")
            self.games = register_games(valid_games, self.session)
        else:
            self._status("No valid games found")
            self.log.warning("no_valid_games_found")

        # Check for debug key during setup
        self._status("Press any key within 2 seconds to enter debug mode...")
        raw_key, _ = self.input_handler.read_key(timeout=2)
        if raw_key:
            self.debug_mode = True

        if errors:
            for error in errors:
                self._status(f"ERROR: {error}")
                self.log.error("setup_error", error=error)
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
                    screen = GameSelectScreen(self, selected_index=getattr(self, "selected_game_index", 0))
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
