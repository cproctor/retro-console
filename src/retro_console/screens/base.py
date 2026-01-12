"""Base screen class for the retro console."""

from retro_console import settings


class Screen:
    """Base class for all screens."""

    def __init__(self, app):
        self.app = app
        self.terminal = app.terminal
        self.input_handler = app.input_handler

    @property
    def width(self):
        return settings.SCREEN_WIDTH

    @property
    def height(self):
        return settings.SCREEN_HEIGHT

    @property
    def offset_x(self):
        """Horizontal offset to center content on terminal."""
        return (self.terminal.width - self.width) // 2

    @property
    def offset_y(self):
        """Vertical offset to center content on terminal."""
        return (self.terminal.height - self.height) // 2

    def move(self, x, y):
        """Return terminal escape sequence to move cursor to (x, y) with centering offset."""
        return self.terminal.move_xy(self.offset_x + x, self.offset_y + y)

    def clear(self):
        """Clear the screen."""
        print(self.terminal.home + self.terminal.clear)

    def draw(self):
        """Draw the screen. Override in subclasses."""
        raise NotImplementedError

    def handle_input(self):
        """Handle input and return the next screen name or None to stay.

        Override in subclasses.
        """
        raise NotImplementedError

    def run(self):
        """Run the screen loop. Returns the name of the next screen."""
        self.clear()
        self.draw()
        return self.handle_input()

    def center_text(self, text, y=None):
        """Print text centered horizontally."""
        x = (self.width - len(text)) // 2
        if y is not None:
            print(self.move(x, y) + text)
        else:
            print(" " * x + text)

    def draw_box(self, x, y, width, height, title=None):
        """Draw a box with optional title."""
        # Top border
        if title:
            title_part = f" {title} "
            left_border = (width - len(title_part) - 2) // 2
            right_border = width - len(title_part) - left_border - 2
            top = "┌" + "─" * left_border + title_part + "─" * right_border + "┐"
        else:
            top = "┌" + "─" * (width - 2) + "┐"
        print(self.move(x, y) + top)

        # Sides
        for i in range(1, height - 1):
            print(self.move(x, y + i) + "│" + " " * (width - 2) + "│")

        # Bottom border
        bottom = "└" + "─" * (width - 2) + "┘"
        print(self.move(x, y + height - 1) + bottom)

    def draw_text_in_box(self, x, y, width, text):
        """Draw text inside a box area, truncating if needed."""
        max_width = width - 2
        if len(text) > max_width:
            text = text[:max_width - 3] + "..."
        print(self.move(x + 1, y) + text)
