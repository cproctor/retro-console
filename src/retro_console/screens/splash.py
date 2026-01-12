"""Splash screen for the retro console."""

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


class SplashScreen(Screen):
    """Splash screen displayed on startup."""

    def draw(self):
        """Draw the splash screen with logo and prompt."""
        # Draw the logo centered
        logo_lines = LOGO.strip().split("\n")
        start_y = (self.height - len(logo_lines) - 4) // 2

        for i, line in enumerate(logo_lines):
            self.center_text(line, start_y + i)

        # Draw prompt
        prompt = "PRESS ANY KEY TO START"
        prompt_y = start_y + len(logo_lines) + 3
        self.center_text(self.terminal.bold + prompt + self.terminal.normal, prompt_y)

    def handle_input(self):
        """Wait for any key press to continue."""
        self.input_handler.wait_for_any_key()
        return "game_select"
