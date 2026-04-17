Sound Designer
==============

This guide is for music students who are creating sound effects for the
Retro Console. You don't need to know how to write code — your job is to
compose short pieces of music, save them as MIDI files, and hand them off
to the console manager to install.

How Sound Works
---------------

The Retro Console uses **MIDI** for its sound effects. MIDI is different
from audio formats like MP3 or WAV: instead of storing a recording of
sound, a MIDI file stores *instructions* — which notes to play, on which
instrument, at what volume, and for how long. A program called
**FluidSynth** reads those instructions and generates the actual audio in
real time.

To know what each instrument should sound like, FluidSynth uses a
**SoundFont** — a file that contains recordings of real instruments mapped
to standard instrument numbers. The console comes with a SoundFont called
**General MIDI** (GM), which includes 128 different instrument sounds:
pianos, guitars, strings, brass, percussion, and more. When you compose
your MIDI files, you can use any of these 128 instruments and they will
play correctly on the console.

What You're Creating
--------------------

Your task is to create a **sounds directory** — a folder full of MIDI
files, one for each sound effect. Each file is named after the sound it
represents (for example, ``jump.mid`` or ``explode.mid``).

When a game needs a sound, the console looks in the sounds directory for a
file with the matching name and plays it. The console comes with a basic
set of sounds already included, but your sounds will replace them if you
give your files the same names.

The Sound List
--------------

The table below lists every sound the console and its games can request.
Each sound has a fixed name — your job is to compose a MIDI piece for each
one and save it with exactly that filename (e.g. ``bounce.mid``).

The "When it plays" column describes the situation in the game that
triggers the sound. How you express that moment musically is entirely up
to you.

If game developers need new sounds in the future, this list will be
extended.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Name
     - When it plays
   * - ``theme_song``
     - Loops on the Lockport Arcade loading screen. Stops after 60 seconds
       of no input, or when the player presses a button.
   * - ``start_game``
     - A game is launched from the select screen.
   * - ``move``
     - The player navigates a menu or moves between options.
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

Creating Your MIDI Files
------------------------

You can compose MIDI files with many different tools. Here are a few good
options:

**Digital Audio Workstations (DAWs)**
    Programs like GarageBand, Logic Pro, Ableton Live, or the free LMMS
    can all export MIDI files. Compose your sound effect as a short
    sequence, then export or "bounce" it as MIDI (not as an audio file like
    MP3 or WAV).

**MuseScore**
    MuseScore is free music notation software — you write notes on a staff,
    and it can export the result as a MIDI file. Go to
    File → Export → MIDI (.mid). It's a good choice if you're more
    comfortable with written music than with a piano roll editor.

**Online MIDI editors**
    Several browser-based tools let you draw notes directly onto a grid and
    download the result as a MIDI file. Search for "online piano roll
    editor" or try tools like BeepBox.

Tips for writing arcade sounds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Keep sound effects **short** — under three seconds for most effects, and
  under five seconds for longer pieces like ``start_game``. Players won't
  wait.
- The ``theme_song`` should **loop smoothly**: end on a note or chord that
  flows naturally back to the beginning, because it will repeat
  continuously while the loading screen is showing.
- **Drums and percussion** can be very effective for short, punchy sounds
  like ``move`` or ``hit_small``.
- You can test your MIDI files before submitting them by opening them in
  your DAW or notation software and listening to the playback.

Handing Off Your Work
---------------------

Once you have a folder of ``.mid`` files, give it to the console manager.
They will add it to the console by listing it in the configuration file
(``settings.py``) so the console can find your sounds. Your files will
replace the built-in default sounds for any names that match, so you can
update individual sounds without replacing the whole set.

Troubleshooting
---------------

**My sound plays but sounds wrong — wrong instrument or unexpected notes**
    Open your MIDI file in the tool you used to create it and double-check
    which instrument is assigned to each track. The console uses the
    General MIDI standard, which assigns a specific sound to each of the
    128 instrument numbers. If your DAW was set to a custom instrument
    library, the numbering may be different.

**My sound doesn't play at all**
    Check that the filename exactly matches the name in the sound list above
    — spelling and capitalisation must be exact. Also make sure the file
    has a ``.mid`` or ``.midi`` extension. If the problem persists, ask the
    console manager to check the console's log file for an error message.
