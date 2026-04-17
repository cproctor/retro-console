"""Splash screen for the retro console."""

from retro_console import settings
from retro_console.screens.base import Screen


LOGO = """
  ██╗      ██████╗  ██████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗
  ██║     ██╔═══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
  ██║     ██║   ██║██║     █████╔╝ ██████╔╝██║   ██║██████╔╝   ██║
  ██║     ██║   ██║██║     ██╔═██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║
  ███████╗╚██████╔╝╚██████╗██║  ██╗██║     ╚██████╔╝██║  ██║   ██║
  ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝
   █████╗ ██████╗  ██████╗ █████╗ ██████╗ ███████╗
  ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝
  ███████║██████╔╝██║     ███████║██║  ██║█████╗
  ██╔══██║██╔══██╗██║     ██╔══██║██║  ██║██╔══╝
  ██║  ██║██║  ██║╚██████╗██║  ██║██████╔╝███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝
"""

# Seconds of inactivity before the theme song stops playing.
THEME_SONG_TIMEOUT = 60


class SplashScreen(Screen):
    """Splash screen displayed on startup."""

    def draw(self):
        """Draw the splash screen with logo and prompt."""
        logo_lines = LOGO.strip().split("\n")
        start_y = (self.height - len(logo_lines) - 4) // 2

        for i, line in enumerate(logo_lines):
            self.center_text(line, start_y + i)

        prompt = "PRESS ANY KEY TO START"
        prompt_y = start_y + len(logo_lines) + 3
        self.center_text(self.terminal.bold + prompt + self.terminal.normal, prompt_y)

    def handle_input(self):
        """Wait for a key press.

        The theme song loops for up to THEME_SONG_TIMEOUT seconds. After that
        it stops, but the splash screen remains until the user presses a key.
        """
        sound_manager = self.app.sound_manager
        sound_manager.play("theme_song", loop=True)

        # Wait up to THEME_SONG_TIMEOUT for a key; if none, stop the music
        # then wait indefinitely for the user to press something.
        key_pressed = self.input_handler.wait_for_any_key(timeout=THEME_SONG_TIMEOUT)
        if not key_pressed:
            sound_manager.stop()
            self.input_handler.wait_for_any_key()
        else:
            sound_manager.stop()

        return "game_select"
