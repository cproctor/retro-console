Sound Directory Guide
=====================

This guide is for music students who are creating sound effects for the
Retro Console. You don't need to know how to write code — you just need to
create MIDI files, organize them in a folder, and tell the console where to
find them.

How Sound Works on the Console
-------------------------------

The Retro Console uses **MIDI** (Musical Instrument Digital Interface) for
sound effects. MIDI files don't contain recorded audio the way an MP3 does.
Instead, they contain *instructions*: which notes to play, on which
instrument, at what volume, and for how long. The console then sends those
instructions to a **synthesizer** (a program called FluidSynth) which
generates the actual audio in real time.

The synthesizer needs a **SoundFont** (.sf2 file) to know what each
instrument should sound like. Think of the SoundFont as a library of
instrument recordings. The console ships with a standard General MIDI
SoundFont (FluidR3 GM) that includes 128 instrument sounds — pianos,
strings, percussion, sound effects, and more.

What Is a Sounds Directory?
----------------------------

A **sounds directory** is a folder containing MIDI files. Each file is a
single sound effect. The console looks up sounds by their file name.

For example, if a game requests the sound ``move``, the console searches for
a file called ``move.midi`` (or ``move.mid``) in the configured sounds
directories. If it finds the file it plays it immediately through the
speakers.

The console searches the sounds directories in the order they are listed in
``settings.py``. If the same sound name exists in two directories, the first
one wins. This lets you override individual sounds without replacing an
entire directory.

The Sound List
--------------

The table below is the canonical list of sounds for the Retro Console.
Each sound has a fixed name; your job as a music student is to implement
each one as a MIDI file. Name the file exactly as shown (e.g.
``bounce.mid``) and place it in your sounds directory.

Games can request any sound on this list — there is no distinction between
"console" sounds and "game" sounds. The description tells you the situation
in which a sound is intended to play; how you express that musically is up
to you.

If game developers need additional sounds in the future, this list will be
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

Creating MIDI Files
-------------------

You can create MIDI files with a wide variety of tools. Here are a few
approaches:

**Digital Audio Workstations (DAWs)**
    Most DAWs (GarageBand, Logic Pro, Ableton Live, LMMS, etc.) can export
    MIDI files. Compose your sound effect as a short MIDI sequence, then
    export or "bounce" it as a MIDI file (not an audio file).

**MuseScore**
    MuseScore is free notation software. Compose a short phrase, then export
    it: File → Export → MIDI (.mid). MuseScore uses General MIDI instrument
    numbers, which work well with the FluidR3 GM SoundFont.

**Online MIDI editors**
    Several browser-based tools let you draw in notes and export MIDI,
    such as BeepBox or Piano Roll editors.

**Tips for good arcade sound effects**

- Keep sounds **short** — under 3 seconds for most effects, under 5 seconds
  for start/end sounds. The player won't wait long.
- Use **General MIDI** instrument numbers (program numbers 1–128) so your
  sounds render correctly with the included SoundFont.
- For the ``theme_song``, make it loop smoothly: end the piece on a note or
  chord that connects naturally back to the beginning.
- **Percussion** (MIDI channel 10) can be very effective for punchy UI
  sounds like ``move`` or ``start_game``.
- Test your files with FluidSynth directly before deploying::

      fluidsynth -ni /usr/share/sounds/sf2/FluidR3_GM.sf2 move.midi

Registering Your Sounds Directory
----------------------------------

Once your folder of MIDI files is ready, an operator adds it to the console
by editing ``src/retro_console/settings.py``:

.. code-block:: python

   SOUNDS_DIRS = [
       Path("/home/pi/my-sounds"),
   ]

Multiple directories can be listed. The console searches them in order::

   SOUNDS_DIRS = [
       Path("/home/pi/my-sounds"),       # checked first
       Path("/home/pi/fallback-sounds"),  # checked if not found above
   ]

After editing ``settings.py``, restart the retro-console service::

    systemctl --user restart retro-console

Troubleshooting
---------------

**Sound plays but sounds wrong or robotic**
    The MIDI file may be using instrument numbers that don't match what you
    intended with the FluidR3 GM SoundFont. Open the file in a MIDI editor
    and check the instrument (program) assignments. Try switching to a
    percussion channel (channel 10) for short attack sounds.

**Sound does not play and the log shows "sound_not_found"**
    The file name doesn't match what the game is requesting. Check spelling
    exactly — names are case-sensitive. Also verify the file has a ``.midi``
    or ``.mid`` extension.

**No sound at all**
    Check that ``SOUNDFONT`` in ``settings.py`` points to a file that exists
    on the Pi. The default path is
    ``/usr/share/sounds/sf2/FluidR3_GM.sf2``; if that file is missing, run
    ``sudo apt-get install fluid-soundfont-gm`` to install it.

    You can also test FluidSynth directly from the command line::

        fluidsynth -ni /usr/share/sounds/sf2/FluidR3_GM.sf2 /path/to/test.midi

    If this produces no sound, the problem is with FluidSynth or the audio
    output device rather than the console configuration.
