"""The runner applies due commands, then advances the substream, once per tick."""

from __future__ import annotations

from wardrum.commands import CommandQueue, move
from wardrum.hashing import state_hash
from wardrum.rng import SimRng
from wardrum.runner import run
from wardrum.state import SimState, Unit


def test_run_applies_only_ticks_it_resolves():
    state = SimState()
    state.add_unit(Unit("solo", 5, 5, 3, "N"))
    queue = CommandQueue()
    queue.enqueue(move(0, 1, "solo", 1, 0))
    queue.enqueue(move(2, 1, "solo", 0, 1))
    rng = SimRng(9)

    digest = run(state, queue, rng, 2)

    assert state.tick == 2
    assert rng.advances == 2
    assert (state.units["solo"].x, state.units["solo"].y) == (6, 5)
    assert len(queue) == 1
    assert digest == state_hash(2, state.units_in_id_order(), state.rng_counter)


def test_zero_ticks_hashes_the_seed_word_without_moving():
    left = SimState()
    right = SimState()
    left_hash = run(left, CommandQueue(), SimRng(1), 0)
    right_hash = run(right, CommandQueue(), SimRng(2), 0)
    assert left.tick == 0
    assert right.tick == 0
    assert left_hash != right_hash
