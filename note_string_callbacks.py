"""Script CHOP callbacks for the CHOP named `note_string`.

No input needed. Reads the shared engine (updated by `note_engine`) and outputs
the last N notes as N-sample channels, oldest first, newest last:

    tx, ty   position where each note was played (0..1; y up)
    pitch    MIDI note number
    vel      MIDI velocity
    valid    1 for real notes, 0 for unused padding

Use `valid` to scale padded instances to zero, and a Math CHOP to remap 0..1
to your scene's coordinate range.
"""
import os
import sys

_SRC = os.path.normpath(os.path.join(project.folder, "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from handnotes import session  # noqa: E402


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.clear()
    engine = session.get_engine()
    length = engine.string.max_len
    scriptOp.numSamples = length
    for name, vals in engine.string.columns(length).items():
        scriptOp.appendChan(name).vals = vals
    return
