"""Pause consumes no ticks, and 4x consumes four ticks of the sim."""

from __future__ import annotations

from wardrum.clock import TickClock
from wardrum.commands import CommandQueue, move
from wardrum.rng import SimRng
from wardrum.runner import step
from wardrum.state import SimState, Unit


def _drive(clock: TickClock, frames: int, state: SimState, queue: CommandQueue, rng: SimRng) -> int:
    consumed = 0
    for _ in range(frames):
        ticks = clock.ticks_for_frame()
        consumed += ticks
        for _ in range(ticks):
            step(state, queue, rng)
    return consumed


def test_paused_scale_consumes_zero_ticks():
    clock = TickClock(0)
    state = SimState()
    state.add_unit(Unit("solo", 3, 3, 1, "N"))
    queue = CommandQueue()
    queue.enqueue(move(0, 1, "solo", 1, 0))
    rng = SimRng(7)

    consumed = _drive(clock, 12, state, queue, rng)

    assert consumed == 0
    assert state.tick == 0
    assert rng.advances == 0
    assert state.units["solo"].x == 3
    assert len(queue) == 1


def test_leaving_pause_resolves_the_tick_that_was_waiting():
    clock = TickClock(0)
    state = SimState()
    state.add_unit(Unit("solo", 3, 3, 1, "N"))
    queue = CommandQueue()
    queue.enqueue(move(0, 1, "solo", 1, 0))
    rng = SimRng(7)
    _drive(clock, 4, state, queue, rng)

    clock.set_scale(1)
    assert clock.ticks_for_frame() == 1
    step(state, queue, rng)

    assert state.tick == 1
    assert state.units["solo"].x == 4
    assert len(queue) == 0


def test_four_x_consumes_four_ticks_per_frame():
    clock = TickClock(4)
    state = SimState()
    queue = CommandQueue()
    rng = SimRng(7)

    first = clock.ticks_for_frame()
    second = clock.ticks_for_frame(frame_budget_ms=50)
    assert first == 4
    assert second == 4

    for _ in range(first):
        step(state, queue, rng)

    assert state.tick == 4
    assert rng.advances == 4
