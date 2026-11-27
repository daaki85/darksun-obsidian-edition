# Research recipes: Wake of the Ravager's records, transfer, kits, saves and gear

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The sequel's transfer program and the Loader's transfer, its 48h sheet, the TOC the Loader writes, its AC and
save modifiers, the kits, STORE and RECALL, saves, looting and keys, weapon specs, the starting gear, picking
pockets, spell arrows and item weights. Setting up and driving the sequel: [RESEARCH-RAVAGER.md](RESEARCH-RAVAGER.md).

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

**Weapons across, kind and material** (2026-11-27, logs/2026-11-27-ravager-weapon-materials.md): to test what an SL weapon
becomes, write it into a party member's backpack item in a copy of an SL save (SAVE 7, 15h bytes an item: +0 the object
negated, +6 the value, +0Ah the type, +12h the name, +14h the plus; keep +4 the next item, +8 the contents and +11h the slot;
`logs/files/2026-11-27-weapon-materials-save.py`), transfer it into a copy of the sequel with the Loader's code and with the
control's (a `git worktree` of origin), and compare the rosters' items offline (`...-roster.py`: type, kind, material) before
any play. **DSCLOG2's rules word is 0 until the dice log attaches** (`ravdice.py`): an equip tried before it tests nothing (no
class or kit limit runs). Read its counters by name with `logs/files/2026-11-27-dsclog2-words.py` (the segment from `ravtail.py`).
A kit's own weapons come before the class limits (KIT_ALLOWS, then CLASS_FORBIDS): a fire cleric Battle Dancer keeps a bone long
sword and a bow; pick a character with no kit for a sphere test. A two-handed weapon also needs the other hand free.
**Item names past 256 show only with the dice log attached** (it writes DSCLOG2's ITEM_NAMES): a box looked at before
shows none. After a change to the names' places, move the dos folder's RAVITEMS.GFF away and transfer again (its
objects keep the name numbers they were made with). In the title menu the pointer may not follow `ravclick.py` at
first: an `xdotool mousemove 510 405 click 1` on the window (640x480 at 192,184) wakes it.

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
