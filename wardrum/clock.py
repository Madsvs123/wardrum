"""Fixed-size tick clock.

One tick is conceptually 50 ms, so a 1x simulation runs at 20 ticks per
second. Callers never sleep. They ask how many integer ticks a frame
consumes, then advance the simulation by that many ticks.

Time scale changes the tick count of a frame. It does not change the
tick size. Pause is scale 0. This module accepts the integer scales
0, 1, 2, 4, and 8. A later change keeps a fractional accumulator so
0.25x can emit a tick on every fourth frame.
"""

from __future__ import annotations

TICK_MS = 50
ALLOWED_SCALES = (0, 1, 2, 4, 8)


class TickClock:
    """How many sim ticks one presentation frame should consume.

    ``ticks_for_frame(50)`` is 1 at 1x, 2 at 2x, 4 at 4x, 8 at 8x, and 0
    while paused. The result is an integer. Nothing in this class waits
    on the wall clock.
    """

    def __init__(self, scale: int = 1) -> None:
        self._scale = 1
        self.set_scale(scale)

    @property
    def scale(self) -> int:
        return self._scale

    def set_scale(self, scale: int) -> None:
        if isinstance(scale, bool) or not isinstance(scale, int):
            raise TypeError("scale must be an int")
        if scale not in ALLOWED_SCALES:
            allowed = ", ".join(str(item) for item in ALLOWED_SCALES)
            raise ValueError(f"scale must be one of {allowed}")
        self._scale = scale

    def ticks_for_frame(self, frame_budget_ms: int = TICK_MS) -> int:
        """Return the integer tick count for this frame at the current scale."""
        if isinstance(frame_budget_ms, bool) or not isinstance(frame_budget_ms, int):
            raise TypeError("frame_budget_ms must be an int")
        if frame_budget_ms < 0:
            raise ValueError("frame_budget_ms must be >= 0")
        if self._scale == 0 or frame_budget_ms == 0:
            return 0
        return (self._scale * frame_budget_ms) // TICK_MS
