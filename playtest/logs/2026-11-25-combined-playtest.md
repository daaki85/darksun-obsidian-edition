# 2026-11-25: every open pull request together, a smoke play of both games

**Under test:** branch `claude/combined-playtest` (from `obsidian-edition` 7248b74), the test branch for
the owner's play: every open pull request merged, by the branch heads that hold them all:

| Branch | Commit | Pull requests it holds |
|---|---|---|
| `claude/ravager-join-loot-tabs` | b0db0cf | #148, #151, #152, #155, #158, #160 to #177 |
| `claude/memory-pass-7` | 464749d | #149, #150, #154, #157, #179 |
| `claude/ravager-play-button` | c6a82b4 | #156 |
| `claude/dosbox-x-default` | 43de3c4 | #146, #178 |
| `claude/test-rules-leak` | 4d08a37 | #147 |
| `claude/sl-patch-jumps` | 7311200 | #159 |
| `claude/community-notes` | a8c9dcb | #153 |

## What the merge needed

- **The spec layout.** #149's six new kinds store the specs as V3 (`game.packed_specs`), and the
  Loader writes the sequel's sheets with the same function, so the sequel's helper got V3 sheets it
  couldn't read (its `SPEC_GET` knew V2 only). DSCLOG2 now has DSCLOG's `SPEC_UNPACK`/`SPEC_CHOOSE`
  (DSCLOG2.EXE 43,216 -> 43,456 bytes), and a spec in one of SL's six new kinds reads as the kind the
  sequel counts that weapon as (`FOLD_KINDS`: two-handed sword -> long sword, lotulis -> gythka, double
  spear and trikal -> polearm, javelin and darts -> chatkcha). `game.specs_of` reads V3 too.
- **The new item types in the sequel.** `npcitems.TYPES` grew from 33 to 44; the sequel's mod types
  stay the first 33 (`ravager.MOD_TYPES`, DSCLOG2's tables), and SL's types past them go across as
  the sequel's own type of that weapon (`ravager.sequel_weapon_type`: 101, 61, 39, 100, 59, 43), not
  keepsakes.
- Launch: the sequel always on GOG's DOSBox, before the engine choice; DOSBox-X's `chosen`/`engine`
  kept; the "Start the game" texts now "Play Shattered Lands".
- Docs merged both ways; the CHANGELOG's Unreleased regrouped for every pull request in it.

## Tests

`python3.12 -m unittest discover -s tests` with the game's files, DSUN_SL and DSUN_WOTR: 2,596 run,
1 failure, `test_ravitems.GameTests.test_trap_user_every_item` (`wide_sheets` in the done list), which
fails the same on the Ravager stack's top alone. Both helpers assemble to the committed EXEs.

## Shattered Lands (`fountain-user`)

- `buildcheck.py` OK: 129 vectors at their handlers, the item tables the game read the Loader's
  (memory pass 7). Upper memory: DSCLOG loaded high, 26,784 bytes free after it at E30Fh (before
  memory pass 7's merge 25,488).
- The ambush with `PT_NO_EDIT=1` (no edits): the party lost (a normal outcome; 391 dice log lines,
  specialization lines fine). Then with the autosave and quick save off, `fightout.sh`: won after 15
  party turns ([picture](img/2026-11-25-combined-sl-won.png)).

## Wake of the Ravager

- `fountain-user`'s party taken across by `python -m dsloader.ravtransfer` into a fresh copy, then
  [the port-all smoke run](files/2026-11-25-ravager-port-all-run.sh) (`comb`, 6 minutes): the four
  ADDed, a new game, HP 250 (a test edit, the copy thrown away), Computer Control in the Draxans'
  ambush. The sheets' specs bytes are V3 (`5da8c9` and the like).
- **Won**: "Each party member receives 10000 experience points!"
  ([picture](img/2026-11-25-combined-ravager-won.png)); STDOUT.TXT empty (no Illegal Op).
- `Seneca hits Draxan#26 for 9: 1d6 = [2] +1 weapon +2 specialized +4 STR 18`: the V3 specs read by
  DSCLOG2. Counters: spec_hits 17, spec_damages 17, spec_rates 17, kit_hits 2, kit_moves 5, two_count 10.
- No water seen (Tyr's ambush street and the pens' fountain, known places).

## Not tried here

DOSBox-X (not installed in this container; the Windows check is the owner's), the new SL weapons'
places (Melkor, Dagger, Dakaren) in play, the sequel's shops, Tab, loot keys and quick saves on this
branch (each played on its own branch).

## 2026-11-26: the new Ravager PRs joined (#198, #199, #200-#202, #203)

DSCLOG2's site table joined as: 130-139 none, 140-149 the new spells (#200, #201), 150 LV_WEAPONS (#199),
151-159 none, 160-163 the graphics (#203), 164-179 none (180 sites, 51 `site_none`); header +1960..+1983
#203's. DSCLOG2.EXE 58,192 bytes. 2,774 tests pass (the start-up tests on the real files among them).

Memory, `RAV_LOADER=1 RAV_UMB=1 sh ravstart.sh` to Tyr, then `dosmem.py`: DSCLOG2's upper memory block
57,648 bytes (plus its 5,632-byte tail), **92,304 bytes of upper memory free** (the largest piece 92,160);
conventional memory 63,232 free after the game.

## 2026-11-27: upper memory with the kit ports joined (#218-#222)

DSCLOG2.EXE 65,136 bytes with #218 (kit PSP, hit dice), #219 (casting levels, cures), #220 (the
Shinobi's spells), #221 (weapon traits) and #222 (poison, arrows, Fine Bow) joined. `RAV_LOADER=1
RAV_UMB=1 sh ravstart.sh` to Tyr, then `dosmem.py`: DSCLOG2's resident block 64,576 bytes (MCB CA0A)
plus its 5,632-byte block at EE9F; **upper memory free 85,376 bytes** (largest piece 85,232), against
92,304 at 58,192 bytes (2026-11-26). Conventional memory after the game 63,168 bytes, its far heap 47 KB
free, HMA on. Afterwards `python3 -m dsloader.ravager narrow /tmp/playtest/rav` (the Loader's start
widens the roster).

## 2026-11-27: upper memory with #228 (DSCLOG2's room) and #223 joined

The same check as above (`RAV_LOADER=1 RAV_UMB=1 sh ravstart.sh` to Tyr, then `dosmem.py`), with #218 to #223
and #228 joined. DSCLOG2's first block (65,792 bytes) is its PSP, its code segment and the tail together (#228: only the code
segment must fit 64 KB; the install after the tail is freed); its other block (5,632 bytes, at the top of upper
memory) was there before #228 too. Free in upper memory: **84,160 bytes** in 2 pieces, the largest 84,016 (85,376
before #223 and #228). Conventional memory after the game: 63,168 bytes, the far heap 47 KB free; the HMA is on.

## 2026-11-27: upper memory with #232 (the port audit's rest) joined

The same check with #232 joined (sites 241-244, header +2114..+2123): to Tyr, then `dosmem.py`. DSCLOG2's first
block (PSP, code segment to E05Ch, tail) is 66,384 bytes (65,792 before: #232's 534 bytes of code and LOCK_BARRED's
64), its other block 5,632 as before; free in upper memory **83,568 bytes** in
2 pieces, the largest 83,424.

## 2026-11-27: upper memory with #240 (the audit's leftovers) joined

To Tyr with everything joined (#217-#236, #238-#240): DSCLOG2's first block 66,560 bytes (66,384 before #240),
its other block 5,632; free in upper memory **83,392 bytes**, the largest piece 83,248.
