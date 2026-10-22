"""skirmish_01 always starts the same two units."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from wardrum.scenario import load_scenario

ROOT = Path(__file__).resolve().parents[1]


def test_skirmish_01_places_two_fixed_units():
    state = load_scenario("skirmish_01")
    assert state.tick == 0
    ranger = state.units["ranger"]
    warden = state.units["warden"]
    assert (ranger.x, ranger.y, ranger.hp, ranger.facing) == (18, 12, 10, "E")
    assert (warden.x, warden.y, warden.hp, warden.facing) == (60, 12, 10, "W")


def test_each_load_is_a_fresh_field():
    first = load_scenario("skirmish_01")
    second = load_scenario("skirmish_01")
    first.units["ranger"].x = 19
    assert second.units["ranger"].x == 18


def test_cli_scenario_changes_the_hash_and_is_stable():
    def invoke(scenario: str | None) -> subprocess.CompletedProcess[str]:
        args = ["--seed", "42", "--ticks", "30", "--hash-out"]
        if scenario is not None:
            args.extend(["--scenario", scenario])
        return subprocess.run(
            [sys.executable, "-m", "wardrum", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    empty = invoke(None)
    skirmish = invoke("skirmish_01")
    again = invoke("skirmish_01")
    assert empty.returncode == 0
    assert skirmish.returncode == 0
    assert re.fullmatch(r"[0-9a-f]{64}\n", skirmish.stdout)
    assert skirmish.stdout == again.stdout
    assert skirmish.stdout != empty.stdout


def test_unknown_scenario_is_rejected():
    proc = subprocess.run(
        [sys.executable, "-m", "wardrum", "--scenario", "missing", "--hash-out"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert proc.stdout == ""
    assert "unknown scenario" in proc.stderr
