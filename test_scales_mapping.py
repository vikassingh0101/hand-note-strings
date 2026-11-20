import pytest

from handnotes.mapping import PitchMapper
from handnotes.scales import midi_to_freq, note_name, scale_notes


def test_scale_notes_minor_pentatonic_c():
    assert scale_notes(60, "minor_pentatonic", 60, 72) == [60, 63, 65, 67, 70, 72]


def test_scale_notes_root_is_pitch_class():
    # Root 72 (C5) gives the same pitch classes as root 60.
    assert scale_notes(72, "major", 60, 71) == [60, 62, 64, 65, 67, 69, 71]


def test_unknown_scale_and_bad_range():
    with pytest.raises(ValueError):
        scale_notes(60, "nope", 48, 84)
    with pytest.raises(ValueError):
        scale_notes(60, "major", 80, 40)


def test_midi_to_freq_and_names():
    assert midi_to_freq(69) == pytest.approx(440.0)
    assert midi_to_freq(60) == pytest.approx(261.6256, rel=1e-5)
    assert note_name(60) == "C4"
    assert note_name(69) == "A4"
    assert note_name(61) == "C#4"


def test_pitch_zones_and_clamping():
    m = PitchMapper(root=60, scale="chromatic", low=60, high=64)  # 5 notes, 0.2 wide
    assert m.pitch(0.0) == 60
    assert m.pitch(0.19) == 60
    assert m.pitch(0.21) == 61
    assert m.pitch(0.99) == 64
    assert m.pitch(1.0) == 64
    assert m.pitch(-3) == 60
    assert m.pitch(7) == 64


def test_pitch_hysteresis_is_sticky_near_edges():
    m = PitchMapper(root=60, scale="chromatic", low=60, high=64, hysteresis=0.25)
    # Note 61 owns [0.2, 0.4]; stickiness extends it to [0.15, 0.45].
    assert m.pitch(0.44, current=61) == 61
    assert m.pitch(0.16, current=61) == 61
    assert m.pitch(0.46, current=61) == 62
    assert m.pitch(0.14, current=61) == 60
    # Without a current note there's no stickiness.
    assert m.pitch(0.44) == 62


def test_velocity_range():
    m = PitchMapper(vel_min=40, vel_max=127)
    assert m.velocity(0.0) == 40
    assert m.velocity(1.0) == 127
    assert m.velocity(5.0) == 127
    assert 40 < m.velocity(0.5) < 127


def test_empty_range_raises():
    with pytest.raises(ValueError):
        PitchMapper(root=60, scale="major", low=61, high=61)  # 61 is C#, not in C major
