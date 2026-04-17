"""MIDI sound playback via FluidSynth."""

import subprocess
import threading
from pathlib import Path

from retro_console import settings
from retro_console.logging_setup import get_logger

log = get_logger(__name__)


class SoundManager:
    """Plays MIDI files using FluidSynth.

    Searches SOUNDS_DIRS for .mid/.midi files by name. Supports one-shot and
    looping playback. Only one sound plays at a time; calling play() or stop()
    terminates any current playback.
    """

    def __init__(self) -> None:
        self._process: subprocess.Popen | None = None
        self._loop_thread: threading.Thread | None = None
        self._stop_loop = threading.Event()
        self._warn_once: set[str] = set()

    def _warn(self, key: str, **kw) -> None:
        if key not in self._warn_once:
            self._warn_once.add(key)
            log.warning(key, **kw)

    def find_sound(self, name: str) -> Path | None:
        """Return the first matching .mid/.midi file in SOUNDS_DIRS, or None."""
        for sounds_dir in settings.SOUNDS_DIRS:
            for ext in (".midi", ".mid"):
                candidate = Path(sounds_dir) / f"{name}{ext}"
                if candidate.exists():
                    return candidate
        self._warn(f"sound_not_found:{name}", name=name, searched=str(settings.SOUNDS_DIRS))
        return None

    def play(self, name: str, loop: bool = False) -> None:
        """Play a sound by name. Stops any currently playing sound first."""
        self.stop()

        if not settings.SOUNDS_DIRS:
            self._warn("no_sounds_dirs_configured")
            return

        soundfont = settings.SOUNDFONT
        if soundfont is None or not soundfont.exists():
            self._warn("soundfont_not_found", path=str(soundfont))
            return

        sound_file = self.find_sound(name)
        if sound_file is None:
            return

        if loop:
            self._stop_loop.clear()
            self._loop_thread = threading.Thread(
                target=self._loop_play,
                args=(sound_file, soundfont),
                daemon=True,
            )
            self._loop_thread.start()
        else:
            self._launch(sound_file, soundfont)

    def stop(self) -> None:
        """Stop any current playback."""
        self._stop_loop.set()
        proc = self._process
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        self._process = None
        if self._loop_thread is not None and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=3)
        self._loop_thread = None

    def _launch(self, sound_file: Path, soundfont: Path) -> subprocess.Popen | None:
        try:
            proc = subprocess.Popen(
                ["fluidsynth", "-ni", str(soundfont), str(sound_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._process = proc
            return proc
        except FileNotFoundError:
            log.error("fluidsynth_not_found")
            return None
        except Exception as e:
            log.error("fluidsynth_error", error=str(e))
            return None

    def _loop_play(self, sound_file: Path, soundfont: Path) -> None:
        while not self._stop_loop.is_set():
            proc = self._launch(sound_file, soundfont)
            if proc is None:
                break
            proc.wait()
