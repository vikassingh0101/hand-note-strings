import pytest

from handnotes.adapters import frame_from_channels


def channels(**over):
    base = {
        "h1:hand_active": 1.0,
        "h1:thumb_tip:x": 0.40, "h1:thumb_tip:y": 0.30,
        "h1:index_finger_tip:x": 0.40, "h1:index_finger_tip:y": 0.30,
        "h1:wrist:x": 0.40, "h1:wrist:y": 0.60,
        "h1:middle_finger_mcp:x": 0.40, "h1:middle_finger_mcp:y": 0.40,
    }
    base.update(over)
    return base


def test_pinched_hand():
    f = frame_from_channels(channels(), t=1.5)
    assert f.present and f.t == 1.5
    assert f.pinch_ratio == pytest.approx(0.0)
    assert f.x == pytest.approx(0.40)
    assert f.y == pytest.approx(0.70)  # flipped: image-y 0.30 -> engine-y 0.70


def test_open_hand_ratio_scales_with_hand_size():
    # Thumb-index gap equals the wrist->knuckle length, so ratio == 1.0
    # (both measured with the same aspect correction).
    v = channels(**{"h1:index_finger_tip:y": 0.50})
    f = frame_from_channels(v)
    assert f.pinch_ratio == pytest.approx(0.2 / 0.2)


def test_missing_hand_size_uses_default():
    v = channels(**{"h1:index_finger_tip:x": 0.46})
    for k in ("h1:wrist:x", "h1:wrist:y", "h1:middle_finger_mcp:x", "h1:middle_finger_mcp:y"):
        v.pop(k)
    f = frame_from_channels(v, default_hand_size=0.12)
    assert f.pinch_ratio == pytest.approx(0.06 / 0.12)


def test_flip_and_mirror_options():
    f = frame_from_channels(channels(), flip_y=False, mirror_x=True)
    assert f.x == pytest.approx(0.60)
    assert f.y == pytest.approx(0.30)


def test_not_present():
    assert not frame_from_channels(channels(**{"h1:hand_active": 0.0})).present
    assert not frame_from_channels({}).present
    assert not frame_from_channels({"h1:thumb_tip:x": 0.1}).present


def test_second_hand():
    v = {k.replace("h1:", "h2:"): val for k, val in channels().items()}
    assert frame_from_channels(v, hand="h2").present
    assert not frame_from_channels(v, hand="h1").present
