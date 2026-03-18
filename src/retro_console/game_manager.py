"""Game validation, setup, and execution."""

import json
import os
import subprocess
from pathlib import Path

import tomli

from retro_console import settings
from retro_console.models import get_session, get_or_create_game, record_play, add_high_score


class GameValidationResult:
    """Result of validating a game package."""

    def __init__(self, path):
        self.path = path
        self.valid = False
        self.errors = []
        self.name = None
        self.author = None
        self.description = None
        self.play_script = None
        self.result_file = None

    def add_error(self, error):
        self.errors.append(error)
        self.valid = False


def validate_game(game_path):
    """Validate a game package and return validation result."""
    result = GameValidationResult(game_path)
    pyproject_path = game_path / "pyproject.toml"

    # Check for pyproject.toml
    if not pyproject_path.exists():
        result.add_error("Missing pyproject.toml")
        return result

    # Parse pyproject.toml
    try:
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)
    except Exception as e:
        result.add_error(f"Failed to parse pyproject.toml: {e}")
        return result

    # Check for required keys
    project = pyproject.get("project", {})
    scripts = project.get("scripts", {})
    tool = pyproject.get("tool", {})
    retro = tool.get("retro", {})

    # Get game name from project.name
    result.name = project.get("name")
    if not result.name:
        result.add_error("Missing project.name")

    # Check for play script
    if "play" not in scripts:
        result.add_error("Missing project.scripts.play")
    else:
        result.play_script = scripts["play"]

    # Check for retro tool settings
    if "author" not in retro:
        result.add_error("Missing tool.retro.author")
    else:
        result.author = retro["author"]

    if "description" not in retro:
        result.add_error("Missing tool.retro.description")
    else:
        result.description = retro["description"]

    if "result_file" not in retro:
        result.add_error("Missing tool.retro.result_file")
    else:
        result.result_file = retro["result_file"]

    # If no errors so far, mark as valid
    if not result.errors:
        result.valid = True

    return result


def install_game(game_path):
    """Install a game's dependencies. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["uv", "sync"],
            cwd=game_path,
            capture_output=True,
            text=True,
            timeout=300,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return (success, output)
    except subprocess.TimeoutExpired:
        return (False, "Installation timed out")
    except Exception as e:
        return (False, str(e))


def discover_games():
    """Discover and validate all games in the games directory.

    Returns (valid_games, validation_results) where valid_games is a list
    of GameValidationResult objects for valid games, and validation_results
    is a list of all validation results.
    """
    games_dir = settings.GAMES_DIR
    if not games_dir.exists():
        return ([], [])

    valid_games = []
    all_results = []

    for item in games_dir.iterdir():
        if not item.is_dir():
            continue

        result = validate_game(item)
        all_results.append(result)

        if result.valid:
            # Try to install
            success, output = install_game(item)
            if success:
                valid_games.append(result)
            else:
                result.add_error(f"Installation failed: {output}")

    return (valid_games, all_results)


def register_games(valid_games, session=None):
    """Register valid games in the database."""
    if session is None:
        session = get_session()
    db_games = []

    for game_result in valid_games:
        db_game = get_or_create_game(
            session,
            name=game_result.name,
            package_path=str(game_result.path),
            author=game_result.author,
            description=game_result.description,
        )
        db_games.append(db_game)

    return db_games


def run_game(game, session=None):
    """Run a game and return the result.

    Returns (success, score) where score may be None.
    """
    game_path = Path(game.package_path)

    # Delete any existing result file
    result_file = game_path / "result.json"
    if result_file.exists():
        result_file.unlink()

    # Run the game
    try:
        timeout = settings.MAX_GAME_DURATION
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        env.pop("VIRTUAL_ENV_PROMPT", None)
        for logical, physical in settings.KEY_MAPPING.items():
            env[f"RETRO_KEY_{logical}"] = physical
        result = subprocess.run(
            ["uv", "run", "play"],
            cwd=game_path,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        # Game timed out - still try to read results
        pass
    except Exception as e:
        return (False, None)

    # Try to read the result file
    score = None
    if result_file.exists():
        try:
            with open(result_file) as f:
                data = json.load(f)
                score = data.get("score")
        except Exception:
            pass

    # Record the play
    if session is None:
        session = get_session()
    record_play(session, game, score)

    return (True, score)


def save_high_score(game, initials, score, session=None):
    """Save a high score for a game."""
    if session is None:
        session = get_session()
    add_high_score(session, game, initials, score)
