"""Integer time scales consume a fixed tick count and never sleep."""

from __future__ import annotations

import inspect

import pytest

import wardrum.clock as clock_mod
from wardrum.clock import TICK_MS, TickClock


def test_tick_size_stays_fifty_milliseconds():
    assert TICK_MS == 50


def test_one_x_consumes_one_tick():
    clock = TickClock(1)
    assert clock.ticks_for_frame() == 1
    assert clock.ticks_for_frame(frame_budget_ms=50) == 1


def test_two_x_consumes_two_ticks():
    assert TickClock(2).ticks_for_frame() == 2


def test_four_x_consumes_four_ticks_per_frame():
    clock = TickClock(4)
    assert clock.ticks_for_frame() == 4
    assert clock.ticks_for_frame() == 4


def test_eight_x_consumes_eight_ticks():
    assert TickClock(8).ticks_for_frame() == 8


def test_paused_scale_consumes_zero_ticks():
    clock = TickClock(0)
    assert clock.scale == 0
    assert [clock.ticks_for_frame() for _ in range(8)] == [0] * 8


def test_changing_scale_does_not_change_tick_size():
    clock = TickClock(1)
    clock.set_scale(8)
    assert clock.ticks_for_frame() == 8
    clock.set_scale(0)
    assert clock.ticks_for_frame() == 0
    assert TICK_MS == 50


def test_unknown_scale_is_rejected():
    with pytest.raises(ValueError):
        TickClock(3)
    clock = TickClock(1)
    with pytest.raises(ValueError):
        clock.set_scale(16)


def test_negative_frame_budget_is_rejected():
    with pytest.raises(ValueError):
        TickClock(1).ticks_for_frame(frame_budget_ms=-1)


def test_clock_does_not_sleep():
    source = inspect.getsource(clock_mod)
    assert "time.sleep" not in source
    assert "import time" not in source
