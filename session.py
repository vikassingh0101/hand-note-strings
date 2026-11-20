"""A process-wide engine, so several TouchDesigner Script CHOPs can share one.

TouchDesigner keeps imported modules alive between cooks, so state stored here
survives from frame to frame.
"""
from __future__ import annotations

from typing import Optional

from .engine import HandNoteEngine
from .mapping import PitchMapper
from .note_string import NoteString
from .triggers import PinchTrigger

_engine: Optional[HandNoteEngine] = None


def configure(
    *,
    root: int = 60,
    scale: str = "minor_pentatonic",
    low: int = 48,
    high: int = 84,
    hysteresis: float = 0.25,
    pinch_on: float = 0.30,
    pinch_off: float = 0.50,
    glide: bool = True,
    max_notes: int = 32,
) -> HandNoteEngine:
    """Replace the shared engine with a freshly configured one."""
    global _engine
    _engine = HandNoteEngine(
        mapper=PitchMapper(root=root, scale=scale, low=low, high=high, hysteresis=hysteresis),
        trigger=PinchTrigger(on_below=pinch_on, off_above=pinch_off),
        string=NoteString(max_len=max_notes),
        glide=glide,
    )
    return _engine


def get_engine() -> HandNoteEngine:
    global _engine
    if _engine is None:
        configure()
    return _engine  # type: ignore[return-value]


def reset() -> None:
    """Forget the engine; the next get_engine() builds a default one."""
    global _engine
    _engine = None
