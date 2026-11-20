"""Frame-by-frame engine: hand data in, note events out."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .mapping import PitchMapper
from .note_string import NoteString, StringNote
from .scales import midi_to_freq
from .triggers import PinchTrigger


@dataclass(frozen=True)
class HandFrame:
    """One frame of tracked-hand data, already in engine space.

    x: 0 = left, 1 = right.  y: 0 = bottom, 1 = top.
    pinch_ratio: thumb-index distance divided by hand size (small = pinched).
    """

    present: bool
    x: float = 0.5
    y: float = 0.5
    pinch_ratio: Optional[float] = None
    t: float = 0.0


@dataclass(frozen=True)
class NoteEvent:
    kind: str  # "on" or "off"
    note: int
    velocity: int
    x: float
    y: float
    t: float


class HandNoteEngine:
    """Pinch to start a note; drag while pinched to glide through the scale
    (each new scale step is a new note on the string); release to stop."""

    def __init__(
        self,
        mapper: Optional[PitchMapper] = None,
        trigger: Optional[PinchTrigger] = None,
        string: Optional[NoteString] = None,
        glide: bool = True,
    ) -> None:
        self.mapper = mapper if mapper is not None else PitchMapper()
        self.trigger = trigger if trigger is not None else PinchTrigger()
        self.string = string if string is not None else NoteString()
        self.glide = glide
        self.held: Optional[int] = None
        self.velocity = 0
        self.last_note = self.mapper.notes[0]
        self.x = 0.5
        self.y = 0.5

    def update(self, frame: HandFrame) -> List[NoteEvent]:
        events: List[NoteEvent] = []
        if frame.present:
            self.x, self.y = frame.x, frame.y
        ratio = frame.pinch_ratio if frame.present else None
        edge = self.trigger.update(ratio)

        if edge == "down":
            events.append(self._note_on(self.mapper.pitch(frame.x), frame.t))
        elif edge == "up":
            events.extend(self._note_off(frame.t))
        elif self.glide and self.held is not None:
            new = self.mapper.pitch(frame.x, current=self.held)
            if new != self.held:
                events.extend(self._note_off(frame.t))
                events.append(self._note_on(new, frame.t))
        return events

    def live_state(self) -> Dict[str, float]:
        gate = 1.0 if self.held is not None else 0.0
        note = self.held if self.held is not None else self.last_note
        return {
            "gate": gate,
            "note": float(note),
            "velocity": float(self.velocity) if gate else 0.0,
            "freq": midi_to_freq(note),
            "amp": (self.velocity / 127.0) if gate else 0.0,
            "x": self.x,
            "y": self.y,
        }

    def reset(self) -> None:
        self.trigger.reset()
        self.string.clear()
        self.held = None
        self.velocity = 0

    def _note_on(self, note: int, t: float) -> NoteEvent:
        self.velocity = self.mapper.velocity(self.y)
        self.held = note
        self.last_note = note
        self.string.add(StringNote(note, self.velocity, self.x, self.y, t))
        return NoteEvent("on", note, self.velocity, self.x, self.y, t)

    def _note_off(self, t: float) -> List[NoteEvent]:
        if self.held is None:
            return []
        note = self.held
        self.string.release(t)
        self.held = None
        return [NoteEvent("off", note, 0, self.x, self.y, t)]
