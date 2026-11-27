# Code audit (2026-11-27)

*The code audited is `claude/combined-playtest` (PR #180, every open PR from #217 to #232) at
`fc865f9`, read with the project skill `thermo-nuclear-code-quality-review`, in the order the
[audit plan](https://claude.ai/artifact/G7XEUJhSTH8trfQqiR7uRM) set. It also covers an outside
playtest audit's code findings C1 to C6 (made at `a36c03d`, an ancestor of `fc865f9`). Each was
checked against the code here, and all six hold. Line numbers are at `fc865f9`. The previous
audit is [code-memory-audit-final.md](code-memory-audit-final.md) (2026-11-19).*

## The short version

| Severity | Count | Fixed |
|---|---|---|
| Bug | 4 | 3 on [#235](https://github.com/daaki85/darksun-obsidian-edition/pull/235); 1 (C2) handed to the port thread |
| Wrong result | 2 | 1 on #235 (C5); 1 (C4) handed to the port thread |
| Risk | 5 | 0: C1 handed to the port thread; the rest are proposals |
| Structural (the skill's blockers) | 5 | 0: proposals, which need the owner's go-ahead because they touch every thread's work |
| Cleanup | 6 | 0 |

The worst finding is **B1**. After a game of Wake of the Ravager played from the Loader's window,
starting Shattered Lands from the same window wrote SL's copies with the sequel's record offsets,
and SL started without its new items, people and icons. #235 fixes it. B1 has the same root as the
largest structural finding (**S1**): the sequel port works by rebinding `game.py`'s module globals
for the whole process.

**Tests.** Before any fix: `python -m unittest discover -s tests` with `DSUN_REQUIRE_NASM=1` ran
3,084 tests, OK (222 skipped). pytest over the whole folder gave 3,147 passed. The plan said
`test_ravghost` and `test_ravshadows` fail under pytest, but they don't now, so that item is
closed. The start-up tests on both games' real files (`test_start_files.py`) passed. With #235 on
`obsidian-edition`, 2,977 tests pass and the start-up tests' three pass.

## Bugs

**B1. Shattered Lands started after the sequel loses its new items** (fixed, #235). `RavDiceLog`
calls `ravlog.apply_layout()`, which rebinds 168 of `game.py`'s names, and every copy any loaded
`dsloader` module took of them by `from .game import` (272 bindings in all), to the sequel's values. They are put back
only by `ravlog.make()` when it next makes a dice log for Shattered Lands. That happens once SL is
running, after `launch.prepare_patched_game` has written SL's copies. So the order *Play Wake of the
Ravager → quit → Play Shattered Lands* in one Loader window wrote the copies with the sequel's
offsets: `npcitems._item` indexed `game.ITEM_PLUS` past a 21-byte record (`bytearray index out of
range`), SEGOBJEX.GFF and the region files were left out ("Started without the new items, people and
icons"), and GPLDATA.GFF came out different (hash `12a51ac7` against the fresh start's `9350e253`).
Reproduced in a script on the real files. The fix puts the layout back first, and the copies are now
byte-identical to a fresh start's. Starting the sequel twice was checked too: its copies don't
depend on the layout.

**B2. The sequel's dice log never flushed held dice** (fixed, #235). `RavDiceLog._after_rolls`
(`ravlog.py:1797`) is a fork of `DiceLog._after_rolls` (`dicelog.py:1618`) with its own list of
passes, and that list left out `self.flush(now)`. Dice held to learn their spell (`PendingDice`: an
unclaimed spell roll, a magic resistance d100) came out only when the next roll forced a flush, or
never, if the fight ended first.

**B3 (C3). `playtest/ravstart.sh`'s object skips undid one another** (fixed, #235). Each object part
in `RAV_SKIP` called `write_objects` with a one-item set, and each write starts from the game's
file, so the last one put back what the others had left out. Measured: 10,628 chunks in all,
10,532 with `new_items` skipped, and 10,628 again after a following `weights` skip. Every control run
with two object skips tested less than its log says. `spell_arrows` reached only the object copy,
not the resource copy. This was already in merged code (5 parts there, 6 on #180).

**B4 (C2). A Spellarcher can start with arrows that have no object** (port thread).
`ravager.write_objects` builds the arrows' objects only when it is given Shattered Lands' folder
(`ravager.py:1871`). `_arrows_ready` hides the USE buttons when they're missing, but it checks only
`ARROWS[0]`'s object. `ravkitstart.fine_bow` calls `ravarrows.starting_arrows` with no check at all
(`ravkitstart.py:204`). With the sequel installed alone, a new Spellarcher gets item records with no
object, and they persist in the roster. Fix: one availability decision from the copies made,
passed to both paths, checking all three objects.

## Wrong results

**W1 (C5). Locks: "the latest four kept" were the highest thing numbers** (fixed, #235).
`locks.barred` turned the tries into a set and kept `sorted(things)[-LOCK_MAX:]`. A thief who failed
more than four locks at one level in one region could try again the one failed last, if its thing
number was low. Now it orders by the game time each was failed at (`DiceLog.picked_at`), as an
optional argument, so the sequel's call on #232 keeps working. The sequel gets the fix once it
passes `picked_at` too, which is the port thread's change. The other half of C5, that `things_now`
reads the whole object and position tables once per object key on every pass, is a cost and not a
wrong result. It goes with S1's per-game state: read one snapshot per pass.

**W2 (C4). A Spellarcher's starting arrows can be lost** (port thread). `starting_arrows`
(`ravarrows.py:137`) unlinks the plain arrows before `npcitems.add_to`, and doesn't check whether
the add worked, so a refusal leaves no ammunition at all. `fine_bow` renames the bow first, and its
"already done" test (any spell arrows worn) then treats a partial grant as finished. The USE path
writes the inventory and debits the slot, then releases the item gate before writing the reply
(`ravlog.py:2135`), which leaves a window where DSCLOG2 marks the request late. Fix: plan the
swap, add first and unlink after, and keep the reply inside the held gate.

## Risks

**R1 (C1). The sequel's helper header has no version or length** (port thread). The Loader takes
a nonzero PICK POCKETS text offset (+2012) as leave to write the arrows mailbox (+2098 to +2106,
`ravlog.py:2117`). The lock table's offset (+2114) works the same way. The signature is still
`DSCLOGR1`, so a helper built before those fields (one started by an older Loader and still running)
has code there, and the Loader writes over it. Proposal: a header-length word at an offset every
older helper has as 0 (one of `glob`'s unused capture words, +26 to +30), checked before any field
past the length is written, and tests with both an old and a new built image.

**R2. DSCLOG's segment, Shattered Lands' helper, has 336 bytes left, not 672, and no margin test.**
`kept_end` is FEB0h (65,200 bytes: `resident_end` 64,208 + 992). DEVELOPMENT-INTERNALS' limits
table says 64,864 and 672. Upper memory once installed (`UMB_KEPT`) is 8,096 paragraphs of 8,182,
so 86 are spare (the table says 109). The far block has 36 bytes spare. Only the hard limit
(`times -(image_len > 0x10000)`) guards it: there is no margin test like `test_dsclog2_room`'s, so
the next SL feature fails at the build with no warning. DSCLOG2 is far better off, despite the plan's
worry: 57,440 bytes (E060h), 8,096 free, with a 2 KB margin test. Proposal: give DSCLOG the same
move to the tail that #228 gave DSCLOG2 (the kits' names are there already; the drawing tables
and the remaining `cs:` tables could follow), then a margin test. The docs' figures are for the
docs audit (sent there).

**R3. DSCLOG2 has no build check on upper memory.** DSCLOG fails its build when `UMB_NEED` or
`UMB_KEPT` passes `UMB_ROOM`. DSCLOG2 has neither check. Its block is 4,133 paragraphs (66,128
bytes, `KEPT_PARAS`) plus the see-through figures' 5,632, and every port adds to it. Proposal: port
DSCLOG's two `times -(...)` checks, sized for the sequel's own overlay and music buffers (measure
them once in the game with `memaudit.py`).

**R4. The kit byte's `KIT_OPEN` (FFh) is also a legal value.** The sheet's kit byte holds the three
class places' kits (2 bits each, bits 0 to 5), `OWN_BIT` (40h) and Friends known (80h). FFh is
read as "kit taken back, none chosen" (`kitpages.kit_at`, DSCLOG2's `NEW_SHEET`, `OWN_RACE_B`,
`DK_ASK`). A character with the third kit in all three places, `OWN_BIT` and Friends known has FFh
too, and loses its kits. Only Terrannus (a human Crusader, kit 3, with `OWN_BIT`) could get there,
by dual-classing twice into a third kit each time and learning Friends. It is unlikely, but the
sentinel should be a value the encoding can't make (kit place 3 in the unused top place of a
single-class character, or a bit of its own in the sheet's last spare bits). Shattered Lands' byte
is the same.

**R5. `apply_layout` matches copies by value.** It rebinds a name in any loaded `dsloader` module
whose value *equals* `game.py`'s Shattered Lands value, so a module's own constant that happens to
have the same value would be rebound too. Modules first imported while the layout is on (lazy
imports inside functions: `worldgear.data_chunks`' `bonescale`, `game.py`'s `spellbook`) take the
sequel's values and are never put back. `bonescale` can't even be imported under the layout: it
raises the `IndexError` B1 hit. #235 closes the path that hit it. S1 removes the class of bug.

## Structural findings (the skill's presumptive blockers)

**S1. The sequel port is a process-wide rebinding of module globals.** `apply_layout`
(`ravlog.py:422`) rewrites `game.py`'s addresses and record offsets in every loaded module, plus
about 20 named tables in `sizes`, `specialize`, `kits`, `dicelog`, `journal`, `kalzith`, `stealth`
and the targeting and fight-key modules. `restore_layout` undoes it from a list. It is the "magic"
the skill warns about. Correctness depends on import order (R5) and on call order (B1), and tests
must restore it in `tearDown` or they leak into each other (C6's point). The code-judo move is a
`Layout` value bound to the game instance: `GameData` already reaches nearly every offset through
`self`, so `self.layout.ITEM_PLUS` in place of `game.ITEM_PLUS` turns the rebinding into a
parameter, and SL and the sequel can run side by side in one process (the tests too). It can be done
incrementally, one module at a time, starting with the ones apply_layout names by hand, keeping
`apply_layout` for what is left until it's empty. **Needs the owner's go-ahead**: it touches
nearly every Loader module and every open thread's work.

**S2. `RavDiceLog` re-lists `DiceLog`'s pass.** `RavDiceLog._after_rolls` is a hand-kept fork of
the 55-line pass, with its own order (the sequel syncs the journal *after* the quick save, though
SL's comment says the order matters) and its own omissions. B2 was one of them. `RavDiceLog`
overrides about 60 of `DiceLog`'s methods, and `ReadOnlyGuest` with its `writable` ranges means
every ported feature has to re-declare the bytes it writes. Proposal: make the pass a list of named
steps in `DiceLog` (each with its interval and its "not while loading" flag) and have the sequel
choose names from that list, so a step SL adds is either picked or left out on purpose, never
missing by accident.

**S3. `DiceLog` is one 4,349-line class** (`dicelog.py`, 4,888 lines), `GameData` 1,741
(`game.py`, 3,006), `Viewer` 2,271 (`viewer.py`, 2,362). Each mod feature has been added as a few
methods on the big class. Clean splits by subject already exist as modules (`locks`, `loot`,
`quicksave`, `squares`); what stays in `DiceLog` is each feature's glue (`_locks_pass`, `_loot_pass`
...). Proposal: a feature object per subject owning its pass, its ranges and its state, with
`DiceLog` holding the list (S2's list). This is the same move as S2 and should be done with it.

**S4. `spritegear.armed` is a 567-line function with 52 `model ==` and 38 `frame ==` tests.**
The class outfits added per-model, per-frame placements (`if costume and model == 2099 and not
combat and frame == 1: parts = parts._replace(hands=..., shoulders=...)`) in one flow, with magic
coordinates inline. `spritegear.py` grew from 1,104 to 2,253 lines. The move: a data table
`PART_FIXES[(model, combat, frame)] -> {field: value}` applied in one line, which deletes most of
the branches. This is also how the figures' data is kept elsewhere (`classoutfits` frames). Since
Codex is still changing the plate tint, do it after that settles. (Whether the tint is still in
one place, as the plan asked, wasn't checked here.)

**S5. DSCLOG and DSCLOG2 share 357 routine names; 44 routines are byte-for-byte the same source
(663 lines) and 37 more over 90% the same (1,539 lines).** Among them are `dust_nudge`,
`wp_harvest`, `c_cells`, `vga_save`, the panel's drawing, `ring_points`, `c_itoa` and `next_die`.
Only `save_bands.inc` is shared today. Proposal: move the address-free ones into `.inc` files, as
C6 suggests. That keeps the emitted bytes the same (the rebuild checks prove it) and stops a fix to
one helper from missing the other. It frees no room.

## Cleanups

- **C-1.** Two names mean different things in Python and DSCLOG2: `ravlog.SH_LEVELS` (a header
  offset, 2080) and DSCLOG2's `SH_LEVELS` (a sheet field, 1Eh); `ravarrows.KNOWN_SEG` (absolute,
  3D62h) and DSCLOG2's (DS-relative, 3D62h − 47E0h). The other 90 shared names agree, checked
  against nasm's map. No test cross-checks them. A test that reads the map and compares every shared
  name would catch drift (C6's "validate the Python constants against the symbol listing").
- **C-2.** `ravager._site` and `gamepatch._site` differ only in the vector. One
  `gamepatch.site(vector, number, length)` would serve both.
- **C-3.** DSCLOG2's `SITE_TABLE` has 245 entries, about 100 of them `site_none` (held ranges, 130
  to 139 "another's"). That costs 200 bytes of the tail, which is fine, but the held ranges have no
  owner named in one place. A comment table at the top would keep threads from taking each other's
  numbers.
- **C-4.** `RavDiceLog._after_rolls`' docstring lists the passes by hand and is already out of date
  (it doesn't name the gear, the arrows or the strays). S2 would remove it.
- **C-5.** `new_sheet` (DSCLOG2) clears +42h to +47h but not the age at +41h. The template's +41h
  is 0 in every save checked (2026-11-22), so it's safe, but a comment should say it relies on that.
- **C-6.** The plan's "CHANGELOG conflicts on every PR" item: confirmed again making #235. A
  `changelog.d/` entry per PR, gathered at a release, is the docs audit's call.

## The 72-byte character sheet

The sequel's sheet is the game's 66 bytes (42h) widened by the Loader to 72 (48h,
`ravager.SHEET_SIZE`: 386 `imul 42h` sites patched). Every byte the mod owns:

| Byte | Bits | Owner | Notes |
|---|---|---|---|
| +3Dh | 0-5 | the kits: 2 bits a class place (0 none, 1-3) | SL's +43h. The high byte of the sound word +3Ch, which the copy reads as a byte (`sound_3c`) |
| +3Dh | 6 | `OWN_BIT`: the games' own party's features | |
| +3Dh | 7 | Friends known | |
| +3Dh | all | `KIT_OPEN` FFh: a kit taken back | collides with a legal value (R4) |
| +3Fh | 0-2 | the Elementalist's second sphere + 1 | SL's +45h. The high byte of the sound word +3Eh (`sound_3e`) |
| +3Fh | 3-7 | Reflected Image, Cat's Grace, Erdlu Claw, Fogbolt, Spook known | |
| +41h | all | the age: years past the race's base + 1 (0 none) | a byte the sequel's program never touches |
| +42h-+44h | 0-16 | the four weapon specs, V3 (`game.packed_specs`) | SL's +14h-+16h |
| +44h | 1-5 (bits 17-21) | the starting age's roll | |
| +44h | 6, 7 | `SPEC_V2`, `SPEC_PACKED` | |
| +45h-+47h | 0-19 | four more specs, 5 bits each (a gladiator's 5th to 8th) | `SPEC_MORE` |
| +47h | 4-7 | **free** | the only spare bits left |

So the rule (all per-character data in the sheet) holds: nothing per character lives in a side
file. The lock and pocket tries in `settings.json` are per world, not per character, as in SL. But
the sheet is now **full but for 4 bits**. The next per-character feature needs a decision: the 4
bits, the sound words' low bytes (a sound number above 255 is never used, which would need
checking), or a wider sheet (48h → 4Ah, the same 386 sites).

## What was checked and found clean

- **DSCLOG2's room.** 8,096 bytes free with the 2 KB margin test. The site table to 244 has no two
  sites on one routine except the deliberate shared handlers (90 to 92's `sh_sphere_*`), and no
  number used twice (the table is positional).
- **The sequel's copies** don't depend on the layout. They are byte-identical with it on or off.
- **The party transfer** writes the 48h sheet with +42h to +44h from SL's +14h to +16h, and
  +45h to +47h as 0. DSCLOG2's `NEW_SHEET` clears the six bytes for a new character.
- **Per-character data** is all in the sheet (above).
