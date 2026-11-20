"""Scales and MIDI helpers. Pure stdlib so it runs inside TouchDesigner's Python."""
from __future__ import annotations

from typing import List

# Semitone offsets from the root.
SCALES = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "blues": (0, 3, 5, 6, 7, 10),
    "chromatic": tuple(range(12)),
}

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def scale_notes(root: int, scale: str, low: int, high: int) -> List[int]:
    """Every MIDI note in `scale` (rooted on the pitch class of `root`) within [low, high]."""
    try:
        intervals = SCALES[scale]
    except KeyError:
        raise ValueError("unknown scale %r; choose from %s" % (scale, sorted(SCALES))) from None
    if low > high:
        raise ValueError("low (%d) must be <= high (%d)" % (low, high))
    pitch_classes = {(root % 12 + i) % 12 for i in intervals}
    return [n for n in range(low, high + 1) if n % 12 in pitch_classes]


def midi_to_freq(note: float) -> float:
    """MIDI note number -> frequency in Hz (A4 = 69 = 440 Hz)."""
    return 440.0 * 2.0 ** ((note - 69) / 12.0)


def note_name(note: int) -> str:
    """60 -> 'C4'."""
    return "%s%d" % (NOTE_NAMES[note % 12], note // 12 - 1)
