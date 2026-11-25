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
