# In-game checks of the kit rebalance (2026-11-15)

Branch `kit-rebalance`, DSCLOG built from the branch (buildcheck.py: every changed routine the same
in memory as dos/DSCLOG.EXE: kinds_allowed, probe_belt, cell_heal, lv_due, arrow_save, th_cast,
probe_init, kit_forbids, av_know, av_harm, lv_scholar, probe_cr_spells, probe_slots, kf_cahulaks;
129 vectors at their handlers).

## Part 1: character creation

### Myrmidon (human fighter 3, "Swat") — PASS

- KITS page: NO KIT clicked off, MYRMIDON taken.
- DONE: PICK A WEAPON SPECIALTY. Every kind lit but the **polearm** (greyed: second row, fourth);
  the **bow lit** (any fighter's pick now). One pick (the long sword) **closed the window** (one
  due, not two).
- Dice log: "Swat starts with a plain bone polearm in the backpack too: a Myrmidon's second weapon spec".
- Sheet: weapon specs **long sword, polearm**; Bone Polearm (type 19) in the backpack; the game's
  shield, sling and long sword as before.

### Seeker, fire (human ranger 3, "Jaardoon") — PASS

- Ranger, CLERICAL SPHERE: AIR clicked off, FIRE on; KITS: SEEKER (the fourth row).
- DONE: PICK A WEAPON OF EXPERTISE. Lit: long sword, dagger, short sword, mace, axe, great axe,
  cahulaks, chatkcha (the kinds with an obsidian weapon). **Greyed: the bow**, club, pick,
  quarterstaff, polearm, gythka, sling, staff sling.
- Sheet: class 15 (fire ranger), Seeker, weapon spec the long sword.
- Gear: the **Wooden Bow in the backpack** (slot 14), its arrows still in the quiver.
- Noted, not from this change: the game's **bone** long sword stays in hand. A kit never forbids a
  weapon of a kind it specialized in ("a weapon spec is a weapon learnt for good"), so a fire
  Seeker who picks the long sword may wield any long sword. (The dice log's hit point line said
  "Ranger (air)": the dice were rolled while AIR was still marked.)

### Scholar (human preserver 3, "Hamonde", INT 19) — PASS

- KITS: SCHOLAR. DONE: CHOOSE A SPELL (its first icon at about 120,74; a click at 99,72 lands
  beside the icons and does nothing).
- Picks counted from shots: **seven at LEVEL 1, then two at LEVEL 2** (the plain preserver 3's
  4 + 2, and the Scholar's one more for each of its 3 levels), then the psionic powers.
- Known in memory: Armor, Burning Hands, Charm Person, Chill Touch, Color Spray, Enlarge, Gaze
  Reflection (1st), Blur, Detect Invisibility (2nd): **9**.
- Slots 2 / 1 / 0 (`max_spell_slots`): a plain preserver 3's, **no slot more** at INT 19.

### Healer (human water cleric 3, "Aticus") — PASS

- Cleric, CLERICAL SPHERE: AIR off, WATER on; KITS: HEALER (third row; offered with WATER marked).
- Known priest spells after DONE: **none of the harming ones**: no Cause Light Wounds (72), Cause
  Disease (97), Cause Serious Wounds (113), Poison (119), Cause Critical Wounds (128), Slay Living
  (136). Its cosmos spells there: Abjure, Cloak of Bravery, Cloak of Fear, Free Action, Neutralize
  Poison, Prot'n from Evil 10' Rad., Cure Critical Wounds, Dispel Evil, Raise Dead; its cures; Blood
  Flow. (Harm: 6th level, past its 3rd.)
- Its psionic discipline was psychokinesis (a cleric's panel shows the spheres, not the
  disciplines: VIEW PSIONICS switches), so no Cell Adjustment to try here.

### Twin-blade (human gladiator 3, "JohnBoy") — PASS

- KITS: TWIN-BLADE (second row). DONE: PICK A WEAPON SPECIALTY: **the cahulaks lit** (second row,
  last); greyed: great axe, quarterstaff, polearm, gythka, bow, staff sling (two-handed).
- Picked the long sword, then the cahulaks (237,79): weapon specs **long sword, cahulaks**.
- The Loader's rule on the live sheet (`restrict.kit_forbids`): the cahulaks of bone (21), metal
  (146) and obsidian (147) allowed, also as a spec pick; the great axe (2) forbidden.

### Healer and Lifebinder with psychometabolism (the user's ask) — PASS at creation

- A cleric's or druid's creation panel shows its spheres; **VIEW PSIONICS** (240,138, in the KITS
  window's place) switches to the disciplines: P-KINESIS (250,106) clicked off, **P-METAB**
  (250,114) on; VIEW SPHERES switches back.
- PICK A PSIONIC POWER for P-METAB: 14 icons, powers 6-19 in order (Animal Affinity first); **Cell
  Adjustment is the 8th**, second row third (157,79).
- **Healer** "Killer" (human water cleric 3): powers Animal Affinity, Energy Containment, Life
  Draining, **Cell Adjustment**; harming spells known: none; its cosmos spells there.
- **Lifebinder** "Halton" (human air druid 3): the same four powers, **Cell Adjustment** among them;
  priest spells known: no Cause Light (72), Cause Disease (97), Cause Serious (113), Poison (119),
  Cause Critical (128), Slay Living (136); the druid's own cosmos spells there (Abjure, Free Action,
  Neutralize Poison, Cure Critical Wounds, Raise Dead...).
- (A dropped character's record stays in memory: `sheetinfo.py` still listed Aticus after DROP, and
  a right-click on the slot opened ADD, the slot empty.)

## Part 2: Cell Adjustment in play (the party at the arena gate, region 2Ah, out of a fight)

The party Swat (Myrmidon), Killer (Healer), Hamonde (Scholar), Halton (Lifebinder); START GAME
(`S` at the main menu), the opening's boxes clicked through to "Step forward". Swat's HP set to 3 in
memory (`setmem.py hp=0:3`; put back to 21 after: never saved). U opens the USE screen; a portrait
picks the user, the kind button (150,171) CLERIC -> PSIONIC; Cell Adjustment the fourth icon
(230,59), then the target's portrait (Swat 66,62).

- **Healer** — PASS: "Killer uses Cell Adjustment: power check d20 = 11, needs 11 or less -> it
  works" / "**Cell Adjustment: 1d4 = 1, +1 (Healer) -> Swat healed 2 HP**" / "Swat now 5/21 HP (+2)".
  (The first try's check failed: d20 18, the 2 PSP a failure costs.)
- **Lifebinder** — PASS: "Halton uses Cell Adjustment: power check d20 = 3, needs 16 or less -> it
  works" / "**Cell Adjustment: 1d4 = 1, +1d4 = 4 (Lifebinder) -> Swat healed 5 HP**" / "Swat now
  10/21 HP (+5)".
- Scholar's THAC0: the creature's +1Fh is **21** (a preserver 3's 20, 1 worse); View Character
  shows 20 (STR 17's +1 taken off), as the creation screen did.

## Part 3: a second party

### Brute (human gladiator 3) — PASS

- KITS: BRUTE (fourth row). DONE: PICK A WEAPON SPECIALTY: lit only the great axe, quarterstaff,
  polearm and gythka; **the cahulaks greyed** (second row, last), as every one-handed kind and the
  missile ones.

### Swashbuckler (human thief 3, "Celos") — PASS at creation

- KITS: SWASHBUCKLER (first). DONE: PICK A WEAPON SPECIALTY lit **only the long sword, dagger and
  short sword**. Picked the short sword: "Celos starts with a plain bone short sword for the weapon
  specialization chosen, in place of the bone long sword".

### Wayfinder (dwarf fighter/thief 2/2, "Morbad th'Worst") — made

- The big portrait (40,60) stepped the race to a dwarf (race 2); THIEF added (multiclass); KITS:
  G-FIGHTER, WAYFINDER (second). Long sword spec. (Its initiative: in the fight below.)

The party for the fight: Finster (Brute: great axe, polearm), Celos (Swashbuckler), Morbad
(Wayfinder), Hamonde (Scholar, from the roster: ADD, the list scrolled with its down arrow 219,146,
the name, ADD 252,46). (A party's last member can't be dropped: "LAST ONE: CAN'T DROP".)

## Part 4: the arena's first fight (Finster, Celos, Morbad, Hamonde)

START GAME, the opening, the step forward (`/tmp/playtest/startfight.sh`, topartyfight.sh's
steps); party turns by Tab + Return.

- **Wayfinder** — PASS: every round, "Morbad th'Worst 32 = 20 + 7 (0-9 roll) +2 DEX **+2 Wayfinder
  +1 Wayfinder's Path-finder**", every other member "+1 Wayfinder's Path-finder"; the totals the
  game's own (no "other" part), so DSCLOG's PROBE_INIT gave the same.
- **Swashbuckler bad luck** (the Loader's stealth roll at its turn) — PASS: "Celos hides in
  shadows: d100 = 59, needs 10 or less (35, halved in daylight; **- 7, a Swashbuckler's bad luck**)"
  and a round later "needs 3 or less (35, halved in daylight; **- 14**, ...)": a new amount each roll.
  Its attack: "THAC0 19, -1 bone, +1 Swashbuckler (a warrior's THAC0) = 19" with its short sword.
- **Brute** — PASS: "Finster attacks Slig with Bone Great Axe (1d10) ... THAC0 18, +3 STR, -1 bone,
  +1 specialized, **+2 Brute** = 13", the hit "1d10 = [10] -1 bone +2 specialized **+2 Brute** +7
  STR 19".
- **Scholar, a touch spell** — PASS: "Hamonde's Chill Touch at Slig: touch attack d20 = 4, needs
  17+ (20%) (**THAC0 21**, +1 STR; target AC 3)".
- **Scholar, Acid Arrow** (taught in memory for the test: the known byte, never saved) — PASS:
  "Hamonde's Acid Arrow at Slig: attack d20 = 6, needs 15+ (30%) (**THAC0 19 (a fighter's of the
  caster's level, a Scholar's 1 worse)**, +1 DEX; target AC 3)": a fighter 3's 18, 1 worse.
- Driving notes: a touch spell from afar says "too far away" and keeps the aim; a right-click
  cancelled it and passed the turn; a walk click that lands on a foe attacks it (Hamonde's staff).

## Part 5: a third party in the arena (Aticus, Deestan, Halton, Swat)

Made: **Sentinel** "Aticus" (human fighter 3, long sword), **Wild Fury** "Deestan" (mul
fighter/druid 2/2: the portrait stepped to race 7, DRUID added; KITS shows only WILD FURY),
**Spellarcher** "Halton" (half-elf fighter/preserver 2/2: race 4, PRESERVER added). The
Spellarcher's spells: CHOOSE A SPELL's icons are 6 a row, about 18 apart from (122,71), rows 22
apart; the list closes up after each pick (the first click took Shield, the same place then
Shocking Grasp). Its weapon window: **everything greyed but the bow**; "Halton's Arm Armor / Leg
Armor is left behind: a Spellarcher can't wear it", "Halton's Shield is left behind".

At the gate, out of the fight:
- **Spell arrow** — the USE screen on Halton (U, its portrait): under its spells, a red (Burning)
  and a blue (Shocking) button; a slow press on the blue one (176,147): "Halton makes one of the
  shocking arrows in the pack (1 of 24 now): a 1st-level slot used ..." (the quiver held its wooden
  arrows: the new stack went to the pack). Swapped in the inventory (I, Halton's portrait 22,118:
  quiver 66,26 to a backpack cell, the Shocking Arrows to the quiver). (The arrow button closes the
  USE screen: an Escape after it opened EXIT: SAVE GAME?; CANCEL 125,116.)
- **Sentinel's AC** — its shield taken off (left hand 173,92 to the backpack): AC on the inventory
  panel **0 -> 3** (the shield's 1 and the Sentinel's 2 gone).

In the fight:
- **Wild Fury** — PASS: "Deestan fights wild: d20 = 9, **needs 15 or less (CON 19 -4)** -> 1 more
  attack a round and +3 damage, -3 to hit and AC 3 worse for the fight"; its attacks "-3 Wild
  Fighting" on to hit, "+3 Wild Fighting" on damage, two a round; a Slig needed 7+ on its AC 10.
- **Sentinel** — PASS: initiative "Aticus 28 = 20 + 6 (0-9 roll) +2 DEX" (**no Sentinel part**);
  without a shield "THAC0 18, -1 bone, +1 specialized, **-1 Sentinel** = 19".
- **Myrmidon**: initiative "Swat 20 = 20 + 0 (0-9 roll) +2 DEX -2 Myrmidon".
- **Spellarcher's arrow save** — PASS: shot at the Screamer Beetle (`pointer.py attack`, a click on
  its figure 10 px above the feet: Tab + Return walks an archer up and punches, the bow unused with a
  foe beside it): "Halton attacks Screamer Beetle with Wooden Bow (1d8) ... HIT" / "Shocking Grasp
  damage: 1d8 = [3] +2 = 5" / "**Screamer Beetle's saving throw vs Shocking Grasp from Halton
  (spell)**: d20 = 11, needs 16 (25% to save) -> failed: full damage, 5". Then Shocking Grasp cast
  by hand at a Slig (its touch attack missed, so no save line either way); the spell records' save
  bytes after it: Burning Hands 0xA1, Chill Touch 0xA1, **Shocking Grasp 0xA0, Vampiric Touch 0xA0**
  (no save, as the game has them: ARROW_SAVE cleared the bit for the hand cast).

## Part 6: a bug found, fixed and checked — the Myrmidon's polearm lost in the roster

- Swat, re-added from the roster in a later session (ADD), had weapon specs **long sword only**,
  and none of the Loader's gear (the polearm, the sling): the game writes a new character to the
  roster at DONE, and the Loader's changes (`weaponchoice.kinds_for`, `kit_gear`, `startgear`) come
  after, in memory only. Picks made on the weapon window survive (DSCLOG writes them during DONE).
- Fix: DSCLOG's new **MYRM_POLEARM**, from CR_WEAPONS right after the weapon window, puts the
  polearm in a new Myrmidon's second weapon spec slot (test: `test_myrmidon_polearm`).
- Checked on the new build (buildcheck: myrm_polearm, cr_weapons the same): a Myrmidon made (the
  bow picked) had "bow, polearm"; DOSBox restarted, the character ADDed from the roster: **"bow,
  polearm"** kept.
- Still open then (older than this branch, every kit and class): the Loader's creation gear (a
  Myrmidon's polearm item, the bow and arrows of a bow spec, fuller starting gear, a Spellarcher's
  armour left behind...) isn't in the roster's copy; a character added again later has the game's
  own gear. Fixed in part 7.

## Part 7: the Loader's creation gear in the roster's copy

- Timed with `gearpoll.py` from DONE: GEAR_DUE set, the weapon window (lv_creating), the dice log's
  gear lines and CHARSAVE.GFF's write. Three causes found, one after another:
  1. `GEAR_WAIT` (VIEW CHARACTER's) cleared GEAR_DUE whenever STATS weren't fresh, and on the
     creation screen they never are: `GEAR_HOLD` (new, before the roster write) then waited for
     nothing. Both now test the Loader's heartbeat (+1865, the stats thread's, every 0.25 s; age 1-5
     ticks seen), and GEAR_WAIT leaves GEAR_DUE set on its timeout.
  2. The Loader cleared GEAR_DUE in a pass while the weapon window was up, giving nothing (the gear
     waits for the specs). Now it leaves it set until the window is gone.
  3. A plain fighter (Holdfast, slot 1) still got nothing: its creature reads **Okay**, not New, all
     through DONE, and the Loader's gear steps take only New ones (an earlier Swashbuckler in slot 3
     got its gear only because that slot's record was left New). DSCLOG now names the character
     (`GEAR_WHO`, +1867, its sheet index) and `game.being_new` counts it.
- Gripsure (human fighter, slot 1, short sword picked): gear_due at 10.41 s, "starts with a plain
  bone short sword" and "more gear: Sling" at 10.51 s, CHARSAVE.GFF written at 30.09 s (after the
  four powers). DOSBox restarted, ADDed: Bone Short Sword in hand, Leather Sling, the leather
  armour and shield. **PASS.**
- Bowtest (human fighter, slot 2, bow picked), Gripsure in slot 1: gear at 10.47 s, written at
  20.79 s; Gripsure (Okay, ADDed) untouched. Restarted, ADDed: Wooden Bow, Wooden Arrows, Bone
  Short Sword, armour and shield. **PASS.**

## Summary

| Kit | What was checked | Result |
|---|---|---|
| Myrmidon | one pick, polearm greyed, bow lit; polearm spec and item; -2 initiative; roster copy (after the fix) | PASS |
| Seeker (fire) | bow greyed, obsidian kinds lit; bow to the backpack | PASS |
| Scholar | 9 spells at creation (7 + 2); no slot more; THAC0 21; Chill Touch and Acid Arrow at its THAC0 | PASS |
| Healer | no harming spells; Cell Adjustment +1 | PASS |
| Lifebinder | no harming spells; Cell Adjustment +1d4 | PASS |
| Twin-blade | cahulaks offered and allowed | PASS |
| Brute | cahulaks greyed; +2 with the great axe | PASS |
| Swashbuckler | long sword, dagger, short sword only; bad luck on its rolls (-7, -14) | PASS |
| Wayfinder | +2 its own, +1 the party | PASS |
| Sentinel | AC +2 with a shield; no initiative; -1 without a shield | PASS |
| Wild Fury | CON - 4 check; -3 / +3 / 1 more attack / AC 3 worse | PASS |
| Spellarcher | bow only; armour left behind; arrow made; save against its Shocking Grasp arrow | PASS |
| (any) | the Loader's creation gear in the roster's copy, ADDed after a restart (part 7) | PASS |

Not played: the Justifier (its bow's expertise), the Crusader and Mind Warrior (extra attacks at
7th level), a non-fire Seeker's bow on the weapon window, the Assassin's and Shinobi's light armour
asleep after a change of class, the Swashbuckler's bad luck on one of the game's own rolls (a lock),
the Twin-blade's cahulaks with no penalty in a fight; the emulator tests cover them.
