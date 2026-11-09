# Changelog

What changed in Obsidian Edition (called Templar's Ledger up to 1.2.0), pull
request by pull request, newest first: the record for developers and testers.
For what a release brings, read its notes, in [`release-notes`](release-notes);
for every change from the original game in one page, [the patch
notes](PATCH-NOTES.md).

A note on DSCLOG's sizes: up to #84 the figure called its "image" may be the file's, DSCLOG.EXE
(#83's 63,680 and #84's 64,320 are the files' sizes; the image is the file less its 32-byte
header), and the spare room beside it, up to #85, is counted from that figure. #85 names the
file's size as such; from #86 on, both are given.

Releases before 2.12.2 give the release's line as a **Release** bullet; from 2.12.2 on it is the
entry's first line.

Releases, newest first: [2.14.1](#pull-request-88-merged-2026-11-08) (#88),
[2.14.0](#pull-request-87-merged-2026-11-07) (#86 and #87),
[2.13.4](#pull-request-85-merged-2026-11-02) (#85),
[2.13.3](#pull-request-84-merged-2026-10-31) (#84), [2.13.2](#pull-request-83-merged-2026-10-30)
(#83), [2.13.1](#pull-request-82-merged-2026-10-30) (#82),
[2.13.0](#pull-request-81-merged-2026-10-30) (#81), [2.12.5](#pull-request-80-merged-2026-10-30)
(#80), [2.12.4](#pull-request-79-merged-2026-10-29) (#79),
[2.12.3](#pull-request-76-merged-2026-10-29) (#76), [2.12.2](#pull-request-75-merged-2026-10-29)
(#75), [2.12.1](#pull-request-74-merged-2026-10-27) (#74),
[2.12.0](#pull-request-73-merged-2026-10-27) (#73), [2.11.0](#pull-request-69-merged-2026-10-26)
(#69), [2.10.0](#pull-request-67-merged-2026-10-26) (#67),
[2.9.0](#pull-request-63-merged-2026-10-26) (#63), [2.8.0](#pull-request-61-merged-2026-10-25)
(#61), [2.7.2](#pull-request-59-merged-2026-10-24) (#59),
[2.7.1](#pull-request-58-merged-2026-10-23) (#58), [2.7.0](#pull-request-56-merged-2026-10-23)
(#56), [2.6.0](#pull-request-54-merged-2026-10-21) (#54),
[2.5.0](#pull-request-51-merged-2026-10-19) (#51), [2.4.0](#pull-request-50-merged-2026-10-16)
(#50), [2.3.0](#pull-request-47-merged-2026-10-15) (#47),
[2.2.1](#pull-request-43-merged-2026-10-14) (#43), [2.2.0](#pull-request-42-merged-2026-10-14)
(#42), [2.1.1](#pull-request-37-merged-2026-10-10) (#37),
[2.1.0](#pull-request-36-merged-2026-10-09) (#36), [2.0.0](#pull-request-33-merged-2026-10-09)
(#33), [1.2.0](#pull-request-30-merged-2026-10-08) (#30),
[1.1.0](#pull-request-18-merged-2026-10-06) (#18), [1.0.0](#pull-request-12-merged-2026-10-02)
(#12).

## Next pull request (not opened yet)

DSCLOG.EXE 66,752 bytes (image 66,720), 1,728 of its segment spare.

**Fixed**
- **Graphics disappearing in a busy area** (SSI's technical note 2712 for Wake of the Ravager, the
  same engine): the game's picture cache (DSUN.EXE 25FA6h) has 300 slots for every wall, door,
  figure and item picture drawn and gives none back until an area loads, so past 300 a new picture
  had no slot and wasn't drawn. DSCLOG's PIC_REUSE (sites 26009h, 260CCh, 2612Bh; always on): with
  all taken, a slot out of memory that no wall (DS:574Eh) and no map thing (+0Fh) names is reused,
  the Loader's STALE ones first, searching round from after the last reused (the inventory's icons,
  let go once drawn, took one slot in turn otherwise: 3,590 reuses in a cycle); its picture goes in
  the first gap of the store it fits, else past the furthest end. The pens hold 203 slots on
  arrival and walking adds none. Seen in DOSBox: 145 items of different kinds dropped in the pens,
  300 slots at the 9th dozen, then 18 reused, the store's end unchanged, every thing with its own
  picture, the inventory, a walk away and back all as before
  (playtest/logs/2026-11-09-picture-slot-reuse.md).

**Changed**
- **New rule: cahulaks as Dark Sun's rules have them** (Options, Weapons and armour; on by default;
  `RULE_CAHULAKS`, DSCLOG's RULE_HI_CAHULAKS and CAHULAKS): a head in each hand, the off head's one
  attack more a round (CAH_MORE in OFF_HAND_HALVES: the attack and the DAM lines) under AD&D's
  two-weapon penalties whatever that rule (CAH_TWO at 59627h, PROBE_TWO's CAH_ADJUST: -2 the main
  head's swings, CAH_SWING at 589B6h: -4 the off head's, the round's last; DEX's reaction adjustment
  added, no better than 0); a hit that does damage tangles a man-sized or smaller target failing a
  save against petrification (its sheet's +39h, a d20): it loses its next turn, as Whirlwind's sweep
  (CAH_HIT at 58B54h). Not half-giants, nor the Large and shapeless by name (cahulaks.py's BIG, a bit
  a combatant in the far block, the header's +1840). The dice log names each head's penalty and the
  tangle's save (KIND_MANUAL 10). Seen in DOSBox: two swings a round at 14+ and 16+ for Lex at DEX
  10, the tangle's saves made and failed, a tangled Templar's next turn gone
  (playtest/logs/2026-11-09-cahulaks.md).
- **The creatures' table** (obsidian-edition/CREATURES.md, made by `dsloader.doccreatures` from the
  game's data): every creature the game defines (189, one a name and race, the default party left
  out), its figure as the game draws it standing (docs/creatures/; the fighting picture's where that
  shows much more: the Bulette and the Silt Horror come up from the ground to fight) and whether the
  cahulaks can tangle it (`cahulaks.why_not`). Also kept from being tangled, the user's call: the
  spiders (Dark Spider, Spider Mage, the "-tunk!" princes), the Sand Howler, Screamer Beetle, Xorn,
  Strine, Daggoran, Magera and Alita (`cahulaks.UNTANGLED`).
- **Cahulaks drawn as a pair**: a short haft and a hooked four-bladed head in each hand (both at
  the hips walking), not one hook in one hand (spritegear's CAHULAKS shape; the left hand given the
  right's). And with half-giants' two-handed weapons in one hand, the cahulaks still take both
  hands (DSCLOG's PROBE_TWO_HANDED by the type's place in the table, TH_CAHULAKS; KIT_FORBIDS and
  restrict.py: a half-giant Twin-blade can't pair them).
- **The move-silently labels say "Silent"**: the inventory screen's thief row reads `SLNT` (it read
  `MOVE`, beside View Character's MOVE, the character's movement), and the item boxes' stealth lines
  `Silent +10` (boots) and `Silent 95%` (the Boots of Elvenkind) for `Move +10` and `Move 95%`: the
  Boots of Speed's box read as if every pair of boots added movement (the user's catch). DSCLOG's
  L_MOVE, IB_QUIET and IB_ELF_QUIET; its sizes unchanged. docs/gear-boxes.png and docs/elvenkind.png
  retaken. Seen in DOSBox: playtest/logs/2026-11-09-silent-labels.md.
- **The mod's magic gear with no plus or power glows on the figures**: the Boots of Speed, the
  Cloak and Boots of Elvenkind, the Girdles of Back Defense and of Urnst (and the Amulet of Magic
  Resistance, should a figure ever show the neck), by type (`sprites.MAGIC_TYPES`): the glow had
  gone by a plus or a power only.
- **New: the Boots of Speed** (the DMG's; the user's item), worn on the feet by anyone: in a fight the
  wearer's movement doubled and AC 2 better while it can move (not Stuck, Paralyzed or Slowed);
  nothing out of a fight. DSCLOG's type SPEED_BOOTS (the 31st extra type, the game's Boots'), name
  170h, BOOTS_MOVE (PROBE_MOVE) and BOOTS_AC (PROBE_AC); a red icon. Dagger, chief of the White Sand
  Outlaws, wears them; Hototo, their other chief, carries the Gythka +3 (its 1000th-trip gift kept).
  Seen in DOSBox: movement 240 for 120, foes' shots at AC 0 for her 2 (playtest/logs/2026-11-09-boots-of-speed.md).
- **People the party fights who had nothing to fight with** (they struck with their fists), with
  the new mundane items on (`worldgear.fighters`): Seref's Drajian Guards (213) and the slave
  village's (195) the armed Drajian Guard's kit; the Lower Castle's unarmed Guard (281) the other
  Guards'; Arant's lazy guard (267) his guards'; the White Sand Outlaws (Slave Hunters 199 and 201,
  Hototo and Dagger, script 133: "swords readied") a bone long sword and leather, the chiefs leather
  arm armour too; the final battle's Psionicist (257) a stone dagger; the arena's Tohr-kreen (292),
  whose picture holds a gythka in every frame, a bone gythka. (Thri-kreen fight with their claws, as
  their pictures show; Jake and Mow are Dagolar's guises; Egrus is dead.)
- **The game's Polearm +1 in play:** the game defines it (object 1577) but never places or gives it
  (no script names it, not even by the negative number a create takes, and nothing holds one).
  Seref, the Draj agent at the Elven Caravan, where the cluebook puts it, carries it, with the new
  items on (`worldgear.MAGIC`): his object (203), which his encounter on the road copies too.
- **Item boxes show a weaker material's to-hit** under a plain weapon's damage: `Hit -3` wood,
  `Hit -1` bone, `Hit -2` stone and obsidian, as the game's attack takes it (the damage line already
  had the material's damage off). Not with a plus, nor for the game's exempt weapons (clubs, staves,
  the chatkcha: type +08h 80h), nor metal (DSCLOG's IB_MATERIAL, always on). Seen in DOSBox:
  playtest/logs/2026-11-09-hit-line.md. The box puts its text below the picture, so a weapon
  picture taller than 16 pixels (the polearms', staves', gythkas', a stone pick's, the cahulaks',
  the striker's, up to 36; the Long Sword's is 15) put the last row at the box's edge: the box alone
  now draws a copy 16 at most (`icons.BOX_TALL`, `BOX_SMALL`; DSCLOG's BOX_PICS, always on), the
  inventory and the ground keeping the game's own picture (the Polearm's too, which the Loader had
  drawn 22 everywhere; the weapon specs' picker keeps its 22).
- **Spells and psionics as the manual describes them** (a new rule change, on by default, from the
  next start: `spells_manual`, `gamepatch.SPELLS_MANUAL`; the spell records and DSCLOG sites; from
  reports/spells-against-the-manual.md, which now says what was done with each of its points):
  - *The records:* Bestow Curse and Blood Flow allow a save; a save negates Flaming Sphere; Solid
    Fog 1d3 rounds + 1 a level (was until removed); Minor Spell Turning 3 rounds a level (was one
    spell, never ending), turning every 1st- to 3rd-level spell for its whole time; Cause Fear 1d4
    rounds (was 1 a level); Quicksand no save; Turn Pebble to Boulder 3d6+8 (was 6d6); Ironskin a
    blow a caster level (its charges and its level divisor 1; was 1d6). Left as they were, after a
    DOSBox run: Magical Stone (the game already throws three stones of 1d4: the report's "one" was
    wrong, and a record of 3d4 made each stone 3d4) and Quicksand's time (its Stuck is a round at a
    time, put on again while the quicksand's own 5d3 rounds last, so the record's time changes
    nothing). Seen in DOSBox: playtest/logs/2026-11-08-manual-spells.md.
  - **Stinking Cloud** 1d4+1 rounds (was 1d6: the record's dice 1d4, and DSCLOG's STINK_SITE adds
    the round, which the record can't); **Chaos** lets a creature of INT 21+ or 4 or less save as
    well as warriors (CHAOS_SITE, at the save modifiers' 79F80h); **Free Action** also frees the
    Stuck (Web, Solid Fog, Quicksand, Entangle, Grease): its handler, shared with Remove Paralysis
    and Protection from Paralysis, made a loop over the effects to remove through its own two far
    calls (a Poisoned creature still stays Paralyzed, as the game has it). FEATURES lists what is
    left as it is and why (Protection from Normal Missiles, Deflection and Inertial Barrier: one
    effect; Confusion's and Chaos's one save; Mirror Image's images until struck). Tests:
    `test_manual_spells`.
  - **Hold Undead** holds only undead of the caster's level or lower (HOLD_HD_SITE, 7A345h);
    **Color Spray** gives no save to creatures of the caster's level or lower (SPRAY_SITE, 79F83h);
    and for saving throws a monster with no class counts its hit dice as its level (HD_SAVE_SITE,
    79D8Ch: the game's level routine gives such a creature 0, so a 14-HD Rampager was Scared like a
    1st-level one, and Dismissal was easy on elementals and slaadi). Seen in DOSBox
    (playtest/logs/2026-11-08-hd-spells.md).
  - **Minute Meteors: five globes of 1d4, each rolling to hit at +2** with spells that roll to hit
    (the record's repeat count 5, as Magical Stone's 3; was one roll of 1d4 a caster level).
    **Flame Arrow: a bolt for every 5 caster levels, 5d6 each** (DSCLOG's FLAME_SITE on the cast's
    repeat count; was one sum of 5d6, 10d6 at 10th); no attack roll, as the manual and AD&D. Only
    the party's casts repeat: a monster's Magical Stone, Minute Meteors or Flame Arrow lands once
    (the game's other casting routes ignore the count).
  - **Turn Undead the AD&D way** (DSCLOG's TURN_SITE at 7AE01h): AD&D 2e's turning table by the
    undead's hit dice (rows: 1, 2, 3-4, 5, 6 ... 11+) and the priest's level (columns 1-9, 10-11,
    12-13, 14+), where the game's formula put 2- and 3-HD undead a row easier and 5 HD a row harder;
    a turn (the number made, or T) makes the undead flee, Afraid for 3d4 rounds (the game had no
    fleeing: every success destroyed); D destroys, D* destroys and up to 2d4 more of its kind
    reached by the same turning; "---" no chance. A priest who fails against an undead can't try it
    again that fight (another priest can). The dice log says which (`turned: flees 3d4 = 9
    rounds`, `destroyed automatically (D*)`, `can't try again`). Seen in DOSBox with Minute
    Meteors and Flame Arrow: playtest/logs/2026-11-09-turn-undead-meteors.md.
  - Fire Shield +2 on saves vs fire and cold (its description says so); Blur +1 on saves; Chill
    Touch's Weakened lasts (an hour: its record gave it 0 rounds) and undead touched take no damage
    and flee 1d4 rounds; Cloudkill kills under 4 HD with no save and those of 4-5 HD that fail, 6+
    HD take its damage; Feeblemind (INT and WIS 3, as the game already did) stops psionics and Heal
    cures it; Lower Resistance takes 30% + 1% a caster level off magic resistance (was halving it);
    Strength's die by class (warriors 1d8, priests, rogues and psionicists 1d6, wizards 1d4) and the
    mod's Cat's Grace's (rogues 1d8, wizards, warriors and psionicists 1d6, priests 1d4), the best
    die for a multiclass character, at most 24, neither stacking with Adrenalin Control; Rainbow
    Pattern a round a caster level, ended by damage on the creature it holds; Cell Adjustment heals
    1d4 (and cures disease, as before); Biofeedback's -2 leaves a blow at least 1. Each seen in
    DOSBox: playtest/logs/2026-11-09-group-3.md.
  - **Monsters as the manual describes them:** Shadows and Greater Shadows drain 1 STR a hit (no
    save, for 2d4 turns, stacking) in place of their cold damage and paralysis, and both are
    unaffected by cold; the Babau's and Blue Slaad's deadly poison (save or die) in place of the
    corroding touch and disease; the Tari a 3-HD bite of 1d3 with a 1-in-20 chance of disease; the
    Styr a 3d6 fire breath, +1 weapons to hurt it, HD 14 and THAC0 7; the Djinn turns invisible and
    makes mirror images at its first turn (the manual promises it no magic resistance). Seen in
    DOSBox: playtest/logs/2026-11-09-group-4.md.
- **Spells roll to hit** (a new rule change, on by default, from the next start: `spell_to_hit`,
  `gamepatch.SPELL_TO_HIT`): the missile spells (Acid Arrow, Turn Pebble to Boulder, Magical Stone,
  Condense, each of Minute Meteors' globes at +2; the Strine's spines) roll a d20 against the
  target's AC with the caster's THAC0 (Acid Arrow a fighter's of the caster's level) and the game's
  own to-hit adjustments (DEX), and the hostile touch spells (Chill Touch, Shocking Grasp, Vampiric
  Touch, Cause Light, Serious and Critical Wounds, Cause Disease, Poison) with STR, at a creature of
  another side; 20 always hits, 1 always misses. A miss does nothing (no damage, no burn, no
  effect): "Miss" floats over the target and the dice log says `-> MISS: the spell does nothing,
  the 2 damage rolled lost`. Each of Magical Stone's three throws rolls on its own. Spells carried
  by a weapon's hit (spell arrows) don't roll again; Magic Missile and the areas are untouched.
  DSCLOG's SPELL_HIT_SITE (7A15Ah, armed by CAST_SITE) and SPELL_STUB_SITE (the always-hit stub,
  78BA3h). Seen in DOSBox (playtest/logs/2026-11-08-spell-to-hit.md). Tests: `test_spell_to_hit`
  (dsclog, gamepatch, dicelog).
- **Resting heals by spells and natural healing** (a new rule change, `rest_heal`, on by default):
  before the rest each priest spends the slots left on Neutralize Poison for the Poisoned, Cure
  Blindness, Cure Disease (when no cleric or druid of 5th+ casts it free), and the Cure Wounds
  spells or Heal on the most wounded, and psionicists use Cell Adjustment, each through the game's
  own cast (`At rest: Cilla casts Cure Critical Wounds on Gerakis (5th-level slots: 8 left)`); then
  each heals 3 HP and CON's hit-point bonus (`Gerakis rests 8 hours: +3, +6 (CON 22) = +9`) instead
  of all of them, CON 20+ regeneration coming on top for the 8 hours.
- **Dual-classing as the manual has it** (a new rule change, `dual_class`, on by default): at 3rd
  level of the old class, and every prime requisite checked (the old class's at 15+, the new one's
  at 17+; the game checked one, WIS for rangers, druids and psionicists). Seen in DOSBox with
  resting and the monsters: playtest/logs/2026-11-09-group-4.md.
- **Turn Undead in the dice log:** `Seneca turns Guard: d20 = 11, needs 7+ (priest level 3 vs 2 HD)
  -> destroyed` / `-> not turned`, and `Zombie is destroyed by Turn Undead` in place of its HP line;
  the floating name over the cleric says "Turn Undead" (was "special attack 190"). Turn Undead is
  the clerics' button on the USE screen (spell 190, no slot): it tries each undead in its area, one
  at a time, each with a d20 of its own against 10 + 3 x (its row - the level's), and a success
  destroys it (the game has no fleeing: a failure calls an empty routine); seen in DOSBox: no limit
  of uses, the same undead can be tried again (HOW-THE-GAME-WORKS's new Turn Undead section,
  against AD&D's table; playtest/logs/2026-11-08-turn-undead.md). With the manual's spells, the
  record carries the priest's and the undead's creatures, so a turning out of a fight, which starts
  one and numbers the combatants afresh before the Loader reads it, names them (it said "?").
- **A fight's summary as it ends** (mock-up G's): `Fight over: 2 rounds, 1 kill; the party dealt 28
  damage and took 6`, then each member's attacks hit, damage dealt, kills and damage taken, written
  once the game's fight flag has been down 2 seconds (each arena wave gets its own). A kill goes to
  whoever hurt the creature last, a spell's damage to its caster (named by the cast's record, so
  Magic Missile's too; only a party member's spells count for the party). The readable layout shows it as the fight's close, its members' lines always shown.
  (`fighttally.py`; tests: `test_fighttally`, `test_ledger`.)
- **The dice log window has a readable layout** (mock-up G of the combat log research, on by
  default, **Readable layout** to switch back; `dsloader/ledger.py`). Each event is a line with its
  outcome first (`● Seneca hits Arena Guard for 11 — backstab, Bone Hayneedle +1`), the HP it left
  and the roll in columns at the right, and the working under it, smaller and dim: the to-hit sum
  with the AC it would have hit, the damage dice, the save's line in full, each initiative score.
  Pips for whose line it is, a rule for each round, `▸` for each turn; the outcome coloured by the
  party's view of it (sky blue good, coral bad, dim for misses and monsters' saves, gold for kills;
  each at 4.5:1 or more on the log). A hit's damage and the HP left are filled into its line as their
  own lines arrive. The log's own lines are kept: Save..., the crash and freeze reports and the
  layout switched off use them. (Tests: `test_ledger`.)
- **The combat log panel's lines are in a smaller font,** 7 pixels a line where the game's is 9: 8
  lines docked (was 6), 14 expanded (was 11). The glyphs are the X11 misc-fixed 4x6 font's (public
  domain) with the game's drop shadow (`smallfont.py`); the header, buttons and filters keep the
  game's font. The panel's pictures retaken in DOSBox with the final build (`docs/combat-log.png`,
  `combat-log-expanded.png` and `combat-log-live.gif`, in Pehtucl's ambush, at Short).
- **The panel's Short level reads as the readable layout does:** what happened first, the roll in
  brackets after it, the damage on the attack's line (`Seneca hits Slig for 11 (15 vs 4+, backstab)`,
  `Guard misses Lex (6 vs 13+)`, `Slig fails vs Fireball (11 vs 16+)`, `Rampager fails to resist
  Fireball (MR 25%: 28)`, `Cilla hides in shadows: seen (85 vs 25 or less)`); was `Rampager attacks
  Defiler: 20 vs 16+ HIT, 4 damage (2d6)`. (`combatlog.shorten`, `Log.at`.)
- **Steady pace keeps the game's real schedule,** and the choppy walking is gone. The game moves
  everything on the map a step at each tick of its clock (96 a second: its timer sets DS:1F7Eh,
  and the step runs only with it set), so a tick that passes while a picture is drawn is a step
  lost. Steady pace assumed 70 pictures a second instead, while the map draws only when something
  moved (about 17 a second), so it found every picture late and left most of them out: 6 shown a
  second at 20,000 cycles. Now it counts the steps lost (the clock's ticks less the steps run)
  against an allowance of 1.5 ticks a picture, about what the unmodded game's own pictures lose,
  and leaves a picture out only while more are lost. (DSCLOG's STEADY PACE; tests:
  `SteadyPaceTests`. `playtest/framerate.py` reports the steps run and lost and the walking speed
  while walking: its speed had counted the waits between clicks.) The figures, with the cheaper
  drawing below, are under it.
- **The helper draws shadows, dust and see-through figures for less.** Shadows are worked out only
  for figures whose shadow can reach the part of the view being drawn, rows outside it stepped over;
  the shadow cache remembers each figure's slot; spans and see-through pixels are looked up with
  XLAT; the lean comes from a table, not a division; the dust's thickness table is built once (in
  the far block); the combat log panel is put back only when the redrawn rectangle overlaps it; dust
  settling after a walk redraws only its rectangle; the floating names' timer code returns at once
  with none shown. A floor pass takes 32% fewer instructions with everything on (39% with shadows
  only), see-through figures 12% fewer, every screen byte-identical (`tests/test_dsclog_drawing.py`,
  9 tests, against the old build's screens). In DOSBox, the whole party walking in the slave pens,
  everything on, with the new steady pace: 20,000 cycles with steady pace on, 15.5 pictures a second
  and walking 112 map units a second (was 10.2); off, 18.9 pictures (was 16.8) and 103 map units
  (was 80); 35,000 cycles, steady pace on, 18.9 pictures and 141 (was 16.0 and 113)
  (playtest/logs/2026-11-08-drawing-savings.md).
- **Fastest (35,000 cycles) is the default game speed** (was Faster, 20,000). With the cheaper
  drawing it shows about all the pictures the game draws while the whole party walks (18.9 a
  second) and walks fastest (141 map units a second, against 112 at 20,000), for about 30% of a
  core in DOSBox. A speed already chosen is kept; Faster stays for older computers.
- **The helper's room** (DEVELOPMENT.md's budget, corrected with each step): the cheaper drawing
  made the helper 944 bytes bigger (448 bytes left in its 64 KB segment) and its far block 2 KB. A
  first memory pass freed 3,136 bytes of the segment (448 -> 3,584 spare) and 190 paragraphs of
  upper memory (the helper with its PSP 65,248 -> 62,208 bytes; the largest free piece 34,320 ->
  37,392): the colour, ring and dust-walked tables moved to the far block (FAR_DAC, FAR_RING_TAB,
  FAR_RED, FAR_WALKED: the header fields now offsets there, the Loader reading them at far_seg);
  the AD&D XP table stored in fiftieths; the 134 vector installs made a table and a loop; the extra
  names packed (playtest/logs/2026-11-08-memory-pass.md). The new rules then took it to 2,032
  spare, and a second pass freed 4,000 (6,032 spare; upper memory 565 paragraphs spare, was 495):
  the sites' dispatch a jump table (688 bytes); the rings' outlines kept as one quarter and
  mirrored (336); a new tail section after the image, kept with the helper and found through header
  +1834 (`tail_seg`), holding the floating names' slots, the extra item names and types and the
  timer notes (the Loader's labels.py and freeze.py read them there); the dust's LIGHT, puffs and
  DARK in the far block; the crash report writing the stack straight from SS
  (playtest/logs/2026-11-09-memory-pass-2.md). Each pass checked in DOSBox (shadows, dust,
  see-through, the ring, the panel's colours, labels, to-hit, Turn Undead, item names and types,
  next-level XP, the Effects screen, Look, creation, a shop). With the manual's spells, the
  monsters, resting and dual-classing, and the audit's fixes (their per-fight tables moved to the
  far block), the helper ends the pull request with 2,736 bytes of its segment spare, 102 bytes
  free in the far block (the HMA) and 357 paragraphs of upper memory spare.
- The helper counts the game's page flips (`flip_count`, header +1832), for a frame rate:
  `playtest/framerate.py` reads it beside steady pace's frames left undrawn.

**Fixed: the game**
- **Alagorn told two items wrong** (script 212 and the Loader's copies of it): the Quicksilver Glove
  as "Quicksilver Gauntlets" that graft a weapon to the hand (it casts Detonate on every hit), the
  Helm of Contemplation as a shield against psionic attacks (it is Gaze Reflection). His menus name
  the glove as the game does, and the two stories say what they do (`alagorn.retold`: the old lines
  jumped over, the new run from after the script's end; always).
- **The Quicksilver Glove fought as a wooden weapon** (-3 to hit, -2 damage): its type has no
  material (40h, a ring's), and the game's to-hit and damage (DSUN.EXE 5EB49h, 5EBC1h) read only the
  low nibble, 0, wood. Its type made leather, as the Chameleon Gloves' (DSCLOG's PROBE_TYPES_FILL,
  as the Great Axe +3's metal): "Leather Quicksilver Glove", 1D6+2 (playtest/logs/2026-11-09-hit-line.md).
- **Scare allowed no saving throw at all,** so the 2.14.0 fix (`scare_elves`: an elf or half-elf
  priest's save) never ran, nor the game's own rule that 6th level and up always save: its record's
  save byte (+1Fh) had "a save allowed" clear, and the saving throw (79A71h) stops at that test.
  Seen in DOSBox: Scare on Merzol, a 7th-level fighter, and a 3rd-level gladiator, no save rolled
  for either (the caster, inside the area, Scared too). The bit set (`scare_save`, 4222Fh A0h ->
  A1h): 6th level and up save, below 6th no one can, but an elf or half-elf priest
  (playtest/logs/2026-11-08-scare-no-save.md; found in the manual's review:
  reports/spells-against-the-manual.md).
- **"Can't save" saved:** the game compared a save's total with the number needed unsigned, so
  every -100 (Chaos, Cloudkill, Scare under 6th level, Color Spray with the manual's spells) wrapped
  round and the creature saved (seen in DOSBox: Arena Guards "unable to save" took half Cloudkill's
  damage, a Guard against Scare was never Afraid). The compare made signed (`save_signed`, 79BBDh
  `jae` -> `jge`), always on whatever the Options: -100 fails, even on a natural 20 (the game took
  a natural 20 as saved before adding the modifiers, 79B5Fh: `save_natural` goes on with them, and
  DSCLOG's SAVE_SUM makes a natural 20 a save unless the total is the -100's; the sum is also kept
  in its byte, so a doubled 19 or 20 with Scare's +100 no longer wraps round to a failure).
- **Resting while poisoned killed a member just cured:** the rest read each member's effects
  before casting its free cures and never again, so a 7th-level druid's Neutralize Poison was cast
  and the member died of the poison anyway (seen in DOSBox: playtest/logs/2026-11-09-rest-poison.md).
  The cures now come before the read (`rest_cures_first`, `rest_cures_loop`: the game's own bytes
  reordered; always on).
- **Pehtucl's ambush brought every guard in the pens:** his script (GPL 145) made its five guards
  at the fountain, then sent the whole kind, -90 and -293, hunting: up to ten more Arena Guards and
  Guards from across the map (a player's save). Now each of the five is made alone and given the
  hunt, the no-orders handler and the sight trigger itself (local big number 40, as the game's own
  scripts give a creature just made its orders), Pehtucl his by kind (he is the only -37). And the
  fountain's yell-masking zone (GPL 137 at FB5h, the fountain's room) takes in the passage before it,
  where the party stands as he turns (x 42-80, y over 90): a fight there set off the alarm.
  (`scriptfixes.py`, two repairs. Tests: `test_scriptfixes`. Seen in DOSBox with the player's save:
  the five made on squares of their own, the fight theirs and Pehtucl's; with the game's script a
  guard 55 squares off set out at once, with the fix none: playtest/logs/2026-11-08-fountain-needle.md.)
- **An arrow or sling stone was from behind by the target's facing, at any distance** (+2, the
  target's DEX and shield lost: a ranger's three arrows from across a room, a player's log), melee's
  rule. A missile is now from behind only as a hidden archer's shot (the stealth rule), and the
  dice log says "unseen" for it. (DSCLOG's `MISSILE_REAR`, first in `PROBE_STEALTH`; `st_now`.
  Tests: `test_missile_from_behind_only_unseen`, `test_unseen_shot`.)
- **A thief's later attacks in a round could still backstab:** with **A backstab multiplies the
  weapon's dice only**, only the round's first attack is meant to be a backstab, but the count it
  read (`[BP-14h]`) leaves the off-hand swing out, so a thief with two weapons and a weapon spec's
  extra attack whose first swing missed had the third, the off-hand one, multiplied (a player's
  log: "Seneca hits Merzol ... +3 backstab (the dice 3 x2 = 6)"), and every swing after the first
  had the backstab's +2 to hit. Each party member's attack now keeps the game's clock (it moves a
  round at a time in a fight); a later attack in the same round is no backstab, its +2 taken back,
  from behind as the game has it. (DSCLOG's `STAB_FIRST`, in `PROBE_STEALTH`. Test:
  `test_backstab_first_attack_only`.)
- **VIEW CHARACTER showed a new character's gear from before the Loader's** (a Poisoner's bone long
  sword where it had a bow and daggers, its DAM line the sword's) until another member was chosen
  and this one again: the Loader gives new characters their gear after the game has made the
  character, and the screen, drawn once, never knew. At DONE the helper raises `gear_due`; the
  Loader's next pass (tens of milliseconds, not the 3 seconds of its usual round) gives the gear
  and says whose items it changed (`gear_given`); VIEW CHARACTER's probe waits for it (at most a
  second, and only with the Loader there) and has the game's own routine draw the screen again
  before it is shown. (`GEAR_WAIT` in `PROBE_VIEW`, the routine at 89E70h, its overlay's start:
  stub 431Fh:3Eh; header +1830, +1831; `DiceLog._gear_due`. Tests: `test_gear_due`. Seen in
  DOSBox: a new fighter given a bow for its weapon spec showed the bow and "DAM 1x1D6+0" at once.)
- **In the helper's drawing:** a walker raised a dust puff on nearly every pass, not one per 6
  pixels walked (AX overwritten before the add), so there is less dust now, as designed; walkers off
  the view raised dust and widened the redrawn area; the whole view could be drawn twice in one pass
  (the panel's tick, then the labels'); a dark area retried its shadow tables on every pass (now
  every 9 BIOS ticks); rings alone widened the redrawn rectangles by the shadows' 72/44 (now 16/8).
- **Turn Undead's once a creature, Whirlwind's lost turn and the Djinn's first-turn tricks
  worked only for the first 64 creatures on the map:** their per-fight tables (TU_FAILED, SWEPT,
  DJ_DONE) had a bit for each of 64 combatants; they now cover every one up to MAP_COUNT (520), in
  the far block (FAR_TU, FAR_SWEPT, FAR_DJ). (Tests: Turn Undead, Whirlwind and the Djinn at
  combatants 64, 300, 519 and 520; seen in DOSBox: playtest/logs/2026-11-09-audit-fixes.md.)
- **The mod's two sounds were hard to hear** (hiding in a fight, a picked pocket): saved at 55%
  and 70% of full scale, and at the lowest priority, so a hide during a fight sound was skipped.
  Now as loud as the game's typical clip (`sound-data/make.py`: full scale, the hide sound 3 dB more
  through a soft limiter) and at priority 10, the game's fight sounds' highest (DSCLOG's
  `mod_desc`). Heard in DOSBox: peaks as the game's (playtest/logs/2026-11-09-sounds-louder.md).

**Fixed: the Loader**
- **Figures vanished from the map after many gear changes in one area:** each time a member's
  outfit changed, the Loader took the old pictures out of the game's picture table, but the game
  takes neither a slot nor its room in its picture store (a fixed 741,376 bytes) back until an area
  loads, and a new outfit takes a new slot at the end. After some 30 to 60 changes in one area a
  picture went past the store's end: the game's write fails unseen, the picture can't be read
  back, and its failed reads keep taking memory, until the party's and the monsters' figures
  weren't drawn (opening the inventory brought them back for a while). Now a figure dressed anew
  takes no new slot at all: the Loader puts its pictures into cells the game's store already has
  (one holding the very picture, an outfit changed back; the figure's own, out of memory; else the
  smallest unused cell with room), writing the store (the game's XMS block, found and checked
  against pictures in memory) while DOSBox is paused and never a picture in memory. A picture the
  store has no cell for (and every picture where the store can't be found, as on Dark Sun
  Recompiled) takes a new slot as before, but only while the store and the table keep room for it
  and for the game's own pictures (64 KB and 24 slots); else the figure stays as it was until the
  next area. In DOSBox about 290 outfit changes
  across two areas, a fight and the inventory took 9 new slots (was one each), every figure drawn.
  (`sprites.Store`, `Dresser._in_store`, `sprites._room_for`; tests:
  `test_no_room_in_the_games_store` and 6 more; reproduced and checked in DOSBox:
  playtest/logs/2026-11-09-missing-figures.md, playtest/logs/2026-11-09-picture-store-fix.md.)
- **An item report said a new character's bone long sword "vanished"** ("the game freed it and
  reused the number") when the Loader had made it the bow its weapon spec asks for, in the same
  record. An item made into another where it was (its number still the same member's, the record
  not freed) is no loss. (`itemwatch.changed_in_place`. Test: `test_changed_in_place`.)
- **A needle avoided said nothing:** Pehtucl's chest's needle sprung and the party's best at traps
  rolling clear of it, the game showed nothing, and it read as no trap. The Loader sees that roll
  beside the needle's narration and sets the needle's flag (DISARMED, clear until then); the
  script, after a click, says "The needle is seen in time, and it hurts no one." (No flag of the
  game's 808 was free.) (`DiceLog._needle_check`, `pehtuclchest.script`. Test:
  `test_needle_avoided`. Seen in DOSBox: Seneca's 22 against 52, the line, then the chest opened.)
- **Pehtucl's chest opened anyway in a game from before 2.14.0** ("You must be next to the chest
  ...", then its window): such a game made the game's plain chest as it came to the pens, but gets
  the chest's USE command all the same, and the game opens a plain chest as a USE script ends,
  whatever it said. The Loader now shuts a chest that isn't unlocked, as it makes a shut one a
  chest once it is: locked and trapped as in a new game. (`pehtuclchest.watch`. Test:
  `test_an_older_games_chest_shut`. Seen in DOSBox with a player's save: reproduced, then shut
  within seconds of loading, and it stayed shut.)
- **A Poisoner's poison was put down to another spell** ("Merzol takes 10 from Shocking Grasp"):
  a loss is named after a recent damage roll it matches, whole or halved, and the list kept an
  earlier fight's rolls. A new fight forgets them, and a poison's fixed damage (10 or 30) is its
  own when its save is the latest. (`DiceLog._damage_source`, `_new_fight`. Test:
  `test_poison_damage_named`.)
- The dice log's notes called the "special effect: d10" roll a thri-kreen's bite: it is the
  disease roll, the game's Blue Slaad's (with the manual's monsters the Blue Slaad has deadly
  poison instead, and the roll is the Tari's, made 1 in 20); a thri-kreen's bite from 5th level
  paralyses with no d10.
- **"Can't save" said it saved** with the manual's spells off: the dice log's line for a -100
  ("the game compares unsigned ... -> saved") is gone with `save_signed` always applied; it says
  `none allowed (cannot save) -> failed`.
- **The combat log panel read a spell's attack roll as a plain line:** at Short it is now `Cermak's
  Minute Meteors hits Kalzith for 2 (8 vs 7+)` / `... misses Kalzith (4 vs 7+)`, the damage joined
  to a hit, and at Least `Cermak's Minute Meteors misses Kalzith`, in the hits' and misses' colours;
  Turn Undead's lines are coloured as a hit (turned, destroyed) or a miss (not turned, no chance,
  can't try again), and the hit points a rest or Cell Adjustment gives back in the damage colour,
  in the Loader's log too (`combatlog`). In the readable layout a spell's attack roll is an event
  row, as a weapon's attack is (`ledger`). Seen in DOSBox: playtest/logs/2026-11-09-audit-fixes.md.
- **The fight summary counted a monster's spells as the party's damage,** and any spell whose
  caster it couldn't tell (Magic Missile's, with no save or attack roll naming the caster). A spell's
  damage now counts for the party only when a saving throw against it or its attack roll names a
  party member as its caster (`fighttally`).
- **A game or mod folder whose path has letters outside Windows' code page** gave DOSBox a broken
  configuration; the Loader now stops at start-up with a clear message saying what to move
  (`launch.conf_encoding`; README's troubleshooting).
- The freeze report's dump of the helper's header runs to +373 (UMB_NEED, the overlay buffer's
  place; was to +361, so the fields after it were left out) (`freeze.HEADER_BYTES`).
- **The picture store's room** was measured from the table's last slot, which need not be the one
  furthest in the store since slots are reused; it is now measured from the furthest. And writing
  the store no longer pauses DOSBox a second time while it is already paused (`sprites`; tests in
  `test_sprites`).

**Docs**
- **ITEMS.md checked against the game's data** (every item record, item type, region placement and
  script that hands an item out, with the cluebook): the Helm of Contemplation's power is Gaze
  Reflection, and the Quicksilver Glove's Detonate (both rows had been taken from what Alagorn says
  of them, script 212); where the Draketooth, the Belt of Might and the Orb of Knowledge lie (they
  had "—"), the Mace +2 (a weapon rack), the Bow +2 (a skeleton), the Serpent Boots (a ceramic pot)
  and El's Drinker (Gedron's safe too) are; the Sling +2's chest that isn't; Dag's Dagger's "extra
  damage" that isn't; the Terror Blade's acid chance (its Poison is a power: 95%); 15 kinds of magic
  fruit and 19 spell scrolls; Grey's Scale's arm and leg icons swapped back; and added the Wand of
  Metal Detection, the plain stone pick, the gloves against acid and the missing finds.
- **ITEMS.md: where the script-given items come from** (each from the script that gives it, with the
  cluebook): Dragonsbane from Kraxis' body after the final battle, the Teaquetzl rewards (Swiftbite,
  the Helm of Might, Phrain's Bow), the warrens' sewer holes (Axe +1, the Parting Staff), the Terror
  Blade made in the Wyrm School's bowl, Notaku's payments, Tanelyv's gifts, Laussa's ring and others;
  "—" now only where nothing gives the item (the Polearm +1, the Golden Torque). The champions' gear
  in the mundane tables; the polearms' doc icons at the game's own 36 pixels.
- **ITEMS.md, FEATURES and the guide: the chatkchas and the Polearm +1.** The acid and corroding
  touch take only a held weapon of reach 1 (the type's +0Ah; the item list routine, DSUN.EXE
  5900Ah, called with 1): chatkchas (reach 9), slings and bows are never taken, so the Chatkcha +1
  and Skycutter are out of the acid table. The Polearm +1 is defined (a stand-alone object in
  RGNFF.GFF, where the objects with no place on a map are, which scripts create into play), but no
  script creates or gives it (by its number, negative as a create takes it, or through a variable),
  and nothing holds one: nothing in play gives it (the cluebook's "Elven Caravan" is not in the data).
- The player guide's **XP left over at the top**: each class's highest level under the 749,999 cap
  and the XP left over (one, two or three classes), and for dual-classing humans the room a new
  class has by the level the old class changed at (dual-classing starts the new class at 0 XP and
  loses any XP past the old level's need: DSUN.EXE 86D38h); FEATURES links to it.

## Pull request #88 ([merged 2026-11-08](https://github.com/daaki85/darksun-obsidian-edition/pull/88))

Obsidian Edition 2.14.1 ([release notes](release-notes/v2.14.1.md)).

DSCLOG.EXE 63,824 bytes (image 63,792), 1,744 of its segment spare.

**Fixed: the Loader's window**
- **The new spells' switch said "New wizard spells"** and then listed the ten 6th-level priest spells
  it also covers. It is "New spells" now, with the six wizard spells and the priest spells named
  apart; FEATURES and the player guide call it that. (`viewer.py`; the setting is still
  `new_spells`.)

**Fixed: the Loader**
- **A bow the Loader gave couldn't shoot** until it was taken off and put on again: a new character's
  whose weapon spec is the bow (whatever its class), a Myrmidon's second spec's, fuller starting
  gear's for a Battle Dancer or Spellarcher, and any Spellarcher's once it made spell arrows in an
  empty quiver. Each gives the bow to the held list and its arrows to the worn one, as the
  inventory screen keeps them (since #85, 2.13.4), and then `bow_ahead`, which put a bow ahead of
  its arrows when both were in one list, swapped the two records across the lists: the bow in the
  worn list, where the game doesn't look for a missile weapon. It swaps only within one list now,
  and a weapon found in any party member's worn list (or arrows in the held one) is moved back as
  the dice log runs, out of a fight: "Yilballa's Bow is now held, ready to use (it had been counted
  as worn)". (`weaponchoice.bow_ahead`, `pickpocket.mend_lists`. Tests: `test_lists_apart`,
  `test_mend_bow_and_arrows`, both failing on the code before the fix.)
- **Changing the leader just after a fight rolled a thief's hiding:** the dice log took a change
  of whose turn within a minute of game time of the last round for a turn of the same fight, and
  game time barely moves out of fights, so the new leader's "turn" printed ("Alura's turn") and,
  with the stealth rule, rolled hide in shadows and move silently. A turn now also needs the
  game's own test that a fight is on (`game.fight_on`, as its rest and USE screen read it).
  (`DiceLog.turn_lines`. Test: `test_no_turn_out_of_a_fight`, which the code before the fix fails.)

**Fixed: DSCLOG**
- **A melee weapon's item box read "0.5x1D8-1",** whoever held it. With no creature the game's damage
  line takes the rate from the item type's +0Bh, a missile weapon's, which a melee weapon's type has
  at 1 (half an attack); the game hid any rate of one attack or less, until #76's `dam_half` let
  "0.5x" through for Slow. With no creature the rate is now at least one a round, so the box shows
  none, as before #76; the inventory's and View Character's lines are as they were. (`PROBE_MISSILE_LINE`.
  Seen in DOSBox: Gerakis's Bone Long Sword's box "1D8-1", his sling's "1D4". Test:
  `test_item_box_rate`, which the helper before the fix fails.)

**Changed: DSCLOG's room**
- **1.7 KB of the helper's 64 KB segment freed** (96 bytes were left): three buffers that start as
  zeros, the new spells' room (`seg_space`, 512 bytes), their areas' pictures' table (`area_space`,
  896) and the shadows' colours (`dark`, 256), no longer take bytes in the image: they lie over the
  install code, which is done with by the time they're used, and `KEEP` zeroes them before its first
  DOS call. DSCLOG.EXE 63,824 bytes (was 65,472), 1,744 of the segment spare; what stays resident
  one paragraph more (`KEEP`'s zeroing), upper memory 7.5 KB spare. (`AFTER_INSTALL`. Test:
  `KeepTests`, `keep` run with the install code's bytes where the buffers go. Seen in DOSBox: the
  helper in upper memory at C90Ah, 63,952 bytes, the game 97 KB free with the map open, as before;
  the three buffers filled in play, the new spells' room made, and the party's shadows drawn.)

**Fixed: the game**
- **The game's Great Axe +3 had no material:** its type (2) carried the 40h of things with none,
  a ring's, so its name showed none, and under the class restrictions no sphere's cleric could
  wield it. DSCLOG makes it metal as the game loads its types, as its icon (the game's metal axe's
  grey and teal head) and its weight (70, the metal great axe's) have it. (`PROBE_TYPES_FILL`:
  5 bytes, which fit the image's last paragraph's padding. Seen in
  DOSBox: type 2's +8 read 04h, and the game's inventory named it "METAL GREAT AXE".)
- **The creation screen's least scores weren't the manual's:** the die raised the class's prime
  requisite to 17 and every other score to the class's one least (9 to 14), so a fighter's STR was
  never below 17 and a thief's CHA never below 9, while a druid's CHA 15, a ranger's STR 13 and
  DEX 13 and a psionicist's CON 11 went unasked. The least for each score is now the manual's (cleric
  WIS 9; druid WIS 12, CHA 15; fighter STR 9; gladiator STR 13, DEX 12, CON 15; preserver INT 9;
  psionicist CON 11, INT 12, WIS 15; ranger STR 13, DEX 13, CON 14, WIS 14; thief DEX 9), the
  highest of a multiclass character's classes, and the dice log says "raised to 9 (the Thief's
  minimum)". (`gamepatch` `least_scores`: 67399h's 104 bytes replaced by `dos/least_scores.asm`,
  the overlay manager's two segment fixups kept in place; `game.CREATION_MINIMUMS`. Tests:
  `test_least_scores`, run in the emulator. Seen in DOSBox: each class's least for each score,
  read after a lowering click, the manual's, and three multiclass sets the highest of theirs; a
  fighter's STR clicked down 17 to 9.)
- **No XP bonus for high prime requisites:** the manual gives a class whose prime requisites are all
  16 or more 10% more XP (Fighter and Gladiator STR; Ranger STR, DEX and WIS; Preserver INT; Cleric
  WIS; Druid WIS and CHA; Thief DEX; Psionicist CON and WIS); the game's award routine (6B817h)
  has none. The dice log's tracker now adds it to each gain it sees, whatever it came from: 10% for
  each such class, divided by the classes, since a sheet has one XP for all of them (the game adds
  one class's share); a human counts only the class it follows now (slot 0). The character's own
  scores count (the sheet's), not an item's or a spell's. It writes the sheet, remembers the XP
  with the bonus so it isn't seen as a gain again, and shows it: "XP: Dag +137 (+12 for Fighter,
  STR 17)". A level the bonus alone reaches comes with the next award. The game's area change,
  which takes the XP away and gives it back, brings none. The tracker also stands aside while the
  creation screen is up (`game.creating`: DS:119Ch's sheet with DS:11A0h's record straight after
  it): there the party's first slot carries the character being made on a stand-in sheet whose XP
  moves with the class chosen, which the log had shown as "XP: SeanBoy +1500". (`tracker.prime_bonus`.
  Tests: `test_prime_requisite_bonus`, `test_prime_bonus_classes`, `test_no_xp_on_the_creation_screen`.
  Seen in DOSBox: an award of 600 gave Gerakis +660 "(+60 for Gladiator, STR 24)", K'ratchek +213
  (his druid's CHA 15 short), Cermak +660 and Cilla +220, written once, in a game loaded after
  the creation screen too.)

## Pull request #87 ([merged 2026-11-07](https://github.com/daaki85/darksun-obsidian-edition/pull/87))

Obsidian Edition 2.14.0 ([release notes](release-notes/v2.14.0.md)), with #86.

DSCLOG.EXE 65,472 bytes, unchanged (comments only).

**Fixed: the Loader** (a fifth review)
- **Writes through a table pointer gone null mid-pass could land in DOS's own memory:** the item
  gate (since #86) covered only where the tables are and were, and the low-memory guard reaches
  600h, where a null table's writes run to 20D0h (items) and 7400h (creatures). A null table is
  covered from 0 now, and the gate refuses while one is gone. (`itemgate.py`. Test:
  `test_tables_moved_mid_pass`.)
- **The Loader could take the game's last free lists and item records** (the game's people
  dressed in every area): 20 of each are left to the game now. (`ring.RESERVE`. Test:
  `ReserveTests`.)
- Smaller: the Loader's own list writes made the pass's later item steps wait a pass (and counted
  as refusals in the freeze report); a two-hander went in the right hand beside a shield already
  held; a finished see-through palette's thread cleared another's mark; a flag past the 808 a
  save keeps is refused (`game.FLAG_COUNT`, `test_flagrange`). `test_scriptchecks`' file times are whole seconds: at 1-3 ns they were all 0 on Windows (100 ns steps), and the test failed there.

**Fixed: the Loader's window**
- **All fields** widens its columns to the longest label and value shown; the **Memory tools**
  byte view scrolls sideways in a narrow pane; the window keeps a smallest size (1080x640) at which
  every tab and row of buttons fits.
- The Characters card says `Features:` for the game's own party's features (`Features: Wild
  Fighting`), `Kit:` when there is a kit; K'ratchek's `Chatkcha 2 a round` reads `One more
  chatkcha throw`. All fields' `Attacks/round` is `Attacks/round (base)`, the game's number
  before specialization. (Test: `test_kit_label`.)
- Options: the floating names' switch names the charges used (`Armor: 7 left`) as well; the
  shadows' says `(soft, on the floor)`, not see-through, which is the hidden and invisible.
- **The divider stops short of the Memory tools' buttons:** widened to fit the party's columns,
  it could hide Stride's Apply and cut Reload layout. It now leaves room for the widest row of
  buttons, the columns widening as the table fills no longer move it, and the byte view asks for
  less width (it scrolls sideways). (`Viewer._fit_party`.)
- Labels reworded: the saves are copied into Named saves only while the window is open; the
  Options note names the .bat files; the Look switch says what it shows (hit points, AC, THAC0
  and defences); Restore defaults says when a switch marked "from the next start" applies.

**Docs**
- The changelog's #86 heading, its fourth-review fixes and the releases list put right; the patch
  notes, README, FEATURES and the player guide given what #86 left out (Kalzith's face, the
  pickpocket sounds, the Kreenfang in a 2.13.4 save); DICE-LOG's picked pockets and the game's own
  party's opening lines; the developer pages given the gate's cover, the reserve, the people's
  gear's tries and the edge cases of names and shadows; #86's "Room for new code" filed under
  Changed; the playtesting guide's repeated notes merged and its save list completed.
- A docs review: the player pages (the saves list in one place, the release notes in a player's
  words, the patch notes refiled); the feature pages (FEATURES' always-on features apart from its
  switches, item places moved to ITEMS, one summary of the rule changes, DICE-LOG's missing lines,
  HOW-THE-GAME-WORKS kept to the game); the developer pages (Building and testing split into
  Build, Tests and Release steps, with the game-file variables and the project-wide tests; Room in
  the helper with one table of sizes; the kits' effects table cut to effect, kit and probe, each
  mechanism below it; the shadows' cache placed in the far block; the developer detail taken off
  the player pages placed here; every Loader flag in `test_flagrange`); the playtesting guide's
  repeats merged; three Loader screenshots retaken.

## Pull request #86 ([merged 2026-11-07](https://github.com/daaki85/darksun-obsidian-edition/pull/86))

DSCLOG.EXE 65,472 bytes (+880 since #85; its image 65,440, 96 bytes of its segment spare).

**New**
- **Kalzith's own portrait:** a face painted for him in the game's portrait style (an old man,
  white of brow and beard, in his figure's green-teal hood), the user's choice of three, in
  place of the game's portrait 61. (`kalzithface.py`, portrait 101. Seen in DOSBox in his talk
  and shop; `docs/kalzith.png` retaken.)
- **See-through figures:** a thief or ranger hidden in a fight, and anyone invisible (a party
  member always, a foe while no party member detects invisibility), is drawn half see-through.
  DSCLOG draws such a figure itself, blending its pixels with what is under it through tables the
  Loader makes from the palette. (Options: "drawn see-through", on. `ghost.py`, DSCLOG's
  `PROBE_GHOST` on `INT 80h`; DEVELOPMENT-CONTENT § See-through figures. Seen in DOSBox with a
  real hide and a real Invisibility. Tests: `test_ghost.py`, `test_ghost_draw_many_runs`.)
- **Sounds for hiding and picking pockets:** a soft breath as a thief or ranger hides in a fight,
  and a purse's jingle for a picked pocket (the three weapons worth XP keep the quest's sound). A
  Spellarcher making spell arrows hears the spell's own cast sound. (`sounds.py`,
  `spellarrows.cast_sound`; DEVELOPMENT-CONTENT § Sounds for hiding and picking pockets. Seen in
  DOSBox, DOSBox's output matched with the clips. Tests: `test_sounds.py`, `test_pick_sound`,
  `test_spellarrows.py`.)
- **The champions' bout:** once a party member has killed Scar in the arena, the next visit's
  first wave is six champions from a distant arena, after a speech of the Announcer's, once: a
  Tohr-kreen with Kreenfang, a half-giant, a mul, a halfling, an elf and a defiler, each armed and
  armoured (a defiler with a scroll). The Tohr-kreen leaves a body of its own, with Kreenfang in
  it. (New items. `champions.py`, `bodyart.py`; flags 759 and 807; DEVELOPMENT-CONTENT § The
  champions' bout. Seen in DOSBox: the speech and the bout after Scar's death in a real game,
  every champion's weapons in use, the body's picture. Tests: `test_champions.py`.)
- **Pehtucl's chest, locked and trapped:** the slave pens' head templar's chest, beside him, holds
  the Cloak of Protection +1. A thief checks it for traps (find/remove traps: a poisoned needle
  drawn out, or sprung) and picks the lock (open locks), as often as wanted; anyone else may bash
  it (the game's safe's odds: 5%, +5% for each of STR 18, 20, 22 and 24), which springs the needle
  if it is still there. The needle is 2d6 poison; the party's best at find/remove traps may still
  avoid it, as with every trap in the game. Worked on only from beside it. A new game only.
  (New items. `pehtuclchest.py`, script 223, flags 795 and 796; DEVELOPMENT-CONTENT § Pehtucl's
  chest. Seen in DOSBox: every branch, the disarm on 2026-11-07. Tests: `test_pehtuclchest.py`.)

**Changed**
- **Thornwall comes onto the slave pens' weapon rack once Semyon has told of it,** in a new
  question ("Seen anything useful?": a crate the guards fussed over); then "We found what was in
  that crate" once a party member carries it. It had been on the rack from the start. (New items.
  `semyon.ship`, flags 756-758. Seen in DOSBox, and after a save and load. Tests:
  `test_semyon.ShipmentTests`.)
- **The Cloak of Protection +1 is in Pehtucl's chest,** not on him: worn, it gave him nothing, as
  a cloak counts for nothing with a shield under AD&D's rule. He keeps his ring. (`npcitems.py`. A
  new game only.)
- **The game's people wear the cloaks, belts, boots, amulets and up to two rings they carry,**
  which the game never put on; each counts by the same rules as the party's. (`people.py`, with
  the fix below.)
- **Cilla's own feature is the "Elven Shadow-walker"** (her hiding never halved in daylight), not
  the "Elven Wanderer", which read like the druid kit Wanderer; SHADOW-WALKER on the Effects
  screen. (`kits.OWN_FEATURES`, DSCLOG's `own_lines`.)
- **The freeze report samples every 32nd strike of the timer,** not every 16th (`freeze.py`).
- **Room for new code:** the end shared by seven handlers that return through the overlay
  manager's frame is written once (`OVR_BACK`), and a sheet's classes read by one routine
  (`SHEET_CLASSES`): 112 bytes freed, 128 spare from 16 (96 after the fix to see-through figures in
  the enemies' turns). The build also fails now if the music pool or the see-through tables
  wouldn't fit upper memory (`UMB_KEPT`; they were left out quietly).

**Fixed: the game**
- **The game's people put on their weapons and armour only at their first action in a fight.**
  Until then each was AC 10 with its armour unworn and its Look box listed no weapon, so a first
  round's blow on one who hadn't acted, a backstab, or an opening blow from outside a fight (which
  is struck before the fight starts) met no armour. The Loader now puts each person's gear on as
  it comes on the map, as the game would. (`people.py`; DEVELOPMENT-CONTENT § The game's people's
  gear. Seen in DOSBox: every person with gear in the pens wearing and holding it. Tests:
  `test_people.py`.)
- **Psionic Blast knocks out instead of killing** while a party member's imagined wounds are
  still to come back; one knocked out wakes with them at the fight's end. This replaces #85's
  "only to a member still Okay". Disintegrate still kills. (From yuan-ti's v0.1.55;
  `gamepatch.blast_knockout`; DEVELOPMENT-CONTENT § Worn items. Seen in DOSBox. Tests:
  `WornTests.test_blast_knocks_out`, `test_psiblast.py`.)
- **Scare's save:** below 6th level an elf or half-elf priest got no save (the game tested for
  both races at once). (From yuan-ti's v0.1.55; `gamepatch.scare_elves`. Tests: `ScareTests`.)

**Fixed: the scripts**
- **Eleven of the Loader's changed scripts no longer decoded** (3, 5, 46, 137, 139, 146, 174, 212,
  213, 220, 221): a jump over a longer command left the rest of it in place. The dice log's
  explanations of the scripts' rolls couldn't read them, and the champions' bout never came with
  Semyon on. Each jump now fills what it leaves with a one-byte command. (`gpl.put_jumps`. Test:
  `AllScriptsTests`.)
- **Kurzak spoke of Legcrusher as gone while he lived:** his lines asked whether Legcrusher was on
  the map, and he is made only as Kurzak calls. They ask the Loader's flag 797 now, set once the
  dice log sees him dead. (`kurzak.py`. Test: `WatchTests`.)
- **A save's talk and use commands could point at another script once a switch changed:** the
  Loader's script entries were numbered only for the parts switched on, so with Kalzith off his
  talk's entry was Semyon's. The three entries (Kalzith's, Semyon's, the chest's) and their scripts
  are always there now, in that order. A save made with an earlier version and Kalzith off has
  Semyon's talk run Kalzith's script (the patch notes' saved games say so). (`kalzith.ENTRY_SCRIPTS`.
  Test: `test_scriptnumbers`.)

**Fixed: DSCLOG**
- **It hooked its interrupts before setting up its buffers,** so with no memory for them it
  exited with its vectors pointing into freed memory. The buffers come first now.
- **The floating names and the shadows shared the VGA's kept registers,** so a timer strike in a
  shadow, panel or see-through pass could put the game's registers back wrong (a likely cause of
  rare drawing gone wrong). (`VGA_BUSY`. Test: `test_vga_busy`.)
- **A pocket picked or spell arrows made after DSCLOG had stopped waiting** still happened, unseen.
  Such a request is marked answered now. (`USE_REPLY`. Test: `test_unanswered_marked`.)
- **It waited for the Loader with interrupts off for a Spellarcher's arrows,** so with the Loader
  slow the game's clock and music stopped for up to two seconds. (Seen in DOSBox: loads and runs.)
- **Its message when its interrupts are taken** names them right (60h-65h and 80h-FFh).
- **A floating name could be drawn above the page,** into other video memory, when the view was
  dragged so that its figure was off the top of the screen; it isn't drawn then. And a timer strike
  while a name was being erased could leave its old place on screen (the erase marked busy first).

**Fixed: the Loader** (an audit and four reviews)
- **One write the Loader stopped ended the dice log for the session** (slicing a deque raised every
  pass). It is told once now, and kept for a crash report, which had always shown none. (Test:
  `test_refused_write_said_once`.)
- **One failing step of the dice log's pass stopped all those after it,** every pass. Each step
  is on its own now, and an error is said once, by where it was raised (not its text, which could
  carry an address and was said every pass), in the window and `play` mode too. (`DiceLog._step`,
  `dicelog.error_key`. Tests: `test_each_step_on_its_own`, `test_error_key_by_where`.)
- **An item moved could be lost:** with the game's things all in use it was taken out of its list
  and put in none. The new list is found first now. (`pickpocket.place`. Test:
  `test_no_list_to_be_had`.)
- **A sold magical item could be lost** while the game was busy with its item lists: the gate is
  asked first, and covers the pointer's thing. (`Buyback.keep`, `THINGS_PAST`.)
- **A weapon's 200 XP for a picked pocket could be had again** by selling it and lifting it back.
  Paid once a game now. (Test: `test_sword_xp_once`.)
- **A pocket picked or a speaker's name learned was lost** if settings.json was held at that
  moment (an antivirus, a backup). It is saved at the next pass. (`DiceLog.save_learned`.)
- **A save of the same party loaded wasn't seen as a load,** and the game's own party wasn't made
  ready in a second new game without closing the Loader. (Tests: `LoadSeenTests`,
  `test_default_party_again_in_a_new_game`.)
- **A dressed figure could be written past its room** in the objects' copy after "Elves have pointed
  ears" changed; each picture's room is read from the copy itself. (Test: `test_rooms`.)
- **The dice log named the wrong script checks** after a switch changed and the game started again;
  **the scenes' pointer file** could stop the game from starting; **the combat log level** chosen on
  the Options tab was undone while the panel showed; **the window forgot the panel's size**.
- **The Look box's AC left out Helms give AC 1** until someone wearing such a helm had been
  attacked. (Test: `test_helm_before_dsclog_sets_it`.)
- **A speaker's name was learned wrongly from a script's speech** (Kurzak's call taught "Trustee"):
  a speech with no replies teaches a name only when its speaker stands near the party. (Test:
  `SpeakerTests`.)
- **Writes across an area's loading:** the item gate now also covers where the item and creature
  tables were as the pass began. (`itemgate.py`. Test: `test_tables_moved_mid_pass`.)
- **A failed copy of the objects or resources file left the last start's** for the game to open,
  made with other switches. It is taken away now.
- **Script checks dropped a roll's line** when the scripts' copy was damaged, and found none with no
  copy (the game's own scripts are read then). (Test: `LoadTests`.)
- **Wake of the Ravager's and the whirlwind's pictures could pulse:** a green was matched to a
  colour the game cycles. (`wotrart.stable_colours`, `whirlart.CYCLED`.)
- **The window kept a second copy of the objects' file** (5.4 MB; now 0.46 MB, what differs).
- Smaller: settings.json tried again before it counts as empty; the arena ring's search kept if
  giving the ring fails; a speaker's name, a saved log and the Named saves folder say when a file
  fails; the Memory tools' "... more" row can't be assigned; the Look texts searched for in the
  dialogue are the last 16.
- Smaller: the panel shortened only plain saves; Kalzith's scrolls weren't trimmed when the lists
  were busy, and his stock waits while the flags have no place in memory (it read as not given);
  a monster's or attacker's THAC0 below 0 showed as 255; WIS's save adjustment read past its
  table; Restore Youth's system shock on a creature with no CON; a party member named Kalzith or
  Semyon counted as his death; Cilla's armour, when the game's lists moved under a piece, is taken
  on the next pass; a palette from an earlier start isn't kept when the game's can't be read;
  crash reports show the new spells' old setting name, the ring and the panel's level as used; a
  failure counting effects' charges no longer loses the pass's lines; a script repair too short for
  its jump is left out rather than shifting the script (none is, today).

**Fixed before release** (in the new work above)
- See-through figures' first vector, 62h, was `PROBE_AC`'s, so every attack's AC went to the
  see-through probe (it is 80h, and `test_vectors_distinct` checks each vector is used once).
- A hidden thief stayed see-through through the enemies' turns after its own (about 1.4 s): the
  whole view is drawn once as one stops hiding. (`GHOST_UNION`. Test: `test_solid_at_turn_end`.)
- Champions made again from a save came on unequipped. (Test: `test_again_after_a_load`.)
- Pehtucl's chest had taken script 220, Alagorn's copy telling of clothes, so his menu called past
  the end of the chest's. The chest is 223, and `test_scriptnumbers` checks no two scripts share
  a number, every call lands inside its script, and every script fits the game's buffer.
- The chest could be worked on from across the room (the game's safe tests the distance first).
- **A figure stayed see-through (or solid) through the enemies' turns** when an invisibility ended
  or began then, until a party member's turn: the view is drawn again from the map's main loop,
  which doesn't run in those turns. The Loader now marks the table changed (`GH_CHANGED`, the last
  byte of GHOST_TAB's room), and `GHOST_UNION` draws the whole view once at the next step of
  anyone's. (Test: `test_whole_view_when_the_table_changes`. Seen in DOSBox: the
  byte cleared 0.06 s into an enemy's 0.36 s turn; playtest/logs/2026-11-07-review-fixes.md.)
- **The sound of the mod's own lent the game's table entry back one byte too far,** over the next
  entry's "loaded" flag (latent: nothing changes it during a play).
- **A see-through figure with no picture yet** was drawn from the interrupt table as if it were
  one; it is left undrawn, as the game's own routine does. (Test: `test_ghost_draw_no_picture`.)
- **See-through figures were drawn solid for a moment every 30 s** where the game cycles colours,
  and their tables were kept all session. They are kept by the colours the game never cycles, the
  last eight. (Seen in DOSBox: GHOST_ON 1 in all 3,722 samples. Test:
  `test_cycling_colours_keep_the_tables`.)
- **See-through tables were kept by too few colours** (224-239 differ between areas) and could
  leave the figures solid after a quick change of palette and back. (Tests:
  `test_area_colours_count`, `test_back_before_made`.)
- **A two-handed weapon was given a shield or a second weapon** among the game's people, and a
  shield went beside one already held at a later visit. (Tests: `test_two_handed_alone`,
  `test_two_handed_already_held`, `test_two_hander_never_second`.)
- Smaller: the chest's watcher no longer scans the item table each pass; Semyon's crate counts a
  Thornwall in a bag.
- The item gate's rule for a null table (in this work) refused every write while the game rebuilt
  its tables, DSCLOG's replies and the see-through tables too, and a refused write could leave
  the tables never made; `ghost.py` marks them only after its write. Floating names near the top
  were hidden under row 40, not only above the page (row 0). A part-dressed person was tried every
  pass for good, each pausing DOSBox (`people.TRIES`: three). The refused writes' "... and N
  more" counts past 200; `GHOST_UNION` reads and clears `GH_CHANGED` in one `xchg`.

**Docs**
- The new work in the patch notes, README, FEATURES, ITEMS, the guide and the DEVELOPMENT pages:
  the champions, the chest and its cloak, the game's people's gear (FEATURES' bug table,
  HOW-THE-GAME-WORKS' Monsters' defences), see-through figures, the sounds.
- FEATURES: Kurzak striking with Shadowseeker in the combat log's detail
  (`docs/combat-log-detail.png`).
- DEVELOPMENT: the room in the helper measured in the running game (`UMB_NEED`, 6,186 at this
  build), the dice log's pass, the flags' ledger in one place (DEVELOPMENT § The Loader's game flags),
  the sounds, `VGA_BUSY` and the unanswered requests.
- From the reviews: `inventory-ranger.png` (it showed a gladiator), `effects-charges.png` and
  `dicelog.png` (Cilla's new name) retaken; the guide's multiclass
  combinations once, in its race table; and many smaller corrections across the pages.

## Pull request #85 ([merged 2026-11-02](https://github.com/daaki85/darksun-obsidian-edition/pull/85))

Obsidian Edition 2.13.4 ([release notes](release-notes/v2.13.4.md)).

DSCLOG.EXE 64,592 bytes (688 bytes of its segment spare).

**Changed**
- **The dice log's `--all` line for each AC gives its parts:** base, armour, DEX and other.
- **The dice log names a thri-kreen's claw or bite:** a party thri-kreen with nothing in hand
  attacks `with a claw (1d4)` (four a round) and `with its bite (1d4+1)`, and the bite's damage
  line shows `+1 bite`, not `+1 weapon`. The claw's dice are the ones it has now, with Erdlu Claw,
  Animal Affinity or Body Weaponry. With weapons in hand a thri-kreen attacks with them and then
  still bites. (`GameData.natural_attack`, `THRI_KREEN_ATTACKS`; DEVELOPMENT-CONTENT § The game's
  spells. Seen in DOSBox with K'ratchek unarmed, and a thri-kreen's attacks put on Gerakis. The
  guide's races table and DICE-LOG say so. Tests: `test_thri_kreen_claw_and_bite`.)
- **Erdlu Claw's talons are the claws alone:** a thri-kreen's four claws become 1d6+1, +1 to hit,
  as a +1 weapon, and its bite stays 1d4+1. Body Weaponry and Animal Affinity already change only
  the first set of natural attacks. (DSCLOG's `NS_CLAW`, `NS_FIST`; the dice log's THAC0 breakdown
  the same. The spell's text, FEATURES, the guide, HOW-THE-GAME-WORKS and the patch notes say so.
  Tests: `test_claw`, `test_fist`, `test_fist_claws_cut`, `test_thri_kreen_claw_and_bite`.)

**Fixed: the game** (from yuan-ti and OpenDS's list, yuan-ti's issue #129; each checked in
DSUN.EXE)
- **A character's most PSP comes from its own CON, INT and WIS.** The level-up check (run for every
  member, and at a game's start) took the WIS bonus from the creation screen's record, in play a
  stray byte, and its tables were 8 scores long (INT 22 gave 0). DSCLOG puts the member's own
  scores in, to 25. The most only rises, so a character's may go up once (Cilla 30 to 43, as the
  game's rules give her). The psionicist's WIS bonus a level is left as it is. (`PSP_SCORES` in
  `PROBE_MAX_PSP`; DEVELOPMENT-RULES. Seen in DOSBox. Tests: `test_max_psp_scores`.)
- **A fight's music level is each creature's own:** an attack starting a fight looked up its
  creature's music level with a word's index, so every creature but the first got another's.
  (`gamepatch`'s `fight_music`. Not heard in play.)
- **Ability items count only when worn:** the game applied every listed item's ability change
  wherever it was carried. (`PROBE_WORN` on `INT 81h`; DEVELOPMENT-CONTENT § Worn items, the
  gladiator's armour and Psionic Blast. Seen in DOSBox: a sling given DEX +2 raised DEX 15 to 17
  worn, not in the backpack. Tests: `WornTests.test_ability_byte_only_worn`.)
- **The gladiator's armour optimisation counts only in armour.** (The same interrupt, with
  `ARMOUR_WORN`; `THORNS_AC` and `counted_ac` follow. Seen in DOSBox: Gerakis at gladiator level 10
  AC 5 in armour, 9 in none (before, 7), and a 10th-level gladiator hit at AC 6 in armour in an
  arena fight; playtest/logs/2026-11-02-dsun-fixes.md. Tests:
  `WornTests.test_gladiator_bonus_needs_armour`, the Wall of Thorns damage's gladiator,
  `CountedAcTests.test_gladiator`.)
- **Psionic Blast's wounds are imagined:** the game took a target that failed its save down to a
  fifth of its most hit points for good. A party member's loss is now kept, and given back as the
  fight ends, up to the most and only to a member still Okay, with a dice log line. A loaded game
  clears it with nothing given. (`gamepatch`'s `psionic_blast`, `PROBE_WORN`, `BLAST_HP`,
  `psiblast.py`; DEVELOPMENT-CONTENT § Worn items. Tests: `WornTests.test_psionic_blast_kept`,
  `test_psiblast.py`.)
- **Checked and left alone:** scores over 25 (capped before the tables are read), the difficulty
  setting (applied as a monster comes, by design), a ghost slot or a vanishing item, and a save
  made mid-scene. Left for a test in the game: bodies after a region is left, and a wall of fire's
  damage twice in one move.

**Fixed: the scripts** (`scriptfixes.py`, always on)
- **yuan-ti's v0.1.49 repairs:** the ranger's tracking at the Wagon Train's bodies (script 210),
  the slave pens' sewer grate (137: "hack the lock off" never offered, his or her, a hack that
  works opens it) and the halfling's greeting and insult (31).
- **The Loader's own sweeps** of every script for a field read from a record that lacks it, every
  RAND comparison and every check on a class, race, sex, item, weapon, thief skill or ability:
  sex in script 42 ("wo"man, "her" purse), race in 80 (a thri-kreen hears the bell) and 203 ("your
  help"), script 44's always-true race test, script 142's class tests, and script 56's slime book
  (its class mask meant every cleric, druid, preserver and psionicist). Every object number and
  every thief skill and ability check was checked.
- **yuan-ti's v0.1.50 and v0.1.51 repairs:** an attack on the grate always broke the lock (it read
  a field no grate has); now it rolls `RAND(30) < STR`, as the rip, and can fail. The Rebel
  Mindhome's leader gave the spiders' 5000 XP at every talk; now once (flag 695). (Tests:
  `test_grate_attack_rolls_strength_and_award_once`.)
- **yuan-ti's v0.1.52 repairs** (OpenDS's triage): region 9's messenger comes when flag 245 is set
  during a stay, not only as the region loads, and the Draj serf comes along from region 38 to
  region 10 from farther away. Looked at and left: the Mindhome's "Have you killed the spiders
  yet?", the Hound Necklace killing prisoners, Alhena, the army count. (Tests:
  `test_messenger_trigger_as_mas_9_registers_it`.)
- **The grate's failed hack:** a weapon that can break "breaks against the grate" and is gone; a
  metal or magic one "rings off the grate, unharmed". The game said it broke and kept it. Which
  can break is the game's rule for a weapon breaking in a fight (`Game.item_breaks`).
- A repair longer than its bytes is a detour after the script's end, with a jump back. (Not seen
  in play. Tests: `test_scriptfixes`.)

**Fixed: DSCLOG**
- **A thri-kreen's bite got the claws' Erdlu Claw bonus:** the game sets a round's natural attacks'
  to-hit and magic once, so what the claws got went on to the bite. A natural attack now starts
  with neither. (`NS_FIST`. Seen in DOSBox: the bite at THAC0 15, the claws 14.)

**Fixed: the Loader**
- **The Loader's starting armour gave no AC:** it put worn things in the held weapons' list
  (`+0Ah`), and the game's AC counts only the worn list (`+08h`), so Fuller starting gear's
  leather armour (and a Stalker's cloak) showed as worn and gave nothing. Items are now filed as
  the inventory screen files them, and what an earlier version put in the wrong list is moved
  ("Gerakis's Leg Armor is now counted as worn"). `counted_ac` and DSCLOG's `THORNS_AC` count
  `+08h` only, as the game. (Fuller starting gear. `pickpocket.list_for`, `mend_lists`. Seen in
  DOSBox: an old save repaired to AC 6, Gerakis hit at AC 6 in a new game, not 8. Tests:
  `ListTests.test_mend_worn`, `test_list_for`, `test_add_to`,
  `CountedAcTests.test_held_armour_doesnt_count`, the Wall of Thorns damage's held armour.)
- **A Slowed thief's skills:** Slow rules out picking pockets alone, as the game's routine does;
  the Loader had it ruling out the other seven. (Tests: `test_now`.)

**Docs**
- **DEVELOPMENT in four pages:** its "How each part works" is three pages beside it, ordered as
  FEATURES: `DEVELOPMENT-SCREENS.md`, `DEVELOPMENT-RULES.md` and `DEVELOPMENT-CONTENT.md`.
  DEVELOPMENT keeps building and testing, the dice log, the helper's room, the reports and memory.
  The 66 "How it works" links in FEATURES, KITS, README and HOW-THE-GAME-WORKS name the page they
  open. (`test_readme_links_how_it_works` reads the three pages.)
- **In the game moves to FEATURES:** the Loader README's **In the game** is FEATURES' first section,
  and the README (58 KB to 38 KB) is installing, running, the window and the dice log.
- **The web pages carry their fonts:** `player-guide.html` and `patch-notes.html` load nothing from
  Google Fonts. (`pagefonts.py`, the fonts and their SIL Open Font Licences in `dsloader/fonts`;
  about 190 KB more a page. Checked in Chromium: no request made.)
- **The changelog's five longest entries shortened** (#55, #31, #51, #44, #61), each linking to
  the file as it was; 278 KB to 246 KB. This entry's groups put in the merged entries' order, and
  the older entries' **Added** and **Documentation** called **New** and **Docs**.
- **Level cap by XP is a rule change:** its switch is in Rule changes, Characters, and FEATURES,
  the README, the guide and `options.png` (retaken) follow. More character customization is
  weapon specs, kits, STORE and RECALL and the starting gear.
- **A review for redundancy:** one copy of each repeated table (thief skills, the highest levels
  under the XP cap, preservers' INT, in the player's guide); saved games in one place (the Loader
  README's **Updating, backups, saved games and the Loader's files**); the README's **The creation
  screen**; FEATURES' Spells on the Effects screen linking to the README; Ages and CON's
  regeneration under Classes and Kits in the patch notes; the root README's What's new the current
  release alone; the Options tab's Kits text and FEATURES' bug table; the weapon window's caption.
- **A second review** (with another chat's review of `main` at 2.13.3): the guide's psionics table
  gave Enhanced Strength, Domination and Mass Domination a cost of 0 (the game works it out when
  used); KITS' slot table shows — for "no spells yet"; the README's bugs-fixed line names the
  scripts' checks. Copied tables, Options texts, old names, links, anchors and images checked.
- **A review after the item-list and Psionic Blast fixes:** the psionic powers' cost table stays in
  the guide alone; DICE-LOG's new lines; the README's bug list and the guide's Psionics and
  Equipment; DEVELOPMENT's helper size and upper-memory figures; the game's own party's armour
  list corrected.
- **Erdlu Claw's and the spell arrows' texts fit their box:** they ran to eight lines and spilled
  over its bottom edge. Each is seven lines now. (`spelltexts.py`. Seen in DOSBox;
  `new-spells.png` retaken.)
- Smaller: ITEMS gives the ability items' amounts and a weapon's spell on every hit;
  HOW-THE-GAME-WORKS' **Resting** gives the priests' cures at a rest; a worn item's helpful spell is
  cast for good, a cursed item's attack spell too, as DEVELOPMENT had it (checked; item 2005's
  swapped lists don't matter, there being no item 2005); DICE-LOG gains the Look box's line, PSP,
  the system shock rolls and ages; the guide's spell slot table shows the priests' 6th-level slots
  and where each class stops; the guide's WIS bonus slot table put right at WIS 23 to 25, with a
  6th-level column (checked against `SLOT_RULES` in DOSBox); the patch notes file the thri-kreen's
  claws and bite under Bug Fixes; the known issues say since when; the release notes keep their
  Getting started.

## Pull request #84 ([merged 2026-10-31](https://github.com/daaki85/darksun-obsidian-edition/pull/84))

Obsidian Edition 2.13.3 ([release notes](release-notes/v2.13.3.md)).

DSCLOG's image 64,320 bytes (960 bytes of its segment spare).

**New**
- **The THAC0 on the creation screen:** `THAC0: M18 R19` right of the hit points, above the age: M
  the character's THAC0 less STR's to-hit adjustment, R less DEX's missile adjustment, drawn again as the scores
  change. (DSCLOG's `CR_THAC0_DRAW`; DEVELOPMENT-RULES. Seen in DOSBox. Tests: `test_thac0_line`.
  The README's inventory THAC0 now says all it counts.)

**Changed**
- **The Shinobi's spell slots go on to 13th level:** 3 2 1 at thief level 11, 3 2 2 at 12th and
  3 3 2 at 13th, as the Seeker table in *The Complete Ranger's Handbook* goes on. The table had
  stopped at 10th, so a Shinobi stayed at 2 2 1 to the XP cap. A Seeker still stops at 10th.
  (Kits. `kits.SEEKER_SLOTS`, DSCLOG's `SEEKER_LAST`. Tests: `test_slots`.)
- **The Shinobi gets 4th-level spells at 13th:** a 4th-level slot (3 3 2 1) and Improved
  Invisibility, Solid Fog and Confusion on its list. CHOOSE A SPELL offers one no sooner than its
  slot; a scroll of one can still be learnt sooner. (Kits. `kits.SHINOBI_SPELLS`,
  `kits.shinobi_pick_level`, DSCLOG's `SHINOBI_PICK_CAST`. Tests: `test_slots`, `test_pick_level`,
  `test_pick_any`.)
- **A Spellarcher adds to the same spell's arrows:** with Chill Arrows in its quiver, Chill Touch
  adds more, and the dice log says how many are there now. Another spell's arrows still stop it.
  (`SpellArrows.make`, `MOST_ARROWS`. Tests: `test_make_more_of_the_same`.)
- **The Wasteland Seer is a thri-kreen druid/fighter/psionicist's,** and a druid/fighter has no
  kit now. A multiclass kit may be three classes. One from an earlier version keeps its kit byte
  but has no kit. (Kits. `kitpages.MULTI`, DSCLOG's `MULTI_FIND`. Tests: `test_multiclass_kits`,
  `test_kit_at`, `test_sky_level`.)
- **The Wasteland Seer's psionics follow the sky too:** every power costs 2 PSP less under the open
  sky and 1 more under a roof, never below 1. K'ratchek, a Wasteland Seer by her own feature, has
  it too. (Kits. `kits.psp_cost`, DSCLOG's `PSI_KIT`. Tests: `test_psp_wasteland_seer`.)
- **An Elementalist has at least 1 slot at each spell level a cleric of its level casts,** its slots
  otherwise a level behind as before. (Kits. `kits.slots`, DSCLOG's `PROBE_SLOTS`; `KITS.md`
  follows. Tests: `test_slots`.)
- **The crash report's two buffers moved out of DSCLOG's 64 KB** into the far block in the HMA
  (6,566 bytes left there). GAMEMSG.BIN is the same. (`FAR_QM_STACK`, `FAR_MSG`; DEVELOPMENT § The
  crash report. Tests: `test_crash_report`.)

**Fixed**
- **EDIT on a party member** (to change a name, say) took its kit away, rolled a new age and asked
  for its weapon specs again. It now keeps the kit, the age and, while its classes and kit are
  unchanged, the weapon specs. (DSCLOG's `CR_OPEN`, `ED_SAME`, `ED_KEEP`. Seen in DOSBox. Tests:
  `test_edit_keeps_its_specs`.)

**Fixed before release** (a review of the changes since 2.13.2)
- The creation screen's THAC0 left out a kit chosen on the panel; it applies it now, and a kit
  chosen or taken back draws the line again. After a Battle Mage's, Mind Warrior's or Arcanist's
  hit points were rolled again the age went missing. (`THAC0_GAME`, `CR_THAC0_BASE`,
  `KIT_REDRAW`. Seen in DOSBox.)
- EDIT gave a kit back whatever the race (a half-elf Shadowblade made a dwarf came back a Ghetto
  Fighter) and a Healer whatever the sphere. (`ED_RACE`, `HEALER_BARRED`.)
- An Elementalist got a 6th-level slot at 11th without AD&D's tables; only with them now.
- K'ratchek's Effects screen line reads "OPEN SKY SPELLS/PSI". (`OWN_LINES`. Seen in DOSBox.)
- Tidier: the Options tab's rule groups in each rule's own entry (`viewer.py`), and the creation
  THAC0 using `DEX_REACTION` and `CREATURE_SCORES`. (Tests: `test_thac0_line`,
  `test_edit_keeps_its_specs`, `test_slots`.)

**Docs**
- **The rule changes in three groups,** the same in the docs and on the Options tab: Characters,
  Weapons and armour, and Magic. FEATURES has a heading and summary table for each (anchors as
  they were). (`viewer.py`'s `rule_groups`; `options.png` retaken.)
- **Pages reordered:** the Loader README's **When something goes wrong** at the end;
  HOW-THE-GAME-WORKS by subject; the player's guide's **Experience and levels** after the kits,
  with **Hit points** and **THAC0 by level** under it, and **Ages** a heading of its own. Anchors
  as they were.
- **A review after the slot table's gap:** hit points past 10th (a preserver +1 a level, a thief
  +2); EDIT in KITS and Ages; the one three-class kit; the Swashbuckler's THAC0 to 13th; K'ratchek
  "is" a Wasteland Seer, her feature named "Open sky spells and psionics" (`kits.OWN_FEATURES`).
- `KITS.md`'s spell slot table goes on to each class's highest level under the XP cap, with a
  druid column, from the code's own tables; the Grove Warden's AC steps go on to 4 at 12th.
- Screenshots retaken: the dice log and Dialogue tab at the arena's opening show, and the creation
  screen with the THAC0.

## Pull request #83 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/83))

Obsidian Edition 2.13.2 ([release notes](release-notes/v2.13.2.md)).

DSCLOG's image 63,680 bytes.

**Changed**
- **The creation screen's age is rolled on Dark Sun's Table 7 dice,** with each roll of the die, a
  choice or the screen opening, not from the name and race. A click on CON, STORE and RECALL keep
  it, and DONE puts it on the sheet. The game's own party, and a character from before ages, get
  real rolls from the Loader. (Ages and magical aging. DSCLOG's `age_dice`, `age_rand`, `AGE_PUT`;
  `give_ages`; DEVELOPMENT-RULES § The age on the creation screen. Seen in DOSBox: four rolls,
  STORE and RECALL, CON down and up, DONE. Tests: `test_age_dice`, `test_age_put`,
  `test_give_ages_once`.)
- **The starting roll is kept on the sheet,** beside the weapon specs (a new layout, v2), so
  Restore Youth's floor is the character's own start and the magical years it can take back have
  no cap. 2.12 and 2.13 sheets still read; a character aged before keeps its age. A save made with
  this is not for 2.13.1 or earlier. (`SPEC_V2`, `aging.start_age`. Tests: `test_packing`,
  `test_rolls`, `test_older_layouts_read`, `test_spec_layouts`,
  `test_an_age_from_before_keeps_its_start`, `test_true_age_from_the_roll`.)

## Pull request #82 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/82))

Obsidian Edition 2.13.1 ([release notes](release-notes/v2.13.1.md)).

DSCLOG's image 63,360 bytes (1,920 bytes of its segment spare).

**New**
- **Grey hair on the party's map figures:** iron grey streaks when middle-aged, grey when old,
  white when venerable, in each figure's own shades. Dwarves and muls (hairless on Athas) and
  thri-kreen are unchanged. The hair is found apart from the gear, with corrections for each race,
  so helms and cloaks don't move. (Ages and magical aging, and What the party wears.
  `greyhair.py`; DEVELOPMENT-RULES § Grey hair on the map. Seen in DOSBox. Tests:
  `test_greyhair`.)
- **The age on the creation screen,** above RECALL (`AGE: 23`), the age the character will start
  at, redrawn as the name changes; the inventory's line is `AGE: 23` too. Characters already given
  an age keep it. (`aging.natural_start`, DSCLOG's `AGE_ROLL`. Seen in DOSBox: six figures and
  three names, each age the Loader's. Tests: `test_creation_age`, and the redraw as the name
  changes.)
- **Natural aging,** as flavour: a year each time the game's clock passes another 365 days, with
  its score changes, and the dice log says `A year has passed: Gerakis is 35.`. The years counted
  are kept in the game's flags (798-806), so a save keeps them, and none is counted twice or lost
  to a load, the arena or play without the Loader. Restore Youth's floor counts them. (Ages and
  magical aging. `aging.natural_tick`; DEVELOPMENT-RULES § Natural aging. Seen in DOSBox. Tests:
  `test_natural_years`, `test_restore_counts_the_games_years`,
  `test_the_log_counts_each_year_once`.)
- **The game's time on the combat log panel:** out of a fight its top line says how long the game
  has run, `Day 47, 14:20`. In the arena it gives the count of arena fights, once the game has
  shown it. (`combatlog.clock_line`. Seen in DOSBox. Tests: `test_clock_line`,
  `test_arena_count_only_once_known`.)

**Fixed: the scripts**
- **Kurzak notices Legcrusher is gone:** once the party has killed him (at the fountain, with no
  alarm), Kurzak's call, his greetings, his answer to "Who is the half-giant?" and Dinos's warning
  ask first whether Legcrusher is on the map. (Always on. `kurzak.py`. Not yet seen in play.
  Tests: `test_kurzak`.)

**Fixed: DSCLOG** (the second audit, with seven agents: code, memory, documents, pictures)
- **RECALL on the creation screen stopped DOSBox** ("DynrecCore: illegal option") from 2.8.0 on,
  when pressed before the die had been rolled on that visit: its redraw called another overlay's
  routine, whose loading could move the creation screen's, and RECALL then jumped to where it had
  been. Both calls are now made so the overlay manager fixes the way back. (`RS_FRAMED`;
  DEVELOPMENT-RULES § STORE and RECALL. Found by re-shooting the creation screen, narrowed down
  release by release. Seen in DOSBox: STORE, the die, RECALL twice.)
- Smaller: the creation screen's text buffer 12 bytes; no far call through an overlay operand not
  yet fixed up; a build guard for the helper's 64 KB segment; the creation age's handlers keep
  their way back apart from `RL_SUM`'s; a duplicate `EXPERT IN` and an unused word gone. (Tests:
  the creation age with 300 random names.)

**Fixed: the Loader**
- **The game folder search no longer holds the window up:** it looks in the folder given and the
  one saved first, then the drives one at a time, once a run, as does Wake of the Ravager's. An
  empty floppy or a sleeping network drive held it up each time the Options tab was built.
  (`launch.drives`, `find_game_dir`. Tests: `test_drives_searched_once_and_only_when_needed`,
  `test_kept_for_the_run`.)
- **The Loader's settings are saved through one helper** that says so on the status line when
  settings.json is held elsewhere, rather than losing the choice unseen.
- Smaller: the game window box shows Single for a window at its own size; a save cut short is
  reported as such; `find-text` and `checks` cope with any text and a lower-case GPLDATA.GFF; a
  missing DOSBox.exe is a launch error; a named save renamed only in case is no longer deleted on
  Windows; the stats thread is waited for before the memory is let go; defilers' scrolls and new
  items in crash reports; `age_by` kept in range, with no "grows younger 0 years" line; the
  mouse wheel's hook thread can't lose a quit; Windows' millisecond timer asked for once a run;
  refused writes kept to the newest 200; the game's art read once a run; confirmations only when
  saved; a settings.json that isn't an object kept aside; the party's figures tried again every
  30 seconds; no armour drawn on a thri-kreen; the Named saves and crash logs folders left out of
  the download mark's removal; dead code gone.

**Docs**
- **The dice log's reference has a page of its own,** `DICE-LOG.md`, linked from both READMEs and
  the guide. The README's Options sections are one list of links, the guide's Options at a glance
  being the one list of switches; the Kits page is the one description of who may take which kit.
- The new work in the guide, the README, the rule table and the patch notes; Dark Sun Recompiled
  in the patch notes; defilers' scrolls counted at once; Enlarge's rule and CON's poison saves in
  the guide; a spoiler note; DEVELOPMENT's memory figures as built and the Ages section in parts.
- Pictures retaken for the age: `inventory.png`, `inventory-ranger.png`,
  `default-party-gerakis.png`, `creation-store-recall.png`, `creation-weapons.png`, `dialogue.png`
  and `dicelog.png`.

## Pull request #81 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/81))

Obsidian Edition 2.13.0 ([release notes](release-notes/v2.13.0.md)).

**New**
- **Ages:** each party member has an age from Dark Sun's Table 7, rolled the first time the Loader
  sees it. Middle, old and venerable age (Table 8) change the scores once and for good, and the
  most a race lives (a secret roll) kills. Shown on the inventory panel (`AGE 23`) and the
  Characters tab. (Ages and magical aging, on. `aging.give_ages`, `aging.age_by`, DSCLOG's
  `AGE_TEXT`; DEVELOPMENT-RULES § Ages. Seen in DOSBox. Tests: `test_aging`,
  `test_effects_specs`.)
- **Haste ages:** each creature Haste speeds rolls system shock by its CON or dies, and a party
  member who survives is a year older. (The same rule. `aging.hasted`. Seen in DOSBox: a failure
  kills as the game kills, a success ages. Tests: `test_aging`'s HasteTests.)
- **Restore Youth, a 6th-level cosmos priest spell (211):** takes back a year of magical aging a
  caster level, never below the target's true age, after a system shock roll. Its icon is the
  mod's own, a fountain of youth, and it is cast with Cure Disease's sound. Negative Plane
  Protection's save record moves to 212. (`aging.restore`, `NPP_SAVE`, `wotrart.DRAWN`;
  DEVELOPMENT-RULES § Restore Youth. Seen in DOSBox: on a 12th-level druid's page, and cast on a
  character aged by Haste. Tests: `test_aging`'s RestoreYouthTests, `test_grace`, `test_dsclog`,
  `test_wotrart`.)

**Changed**
- **Enlarge multiplies the weapon's dice only:** the game's Enlarge multiplied the whole melee
  damage, STR's bonus included. Now only the dice, rounded up, the rest added once; a backstab then
  multiplies the enlarged dice. The dice log and the Effects screen follow. (Enlarge multiplies
  the weapon's dice only, on. `RULE_ENLARGE`, DSCLOG's `ENL_SITE`; DEVELOPMENT-RULES § Enlarge's
  dice. Seen in DOSBox: three hits by an Enlarged gladiator. Tests: `test_enlarge_dice`,
  `test_enlarge_dice_only`.)
- **CON as in AD&D:** the game gave a member with CON 20 or more a hit point every 300 seconds at
  any CON. Now the Player's Handbook's rate, (26 − CON) × 600 seconds a hit point, the remainder
  kept. A dwarf's or halfling's poison save gets no CON adjustment on top of its racial bonus. (CON
  as in AD&D, on. `RULE_CON`, `REGEN_SITE`, `CON_SAVE`; DEVELOPMENT-RULES § CON as in AD&D. Seen
  in DOSBox: Gerakis at CON 22. Tests: `test_regeneration`, `test_dwarves_poison_saves`,
  `test_modifiers_by_damage_kind_and_con`.)
- **The weapon specs are packed, making room for a character's age** in the sheet's last unused
  byte. A sheet keeps the old layout until its specs are written, and every reader takes both, so
  older saves and roster characters need no conversion. (`SPEC_PACKED`, `SHEET_AGE`,
  `game.spec_kinds`. Seen in DOSBox: both layouts read alike, through a save and load. Tests:
  `test_specslots`, `test_spec_layouts`, `test_specs_packed`.)

**Fixed** (from a code audit of this pull request and the Loader)
- **A new character could keep the last one's age:** DONE cleared the specs but not the age. (Test:
  `test_spec_layouts`.)
- **Haste rolled again after a reload:** the same party loaded again counts as a load now.
- Smaller: Enlarge's dice kept for a melee hit only; a score past 25 not cut by a +1, nor one under
  3 by a −1; a thri-kreen made young "no longer venerable"; no system shock for a creature with no
  scores; a CON past 25 reads no table; the game's Enlarge rounds toward 0 in the dice log; the
  patch notes' page no longer hangs on a "> " line; settings.json with a byte-order mark is read;
  the recompiled program's ordinary exit isn't "cut off"; more errors caught (a short GFF, the
  age, the named saves' folder, Restore Youth's icon). (Tests: `test_settings_with_a_bom`,
  `test_recompiled_exit_is_not_cut_off`, `test_a_plain_quote_is_text`,
  `test_scores_never_cut_the_wrong_way`, `test_every_rule_has_its_box`.)

**Docs**
- A review of every document for the new rules: the patch notes, FEATURES (the whole system shock
  table), the guide, the README and DEVELOPMENT's memory figures. Screenshots retaken: the ten
  priest spells, the inventory panels, the default party's inventory, the Options tab.

## Pull request #80 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/80))

Obsidian Edition 2.12.5 ([release notes](release-notes/v2.12.5.md)).

**New**
- **The Effects screen names Enlarge's damage:** ENLARGED (+90% DAMAGE), 10% a level of its
  caster. The inventory's DAM lines have no room for it. The game lets only one Enlarge on a
  creature. (`GameData.enlarge_level`, `STATS_ENLARGE`, DSCLOG's `EF_CHARGES`. Seen in DOSBox:
  Cermak's Enlarge on Gerakis. Test: `test_enlarge_level`.)
- **The Effects screen names the armour spells' AC:** BARKSKIN (AC 3), FLESH ARMOR (AC 8),
  MAGICAL VESTMENTS (AC 3), from the effect's level as the game has it (a psionic power's is the
  psionicist level). (`GameData.armour_spells_ac`, `GameData.effect_level`. Seen in DOSBox on
  K'ratchek and Cermak. Test: `test_armour_spells_ac`.)

**Fixed**
- **Whirlwind's swept creatures lose their next turn, and it strikes once a round:** a swept
  creature still took the turn that swept it, and a turn lost was a round of 2d8 spared. Now it
  strikes everyone in it at the start of each round, before anyone acts, and those who fail lose
  that round's turn. As it is cast, one swept that has yet to act loses that turn. (`WW_PASS`,
  `WW_GATE`, `SWEPT_NOW`; DEVELOPMENT-CONTENT § The game's spells. Found and seen in DOSBox:
  K'ratchek's Whirlwind on the arena's sligs.)

**Docs**
- A review for 2.12.5: Whirlwind's timing, and the Effects screen's Enlarge and armour lines.
  Links, anchors and pictures checked; `whirlwind.gif` still right.

**Tests**
- `test_to_hit_effects`: THAC0 with each effect the game's attack counts and none from another
  creature's.

## Pull request #79 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/79))

Obsidian Edition 2.12.4 ([release notes](release-notes/v2.12.4.md)): Dark Sun Recompiled, from pull
request #78, in a release.

## Pull request #78 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/78))

**New**
- **The Loader reads the game when it runs as Dark Sun Recompiled**
  ([its page](https://github.com/daaki85/darksun-recompiled); a `dsun` process; its memory found
  by the BIOS date, or by the mark `DARKSUN-RECOMPILED`).
- **The Loader can start that program instead of DOSBox:** `dsloader launch --recompiled <path to
  dsun.exe>` remembers it (`--dosbox` goes back), and `launch`, `play` and **Start the game** run
  it with the game's folder and the mod's `dos` folder. (README, "Other ways to start".)

**Fixed before release** (a review after main, with 2.12.2, was merged in)
- The game's own DOS `DSUN.EXE` was taken for the program on Windows when the mod was unzipped in
  the game's folder. A program found or named must be a Windows PE or an ELF.
  (`launch.native_program`. Test: `test_the_games_dos_program_is_not_it`.)
- Which one runs is said as the game starts, in the dice log, and the closing line goes by what
  was started, not the settings. (`launch.started_line`, `launch.STARTED`. Test:
  `test_started_and_closed_lines`.)
- The memory search's chunks overlap by the longest mark, so the mark is found across two. (Test:
  `test_recompiled_mark_across_two_chunks`.)
- `--recompiled` and `--dosbox` save with `launch.update_settings`, so a settings file locked for a
  moment is never saved over with only that change. The test's stand-in programs are Windows
  programs.

## Pull request #77 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/77))

- The changelog names pull request #76.

## Pull request #76 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/76))

Obsidian Edition 2.12.3 ([release notes](release-notes/v2.12.3.md)).

**Fixed: DSCLOG** (from a code audit, and Haste and Slow)
- **Haste and Slow show in the attacks a round:** a fight doubles a hasted character's attacks and
  halves a slowed one's, but neither the DAM lines nor the Characters tab did. The inventory's line
  also showed one half-attack as one a round; a slowed character's reads `0.5x1D8+6` now.
  (Whatever the rules. `GameData.weapon_hits`, DSCLOG's `SPEED_HALVES`, `gamepatch` `dam_half`.
  Seen in DOSBox: Gerakis hasted 5 attacks a turn, K'ratchek 10. Tests: `test_hasted_and_slowed`,
  `test_dam_half`.)
- **View Character's damage matches the fight's:** it left out a non-magical weapon's penalty for a
  weaker material (2 less in wood, 1 in bone, stone or obsidian). The dice log's damage line names
  it (`-1 bone`). (`VIEW_MATERIAL`, `game.MATERIAL_DAMAGE`. Found in DOSBox with Cilla's bone long
  sword. Tests: `test_view_dam_weak_material`, `test_weapon_damage_weak_material`.)

**Fixed: the Loader**
- **The arena's Ring +1 shimmers as soon as it is found:** it got its own picture a pass later, and
  an inventory opened between kept the plain ring's. Every item the Loader makes now gets its own
  picture as it is made. (`icons.fit`, `icons.COPY_OPEN`. Test: `test_its_own_icon_at_once`.)
- **K'ratchek's second chatkcha throw a round shows with weapon specialization on** on the
  Characters tab. (Test: `test_kratcheks_chatkcha_with_specialization`.)
- **The no-window Play mode carries on after an error,** as the window has since 2.12.1, and DOSBox
  closing mid-read counts as a disconnect. Other errors go to `play.log` once each.
- **settings.json is never replaced by a single change:** a failed read (a Windows lock from an
  antivirus or a backup) gave empty settings, and a save then lost every option. Such reads now
  retry and then raise, and the Options tab says if a save can't be made. (Test:
  `test_a_locked_settings_file_is_never_saved_over`.)
- **A roll half seen no longer spoils the next:** dice collected when the rest was missed are
  dropped. (`_forget_partial_rolls`. Test: `test_half_seen_rolls_dropped_when_rolls_are_missed`.)
- **An error after a pass's rolls keeps those rolls,** with one line in the dice log once a kind,
  and the item lists' gate is released whatever happens. (`_after_rolls`. Test:
  `test_rolls_kept_when_a_later_step_fails`.)
- **The arena's Ring +1 never loses an item record:** the backpack's list is checked first. (Test:
  `test_no_list_keeps_the_record_free`.)
- Smaller: the dialogue pane stays at 3,000 lines and a portrait shown many times is one image;
  the game folder is kept as a full path.

**Docs**
- A review for 2.12.3: weaker materials' penalties in the guide, Haste and Slow in FEATURES, the
  backstab example's `-1 bone`, and `docs/dicelog.png` retaken (K'ratchek's chatkcha at 5/2).
  Links, anchors and pictures checked.
- **A thri-kreen Mind Warrior who presses EXIT on the weapon window gets the chatkcha;** KITS.md
  said the club. (Test: `test_mind_warrior_exit`.)

## Pull request #75 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/75))

Obsidian Edition 2.12.2 ([release notes](release-notes/v2.12.2.md)).

**Changed**
- **A thri-kreen Mind Warrior may take the chatkcha as its weapon spec,** as well as its class's
  melee ones: 3/2 throws a round, 2 from a warrior class's 7th level. (Weapon specialization.
  `restrict.allowed_kinds`, DSCLOG's `KINDS_ALLOWED`. Test: `KindsAllowedTests`.)

**Fixed: DSCLOG**
- **The in-game combat log no longer flickers in a fight:** many drawings go to the game's second
  screen and are then flipped, and the panel was only on the first. DSCLOG now puts it on the
  screen about to be shown. (`FLIP_PANEL`, `FLIP_SITE`, `gamepatch` `panel_flip`;
  DEVELOPMENT-SCREENS § The combat log in the game. Seen in DOSBox: 40 seconds of an arena fight
  at 43 frames a second, no frame without the panel but under a game window. Test:
  `test_panel_flip`.)
- **A fight runs as fast with the combat log up as without it:** a rectangle drawn over the panel
  was drawn in parts, each its own flip waiting for the monitor, so a monster's turn took a sixth
  longer (1.03 seconds against 0.89). It is drawn whole now. (Seen in DOSBox: 0.95 seconds with the
  panel against 0.83 without, within how much turns vary.)

**Fixed: the Loader**
- **Shillelagh and Spiritual Hammer shimmer on the party's figures,** as the Flame Blade does,
  drawn whole in the game's animated colours. (`spritegear.SPELL_WEAPONS`. Seen in DOSBox. Tests:
  `test_spell_weapons`, `test_named_weapons`.)
- **A new Poisoner with the short sword as its weapon spec starts with a short sword in each
  hand,** not two daggers. One made before, still New, has both made short swords. (Tests:
  `test_poisoner_daggers`, `test_poisoner_spec_changed`.)

**Docs**
- **Three animated pictures, recorded in DOSBox:** `docs/combat-log-live.gif` in the Loader README,
  `docs/whirlwind.gif` anew in FEATURES and `docs/magic-glint.gif` under What the party wears,
  grabbed at about 48 frames a second and scaled whole.
- A review for 2.12.2: the patch notes' line on magic gear's glow, and the guide's attacks-a-round
  table gains a thri-kreen Mind Warrior's chatkcha. Links, anchors and pictures checked.

## Pull request #74 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/74))

**Release**
- **Obsidian Edition 2.12.1**: the version is 2.12.1, with its notes in `release-notes/v2.12.1.md`.

**Fixed: the Loader** (from an outside audit of 2.12.0)
- **"In a fight" means a fight again.** The Loader read only the game's `IN_COMBAT`, which stays up
  while the party walks spread out, and since 2.12.0 spreads the party after every load and fight,
  it took much of ordinary walking for a fight. Stuck walkers weren't set going again, the Battle
  Dancer's dances and Wild Fighting weren't ended with the fight, defilers were rolled for scrolls
  outside fights, and the combat log's fight state, Tab targeting and an item report's "In a fight"
  went wrong. It now also asks the game's own fight test (the fight state's +19h, as stealth already
  did). (`GameData.in_combat`, `stuckwalk`. Test: `InCombatTests.test_spread_out_isnt_a_fight`.)
- **Settings never lost.** The settings are written to a temporary file and put in place (retried a
  moment on Windows), so a read never sees a half-written file. One that can't be read is set aside
  as `settings.json.bad`, not saved over with only the keys a caller had (the combat log panel's
  level could wipe every option and the game folder). The window and the thread reading the game no
  longer lose each other's changes: each read-modify-write is one step. (`save_settings`,
  `SETTINGS_LOCK`, `update_settings`. Test:
  `test_settings_saved_whole_and_never_over_an_unreadable_file`.)
- **The party table and the dice log keep going** after an error they didn't expect. Both refresh
  loops schedule the next pass whatever happens, and say the error once in the dice log (`Loader
  error in ...`, with the file and line) instead of stopping for the rest of the session. (`_tick`,
  `_dice_tick`.)
- **The combat log's header shows the arena count between fights again.** In the slave pens and the
  arena it had shown the round (the fight above), and where the game's numbers weren't in memory
  (most of the time outside a script's run) it showed nothing. The Loader keeps the count it last
  read, and says `Arena fights: ?` until it has read one. (`combatlog.Panel.update`. Seen in DOSBox:
  `Arena fights: 1` in the pens, the party spread out. Tests: `test_arena_count_in_the_header`,
  `test_arena_count_remembered_for_the_header`.)
- **Defilers' scrolls in every fight.** The rolls were kept for the session by area, slot and name,
  so a later fight's defiler in the same place under the same name (the arena's) got none until a
  game was loaded. They are forgotten as each fight ends. (Test: `test_again_in_the_next_fight`.)
- **No spell arrows in armour:** a Spellarcher in armour casts nothing, and now weaves no arrows
  either. (`restrict.no_spells`. Test: `test_make_in_armour`.)
- Smaller: DOSBox is never left paused (the item gate resumes it if the look after pausing fails);
  DOSBox's process handle is closed on a disconnect, a reconnect and a failed try, and the mouse
  wheel's hook comes off when its dice log closes, where each reconnect added another (`_located`,
  `_drop_guest`, `WheelHook.stop`); the combat log's short attack line for an attack that hits on
  anything but a 1, which showed the long line (test `test_attack_that_hits_on_anything_but_a_1`);
  Dispel Magic's caster level for the 6th-level priest spells (202-210), whose spheres it gave none
  (`effect_caster_level`, `PRIEST6_MASKS`).

**Docs**
- **Psionicists' and thieves' weapons and shields,** checked against the game's item lists and
  `restrict.allowed` for each mix of classes (a human's save holds only its present class, so the
  game's own check sees that one). A psionicist alone: daggers, bone and obsidian short swords,
  clubs, chatkchas and bows, and no shield (the rule takes away the axes, picks, gythka and long
  swords the lists allow). With another class, also the maces, metal short sword and slings that
  class's lists allow, and a leather shield with a fighter, gladiator, ranger or cleric class. A
  thief of any kind: leather shields only, and a multiclass one only with one of those classes. The
  guide's and FEATURES' tables and the guide's psionicist section say so (#71's review had taken
  maces and slings from every psionicist, and both tables gave a psionicist alone a leather shield).
- **Documentation review** (the audit's remaining documentation findings, each checked against the
  code): the front page and the Loader README say the patched game writes page 1's saves and every
  character too, and that a save with the new items wants the Loader; "nearly every" rule change has
  a switch (not the keys or the game's fixed bugs); the Loader README lists `dosbox_dicelog.conf`
  and the Memory tools' layout and search files; FEATURES says its bold switch names are short forms
  of the Options tab's sentences, lists all five thieving switches, gives the thief table's cap (95)
  beside its 99s (the guide too), says which items Alagorn has no story for and when a defiler is
  rolled for; the guide's Options table gains Wake of the Ravager and says kits and starting gear go
  to new characters; KITS: a Twin-blade can't use a bow or the staff sling; DEVELOPMENT:
  `--window-scale` 1 to 4, and a line on each module the sections don't come back to; the combat
  log's HANDOFF no longer points at a section that's gone; the README's level-cap range and Linux
  line made exact (Windows only for the `.bat` files and Start the game; no macOS). Reports now list
  the combat log's level with the other switches (`launch.SWITCH_DEFAULTS`).
- Smaller: the Loader README has three built files, not one, what a report holds, and to read one
  before posting it; FEATURES' Kalzith caption no longer claims a quarter off at CHA 20 (15%); KITS:
  no spell arrows in armour; DEVELOPMENT's party-in-view and camera notes say `IN_COMBAT` is also
  set while the party is spread out; the patch notes put the half-giant and thri-kreen lines under a
  Races heading; the 2.12.1 notes and the front page lead with the fight fix; the Loader README says
  the panel's round once. Screenshots checked: none out of date.

## Pull request #73 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/73))

- **Obsidian Edition 2.12.0**: the version is 2.12.0, with its notes in `release-notes/v2.12.0.md`,
  for #70 to #72.

## Pull request #72 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/72))

**Docs**
- **ITEMS' Every mundane armour piece gives each piece's AC:** how many points it takes off AC 10,
  read from the game's item types (the byte that gives plate's 3, 2 and 2 and the shields' 1); helms
  0, or 1 with Helms give AC 1.
- Small pass after the review: the guide's "Making a party" points to KITS' Choosing a kit instead
  of repeating it; its Starting gear links KITS' for the kits' weapons; the Shinobi's Effects screen
  picture is in KITS only; each class's dual-class line links the kits that rule a change out. KITS:
  a shorter introduction, no quoted Loader strings in The kits in play and Changing class.

## Pull request #71 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/71))

DSCLOG's image 61,040 bytes (about 4.4 KB of the helper's room spare).

**New**
- **U and I close their screens again,** as M does the overhead map. U on the inventory or I on USE
  still switches screens (the game's), the other key then closing it. The game reads a key with a
  peek and then the read, so the key is kept only on the read: kept on the peek, I on USE switched
  and was then read as Escape. (DSCLOG's `MAP_KEY`, `OVERHEAD`, `MK_READ`. Seen in DOSBox: U, I and
  M each opening and closing their screens, U and I switching between USE and the inventory.)
- **The whole party in view** as a game starts or loads and after each fight, as the game's 5 does;
  6 still gathers it. DSCLOG calls the game's own spreading routine on the map, out of a fight,
  after a load or a fight's end (not after 6). A 5 put in the BIOS's keyboard buffer was tried first
  and never read, as the game reads keys only in its keyboard interrupt. (Options: "The whole party
  in view", on; `party_spread`. `gamepatch.PARTY_SPREAD`, DSCLOG's `SPREAD_LOAD`, `SPREAD_GATHER`,
  `SPREAD_TICK`. Seen in DOSBox: the "Kalzith test" save loading with the whole party in view, a new
  game's opening fight ending so, 6 gathering it and it staying gathered. Test:
  `test_party_spread`.)

**Fixed**
- **No "(15 CHARGES)" on a magic item's power on the Effects screen** (Shadowseeker's Detect
  Invisibility). The game adds an item's power as it does a permanent effect, leaving a stray value
  in its record's charges byte, and charges showed unless the spell's own time was permanent. They
  show now only for a spell lasting a number of uses or a timed effect, as Armor's. The same rule
  gives the dice log's and the Characters tab's effects. (DSCLOG's `EF_CHARGES`, `NS_CHARGES`;
  `game.effects_left`. Tests: `test_item_power_has_no_charges`, `test_time_and_charges`.)
- **Two Whirlwinds on the map both turn.** DSCLOG kept one funnel, so with two each one drawn
  replaced the other and only the last drawn turned. Each Whirlwind has its own entry now, up to
  four, emptied at each round's start and each cast. (`WT_TABLE`, `WHIRL_PICK`, `WHIRL_TICK`,
  `WHIRL_CLEAR`. Seen in DOSBox: two Whirlwinds in Scar's fight, both funnels changing in each of 9
  frames in a row.)
- **Restore defaults keeps the combat log on** (the Loader set it off).

**Docs**
- The new work in FEATURES (Controls: M, U and I; The whole party in view), the guide's Controls and
  Effects screen rows, PATCH-NOTES, the Loader README's summary and Effects screen, and DEVELOPMENT
  (M, U and I; the whole party in view; charges on the Effects screen; Whirlwind's funnels; the
  helper's room).
- **Full documentation review** (with reviewers per document group). PATCH-NOTES: a stray
  parenthesis, the two game-speed lines merged, the party-in-view line's switch, four more kit
  changes. Root README: name history dropped, a note on what is new since 2.11.0. Loader README:
  Fastest "nearly every frame", GOG's 7,000 cycles, the jerky-walking text, the Controls and Game
  speed summaries, the defaults sentence. FEATURES: M, U and I simpler, Whirlwind's two funnels,
  item powers' charges, the old Healer's cosmos spells (moved from KITS). DEVELOPMENT: stale names
  (`PP_EXTRA_DRAW`, no `WP_TWO`), history trimmed, two missing contents entries. The guide: the
  whole party in view in the Options table, psionicist weapons as the game's lists allow, Gythka +2
  and Kreenfang marked as the mod's, no place name in the Poisoner's text, multiclass kits in the
  Kits intro, Magic's "Effects" renamed "Status effects". KITS: the Loader's once-a-second check and
  version history out. No helm has Gaze Reflection, so the item-power example is Shadowseeker's
  alone. Screenshots checked: `options.png` opens only sections that have not changed.
- **Doc review, part 3.** The guide: Quality of life's running-the-game table and Loader-window list
  cut to two paragraphs linking the README; the New items weapon table loses its "who can wield it"
  column (each class's list says that); the Spellarcher's arrows added to Other magic items; casting
  when hit explained once, under Initiative, and linked from the preserver, Worth knowing and KITS.
  ITEMS: **Every mundane armour piece**, a new table of plain armour and shields with who sells and
  carries each (read from the game's data, as the weapon table).

## Pull request #70 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/70))

DSCLOG's image 60,528 bytes (4.9 KB of the helper's room spare).

**New**
- **The whole party walks at full speed on the map,** shadows and dust on, at the default 20,000
  cycles (in the slave pens 249 to 278 pixels a second, where it was 152 to 175; the leader alone
  about 220 to 260). When a frame would be drawn late the next one isn't drawn: the game's step for
  everything still runs, and the frame after draws what moved in both. DSCLOG keeps a schedule of 70
  frames a second on the game's clock, in place of the map frame's two far calls; fights draw every
  frame. An earlier try that caught up only figures' animation steps did nothing, as the "think"
  that starts a figure on its next square runs once a frame. (Options, under Game speed: "Walking at
  full speed on the map", on, from the next start; `steady_pace`. `gamepatch.STEADY_PACE`, DSCLOG's
  `PROBE_PACE_PASS`, `PROBE_PACE_DRAW`, `FAR_PACE`; DEVELOPMENT-SCREENS § Game speed. Seen in
  DOSBox: walking, two arena fights with no frame skipped, the view scrolling with frames skipped in
  the arena and in the pens at 6,700 cycles, and the arena-to-pens change, each followed by a full
  redraw that matched the screen but for braziers and figures mid-step. Tests: `SteadyPaceTests`,
  `test_steady_pace`.)

**Docs**
- Steady pace in FEATURES' and DEVELOPMENT's Game speed, the requirements table's Fastest, the
  guide's Game speed and Options rows, and the patch notes. FEATURES' Game speed has
  `steady-pace.gif`, the whole party walking in the slave pens with steady pace off and on side by
  side (recorded at 70 frames a second, shown at half speed).
- **FEATURES' pictures shown a second, measured** by counting the game's page flips while the whole
  party walks in the slave pens: about 37 with steady pace off, about 27 with it on (it said about
  40). DEVELOPMENT says how to count them.
- Doc review: the patch notes' two game speed lines made one (the old one gave the party's walking
  to the cycles setting), and four "fixes" of the mod's own bugs taken out of them (shadows lost in
  big fights, figures vanishing, the Weapon Merchant and Jark, the spell arrows' level: the
  Spellarcher's line says it); FEATURES' bug table gains "Out of memory in OEOpenGraph" and Slay
  Living's description; the guide's backstab (it said STR's bonus is multiplied, the game's own
  rule) and its hit-die kits (two, not three); the gladiator's AC line as the game's own;
  HOW-THE-GAME-WORKS gains "How fast the party walks", linked from FEATURES' Game speed;
  DEVELOPMENT's room in the helper and memory map brought up to date; ITEMS' acid table without
  Dunesong (bows are never at risk); the README's feature list and troubleshooting mention steady
  pace; Jark is in Kel's caravan (#64's entry said Tyr).

## Pull request #69 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/69))

- **Obsidian Edition 2.11.0**: the version is 2.11.0, with its notes in `release-notes/v2.11.0.md`,
  for #68.

## Pull request #68 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/68))

**Changed** (kit balance)
- **Arcanist** keeps two preserver spells a turn but loses its spell slot more at each level; the
  **Scholar** has it now. (`kits.slots`, DSCLOG's `PROBE_SLOTS`.)
- **Mind Warrior:** the psionicist's d6 hit die, not a d8; its tenth fewer PSP stays.
  (`kits.hit_die`, `PROBE_HIT_DIE`, `PROBE_CR_DIE`.)
- **Rescuer:** its cures heal 1 more a die anywhere, not only under the open sky, and it has 2 more
  Move in a fight. It may no longer hold a shield (a new one's starting shield is left behind).
  (`KIT_MOVE`, `KIT_FORBIDS`, `kits.forbids`.)
- **Wilderness Avenger:** +1 to hit and damage against anything, not only undead. Its cost, a druid
  slot fewer at each level, became light armour only for a while, which cost a druid nothing; it is
  now **no healing spells**. Cure Light, Serious and Critical Wounds, Blood Flow, Heal and Water of
  Life are kept from it as it is made, in the routine giving a priest its spheres' spells and for
  the 6th-level two (a level up marks no priest spells), and one in an older save loses them when it
  is loaded. In return its Cause Light, Serious and Critical Wounds do 1 more a die. (`KIT_EXTRA`,
  `AV_HEAL`, `AV_KNOW`, `AV_GRANT`, `NS_PRIEST_KNOWS`, `kits.avenger_heals`, `AV_CAUSE`, the dice
  log's `_harm_bonus`; `LIGHT_KITS` and `KIT_LIGHT` dropped. Seen in DOSBox: a new Avenger with no
  cures known and the causes known, one through a level up given no cures, and its Cause Wounds'
  extra die.)
- **Assassin:** a backstab's multiplier one more, x3 to x6. (`STAB_TIMES`, `kits.backstab_times`.
  Seen in DOSBox: x5 at 9th level.)
- **Poisoner:** every melee weapon hit poisons, not a shot or a throw, the target's save as before;
  no −1 to hit; its weapon spec the dagger or the short sword only. The poison works only on damage
  with no spell or power behind it, as the poison's own damage comes back through the same routine
  and, once a fight no longer stopped it, poisoned again and again. (`KIT_SHOT`, `PROBE_ATTACKS`,
  `PROBE_POISON`, `KIT_POISON_KINDS`, `kits.POISONER_KINDS`. Seen in DOSBox: hits, one save each.)
- **Healer:** no ranger of air, earth or fire, either way of DUAL (the game already bars a cleric
  from becoming a cleric or druid, and a druid a cleric). After DUAL the sphere menu is WATER ONLY
  for a Healer, as the DUAL window keeps a ranger's row open while the water ranger is allowed.
  (`DUAL_BANS`, `DUAL_SPHERES`, `PROBE_SPHERE`. Seen in DOSBox: DUAL both ways, and which classes
  the game itself bars.)
- **Spellarcher:** spell arrows only into an empty quiver (else nothing is made and no slot used),
  and kept there as a Flame Blade is kept in the hand. The drop at the party's feet is gone.
  (`PROBE_TAKE`, `QUIVER_KEPT`; `ARROWS_DROP`, `Attempt.drop` removed. Seen in DOSBox: all four
  cases. Tests: `QuiverTests`, and the kits' slots, move, to-hit, poison and kinds tests and the
  Rescuer's shield for the rest.)

**Docs**
- Doc review: the dice log's hit-die line names the Battle Mage and Arcanist (the Mind Warrior has
  the psionicist's die now), and the guide's hit points list them; the item report's example names
  Inixhide as the log does; the guide's Spellarcher entry is flavour and a link, as the other kits'
  are; the patch notes' new spells by level, and Kalzith's scrolls said once; a repeated clause gone
  from the Military Scout's row; long lines wrapped. Screenshots checked: none out of date.

## Pull request #67 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/67))

- **Obsidian Edition 2.10.0**: the version is 2.10.0, with its notes in `release-notes/v2.10.0.md`,
  for this pull request and #64 to #66.

## Pull request #66 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/66))

**Docs**
- The patch notes no longer say a save already in Teaquetzl stays without the Weapon Merchant (the
  user's save has him); the fix is under Bug Fixes instead.

## Pull request #65 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/65))

**Fixed**
- **Dunesong counts at the Bowyer's archery target.** Script 178 counted the bows in hand by their
  objects, the game's three. A jump to code at the script's end now counts Dunesong as Phrain's Bow
  is counted, and the rest of the jumped-over command is a filler command, so the script still reads
  command by command and nothing moves (the roll is still where the dice log looks).
  (`bowyer.with_dunesong`; DEVELOPMENT-SCREENS § The Bowyer's archery target. Seen in DOSBox: a
  centre shot with Dunesong from 15 squares, and the Bowyer's arrows.)

**Docs**
- Dunesong's line in the patch notes is its row in the Items table (no second bullet under World),
  and FEATURES' New items says it counts at the Bowyer's target, linking to the target's rules.
- From a review of the docs: the front page's first caption describes its picture (round 7,
  K'ratchek's turn, a Slig's hits on Cermak); DEVELOPMENT says "a few hundred" of the game's
  changes, not a count that goes stale; #64, #63 and #61 have their merge dates; the patch notes say
  they follow the repository (a change since the current version is in them before its release); the
  front page's "What's new" has the latest release only; and the tests workflow runs when only
  `CHANGELOG.md` or `release-notes/` change, as the link tests read them.
- `creation-store-recall.png` retaken: the creation screen as it is now, KITS where it showed the
  WEAPON SPEC label the mod no longer draws (the spec is picked after DONE).

## Pull request #64 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/64))

**New**
- **The scripts' own ability checks in the dice log.** 13 conditions compare the scripts' random
  command with an ability of the character acting instead of using the ability check command:
  Chahl's CHA (181), the chains' STR (76), secret doors' INT - 10 (69)... The Loader finds them in
  its GPLDATA.GFF and evaluates each with the roll and the score of whoever's turn it is: `Daaki CHA
  check: 0-19 = 15, always made (CHA 20) -> success`. (`scriptchecks.py`, `_script_check`;
  DEVELOPMENT-SCREENS § Ability checks in the scripts' conditions.)
- **Nineteen of the game's magic items shine** in their icons, as the Parting Staff's gem does: the
  Chameleon Gloves, the Hornblade, Cahulaks +1, Dag's Dagger, the Terror Blade, Blackmace, the
  Shimmer, Drake and Silk Armor, Tanelyv's and Grey's arms and legs, the Living Cloak, the Golden
  Torque, Light of Dawn, El's Ring and the Orb of Knowledge. Their metal, gems or leather take the
  water's or the fire's cycling colours, every other pixel (a leaf's greens for the silk and the
  cloak). Cahulaks +1, Light of Dawn and El's Ring shared their icon with plain items, so they get
  pictures of their own (BMP 2653-2655). (`icons.SHINE`.)
- **The Bowyer's archery target in the dice log** (script 178): each shot's roll, what it needed
  (DEX - distance / 2), the distances from the target and the Bowyer (the game's distance command
  ported) and the result: a miss, a ring, the centre, and whether it earns the arrows. (`bowyer.py`,
  `bowyer.distance`, `GameData.thing_square`, `things_of`; DEVELOPMENT-SCREENS § The Bowyer's
  archery target.)

**Fixed**
- **The Weapon Merchant was missing from Teaquetzl's market** (since 1.2.0), and Jark from Kel's
  caravan. The game's routine reading an object's records keeps them in a table of 80 and gives up
  on an object with more, and the person's map entry was then freed: the merchant had 89 records
  with the Loader's 11 weapons, Jark 95 (the game's largest has 74). The table has room for 120 now.
  A save already in the village has him too (checked in the user's save). (`gamepatch`'s
  `records_*`. Test: `test_records_fit` keeps every object the Loader adds under it.)

**Docs**
- **Documentation review.** FEATURES has a section on the magic items' icons (and its Graphics intro
  and contents say so), DEVELOPMENT how `icons.SHINE` works and its three own pictures,
  HOW-THE-GAME-WORKS the Bowyer's archery target (the three bows its script names: not the Loader's
  Dunesong, as ITEMS now says), the Loader README's summary the gear's glint and the icons' shine;
  the patch notes' long dice-log line is three.

## Pull request #63 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/63))

- **Obsidian Edition 2.9.0**: the version is 2.9.0, with its notes in `release-notes/v2.9.0.md`, for
  this pull request and #62.

## Pull request #62 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/62))

DSCLOG's resident part 56,496 bytes (7.1 KB of its 64 KB segment spare).

**New**
- **Charges left, in the dice log and on the Effects screen.** Each charge used says how many are
  left (`Improved AC on Slig: one charge used, 7 left`, "none left: it ends" for the last). The
  charge routine's 2d4, a bare "Dice: 2d4" line, is told by its arguments. On the Effects screen the
  name under the pointer says them too, for any effect with charges: IMPROVED AC (10 CHARGES),
  MIRROR IMAGES (3 CHARGES), REFLECTED IMAGE (2 CHARGES); not for a permanent effect.
  (`count_charges`, `_overlay_charge`; DSCLOG's `EF_CHARGES`, `EF_TEXT`, `REFLECT_ENTRY`,
  `ns_reflect_entry`.)
- **A charge used floats over its creature,** as "Miss" does: "Armor: 7 left", "Reflected Image: 2
  left", "Armor ends", in light blue, from each charge line of the dice log. The image-lost line
  says what is left too. These stay 3 seconds, and a "Miss" or a spell's name doesn't take their
  slot. (`labels.CHARGE_INK`, `_charge_spells`, `CHARGE_FOR`, `priority`.)
- **Up to four floating labels at once** (were two). (`LBL_SLOTS`, `labels.SLOTS`.)
- **M opens the overhead map,** and M again closes it. (DSCLOG's `MAP_KEY`, `OVERHEAD`.)
- **A Shinobi's read languages on the Effects screen,** under its kit: `READ LANG. 40%`.
  (`RL_LINE_OF`, from the Loader's `READ_LANG`.)
- **Scar's henchmen carry bone axes,** dropped when they die. (`worldgear.GIFTS`, object 229.)
- **The Parting Staff shines** as the game's magic weapons do: its gem's blues in the water's
  cycling colours. (`icons.SHINE`, its own icon, picture 2157.)
- **A Battle Dancer can't use a shield,** as it already fought with long swords and bows only.
  (`KIT_FORBIDS`, `kits.forbids`.)
- **A scroll's answer on the inventory screen.** What the item box says (YOU LEARN THE SPELL, YOU
  ALREADY KNOW THIS SPELL, YOU CAN NOT READ THE SCROLL, THAT IS NOT A SHINOBI SPELL, CANNOT LEARN
  FROM THIS ITEM, the tome's) was never seen: the game writes it to the line under the paper doll
  while the box runs, and nothing written then reaches the screen. DSCLOG keeps the text and for 5
  seconds puts it on that line, and tells the game's mouse handler the pointer moved, so it shows
  with the mouse still; as the game's own messages there, it stays till the pointer is on something
  else. (`BOX_SAID`, `LINE_SAID`, `LINE_CLEARED`, `BOX_NUDGE`.)

**Changed**
- **A backstab's dice log line shows the sum:** `+2 backstab (the dice 1 x3 = 3)`, not `(the dice
  x3)`. The die's 1 is already in the line, so the backstab adds 2 more.
- **The helper's big buffers moved to the HMA:** the dice log's ring, the combat log panel's
  picture, the shadows' cache, the text buffer, the shadows' spans and the dust's last places
  (57,800 bytes), with A20 on, else a block of their own. Upper memory has about 57.8 KB free in one
  piece, from 0.5 KB. (DSCLOG's `FAR_INIT`, `FAR_SEG`; `textlog.TBUF_SEG`,
  `combatlog.TSR_PANEL_OFF`. Seen in DOSBox: the dice log, the text log, the panel, shadows, dust
  and the arena's fight, with and without `UMBPLUS.COM`.)

**Fixed**
- **A Shinobi couldn't learn from a scroll:** clicking the spell's picture in the scroll's box did
  nothing. The game makes the picture a button only for a class the item type allows, and the scroll
  type allows wizards only. (`SCROLL_USE` passes a scroll for a Shinobi.)
- **Spells cast by weapons were at caster level 6** whoever struck. A Spellarcher's spell arrows now
  go at the archer's preserver level (a 2nd-level archer's Shocking Grasp did 1d8+6); a weapon's own
  spell stays at 6. (`ARROW_LEVEL`.)
- **A backstab multiplied the round's second attack too** (an off-hand one after a miss): the game
  multiplies while fewer than two attacks are made. With the dice-only rule, only the first.
- **Immunity in the dice log.** The HP line matched hits to the HP lost from the first, so a hit the
  creature was immune to (a slime and a club) was counted and the next one dropped. The hits that
  sum to the loss are taken, and each passed-over hit gets "takes none of the N damage: <reason>".
  (`_hits_matching`.)
- Smaller: "Bracers/Defense+4" ran past the item box (now `Bracers/Defns`); a preserver's scroll
  line in the dice log showed the last Shinobi's read-languages roll, left in the header
  (`INT_LEARN` clears `LEARN_READ` now); the cooked vulture used on a party member no longer says it
  is tough and bland (`vulture.use` removed; eating it is the game's, with the meal's rest from the
  Loader as before).

**Docs**
- The Loader README's In the game has a section for the Effects screen (kits, a Shinobi's read
  languages, charges under the pointer, the click fix) with `effects-charges.png`, and Names over
  figures a picture of a charge label beside a "Miss" (`floating-charges.png`). FEATURES gives M its
  own Controls section; the guide's screens table gains the scroll's answer.

## Pull request #61 ([merged 2026-10-25](https://github.com/daaki85/darksun-obsidian-edition/pull/61))

**Release**
- **Obsidian Edition 2.8.0**: the version is 2.8.0, with its notes in `release-notes/v2.8.0.md`, for
  this pull request and #60.

**New**
- **The glow in each item's own colour.** The game's palette cycles four runs on the map (1-5 green,
  6-10 violet, 11-15 the water's blue, 240-248 fire), the same in every area's palette but for a
  step.
- **A cloak from the front no longer looks held.** The cloak is fitted from the human woman's, which
  swings out to one side as she walks; on the elves and the half-elf man that showed as a dark panel
  by one hand.
- **The glow on every magic item a figure shows:** armour (in place of picking its light shades,
  which the human and half-elf women's dark clothes hadn't), bracers, cloaks, helms, boots and
  belts. After a magic piece is drawn, every fifth pixel of those it changed, on a diagonal, is
  marked in `GLINT` (every ninth on a piece as large as a cloak; at least every other on a small
  one). (`spritegear.sparkle`.)
- **The pointer at the desktop's speed in a window.** Captured, DOSBox 0.74 moves the driver's
  pointer a game pixel for each desktop pixel the mouse moves, three screen pixels in the usual
  window: too fast and coarse for placing items.
- **Magic weapons, shields and armour glow on figures:** a weapon or shield with a plus or a power,
  and magic armour (Kreenfang and the Flame Blade keep their own colours). (`sprites.worn`,
  `spritegear.MAGIC`, `MAGIC_ARMOUR`.)
- **Shadows kept for figures whose pictures the game lets go of.** In the arena's fight every figure
  but one had its picture out of the game's cache as the floor was drawn, so no shadow was drawn
  (`SHADOW_OF` won't load one mid-drawing).
- **The game's music buffer in upper memory: 12 KB more of the 640 KB.** A research build of the
  helper logged the far heap's calls: 134 KB of it is taken before the main menu and kept, never
  freed or resized through a load, an area change and a fight (music 12,001 bytes, sound effects
  24,001, tables).
- **28 KB more upper memory.** DOSBox 0.74 starts its upper memory block at D000h, but C800h-CFFFh
  is RAM too, and DOSBox's own tables use only its start.

**Changed**
- **Removed, to free the helper's memory: scrolling by holding the right button.** The right button
  goes straight to the game again; the wheel's drag stays. (`MOUSE_EVENT`; `SCROLL_RIGHT`,
  `DRAG_START` gone; `scrolling.DRAG_MIDDLE` the only bit.)
- **Removed: rings under all the enemies.** Only the enemy chosen with Tab gets one (or none), and
  an older `"rings": "all"` reads as the chosen one's. (`rings.ring_table`.)
- **Removed: the combat log strip below the map.** The panel over the map (L) is as it was.
  (`PROBE_STRIP`, `PROBE_PALETTE`, `PROBE_COLOURS`, `STRIP_*`, gamepatch's eight `STRIP` patches and
  `combatlog.STRIP` gone.)

**Fixed**
- **A shorter pause after picking up or putting down an item.** The pointer stood still 56-103 ms
  (85 on average, in the user's save, at 20,000 cycles) while the game redrew the inventory: its
  mouse handler only queues the moves, and the pointer is drawn again once the redraw is done.
- **A shorter wait for the Loader after picking up or putting down an item.** Each time an item
  moves on the inventory screen the helper has the game stand still until the Loader brings the
  THAC0, saves and thief skills up to date, so an item just put on counts. (`STATS_SYNC`.)
- **The Loader's own magic items glowed blue on figures.** Each item's object and icon were looked
  up in the game's SEGOBJEX.GFF, which has none of the Loader's items (the Hayneedle, Kreenfang,
  Thornwall, Inixhide, the Ashen Robe...), so they fell back to blue whatever their icon.
  (`sprites.item_glow`.)
- **No thief skill above 95.** With **Thief skills from AD&D's table** a skill had no ceiling: a
  13th-level thief with DEX 24 showed move silently 121 and pick pockets 117.
- **The pointer put back where it was as screens changed,** not in the middle. A video mode set
  (each scene's start, the menus, loading a save) leaves the pointer at the right edge, and it was
  put in the middle; it goes now where it was last seen. (`MOUSE_SET`, `CINE_MOUSE`, `CINE_WHERE`,
  `MP_X`, `MP_Y`, `MOUSE_EVENT`.)
- **"Regains 1 HP from Fire attack."** A hit point regenerated (CON 20 or more) just after a spell
  or attack was put down to it, as the spell's healing was tested first; regeneration is tested
  first now.
- **"Script: a creature changes sides" in runs of a dozen** as a fight's scripts set up: request 18
  shows only with "Show unlabelled rolls". (`REQUESTS_SHOWN`.)
- **An archer's pointer with shots left.** The game marks a combatant's attacks as all made once
  they are, but the pointer's missile test refused any count but none, so after a shot that killed
  it showed "can't shoot", though a click still shot.
- **Cermak's Arcanist slot at the start of a new game.** The game fills the party's spell slots
  before the Loader makes Cermak an Arcanist, so the USE screen showed WIZ 1/2 until his first rest.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #60 ([merged 2026-10-24](https://github.com/daaki85/darksun-obsidian-edition/pull/60))

**New**
- **A pointer in scenes, and a click skips one.** The intro, its logos and the game's other scenes
  had no pointer, and only a key skipped them. DSCLOG draws the game's own arrow there, as the
  scenes' unchained VGA mode is one the mouse driver's pointer can't draw in: ICON 6001 and its
  colours, read from the player's game by the Loader into `dos\POINTER.BIN` (without it a plain
  arrow of DSCLOG's own), each colour as the scene palette's nearest. A button pressed ends the
  scene as a key does. (Options: "A pointer in the intro and the game's other scenes", on;
  `scene_pointer`. `scenepointer.py`, DSCLOG's `CINE_STEP`, `CINE_END`; DEVELOPMENT-SCREENS § The
  pointer in scenes, and where it starts.)
- **The pointer starts in the middle and moves as far up and down as across.** The game's ranges
  left the pointer at the right edge after a video mode set, and it is put in the middle there; the
  driver's 16 mickeys a pixel up and down are made 8, as across, from the game's start. (Options:
  "The pointer starts in the middle of the screen", on; `mouse_start`. `MOUSE_SET`, `MOUSE_INIT`.)

**Changed**
- **The freeze report keeps 16 records, every 32nd timer strike** (were 32, every 16th; the same 4
  seconds), to make room in upper memory for the above.

**Docs**
- The guide's tables list the scenes' pointer and the pointer's start and speed; the README's
  troubleshooting says how to let go of the mouse (Ctrl+F10) and the freeze report's 4 samples a
  second; the patch notes' pointer line reads better; a picture of the pointer in scenes in
  FEATURES.
- **Organisation and trims.** The Loader README gathers Troubleshooting, Known issues, the reports
  and Reporting a problem under **When something goes wrong**; its How the game works and Item
  tables indexes become one **More pages** list; the character card's contents move into **The
  Characters tab**; the game window's command-line options and the practice program move to
  DEVELOPMENT.md; a shorter Requirements, game window and item-report text. FEATURES follows the
  Options tab's order, with the game's bugs fixed last. The guide's quality-of-life table is grouped
  (screens, controls, saves, running the game), and its intro points to the features page for the
  rules.
- **A line-by-line audit of every page.** Corrected: the guide's backstab multipliers (×4 at 9-12,
  ×5 at 13, as the game has them), DEVELOPMENT's room in upper memory (1 paragraph spare, not 54),
  its patch count (some 320), the helper's added item types (30), Negative Plane Protection's record
  (211) and the timer's rate (about 120 a second); the switch the 6th-level priest spells come with
  named everywhere (**New wizard spells**, with AD&D's class tables). Repeats removed (the README's
  save note, its window size in the start steps, the combat log's EMS aside, the guide's note on the
  game's own party's spells); "started from the Loader" and "pointer" used throughout; unclear
  sentences rewritten (preservers' starting spells, the pens' new people, the Items and Kits
  headers); DEVELOPMENT's contents list the pointer section; every page's prose wrapped at 80
  columns.

## Pull request #59 ([merged 2026-10-24](https://github.com/daaki85/darksun-obsidian-edition/pull/59))

**Release**
- **Obsidian Edition 2.7.2**: the version is 2.7.2, with its notes in `release-notes/v2.7.2.md`,
  listed on the front page with the others.

DSCLOG in upper memory: 54 paragraphs spare (none before).

**Fixed**
- **Sunstroke ends the caster's turn.** Its record kept Hold Person's aim (several targets: after
  the first the spell stayed armed and the turn went on); it has Slay Living's now (one creature),
  as meant. (Seen in DOSBox: Grog's Sunstroke on Scar, and the turn passed straight on.)
- **Wall of Thorns counts a monster's armour.** For anyone but a party member the game had seen
  attacked, it took the sheet's base AC, 10 for an armed man, as the game adds armour in an AC
  routine the damage's code can't call. It now counts as that routine does: each worn item's plus
  and its type's AC, a fifth of a gladiator's level and the DEX adjustment; spells' AC still not.
  The ring is 64 entries (65 before) to make room. (DSCLOG's `THORNS_AC`. Seen in DOSBox: Scar, in
  leather arm and chest armour with DEX 17, took 8 + AC 5 = 13, not 18; his henchmen 18 (AC 10); the
  party their own ACs.)
- **The Look box's AC counts a monster's armour.** Before anything had attacked a monster, the Look
  box (and its `Look:` line) gave its sheet's base AC, as Wall of Thorns did. It now counts as the
  game does. (`GameData.counted_ac`, the Loader's twin of `THORNS_AC`; `_worn`. Seen in DOSBox:
  Scar's Look box AC 5 at the fight's start, where it said 10; his henchmen 10.)
- **Room in upper memory.** DSCLOG's shadow table is a bit for each of the game's 520 things, not a
  byte, and its 46 extra names are kept in 16 bytes each (15 letters at most), padded to the game's
  25 as they are copied: 455 and 414 bytes saved. (`SHADOW_TAB`, `shadows.casting`, `EXTRA_NAMES`,
  `NAME_KEPT`, `PROBE_NAMES_FILL`. Seen in DOSBox: all 46 names in the game's table as before, and
  the figures' shadows drawn.)
- **Heartseeker's and Slay Living's descriptions.** A creature that saves still takes half of 4d8, 2
  to 16: Heartseeker's said only that it slays, and Slay Living's said 3 to 17 (the book's 2d8+1,
  not what the game rolls). (`spelltexts.py`, SPIN 209 and 137; the spellbook line, FEATURES, the
  guide and the patch notes say so.)

**Docs**
- **Documentation review.** The Loader README lists the Options tab's Wake of the Ravager section;
  DEVELOPMENT describes how `THORNS_AC` now counts a monster's AC; How the game works keeps the
  manual's column the manual's (Slay Living); two sentences in the patch notes untangled. Two
  screenshots retaken: `options.png` (with the Wake of the Ravager section) and Heartseeker's tile
  in `new-priest-spells.png` (its new description).

## Pull request #58 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/58))

**Release**
- **Obsidian Edition 2.7.1** (pull request #57): the version is 2.7.1, with its notes in
  `release-notes/v2.7.1.md`, listed on the front page with the others.

## Pull request #57 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/57))

**New**
- **Wake of the Ravager found in more places, or chosen:** any folder beside Shattered Lands (GOG
  Galaxy installs them as `Dark Sun` and `Dark Sun 2`, so a Galaxy install was never found), GOG's
  usual folders on any drive, and a folder inside each. The Options tab's new **Wake of the
  Ravager** section says where it was found, or that it wasn't, and **Choose its folder...** keeps
  one installed anywhere else. Before, the Loader looked beside Shattered Lands only and said
  nothing, so a player whose copy was elsewhere saw the Loader's own icons without knowing why. GOG
  Galaxy's `Dark Sun` is among the places the Loader looks for Shattered Lands too.
  (`wotrart.find_resources`, `wotr_dir`, `launch.GOG_SUBDIRS`.)

**Changed**
- **Monsters' powers named in the dice log** by what their records do: the effect a power puts on
  (`Paralysing attack`, `Disease attack`, `Entangling attack`, `Poison attack`), else its damage's
  kind (`Fire attack (6d6 fire)`), else its number as before. The dice rolled before the save
  against one that puts on an effect are its duration, and the log says so (`Paralysing attack:
  lasts 7 rounds unless saved against (2d4 = [4 + 3] = 7)`; the Red Slaad's 182 was `special attack
  182: 2d4 = [4 + 3] = 7`). (`game._power_name`, `POWER_EFFECT_NAMES`.)

**Docs**
- Wake of the Ravager described as what it is for nearly every player, the game GOG sells with
  Shattered Lands, rather than an optional extra (the Loader README's requirements, FEATURES, the
  patch notes); the patch notes list this pull request's changes as coming after 2.7.0.

## Pull request #56 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/56))

**Release**
- **Obsidian Edition 2.7.0** (pull requests #55 and #56): the version is 2.7.0, with its notes in
  `release-notes/v2.7.0.md`, listed on the front page with the others.

**Changed**
- **The 6th-level priest spells' descriptions in the game's own style:** the name, then a terse line
  with damage as ranges ("Inflicts 8 to 64 pts of damage"), and no level or sphere, which none of
  the game's own descriptions give. Harm's text no longer says the target is diseased: the Diseased
  effect here lowers nothing, it only keeps a STR lowered by something else from coming back (see
  Cause Disease in HOW-THE-GAME-WORKS); the docs say so too. The priest spells screenshot retaken.
  (`spelltexts.py`.)

**Docs**
- A fourth review. The root README says what the repository has beyond 2.6.0 (the patch notes
  already did). FEATURES moves Harm's Diseased note out of its table row into the spell's notes,
  linked to Cause Disease. DEVELOPMENT gives the 6th-level priest spells' description chunks (SPIN
  203-211), the game's description style and the box's size. The patch notes' memory figure matches
  the latest measure (85 KB). Links, anchors and every screenshot checked; none out of date.

## Pull request #55 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/55))

**New**
- **6th-level priest spells** (with **New wizard spells**, slots with AD&D's tables): Heal, Harm,
  Blade Barrier, Wall of Thorns and Sunstroke (cosmos: druids and Healer clerics), Fire Seeds
  (fire), Heartseeker (earth, water), Water of Life (water) and Whirlwind (air), spells 202-210.
  Each is built on a record the game already casts (Cure and Cause Critical Wounds, the priest's
  Wall of Fire, Hold Person, Flame Strike, Slay Living, Lend Health) with its own changes.
  (`NS_PATCH`.)
- **The 6th-level priest spells closer to the books and Wake of the Ravager.** Wall of Thorns does
  8 + the creature's AC (at least 1), not 1d10 + 8; a monster's AC is its sheet's, a party member's
  as the game last worked it out, and the dice log shows it. (`THORNS_AC`, `PROBE_AC`, `AC_SEEN`.)
- **The ground pictures checked live:** the blades and the thorns standing as walls, Fire Seeds'
  fireball, and Whirlwind's entry holding the dust (8403) after its cast, the other entries back to
  the game's.
- **Spheres:** Blade Barrier is air's, Wall of Thorns earth's and Sunstroke fire's, not the
  cosmos's; the cosmos keeps Heal and Harm. (`P6_MASKS`, `game.PRIEST6_MASKS`: `AIR_MASK`,
  `EARTH_MASK`, `FIRE_MASK`.)
- **Whirlwind lasts and sweeps:** built on Stinking Cloud (a lasting ground entry whose spell acts
  each round on those in it) with Sand Storm's picture: 1d4 rounds and 1 more from 7th level, 2d8
  crushing each round, a save vs spell for half. (`ns_templates`, `AREA_NEW 8`.)
- **Whirlwind's funnel, drawn once, blocking sight:** its own picture, a funnel of dust in ground
  ellipses, object 8433 in the Loader's SEGOBJEX copy. (`whirlart.py`, `NS_SETUP`.)
- **Sunstroke's heat:** 1d4 of fire at the start of each round on a creature Sunstroke holds.
- **Backstabs multiply the weapon's dice only:** a hit's dice are added again for each time past the
  first, in place of the game multiplying the whole damage by x2-x5. (Options: "A backstab
  multiplies the weapon's dice only", on; `backstab_dice`. `RULE_BACKSTAB`, DSCLOG's
  `RULE_HI_BACKSTAB`, `STAB_ROLL`, `STAB_TIMES`.)
- **Acid Arrow burns each round.** In the game its acid never burned after the hit: the routine
  spending an effect's charges was called for Acid only on chance events, and Acid Arrow's time was
  a timer on the game clock that only ended it, with no charges to spend.
- **Names over figures: no leftover sliver.** When a label went away the game's redraw of its
  rectangle drew only whole bytes of the VGA planes inside it, so a label starting mid-byte left its
  first columns on the map (a "[" left on the sand after Prayer's cloud). The rectangle is widened
  to whole 4-pixel columns. (`LABEL_ERASE`. Seen in DOSBox: Prayer cast in the Scar fight, and
  nothing left after it.)
- **Walls of their own.** Blade Barrier, Wall of Thorns, Fire Seeds and Whirlwind each have an entry
  of their own in the table of ground pictures, so walls no longer share Wall of Fire's (a Wall of
  Fire cast while a Blade Barrier stood made both burn as Wall of Fire).
- **Pictures on the ground for the 6th-level priest spells,** Wake of the Ravager's: Blade Barrier's
  circling blades and Wall of Thorns' thorns (its objects 8432 and 8425, added to the Loader's
  SEGOBJEX copy and recoloured; without it the fire wall tinted grey or dark brown), Fire Seeds'
  fireball (8405) and Whirlwind's Sand Storm dust (8403). (`wotrart.area_chunks`.)
- **Names over figures.** A spell's name floats over its caster for 1.5 seconds as it is cast (any
  cast: the party's, the monsters', a weapon's on a hit), and "Miss" over the target of an attack
  that missed, in the game's font with a dark edge; at most two at once.
- **Spellarcher spell arrows.** Outside a fight, a Spellarcher's USE screen has a button for each
  touch spell it knows (Burning, Chill, Shocking and Vampiric Arrows) in the row of class abilities,
  the first where a priest's Turn Undead is, the rest beside it.
- **Three new magic items** (with New items on), each with its own icon: the **Girdle of Back
  Defense** (no enemy gets the bonus for attacking its wearer from behind, nor a backstab; the Troop
  Leader carries it), the **Golden Girdle of Urnst** (AC 3 better against long and short swords;
  Wyrmias) and the **Amulet of Magic Resistance** (15% magic resistance; it never shatters; sold by
  Kel).
- **The Crusader and Mind Warrior have expertise in one melee weapon spec of their choice** (with
  weapon specialization), as the Battle Mage has: 3/2 attacks a round, 2 from 7th level, picked on
  the weapon window after DONE.
- **The dice log names a refused cast's reason** (`can't cast Fireball there: no line of sight`;
  DSCLOG's `AIM_SITE`) **and the scripts' requests** (`Script: random monsters come`; `REQ_SITE`,
  all 20 named, from the yuan-ti project's notes on the game).
- **The Wanderer halves fire and cold spells' damage,** as Resist Fire and Resist Cold do (it had
  their saves only), at the game's own test of what a creature is guarded from; the log says
  `(halved: Wanderer)`. (DSCLOG's `WANDER_DMG`.)
- **The Myrmidon's initiative is 2 worse,** a second drawback beside its −4 against charms; the
  log's initiative line names it. (`PROBE_INIT`.)
- **Cleric spells against the manual.** HOW-THE-GAME-WORKS has a table of every cleric spell: the
  manual's text, what the game's records and code do, and what the log shows.
- **The log names a protection that halves a spell's damage.** The game halves a spell that is all
  fire under Resist Fire or Protection from Fire, all cold under Resist Cold, all electricity under
  Protection from Lightning, fire or cold under Fire Shield: `takes 9 from Fireball (halved: Prot
  Fire)`.
- **A party member's ability scores changing** get a line once the change holds: `Cilla's STR 12 ->
  16` (Strength, Remove Curse, Raise Dead's CON, the Tome).
- **Psionic powers checked against the manual.** A table in How the game works, power by power: the
  manual's text, what the game's code does (Detonate hits only its target, no save; Cell Adjustment
  heals 2 and cures nothing; Biofeedback gives AC -1 and takes no damage off; Inertial Barrier makes
  missile attacks miss and does nothing else; Psionic Blast takes real HP down to a fifth; Control
  Body and the dominations are a charm; Mass Domination's record targets one creature) and what the
  log shows.
- **The psionic defence in the dice log.** An attack mode's target rolls 1 to its defence twice,
  each over the attacker's power check d20, to resist; the log skipped both rolls: `Gerakis's
  psionic defence: d6 = 5 and 6, both need over 4 (the attacker's power check d20) -> resisted`.
- **What more powers do, in the log's effect lines:** Inertial Barrier (missile attacks miss),
  Energy Containment (no damage from fire, cold, electricity or magic alone), Synaptic Static,
  Enhanced Strength (STR 24, read from the game's stats code), Adrenalin Control (STR + 1d6) and
  Share Strength's lender (STR - twice the amount); Detonate's 1d10 named "Detonate's blast".
- **Detonate's blast on an item in the dice log.** The power (a daggoran's too) destroys the
  target's worn item with the lowest item +10h (under 6) on a 1d20 under 15 less its plus (one of a
  stack), and nothing showed it. (DEVELOPMENT-SCREENS § Detonate's blast on an item.)
- **Find in the dice log and the dialogue.** A box above each (Ctrl+F): every match (any case)
  highlighted, the one shown in amber with `n of N`, Enter / **Next** and Shift+Enter / **Previous**
  round the end, Escape to clear; details hidden aren't searched, and the log stops following its
  newest line while a match is shown. (`viewer.Viewer._find_bar`, `palette.TEXT_PAIRS`. Tests:
  `tests/test_find.py`.)
- **The psionic power check in the dice log.** `Zulak uses Graft Weapon: power check d20 = 14, needs
  11 or less -> it fails`, with the score's parts (`16 CON - 5 Graft Weapon`), and the Synaptic
  Static contest when someone else keeps it up.

**Changed**
- **Axes and maces on figures look like the game's own:** the axe was a thin stick in its metal with
  a hollow hook for a head (it read as a fork), the mace the same with a thin diamond.
- **Level cap by XP.** The levels-up-to-10 rule is now an XP cap: a class goes up while its next
  level needs no more than 749,999 XP, the whole of it for a character of one class, an even share
  for each class of a multiclass character (as the game shares out XP), and for a human who changed
  class the cap less what its old classes' levels needed (the game starts the new class at 0).
- **Weapons spells make count for weapon specialization,** for its attacks, to-hit and damage alone.
  The Flame Blade counts as a long sword (AD&D's scimitar, which Athas hasn't), Shillelagh as a
  club, Spiritual Hammer as a mace (the war hammer's nearest). (DSCLOG's `SPEC_KIND`,
  `specialize.spec_kind_of`.)

**Fixed**
- **Whirlwind lasts a round a caster level,** as AD&D has it (11 rounds or more for a priest who can
  cast it), not Stinking Cloud's shape of 1d4 + 1 for each 7 levels. (`NS_PATCH`.)
- **Three of the game's script bugs mended,** always on, in the Loader's copy of GPLDATA.GFF: each
  re-points one trigger or call to the handler it was meant to have, applied only where the script
  holds the expected bytes. (`scriptfixes.py`; DEVELOPMENT-CONTENT § The game's script bugs.)
- **The Spells tab's 6th-level priest spells** were described from the records they are built on, so
  Harm read as 3d8+3 draining, Heartseeker as 4d8 halved by a save, Wall of Thorns as 1d10+8, Heal
  and Water of Life as next to nothing, Sunstroke without its heat and Whirlwind as "can't move".
- **The USE screen's spell slots line ran off its panel** with a 6th spell level: the panel shows
  the slots of the level and list on show only (`SPELLS LEFT`, then e.g. `PRI 2/1`: `WIZ` on MAGE,
  `PRI` on CLERIC, none on PSIONIC).
- **Spell arrows fade at the game's own rest.** They faded only at a script's rest request and the
  vulture meal; camping at a fire ring runs the game's rest routine without one.
- **Spell arrows (and Pick Pockets, and the vulture meal) work with the party spread out.** The
  Loader's fight check read a flag of the game's that stays up while the party walks uncollapsed
  with no one to fight, so it answered "can't be made in a fight".
- **The pointer on a spell arrow button lights that button.** Turn Undead's handler, which the
  buttons beside it share, lit and unlit the frame at Turn Undead's place, so the Vampiric Arrows
  button lit the Burning Arrows one; the button's own place lights now, as its press already did.
- **Every magic item of the Loader's shines.** The game shines a magic item by cycling palette
  colours (11-15, the water's, and 224-255, fire's among them), so icons tinted in colours it
  doesn't cycle stood still: the Chill, Shocking and Vampiric Arrows, Shadowseeker, the Cloak of
  Protection +1, Pehtucl's ring, the Girdle of Back Defense, the Amulet of Magic Resistance, the
  Veiled Robe, the Cloak and Boots of Elvenkind and the Golden Girdle of Urnst.
- **A Fireball no longer floods the dice log.** The filter for `random(low, high)`, kept for psionic
  ranges, also recorded the eleven picture-point calls a spell burst makes, so a Fireball filled the
  ring ("148 rolls came too fast to record").
- **More room in the helper's upper memory:** 3.8 KB of the upper memory block spare rather than 224
  bytes, for features to come. Its text buffer is 2 KB, not 4 (251 bytes came between two of the
  Loader's reads at most), and the descriptions of the new spells, Pick Pockets and the spell arrows
  are SPIN chunks in the Loader's copy of RESOURCE.GFF, not the helper's text. (`spelltexts.py`,
  `PROBE_CHUNK_ID`.)
- **An item the game destroys gets its crash-log report.** The game frees a destroyed item
  (Detonate's blast, acid, a script) by zeroing only the first word of its record and linking it
  into the free list: its type and name stay.
- **A party's thief skill roll goes to its best member.** Where the game asks the whole party (a
  trap's find/remove traps, all 50 trap triggers with the arena prisoner's among them, and hear
  noise by the wagon), its pick was to keep the highest chance but kept the lower of a best starting
  at 0, so the first party member always rolled.
- **Random monsters come in the right numbers and can't crash the game.** The scripts' request for
  random monsters (8; scripts 99 and 106) sends 2 x the party's strength / the monster's, 1 to 6,
  but took the strength of the slot after the one picked: from the next region's record after the
  tenth, and 0 after the last in regions 6, 13, 14, 27, 39, 40, 44 and 255, a division by 0 that
  ends the game ("Divide error").
- **A likely cause of figures vanishing and then a freeze.** A freeze report (2.6.0, 49 minutes into
  an arena trip) had the game's picture row decoder unpacking a figure's picture from garbage: never
  meeting the row's end, it copied on from its 5,408-byte buffer over the code after it, itself
  included, and the game's data segment was then overwritten by its own stack.
- **Magic items shine in a shop.** The palette's colour cycles turn only in the map's main loop,
  when the timer asks; a shop, opened from a conversation, runs its own event loop and waits in the
  game's wait for an event, and neither turned them, so its items stood still.
- **Freeze reports with the game's memory overwritten.** The report found DSCLOG only through the
  dice log, which had lost the game with its data segment. It now finds DSCLOG by its signature and
  the game's load segment from its DOS block, so where the game was still shows.
  (`freeze.find_header`, `load_from_block`.)

**Docs**
- **Reviews, pictures and the since-2.6.0 list:** the patch notes' list of what comes after 2.6.0
  brought up to date; the XP cap, the 6th-level spells and the new switches in the Loader README,
  the guide's Options summary and the dice log table; Wake of the Ravager as an optional install; a
  link and anchor check over every page (none broken, no picture unused).
- A review of every page.
- A second review: the patch notes say which of their changes come with the next release, not 2.6.0,
  and name the Battle Mage's, Crusader's and Mind Warrior's weapon expertise (the release steps now
  drop that line); the README's known issues add the vanishing figures and freeze, and lose a
  class-letter table that repeated its sentence; spell arrows left on the ground fade at the first
  rest after they're picked up (KITS, and the guide, whose paragraph is rewritten).

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #54 ([merged 2026-10-21](https://github.com/daaki85/darksun-obsidian-edition/pull/54))

**Release**
- **Obsidian Edition 2.6.0** (pull requests #52 and #53): the version is 2.6.0, with its notes in
  `release-notes/v2.6.0.md`, listed on the front page with the others.

## Pull request #53 ([merged 2026-10-21](https://github.com/daaki85/darksun-obsidian-edition/pull/53))

**New**
- **A warning when the game's memory runs low.** With the map open, below 24 KB spare the dice log
  says so and to save and restart soon (a new start has it all back); once, then again only after it
  has recovered. If upper memory had no room for the overlay buffer (another DOSBox, other settings)
  the dice log says that too, and crash reports say where the buffer is. The helper's build fails if
  what it puts in upper memory outgrows it, and its signature is now `DSCLOGva`. (`UMB_NEED`, also
  checked by a test.)
- **Enlarge shows in the damage line.** A melee hit by someone under Enlarge reads e.g. `(1d8 = [5]
  +12 STR 24) x140% Enlarge (level 4)`, as the game works it out: the dice, weapon and STR bonus
  together, times 100% + 10% a level, rounded down, before a backstab's multiplier. The level is the
  caster's level for the spell (as Dispel Magic weighs it), each Enlarge on the attacker added up.
  Missiles don't get it. (DEVELOPMENT-RULES § Enlarge's dice. Tests: `test_dicelog.py`.)
- **Crash reports tell the game's memory.** "Out of memory in OEOpenGraph" is the game failing to
  open the map's view again, which needs one block of 60,000 bytes from the game's heap each time.
  On the map with a long game's save there are about 53 KB of DOS memory to spare (the unmodded
  game: 57 KB). Making characters over and over uses none of it (35 made in a row). What used it up
  in a 97-minute game isn't known yet, so the Loader reads the heap every few seconds, and a crash
  report gives the last reading and the session's lowest. (`heapcheck.py`.)

**Changed**
- **The arena's count of fights shows by itself,** with no button: between fights in the slave pens
  and the arena (regions 29h and 2Ah) the combat log panel's header says `Arena fights: N` (docked
  or expanded); in a fight it says the round, and anywhere else (the party escaped) it's gone. The
  header's **A** is dropped, as the game's own A key turns animations on and off, so a button A read
  as a key it wasn't. This replaces #52's A button; `combat_log_arena` is no longer saved.
  (`combatlog.ARENA_REGIONS`.)

**Fixed**
- **The game ran out of memory in long sessions** ("Out of memory in OEOpenGraph"). Each time the
  map's view opens it needs 60,000 bytes in one piece from the game's heap, and with the map open
  only about 53 KB were left over. The game's largest block for good, the overlay manager's buffer
  (32,992 bytes), is now in upper memory, and DSCLOG lays out its own blocks so the room is in one
  piece. With the map open about 86 KB are now left over (the unmodded game: 57 KB). Without upper
  memory the game takes it from its heap as before. (DSCLOG's `PROBE_OVR_BUF`, the patch
  `overlay_umb`. Tests: `test_dsclog.py`.)
- **Dinos's talk lost its upper box after the vulture meal:** the XP's words go to the narration
  window, which takes the portrait and his words away, and his menu came back under an empty screen.
  After the XP his script sets his portrait again and he says a line before the menu.
  (`pensasks.AFTER_MEAL`. Tests: `test_pensasks.py`.)
- **The Characters tab showed noise for items before the game had its item tables** (at the main
  menu or creating characters: "Wooden GF╨╢...", "Attacks: 120 a round with item 2"). Items count
  only when every name reads as plain text; until then a card shows no equipment and the sheet's
  attacks, and an item's name is never noise. (`GameData.items_readable`, `game.plain_name`,
  `item_name`. Tests: `test_equipment.py`, `test_names.py`.)
- **An item couldn't be put down on another in a character's pack** (the swap was refused, for any
  items and anyone's pack; the original game swaps them). The cause was an object numbered 2563 in
  the Loader's copy of SEGOBJEX.GFF, the slave pens' weapon rack with Thornwall on it, numbered so
  since 1.2.0: with any object of that number in the file, the game refuses the swap. The rack is
  now 2599, and 2563 is never used. In a save that has already been to the pens, the game leaves the
  old rack off the map; renumbering it in the save doesn't bring it back, as something else in the
  save still names 2563. (`worldgear.PENS_RACK_OBJECT`, `NOT_AN_OBJECT`. Tests:
  `test_worldgear.py`.)
- **The Ashen Robe (and the Veiled Robe) gave no AC under the Armor spell.** Worn on the chest, the
  robe's plus went into the game's armour value, and the Armor spell puts its 6 in that value's
  place, so the robe added nothing. Its plus now counts with the AC's other bonuses, as a ring's,
  still only without armour on the arms, legs or head. (DSCLOG's `PROBE_RING_AC`;
  DEVELOPMENT-CONTENT § Robes. Seen in a save: AC 0 with the robe off, -1 with it on, the spell and
  a shield on. Tests: `RobeTests` in `test_dsclog.py`.)
- **The Trustee stood still for good after a load** (the game's own way too). His rounds are his "no
  orders" script, which runs only while he has no order, and a walk is an order that ends when he
  gets there. A save made while he walked keeps the order but not the way, so once loaded he stood
  with it forever, and after a talk he was busy for good. The Loader takes such an order back
  (anyone with a no-orders script, standing still with a walk order for 30 game seconds, out of
  fights), and his script sends him on; the dice log says "Trustee walks on". (`stuckwalk.py`. In
  the save it was found in, he walked his rounds again about 20 s after loading. Tests:
  `test_stuckwalk.py`.)

## Pull request #52 ([merged 2026-10-20](https://github.com/daaki85/darksun-obsidian-edition/pull/52))

**New**
- **The arena's count of fights, on the combat log panel's A.** A button left of the header's L puts
  "Arena fights: N" in the header instead of the round (lit while on, saved as `combat_log_arena`;
  not in the strip, which has no buttons). N is the game's own count, its global number 12, which
  script 3 adds one to each time the party leaves the arena after a call, however many waves came;
  the announcer's speech changes with it (for the first five fights, the 1000th and the 5000th).
  (`GameData.number`, `game.NUMBERS_PTR`, `ARENA_FIGHTS`, `combatlog.arena_rect`, `arena_line`.)

**Changed**
- **The Healer has the sphere of the cosmos, and is a water cleric's only** (with kits on). The
  cosmos's spells are those every druid casts and no cleric (the game gives Cure Serious and
  Critical Wounds, Raise Dead, Neutralize Poison and the other common 4th and 5th-level priest
  spells to druids alone, so a Healer's extra healing on the two cures never came into play). A
  Healer knows them from the start and casts them at its cleric level. On the KIT page its row is
  greyed unless WATER is the sphere marked, the sphere stays while the kit is taken, and taking
  WATER back takes the Healer back too, as choosing another class does. After DUAL the kit menu
  offers it to a water cleric only. A Healer from an earlier version keeps its sphere, and the
  Loader marks its element's cosmos spells known when the game is loaded (the game marks a priest's
  spells only when the character is made or changes class), with a line in the dice log. KITS.md,
  the guide and the patch notes say so. (DSCLOG's `HEALER_COSMOS`, `HEALER_BARRED`, `EL_CLICK`,
  `DK_BANNED`; `kits.spell_spheres`, `kits.dual_kit_banned`, `kits.cosmos_spells`. Tests: the water
  cleric's DUAL menu, `cosmos_spells`.)

**Fixed**
- **More of the game's own bugs,** whatever the Options (from yuan-ti's notes, each checked in the
  code): Negative Plane Protection saved as against Vampiric Touch, which allows no save, so it
  never worked (`NS_NPP`); Cloak of Bravery's +4 against fear asked for a mark no spell had (now on
  the fear spells, Spook's record too); Absorb Disease gave 1d6 STR too; Bless and Aid's check for
  an enemy beside an ally measured from (x, x); a berserk or confused member could end it on the
  monsters' side (`NS_SIDE`); the fire elementals' resistances were swapped; the computer cast its
  walls as a single point (`NS_WALL`). The dice log's saves show Cloak of Bravery's +4 and name
  Negative Plane Protection's.
- **The Loader's changes to the game's item lists could land mid-load.** The game gives every item a
  new number as an area loads, and a change made across that, from numbers read before it, could cut
  an item out of its list (a likely way for an item to vanish without a trace). Every write to the
  item lists now goes through one gate: it waits until the game's free lists, area and item table
  have stayed as they were for 60 ms, pauses DOSBox, looks again, and writes with the game held
  still; anything changed and the pass's item writes wait for the next. Kalzith's stock and loot,
  the arena ring, buyback and defilers' scrolls had no such check before, and the others' left a gap
  between the look and the writes. Rolls and queues taken before a refused write are kept for the
  next try. (`itemgate.py`, `GuestMemory.write`, `ProcessMemory.suspend`, `resume`, `itemgate.hold`;
  DEVELOPMENT § Changing the game's item lists. Tests: `test_itemgate.py`.)
- **Item reports through a change of area.** The game renumbers every item then, and this pull
  request's first way of telling a load (most items gone at once) took it for one and started
  afresh, so an item lost in the change passed unseen. A bulk change now waits until the new numbers
  hold still, matches old items with new by owner, slot and item, and reports one with no match;
  under half matched, or nothing settled in time, is a load. A number another item took over is no
  longer read as the old item still there. (`itemwatch._settle`, `renumbered`, `BULK_MATCH`,
  `BULK_WAIT`.)
- **Item reports, smaller:** a later save of the same party loaded no longer reports the items it
  doesn't have (the clock moving on more than `CLOCK_JUMP` with the party somewhere else is a load;
  a rest, with the party where it was, isn't, so an item gone as the party rests is still reported:
  `GameData.party_position`); money is taken for a sale only when it rose by what a shop pays for
  the item (its price, or 60%), so a purse picked or a reward no longer hides a vanish; an item
  handed over is remembered for 10 seconds (`ARRIVED_KEEP`), so a busy Loader doesn't report it.
- **A new character's gear fitted while the weapon window was still up:** the class restrictions,
  the kit's gear and the fuller starting gear now wait for it, as the starting weapon did, since a
  slow pick could leave a Titan Mind without its weapon, or a Ravager's two hands holding different
  weapons. (`_weapons_asked`.)
- **The arena's next wave** (a new fight by the fight flag, the clock not yet past `FIGHT_GAP`): the
  Poisoner's poison ready again, the rounds counted from 1, and the last wave's monsters' ACs
  forgotten, as the dances and Wild Fighting already were. (`_new_fight`.)
- Smaller: Pick Pockets could lose an item taken from someone when the thief's backpack list
  couldn't be made (the list is made first now); the freeze report after 2.3 hours of play listed
  only a few places once DSCLOG's count of them wrapped past 65535 (all 32 now); the combat log
  between fights kept a roll's detail lines arriving in a later batch than the line they belong to
  when that line was left out; `Play Dark Sun (in-game rolls).bat` said only "Something went wrong"
  when a crash report couldn't be written, and says why now, with how DOSBox closed.

**Docs**
- **Crash, freeze and item reports** are one section of the README, with a table of when each is
  written and what it holds (what all three share said once); closing DOSBox's window while the game
  runs is a crash report, as the code has it.
- **Draft release notes for 2.6.0** (`release-notes/v2.6.0.md`) and a "Coming in 2.6.0" line on the
  front page; How the game works notes that clerics never have the common 4th and 5th-level priest
  spells.
- How the game works has **the arena's count of fights:** what the announcer says at each count, the
  1000th trip's gifts and the 5000th's war won. DEVELOPMENT.md has the item gate, the item watch's
  area changes and the rings and cloaks of protection; the README's item reports say what an area
  change does.
- The damage numbers over creatures are off the README's known issues: seen in fights with the panel
  collapsed, docked and hidden since the panel's slowdown was fixed; the README says the expanded
  panel covers those under it. `tests/test_doclinks.py` checks the docs' links and the README's "How
  it works" links.
- **The original game's code, checked against yuan-ti's findings** (a new engine for the game,
  github.com/CalvinRodo/yuan-ti): How the game works has the psionic defence as the code has it
  (only defence modes already raised count, their cost paid again) and Enhanced Strength's and the
  Dominations' costs (worked out as used, not 0); armour with a magical power rolls against acid
  (always coming through). Hold Undead never held the living: every spell's targets are sifted
  before it lands, and the guard the mod added there stays; the claim is gone from the docs. A
  target turning to face its first attacker each round and the backstab multiplying only the first
  attack were confirmed in the code.
- **Features and rules, a page of their own** (`obsidian-edition/FEATURES.md`): the README's rule
  changes, character customization, expanded features, new content, graphics, controls, bug fixes,
  saves and game speed (about 1,800 lines) moved there, the README (about 1,000 lines) keeping
  installing, running, the Loader's window and the dice log, with a line pointing to the new page;
  every link to the moved sections points there now.

## Pull request #51 ([merged 2026-10-19](https://github.com/daaki85/darksun-obsidian-edition/pull/51))

**Release**
- **Obsidian Edition 2.5.0**: the version is 2.5.0, with its notes in `release-notes/v2.5.0.md`,
  listed on the front page with the others.

**New**
- **Item reports:** the Loader watches the party's items and, when one is gone from the whole party
  for two seconds, saves `crash-logs\item-<time>.txt` (the item, who had it and where, what its
  record says now, the game's time and region, the fight, the party's items before and after, the
  switches, and the dice log's and dialogue's last lines) and says so in the dice log, so a vanished
  item can be looked into as a crash is.
- **Four more magic weapons** for the kits that had too few (the dagger fighters, the archers, the
  thri-kreen), each with its icon, its name in DSCLOG's table (now 39 names) and a story from
  Alagorn. **Hayneedle,** a bone dagger +1 (a water cleric's too), early: hidden in Merzol's
  haystack in the slave pens with his sack of ceramic pieces.

**Changed**
- **Weapon specs picked after DONE** (with weapon specialization on): the creation screen's WEAPON
  SPEC pages are gone.
- **Claws cut:** the game makes every unarmed attack crushing, so a creature crushing weapons can't
  hurt (the mastyrials) took nothing from a thri-kreen's claws.
- **A Shinobi learns its own spells from scrolls too** (with kits on): it first reads the scroll, a
  d100 against its read languages, and then, with the rule for INT on, learns the spell at INT's
  chance.
- **A Pick Pockets button for thieves** in place of Thieves' Tools: on the USE screen, where a
  priest's Turn Undead is, a character with thief levels has a purse (outside fights; a cleric/thief
  has both, the purse beside Turn Undead, and Turn Undead alone in a fight).
- **Coins from a picked purse grow with the thief:** 2 to 5 ceramic pieces for each thief level (a
  4th-level thief takes 8 to 20) instead of 2 to 5 in all.

**Fixed**
- **Gerakis's Wild Fighting damage logged as the weapon's:** the game added his +3 (DSCLOG gives it
  to whoever's check passed), but the dice log credited Wild Fighting only to a Wild Fury's kit, so
  a passed check showed as "+2 weapon" (a bone sword's −1 and the +3), and a failed one's −3 to hit
  went unexplained.
- **A Battle Dancer's dance and Wild Fighting not rolled at a fight's start:** the Loader rolled
  them only for a fight's round 1, and it took a fight to be new only when the game's clock had run
  two minutes past the last one's last round.
- **Turn Undead's right click showed a new spell's description** (Fogbolt's, for an earth cleric;
  seen in 2.3.0 on): the game describes Turn Undead by numbers the new spells took.
- **Pick Pockets' right click showed nothing:** it now shows the purse and what it does.
- **A Shadowblade or Ghetto Fighter could start with a shield in the backpack:** the kit's gear left
  a shield behind only from a hand, so one already moved to the backpack stayed.
- **White ability labels on the inventory screen** (STR: to CHR:, among the yellow): the fix that
  drew the creation screen's labels in its white drew the inventory's in it too, as both screens
  draw them with one routine.
- **The Trustee stuck in the pens** (again): his rounds' two pauses took their corner from numbers
  any script in the pens could change, and once another had, he set off for a spot that doesn't
  exist and stood still for good, busy.
- **Figures hold the Loader's own weapons:** the bone and obsidian short swords and axes a new
  warrior starts with, the metal daggers, maces, great axes, picks and polearms, and the other new
  weapons were drawn as nothing, so a figure carrying one swung empty-handed (the game's own weapons
  were drawn).
- **Dinos's talk after the cooked vulture:** once he had given the meal's XP, his menu came back
  with only "Goodbye.", and a stray "Goodbye." followed in a window with no portrait.
- **Mirror Image works as it says** (seen in 2.4.0).
- **Armor lasts as long as it should:** it used a charge each time any spell or blow landed on its
  wearer, as well as for the damage, so each hit cost two and a friend's Bless one.
- **Share Strength's strength goes when the power ends:** the game looked for it under the
  psionicist rather than the one who got it, who kept it (and could end another of the psionicist's
  own effects instead).
- **The preserver's Dispel Magic no longer silences:** it laid "No spell use" on everyone it caught,
  the party too, which Dispel Magic can't remove.
- **Hold Undead holds only the undead:** it held living creatures too.
- **Cause Serious and Critical Wounds do 2d8+1 and 3d8+3,** as AD&D has them and the Cure spells
  heal; their records had 2d9 and 3d9.
- **A new game's arena could be left without its announcer, and new characters without their gear**
  (seen in 2.4.0): the Loader's starting gear, fitted just as START GAME rebuilt the game's item
  records, could use up the game's free records.
- **A Brute started with no weapon:** its long sword and club, which the game puts in the backpack,
  were left behind.
- **No crash report when DOSBox closed while the game still ran** (a freeze, DOSBox stopping with an
  error of its own, or its window closed): a report was saved only for an error code or the game's
  own error.
- **A crash after Continue on a monster's whole description** (the window that follows a Look box
  with more to say): the dialogue window can load other parts of the game's code over the routine
  that closed the Look box, and DSCLOG went back into it without a way back the game's overlay
  manager could mend.
- **The Loader's item-list changes made safer** (found in review): taking an item out of a list
  while the game's own free list moved could leave the item in no list at all; it now goes back
  where it was.
- **Defilers' scrolls on creatures that aren't defilers** (one of Scar's henchmen dropped one): the
  Loader knew a defiler by the class on its character sheet, which the game hands on from one
  creature to the next.

**Docs**
- **Kits, a page of their own** (`obsidian-edition/KITS.md`): the README's kit tables and rules
  moved out, as Items were, the README keeping a table of the kits' names with links; each kit fact
  repeated across the section (the Shinobi's spell list, the Seeker's and Justifier's casting
  levels, the Battle Mage's weapon pick, the Arcanist's two spells, Wild Fighting) is now said once.
- **A documentation review:** the Options tab's Weapon specialization switch no longer names the
  weapon pages; the mod's items are "the mod's", not "the Loader's"; the guide says weapon spec, as
  the game's screens do; the Effects-screen click among the bug fixes; item reports and thri-kreen
  claws in the guide and the README's bug fixes; the acid table in ITEMS.md ("Items against acid");
  the dice log's attack and save rows shortened, their detail under the tables; the front page's
  "What it does" a paragraph; install advice said once.
- **New:** "Where to start" and "Known issues" in the README, a glossary in the guide (THAC0, AC,
  PSP, the saves' letters and more), and in DEVELOPMENT.md the folders and how a release is made.
- **Items, a page of its own** (`obsidian-edition/ITEMS.md`): the README's item tables (every magic
  item, the magic weapons by weapon spec, every mundane weapon) moved out, as How the game works
  was; the README keeps a short section linking to it, and the front page, the guide and the
  docicons test name it.
- **Draft release notes for 2.5.0** (`release-notes/v2.5.0.md`), this pull request's changes for
  players, and a "Coming in 2.5.0" line on the front page.
- **The Warden's Legs' chest is the Wagon Train's,** not the Gemfields' (its chest, object 1065, is
  in region 8, with the magera and their prisoners; the Gemfields are region 6).
- **Patch notes:** the six new spells and the nineteen magic weapons as tables; the air cleric's
  dagger line says what the game had (none); acid on armour with the other Combat rules; the
  Loader's accessibility (larger text, the keyboard, contrast, logs as text).
- **The Loader's Options tab:** Picking pockets says a click on anyone in sight (it said "talk to
  someone"); the hiding switch reads more plainly; "...
- **Credits** on the front page: the code and documentation written by Claude, the direction and
  testing, the game and its makers, the rule books, and the tools.
- **The Loader's items in bold italics** in the item tables.
- **One item catalogue:** the README's New items tables merged into the item tables, which list the
  game's items and the Loader's together.
- **`patch-notes.html` made from `PATCH-NOTES.md`** by `python -m dsloader.patchnotes`, as the
  guide's page is (a test fails when it falls behind); its Copy as Markdown button gives the
  Markdown itself.
- **The front page tidied:** a list of the documents in place of the contents, the fan-project and
  license notes at the end, and the release notes listed once.
- **DEVELOPMENT.md opens with how to test, build and run** from a command prompt, then how it works;
  it says how the two web pages are made.
- **The README's "What it changes on your computer"** points to the files table instead of listing
  them twice; the patch notes' first line split in two.
- **GPL-3.0:** the project's code and documentation are licensed under the GNU General Public
  License v3.0 (`LICENSE`, in the release zip too), with a note that the game's own art in the pages
  isn't covered.
- **How the game works** moved out of the README into `obsidian-edition/HOW-THE-GAME-WORKS.md` (the
  original game's own rules, about 490 lines), the README keeping a list of its sections.
- **One source for the kits' numbers:** the README's kit tables.
- **[The game's bugs, fixed](obsidian-edition/FEATURES.md#the-games-bugs-fixed):** a README section
  with every bug of the game's own the Loader mends, the spells' among them, and a line for them
  under What it does on both front pages.
- **Rules the game got wrong** (the README's bug fixes, and a paragraph under the patch notes' Bug
  Fixes): the spell save, the doubled d20, two weapons, warriors' attacks, class restrictions,
  multiclass hit points, rangers' spells, acid, the class tables and thief skills, each with what
  the game did and the rule that puts it right; the thief skills' equipment penalty among the bugs
  always fixed.
- **The player's guide as a web page,** `obsidian-edition/player-guide.html`, in the patch notes'
  look with its sections as an index, made from PLAYER-GUIDE.md by `python -m dsloader.guidepage` (a
  test fails when it falls behind the guide).
- **Your saved games** (the patch notes, and the README's bug fixes): no new game needed for the
  fixes, which work from loading; what the old bugs already did to a save stays (Share Strength's
  kept strength, a Dispel Magic silence until it wears off, a 2.4.0 arena without its announcer); a
  new game still the way to see kits, fuller starting gear and the early new content.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #50 ([merged 2026-10-16](https://github.com/daaki85/darksun-obsidian-edition/pull/50))

**Release**
- **Obsidian Edition 2.4.0** (pull requests #48 and #49): the version is
  2.4.0, with its notes in `release-notes/v2.4.0.md`, listed on the front
  page with the others.

## Pull request #49 ([merged 2026-10-16](https://github.com/daaki85/darksun-obsidian-edition/pull/49))

**New**
- **The game's own party have features of their own:** Gerakis fights wild (the Wild Fury's Wild
  Fighting). K'ratchek casts as a Wasteland Seer, and her chatkcha comes back as if she had
  several (one more throw a round). Cilla is an Elven Wanderer, her hiding never halved in
  daylight. No character made on the creation screen can have them. (Kits. The Effects screen
  lists them as WILD FIGHTING, OPEN SKY SPELLS and CHATKCHA 2/ROUND, and KIT: E-WANDERER; the
  Characters tab beside the kit; the dice log as a new game starts.)
- **Six new multiclass kits:** the **Spellarcher** (half-elf fighter/preserver: its arrows 1
  better and at least +1, magical; its weapon spec the bow only), **Titan Mind** (half-giant
  fighter/psionicist: psychometabolism 2 PSP less, telepathy 2 more), **Poisoner** (halfling
  fighter/thief: its first hit in each fight poisons, a save or 10 damage; −1 to hit), **Spirit
  Caller** (halfling cleric/psionicist), **Wasteland Seer** (thri-kreen druid/fighter: spells
  cast 2 levels higher under the open sky, 1 lower under a roof) and **Wild Fury** (mul
  druid/fighter). (Kits.)
- **Wild Fighting** (the AD&D proficiency), the Wild Fury's: as each fight starts, a d20 against
  CON − 4, a natural 20 always failing. Passed, 1 more attack a round in melee and +3 damage for
  the fight; failed, −3 to hit and AC 3 worse. (Kits. The dice log shows the check.)
- **Crash reports say why the game quit:** the game prints its own error while the screen is in
  graphics, then clears it switching back to text, so the message was lost (as after the opening
  arena fight, "return code 01h" and a blank screen). The helper now keeps what the game last
  wrote, with the calls that led there, for the Loader's crash report.
- **Monsters' powers told apart in the dice log:** the game has no name for them, so the log adds
  the power's damage dice and kinds, as in "special attack 195 (1d10 crushing)" (Daggoran's).
- **A freeze report:** when the game stops but DOSBox stays open, the Loader's **Freeze report**
  button saves a zip in `crash-logs`. It holds where the game was running for its last few
  seconds (noted by the helper from the game's timer), the helper's state, the switches, the end
  of the dice log and dialogue, and a copy of the game's memory. (DEVELOPMENT § The freeze
  report.)

**Changed**
- **The Battle Dancer's dance rolls at −4:** a d20 against DEX − 4, a natural 20 always failing,
  as a proficiency check and as Wild Fighting's. It lasts that less the roll in rounds. (Kits.)
- **More for three multiclass kits:** the Military Scout, under the open sky, has +2 initiative
  and +1 to hit with a bow, sling or staff sling, and its hiding isn't halved in daylight. The
  Shadowblade tries to hide in shadows even with an enemy right beside it. The Wayfinder gets
  **Path-finder**: while it's up, every party member has +1 initiative and +1 Move in a fight.
  (Kits; the first two with hiding to backstab.)
- **Stronger costs for six multiclass kits:** the Shadowblade can't use a shield. The Military
  Scout never backstabs (from behind is still +2 to hit). The Wilderness Avenger has 1 fewer
  druid spell slot at each spell level. The Rescuer gets +1 to hit from behind, not +2. The
  Ghetto Fighter is −1 to hit with anything but a dagger and can't use a shield. While a
  Wayfinder is down (and no other is up), the party has −1 initiative and −1 Move in a fight.
  (Kits.)
- **Thieves' Tools are Mirlon's** (in the slave pens), for a party that kills him, as well as
  Kel's to sell. No thief starts with a set any more, and none is put in a thief's backpack
  later.
- **The leather helm keeps its own name,** no more `Helm (AC 1)`: its box shows `AC BONUS:1`
  with the helms rule, which says the same.
- **Thieves wear light armour only** (leather, hide, silk). Before, a thief of one class could
  wear any armour. A multiclass thief, or a human thief who was a fighter, gladiator, ranger or
  cleric, may wear the heavier armour its other class allows, but has no thief skills (all 0, on
  the inventory screen too) and no backstab in it. A human who has been a preserver and a warrior
  (either order) may wear the warrior's armour too, and casts no spells in it. (Class
  restrictions.)
- **Light armour only for the Assassin, Shinobi, Shadowblade, Poisoner and Spellarcher,** even
  with the kit asleep after changing class. (Kits.)
- **Starting gear for the kits:** a Battle Dancer starts with two long swords (the second in the
  left hand, in place of the shield). A Myrmidon has its second weapon in the left hand when it's
  a one-handed melee weapon (a bow still in the missile slot, a two-handed weapon in the
  backpack). A Poisoner has a dagger in each hand (its long sword made one, its shield left
  behind), and a Ghetto Fighter a dagger in its hand, whatever its weapon spec. Weapon specs
  start as the chatkcha for a thri-kreen whose classes allow it, the dagger for a Ghetto Fighter
  or Poisoner and the long sword for a Battle Dancer, unless the player picks another on the
  weapon pages. (Kits.)
- **Smaller starting gear changes:** a multiclass preserver's armour is left out, not put in its
  backpack. Fuller starting gear no longer adds a dagger to every backpack (a character whose
  classes start with one keeps it).
- **A ranger's bow is listed** on the Effects screen and the Characters tab (`EXPERT IN / LONG
  SWORD / BOW` for a cleric/ranger). Every ranger is an expert with the bow, chosen or not, but
  only the chosen weapons were listed.

**Fixed**
- **A Battle Dancer whose cleric sphere bars long swords couldn't specialize in one** on the
  creation screen, and started with a bow and a shield. The weapon pages left out what the kit
  allows whatever the classes do. It now starts with a long sword in each hand.
- **The game slowed down with the combat log's panel shown** (2.3.0). The helper put the panel
  on screen again on almost every pass of the game's main loop, with a slow byte-at-a-time copy.
  It is now put again at most once a BIOS tick, and the Loader stores the picture so each plane's
  part of a row is copied whole. (Measured in a fight: the idle loop ran 1,100 to 1,500 times a
  second with the panel, against 3,600 without; now 3,500 to 3,600.)
- **A multiclass preserver could cast in armour** (class restrictions on, since 2.0.0). The USE
  screen said NO SPELLS IN ARMOUR, but the spells stayed in use: the helper read the character
  from a register the game's own test had changed. It now reads the character the game asked
  about.
- **Copies of the combat log's panel were left on the map** (2.3.0) when the view scrolled by the
  game's own scrolling, which copies the screen, the panel with it. When the view has moved, the
  helper now has it drawn again whole, round the panel.
- **A patch of map showed under the pointer on the combat log's panel** (2.3.0). In a fight the
  game moves its pointer on the screen not on show and copies the box round it to the one on
  show. The panel was only on the one on show, so the copy brought the map back. It is now put on
  both.
- **A new character's bow was listed as "Arrows 1D6",** with no THAC0, on the inventory screen.
  The mod gave the arrows after the bow, which put them first in the character's items, and the
  game lists whichever comes first. The bow now goes first, and an "Arrows" line the game still
  shows gets the bow's THAC0.
- **Yellow text on the character creation screen** (since 2.3.0): the scores, the lines below
  them and the labels STR: to CHR:. The creation screen never sets its own colour, so after a
  character screen it took that screen's yellow. Its white is now set as it rolls, and the labels
  are drawn in it.
- **The combat log's panel showed on the USE screen,** hiding its right side and taking its
  clicks (2.3.0). It now shows on the map only.
- **A new character's weapon specialization carried over** from the character made before it.
  The game keeps one sheet for every character it creates, and changing the classes cleared the
  kit but not the specs. The specs are now cleared with the kit.
- **The dice log's damage for a STR 18 character was 2 short:** it added +2 for STR 18, but the
  game's own table adds +4. The Loader now reads the game's table, as it does STR's to-hit.

## Pull request #48 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/48))

**New**
- **Multiclass kits:** seven kits for two classes taken at once, each for one race only, chosen
  on the creation panel's KIT page as a class's kit is. (Kits.)
  - Elf cleric/fighter: **Battle Dancer**, which dances as each fight starts (a d20 against DEX:
    +1 to hit, damage and AC for DEX less the roll in rounds, or −1 for 1d8 rounds). Long swords
    and bows only, but any of them, whatever its cleric's sphere allows.
  - Half-elf fighter/thief: **Shadowblade** (+10 hide, +5 move, −10 pick pockets) and **Military
    Scout** (+10 to traps, move, hide and climb under the open sky, −5 under a roof).
  - Half-elf druid/fighter: **Wilderness Avenger** (+1 to hit and damage against undead; hides
    and moves as a ranger).
  - Half-elf cleric/ranger: **Rescuer** (cures heal 1 more a die under the open sky).
  - Dwarf fighter/thief: **Ghetto Fighter** (+1 with a dagger; two weapons at 0 and −2; +5 pick
    pockets and hide, −5 traps) and **Wayfinder** (+10 hide and move, −10 pick pockets).
- **The combat log below the map:** the game's screen is 320 × 222 and the log a strip under the
  map, always shown, covering none of it; the game's speed and the map's shape are as ever. In a
  fight it shows the round and the newest line, between fights the two newest lines. The mouse
  wheel scrolls it, with a **Latest** chip while scrolled back. (In the game, off by default. It
  is kept up through the arena's opening show; in the panel's darker shade, blue-grey under a
  screen in other colours, black on the title, the main menu and in character creation.)
- **Rolls out of fights in the combat log:** a thief's skills, a scroll learned, a new level's hit
  points, in the panel and the strip alike.
- **An L in the panel's top line,** a button that hides it as the key does.

**Changed**
- **The combat log's panel is shown and hidden with L:** 2.3.0 opened it in each fight and closed
  it at the end. **L** on the map shows or hides it, in a fight or out of one, to read back over
  the last fight or the rolls since. It stays as it was left, from one game to the next too. (L
  used to collapse it to one line; **-** does.)
- **Fuller starting gear for the game's own party too,** in the first moments of a new game:
  Gerakis a sling, leather chest and leg armour and a dagger; Cermak and Cilla a dagger.
  K'ratchek, a thri-kreen, keeps the game's own chatkcha and gets nothing more.
- **Fuller starting gear gives no belt or boots, and a cloak only to a Stalker, an Assassin or a
  Shinobi** (2.3.0 gave everyone a belt and boots, and a cloak to every ranger).
- **The inventory screen's `HIDE` and `MOVE` count a worn cloak and boots,** for thieves, rangers
  and their kits, as the rolls do: 10 each, to no more than 95, or the Cloak or Boots of
  Elvenkind's 95. The Characters tab's skills too. A worn belt's 5 was already in `PICK` and
  `LOCK`. (Hiding to backstab, with the cloak, boots and belt switch.)
- **The view in a fight** no longer drifts after each figure that walks near the screen's edge. It
  moves only to bring back one that has walked off the screen. (A switch, on by default.)

**Fixed**
- **The backpack's dagger was fought with** (fuller starting gear, 2.3.0). The Loader put the
  backpack's items (the dagger, Thieves' Tools, the arena's Ring +1, what's lifted from pockets) in
  the list of what a character wears and holds, where the game counts every weapon as in hand. So
  Gerakis fought with the dagger, not his long sword, and Cermak struck with it as a second
  weapon. Backpack items now go in the backpack's list, what the Loader takes in hand or puts away
  moves between the lists, and games where it happened are put right next time out of a fight
  (the dice log says `... is put away in the backpack`).
- **The game quit ("Return code 01h") or froze in fights with the combat log on** (2.3.0): the
  redraw routine, drawn in parts round the panel, went on from a way back the parts' drawing had
  overwritten (a variable the other probes share). The game ran on from the wrong place, writing
  over its memory (garbled names, stripes) until it quit. The way back is now kept on the stack.
- **A new thri-kreen was given gear** it can't wear or use (fuller starting gear, 2.3.0): armour,
  a belt, boots, a cloak, and a weapon and a dagger where its claws serve better. It now gets
  nothing more than the game's own starting gear.
- **The pointer over the combat log's panel** was hidden by it, and moving across the panel could
  leave a patch of map or no pointer (2.3.0). The panel is now put on before the game draws its
  pointer, the pointer is drawn again after the panel, and the panel's refresh leaves the
  pointer's box alone. (Checked: held still for 48 frames and moved across, the pointer showed
  every time and no map came through.)

## Pull request #47 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/47))

**Release**
- **Obsidian Edition 2.3.0** (pull requests #44 to #46): the version is
  2.3.0, with its notes in `release-notes/v2.3.0.md`, listed on the front
  page with the others (tag `v2.3.0`).

## Pull request #46 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/46))

**New**
- **Fuller starting gear:** before a new character is first played, the Loader adds plain gear it
  can use and hasn't got. That is a weapon in an empty right hand (from the backpack, as a
  cleric's club, else a plain one of its weapon spec or a short sword, club, mace, dagger or
  quarterstaff), a sling if it has no missile weapon (an earth or fire cleric a chatkcha), leather
  chest, arm and leg armour in empty places, a belt, boots, a dagger, and a cloak for a ranger or
  Stalker. A thief/psionicist and an air or fire cleric had started with no melee weapon. (More
  character customization, on by default. With the class restrictions, a multiclass preserver's
  armour goes into the backpack, so it can cast.)

**Changed**
- **An air cleric of one class may use daggers,** as its sphere allows. None of the game's daggers
  had the air cleric in its class list, so only Galefang would do. DSCLOG now adds it to every
  dagger type, the game's and the Loader's.

**Fixed**
- **The combat log's panel flickered and lost pieces** as figures moved and fought: the game drew
  the map over it a rectangle at a time, and DSCLOG only put it back afterwards. The rectangles
  are now drawn round the panel, and before the screens flip the panel is put on the one about to
  show. (The old way, through the redraw routine's way back, could also go stale if the game moved
  that code.)
- **A fighter/druid kept the shield it can't use.** Starting gear its classes can't use is left
  behind, but the last item of a list was kept (as a container's must be), and with the druid's
  armour gone that was the shield. A character's list may now empty, for the kits' gear too (a
  Ravager's shield, a Brute's club).

**Docs**
- **The docs said a multiclass character gets each class's gear:** the game gives one class's, the
  first of fighter or ranger, cleric, thief, psionicist, preserver and druid. (Seen in play for
  each two-class combination a half-elf can take.)
- **The documentation reviewed for clarity and repetition:** DEVELOPMENT.md's kits chapter moved
  after weapon specialization, as in the README; the README's new-item prices in a table, a
  preserver's first spells under a heading of their own, the requirements naming the GOG release
  only, and repeated "ticked by default" notes cut.

## Pull request #45 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/45))

**Changed**
- **The combat log in the game is on by default** (it was off until ticked). In a fight its panel
  shows the rolls over the map's lower right; **L** or its **-** button folds it to one line, and
  the Options tab's switch turns it off. Settings saved by an earlier version have it turned on
  once; after that the player's choice stands. (`settings_version` 2 in `settings.json`.)

## Pull request #44 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/44))

**New**
- **A combat log in the game:** in a fight, a panel over the map's lower right shows the dice
  log's lines as they come, in the game's font and the Ledger's colours, with the round and who
  acts next above them. At the least, in short (the default) or in detail.
- **Saves under their names:** the Ledger keeps a second copy of every save in its **Named saves**
  folder, named as in the game (`Page 2 slot 05 - Before Scar's battle.SAV`). The Options tab's
  new **Saves** section opens the folder and puts a named save back in a slot of the game's list.
- **Two magic shields:** **Gutterward**, a wooden shield +1, on a skeleton in the Tari's warrens,
  and **Ironbulwark**, a metal shield +3 (a type of the Ledger's: the game has no metal shield),
  carried by the Guardian of Balkazar's fortress.
- **Three new wizard spells,** all 1st level. **Reflected Image** (on the caster): one image,
  struck instead of the caster half the time; it and Mirror Image replace each other. **Spook**:
  one creature flees for 3 rounds unless it saves, at -1 for every 2 caster levels, at most -6;
  undead aren't affected. **Friends** (on the caster): CHA + 2d4, at most 25, for 1d4 rounds and
  1 a level, for better prices. (New wizard spells.)
- **Defilers' scrolls:** each defiler in a fight has a 5% chance of carrying a scroll of a random
  preserver spell (the game's 69, and the new spells with them on), found on its body when it
  dies. Rolled once a fight, and kept out of the dice log so it isn't given away.
- **Buying back magical items:** a magical item sold to a merchant (a plus, or a power: rings,
  wands, scrolls) stays in the merchant's stock to buy back. The game destroys everything sold,
  and still does other items.

**Changed**
- **Templar's Ledger is now the Dark Sun Obsidian Edition Loader** (the Loader for short): the
  window's banner and title, the crash message in the game, and every page of the docs, which now
  call it what starts the game with the mod rather than a companion window.
- **The folder is `obsidian-edition` and the Python package `dsloader`** (they were
  `darksun-companion` and `dscompanion`). `python -m dsloader` runs the command line, and the
  tests workflow is `tests.yml`.
- **More kits that can't go together:** the Grove Warden can't dual to gladiator, nor a gladiator
  who duals to druid take it (its AC would add to the gladiator's own). The Swashbuckler,
  Crusader, Battle Mage and Mind Warrior, each giving a warrior's THAC0, can't go with one
  another. The Ravager and the Grove Warden can't go together: each has an AC of its own that
  betters with level, and they would stack. (Kits.)
- **The Stalker and the thief:** a human Stalker can't dual to thief, and a thief who duals to
  ranger isn't offered the Stalker kit, whose +15 to hiding would add to a thief's own skills.
  (Kits.)
- **EMS is off in the launcher's DOSBox settings:** GOG's settings turn it on, and its 64 KB page
  frame left the helper 1 KB of upper memory. The game uses XMS instead, and the helper gets a
  64 KB block more, with conventional memory unchanged (632 KB).
- **The leader's CHA at shops:** 5% off from CHA 18 and 5% more for each point after, to 40% at
  25 (it was 5% at 16 to 25% from 20). Shops pay 60% of an item's price when the party sells: the
  game paid all of it, which with the discount let anything bought be sold at a profit.
- **Fogbolt's icon is grey,** its cloud on Armor's grey tile rather than Charm Person's purple.
- **The Shinobi can learn Fogbolt,** a 1st-level spell on its list beside the game's five,
  offered at a level up and cast at the thief level less 5 as the others are. (Kits, with New
  wizard spells.)
- **The bone and obsidian axes weigh 30** (35 and 70 before), the most a weapon can weigh without
  being HEAVY. Either can now go in the off hand with another weapon, and both can backstab.
- **Removed: each turn's rolls in the game's dialogue window,** since the combat log shows them
  without stopping the game. (The "Show each turn's rolls" switch and `--popups` are gone.)

**Fixed**
- **The dice log stopped in a fight whose round order named someone it couldn't match** (the
  Defiler and a Slig in the arena's opening show). The turn's lines now pass over that entry.
- **The new spells' records shared memory with a stack:** the game kept a small stack where Cat's
  Grace, Erdlu Claw and Fogbolt's records are. The helper now moves it (and the monster kinds
  table) into its own memory as the game starts, which also makes room for the three new spells.
- **New preservers weren't offered their spells:** DONE on the creation screen gave the game's own
  starting spells instead of CHOOSE A SPELL. The check meant to leave START GAME's ready-made party
  alone read the character's status, which says Okay for a character being made too.
- **Stuck on the creation panel's KITS page:** a warrior given a second class on the last weapon
  page kept its KITS button, which opened a page with no kits whose KITS button opened it again.
- **A kit was lost on a new roll:** the die's new roll takes a kit away when the classes aren't
  the ones the panel last saw, which it learns from a click on a class.
- **The panel after a new race or sex:** the creation screen puts the default class back without a
  click, so a fighter was left with the game's VIEW SPHERES (which did nothing) where WEAPON SPEC
  belongs.
- **Starting gear the classes can't use:** a character of several classes started with each
  class's gear, what it couldn't wear in the backpack (a fighter/druid/thief's leather armour).
- **A missile weapon's line on the inventory screen** showed the weapon's own rate of fire and no
  specialization bonus (a staff sling specialist's `1D4`).
- **A helm's item box said AC BONUS:0** (beside its name's "(AC 1)") until it had been worn: the
  rule set the helms' AC only as the game added up a character's.
- **Doors with charges:** a door's box (or a mirror's, a crank's) could say `Charges: 10`, read
  from bytes that hold something else in scenery.
- **The Cloak of Protection was forbidden to druids:** its type counts for AC as armour does, so
  class restrictions took it for armour.
- **A polearm's item box ran out of the box:** the game's Polearm picture is 36 pixels tall where
  every other is 22 at most, so the damage line (Thornwall's, Linebreaker's, the bone polearm's)
  fell outside.
- **The Trustee stuck at "I have to get back to work":** the game makes him busy after a talk
  until his rounds bring him back to their first corner. When his rounds stalled, he stayed busy
  for good and never talked again.
- **Rows of the creation panel's weapon and kit pages took clicks only at their left:** each row
  is a copy of the game's AIR row, a button 33 pixels wide, so a click on the rest of a longer
  name (MYRMIDON, LNG SWORD) did nothing.

**Docs**
- **Kits in the docs, class by class:** the README's one table of kits is a table for each class,
  under its own heading, with the level each part of a kit comes at, its starting gear and what
  else a player should know (the classes and kits it rules out, where its choices are made). The
  player guide's class sections have the same rows.
- **The player's guide is now `PLAYER-GUIDE.md`** (it was `GUIDE.md`); the links follow.
- **A review of every page for this pull request's changes:** the Trustee's key in picking
  pockets, a cloak isn't armour, a new roll keeps the kit, the axes' weight, the Saves section,
  `cloud_saves` under More saves, and STORE and RECALL in the More character customization table.
- **A second review, after the combat log:** the overviews name the combat log, the six wizard
  spells, buying back and defilers' scrolls; the top README's overview is a short list linking to
  the full one; the turn pop-up's last mentions are gone; the kits' starting gear is said once, in
  each class's table; the Options tab's new spells box names all six, and its screenshot is
  retaken.
- **A third review, after the rename:** the full README puts **In the game** (the combat log
  first) before the Loader's window, its overview a list; the player's guide starts with the
  combat log; the patch notes put the game's changes before the Loader's; DEVELOPMENT.md has the
  combat log under How each part works and Room in the helper as its own section (they were in
  Kits), a split Shinobi table is whole again, and "viewer" is gone from the docs.
- **The polearms' icons** in the README's item tables (the bone and metal Polearm, Thornwall,
  Linebreaker) are redrawn at the 22 pixels the game now shows them at.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file as it was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md), and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #43 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/43))

**Release**
- **Obsidian Edition 2.2.1:** the version is 2.2.1, with its notes in
  `release-notes/v2.2.1.md`, listed on the front page with the others.

**New**
- **A switch for the elves' and half-elves' looks:** "Elves have pointed ears, and half-elves
  figures of their own", in Graphics, on by default, from the next start. Off, elves are as the
  game draws them and half-elves the human figures in their own colours, as before 2.2.0.
- **A switch for Cilla's elf figure** in Graphics, on by default: off, she keeps the game's
  half-elf woman's figure, from the next start.
- **A switch for STORE and RECALL** under More character customization, on by default: off, the
  creation screen is the game's, from the next start.
- **Restore defaults** at the bottom of the Options tab sets every switch back, after asking.

**Changed**
- **The Options tab's headings are plain names** (In the game, Rule changes, More character
  customization, Expanded features, New content, Graphics, Controls, Game speed). One line above
  them says that everything applies in games started from the Ledger and that a switch marked
  "from the next start" waits for the game to be started again. The elves' and half-elves' looks
  come first in Graphics.

## Pull request #42 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/42))

**Release**
- **Obsidian Edition 2.2.0:** the version is 2.2.0, with its notes in
  `release-notes/v2.2.0.md` (pull requests #39 to #42), listed on the front
  page with the others; the patch notes say 2.2.0.

## Pull request #41 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/41))

**New**
- **STORE and RECALL on the creation screen,** as Baldur's Gate has them. STORE keeps the roll on
  screen (the six scores and the die's total, the hit points and PSP); RECALL brings it back
  however many times the die has been rolled since, AC and damage with it. Changing the race,
  sex, classes or kit forgets it. (The two buttons are carved like the game's own, under the hit
  points. The dice log's ring is 84 entries, was 88, to make room in upper memory.)
- **Half-elves have their own figures** on the map and in fights, where the game drew the human
  ones. The man is built on the elf's figure, a little broader, with short fair hair, a linen
  shirt under a leather jerkin, green trousers, brown boots and small pointed ears. The woman is a
  little slimmer than the human woman, her golden hair in a bun, with pointed ears, a purple
  cloak, purple wristbands and red boots. Worn gear is drawn over them as on the figures they were
  made from (armour on his clothes, a worn cloak in place of her purple one, a shield on the
  forearm in a fight).
- **Elves have pointed ears,** walking and fighting, beside any helm.

**Changed**
- **The Options tab in four groups:** **Rule changes** (the game's rules closer to AD&D), **More
  character customization** (weapon specialization, kits, levels up to 10), **Expanded features**
  (the leader's CHA at shops, and **Improved thieving**: AD&D's thief skills, hiding to backstab,
  the cloak, boots and belt, picking pockets) and **New content** (now with the new wizard
  spells). The Thieves section is gone, its switches under Improved thieving; each switch keeps
  its setting.
- **Removed: P in a conversation** for picking pockets: Thieves' Tools are the way to pick a
  pocket. The game is no longer patched where the conversation window passes on a key, and
  DSCLOG's handler for it is gone.

**Fixed**
- **Cilla looks like the elf she is:** the game's own party gave her the half-elf woman's figure.
  She has the elf woman's now, in a new game and (from the next area) in one already begun.

**Docs**
- **Graphics** is the README's section for what the Ledger draws on the map (was "On the
  screen"), with a part for elves and half-elves. The Options tab's section has the same name,
  and DEVELOPMENT.md a section on how elves and half-elves are drawn.
- **The patch notes have a table of contents,** as their web page does.
- **The README in the Options tab's groups,** STORE and RECALL under More character
  customization and the new wizard spells first in New content. The guide's Options table and both
  READMEs' overviews follow, and the Options tab's screenshot is new.
- **Smaller:** the game's own party is under More character customization (its weapon specs and
  Cermak's kit) and points to Cilla's elf figure; the bracers and robes are parts of New items;
  "hiding to backstab" where the README said "the stealth rule"; DEVELOPMENT.md's "How each part
  works" follows the README's order; the patch notes' Thieves section is **Improved Thieving**.
- **The patch notes' items, one by one,** in four groups: magic weapons (fifteen, each with what
  it is, and the Elven Leader's Gythka +2), magic armour and worn items (Inixhide among them,
  missing before; Arrowbane and the Sunking Crown said not to be armour), other magic items (the
  Tome and Kalzith's six scrolls, by name) and mundane items (Thieves' Tools among them).
- **"Weapon type" throughout,** where the pages said "kind of weapon" or "weapon kind"; the item
  tables' Kind column is Type.

## Pull request #40 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/40))

**Docs**
- **Semyon as the game tells him:** the README called him "of the Veiled Alliance". In the game he
  is a slave tied up for asking after it, "much more of a scout than a warrior", who takes the
  party for the Alliance and asks to join. His section now says so, in his own words from the
  arena, as does the description in the Ledger's code.

## Pull request #39 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/39))

**New**
- **Two new wizard spells, Erdlu Claw and Fogbolt, and Cat's Grace is a spell of its own.** Erdlu
  Claw (1st level): for 5 rounds a caster level, natural and unarmed attacks do 1d6+1 where that's
  better (or Body Weaponry's and Animal Affinity's dice +1), are +1 to hit and count as a +1
  magical weapon. Fogbolt (1st level): a dark grey bolt of its own that needs a clear line to its
  target; for 2d4 rounds unless saved against, -3 to the fogged creature's attacks and +2 to
  attacks on it. (New wizard spells, was Cat's Grace.)
- **The three spells are spells 196-198,** learnt, listed, cast and shown on the Effects screen
  like the game's own, each with its icon, description and sounds (Cat's Grace Haste's, Erdlu
  Claw Shocking Grasp's, Fogbolt Fog Cloud's). Cat's Grace no longer takes Flaming Sphere's
  place, and Magic Missile's bolt stays blue. Who knows them is kept in the character's sheet.
  (The dice log's ring is 88 entries, was 96, so the helper still fits in upper memory.)

**Changed**
- **Multiclass hit points follow Demihuman Deities (TSR 1998):** CON's bonus goes on every hit die
  (a warrior's +3, +4 if one of the classes is a fighter, gladiator or ranger, else at most +2),
  and the running total is divided by the classes. The rule had divided CON's bonus, which the
  game counts once a level of the highest class, by the classes again. (A fighter 9 / preserver
  10 / thief 10 with CON 18 got 12 hit points from CON, now 38.)
- **The level-up weapon window shows the weapons:** a bigger window with each weapon type's
  inventory picture, six to a row, in place of the names, those the character can't pick greyed.
  Pointing at one names it (SPECIALIZE IN / DAGGER, or EXPERT IN for a ranger or Battle Mage), as
  CHOOSE A SPELL names a spell. (Also on becoming a warrior by DUAL.)
- **View Character labels the saves and adds MOVE:** the five saves each have their label (PPD,
  RSW, PP, BW, SP, as on the inventory screen) in place of one SAVE line. THAC0 moves down beside
  PSI, and MOVE is new, beside HP.
- **Rangers and Twin-blades fight with two weapons at no penalty only in light armour:** every
  piece worn, a helm too, of leather or of no material. In other armour they take AD&D's -2 and
  -4, as anyone does; the dice log and the Characters tab say the same. A Justifier has no penalty
  in any armour, a bonus of its own. (The two-weapon rule.)
- **Cermak is an Arcanist** in the game's own party, his gear and hit points as the game gives
  them. Gerakis has no kit. (Kits.)
- **Removed: boots no longer give a move in a fight.** The rule was a leftover from trying out
  changes to items. Its switch is gone, boots are plain "Boots" again (games with "Boots
  (Speed+1)" get the game's names back), and the Characters tab's move shows only a kit's extra
  (the Stalker's).

**Fixed**
- **A save line read as if the save succeeded** ("Thrikreen saves vs Fogbolt ... -> failed"). It
  is now the creature's saving throw, then the result: `Wild Mul's saving throw vs Fogbolt from
  Daaki (spell): d20 = 16, needs 14 (35% to save) -> saved`. "Cannot save" and "saves
  automatically" read `none allowed (cannot save) -> failed` and `not needed (saves
  automatically) -> saved`.
- **The dice log showed XP for every kill,** from the creature's sheet, even where the party gains
  none (the arena's opening fight). A kill now reads "Rampager is killed"; XP shows only on the
  "XP: ..." line, when the party's XP really goes up.
- **EXIT on CHOOSE A SPELL did nothing** when a new preserver picked its starting spells (or a
  human its spells on becoming a preserver): the window only opened again. EXIT now ends the
  picking, and the spells left are the game's own starting spells, less any picked.
- **The game's own party had to pick spells:** starting with no party made, Cermak and Cilla were
  put on CHOOSE A SPELL. They keep the game's spells again; only a character made on the creation
  screen (still New) picks.

**Docs**
- **The new spells' screenshots:** their three descriptions, the Effects screen with Cat's Grace
  and Erdlu Claw, and Fogbolt's bolt replace the two Cat's Grace pictures. The Options tab and a
  spell's end-of-turn window (a Fogbolt, where it was a Cone of Cold save) are retaken.
- **A review of every page:** the README's main screenshot (the arena's opening show's dice log)
  is retaken without the kill XP, and the Options tab's with every rule switch. The README gains a
  Characters tab section, the missing "Scores and hit points as rolled" in its contents, a clearer
  list of what play writes to the game folder, and the kits' details in one list; notes on how
  things were tested and the old release names are gone. The guide has its first pictures (the
  dice log, the weapon window) and no longer says the game's own party has no weapon specs.
  DEVELOPMENT.md points to the README for the kits' table, says what the helper's memory is now,
  and drops the kits' build diary.
- **Screenshots retaken where they had fallen behind:** the inventory, the tome, the game's own
  party (the off hand at one attack a round, not 1.5), the creation screen's weapons page (the
  scores' total under CHR), the gear boxes (plain boots), the figures' gear (now with shadows),
  Kalzith's shop (the CHA discount) and the Options tab (no boots switch).

## Pull request #38 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/38))

**Release**
- **The release zip is `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`,** unzipping to
  a folder of that name, to match the releases' title (it was `Obsidian-Edition-<version>.zip`).

## Pull request #37 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/37))

**Release**
- **Obsidian Edition 2.1.1:** the version is 2.1.1, with its notes in
  `release-notes/v2.1.1.md`, listed on the front page with the others.
- **Releases are titled "Dark Sun: Shattered Lands - Obsidian Edition"** and the version, rather
  than "Obsidian Edition" alone.

**Fixed**
- **The dice log missed character creation rolls:** the die rolls a whole character many times
  while it tumbles, more than the log could read, so abilities often came as "its rolls came too
  fast to record". The helper now keeps each ability's last four 4d4, and the log reads them when
  the die stops; the rolls missed meanwhile are no longer mentioned.
- **Raising CON on the creation screen didn't raise the hit points** (lowering it could lower
  them): the game only kept them within the new range. A change of CON now adds or takes off its
  bonus for every level, as the game counts it. (Scores and hit points as rolled.)

## Pull request #36 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/36))

**Release**
- **Obsidian Edition 2.1.0:** the version is 2.1.0, with its notes in
  `release-notes/v2.1.0.md` (pull request #35), listed on the front page with
  the others.

## Pull request #35 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/35))

**New**
- **Scores and hit points as rolled:** on the creation screen a click raises a score only while
  the six add up to no more than the die gave, so lowering one frees points for another, and a
  click on the hit points does nothing. Under CHR the screen shows the six's total and the die's
  (`SUM:99/101`); a new class that raises a score to its minimum raises the die's total with it.
  The dice log adds each roll's total. (A new rule, on by default, with its own box on the Options
  tab. No interrupt vectors were left, so the new sites share the one for choosing a preserver's
  spells, with a site number after the `INT`.)

**Changed**
- **Removed: turning the mouse wheel no longer scrolls the map** (the Ledger's Windows mouse hook
  is gone); pressing the wheel and dragging still does.

**Fixed**
- **A click on a score on the creation screen stopped the game** (since 2.0.0): the Mind Warrior's
  PSP check at the end of the game's PSP routine returned with interrupts off, and nothing turned
  them on again. The flags are now put back.

**Docs**
- **Patch notes** (`PATCH-NOTES.md`, and `patch-notes.html` as a page with a copy-as-Markdown
  button): every change from the original game, laid out as patch notes to share online. Linked
  from the front page.

## Pull request #34 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/34))

- This changelog: pull request #33 marked as merged, with its date and link.

## Pull request #33 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/33))

**Release**
- **Obsidian Edition 2.0.0:** the version is 2.0.0, the first release under
  the new name, with its notes in `release-notes/v2.0.0.md` (pull requests #31
  and #32), listed on the front page with the others.

## Pull request #32 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/32))

**Docs**
- **All the documents reviewed:** the front page and the README name AD&D's class tables, the
  leader's CHA and the robes among the rules and items. The README's rule count (21), item and
  price tables and Kalzith's shop are up to date. The guide's gladiator AC (with or without
  armour) and the game's priest THAC0 are corrected, and its "What the Ledger shows you" (which
  the quality of life table covers) is gone. DEVELOPMENT.md's kits are no longer "being built",
  its parts follow the README's order, and the shop's NO DEAL! and the CHA rule's check are there.

## Pull request #31 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/31))

**New**
- **Kits:** a character of one class may take one of three kits for its class, or none, on the
  creation panel's new KIT page (KITS, at the end of the panel's pages), NO KIT first, the rows
  not chosen greyed as the spheres' are. (DEVELOPMENT.md has how they are built, each effect's
  hook among them; the probes are listed in `gamepatch.py`.)
- **What the kits do:** the Myrmidon, Sentinel and Ravager (fighter); the Arena Champion,
  Twin-blade and Brute (gladiator); the Stalker (ranger); the Assassin (thief); the Grove Warden
  and Wanderer (druid); the Lifebinder's weapons, and the Shinobi's weapons and armour.
- **Kits' THAC0:** the Swashbuckler, Crusader, Battle Mage and Mind Warrior get a warrior's THAC0,
  the Scholar's is 1 worse (a new probe at the end of the game's THAC0 routine). The
  Swashbuckler's −10 to every thief skill is named in the dice log's thief skill lines, as the
  Assassin's now is.
- **Kits' spell slots:** the Arcanist's wizard slots are 1 more at each spell level, the Battle
  Mage's and Crusader's 1 fewer, the Elementalist's a level behind, and the Seeker's and
  Justifier's priest slots their own tables. The Ledger's Spells tab counts them the same way.
- **Kits' PSP:** the Mind Bender's telepathy powers (the defence modes too) cost 2 PSP less to use
  and keep up and its psychokinesis 2 more; the Kineticist's the other way about.
- **Kits' healing:** the Healer's Cure Light, Serious and Critical Wounds heal 1 more a die, and
  the Lifebinder's cures heal a die more. The dice log shows each.
- **The Battle Mage** casts though hit earlier in the round (the game stops anyone else), and holds
  nothing in the off hand.
- **Kits' casting level:** the Seeker casts at its ranger level less 5 and the Justifier less 9 (a
  ranger's: less 7), which also lets a 6th-level Seeker choose 1st-level priest spells.
- **Rangers' casting level:** a ranger's spells last and do damage as cast at its level less 7, as
  the spell levels it may cast already count it. The game took the whole ranger level. (A rule, on
  by default.)
- **The Shinobi's spells:** preserver spells from 6th thief level on the Seeker's slots, cast at
  the thief level less 5, from its own list of 14. One is learnt at each level up from 6th, on
  CHOOSE A SPELL, which shows its spells only; none from scrolls.
- **The Scholar** learns a spell more at each level up: CHOOSE A SPELL comes up twice.
- **The Battle Mage's weapon and armour:** it wears light armour (leather, or none) and casts in
  it. With weapon specialization it chooses one weapon spec (long sword, club, dagger, short
  sword, mace, axe or pick) on the weapon pages, may use those weapons as well as a preserver's,
  and attacks with them at expertise's rate, 3/2 a round (2 from 7th level).
- **The Elementalist's second sphere,** chosen on the CLERICAL SPHERE list once the kit is taken:
  its spells known from the start, cast at its cleric level, and its weapons allowed as well as
  its own sphere's.
- **The Seeker's weapons** are its sphere's, as a cleric's of that sphere, but for the bow.
- **Kits' hit dice and PSP:** the Battle Mage rolls a d6 for hit points, the Mind Warrior a d8 with
  a tenth fewer PSP (rounded down), and the Arcanist a d3, at each level up and on the creation
  screen. Choosing or taking back one of these kits rolls the hit points and works out the PSP
  again, which the game did only on a click on a class.
- **A kit sleeps when a human dual-classes** (DUAL on a portrait's menu), as the class it came
  with does, and wakes, gifts and costs, once the new class's level passes the old one's.
- **Classes a kit bars on dual-classing are greyed on the DUAL window:** a Seeker or Justifier
  can't become a cleric or druid, nor a Shinobi a preserver (their slot tables would replace the
  new class's). The Swashbuckler, Crusader, Battle Mage and Mind Warrior take no warrior class
  (they have a warrior's THAC0). An Arena Champion or Sentinel takes no druid or preserver (no
  shield), and a Brute no psionicist or air cleric (no two-handed melee weapon).
- **Weapon specs are weapons learnt for good,** while the class or kit that gave them is awake: no
  kit forbids a weapon type the character specialized in (but for the off hand's rules).
- **A human who becomes a preserver picks its two spells** on CHOOSE A SPELL (1st level only), not
  Grease and Magic Missile.
- **Kits for a human's new class:** after DUAL, the game's three-choice menu asks for the new
  class's kit (**KIT: NONE**, then its kits, leaving off one barred by the other classes or kits),
  and a new Elementalist's second sphere. With weapon specialization, a new fighter, gladiator,
  ranger or Battle Mage then picks the weapon types it is due.
- **The Effects screen a page at a time:** its lower panel has room for five lines, too few for
  three kits and a gladiator's weapon specs.
- **A new preserver picks its starting spells** on CHOOSE A SPELL when DONE is clicked on the
  creation screen (two 1st-level at 1st level, four at 2nd, four and two of 2nd level at 3rd; a
  Scholar one more a level), in place of the ones the game handed out.
- **The Stalker hides in shadows indoors** with its full chance (the stealth rule halves a
  ranger's indoors).
- **Starting gear fitted to the kit,** changed while the character is new: a Shinobi's long sword
  becomes a bone short sword, a Brute's a bone great axe, a Seeker's one of its sphere's material.
  A Ravager's shield is taken away, an Arena Champion's off-hand club becomes a shield, and a
  Battle Mage's quarterstaff its weapon spec's weapon. A Myrmidon also gets a plain weapon of its
  second weapon spec (in the backpack; a bow in the missile slot, with arrows), a Ravager a second
  of its weapon for the hand its shield left (none for a two-handed one), and a Brute's club is
  left behind.
- **Two magic robes** for preservers, psionicists and druids, worn on the chest and not armour
  (they cast in them; their AC with no armour worn, as bracers'). The **Ashen Robe** (+1 AC, +1 on
  saves against spells) is Kalzith's, worn, sold and left when he is killed. The **Veiled Robe**
  (+2 AC, +1 on every save, a wizard slot more at spell levels 1-3) is sold by Kel.
- **Charges in an item's box:** a wand, the Storm Ring or a necklace shows the charges left
  (`Charges: 50`).
- **Preservers' INT:** AD&D's table gives a preserver a chance to learn a spell from a scroll (35%
  at INT 9 to 100% at 24; a failed try uses the scroll up) and caps the spells of each level it may
  know (6 at INT 9, all from 19), which also limits CHOOSE A SPELL at a level up. (A rule change,
  on by default.)
- **The leader's CHA at shops:** the party leader's CHA lowers what shops ask, as Baldur's Gate's
  table has it (5% at CHA 16 to 25% from 20), in the price shown, the price charged and the
  greying of what the party can't afford; selling unchanged. (A rule change, on by default.)
- **AD&D's class tables:** AD&D's XP tables (a gladiator's and ranger's 2nd level 2,250, a
  thief's 1,250; the game had a gladiator on the fighter's), priests' THAC0 (2 better every 3
  levels from 4th; the game's from 3rd) and spell slots (AD&D's priest table for clerics and
  druids, its wizard table for preservers). (A rule change, on by default.)

**Changed**
- **The mod is now Obsidian Edition.** Templar's Ledger stays the name of its companion window.
- **Kalzith wears his Ashen Robe, Cloak and Quarterstaff from the start** and sells them with his
  scrolls (the game's shops sell all a merchant carries, worn or not).
- **The helper loads into upper memory again,** leaving the game 62 KB more conventional memory
  (632 KB free, was 570). The dice log's ring buffer now follows the helper in a segment of its
  own, so the helper's image is 40 KB (was 63).
- **Two weapons:** the off hand attacks once a round, whoever holds it; the extra attacks (the
  game's 3/2 for warriors, specialization's, the kits') are the main hand's.
- **A kit for each class:** the kit byte keeps two bits for each of a human's classes, so a human
  who changes class can have up to three kits. Every kit rule asks for each kit the character has
  awake, and the Effects screen lists them all.
- **The Arcanist casts two preserver spells in a turn** in a fight: its first doesn't end the turn
  (a hit still keeps it from a second). Its drawback is a d3 hit die (a preserver's is a d4), in
  place of −2 CON.
- **The Crusader and Mind Warrior** have a warrior's extra attacks in melee, 3/2 a round from 7th
  level of the kit's class, with weapon specialization on or off (the DAM lines and the Ledger's
  party view show them too).
- **The Ravager's base AC** is described only up to 10th level, the highest the game goes.
- **Room in the helper:** the dice log's ring holds 96 entries (was 128) and the text buffer is 4
  KB (was 8), for the kits' code. The helper's interrupts are now 8Ch to FEh (and 60h to 65h); the
  message when they are in use says so.

**Fixed**
- **A kit or a second sphere could change a sound:** the game reads two sound numbers on the
  character sheet as words, and the kit and second sphere sit in their high bytes. They are read a
  byte each now.
- **Arena crash after a kill (hardened):** DOSBox could close as a creature died in a fight.

**Docs**
- **The player's guide** (`GUIDE.md`), new: the game's rules as its code works them and the mod's
  changes, laid out like the game's rule book, with the tables, and no spoilers. It was rewritten
  to tell how the mod plays, with its default options and a "Without the mod" note where a switch
  changes the game's own; the manual's comparisons, race and class list and unchecked hot keys
  are gone.
- **The player's guide, more:** the quality of life changes in a table; each kit's starting gear;
  the kits' spell slots and the Shinobi's spell list; the preservers' and priests' spells by
  level, sphere and class (from the game's spell records); things worth knowing in play; the
  races' ranges of scores and why a half-giant's penalties give the Dark Sun book's caps; a short
  description of who takes each kit on Athas; the Battle Mage's 3/2 attacks (2 from 7th level).
- **The player's guide by class:** for each class, how it plays, what the mod changes, its weapons
  and armour, its kits, starting gear and races, every multiclass combination (from the game's
  creation tables: gladiators never multiclass), how a human dual-classes into or out of it (from
  the game's DUAL check) and the magic weapons it can wield.
- **The README reorganised:** what the game does on its own under How the game works, every rule
  change under Rule changes, sub-headings for Kits, the item box charges under In the game,
  addresses left to DEVELOPMENT.md, and every section in the contents.
- **Kits that can't go together** lists only pairs that can meet: the Arena Champion and Sentinel
  clash only with the Shinobi (README, guide).
- **Smaller:** the Warden's Plate's AC explained (12 points better as a set, not "AC 11"); the
  Kits switch no longer says half the kits work; the front page names the kits and INT among the
  rules, and what has changed since 1.2.0; DEVELOPMENT.md has how kits are built (room in the
  helper, the sheet's kit byte, the creation page, each effect's hook) and a summary of the
  patched game's interrupts, with `gamepatch.py` as the list.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file as it was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md), and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #30 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/30))

**Release**
- **Templar's Ledger 1.2.0:** the version is 1.2.0, with its notes in
  `release-notes/v1.2.0.md` (pull requests #19 to #29), listed on the front
  page with the others.

## Pull request #29 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/29))

**Changed**
- **A ranger's bow is its own:** a multiclass ranger may use bows whatever its cleric sphere allows
  (a fire cleric/ranger, whose sphere allows only obsidian). A human ranger turned cleric gets the
  bow back with its chosen weapon spec once the cleric level passes the ranger's. Before, its bow
  expertise was there but no bow could be readied. (Class restrictions.)

**Docs**
- **What it does,** on the front page and in the guide alike: what the Ledger shows of the game's
  hidden rolls, how it brings the rules closer to AD&D, what it adds to Athas and on the screen,
  and its quality of life changes.
- **Two weapons** is a section of its own, beside Thieves and Saving throws (the game's rule, then
  AD&D's penalties), rather than under The dice log.

## Pull request #28 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/28))

**Changed**
- **Warriors shoot faster from 7th level** with a missile weapon they haven't specialized in, as
  their melee goes from 1 to 3/2: a bow 3 a round (was 2), a sling, staff sling or chatkcha 3/2
  (was 1). Specialists keep their rates, a step ahead at every level.
- **The Options tab:** a **Thieves** section of its own, after Rule changes, with AD&D's thief
  skills, hiding to backstab (and the cloak, boots and belt) and picking pockets (and the P key);
  the weapon specialization box is shorter. The arena's ring goes with New items, magical and
  mundane, its own box gone. The red rings are under Controls, with Tab and Enter; scrolling with
  the right button is a line under the mouse wheel's.
- **The Ledger's window:** Show details and Show unlabelled rolls are on the Dice log tab, above
  the log. Save layout and Reload layout are on the Memory tools tab, leaving the top row to
  starting the game, its window, the text size and Reconnect. A byte's decoding has its own line.
- **Smaller:** "Not connected" says to start the game with Start the game, not a command-line
  option; a character's card leaves out empty lines (a non-warrior's weapon specs).

**Docs**
- **The guide reorganised:** Every magic item and Every mundane weapon under Item tables;
  Suggested system requirements under Requirements, linked from Game speed; Picking pockets moved
  to Thieves; weapon specialization tidied ("weapon spec" throughout, every ranger's bow expertise
  said first); the two Two weapons sections one; the Effects screen's click under Controls.
- **The guide read through:** the game's own saving throws explained once, under Saving throws;
  the crash sections one; Show Save with the practice program under Without the game; the
  Characters tab's card as a list; the backstab table with the new weapons (a bone axe and a pick
  can backstab); sixteen rule changes, not fifteen; technical notes moved to DEVELOPMENT; old-save
  notes gone.
- **Screenshots retaken with the game installed** (its title lettering, portraits and figures):
  the dice log, the Dialogue tab, the practice program and a thief's card. The backstab table is
  checked against the game's item data (named long swords weigh 10 to 40).

## Pull request #27 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/27))

**Changed**
- **No bow to choose for a ranger** at creation, nor in the catch-up pick at a level gained:
  every ranger has expertise with the bow already.

**Docs**
- Where a ranger's bow expertise and missile weapons' rates show, and the Options tab's weapon
  specialization box, mention them.

## Pull request #26 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/26))

**Changed**
- **Missile specialists shoot faster:** a fighter or gladiator with a chosen bow shoots 3 a round,
  then 4 from 7th level; a sling, staff sling or chatkcha 3/2, then 2 (AD&D's specialist's rate
  for the sling, a step above it for the others). A grand master shoots once more a round, as in
  melee. Before, missiles kept the game's rate. (Weapon specialization. The Characters tab shows
  each missile weapon's rate.)
- **Rangers and the bow:** every ranger has expertise with the bow on top of the weapon type it
  chooses, and a ranger's expertise with a missile weapon gives the same rate of fire, with no
  other bonus.

**Docs**
- **Attacks a round:** a table in the guide by skill (non-warriors, a weapon type not chosen,
  expertise, specialized, mastery, grand mastery) and level, for melee, bows and the other missile
  weapons.

## Pull request #25 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/25))

**New**
- **Bone and obsidian great axes and a bone dagger,** each with an icon. A warrior's starting
  great axe is now bone (obsidian for a fire or earth cleric), and a water cleric's starting
  dagger bone. Water and fire clerics' warriors can now choose the great axe, and water clerics'
  the dagger.
- **Replacements for what breaks:** the Weapon Merchant sells great axes in all three materials,
  the metal pick and the bone dagger. Jark sells bone and obsidian great axes and the bone dagger,
  and every Wild Mul carries a bone great axe. Kel sells two sets of Thieves' Tools.
- **Defilers leave a body:** each of the game's two kinds of defiler carries a dagger, one
  obsidian and one bone. The game leaves no body for someone who carried nothing.
- **Mindshard from Maris's pocket:** a thief can lift it, as Shadowseeker and Gutterknot, for 200
  XP.

**Changed**
- **One box for the new items:** the Options tab's four item boxes are one, **New items, magical
  and mundane**. The arena's ring keeps its own box, and the "Give thieving tools now" button is
  gone (Kel sells them).
- **Weapons off the allies:** Krikor's bone axe, Uskuye's metal great axe and Lt. Kwerin's metal
  pick are gone; the Weapon Merchant sells the metal ones.
- **The Sunking Crown** gives Protection from Evil, not the 10' Radius one.

**Fixed**
- **The game's Sling +1** (in a chest) showed a blank icon: its picture was missing from the
  game's data. It now has one, the Sling's with a glow.

**Docs**
- **Item icons** in every item table of the guide.
- **[Every magic item](obsidian-edition/ITEMS.md#every-magic-item)** and **[Every mundane
  weapon](obsidian-edition/ITEMS.md#every-mundane-weapon):** each item, the game's and the
  Ledger's, with its bonus or power and who sells or carries it; the magic weapons of each weapon
  type for weapon specialization.
- **Mundane items** in a table of their own in New items, and the Ledger's weapons in the acid
  saving throw table.

## Pull request #24 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/24))

**New**
- **Magic weapons for the classes that had too few,** each with an icon and a story from Alagorn:
  - **Galefang,** a metal dagger +2 an air cleric can wield (a new item type: none of the game's
    daggers are an air cleric's), on the Rogue Shaman;
  - **Mindshard,** an obsidian short sword +1, on Maris, and **Stillwater,** a bone short sword
    +1, in the chest Chaya gives as her apology: a psionicist's, alone or with a cleric's;
  - **Linebreaker,** a metal polearm +2, on the Troop Leader, and **Thornwall,** a bone polearm
    +1, on the slave pens' weapon rack in place of one of its two plain ones (the rack gets an
    object of its own: the Lower Castle's is the same object).
  - Alagorn's weapons menu now has more items than a script has locals: the last are kept in the
    Ledger's flags.

**Fixed**
- **Drakejaw** (pull request #23) was never on its Magera: the game read its own Gemfields region,
  not the Ledger's copy, which DSCLOG now opens instead.

## Pull request #23 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/23))

**New**
- **Three magic axes,** each with an icon and a story from Alagorn:
  - **Drakejaw,** a bone axe +1, on one of the Magera guarding the wagon's prisoners (he gets an
    object of his own);
  - **Glasshewer,** an obsidian axe +2, on the elven slavers' Templar;
  - **Headsman,** a metal great axe +2, in the arena Announcer's stash.
  - Alagorn's weapons are told by a copy of his script 213 (222), so no script overflows the
    game's script buffer.

**Changed**
- **The Elven Leader's Gythka is +2** (was +1). It also no longer takes Kreenfang's icon, which
  any Gythka +1 did.

## Pull request #22 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/22))

**Changed**
- **Cermak, of the game's own party, specializes in the long sword and the axe** (was the club),
  which count once his gladiator levels do again.

## Pull request #21 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/21))

**New**
- **The Tome of Understanding:** Father Garyn's gift when the party brings him the ranike pith.
  Read like a scroll (right-click it, click its icon), it gives the reader a point of WIS for good
  (at most 25) and is used up. It is the game's book, with a night-steel cover and an emblem in
  the fire colours of its magic items.
- **The game's own party is made ready for the rule changes,** for a new player who presses START
  GAME. Gerakis specializes in the long sword and the gythka and carries a bone gythka in place of
  his club; K'ratchek specializes in the chatkcha; Cermak in the long sword and the club. Cilla, a
  druid who can't wear armour, has her leather armour taken away and knows Armor instead.
- **The Warden's Plate,** plate mail +1 in four pieces: the Helm on Dagolar's body (Cloak of
  Bravery while worn), the Arms in the Lower Castle's treasure chest with Dark Flame, the Legs in
  the Gemfields' chest, the Chest on Balkazar's body (Resist Fire while worn). Plate is AC 3 chest,
  2 arms, 2 legs (DSCLOG's new item types), each +1; the helm is the game's metal helm +1. Each
  piece has an icon of its own and is drawn on the figures. (The magic weapons' switch.)
- **The Cloak and Boots of Elvenkind,** for thieves and rangers only (multiclasses too). The cloak
  is the Elven Leader's gift with his Gythka +1; the boots are in the buried chest of Kel's
  caravan. With the hiding rule, the cloak's wearer hides in shadows on 95 or less under the open
  sky and 90 under a roof (not halved by the light), and the boots' wearer moves silently on 95 or
  less. Their item boxes say so (`Hide 90-95%`, `Move 95%`). (The magic weapons' switch.)
- **The Flame Blade,** an obsidian long sword +1 in the pack of the Hot Springs' Templar. Its
  blade casts the fire clerics' Focus Heat on what it hits (2d6 fire, a save for half), as the
  game's Dark Flame does Burning Hands. Obsidian, so a fire cleric can wield it. (The magic
  weapons' switch.)
- **Alagorn knows every new magic item,** each in the menu the game would put it in: the Flame
  Blade, the Warden's Plate (a part of Haldren's story for each piece), the Cloak and Boots of
  Elvenkind, the Bracers of Defense, Arrowbane, the Sunking Crown, Inixhide, the Rings and Cloak of
  Protection and the Tome of Understanding. There is one story for each kind, as with the game's
  own items: the four pairs of bracers share one, and so do both rings. His clothes, rings and
  other items are told by copies of his script 212 (220 and 221), so no script overflows the
  game's script buffer.

**Changed**
- **The world's new items are in the game's own data,** not added while you play. The launcher
  writes them into their people's and chests' objects, so a new game makes them where they belong.
  The slave pens' items (Kurzak's Shadowseeker and helm, Legcrusher's armour, Pehtucl's cloak and
  ring) and Kreenfang (the arena's dead body's gythka) are in the data too. The Boots of Elvenkind
  are in the buried chest when it is dug up; the bone scale set's arm and leg pieces and helm are
  in the slave pens' chest with its chest piece; one Castle Guard and one Undermountain miner have
  objects of their own for their items. The Options tab's switches take effect from the next
  start, in regions not yet visited.
- **The Elven Leader gives the Cloak of Elvenkind himself,** after his Gythka +1, with a line of
  his own. When it can't be carried he leaves it on the ground beside him, as with the Gythka.
- **Grey's Scale's arm and leg armour are AC 3** (the game's are 2).
- **A new warrior with a staff sling keeps its shield,** as with a bow. Both go in the missile
  slot, and the game asks nothing of the hands for them; the shield went into the backpack before.
- **The magic weapons and Legcrusher's leather have names:** the Club +1 is Gutterknot, the Pick
  +1 Deepbiter, the Staff Sling +1 Windlash, the Short Sword +2 Greenbright and the Leather Chest
  Armor +1 Inixhide, each with a story from Alagorn. Greenbright is now on Arant, who holds the
  captured gladiators (the Elite Guards are only in the final fight). A thief can lift Gutterknot
  from Churrr's pocket for 200 XP, as Shadowseeker from Kurzak's.
- **A circlet and a crown, worn on the head and not armour:** Arrowbane, a silver circlet sold by
  Kel, keeps Protection from Normal Missiles on its wearer; the Sunking Crown, worn by Keldar,
  Protection from Evil, 10' Radius. Neither gives AC, nor stops bracers of defense or a
  preserver's spells. Each has an icon of its own and is drawn on the figures (a silver band with a
  stone; a gold band with points). (The magic weapons' switch.)
- **Bracers of defense give nothing with a helm on,** as with any armour. A shield and rings and
  cloaks of protection still go with them.

**Fixed**
- **Alagorn's clothes with none carried:** he said "no magic clothes", then "Ah, magic clothes",
  and showed an empty menu. The game's two nested tests for clothes are now kept.
- **Armor, spell 0, was missing from the Ledger:** the Spells tab left it out and the dice log
  would have named it "spell 0". The game numbers its spells from 0.
- **No manual check:** the dragon asking for a word from the manual when the party first leaves
  the sewers (the game's copy protection) no longer comes. The game goes on as if it had been
  answered.
- **The Ledger's window started with an error,** from an indentation slip in its Options code
  since pull request #20. A test now compiles every module.

**Docs**
- **The documents are shorter and better organised:** the front page gives an overview and only
  the latest pull request's news. The guide's dice log lines are grouped by topic, its internals
  moved to DEVELOPMENT.md (with the command-line use), and its new items described once. Released
  pull requests here are summarised.
- **The README's new items** are one item to a row, with the prices and the Options tab's boxes
  after the table. The ranger's row no longer names a fighter/ranger (the game has none).

## Pull request #20 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/20))

**New**
- **The new plain weapons in the world** (a new content switch, on by default). The Weapon
  Merchant and Jark sell the bone and obsidian short swords and axes and the obsidian mace, and the
  Weapon Merchant a plain metal short sword. Merzol, Krikor and Chaero carry one, and every Tari in
  the warrens, Renegade and Wild Mul has one as loot.
- **Bracers of defense** (a new content switch with the magic weapons, on by default): AC 6 on
  Mikquetzl, AC 5 on Wyrmias, AC 4 on Balkazar and AC 2 on Dagolar, 20,000 to 40,000. Worn on the
  arms, they give nothing while armour is worn on the arms, legs or chest, and are not armour to
  the class rules (a preserver casts in them).
- **Magic weapons of the weapon types the game has none of:** a Club +1 on Churrr in the warrens,
  a stone Pick +1 on one of the Undermountain folk, a Staff Sling +1 sold by the Bowyer and a metal
  Short Sword +2 on an Elite Guard. Each has an icon of its own and is priced as the game prices
  its own: the melee ones as its Obsidian Bloodwrath +1, 20,800 a plus; the staff sling as its
  Sling +1, 2,800.
- **Metal daggers, maces, great axes, picks and polearms,** which the game has none of plain: one
  each on Tobrian, a Templar of the slavers' camp, Uskuye, Kwerin and a Castle Guard. An earth
  cleric may now take the great axe and the polearm, and starts with a metal one.
- **Weapon specialization** (a new rule change, on by default). Fighters and gladiators specialize
  in weapon types (+1 to hit, +2 damage), fighters on to mastery at 5th level (+3, +3) and grand
  mastery at 9th (the damage die a size larger and an attack more); rangers take expertise. A
  warrior with a weapon of another type attacks at AD&D's plain rate.
  - Sixteen weapon types, chosen on the creation screen's new WEAPON SPEC pages, greyed as the
    game's disciplines are. A multiclass warrior's are limited to the weapon types it may use some
    weapon of, in any material (a fire cleric's obsidian long sword).
  - A new warrior starts with a plain weapon of its type in a material it may use. New bone short
    swords and axes, and obsidian ones for fire and earth clerics, since the game has only Kurzak's
    short sword and a metal axe; an obsidian mace pictured without Blackmace's glow; a plain great
    axe without the Great Axe +3's gem. A two-handed weapon puts the starting shield in the
    backpack.
  - A gladiator's 3rd and 4th (and any warrior's from before the rule) are picked at a level
    gained, in the game's own pop-up for a psionicist's new power.
  - The weapon types are listed on the Effects screen and counted on the DAM lines and in the dice
    log. The Characters tab lists each character's weapon types (`Weapons: long sword (grand
    mastery)`) and the attacks a round with each weapon held (`Attacks: 3/2 a round with Long
    Sword, 1 with Axe`).
- **Class restrictions** (a new rule change, on by default): psionicists, multiclass thieves,
  preservers, druids and clerics are held to their own limits on armour, shields and weapons
  whatever their other classes allow, the strictest winning. A multiclass preserver casts no
  spells in armour: its spell slots are headed NO SPELLS IN ARMOUR on the USE screen, and the
  Characters tab says "(no spells in armour)".
- **Multiclass hit points** (a new rule change, on by default): each level's die and CON's bonus
  are divided between a character's classes, as in AD&D, at creation and at every level. The dice
  log shows the share. Meant for a new game: ticked during one, a character's next level shares
  CON's bonus for all its levels.
- **Hit dice, the better of two** (a new rule change, on by default): every character's hit die is
  rolled twice, at creation and at each level, and the better roll kept. The dice log shows both.

**Changed**
- **The Ledger's magic items are priced as the game's own:** the Rings and the Cloak of Protection
  +1 15,000 (were 5,000), Leather Chest Armor +1 6,000 (was 3,000), Kreenfang 20,800 (was 18,000),
  as the game's Gythka +1. Ones already given are repriced.

**Fixed**
- **The Characters tab read the game as if every rule were off** in its THAC0, attacks and
  specialization lines. It now uses the rules ticked.
- **Character creation in the dice log logged every roll:** one click on the die rolls a whole
  character several times while it tumbles, and the log gave every one. When rolls came too fast
  to record, the hit point line took CON from an earlier one (37 logged where the game had 40).
  Now only the character the die stops on is logged, each ability and the hit points checked
  against the screen (`DEX 19 (its rolls came too fast to record)`).
- **"No hit point roll" on a level gained:** the dice log said the game rolls hit points only when
  a character's highest class level rises. It rolls for every new class level; a level that leaves
  the most hit points unchanged only added a fraction (the game divides the whole total by the
  classes).

**Docs**
- **The README is shorter** (2,974 lines to about 2,300). How each part works (the helper's
  interrupts, the game's offsets and flags), how the dice log works, what's known of the game's
  data and the development notes are in a new `obsidian-edition/DEVELOPMENT.md`, each README
  section linking to its part. "What it does" is a short overview. The thieves' skills and
  backstabs, and the saving throws, are each one section with their rule changes; the two-weapon
  rule sits with the dice log's two weapons. The new items are one section with a table, Kalzith
  and Semyon one of new people told as a player meets them, and the helms' and boots' rules one.

## Pull request #19 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/19))

**New**
- **View Character names the class that levels up next:** for a character of more than one class,
  the XP in brackets on the experience line names the class that reaches its next level there
  (`EXP:87230 (90000 Pr)`). A letter for each class, but Pr and Ps for preserver and psionicist;
  both are named when two level up at the same XP (`(20000 Pr/T)`), and a class already at the
  highest level never. One class is as before. (The patched game's `INT D2h`, where the game adds
  the bracket.)

**Changed**
- **Kalzith sells Shield and Burning Hands** in place of Magic Missile and Color Spray (3,000
  each), so none of his scrolls is one the game has (Color Spray's is in the sewers). Magic Missile
  and Color Spray scrolls he stocked before become Shield and Burning Hands, wherever they are.

**Fixed**
- **Kalzith's prices:** Blur 6,000 (was 3,000) and Haste 9,000 (was 12,000). They were taken from
  the game's scrolls with the spell numbers read one off (Wall of Fog's and Flame Arrow's). The
  game has no scroll of either, so they're its price for the spell's level, 3,000 a level. His
  stock is repriced when the Ledger next sees the game.

## Pull request #18 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/18))

**Release 1.1.0:** the version, its notes, and pull request #17 marked merged in the READMEs.

## Pull request #17 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/17))

**New**
- **Searching junk, hay and wardrobes in the dice log:** each search's roll, what it found, and
  how far the count of finds has got. A rat's bite or a falling pot shows its damage roll.
- **More saves:** 40 instead of the game's 10, on four pages of ten in the save and load window.
  PAGE 1 to PAGE 4 buttons sit under EXIT, and PgDn and PgUp go to the next page and the one
  before.
- **More characters:** 29 saved characters instead of the game's 19.
- **Rule change, items saving against acid:** a worn piece of armour or a held melee weapon the
  Rampager's acid or the Babau's corroding touch could destroy needs the easier of the game's
  number and AD&D's save against acid for its material, less its plus and 1 more for a magical
  power.
- **Rule change, rings and cloaks of protection as in AD&D:** of two rings only the better counts,
  and a ring gives no AC with magical armour. A cloak of protection does nothing with magical
  armour, metal armour or a shield in either hand; natural armour is fine.
- **A worn belt helps a thief:** +5 to picking pockets and opening locks, counted by the game's
  own lock picking and by the Ledger. Its item box says `Pick +5, Lock +5`.
- **Kreenfang and Shadowseeker:** the 2 handed Bone Gythka on the dead body by the stone arch in
  the arena is Kreenfang, a gythka +1. Kurzak's short sword is Shadowseeker, a short sword +1
  whose wielder sees the invisible.
- **Alagorn knows Kreenfang and Shadowseeker:** the Painted Badlands wizard who identifies magic
  items has each in his menus when the party carries it, with a story of its own.
- **200 XP for lifting Kurzak's sword:** the conversation says the thief lifts "a metal short
  sword" and receives 200 experience points, with the quest's sound, given by the game's own
  routine for a quest's XP.

**Changed**
- **Kalzith's scrolls at the game's prices,** 3,000 to 12,000 ceramic: the game's own price for a
  scroll of the same spell, else its price for the spell's level.
- **A monster's alignment in the Look box:** `THAC0 17 AL TN`, the alignment in two letters. The
  description in the dialogue window and the dice log's `Look:` line name it in words.
- **The Options tab's sections open and close:** each group of switches is under a heading to
  click, so the tab is short. Which are open is remembered.
- **The whole party walks as fast as the leader alone at the fastest game speed:** the Ledger's
  shadows and dust are drawn much more cheaply, and look the same.
- **Cloaks and boots say what they do:** with the cloak and boots bonuses on, their item box says
  `Hide +10` or `Move +10` under the name.
- **Boots are named "Boots (Speed+1)"** for the boots rule, so their extra move in a fight isn't
  mistaken for the item box's `Move +10`.
- **Plain cloaks, boots and belts cost 24** (the Leather Cloak was 20). Magic ones keep their
  prices.

**Fixed**
- **DELETE in the roster deleted the wrong character,** a bug of the game's own. It counted the
  row clicked from the top of the list, not of what was shown, so with the list scrolled down
  another character was deleted.
- **Kalzith's and Semyon's questions are asked once a talk:** a reply that doesn't end the talk
  leaves the list once chosen, as the game's own people's do, and is back the next time you talk
  to them.
- **The load window shows an empty page:** PAGE 2 to PAGE 4 did nothing in the load window when
  that page had no saves.
- **A shield on a figure walking side-on showed nowhere.** It is now held forward of the chest,
  its near half showing.
- Smaller: a character not yet played counted as not Okay, so a new thief's skills all showed 0
  on the inventory screen. The Look box showed an AC the Ledger worked out for another creature:
  the arena's first fight comes too soon after the opening one to tell them apart by the game's
  time, and a Slig showed the opening fight's Defiler's AC -9. The Ledger's new item pictures
  wiped an item's spell: changing an icon cleared four bytes of the item where the game's picture
  cache is two.

## Pull request #16 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/16))

**New**
- **Semyon breaks out with Scar:** recruit Semyon before the fight with Scar and take up Scar's
  offer to break out, and Semyon comes along to the slave pens with Scar's men. He fights the
  guards on the party's side and has a line of his own for the breakout.
- **Game speed on the Options tab:** the launcher gives DOSBox 20,000 cycles by default; GOG's own
  speed and 30,000 can be chosen. The companion's README suggests system requirements for each.
- **Faster walking with gear shown:** the party's figure pictures keep only the room their gear
  needs while walking.
- **New content switches:** Kalzith, Semyon, the cooked vulture, the slave pens' gear, a worn
  cloak's and boots' bonuses to hiding, and the Effects screen's click keeping a spell can each be
  switched off on the Options tab.
- **Crash reports:** when DOSBox crashes or the game stops with an error, the game's message stays
  on screen. The Ledger saves a report in `crash-logs` with how it closed, what was on screen, the
  switches, and the end of the dice log and dialogue.
- **The Trustee knows Semyon got away:** if Semyon broke out with the party and lived, the Trustee
  says so after the escape, instead of "Every single one" for all the pens.

**Changed**
- **Kalzith and the alarm:** while the escape's alarm sounds he has a line for the party and no
  talk, as the pens' other slaves do.
- **A vanished bone scale piece is written up:** the set is still given once a game and never
  again. Should the Bone Helm, or the arm or leg piece, vanish, the Ledger saves a report on what
  became of it in `crash-logs`, and the log says so.
- **Finding the Ring +1 is worth 50 XP** to whoever searches the Tied-up Prisoner's body, given as
  the game gives a quest's, once.
- **Picking pockets is with the Thieves' Tools only, by default:** the Options tab's switch is now
  about the tools, and P in a conversation is a choice under it, off unless ticked.

**Fixed**
- **A crash in the opening fight:** when the game couldn't make the first of two drawing areas of
  the map's view, it freed the second one anyway with a number it had never set.
- **The bone scale set in a second new game:** the Ledger remembered it as given across games, so
  a later new game never had it. It is now kept for each game.
- **Thieves' Tools clicked between turns** (as an area changes) stopped the dice log with an error.
- **The game's flags** were read and written through a null pointer at times. The Ledger's guard
  stopped the writes.
- **Crash messages readable:** a game that stopped in graphics mode left its error message
  invisible. The screen goes back to text before the message.
- From a review of the code:
  - **Clicks after Tab + Enter:** for a few seconds after Enter, anything the next character
    clicked could still count as the enemy chosen before.
  - **Kalzith and Semyon in fights:** people past the map's 256th thing were missing from the
    Ledger's list of who is in a fight, so they had no ring, no Tab, no HP lines and no "killed"
    line.
  - **A thief who went last and is next** after someone first who can't act lost their turn line
    and hiding roll.
  - **Two halved hits seen together** were put down to the first, and the second later logged as
    doing nothing.
  - **The mouse wheel's watch** (Windows) was started again on every reconnect without stopping
    the last one.
  - **Kalzith only with his object:** a copy of the game whose objects lack what he is made from
    no longer gets his scripts, and a clash over his scrolls' pictures no longer loses every icon.
  - **Speed:** the rings' and dust's colour tables are worked out once for a palette, not every 30
    seconds.

**Docs**
- **The READMEs reorganised,** each with a table of contents: the guide's sections grouped as the
  Options tab is, the window's guide beside how to start it, the memory-mapping steps under
  Development. This changelog moved out of the main README into its own file.

## Pull request #15 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/15))

**READMEs after pull request #14:** the changelog, the cooked vulture quest and its screenshot, and
the new log lines.

## Pull request #14 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/14))

**New**
- **What the party wears, on the map:** each character's figure shows their weapons and shields,
  bow and quiver on the back, armour, helms as circlets, cloaks, boots and belts, walking and
  fighting. It changes as soon as their gear does.
- **Kalzith, a defiler in the slave pens:** a slave the templars put in the arena now and then,
  kept in a pen of his own, with a face of his own.
- **Semyon in the slave pens,** once he has left the arena: in a pen of his own above Kalzith's,
  with his own conversation.
- **Dinos and the Trustee know about them:** their "who else is in here" questions also ask about
  Kalzith, and about Semyon once he is in the pens. If either is killed, they speak of him as of
  the game's dead.
- **Shadows under every figure on the map:** each living creature's outline, laid down toward the
  lower right, see-through and in the floor's own colours. They are drawn on the floor before the
  walls and figures, so everything in front stands on them.
- **Scrolling the map with the mouse:** pressing the wheel and moving drags the map with the
  pointer, in fights too, and in Windows turning the wheel scrolls it.
- **Dust behind walking feet:** puffs on sand and dirt behind anyone walking, spreading and fading
  in about a second, under the walls and figures.
- **Tab chooses an enemy, Enter attacks it:** on a party member's turn in a fight, Tab picks an
  enemy, marked by a red ring, with the view scrolled to it. Enter attacks it as a click on it
  would, even when someone stands in front of it.
- **Hits that do less than rolled** in the dice log: a weapon hit that took part of its damage, or
  none, with what the monster's defences say.
- **The quest sound for the vulture:** giving Dinos the cooked vulture plays the sound the game
  plays when a quest is done.
- **Cloaks and boots help thieves and rangers hide:** with the stealth rule, a worn cloak adds 10
  to hiding in shadows and worn boots 10 to moving silently, up to 95.
- **Regeneration in the dice log:** a hit point back by itself, which the game gives anyone with
  CON 20 or more, is logged as such.
- **A safety net against stray writes:** the Ledger never writes over the start of memory or the
  first bytes of the game's data. A write stopped there is named in the dice log.

**Changed**
- **The Effects screen no longer ends a spell's effect when its icon is clicked.**
- **Windows' security warning only once:** after the first `.bat` file is let through, the Ledger
  takes the download mark off the files in its own folder, so the others start without asking.
- **The vulture quest is part of Dinos's talk:** while the party carries the cooked vulture, his
  first menu has "We cooked the vulture from the arena." just before "Goodbye." His answer is in
  his own dialogue window, with his portrait, and the XP comes as the game's quests give it, in
  the game's own window. The vulture is no longer used on him from the inventory.
- **Cat's Grace's icon** is a cat's paw print instead of a cat's face.
- **Dinos's vulture lines** are his own words, without narration (the game's conversations are
  people speaking).

**Fixed**
- **DOSBox crashes, garbled figures, freezes and "Null pointer assignment":** the gear writer kept
  writing a party picture over memory the game had freed and given to something else.
- **Kalzith said he had nothing left to sell** after one purchase: while a save loaded, the Ledger
  could read the new game's flags with the last game's Kalzith and mark it sold out.
- **The vulture's reward came in the dice log when a game was loaded,** and its XP and rest were
  given then. The flag was read from memory still being loaded.
- **A thief first in a round didn't hide:** someone who had the last turn of one round and the
  first of the next got no new turn in the log, so no hide in shadows or move silently roll.
- **Tab + Enter froze the game:** after Enter, the walk to the chosen enemy stalled, sometimes
  until a mouse click.
- **The party's gear showed late after an area change:** the Ledger looked for the area's newly
  loaded pictures only every 10 seconds, and dressed the party with its slower checks. A party
  walking off as the area loaded stayed plain meanwhile.
- **Cat's Grace was missing from the Effects screen:** its effect had no icon in the game's table
  of effects, and the screen shows only effects with one.
- **Kalzith's scrolls cast their spell instead of teaching it:** the game teaches only from scroll
  objects numbered 1400 to 1499, and his were 1001 to 1006.
- **Figures' shadows fell the wrong way,** toward the lower left, while the walls', bones' and
  stones' shadows on the maps fall toward the lower right.
- **Kalzith's and Semyon's Look box** sometimes lacked the HP, AC and THAC0 lines: the Ledger only
  looked among the map's first 256 things, and the game numbers them anew, sometimes past that.
- **The slave pens broken by Kalzith:** Kurzak vanished after leading the party in, people were
  missing, Merzol didn't stop the party, the doors' "pick the lock" and "knock" and the main
  door's "Summon Kurzak!" were gone, and the water jug couldn't be filled.
- **Figures took extra steps after their turn in a fight:** to have figures drawn again with their
  shadows, the Ledger marked them "changed", which in a fight could set one walking again.
- **"Killed" lines for everyone in an area the party left:** walking from the slave pens into the
  arena logged most of the pens as "is killed".
- Smaller: Kalzith's scrolls taught the spell before their own; "Who are you?" hung the game when
  asked of Kalzith; picking pockets said "won't get another chance" to everyone in a new game with
  the same party, since the last game's tries were remembered.

## Pull request #13 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/13))

**The Release workflow can be run by hand,** making the version's tag.

## Pull request #12 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/12))

**Release 1.0.0:** the version, its release notes, and a workflow that builds the release zip.

## Pull request #11 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/11))

**New**
- **Cat's Grace looks like itself:** its own icon and its own description in the spell box,
  instead of Flaming Sphere's.

**Changed**
- **Getting started:** open the Ledger first, pick the options, then Start the game from it.

**Fixed**
- **The slave pens' gear was given twice** to a game loaded after it was given. None of it is
  given where it is already in the game.
- **The bone scale set was added twice** to a game loaded after it was added. It is now added only
  where none of its pieces is.
- **Prices:** Leather Chest Armor +1 is worth 3000, the Cloak of Protection +1 5000 and the Rings
  of Protection +1 5000, as magic items. Ones already in a game are repriced.
- **Dinos takes the vulture as soon as a fight is over:** the Ledger now reads the game's own
  combat flag.
- **Thieves' Tools can't be used in a fight,** only out of one.
- **The dice log and the Dialogue tab keep up with the newest lines;** scrolling up to read back
  still holds the place.
- **No more log lines for the Ledger's items** handed out: they're there to be found.
- **The Bone Helm** can only be worn by those who can wear bone scale armour (not thieves).

## Pull request #10 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/10))

**Fixed:** half-giants' two-handed weapons in one hand. The rule didn't take effect.

## Pull request #9 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/9))

**New**
- **Rule change, thief skills from AD&D's table:** a skill is AD&D's average for the thief level,
  plus the race's adjustment, plus Dark Sun's DEX adjustment.
- **The bone scale set:** where the Bone Scale Chest Armor is found, its arm and leg pieces and a
  new Bone Helm, coloured to match, are found with it.
- **Rule change, half-giants wield two-handed weapons in one hand,** with a shield or a light
  weapon in the other.
- **Names in colour in the dice log:** each party member's in a colour of their own, monsters' in
  red, bold, all at 4.5:1 contrast or more.

**Changed**
- **The Options tab scrolls** when the window is too small to show it all.
- **Options:** the Ring +1, picking pockets and the thieving tools button sit under Rule changes,
  with the other changes to play.

**Fixed**
- **A game that stops with an error** leaves its message on screen, and the dice log says how
  DOSBox closed, telling a crash of DOSBox's own apart.
- **Picking a pocket after loading a save:** a try made after the save is forgotten when it's
  loaded, so that person can be tried again.
- **XP taken away and given back between areas** is no longer logged as a loss and a gain. A loss
  that stays is logged after a minute.
- **A monster's AC in its Look box** could be an earlier fight's creature's: a slig in the first
  arena fight showed the opening fight's Defiler's AC −9.

## Pull request #8 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/8))

**New**
- **Rule change, levels up to 10:** every class can reach 10th level, at AD&D's XP.
- **Gear for the slave pens' bosses,** given once a game with the Ledger running. Kurzak has a
  metal Short Sword (1d6, a new item type; a thief can lift it) and a leather Helm; Legcrusher,
  Leather Chest Armor +1; Pehtucl, a Cloak of Protection +1 (a new item type: +1 AC and +1 on
  saves, as the ring) and a Ring of Protection +1 (a thief can lift it).
- **Rangers hide in shadows and move silently too,** with AD&D's ranger chances: the full chance
  outdoors and half indoors, the reverse of thieves.
- **Item icons of their own** for the Short Sword, Leather Chest Armor +1, the Cloak of Protection
  +1 and the two Rings of Protection +1, made from the game's plain ones.

**Changed**
- **Thief skills have no equipment penalty:** the game took 5 to 10 off some thief skills for
  anything in the legs slot, the quiver or either hand. It no longer does in games started with
  the dice log.
- **The inventory screen shows hide in shadows** in hear noise's place. The Ledger's own screens
  show both.
- **Pick pockets lifts a short sword** too, though it weighs more than other small things.

## Pull request #7 ([merged 2026-10-01](https://github.com/daaki85/darksun-obsidian-edition/pull/7))

**New**
- **Rule change, AD&D's two-weapon penalties:** a non-ranger with a melee weapon in each hand
  attacks at −2 with the main hand and −4 with the off hand, offset by the DEX reaction
  adjustment.
- **Rule change, the spell save:** spells are saved against with the spell save, not
  petrification/polymorph.
- **Rule change, DEX instead of a doubled d20:** on saves against fire, cold and electricity, the
  DEX defensive adjustment counts instead of a doubled d20.
- **Cat's Grace,** a new 2nd-level wizard spell in Flaming Sphere's place: +1d6 DEX, at most 24,
  working exactly as Strength does for STR. Untick the rule and Flaming Sphere is back.
- **REAC and DEF on the inventory screen:** REAC sits beside SP, DEF on the AC line.
- **Rule change, hiding in shadows to backstab:** a thief whose turn comes with no enemy beside
  them rolls hide in shadows, then move silently.
- **The cooked vulture quest:** take the cooked vulture to Dinos in the slave pens. He cooks it
  for the party, who eat with him.
- **32 new entries in the game's item name table,** for the Ledger's own items.

**Changed**
- **Turn pop-ups in the game are off by default,** and have three levels: at the least, in short,
  or in detail.
- **Spell slots** only show the spell levels the character can cast.

**Fixed**
- **Item names numbered past 255** were read wrongly by the Ledger (for example, Serpent Boots).

## Pull request #6 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/6))

**Fixed**
- **Boots gave no extra move:** the rule looked at the wrong equipment slot.

**Docs**
- README screenshots retaken (move silently, boots, Thieves' Tools, Options).

## Pull request #5 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/5))

**New**
- **A Give thieving tools now button** on the Options tab.
- **Thieves' Tools** get a name of their own and a leather satchel's picture instead of a key's.

**Fixed**
- Smaller: the arena ring, and the backpack cell the thieving tools went into; only one set of
  tools per thief; long lines on the Options tab wrap to the window.

## Pull request #4 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/4))

**New**
- **Picking pockets:** press P in a conversation, with a thief leading. Small things only; a move
  silently roll decides whether a fumble is noticed; a few coins when there's nothing else to take.
- **Thieving tools:** every thief starts a new game with a set.
- **Ring of Protection +1,** found on the Tied-up Prisoner in the arena.
- **Items named for the rule changes** ("Helm (AC 1)", "Boots (+1 Move)").
- **Thief skills as they stand:** equipment penalties and effects, in the game and in the Ledger.
- **Start the game from the Ledger's window,** and a triple-size game window.

**Fixed**
- Smaller: fights restarting or crashing after a pop-up's Continue; the arena's opening show; the
  Announcer's name being replaced by one learned mid-fight.

## Pull request #3 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/3))

**New**
- **In the game:** THAC0, saves and thief skills on the inventory and View Character screens;
  spell slots on the USE screen; each turn's rolls in the game's own window, with monsters' turns
  in a pop-up of their own; monsters' defences in the Look box.
- **Spells tab:** what every spell and psionic power does.
- **Launchers:** one for the game alone with the in-game additions, and one for the game and the
  Ledger together.
- **Script decoder:** every thief and ability check in the game's scripts.
- **The first rule changes:** helms give AC 1; boots give a move more in a fight.
- **Saving throws** with each modifier named.
- **THAC0** shown with each weapon, fresh on every redraw.
- **The Ring +1** (+1 AC and saves).

**Changed**
- **No packaged .exe:** the .bat files offer to install Python instead.

## Pull request #2 ([merged 2026-09-29](https://github.com/daaki85/darksun-obsidian-edition/pull/2))

**New**
- **The game's own portraits and font,** read from your install at run time.
- **A Characters tab** laid out like the game's View Character screen: each character's equipment
  by slot, effects with rounds or charges left, and spell slots.
- **Spell detail in the dice log:** damage formulas, durations and what a save does; rules for 20
  more effects; healing, Magic Missile and Slay Living dice labelled; Dispel Magic per effect.
- **Thief skill rolls,** with what each chance is made of.
- **Psionics:** powers named, PSP spent logged, magic resistance changes.
- **Saves:** the chance to save, and what the save left.
- **Dialogue:** the reply you picked, and named speakers.
- **The log at a glance:** round headers, hit chances, HP left, and a details switch.

## Pull request #1 ([merged 2026-09-28](https://github.com/daaki85/darksun-obsidian-edition/pull/1))

**New**
- **The party viewer,** reading Shattered Lands' character records live.
- **The dice log:** attack bonuses, weapons, saving throws, spells and buffs; kills and XP, weapon
  breaks, level-up HP and AC make-up; attacks from behind and backstabs (with the damage
  multiplier); each round's initiative order and how each score was made up; the two-weapon
  adjustment, and character creation rolls.
- **A dialogue tab.**
- **Accessibility** (AODA / WCAG 2.0 AA): contrast checked in tests, text size controls, full
  keyboard access, and logs you can save.
- **Double-click launchers** and a step-by-step Windows guide.
- **The name *Templar's Ledger*,** and a window in the game's colours.
