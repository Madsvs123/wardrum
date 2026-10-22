"""The sim substream is pure Python, seeded, and independent of random.Random."""

from __future__ import annotations

import inspect
import random

import pytest

from wardrum.rng import SimRng


def test_same_seed_replays_the_same_words():
    first = SimRng(42)
    second = SimRng(42)
    drawn_first = [first.advance() for _ in range(64)]
    drawn_second = [second.advance() for _ in range(64)]
    assert drawn_first == drawn_second
    assert first.counter == drawn_first[-1]
    assert first.advances == 64


def test_different_seeds_diverge():
    assert SimRng(1).advance() != SimRng(2).advance()


def test_seed_zero_is_usable():
    rng = SimRng(0)
    assert rng.counter != 0
    assert rng.advance() != 0


def test_generator_is_not_random_random():
    rng = SimRng(7)
    assert not isinstance(rng, random.Random)
    source = inspect.getsource(inspect.getmodule(rng))
    assert "import random" not in source
    assert "random.Random" not in source


def test_bool_seed_is_rejected():
    with pytest.raises(TypeError):
        SimRng(True)
