# TouchDesigner setup

**Status:** the Python logic is unit-tested; this wiring has not been run
inside TouchDesigner yet. Check these first if something is off:

1. Channel names in the `hands` Null CHOP (middle-click it to see the list). The code expects
   `h1:thumb_tip:x`, `h1:index_finger_tip:y`, `h1:hand_active`, and optionally
   `h1:wrist:x/y` and `h1:middle_finger_mcp:x/y` (used for hand size).
2. Y direction. Raise your hand: if the y channel goes up, set `FLIP_Y = False` in `note_engine_callbacks.py`.
3. Camera frame size. `ASPECT` is frame height / width (720p = 0.5625).

## 1. Get the MediaPipe plugin

The plugin is [torinmb/mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner).
Download **`release.zip`** from its Releases page (not the "Source code" zip),
extract the `toxes/` folder into `touchdesigner/toxes/` (git-ignored), and check
the plugin README for the minimum TouchDesigner version.

## 2. Build the network

Save a new project as `touchdesigner/handnotes.toe` (the callbacks find `src/` relative to it).

```
MediaPipe.tox  (hands only, webcam source)
   ├─ hand landmarks CHOP ─┐
   └─ helpers CHOP ────────┴─ Merge CHOP ─ Null CHOP `hands`
                                              │
                                              ▼
                                  Script CHOP `note_engine` ─┬─ Select CHOP (ch1n*) ─ MIDI Out CHOP
                                                             └─ Select CHOP (freq amp) ─ audio / visuals
                                  Script CHOP `note_string` ───── Math CHOP ─ Geometry COMP (instancing)
                                  Execute DAT (frame_driver.py)
```

- **Script CHOP `note_engine`**: connect `hands` to its input. Create a Text DAT, set its File parameter to
  `note_engine_callbacks.py` with Sync to File on, and set the Script CHOP's Callbacks DAT to it.
- **Script CHOP `note_string`**: no input. Same steps with `note_string_callbacks.py`.
- **Execute DAT**: File = `frame_driver.py`, turn on Active and Frame Start. This force-cooks both
  Script CHOPs every frame so a held note is always released when the hand disappears.

## 3. What comes out

`note_engine` (1 sample per channel):

| Channel | Meaning |
| --- | --- |
| `gate` | 1 while a note is held |
| `note`, `velocity` | MIDI note number and velocity |
| `freq`, `amp` | Hz and 0..1 amplitude, for a quick Audio Oscillator CHOP preview |
| `x`, `y` | Hand position, 0..1 (y up) |
| `ch1n<N>` | One channel per scale note; value is velocity (0 = off). Select `ch1n*` into a MIDI Out CHOP |

`note_string` (32 samples per channel, oldest first):
`tx`, `ty` (where each note was played), `pitch`, `vel`, `valid` (0 on unused samples).

## 4. Saving your work

`.toe` and `.tox` files are binary, so git can't diff them. Commit them anyway
after meaningful changes (`.gitattributes` marks them binary; Git LFS lines are
there to uncomment). Saving the finished network as a component,
`touchdesigner/hand_notes.tox`, keeps it reusable in other projects.
