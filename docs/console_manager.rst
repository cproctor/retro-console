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

The console is designed for a USB gamepad. The gamepad buttons are mapped
to keyboard keys by antimicrox using the following defaults (you can change
these in ``settings.py`` if your gamepad is wired differently):

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

On the **game select screen**: press UP or DOWN to scroll through games and
press **A** to launch one. If nobody touches the controls for 60 seconds, the
screen returns to the loading screen automatically.

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
