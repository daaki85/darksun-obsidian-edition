# Research recipes: memory, sounds, pictures, timing, scripts and other targets

Part of the playtest guide ([PLAYTESTING.md](PLAYTESTING.md): read its startup procedure before any
in-game test). These recipes are for writing the game's memory for a test and for finding out how
the game works rather than for checking a change: the game's records and memory edits, its sounds,
the see-through figures, the picture store, the figure prototypes in the game, frame rate and cycles, the picture and the music device, its scripts, the unchanged game,
the recompiled program and Wake of the Ravager. Tools: [TOOLS.md](TOOLS.md).

## Memory edits for a test

The game's records as a test reads and writes them, moved here from the guide's recipes (which name
each tool and link here: [memory edits for a test](PLAYTESTING.md#memory-edits-for-a-test)).
Everything here is memory only: **never save after** (the guide's rule 8), and restore what was
raised before stopping.

### The party and the map's people

- **The game clock**: the dword at DS:9B72h's far pointer, in seconds (a rest adds 28,808).
- **The party's item lists**: worn things (armour, a shield, rings, a cloak, ammunition) at the
  creature record's +08h, held weapons at +0Ah, the backpack at +0Ch; the inventory screen files
  by the type's kind, and the game's AC counts +08h only. `itemlists.py` shows where things are;
  swapping two list words in memory (the record's +08h/+0Ah/+0Ch) is a quick, undoable test of
  what a list does.
- **Ability items and memory edits**: an item's +0Fh is also the spell the game casts on the wearer
  as it is put on (FAh-FFh: STR to CHA, +0Eh the amount), kept as an effect (the item's byte 2
  links it, for taking it off). Picking an item up or putting it down recounts the scores (opening
  the inventory doesn't); clearing the bytes of a worn item leaves its effect behind: reload.
  `itemedit.py MEMBER SLOT [slot= e= f=]`, `sheetedit.py MEMBER [levelN= flags|=]` and `party.py`
  (classes, flags, scores, items) are the tools.
- **A class in memory** (logs/2026-11-10-air-cleric-gythka-shadows.md): a member's sheet at the far
  pointer DS:1661h + (creature +4) x 47h; classes +21h, levels +24h, flags +12h (the offsets: [the
  sheet's table](../obsidian-edition/DEVELOPMENT-INTERNALS.md#whats-known-of-the-save-and-records)). Then take a held item out and
  put it back (two clicks on its place in the inventory) to run the game's can-use check: "CANNOT
  USE THIS ITEM" when refused. A class can be tried for a picture too: the sheet's class byte
  (`SHEET_CLASSES`, 13 a ranger) and its flags (0200h a ranger, 0040h a gladiator). **party.py's
  classes don't tell a human**: a human who dual-classed lists two; read the race (sheet +18h, 1
  human) before making a priest with turnsetup.py (a human's added class is level 0).
- **A creature's name** for a test: its record's +28h (16 bytes); the Loader's lists that go by
  name (`cahulaks.big_table`) follow within a pass.
- **An item type's record**: `gd.item_type_record(item)` through live.py reads an item's 20-byte
  type record; its fields (material codes, damage dice) are in [the item types'
  table](../obsidian-edition/DEVELOPMENT-INTERNALS.md#whats-known-of-the-save-and-records).
- **A creature's level / hit dice** (logs/2026-11-08-touch-level-and-hd.md): every creature has a
  47h-byte sheet (`gd.sheet(creature)`; race +18h, classes +21h, levels +24h). The game's level of a
  combatant (508h:2Ah, 5E85Fh) is +24h for a human, else the best level of a class that is set, so a
  monster with no class (elementals, slaads, Sand Howler, Rampager...) counts as 0 though its hit
  dice are at +24h. The game's own monster sheets are the RDFF chunks of SEGOBJEX.GFF (record type 4,
  `dataitems.records`). The undead (race 9) all have a class. With "Spells and psionics as the
  manual describes them" a classless creature's saves count its hit dice as its level (DSCLOG's
  HD_SAVE_SITE in the save modifiers only; checked in logs/2026-11-08-hd-spells.md).
- **A creature's scores (+22h) are worked out only when something asks** (a spell's handler that
  changes them, an effect's end): an effect put on in memory shows in them after the next Strength
  cast on that creature, for one.
- **A Shinobi for a test**: `scrolltest.py shinobi` makes member 0 an 8th-level thief with the
  Shinobi kit in memory (class 17 at sheet +21h, level +24h, kit byte +43h = 3, flags 0400h).
  `give` adds the defilers' scrolls (`defilerscrolls.scroll`). live.py's `gd` has no rules set, so
  `gd.kit_ids` reads []: use `kitpages.kits_of(gd.sheet(m))`.
- **A Spellarcher for a test**: a sheet made a half-elf (+18h 4) fighter/preserver (+21h 9, 11)
  with kit byte +43h 1, **and the class mask (+12h) with the fighter's bit (20h)** (the game tests
  it before DSCLOG's kit checks: a preserver's alone, 80h, bars the arrows), and `spellsetup.py M=5
  10 1 3 39`; the arrow buttons: [spell
  arrows](PLAYTESTING.md#casting-spells-for-a-test). `trap-user`'s Lex is a Spellarcher (Shocking
  Grasp; logs/2026-11-14-quiver-turn.md part 5).
- **A thief in memory**: `thief.py N LEVEL` / `thief.py N off`.
- **A kit's rules on a member in memory** (logs/2026-11-15-kit-rebalance-checks.md part 8):
  `kitset.py MEMBER CLASS LEVEL KIT` (a Crusader 7: `1 1 7 3`; a Mind Warrior: `1 12 7 2`) also sets
  the sheet's +2Ah, the attacks a round the game reads (set at creation and level-up: a warrior's 3
  left there keeps 3/2 whatever the class). Before the fight, or at least before the member's next
  attack. `fountain-user`'s Jenna (long sword spec, two long swords) is a good subject: count the
  main hand's lines ("with Bone Long Sword") each round.
- **A kit's limits on items**: a weapon kind the character specialized in is never barred by its
  kit (a Grove Warden with a long sword spec keeps its long sword): clear the specs (sheet
  +14h-+17h) in memory to see the limit. Take the item off and put it back on in the inventory: a
  barred one gives "CANNOT USE THIS ITEM". A heavy armour for a test: a worn chest item's type set
  to 12 in memory.
- **An XP award by hand**: the dice log's tracker sees an award only as each sheet's XP going up, so
  `award.py N` (each member's sheet XP += N / its classes, a human's N; the sheet from
  `aging.sheet_address`) stands in for a kill's to check what follows an award (the prime
  requisite bonus). Then restart the dice log to run changed Loader code ([builds, the Loader and
  the tests](PLAYTESTING.md#builds-the-loader-and-the-tests)).
- **People's gear** (logs/2026-11-06-npcs-equip.md): the game makes a person's items in its
  backpack list (+0Ch) and puts them on itself at that person's first action in a fight (weapons
  held, armour worn: Legcrusher's Leather Inixhide +1 and both clubs, an Arena Guard's leather,
  arrows, long sword and bow, and his AC from behind 8, not 10). Before that, out of a fight or
  killed first (Kurzak by a backstab: target AC 10), all of it was in the pack, and the game's
  Look box, which lists held weapons, showed none. **`people.py` puts it on as each person comes on
  the map** (since 2026-11-06): `npcgear.py` lists every creature on the map with its worn, held
  and backpack items. Moved into the held list (`pickpocket.place(gd, creature, item, 3)`) a weapon
  is fought with by anyone (a Tohr-kreen with Headsman: "attacks Cermak with Headsman +2
  (1d10+2)"); armour in the worn list counts for anyone's AC. A creature that dies carrying
  something leaves a Dead Body (object 1101) with its things.
- **A person's new gear and old saves**: the Loader's changes to a person's items (its object's
  record in SEGOBJEX, as worldgear's) reach only creatures the game makes after them: in
  `fountain-user` Legcrusher still held his two Wooden Clubs (`npcgear.py`), not the Cahulaks +1,
  since the save holds him as he was made. Test such a change in a new game, or an area not yet
  visited. Type 146 (the metal cahulaks) read from the game's type table as built
  (`gd.item_type_record`). The arena's people likewise: [made at its first
  visit](ROUTE.md#the-arena-region-2ah).
- **The game makes a region's map objects near the party**: on arriving in the pens the weapon rack
  (object 2599, square 48,34) and many others were not among the map objects (`gd.things_of(obj)`,
  DS:66AEh), and so their items were not in memory either; walking south made more (1221, 1224,
  1230...). Once made they stayed after the party walked off. To find an object's items, look it
  up by its object number when it is made, not by item type: type 6Ch is the weapon rack's and a
  coffin's (1574, at 75,43, holding a gem).
- **The game's free things**: `thingsfree.py LABEL` gives one line: the free list's length (of the
  200, things 320-519), the count out (DS:4C48h), and the item lists the people on the map hold.
  The pens: 143 free after loading, 131 in the alarm fight; the arena on arrival 191 (the pens' all
  freed). `arenatrip.sh` loads `pens-after-scar` (through `toalarm.sh`), rests in the fire room
  till Kurzak calls, and takes the party to the arena, counting the things on the way.
- **Combatants past 64** (logs/2026-11-09-audit-fixes.md): out of a fight the map's things keep
  their numbers (`pens-after-scar`: Kalzith 220, guards 256-290, Mirlon 317; every combatant of
  `fountain-user` is under 64), but **a fight renumbers them**: at its Round 1 the things past the
  party moved to 21-47 (Kalzith 42). So a combatant past 64 in a fight is rare; the unit tests
  cover them. A Turn Undead out of a fight starts one ([its line once named the target
  "?"](HISTORY.md#turn-undeads-unnamed-target)). DSCLOG's per-fight tables are in the far block:
  TU_FAILED at FFFF0h + FD10h (a byte a combatant, bit N priest N), SWEPT (FF18h) and DJ_DONE
  (FF59h), a bit a combatant.

### Items in memory

- **An item turned into another in memory** (a whole record but its link +4, flags +10h and slot
  +11h, so the price comes with it) shows in its box once the portrait is switched away and back.
  `setitem.py ITEM obj=N` takes object N's own item record (Tanelyv's chest piece: `obj=2004`),
  `rec=HEX` a whole record (one of the Loader's: `worldgear.SEARING_BLADE.hex()`)
  (logs/2026-11-18-item-glows.md: a whole record's type and price show at once in the box).
  **An item record copied from the objects file needs +08h set to 270Fh** (no contents; the file
  has 0, which in memory names item 0, and then the inventory drew no icons at all, whatever the
  build). `setitem.py ITEM TYPE` does it with the game's first plain record of a type.
- **Armour changed for a look at the figure** (logs/2026-11-26-class-outfits-loader.md): the item's
  type is the word at +0Ah of its record; written there (a party member's chest, leg and arm pieces
  made plate, 88/26/25, or chain, 57/59/58) the attached Loader dresses the figure again within a
  few seconds, on the map, with no inventory opened. `setitem.py` refuses those types ("no item
  record for 88 in SEGOBJEX.GFF": the game has no plain record of them). Save the records first
  and write them back whole after; memory only, never save.
- **A weapon for a test of its rate or traits** (logs/2026-11-23-ravager-weapons.md): put it in
  the right hand (`itemedit.py M 10 slot=3`): one in the left hand (slot 10) swings once a round
  whatever the rate. A second weapon moved to slot 20 is still worn and still swings: make it
  something else (`setitem.py N 60`). The Loader's types with no SEGOBJEX record (Wake of the
  Ravager's, 148-153) need `rec=` (`worldgear.weapon(worldgear.LOTULIS).hex()`); `specset.py M
  KIND...` gives the member the weapon specs. **A sheet's address moves with the build** (the
  origin worktree's DSCLOG put Jenna's at 669FBh, the branch's at 66A3Bh): read it from
  `sheetedit.py` at every load before writing to it.
- **A held item changed in memory** (logs/2026-11-10-outstanding-checks.md): write it with the
  inventory **closed** (closing it writes the screen's copy back over the record), clear its +0Ch
  (the game keeps there the icon it last drew, and draws that again), and give it the item's own
  type (+0Ah): the Loader sets +0, the object, from the type, so a type 127 always comes back as the
  Metal Pick (Deepbiter is type 112). To take a held item out in memory: `ring.unlink(gd,
  ring.Items(gd), ITEM, "why")` through live.py.
- **An item's icon in the game**: write a held item's +0 (minus the object: -2672 the Cahulaks +2's)
  and +0Ah (its type) through live.py (the items at the far pointer DS:165Dh, 15h bytes each; Lex's
  43 the right hand, 36 the missile slot in `fountain-user`), then I and the member's portrait: the
  slot draws the object's icon (the box's text stays the old item's).
- **A magic item for a look at its box** (for the docs): an item's +0 (object), +0Ah (type), +12h
  (name), +14h (plus), +0Ch cleared, written with the inventory closed
  (logs/2026-11-10-memory-pass-3-and-new-cahulaks.md).
- **Checking a figure's glow**: `sprites.worn(gd, MEMBER)` (through live.py) gives what the Loader
  dresses it in, `'magic'` on a magic piece; then eight `import -window` grabs 0.2 s apart, cropped
  round the piece and montaged: a glint is a few pixels changing between grabs (the pointer's
  animation changes pixels too: move it off with `click.py 280 180 none` first). **An outfit
  changed in memory on the map shows only once the game draws the figure again**: the Loader
  writes the store in place when the slot's picture isn't in memory (flags 1: stored; 3: stored and
  in memory), and the game reads it back at its next draw (a walk). Compare the slot's memory (its
  far pointer) with the Loader's copy (`dos/SEGOBJEX.GFF`) before calling a figure undressed.
- **A weapon's rule in a fight** (logs/2026-11-09-cahulaks.md): from `fountain-user`, a weapon put
  on a member in memory (a whole record from SEGOBJEX: `champions.game_item(chunks, TYPE)`, its
  link +4, flags and slot kept, +08h 270Fh: `setitem.py`) before the speech box is clicked; Tab +
  Return on the member's turn (`passuntil.sh N`).
- **A shot with a weapon put in memory** (logs/2026-11-10-stinkpots.md): a missile-slot weapon
  replaced by another type (`setitem.py ITEM TYPE`: Lex's bow, item 36, made the Leather Staff
  Sling, type 0; in `fountain-user`, before the speech) shoots on the member's turn with `pointer.py attack` and a click on the foe's
  figure, about 10 pixels above its feet (DS:669Dh + 32 x combatant, less the camera); beside the
  figure the pointer shows the red "can't" sign and nothing happens.
- **A named weapon for a shot**: write an item's name entry (+12h) in memory: the dice log, DSCLOG,
  the item box and the inventory's weapon line all follow it (the Spellarcher's Fine Bow, 173h: "+1
  fine" in the THAC0 line, "Hit +1" in its box). In `fountain-user` Ester's bow is item 10 and Lex's
  item 36, both name 2. Write the old entry back.
- **Arrows in memory** (logs/2026-11-14-quiver-turn.md): a stack's count at its item +
  `weaponchoice.ITEM_COUNT` (`setarrows.py MEMBER N`), **set before the fight starts** (before the
  ambush's speech is clicked): changed in a fight the game's own readied list doesn't see it.
  `ammodump.py` prints the archers' item records.
- **A reach test goes by the click, never Tab** (logs/2026-11-24-ravager-weapons-followups.md): a
  foe moved in memory (`placefoe.py THING DX DY MEMBER`, DS:669Dh + 20h a thing) stays drawn where it
  was until it moves, so a click on its new square finds nothing; Tab chooses it, but **Tab + Return
  swings a melee weapon from two squares in a build without reach too** (the control, 2026-11-24): it
  doesn't ask the distance routine the click does. Walk the member two squares from a held foe
  drawn where it stands (`squarewalk.py COL ROW`), make its Move 0 (37BD:022Bh + creature x 2) and
  click the foe's figure with the attack pointer: with reach the melee weapon swings; without, a
  bow in the missile slot shoots (or nothing happens).
- **Melee reach isn't the type's range byte** (logs/2026-11-10-polearm-reach.md): a polearm with its
  type's +0Ah set to 2, held alone, with Move 0, two squares from a held foe: the attack does nothing
  and the turn passes; with a bow in the missile slot the click shoots it instead.
- **A weapon spec's grand master for a test** (logs/2026-11-10-grand-mastery-large.md): write the
  member's sheet (the far pointer DS:1661h + (creature +4) x 47h) classes (9,0,0), levels (9,0,0)
  and +14h-+17h `01 00 00 00` (the long sword, unpacked; a sheet's +16h top bit marks them packed),
  then `specialize.skill(sheet, ITEM_TYPE)` reads 5 (GRAND). `foeset.py C race=5` makes a kind large
  (a sheet is shared, so one combatant of each). With every foe held, Tab chooses the nearest foe
  even when the member can't reach it: the END menu then opens with Move 0 (E ends the turn).
- **A mod weapon put on a member for a test** (logs/2026-11-26-sl-saves-scout.md): `setitem.py` has no
  record for a mod type ("no item record for 152"); write the whole record instead, `setitem.py ITEM
  rec=$(python3 -c "from dsloader import worldgear; print(worldgear.weapon(worldgear.JAVELIN).hex())")`.
  A changed type word alone leaves it unused. The javelin was thrown only with the attack pointer on a
  foe right beside the member; darts made so gave "NO PATH FROM HERE" on every try.
- **A kit's open-sky rule in an indoor area** (the same log): the dice log writes KIT_OUTDOORS (DSCLOG's
  header +350) once a second from `stealth.daylight` and `stealth.OUTDOORS`; the slave pens (region
  29h) are indoors. For a Military Scout's or Arcane Archer's test run the dice log through a small
  wrapper that adds 29h to `stealth.OUTDOORS` before `dsloader dicelog` starts (the initiative line then
  shows "+2 Military Scout under the open sky"); start.sh doesn't kill a `python3 -u -c` dice log, so
  stop it by its pid.

### Fights and foes in memory

- **Where the turn's movement is** (logs/2026-11-09-boots-of-speed.md): a word a creature at
  segment DS - (4356h - 37BDh), +22Bh + creature x 2 (Move x 10, set as its turn starts: 57566h,
  DSCLOG's PROBE_MOVE). **The turn's flags** are a word a creature at +1D5h there (3FFh as the
  round starts; bit 0: can still walk, cleared with the last step, 59106h), and a walk's next
  step a byte a thing at 3972:0377h + thing x 1Ch (FFh: none). DS:4964h-4968h keep the points and
  the place the turn began with, for F10 (logs/2026-11-18-squares-in-reach.md).
- **DSUN.EXE's overlays** (the same log): the root ends at file 52EA0h (`FBOV`); each overlay has
  a stub segment in the root (41A6h and up: `CD 3F`, the overlay's place and size, then 5 bytes
  an entry: `CD 3F`, the routine's offset), so a far call to 41BE:0093h is the combat overlay's
  (56CC0h-5A031h) routine at 59106h. A routine no far call names is reached this way.
- **The melee attack routine** (58019h in DSUN.EXE's file; logs/2026-11-19-backstab-str-line.md):
  one call plays all of a member's round (the loop from 58113h, [BP-22h] the attack's number).
  [BP-1Ah] (from behind) and [BP-24h] (backstab) are cleared once at its start; [BP-20h] is the
  creature's THAC0 (+1Fh) again on each pass, 2 off for from behind and 2 more for a backstab only
  when this pass is from behind (582D0h: the target's facing byte, +5Bh + creature at the segment
  below, against the attacker's direction to it, DS:494Ch). DSCLOG's REAR_FRESH clears a flag a
  pass didn't pay for.
- **An archer's turn bytes** (logs/2026-11-14-quiver-turn.md; `turnwatch.py`): at segment
  DS - (4356h - 37BDh), a byte a combatant: **+181h** the attacks made this round (63h: spent, the turn ends;
  set back to 0 as it does), **+1ABh** the attack commands.
- **`foeset.py`** (logs/2026-11-09-group-3.md, `fountain-user`) lists every combatant (creature,
  HP, sheet, race, classes, levels, magic resistance, the creature record's six scores) and the
  table of active effects (owner, caster, spell, effect, handle, charges, amount); `foeset.py C
  race= cls=a,b,c lv=a,b,c mr= hp= int= eff=ID[:SPELL[:AMOUNT]]` writes them (the sheet is shared
  by a kind; effects go in owner order, handles from 200, no timer). Used for Fire Shield (20), Blur
  (55), Biofeedback (4), Feeblemind (19), Diseased (13) and Paralyzed (34) on a creature
  (`addeffect.py`, below, adds effects too).
- **A foe's save numbers** are its sheet's +37h-+3Bh (PPD, RSW, PP, BW, SP), shared by its kind.
- **Level and class tests on a foe** (logs/2026-11-08-hd-spells.md): write the target's sheet in
  memory (race +18h, classes +21h..23h, levels +24h..26h; race 9 makes it undead for Hold Undead).
  Creatures of one kind share a sheet (the ambush's three Guards, 8, 9 and 31, all sheet 15). The
  fight's Templar was creature 30 (the dice log's saves showed its WIS 17), not 11: check which
  creature a combatant is before writing its scores. The ambush's foes read map position -1,-1 at
  DS:669Dh + 32 x thing in that test: find them on a shot, not from that table (in the Turn Undead
  tests they read right; most Arena Guards read far off the map).
- **A rule by size in a fight** (logs/2026-11-10-creature-size.md): from `fountain-user`, every foe
  Paralyzed (`foeset.py C eff=34`) and its sheet made a half-giant (`foeset.py C race=5`: large by
  race; the Guards there, Legcrusher's kind, are half-giants already), then Tab + Return on party
  turns: the dice log's damage line says "(1d12 for 1d8: a large target)". The rule has no off
  side since 2026-11-19 (a `setmem.py ruleshi=-N` changes nothing: [the
  guide](PLAYTESTING.md#builds-the-loader-and-the-tests)); for the game's way, an older build.
- **Held targets in memory**: the game's damage routine (79BF9h) takes the attack's damage x2 for
  a Paralyzed or Out Cold target; DSCLOG's HELD_DAMAGE hands it the damage as it is, always (no
  setting or memory edit turns it off since 2026-11-19; for the game's way, an older build; the
  guide's [foes in a test fight](PLAYTESTING.md#foes-in-a-test-fight)). To see a held target hit on any
  roll, write its sheet's base AC (+27h) -10 in memory: "only a 20 hits ... -> HIT".
- **Seneca's poisoned weapons**: since 2.18 each weapon's first hit a fight is marked in the
  header's +1860, which `symread.py`-style reads show as 88h once both her hands have poisoned.
- **Testing Psionic Blast without a blaster**: find DSCLOG's header in memory (its signature,
  `dicelog.HDR_SIG`, 16-aligned; 0xC91B0 in that run), write a member's kept hit points at +1814 (a
  word per combatant 0-3) and the member's HP (creature record +0) to -9, so any blow would kill by
  the game's rule (damage at HP + 10); pass turns until it's hit: it goes to 0 HP, not dead, and the
  fight's end gives the hit points back ("shakes off Psionic Blast's imagined wounds"). CON 20+
  regeneration can wake it first (Gerakis did).
- **Monster powers on demand** (logs/2026-11-09-group-4.md): `kinds.py CREATURE=KIND` writes a
  creature record's kind (+16h); a kind's properties and resistance class then apply to it (15/13
  the shadows' STR drain, 3 the babau's deadly poison, 38 the Styr's breath, 39 the Djinn's
  first-turn invisibility and images, 40 the Tari's disease). **The hit powers come with melee hits
  only** (7A6BAh): the ambush's Arena Guards (bows) never brought one; the Guards (two clubs) did,
  and only from the first attack set (the off hand's hits brought none). A kind set on a creature
  not in the fight does nothing: set every guard of the kind. **The priests' Poison a hit casts
  (bit 15) kills at once on a failed save**, in a fight too ("Jenna takes 263 from Poison, now
  0/300 HP", status 5): put the member back in memory (`addeffect.py del N 35`, `setmem.py
  status=N:1 hp=N:300`).
- **A Weakened's amount is added to STR** (the ability routine, 7B80Eh): -1 takes a point off, 1 adds
  one (a first drain raised STR, seen); Chill Touch's is -1 (79855h). Each Weakened is its own entry.
- **Giving an effect in memory** (logs/2026-11-09-rest-poison.md): `addeffect.py OWNER EFFECT
  [SPELL]` inserts a record in the effect table in owner order (35 Poisoned, 13 Diseased);
  `addeffect.py del OWNER EFFECT` takes it out. A rest at the fire ring then shows what the rest does
  with it (a Poisoned member dies: status 5, creature +1Ch). `restfixmem.py check|fix|undo` swaps the
  rest's pass 2 in the overlay buffer for the proposed "cures first" order (rest once first, so the
  overlay is loaded). Death does not take effects off a member.
- **`effects.py`** lists the effects with time left (Stuck (11 rounds), Ironskin (6 charges));
  `effects.py OWNER 51 34 86` rewrites a Stuck into Paralyzed (47 Slowed) to test a cure.
- **Where a pin comes from in the code** (logs/2026-11-20-f10-real-pin.md): every effect put on
  goes through the far routine at DSUN.EXE 78480h (the effects' overlay; the immunities first, by
  a table of ids at 647h in its segment), and for 34 (Paralyzed) or 51 (Stuck) it runs
  786A9h-786CBh, which clears bit 0 of the creature's turn flags (37BDh:01D5h): whatever gives the
  effect, on whoever's turn. 598:20 is "has effect" and 598:4D "take it off" (59D20h, the fight's
  end, takes Paralyzed off the party that way). The only other `and ...,0FFFEh` on the flags,
  591BCh, is the walk's (under 10 points left). In play: a Web pins on the step into it, on the
  walker's turn; Hold Person turned back by Spell Turning pins the caster on its own turn; Rainbow
  Pattern's save comes at each creature's turn start, and a Paralyzed member's turn is skipped.

### Spells and powers in memory

- **A spell taught in memory** (the known byte at segment DS-B56h, 168h + member x 8Ah + spell)
  shows and casts as any other; `spellsetup.py` writes it. A new wizard spell is known by a bit of
  the sheet's +45h (`game.NEW_KNOWN`: Erdlu Claw 20h), which a scratch write can set for a shot
  (the sheet from SHEETS_PTR and the creature's +4 index).
- **The game's rule for the LEVEL button's pages** (88A94h -> 81664h): a level is offered when a
  spell of it is known, the classes give a slot there on resting (not slots left: a 0/1 page is
  offered) and it is at most (caster level + 1) / 2 (81B16h for spell 0 or 69); a **human's casting
  class in place 2 or 3 counts 0 unless below the first class's level** (5E7CFh, and no slots,
  5E130h: the MAGE page went away entirely). spellsetup.py prints the pages and warns of that.
- **A spell outside the caster's spheres is cast at level 0** (logs/2026-11-08-touch-level-and-hd.md):
  spellsetup.py teaches any spell, and the USE screen lets it be cast, but the level its time and
  damage take (5E25Ch) counts only classes sharing a sphere with it, so a fire cleric's Blood Flow or
  Ironskin got "caster level 0" (taken as 1). Touch or aimed makes no difference (Free Action on a
  portrait: 600 s at druid 1, 5400 s at druid 9). Set a class of that sphere in memory.
- **Several casts a slot**: the count is the spell record's byte +0, bits 2-7 (Magical Stone 3, Hold
  Person 4, Hold Undead 2, the rest 1), counted at DS:942Ch by the cast's end (DSUN 7566Eh).
- **Spells rolling to hit, on demand** (logs/2026-11-08-spell-to-hit.md): raise the target's sheet
  base AC (+27h) in memory (30 for a sure hit); a weapon's spell on a hit can be tried by writing a
  held weapon's item +0Fh (the spell + 1). Put both back.
- **Turn Undead in memory** (logs/2026-11-08-turn-undead.md): the button shows for any sheet with a
  cleric element in +12h bits 0-3 (1/2/4/8): to make a member a cleric in memory, set a class byte
  (+21h..) to 1-4, its level (+24h..), and OR +12h with the element (a druid, 5-8, has 0 there: no
  button). A target is undead by the sheet's race (+18h = 9), its HD the sheet's +24h; creatures of
  a kind share a sheet. The ambush's foes' places read right in that test (`DS:669Dh + 32 x
  combatant`, map units): screen = map - camera.
- **Turn Undead the AD&D way** (logs/2026-11-09-turn-undead-meteors.md; "Spells as the manual
  describes them"): `turnsetup.py MEMBER LEVEL [COMBATANT=HD ...]` makes a member a fire cleric of
  LEVEL in its **second** class place (+22h; a preserver whose class is there, Lex in
  `fountain-user`, loses it: give him a cleric third class by hand, +23h 3, +26h the level) and each
  combatant's sheet undead of HD hit dice (every creature of that sheet), and lists the combatants
  with sheet, race, HD and HP. Each outcome by the table: level 4 vs 1 HD is T, 6 D, 8 D\*, 3 a 4
  needed, 1 vs 5 HD a 20. The Templar beside a Guard was tried too. A human with a cleric class
  added in memory is priest level 0 to the game (Jenna). The party's places (DS:669Dh + 32n) were
  right.
- **Psionic powers in memory**: a member knows power P (0-33, numbered from 138) when its byte at
  the segment of selector 2F0h (`game.SEGMENT_TABLE` + `POWER_OWN_SELECTOR`), +77h + member x 22h
  + P, has bits 3-7 set (write 8). `powers.py` lists each member's. The four members of
  `fountain-user` already know Life Draining, Biofeedback, Flesh Armor, Graft Weapon and Mind
  Blank. `setmem.py power=1:13` makes one known (K'ratchek's Cell Adjustment).

### Creation and levels

- **The creation screen in memory** (logs/2026-11-08-creation-least.md): a score's least is at
  DS:4994h (just worked out for that score by 67399h), its most at DS:4992h; `creationscores.py`
  reads them. **The pointers stay set afterwards**: DS:119Ch then points at the party's first sheet
  and DS:11A0h at the creature table, in play too (null only in a game loaded first); on the
  screen the record is straight after the sheet (`gd.creating()`). While the screen is up the
  party's first slot carries the character's name on a stand-in sheet (XP 4,000, scores 10) whose
  XP moves with the class; the Loader gives it no gear (only the character DONE makes).
- **Race, classes and kit on the creation sheet**: a race and classes can be set in memory for a
  check (the creation sheet at the far pointer DS:119Ch: race +18h, classes +21h). The class
  list's numbers there (+21h) are the list's (1 cleric ... 7 ranger, 8 thief), not the game's; DONE
  turns them into the game's (a fire ranger 15). The kit is the sheet's +43h (1-3).
- **The creation screen's figure** (logs/2026-11-27-creation-figure-outfits.md): drawn from a blob
  the game makes at start-up of each figure's walking frame 0 (from the Loader's copy of
  SEGOBJEX, object 300 + figure), in the paged-memory handle at DS:4C2Fh (4B000h bytes, XMS pages
  30h-42h in DOSBox: guest 1D0000h on), entry n from the dword table DS:543Dh[n] to [n+1], the
  figures 20h + figure, [2Eh] the end. Each entry is a one-frame picture chunk (length, 1, 10).
  4414h:9Dh reads the entry at each drawing (stub 4239h:2Ah draws it at 91h,16h: on opening at
  65FACh, and after a race or portrait click, its box first put back by 1A0Ah:30C3h with DS:E8Ah,
  E8Ch), so writing an entry shows at the next drawing; a class click doesn't draw it. A new
  character gets its class after the first drawing, at the hit points' drawing (63EDAh). Read
  the blob with `creationfigure.Figures(gd)` (its `table()`, `read`). Changing a human's class:
  click the class off first.
- **Psionic powers' place**: `powers.py` reads selector 2F0h's segment, +77h + member x 22h +
  power, bits 3-7 ([psionic powers in memory](#spells-and-powers-in-memory)).
- **A level-up for a test** (logs/2026-11-15-kit-rebalance-checks.md part 10): write the sheet's
  XP (+0, a dword) just short of the next level (`tables.xp_needed(row, level)`: a preserver's 5th
  20,000), then a kill in a fight: the level comes during the next turns, and `fightout.sh` answers
  CHOOSE A SPELL with `levelup.sh` (count its "picked a spell" lines). A loop of `levelup.sh` until it
  fails counts the picks of one screen.
- **Level-ups by XP written in memory** (logs/2026-11-26-sl-saves-scout.md): the dice log's tracker
  takes the edit for an award and adds the prime requisites' 10%, and the Loader holds a multiclass's
  XP at the cap's share (749,999 over the classes, a class) at once: write a few XP short of the level.
  The saves after a level up are the sheet's +37h (PPD, RSW, PP, BW, SP); with RULE_HI_TABLES off
  (`setmem.py ruleshi=-8`) they are the game's own (its table 420h:6Ch), the control. A psionicist's
  level brings PICK A PSIONIC POWER: a red power's icon (158,62 or 177,62), FINISHED (112,139) turns
  the discipline page. In the sequel (`ravlevel.py set`, `foes 1`, Computer Control, the boxes at
  160,100) a psionicist's level up brought no pop-up, and `RAV_SKIP=save_table` is the saves' control.
- **DUAL in memory**: the DUAL window greys a class by the creature record's scores (+22h), not the
  sheet's: raise one with `foeset.py C int=18`. `sheetscore.py M lv=N con=N ...` sets the first
  level and the creature's scores (what the window reads). A member with a kit is asked for none
  (clear the sheet's +43h to see the kit menu: its title "KIT: NONE", the class's kits as rows, a
  barred one left out). The rule has no off side since 2026-11-19 (`setmem.py ruleshi=-N` changes
  nothing); for the game's DUAL, an older build.

## Sounds

- **Hearing the game**: start.sh sends DOSBox's sound to a file when `PT_AUDIO` names one (`export
  PT_AUDIO=$WORK/audio.raw` before start.sh or loadsave.sh; else /dev/null): raw 16-bit stereo at
  44100 Hz, about 176 KB a second, real time. Note the file's size before and after an action, then
  `python3.13 soundmatch.py $PT_AUDIO A B clip.wav...` gives the loudest sample and how well each
  clip matches (r about 1.0 for the one played; 0.04 for another). `playsound.py N` has DSCLOG play
  sound N (its SOUND_REQ). The game plays nothing much on its own while the party stands about: a
  recording of minutes was silence but for a second at the start. The game's own 53 and 96 recorded
  at peaks near 2,800.
- **Comparing loudness** (logs/2026-11-09-sounds-louder.md): `playsound.py N` for each sound with 3 s
  between, the raw file's size noted round each, then the peak and the loudest 400 ms RMS of each
  stretch (numpy over the memmap): the game's fight sounds peak about 2,960, RMS -27 to -31 dBFS. A
  sound's descriptor +6 is its priority: the game skips one lower than the sound playing. **The
  descriptor's +0Ah (6Eh) is not a volume** (logs/2026-11-10-sounds-denser.md): set from 20 to 127
  the output peaked at 2,957 each time. DOSBox plays every clip at the same peak, so a quiet clip can
  only be made denser (make.py's soft-limiter drive): hide now -27.5, pick -30.5 dBFS.
- **The game's table of sounds**: at load segment + 3A98h, offset 08A2h, 6 bytes each: +1 the kind
  (5 a digital clip), +2 a far pointer to a 12-byte descriptor (+7 its BVOC). 0-130 are digital,
  131-180 another kind (4), past 180 other data: a BVOC numbered past 130 isn't played by its number
  (the mod's 140 and 141 were silent until DSCLOG lent itself entries 131 and 132 for the call), and
  the game keeps the last clip loaded under a number (one lent entry for both sounds played the
  first again).

## See-through figures

- **`ghostchk.py`** shows DSCLOG's block (GHOST_SEG), GHOST_ON and the tables; `ghostchk.py 0` marks
  thing 0 (the leader) see-through and has the view drawn again, for a look without a fight or a
  spell; `ghostchk.py 0 1` marks things 0 and 1 (each call replaces the marks). Outside a fight the
  party is one figure, the leader's; walking, it spreads into four. The live table of vectors
  (segment 0, 4 bytes each) shows which handler has each; **the install's bytes turning up twice in
  the image means two probes on one vector**, not chance ([target AC
  255](HISTORY.md#two-probes-on-one-vector-target-ac-255)).
- **A big frame see-through** (logs/2026-11-06-see-through-after-fix.md): `bigthings.py` lists the
  map's things with their pictures' most runs (near the pens' gate none past 164); `setpic.py THING
  PICTURE` draws a thing with another picture in memory (picture 459, a tuft of grass of 563 runs;
  put the old number back after), and `pastblock.py save|cmp FILE` keeps and compares the 4 KB past
  GHOST's block. Past 192 runs only the frame's top is drawn see-through, by design.
- **In a fight** (logs/2026-11-05-fight-test.md): seen from a real hide and a real Invisibility. The
  pale bits behind a walking figure are the mod's dust (dust.py), not a smear: solid figures leave
  them too, and a full redraw clears them; an END menu left up keeps them on screen.
- **A hidden walk to Move 0, and the turn's end** (logs/2026-11-06-solid-frames-turn-end.md):
  `walkprobe.py N X Y DIR [SECS]` clicks, then keeps a window grab with N's position, whose turn and
  DSCLOG's STEALTH word (header +204) as often as it can (about 50 a second). **Since GHOST_UNION**
  (logs/2026-11-06-solid-at-turn-end.md) the figure is solid about 0.1 s after the hiding ends, in
  the next enemy's turn, if that enemy steps or swings; one that does nothing redraws nothing, and
  the old wait applies: the figure keeps its see-through picture through the enemies' turns and is
  drawn solid when a party member's turn begins ([the old wait](HISTORY.md#see-through-figures-at-a-turns-end)).
- **`ghostclear.py [TRIALS]`**: at each enemy turn's start, Cermak marked see-through with
  GH_CHANGED set, the byte and the turn read every 20 ms: whether GHOST_UNION cleared it within that
  turn. `markmember.py THING|none CHANGED` writes GHOST_TAB and its changed byte (GH_CHANGED) by
  hand.
- **Pointer trails**: sweeping the pointer with `xdotool mousemove_relative` (DOSBox takes only
  relative moves) while asking for view redraws (DSCLOG header +242 = 1, 30 a second) showed no
  trails, before or after the fix (interrupts off again while DSCLOG draws: DRAW_MASKED).

## Pictures, the picture store and memory

- **Memory**: `memaudit.py` lists every DOS block (the game's, DSCLOG's, the overlay buffer, the
  see-through tables, the music buffer, free) and the heap; `memsample.py LABEL` gives one line (free
  DOS memory after the game, more while the inventory or USE screen is open); `dacwatch.py SECONDS`
  shows DSCLOG's palette copy changing (every 30 s where the game cycles colours); `ghostwatch.py
  SECONDS` counts samples with GHOST_ON 0. The current figures are in [where DOSBox's memory
  is](../obsidian-edition/DEVELOPMENT-INTERNALS.md#where-dosboxs-memory-is); the history is in
  logs/2026-11-08-memory-pass.md and logs/2026-11-09-memory-pass-2.md. Comparing builds: [builds,
  the Loader and the tests](PLAYTESTING.md#builds-the-loader-and-the-tests).
- **The picture store** (logs/2026-11-09-missing-figures.md): the game's store (741,376 bytes,
  fixed, DSUN.EXE 60D9Bh) and its table of 300 picture slots (load segment + 3E60h; DS:1F84h the
  slots taken) are given back only at an area load. The pens load 203 of the 300 slots on arrival
  and walking about adds none (`slotcount.py` at each stop; logs/2026-11-09-picture-slots-explore.md);
  fights add a few (bodies, dropped items, spells). Wake of the Ravager's "graphics disappear" note
  is this same limit; leaving the region clears it. The Loader leaves a figure undressed when the
  store has no room (`_room_for`), and puts a re-dressed picture into a slot the game already has
  (`sprites.Dresser._in_store`, logs/2026-11-09-picture-store-fix.md), so `cachelist.py`'s slot count
  no longer climbs one a gear change: a toggle reuses the slot holding that outfit, the inventory
  open writes each picture's own slot, other outfits take a free STALE slot; a new slot only when
  the outfit is bigger than any free one (a few in the first dozens of changes, then none). DSCLOG's
  PIC_REUSE reuses free slots past 300. **Figures gone from the map** (the party, at times the foes,
  not drawn though their places are right; clicks on them miss) mean the store ran out: check
  `cachelist.py` (slots taken) and `cachelist.py all` (the last slot's place + length against
  741,376), and reload the save or change area to start afresh; I then Escape draws them again for a
  while. How it was found and what it did before the fix: [the picture
  store](HISTORY.md#figures-gone-from-the-map-the-picture-store).
- **Watching figures and pictures**: `figwatch.py SECONDS [EVERY] [TAG]` (passive, no writes: each
  member's screen place, its map record's +0 (80h: not drawn), its picture slot (+0Fh) with that
  slot's number and flags (2: in memory), the draw list's order and the member's place in it, and a
  strip of grabs round each figure); `drawlist.py [all]` (the draw list at DS:6690h, kept in rising
  y: the drawing finds its window DS:57CAh-57C8h by a scan that stops at the first y past the view,
  so an entry out of order would hide all after it; never seen out of order); `cachelist.py [all]`;
  `poolfree.py [SECONDS]` (the picture memory's free bytes, DS:8E94h); `figcheck.py LABEL` (a grab
  before and after DSCLOG's VIEW_REDRAW, header +242, and the pixels changed round each member: a
  figure missing then drawn shows hundreds). An inventory move in a test: `click.py` the item, then
  the place.
- **The store itself** (logs/2026-11-09-picture-store.md): an XMS block behind the game's paged
  memory manager (handle DS:4C33h, pages through the directory at DS:42D2h); in DOSBox it was guest
  RAM at 110000h, XMS pages 2-2Fh in one run. `picstore.py` finds it and checks every in-memory
  picture against its store bytes (`check`; all should match), lists the STALE cells (`stale`) or
  dumps a slot. The picture pool is 60,000 bytes; opening the inventory (I) puts every picture out
  of memory (`cachelist.py`: 0 in memory).
- **Changing outfits for a test**: `outfitcycle.py MEMBER SLOT N` changes an outfit N times
  (waiting for the Loader's copy to be written, not for the slots to grow) and prints slots, STALE,
  the store's end and whether the figure is drawn each time; `randout.py N [SEED]` puts random items
  of member 0 on and off. `fillcache.py MEMBER SLOT UNTIL` fills the slots fast by toggling a worn
  item's slot byte, the Loader dressing each time (memory edit, never save), but it waits for the
  count to grow, which the store's reuse stopped: it stalls (4 s a change) and is of no use now. A
  test that needs the store full needs a picture loaded anew some other way.
- **Lots of items on the ground** (logs/2026-11-09-picture-slot-reuse.md): `giveitems.py MEMBER N
  [FIRST]` gives items of different objects (each its own picture) into free backpack cells in
  memory (12 cells: then "no room"); `groundfill.sh CYCLES [FIRST]` gives Gerakis 12 and DROPs each
  (I, his portrait 20,20, a cell then DROP at 213,134; cells x 195/213, y 26-116), cycle after
  cycle, printing `slotcount.py` (slots, store end, in memory, STALE, and PIC_REUSE's reuse count
  `pf_count`, read through a symbol map). Dropped items pile on the party's square: walk off to see
  them. `slotcheck.py`: every map thing with a slot finds its own picture there, every wall's slot
  taken; six entries of the thing table naming slot 0 with nonsense pictures are the table's unused
  ones (the same on a fresh load). From `pens-thornwall-rack` 145 items took the table from 203 to
  300 in nine dozen (about 40 s a dozen).
- **The inventory and the picture cache**: opening it puts every picture out of memory, and its
  icons are loaded through the same cache and let go once drawn, so at 300 slots they are free for
  reuse. PIC_REUSE searches round from after the last slot it reused ([why](HISTORY.md#slot-reuse-and-the-inventorys-icons)).

## Frame rate and cycles (framerate.py)

`python3 framerate.py 20` walks the party back and forth (screen 40,104 to 280,104, a click every
3 s) for 20 s, out of a fight, and prints: the frames shown a second (DSCLOG's flip_count); those
steady pace left undrawn (pace_skipped); the steps run and lost (pace_ran, pace_lost: steady pace on
only); these found from a symbol map of the helper as built; the main loop's passes; the BIOS
clock and the game's clock (96 a second) against real time; the leader's map units a second
**while walking** (the waits at a target left out); and DOSBox's CPU. `PT_CYCLES=N sh start.sh` (or
before loadsave.sh) sets DOSBox's cycles; settings are changed with `launch.save_settings` before
loading (the log of 2026-11-08).
Its walk clicks are at y 104: from `fountain-user` after its fight they land in the fountain and
nobody walks (0 map units/s), so measure from another save.

**The rings' cost** (2026-11-16): `ringall.py [N | all | still | clear] [KIND]` puts a ring under
every thing on the screen (still: all but the party) straight in DSCLOG's table, for a framerate
run without the Loader's say; the Loader writes its own table only when it changes, so they stay
until Alt or a fight's Tab ring. DSCLOG goes round every marked thing's ring at each floor pass,
on the screen or not: 16 rings (4 under the walking party) took the walk from 155 to 122 map
units a second, 87 marked across the region with one in view from 134 to 120, and a ring's
thickness made no difference. Put the party back first (`walkto.py 1672 344`, `viewto.py 1672
344` from `pens-after-arena`): a run started from wherever the last one ended walks into a wall
or drags the view along, and its numbers aren't comparable (0 map units a second once).

How the game paces walking: its timer (DSUN.EXE seg 1DF3:29E8h) sets DS:1F7Eh at each tick of
the game's clock (DS:11D6h, 96 a second); the step (1DF3:26DCh) runs only with it set and clears
it. A tick passed while a frame draws is a step lost.

How to compare two builds fairly: run them **alternately in the same session** (before, after,
before, after) rather than against an older table: runs of one build agreed within 0.3 frames a
second, so a difference of 1 is real. A loaded game's first framerate.py run is as good as later
ones. `framerate.py` takes the symbols from `obsidian-edition/dos/dsclog.asm`; for another build's
EXE in `dos/`, set `DSCLOG_ASM` to that build's source, or it reads the wrong counters. The script
is logs/files/2026-11-08-drawing-savings-runs.sh (results in logs/2026-11-08-drawing-savings.md); put the
EXE back and `cmp` it afterwards.

The measurements (pens-after-arena, the whole party walking, 2026-11-08), the old steady pace's
and the faster drawing's: [HISTORY.md](HISTORY.md#frame-rate-measurements).

**Two engines' speeds** (2026-11-19, logs/2026-11-19-dosbox-x-engine.md): the same cycles do less
on DOSBox-X than on 0.74, and each core has its own pace, so a speed is found by walking, not by
the number. `framerate.py` reads its own game's pid (`live.py`'s: `dsun.pid`), so it measures a
DOSBox-X or a DOSBox under another name beside the shared one. A fresh start for every run, the
engines in turn in one session, `framerate.py 20` from `pens-after-arena`; match the steps run
and lost and the map units a second (within 2 between runs of one setting), then the frames.
0.74's 35,000 on its dynamic core is DOSBox-X's 42,000 on its dynamic core, 20,000 is 22,000, and
GOG's 7,000 (0.74's normal core) is about 8,000 on DOSBox-X's normal core; `dosboxx.SPEEDS` has
them. DOSBox-X's own speeds for a test: `cycles=N core=normal|dynamic` after the program on
`start_dosboxx.sh`.

## The picture and the music device (picstart.sh, picpattern.sh)

The Loader's **Picture** (plain, scanlines, tv, sharp: `launch.display_lines`) and **Music device**
(`midiout.py`) are DOSBox settings, so most of a check needs no game
(logs/2026-11-17-picture-music.md).

- **Without the game or the lock: `sh picpattern.sh win:3:scanlines win:4:sharp full:3:sharp`.** A
  DOSBox of its own shows a pattern in the game's screen mode (13h) with the Loader's display lines
  for a window (`win`) or full screen (`full`), a scale and a picture; it prints the settings, the
  window's size and any complaint of DOSBox's, and grabs the window (the whole screen for `full`)
  to `$WORK/picpattern/`. It runs on its own display (`:57`, 1920x1080, so the 1280x960 window and
  full screen fit, which `:55`'s 1024x768 can't show) and under another process name (a copy of
  the program called `dbpat`), so it never disturbs a play: `live.py` attaches to the newest process
  named dosbox, and `start.sh` kills every one. **A second DOSBox under its own name would be taken
  for the game by every tool of every agent.** Its window's class is the program's name (`xdotool
  search --class dbpat`).
- **In the game: `sh picstart.sh PICTURE [SCALE] [OUT_DIR]`**, under the lock. A start of its own
  (not the kit's 320x240): `pens-after-arena` loaded with `click.py` alone, which works at any
  scale because it moves the hand until the game's pointer reads the place; then the window's
  size, `picmove.py DX DY` (the hand moved, how far the pointer went), a grab (`import -window`)
  and DOSBox's log. It writes `window_scale` 1 and the plain picture back to settings.json as soon
  as the configuration is written, so a run cut short still leaves the kit's settings. About 75 s
  a picture.
- **The kit's own start never changes with the picture**: at `window_scale` 1 the Loader writes
  `scaler=none` whatever `picture` is stored (`tests/test_launch.py`).
- **What Linux's DOSBox 0.74-3 can and can't show.** It has no DirectDraw: GOG's `output=ddraw`
  is refused ("not a valid value... reset to surface") and the plain surface used. Windows open at
  their sizes with every picture, and OpenGL (`opengl`, `openglnb`) works under Xvfb. Full screen
  with the surface output is not stretched (the picture sits unscaled, and partly off the screen
  under Xvfb), so only Sharp's full screen can be judged here; Scanlines and TV in full screen, and
  how DirectDraw smooths a window's stretch, are for the owner's Windows.
- **Reading a grab for scanlines**: sum a column's pixels down the picture (`PIL`): at Triple a
  game row reads lit, lit, black, with the black line twice under three rows in five (the aspect
  correction's line table); TV reads full, about 5/8, about 1/3.
- **The music device can't be heard here**: the container has no ALSA sequencer ("ALSA:Can't open
  sequencer", then "MIDI:Opened device:none" in `dosbox.log`), and the Windows device list
  (`midiout.devices`, winmm) is None off Windows. The unit tests use a stand-in for winmm.

## Scripts and the game's code

- **What is under the pointer** (logs/2026-11-18-hit-chance-hover.md): **DS:0BCBh** is the thing
  the game last found under its pointer on the map (FFFFh: none), from the finder a click uses
  (25B52h: the front figure with a pixel there); the routine that keeps it (1E126h) lights the
  thing up, the one lit in DS:0BD1h, and puts that one back in DS:0BCBh for a pass after the
  pointer has moved on. DS:0BC9h is 1 with the map up and 2 with a menu (the END menu too), a
  window or a talk; DS:11B8h the pointer's mode (1 walk, 2 look, 4 attack; the game puts the walk
  arrow back as each member's turn begins). A map thing's picture box: left at +3, top at +5 less
  the signed byte +0Dh, width +12h, height +13h of its record (DS:6694h + 32 x thing).
- **A floating label taken off in a still scene comes back** a frame after DSCLOG erases it, until
  the view is drawn again (window grabs every 30 ms count its ink: `import -window`, the pixels
  near the label's colour). The Loader asks for the view again itself now (`Labels.took_off`); a
  test that writes a slot by hand must do the same (`shadows.redraw(gd, hdr)`).

- **The docs' code addresses (5883Ah and the like) are DSUN.EXE file offsets**, the patches'
  (`gamepatch.Patch`'s offset), not linear addresses in memory: most of the fight code is an
  overlay, so memory there reads zeros or other code. Disassemble the file (capstone, 16-bit, the
  offset as the address: near jumps and calls come out right within a routine); a near call's
  target is offset + 3 + rel16. Far calls in it carry relocations: leave their bytes where they are
  in a patch. A new hook needs no vector of its own: a site (`gamepatch._site`, DSCLOG's `site`
  table, in order) on VEC_CR_SPELLS; a site replacing a compare puts its flags into the INT's frame
  (`ammo_turn`). (logs/2026-11-14-quiver-turn.md)

- **The arena's flags and numbers can't be set from outside**: the pointers at DS:1352h and 1356h
  stay null in the arena even while a script waits on a message, so a poller never finds them. To
  test a script's branch there, build a copy of the scripts with the test forced (edit the module,
  run `start.sh`, which writes `dos/GPLDATA.GFF`, then put the module back) and say so in the log.
- **Setting the arena's visit count**: in the pens the game's numbers have a place in memory;
  number 12 is the count (4: the next trip is Scar's; 5 and up the everyday speech, or the
  champions' after Scar's death in the arena). Write it at the far pointer DS:1356h + 2 x 12:
  **`setcount.py [N]`** reads it and, with N, writes it.
- **Reading a value inside a script**: a test build whose repair PRINTs (4Fh, 98) a field prints
  nothing for a number; print a marker string under an IF per guess instead (TEST field == N, IF,
  PRINT " aN", ENDIF; the IF's address in `relocate`). Keep such a probe small: one of about 200
  tests (some 5 KB of detour) ran nothing at all, nor did 100 reading fields 72,n. Item fields seen:
  72 = the item's +00h (its kind, minus its object), 85 = its slot (+11h); no field 0-99, nor
  72,0-99, gave its type.
- **The game's command table** is words at DS:00C0h + 2 x command, the handlers in segment 5DFh
  (the dispatcher at linear 5FE9h, `call [bx+0C0h]`): dump memory with live.py (`gd.guest.read(0,
  0xA0000)`) and `ndisasm -b16 -o OFF`. 41h (5DF:1895h) stores its value, an object's number (or a
  kind, looked up), in 3923:361h (object 2Ch); 49h (5DF:140Ah), the item loop, copies each item into
  one scratch object (2Bh, 3923:35Fh).
- **The pens' master script and named routines**: `KIND='MAS ' dec.py 29 0 140` decodes the pens'
  master script; GPLI 1 is the index of named routines (id, offset, script: 2-byte words).
- **The triggers in memory** (which things have a talk, attack, look, use or use-with script: found
  2026-11-16, logs/2026-11-17-show-usable.md): one table of 13-byte records at the far pointer
  DS:42CCh (+0 the place in the script, +2 the script, +4 the object's id, the number negated as
  the scripts write it, +6 a use-with's other id, +0Bh the next record's index, FFFFh the last),
  the lists' heads words in segment 377Eh plus the load segment (+0Fh talk, +11h attack, +13h
  look, +15h use, +17h use with; +09h the tile and box triggers). DSUN.EXE 967Ah is the game's own
  "what can be done with this thing" (bits 4 talk, 2 attack, 8 look, 10h use, 20h use with). A
  thing's id: an item record's first word, a creature record's +6. `dsloader.usable.triggers(gd)`
  reads the lists; `usable.py` prints what the Loader would mark.
- **Finding a table in memory from the scripts' numbers**: search the game's memory
  (`g.read(0, 0x110000)`) for one record's words near each other (a trigger's place, script and
  object from the MAS script), print the neighbourhood in the record's size, then look for a far
  pointer to its start in the data segment and for the code that uses that pointer (capstone over
  DSUN.EXE: the image starts at file 5400h; the relocation table gives every use of a segment).
  **Never name a scratch script after a module of Python's** (`dis.py`, `types.py`: capstone and
  live.py then import the script instead, "partially initialized module").
- **The draw list's three sorts of entry** (`drawlist.py all`): things 0-519 that are creatures or
  items; things 0-519 of kind 0 (drawn, no record: the pens' banners and braziers); and numbers
  past 519 (the region's own scenery: 55135...). DSCLOG's rings and labels take the first two
  only. The list holds the whole region (415 entries in the pens), not the view.
- **The inventory's input** (for anyone trying a click there by hand): the game takes clicks from
  its queue of events, never INT 33h's position; what was tried is in [HISTORY.md](HISTORY.md#the-inventorys-input).

## The figure prototypes in the game (outfitgame.py)

- The figure prototypes' pictures (`prototypes/outfits.py`, `prototypes/wornlooks.py`) are not the Loader's: to see them in the game they are put
  into the Loader's copy of SEGOBJEX.GFF between the Loader writing it and DOSBox opening it, and
  the game is run with no Loader attached (it would dress the figures again):
  `PT_NO_LOADER=1 PT_AFTER_PREPARE="python3 outfitgame.py 300=Mage,305=Thief,308=Priest" sh
  loadsave.sh pens-after-arena` (`all=Warrior` for every figure). `start.sh` runs
  `PT_AFTER_PREPARE` in `playtest/` after `prepare_patched_game`, and with `PT_NO_LOADER` stops
  before the dice log (so `dice.txt` is not written and nothing of the Loader's runs).
  loadsave.sh shows only start.sh's last line: send the command's output to a file to read it.
- **With no Loader attached the game draws a party member from the game's own picture of its
  figure** (the human man's 2095/2096...), not from the object's own pair in the copy (2450 and
  on, `sprites.picture_ids`): pictures put only into the pair don't show. outfitgame.py writes
  both, so everyone of that figure wears the outfit (Kurzak, a half-giant, has a picture of his
  own and doesn't).
- `OBJECT=worn:LOOK` puts in a look by what's worn (`prototypes/wornlooks.py`: Robe, Leather, Bone
  scale, Chain, Cloak and hood). The names have spaces, so quote the list inside the double quotes:
  `PT_AFTER_PREPARE="python3 outfitgame.py '300=worn:Bone scale,308=worn:Robe'"`
  (logs/2026-11-21-worn-looks-in-game.md).
- **A fight with no Loader attached**: Tab's nearest-enemy pick is the Loader's, so Tab + Return
  opens the game's menu instead of attacking (and fightout.sh's E then the Effects screen; Escape
  closes either, a screen being up). Attack by clicking the foe. `fountain-user` starts Pehtucl's
  ambush on loading; its party is Lex (half-elf woman, object 307), Jenna (human woman, 301), Ester
  (elf woman, 305) and Seneca (halfling woman, 311), not pens-after-arena's: `python3 -m dsloader
  save SAVE01.SAV` (in obsidian-edition/) lists a save's party, race and sex, before guessing who is
  who from the screen.
- `OBJECT=preset:CLASS` puts in `prototypes/presets.py`'s picture instead: the class as a preset of
  the Loader's own gear drawing (clothes recoloured, boots, the fitted cloak), to compare.
- `pens-after-arena`'s party: a human man (object 300), an elf woman (Cilla, 305), a half-giant
  man (308) and a thri-kreen (313).
- A picture 8 pixels wider each side and taller than the game's own draws in its place without
  being cut (it stands on its bottom edge, its middle on the figure's): nothing under the feet.
- A click on a wall shows the no-walk pointer and moves nobody: click the floor.
- Grabbing a walk: `import -window $W` every quarter second from half a second after the click;
  the party crosses the hall in about two seconds, so most grabs are of it standing.

## The unchanged game

For a comparison with the game as it shipped (no DSCLOG, no Loader, no dice log;
logs/2026-11-16-spell-grid.md):

- **Starting it**: a DOSBox config of the Loader's settings with its own autoexec: `sed
  '/^\[autoexec\]/,$d' ../obsidian-edition/dosbox_dicelog.conf > $WORK/plain.conf`, then append
  `[autoexec]`, `mount c ".."`, `c:`, `DSUN.EXE`, `exit`. Kill any DOSBox (by pid), then from
  `$DS_GAME/DOSBOX`: `setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf $WORK/plain.conf
  &`. The game folder's files are the originals (the Loader writes its copies to
  `obsidian-edition/dos/`). **Not `start.sh` or `loadsave.sh`**: they start the Loader's game.
- **Its intro plays**: two title clicks, then Escape a few times, then the main menu.
- **A save**: copy `saves/NAME/*` into the game folder, then LOAD SAVED GAME (170,109), the slot
  (100,46), LOAD (253,46). A save made with the mod loads.
- **What works**: `click.py`, `creationscores.py`, `sheetinfo.py`, `shotinfo.py`, `hp.py` and the
  memory tools. Not: `buildcheck.py`, the dice log and its readers, and Tab's target (`fightout.sh`,
  `toturn.sh`): attack with `pointer.py attack` and a click on the foe.
- **It differs at creation**: a new preserver gets no CHOOSE A SPELL (the mod's); the window shows
  at a level-up.
- **A screen's layout**: read its WIND chunk in the game's RESOURCE.GFF against the Loader's copy
  in `obsidian-edition/dos/` (`dsloader.gff.read_gff`; a window's places are 30-byte items from
  +105h: the tag at +4, the id at +8, x and y at +0Ch).

## DOSBox-X: what the engine is like inside

For a test of the DOSBox-X engine ([a game in DOSBox-X](PLAYTESTING.md#a-game-in-dosbox-x) has the
kit's side; `dsloader/dosboxx.py` the configuration and why each line is there).

- **The memory file** is the guest's RAM, offset = guest address, 33,554,432 bytes (`memsize=32`),
  sparse, mode 0600, made again at every start (cut to nothing first: a mapping held over a
  restart would fault, so the Loader uses `pread` and `pwrite`). It stays when DOSBox-X closes;
  the Loader removes it. Read it with any tool: `python3 -c "print(open(PATH,'rb').read()[0xFFFF5:0xFFFFD])"`
  gives the BIOS date.
- **Memory layout**: the game loads at 0224h (0.74: 01A2h) and has 96,928 bytes free with the
  map open (0.74: 99,008); upper memory is CC00h-EFFFh, DSCLOG at CC4Bh with 1,168 bytes free
  below it, the overlay buffer at DD84h, 16,496 bytes free at E592h, the see-through tables at
  E99Bh and the music buffer at ED11h as on 0.74; the far block in the HMA. `memaudit.py` prints
  it all.
- **DOSBox-X's own keys**: its host key is F12 (F11 on Windows); host+F is full screen, Ctrl+F10
  lets the mouse go (as 0.74), Ctrl+F9 quits. Bare F5, F9, F10, Tab, L, R, Alt reach the game
  (all seen). Its menu bar is off (`-nomenu`, `showmenu=false`).
- **Its log** (stdout: `$WORK/dosbox.log` from the kit's script, `obsidian-edition/dosbox-x/dosbox-x.log`
  from the Loader's start) has DOS's own text ("DSCLOG loaded.") with `log console=true`, the
  window sizes it chose ("surface consider=960x720"), "Using memory file", FluidSynth's lines.
- **Pictures**: `normal3x` and `normal4x` on `output=surface` draw an empty grey window with
  this game; everything else the Loader writes draws. A picture test: start with
  `window_scale=3 picture=scanlines`, two clicks past the title, `import -window root`.
- **A write to code** made from outside may not be acted on, on a dynamic core, on either
  engine (`codepatch.py`); `core=normal` after the program on `start_dosboxx.sh` if a test needs
  it acted on.
- **Sound**: no device in the container (`SDL_AUDIODRIVER=dummy`). Since 2026-11-21 the Loader
  writes `mididevice=synth` with the soundfont in `midiconfig`: DOSBox-X's FluidSynth playing into
  its own mixer, so `PT_SDL_AUDIO=disk` records the music and the effects together. The other
  device, `mididevice=fluidsynth`, plays through FluidSynth's own driver ("Failed to create
  PulseAudio connection" here, no music; `extra='midi|fluid.driver=file'` renders it to
  `fluidsynth.wav` instead: the experiment's way).

## The recompiled program as the target

The kit drives the recompiled program (Dark Sun Recompiled) too (`PT_TARGET=recomp`, exported for
every tool; `DSUN` names the program, default `/home/user/darksun-recompiled/build/cmake/dsun`):

- `start_recomp.sh` (and `loadsave.sh` under that target) starts it with the Loader's patched
  game (`prepare_patched_game`, as start.sh) and the mod's `dos` folder, makes its window 320x240
  at 0,0 (so the window grabs and their pixel positions are DOSBox's), records its pid in
  `$WORK/dsun.pid` (the dice log and `live.py` use that pid: other dsun processes may be headless
  runs of the program's own tests, and `dsloader dicelog` refuses to guess among several) and
  attaches the dice log. **Its build must match the mod's helper**: the program lifts
  `dos/DSCLOG.EXE` into its `build/ds1o`; a branch with a newer helper needs
  `tools/build_mod.sh <this repo>/obsidian-edition` in the program's repository and its
  convergence runs first (a wrong helper shows as `no function at B....` in `$WORK/dsun.log`).
- `shot.sh` grabs its window and scales it to 320x200 (there is no Ctrl+F5 capture). Its colours
  differ from DOSBox's by one (38 of 63 is 153, DOSBox says 154) and its picture is stretched to
  240 rows a row apart, so pixel checks go through `pixmatch.py` (within 3 a channel, a row up or
  down): msgbox.sh, panel.sh and levelup.sh use it.
- **The dice log must be attached after the game is loaded**: attached at the program's start,
  or before a save is loaded, it prints nothing afterwards; `loadsave.sh` restarts it after the
  load, and after any restart of the program check that an action shows in `$WORK/dice.txt` before
  trusting its silence.
- **Saves cross over both ways**: a save made in DOSBox loads on the program (pens-kurzak-door),
  and one made on the program loads in DOSBox (pens-kurzak-door-recomp). The program's save
  leaves DARKSAVE.GFF as it was, as DOSBox's did.
- Controls behave as in DOSBox: click.py's relative moves converge on the pointer, walkto walks,
  right-click cycles arrow, red sword, red look, arrow; the arrow over a person shows the portrait
  pointer and a click opens the mod's Look box (Talk is its first button, 216,99).
- **The view does not scroll by itself** here either; the middle-button drag works (the program's
  runtime passes the middle button through). **The drag scrolls only with the Loader attached**
  (the dice log counts: it switches the helper's `scroll_on` on at attach); a program started with
  no Loader, as its own headless tests run, keeps the view still. **A kit tool that stalls on the
  program and not in DOSBox is a program fault to report**, not a tool to work around.
- **Doors at Kurzak's stop**: the look pointer on the doorway's drawing (square 95,27, above the
  door square) opens the mod's Look box "Door" (INFO only); the arrow, the look click and the sword
  on the door square do nothing and log nothing; the sword on Kurzak (object 29, then at square
  99,31) does nothing either: no fight starts from a click on a friendly figure.

## Wake of the Ravager

For comparing (its code, data and README; nothing in the kit plays it): `sh setup_ravager.sh` puts
the user's GOG installer (from the private repository, as the game's: the guide's [rule
10](PLAYTESTING.md#1-the-rules), or put at `$WORK/dl/rav.exe`) into `$WORK/rav`. Its DSUN.EXE is
laid out otherwise:
the creature/sheet records 42h bytes at the far pointer DS:19C5h, a class's level at +1Eh, its class
at +1Bh; the XP table is RESOURCE.GFF's DATA 1000 (8 rows of 20 words, in hundreds, looked up by
`lcall 5C8:20` with 3E8h); much of the code is in overlays, so a far call's segment isn't a place in
the file. Its level-up (95860h on) caps XP at the table's entry 3 levels past each class's own, then
raises a class under 15 (2026-11-08: no race limits, whatever its README says).

**Playing it in DOSBox** (2026-11-19, logs/2026-11-19-ravager-memory.md): GOG's settings are in
`__support/app/dosbox_darksun2.conf` (memsize 16, cycles fixed 15000, XMS, EMS and upper memory
on); it runs as `DSUN -W0 -L` (RAVAGER.BAT) from its folder as C:, with `CHARSAVE.GFF` and
`DARKSAVE.GFF` copied in from `__support/save` as SL's are. The CD is D:: Linux's DOSBox 0.74 can't
take GOG's `game.ins` (its music tracks are .ogg files), so mount a cue of the data track alone
(`FILE "game.gog" BINARY` / `TRACK 01 MODE2/2352` / `INDEX 01 00:00:00`) with `imgmount d data.cue
-t iso`; the music is then silent, nothing else missing. Shift held a second skips the intro (the
menu at 6 s). Its window is 640x480 (SVGA). **The first click only captures the mouse**: click once
anywhere harmless, then `xdotool mousemove_relative`, checking with a grab (START GAME at window
310,170). START GAME, the narrated cinematic (about 60 s, no skip), then Tyr: "Hurry! You must
come with me to the Veiled Alliance!" over the map. It runs with `ems=false` and `UMBPLUS.COM` too.
**`dosmem.py [PID]`** reads the memory of any DOSBox (no helper needed): both MCB chains, the
program's far heap (load + 0FE7h in SL, **+ 135Bh** in WotR) and DOS memory after it.

**The Loader's way** (the port, `dsloader/ravager.py`): `RAV_LOADER=1 sh ravstart.sh FOLDER` makes the
Loader's copies (DSUNLOG2.EXE, RESOURC2.GFF in the mod's dos folder) and starts DSUNLOG2.EXE from D:
(the mod's folder) with the game as C: and the CD as **F:**: the game finds its CD through MSCDEX
whatever its letter (2026-11-19: to Tyr with the CD on F:, as on D:). The copy reads its data from the
current folder (C:) by its "path" patch (DS:44F2h, SL's 4B81h).

**Driving it** (2026-11-19, logs/2026-11-19-ravager-fixes-2.md): `sh ravstart.sh [FOLDER]` starts
it to Tyr with no mouse (Shift twice, **S** on the menu is START GAME, 80 s). The game is 320x200
shown at 640x480: **game y = window y / 2.4**. Its pointer is DS:A109h (x) and A10Bh (y) (SL's
A133h); `python3 ravclick.py X Y [left|right|none]` moves there and presses slowly (0.3 s). The USE
screen (the top-left icon, 22,17) acts for the leader out of a fight (a portrait click doesn't
change who); the small top button left of a portrait is MAKE <NAME> LEADER (47,43 the first);
hovering names a button in the bar below; VIEW CHARACTER 47,171, VIEW INVENTORY 74,171, LEVEL
197,171. Out of a fight the keys **U** (USE) and **I** (the inventory) open them straight (2026-11-27), and the top-left icon
opens the screen last used; a click on an inventory slot takes up its item (AC changes when it is armour): click the
same slot again to put it back (logs/2026-11-27-ravager-sl-interface.md). The opening party: Ar'anda (elf preserver/psionicist/thief 6/6/7), an earth cleric 7,
Thy'rokh (thri-kreen fighter/druid, the leader), a half-giant gladiator 7; its sheets at the far
pointer DS:19C5h. **Running one of its routines on the live game** (`ravthief.py`, the thief
skills): most of its code is in overlays swapped out to XMS, so lay every overlay above A0000h from
Dark Sun Recompiled's `build_image.py` (its PSP set to the live one) with that image's stubs, the
live memory below; and give the emulator SS = DS (Borland reads stack buffers through DS).

**Running a routine through the helper** (2026-11-22, logs/2026-11-22-ravager-class-restrictions.md): an
overlay routine the Loader has patched with INT F5h (DSCLOG2's sites) can't run in the emulator as above,
which stops at an INT and lays the overlays over C0000h-FFFFFh, where DSCLOG2's upper memory block is
(CA1Bh:0 in that run). `ravthief.py --helper` shows the way: patch the site's bytes in the emulator's
copy, copy DSCLOG2's segment (the INT F5h vector's) to A01Bh:0 (A0000h-BFFFFh is free in the image) and
point the vector there, and dispatch every INT as real mode does (FLAGS, CS, IP pushed; CS:IP from the
vector table). **Moving items on the inventory screen**: a click on an item picks it up (the backpack's
cells light where it may go), a click on a slot puts it down ("CANNOT USE THIS ITEM", "ILLEGAL
PLACEMENT", "NEED TWO FREE HANDS", "THRIKREEN CAN'T USE" leave it on the pointer); a click on another
portrait shows that character with the item still held, so it can be carried across. Window to game:
x / 2, y / 2.4 (Ar'anda's right hand game 65,92, the left 172,92, the legs 172,127, the backpack's first
cells 195,27 and 207,27; the portraits 25 by 25, 69, 117, 165).

**Forcing a case in a fight** (2026-11-22): an edit of the game's own overlay code in memory doesn't hold:
the fight's overlays are reloaded from XMS several times a round, each time at another address (the
attack set-up was found at 5B865h, 5C215h, 5E445h, 5F3D5h and 60025h within one fight), so a loop
re-patching it every 50 ms still missed most attacks. Edit DSCLOG2's own code instead (it stays put in
its upper memory block, its segment the INT F5h vector's; offsets from `nasm -l`): for the backstab test
MISSILE_REAR's first 25 bytes (914h, the class restrictions' version) became `or si,si / jnz .out / mov
byte [bp-19h],1 / mov byte [bp-21h],1 / sub word [bp-1Eh],4` and NOPs, so every attack of the first
member is from behind and a backstab, as the game makes one. **Tyr's thieves for a fight**: from
`ravager-after-ambush`, the arrow keys Up 8 and Right 40 (world 1839, 1224), answer 2 ("Run along now,
pip"), Space: two thieves and two thugs; Computer Control for all four on the USE screen in the fight
(the lower small icon by each box, game 47,52 / 100,52 / 47,112 / 100,112), Escape to close it.

**Items saving against acid in the sequel** (2026-11-22, logs/2026-11-22-ravager-item-saves.md): the acid checks
(7CEC0h the weapon, 7D02Ah the armour) are reached only from the power handler's switch (656ECh, the power at
[BP+0Eh], 81 cases at CS:28C1h): Crystal Brittle 103 and the monster powers 275, 283, 284. To play one,
`ravknow.py 103 18` and cast it from USE (level 9) on a foe; the armour loop takes only the worn slots 0, 6
and 9, and Tyr's street thieves had their armour in slots 14-16 at the fight's start (`ravitems.py N
--worn` moves it). A foe under the spell's pointer shows red; `ravclick.py` takes 320x200 game pixels, and
a foe was taken about (8, 5) off its `ravfight.py state` place. A rule-off control records nothing in
the helper: read the dice log's plain d20 and the items gone (`ravitems.py`). Casting the last of a
level's slots shows "ZERO LEVEL 9 SPELLS TO CAST": write the slots again and press LEVEL round.

**Weapon specialization in the sequel** (2026-11-24, logs/2026-11-24-ravager-specialize.md): the weapon attack routine (5CE80h, SL's 58780h) has SL's frame with its locals two lower: the attacks a round in halves `[BP-0Ah]` (stored at 5CEE8h from the sheet's +24h in melee, the type's +7 for a missile), the damage dice `[BP-10h]` (type +9), sides `[BP-12h]` (+8), bonus `[BP-14h]` (+0Ah; the item's plus +16h added unless an Enlarge-like effect 4 is on either side, then the strength bonus, 98h:42Bh, at 5CF6Dh); `[BP+0Ah]` the THAC0 the d20 is held against (less `[BP+0Ch]`), `[BP+10h]` the sheet, `[BP+12h]` the item, `[BP+14h]` the type, `[BP+16h]` above 1 a missile. After the store the game doubles the halves for a status 4, halves them for 1, a ninth for 7 (628h:5Ch), then (the round's parity + halves) / 2, and cuts a shot's attacks to the ammunition left (5D007h-5D046h: "Out of ammo"). The sequel gives every warrior 3 halves (sheet +24h) as SL does. **A specialist's line in the dice log** reads "THAC0 19 base, +3 in bonuses, +1 specialized = 15" (the sequel's set-up frame isn't SL's, so the bonuses aren't itemized) and "1d6 = [3] +1 weapon +2 specialized +4 STR 18". DSCLOG2's `spec_hits`, `spec_damages`, `spec_rates` count what it did (scratch `spcount.py`: the symbols from `nasm`, the helper found by its `DSCLOGR1` header). **The transferred party in Tyr's ambush** under Computer Control: give the four HP 250 and base AC -10 in memory (48h sheets: `sheet * 48h + 21h`; never saved) so the fight lasts 30 rounds or more; put an archer's melee weapon in the pack (an item's +13h 14) to have the AI shoot, though it may take it up again. **"Illegal Op (gpl=49)"**: 9 of 14 of those fights (ravG48's 48h party: 5 of 9 with the rule on, 4 of 5 with it off) end with the game quitting so (`RAV_STDOUT=1` shows it, `RAV_MARK=1` writes ENDED.TXT), mostly at Ester's turn; not yet looked into. **Another agent's dice log** attached to this DOSBox (a Loader test of its own) wrote its rules word into DSCLOG2's header: a run whose `rules` (header +170) isn't the Loader's is void (`spcount.py` prints it).

**The lotulis', double spear's and trikal's traits in the sequel** (2026-11-26, logs/2026-11-26-ravager-weapon-traits.md): the attack's set-up (5C5E1h) takes `[BP+0Eh]`, its caller's distance to the target (the computer's at 5C0D7h, from the distance routine 1D40:35EFh), and passes it on as the hit routine's `[BP+16h]`: **above 1 is a shot** (5C77Dh: the set-up's missile way, the type's range +6 held against it at 5C8A9h). So a melee weapon of range 2 (the sequel's Double Spear 39, alone among the weapons; type 22's +6 is 2 too) swung from 2 squares took the type's +7 halves (the double spear's 2: one a round), DEX to hit, no STR damage, and the computer (5BDC2h: its target's distance against the weapon's range) swung it from there; the DAM lines (7B0B4h: "cmp byte es:[bx+6],1 / ja") show such a type as a missile weapon. The hit routine's frame: `[BP+0Ch]` the target's AC (the set-up's `[BP-6]`, from the AC routine 5D520h: target, attacker, the behind flag `[BP+20h]`, a far routine called "push cs / call near" at 5C9A7h), `[BP+0Eh]` the attacker's creature, `[BP+18h]` its combatant, `[BP+1Eh]`/`[BP+20h]` the backstab and behind flags. The swing loop's "cmp ax,[bp-0Ah]" (5D308h, after "inc [bp-16h]") is passed by every swing and once before the first (SL's AMMO_TURN site). A creature's +15h is its group: the game's friends by the bit mask 71h, its foes F80h (23838h); +14h 1 Okay, 3 out cold. An overlay routine called from DSCLOG2 by its address (the INT's way back's CS, its IP + the distance) needs the INT's way back in a BP frame below it, as the stinkpots' far calls do, for the overlay manager to fix up. The game keeps a combatant's hand weapons in a copy of its own: moving the off-hand weapon to a pack slot in the sheet (a test edit) left its off-hand swing in place (2026-11-27), so for a test of one weapon alone, put the other in the pack from the inventory screen before the fight.

**The sequel's own six weapon specs** (2026-11-25, logs/2026-11-25-ravager-new-specs.md): a spec for a test made in the
**Shattered Lands save** before the party transfer (`game.with_specs` on a copy's `SAVE 6` sheets, written back with
`icons.with_chunks`), then `python -m dsloader.ravtransfer SAVE COPY SL_FOLDER DOS_FOLDER`: the roster's 48h sheets
carry it (V3 at +42h..+44h). A weapon of a kind for a test: the held item's type word (+0Ah of its 17h record) made
the sequel's type in memory (never saved; the item keeps its name, so the dice log's "Obsidian Longsword (1d10)" is
the Twohand Sword's type), its left hand's item to the pack (+13h 14). The sequel's own types of SL's six kinds: the
Twohand Sword 101 and Crystal sword 35 (two-handed 1d10: the type's +0Bh 40h), Lotulis 61, Double Spear 39,
Trikal 100, Javelin 59, Darts 38 and 43 (the type's dice: count +9, sides +8). **A second sequel game** when the
shared DOSBox is busy: a copy of the kit with `:57` in env.sh, paths.py, ravclick.py, ravfight.py and ravstart.sh's
Xvfb line, `PLAYTEST_WORK` its own folder (rav.pid, rav.conf there) and a `dosbox` wrapper first in PATH that runs
a copy named `dbns`; a script testing `/proc/PID/comm` must then look for `dbns`, not `dosbox`.

**The sequel's screens: DAM lines, Effects, the Look box's close** (2026-11-25, logs/2026-11-25-ravager-screens.md): the inventory's DAM line routine is SL's at 7AF9Eh (its item DI, type SI, the creature far at `[BP-6]`, 0 in an item box): the melee branch reads the sheet's +24h at 7B19Eh, the missile branch the type's +7 at 7B124h, each then "mov ah,0" and the push for the line's routine (7B1D9h); the bonus, sides and count are pushed under it. View Character's line is at 6CA43h on (`[BP-6]` the attacks, `[BP-2]`/`[BP-4]` the dice, `[BP-0Ah]` the item, the bonus stored at 6CAC9h); it took Ester's left-hand weapon. The likeness search missed both (the sheet's and types' sizes differ): search for the sheet read (`26 8A 47 24`) instead. **The Effects screen**: the cells' routine 8AC6Fh (ends 8AFA9h, `[BP-4]` the cells used), the handler 8AB13h (its redraw "call 140:60Dh" at 8AC62h, way out 8AC6Ah); USE, then EFFECTS (122,171), the portraits at (70,56), (117,56), (70,127), (117,127), the lower panel's lines from (150,108). **The dialogue window**: its stub 476Ch (SL's 42CAh, entries 25h the input and 34h the wait), found by its callers' likeness (SL's 42CA:2Ah calls at 1BC2Ch/1BE74h, the sequel's 476C:2Ah at 1F063h/1F2D6h). **To see the Look box's description** a monster needs more than HP, AC and THAC0 to say: Draxans have no defences, so set their resistance class (the creature's +0Fh) to 2 in memory for a test (never saved). **A spec edit for a test** must write the packed SPEC_V2 form (the kinds base 17 in the low 17 bits of +42h..+44h): the Loader's age pass rewrites plain bytes there. The Effects screen's kit line needs RULE_HI_KITS (1) in DSCLOG2's rules_hi (header +270), which the Loader doesn't set until the kits' rules are ported. **The opening talk** of a new game with the transferred party runs into the Draxans' fight after three Continues (100,171); the screens open in the fight: the top-left icon (22,17), then VIEW INVENTORY (74,171); on the inventory its bar's first icon (170,187) is VIEW CHARACTER; on View Character and Effects the bar is (47,171) VIEW CHARACTER, (74,171) the inventory, (122,171) EFFECTS; the inventory's portraits at (25,25), (25,69), (25,117), (25,165).

**The new wizard spells' numbers** (2026-11-26, logs/2026-11-26-ravager-new-spells.md): DATA 0-319 are all the
sequel's (wizard 0-114, priest 115-234, psionic 235-268, MONS269-319); the known bitset's free bits 115-119 are priest
records' numbers. So the mod's six are 320-325 (`dsloader/ravspells.py`: DATA 320-325, ICON 21320-21325, SPIN 321-326
in RESOURC2.GFF; the game's own ICON stop at 21268, SPIN at 269), known by the sheet's +3Fh/+3Dh bits (as SL's). The
game never asks for them until DSCLOG2 does. The sequel's spell icons are PLNR or PLAN, and a few of its ICON and BMP
chunks are SL's kind; `sequelicons.decode` reads all three.

**Casting the new spells in the sequel** (2026-11-26, the same log, part 2): the spell handler's switch at 656D0h
(81 cases at CS:28C1h of the module from 642E0h; Strength 23 and Adrenalin Control F5h share 6623Bh, the effect in
`[BP-12h]`, its 1d6 pushed at 6624Eh, the adder at 65AFBh); the abilities routine 8527Bh (`[BP-9]` 0 under
Anti-Magic 4: no wizard or priest spell's effect), its effect switch at 85351h (9 cases at module 83400h + 2386h;
STR `[BP-348h]`, DEX `-346h` ... CHA `-33Eh`; out at 8543Bh); a natural attack's dice 86A45h (DX the attack, far
`[BP+0Eh]`/`[BP+12h]`/`[BP+16h]` count, sides, bonus); the effect records (31 bytes at the load + 3C870h) end
with 112, zeros after for 3169 bytes, and the creature's effect bits are 15 bytes (7FE93h: 0-119), so 113-116 are
free for data. The swing's `[BP+0Ah]` THAC0 holds for the call's swings (5D052h is each swing's start; the first
when `[BP-16h]` = `[BP-0Ch]`). In play: a spell dropped on a member's portrait on USE is cast on that member, a
drop on the list's panel brings the aim pointer up; the USE screen keeps its LEVEL between openings.

**Learning the new spells in the sequel** (2026-11-26, the same log, part 3): CHOOSE A SPELL's pick sets the bitset bit
at 936B4h (`mov es,ax / or es:[bx+39Ch],dl`, ES 370h before, the spell `[370h:7 + SI]`, the member `[370h:0B44h]`);
the page's list is words at 370h:7 (room for 20: 370h:2Fh is a dword of the game's). A spellbook's read (from the
item box's spell icon, outside a fight) is 999A9h on: `[BP-4]` the power - 1, objects 7918h-79DFh and 7AA8h-7B0Bh
(31000-31199, 31400-31499) learn, any other (a one-use scroll, 313xx) goes to the cast at 9B7Dh; the bit test from
999F8h, YOU LEARN THE SPELL at 99A5Ch (the book used up), YOU ALREADY KNOW THIS SPELL at 99A86h. An item's power is
the spell + 1, compared with 140h at 77CF9h, 9A7D4h and 9A9C5h. **The overlay manager fixes up segment words in
overlay code** (`mov ax,370h` at 999F8h, as `mov dx,338h` in least_scores): none of them is in the MZ relocation
table (`gamepatch.relocated` doesn't see them), so a site whose INT number or NOPs land on one runs another INT
(here: DS:4 and DS:4Ch written, the Borland signature broken, the Loader's `find_data_segment` then None). Put a site
after such a `mov` (999FBh). **The hit routine's frame**: NS_SWING's BP is the hit routine's; the set-up's locals
(the natural attacks' set `[BP-20h]`, which the dice log reads as the d20's parent) are at `[bp]`'s frame.
**A party member with nothing in hand** (a thri-kreen too) can't attack after a slot edit in memory alone (a
barred sword over a foe); moved to the pack on the inventory screen (pick the hand's item, click a pack square) the
foe turns red and a thri-kreen fights with its claws and bite (the inventory's DAM "<4x1D6+8>" with Erdlu Claw). A
spellbook for a test: `logs/files/2026-11-26-ravager-new-spells-scroll.py ITEM POWER 60` (the record of item 60, a
spellbook, over a carried item; the box's spell icon then teaches). A level up for CHOOSE A SPELL: the log's
`-levelup.sh`; creation's: `-create.sh` (a throwaway copy's roster).

**The sequel's first spells and powers** (2026-11-25, logs/2026-11-25-ravager-first-spells.md): the creation
screen's DONE (6E0B9h, 5C0:57h; SI the member) calls 6E6D8h, the powers (6E906h, 5C0:2Ah), a preserver's spells
(6EA10h, 5C0:2Fh), 6ED7Dh, then 98:0Fh, all from DONE only (no START GAME path as in SL). The wizard spells known
are a bitset (selector 320h, the load + 3D62h: 39Ch + 15 a member, bit n spell n; SPELL_STARTS at DS:0656h: 1st
level 0-11, 2nd 12-24, 3rd 25-38, 4th 39-55); the powers a byte each (selector 370h, the load + 3E71h: 9CDh + 22h a
member, bits 1-7 the number, 580:39h gives one as 2), the disciplines' bits A55h + the member; the pop-up's
discipline shown DS:9D7Bh + the member, its picks left DS:43ECh (CHOOSE A SPELL's page level too), its list DS:9C20h
(words, 0 the end). Selector 360h holds the screen's snapshot (+0 the preserver level at an EDIT's opening, the
spells given again only when it differs) and the powers' table (+6 three rows of 5, +15h the psionicist's 20). The
level up's windows take a member and run until closed: CHOOSE A SPELL 688:66h (93160h; one spell a call), the
psionicists' pop-up 688:61h (93B62h; its count from the psionicist level, closed at none); module 40's stub segment is
DS - 30h, module 15's DS - 103h. The overlay layout (modules, stubs, entries) from Dark Sun Recompiled's
`tools/build_image.py DSUN.EXE --out DIR` (its layout.json: a module's `record` x 8 is its selector). **SITE's way
back** is the byte after the site's number: for a 4-byte site the NOP, so a site that stands for a jump adds the
target less that address (one byte late, PSI_LIST jumped into an instruction: "Illegal Op (gpl=49)" on a click).
`ravfirst.py` reads it all. In the creation screen the pop-up's discipline button is (115,140), EXIT (202,140), its
icons from (121,62) 19 apart; CHOOSE A SPELL's icons five a row from (124,74), 19 by 17 apart, LEVEL (107,147), EXIT
(205,147); "YOU HAVEN'T CHOSEN"/"YOU HAVE MORE"'s EXIT (112,92).

**With STORE/RECALL and the starting gear** (2026-11-25, logs/2026-11-25-ravager-join-gear-spells.md): DONE's
windows (CHOOSE A SPELL, then the powers' pop-up, which every class gets: everyone has a discipline) all come before
GEAR_DONE (6E2F2h), so its hold for the Loader starts only once the last window is closed, however long they stay up
(gear_timeouts stays 0). CHOOSE A SPELL's LEVEL button does nothing while the level being picked is 1 (CR_CAP is that
level). A stored roll outlives NEW: it is forgotten only at the first button after a change of race, sex, classes
or kit, so a new character like the stored one could RECALL it (SL's DSCLOG the same). Making more than one: View
Character's bar's right icon (270,171) goes back to the title menu, then CREATE CHARACTERS again; a right-click on
slot 2 (117,56) puts its menu top right (NEW 160,57), on slot 3 (70,127) beside the slot (NEW 110,118). PSIONICIST
on the classes' list is (265,53).

**The level up, the XP table and the saves in the sequel** (2026-11-25, logs/2026-11-25-ravager-level-cap.md): the
level up (95820h on: SI the member, DI the class's place; `[BP+6]` nonzero levels without the XP) holds the
sheet's XP to the table's entry level + 3 (958AAh-95940h: "add ax,3" at 958BDh, the reads at 958E3h and
95931h), then reads entry level (9597Ah: the next level's XP) and at 959A5h holds the level below 15; it
loops on the same place while a level comes (95A85h "dec di"), a human only on place 0 (9587Fh). The XP
table is read only through 5C8:20 (6F640h: the resource DATA 3E8h loaded by 128:4ABh, the word at row x
40 + index x 2, let go by 1D0:92h each call): nothing stays in memory, so DSCLOG2 keeps its own copy
(RAV_XP_AT). Out of range it reads on into the next row (row 7, the thief's, past the resource). The
class-to-row map is 360h:9Dh (a word a class: 1-4 cleric 1, 5-8 druid 2, 9 fighter 3, 10 gladiator 4, 11
preserver 5, 12 psionicist 6, 13-16 ranger 7, 17 thief 8). View Character's next XP (6FB21h): its copy's
classes are rows, the least next XP at `[BP-6]`, "push 1383h" "(" and "push 1386h" ")" around it (6FBDFh,
6FC08h). Creation (6C3A4h-6C4E7h) puts a class at 6th or 7th (XP the most of their needs), then one
level more where the XP allows: 8th at most. **Hit dice**: the class-to-group bytes 4D0h:10h + class
(0 priest, 1 warrior, 2 wizard, 3 rogue: psionicist 12 and thief 17), the groups 4D0h:0 four bytes each
(die, levels rolled, fixed gain after, CON's most): (8,9,2), (10,9,3), (4,10,1), (6,9,2). **Saves**:
954D2h, the per-group levels from 953A9h (`[BP-0Ah]` + group x 2), the table 4D0h:6Ch + group x 15 + save x 3
(1st level's, a rate in hundredths, AD&D's last row), save = first - min((level - 1) x rate / 100, last); a
dwarf's or halfling's CON x 2 / 7 is added for the warrior group (it tests the group, CX, for 1 or 4: SL's
the same). **Spell slots**: 62A10h by a formula (DS:0670h + class: a nibble list of DS:0684h words: start
level, odd/even, most), a ranger's 3 2 1 at 12th, 3 2 2 at 13th, 3 3 2 at 14th, AD&D's 2 2 1, 3 2 1, 3 2 2
(ADND_SLOTS now gives the Handbook's). `ravlevel.py` shows the party's levels, XP, saves and the helper's
counts, and sets a member for a test. **Played** (2026-11-25, logs/2026-11-25-ravager-level-cap.md): without the fix the game's XP clamp reads
past the table's end for a class at 17th or more and sets the XP to 0; the saves are the least of each group's
(954D2h's loop); a fight's XP goes a third to each class of a triple class. On View Character a click on a
portrait at the Effects screen's spots (70,56) (117,56) (70,127) (117,127) shows that member; level-up messages
come one a click of the box (160,100), the dice log's "Message:" lines list them all. **Levels 21-30**
(2026-11-26, the same log): the game's XP table has 20 entries a class and its reads past them run on into
the next row; THAC0 (creature +16h) is read signed (`cbw` at 5C6E9h, 7CFF7h, 844B6h) and View Character
shows "THAC0: -9"; hit points take the group's fixed gain past its rolled levels (94FF2h); the level up's
message (959A5h on) pushes "th" (DS:2B7Eh) for every level past 3rd, and "%Fs gains a level" (DS:2B87h)
when the long one passes 29 characters (a preserver's "is 22nd level Preserver"). The wizard spells run
to a 10th level (DS:0656h's starts: 111-114 Dome of Invulnerability, Magical Plague, Rift, Wall of Ash),
and CHOOSE A SPELL opens on level / 2 from 10th, so a preserver's level up from 20th offers those first.
The psionicists' pop-up (688:61h; its picks 1, 2 at odd levels and at 4th, from 98:C1h's psionicist
level, root code at 1D111h) lists known powers too: a pick adds 2 to the power's byte (bits 1-7 its
number), so it never runs out. The slots left are set only by a rest (the Roost: `ravload.sh
ravager-roost`, Reyhan "1 3 4", the corridor, the second doorway's steps at game (262,93), Up 6, the look
pointer on the ring at (265,113); the pointer mode DS:1440h, 1 the arrow, 4 the sword, 2 the look). The
level up's hold (3 levels on) raises a class four levels an award at most. Without PICK_ANY the game's own CHOOSE A SPELL counts from the class level (a 22nd-level preserver's
window opened on "LEVEL 11", the priest spells' empty page, and no pick closed it); with it the page is
level / 2, now 9 at most (PICK_MOST). The THAC0 routine (9534Ch) runs PRIEST_THAC0's site for every
class group (CX 0-3), so a group's limit goes there.

**Stealth in the sequel** (2026-11-24, logs/2026-11-24-ravager-stealth.md): the attack's set-up (5C5E1h)
keeps the attacker's creature in `[BP-0Eh]` (records 31h bytes, its THAC0 at +16h, taken into `[BP-1Eh]`
at 5C6EEh each attack), the sheet in `[BP-12h]`, the weapon type in `[BP-4]`, the target-is-an-object
byte `[BP-1Ah]`, from behind `[BP-19h]` and backstab `[BP-21h]` (both cleared once a call, 5C5FEh, while
the loop back to 5C6DDh runs a round's attacks); melee is `[BP+0Eh]` 1 there and `[BP+16h]` 1 in the hit
routine (5D1D6h). Map objects' x, y at DS:67C5h, 25h apart. Each RGNxx.GFF names itself in an `RNME`
chunk (forest, Tyr, VA Headquarters, Pyramid, Yuan-ti Tunnels, El's Temple, Mines1-3, Jann, Mosaic,
Volcano Level 1-3, Silt Giants, Cloud, Crypt, Cosmos, UnderTyr, Limbo). The sequel's effect numbers
are not SL's (its 25 is Detect Invisible): map SL's tables by name (`ravlog.effect_names`).
`ravdice.py` with `RAV_STEALTH_ROLL=1` hides every thief and ranger who can. **DOSBox dying** in the
transferred party's Tyr fight (about half the runs): `ravstart.sh`'s `RAV_CORE=normal` (the CPU core)
and `RAV_NOEXIT=1` (DOSBox stays up if the game quits) ruled out the dynamic core and the game's own
exit; `strace -f -e trace=exit_group,kill,tgkill -p PID` on DOSBox to see how it ends.
**Thieves as in AD&D in the sequel** (2026-11-24, found statically, the sites run on the game's own bytes in
`tests/test_ravthief.py` with `DSUN_WOTR`; played 2026-11-25 on the kits branch, logs/2026-11-25-ravager-thieves.md,
where the two sites became 52 and 53 and STAB_TIMES gives an Assassin one more): the thief skill routine is 8C647h (SL's 8023Bh),
the same code with the sequel's frame: DEX in `[BP-2]` (SL's `[BP-0Ch]`), the skill a dword at `[BP+8]`,
the thief level in SI (580h:61h, class 11h), the tables at the game's segment 4A0h (file 49BB0h, load +
449Bh: the base at +skill, race R's row at 8 + 8R, the DEX limits A0h, A8h, B0h, the armour penalty B8h).
SL's `thief_skill` bytes are at 8C716h ("mov ax,si / shl ax,2 / add dx,ax / mov si,dx", DX base + race),
the game's DEX formula after them to 8C795h ("push di", its armour and effects): DSCLOG2's site 52
(THIEF_SKILL, then "jc" +7Ah) does SL's PROBE_THIEF_SKILL there, and BELT_SITE (8C7C5h) keeps the chance
to 95. The attack's hit routine (5CE80h, SL's 5883Ah) keeps the round's attacks so far in `[BP-16h]` (from
the creature's byte at selector 308h, +184h; SL's `[BP-14h]`), the damage roll's bonus in `[BP-14h]`; the
backstab multiply (SL's 58A80h) is 5D11Bh, the same 10 bytes, after the game's test (`[BP+1Eh]` and
`[BP+20h]` bytes, the attacks at most 1, 5D0F8h-5D112h) and the multiplier routine 5DE0Ch (SL's 595C4h,
the same: x2 to x5 by thief level). Enlarge (628h:57h) runs before it at 5D0D2h, so ENL_SITE's enlarged
dice are the ones multiplied. STAB_FIRST (from MISSILE_REAR) takes back a member's second backstab at the
same game clock (the far pointer at DS:9C0Ch, SL's 9B72h: the timer set-up at 2CB40h writes it). In a play: `ravdice.py` should show a thief's skill check as `"<name> tries to
open locks: d100 = N, needs C or less"` with the second line `open locks C = <AD&D's> thief level L + <race>
+ <DEX>` and no "equipment" part when nothing is worn in the hands, legs or quiver (the old game sum showed a
large "equipment" remainder), the inventory's skills the same numbers before equipment, and a backstab as
`"+M backstab (the dice D xT = D*T)"` with the damage the dice x T plus STR once (DSCLOG2's `stabs` counts
them). **Played** (2026-11-25): Seneca's inventory (USE, VIEW INVENTORY, her portrait at 25,69) is AD&D's
average + the sequel's race row + Dark Sun's DEX (the control, `RAV_RULES_OFF=0x100`, the game's sum); a hidden
backstab in the Draxans' ambush "1d4 = [4] +1 weapon +4 STR 18 +4 backstab (the dice 4 x2 = 8)", 13 HP off
(control "(1d4 = [2] +1 weapon +4 STR 18) x2 backstab", 14); a human thief 3 made an Assassin (`ravkits.py
set 1 2 1 17`: a halfling fighter/thief's only kit is the Poisoner) "+6 backstab (the dice 3 x3 = 9)", x2 with
the kits off (`kit_stabs` in `ravkits.py count`). With `RAV_STEALTH_ROLL=1` the CC AI hides Seneca every turn
but shoots her sling at range: half the runs end without a backstab. The dice log's hiding chance is the
Loader's (stealth.py, the table always), so it doesn't follow a thief-table control.

**Its fights in the Loader's dice log** (logs/2026-11-20-ravager-dicelog.md): `python3 ravdice.py SECONDS
[OUT]` runs dsloader.ravlog.RavDiceLog (SL's dice log on the sequel's layout, its memory read only) on the
running sequel. Addresses found for it: the combatants selector 388h at C33h (load + 3F49h), the
initiative selector 308h at DCh (load + 3C4Fh), the attack's target DS:4206h, the item types 15 bytes
(DS:19CDh), the item names RESOURCE.GFF's TEXT 1000 (a line a name, from 1), the rules' small tables SL's
+70h. A selector's segment: the segment table at load + 45E8h, + the selector. `ravds.py --fuzzy HEX`
maps an SL data address by the code round its uses.
The AC function is the sequel's own (5D520h; its end 5D6E6h, PROBE_AC). `ravdice.py --all` shows every
roll and each AC worked out. **To find an unnamed roll's code**: catch its entry (its frame's first words
are the return address, then the arguments: the dice routine's count and sides) and read the code at
that address at once, before the overlay moves, then find those bytes in DSUN.EXE.
**Playing it** (2026-11-20, logs/2026-11-20-ravager-dicelog.md; the walkthrough: `setup_guide.sh`, then
`$WORK/guide/ravager.txt`, the owner's copy from the private repository):
- **Attacking**: in a fight the **Walk pointer, the plain arrow**, clicked on a foe walks to it and attacks
  (the manual); the sword pointer shows a barred sword in a fight and does nothing. Right clicks on bare
  floor cycle arrow, sword, look: track the pointer by picture, not by count. A foe under the arrow turns
  red. In a crowd a click can take the wrong figure (`ravfight.py attack` aims at a figure's place + 10,
  22). `ravfight.py fight` attacks on every party turn; the ambush was lost that way (Gerakis never
  struck).
- **Computer Control**: the inventory screen (the top-left icon out of a fight; in a fight USE, then the
  second icon of its bottom row), the lower of the two small icons left of each character box (a small
  screen; lit orange when on; the upper one marks the character shown). All four on won the opening
  ambush by itself (3 Draxans, a templar) with the party standing. Once the inventory has been opened in a fight,
  the top-left icon brings it back (the menu keeps its last screen) and its lower icons may miss one
  (2026-11-25): **C** then the USE screen's lower small icons (47,53 / 98,53 / 47,112 / 98,112) is sure.
- **Sides**: creature +15h: 0 the party, 7 the opening's Draxans, 1 the town's people.
- **Saving**: the inventory's GAME MENU (game 267,187), the disk (136,100), SAVE (145,105), a slot
  (127,46), type the name, SAVE (252,47): SAVE01.SAV, CHARSAVE.GFF (DARKSAVE.GFF not rewritten).
  **Loading**: the title menu's LOAD SAVED GAME (159,110), the slot, LOAD (252,47): `ravload.sh NAME`
  (`saves/ravager-after-ambush`, the opening won). Escape with nothing up brings EXIT GAME? (QUIT /
  CANCEL at 145,116): a second Escape after closing a screen does it.
- **Walking**: the **arrow keys** (not the keypad's) walk the leader a step (16 px) a press and the view
  follows; clicks with the arrow walk too but only on screen, and are barred near its edges or on
  walls. Out of a fight only the leader is on the map (its object, 2 for Thy'rokh as leader); world
  pixels are screen pixels from the camera (DS:1408h). Inside a building with its roof cut away the
  leader can be hidden behind the roof's edge. The area map (game menu) shows a marker that doesn't
  follow the party.
- **A new game** (2026-11-25, logs/2026-11-25-ravager-weapon-gaps.md): the title menu's START GAME (game
  159,75), the opening film about 75 s, then the opening talk (3, Return x4) and the ambush: C, the four
  lower small icons (47,53 / 98,53 / 47,112 / 98,112), Escape, about 90 s to "Each party member receives
  10000 experience points!" (Return x4 for the level lines). Everything from OBJEX.GFF (the Loader's new
  items, `dsloader/ravgear.py`) shows only so: a save keeps the people and things it has made.
  **Shadow Square from there** (`ravgo.py y 1224 x 560 y 1130 x 420 y 1000 x 300 y 900`, about 2 minutes):
  a ranged-weapon stall blocks y 1224 at x 536 (its seller in front of it talks: 1 opens the shop: the
  Limbo seller 323, thing 16), Notaku's stall north of the end. **The pointer** over bare ground shows
  its barred form (an orange ring: the sword's, then the eye's); right-clicks go arrow, sword, look, so
  take a picture of it before a click on a person: **the sword on Notaku started a fight**. With the eye on
  him the Look box's first button (left, about game 181,66 when the box is beside him) talks.
- **A creature's object** is its record's +6, negated (as OBJEX.GFF's kind-2 record has it: Notaku -58,
  the weaponer -153): how `shopstock.py` knows a seller in memory. A **Limbo seller** (the stalls: 323 and
  the like) is made afresh from OBJEX.GFF's copy when its talk starts, so it has the Loader's items even in a
  saved game; Notaku, who lives in Tyr, keeps the save's list and is topped up by the Loader. **In a shop a
  click on an item buys it** at once ("NOT ENOUGH MONEY" if it can't); the item goes on the pointer.
- **Item names 256 on** (the mod's, DSCLOG2's ITEM_NAMES) are written by the dice log as it attaches:
  without `ravdice.py` running a mod-named item shows another word ("METAL" for the Short Sword).
- **Objects 13000-13999 draw another picture** (a grey ring) whatever their BMP: the Loader's pictures sit
  at 14000-29999 (`ravitems.own_object`, `ravgear.OWN_ICONS` 19900). **Palette numbers 1-15** are set by the
  inventory and shop screens (PAL 1000's 2, a light blue, showed pure blue there): `ravitems.stable_colours`
  leaves them out.
- **Every item record from a map** (the far DS:19C1h, 17h each, as `ravshop.py` reads them): a scan for
  entities -14000 to -29999 lists the Loader's items loaded in the region (Tyr in a new game: Short Sword
  +1 and +2, Great Axe +1, the metal mace, dagger, pick and polearm).
- **Tyr from the save**: the street runs north-south at x ~1175; its south end is the city gate ("The
  gates are locked."). Uhubito's building east of it (door on the street, y ~1340); an alley east at
  y ~1225 (entered from the street at y ~1225-1240), past Arslan's side and the beggar, along the
  Harbinger's Roost's north wall (no door there: its arches are inside doorways seen through the
  cut-away) to the map's east edge (x ~2020); two thieves stop the party near x 1840 ("Run along now,
  pip" makes them fight: won by Computer Control, the party hurt). Fayina is in the Roost's back room
  (1807, 1352). **The Roost's door**: on its north wall at world x ~1621 (an arched doorway with white
  steps, drawn as if inside): the arrow clicked on the steps takes the leader through (the arrow keys
  stop at the wall line, y 1274). Inside: Reyhan, the owner, behind the counter (the look pointer on him
  talks: 1 rent a room, 3 one night, 25 cp: "the room at the end of the corridor, second door on your
  left": the corridor runs east along the south front, the second doorway is open, its steps clicked
  again). Renting adds one map object, a fire ring (object 156 at 1976, 1352, kind -1317), beside the
  bed (which takes no pointer). **The route** (from `ravager-roost`, about 3 minutes): the look pointer
  (two right-clicks from the arrow) on Reyhan (game 150,128), keys 1, 3, 4 (rent, one night, goodbye: the
  talk ends on Reyhan's "Goodbye.": Space closes it, and in the 2026-11-22 run the pointer was then the look's: one right-click gave the walk arrow; check before the arrow keys: the sword ignores the arrow keys),
  the arrow keys Left 4, Down 9, Right 14 (the corridor, x 1871, y 1465), the arrow on the second
  doorway's steps (game 270,104), Up 6 (beside the ring, 1956, 1335), the look pointer on the ring (game
  267,108: the screen is 2.4 px a game row) and click. **A look at the ring rests the party** (the screen
  dims, 8 hours: HP back, spells, DSCLOG2's REST_POISON per member) only with the Loader's `inn_rest`
  fix: the game's own script loses the one paid night (dsloader/ravager.py SCRIPT_FIXES; logs/
  2026-11-20-ravager-dicelog.md 25-26). A second look takes the spent ring away.
- **How a look reaches a rest** (2026-11-20): the look dispatcher (63174h-63400h) runs the object's look
  trigger scripts (a 66h trigger: trigger list load+3C10h:13h, bit 8 of 28:834's flags), then, if the
  object is still there, the program's own look (5B0h:70h, 69473h), whose kind-525h (1317, fire ring)
  branch calls rest(0, 8, 7FFEh) (6951Ch: the rest routine 8CA7Ah). A script's do_action 1 is rest(1, ...),
  the healers' full heal (status 1 for all, the dead too). do_action 15 is no camp: it sets DS:1440h
  (the pointer mode: 1 the arrow) and DS:4596h to 1, the end of many scripts. `triggers.py`-style dump:
  the six lists' heads at load+3C10h:0Dh-17h, records 13 bytes at the far pointer DS:40C0h (+4 the
  object, +0Bh the next).
- **Keys** (gibberishh's walkthrough, in the private repository's guide/): I inventory, O overhead map, V
  character, C cast, 1-4 leader, 5 the whole party shown, 6 the leader only, F1 save (straight to the save
  screen), F2 load, Tab preferences (difficulty), A animations, H the view back to the party; in a fight
  W wait, G guard, Q end turn; in a talk the number keys, Space to go on. The save screen's name field:
  End, then Backspace, before typing (the cursor starts at its start).
- **Resting**: only at a fire ring (the Look icon on it), or a room at an inn (Tyr's Harbinger's Roost,
  25 cp, southeast of the start). The Mines of Tyr level 1 have a fire ring in the room past exit C
  (the owner's map, 2026-11-20: by the dying miner).

**Its picture cache** (2026-11-20): the loader at 2A568h (SL's 25FA6h) keeps SL's 300 slots, 16 bytes each
(number, length, store place, memory, flags), the count at DS:265Dh, the table at load + 42A2h:0CA8h;
253 taken at the start of Tyr (`cache.py`-style dump: the count, then each slot). Its one caller is the
map things' routine (2A388h: DS:67BBh, 25h bytes a thing, up to 141h, the slot at +10h); the walls don't
come through it. `ravsites.py [NAME...]` finds SL's patch sites in the sequel by likeness (about 8 minutes
for all 454; its finds are leads to read by hand).

**Shattered Lands' figures in the sequel** (2026-11-20, logs/2026-11-20-ravager-sl-figures.md):
`darksun-recompiled/tools/sl_figures.py build SL_DIR WR_DIR OUT.GFF` writes the sequel's `OBJEX.GFF`
with the party's 14 figures taken from SL (the walking `BMP n`, the combat `CBMP n`, the script `SCMD
n`; the study is that repository's `docs/FIGURES.md`). To play it, **copy the install for real**
(`cp -a $WORK/rav $WORK/ravsl`, 287 MB): with hard links the game's writes (DARKRUN.GFF, saves)
would change the original too. Put the built file in the copy and `sh ravstart.sh $WORK/ravsl`.
Seen working: standing, walking, the swing, hits and deaths, the anchors right. **`sh ravburst.sh
NAME SECONDS X Y W H`** grabs the window as fast as `import` goes (about 15 a second) while an action
plays, and makes a sheet of 24 of them cropped to X Y W H (window pixels); look at single grabs
(`$WORK/burst/NAME-NNN.png`) round a moment at full rate. For a death on cue, set members' HP to 1
(the creature records at DS:19C9h, +0; `ravcreatures.py` lists them): a test edit, never saved.
SL's standing side frame has the legs apart: it isn't a walk frame left on screen.
**The dressed people** (`people_dress.py build`, 2026-11-21, logs/2026-11-21-ravager-dressed-people.md) are
quickest seen at the start: the blonde woman of the opening talk is picture 2426, and answer 3 brings
the Draxans' ambush, whose two Draxans are 2428 (walking, then fighting round the party). Which
regions hold which pictures: each RGN's ETAB objects (negated) through OBJEX's OJFF (+PIC).
To see a figure that stands elsewhere, build a test OBJEX with its dress put in a slot the opening
shows (dress['2428'] = dress[N]): writing the camera (DS:1408h) in a fight doesn't redraw and snaps
back, and HP 0 on the Draxans doesn't end the fight.
A **restyled creature** goes in the same way, its own chunks written over the slot's (BMP, CBMP
and SCMD of 2428 or 2426 replaced by the creature's from `restyle.py`/`loosen.py`'s `build(pic)`, then
`write_ranged` on the built OBJEX): the creature then walks the Draxans' route and fights, its own
script driving it (2026-11-22, logs/2026-11-22-restyled-creatures.md). Tyr's street is grey: a grey
creature (the soulshard) is hard to see there.
`sl_figures.py build-ui` does the same for the interface (`RESOURCE.GFF`: pictures and icons; put it
in the copy beside the patched OBJEX.GFF). Its screens in a fight: **Q** the END menu (Escape closes
it); a click on the status box (window 560,50) captures the mouse harmlessly; USE at game 22,17;
VIEW INVENTORY 74,171 on USE (47,171 opened the inventory too, not the character sheet); Escape in
the inventory closes it and USE together. The game writes its run files (DARKRUN.GFF and the like)
into the folder it runs from, so copy `__support/save`'s three files back into the copy between
runs for the same start.
`sl_figures.py regrade SL_DIR WR_DIR RGN032 STRENGTH OUT.GFF` regrades a region (Tyr is RGN032,
the opening street); put it in the copy as `RGN032.GFF`. **The sequel cycles palette entries 16-23 at
run time** (torches, fire): a colour put there shows in the game's glow colours, not the file's.
To check a colour on screen, sample the grab's pixels and match them to the region's PAL (in its
`RGNxxx.GFF`). Shattered Lands draws region N in `GPLDATA.GFF`'s PAL N (the pens, RGN29, in PAL 41).
**What's on screen where:** the camera is DS:1408h (x, y), in map pixels; the screen shows map
pixels minus the camera. The ground: **`MAP ` (or `RMAP`) is 98 rows of 128 tile numbers** (not 112 x
112), tile (c, r) at map pixel (16c, 16r); `GMAP`, the same shape, holds per-cell flags. A region's
entities (its `ETAB`, 8 bytes each: x, y, height, flags, the object negated) stand at map pixel (x, y). An object's record (`OJFF`) anchors its picture by +2 (x) and +4 (y):
the bottom centre. `sl_figures.py squash` lowers a region's structures for SL's angle.
**An exact frame from a grab:** the sequel's 320x200 frame shows in DOSBox's 640x480 window with every
pixel doubled across and rows repeated 2 or 3 times (2, 2, 3, 2, 3...), no blending: the first row of
each repeat, every other pixel, is the frame exactly, and each pixel matches a palette colour shown as
v x 4 + v / 16 (`darksun-recompiled/tools/proto/frame.py`). Sampling rows at (r + 0.5) x 2.4 instead
picks the wrong row now and then, enough to spoil tile matching. The frame isn't in guest memory as a
320x200 buffer.

**Wall shadows at run time** (2026-11-20, logs/2026-11-20-ravager-shadows.md): DSCLOG2's WALL SHADOWS
darkens the floor right of and below each wall cell (GMAP C0h, DS:0538h far, 128 a row) as the game
draws it, as DSCLOG's SHADOWS does SL's figures': site 40 at 2B81Ch (the view's floor: page, camera x,
y) and site 41 at 2B97Fh (a rectangle's: page, x0, y0, x1 + 1, y1, camera x, y), their way back made
FLOOR_POST; the page table (SL's layout) in segment load + 0BF3h, FLOOR_ON DS:29EAh, DGROUP 47E0h.
Retuned to SL's own shadows (the owner: the first try "didn't look as good"): each wall square swept
45 degrees by a full cell, so an open cell with a wall NW is all dark, W only x <= y, N only x > y;
the walk map pads each wall a cell into the room (drawn as floor), so a wall-marked cell is darkened
only when wholly in shadow. DARK was SL's tone (Lab L x 0.73, a + 11, b x 0.82), which read maroon on the sequel's grey cobbles;
the owner chose a neutral one: lightness x 0.73, a and b kept (x 0.74 a channel in 6-bit values), the
nearest of colours 32-255 (240-255 are the sequel's only greys, its ramp), made from the DAC when
the palette changes (once a second at most, not in a fade). The sequel cycles colours 1-31 (blues,
magentas, greens, flame, water, the turn marker's flash): they map to themselves and stay out of the
change check, else DARK is made again every second. `ravtone.py warm|neutral [FLAG]` swaps the tone
in guest memory (a test edit: WS_GAIN at header + 5F8Bh, WS_DAC_SUM at + 5FD1h in the 2026-11-22 build:
check the listing) for a same-view comparison. Same-view toggle: write the
header's +1872, press C then Escape (the left half redrawn). The header (signature `DSCLOGR1`) has
wall_shadows at +1872, the passes drawn at +1874, DARK's builds at +1876 (DSCLOG2's own, past DSCLOG's
header; +148 to +152 were theirs before the port's fields took them): find it in guest memory to check it ran. `RAV_LOADER=1 sh ravstart.sh FOLDER`
loads it; rebuild with `nasm -f bin -o dos/DSCLOG2.EXE dos/dsclog2.asm`.

**The figures' shadows at run time** (2026-11-26, logs/2026-11-26-ravager-figure-shadows.md): DSCLOG2's FIGURE
SHADOWS draws in the walls' floor pass. **The sequel lets a picture go from memory whenever it wants room**: a picture
cache slot (load + 42A2h:0CA8h + 16 x slot) has +0 the number, +2 the length, +6 its place in the store (XMS), +0Ah
its memory (far) and +0Eh bit 2 "in memory", which the freeing loop (2AB90h on, each through 2AD2Ah) clears; the thing
drawer (2A28Fh, SL's 25E0Ch: SI the slot, DI the thing) loads it again through 2A1F7h and draws it through `call far
1D40:3BEC` (2A347h). So a floor drawing mostly finds a figure's picture out (Tyr's street: the leader's at nearly
every one): read a picture only at the drawer's call (FIG_KEEP, site 162). The draw list's entries are SL's (8 bytes;
flag 10h not drawn, 20h placed by the entry: x less the map thing's byte +7, y less its **word** +8 and the height;
else the map thing's +3, +5); the map thing's picture slot +10h, frame +12h. Out of a fight only the leader is on the
map. `ravfig.py [0|1]` reads (or switches) the header's +1960 to +1971; a same-view toggle through VIEW_REDRAW lands a
frame late and the street's walkers move, so make the control a RAV_SKIP run (`fig_wide_all,fig_wide,fig_keep`) and
the same walk (`ravgo.py x 1180` from `ravager-after-ambush`). A throwaway copy of the sequel needs no 200 MB
`game.gog` of its own: link it to the plain install's (DOSBox only reads it).

**Dust, and the figures' shadows in a fight** (2026-11-26, logs/2026-11-26-ravager-dust.md): **Tyr's ground is
darker than SL's sand**: the dirt of the squares and yards (Shadow Square, world ~600, 1226 on, west of the ambush
street by y 1230) is colours 230, 95, 229, 228 (56,44,28 to 113,105,77 of 255), below `dust.is_ground`'s least value
0.4, and the grey cobbles have no hue: with SL's table no floor in Tyr took dust (the puffs were raised and counted,
none seen). The sequel's table (least 0.2, a step of 0.2 toward white, `ravlog.DUST_LEAST`, `DUST_LIGHTER`) takes the
dirt one or two up its ramp; 0.45 gave near-white trails. The house floors (the same browns) take it too. **The squares'
LIGHT read the palette from the wrong place** before (squares.py read LIGHT's and DAC's offsets as one pair at +1926,
SL's +236/+238 side by side; the sequel's +1928 is `square_draws`), so LIGHT was made from whatever lay at that
counter's value. **In a full fight** (the Draxans' ambush under Computer Control, four of the party and four foes,
then the bodies): 2,753 shadows cast in 586 floor passes, 1,556 of them from kept frames, 79 frames kept over the
fight (the 64 slots went round once), 2 cast from another frame of the picture and 2 none for want of one (both
before the fight, as the first frames came): 64 slots are enough for that. On the dark floors (the street's grey,
the houses' brown) the shadow is a faint darker streak, as SL's on dark ground. `ravfig.py` reads both features'
counters; find a dirt square with the area map (the game menu's maze icon, game 184,100: the brown ground west of the
grey streets). DSCLOG2 with dust: 55,072 bytes, 54,544 of upper memory, 100,912 left (its largest piece).

**Comparing two dice logs on the sequel** (2026-11-27, the pass as named steps): a second `ravdice.py` on
the same running game says nothing of the stock, the own party or the ages, which the first wrote into the
game (once a game). To compare two builds of the Loader, start the game afresh from the save for each
(`ravload.sh`, then `ravdice.py --all 25 OUT`): only the age rolls differ between runs.

**DSCLOG2's upper memory, measured for the audit's R3** (2026-11-27, claude/combined-playtest at 9c8dc0b3,
`ravload.sh ravager-after-ambush` with and without `RAV_SOUND=1`, the same both ways; the chain walked from 9FFFh):
upper memory is CA00h-EFFFh, 9,718 paragraphs past the first 9-paragraph scrap. DSCLOG2's block at CA0Ah is 4,151
paragraphs (66,416 bytes, with its PSP), the see-through figures' block at EE9Fh 352 (5,632 bytes), and **5,212
paragraphs (83,392 bytes) are free between them**. The game itself puts nothing in upper memory (no overlay or music
buffer there, unlike SL's), so DSCLOG2's limit is the 9,718 paragraphs less its own two blocks and their MCBs.

**The magic items' shine in the sequel** (2026-11-26, logs/2026-11-26-ravager-shine.md): the sequel cycles colours
1-31 in five runs (1-5 blue, 6-10 pink and violet, 11-15 green, 16-23 fire, 24-31 the water's blue-greys) with SL's
cycler (2CFDCh, 2796h:047Ch), called only from the map's loop (1CF0Eh, when byte DS:1424h is set; the main loop
clears it), so **a shop's screen stood still**, as SL's did. The shop's loop (88D52h, while byte [143Dh] is 1) and the
game's wait (its "or di,di / jz" at 2F7BEh, the jump to 2F777h) are SL's (7DDE4h, 2AFA6h). To check an icon shines,
burst-grab it (`ravburst.sh`) and count the frames its box changes in. A survey of OBJEX.GFF's magic items: an item
record (+0 its picture negated, +10h a power, +16h the plus, +14h its name, `ravitems.sequel_names`) in any RDFF,
its object's icon decoded with `sequelicons.decode` (PLNR, PLAN or SL's runs); most magic weapons have 2-8 cycled
pixels, twelve items none or one or two (`dsloader/ravshine.py`). A picture of Shattered Lands' kind put in the
copy of OBJEX.GFF for one of the sequel's own icons is drawn as its own.

**See-through figures in the sequel** (2026-11-26, logs/2026-11-26-ravager-see-through.md): `ghost_draws` (DSCLOG2's
header +1994) counts the figures drawn see-through, `ghost_on` (+1986) is 1 once the Loader has written the tables,
`ghost_seg` (+1984) the upper memory block; the STEALTH word (+204) has a bit for each party member hidden. To see
one without waiting for a thief's lucky roll, a **test edit** of STEALTH to 1 (member 0) out of a fight draws the
leader see-through at the next redraw (a step: the map isn't drawn again while nothing moves, so a write alone
changes nothing on the screen); write it back to 0 and never save. In the Draxans' ambush under Computer Control
Ar'Anda tries to hide each turn (`hides in shadows` in the dice log), but in daylight her chance is halved
(36%): one hide in the fight. **The
leader** (DS:426Dh, whose turn) is the same after every load of a save (Thy'rokh, 2, in ravager-after-ambush:
three loads); the number keys 1-4 on the map make member 0-3 the leader, so a talk's answer keys that land
on the map before the talk is up change it (the shop's prices with it: CHA 18 is 5% off). The shop's portraits
change whose inventory is shown, not the leader.

**The Loader's window on the sequel**: `apt-get install -y python3-tk`, Xvfb `:56` 1440x900 (`:55` is
smaller than the window), `python3.12 -m dsloader view --pid $(cat $WORK/rav.pid)` from `obsidian-edition/`;
stop `ravdice.py` first and the window (by pid) before running it again (the game's lock). Its party tabs
use the sequel's layout made from SL's. No moment out of a fight at the start: the opening talk ends in
the ambush, so the inventory screen (to check the gear's slot names) waits for a later save.

**Its first fight** (logs/2026-11-19-ravager-fight.md): the opening talk (3, Return) ends in the
Draxans' ambush, a fight at once; in a fight USE opens for the one whose turn it is (DS:426Dh, SL's
4979h). Right clicks on bare floor cycle the pointer: arrow, sword, look (the mode at DS:1440h: 1 the arrow; a talk's end sets it back to the arrow, and the arrow keys walk only with the arrow); a figure under it turns
red; a look opens a box (name, level, weapons) that a click on it closes. Creature records: 31h
bytes at the far pointer DS:19C9h, +0 HP, the region's people all listed (`ravcreatures.py`).
`ravds.py HEX` finds the WotR address of an SL data-segment offset by the code before its uses.
Of the opening party's spells only Chill Touch is a fixed one (Ar'anda's); its aimed click wasn't
taken on a Draxan 1.5 squares off (a touch spell: too far, likely).

**Fights and spells, for a test** (logs/2026-11-19-ravager-scare.md): the manual's hot keys: **Q**
brings the END menu (**E** in it is END TURN), C the cast screen, G guard, W wait, N/P the next or
previous foe, 1-4 the leader; Esc with nothing up quits. `ravfight.py until N` ends the others' turns
until member N's (the order varies run to run). A caster hit this round has every icon crossed out.
**Spells known**: a 15-byte bitset a member (bit n, spell n; wizard spells only), the roster's `SPST`
chunk; Ar'anda's at 3F3DCh after START GAME (a set bit is offered on USE at once: a test edit, never
saved). An area spell's reach shows as a ring of dots round the aim (on bare floor or a foe, not on a
party figure). A creature record's +18h is 60h while Afraid. **Spell slots**: DS:446Ah + 22h a
member, wizard casts left by level, the priest's 0Bh on: a cast went off if its level's count
dropped (logs/2026-11-19-ravager-cant-save.md). **A creature's level** for the saves (1987:154 in
build_image's image): a human's first level (sheet +1Eh), else the best of its class levels. In the
file, an overlay's far call names an overlay-manager selector (98h), not a segment: follow it in
the image.

**Its spells, and the fixes carried over** (2026-11-19, logs/2026-11-19-ravager-fixes.md): no
spell table in its program; each spell is `RESOURCE.GFF`'s `DATA` 0-319, 73 bytes (SL's 32-byte
record, then the name and an 8-letter short name), read one at a time as the spell is used
(choosing Bless on USE loaded `DATA` 115 whole; nothing else held). In Tyr: Return pages a talk,
the number keys pick a reply, the top-left icon opens USE, a right click cancels a spell's aim.
**`ravfixes.py [OUT]`** makes a copy of the sequel (`$WORK/ravfix`) with the mod's fixes that
carry over unchanged: five of the program's at their twins' offsets, the spell records' by name.

**Its USE screen and spell slots** (2026-11-20, logs/2026-11-20-ravager-use-slots.md): SL's code at other
addresses: the LEVEL button labelled at 7950Dh (its "add sp,0Ch" 79543h), a window brought to the front
ending 303BEh; the window on show DS:1431h (SL's 11A4h), the level on show DS:43ECh, the list a byte a
member DS:43E8h (1 MAGE, 2 CLERIC, 3 PSIONIC), the character on show selector 370h:0B44h (load + 3E71h), the
USE screen's window selector 4D8h:0 (load + 45C9h), the text routine 301Bh:172h (SL's 2B7Ah:16Dh, its one
far caller 221E3h). **The slot routine** is 626B7h (SL's 5E0ACh): the same but for its test switch (a byte,
DS:13F8h) and which classes cast, asked of 62B45h (spell, class): wizard spells classes 11 and 18, priest
spells by a jump table of spheres (1-8, 13-16, and 19 all of them; the spheres a byte a spell at selector
3D0h:7D3h, load + 41F1h). **Finding a far data address**: SL's selector (the segment table at load +
4137h, + the selector; the sequel's at load + 45E8h) and the code using it, then the same code in the
sequel (`b8 SEL 8e c0 26 ...`). **On USE out of a fight**: MAKE <NAME> LEADER (the small top button left of a
portrait) doesn't change whose spells show, but a click on that portrait then does; a spell is cast by
clicking its icon (it hangs on the pointer) and then the target's portrait. The roost's second doorway's
steps were at game (253, 90) in one run (the view differs from run to run): look at a grab first.

**Its items and item boxes** (2026-11-20, logs/2026-11-20-ravager-item-box.md): an item record (17h bytes,
DS:19C1h) keeps SL's fields to +0Eh (the charges, read as a word), then **the power, spell + 1, a word at
+10h** (SL's byte at +0Fh; +0Fh unused), then SL's +10h on two bytes later (the slot +13h, the name +14h, the
plus +16h). Counting each field's uses in the two programs (the code `imul ..,15h/17h; les bx,[items];
add bx,..; <op> es:[bx+N]`) matches the fields where a running game has nothing to show. The item box
routine ends at 9A4FEh (SL's 8C1A1h); the box has an INFO button at the right of its last row, so a line
drawn there must stay short. **Opening a box**: I (inventory), a portrait on the left for the member, a
right click on the item (Ar'anda's left hand at game 174,92, chest 174,67); a second right click closes
it. The material to-hit routine is 1D401h (SL's 5EB31h), the same table.

**Its inventory panel** (2026-11-20, logs/2026-11-20-ravager-inventory.md): SL's code at the same
distances, ending the weapon lines at 91286h (SL's 6F6BFh); the thief tables at load + 449Bh (race rows
from +8, DEX's low/high/top at +A0h/+A8h/+B0h, the armour penalty +B8h), the DEX reaction and defence
tables at DS:084Ch and DS:0866h. The thief routine (8C647h) gets DEX and the level from functions; for a
check run `ravthief.py MEMBER` (it needs `ravfixes.py` run first, for `$WORK/ravfix`). **Reading the
panel's numbers**: zoom the screenshot, the small font's 6 looks like a 5. Portraits are at game x 30,
y 21, 67, 112 and 158.

**Its View Character screen** (2026-11-21, logs/2026-11-21-ravager-view-character.md): SL's screen and
code, ending its panels at 987FBh (SL's 8A471h), the text routine, window and character at SL's distances
(-1A9h, -1B4h, -19Bh); the creature's movement +13h. The game's text routine changes ES: read what you
need before drawing. Opened by the bar's top-left icon (22,17), then VIEW CHARACTER (47,171).

**Its creation screen** (2026-11-21, logs/2026-11-21-ravager-creation.md): SL's code and boxes (DS:11F4h
on, the hit points' DS:1224h); the sheet, creature and window at DS:1429h, 142Dh, 1431h (SL's 119Ch,
11A0h, 11A4h); the creature's THAC0 (+16h) follows the classes as they change; the hit points drawn by
6C87Bh, PSP after them (6D6AEh, 6B79Ch); the labels' ink DS:2D14h, F0h white there. Title menu's CREATE
CHARACTERS (160,92), right-click a slot (70,56), NEW (110,57); EXIT (280,160).

**Its creation screen's clicks** (2026-11-22, logs/2026-11-22-ravager-rolled.md): after `ravcreation.sh`, a score
answers a click on its number (`ravclick.py 40 Y`, Y 140, 147, 154, 161, 168, 175 for STR to CHR; left +1,
right -1, going round past the least and most), the hit points on the line below their numbers (`ravclick.py
100 176`). The screen's numbers: the creature being made DS:142Dh (scores +19h), the sheet DS:1429h (hit
points +8), the least and most score DS:42D4h and 42D2h, the hit points' most and least DS:42D6h, 42D8h.

**Its rules and hit dice** (2026-11-21, logs/2026-11-21-ravager-hit-dice.md): DSCLOG2's header has
DSCLOG's RULES (+170) and RULES_HI (+270), written by the Loader with only ravager.RULES_PORTED; a
dice log started without settings (`ravdice.py`) writes 0. The hit-die rolls: 9501Dh (94F60h's: creation's
die and the level-up from XP, called from 9574Bh), into the sheet's +0Ah, the class table's +38h by CON
a floor; and 95CCEh, a level lost (the XP set lower, the rolls taken off). The most hit points from
+0Ah: 95193h (SL's 874B0h), which the sequel calls only in the level-up (957E0h): creation's fix,
logs/2026-11-21-ravager-creation-hp.md.

**Its item types are OBJEX.GFF's ALL 4** (2026-11-22, logs/2026-11-22-ravager-item-types.md): 102 types,
read into memory at the chunk's own length, so a longer chunk adds types (the Loader's OBJEX2.GFF adds the
mod's 33 as 102-134). A test edit of an item's type (the word at item +0Ah, items from DS:19C1h) shows in
the item box at once (material and dice).
Its item names (RESOURCE.GFF's TEXT 1000, 255 lines; an item's +14h word) can't be added to by
lines: 4 more broke the inventory screen (wrong items shown, AC -12), with a control: the lines
run past the game's table of 256 far pointers (DS:56F3h). DSCLOG2's SITE_NAME at the table's 7 reads gives
names 256-415 from its ITEM_NAMES, which the Loader writes as it attaches (logs/2026-11-22-ravager-item-names.md).

**Its item types and helms** (2026-11-21, logs/2026-11-21-ravager-helms.md): the types' table at DS:19CDh,
15 bytes a type (AC +0Eh, 80h at +0Bh counts for AC, slot +05h); the items' types and names can be listed
from OBJEX.GFF's RDFF records (kind 1, 17h bytes, as in memory) without a save that has them. Helms: type
55 (AC 0, hats too) and 56 (AC 1). The AC function's worn list is at [BP-324h], 10 bytes an entry.

**Its two weapons** (2026-11-21, logs/2026-11-21-ravager-two-weapons.md): SL's two-weapon routine at
5DE34h (called from the attack, 5C78Ch: [BP+6] the weapons ready, [BP+8] the combatant, [BP+0Ah] the
item; the ranger test on the sheet's +10h 200h), the attacks a round stored at 5CEE8h ([BP-0Ah]; the
attack's item [BP+12h], range [BP+16h]). A creature's item lists (+8, +0Ah, +0Ch) are things in the
combatants' table numbered from 201h for the party, not below 400. Computer Control in a fight: C, then
the lower small icon left of each character box (game 47,53 / 98,53 / 47,113 / 98,113).

**Its inventory's two hands** (2026-11-21, logs/2026-11-21-ravager-half-giant.md): the routine that
puts an item in a hand at 7761Bh (SL's), the character on show at (load + 3E71h):0B44h, an item type's
two-handed bit +0Bh 40h (SL's +0Fh), tested at 77976h (the other hand's: "Two handed weapon in use") and
77A0Dh (the new one's: "Need two free hands"). The far "has effect" routine 608h:20h and "take it off"
608h:4Dh (SL's 598:20, 598:4D; the bytes in a call are `08 06`).

**Its weapons and the attack's frame** (2026-11-21, logs/2026-11-21-ravager-cahulaks.md): from
OBJEX.GFF's items, Cahulaks 24, Double Spear 39, Gythka 52, Polearm 80, Sling 93, Staff Sling 98,
Trikal 100. The attack routine's frame: [BP-0Ah] the round's swings, [BP-16h] the swing, [BP+12h] the
item, [BP+14h] its type, [BP+16h] the range, [BP+18h] the attacker, [BP+0Ah] - [BP+0Ch] what the d20
must reach; each swing starts at 5D052h; a hit's damage done at 5D1FEh ("mov byte [bp-19h],0").

**Its far calls and stubs** (2026-11-21, logs/2026-11-21-ravager-stinkpots.md): a far call names a
selector (388h, 598h, 608h...), a row of the word table at file 4B080h, 8 bytes a selector, its first
word the segment less the load (388h: 3F49h, 598h: 46A7h, 608h: 473Bh, 628h: 475Ah). Overlay routines
are reached through a stub segment in the root (`CD 3F 00 00`, the overlay's place from file 57580h as a
dword, its size; then 5 bytes an entry from +20h: `CD 3F` and the routine's offset). The saving throw
66D26h is 598h:75h (target, thrower, power, level; AL 0 failed), the damage resistance 85052h 628h:25h,
the effect adder 7F9E6h 608h:3Eh (target, thrower, spell, effect, a dword time: seconds a timer, negative
charges; a last byte). DSCLOG2 calls them as DS + (segment - 47E0h) : entry. The effects' records (31
bytes: name, icon ICON 21000 + spell) have two empty ones, 12 (now Nauseated) and 88. **To throw by
hand in a fight**: walk two squares off, one right-click (the sword), hover a foe until red shows under
it (yellow is a friend), mousedown / mouseup. Web from the Draxans gives a webbed member an END menu and
turns its Computer Control off: E ends it; taking effect 66 off the party in memory keeps the fight going.

**Its distance routine** (2026-11-21, logs/2026-11-21-ravager-reach.md): 1D40:35EFh (file 25BEFh),
[BP+6] and [BP+8] two combatants, the squares between in [BP-1Ch] at its end (25CDDh); its melee
callers' ways back 20617h (the sword pointer), 1EADCh (the attack click), 1E2AAh (the walk arrow on a
foe), 1FF39h and 260CBh (the walk to attack), 2420Ah (the step switch), and the combat overlay's IP
14A2h and 1A72h (the computer's). The line test 0B0Bh:00A4h (10354h); the map things' feet DS:67C5h.
The pointer cycles on a right-click (walk arrow, sword, eye); "no" on the floor in sword mode is
normal. **To place a figure for a test**: move its map thing's top left (+3/+5) and feet (+0Ah/+0Ch,
sixteenths of a square, `shr 4` the square) by the same amount; the game draws it there at its next
redraw and its distance and line tests use the new place (logs/2026-11-21-ravager-reach.md). The
game's dice for each item type: +08h the sides, +09h the count, +0Ah the bonus (signed). A creature's item lists are things 201h and on in the combatants' table.

**Creature size in it** (2026-11-21, logs/2026-11-21-ravager-size.md): the swing's dice at [BP-10h]
count, [BP-12h] sides, [BP-14h] bonus; the call's first swing [BP-0Ch]. The Draxans are people (race
1 to 8), so medium; the Giant Skeletons up the street are large. A spell test: aim Hold Person with
`ravclick.py X Y none` until red shows under the pointer (yellow is the pointer itself), then mousedown
/ mouseup; a right-click on bare floor drops the pointer and ends the turn. To make a medium foe large
for a test, patch `sizes.large_by_table` in the dice log's own process (RAV_NAMES alone won't do for a
people: its race wins).

**Its Look box and damage resistance** (2026-11-21, logs/2026-11-21-ravager-look.md): the box's
routine at 640FBh (the combatant in DI, the lines' count [BP-0Ah], the text routine -20h); its damage
resistance (85052h) by a class byte at the creature's +0Fh, the classes' immune kinds at DS:2588h (18
words; weapon kinds only below the magic bits B000h) and halved kinds at DS:25ACh (7). To Look in a
fight: right-click to the eye (arrow, sword, eye) and a slow press on the figure.

**Its map and names over figures** (2026-11-21, logs/2026-11-21-ravager-labels.md): the map things
from DS:67BBh, 25h bytes each, their feet at +0Ah/+0Ch (`ravfight.py`'s +3/+5 is the top left, about 30
above); the object list's far pointer DS:67B7h (8 bytes an entry, +6 the thing), its count DS:264Eh;
the view DS:1408h/140Ah; DS:0DABh 1 on the map. The view's rectangle routine 21E0:128Ch (SL's
1DF3:142Fh), the cast routine 80580h, the main loop's pointer call 20230h, the timer 3DA2Ch. **To catch
a label**: capture frames (`import` every 0.2-0.4 s) during `ravfight.py fight` or a cast, then look for
the label's ink in them (a Miss is about RGB 239,239,223, a spell's name 251,223,93) rather than by eye.
A label written by a script of its own stays until cleared (its byte +0 zeroed): only the dice log
ticks them off.

**Choosing an enemy, the ring, the pointer** (2026-11-25, logs/2026-11-25-ravager-tab-target.md): the
routine lighting the thing under the pointer is 21060h (SL's 1E126h; found by its pushes of the pointer
DS:A109h and the view DS:140Ah/1408h before the finder's far call), keeping that thing in **DS:0DADh**
(SL's 0BCBh; FFFFh none) beside DS:0DABh (1 on the map); the finder is 21E0:2DBD (file **29DBDh**, SL's
25B52h: "push bp / mov bp,sp / sub sp,0Eh", DSCLOG2's site 77 there), reading a map thing's flags +0
(10h drawn), left +3, top +5, rise +0Eh, picture +10h, width +13h and height +14h (unsigned bytes). The
pointer's mode is **DS:1440h** (1 walk, 2 look, 4 attack; the routine setting it 2037Bh, SL's 11B8h), the
facing byte a creature at +5Eh of the round's segment (load + 3C4Fh; SL's +5Bh), the eight directions'
flag a byte at DS:0442h (the direction routine 1109Dh, SL's word DS:01F8h). `ravtab.py` prints DSCLOG2's
Tab words and these; `ravtab.py feet` each combatant's feet and screen place. **Clicks** reach the game
through the handler it sets with INT 33h 0Ch (its mouse routines at 35B9:0000 on: 35B9:0034 is INT 33h 3,
the pointer's place for edge scrolling only; the button bits it returns aren't the clicks): to give the game
a click, find that handler (INT 33h 14h, swapped and given back) and call it with event 2 then 4 (DSCLOG2's
TARGET_MOUSE). **Tab** without the Loader opens the game's own menu (the save/load/options panel), with the
Loader on a party member's turn in a fight it is the Loader's. **A DSCLOG2 routine must go above
RESIDENT_END**: code after it is freed as the helper goes resident, and the next allocation writes over it
(the upper memory chain "broken" just past DSCLOG2's block in `dosmem.py`; it ran by luck until then). **DSCLOG2's room** (2026-11-27, claude/dsclog2-segment-room): the helper is three parts, the segment
(CS: the header and the code, to IMAGE_END, under 64 KB), the tail (TAIL_PARAS on: tables and buffers, read
through FS = CS + TAIL_PARAS, `TAIL_FS`; the Loader at the header's +1834 x 16 + the buffer's word) and the
install (INSTALL_PARAS on, the EXE header's CS:IP, freed). With #218-#223 joined the segment had reached
FF1Fh and the install wrapped past FFFFh (nasm's "word data exceeds bounds"); now `test_dsclog2_room.py`
fails on a warning or under 2 KB free, and names a tail label read through `cs:`. In memory (`dosmem.py`
after `RAV_LOADER=1 RAV_UMB=1 sh ravstart.sh`) the helper's block is the segment and the tail together
(10h + KEPT_PARAS paragraphs with its PSP). To read a tail table: the header's +1836 x 16 past the image, or +1834 x 16 in the
running game; `ravtail.py` checks the tail in play (logs/2026-11-27-dsclog2-segment-room.md: with #218-#223
joined, 84,160 bytes of upper memory free, the helper's block 65,792 with its PSP). Details: DEVELOPMENT-INTERNALS.md, DSCLOG2's segment,
tail and install.
**The view to the chosen enemy, and a monster's gear before it fights** (2026-11-25,
logs/2026-11-25-ravager-tab-followups.md): the sequel's centring routine 1C5F:01F3 (file 219E3h; x, y the
view's middle, then 1 to draw) sets the view's top left to (x - 160, y - 100) rounded down to 8 and keeps it
inside the map's limits itself (DS:14D7h, 14D9h the least, 14DBh, 14DDh the most, right and bottom edges), so
DSCLOG2's PAN_TICK (PROBE_SCROLL's, DSCLOG's PAN_X/PAN_Y at +230/+232) only adds the Loader's pixels to the
view and calls it; `ravtab.py` prints PAN and `pan_moves`. **To scroll the view off a fight's figures for a
test**: `ravclick.py 319 100 none`, then `xdotool mousemove_relative -- 20 0` a few times (the game's edge
scrolling: about 500 pixels in 3 s); `ravclick.py 160 100 none` stops it. **A monster's items are unplaced
until it first fights**: their slot bytes (item +13h) run 14, 15, ... in list order (a Draxan's brigandine in
14-16, its weapons in 17-19); by its first attacker's swing the game has put them on (chest 9, legs 6, arm 0,
right hand 3, missile 2, ammo 1), and the AC routine weighs them so. The Draxans are gladiators of level 8
(sheet flags 40h, class 10): AC 1 better in armour, which the Loader's armour_worn (by the slots) missed
before their first fight (`game.armour_ready`). `ravdice.py` with `RAV_PREDICT=1` takes a Tab line's chance
apart; `RAV_NO_PAN=1` is the control for the view. Enter on an enemy out of reach (in a room behind the
doorway) gives the click and the game does nothing. **The sequel's sides** (the creature's +15h): an index into
bit masks, not SL's "same or not": the game colours the figure under the pointer as a foe when `1 << side` is in
**0F80h** (sides 7-11; 21112h: "shl ax,cl / test ax,0F80h", then side 1 another colour), and its combat code
tests them too (near 5B649h "test ax,0F80h" and "test ax,0C58h"; at 5C29Dh and 8664Eh a mask of 0F80h made for
side 0, the party's; at 5F027h 71h).
In the Tyr ambush the party is 0, the four ambushing Draxans 7, and everyone else on the map 1 (the Caravan
Master, Notaku, Templar, Boric, the soldiers, the pedestrians, the Giant Skeletons up the street, other
Draxans): SL's rule (another side than the leader's, not 4) made 31 of them foes for Tab; `rings.HOSTILE_SIDES`
(0F80h, set by ravlog) makes 4. `ravtab.py sides` lists every combatant's side through the dice log's reading
and Tab's list both ways; `ravdice.py` with `RAV_FOES_SL=1` is the control.

**Its combat log's panel** (2026-11-21, logs/2026-11-21-ravager-combat-log.md): the fight flag is a
byte at DS:13FAh, the fight's state 3C10h:19h, the clock DS:9C0Ah (scale) and DS:9C0Ch (far pointer);
the flip 16974h (pages segment 0BF3h, [118Eh]), the pointer routine 2D72:0942 and its DS:332Ch, A10Dh,
A115h, A155h, 3330h, 33B6h, 33B8h; the view centred again by 1C5F:01F3. The view moves by that routine (its end 21A5Ah) or by following
a figure (262C:0D80 given CAM_X/CAM_Y's addresses, then drawn by 262C:06C4: calls at 1E3E7h, 2018Eh,
21439h); the game's drawing scrolls the screen, panel and all, so DSCLOG2 draws the view again after
each (INT D7h, D8h). The interface's blue-greys are palette 232 to 239 (combatlog.LAST 253). To count
copies: `import -window` in a loop (about 20 frames a second), the well colour (56,56,77) outside the
panel. **To play with it**:
`ravdice.py` running, L on the map (the dice log starts with the panel closed); the collapsed panel's
line sits at game y about 190. A copy of the panel after a scroll lasts one frame: check by frames
(`import` every 0.4 s) for the panel's well colour left of x 134.

**The panel's copies in Shattered Lands** (2026-11-27, logs/2026-11-27-panel-scroll-autosave.md): `framegrab.sh
DIR SECONDS` in the background while `untilturn.sh` plays, then `panelcopies.py DIR` counts the frames with the
panel's colours left of or above it and their runs. The game's moves of the view: following a figure (2191:0BE3
writes CAM_X/CAM_Y, 2191:0648 draws, from 1B278h, 1CA32h, 1E439h) and centring (191F:01FF on a thing, 191F:0281
on (x, y)); 2191:0648 scrolls when the view moved 40h or less. Redrawing the whole view after a move leaves the
copy up as long as before (the top is drawn first): draw again only where the copy went.

**Its transfer program, CHARTRAN.EXE** (2026-11-19; the study in
[reports/wake-of-the-ravager.md](../reports/wake-of-the-ravager.md)): `sh chartran.sh SAVE.SAV OUTDIR
DEBUG` runs it in a headless DOSBox of its own (its own config: `C:\DSUN` holds the save as
SAVE01.SAV, `C:\RAVAGER` CHARTRAN, `ITEMS.BIN`, `OBJEX.GFF` and the install's roster from
`__support/save`), types Enter (the paths screen) and A (the one save), and leaves the roster it
wrote in `OUTDIR/C/RAVAGER/CHARSAVE.GFF`; 15 seconds, no Loader, no lock. Its screen goes to
`OUT.TXT` (the command line redirects it). `DEBUG` on its command line writes `DEBUG.DAT`: each item
`OLD: -<SL object>, NEW: <WotR object>` (900: a money bag, for anything not in `ITEMS.BIN`'s 234
pairs of words, so every mod item) and each spell or psionic aptitude it couldn't carry.
The party goes into free `CHAR` slots (32-35 of the install's roster, their `CACT` set from 0 to
the entity's number). A `CHAR` record: the creature record at `+0Ah` (name `+2Bh`), the sheet at
`+45h`, SL's sheet less `+0Eh`-`+0Fh`, `+14h`-`+17h` (the mod's weapon specs: lost) and `+3Ch`; SL's
`+43h` (the mod's kit byte) lands at `+3Dh` and `+45h` (second sphere) at `+3Fh`. **Wrong, found
2026-11-24:** those are the high bytes of two WORDS the sequel reads whole, `+3Ch` and `+3Eh` (`mov
dx,[es:bx+3Ch]` at 6012Ah, overlaid, and `mov ax,[es:bx+3Eh]` at 89859h, after `imul 42h` and `les
bx,[19C5h]`): sound numbers played at a member's turn in a fight (0: the default, 62h), through
B8:0A22h. A kit made the sound 100h or 8100h, the sound manager stopped the game ("Mel Fatal Error",
through 39DEFh, then exit to DOS: the "crash" of the transferred party's Tyr fights, about 1 in 4, on
the druid Ester's turn). For a while the Loader's transfer left both bytes 0; tried on the user's
saves `selling-junk-user`, `trap-user` and `rest-no-call-user`: all transferred. **Now (2026-11-24,
`claude/ravager-sheet-room`)** the bytes stay (as CHARTRAN copies them) and DSUNLOG2 reads the words'
low bytes alone, in place, no helper code (`ravager.PATCHES` `sound_3c` at file 65333h, `sound_3e` at
8EA59h: `xor ax,ax / or al,es:[bx+N]`, then the game's own move, ZF as before). Every decode of the
whole program (each start offset, capstone) with a displacement 3Ch-3Fh on an ES base: only those
two words and two byte reads of `+3Ch` (8ACB7h, 8ADA5h image), none of `+3Dh`/`+3Fh`; the sheet's
42h-byte copies (CHARSAVE's load and save, 6950Bh/69C67h/6B17Ch: a GFF call of 42h) copy whole;
DSCLOG2 reads none of them. ravlog's layout reads the kit (`KIT_SHEET`, `kitpages.KIT_BYTE`) at `+3Dh`
and the second sphere and new spells (`NEW_KNOWN_SHEET`, `kits.SPHERE2`, `NEW_KNOWN`) at `+3Fh`;
kitpages and kits read race, classes and levels by `game.SHEET_*`. Only verified statically: a
transferred party with kits must play the Tyr fight with no quit and its turn sounds still heard.

**The starting age's roll in the sequel** (2026-11-24; **replaced the same day** by the 48h sheet below: the roll is on the sheet again, the transfer's SPST CHARTRAN's 9 bytes, `known_roll` and `start_roll` gone): the known wizard spells are 15 bytes a member
at selector 320h:39Ch (load + 3D62h); the game's loops and tests stop at bit 114 (`cmp ...,73h`:
19CFAh, 5D425h, 6990Fh, 8F8A5h image; its scrolls' spells are 1-112, its priest scrolls' 236 and up
take another branch at 947EEh, `cmp [bp-4],0EBh`), so bits 115-119 are free: the roll + 1 there
(`ravager.known_roll`, 0 none: the install's characters' SPST are 15 zero bytes), written by the
Loader's transfer (a 15-byte SPST; CHARTRAN's is 9). The roster's load (6A782h image, `128h:4ABh` =
29497h, GFF read with length -1: the chunk's own) reads the chunk whole; its save (6A6B6h) writes 15;
a save game keeps the 60-byte table (SAVE 20). Nothing writes bits 115-119, and nothing clears them:
a character made in a slot keeps the slot's (creation clears 0-114 only), and a 9-byte SPST leaves
bytes 9-14 as they were. `RavGameData.start_roll(member)` reads it.

**Room for the weapon specs in the sequel's sheet** (2026-11-24, static, not built): the specs need 17
bits (four base-17 digits, filled in order, repeats possible), 22 with the roll. Bytes 0 in every sheet
of CHARSAVE.GFF and SAVE01's chunk 6: 03, 07, 09, 0B, 0D (high bytes of XP, the +4 XP cap, max HP, HP
rolled, max PSP: all can grow there), 23, 26, 29, 2C, 2F (a third class, a second natural attack's
fields), 37 (footprint), 3D, 3F, 40, 41. Found clean:
- **`+36h`, 8 bits, no site at all.** It is SL's `+3Ch`, the default side SL copies into the creature's
  `+1Dh` (SL 7340Eh, `cmp byte [es:bx+3Ch],2` at 73685h); the sequel dropped that code: no
  instruction reads or writes the sheet's `+36h` (every decode with displacement 36h on an ES base:
  only another record's, `[3411h]`). The sequel's scripts have no GPLX (SL's table of object field
  offsets, loaded to DS:4D7Ah at SL 65027h: its sheet fields +18h-+46h): its GPLDATA.GFF has none, the
  program loads none, and no table of sheet offsets is in the program; so its fields are compiled code,
  all in the scan. The game's own sheets hold 0, 1, 4, 7 there (SSI's data, inert): a reader needs a
  marker to tell a transferred member's bits from those.
- **`+40h`'s high nibble, 4 bits, 2 patches.** `+40h` (SL's `+46h`) is read twice as an index 1-8 into
  the table at 410h:3 (5A24Ah: `mov al / mov ah,0 / mov di,ax / or di,di / jg`; 82400h: `... / mov
  [bp-6],ax / cmp word [bp-6],0 / jg`), never written; same-length rewrites `mov ax,es:[bx+40h] / and
  ax,0Fh` then the move (flags from the AND, OF 0 for the jg) keep the game's nibble.
That is 12. Five more clean bits are only in the mod's own bytes: `+3Fh`'s new-spell bits (08h-80h:
Cat's Grace, Erdlu Claw, Fogbolt, Reflect, Spook, spells the sequel hasn't) and `+3Dh`'s Friends bit
(80h) as the marker: 8 + 4 + 5 + 1 = 18, the new spells known not carried. Everything else costs
dozens of sites (abilities, levels, saves: top bits) or can overflow (the words' high bytes).

**A bigger sheet in the sequel (42h to 48h)?** (2026-11-24, static study; **built** after it, next paragraph.) What depends
on the size: **386** `imul r,r,42h` (`6B xx 42`), every one followed within four instructions by a load
of the sheets' pointer [19C5h]/[19C7h], so all sheets, root and overlays alike (the overlays load from
the file, so file patches reach them); each a one-byte change of the immediate. Besides: one stride,
`add di,42h` at 1C57Bh (a loop over the party's four); the table's allocation, `1D0h:8` with dword
462h (6DE4Dh: 17 sheets x 42h, at [19C5h], far heap, freed at 6E0D5h), +102 bytes; the save game's
chunk sizes, a dword table at selector 378h:0 (file 3F38h x 16 + 5200h; SAVE 6's 462h, 5th entry); the
CHARSAVE record copies of 42h (`push 42h` to the GFF calls at 6950Bh, 69560h, 69C67h, 6B17Ch); no
`shl 6` or word-immediate forms found near a sheet load. DSCLOG2: 23 uses of SHEET_SIZE/CU_SHEET_SIZE/42h
(one constant); the Loader: ravager.SHEET_SIZE, ravtransfer.SHEET, ravlog's profile, the tests. So the
program's patches are about 395, all mechanical and checkable by a scan (every `imul 42h` before a
19C5h load patched, none left). **The cost is compatibility**: a save's SAVE 6 is read whole (length
-1) into the table, so an old save's 17 x 42h would land misaligned, and an old CHARSAVE record (42h,
CHARTRAN's too) read as 48h overruns; both need converting (by the Loader on the files, or a DSCLOG2
hook after the load), and every save and roster written by the patched game is unreadable by the game
started by itself (and by CHARTRAN's world). Monster sheets copied in at 42h would leave the 6 new
bytes stale from the slot's last owner unless cleared. **Verdict: feasible, not recommended for 17-22
bits**: the in-place room above (+36h, +40h's nibble, the mod's spell bits) gives 18 bits with 2
patches and no file format change; a bigger sheet is worth it only if the mod needs many more bytes
later. Verifying it would take a unicorn test per patch shape, a scan test for leftover 42h strides,
and play of create, ADD, save, load (old and new saves), level up, a fight and a talk.

**The 48h sheet, built** (2026-11-24, `claude/ravager-sheet-room`; played the same day, below): `ravager.SHEET_SIZE` 48h (`GAME_SHEET_SIZE` 42h). +42h..+44h hold SL's +14h..+16h as
`game.packed_specs` packs them (specs base 17, the roll, the flag bits; ravlog's `SPEC_SLOTS` 42h,
`sheet_field` 14h-16h -> 42h-44h), +45h..+47h spare (0); the age stays at +41h. **392 patches**
(`ravager.PATCHES`, each checking its original bytes): the 386 strides `sheet_stride_*`
(`SHEET_STRIDES_AX`/`_DX`, file offsets: 350 `imul ax,ax,42h`, 36 `imul dx,dx,42h`, no overlap with an
earlier patch); `sheet_party_loop` (`add di,42h`, 1C57Bh image); `sheet_table` (6DE4Dh, 17 x 48h);
`sheet_record_size` (6DD62h: the record-size table 6D0h:6169h + 2 x (kind - 1), sheets' 616Dh: the
record writer 1F6BDh and the generic accessors AA46h, AB66h, AC46h, 1E259h, 1F6AEh use it);
`sheet_record_load` (6B17Ch `push 42h`, memcpy of a sheet record's data into its slot: an ADD from the
roster, a map's monsters from OBJEX's RDFF); `sheet_save_size` (SAVE 6's dword in the table at 378h:0,
file 44594h); `sheet_new_tail` (site 50, below). **Kept 42h**: the creation screen's template copies
6950Bh (template -> sheet [112Eh], an edit), 69560h (template -> new sheet) and 69C67h (sheet, a far
argument, -> template): the template at 360h:29h is 42h bytes with the creature's at 360h:6Bh right
after it, so an edit leaves +42h..+47h as they were; a new character's six would be the slot's last
owner's, so DSCLOG2's `NEW_SHEET` (site 50) replaces the `add sp,0Ah` after 69560h's memcpy (6957Dh),
clears dst+42h..+47h and does the ADD SP by moving its IRET frame and BP up 10. The other `push 42h`s
(608A3h, 60FDAh, 7D14Ah, 80D19h...) are effect or text numbers, not sizes. DSCLOG2: `SHEET_SIZE` 48h,
`CU_SHEET_SIZE` its alias, the one literal 42h stride (STEALTH's, line 472) by name. **Files**: kind-3
records are always sheets (42h, level 3) in the sequel's OBJEX.GFF (352, RDFF) and CHARSAVE.GFF (19,
CHAR); no RGN or other file has any. `objects_fixed` widens OBJEX2's (`wide_sheets`), and
`ravager.widen_files(game_dir)` (launch's `_launch_wotr` after prepare, and `ravstart.sh` with
RAV_LOADER) widens CHARSAVE.GFF, DARKRUN.GFF, DARKSAVE.GFF and SAVEnn.SAV: CHAR/RDFF sheet records 42h
-> 48h, SAVE 6 462h -> 4C8h (17 sheets), each by length (idempotent; a roster with the transfer's 48h
beside CHARTRAN's 42h is made one), the file copied first to NAME.42H. `python -m dsloader.ravager
narrow FOLDER` does the reverse (NAME.48H backups) for the game started by itself. Not prepare: the
tests run it on the player's own folder. Tests: `tests/test_ravsheet.py` (each patch shape run, the
patched program scanned: no `6B /r 42` before a [19C5h]/[19C7h] load, no `push 42h` memcpy but the
template's three, NEW_SHEET run, widen/narrow round trips on the install's roster and save). **To
play**: create a character (its +42h..+47h 0), ADD (old and transferred), save and load (an old save
widened, a new one), level up, a fight, a talk, the dice log reading the transferred party's specs;
playtest tools that index sheets (ravhold.sh, ravscare.sh, ravknow.py) take 48h with RAV_LOADER.
**Played** (2026-11-24, logs/2026-11-24-ravager-48h-sheet-play.md): all nine checks passed. Read the table
at far DS:19C5h in steps of 48h. On CREATE CHARACTERS the creation sheet (far DS:1429h) is table slot 0 until
NEW, then the template (360h:29h, its "+42h" the creature's bytes). Bytes put in a slot's +42h..+47h
before NEW were 0 after it, and an EDIT kept them. The dice log reads the transferred specs, rolls and ages
through `ravlog.apply_layout()` (`game.spec_kinds`, `game.sheet_roll`, `aging.age_of`). No spec bonus shows
in an attack: weapon specialization isn't a ported rule (`RULE_SPECIALIZE` not in `RULES_PORTED`). The
game writes DARKRUN.GFF as it plays, with the region's sheets in it (48h, so `narrow` changes it too).
**The TOC the Loader writes**: SSI's GFF TOC is the type table, then a word count of free holes where its
second dword says, then 8 bytes a hole (the TOC's length = that place + 2 + 8 x holes). `icons.with_chunks`
(widen, narrow, the transfer's roster) left the count out with the dword at `len - 2`, on the last entry's
length high word; the game's next roster write (a character made) put its count (1) there: CHAR 53 1E1h ->
101E1h, the file unreadable by `gff.read_gff`. Fixed (a count of 0 written; `test_free_list_count`). Check a
file with: second dword == type table's end, TOC length == it + 2 + 8 x count. A file the old writer made
and the game then wrote keeps its one bad length (the last type's last entry): repair by hand.

**Finding why the sequel quits** (2026-11-24): `ravstart.sh` `RAV_STDOUT=1` sends the game's own
printing to `STDOUT.TXT` in the game folder ("Illegal Op (gpl=49)" was one message; the sound case
prints nothing there); `RAV_MARK=1` writes `ENDED.TXT` when the program ends; `RAV_POKE=OFF=HEX` puts
bytes in the patched program: a probe `1E 31C0 8ED8 8926F204 8C16F404 892EF604 C706F004 xxxx 1F EBFE`
(SS:SP and BP to 0:4F2h, a flag to 0:4F0h, then a hang) at the fatal routine (file 3EFEFh), the
illegal-op routine (2660Ch) or `exit` (55DFh), and `/tmp`'s hangwatch (a guest dump when the flag
comes) gave the call chain by BP. The overlaid code is only in the dump, not at its file offsets.
Two cautions (2026-11-25, logs/2026-11-25-ravager-illegal-op.md): a probe must not cover a relocated
word (the 26 bytes at 2660Ch covered a far call's segment at +18h, which the load relocated: DOSBox's
"Illegal GRP4"; use the 24 bytes `5031C08EC0268926F20426892EF60426C706F004EFBEEBFE`), and the fatal
routine is no place for one: it returns at once for trap 6Ah (only 69h stops the game), and the sound
loader reports error 0Bh, trap 6Ah, for every sound over its 25000-byte buffer (4013:B63h, 61A8h set at
62042h; BVOC 132, 138, 147, the last two among the female hurt and death sounds, DS:2909h, one of 8 at
random), so a probe there turned harmless warnings into "hangs". `RAV_SOUND=1` keeps DOSBox's sound on
(SDL's dummy device). **A patch's site can be a jump's target:** "Illegal Op (gpl=49)" in the Tyr
ambush was the spell immunity routine's "immune" exit (7F362h in the image) jumping to the `pop di` that
`spell_hit` (84AAFh) had made its site number; the fault's CS:IP was SI:DI (0083:0001, SI the spell).
`tests/test_ravager.py`'s `JumpIntoSiteTests` scans for such jumps; a byte scan's calls and short
jumps were all data or mid-instruction (check against a disassembly). SL's `window` patch (2BBA9h)
has one (from 264FCh in SL's image), not yet mended.

**The Loader's transfer and the party in the sequel** (2026-11-22, logs/2026-11-22-ravager-transfer-items.md):
`python -m dsloader.ravtransfer SAVE.SAV RAVFOLDER [SL_FOLDER DOS_FOLDER]` on a copy of `$WORK/rav`
(its roster first reset from `__support/save/CHARSAVE.GFF`; with the two folders, the items the sequel
lacks become the Loader's objects, kept in the dos folder's RAVITEMS.GFF), then `RAV_LOADER=1 RAV_MENU=1
sh ravstart.sh COPY` and `ravdice.py` attached (it writes the names past 256). In the game, at
`ravclick.py`'s coordinates (320x200, whatever the window's size): CREATE CHARACTERS (160,92); a slot
right-clicked (the four: (70,56), (120,56), (70,115), (120,115)), ADD 45 right and 14 down of it; the
ADD list's rows at y 45, 56, 67, 78... (x 130), its ADD button (252,47); the inventory icon (75,171);
an inventory item right-clicked for its box, the box's spell icon (287,83) right-clicked for the
spell's summary. Escape goes back to the title menu, and S there starts a new game with the party
(the opening talk: "Lead on!" at (100,171)). A party of one loses the opening fight (back to the title).
The sequel's scrolls: types 4Dh (wizard: One-use Scroll, 313xx, +0Eh 1; Spellbook, 310xx) and 4Eh
(priest), the spell at +2 and +10h; SL's wizard spell n is the sequel's spell_place(n) + 1, SL's
priest scroll word w is w + 97.
The roster the ADD list offers is CHAR 32-39, a place listed while its CACT word isn't 0 (the
install's 32-35 are 0; CHAR 44-46 and 60 with CACT set weren't listed); the game's DELETE writes CACT
0 at once and keeps the CHAR.
A control for a DSCLOG2 change: the build before is git's (`git show HEAD:obsidian-edition/dos/DSCLOG2.EXE >
obsidian-edition/dos/DSCLOG2.EXE`, the new one kept aside and put back after; ravstart.sh's Loader way
copies it). An equip test on the roster's inventory: a click picks an item up, a click on a pack
square or its slot puts it down; a refusal says CANNOT USE THIS ITEM and leaves it on the pointer
(logs/2026-11-23-ravager-item-wield.md).
**The sequel's AC function and save modifiers** (2026-11-23, logs/2026-11-23-ravager-protection.md):
- **The AC function** is at 5D520h. SI is the combatant (things at 388h:SI*3 + 0C33h, kind 2 a
  creature). [BP-4] is the AC, starting from the creature's +21h. [BP-6] is the other total (DEX, the
  Armor spell's call 628h:6Bh). [BP-7] is 0 when effect 4 is on, and then no plus counts.
- **Its worn list** is at [BP-324h], 10 bytes an entry. Each worn item counts only with its type's
  +0Bh bit 80h (the test at 5D61Ah), as its plus (+16h) plus its type's AC (+0Eh).
- **The save modifiers** are at 83606h. [BP+6] is the one saving, DI the modifier (higher is better),
  [BP+14h] the spell.
- **Slots and rings.** The item slots (+13h) are SL's: fingers 4 and 11, the back 12, the feet 13.
  The sequel's Ring is type 45, of no AC. Its own rings carry a spell power and plus 0.
- **The inventory panel's saves** are the sheet's own: a ring's save bonus shows only in a fight.
- **The first click.** After `RAV_MENU=1` the first click on the title menu is often lost: click
  CREATE CHARACTERS again.
- **A hung display** (2026-11-23, 01:00 UTC). During the Draxans' fight, a Hold Person cast left
  DOSBox gone. The `import -window` that followed, on the dead window, never returned, and the Xvfb on
  :55 stopped answering (`timeout 10 xdpyinfo` fails), even after that import and every DOSBox were
  killed. Which came first is not known. Only a new Xvfb gets the display back, so take every grab
  with `timeout`.
  With a new Xvfb the same cast on the same build ran clean three times (00:45-01:00 UTC,
  logs/2026-11-23-ravager-girdles-amulet.md), so the display, not the helper's new code, is the likely cause.
- **An item's spell in the sequel** (2026-11-23, logs/2026-11-23-ravager-on-hit.md): the item's +10h word, the
  spell + 1 (its box's icon the +2 word, the same); a weapon's is cast on the one hit at level 6 (5D2CCh), and
  for a shot the ammunition's first (a word at 308h:[7]). To try one, write both words in memory on a held
  weapon or on arrows (the Draxans' are type 18, items 154, 148 and 142 in ravhold.sh's fight). SL and the
  sequel number spells apart: match them by name (`ravtransfer.spell_map`).
- **A worn item's spell** (2026-11-23, logs/2026-11-23-ravager-worn.md): readied (77C1Ah, 5E8h:39h:
  the creature, the item) it is cast on the wearer if the spell is the self kind; unreadied (77CDBh) it
  ends (628h:BBh, 864EDh: the wearer's effects of that spell), which only the Loader's `worn_spell_off`
  makes work. A roster member added on the ADD screen is readied by DSCLOG2's JOIN_READY. **To test
  the ADD screen with a powered item**: a copy of `$WORK/rav` (`cp -al`, then the roster replaced by a
  real file) with a roster CHAR's item records changed through `icons.with_chunks` on the original
  file (`ravtransfer._gff_file` makes a file the ADD list reads as empty). Read effects raw at the
  load + 3E71h:24Dh (owner, caster, spell, the effect's id at +6). `shot.sh` fails for the sequel's
  copy; `import -window ID` (xdotool search --pid) grabs it.
- **Using an item from its box** (2026-11-23, logs/2026-11-23-ravager-tome-scrolls.md): the box's
  icon for the tome worked only in a fight, on the member's turn (the opener 99260h sets `[9D8Ch]`
  from its caller, 1 only in a fight), while a spellbook is learnt outside a fight (2026-11-21, and
  Kalzith's transferred Blur on 2026-11-24) and not in a fight nor on the roster's inventory (the book
  kept; the gate not found); the known spells at `(load + 3D62h):39Ch` + 15 a member; the handler 995AFh goes on through 9986Fh, 999A9h and 999CDh (`[bp-4]` the
  spell, power - 1; learning from objects 31000-31199 and 31400-31499; spells 0EBh-10Ch psionic,
  10Dh up "CANNOT LEARN"); 99B44h uses the item up with the message at `[bp-56h]`, 99B67h shows it
  only. DSCLOG2's TOME_READ (site 48) is the tome's case there.
- **A shot's items and a skipped cast** (2026-11-24, logs/2026-11-24-ravager-spell-arrows.md): in the
  sequel's items arrows are type 6 (slot 1) and a bow type 18 (slot 2); the attack's item SI is the bow,
  and `308h:[7]` the arrows' power (first). The cast on a hit starts with 5F0h:D4h (5D285h) before its
  pushes: skip a cast before that (the game's own test of the spell at 5D24Eh, PLAIN_ARROW's way), never
  after it (a skipped 608h:89h crashed the game a round later). A test archer: memory edits (power at
  +10h and +2, plus at +16h), never saved.
- **The monsters' poison and the ammunition's plus** (2026-11-26, logs/2026-11-26-ravager-poison-arrows.md):
  the sequel's spell records 273, 274 and 275 are Shattered Lands' 176, 177 and 178 byte for byte but the
  name (`Mons273`: poison 10 damage, 30, 20; the damage at the record's +1Ch), so "no monster poison power"
  was wrong. A weapon hit with no spell of its own and nothing in `308h:[7]` leaves at 5D212h (`cmp word
  [es:bx+10h],0` at 5D20Dh) before PLAIN_ARROW's 5D248h: a spell put on a plain weapon's hit goes in there
  (DSCLOG2's POISON_HIT). The ammunition routine 5D3BAh ([BP+0Ah] the weapon's item, [BP+0Ch] its type, DI
  the arrows) keeps their plus at `308h:[9]` (`mov es:[0009h],al`, 5D456h), which the shot's damage adds
  (5D021h) and the damage kinds take where better than the weapon's (5C7B5h, the other caller): SL's
  `ES:[6]`. `ravitems.py N --fine` names a combatant's bows the Fine Bow (a test edit, never saved).
- **Telling foes of one name apart in the dice log**: `ravdice.py --numbers` puts each combatant's
  number after its name ("Draxan#26"), the number `ravitems.py` and `ravfight.py state` use. The
  Draxans' ambush has a fourth "Draxan", combatant 21 (sheet 14, its armour unworn: AC 7, no DEX).

**The kits in the sequel** (2026-11-25, logs/2026-11-25-ravager-kits.md):
- **Giving a kit for a test**: `ravkits.py show` lists each member's race, classes (sheet +1Bh, the
  sheet's numbering: 1-4 clerics, 5-8 druids, 9 fighter, 10 gladiator, 11 preserver, 12 psionicist,
  13-16 rangers, 17 thief), levels and kit byte (+3Dh); `ravkits.py match C1,C2 BYTE [RACE|- [CLASS...]]`
  edits the member with those classes (a race edit makes a multiclass group: race 2 dwarf, 3 elf, 4
  half-elf, 5 half-giant, 6 halfling, 7 mul). Never save after. The `fountain-user` party transferred
  already has kits: Lex 81h, the others 01h (Ester an elf Battle Dancer).
- **The rules word**: DSCLOG2's assembled `rules`/`rules_hi` hold only the always-on rules; the Loader's
  dice log writes the switched ones (kits are `rules_hi` bit 0). A tool that writes the header must start
  from `game.rules_from_settings`, as `ravdice.py` now does; `ravkits.py count` shows the words.
- **Seeing a kit work**: `ravkits.py count`'s counters count the changes each kit routine made
  (AC, to hit, damage, rates, saves, skills, rears, moves, two weapons, initiative), so a control run
  (`RAV_RULES_OFF=0x10000`) reads all 0. The game's AC in the dice log is DSCLOG2's (PROBE_AC), so a
  kit's AC shows there even with the Python side's kits off; initiative's lines are the Python side's.
- **The sites**: initiative's "add dx,14h" at 5B7E9h (SI the creature: site 60); the caster level
  routine's "sub dx,7" for a ranger at 97E00h ([BP+6] the combatant: site 61). Priest spheres are asked
  per use by 62B45h (spell, class) through a jump table (CL 01 air, 02 earth, 04 fire, 08 water): the
  Elementalist's second sphere is hooked after its callers instead (next).

**The kits' gear** (2026-11-26, logs/2026-11-26-ravager-kit-gear.md):
- **The equip test**: "may this character equip it" is 77514h ([BP+6] the item, [BP+8] show the message,
  [BP+0Ah] the sheet, far), its one caller the equip routine 7761Bh ([BP+6] the item, [BP+8] the slot,
  DI: the worn slot + 4, so 7 the right hand, 14 the left; [BP+0Ah] show). Every other "no" of 77514h
  (no such item, its +4 flags 10h/20h, a thri-kreen's) leaves before 775FDh (to 77561h), so CU_SITE's
  AL 0 is the classes' lists alone and the kit's own may make it yes. The slot is read through the
  frame under 77514h's ([BP] the equip routine's BP).
- **Giving a kit for an equip test** on the roster's inventory: `ravkits.py set 0 BYTE RACE CLASS...`
  and `ravkits.py flags 0 WORD` (the class bits: 80h a preserver alone makes the game's lists say no
  to a bow, A0h fighter and preserver yes). `ravkits.py count`'s `kit_refused` and `kit_allowed` count
  the kits' answers (several a try: the screen asks to light the slots, then on the click).
- **A kind specialized in** is never a kit's limit (SL's): pick a test item of no kind (arrows) or a
  character without that spec to see a Ravager's missile refused.

**The priests' spheres and the Elementalist's second sphere** (2026-11-25, logs/2026-11-25-ravager-sphere.md):
- **The sequel keeps no spells known for a priest.** A wizard's are bits a member (selector 320h, +39Ch,
  0Fh bytes a member); a priest's are worked out every time: the USE screen's list (62500h, a level's
  spells from the tables DS:656h/661h) asks 6260Ah "does member SI know spell N", which for a priest spell
  (73h-EAh) asks 62C00h (spell, member: does one of its classes cast it) and then the spell's level
  (62AC5h) against the member's highest (97E9Ch, from the caster level of spell 73h). **62B45h (spell,
  class)** answers by a byte a spell (selector 3D0h:7D3h, file 478E3h: 1 air, 2 earth, 4 fire, 8 water,
  10h every priest's, 20h the druids') met by the class's mask from its jump table (CS:0ADAh, the overlay's
  code from file 62100h): a cleric 10h + its element, a druid 30h + its element, a ranger as its element's
  cleric, class 19 all; wizard spells (below 73h) classes 11 and 18. So a cleric never casts a 20h spell
  (Cure Serious Wounds, Raise Dead, Heal...: the druids' alone in the sequel), which is where SL's
  Healer's cosmos would go (its water cleric's 20h spells) with the same hook.
- **Its callers**: four in its own overlay (62C00h at 62CABh, 628AFh at 629BBh, 626B7h's two at 627D3h and
  62818h, the slot count's "is this class a caster" with spells 8 and 73h) and one far, 97DC5h (the
  caster level) at 97DDCh through its stub 588h:20h (overlay far calls name the stub by a selector: the
  segment table's word, load + 45E8h + the selector, is the stub's segment less the load's). Every
  caller that asks for a member has it: 62C00h in DI, 628AFh and 97DC5h at [BP+6]; each call is followed
  by "add sp,4 / or al,al". DSCLOG2's EL_SPHERE (sites 90-92) replaces the ADD: the frame's two words
  (spell, class) under the INT's are read and dropped, AL made 1 for an Elementalist's own cleric class
  and a spell of its second sphere. `tests/test_ravsphere.py` runs 62B45h from DSUN.EXE against
  `ravager.class_spheres` and checks no other call to it exists.
- **Finding an overlay routine's callers** (scratch, in the log's files): the module from
  `ravimg/layout.json`'s `modules` (`file`, `size`, `stubs`: `entry` an offset in the module, `stub_off`,
  `stub_seg` with the load segment 418 added), then "0E E8 rel16" inside the module and "9A stub_off
  selector" anywhere, the selector found by its segment-table word.
- **Giving a member a second sphere for a test**: `ravkits.py set M 0x01 - C` (a single-class cleric C:
  the Elementalist is a cleric's kit, and a multiclass character's kit is its group's), `ravkits.py
  levels M 5`, `ravkits.py sphere M S` (1 air, 2 earth, 3 fire, 4 water); `ravkits.py count`'s
  `el_spheres` counts the game's no made yes (thousands: USE asks at every redraw). Never save after.
- **Playing a spell on a chosen member's turn** (the log's run script): Computer Control for the others
  (View Character's small icons, as the kits' runs), a test base AC of -10 for the caster (a caster hit in
  the round finds every spell crossed out, "YOU WERE HIT"), then wait for the member's name in the top-right
  panel (a crop compared with `compare -metric AE`); the top-left icon, then the bar's third (97,171), CAST
  SPELL. Tab then Return brought the game's menu, not an attack: a click on an adjacent foe ends a turn.

**The Shinobi's wizard spells** (2026-11-27, logs/2026-11-27-ravager-shinobi-spells.md; branch
claude/ravager-shinobi-spells): a Shinobi is a thief kit (the sheet's kit byte +3Dh 11h, class 17) that
casts preserver spells by thief level (its slots: SHINOBI_MAGE, site 190, the kit slots' entry above).
- **Where the game asks**: the USE screen's MAGE list (DS:43E8h a list a member, the 1 = MAGE) comes when
  62C00h finds a known wizard spell the member casts; its levels stop at 698:2Ah (97D1Fh, the highest
  wizard level with a known spell) capped by 97E9Ch (member, 1), from the caster level 97DC5h (member,
  spell 0) as (level+1)/2. 97DC5h's loop takes, for each class 588:20h says yes to, 98:C1h (member,
  class) the class's level, then "add sp,4" at 97DF1h, then "sub dx,7" for classes 13-16 alone.
  Wizard knowledge is 6260Ah's bitset (selector 320h, +39Ch, 0Fh bytes a member); the new spells
  320-325 the sheet's bits (+3Fh 40h, 08h, 80h; 325 the kit byte's 80h).
- **The hooks** (DSCLOG2's THE SHINOBI'S SPELLS): the "yes" for a Shinobi's class 17 and any wizard spell
  (it learns only its list's, so it knows no other in play: a test edit's other known spells showed too)
  rides on EL_SPHERE's three sites (90-92 now SH_SPHERE_DI/BP, then EL_SPHERE as before); the caster
  level is site 209 at 97DF1h (SHINOBI_CAST_LEVEL: thief level less 5, 11 at most, none below 6th); the level-up's
  "is it class 0Bh" at 957ABh is site 210 (SHINOBI_LEVEL_UP: a Shinobi's thief from 6th picks a spell
  through 688:66h, 93160h, as a preserver does; inside it PICK_ANY, PICK_PAGE, PICK_LIST and PICK_TOP
  keep to its list and its slot levels); creation's CR_PICKS (site 87) gives a Shinobi its first spells
  (SH_FIRST_SPELLS: a CHOOSE A SPELL a pick); SCROLL_LEARN (99A2Fh) and NS_SCROLL (site 148) make a scroll
  its own (THAT IS NOT A SHINOBI SPELL), roll its READ LANG. (AD&D: the thief table's skill 7 with race,
  95 at most; else 5% a level with race) for YOU CAN NOT READ THE SCROLL and then the INT chance.
  NS_SPOOK_SAVE counts its casting level. Header +2076..+2087 (learn_read, learn_read_chance,
  learn_spell_hi; SH_LEVELS_N, SH_ASKS, SH_PAGED, SH_SCROLLS counters: `ravlevel.py counts`).
- **Played** (the log): Ar'Anda made a thief 13th Shinobi on her turn in the Draxans' ambush (`ravkits.py
  set 0 0x43 - 17`, `levels 0 13`): MAGE LEVEL 1-4, WIZ slots 3 3 2 1; at thief 10th levels 1-3 only.
  Her Hold Person: Paralyzed (69) on the Draxan for 960 game seconds, 16 rounds at casting level 8 (read
  with `RavGameData.effects_left()`). The control (kit byte 0x40, no kit): PSIONIC only.
- **Tests**: `tests/test_ravshinobi.py` runs the hooks on the emulator against `kits.RAV_SHINOBI_SPELLS`
  and `kits.rav_pick_top`; its list test reads the sequel's spell names (DSUN_WOTR).
- **Not ported**: the Effects screen's READ LANG. line; armour and effects in read languages; a
  preserver-thief multiclass Shinobi (its preserver class casts as a preserver's).

**Choosing a kit in the sequel** (2026-11-25, logs/2026-11-25-ravager-kit-choice.md):
- **The creation overlay is SL's code at other addresses** (overlay 6AFE0h-6CE93h, its stub 46CCh,
  the same entries as SL's 421Dh: 66h the rows marked 6BC81h, 7Ah back to the disciplines 6BF3Fh; the
  next overlay 6D090h-6F3B0h, stub 46DDh). A stub's header (`CD 3F 00 00`, then the overlay's file
  offset as a dword, its size, fixups, entries) gives the overlay's place: file offset = the dword +
  57580h (the root image's end + 10h; SL's + 52EB0h). Side by side with SL's (`paste` of two
  disassemblies) the routines line up byte for byte but the DS addresses: the panel's windows
  DS:1134h/1138h (SL's EA2h/EA6h), their marks 42C0h/42C2h (4980h/4982h), the sheet being made
  1429h, EDIT's member 112Eh (0E9Ch), the marks' window 11C4h (F32h) and table 360h:17Eh (338h:1ABh),
  the title's format 109Fh (E11h), the ink 2D16h (3270h, F0h for 34h), the help line's text 4A9Dh.
  The window ids are the sequel's own: the creation screen 19503, the disciplines 19504, the spheres
  19505 (SL's 3011-3013; the buttons' ids are SL's). The sites: `ravager.PATCHES`' kp_* (62-69).
- **Its labels are planar pictures**: after the width and height, FFh "PLAN", a word the planes, then
  each plane's colour byte and its bits (MSB first, the rows run on unpadded). SL's RLE form decoded
  them as empty; `art.decode_frame` reads both, `art.planar_frames` writes it. The letters are SL's
  shapes, so `weaponpages.glyphs` and its CUTS work on the sequel's icons.
- **After DUAL**: the routine that changes a human's class is 9493Ch (SI the member, [BP+8] the new
  class; SL's 86C80h), its "cmp word [bp+8],0Ch" at 94A57h (site 76); the game's three-choice menu
  (the new cleric's sphere's) is its call 560:25h at 94878h, read from the code at run time.
- **Looking at it**: `ravkits.py page` shows the sheet being made (race, classes, kit byte), the
  panel's windows by id (19504/19505 the game's, 3022/3023 the KITS ones, 3026 on a kit page) and
  DSCLOG2's counters (kit_pages_shown, kit_rows_taken; dual_asks, dual_kits for DUAL).

**STORE, RECALL and the starting gear in the sequel** (2026-11-25, logs/2026-11-25-ravager-store-gear.md):
- **The click overlay** (6D090h-6F3B0h, stub 46DDh, SL's from 65480h) has SL's code with DS addresses moved: the
  button lookup "mov cx,16h" at 6DE85h (its way on for another button 6DF97h), the die's routine 6D3CEh (stub entry
  5Ch; its argument a byte [BP+6], 1 a roll, where SL's took DI) with the hit points rolled by 6D5EBh and "cmp byte
  [bp+6],0" at 6D5F1h after; the scores' redraw is the creation overlay's (46CCh) entry **B6h** (6CD7Bh), SL's BBh
  (the sequel's stub entries are SL's less 5 from about there: raw "call 5B8:xx" in an overlay is 46CCh's stub).
  The new character's routine 46DDh:20h (6E6D8h: the template copied, the classes, thri-kreen's claws); DONE calls
  the game's gear (6F197h, entry 7Fh) then the roster write (6E4D6h, entry 4Dh) at 6E2ECh-6E2FDh.
- **The sequel's carved buttons** (SAVE 18108, LOAD 18102, ADD 18104, DROP 18106, EXIT 18109, DELETE 18110, DONE
  19100; BUTN 18300-18303, 19304) are packed pictures: FFh "PLAN", a byte BITS, 2^BITS palette bytes, then each
  pixel's index, BITS a pixel (`art.decode_packed`); four frames. A one-colour label's planar form is the same bytes.
- **Its items** (OBJEX.GFF RDFF records, 17h bytes): the name number is TEXT 1000's line counted from 1 (a list read
  from 0 is one off: type 91 the Shield, not a cloak). Armour types in fives by place: 1-5 the arms (slot 0), 30-34
  the chest (9), 62-66 the legs (6); leather is "Armor" 32/3/64. A new fighter: bone arm/chest/legs (4, 33, 65), a +1
  shield (91) in slot 3 and a +1 metal long sword (97) in slot 10; a thief leather chest, the long sword in slot 3,
  an obsidian dagger, a sling; a cleric leather, the shield, a wooden club in the pack (a fire cleric's useless).
  `ravitems.py N` lists them with slots.

**A ranger's two weapons, the charges' labels and the music** (2026-11-25, logs/2026-11-25-ravager-small-ports.md):
- **The sequel's two-weapon routine** (5DE34h) is SL's (595ECh) on the sequel's records: its test for a ranger
  is "test word es:[bx+10h],200h" at 5DE67h (the sheet's flags +10h, SL's +12h; DSCLOG2's site 78 RG_TWO now),
  then "jnz" to no penalty. A party member's flags: `ravkits.py flags MEMBER [+WORD]` (`show` lists them too).
- **Armor for a test**: `ravknow.py 0` teaches the transferred party's member 0 (Lex) Armor too (the bitset at
  3F3DCh is member 0's whoever it is); on his turn C, the first icon (game 175,58), then a portrait on USE (Jenna's
  120,117) casts it on that member: 10 charges at caster level 2.
- **A creature's DEX** is its record's +1Ah (`CREATURE_ABILITIES` +1 in ravlog's layout). An edit holds through
  a fight's turns but not a spell cast on the creature: Armor cast on Jenna read her DEX from her sheet again.
- **An item's worn slot** (+13h): trading two items' slots (the chest's leather and an armour from the pack) puts
  a member into other armour at once, for the game's routines and DSCLOG2's ARMOUR_WORN alike (no screen needed).
- **The event queues** (timed effects' ends) are two far pointers at DS:2A63h and two counts at DS:2A6Bh, 11h
  bytes an event (SL's 2FBEh, 2FC6h: `ravds.py --fuzzy`; the queue routines from 2C4FCh). The charges pass
  (DiceLog.count_charges) reads them; `RAV_CHARGES_OFF=1` for `ravdice.py` takes the pass out for a control.
- **A label on screen**: DSCLOG2 puts a slot's label up only as the game draws the map, so a charge used during
  a foe's blow shows once its picture is done, and one written and gone within a blow's animation (two charges in
  one turn) isn't seen at all. To catch labels: grab the window every 0.3 s and watch the slots (number, width,
  thing at the tail's LBL_SLOTS) with the time; the label's ink is one palette colour (#9AE3FF for the charges'
  blue in Tyr's street), so `convert FRAME -format %c histogram:info:` finds the frames with it.
- **The sequel's music** is its CD's audio (README.TXT: "no MIDI music (just off the CD)"; SOUND.INI
  `[MidiNotEnabled]`; GOG's SOUND.CFG the SB Pro II's FM and digital drivers; 40 .ogg tracks): the Loader's
  music device is Shattered Lands' alone.
- **Tyr's thieves from `ravager-after-ambush`**: the arrow keys (Up 8, Right 40, 150 ms apart) left the leader
  at world (2112, 1632) in one try, not the alley; the transferred party's ambush (the Tab log's run script) is
  the surer fight.

**Saves in the sequel: quick saves, GREQ, the save window and the roster** (2026-11-25, logs/2026-11-25-ravager-quick-saves.md):
- **The save call**: the LOAD/SAVE window's wrapper saves with `lcall 5D8:84h` (file far, name far) at 7D84Ah,
  the result in AL (SL's 4242h:89h). The selector table is at file 4B080h (8 bytes a selector; SL's 46770h):
  5D8h→46EFh the save stub, 600h→4736h the window's stub (20h load, 25h save), 5D0h→46E9h the roster file's
  open (52h) and close (57h), 2E0h→3C10h the fight state (+19h, F1's "CAN'T SAVE DURING COMBAT" test at 79AFDh),
  2F8h→3C4Ch the list window's data (+0 the chosen row, +2 the first row shown).
- **Its strings**: the save path DS:44F2h; "SAVE??.SAV" at DS:2085h (the page letter 2088h), "SAVE%.2d.SAV"
  at DS:20B6h (20B9h); SCREEN_IS DS:0DABh. The window allocates 10 entries of 7Dh bytes and takes the number
  from SAVEnn.
- **GREQ**: after the save the wrapper writes into the roster file (DS:144Ah) PREF 100 and **GREQ slot**, 9
  bytes: the map's limits DS:14D7h..14DDh (4 words, set by a script at 8C322h, 0,0,800h,620h at an area
  change) and the byte at DS:4459h; the load reads GREQ (es:[2] = row + 1, 7DA2Bh-7DA48h) and puts them back.
  The calls: open 46E9:52, check 27ED:64(dword [144Ah]) (nonzero: skip), delete 27FC:5C5(type, id), write
  27FC:E8(far buffer, 9, type, id), close 46E9:57. A quick save therefore writes **GREQ 100+slot** (DSCLOG2's
  `greq_write`), and site 84 (7DA30h, `mov ax,es:[2]`) adds 100 when the page letter is Q, so a quick load gets
  its own limits and not those of the manual save in the same row. `ravquick.py greq FOLDER` lists them.
- **Its keys** (the main loop's table at cs:1F44h, code base 78340h): F1 the save window, F2 the load window
  (`lcall 600:20` at 79B74h), F3 like Esc, F4 the music, **F5 the sound effects**, F6 the animations; F9 isn't
  taken. DSCLOG2 takes F5 and F9 only while the Loader is there (`loader_fresh`) with the quick save on; with
  the Loader gone F5 is the game's again. No camp: rests are at fire rings and inns, so the camp autosave has no
  sequel side.
- **The roster holds 40 already** (28h at 58380h, 58A34h, 585C0h, 591F5h, 6E541h, 6EDFAh, 6EE05h, 6FB08h; SL
  14h), and the roster window scrolls with 2F8:0/2 (58742h sets the first row).
- **More save pages** would go where SL's do: SL's save_page (74901h) and save_click (74B9Fh), the switches'
  default jumps, are the sequel's 7DABCh (`jmp 7E00Fh`) and 7DD51h (`jmp 7E008h`). But the sequel's
  RESOURCE.GFF has no WIND 3009 and no ICON/BUTN 80Ah (SL's page buttons), so the window's own resource and
  room for the arrows must be found first.
- **Played** (the log): F5, F9 and the autosave after a won fight in the sequel, GREQ 101-103 and 106 written,
  a quick load through site 84 with GREQ 102's limits; F5 with the dice log stopped the game's SOUND EFFECTS
  ON. **DOSBox caches a mounted folder's listing**: a save written into the folder by the Loader from outside
  (a named save put back) isn't in the game's list until DOSBox restarts (the quick saves are the game's own
  writes, so they show). The sequel's save rows are narrower than SL's: an autosave's "- after a fight" runs
  past the row.
- **F9's LOAD window runs on the main loop** (2026-11-25, logs/2026-11-25-ravager-loot-keys.md):
  the window's routine (600:20) **returns with the window up**. SAVE_REQ was 3 0.4 s after F9 with the
  window still open. The map's main loop then runs the window, PROBE_SCROLL with it, with SCREEN_IS
  (DS:0DABh) 2. A page-back on "the main loop running" therefore took the QUICK page off under the open
  window: DSCLOG2's and, after ANSWER_WAIT, the Loader's own. Now only DSCLOG2 does it, and only when
  SCREEN_IS is 1. The sequel's autosave names are short ("Auto Day 1, 00:06 fight", `ravlog.region_short`,
  at most 28 letters).
- **The save window's name** (2026-11-25, logs/2026-11-25-ravager-loot-tabs-join.md): a click on an empty row
  puts the cursor in the name box at the bottom, and the letters typed go there (the mod's T, S, M/U/I, F5 and F9
  take none of them). **SAVE (252,46) or Return with the box empty saves at once, with an empty name**, in the
  plain sequel as with the mod. Escape in the name box doesn't close the window; EXIT (252,67) does. A save's name
  is `namedsaves.save_name(data, wotr=True)`.

**Looting, selling and the pointer in the sequel** (2026-11-25, logs/2026-11-25-ravager-loot-keys.md):
- **The pointer's modes** (DS:1440h): 1 the walk arrow, 4 the sword, 2 the eye (look), 3 an item held.
  Right-click turns 1 → 4 → 2. The eye on a body opens its container window. The eye on an item on the ground
  picks it up onto the pointer (thing 523), and a click then puts it into the leader's pack.
- **Containers**: DS:05D6h is the container whose window is open (SL's 05E6h), 9999 none. The things'
  table is at (load+3F49h):0C33h, 3 bytes a thing (kind, first item).
  - Dynamic things: the free list's head is DS:56EFh, the count out DS:55C6h. There are 200 dynamic things
    (135 free and 65 out after the ambush).
  - Items: 400 records of 17h bytes at the far pointer DS:19C1h. The free items' head is DS:5AF3h, linked
    by +4. The power is a word at +10h (SL's a byte: `game.POWER_BYTES`).
- **The shop**: the byte DS:143Dh is 1 while a merchant's shop is open (set at 7BCA6h), and its merchant
  is DS:1A30h (SL's 179Ch). The shop's loop is at 88D52h, its test `cmp byte [143Dh],1` at 88D99h (site 82,
  `shop_loop`).
  - The character on show is at (load+3E71h):0B44h, selector 370h (SL's 3931h:25Bh).
  - The party's money is a dword at (load+3C13h):357h, selector 2E8h.
- **Status names**: far pointers at DS:1463h. 0 New, 1 Okay, 2 Stunned, 3 Out Cold, 4 Dying, 5 Animated,
  6 Petrified, 7 Dead, 8 Gone (SL's numbering differs: `ravlog.ADDRESSES["STATUS_NAMES"]`).
- **Keys**: O is the sequel's overhead map, so DSCLOG2's M is made O. U and I are USE and the inventory,
  as in SL.
- **Loading the after-ambush save without memory-assisted clicks.** At the title menu press L, then Return on the slot screen with AFTER AMBUSH highlighted. A 640 × 480 Ravager surface scales the 320 × 200 game by 2 horizontally and 2.4 vertically. The purple chair at Tyr (1341, 238) is visible from the street, making it possible to verify the furniture package from an ordinary screenshot. [Furniture playtest](logs/2026-11-27-ravager-furniture.md)
- **Notaku** (Tyr, south of Shadow Square; arrow keys y 1224, x 296, y 936 from `ravager-after-ambush`; the
  eye on him, talk 3, 1, 3, 2) sells. **His talk script drops "Show me your goods" for the rest of the
  conversation after any visit to the shop**: a sale, a sale by hand, or none. It does so in the plain sequel too,
  and a new talk offers it again (logs/2026-11-25-ravager-loot-tabs-join.md). His line after the shop tells a
  trade from none by the money (next item); S gets the thank-you since the fix. The sequel's offer for an item is the mod's `sell_price` (28 for Bone Brigandine Armor; the
  plain sequel offers 48). `ravloot.py` shows all of the above.
- **The plain sequel as a control** (no Loader, no DSCLOG2, no patch): `ravstart.sh` without `RAV_LOADER`,
  `RAV_MENU=1`, on a fresh copy of `rav` with the save's three files copied in (narrow as they come from
  `saves/`), then `ravload.sh`'s three clicks
  ([the script](logs/files/2026-11-25-ravager-loot-tabs-join-plain.sh)). `dosmem.py` shows no DSCLOG2 (upper
  memory 9FFFh SC and D000h free). The view doesn't follow the leader the same way there (no `centre`), so look
  for a figure before clicking on it.
- **A merchant's script tells a sale from none by the money**: Notaku's (GPL 153) keeps the party's money
  (variable 85h 0, the dword at 2E8h:357h) in 89h 42 before the shop (3EFh), and tests it again as the shop
  returns (400h): changed, "Thank you, your business is appreciated."; not, "Sometimes the wisest purchase is
  none at all, yes?". Other sequel scripts test 85h 0 too (28, 91, 129, 140, 157-159, 165, 174, 322, 325;
  SL's 2, 24, 65, 88, 135, 149, 152, 206). So the Loader's S must pay before the shop returns to the
  script. DSCLOG2's SHOP_LOOP holds the loop's way out after S until the Loader's SELL_DONE (+1884) is
  SELL_SEQ, at most 3 s (logs/2026-11-25-ravager-loot-keys.md). A memory diff around a sale didn't find this,
  but the script's decode did (`dec.py` with `GPLDATA` the sequel's, from 0 to the line).
- **The pointer's mode before a click on someone**: right-clicks cycle 1 arrow, 4 sword, 2 eye (DS:1440h).
  After the inventory is closed the mode isn't always the arrow, so read it: a sword's click on Notaku
  started a fight.

**R, F10 and Alt in the sequel** (2026-11-25, logs/2026-11-25-ravager-fight-keys.md): the Loader's
squares.py, moveback.py and usable.py run on the sequel with `ravlog.RAV_FIGHT_KEYS` (applied by `apply_layout`):
- **Squares**: the live walk map DS:0538h (SL's 0556h), the step costs 10/14 at DS:0551h, the movement points and
  turn flags at (load + 3C4Fh):22Eh and :1D8h (SL's 37BDh:22Bh/:1D5h), whose turn DS:426Dh (SL's 4979h), positions
  67C5h stride 25h. The sequel's palette has no light for stone: LIGHT (DSCLOG2 header +1926, the far block's 256
  bytes) falls back to DARK, so the crosses are dark on Tyr's grey street. DSCLOG2's squares pass is DSCLOG's
  TINT_FAR, its map at PSP:5Ch; the header's view_redraw (+1922) asks its `redraw_tick` (in the main loop's
  PROBE_SCROLL) to draw the view again once nothing is drawing, as `shadows.redraw` does in SL.
- **F10**: the handler 1EC05h (SL's 1B83Ah), the turn's start points, y, x at DS:4258h/425Ah/425Ch (SL's
  4964h..4968h). After the last step the sequel opens **END <name>'s MOVE: GUARD / WAIT / END TURN**, and F10 does
  nothing while it is up (Escape closes it). The game's F10 then gives the points back but leaves the flags' bit 0
  clear, so the step routine (5D8F1h) walks nowhere: moveback.py sets it again (flags 0x3EE to 0x3EF). Its
  standing-still test (1F3FCh, the map record 67BBh + 25h x thing, bit 20h) is where site 100 (F10_PIN, 1EC36h)
  sits: a member under Paralyzed (69) or Cannot Move (66) stays put, anyone else goes back even after the last
  step. The walk's next step and steps left are (load + 3F49h):374h + 1Ch x thing and :8A7h + 13h x thing; the
  swings +184h and attack commands +1AEh (bytes) off the points' segment.
- **Alt**: the draw list is a far pointer at DS:67B7h, its count DS:264Eh, 8 bytes an entry (x, y, two bytes,
  thing), **873 entries for the whole map** (SL's cap of 600 misses the view's things: DRAW_MOST 2000). The map
  record's object at +1Bh. Triggers: a far pointer at DS:40C0h, 13-byte records, the heads at (load + 3C10h)
  offsets 0Dh..17h. Doors are items of type 41 named "Door", bodies object 2200 (a container, type 58: its ring
  sits at the item's feet, the corpse drawn below right of it), the dead status 7, foes by the side mask 0F80h. The gold
  rings use the Tab ring's DSCLOG2 drawing: a 520-byte RING_TAB in the far block (header +246), each mark's
  kind a byte, the gold tints through RED while marks are up (red again on release).
- `ravkeys.py` reads all this (the state line, `things`, `marks`) and gives or takes effects for a test
  (`effect OWNER EFFECT`, `del OWNER EFFECT`: the sequel's effects table at (load + 3E71h):24Dh, count DS:2100h).
  The dice log's switches `RAV_NO_SQUARES`, `RAV_NO_MOVEBACK`, `RAV_NO_USABLE` (and `RAV_NO_SAVES`) make a control.

**Picking weapon specs at creation in the sequel** (2026-11-26, logs/2026-11-26-ravager-spec-pick.md): DSCLOG2's
WEAPON PICKS (sites 120-125) shows the Loader's weapon window on the psionicists' pop-up in weapon mode, as SL's
PROBE_PK_* do. What it needed from the sequel:
- **DONE** (6E0B9h) runs the powers (6E906h), the spells (6EA10h, CR_PICKS at 6ED55h), frees the screen's windows,
  then "push si / nop / push cs" (6E2ECh: CR_WEAPONS, site 120) and the call for the starting gear (6F197h; GEAR_DONE,
  site 85, at 6E2F2h). The pick runs there, after the spells and powers (SL asks for the weapons before the powers).
- **The pop-up** (688:61h, 93B62h): its event loop's "or ax,ax / jnz" at 93BBAh (PK_HOVER); the window routine
  93BE4h ("push 2B0050h" the place, then "push 445Dh" the window at 93C94h: PK_WIN); the title "push ds / push
  2ACCh" at 93D63h (PK_TITLE; the colours E7h/E3h at 93D6Bh/93D71h, width 9Fh at 93D6Fh, y "push 46h" at 93D73h);
  the two lines routine 93930h; the powers' list fill 93DECh (PK_FILL) to its end 93F7Eh ("xor ax,ax"); a button
  in use or not 168:71Fh (its far address at 93D09h), a button's text 168:7FFh (at 93CF4h); the click handler
  93F8Dh, its "mov ax,[bp+8]" at 93FABh (PK_CLICK), the stay 9403Eh and the close 94047h. The window far pointer
  DS:1431h; the pop-up writes the member's sheet and creature to DS:1429h/142Dh (put back after it).
- **EDIT**: the creation screen's EDIT is 6E696h (5C0:48h). View Character's right-click menu offers it only while
  the creature's status (+14h) is 0 ("New"; else EDIT NAME). The creation screen copies only 42h bytes of the sheet,
  so the specs (+42h..+44h) and +45h survive an EDIT; DONE after an EDIT asks only for what is still due.
- **The pictures**: the sequel's are PLNR (FFh "PLNR", BITS, a colour map, codes with the escape 0: "0 0" a pixel
  of colour 0, "0 k" the last code k+2 more times); `art.plnr_frames` writes it. Its UI palette is PAL 1000:
  blue-greys 233-238, the marble's bevel 247/231; the marble is BMP 17001, the powers' window WIND 17501, its
  buttons' BUTN 7FAh. The weapons' pictures are OBJEX objects (`weaponpages.RAV_PICTURES`; no short sword: the
  long sword's at three quarters).
- **Testing it**: DSCLOG2's rules word is 0 until the Loader (or the dice log) writes it, so a new character made
  with neither attached gets no window. `ravspecs.py` reads the party's specs and the pick's counters (wp_asks,
  wp_picked, wp_filled); `ravspecs.py check` compares the routines in memory with dos/DSCLOG2.EXE. The roster
  (CHARSAVE.GFF) keeps the picks; START GAME takes the party CREATE CHARACTERS has, empty after a restart (ADD the
  roster's). The new characters are 7th level: a gladiator is due 3. In the Tyr ambush Borzak's right hand held a
  type 91 (flags 4, not a weapon) and his sword was in slot 10: a test edit of that item's type to the Lotulis (61)
  gave "+3 mastery" to hit and damage.
- **A new fighter's attacks a round** (2026-11-26, the same log's part 9): the sequel's creation gives a 7th-level
  fighter 4 halves (2 a round) at the sheet's +24h. Its gear puts the +1 shield (91) in slot 3, the right hand, and the
  +1 Longsword (97) in slot 10, the left hand (one swing a round whatever the skill); party member 0 of a new game also
  has an Obsidian Dragonsbane +4 (73) in slot 14 that Computer Control readies in the left hand. For a rate test move
  the sword to slot 3 (the shield to 14: Computer Control puts it back in the left hand, harmless) and make any second
  weapon a shield (type 91), all with the dice log attached and never saved. Seen: a long sword specialist (mastery) 2
  every round, a club specialist with the long sword 2, 1, 2, 1, a fighter with no spec the game's 2.

**The starting gear's table and the weapon hand** (2026-11-26, logs/2026-11-26-ravager-starting-gear.md): 6F197h
(DONE's gear call) gives a new character (creature +14h 0) its items through 6EF49h, from a table of 3-byte entries
(word: the OBJEX object; byte: the worn slot) at file 43680h, load + 3E48h in memory (the overlay's "mov ax,358h"
fixed up: read it from the code once the creation overlay is in, `ndisasm -b16 -e 0x6EF49 DSUN.EXE` for the
routine), each class a range by its flags (sheet +12h, fighter tested first: the log's table). Each item is put in
its slot by c8:288Ch, or dropped back into the pack where the class can't use it (an air cleric's club). The game
put the fighter's +1 long sword and the cleric's club in the left hand (10) behind a shield in the right (3), and
the druid's, preserver's and psionicist's weapon in the left with the right empty; the Loader's patch `gear_hands`
(ravager.GEAR_HANDS: seven slot bytes) puts each weapon in the right hand and the shield in the left, so a new
fighter needs no test edit for its attacks a round (`RAV_SKIP=gear_hands` for the game's). The OBJEX objects:
an RDFF chunk's item record starts at +0Ah (17h bytes: the type at +0Ah, the plus at +16h). In a fight, C on a
member's turn opens USE or View Character (whichever the menu last had); the USE screen's second bottom icon
(75,171) is the inventory, whose Computer Control icons are the lower small ones left of the portraits (6,17 /
6,65 / 6,113 / 6,161), View Character's 47,53 / 98,53 / 47,113 / 98,113.

**Where DSCLOG2's far block goes** (2026-11-26, logs/2026-11-26-ravager-hma.md; it reaches FD00h since the
see-through tables moved in). FAR_INIT asks XMS for the HMA (01h): GOG's DOSBox 0.74 always answers 90h (no
HMA: its 01h/02h are stubs) though A20 and 100000h work, so the HMA is used when FAR_RING-FAR_TOP is all zero;
91h (DOS=HIGH, DOSBox-X's default `dos=high`) goes straight to upper memory (strategy 42h: the top of it), then
conventional memory; no room anywhere: "no memory for its ring", exit 4C01h, nothing hooked. A20 by 03h (global:
the owner's), checked by the wrap test before any write; an HMA given but unusable is handed back (02h). Nothing
ever releases them (a TSR). To see it: `dosmem.py` (the chains, A20) and the header's +142 (FAR_SEG: FFFFh the
HMA). **To take the HMA for a test** in 0.74, where XMS gives it to nobody: put bytes in it before DSCLOG2
(`logs/files/2026-11-26-hmagrab.asm`, run from a throwaway config's autoexec before `lh d:\dsclog2.exe`): the far
block then lands at E02Fh, the game runs, shadows and the Loader's see-through tables follow FAR_SEG. The
emulator tests: `tests/test_far_init.py` (XMS and DOS played by the test). A second launch of `dosbox` by
`setsid nohup ... &` from a shell: `$!` is setsid's pid when setsid forks, not DOSBox's; find DOSBox with
`pgrep -x dosbox` and its start time before writing rav.pid (two games from one config wrote the same files).

**Picking pockets in the sequel** (2026-11-26, logs/2026-11-26-ravager-pick-pockets.md): DSCLOG2's PICK POCKETS
(sites 180-186) puts SL's purse in the place of the sequel's Turn Undead button. What it needed from the sequel:
- **Turn Undead's button**: the routine that shows the USE screen's buttons (97AC8h) tests the element word DS:9C1Ch
  at 97AF4h (pp_show: a thief out of a fight gets element 9 and icon 3048 in DS:9D77h); the handler 9756Eh (end
  9772Bh): its pressed byte DS:9D76h tested at 97623h (pp_click), the icon read at 9767Bh (pp_lit) and 97716h
  (pp_info, the right click's box skipped to 97726h), "push dword 132FFFFh" at 97699h (pp_arm: the purse arms the
  pointer and leaves by 9772Bh), the name "push ds / push 2D08h" ("TURN UNDEAD") at 975CBh and 97702h (pp_text).
  The button's cache DS:2B9Ah keeps a member's button: let go when the purse was shown, or a cleric viewed next
  shows the purse. The sheet's far pointer for the member shown is DS:1429h; the fight word QS_FIGHT_SEG 3C10h +19h.
- **The pointer**: the sequel's mode DS:1440h 2 is the look pointer (SL's 2 is a pick-pocket pointer of its own); a
  click with it runs the talk routine 630F0h (SL's 5ECD0h; its end 6373Fh), patched at 630F8h (pp_hand: an armed
  pick asks the Loader and shows its answer through the overlay frame, as unlook's window). A right click (mode 1)
  disarms (probe_pointer's pp_disarm). The thing under the click: the combatants' kinds at 388h:C33h (2 a creature).
- **The Loader's side**: `_answer_pick` under itemgate (the NPC's item-list head made writable), SL's
  `pickpocket.attempt` with the sequel's layout: LIFTABLE_TYPES/NAMES and OWN_POCKETS empty, and
  `pocket_sized = ravlog.rav_pocket_sized`, since **the sequel's item types have no weight** (the byte at raw +2, SL's
  word +4, is 0 for its dagger, long sword, shield and armour): without it a long sword came out of a pocket.
- **Testing it**: `RAV_PICK_ROLL=N` on `ravdice.py` fixes every pick's d100 (1 a success, 100 caught). The header's
  words from +2000 (on, seq, reply, who, thief, taken, text offset, shown, armed, late): late counts picks the Loader
  didn't answer in time (0 in the play). The purse is ICON 3048 in the Loader's RESOURCE copy (`RAV_SKIP=pick_icon`
  leaves it out).

**Spell arrows made in the sequel** (2026-11-27, logs/2026-11-27-ravager-spell-arrows-made.md): DSCLOG2's SPELL
ARROWS puts SL's arrows buttons on the sequel's USE screen through PICK POCKETS' sites (180-185) and site 240. What
it needed from the sequel:
- **The places beside Turn Undead's**: WIND 11500 is the same in both games; Turn Undead is APFM 2BEFh at (148,129),
  and the spare places 2BE7h-2BEAh (index 1Ah on) right of it take the second to fourth buttons (on the screen the
  first sits at 157,147, the second at 176,147, as in SL). The routines they call are reached through the selector
  table at file (45E8h x 16 + 5200h) + selector, segments less the load segment: 4D8h 45C9h (the USE window), 370h
  3E71h (the frame; USE_WHO at :0B44h), 5B0h 46BDh (the button register stub, entry 4Dh), 128h 28FFh (the chunk
  load, :4ABh), 698h 47C1h (the USE overlay's stub: the handler entry 66h, 9756Eh; the draw entry 6Bh, 97743h), 1D0h
  344Ch (the free, :92h). An overlay stub is `CD 3F` then 5-byte entries (`CD 3F` + offset).
- **Closing**: site 240 at 9659Eh (`cmp word [2B9Ah],0`, the button cache's test as the screen closes) lets the
  extra buttons' icons go.
- **The known spells**: selector 320h (load + 3D62h):39Ch + 15 x member, bit n for spell n (Chill Touch 3, Shocking
  Grasp 10, Vampiric Touch 38); wizard slots left at DS:4469h + 22h a member (ravlog's SLOTS_LEFT).
- **The arrow**: a 17h-byte item of type 6, power the spell + 1, name 256 + 42 + row (ravager.mod_name 16Ch + row),
  object 22616/22618/22620 (ravitems.own_object of SL's pictures 2616-2620), in OBJEX2.GFF with no transfer needed.
- **Testing it**: the header's words from +2098 (on, seq, reply, who, row, shown, late, drawn;
  [the reader](logs/files/2026-11-27-ravager-spell-arrows-hdr.py)); `RAV_NO_ARROWS=1` on `ravdice.py` turns the
  buttons off (the control); `RAV_SKIP=spell_arrows` leaves the objects out of OBJEX2.GFF (no buttons either).
  The arrows go to the pack when the quiver holds other arrows: [the quiver edit](logs/files/2026-11-27-ravager-spell-arrows-quiver.py)
  swaps them in for a shot (or the inventory screen). After a shot the game says "Out of ammo" when the stack holds
  fewer than the round's shots: its own cut, not the Loader's.
- **A new game's party for it**: the title menu forgets the party at each start of the sequel (START GAME with
  no one ADDed plays the ready-made four): ADD them again (the roster keeps a new character). A new 6/6
  Spellarcher with three roster members lost the Draxans' ambush under Computer Control; with HP 250 (a test
  edit, [the script](logs/files/2026-11-27-ravager-spell-arrows-hp250.py)) it was won. C's small icons toggle,
  so a second round of clicks in the next fight turns Computer Control off. The leader starts that game in the
  house west of the ambush's street (world 1072, 1322): `ravgo.py` can't leave it, a click on the street (game
  250,125) can; then `ravgo.py y 1224 x 1839` and Right x4 meet Tyr's thieves.

**The spell arrows' leftovers** (2026-11-27, logs/2026-11-27-ravager-arrow-leftovers.md), all on the Loader's side
(no DSCLOG2 bytes):
- **Starting arrows**: at DONE a new character's known wizard spells are already in selector 320h's bitset, so
  `ravarrows.starting_arrows` (from `ravkitstart.fine_bow`) reads the picks there and swaps the plain arrows (type 6)
  for 24 of each touch spell's arrows, the first in the quiver.
- **Strays**: `ravarrows.return_strays` (RavDiceLog._strays_pass) uses spellarrows.return_strays on the sequel's names
  (299-301), with the map-up word DS:0DABh (1: the map) for SL's inventory_up: nothing moves while a screen is up.
- **The item names**: the dice log named the Loader's own names (256 on) "item N"; `RavGameData.item_name` reads
  them from the table `_write_item_names` wrote (or ravager.item_names()).
- **The hover light**: Turn Undead's handler (9756Eh) draws its hover cases (975AEh, 975F3h) at `push word [2B9Eh]`
  (22h, Turn Undead's place); the press case at [bp-2], the button's own. `arrows_lit_on`/`arrows_lit_off` patch
  FF369E2B to FF76FE90 at 975B2h and 975F7h. A control run with `RAV_SKIP=arrows_lit_on,arrows_lit_off` is still
  to do.
- **The cast sound**: the sequel's sound routine is selector B8h:0A22h (a byte sound number, FFh none); the spell
  record's cast sound is +0Fh, the landing +16h. Chill Touch's and Shocking Grasp's are FFh, Vampiric Touch's 6Eh.
  Not played on a make (it would need DSCLOG2 code).
- **Shooting in a test**: the new Spellarcher's pack holds an Obsidian Dragonsbane +4 and its left hand a Longsword
  +1, which Computer Control takes up: give them to another member first. With a foe beside it a member punches
  though a bow is readied, and Tab and Enter walk up and punch even at range; Computer Control with no melee weapon
  shoots. The game picks a shot's arrows before the round, so a stack swapped into the quiver mid-round waits. A
  PRESS CONTINUE after a refusal shuts with a click on Continue (22,157), not Return. Tyr's thieves leave the map
  after their fight, so a second shot test needs a new game.

**The starting weapon of the first pick** (2026-11-26, logs/2026-11-26-ravager-first-pick-weapon.md):
`ravfirstweapon.fill` in ravlog's `_gear_pass` (GEAR_DONE: after CR_WEAPONS' picks and the game's gear, before the
roster write; `RAV_NO_FIRST_WEAPON=1` on ravdice.py turns it off for a control) makes the weapon in hand over in place
(the record's picture, count, value, type, power, +12h byte, name and plus; its ITEM_NEXT and slot kept). **The
sequel's weapon lines and attack take a double spear that isn't first in the creature's item list (+0Ah) for no
weapon** ("(2x1D1+1)", the bare hand; a lotulis behind a sling is taken): `weapon_first` rotates the records' contents
so the weapon in hand is first, as the inventory's equip leaves it. A double spear specialist swings once a round even
so (the same after a hand equip). The sequel's type records (15 bytes: flags +0, material +4, two-handed +0Bh 40h,
classes +0Ch: air 1, earth 2, fire 4, water 8, druid 10h, fighter 20h, gladiator 40h, preserver 80h, psionicist 100h,
ranger 200h, thief 400h): its daggers (37, 72) lacked the air cleric's bit (ravager.mod_types_table adds it), and its
club (29) has no material (40h), so the sphere rule refuses it to earth and water clerics too (open). The creation
screen: the sphere's AIR clicked off at 240,106, then EARTH 114, FIRE 122, WATER 130; a gladiator needs FIGHTER
(255,29) clicked off first; the weapon window's slots at x 75, 109, 143, 177, 211, 245 and y 32, 66, 100, 134 in
specialize.KINDS' order. A ranger can't pick the bow (greyed). The roster's ADD (a right click on an empty party slot)
lists the roster newest first, rows from y 45, 11 apart.
**Item weights in the sequel** (2026-11-26, logs/2026-11-26-ravager-item-weights.md): the weight is a byte at +2
of each of `OBJEX.GFF` `ALL 4`'s 102 types (15 bytes each; in memory from DS:19CDh), SSI's 0 for 71 of them; each
object's `RDFF` record holds a copy of its type (level 3, kind 4, number the type's), all equal to `ALL 4`. The
Loader writes SL's weights into both in `OBJEX2.GFF` (`ravager.RAV_WEIGHTS`; `RAV_SKIP=weights` for the control).
What reads it: two heavy weapons (779CEh/779E0h, "CANNOT USE TWO HEAVY WEAPONS" DS:1C3Eh), backstab 40 or less
(5C978h), HEAVY in the item box (9A410h), equipping a creature (1D3C9h). **The load check never refuses, in either
game**: the sequel's (77893h) sums GPL field 59h, which only the item-type class has (class 4, offset 2; an item,
class 1, has -1), and SL's (6F248h, field 6) came to nothing too: STR 1 took 45 lb in the sequel, a long sword in
SL. The STR table (weight allowance, maximum press, x10) is at SL DS:0740h, the sequel's DS:07B0h, the same values.
- **Probing it**: [`ravweights.py`](ravweights.py) prints each combatant's items with their weights, the total, STR
  (creature +19h) and maximum press; `--str N=S` sets a STR (a test edit, never saved), `--types` all 102 weights.
- **The control's message**: with the weights left out, two long swords give "CANNOT USE THIS ITEM", a later check,
  not "CANNOT USE TWO HEAVY WEAPONS".

**The kits' starting gear** (2026-11-26, logs/2026-11-26-ravager-kit-start-gear.md): `ravkitstart.kit_gear` then
`weaponchoice.class_gear` in ravlog's `_gear_pass` (after ravfirstweapon.fill, before startgear.fill;
`RAV_NO_KIT_START=1` on ravdice.py a control). **The game's give routine drops what the equip test refuses into the
backpack**: with DSCLOG2's KIT_FORBIDS at CU_SITE a new Ravager's Shield +1 and ring armour (33, 4, 65) land in cells
14-17, not worn, so a kit's gear step must look in the pack too (a weapon there with the right hand empty, armour by its
type's place on the body: the type's +5, 1 the chest, 3 the arms, 0Ah the legs, 5 a hand), and must run before
class_gear, which leaves kit-forbidden armour behind. The creation screen's KITS (232,138), NO KIT (250,106) and the
kit rows (250,114 / 122 / 130); a class at x 255 (FIGHTER y 29, GLADIATOR 37, THIEF 69); NEW on a slot's right-click
menu 40 to the right of the click; DROP (140,129) and YES (140,117) on a member's.

### The port audit's rest (2026-11-27, logs/2026-11-27-ravager-audit-rest.md)

- **DSCLOG2.EXE is checked in**: after any change to `dos/dsclog2.asm`, `nasm -f bin -I ./ -o DSCLOG2.EXE
  dsclog2.asm` in `obsidian-edition/dos` before a play (the Loader starts the file, not the source; a stale
  one shows its header words past the end as 9090h, 37008, in `ravaudit.py`), and `test_audit_builds` fails
  until it is rebuilt.
- **`ravaudit.py`** prints DSCLOG2's audit words: LOCK_BARRED's rows, lock_bars (+2116), gl_bare (+2118),
  ai_walls (+2120), kreen_cuts (+2122), the region and the talk thing.
- **The gladiator's armour (GL_ARMOUR)** in the ambush: `ravitems.py 3 --bare` puts Gerakis's leg and chest
  armour (slots 6, 9) in pack cells 21, 23 (a test edit, never saved); attacked so, his AC was 9 and gl_bare
  rose (0 to 3); `--dress` put it back, AC 8, gl_bare held. To have the foes reach him before the party ends the
  fight, the foes' HP 300 (a scratch `foehp.py`: creature +0 for every creature combatant from 4; the region's
  bystanders too, harmless in a throwaway copy). Gerakis is below 5th gladiator level, so the bonus itself
  (1 a 5 levels) is 0 either way: the count is what shows the test.
- **PSP_SCORES** at the ambush's level ups: the creation record (DS:142Dh) held WIS 18; with the fix
  Terrannus and Thy'rokh (WIS 19) got 28 PSP more and Gerakis (WIS 15) 28, where the game gave 26, 26 and 34:
  each member's own WIS (2 x WIS - 10), CON and INT the game's own to 22 (checked against the three gains).
- **KREEN_CLAWS**: kreen_cuts counts 2 for each of Thy'rokh's natural attacks seen (the magic test runs twice
  for one).
- **The dice log's PSP and ability lines** with a test edit (Ar'Anda's creature +2 PSP -5 and +19h STR +1, put
  back after): "spends 5 PSP (96 -> 91)", "STR 18 -> 19", then "regains" and "19 -> 18". A level up's higher
  most shows as "regains N PSP". Effect lines: "Thy'rokh#2 gives Paralyzed to Draxan#21", "Controlled ends on
  Draxan#26". With `--numbers` a creature gone by the fight's end was "?#21" (ravdice.py's suffix on "?"
  defeated the log's kept name): fixed, it says the name it kept.
- **The ambush's end is often not logged**: the last foes' blows and the kills are missing and the summary says
  "0 kills" (seen in 3 of 3 runs; known since logs/2026-11-24-ravager-48h-sheet-play.md). Not looked into.
- **Starting a new game from `ravstart.sh`'s title menu**: a click in the window first (the pointer is not
  captured until then), S, then the dragon picture waits: Escape, a few seconds, Return gives the opening talk
  (3, Return x4: the ambush). Computer Control: C, then a `ravclick.py` move to capture the pointer, then the four
  lower icons.
- **A lock to play the lock rule**: `gpl.checks` on the sequel's GPLDATA.GFF decodes 257 of its 350 scripts and
  finds one open-locks check, in GPL 9 (a grate with a trap: "finds a trap concealed in the grate!"); where that
  is in the game is not known yet, and the 93 scripts that don't decode may hold more.

### A control run: RAV_SKIP

(ravstart.sh with `RAV_LOADER=1`; the contract since 2026-11-27, PR
#235). `RAV_SKIP=NAME,NAME,...` leaves those parts of the Loader's work out of the copy, so a test can
show the game's own behaviour beside the mod's. The names are read once, all together:

| Kind | Names | What is left out | Files changed in the mod's `dos` folder | Expected |
|---|---|---|---|---|
| An executable patch | any `name` in `dsloader.ravager.PATCHES` | the patch's bytes put back to the game's (each checked to be the patch's first) | `DSUNLOG2.EXE` | the game's own behaviour at that site |
| A script fix | any key of `ravager.SCRIPT_FIXES` | the fix | `GPLDAT2.GFF` | the game's script |
| An object part | `mod_types`, `new_items`, `new_spells` (the spellbooks only, `ravgear.BOOKS`: the spells stay), `item_shine`, `weights`, `spell_arrows`, `melee_range` | that part of the objects, all the named parts in one write of the copy | `OBJEX2.GFF` | e.g. `weights`: the sequel's items weigh 0 again |
| `spell_arrows`, also | the same name | the arrows' icons and names too | `RESOURC2.GFF` as well | no arrow buttons, no arrow objects |
| The redrawn figures | `figures` | Codex's redraws (`ravfigures`): the pictures, the moved objects, the Tarrasque and drakes, the dining room | `OBJEX2.GFF`, `RESOURC2.GFF`, and no `RGN03A2.GFF` | the sequel's own figures. DSCLOG2's COPIED word (its header's +146) has bit 8 set once the game opened `RGN03A2.GFF` |
| Shattered Lands' interface | `sl_interface` | its 45 screen pictures and 221 icons (`ravui`) | `RESOURC2.GFF` | the sequel's own screens and icons: `BMP 10000` in the copy is the game's |

Any other name stops the script with `RAV_SKIP: no such patch NAME`; `$WORK/rav.conf` starts with
`# left out: ...` when the run went ahead. Prerequisite: `RAV_LOADER=1` (without it nothing is copied,
so nothing is left out); the new items' pictures come from `$GAME`'s Shattered Lands (`RAV_SL=` for
none, which also leaves out the new items and the spell arrows' objects). To check a run, look at the
copy (the bytes at the patch's offset, or the chunk in `OBJEX2.GFF`), not at the printed list.

**Before 2026-11-27** each object part was written in a run of its own, each from the game's file, so
with two or more object parts named only the last was left out. No play log named two object parts in
one run (the controls on record name patches, or one of `weights`, `item_shine` and `new_spells`), so
their results stand. `spell_arrows` also left `RESOURC2.GFF` as it was then.
### The audit's leftovers (2026-11-27, logs/2026-11-27-ravager-audit-leftovers.md)

- **The effect module** (618h, file 81770h): the add check 0AF9h (a switch of 19 effects at cs:0FB4h, its default
  "jmp 0F1Eh" at 822A1h; [BP+6] the thing, [BP+0Ah] the effect, [BP+0Ch] a far pointer to the record's +9 byte,
  where Confused 21 and Controlled 20 save the creature's side, +15h) and the end 1017h (a switch at cs:13BAh, its
  default "jmp 12E9h" at 827D6h; DX the record's index; case 120Dh puts the side back from +9). Berserk 7 is in
  neither; effect 102 (named Berserk too) is Tenser's Transformation, whose case 106Dh only clamps the hit points.
  The AI's side routine 618h:000Eh rolls a d2 side for Berserk (byte 0 bit 7) and Confused: Shattered Lands' bug
  shared. DSCLOG2's sites 245 and 246 sit on the two defaults (the handlers move the way back's IP at [SP]).
- **Effect records** (load + 3E71h):24Dh, 10 bytes (owner +0, caster +2, spell +4, effect +6, charges +8, extra +9),
  the count at DS:2100h; the owner is the combatant's number. Effect names: 31-byte records at file 41A70h.
- **A test Berserk**: RESOURC2's DATA records (73 bytes, the effect at +19h) of the ten effect-20 spells (2, 39,
  61, 82, 94, 131, 230, 239, 255, 256) and Armor (0, effect 5) made 7 in the Loader's copy (`dos/RESOURC2.GFF`,
  rewritten by every start, so the edit goes after ravstart.sh). In the ambush Thy'rokh's Charm Mammal took on a
  Draxan (a natural 1); Ar'Anda's Armor on Gerakis from USE gives Berserk out of a fight.
- **An effect outside a fight** didn't run down while the party stood or walked for some minutes (Berserk with
  1 charge, a test edit): its charges are spent by rounds or longer rests, not by a short walk.
- **Ability scores** (0628h:0039h, file 8527Bh, module 83400h): an item power 140h-147h counts (charges under 10h
  add, under 20h set) only when 568h:7Fh's top place is 10h (worn; the pack's is 4). Called by the ready 77C5Ah
  and unready 77D07h (powers 140h-147h only), the effect end and remove, and spell handlers. The unready
  recomputes while the item still counts: one taken off to the pack keeps its score until the next recompute.
- **The combatants' table** ((load + 3F49h):C33h, 3 bytes: kind, word index; creatures [DS:19C9h], 31h bytes):
  a killed creature leaves it at once, often before the dice log's next look saw its last fall; its record keeps
  its name, which is how hp_changes still finds it.

### The final items (2026-11-27, logs/2026-11-27-ravager-final-items.md)

- **The event queue**: a far pointer at DS:2A63h, the count at DS:2A6Bh, 11h bytes an event: +0 the time (a dword,
  the game clock's seconds), +4 the kind (7: an effect ends), +5 the thing (a word: the combatant's number, a party
  member 0-3 out of a fight too), +7 the effect's handle (the effect record's +7). A timed effect has one; an
  effect that runs down by uses (Armor) or an item's power (charges byte a stray 15) has none. **Bringing an end
  forward** (a test edit): write the event's time as the clock + a few seconds; out of a fight the clock (the far
  pointer at DS:9C0Ch) runs at about one to two game seconds a real one.
- **The effect records** (load + 3E71h):24Dh, 10 bytes: +0 owner, +2 caster, +4 spell, +6 effect, +7 handle,
  +8 charges, +9 extra (Berserk's kept side); the count DS:2100h.
- **The Effects screen's cells** (8AB13h, the event at [BP+0Ah]): each cell's name is a far push of 318h:effect x 31
  (the 31-byte name records: name 29 bytes, the icon), the segment word fixed up by the overlay manager (8ABB9h),
  then "push 2C06h / push dword [1431h]" at 8ABBDh and the far call 5F0h:61h. The character on show is
  370h:0B44h. DSCLOG2's EF_CHARGES (site 247) sits on the second push and changes the name's far pointer.
- **The sound routine** B8h:0A22h is resident (load + 1C5Fh, file 22212h), a far call with the sound byte at
  [BP+6]; the flags DS:13F7h and 1435h say sound is on. The touch spells' cast sounds are their records' +0Fh:
  Chill Touch and Shocking Grasp FFh (none) in the sequel, Vampiric Touch 6Eh (SL's 4Eh, 51h, 6Eh).
- **The sequel's spell records are read from RESOURC2.GFF each cast**: an edit of the Loader's copy (an effect byte
  at +19h of the 73-byte DATA record, `gff.index_places`) takes at once in a running game. Haste (29) made
  Berserk 7 and cast from USE out of a fight landed on the caster (Haste's area), a timed Berserk with an event.
- **The sequel's open-locks checks** (DO_ACTION 3 read from every byte of the 350 scripts, the 93 that don't decode
  whole too): GPL 9 at 4378 (the Pyramid's grate under the Garden), GPL 40 at 6218 (Magnolia's chain, Humbleton
  Forest), GPL 89 at 7826 (the mind flayers' chest; MAS 58's use trigger, place 7120, object -5102), GPL 264 at
  1154 (the Generoe acolyte's cage, with a jammed-picks lock-out of its own). None near Tyr.
- **A script anywhere, for a test** (never saved): the triggers are 13-byte records at far DS:40C0h (+0 the place,
  +2 the script, +4 the object), their lists' heads at (load + 3C10h) +0Fh talk, +11h attack, +13h look, +15h use,
  +17h use with, +0Bh in a record the next. Point every talk trigger of the region at (place, script) and talk to
  anyone (the look pointer, two right-clicks, on a person): the script runs. Put them back after.
- **A computer caster's choice**: under Computer Control, Ar'Anda knowing Wall of Fog alone (her 15-byte bitset at
  3F3DCh, a test edit) in Tyr's thieves' fight fought with her weapons beside the thugs and cast nothing
  (ai_walls 0, the fight over in 3 rounds). Why: Wall of Fog's AI weight is 0 (the next section).
- **The USE screen out of a fight** from the map: the inventory's portraits (22,25 for the first), its bottom icons
  at y 188 (197 the inventory, 218 USE); on USE the kind button (151,171) and LEVEL (197,171), the spells' row at
  y 60 (x 175, 194, ...), the name in the bottom bar under the pointer.

### The Effects screen's other lines and the computer's walls (2026-11-27, logs/2026-11-27-ravager-effects-lines.md)

- **The AI's spell choice** (5EEB6h, called by the area cast 5EE00h, 570h:20h, from the computer's turn 5BEB5h): for
  each spell of the list (588h:52h with 3) a party member's must pass 628h:7Fh or 588h:48h; its score is rand() x
  the spell's **weight** / 8000h, the weight a signed byte a spell at selector 310h (segment 3C78h: file 5200h +
  3C78h x 16), the best above 0 taken. **Wall of Fog (11), Wall of Force, Wall of Stone, Death Fog, Prismatic Wall,
  Wall of Ash, Blade Barrier, Wall of Thorns... weigh 0: the computer never casts them.** Wall of Fire (54) and Wall
  of Ice (55) weigh 20, the priests' Wall of Fire (207) 40. The turn tries a spell only with the creature's +1Ch
  (INT) above 9, its 308h:+B2h byte 0 (set when a try finds nothing), DS:420Ch not 1, the target within 24 squares.
  **To see a computer's wall**: [walls.py](logs/files/2026-11-27-ravager-effects-lines-walls.py) (Ar'Anda knows Wall
  of Fire and Wall of Ice, first level 9), Tyr's thieves under Computer Control: she cast Wall of Fire on her
  first turn, a thief beside her (ai_walls 1).
- **One effect a spell**: a second cast of a spell already on the creature takes the slot and adds nothing; to put
  several effects on by RESOURC2's effect byte use different spells. Armor's handler sets its effect (5) itself,
  whatever the byte.
- **The Effects screen's other lines** (DSCLOG2's EC_MOD, EC_REFLECT in EF_CHARGES): the Loader writes EF_STATS
  (the tail's, offset at header +2134: a member's Enlarge level, then the AC of Barkskin, Flesh Armor, Magical
  Vestments, -128 none) each quarter second; the sequel's AC routine (85BA7h) gives the armour spells SL's AC
  (6 - level/4, 10 - level, 5 less 1 a 3 levels past 5). `ravaudit.py` prints EF_STATS and ef_mod_lines (+2136).
- **The USE screen's buttons out of a fight**: MAGE (151,171) picks the kind, LEVEL (197,171) cycles the levels
  (back to 1 after the last the character casts).

### The sequel's spells in a fight (2026-11-21)

- **Teaching a wizard spell**: Ar'anda's known-spells bitset, 15 bytes at 3F3DCh in the Draxans' fight
  from `ravhold.sh` (bit n spell n; Enlarge bit 5 of the first byte); her USE screen then shows it
  at once (LEVEL cycles 1, 2, 3 with clicks on (197,171)). The spells by number: wizard 0-114,
  priest 115-234, psionic 235-268, the monsters' powers after (RESOURCE.GFF's DATA names).
- **Casting on a party member**: on USE, click the spell (it hangs on the pointer, its name in the
  bottom bar), then click the member's portrait on the same screen (Gerakis's at (120,117)); the
  slots line drops by one. An area spell (Fireball) closes USE and aims on the map instead.
- **A class for a test**: the sheet's classes at +1Bh, levels +1Eh (three each); Thy'rokh made a
  ranger by writing 15 and 12 there (`ravfight.py until 2` first, for his turn).
- **The effects in force**: a word count at DS:2100h, the records 10 bytes each at (load + 3E71h):24Dh:
  the owner, the caster, the spell (words), the effect (byte +6).
- **The real damage, not the log's**: the dice log's "hits ... for N" is its own sum; the target's
  "now X/Y HP (-Z)" lines are the game's, so compare the two when a rule changes the damage (Enlarge
  found so: the log's line had missed it).
- **A control run**: `RAV_SKIP=NAME,...` with `RAV_LOADER=1`: [the controls, what each changes and how
  to check it](#a-control-run-rav_skip).
- **A scroll for a test**: copy a real scroll's item record (in the after-ambush save, item 58: entity
  -7939h, type 77, a wizard scroll) over a party member's carried item (+0 the entity, +0Ah the type,
  +14h the name), its power (+10h) the spell + 1; on the inventory screen right-click the item, then
  click the spell's icon at the box's right (`ravclick.py X Y right`; xdotool alone doesn't move the
  game's pointer). The party's items are the first item records (Ar'anda's 1-3 there).
- **The sequel's shops** (2026-11-25, logs/2026-11-25-ravager-shops-scrolls.md): the shop is SL's at 90xxxh
  (its list of the merchant's items, 10 bytes an entry, at the far DS:619Dh, built by C8h:2196h from the
  merchant's thing DS:1A30h, SL's 179Ch; the thing on the pointer DS:1A32h, 523 as SL's 179Eh; its slot
  DS:1A34h). The price is the item's +6 word as in SL; then the sequel's own markups, 370h:36h buying
  (914A5h) and 370h:34h selling (915B8h), 0 at Notaku's. The reads: 90E2Ah the price shown, 90AA7h the
  price charged (times the count for a stack, 2E8h:357h the money), 9036Ch the list's greying, 90F4Dh what
  the shop offers ("I'll give you %lu$"), 91043h the free of the sold item's thing (C8h:2410h, nothing for
  270Fh). Items in the merchant's list carry backpack cells 14+ till the shop opens and numbers 1, 2, 3...
  after. **A shop in Tyr**: Notaku's stall in Shadow Square (map object 33 at world 312, 904; from
  `ravager-after-ambush` the street to y 1224, west along y 1224 to x 296, north to y 936), the look
  pointer on him, the Look box's first button talks, "Show me your goods." (fourth reply after declining
  his job). He sells magic items, a one-use scroll of Shield at 300 among them. The shop's buttons: MORE
  (254,164) pages the list and draws it again (twice for the first page), SELL (297,164) offers for the
  item on the pointer, TAKE IT at (120,92) or (145,92) as the box falls. `ravshop.py` reads the shop and
  edits CHA, INT, scrolls and known spells.
- **The sequel's shops and its spellbooks** (2026-11-26, logs/2026-11-26-ravager-spell-books.md): GPL op 24h (36)
  opens a shop on the merchant its argument names (`('n', -153)` the weaponer, or the talker): scripts 43, 53, 54,
  143, 144, 148, 153 (Notaku), 155, 157, 158 (the ranged stall 323), 221 (the weaponer). Of the sellers only Notaku
  has spellbooks (OBJEX.GFF: 31402, 31023); other wizards' books are carried (Melantha 51, Fermin 160, Kalaobuta
  290, Solurnis 436, Raenika 496, a Crypt body 3088). The sequel's wizard spellbooks are 31002-31061 by level (3000
  a level, all one picture: their OJFF's icon, BMP 1969; name 4, "Spellbook"); 31190-31199 are free. **A merchant
  with more than 12 pack items** (Notaku with the books: 14): the game gives cells 14-25 and 255 to the rest, and
  the shop lists all 14 (three pages). **A spellbook can't be read in the shop's screen** (the box's icon clicked
  closes the box, nothing learnt): leave the shop, open the inventory. Money for a test:
  `logs/files/2026-11-26-ravager-spell-books-money.py N` (the dword at (load + 3C13h):357h). The opening ambush's
  Computer Control: the USE screen's first click only takes the mouse (a click on the window first).
- **The sequel's dialogue window and the Loader's tabs** (2026-11-25, logs/2026-11-25-ravager-loader-tabs.md): the
  window's input is 87BA0h (SL's 7CE83h, the same code with a check more; the dialogue stub 476Ch's entry 25h):
  (kind, far text, word), SL's kinds (0 a reply, its number in the word; 1 a portrait; 2 text, word 115; 3 the
  replies shown), "END" each page, "CLOSE" once the last is clicked away. The replies' copies at DS:6356h + n x 33h,
  the row clicked DS:25BAh (FFh till then), the scroll DS:6321h (SL's 5537h, 1F0Ah, 5502h); the thing a script was
  started on at (load + 3C13h):365h (SL's 3781h). DSCLOG2's TEXT (sites 93, 94) copies it and the message box into
  its text buffer; `ravtext.py` prints the last records. To talk to Uhubito from `ravager-after-ambush`: a click on
  his office's floor (game 240,140), then 220,170, the look pointer (two right-clicks) on him (210,165), the Look
  box's first button (230,188). A second click at (220,170) straight after the walk-in can open his talk by
  itself and choose a reply. That talk's "talked to" (`ravtext.py`) was thing 16, and the Dialogue tab kept
  "Portrait 18" after CLOSE: no name learned (logs/2026-11-25-ravager-loot-tabs-join.md; the tabs log's talk,
  through the Look box, learned "Caravan Master"). The Loader's window there: `python3.12 -m dsloader view --pid`
  on Xvfb `:56` 1440x900 (tabs at y 132: Dice log 660, Dialogue 752, Journal 841, Spells 911, Memory tools 1013). The sequel's
  global numbers' pointer (SL's DS:1356h) isn't found by `ravds.py --fuzzy`, and 93 of its scripts don't decode
  with SL's decoder (those that do use numbers up to 150): the journal can't keep its head in a save there yet.
- **The sequel's message box** (560h:2Ah at 59A0Bh; its stub's entry 5DBh in the overlay at file 59430h):
  opens window 2905h (5B0h:48h, kept at 300h:7), writes the text, waits `[26B7h]` x 100 ms with the game's
  delay (0:12FAh, Borland's, on the PIT) and closes it. It was never seen: the windows are drawn only as a
  new picture is shown (3328h:0B4Ch, from the main loop; 0B0h:2A81h with 1 marks one due and shows it), and
  the delay was over at once (15 s asked, the inventory answered 4 s after). DSCLOG2's MSG_SHOWN does both
  (the picture, then the time on the BIOS clock). **Overlay stubs**: a far call to a selector below 600h
  is an overlay stub; its target is the stub block's (selector / 8 in the segment table at the FBOV
  header's exeinfo) descriptor's payload + the area (as `build_image.py` reads them) plus the stub's entry
  word (stub + 2, the stub at block + 20h + 5n).
- **XP, THAC0 and slots in the sequel** (logs/2026-11-22-ravager-class-tables.md): a sheet's XP is its
  +0 dword; the class needs the XP table's entry at the index **of its level** (an 11th-level cleric
  needs entry 11, 900,000, the 12th level's), and the level up caps the XP at the entry 3 above. A
  combatant's THAC0 is the creature's +16h, worked out only at a level up (so an edited level shows its
  THAC0 only after one). The slots left are the game's bytes at DS:4469h + level (wizard) and
  DS:4474h + level (priest), a member 22h on; a rest at the Roost's ring sets them from the slot routine.
  On the Roost's route the "look" pointer two right-clicks from the arrow is the face (talk) icon:
  it is the one that talks to Reyhan and rests at the ring; after Reyhan's "Goodbye." and Space one more
  right-click gives the arrow. The second doorway's steps were at game (253, 90), then (253, 118) to step
  through, the ring at (267, 121) after Up 6.
- **Regeneration and poison saves in the sequel** (logs/2026-11-22-ravager-con.md): regeneration runs
  outside a fight once the clock is 300 s past DS:19B8h (a dword): put that back 3600 s and it runs at
  once (a member needs CON 20 or more). A save that takes CON's adjustment is the paralysis/poison/death
  save (kind 1): Stinking Cloud's (spell 22, `ravknow.py 22`, USE level 2, the third icon at 213, 60), not
  Hold Person's (the spell save). A foe made a dwarf: its sheet's +12h 2 (the kind's sheet, shared).
- **Ages in the sequel** (logs/2026-11-22-ravager-ages.md): the sheet bytes no instruction touches are
  +41h alone (+3Dh and +3Fh, which a byte search found free, are the high bytes of the sound words
  +3Ch and +3Eh: see the party's sheet above), so the age is at +41h. The game clock: scale a byte at
  DS:9C0Ah, the dword through the far pointer at DS:9C0Ch (seconds x scale); it stands still during a
  turn and runs with the fight's rounds. Ar'anda's Haste: USE, LEVEL 3, the middle icon (196, 60); it
  aims on the map (an area spell); with class restrictions on she can't cast it (rules 4804h for a test).
- **The DUAL window in the sequel** (logs/2026-11-22-ravager-dual-class.md): the inventory (I), a
  right-click on a portrait (game 30, 69 for the second member) gives EDIT NAME / DROP / DUAL (CANCEL
  when it isn't offered); DUAL at game (70, 98), the window's EXIT at (219, 146). Only a human (sheet
  +12h 1) gets it; a dead member (creature +14h 7) can be made Okay with +14h 1 and some HP.
  Its class buttons in game pixels: FIGHTER (189, 87), the others about 9 apart down the list. A
  class taken puts **the new class first**: Terrannus (cleric 7) as a fighter has classes 9, 2, levels
  1, 7 and class bits (+10h) the fighter's alone (logs/2026-11-22-ravager-class-restrictions.md).
- **An equip test in the sequel** (the same log): the inventory on the member, the chest armour (game
  173, 80) to the backpack (195, 35) and back, the shield at (65, 90); the item's worn slot (+13h) says
  how it went (9 the chest, 255 still on the pointer). A member's classes and race can be test-edited
  (sheet +1Bh, +12h) with his class bits (+10h) left, so that the game's own test passes and only the
  Loader's rule can refuse.
  A bow goes in the slot at the top left (65, 50), which the game lights when the bow is picked up
  (in a hand: "ILLEGAL PLACEMENT"). The inventory's bar, hovered: VIEW CHARACTER (170, 185), VIEW
  INVENTORY (195, 185), CAST SPELL/USE PSIONIC (217, 185), CURRENT SPELL EFFECTS (242, 185), GAME MENU
  (267, 187), RETURN TO GAME (302, 185). On the View Character screen a right-click on a portrait
  ((70, 56), (120, 56), (70, 117), (120, 117)) gives the second portrait menu (EDIT NAME / DROP /
  DUAL or CANCEL; its third line at (165, 81), so a click there on DUAL opens the window: EXIT 219, 146).
  A priest's weapons: SL's rule counts every class's sphere (a human's earlier class too), so an air
  ranger's sphere lets a cleric use a bow: test a ranger's bow with an earth ranger (class 14).
- **`ravthief.py --helper` and hear noise**: for Terrannus the routine leaves early for hear noise
  (8C6C1h, after its test at 8C802h), the rule's site never reached, and the emulator then runs on past
  the routine's return: its number for that skill is no reading (94 here). Check the trace for an INT
  F5h before trusting a skill's line.
- **After a load, and at the edge** (2026-11-24, logs/2026-11-24-ravager-48h-sheet-play.md): after LOAD
  (the title menu's or F2's) a picture (the dragon's orb, a progress bar under it) waits for a click
  (`ravclick.py 160 100`). Once, after F2, `ravclick.py` found the game's pointer stuck at the LOAD
  button and the picture stayed; an `xdotool mousemove` with a `mousemove_relative` then showed the map. The camera scrolls while the pointer rests at the window's edge (the
  save screen then shows another part of the map behind it); H brings it back to the party. A Computer
  Control click on USE can fail to take (a member's turn then waits for ever): look for the orange lit
  icon by each portrait and click again.
- **`ravload.sh` doesn't stop an older DOSBox**: two `ravload.sh` runs leave two (the tools take the
  newest). Kill the old one by pid before a second load.
- **A level up for a test in the sequel** (logs/2026-11-21-ravager-int-levelup.md): in `ravhold.sh`'s
  fight lower a class's level (the sheet's +1Eh + the class's place) **and** its best level reached
  (+39h + the place): the game gives a new level's extras (a preserver's CHOOSE A SPELL) only for a
  level above +39h. Ar'anda (member 0: preserver 6, psionicist 6, class 17 7; 40,000 XP) made a 5th-level
  preserver levels up when the fight's XP comes, after its "Each party member receives 10000" box is
  clicked (`ravclick.py 160 100`). Her INT is the creature's +1Ch **and** the sheet's +18h (the
  creature's is written again from the sheet after a fight). The foes' HP: creature records whose
  +15h is 7 (`hpup.py`-style; the party's aren't those). **The helper's rules are 0 until the dice log
  attaches** (`ravdice.py`: RavDiceLog writes RULES_PORTED): a level up with no dice log is the game's
  own, a control.
- **The weapon window at a level up in the sequel** (logs/2026-11-26-ravager-high-levels.md): DSCLOG2's
  LV_WEAPONS (site 150) opens it after the level up's other windows when a member has fewer specs than
  `lv_due` (a gladiator 2/3/4 then one more every 4 levels past 9th; a fighter a second at 13th). Set a member
  with `ravlevel.py set` and its specs with `logs/files/2026-11-26-ravager-high-levels-specs.py MEMBER
  KIND,...` (the packed form kept, the age roll too; specs 5-8 in +45h-+47h), then win the fight. The 640x480
  window maps to ravclick.py's game coordinates as x / 2, y / 2.4 (the slots from (75,37), 35 apart, rows at
  y 37, 70, 100, 133); grab the screen between box clicks at (160,100), as one can land on a slot. The
  sequel's own party has no specs, so any of their level ups asks too. The Effects screen pages the spec
  lines with MORE (a click at (180,146)).
- **Kit spell slots in the sequel** (logs/2026-11-26-ravager-kit-slots.md): the slot routine 626B7h
  (member, kind 1 wizard / 2 priest, spell level) runs each class place 0-2, asks 62B45h whether the class
  casts the kind (spell 8 at 627D3h for wizard, 73h at 62818h for priest: wizard classes 11 and 18 alone,
  so a thief is never asked), then 62A10h for that class's count at 62893h (ADND_SLOTS, site 34), and sums.
  So the kits' slots go per class there (SLOT_BEHIND, BEHIND_LEAST, KIT_TABLE), and a Shinobi's thief class
  is let in by SHINOBI_MAGE (site 190 on 627D6h's "add sp,4"). The caster level routine 97DC5h starts its
  best at 0 and compares signed (`cmp dx,di / jng`): a class whose level less the drop is below 0 counts
  0, never less. A test: `ravload.sh ravager-roost` on a throwaway copy, the members edited (`ravkits.py
  set`, `levels`; kit byte 80h for a control, so the Loader leaves the own party's features alone),
  **Terrannus made alive** (creature +14h 7 in that save: the rest skips the dead), the Roost's rest (the
  ring was at game (267,121) in one run and (267,110) in the next: grab the screen after Up 6), then
  `ravlevel.py show` (the casts left) and `ravlevel.py counts kt_count sb_count sh_mages`. The USE screen
  offers MAGE or CLERIC by class and spells known, not by slots.
- **Kit PSP costs, hit dice and the hit's mark in the sequel** (logs/2026-11-26-ravager-kit-psp-hd.md): the
  power routines are SL's code at 615xxh-61Fxxh with the powers' table at 3D0h:7E0h, **3 bytes a power** (+1
  the cost, +2 the upkeep; SL's 8), BX the power x 3; the powers are SL's 34 in SL's order (Enhanced
  Strength 0Fh, Domination 14h/15h). The USE screen's hover ("PSIONIC BLAST 18 10") reads the table (97135h),
  so it shows the plain cost whatever the kit. A member's PSP is the creature's +2; ravkits.py's 200 is held
  to the sheet's most (+0Ch) at a round's start. A failed power check costs half, "Message: psionic power
  check fails" in the dice log. The level up's hit points (94F60h: `[BP+8]` the class, `[BP-4]` the sheet)
  read the group's die at 95014h and its gain past the dice at 95000h; to see a level up's most PSP whole,
  make the sheet's +0Ch 1 first (the game writes it only when more). **The hit's mark** is a byte a creature
  at 308h:0B2h (the helper's `hr_seg` holds the segment the last hit used: 3DF1h in that run), cleared at a
  round's start; a member hit before its turn in the round has its spells (and powers) crossed out on USE.
  To have a member hit before her turn, make her DEX 3 (creature +1Ah, sheet +16h; a test edit): she acts
  last. A kit byte changed between turns takes at once (a control in the same fight). **Tyr's thieves**:
  `ravgo.py y 1224 x 1839` from `ravager-after-ambush`, then 2 and Space; `ravfight.py fight` there often
  gets "NO PATH FROM HERE": click the foe yourself (the walk arrow over a foe shows its to-hit, "7+ (70%)").
- **Kit casting levels, cures and spells known in the sequel** (logs/2026-11-26-ravager-kit-casting.md): the level a
  spell is cast at for its duration and damage is 628AFh's (SL's 5E25Ch; [BP+6] the caster, [BP+8] the spell): a loop
  over the three class places ([BP-1]) keeping the best level in DI, ending "inc byte [bp-1] / cmp byte [bp-1],3 /
  jge / jmp" (629FEh) and "mov ax,di" (62A0Ah); KIT_CAST_LEVEL (site 205) takes the INC, so nothing on the stack
  moves. The spell levels a member may cast are 97DC5h's (the caster level), not this one's. **The handler for spells
  with rules of their own** is SL's at other addresses: its switch at 656D0h (81 cases at CS:28C1h, the overlay's CS:0
  at file 642E0h); Cure Light Wounds (117) at 6648Ah ("push 80001h", jmp 6653Dh, the dice call, then 66545h "push ax /
  jmp 65811h"), Cure Serious Wounds (170) 2d8 + 1 at 66493h, Cure Critical Wounds (194) 3d8 + 3 at 664A5h (after
  628h:8Eh with D5h), Blood Flow (166) at 6652Bh (healing only on the caster's own side), Cell Adjustment (248) at
  664C5h (CELL_HEAL, site 11), all to 65811h ("push di / call 628h:43h": the heal). **The spells' damage**: 80278h
  (spell, level, a near pointer to the most) called by the area routine at 7E7A0h (stored at 7E7A6h "mov [bp-14h],ax",
  the most [BP-16h]; SL's 754ECh) and the one-creature routine at 7F721h (7F727h "mov [bp-6],ax", the most [BP-8];
  SL's 761A9h). **The sequel's spells for the kits** (RESOURCE.GFF's names): wizard spells 0-72h, priest 73h-EAh;
  Cure Light Wounds 117, Cause Light 118, Cause Disease 149, Blood Flow 166, Cure Serious 170, Cause Serious 171, Poison
  179, Cure Critical 194, Cause Critical 195, Slay Living 204, Heal 210, Harm 211, Waters of Life 215. The sphere byte
  20h (the druids') is the sphere of the cosmos: Abjure, Cloak of Bravery and of Fear, Cure Serious and Critical
  Wounds and their Causes, Free Action, Neutralize Poison, Poison, Protection from Evil 10', Dispel Evil, Rainbow,
  Raise Dead, Slay Living, Blade Barrier, Heal, Harm, Wall of Thorns, Confusion, Creeping Doom, Restore, Energy Drain,
  the three Symbols, Rift. DSCLOG2's counters `kc_levels`, `kc_cures`, `kc_causes`, `kc_cosmos`, `kc_barred`,
  `kc_cells` (the header's +2064 on): `ravlevel.py counts kc_levels ...`.
- **A kit's hit points and PSP at creation in the sequel** (logs/2026-11-26-ravager-kit-psp-hd.md, step 4):
  the creation rolls' overlay is stub segment 5C0h: its 66h the hit points' routine (6D1EDh; it copies the
  sheet being made to the member's party sheet with 6E6D8h, rolls each level there by the level up's
  routine 690h:20h, and copies it back with 6EE5Eh, which leaves a taken-back kit, KIT_OPEN, none), its
  6Bh the PSP routine (6D75Dh, all its own code, no call to the level up's). The least and most hit points
  are DS:42D8h and 42D6h, the numbers' places DS:1224h (hit points) and 122Ch (PSP), x then y, their
  backdrop words at 368h:70h/84h and 72h/86h, the backdrop routine the root's 0C8h:3B30h, the numbers
  drawn by the panel's stub 5B8h's 3Eh and 43h. A creation sheet's class is 1-8 (5 preserver, 6
  psionicist; the copy to the party sheet makes it 1-17). `ravkits.py page` prints the hit points with
  their range, the PSP and the creation counters. A 7th-level human preserver with CON 18 has 21 to 42
  (a Battle Mage 21 to 56, an Arcanist 21 to 35); a click on CON moves the range (CON 15: 7 more, 14: none
  for a preserver). The DROP and EDIT rows of a member's menu are 12 apart (EDIT at 110,57 for slot 1;
  110,67 is DROP: CANCEL its question at 110,82).
- **Abilities and a spell cast for a test in the sequel** (logs/2026-11-21-ravager-flame-biofeedback.md):
  the abilities STR DEX CON INT WIS CHA are the creature's +19h on and the sheet's +15h on (write both). A
  spell cast in `ravhold.sh`'s fight: USE (the top-left icon, `ravclick.py 22 17`), LEVEL (`ravclick.py
  197 171`, the screen's bottom row) round the levels with spells known (the screen opens on the last
  level shown), the spell's icon (y 60, x 175/194/213/232; the name shows in the bar
  below when the pointer rests on it), then click **on a combatant** (`ravfight.py state` gives their
  places: game x = state x + 7, y = state y + 19 in this street); a click on bare street does nothing. A
  spell cast again (Flaming Arrow's second bolt) puts its icon up as the pointer for the next target.
  For a caster's next turn put the others under Computer Control and use `ravfight.py wait` (with its
  HP raised the party holds); `ravfight.py until 0` ends the others' turns, so the Draxans win.
  Aiming: a foe under the spell's pointer shows red (a friend yellow, and a hold can't take one);
  a figure drawn behind another can't be picked; the places from `ravfight.py state` plus about
  (7, 14) hit the figure in the ambush's street. The undead are the sheet's race (+12h) 9: a test can
  make a kind undead there (the sheet is shared by the kind). A caster's level for a test: the class
  level (sheet +1Eh) is the cast's level (`probe.py level=N`).
- **Turn Undead in the sequel** (logs/2026-11-21-ravager-turn-undead.md): the opening party's cleric
  is Terrannus (member 1, earth cleric 7); his USE screen has a TURN UNDEAD icon under SPELLS LEFT
  (`ravclick.py 157 145`). It puts a circle round the pointer on the map; a click turns every undead
  foe in it. Reach is about 100 game pixels from him, and walls block it (the pointer shows a barred
  sign: a click there does nothing); the ambush's real undead (Giant Skeletons, sheet 9) stand far
  off, so make a near kind undead (its sheet's race, +12h, 9; hit dice +1Eh). `ravfight.py state`'s
  object numbers are the combatants' (a dead one's record is all FFh). `ravfight.py until 1` gives
  him the next turn; the camera moves with whoever acts, so read `state` again before aiming.
- **Casting in the sequel's fights** (logs/2026-11-22-ravager-spell-to-hit.md): a member hit this round
  has every spell crossed out on USE ("YOU WERE HIT" in the bar): for a cast, raise the party's base AC
  (sheet +21h, -10) so the Draxans miss, and end the turn (`ravfight.py end`) to get a fresh round. A
  missile spell can't take a foe right beside the caster (the barred sign). Terrannus's priest spells
  on USE: row 1 at y 59 Bless, Curse, Cure Light Wounds, Cause Light Wounds (x 231), Entangle; the
  icons sit about 22 apart from x 175, so hover to check the name before a click.
- **Psionic Blast in the sequel** (2026-11-25, logs/2026-11-25-ravager-blast-log.md): the effect routine's case is
  at 6660Ah (SL's 796CBh, the same code: the loss, HP less a fifth of the most, in `[bp-16h]`, DI the target), but
  it jumps to a tail shared with other cases (656FAh: the damage, then "or byte [bx],1"), so SL's site after the
  damage (79707h) has no likeness: DSCLOG2's BLAST_LOSS (site 79) takes the loss at "mov [bp-16h],dx" (6662Dh).
  The damage routine's death test is SL's at other addresses (5CC51h "add ax,0Ah", 5CC54h "cmp ax,dx / jg": the
  Out Cold case at 5CC96h reads only DX and BX), so BLAST_KO (site 80) makes AX DX + 1 there. The sequel's dead
  status is 7 (SL's 5).
- **A psionic power for a test**: the sequel's powers are spells EBh-10Ch (RESOURCE.GFF's names: Psionic Blast is
  power 31, spell 266); each member's own byte for each is at selector 370h (the load + 3E71h):9CDh + member x 22h
  + power (SL's 2F0h:77h; ten code uses agree, "imul bx,bx,22h ... mov ax,370h ... mov al,es:[bx+9CDh]"), 02h a
  power known: `ravkits.py power MEMBER POWER` gives one (0Ah) and 200 PSP. The USE screen (C) opens on the
  member's magic for a caster: its class button (game 150,171) turns it to PSIONIC, the discipline button
  (195,171) goes round Metabolic and Telepath (Telepath's second icon, 192,59, Psionic Blast). A use costs 10 PSP;
  a failed power check 5, with no line (the power check isn't in the sequel's dice log). A member hit this round
  has its powers crossed out too (the casting rule above).
- **Aiming a power at a party member**: the game refuses (the figure under the pointer lights yellow, nothing
  cast); with its side (+15h) made 7 (the Draxans') it takes it. Two members on one spot (0 and 1 start together, 2
  and 3 together) are taken first by the first of them: make both 7 (`files/2026-11-25-ravager-blast-log-side.py`),
  and to have the target fail its save, its sheet's five saves (+30h: the save routine's `[bp-1]`) 30
  (`-saves.py`). The spot's members' objects at (x, y) are hit by a click at about (x + 11, y + 11).
- **The Draxans' HP for a test** (2026-11-25, logs/2026-11-25-ravager-blast-saves-join.md): the dice log's
  numbers (Draxan#21-27) are combatant numbers, not creature indices: `ravkits.py hp 21` writes creature 21 (not a
  Draxan) and the sheet's +8, which three Draxans share as their most. Write the HP at +0 of the creature records
  whose +15h is 7 (indices 25, 26, 29, 31 in the ambush). **Quick saves off for a test-edit run**: `ravdice.py`
  doesn't read settings.json's `quick_save` and `autosave`; hold `QuickSave.keys` and `.auto` False (a
  `sitecustomize.py` on PYTHONPATH patching `dsloader.quicksave.QuickSave`) and check `ravquick.py` shows keys
  FFFF FFFF.
- **The saving throw's frame** (66D26h): the target's creature record's far pointer at `[bp-0Ah]`:`[bp-8]` (SL's
  `[bp-1Eh]`), set before the d20 (66E33h, `push dword 140001h` to the dice routine 0B0h:391Dh); the number needed
  `[bp-1]`, the save `[bp-6]`, the spell `[bp+0Ah]` as SL's. A natural 1 leaves before the save probe: with SL's
  frame read the log had no line at all for it (the "save line that didn't show", 2026-11-20). The modifiers come
  from 628h:A7h (AL) and the spell record's +1Fh bits 1-4; the dice log names them since 2026-11-25 (below; it
  called them "other" while its save_modifiers was SL's routine).
- **The map up**: DS:0DABh is 1 on the map (SL's 0BC9h, which in the sequel holds 0A2Eh): the combat log's panel is
  drawn only while it is (DiceLog._map_up through quicksave.SCREEN_IS).
- **The creation screen's ability roll** is at 6C504h (SL's 6490Dh): four 4d4 (`push 4 / push 4 / call 0B0h:391Dh`),
  each + DS:42DAh (the race's adjustment + 4: the races' table at the load + 3E4Fh:120h, SL's 38D4h:14Dh, the same
  96 bytes), the best kept, raised to DS:42D4h (the classes' least: the game's own rule, a prime requisite 17).
  DSCLOG2's RL_TRY (site 81) at "add ax,[42DAh]" (6C585h). About 147 4d4 a press of the die as it tumbles.

**The sequel's save modifiers and THAC0 line in the dice log** (2026-11-25, logs/2026-11-25-ravager-save-mods.md):
- **The save modifiers' routine** (628h:A7h, 83606h): [bp+6] the target, [bp+8] the caster, [bp+0Ah] and [bp+0Eh]
  their effect bit sets (608h:25h, 7FE93h: effect N at bit N%8 of byte N/8, only for combatants below 30h),
  [bp+12h] the save, [bp+14h] the spell, [bp+16h] the level. In order: Life Drained (59) -2 x its +8 byte;
  for spells 32/58/69/93 Protected vs Weather (80) +6, Vulnerable (107) -20; Entranced (33) -3 against spells 2,
  39, 94, 131, 255; Bound By Thorns (16) -4 against spell 188; Heat Exhaustion (44) -2, effect 88 -1; Spirit
  Armored (94) +3 unless the save is 1; Barkskin (6) +1, Blessed (9) +1; Protected vs Evil (75) +2 when the
  caster's sheet +14h is 3, 6 or 9; the spell's kinds: 80h with 78 +4, 4 with 73 +3, 2 with 77 +4; Prayer (72)
  +1 from one's own side, else -1; +4 when a caster below 30h can't see the target (Blind 10; Invisible 53
  without Detect Invisible 25; 54 against an undead caster, race 9) and the spell's range at level 1 (680h:20h)
  is 8 or less; Brave (18) +4 against fear (category 100h); druids (classes 5-8) +2 against kinds 82h; a
  psionicist (98h:C1h class 12) +2 against category 6; category 40h minus the DEX AC table (DS:866h), 1Eh the
  WIS table (DS:89Ah); save 1 a dwarf's or halfling's CON x2/7 and the CON table (DS:880h). Chaos, Cloudkill,
  Dismissal and Scare (-100, +100, levels) are the save line's own cases. `RavGameData.save_modifiers` models it,
  with DSCLOG2's PROT_SAVE (rings 45, cloak 103 without metal armour or a shield, robe 127), KIT_SAVE, BLUR_SAVE
  and FSHIELD_SAVE.
- **The spells past 255**: the sequel's spell table has 320 records (Psionic Blast 266); SL's `spell_record` stops at
  255, so the save's +1Fh part and the category were lost for the powers until `RavGameData` read them all.
- **The attack set-up's locals** (5C5E1h; si the attacker, di the target): [BP-1Eh] the THAC0 (SL's [BP-20h]),
  [BP-8] the weapon's bonus (its plus, 0 under Anti Magic Shell, effect 4; the material, 98h:3B1h; two weapons,
  5DE34h; difficulty-1 from DS:143Ah for combatants 4 and up), bytes [BP-19h] from behind and [BP-21h] backstab,
  [BP-20h] the natural attacks, [BP-16h] weapons ready. `ravdice.py` with `RAV_FRAMES=1` prints them after each THAC0
  line.
- **The to-hit routine** (628h:66h, 8599Eh; [bp+6] the target, di the attacker): the target's Life Drained -2 x;
  Blessed (9) +1, Cursed (22) -1, Slowed (91) -4, Impeded (50) -2, Weapon Grafted (106) +1, Heat Exhaustion (44) -2;
  Berserk (102) (L-1) - (L-1)/3 at level L in class 11; Extra HP (34) from Soothe (187) -2 in melee; the target's
  Blurry (13) -2; Prayer (72); a halfling +1 with a missile (range above 1Ch, type flags 10h, or 2 without 8); STR
  (98h:2C0h) in melee, DEX (98h:2D9h) for missiles. DSCLOG2's STINK_SWING adds a Nauseated (12) attacker's -2 after
  it.
- **The cahulaks and the kits**: DSCLOG2's PROBE_TWO took the cahulaks' head penalty without asking `kit_two`, so a
  Battle Dancer in light armour paid it (bone -1, head -2: -3); SL's DSCLOG asks. Now the cahulaks' branch sets
  `two_base` -2 and calls `kit_two` (a Ghetto Fighter 2 better, a Twin-blade or Battle Dancer in light armour none).
- **Cahulak users** in the sequel's data (OBJEX RDFF): 153 Weaponer, 203 a Draxan, 320 Salesperson, 438 Tantris,
  514 and 516 Gladiators, placed in Limbo (RGN0FF) and Gladiator2 in the Pyramid (RGN034); none in the Tyr ambush.
  For a test, make a member's weapon type 24 (`logs/files/2026-11-25-ravager-save-mods-type.py ITEM 24`) and lower
  its DEX (`...-ability.py CREATURE 1 12`): a creature's ability edit goes back to the sheet's at the round's turn.
- **Two dice logs on one game** (a control: the commit before checked out with `git worktree add --detach`, its
  `ravdice.py` run beside this one) give the same rolls, but both make the Python side's hiding rolls and write the
  stealth word, so the hide results differ between them.
- **A psionic power with a foe beside the user**: every icon crossed, CAN'T START THAT PSIONIC. The USE panel reads
  the PSP when it opens.
- **What is left**: a Battle Dancer's first swing in the round she starts dancing falls back to "in bonuses" (the
  game's THAC0 lacks the dance's +1 the log already counts).

The [Ravager figure project handoff](logs/2026-11-22-ravager-figure-project.md) indexes the 18-figure review build, its approved knight profiles, the animated comparisons, and the open Soulshard gait revision.
