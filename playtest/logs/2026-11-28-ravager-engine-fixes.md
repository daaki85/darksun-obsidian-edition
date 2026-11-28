# Test log: Shattered Lands' engine fixes in Wake of the Ravager (2026-11-28)

Branch claude/ravager-engine-fixes. Under test: Scare's save for an elf or half-elf priest (scare_elves at
84256h), a natural 20 against "can't save" (SAVE_SUM/SAVE_NAT, sites 220-221), an archer's quiver running dry
(AMMO_CAP/TURN/OKAY, sites 217-219), New counted as Okay (23 tests), the scripts' buffer (11,776 bytes).
- Scare's save, elf priest: Terrannus (member 1, earth cleric) made race 3 (elf) and level 3 in memory; Ar'anda's Scare: 'Terrannus's saving throw vs Scare: d20 = 9 +4 WIS 19 = 13, needs 13 -> saved' (unfixed: an elf priest below 6th couldn't save). Gerakis 7th saved automatically; Thy'rokh natural 20.
- Quiver, first try (the Draxans' ambush, Gerakis's weapon made a bow and his left-hand item one arrow mid-fight): the game took the bow as a melee weapon (1d1 + STR) and the pointer stayed the sword: a fight's ready weapon is set as it starts. Next: the edit before the thieves' fight.
- Quiver (fixed build): ravager-after-ambush loaded; before the thieves' fight Gerakis's long sword (item 13) made a bow (type 18, slot 2) and his left-hand item (14) one arrow (type 6, slot 1, count 1); ravgo.py to (1841,1253), answer 2, Space; the thieves and thugs at 1 HP. On Gerakis's turn the bow pointer (one right-click from the walk arrow) on a thug: he shot (the arrow gone from his items), killed the Thief beside it, and DSCLOG2's AMMO_OUT was 3 (his shots cut with attacks left). The turn stayed his (Move 12); with the walk arrow he walked (154,84) to (105,69) on the same turn.
