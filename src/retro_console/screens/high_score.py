"""High score entry screen with virtual keyboard."""

from retro_console import settings
from retro_console.screens.base import Screen
from retro_console.game_manager import save_high_score


# Virtual keyboard layout
KEYBOARD_ROWS = [
    "ABCDEFGHIJ",
    "KLMNOPQRST",
    "UVWXYZ",
]


class HighScoreScreen(Screen):
    """Screen for entering initials for a high score."""

    def __init__(self, app):
        super().__init__(app)
        self.game = app.pending_high_score["game"]
        self.score = app.pending_high_score["score"]
        self.initials = ""
        self.cursor_row = 0
        self.cursor_col = 0
        self.forbidden_words = settings.get_forbidden_words()

    def draw(self):
        """Draw the high score entry screen."""
        t = self.terminal

        # Title
        self.center_text(t.bold + "NEW HIGH SCORE!" + t.normal, 2)

        # Game and score info
        self.center_text(f"Game: {self.game.name}", 5)
        self.center_text(f"Score: {self.score}", 6)

        # Current initials
        initials_display = self.initials + "_" * (3 - len(self.initials))
        self.center_text("Enter your initials:", 9)
        self.center_text(t.bold + f"[ {initials_display} ]" + t.normal, 11)

        # Virtual keyboard
        self._draw_keyboard(14)

        # Instructions — buttons shown only when their action is available
        instructions = t.red + "[A] Select" + t.normal
        if self.initials:
            instructions += "  " + t.yellow + "[B] Delete" + t.normal
        if len(self.initials) == 3 and self._is_valid_initials():
            instructions += "  " + t.green + "[C] Save" + t.normal
        self.center_text(instructions, self.height - 2)

    def _draw_keyboard(self, start_y):
        """Draw the virtual keyboard."""
        for row_idx, row in enumerate(KEYBOARD_ROWS):
            row_str = ""
            for col_idx, char in enumerate(row):
                if row_idx == self.cursor_row and col_idx == self.cursor_col:
                    row_str += self.terminal.reverse + f" {char} " + self.terminal.normal + " "
                else:
                    row_str += f" {char}  "
            self.center_text(row_str, start_y + row_idx * 2)

    def _get_current_char(self):
        """Get the character at the current cursor position."""
        return KEYBOARD_ROWS[self.cursor_row][self.cursor_col]

    def _save_and_exit(self):
        save_high_score(self.game, self.initials, self.score, self.app.session)
        self.app.pending_high_score = None
        self.app.refresh_games()
        return "game_select"

    def handle_input(self):
        """Handle input for initial entry."""
        while True:
            raw_key, logical_key = self.input_handler.read_key()

            if logical_key == "UP":
                if self.cursor_row > 0:
                    self.cursor_row -= 1
                    self._adjust_cursor_col()
                    self.clear()
                    self.draw()

            elif logical_key == "DOWN":
                if self.cursor_row < len(KEYBOARD_ROWS) - 1:
                    self.cursor_row += 1
                    self._adjust_cursor_col()
                    self.clear()
                    self.draw()

            elif logical_key == "LEFT":
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                    self.clear()
                    self.draw()

            elif logical_key == "RIGHT":
                row_len = len(KEYBOARD_ROWS[self.cursor_row])
                if self.cursor_col < row_len - 1:
                    self.cursor_col += 1
                    self.clear()
                    self.draw()

            elif logical_key == "A":
                if len(self.initials) < 3:
                    self.initials += self._get_current_char()
                    self.clear()
                    self.draw()

            elif logical_key == "B":
                if self.initials:
                    self.initials = self.initials[:-1]
                    self.clear()
                    self.draw()

            elif logical_key == "C":
                if len(self.initials) == 3 and self._is_valid_initials():
                    return self._save_and_exit()

    def _adjust_cursor_col(self):
        """Adjust cursor column when changing rows to a shorter row."""
        row_len = len(KEYBOARD_ROWS[self.cursor_row])
        if self.cursor_col >= row_len:
            self.cursor_col = row_len - 1

    def _is_valid_initials(self):
        """Check if initials are valid (not a forbidden word)."""
        return self.initials.upper() not in self.forbidden_words
