"""Settings for the retro console. Configure by editing this file."""

from pathlib import Path

# Screen dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

# Debug settings
DEBUG_KEY = "KEY_F12"

# Game settings
MAX_GAME_DURATION = None  # Set to number of seconds, or None for no limit
GAMES_DIR = Path("games")

# High score settings
FORBIDDEN_WORDS_FILE = None  # Path to file with forbidden three-letter words

# Timeout settings
GAME_SELECT_TIMEOUT = 60  # Seconds of inactivity before returning to splash

# Database settings
DATABASE_PATH = Path("retro_console.db")

# Key mapping: logical button names to keyboard key names
KEY_MAPPING = {
    # Joystick directions
    "UP": "KEY_UP",
    "LEFT": "KEY_LEFT",
    "DOWN": "KEY_DOWN",
    "RIGHT": "KEY_RIGHT",
    # Action buttons
    "A": "z",
    "B": "x",
    "C": "c",
    "D": "v",
    "E": "a",
    "F": "s",
    "G": "d",
    "H": "f",
}

# Reverse mapping for quick lookup
_KEY_TO_LOGICAL = {v: k for k, v in KEY_MAPPING.items()}


def get_logical_key(key_name):
    """Convert a keyboard key name to a logical button name."""
    return _KEY_TO_LOGICAL.get(key_name)


def get_forbidden_words():
    """Load forbidden words from file if specified."""
    if FORBIDDEN_WORDS_FILE is None:
        return set()

    path = Path(FORBIDDEN_WORDS_FILE)
    if not path.exists():
        return set()

    words = set()
    with open(path, "r") as f:
        for line in f:
            word = line.strip().upper()
            if len(word) == 3:
                words.add(word)
    return words
