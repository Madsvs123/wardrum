"""Headless lockstep runner.

Each resolved tick, in order:

1. Release commands stamped for the current tick and apply them in seq order.
2. Advance the sim substream once and store that word as ``rng_counter``.
3. Increment the tick by one.

Commands are applied only at that boundary. The runner never sleeps.
``run`` returns the canonical state hash after the requested number of
boundaries. ``--debug`` may trace each boundary; the trace is not an
input to the hash.
"""

from __future__ import annotations

from collections.abc import Callable

from wardrum.commands import CommandQueue
from wardrum.hashing import state_hash
from wardrum.rng import SimRng
from wardrum.state import SimState


def step(state: SimState, queue: CommandQueue, rng: SimRng) -> None:
    """Resolve the boundary for ``state.tick`` and then advance time."""
    if not isinstance(state, SimState):
        raise TypeError("state must be a SimState")
    if not isinstance(queue, CommandQueue):
        raise TypeError("queue must be a CommandQueue")
    if not isinstance(rng, SimRng):
        raise TypeError("rng must be a SimRng")
    for command in queue.pop_due(state.tick):
        state.apply(command)
    state.rng_counter = rng.advance()
    state.tick += 1


def run(
    state: SimState,
    queue: CommandQueue,
    rng: SimRng,
    ticks: int,
    *,
    debug: bool = False,
    debug_sink: Callable[[str], None] | None = None,
) -> str:
    """Resolve ``ticks`` boundaries and return the state hash.

    When ``debug`` is set, each resolved tick is described to
    ``debug_sink``. The sink cannot change the hash.
    """
    if isinstance(ticks, bool) or not isinstance(ticks, int):
        raise TypeError("ticks must be an int")
    if ticks < 0:
        raise ValueError("ticks must be >= 0")
    if not isinstance(debug, bool):
        raise TypeError("debug must be a bool")
    for _ in range(ticks):
        step(state, queue, rng)
        if debug and debug_sink is not None:
            debug_sink(f"tick={state.tick} rng_counter={state.rng_counter}")
    if ticks == 0:
        state.rng_counter = rng.counter
    return state_hash(state.tick, state.units_in_id_order(), state.rng_counter)
