"""A debug trace lists ticks and leaves the lockstep hash unchanged."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from wardrum.commands import CommandQueue, move
from wardrum.rng import SimRng
from wardrum.runner import run
from wardrum.state import SimState, Unit

ROOT = Path(__file__).resolve().parents[1]


def _field(seed: int, debug: bool, sink) -> tuple[str, int]:
    state = SimState()
    state.add_unit(Unit("solo", 4, 4, 2, "E"))
    queue = CommandQueue()
    queue.enqueue(move(1, 1, "solo", 1, 0))
    digest = run(state, queue, SimRng(seed), 3, debug=debug, debug_sink=sink)
    return digest, state.units["solo"].x


def test_debug_trace_does_not_change_the_hash():
    quiet_hash, quiet_x = _field(11, False, None)
    lines: list[str] = []
    loud_hash, loud_x = _field(11, True, lines.append)
    assert quiet_hash == loud_hash
    assert quiet_x == loud_x == 5
    assert [line.split()[0] for line in lines] == ["tick=1", "tick=2", "tick=3"]
    words = [line.split("rng_counter=", 1)[1] for line in lines]
    assert len(words) == 3
    assert len(set(words)) == 3


def test_debug_off_does_not_call_the_sink():
    called: list[str] = []
    run(SimState(), CommandQueue(), SimRng(1), 2, debug=False, debug_sink=called.append)
    assert called == []


def test_cli_debug_keeps_the_hash_on_stdout():
    base = [sys.executable, "-m", "wardrum", "--seed", "42", "--ticks", "5", "--hash-out"]
    quiet = subprocess.run(base, cwd=ROOT, capture_output=True, text=True, check=False)
    loud = subprocess.run(
        [*base, "--debug", "--scenario", "skirmish_01"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    plain = subprocess.run(
        [*base, "--scenario", "skirmish_01"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert quiet.returncode == 0
    assert loud.returncode == 0
    assert plain.returncode == 0
    assert quiet.stderr == ""
    assert plain.stderr == ""
    assert loud.stdout == plain.stdout
    assert loud.stdout != quiet.stdout
    assert [line.split()[0] for line in loud.stderr.splitlines()] == [
        "tick=1",
        "tick=2",
        "tick=3",
        "tick=4",
        "tick=5",
    ]
