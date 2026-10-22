"""Same seed and the same command list always hash alike."""

from __future__ import annotations

from wardrum.commands import CommandQueue, move
from wardrum.rng import SimRng
from wardrum.runner import run
from wardrum.state import SimState, Unit


def _hash(seed: int, commands: list, ticks: int) -> str:
    state = SimState()
    state.add_unit(Unit("solo", 0, 10, 5, "E"))
    queue = CommandQueue()
    for command in commands:
        queue.enqueue(command)
    return run(state, queue, SimRng(seed), ticks)


def test_same_seed_and_command_list_match():
    commands = [move(0, 1, "solo", 1, 0), move(1, 1, "solo", 0, 1)]
    assert _hash(42, commands, 4) == _hash(42, commands, 4)


def test_different_seed_changes_the_hash():
    commands = [move(0, 1, "solo", 1, 0)]
    assert _hash(1, commands, 4) != _hash(2, commands, 4)


def test_different_command_order_changes_the_hash():
    west_then_east = [move(0, 1, "solo", -1, 0), move(0, 2, "solo", 1, 0)]
    east_then_west = [move(0, 1, "solo", 1, 0), move(0, 2, "solo", -1, 0)]
    west_hash = _hash(42, west_then_east, 1)
    east_hash = _hash(42, east_then_west, 1)
    assert west_hash != east_hash
    assert west_hash == "271a08cd2232c3ff5866090192aef71d374a2c17d81d3a28b197634dd8022e82"
    assert east_hash == "fe8234b8914304194bf4592795250de9fb4c94d1ae40d4479d2367b08c9fe86e"


def test_seq_not_enqueue_order_decides_application():
    south_first = [move(0, 2, "solo", 1, 0), move(0, 1, "solo", 0, 1)]
    east_queued_first = [move(0, 1, "solo", 0, 1), move(0, 2, "solo", 1, 0)]
    assert _hash(42, south_first, 1) == _hash(42, east_queued_first, 1)
