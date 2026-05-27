"""Settings for the retro console. Configure by editing this file."""

import os
from pathlib import Path

# Screen dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

# Game settings
MAX_GAME_DURATION = None  # Set to number of seconds, or None for no limit
GAMES_DIR = Path("games")

# High score settings
FORBIDDEN_WORDS_FILE = Path(__file__).parent / "banned_words.txt"

# Timeout settings
GAME_SELECT_TIMEOUT = 60  # Seconds of inactivity before returning to splash

# Database settings
DATABASE_PATH = Path("retro_console.db")

# Logging
LOG_FILE = Path("retro_console.log")

# Sound settings
# Path to a SoundFont (.sf2) file for FluidSynth.
# Auto-detected from known install locations; set explicitly to override.
def _find_soundfont() -> Path | None:
    candidates = [
        Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"),                               # Debian/Ubuntu
        Path("/opt/homebrew/share/fluid-synth/sf2/VintageDreamsWaves-v2.sf2"),      # macOS Homebrew (Apple Silicon)
        Path("/usr/local/share/fluid-synth/sf2/VintageDreamsWaves-v2.sf2"),         # macOS Homebrew (Intel)
        Path("/usr/share/sounds/sf2/default.sf2"),                                   # Some Linux distros
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

SOUNDFONT: Path | None = _find_soundfont()

# FluidSynth audio driver. Auto-detected from running audio system.
# Set explicitly to override (e.g. "alsa", "pulseaudio", "pipewire").
def _find_audio_driver() -> str | None:
    uid = os.getuid()
    if Path(f"/run/user/{uid}/pipewire-0").exists():
        return "pipewire"
    if Path(f"/run/user/{uid}/pulse").exists():
        return "pulseaudio"
    return None

FLUIDSYNTH_AUDIO_DRIVER: str | None = _find_audio_driver()

# Directories to search (in order) for MIDI sound files.
# Each entry is a Path to a directory containing .mid or .midi files.
SOUNDS_DIRS: list[Path] = [Path("sounds")]

# Key mapping: logical button names (P1_/P2_ prefixed) to keyboard key strings.
#
# Values are what blessed returns: key.name for sequences (e.g. "KEY_ENTER"),
# or str(key) for regular characters (e.g. "w", " ", "\n").
#
# Physical layout:
#   Joystick directions → UP / DOWN / LEFT / RIGHT
#   Row 1 buttons (red / yellow / green / blue) → A / B / C / D
#   Row 2 buttons (red / yellow / green / blue) → E / F / G / H
#
# Player 1:
#   Joystick → w / s / a / d
#   Row 1    → space / g / h / j
#   Row 2    → t / y / u / i
#
# Player 2:
#   Joystick → 8 / 2 / 4 / 6
#   Row 1    → enter / k / l / ;
#   Row 2    → o / p / [ / ]
KEY_MAPPING = {
    # Player 1 — joystick
    "P1_UP":    "w",
    "P1_DOWN":  "s",
    "P1_LEFT":  "a",
    "P1_RIGHT": "d",
    # Player 1 — Row 1 buttons
    "P1_A": " ",    # red
    "P1_B": "g",    # yellow
    "P1_C": "h",    # green
    "P1_D": "j",    # blue
    # Player 1 — Row 2 buttons
    "P1_E": "t",    # red
    "P1_F": "y",    # yellow
    "P1_G": "u",    # green
    "P1_H": "i",    # blue
    # Player 2 — joystick
    "P2_UP":    "8",
    "P2_DOWN":  "2",
    "P2_LEFT":  "4",
    "P2_RIGHT": "6",
    # Player 2 — Row 1 buttons
    "P2_A": "\n",   # red   — enter
    "P2_B": "k",    # yellow
    "P2_C": "l",    # green
    "P2_D": ";",    # blue
    # Player 2 — Row 2 buttons
    "P2_E": "o",    # red
    "P2_F": "p",    # yellow
    "P2_G": "[",    # green
    "P2_H": "]",    # blue
}


def get_ui_action(logical_key):
    """Strip the P1_/P2_ player prefix to get the generic action for UI navigation.

    Both 'P1_UP' and 'P2_UP' return 'UP', so all console screens respond
    identically to either player's input.  Returns None if logical_key is None.
    """
    if logical_key is None:
        return None
    if logical_key.startswith(("P1_", "P2_")):
        return logical_key[3:]
    return logical_key


def get_player(logical_key):
    """Return 1, 2, or None based on the player prefix of a logical key."""
    if logical_key is None:
        return None
    if logical_key.startswith("P1_"):
        return 1
    if logical_key.startswith("P2_"):
        return 2
    return None


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
            if word and not word.startswith("#") and len(word) == 3:
                words.add(word)
    return words
