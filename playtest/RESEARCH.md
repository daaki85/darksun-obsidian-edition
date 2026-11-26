# Research recipes: memory, sounds, pictures, timing, scripts and other targets

Part of the playtest guide ([PLAYTESTING.md](PLAYTESTING.md): read its startup procedure before any
in-game test). These recipes are for writing the game's memory for a test and for finding out how
the game works rather than for checking a change: the game's records and memory edits, its sounds,
the see-through figures, the picture store, frame rate and cycles, the picture and the music device, its scripts, the unchanged game,
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
- **Melee reach isn't the type's range byte** (logs/2026-11-10-polearm-reach.md): a polearm with its
  type's +0Ah set to 2, held alone, with Move 0, two squares from a held foe: the attack does nothing
  and the turn passes; with a bow in the missile slot the click shoots it instead.
- **A weapon spec's grand master for a test** (logs/2026-11-10-grand-mastery-large.md): write the
  member's sheet (the far pointer DS:1661h + (creature +4) x 47h) classes (9,0,0), levels (9,0,0)
  and +14h-+17h `01 00 00 00` (the long sword, unpacked; a sheet's +16h top bit marks them packed),
  then `specialize.skill(sheet, ITEM_TYPE)` reads 5 (GRAND). `foeset.py C race=5` makes a kind large
  (a sheet is shared, so one combatant of each). With every foe held, Tab chooses the nearest foe
  even when the member can't reach it: the END menu then opens with Move 0 (E ends the turn).

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
- **Psionic powers' place**: `powers.py` reads selector 2F0h's segment, +77h + member x 22h +
  power, bits 3-7 ([psionic powers in memory](#spells-and-powers-in-memory)).
- **A level-up for a test** (logs/2026-11-15-kit-rebalance-checks.md part 10): write the sheet's
  XP (+0, a dword) just short of the next level (`tables.xp_needed(row, level)`: a preserver's 5th
  20,000), then a kill in a fight: the level comes during the next turns, and `fightout.sh` answers
  CHOOSE A SPELL with `levelup.sh` (count its "picked a spell" lines). A loop of `levelup.sh` until it
  fails counts the picks of one screen.
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
197,171. The opening party: Ar'anda (elf preserver/psionicist/thief 6/6/7), an earth cleric 7,
Thy'rokh (thri-kreen fighter/druid, the leader), a half-giant gladiator 7; its sheets at the far
pointer DS:19C5h. **Running one of its routines on the live game** (`ravthief.py`, the thief
skills): most of its code is in overlays swapped out to XMS, so lay every overlay above A0000h from
Dark Sun Recompiled's `build_image.py` (its PSP set to the live one) with that image's stubs, the
live memory below; and give the emulator SS = DS (Borland reads stack buffers through DS).

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
**The approved catalogue redraws** (2026-11-24, logs/2026-11-24-ravager-catalogue-import.md) go into
a test build by `darksun-recompiled/tools/proto/import_catalogue.py` (the private catalogue's
`approved.json`). Their fighters go in the Draxans' slot (2428) one per run and fight as above.
**A still figure (no walk) put in the rug room's people (2427, 2420) stalls the ambush**: the
Draxans walk up and stand, and the fight never starts (half the runs, every one with a still figure in
those slots; the same fighters fought on the first try without them). Pointing an object's OJFF
record at another picture shows nothing at the start: the opening's objects come from the save
(DARKSAVE.GFF), so replace the picture's chunks instead.
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
draws it, as DSCLOG's SHADOWS does SL's figures': INT C4h at 2B81Ch (the view's floor: page, camera x,
y) and INT C5h at 2B97Fh (a rectangle's: page, x0, y0, x1 + 1, y1, camera x, y), their way back made
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
in guest memory (a test edit: the table at header + 120Ch, the sum at + 1252h for this build) for a
same-view comparison. Same-view toggle: write the
header's +148, press C then Escape (the left half redrawn). The header (signature `DSCLOGR1`) has wall_shadows at +148, the passes drawn at +150,
DARK's builds at +152: find it in guest memory to check it ran. `RAV_LOADER=1 sh ravstart.sh FOLDER`
loads it; rebuild with `nasm -f bin -o dos/DSCLOG2.EXE dos/dsclog2.asm`.

**The Loader's window on the sequel**: `apt-get install -y python3-tk`, Xvfb `:56` 1440x900 (`:55` is
smaller than the window), `python3.12 -m dsloader view --pid $(cat $WORK/rav.pid)` from `obsidian-edition/`;
stop `ravdice.py` first and the window (by pid) before running it again (the game's lock). Its party tabs
use the sequel's layout made from SL's. No moment out of a fight at the start: the opening talk ends in
the ambush, so the inventory screen (to check the gear's slot names) waits for a later save.

**Its first fight** (logs/2026-11-19-ravager-fight.md): the opening talk (3, Return) ends in the
Draxans' ambush, a fight at once; in a fight USE opens for the one whose turn it is (DS:426Dh, SL's
4979h). Right clicks on bare floor cycle the pointer: arrow, sword, look; a figure under it turns
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
`+43h` (the mod's kit byte) lands at `+3Dh` and `+45h` (second sphere) at `+3Fh`, which no
`es:[...]` access in WotR's code reads. Tried on the user's saves `selling-junk-user`, `trap-user`
and `rest-no-call-user`: all transferred, the kits kept.

The [Ravager figure project handoff](logs/2026-11-22-ravager-figure-project.md) indexes the 18-figure review build, its approved knight profiles, the animated comparisons, and the open Soulshard gait revision.
