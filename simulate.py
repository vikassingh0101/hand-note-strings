#!/usr/bin/env python3
"""Run the engine on a synthetic hand so you can hear/see the logic without TouchDesigner.

A virtual hand sweeps left to right while pinching twice; the first pinch is
held long enough to glide across several notes. Prints the note events.

    python tools/simulate.py
    python tools/simulate.py --scale major --low 60 --high 72
    python tools/simulate.py --json            # dump the resulting note string
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from handnotes import HandFrame, HandNoteEngine, NoteString, PinchTrigger, PitchMapper  # noqa: E402
from handnotes.scales import SCALES, note_name  # noqa: E402


def frames(fps=60, seconds=5.0):
    for i in range(int(fps * seconds)):
        t = i / fps
        x = 0.1 + 0.8 * (t / seconds)
        y = 0.55 + 0.35 * math.sin(t * 2.0)
        pinching = 0.5 <= t < 2.5 or 3.0 <= t < 3.8
        yield HandFrame(present=t < 4.5, x=x, y=y, pinch_ratio=0.15 if pinching else 0.8, t=t)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", default="minor_pentatonic", choices=sorted(SCALES))
    ap.add_argument("--root", type=int, default=60)
    ap.add_argument("--low", type=int, default=48)
    ap.add_argument("--high", type=int, default=84)
    ap.add_argument("--no-glide", action="store_true")
    ap.add_argument("--json", action="store_true", help="print the final note string as JSON")
    args = ap.parse_args()

    engine = HandNoteEngine(
        mapper=PitchMapper(root=args.root, scale=args.scale, low=args.low, high=args.high),
        trigger=PinchTrigger(),
        string=NoteString(32),
        glide=not args.no_glide,
    )
    for frame in frames():
        for ev in engine.update(frame):
            print("%6.2fs  %-3s %-4s vel=%3d  x=%.2f y=%.2f" % (ev.t, ev.kind, note_name(ev.note), ev.velocity, ev.x, ev.y))
    if args.json:
        print(engine.string.to_json(indent=2))


if __name__ == "__main__":
    main()
