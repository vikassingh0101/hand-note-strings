"""The "string": a rolling history of the most recent notes."""
from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from typing import Deque, Dict, Iterator, List, Optional


@dataclass
class StringNote:
    note: int
    velocity: int
    x: float  # 0..1, left -> right
    y: float  # 0..1, bottom -> top
    t: float  # seconds
    duration: Optional[float] = None  # None while still held


class NoteString:
    """Keeps the last `max_len` notes, oldest first, newest last."""

    def __init__(self, max_len: int = 32) -> None:
        if max_len < 1:
            raise ValueError("max_len must be >= 1")
        self.max_len = max_len
        self._notes: Deque[StringNote] = deque(maxlen=max_len)

    def add(self, note: StringNote) -> None:
        self._notes.append(note)

    def release(self, t: float) -> None:
        """Close the newest note (sets its duration) if it is still open."""
        if self._notes and self._notes[-1].duration is None:
            last = self._notes[-1]
            last.duration = max(0.0, t - last.t)

    def clear(self) -> None:
        self._notes.clear()

    def __len__(self) -> int:
        return len(self._notes)

    def __iter__(self) -> Iterator[StringNote]:
        return iter(self._notes)

    def columns(self, length: Optional[int] = None) -> Dict[str, List[float]]:
        """Fixed-length columns for a CHOP: tx, ty, pitch, vel, valid.

        Unused trailing samples are 0.0 with valid == 0.0.
        """
        length = length or self.max_len
        notes = list(self._notes)[-length:]
        pad = [0.0] * (length - len(notes))

        def col(attr: str) -> List[float]:
            return [float(getattr(n, attr)) for n in notes] + pad

        return {
            "tx": col("x"),
            "ty": col("y"),
            "pitch": col("note"),
            "vel": col("velocity"),
            "valid": [1.0] * len(notes) + pad,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps([asdict(n) for n in self._notes], indent=indent)
