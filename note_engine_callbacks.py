"""Script CHOP callbacks for the CHOP named `note_engine`.

Input 0 : a Null CHOP (`hands`) holding the MediaPipe plugin's hand channels
          (landmarks + helpers), e.g. h1:thumb_tip:x, h1:hand_active ...
Outputs : 1-sample channels
            gate, note, velocity, freq, amp, x, y
          plus one channel per scale note named like ch1n60 (value = velocity,
          0 = off) which a Select CHOP (ch1n*) can feed into a MIDI Out CHOP.

Keep this file in git and point the callbacks DAT's File parameter at it
(with Sync to File on), so edits in your editor show up live in TouchDesigner.
"""
import os
import sys

# touchdesigner/handnotes.toe lives one level below the repo root.
_SRC = os.path.normpath(os.path.join(project.folder, "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from handnotes import session  # noqa: E402
from handnotes.adapters import frame_from_channels  # noqa: E402

# ---- tweak me -------------------------------------------------------------
HAND = "h1"            # "h1" or "h2" (first / second detected hand)
ASPECT = 9.0 / 16.0    # camera frame height / width (720p -> 0.5625)
FLIP_Y = True          # set False if raising your hand makes y go UP in the CHOP
MIRROR_X = False       # set True if left/right feel reversed
MIDI_CHANNEL = 1

# Uncomment to change scale / range / pinch thresholds (rebuilds the engine
# every time this DAT is re-run, which also clears the note string):
# session.configure(root=60, scale="minor_pentatonic", low=48, high=84,
#                   pinch_on=0.30, pinch_off=0.50, glide=True, max_notes=32)
# ---------------------------------------------------------------------------


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.clear()
    scriptOp.numSamples = 1

    values = {}
    if scriptOp.inputs:
        values = {c.name: c.eval() for c in scriptOp.inputs[0].chans()}

    frame = frame_from_channels(
        values,
        hand=HAND,
        aspect=ASPECT,
        flip_y=FLIP_Y,
        mirror_x=MIRROR_X,
        t=absTime.seconds,
    )

    engine = session.get_engine()
    engine.update(frame)
    state = engine.live_state()

    for name in ("gate", "note", "velocity", "freq", "amp", "x", "y"):
        scriptOp.appendChan(name).vals = [state[name]]

    for n in engine.mapper.notes:
        held = state["gate"] > 0 and n == int(state["note"])
        scriptOp.appendChan("ch%dn%d" % (MIDI_CHANNEL, n)).vals = [state["velocity"] if held else 0]
    return
