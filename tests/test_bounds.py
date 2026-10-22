"""Moves that would leave the map are recorded and not applied."""

from __future__ import annotations

import pytest

from wardrum.commands import Command, move
from wardrum.state import MAP_MAX_X, MAP_MAX_Y, Unit, SimState


def _state_with(unit: Unit) -> SimState:
    state = SimState()
    state.add_unit(unit)
    return state


def test_map_corners_are_legal_and_the_next_cell_is_not():
    Unit("corner", 0, 0, 1, "E")
    Unit("far", MAP_MAX_X, MAP_MAX_Y, 1, "W")
    with pytest.raises(ValueError):
        Unit("east", MAP_MAX_X + 1, 0, 1, "E")
    with pytest.raises(ValueError):
        Unit("north", 0, -1, 1, "N")
    with pytest.raises(ValueError):
        Unit("south", 0, MAP_MAX_Y + 1, 1, "S")


def test_move_steps_one_cell_and_turns_to_face_it():
    state = _state_with(Unit("solo", 10, 10, 8, "N"))
    state.apply(move(0, 1, "solo", 1, 0))
    unit = state.units["solo"]
    assert (unit.x, unit.y, unit.facing) == (11, 10, "E")
    assert state.rejections == []
    assert unit.hp == 8


def test_move_does_not_leave_the_map():
    state = _state_with(Unit("solo", MAP_MAX_X, 20, 5, "W"))
    state.apply(move(0, 1, "solo", 1, 0))
    unit = state.units["solo"]
    assert (unit.x, unit.y, unit.facing) == (MAP_MAX_X, 20, "W")
    assert len(state.rejections) == 1
    assert state.rejections[0].reason == "out_of_bounds"
    assert state.rejections[0].unit_id == "solo"

    state.apply(move(0, 2, "solo", 0, -1))
    assert (unit.x, unit.y) == (MAP_MAX_X, 19)


def test_edges_reject_the_outward_step_only():
    north = _state_with(Unit("solo", 4, 0, 1, "S"))
    north.apply(move(0, 1, "solo", 0, -1))
    assert north.units["solo"].y == 0
    assert north.rejections[0].reason == "out_of_bounds"

    west = _state_with(Unit("solo", 0, 4, 1, "E"))
    west.apply(move(0, 1, "solo", -1, 0))
    assert west.units["solo"].x == 0
    west.apply(move(0, 2, "solo", 1, 0))
    assert west.units["solo"].x == 1


def test_diagonal_and_zero_steps_are_rejected():
    state = _state_with(Unit("solo", 3, 3, 1, "N"))
    state.apply(move(0, 1, "solo", 1, 1))
    state.apply(Command(0, 2, "move", "solo", (("dx", 0), ("dy", 0))))
    assert (state.units["solo"].x, state.units["solo"].y) == (3, 3)
    assert [item.reason for item in state.rejections] == ["illegal_step", "illegal_step"]


def test_missing_unit_is_recorded():
    state = SimState()
    state.apply(move(0, 1, "ghost", 1, 0))
    assert state.rejections[0].reason == "missing_unit"
    assert state.units == {}
