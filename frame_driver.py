"""Execute DAT: cooks the two Script CHOPs once per frame, in order.

A Script CHOP only re-cooks when its inputs change. If the hand disappears and
the plugin's channels stop changing, a held note would never be released, so we
force a cook every frame. Turn on "Frame Start" (and "Active") on the DAT.
"""


def onFrameStart(frame):
    op("note_engine").cook(force=True)
    op("note_string").cook(force=True)
    return
