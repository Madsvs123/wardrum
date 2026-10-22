"""Command-line entry for the headless tick engine.

``py -3 -m wardrum --seed 42 --ticks 2000 --hash-out`` prints one hex
digest. The sim package itself has no UI dependencies; this module is
the only place that parses arguments, and it uses argparse.
"""

from __future__ import annotations

import argparse
import sys

from wardrum.commands import CommandQueue
from wardrum.rng import SimRng
from wardrum.runner import run
from wardrum.state import SimState


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wardrum",
        description=(
            "Deterministic tick engine for a future war campaign. "
            "Prints a lockstep hash. Stores no personal data."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="sim substream seed (default: 42)",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=2000,
        help="tick boundaries to resolve (default: 2000)",
    )
    parser.add_argument(
        "--hash-out",
        action="store_true",
        help="print the final state hash as one hex line",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.ticks < 0:
        parser.error("--ticks must be >= 0")
    state = SimState()
    digest = run(state, CommandQueue(), SimRng(args.seed), args.ticks)
    if args.hash_out:
        print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
