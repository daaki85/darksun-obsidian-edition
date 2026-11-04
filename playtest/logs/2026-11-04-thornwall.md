# Thornwall on the pens' weapon rack after Semyon's tip (2026-11-04)

Build: `obsidian-edition` at 46d05e3 plus the fix below. DOSBox, a new game with the ready-made party.

1. `start.sh`, `topartyfight.sh`, then `arenawaves.sh && leavearena.sh`: the waves, N to the
   Announcer, out by the gate; in the pens (region 29h) at (1816, 440), Kurzak's greeting.
2. Before the tip: the only item of the racks' type (6Ch) in memory was a **Coffin** (object 1574,
   at 75,43) holding a Gem. The weapon rack itself (object 2599, square 48,34) wasn't among the
   map objects.
3. Flag 756 set in memory (what Semyon's new answer sets). Within seconds `semyon.ship` (the
   committed version) put Thornwall **in the coffin**: it took the first item of type 6Ch.
   **Bug.**
4. Why: the game makes a region's map objects as the party comes near them. Walking south made
   objects 1221, 1224, 1230, 1236 and 1390 that weren't there before.
5. Fix: `ship` now looks for the rack by its object (2599) among the map objects and does
   nothing until the game has made it. The coffin's Thornwall was undone in memory (its record
   returned to the free list, 757 cleared) and the dice log restarted on the fixed code.
6. Kurzak followed to his stop, then through his door and down the east passage. The door at
   (113, 90) is **locked** ("The door is locked. It appears quite sturdy."), so the party was
   moved in memory to (840, 584) and walked a step. The game then made the rack (map object 173,
   item 210, contents 478) and Thornwall was put first: **Thornwall, Polearm, Quarterstaff,
   Polearm, Axe**. Flag 757 set.
7. Walked back east and about: the rack and Thornwall stayed.
8. Saved (slot "THORNWALL RACK", `saves/pens-thornwall-rack`) and loaded: the rack still holds
   Thornwall, one of it, with flags 756 and 757 set.

Not checked in the game: Semyon's new line itself. He is in his pen only after the arena rescue,
and this run didn't get him there. The unit tests cover the line and its flag.
