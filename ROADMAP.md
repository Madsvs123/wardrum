# Roadmap

Steps 1 and 2 are the tick clock, the lockstep command boundary, the seeded substream, and the state hash in this repository. Steps 3 through 30 are future work. None of them are implemented.

## Field

3. Terrain types as static data on each cell: open ground, forest, and road.
4. A movement cost taken from the cell a unit is entering.
5. Line of sight that stops on blocking terrain.
6. Elevation, and a rule for moving between heights.

## Squads and contact

7. Squads that group units without replacing the unit record.
8. Formation slots so a squad keeps a shape while it moves.
9. A leader inside the squad, and a record of what happens when that leader is lost.
10. Facing arcs that mark front, flank, and rear.
11. Melee contact when two opposing units are on adjacent cells.
12. Ranged resolution that reads only the sim substream.
13. Armor and damage tables applied at a tick boundary.

## Morale and supply

14. Morale states on a unit.
15. Morale contagion among units that share a squad.
16. Rally and rout as commands applied on a tick boundary.
17. Supply measured in days, with attrition when the days run out.
18. Baggage and a resupply point a force can reach.
19. Fatigue that accumulates across resolved ticks.

## Conditions

20. Weather as a value drawn from the existing sim substream, so it stays in the hash.
21. Reduced visibility during a night period of the campaign clock.

## Campaign

22. A campaign graph whose nodes name places a force can occupy.
23. Army movement from one node to a neighboring node.
24. A handoff that starts a battle from a campaign contact and returns a result to the graph.

## Save, replay, and scenarios

25. A save snapshot of the tick, the units, the rng counter, and the commands still waiting.
26. Loading that snapshot and continuing the same hash sequence.
27. A replay log that is the command list plus the seed.
28. Checking a replay by comparing its final hash with the saved digest.
29. A scenario document format for fields other than the built-in skirmish.
30. A second skirmish loaded through that format, still with fixed starting units.

Later steps must keep the tick size fixed, apply commands only on a tick boundary, and hash canonical state. The package stays free of UI dependencies until a separate presentation layer exists.
