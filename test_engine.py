import json

from handnotes import HandFrame, HandNoteEngine, NoteString, PitchMapper, PinchTrigger, session


def make_engine(**kw):
    # chromatic 60..64 => five 0.2-wide zones
    return HandNoteEngine(mapper=PitchMapper(root=60, scale="chromatic", low=60, high=64), **kw)


def pinch(x, y=0.5, t=0.0):
    return HandFrame(True, x, y, 0.1, t)


def open_hand(x=0.5, y=0.5, t=0.0):
    return HandFrame(True, x, y, 0.9, t)


def test_pinch_plays_and_release_stops():
    e = make_engine()
    assert e.update(open_hand(0.1, t=0.0)) == []
    on = e.update(pinch(0.1, 1.0, t=0.1))
    assert [(ev.kind, ev.note, ev.velocity) for ev in on] == [("on", 60, 127)]
    assert e.live_state()["gate"] == 1.0
    assert e.update(pinch(0.1, 1.0, t=0.2)) == []  # holding: nothing new
    off = e.update(open_hand(0.1, t=0.5))
    assert [(ev.kind, ev.note) for ev in off] == [("off", 60)]
    assert e.live_state()["gate"] == 0.0
    assert len(e.string) == 1
    assert list(e.string)[0].duration == 0.4


def test_dragging_glides_through_notes():
    e = make_engine()
    events = []
    events += e.update(pinch(0.1, t=0.0))
    events += e.update(pinch(0.3, t=0.1))
    events += e.update(pinch(0.5, t=0.2))
    events += e.update(open_hand(0.5, t=0.3))
    assert [(ev.kind, ev.note) for ev in events] == [
        ("on", 60), ("off", 60), ("on", 61), ("off", 61), ("on", 62),
        ("off", 62),
    ]
    assert [n.note for n in e.string] == [60, 61, 62]


def test_no_glide_option():
    e = make_engine(glide=False)
    e.update(pinch(0.1))
    assert e.update(pinch(0.9, t=0.1)) == []
    assert e.held == 60


def test_hand_lost_stops_note():
    e = make_engine()
    e.update(pinch(0.1))
    off = e.update(HandFrame(present=False, t=1.0))
    assert [(ev.kind, ev.note) for ev in off] == [("off", 60)]
    assert e.held is None


def test_string_keeps_only_latest_notes():
    e = make_engine(string=NoteString(max_len=3))
    for i in range(5):
        e.update(pinch(0.1, t=i * 2.0))
        e.update(open_hand(0.1, t=i * 2.0 + 1.0))
    assert len(e.string) == 3


def test_live_state_when_idle_and_after_release():
    e = make_engine()
    s = e.live_state()
    assert s["gate"] == 0.0 and s["amp"] == 0.0 and s["velocity"] == 0.0
    e.update(pinch(0.9))
    e.update(open_hand(0.9, t=1.0))
    s = e.live_state()
    assert s["note"] == 64.0  # remembers the last pitch for envelope tails
    assert s["gate"] == 0.0


def test_string_columns_and_json():
    e = make_engine()
    e.update(pinch(0.1, 0.25, t=0.0))
    e.update(open_hand(0.1, t=0.5))
    cols = e.string.columns(4)
    assert cols["valid"] == [1.0, 0.0, 0.0, 0.0]
    assert cols["pitch"] == [60.0, 0.0, 0.0, 0.0]
    assert all(len(v) == 4 for v in cols.values())
    data = json.loads(e.string.to_json())
    assert data[0]["note"] == 60 and data[0]["duration"] == 0.5


def test_session_configure_and_reset():
    session.reset()
    e1 = session.get_engine()
    assert session.get_engine() is e1
    e2 = session.configure(scale="major", low=60, high=72, max_notes=8)
    assert e2 is not e1 and session.get_engine() is e2
    assert e2.string.max_len == 8
    session.reset()
    assert session.get_engine() is not e2
