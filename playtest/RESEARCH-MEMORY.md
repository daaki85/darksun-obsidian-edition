# Research recipes: memory edits for a test

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The game's records (the party, items, fights and foes, spells and powers, creation and levels) and how to
read and write them in memory for a test.

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
