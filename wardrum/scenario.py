"""Named starting fields.

Scenarios place a fixed set of units. They do not read files and they
do not carry player accounts. ``skirmish_01`` is two units on the open
map, facing each other.
"""

from __future__ import annotations

from wardrum.state import SimState, Unit

SKIRMISH_01 = "skirmish_01"


def load_scenario(name: str) -> SimState:
    """Return a fresh state for ``name``.

    ``skirmish_01`` places ranger at (18, 12) facing east and warden at
    (60, 12) facing west. Both start with 10 hit points. Each call builds
    new unit objects.
    """
    if name != SKIRMISH_01:
        raise KeyError(f"unknown scenario {name!r}; known: {SKIRMISH_01}")
    state = SimState()
    state.add_unit(Unit("ranger", 18, 12, 10, "E"))
    state.add_unit(Unit("warden", 60, 12, 10, "W"))
    return state
