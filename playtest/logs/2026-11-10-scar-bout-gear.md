# 2026-11-10: Scar's bout with his new gear

Under test (commit be78f1d):
- Scar (object 87): obsidian cahulaks in place of his obsidian long sword, plus leather leggings and a helm on top of his leather chest and arm armour.
- His henchmen (object 229): a bone axe, and leather chest and arm armour.

## From `pens-fire-count4` (the arena count 4)
- `buildcheck.py` OK. Rested at the ring; Kurzak called on the third rest; `toarena.sh`, Y.
- In the arena, from (488,264): `walkto.py` can't reach the bone wall's gap (NO PATH; the view snaps back). Instead: `scroll.py 0 -100` twice, a click at screen (180,130) (the gap, map 504,360), then clicks at map (488,420) until the bout started (two).
- **Scar swung his Obsidian Long Sword**, and wore only leather chest and arm armour; his henchmen held only bone axes (`npcgear.py`).
- The Loader's `dos/SEGOBJEX.GFF` had the new gear (87: types 7, 6, 147, 8, 5; 229: 119, 6, 7). The save holds the arena's people as they were made on its first visit (before this change). So a game already past the first bout keeps the old Scar. CHANGELOG says so.

## A new game
In the background: `start.sh`, `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh`.
- New game: `start.sh`, `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh`, about 25 minutes, with no stalls. The party came out in the pens at (1816,440).
- Kurzak's greeting: the 6 key did nothing (the talk keys are 1-5). The list's down arrow (311,187) scrolled it, and a click on Goodbye (30,189) chose it. Then `follow.py 29` took the party to his stop (99,32).
- The arena count was set to 4 in memory (`setcount.py 4`, new; it read 1).
- `route.py 1592 584`, walkto (1600,600), (1720,600), (1832,600), then `route.py 1832 856`. The fire room door was shut in the new game. I opened it with the eye on the gold pole at screen (198,112), camera (1656,720), then clicked the room's floor (240,160).
- With that camera, the ring is at screen (276,134). Kurzak called on the fourth rest. Then `toarena.sh`, Y.
- In the arena: walkto (488,264) stopped at 216, then `scroll.py 0 -100` twice, a click on the gap (176,106) and two clicks at map (488,420). The Announcer and Scar spoke; I chose "No more talk" (5).

## Scar's bout (new game)
- `npcgear.py` before the fight:
  - **Scar:** worn Leather Helm, Leather Leg Armor, Leather Chest Armor, Leather Arm Armor; held Obsidian Cahulaks.
  - **Each of the three henchmen:** worn Leather Arm Armor, Leather Chest Armor; held Bone Axe.
- `acs.py` (the game's AC):
  - Scar 4 (5 before);
  - the henchmen 8 (10 before).
- In the attacks, Scar's target AC was 3: the helm's point, with Helms give AC 1, is counted at the attack.
- **Scar's swings:** "Scar attacks K'ratchek with Obsidian Cahulaks (1d6) ... THAC0 14, +1 STR, -2 obsidian = 15", then the second head: "... -2 cahulaks, off head at DEX 17 = 17". Both missed K'ratchek (AC 0), so there was no hit or tangle to see.
- The henchmen swung their bone axes (THAC0 18, -1 bone).
- `fightout.sh` finished it: Scar and all three henchmen killed.
- My Tab + Return loop stalled on Gerakis with no Move left (Tab kept choosing, and nothing attacked). `fightout.sh` handles that with E.
