"""The CLI prints one lockstep hash and nothing else."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wardrum", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_hash_out_prints_one_hex_line():
    first = _run(["--seed", "42", "--ticks", "2000", "--hash-out"])
    second = _run(["--seed", "42", "--ticks", "2000", "--hash-out"])
    assert first.returncode == 0
    assert second.returncode == 0
    assert first.stdout == second.stdout
    assert re.fullmatch(r"[0-9a-f]{64}\n", first.stdout)
    assert first.stderr == ""


def test_without_hash_out_stdout_stays_empty():
    proc = _run(["--seed", "1", "--ticks", "3"])
    assert proc.returncode == 0
    assert proc.stdout == ""


def test_negative_ticks_fail():
    proc = _run(["--ticks", "-1", "--hash-out"])
    assert proc.returncode != 0
    assert proc.stdout == ""
