Console Manager
===============

This guide is for the person responsible for setting up and running the
Lockport Arcade machine. You'll learn how to install the software, keep it
running, and troubleshoot problems.

Installation
------------

What you'll need
~~~~~~~~~~~~~~~~

The console runs on a **Raspberry Pi** — a small, inexpensive computer that
connects to a monitor and speakers. Before running the install script, make
sure the following are set up:

**On the Raspberry Pi:**

- **antimicrox** — a program that translates gamepad button presses into
  keyboard keys, so the console can read them. Install it with::

      sudo apt install antimicrox

- **uv** — a tool that downloads and manages the Python libraries the console
  depends on. Install it with::

      curl -LsSf https://astral.sh/uv/install.sh | sh

- **xterm** — a terminal window that the console runs inside. Install it with::

      sudo apt install xterm

- **Auto-login** — the Pi should log in to the desktop automatically when it
  starts up, without waiting for a password. Set this in
  ``raspi-config`` → System → Auto Login.

**On macOS (for development and testing only):**

- **Homebrew** — a package manager for macOS: https://brew.sh
- **uv** — install with::

      curl -LsSf https://astral.sh/uv/install.sh | sh

Running the install script
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the prerequisites are in place, open a terminal in the retro-console
folder and run::

    bash config/install.sh

The script detects whether it's running on a Raspberry Pi or a Mac and does
the right thing automatically.

**On the Raspberry Pi, the script will:**

1. Install **FluidSynth** (the program that plays MIDI sound effects) and a
   standard set of instrument sounds.
2. Copy the console software to ``/opt/retro-console``, a system folder that
   stays out of the way.
3. Download and set up the game packages.
4. Install and start the console as a **background service** — meaning it will
   start automatically every time the Pi boots, without you having to do
   anything.

When it's done, either reboot the Pi or start the console right away::

    systemctl --user start antimicrox retro-console

**On macOS, the script will:**

1. Install FluidSynth via Homebrew.
2. Set up everything in-place inside the folder you're working in.
3. No background service is installed — run the console manually when you need
   it::

       uv run retro-console

Running the Console
-------------------

On the Raspberry Pi the console starts itself after every reboot. It
pulls the latest code from the internet, finds all the games in the
``games/`` folder, and shows the **Lockport Arcade** loading screen.

Controls
~~~~~~~~

The console uses two USB gamepads — one for each player. The gamepad buttons
are translated to keyboard keys by **antimicrox** using the profiles in
``config/``. Either player can navigate the console menus.

.. list-table::
   :header-rows: 1
   :widths: 15 15 15 15

   * - Button
     - Logical name
     - Player 1 key
     - Player 2 key
   * - Joystick up
     - UP
     - ``w``
     - ``8``
   * - Joystick down
     - DOWN
     - ``s``
     - ``2``
   * - Joystick left
     - LEFT
     - ``a``
     - ``4``
   * - Joystick right
     - RIGHT
     - ``d``
     - ``6``
   * - Row 1 red (A)
     - A
     - ``space``
     - ``enter``
   * - Row 1 yellow (B)
     - B
     - ``g``
     - ``k``
   * - Row 1 green (C)
     - C
     - ``h``
     - ``l``
   * - Row 1 blue (D)
     - D
     - ``j``
     - ``;``
   * - Row 2 red (E)
     - E
     - ``t``
     - ``o``
   * - Row 2 yellow (F)
     - F
     - ``y``
     - ``p``
   * - Row 2 green (G)
     - G
     - ``u``
     - ``[``
   * - Row 2 blue (H)
     - H
     - ``i``
     - ``]``

On the **game select screen**: press UP or DOWN to scroll through games and
press **A** to launch one. If nobody touches the controls for 60 seconds, the
screen returns to the loading screen automatically.

Updating the key mapping
~~~~~~~~~~~~~~~~~~~~~~~~

If you change ``KEY_MAPPING`` in ``settings.py`` or update the antimicrox
profile files, antimicrox must be restarted for the changes to take effect::

    systemctl --user restart antimicrox

The console does this automatically at startup whenever it detects that a
profile file is newer than antimicrox's last start.

Setting up the Player 2 controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Player 2 antimicrox profile is stored in
``config/gamecontroller_p2.amgp``. Before it will work, you need to fill in
the Player 2 controller's unique ID:

1. Connect the Player 2 USB gamepad.
2. Open ``antimicrox`` in the graphical interface.
3. Select the Player 2 controller and note its **Unique ID**.
4. Open ``config/gamecontroller_p2.amgp`` in a text editor and replace
   ``REPLACE_WITH_P2_CONTROLLER_UNIQUE_ID`` with the actual ID.
5. Update ``config/systemd/antimicrox.service`` to add a second
   ``--profile`` flag pointing to ``gamecontroller_p2.amgp`` (instructions
   are in a comment inside that file).
6. Re-run ``bash config/install.sh`` and restart the services.

Adding Games
------------

Games live in the ``games/`` folder as regular Python packages. The console
finds and loads them automatically on startup.

.. note::

   Do not add games as git submodules. Keep them as plain files inside the
   repo. Submodules add complexity and can expose student information (git
   commit authors and email addresses) that should stay private.

Step-by-step: adding a student game
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These steps are written for a teacher who has received a game from a student
and wants to add it to the arcade.

1. **Copy the game into the** ``games/`` **folder.**

   Give the subfolder a short, lowercase name with no spaces, for example::

       games/student-pong/

   The folder should contain at least a ``pyproject.toml`` and the game's
   Python source code.

2. **Check** ``pyproject.toml`` **for required fields.**

   Open ``games/student-pong/pyproject.toml`` and verify that the
   ``[tool.retro]`` section contains at minimum:

   .. code-block:: toml

       [tool.retro]
       name = "Student Pong"
       author = "Student Name"
       description = "A short description."
       result_file = "result.json"
       single_player = true

   If any of these are missing, add them. If neither ``single_player`` nor
   ``two_player`` is set the console will still load the game (defaulting to
   ``single_player = true``) but will log a warning.

3. **Commit the game to the repository.**::

       git add games/student-pong
       git commit -m "Add student-pong game"
       git push

4. **Restart the console** (or wait for the Pi to reboot). The console
   pulls the latest code and discovers the new game automatically. You can
   also press **B** on the game select screen to trigger an immediate rescan
   without restarting.

Troubleshooting a game that won't appear
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Press any key during the 2-second startup window to enter **debug mode**.
Debug mode shows the validation result for every game in the ``games/``
folder, including specific error messages. Common issues:

- **Missing field in** ``[tool.retro]`` — add the missing key.
- **Missing** ``[project.scripts] play = "..."`` — the console needs this to
  know how to launch the game.
- **Dependency install failed** — the game's ``pyproject.toml`` may require
  a package that can't be installed on the Pi. Check the error message and
  simplify the dependency list if needed.
- **Syntax error in** ``pyproject.toml`` — validate the TOML with an online
  checker.

Debug Mode
----------

When the console starts up, it shows a few lines of status text for about
two seconds. If you press any key during that window, it enters **debug
mode** — a diagnostic view that shows you what's going on under the hood.

Debug mode displays:

- Where the games folder and database are located
- How big the terminal window is (the console requires at least 80×24)
- Whether each game was loaded successfully, and any errors if not
- A list of all registered games and how many times each has been played

After showing the summary, it drops you into a shell so you can inspect
things manually. Type ``exit`` when you're done and the console will close.

Debug mode also turns on automatically if something goes wrong during
startup — for example if the terminal window is too small, or the database
can't be opened.

Configuration
-------------

All settings are in ``src/retro_console/settings.py``. Open that file in a
text editor, make your changes, then reinstall (re-run ``install.sh``) or
restart the service for them to take effect.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Setting
     - Default
     - What it does
   * - ``SCREEN_WIDTH``
     - ``80``
     - Minimum terminal width (in characters) required to run.
   * - ``SCREEN_HEIGHT``
     - ``24``
     - Minimum terminal height (in lines) required to run.
   * - ``GAMES_DIR``
     - ``Path("games")``
     - Folder containing the game packages, relative to where the console
       is installed.
   * - ``MAX_GAME_DURATION``
     - ``None``
     - Maximum time (in seconds) a game is allowed to run before being
       stopped automatically. ``None`` means no limit.
   * - ``GAME_SELECT_TIMEOUT``
     - ``60``
     - Seconds of no input on the game select screen before returning to
       the loading screen.
   * - ``DATABASE_PATH``
     - ``Path("retro_console.db")``
     - File where high scores and play history are saved.
   * - ``LOG_FILE``
     - ``Path("retro_console.log")``
     - File where the console writes its own activity log, useful for
       diagnosing problems.
   * - ``KEY_MAPPING``
     - see table above
     - Maps logical button names (``P1_UP``, ``P2_A``, …) to keyboard key
       strings. After changing this, restart antimicrox (the console does
       this automatically on the next startup).
   * - ``SOUNDFONT``
     - auto-detected
     - The instrument library used for MIDI sound playback. The install
       script sets this up automatically. Set to ``None`` to turn off
       sound entirely.
   * - ``SOUNDS_DIRS``
     - ``[Path("sounds")]``
     - A list of folders to search for sound effect files. The console
       checks each folder in order and plays the first match it finds.
       Add your own sounds folder at the front of the list to override
       the defaults.
