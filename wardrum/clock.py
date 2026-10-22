"""Fixed-size tick clock.

One tick is conceptually 50 ms, so a 1x simulation runs at 20 ticks per
second. Callers never sleep. They ask how many integer ticks a frame
consumes, then advance the simulation by that many ticks.

Time scale changes the tick count of a frame. It does not change the
tick size. Allowed scales are 0 (pause), 0.25, 1, 2, 4, and 8.

Accumulator
-----------
The clock keeps an integer residue measured in quarter-milliseconds of
scaled time. Each frame adds ``quarters * frame_budget_ms``:

    scale 0    -> 0 quarters   (pause adds nothing)
    scale 0.25 -> 1 quarter
    scale 1    -> 4 quarters
    scale 2    -> 8 quarters
    scale 4    -> 16 quarters
    scale 8    -> 32 quarters

One tick is released for every 4 * 50 = 200 accumulated units. At 0.25x
with a 50 ms frame the clock adds 50 units, so the first three frames
return 0 and the fourth frame returns 1. The leftover residue is kept,
including across a pause.
"""

from __future__ import annotations

from fractions import Fraction

TICK_MS = 50
_QUARTERS_PER_TICK = 4
_UNITS_PER_TICK = _QUARTERS_PER_TICK * TICK_MS

_CANONICAL: dict[Fraction, float] = {
    Fraction(0): 0,
    Fraction(1, 4): 0.25,
    Fraction(1): 1,
    Fraction(2): 2,
    Fraction(4): 4,
    Fraction(8): 8,
}
_QUARTERS: dict[float, int] = {
    0: 0,
    0.25: 1,
    1: 4,
    2: 8,
    4: 16,
    8: 32,
}
ALLOWED_SCALES = (0, 0.25, 1, 2, 4, 8)


class TickClock:
    """How many sim ticks one presentation frame should consume.

    ``ticks_for_frame(50)`` is 1 at 1x, 2 at 2x, 4 at 4x, 8 at 8x, and 0
    while paused. At 0.25x the same frame returns 1 only on every fourth
    call. The result is always an integer. Nothing in this class waits
    on the wall clock.
    """

    def __init__(self, scale: float = 1) -> None:
        self._quarters = 0
        self._residue = 0
        self._scale: float = 0
        self.set_scale(scale)

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def residue(self) -> int:
        """Unreleased accumulator units. 200 units become one tick."""
        return self._residue

    def set_scale(self, scale: float) -> None:
        """Select a scale. The accumulator residue is left as it is."""
        if isinstance(scale, bool) or not isinstance(scale, (int, float, Fraction)):
            raise TypeError("scale must be a number")
        exact = Fraction(scale)
        if exact not in _CANONICAL:
            allowed = ", ".join(str(item) for item in ALLOWED_SCALES)
            raise ValueError(f"scale must be one of {allowed}")
        canonical = _CANONICAL[exact]
        self._scale = canonical
        self._quarters = _QUARTERS[canonical]

    def ticks_for_frame(self, frame_budget_ms: int = TICK_MS) -> int:
        """Return the integer tick count for this frame at the current scale.

        Fractional scales keep the remainder in ``residue`` so a later frame
        can release it. Pause adds zero units.
        """
        if isinstance(frame_budget_ms, bool) or not isinstance(frame_budget_ms, int):
            raise TypeError("frame_budget_ms must be an int")
        if frame_budget_ms < 0:
            raise ValueError("frame_budget_ms must be >= 0")
        self._residue += self._quarters * frame_budget_ms
        ticks, self._residue = divmod(self._residue, _UNITS_PER_TICK)
        return ticks
