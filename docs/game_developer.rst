Game Developer Guide
====================

This guide walks you through building a game that runs on the Retro Console.
No prior experience with game development is required — if you can write a
Python program that reads keys and draws to the screen, you can build a game
for the arcade.

Overview
--------

A game for the Retro Console is a **Python package** (a folder with source
code and a ``pyproject.toml`` file). When the console starts, it scans the
``games/`` folder, installs each game's dependencies automatically, and
shows them on the game-select screen.

When a player launches your game, the console runs the command
``uv run play`` inside your game's folder. Your game runs, the player plays,
and when it ends your code writes a score to a file called ``result.json``.
The console reads that file and records the high score.

Setting Up Your Game Package
----------------------------

Your game folder needs to look roughly like this::

    games/
    └── my-game/
        ├── pyproject.toml
        ├── my_game/
        │   └── __init__.py
        └── ...

``pyproject.toml`` — The Package Manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every game needs a ``pyproject.toml`` file. Here is a template you can copy
and adapt:

.. code-block:: toml

    [project]
    name = "my-game"
    version = "0.1.0"
    requires-python = ">=3.10"
    dependencies = [
        "retro>=2.0.0",
    ]

    [project.scripts]
    play = "my_game:main"

    [tool.retro]
    name = "My Game"
    author = "Your Name"
    description = "A short description shown on the game select screen."
    result_file = "result.json"
    log_file = "game.log"

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

The parts that matter most:

``[project.scripts] play = "my_game:main"``
    This tells the console how to start your game. ``my_game`` is the name
    of your Python module and ``main`` is the function to call. When the
    player presses A on the game select screen, the console runs
    ``uv run play``, which calls your ``main()`` function.

``[tool.retro]``
    The console reads these fields to register your game. All five keys
    (``name``, ``author``, ``description``, ``result_file``, and ``log_file``)
    are required.

Writing Your ``main()`` Function
---------------------------------

Your ``main()`` function is the entry point. A minimal skeleton using the
``retro`` library looks like this:

.. code-block:: python

    from retro.game import Game
    from retro.agent import ArrowKeyAgent
    from my_game.state import MyGameState
    from my_game.view import MyGameView

    def main():
        state = MyGameState()
        agents = [ArrowKeyAgent()]
        game = Game(agents, state, dump_state="result.json", log_file="game.log")

        with MyGameView(game) as view:
            game.run()

Key points:

- ``dump_state="result.json"`` tells the ``retro`` library to write the
  game state (including ``score``) to ``result.json`` automatically when
  the game ends. If you don't include this, no score is recorded and the
  high-score screen won't appear.
- ``log_file="game.log"`` must match the ``log_file`` value in your
  ``pyproject.toml`` so that the console knows where to watch for
  sound-effect requests. The path is relative to your game's directory.

Reading the Controls
--------------------

The console passes key mappings to your game via environment variables so
that the physical joystick/gamepad buttons map correctly regardless of how
the hardware is configured. The variables are named ``RETRO_KEY_<BUTTON>``
where ``<BUTTON>`` is one of ``UP``, ``DOWN``, ``LEFT``, ``RIGHT``,
``A``, ``B``, ``C``, ``D``, ``E``, ``F``, ``G``, ``H``.

The ``retro`` library's ``ArrowKeyAgent`` reads these automatically. If you
are building your own input handling, you can read the variables directly:

.. code-block:: python

    import os

    up_key    = os.environ.get("RETRO_KEY_UP",    "KEY_UP")
    down_key  = os.environ.get("RETRO_KEY_DOWN",  "KEY_DOWN")
    left_key  = os.environ.get("RETRO_KEY_LEFT",  "KEY_LEFT")
    right_key = os.environ.get("RETRO_KEY_RIGHT", "KEY_RIGHT")
    a_button  = os.environ.get("RETRO_KEY_A", "z")

Playing Sound Effects
---------------------

The console can play MIDI sound effects while your game is running. To
trigger a sound, call ``game.log()`` with a message in the format
``play <sound_name>``:

.. code-block:: python

    game.log("play jump")
    game.log("play success_large")
    game.log("play lose_a_life")

The console watches your game's log file in real time and plays the
matching ``.mid`` file through the speakers. If the sound file doesn't
exist, the console logs a warning and your game continues unaffected.

The following sounds are available. For guidance on implementing them,
see the :doc:`sound_directory`.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Name
     - Intended use
   * - ``theme_song``
     - Background music on the loading screen.
   * - ``start_game``
     - A game is launched from the select screen.
   * - ``move``
     - Navigating a menu or moving between options.
   * - ``bounce``
     - A ball or object rebounds off a surface.
   * - ``explode``
     - Something explodes or is destroyed.
   * - ``hit_large``
     - A large, heavy impact.
   * - ``hit_medium``
     - A medium impact.
   * - ``hit_small``
     - A small, sharp impact.
   * - ``jump``
     - A player or object jumps.
   * - ``light_hit``
     - A glancing blow or minor collision.
   * - ``lose_a_life``
     - The player loses a life or fails.
   * - ``parry``
     - A defensive move deflects an attack.
   * - ``select``
     - The player confirms a selection.
   * - ``shoot_large``
     - A large projectile is fired.
   * - ``shoot_medium``
     - A medium projectile is fired.
   * - ``shoot_small``
     - A small projectile is fired.
   * - ``success_large``
     - The player completes a level or wins the game.
   * - ``success_medium``
     - A moderately significant achievement.
   * - ``success_small``
     - A small positive event, such as collecting an item or scoring a point.

Testing Your Game Locally
--------------------------

To test your game without the full console, run from inside your game's
folder::

    uv run play

This starts your game directly in the terminal. Press Ctrl-C to quit. The
game won't have joystick mappings (``RETRO_KEY_*`` variables) unless you set
them yourself, so the defaults from the ``retro`` library will be used
(arrow keys and ``z``/``x``/``c``).

To simulate the console environment::

    RETRO_KEY_UP=KEY_UP RETRO_KEY_DOWN=KEY_DOWN RETRO_KEY_A=z uv run play

Common Problems
---------------

**"Missing tool.retro.result_file" error in debug mode**
    Your ``pyproject.toml`` is missing one of the required ``[tool.retro]``
    keys. Check that ``name``, ``author``, ``description``, and
    ``result_file`` are all present.

**Game doesn't appear on the game select screen**
    Enter debug mode (press any key during the 2-second startup window) to
    see validation errors. Common causes: missing ``pyproject.toml``,
    missing ``[project.scripts] play`` entry, or a dependency that failed
    to install.

**Score is not recorded**
    Make sure you pass ``dump_state="result.json"`` to ``Game()``. The
    ``retro`` library writes the score automatically when the game ends.
