Operator Guide
==============

This section covers installing retro-console on a Raspberry Pi, configuring
it, and keeping it running.

Installation
------------

Prerequisites
~~~~~~~~~~~~~

**Raspberry Pi (Linux)**

- **antimicrox** — translates gamepad input to keyboard events:
  ``sudo apt install antimicrox``
- **uv** — Python package manager:
  ``curl -LsSf https://astral.sh/uv/install.sh | sh``
- **xterm** — terminal emulator used to run the console fullscreen:
  ``sudo apt install xterm``
- Auto-login to the desktop (configure via ``raspi-config`` → System →
  Auto Login).

**macOS (development)**

- **Homebrew**: https://brew.sh
- **uv**: ``curl -LsSf https://astral.sh/uv/install.sh | sh``

Running the Install Script
~~~~~~~~~~~~~~~~~~~~~~~~~~

From the root of the repository, run::

    bash config/install.sh

The script detects the operating system and behaves accordingly.

**On Linux (Raspberry Pi):**

1. Installs **fluidsynth** and the **FluidR3 GM soundfont** via apt.
2. Copies the repository to ``/opt/retro-console``.
3. Initialises git submodules (the game packages).
4. Runs ``uv sync`` to install Python dependencies.
5. Installs and enables systemd user services for retro-console and antimicrox.
6. Enables user linger so services start at boot without a login.

After the script completes, either reboot or start services manually::

    systemctl --user start antimicrox retro-console

**On macOS:**

1. Installs **fluidsynth** via Homebrew.
2. Works in-place in the repository directory (no copy step).
3. Initialises git submodules.
4. Runs ``uv sync``.
5. No services are installed.

Run the console directly::

    uv run retro-console

Running
-------

When installed as a service, retro-console starts automatically on boot inside
a fullscreen xterm window. It pulls the latest code from git, discovers game
packages in the ``games/`` subdirectory, and presents the Lockport Arcade
loading screen.

Controls
~~~~~~~~

The console is designed for use with a USB gamepad mapped through antimicrox.
The default key mapping (configurable in ``settings.py``) is:

======= ==================
Button  Key
======= ==================
UP      Arrow Up
DOWN    Arrow Down
LEFT    Arrow Left
RIGHT   Arrow Right
A       z
B       x
C       c
D       v
======= ==================

On the **game select screen**: use UP/DOWN to scroll through games and press
**A** to launch the selected game. The screen returns to the loading screen
after 60 seconds of inactivity.

Debug Mode
----------

During the 2-second startup window (while the terminal shows initial output),
press any key to enter **debug mode**. Debug mode displays:

- The games directory and database path
- Terminal dimensions
- Validation results for each discovered game package
- All registered games and play counts

After the summary, a shell is opened for manual inspection. Type ``exit`` to
quit retro-console.

Debug mode also activates automatically if any setup step fails (for example,
if the terminal is too small or the database cannot be opened).

Configuration
-------------

All settings live in ``src/retro_console/settings.py``. Edit this file to
change any of the options below, then reinstall (re-run ``install.sh``) or
restart the service.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Setting
     - Default
     - Description
   * - ``SCREEN_WIDTH``
     - ``80``
     - Required terminal width in columns.
   * - ``SCREEN_HEIGHT``
     - ``24``
     - Required terminal height in rows.
   * - ``GAMES_DIR``
     - ``Path("games")``
     - Directory (relative to working directory) containing game packages.
   * - ``MAX_GAME_DURATION``
     - ``None``
     - Maximum seconds a game may run; ``None`` means no limit.
   * - ``GAME_SELECT_TIMEOUT``
     - ``60``
     - Seconds of inactivity on the game select screen before returning to
       the loading screen.
   * - ``DATABASE_PATH``
     - ``Path("retro_console.db")``
     - SQLite database file for high scores and play records.
   * - ``LOG_FILE``
     - ``Path("retro_console.log")``
     - Structured JSON log file written by retro-console itself.
   * - ``SOUNDFONT``
     - ``Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")``
     - Path to a SoundFont (.sf2) file used by FluidSynth for MIDI playback.
       Set to ``None`` to disable sound entirely.
   * - ``SOUNDS_DIRS``
     - ``[]``
     - List of ``Path`` objects pointing to directories that contain MIDI
       sound files. Searched in order when a sound is requested.
