"""A command stamped for tick 5 is still waiting while tick 4 resolves."""

from __future__ import annotations

from wardrum.commands import CommandQueue, move
from wardrum.rng import SimRng
from wardrum.runner import step
from wardrum.state import SimState, Unit


def test_command_for_tick_5_does_not_apply_at_tick_4():
    state = SimState()
    state.add_unit(Unit("solo", 10, 10, 4, "N"))
    queue = CommandQueue()
    queue.enqueue(move(5, 1, "solo", 1, 0))
    rng = SimRng(3)

    while state.tick < 4:
        step(state, queue, rng)

    assert state.tick == 4
    assert state.units["solo"].x == 10
    assert len(queue) == 1

    step(state, queue, rng)
    assert state.tick == 5
    assert state.units["solo"].x == 10
    assert state.units["solo"].facing == "N"
    assert len(queue) == 1

    step(state, queue, rng)
    assert state.tick == 6
    assert state.units["solo"].x == 11
    assert state.units["solo"].facing == "E"
    assert len(queue) == 0
    assert rng.advances == 6
