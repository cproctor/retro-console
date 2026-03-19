"""Game selection screen for the retro console."""

from retro_console import settings
from retro_console.screens.base import Screen
from retro_console.game_manager import run_game


class GameSelectScreen(Screen):
    """Screen for selecting a game to play."""

    def __init__(self, app, selected_index=0):
        super().__init__(app)
        self.games = app.games
        self.selected_index = selected_index
        self.scroll_offset = 0
        self.list_height = self.height - 4  # Leave room for borders

    def draw(self):
        """Draw the game selection screen."""
        # Calculate layout - left panel for list, right for details
        list_width = self.width // 3
        detail_width = self.width - list_width - 1

        # Draw game list panel
        self.draw_box(0, 0, list_width, self.height, "GAMES")
        self._draw_game_list(1, 1, list_width - 2)

        # Reset terminal state before drawing details panel (clears any reverse from game list)
        print(self.terminal.normal, end='', flush=True)

        # Draw details panel
        detail_title = self.games[self.selected_index].name if self.games else "DETAILS"
        max_title_len = detail_width - 4
        if len(detail_title) > max_title_len:
            detail_title = detail_title[:max_title_len - 1] + "…"
        self.draw_box(list_width, 0, detail_width, self.height, detail_title)
        self._draw_game_details(list_width + 1, 1, detail_width - 2)

    def _draw_game_list(self, x, y, width):
        """Draw the scrollable list of games."""
        if not self.games:
            print(self.move(x, y) + "No games found")
            return

        visible_count = self.list_height - 2

        # Adjust scroll offset if needed
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1

        # Draw visible games
        for i in range(visible_count):
            game_index = self.scroll_offset + i
            if game_index >= len(self.games):
                break

            game = self.games[game_index]
            name = game.name[:width - 4]

            if game_index == self.selected_index:
                # Highlight selected game
                line = self.terminal.reverse + "> " + name.ljust(width - 2) + self.terminal.normal
            else:
                line = self.terminal.normal + "  " + name

            print(self.move(x, y + i + 1) + line[:width])

        # Draw scroll indicators
        if self.scroll_offset > 0:
            print(self.move(x + width - 1, y) + "^")
        if self.scroll_offset + visible_count < len(self.games):
            print(self.move(x + width - 1, y + visible_count + 1) + "v")

    def _draw_game_details(self, x, y, width):
        """Draw details for the selected game."""
        if not self.games:
            return

        game = self.games[self.selected_index]
        line = y + 1
        t = self.terminal

        # Game name
        print(self.move(x, line) + t.bold + game.name + t.normal)
        line += 2

        # Author
        print(self.move(x, line) + f"Author: {game.author or 'Unknown'}")
        line += 2

        # Description - word wrap
        desc = game.description or "No description"
        desc_lines = self._wrap_text(desc, width - 2)
        for desc_line in desc_lines[:4]:  # Limit to 4 lines
            print(self.move(x, line) + desc_line)
            line += 1
        line += 1

        # Play count
        print(self.move(x, line) + f"Times played: {game.play_count}")
        line += 2

        # High scores
        print(self.move(x, line) + t.underline + "HIGH SCORES" + t.normal)
        line += 1

        top_scores = game.get_top_scores(10)
        if top_scores:
            for i, score in enumerate(top_scores, 1):
                score_line = f"{i:2}. {score.initials:3} {score.score:>8}"
                print(self.move(x, line) + score_line)
                line += 1
        else:
            print(self.move(x, line) + "No high scores yet")
            line += 1

        # Instructions at bottom
        t = self.terminal
        print(self.move(x, self.height - 2) + t.red + "[A] Play" + t.normal + "  [UP/DOWN] Select")

    def _wrap_text(self, text, width):
        """Simple word wrapping."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def handle_input(self):
        """Handle input for game selection."""
        timeout = settings.GAME_SELECT_TIMEOUT

        while True:
            raw_key, logical_key = self.input_handler.read_key(timeout=timeout)

            # Timeout - return to splash
            if raw_key is None:
                return "splash"

            if logical_key == "UP":
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self.clear()
                    self.draw()

            elif logical_key == "DOWN":
                if self.selected_index < len(self.games) - 1:
                    self.selected_index += 1
                    self.clear()
                    self.draw()

            elif logical_key == "A":
                if self.games:
                    return self._play_selected_game()

    def _play_selected_game(self):
        """Play the selected game and handle the result."""
        game = self.games[self.selected_index]

        self.clear()
        self.center_text(f"Starting {game.name}...", self.height // 2)

        success, score = run_game(game, self.app.session)

        # Restore terminal state after subprocess (game's blessed context emits show-cursor on exit)
        print(self.terminal.normal + self.terminal.hide_cursor, end='', flush=True)
        print(self.terminal.home + self.terminal.clear)

        # Refresh game data from database
        self.app.refresh_games()
        self.games = self.app.games
        self.app.selected_game_index = self.selected_index

        if score is not None and game.is_high_score(score):
            # Store for high score entry
            self.app.pending_high_score = {
                "game": game,
                "score": score,
            }
            return "high_score"

        # Return to game select screen
        return "game_select"
