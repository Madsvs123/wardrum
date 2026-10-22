# wardrum

wardrum is a deterministic tick engine for a future war campaign. It advances a battle as a sequence of integer ticks, applies commands only on tick boundaries, and hashes the result so a replay can be checked. Combat, terrain, and a campaign map are not in this repository yet. See [ROADMAP.md](ROADMAP.md).

This project is for the author alone. There are no player accounts and no personal data.

## Language

Python 3, standard library only. The `wardrum` package has zero UI dependencies. The command line uses `argparse`.

## Defaults

The engine is built for real-time-with-pause and strict lockstep. The setting, when combat arrives, is low-fantasy. Those defaults are design constraints, not features implemented beyond the tick clock, the command queue, and the state hash.

A tick is conceptually 50 ms (20 ticks per second). The simulation never sleeps on the wall clock. Time scale is one of `0` (pause), `0.25`, `1`, `2`, `4`, or `8`, and it only changes how many ticks a frame consumes. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Run

From this directory:

```text
py -3 -m wardrum --seed 42 --ticks 2000 --hash-out
py -3 -m wardrum --seed 42 --ticks 2000 --hash-out --scenario skirmish_01
```

`--hash-out` prints one SHA-256 hex line. `--seed` defaults to 42 and `--ticks` defaults to 2000. Without `--scenario` the map is empty. `skirmish_01` places two units at fixed positions: `ranger` at (18, 12) facing east, and `warden` at (60, 12) facing west.

## Test

```text
py -3 -m pytest
```

The same seed and the same command list produce the same hash. A different seed, or the same commands in a different seq order, produces a different hash.

## License

MIT. See [LICENSE](LICENSE). Copyright 2026 Madsvs123.
