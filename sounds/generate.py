#!/usr/bin/env python3
"""Generate chiptune MIDI sound effects for the retro-console sounds directory.

Re-run this script any time you want to regenerate the .mid files:
    python generate.py
"""
import struct
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# MIDI primitives
# ---------------------------------------------------------------------------

def vlq(n: int) -> bytes:
    """Encode n as a MIDI variable-length quantity."""
    if n == 0:
        return b'\x00'
    groups = []
    groups.append(n & 0x7F)
    n >>= 7
    while n:
        groups.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(groups))


def make_midi(events: list[tuple[int, bytes]], tempo: int = 500_000, ticks: int = 480) -> bytes:
    """Build a single-track Format-0 MIDI file at the given tempo.

    events: list of (delta_ticks, event_bytes)
    tempo:  microseconds per beat (500000 = 120 BPM)
    ticks:  ticks per beat
    """
    body = bytearray()
    body += vlq(0) + b'\xff\x51\x03' + tempo.to_bytes(3, 'big')
    for dt, ev in events:
        body += vlq(dt) + bytes(ev)
    body += vlq(0) + b'\xff\x2f\x00'
    return (
        b'MThd' + struct.pack('>IHHH', 6, 0, 1, ticks)
        + b'MTrk' + struct.pack('>I', len(body)) + bytes(body)
    )


def pc(prog: int, ch: int = 0) -> bytes:
    """Program change. prog is 0-indexed GM (0–127)."""
    return bytes([0xC0 | ch, prog])


def on(note: int, vel: int = 100, ch: int = 0) -> bytes:
    return bytes([0x90 | ch, note, vel])


def off(note: int, ch: int = 0) -> bytes:
    return bytes([0x80 | ch, note, 0])


# ---------------------------------------------------------------------------
# Note durations (ticks at 480 ticks/beat)
# ---------------------------------------------------------------------------
T = 60     # 32nd note
S = 120    # 16th note
E = 240    # 8th note
Q = 480    # quarter note
H = 960    # half note
W = 1920   # whole note

# ---------------------------------------------------------------------------
# GM instrument programs, 0-indexed
# ---------------------------------------------------------------------------
SQUARE = 79   # Lead 1 (Square)   — main chiptune voice
SAW    = 80   # Lead 2 (Sawtooth) — heavier hits and zaps


def seq(
    prog: int,
    melody: list[tuple[int, int]],
    vel: int = 100,
    legato: bool = False,
) -> list[tuple[int, bytes]]:
    """Convert [(pitch, duration_ticks), ...] into MIDI events.

    With legato=False each note sounds for 85% of its duration so there is
    a small gap between notes (classic chiptune staccato feel).
    """
    ratio = 1.0 if legato else 0.85
    events: list[tuple[int, bytes]] = [(0, pc(prog))]
    gap = 0
    for note, dur in melody:
        sounding = max(1, int(dur * ratio))
        events.append((gap, on(note, vel)))
        events.append((sounding, off(note)))
        gap = dur - sounding
    return events


# ---------------------------------------------------------------------------
# Sound definitions
# ---------------------------------------------------------------------------

SOUNDS: dict[str, list[tuple[int, bytes]]] = {}

# --- Retro Console UI sounds ------------------------------------------------

# theme_song — 8-bar looping chiptune in C major (16 s at 120 BPM, ~4 loops
# before the 60-second timeout stops playback).
# Chord sequence: I – IV – V – I – I – vi – VII – I
SOUNDS['theme_song'] = seq(SQUARE, [
    # Bar 1  I   C5 E5 G5 E5
    (72, Q), (76, Q), (79, Q), (76, Q),
    # Bar 2  IV  F5 A5 C6 A5
    (77, Q), (81, Q), (84, Q), (81, Q),
    # Bar 3  V   G5 B5 D6 B5
    (79, Q), (83, Q), (86, Q), (83, Q),
    # Bar 4  I   C6(H) G5(H)
    (84, H), (79, H),
    # Bar 5  I   C5 E5 G5 E5
    (72, Q), (76, Q), (79, Q), (76, Q),
    # Bar 6  vi  A5 E5 C5 E5
    (81, Q), (76, Q), (72, Q), (76, Q),
    # Bar 7  VII descending walk G5 F5 E5 D5
    (79, Q), (77, Q), (76, Q), (74, Q),
    # Bar 8  I   C5 whole — loops cleanly back to bar 1
    (72, W),
], vel=90, legato=True)

# start_game — energetic ascending C major arpeggio with a held high note
SOUNDS['start_game'] = seq(SQUARE, [
    (60, E), (64, E), (67, E),   # C4 E4 G4
    (72, E), (76, E), (79, E),   # C5 E5 G5
    (84, H + Q),                  # C6 held
], vel=110)

# move — two-note ascending blip for menu navigation
SOUNDS['move'] = seq(SQUARE, [
    (79, S),   # G5
    (84, S),   # C6
], vel=75)

# --- Game sounds ------------------------------------------------------------

# bounce — short upward chirp (ball hitting a wall, block landing, etc.)
SOUNDS['bounce'] = seq(SQUARE, [
    (67, S),   # G4
    (72, S),   # C5
    (79, E),   # G5
], vel=90)

# explode — rapid descending chromatic burst fading to low rumble
SOUNDS['explode'] = seq(SAW, [
    (72, T), (71, T), (69, T), (67, T),   # C5 B4 A4 G4
    (65, T), (62, T), (57, T),            # F4 D4 A3
    (48, Q),                               # C3 — low thud
], vel=120)

# hit_large — heavy low impact
SOUNDS['hit_large'] = seq(SAW, [
    (48, E),   # C3
    (43, Q),   # G2
], vel=127)

# hit_medium — solid mid-range impact
SOUNDS['hit_medium'] = seq(SQUARE, [
    (60, S),   # C4
    (55, E),   # G3
], vel=110)

# hit_small — quick sharp sting
SOUNDS['hit_small'] = seq(SQUARE, [
    (84, T),   # C6
], vel=100)

# jump — rapid ascending scale burst
SOUNDS['jump'] = seq(SQUARE, [
    (60, T), (64, T), (67, T), (72, T),   # C4 E4 G4 C5
    (76, E),                               # E5
], vel=95)

# light_hit — gentle soft tap (glancing blow, small collision)
SOUNDS['light_hit'] = seq(SQUARE, [
    (76, S),   # E5
], vel=55)

# lose_a_life — classic chromatic descending "wah-wah" phrase
SOUNDS['lose_a_life'] = seq(SQUARE, [
    (72, E),   # C5
    (71, E),   # B4
    (70, E),   # Bb4
    (69, E),   # A4
    (68, E),   # Ab4
    (65, E),   # F4
    (60, H),   # C4 — held
], vel=90)

# parry — sharp metallic deflect (high note, silence, high note)
SOUNDS['parry'] = seq(SQUARE, [
    (88, T),   # E6 — very high
    (84, T),   # C6
    (88, S),   # E6 again
], vel=127)

# select — ascending fifth confirmation
SOUNDS['select'] = seq(SQUARE, [
    (72, E),   # C5
    (79, Q),   # G5
], vel=90)

# shoot_large — low descending sawtooth zap
SOUNDS['shoot_large'] = seq(SAW, [
    (67, E),   # G4
    (60, E),   # C4
    (53, Q),   # F3
], vel=110)

# shoot_medium — mid-range two-step zap
SOUNDS['shoot_medium'] = seq(SQUARE, [
    (79, S),   # G5
    (74, S),   # D5
    (67, E),   # G4
], vel=95)

# shoot_small — quick high-pitched blip
SOUNDS['shoot_small'] = seq(SQUARE, [
    (84, T),   # C6
    (79, T),   # G5
], vel=90)

# success_large — triumphant full-range fanfare with held finale
SOUNDS['success_large'] = seq(SQUARE, [
    (60, E), (64, E), (67, E),   # C4 E4 G4
    (72, E), (76, E), (79, E),   # C5 E5 G5
    (84, H + Q),                  # C6 — long hold
], vel=120)

# success_medium — bright short victory jingle
SOUNDS['success_medium'] = seq(SQUARE, [
    (67, E),   # G4
    (72, E),   # C5
    (76, E),   # E5
    (79, E),   # G5
    (84, Q),   # C6
], vel=110)

# success_small — quick positive ding
SOUNDS['success_small'] = seq(SQUARE, [
    (72, S),   # C5
    (76, S),   # E5
    (79, E),   # G5
], vel=100)

# ---------------------------------------------------------------------------
# Generate files
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    for name, events in SOUNDS.items():
        path = HERE / f'{name}.mid'
        path.write_bytes(make_midi(events))
        print(f'  wrote {path.name}')
    print(f'\nGenerated {len(SOUNDS)} files in {HERE}')
