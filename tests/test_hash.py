"""The lockstep digest is SHA-256 of canonical JSON, units ordered by id."""

from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from wardrum.hashing import state_hash


def _unit(unit_id: str, x: int = 0, y: int = 0, hp: int = 1, facing: str = "N"):
    return SimpleNamespace(id=unit_id, x=x, y=y, hp=hp, facing=facing)


def _canonical(tick: int, units: list[dict[str, object]], rng_counter: int) -> str:
    payload = {"rng_counter": rng_counter, "tick": tick, "units": units}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def test_hash_is_sha256_of_canonical_json():
    digest = state_hash(4, [_unit("alpha", 3, 8, 9, "E")], 99)
    expected = _canonical(
        4,
        [{"facing": "E", "hp": 9, "id": "alpha", "x": 3, "y": 8}],
        99,
    )
    assert digest == expected
    assert len(digest) == 64
    int(digest, 16)


def test_units_are_ordered_by_id():
    north = _unit("north", 1, 2, 3, "S")
    south = _unit("south", 4, 5, 6, "N")
    assert state_hash(0, [south, north], 1) == state_hash(0, [north, south], 1)


def test_tick_and_rng_counter_change_the_hash():
    units = [_unit("solo")]
    base = state_hash(0, units, 1)
    assert state_hash(1, units, 1) != base
    assert state_hash(0, units, 2) != base


def test_duplicate_unit_id_is_rejected():
    with pytest.raises(ValueError):
        state_hash(0, [_unit("solo", 0, 0), _unit("solo", 1, 1)], 0)
