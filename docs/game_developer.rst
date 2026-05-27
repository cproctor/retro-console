Game Developer
==============

This guide walks you through building a game that runs on the Retro Console.
You don't need any prior experience with game development — if you can write
a Python program, you can build a game for the arcade.

How it works
------------

A game for the Retro Console is a **Python package** — a folder of Python
code with a configuration file. When the console starts up, it looks inside
the ``games/`` folder, finds your game, and shows it on the game select
screen. When a player chooses your game, the console runs it. When the game
ends, the console reads the player's score and saves it to the high score
table.

Your game doesn't need to do anything special to interact with the console —
you just write a normal Python program using the ``retro`` library, and the
console takes care of the rest.

Setting Up Your Game
--------------------

Your game folder should look like this::

    games/
    └── my-game/
        ├── pyproject.toml
        ├── my_game/
        │   └── __init__.py
        └── ...

The configuration file: ``pyproject.toml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every game needs a file called ``pyproject.toml`` at the top of its folder.
This file tells the console (and Python's packaging tools) everything they
need to know about your game: its name, who wrote it, what libraries it
needs, and how to run it.

Here is a template you can copy and fill in:

.. code-block:: toml

    [project]
    name = "my-game"
    version = "0.1.0"
    requires-python = ">=3.10"
    dependencies = [
        "retro-games>=2.2.0",
    ]

    [project.scripts]
    play = "my_game:main"

    [tool.retro]
    name = "My Game"
    author = "Your Name"
    description = "A short description shown on the game select screen."
    result_file = "result.json"
    log_file = "game.log"
    single_player = true

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

The parts that matter most:

``dependencies``
    Lists the Python libraries your game needs. At minimum you'll want
    ``retro-games``, which provides the ``Game`` class and other tools.
    The console installs these automatically when it first finds your game.

``[project.scripts] play = "my_game:main"``
    This tells the console how to start your game. ``my_game`` is the name
    of your Python module (matching the folder name ``my_game/``) and
    ``main`` is the function inside it to call. When a player presses A on
    the game select screen, the console runs ``uv run play``, which calls
    your ``main()`` function.

``[tool.retro]``
    The console reads these fields to register your game:

    - ``name``, ``author``, ``description``, ``result_file`` — required.
    - ``log_file`` — optional; enables sound effect syncing (see below).
    - ``single_player`` / ``two_player`` — at least one must be ``true``.
      If neither is set, the console defaults to ``single_player = true``
      and logs a warning. See `Two-Player Games`_ for details.

Writing Your ``main()`` Function
---------------------------------

Your ``main()`` function is where your game starts. Here is a minimal
example using the ``retro`` library:

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

A few things to note:

- **``state``** holds the information your game needs to keep track of —
  things like the score, lives remaining, or the positions of objects on
  screen.
- **``agents``** are the things that can act in your game: the player
  character, enemies, items. ``ArrowKeyAgent`` is a built-in agent that
  reads the arrow keys so the player can move.
- **``dump_state="result.json"``** tells the ``retro`` library to save the
  game state (including the score) to a file called ``result.json``
  automatically when the game ends. The console reads this file to record
  the high score. If you leave this out, no score is saved.
- **``log_file="game.log"``** tells the library where to write a log of
  game events. The console watches this file to trigger sound effects. This
  value must match the ``log_file`` setting in your ``pyproject.toml``.

Reading the Controls
--------------------

The console injects the current key mapping into your game as environment
variables when it launches. Use these instead of hardcoding keys directly —
this way your game works correctly even if the key mapping ever changes.

Each variable is named ``RETRO_KEY_<LOGICAL>`` where ``<LOGICAL>`` is the
player-prefixed button name. For example:

.. code-block:: python

    import os

    KEY_UP    = os.environ.get("RETRO_KEY_P1_UP",    "w")
    KEY_DOWN  = os.environ.get("RETRO_KEY_P1_DOWN",  "s")
    KEY_LEFT  = os.environ.get("RETRO_KEY_P1_LEFT",  "a")
    KEY_RIGHT = os.environ.get("RETRO_KEY_P1_RIGHT", "d")
    KEY_A     = os.environ.get("RETRO_KEY_P1_A",     " ")  # space

The full key mapping is:

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Button
     - Logical name
     - P1 key
     - P2 key
     - Env var (P1)
   * - Joystick up
     - UP
     - ``w``
     - ``8``
     - ``RETRO_KEY_P1_UP``
   * - Joystick down
     - DOWN
     - ``s``
     - ``2``
     - ``RETRO_KEY_P1_DOWN``
   * - Joystick left
     - LEFT
     - ``a``
     - ``4``
     - ``RETRO_KEY_P1_LEFT``
   * - Joystick right
     - RIGHT
     - ``d``
     - ``6``
     - ``RETRO_KEY_P1_RIGHT``
   * - Row 1 red
     - A
     - ``space``
     - ``enter``
     - ``RETRO_KEY_P1_A``
   * - Row 1 yellow
     - B
     - ``g``
     - ``k``
     - ``RETRO_KEY_P1_B``
   * - Row 1 green
     - C
     - ``h``
     - ``l``
     - ``RETRO_KEY_P1_C``
   * - Row 1 blue
     - D
     - ``j``
     - ``;``
     - ``RETRO_KEY_P1_D``
   * - Row 2 red
     - E
     - ``t``
     - ``o``
     - ``RETRO_KEY_P1_E``
   * - Row 2 yellow
     - F
     - ``y``
     - ``p``
     - ``RETRO_KEY_P1_F``
   * - Row 2 green
     - G
     - ``u``
     - ``[``
     - ``RETRO_KEY_P1_G``
   * - Row 2 blue
     - H
     - ``i``
     - ``]``
     - ``RETRO_KEY_P1_H``

Substitute ``P2`` for ``P1`` in the env var names to get the Player 2 keys
(e.g. ``RETRO_KEY_P2_UP``).

Two-Player Games
----------------

Declaring player support
~~~~~~~~~~~~~~~~~~~~~~~~~

In your ``pyproject.toml``, set one or both of:

.. code-block:: toml

    [tool.retro]
    single_player = true   # game can be played by one player
    two_player = true      # game can be played by two players

The game select screen shows this information to players. The console does
not manage which mode is active — that is entirely up to your game. Many
games support both modes and switch based on whether a second player's input
is detected at the start.

Result file for two-player games
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When your game ends, it writes ``result.json``. For two-player games, you
may optionally include a ``"winner"`` key:

.. code-block:: json

    {"score": 1234, "winner": 2}

``winner`` must be ``1`` or ``2``. When present, the console hands control
of the high-score entry screen to that player (using their key mapping).
When absent or invalid, Player 1 enters the initials by default.

Playing Sound Effects
---------------------

To play a sound, call ``game.log()`` with the message ``play`` followed by
the sound name:

.. code-block:: python

    game.log("play jump")
    game.log("play success_large")
    game.log("play lose_a_life")

The console watches your game's log file while the game runs. When it sees
a ``play`` message, it looks up the sound by name and plays it through the
speakers. If the sound file doesn't exist, the console notes the problem in
its own log and your game keeps running normally — sounds are never required.

The sounds listed below are available in the default sounds package. For
details on how they are created, see the :doc:`sound_designer` guide.

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

Testing Your Game
-----------------

To try your game without the full console, open a terminal inside your
game's folder and run::

    uv run play

This starts your game directly. Press Ctrl-C to quit. When running this
way, the console hasn't set the ``RETRO_KEY_*`` environment variables, so
use ``os.environ.get("RETRO_KEY_P1_UP", "w")``-style fallbacks (as shown
above) to keep your game playable in both contexts.

Common Problems
---------------

**My game doesn't appear on the game select screen**
    The console checks games for errors when it starts up. Press any key
    during the 2-second startup window to enter debug mode and see a list
    of validation errors. The most common causes are: a missing or
    misspelled field in ``pyproject.toml``, a missing ``play`` entry under
    ``[project.scripts]``, or a library that failed to install.

**"Missing tool.retro.result_file" error in debug mode**
    Your ``pyproject.toml`` is missing one of the required ``[tool.retro]``
    fields. Check that ``name``, ``author``, ``description``, and
    ``result_file`` are all present.

**The score isn't being saved**
    Make sure you pass ``dump_state="result.json"`` to ``Game()``. The
    ``retro`` library writes the score automatically when the game ends.

**The winner isn't getting the high-score screen**
    Check that your ``result.json`` includes ``"winner": 1`` or
    ``"winner": 2`` (an integer, not a string). If the value is missing,
    invalid, or the wrong type, the console defaults to Player 1.
