# Research recipes: Wake of the Ravager's port audit and its spells in a fight

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The port audit's dated notes (its rest, a control run, its leftovers, the final items, the Effects screen's
other lines), the sequel's spells in a fight and its save modifiers and THAC0 line in the dice log. Setting up
and driving the sequel: [RESEARCH-RAVAGER.md](RESEARCH-RAVAGER.md).

## The port audit's rest (2026-11-27, logs/2026-11-27-ravager-audit-rest.md)

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

## A control run: RAV_SKIP

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
| The talk portraits' size | `small_portraits` | the five `small_portraits_*` patches, the smaller faces, the talk window and the empty frame (`ravportraits`) | `DSUNLOG2.EXE`, `GPLDAT2.GFF`, `RESOURC2.GFF` | the sequel's 72 by 72 faces, the talk box 72 high, its text from x 75 |

Any other name stops the script with `RAV_SKIP: no such patch NAME`; `$WORK/rav.conf` starts with
`# left out: ...` when the run went ahead. Prerequisite: `RAV_LOADER=1` (without it nothing is copied,
so nothing is left out); the new items' pictures come from `$GAME`'s Shattered Lands (`RAV_SL=` for
none, which also leaves out the new items and the spell arrows' objects). To check a run, look at the
copy (the bytes at the patch's offset, or the chunk in `OBJEX2.GFF`), not at the printed list.

**Before 2026-11-27** each object part was written in a run of its own, each from the game's file, so
with two or more object parts named only the last was left out. No play log named two object parts in
one run (the controls on record name patches, or one of `weights`, `item_shine` and `new_spells`), so
their results stand. `spell_arrows` also left `RESOURC2.GFF` as it was then.
## The audit's leftovers (2026-11-27, logs/2026-11-27-ravager-audit-leftovers.md)

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

## The final items (2026-11-27, logs/2026-11-27-ravager-final-items.md)

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

## The Effects screen's other lines and the computer's walls (2026-11-27, logs/2026-11-27-ravager-effects-lines.md)

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

## The sequel's spells in a fight (2026-11-21)

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
