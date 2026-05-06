# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Retro Console is a Python TUI application that runs on Raspberry Pi as a retro-style arcade menu system. It displays a splash screen, lets players select and launch games, tracks high scores in SQLite, and plays MIDI sound effects via FluidSynth.

## Common Commands

```bash
# Install dependencies
uv sync

# Run the application
uv run retro-console

# Build documentation
cd docs && make html

# Install on Raspberry Pi (copies to /opt, enables systemd services)
bash config/install.sh

# Start systemd services after install
systemctl --user start antimicrox retro-console
```

No test suite exists in this project.

## Architecture

The app uses a **screen-based state machine**. `RetroConsoleApp` (`main.py`) owns a `Terminal`, `InputHandler`, `SoundManager`, and SQLAlchemy session. It runs a loop that instantiates one `Screen` subclass at a time; each `Screen.run()` returns the name of the next screen (`"splash"`, `"game_select"`, `"high_score"`).

**Startup sequence** (inside `RetroConsoleApp.setup`):
1. Init SQLite DB (`models.py`)
2. Git pull + submodule update
3. Discover games: scan `games/` subdirs → validate each `pyproject.toml` → `uv sync` in each game dir → register in DB
4. 2-second debug-mode window

**Screen flow:** Splash → GameSelect → (launches game subprocess) → HighScore (if score qualifies) → GameSelect

**Game execution** (`game_manager.py`):
- Games run as subprocesses: `uv run play` in the game directory
- Key mappings are injected as env vars: `RETRO_KEY_UP`, `RETRO_KEY_A`, etc.
- A background thread tails the game's log file watching for `play <name>` lines to trigger sound effects
- After the subprocess exits, `result.json` is read for the score

**Sound** (`sound_manager.py`): wraps FluidSynth; plays `.mid`/`.midi` files from `sounds/`. SoundFont auto-detected from standard Linux/macOS paths.

**Input** (`input_handler.py`): wraps `blessed`'s terminal input; translates raw keyboard keys to logical button names (`UP`, `A`, `B`, etc.) via `settings.KEY_MAPPING`.

**Screen base class** (`screens/base.py`): provides `move(x, y)` with auto-centering offset, `draw_box()`, and `center_text()`. All rendering uses absolute coordinates within an 80×24 viewport.

## Configuration

All config lives in `src/retro_console/settings.py` — edit directly to change:
- `SCREEN_WIDTH`/`SCREEN_HEIGHT` (default 80×24)
- `GAMES_DIR` (default `games/`)
- `MAX_GAME_DURATION` (default `None` = unlimited)
- `GAME_SELECT_TIMEOUT` (default 60 s)
- `KEY_MAPPING` (joystick/button → keyboard key)
- `SOUNDS_DIRS` (where to find `.mid` files)
- `SOUNDFONT` (auto-detected; override path here)
- `FLUIDSYNTH_AUDIO_DRIVER` (auto-detected: `"pipewire"` if PipeWire socket exists, `"pulseaudio"` if PulseAudio socket exists, `None` for FluidSynth default)

## Adding a Game

Each game is a self-contained Python package under `games/`. It must have:

```toml
# games/my-game/pyproject.toml
[project.scripts]
play = "my_game.game:main"

[tool.retro]
name = "Display Name"
author = "Author"
description = "Short description"
instructions = "How to play"
result_file = "result.json"
log_file = "game.log"   # optional; enables sound effect syncing
```

On exit the game writes `{"score": 1234}` to `result_file`. Games can be added as git submodules:

```bash
git submodule add <repo-url> games/<game-name>
```

## Database

SQLite at `retro_console.db` (relative to CWD). Three tables via SQLAlchemy ORM in `models.py`: `games`, `high_scores`, `plays`. High scores with forbidden 3-letter initials are purged on each startup (`banned_words.txt`).

## Logging

Structlog JSON output to `retro_console.log`. All game lifecycle events, setup steps, and errors are logged with structured key-value fields.
