"""Map hand position to pitch and velocity."""
from __future__ import annotations

from typing import Dict, Optional

from .scales import scale_notes


def _clamp01(v: float) -> float:
    return min(max(v, 0.0), 1.0)


class PitchMapper:
    """Quantises horizontal position (0 = left, 1 = right) onto a scale.

    `hysteresis` (fraction of one note-width) makes the current note "sticky"
    near zone boundaries, so a hand hovering on an edge doesn't stutter.
    Vertical position (0 = bottom, 1 = top) maps to MIDI velocity.
    """

    def __init__(
        self,
        root: int = 60,
        scale: str = "minor_pentatonic",
        low: int = 48,
        high: int = 84,
        hysteresis: float = 0.25,
        vel_min: int = 40,
        vel_max: int = 127,
    ) -> None:
        self.notes = scale_notes(root, scale, low, high)
        if not self.notes:
            raise ValueError("no notes in range %d-%d for scale %r" % (low, high, scale))
        self._index: Dict[int, int] = {n: i for i, n in enumerate(self.notes)}
        self.hysteresis = hysteresis
        self.vel_min = vel_min
        self.vel_max = vel_max

    def pitch(self, x: float, current: Optional[int] = None) -> int:
        n = len(self.notes)
        x = _clamp01(x)
        idx = min(int(x * n), n - 1)
        if current is not None and current in self._index:
            c = self._index[current]
            lo = (c - self.hysteresis) / n
            hi = (c + 1 + self.hysteresis) / n
            if lo <= x <= hi:
                idx = c
        return self.notes[idx]

    def velocity(self, y: float) -> int:
        return int(round(self.vel_min + (self.vel_max - self.vel_min) * _clamp01(y)))
