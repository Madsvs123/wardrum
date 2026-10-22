"""One seeded substream for the simulation.

This is a pure integer xorshift64* generator. It is not ``random.Random``
and it does not draw from process-wide entropy. The word returned by
``advance`` is the rng counter stored in the lockstep hash, so two runs
with different seeds diverge even when every unit stands still.
"""

from __future__ import annotations

_MASK = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15
_MULTIPLIER = 0x2545F4914F6CDD1D


def _splitmix64(seed: int) -> int:
    """Expand a 64-bit seed into a nonzero starting state."""
    z = (seed + _GOLDEN) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    z = (z ^ (z >> 31)) & _MASK
    if z == 0:
        return _GOLDEN
    return z


class SimRng:
    """Seeded xorshift64* substream used only by the simulation."""

    def __init__(self, seed: int) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("seed must be an int")
        self._state = _splitmix64(seed & _MASK)
        self.advances = 0
        self.counter = self._state

    def advance(self) -> int:
        """Step the substream once and return the new counter word."""
        x = self._state
        x ^= x >> 12
        x &= _MASK
        x ^= (x << 25) & _MASK
        x ^= x >> 27
        x &= _MASK
        self._state = x
        self.advances += 1
        word = (x * _MULTIPLIER) & _MASK
        self.counter = word
        return word
