"""Canonical SHA-256 of a lockstep state.

``state_hash`` hashes the tick, the rng counter word, and every unit.
Units are ordered by id before encoding. JSON objects use sorted keys
and no insignificant whitespace, so two machines build the same digest
from the same state.
"""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, Protocol


class _UnitView(Protocol):
    id: str
    x: int
    y: int
    hp: int
    facing: str


def _require_int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    return value


def state_hash(tick: int, units: Iterable[_UnitView], rng_counter: int) -> str:
    """Return the hex SHA-256 of the canonical state document."""
    tick_value = _require_int("tick", tick)
    counter_value = _require_int("rng_counter", rng_counter)
    if tick_value < 0:
        raise ValueError("tick must be >= 0")
    if counter_value < 0:
        raise ValueError("rng_counter must be >= 0")

    ordered = sorted(units, key=lambda unit: unit.id)
    seen: set[str] = set()
    encoded_units: list[dict[str, object]] = []
    for unit in ordered:
        if not isinstance(unit.id, str) or not unit.id:
            raise TypeError("unit id must be a non-empty str")
        if unit.id in seen:
            raise ValueError(f"duplicate unit id {unit.id}")
        seen.add(unit.id)
        if not isinstance(unit.facing, str) or not unit.facing:
            raise TypeError("facing must be a non-empty str")
        encoded_units.append(
            {
                "facing": unit.facing,
                "hp": _require_int("hp", unit.hp),
                "id": unit.id,
                "x": _require_int("x", unit.x),
                "y": _require_int("y", unit.y),
            }
        )

    payload = {
        "rng_counter": counter_value,
        "tick": tick_value,
        "units": encoded_units,
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
