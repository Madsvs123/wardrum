"""Lockstep commands.

A command carries the tick it belongs to and a seq that orders it among
the other commands of that tick. The queue releases commands only when
the simulation resolves that exact tick, and it releases them in seq
order. A stamp for a future tick waits. This module does not apply
commands; the runner does that at the tick boundary, never mid-tick.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """One ordered intention, applied only on its stamped tick boundary."""

    tick: int
    seq: int
    kind: str
    unit_id: str
    payload: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise TypeError("tick must be an int")
        if isinstance(self.seq, bool) or not isinstance(self.seq, int):
            raise TypeError("seq must be an int")
        if self.tick < 0:
            raise ValueError("tick must be >= 0")
        if self.seq < 0:
            raise ValueError("seq must be >= 0")
        if not isinstance(self.kind, str) or not self.kind:
            raise ValueError("kind must be a non-empty string")
        if not isinstance(self.unit_id, str) or not self.unit_id:
            raise ValueError("unit_id must be a non-empty string")
        if not isinstance(self.payload, tuple):
            raise TypeError("payload must be a tuple of pairs")
        for item in self.payload:
            if (
                not isinstance(item, tuple)
                or len(item) != 2
                or not isinstance(item[0], str)
                or isinstance(item[1], bool)
                or not isinstance(item[1], int)
            ):
                raise TypeError("payload pairs must be (str, int)")

    def payload_map(self) -> dict[str, int]:
        return {key: value for key, value in self.payload}


def move(tick: int, seq: int, unit_id: str, dx: int, dy: int) -> Command:
    """Build a one-step move. Legality is decided when the tick resolves."""
    if isinstance(dx, bool) or not isinstance(dx, int):
        raise TypeError("dx must be an int")
    if isinstance(dy, bool) or not isinstance(dy, int):
        raise TypeError("dy must be an int")
    return Command(
        tick=tick,
        seq=seq,
        kind="move",
        unit_id=unit_id,
        payload=(("dx", dx), ("dy", dy)),
    )


class CommandQueue:
    """Hold commands until the tick they are stamped for is resolved.

    ``pop_due(tick)`` returns commands with that exact tick, sorted by
    ascending seq. Insertion order breaks ties. Later ticks stay queued.
    """

    def __init__(self) -> None:
        self._items: list[tuple[int, Command]] = []
        self._next_index = 0

    def enqueue(self, command: Command) -> None:
        if not isinstance(command, Command):
            raise TypeError("command must be a Command")
        self._items.append((self._next_index, command))
        self._next_index += 1

    def pop_due(self, tick: int) -> list[Command]:
        if isinstance(tick, bool) or not isinstance(tick, int):
            raise TypeError("tick must be an int")
        if tick < 0:
            raise ValueError("tick must be >= 0")
        due = [item for item in self._items if item[1].tick == tick]
        self._items = [item for item in self._items if item[1].tick != tick]
        due.sort(key=lambda item: (item[1].seq, item[0]))
        return [item[1] for item in due]

    def __len__(self) -> int:
        return len(self._items)
