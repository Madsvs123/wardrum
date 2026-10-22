"""Units on a fixed map, and the moves the map will accept.

The field is 80 by 40 cells: x runs from 0 through 79, y from 0 through
39. North decreases y. A move is one orthogonal step. A step that would
leave the map is rejected and recorded. The unit stays where it was.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from wardrum.commands import Command

MAP_MIN_X = 0
MAP_MAX_X = 79
MAP_MIN_Y = 0
MAP_MAX_Y = 39

_FACING_OF_STEP = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}
ALLOWED_FACING = frozenset(_FACING_OF_STEP.values())


def in_bounds(x: int, y: int) -> bool:
    return MAP_MIN_X <= x <= MAP_MAX_X and MAP_MIN_Y <= y <= MAP_MAX_Y


def _require_int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    return value


@dataclass
class Unit:
    """One body on the map. The state mutates x, y, and facing in place."""

    id: str
    x: int
    y: int
    hp: int
    facing: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("id must be a non-empty str")
        self.x = _require_int("x", self.x)
        self.y = _require_int("y", self.y)
        self.hp = _require_int("hp", self.hp)
        if self.hp < 0:
            raise ValueError("hp must be >= 0")
        if self.facing not in ALLOWED_FACING:
            raise ValueError("facing must be N, E, S, or W")
        if not in_bounds(self.x, self.y):
            raise ValueError(
                f"position {(self.x, self.y)} is outside 0..{MAP_MAX_X} by 0..{MAP_MAX_Y}"
            )


@dataclass(frozen=True)
class Rejection:
    """A command the tick boundary refused to apply."""

    tick: int
    seq: int
    unit_id: str
    reason: str


@dataclass
class SimState:
    """Mutable lockstep state. Commands are applied by ``apply``."""

    tick: int = 0
    rng_counter: int = 0
    units: dict[str, Unit] = field(default_factory=dict)
    rejections: list[Rejection] = field(default_factory=list)

    def add_unit(self, unit: Unit) -> None:
        if not isinstance(unit, Unit):
            raise TypeError("unit must be a Unit")
        if unit.id in self.units:
            raise ValueError(f"duplicate unit id {unit.id}")
        self.units[unit.id] = unit

    def units_in_id_order(self) -> list[Unit]:
        return [self.units[key] for key in sorted(self.units)]

    def apply(self, command: Command) -> None:
        """Apply one command, or record why it was refused.

        A refused move does not change the unit. Call this only at a tick
        boundary; the runner is what keeps that rule.
        """
        if not isinstance(command, Command):
            raise TypeError("command must be a Command")
        if command.kind != "move":
            self._reject(command, "unknown_kind")
            return
        unit = self.units.get(command.unit_id)
        if unit is None:
            self._reject(command, "missing_unit")
            return
        payload = command.payload_map()
        if "dx" not in payload or "dy" not in payload:
            self._reject(command, "bad_payload")
            return
        step = (payload["dx"], payload["dy"])
        if step not in _FACING_OF_STEP:
            self._reject(command, "illegal_step")
            return
        next_x = unit.x + step[0]
        next_y = unit.y + step[1]
        if not in_bounds(next_x, next_y):
            self._reject(command, "out_of_bounds")
            return
        unit.x = next_x
        unit.y = next_y
        unit.facing = _FACING_OF_STEP[step]

    def _reject(self, command: Command, reason: str) -> None:
        self.rejections.append(
            Rejection(
                tick=self.tick,
                seq=command.seq,
                unit_id=command.unit_id,
                reason=reason,
            )
        )
