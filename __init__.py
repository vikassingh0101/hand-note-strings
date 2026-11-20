"""handnotes: turn hand-tracking data into strings of music notes."""
from .engine import HandFrame, HandNoteEngine, NoteEvent
from .mapping import PitchMapper
from .note_string import NoteString, StringNote
from .triggers import PinchTrigger

__version__ = "0.1.0"
__all__ = [
    "HandFrame",
    "HandNoteEngine",
    "NoteEvent",
    "PitchMapper",
    "NoteString",
    "StringNote",
    "PinchTrigger",
]
