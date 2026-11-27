# Code audit, the follow-up (2026-11-27)

*The code audited is `origin/obsidian-edition` at `b6027f9` (#258 and #255 merged), read with the project
skill `thermo-nuclear-code-quality-review`. It covers what [the first audit](code-audit-2026-11-27.md) (at
`fc865f9`) skipped from the [audit plan](https://claude.ai/artifact/G7XEUJhSTH8trfQqiR7uRM): area 5
(DOSBox-X), area 6 (class outfits: the colour fix #230, the creation figure #231), the rest of area 4 (the
big shared files) and areas 7 and 8 (DSCLOG, tests); and a code read of everything merged after `fc865f9`
(#238 to #258, 203 files). The owner's rule of 2026-11-27 applies throughout: **every change lands in
both games**, so each area also asks what one game has and the other lacks. The weights were checked
first, at the owner's ask ("Just ensure weight is the same in both games"). Line numbers are at
`b6027f9`.*

## The short version

| Severity | Count | Fixed here |
|---|---|---|
| Wrong result (the two games disagree) | 2 | 2 (W1, W2) |
| Repository rule | 1 | 0: the owner's call (P1) |
| Structural | 4 | 1 (S3); 3 proposals |
| Risk | 2 | 1 (R2) |
| Cleanup | 3 | 1 (C1) |
| Both-games gaps | 1 list | 0: listed (G) |

The worst: **P1**, game data in `dsloader/ravager-figures.zip` (#250), which is public. Then **S1**, the
"colours no area changes" worked out three ways, one of them hard-coded. Nothing found breaks a start: the
full suite (3,146 tests) and the start-up tests on both games' real files pass with the fixes.

## Wrong results: the two games disagree

**W1. Shattered Lands' leather chest armour weighed 75 lb, the sequel's 9.6 lb** (fixed). SL's type 6
(Chest Armor) is 750 tenths of a pound, five times AD&D's whole leather suit (15 lb), against its own arm
and leg pieces' 36 and 18. The sequel's type 32 is 96 (`ravager.RAV_WEIGHTS`, #211), so that the suit makes
15 lb; its weight is one byte, so 750 can't be had there. The fix gives SL 96 too, in the Loader's copy of
GPLDATA's item types (`itemtables.TYPE_FIXES`, `LEATHER_CHEST_WEIGHT`). No rule reads an armour's weight:
the load check never refuses (HOW-THE-GAME-WORKS, Weight and carrying), HEAVY and the backstab limit are
weapons', and nothing worn is picked from a pocket (`pickpocket.py:9`). So nothing plays differently.

**W2. The sequel's small things weighed 1 lb, Shattered Lands' 0.1 lb** (fixed). The sequel's type 9 (keys,
gems, rope, bottles, scrolls, coins, and the party transfer's keepsakes: `ravitems.KEEPSAKE_TYPE`) is SSI's
10; SL's small things (type 60) are 1. `RAV_WEIGHTS` now gives 9 the 1 (from SSI's 10). Pick pockets lift
both (10 or less), so nothing plays differently.

Measured on the GOG releases: every item type paired by hand (the armour pieces, shields, helm, the
weapons, the six Ravager weapons backported to SL) and every item name both games have, carried. The new
`tests/test_item_weights.py` keeps them equal; it reads both games' files (`DSUN_SL`, `DSUN_WOTR`, as
`test_start_files.py`) and failed 10 times before the fix. Four items stay apart, each named in the test with
why: the sequel's obsidian Axe (SL's Axe is metal), a Bag among the sequel's small things, the sequel's Rock
to strike with, and **Dragonsbane**, a metal long sword in SL (40) and an obsidian one in the sequel (30).
Making those two the same means another type and so another material (damage, breakage): the owner's call,
not a weight fix. Furniture, doors and scenery are left out in both (nobody carries them).

## Repository rule

**P1. `dsloader/ravager-figures.zip` (#250, 1.9 MB, in the public repository) holds the sequel's own data,
not only redrawn art.** Of its 631 chunks, 477 are pictures (BMP, CBMP: 5 to 7 % alike with the game's, so
redrawn) but 153 are SCMD, the figures' animation scripts, which are 69 % (median) the same bytes as the
game's own, and one is RGN03A's ETAB (the dining room's furniture table). The owner's rule (2026-11-23) is
that derived art may be public and the game's files may not; the branch review of 2026-11-26 proposed that
the catalogue's chunk packages stay private and the public side carry edits only (as
`dsloader/*_outfit_layers.zip` do: a change the Loader applies to the player's own file). Whether the
scripts count as game files is the owner's to say. If they do: ship the SCMD and ETAB changes as edits
against the player's own chunks (the bytes that differ), which the Loader applies, and keep the pictures.
Nothing was changed here.

## Structural findings

**S1. "The colours no area changes" is worked out three ways.** `spritegear.REGIONAL` and `STEADY`
(`spritegear.py:676-678`, #230) hard-code SL's from a reading of GPLDATA's PAL 1-45 ("80-127 and 223-239 are
each area's own ramps, 19, 21 and 29 a few areas' tweaks"); `wotrart.stable_colours` (`wotrart.py:194`)
computes the same thing for SL from the player's GPLDATA; `ravitems.stable_colours` (`ravitems.py:123`) the
sequel's from its regions. And at least eight modules keep their own nearest-colour search (`bodyart`,
`combatlog`, `dust`, `ghost`, `ravitems`, `ravspells`, `ravui`, `rings`, `spritegear`'s own weighted one).
The move: one `palette` pair, `stable(palettes)` and `nearest(rgb, among, weights=...)`, used by all; the
outfits' steady colours then come from the player's files like everything else, and a release with other
palettes can't leave a hard-coded list wrong. Proposal (it touches every outfit's pixels: a picture check
before and after).

**S2. Parity has no ledger outside the dice log's steps.** The one place the code says what the sequel
leaves out, and why, is `ravlog.PASS_LEFT_OUT` (a test fails on a step in neither list). The rules
(`ravager.RULES_PORTED`), the program patches (`gamepatch` against `ravager.PATCHES`), DSCLOG's sites
against DSCLOG2's, and the Options tab's switches have none. So a change made to one game alone passes
every test. Example: `RULES_PORTED` leaves out RULE_PROTECTION and RULE_SPELL_SAVE, though DSCLOG2 has both
(its PROTECTION and the fire, cold and electricity save: `dsclog2.asm:13524`, `ravager.py:478`). It is
harmless (both rules are always on, with no off path), but the list says the opposite of the code. The
move, which the owner's rule asks for: one ledger per kind, each entry of one game either matched in the
other or named with why, and a test per ledger. Proposal (it touches the port's every module, so the owner
first).

**S3. The same region-palette read four times** (fixed). `ravarrows.py:281`, `ravgear.py:389` and
`ravtransfer.py:630` each globbed `RGN*.GFF` for its palettes; `ravui.region_palettes` (#255) did it again,
in both letter cases. Now one `ravitems.region_palettes`, next to `stable_colours`, which all four call.

**S4. The two dice logs' save modifiers are forks.** `game.Game.save_modifiers` (`game.py:1828`, 95 lines)
and `ravlog`'s (`ravlog.py:1048`, 92 lines) share the kits' loop and Spook's penalty line for line, and a
change to one won't reach the other (the first audit's B2 was this kind: a pass missing from the fork).
The routines' orders differ because the games' do, so a shared list of the pieces each calls, in the
order each game has, is the move. Proposal.

## Risks

**R1. `dosboxx.problem()` asks the program its version on every start** (`dosboxx.py:230`), a subprocess
of up to 15 s (`VERSION_WAIT`), though `usable()` caches the same answer by program and file time. Harmless
while DOSBox-X answers at once; on a slow or hung program each start waits. The move: `problem()` uses
`usable()`'s cache. Left for the DOSBox-X thread (it is the Windows default, played there only in part).

**R2. The bundled DOSBox-X is pinned in two workflows** (fixed by a test). `release.yml` and
`test-package.yml` each set `DOSBOX_X_VERSION` and `DOSBOX_X_SHA256`; a test download is only the
release's package while they agree. `tests/test_dosboxx_pin.py` fails if they part.

## Cleanups

**C1. The last game's end files were removed by the same five lines four times** in `launch.py` (SL in GOG's
DOSBox, the recompiled program, the sequel in GOG's DOSBox, DOSBox-X for either) (fixed:
`_clear_end_files`).

**C2. Files past 1,000 lines with no plan yet**: `viewer.py` (2,368: `_build_options` alone is 277 lines,
`_build` 259), `icons.py` (1,610), `launch.py` (1,502: the engine choice, `_launch`'s four ways to start and
`prepare_patched_game`'s 122 lines), `gamepatch.py` (1,439, mostly data). The first audit's S1, S2 and S4
dealt with `game.py`, `dicelog.py` and `spritegear.py`. The clearest next split: the Options tab out of
`viewer.py` (its own module, one function per section), and the starts out of `launch.py` (one per engine).

**C3. `ravui.chunks` drops the whole interface on any read error** with no word (`except (...): return {}`),
as `ravfigures` and `ravitems` don't. A player whose SL files are another release's gets the sequel's
interface and isn't told. The Loader's `LEFT_OUT` line exists for this.

## The both-games gaps (G)

What one game has and the other lacks, from the code's own lists:

- **In Shattered Lands only**: the class outfits and the creation screen's outfit (`PASS_LEFT_OUT`'s
  "dress", "creation_figure": "the sequel has no class outfits"); the dice log's stats file, tracker and
  item watches, the scroll and initiative lines ("not ported"); a cleric/thief's purse beside Turn Undead
  (`dsclog2.asm:22685`); the thri-kreen's chatkcha throws (OWN_THROWS, `dsclog2.asm:11134`); Reflected
  Image's own icon on the Effects screen (`dsclog2.asm:23824`). The port audit's open items (Whirlwind and
  Restore Youth: with Codex) stand.
- **In the sequel only**: its figures in SL's style (#250 to #253) and SL's interface pictures in it (#255)
  are the sequel catching up, not new to it. Nothing found that the sequel has and SL lacks.
- **Merged since `fc865f9`**, each checked for its other game: the sequel's Effects screen charges (#245) and
  Enlarge and armour lines (#249) are SL's (EF_CHARGES and the AC routine, ported); the combat log panel fix
  and live autosave switch (#254) are the Loader's, for both; the kit marker (#239) and the room checks
  (#238, #242) are each one helper's own. #243 put 44 routines both helpers share in one file
  (`dos/shared_routines.inc`): a fix there now reaches both, the right shape for the owner's rule.

## What was checked and found clean

- **DOSBox-X's engine choice** (`dosboxx.engine`, `launch._launch`): one order, the same for both games
  (the sequel follows the engine, #185); a chosen DOSBox-X goes before a found recompiled program, a found
  one after it; every failure says what to do. The zip's DOSBox-X comes from DOSBox-X's own release, its
  hash checked, with COPYING.txt and SOURCE.txt and the source archive beside the zip (GPL 2, section 3).
- **The colour fix (#230)** keeps the game's own pixels (`steadied` moves only what gear and outfits add),
  and has its test (`test_steady_colours.py`).
- **The creation figure (#231)** draws through the same `sprites.Pictures` as the map figures, so the
  outfit is the same one.
- **DSCLOG and DSCLOG2's room**: the margin tests (#238, #242) pass; DSCLOG.EXE 70,336 B, DSCLOG2.EXE
  68,032 B at `b6027f9`, both rebuilt byte for byte from their sources by the suite.
- **Tests**: the full suite under `unittest`, as CI runs it (`DSUN_REQUIRE_NASM=1`), 3,146 tests, 229
  skipped without the game's files; the start-up tests and the new weights test with both games' files.
  `test_ravghost` and `test_ravshadows` (the first plan's "fail under pytest") load under pytest now.

Not read line by line: DSCLOG's and DSCLOG2's new routines since `fc865f9` (about 3,300 changed lines, most
of them #243's move into `shared_routines.inc`, which the rebuild checks prove changed no byte).
