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
    The console reads these five fields to register your game. All five are
    required: ``name``, ``author``, ``description``, ``result_file``, and
    ``log_file``.

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

The arcade joystick sends arrow keys, and the two rows of buttons send the
keys ``z``, ``x``, ``c``, ``v`` (top row) and ``a``, ``s``, ``d``, ``f``
(bottom row). You can hardcode these directly in your game:

.. code-block:: python

    # Joystick
    "KEY_UP"    # up
    "KEY_DOWN"  # down
    "KEY_LEFT"  # left
    "KEY_RIGHT" # right

    # Buttons, left to right
    "a"  "s"  "d"  "f"   # top row
    "z"  "x"  "c"  "v"   # bottom row

.. note::

   Two-player games are not yet supported. Each game has access to one
   joystick and one set of buttons.

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
way, the console hasn't set the ``RETRO_KEY_*`` settings, so the defaults
from the ``retro`` library will be used (arrow keys and ``z``/``x``/``c``).

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
    fields. Check that ``name``, ``author``, ``description``,
    ``result_file``, and ``log_file`` are all present.

**The score isn't being saved**
    Make sure you pass ``dump_state="result.json"`` to ``Game()``. The
    ``retro`` library writes the score automatically when the game ends.
