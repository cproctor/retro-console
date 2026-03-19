# Retro Console

A retro-style video game console menu system for the terminal. Built with Python using the Blessed library for TUI rendering.

## Features

- Splash screen with ASCII art logo
- Game selection interface with scrolling list
- High score tracking with SQLite database
- Virtual keyboard for entering initials
- Configurable joystick and button mapping
- Debug mode for troubleshooting

## Raspberry Pi Setup

The console is designed to run on a Raspberry Pi with a game controller mapped to keyboard input via AntiMicroX.

### Prerequisites

```bash
sudo apt install antimicrox xterm
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Configure the Pi to auto-login to the desktop (via `raspi-config` > System > Auto Login).

### Install and enable services

```bash
bash config/install.sh
```

This copies the app to `/opt/retro-console`, installs Python dependencies, and enables two systemd user services:

- **antimicrox** — starts AntiMicroX with `config/gamecontroller.amgp` on desktop login
- **retro-console** — opens a fullscreen terminal running `uv run retro-console`

After rebooting the services start automatically. To start them immediately without rebooting:

```bash
systemctl --user start antimicrox retro-console
```

## Installation

```bash
uv sync
```

## Usage

```bash
uv run retro-console
```

### Controls

The console is designed to work with a joystick and buttons that appear as keyboard input. Default mappings:

**Joystick:**
- UP, DOWN, LEFT, RIGHT: Arrow keys
- UPLEFT: Home
- UPRIGHT: Page Up
- DOWNLEFT: End
- DOWNRIGHT: Page Down

**Buttons:**
- A: z
- B: x
- C: c
- D: v
- E: a
- F: s
- G: d
- H: f

### Debug Mode

Press any key during startup to enter debug mode, which displays validation results and drops to a shell.

## Configuration

Edit `src/retro_console/settings.py` to customize:

- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: Terminal dimensions
- `MAX_GAME_DURATION`: Auto-kill games after this many seconds
- `GAMES_DIR`: Directory containing game packages
- `GAME_SELECT_TIMEOUT`: Return to splash after inactivity
- `KEY_MAPPING`: Joystick/button to key mappings

## Adding Games

Games are Python packages in the `games/` directory. Each game must have a `pyproject.toml` with:

```toml
[project]
name = "my-game"

[project.scripts]
play = "my_game.game:main"

[tool.retro]
name = "Game name for display"
author = "Your Name"
description = "A short description of your game"
instructions = "How to play"
result_file = "result.json"
```

When a game ends, it should write a JSON file with the score:

```json
{"score": 1234}
```

Games should use the [retro-games](https://github.com/cproctor/retro) library for terminal rendering.

Games can be added as submodules, allowing authors to keep making changes. In this case, 

```
git submodule add <repo-url> games/<game-name>
git commit -m "Add <game-name> as submodule"
```

## Project Structure

```
src/retro_console/
├── __init__.py
├── settings.py          # Configuration variables
├── models.py            # SQLAlchemy database models
├── input_handler.py     # Joystick/button input mapping
├── game_manager.py      # Game validation and execution
├── main.py              # Application entry point
└── screens/
    ├── __init__.py
    ├── base.py          # Base screen class
    ├── splash.py        # Splash screen
    ├── game_select.py   # Game selection screen
    └── high_score.py    # High score entry screen
```

## License

MIT
