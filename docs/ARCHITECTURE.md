# Architecture

wardrum separates three clocks that are easy to mix up: the tick size, the time scale, and the wall clock. Only the first two exist here, and the wall clock is never read.

## Tick size

One tick is the smallest step the simulation will ever take. It is conceptually 50 ms, which is 20 ticks per second at 1x. Hit points, positions, and the rng counter change only when a tick is resolved. Callers pass an integer tick count into the runner. There is no `sleep`, and tests stay deterministic because nothing waits for real time.

The tick size does not change when the player speeds up or pauses.

## Time scale

`TickClock` answers a different question: how many of those fixed ticks should one presentation frame consume?

| Scale | Meaning | Ticks from one 50 ms frame |
| --- | --- | --- |
| 0 | Pause | 0 |
| 0.25 | Quarter speed | 1 on every 4th frame, otherwise 0 |
| 1 | Real time | 1 |
| 2 | Double | 2 |
| 4 | Quadruple | 4 |
| 8 | Octuple | 8 |

The clock keeps an integer accumulator. A scale is a number of quarters of a tick (0, 1, 4, 8, 16, or 32). Each frame adds `quarters * frame_budget_ms`. Every 200 units (`4 * 50`) become one tick, and the remainder stays in the accumulator.

At 0.25x a 50 ms frame adds 50 units. Frames 1, 2, and 3 return 0. Frame 4 reaches 200 and returns 1, then the residue is 0. The pattern repeats. Pause adds nothing, so it does not throw away a partial tick that quarter-speed has already stored.

Scale changes how many ticks a frame consumes. It never resizes a tick.

## Command boundary

A `Command` is a frozen value: `tick`, `seq`, `kind`, `unit_id`, and an immutable payload. The queue will not hand it to the state until the simulation resolves that exact tick. A command stamped for tick 5 is still sitting in the queue while tick 4 resolves. Commands for the tick being resolved are applied in ascending `seq`. Equal seq values keep enqueue order.

The headless runner resolves one boundary like this:

1. Pop commands whose stamp equals the current tick.
2. Apply them in seq order. A move changes `x` and `y` by one orthogonal step. The map is `x` in 0..79 and `y` in 0..39. An illegal move, including one that would leave the map, is recorded on the state and not applied.
3. Advance the seeded substream once. The word it returns is stored as `rng_counter`.
4. Increment the tick.

Nothing is applied mid-tick. The generator is a pure Python xorshift64* substream, not `random.Random`. One substream belongs to the sim.

## Hash

After the requested ticks, `state_hash(tick, units, rng_counter)` builds one JSON document and returns its SHA-256 hex digest.

- `tick` is the tick index after the run (it equals the number of boundaries resolved when the run started at 0).
- `units` are objects with `id`, `x`, `y`, `hp`, and `facing`, sorted by `id` before encoding.
- `rng_counter` is the substream word from the last advance, or the seed-derived initial word when zero ticks were resolved. Different seeds therefore hash differently even if no unit moved.

JSON objects use sorted keys and no extra whitespace. Rejections are recorded for the caller, and they are not part of this digest. Position, hit points, facing, tick, and the rng word are.

The same seed and the same command list produce the same hash. A different seed, or the same moves ordered by a different `seq`, produce a different hash.
