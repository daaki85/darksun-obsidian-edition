# Audit leftovers and the selling order, in the game (2026-11-11)

Build: obsidian-edition with locks by identity, LOOT_KEY holding a second T, and S paying per item
(DSCLOG 69,360 bytes; `buildcheck.py` OK).

- **A lock by what it is.** From `pens-new-chest`: `shut.py`, `teleport.py 200 1432 40 1322`,
  walkto (216,1440) then (184,1400), `thief.py 0 1`. `chestuse.sh`: "Gerakis tries to open locks:
  d100 = 46, needs 25 or less -> failure". The look pointer then wouldn't open the chest's box (the
  eye red over it, three tries); `pointer.py walk` and `chestuse.sh` again did: "Gerakis tries to
  open locks: d100 = 81 -> failure (Gerakis failed this lock at this thief level: another try once
  a level is gained)". From memory: the chest is thing 239, `locks.identity` "o1568@201,1402",
  `things_now` [239].
- **S** from `selling-junk-user` (`openshop.sh`, S): "Gerakis sells 9 things for 95 ceramic
  pieces"; the purse 85 -> 180.
- **Two bodies' T one after the other.** From `fountain-user`: `dismiss.sh`, `fightout.sh`, the
  party walked west (`walkto.py 1000 1490`), the panel hidden (L: it covered the guards' bodies).
  Pehtucl's body (the eye at 78,140), T: "Lex takes Slavepen key, Grapes, Guava (4), Obsidian
  Bloodwrath +1" / "Ester takes ... Leather Shield"; then a guard's (235,146), T: "Ester takes
  Shovel, Corn, Wooden Bow, Obsidian Long Sword, Leather Arm Armor, Wooden Arrows, Leather Chest
  Armor". Both taken: the first T released for the second.
- Not saved (memory edits).
