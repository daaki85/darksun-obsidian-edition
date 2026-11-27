# 2026-11-27: a Spellarcher makes spell arrows in Wake of the Ravager

**Under test:** branch `claude/ravager-spell-arrows` (ce1ff745, on claude/ravager-poison-arrows): DSCLOG2's SPELL
ARROWS (site 240 at 9659Eh and PICK POCKETS' sites 180-185 extended), the header's +2098 to +2113, and the Loader's
`ravarrows.make` (RavDiceLog._answer_arrows); the arrows' objects in OBJEX2.GFF and the buttons' icons (ICON
3050-3052) in RESOURC2.GFF from the Loader's copies.

**Set-up:** `ravSA`, a throwaway copy of `$WORK/rav` (the big files hard-linked, the roster and DARKSAVE from
__support/save, no saves, no party transferred): `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh
/tmp/playtest/ravSA`, the dice log `RAV_NO_SAVES=1 ravdice.py 7000 sa-dice.txt --numbers`. The DOSBox lock held
throughout (no other DOSBox running at the start, about 02:45 UTC).

## Steps

1. **A new Spellarcher in a new game.** CREATE CHARACTERS, the first slot's NEW; the big portrait clicked six times
   (race 4, a male half-elf), PRESERVER (255,45) added to FIGHTER, KITS (234,138), NO KIT off (250,106),
   SPELLARCH (250,114): `ravkits.py page` race 4, classes [3, 5], kit byte 0x01. Named Fletch (a fighter 6 /
   preserver 6, the template's 64000 XP split). DONE: CHOOSE A SPELL, **Chill Touch** (170,71) and **Shocking
   Grasp** (189,91) picked, EXIT and EXIT for the rest; the powers' EXIT and EXIT; the weapon window offered the
   bow alone (a Spellarcher's) and it was picked. The dice log: "starts with a bow for the weapon specialization
   chosen ... +1 arrows with it", the shield and ring armour left behind, "Fletch starts with a Fine Bow (+1 to
   hit): a Spellarcher's". Then ADD from the roster: Clk'whrr, Meggyn, Zontorra (slot 2 to 4; the ADD list's rows
   y 56, 67, 78, ADD 253,46; a slot's right-click menu's ADD 40 right of the slot, 12 below). The bottom bar's
   right-hand icon (266,171) back to the title menu, then START GAME (S).
2. **The first game lost.** With Fletch, Clk'whrr, Meggyn and Zontorra and Computer Control on for all four, the
   Draxans' ambush ended "YOUR PARTY HAS BEEN DEFEATED". DOSBox stopped (by its pid) and started again on the same
   copy: **the party isn't kept between starts** (START GAME with no one ADDed in this run plays the ready-made
   party, Ar'Anda, Terrannus, Thy'rokh and Gerakis: `ravcreatures.py` read them in the ambush, so that game was
   dropped too). CREATE CHARACTERS again: the roster keeps Fletch (ADD's first row); Fletch, Clk'whrr, Zontorra
   and Borzak (a mul gladiator 7, 112 HP) ADDed (the ADD list's rows at game y 46, 57, 68, 78, 89; a slot's menu
   ADD 40 right of the slot and 12 below on the top row, on the bottom row at the slot's x + 73, y 129). The
   bottom bar's right-hand icon, S, the opening talk (3, Return x4).
3. **The ambush won** with HP 250 for the four (a test edit, never saved:
   [files/2026-11-27-ravager-spell-arrows-hp250.py](files/2026-11-27-ravager-spell-arrows-hp250.py), the creature
   records' +0) and Computer Control for all four (C, the four lower small icons). "Each party member receives
   10000 experience points!"; the level-up lines and Zontorra's weapon window (EXIT 230,175, then EXIT 145,92 in
   YOU HAVE MORE). The dice log had turned off quick saves and autosaves, and nothing was saved all play.
4. **The buttons.** USE (23,18) out of the fight, Fletch's portrait (70,56): under his spells **two buttons**, light
   blue and blue, at the place SL has them (157,147 and 176,147 at the game's size), the pointer on them naming them
   **CHILL ARROWS** and **SHOCKING ARROWS** in the bar ([the screen](img/2026-11-27-ravager-spell-arrows-buttons.png)).
   They stay on the PSIONIC and MAGE pages alike (the selector at 150,171). Header (
   [files/2026-11-27-ravager-spell-arrows-hdr.py](files/2026-11-27-ravager-spell-arrows-hdr.py)): on 1,
   arrows_shown 6 (two a showing), extras_drawn 3 (the second button, beside the first's place), late 0.
5. **One made.** A slow press on CHILL ARROWS closed the screen and the dice log said:
   > Fletch makes one of the chill arrows in the pack (1 of 24 now): a 1st-level slot used; it casts Chill Touch on
   > what it hits, at Fletch's preserver level, and lasts until shot

   `ravitems.py 0`: a new item 212, type 6 (arrows), slot 14 (the pack), name 299 (256 + 42 + 1, "Chill Arrows"),
   power 4 (Chill Touch 3, + 1); its record `a8a7 0100 ...`: object 22616 (the Loader's copy of SL's chill
   arrows' picture).
6. **A second, stacked.** USE, Fletch, CHILL ARROWS again: "Fletch makes one of the chill arrows (2 of 24 now)";
   still item 212, its count 2 (no second item). The MAGE page: **SPELLS LEFT WIZ 2/4** (4/4 before: one slot a
   press; [the screen](img/2026-11-27-ravager-spell-arrows-slots.png)).
7. **Shot.** The chill stack put in the quiver and the plain +1 arrows (count 12) in the pack (a test edit, never
   saved: [files/2026-11-27-ravager-spell-arrows-quiver.py](files/2026-11-27-ravager-spell-arrows-quiver.py)
   `--write`; the inventory screen would do the same), the bow +15 (`ravitems.py 0 --bow15`, a test edit, never
   saved) so that Computer Control shoots. Out of the house by a click on the street (game 250,125), `ravgo.py y
   1224 x 1839` and Right x4: Tyr's thieves ("Hey, sewer-scum!"), 2, Space. In the fight Fletch's USE screen has
   **no arrows buttons** ([the screen](img/2026-11-27-ravager-spell-arrows-fight.png); and a click on a portrait
   there gave "ONLY ACTIVE CHAR CAN CAST"); C's small icons were still on from the ambush, so the first clicks
   turned Computer Control off: clicked again. The dice log, rounds 1 and 2:
   ```
   Fletch attacks Thief#18 with Wooden item 305 +15 (1d8+15): d20 = 7, hits on anything but a 1 (95%), ... -> HIT
     Fletch hits Thief#18 for 22: 1d8 = [3] +16 weapon +3 mastery
   Chill Touch damage: 1d4 = [1] = 1
       Chill Touch lasts 60 rounds (caster level 6: 1 from the dice; dice 1d1)
   Thief#18's saving throw vs Chill Touch from Fletch#0 (spell): d20 = 19 ... -> saved: no damage (not 1)
   ...
   Fletch hits Thief#18 for 20: 1d8 = [1] +16 weapon +3 mastery
   Chill Touch damage: 1d4 = [1] = 1
       Chill Touch lasts 60 rounds (caster level 6: 1 from the dice; dice 1d1)
   Thief#18's saving throw vs Chill Touch from Fletch#0 (spell): d20 = 2 ... -> failed: full damage, 1
     Thief takes 1 from Chill Touch, now 2/45 HP
   ```
   **Caster level 6: Fletch's preserver level** (the Spellarcher's rule). Count 2, 1, then the item let go (slot
   255); the game took the plain arrows into the quiver by itself and the next shot (round 5) cast nothing. After
   each shot the game said "Out of ammo" (three times after the last): its own cut of a round's shots to the
   stack's count, not the Loader's.
8. **Control.** The dice log restarted with `RAV_NO_ARROWS=1` ("spell arrows buttons off"; header on 0): Fletch's
   USE screen out of a fight has **no buttons** under his spells and arrows_shown stayed 16
   ([the screen](img/2026-11-27-ravager-spell-arrows-control.png)).

## What was learned

- Each start of the sequel's title menu forgets the party: ADD them again before every START GAME (the roster keeps
  them). A new 6/6 Spellarcher with three roster members lost the Draxans' ambush under Computer Control; HP 250 (a
  test edit) won it.
- The thieves' street from the ambush: the leader starts inside the house west of the street (world 1072, 1322);
  `ravgo.py` can't leave it (the walls), a click on the street (game 250,125) can; then `ravgo.py y 1224 x 1839`
  and Right x4.
- C's small icons toggle: Computer Control left on from the ambush is turned off by a second round of clicks.
- The dice log names the Loader's Fine Bow "Wooden item 305" (its name number, ravager.FINE_BOW_NAME, one of the
  Loader's own names, which the dice log's item names don't read): a naming gap of the dice log's, not looked into.

## Water

No new area (Tyr's ambush street and the thieves' street, as before).

## Clean-up

DOSBox, the dice logs and the lock's holder stopped by pid; `ravSA` thrown away; nothing written into `rav` or `ravK`.
