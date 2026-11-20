import pytest

from handnotes.triggers import PinchTrigger


def test_down_and_up_with_hysteresis():
    p = PinchTrigger(on_below=0.3, off_above=0.5)
    assert p.update(0.8) is None
    assert p.update(0.29) == "down"
    assert p.update(0.35) is None  # between thresholds: stays down
    assert p.update(0.49) is None
    assert p.update(0.51) == "up"
    assert p.update(0.4) is None  # between thresholds: stays up


def test_no_repeat_edges():
    p = PinchTrigger()
    assert p.update(0.1) == "down"
    assert p.update(0.1) is None
    assert p.update(0.9) == "up"
    assert p.update(0.9) is None


def test_hand_lost_releases():
    p = PinchTrigger()
    assert p.update(None) is None
    p.update(0.1)
    assert p.update(None) == "up"
    assert p.update(None) is None


def test_invalid_thresholds():
    with pytest.raises(ValueError):
        PinchTrigger(on_below=0.5, off_above=0.5)
