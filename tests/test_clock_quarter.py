"""Quarter-speed play emits one tick on every fourth 50 ms frame."""

from __future__ import annotations

import pytest

from wardrum.clock import TickClock


def test_quarter_speed_emits_one_tick_every_fourth_frame():
    clock = TickClock(0.25)
    assert clock.scale == 0.25
    emitted = [clock.ticks_for_frame() for _ in range(8)]
    assert emitted == [0, 0, 0, 1, 0, 0, 0, 1]


def test_quarter_speed_residue_lands_on_the_fourth_frame():
    clock = TickClock(0.25)
    assert clock.ticks_for_frame() == 0
    assert clock.residue == 50
    assert clock.ticks_for_frame() == 0
    assert clock.residue == 100
    assert clock.ticks_for_frame() == 0
    assert clock.residue == 150
    assert clock.ticks_for_frame() == 1
    assert clock.residue == 0


def test_pause_preserves_quarter_speed_residue():
    clock = TickClock(0.25)
    for _ in range(3):
        assert clock.ticks_for_frame() == 0
    assert clock.residue == 150
    clock.set_scale(0)
    assert clock.ticks_for_frame() == 0
    assert clock.residue == 150
    clock.set_scale(0.25)
    assert clock.ticks_for_frame() == 1
    assert clock.residue == 0


def test_integer_scales_still_divide_a_fifty_ms_frame_evenly():
    assert TickClock(1).ticks_for_frame() == 1
    assert TickClock(2).ticks_for_frame() == 2
    assert TickClock(4).ticks_for_frame() == 4
    assert TickClock(8).ticks_for_frame() == 8
    assert TickClock(0).ticks_for_frame() == 0


def test_half_speed_is_not_a_legal_scale():
    with pytest.raises(ValueError):
        TickClock(0.5)


def test_longer_frame_at_quarter_speed_still_uses_the_accumulator():
    clock = TickClock(0.25)
    assert clock.ticks_for_frame(frame_budget_ms=100) == 0
    assert clock.residue == 100
    assert clock.ticks_for_frame(frame_budget_ms=100) == 1
    assert clock.residue == 0
