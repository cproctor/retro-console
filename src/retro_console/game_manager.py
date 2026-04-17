"""Game validation, setup, and execution."""

import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

import tomli

from retro_console import settings
from retro_console.logging_setup import get_logger
from retro_console.models import get_session, get_or_create_game, record_play, add_high_score, Game

if TYPE_CHECKING:
    from retro_console.sound_manager import SoundManager

log = get_logger(__name__)

_PLAY_PATTERN = re.compile(r"^\d+: play (\S+)$")


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
        self.log_file = None  # optional; relative to the game directory

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

    # Check for play script
    if "play" not in scripts:
        result.add_error("Missing project.scripts.play")
    else:
        result.play_script = scripts["play"]

    # Check for retro tool settings
    if "name" not in retro:
        result.add_error("Missing tool.retro.name")
    else:
        result.name = retro["name"]

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

    if "log_file" in retro:
        result.log_file = retro["log_file"]
    else:
        log.warning("game_no_log_file", game=game_path.name)

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
    """Register valid games in the database, removing any that no longer exist."""
    if session is None:
        session = get_session()

    valid_paths = {str(g.path) for g in valid_games}
    for db_game in session.query(Game).all():
        if db_game.package_path not in valid_paths:
            session.delete(db_game)
    session.commit()

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


def _watch_log(log_file: Path, sound_manager: "SoundManager", stop: threading.Event) -> None:
    """Background thread: tail log_file and play sounds for 'play <name>' lines.

    The retro Game class truncates the log file to 0 bytes on __init__, so we
    wait for that truncation before opening the file. This avoids the stale-
    position bug where a file handle seeked to the end of a previous run's log
    would sit past EOF forever after the file is truncated.
    """
    deadline = time.monotonic() + 15
    while not stop.is_set():
        if time.monotonic() > deadline:
            return
        try:
            if log_file.stat().st_size == 0:
                break
        except FileNotFoundError:
            pass
        time.sleep(0.05)

    if stop.is_set():
        return

    with open(log_file) as f:
        while not stop.is_set():
            line = f.readline()
            if line:
                m = _PLAY_PATTERN.match(line.strip())
                if m:
                    sound_manager.play(m.group(1))
            else:
                time.sleep(0.05)


def run_game(game, session=None, sound_manager: "SoundManager | None" = None):
    """Run a game and return (success, score). score may be None."""
    game_path = Path(game.package_path)

    result_file = game_path / "result.json"
    if result_file.exists():
        result_file.unlink()

    # Read the game's log file path from its pyproject.toml (optional).
    game_log_path: Path | None = None
    try:
        with open(game_path / "pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
        log_file_rel = pyproject.get("tool", {}).get("retro", {}).get("log_file")
        if log_file_rel:
            game_log_path = game_path / log_file_rel
    except Exception as e:
        log.warning("game_log_path_read_error", game=game.name, error=str(e))

    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env.pop("VIRTUAL_ENV_PROMPT", None)
    for logical, physical in settings.KEY_MAPPING.items():
        env[f"RETRO_KEY_{logical}"] = physical

    if sound_manager is not None:
        sound_manager.play("start_game")

    log.info("game_start", game=game.name)
    stop_watch = threading.Event()
    watch_thread = None

    try:
        proc = subprocess.Popen(
            ["uv", "run", "play"],
            cwd=game_path,
            env=env,
        )

        if sound_manager is not None and game_log_path is not None:
            watch_thread = threading.Thread(
                target=_watch_log,
                args=(game_log_path, sound_manager, stop_watch),
                daemon=True,
            )
            watch_thread.start()

        try:
            proc.wait(timeout=settings.MAX_GAME_DURATION)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    except Exception as e:
        log.error("game_launch_error", game=game.name, error=str(e))
        return (False, None)
    finally:
        stop_watch.set()
        if watch_thread is not None:
            watch_thread.join(timeout=2)

    score = None
    if result_file.exists():
        try:
            with open(result_file) as f:
                data = json.load(f)
                score = data.get("score")
        except Exception:
            pass

    if session is None:
        session = get_session()
    record_play(session, game, score)

    log.info("game_end", game=game.name, score=score)
    return (True, score)


def save_high_score(game, initials, score, session=None):
    """Save a high score for a game."""
    if session is None:
        session = get_session()
    add_high_score(session, game, initials, score)
