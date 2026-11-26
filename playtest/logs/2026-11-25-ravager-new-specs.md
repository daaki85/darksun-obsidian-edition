# 2026-11-25: Wake of the Ravager's own six weapon specs (lotulis, double spear, trikal, two-handed sword, javelin, darts)

**Under test:** branch `claude/ravager-new-specs` (on `claude/sl-ravager-integration`, PR #181): DSCLOG2's KIND_OF_TYPE
with SL's kinds 17-22 for the sequel's own Twohand Sword and Crystal sword (101, 35), Lotulis (61), Double Spear (39),
Trikal (100), Javelin (59) and Darts (38, 43); SPEC_GET without #181's FOLD_KINDS; MISSILE_RATE's javelin and darts;
the Effects screen's six names; PSI_KINDS' darts; the Military Scout's outdoor bonus kept to the bow, sling and staff
sling. No new sites, no new header fields.

**Set-up:** `fountain-user`'s SAVE01.SAV copied and its sheets' specs set (game.with_specs, V3): Seneca (thief 3 /
fighter 2) **lotulis**, Ester (fighter 2 / cleric 3) **two-handed sword**, Lex (fighter 3 / preserver 2) **gythka**
(the fold's control: under #181 a gythka spec counted with the sequel's Lotulis), Jenna (ranger) long sword as it was.
`python -m dsloader.ravtransfer` into `ravNS`, a throwaway copy of `$WORK/rav` (its roster reset from
`__support/save`): the roster's 48h sheets read back lotulis, two-handed sword, long sword, gythka (V3, the rolls kept).

**Where played:** a second game (the shared DOSBox held by another agent's long session): a copy of the kit on
display `:57` (env.sh, paths.py, ravclick.py, ravfight.py, ravstart.sh's Xvfb), `PLAYTEST_WORK=/tmp/playtest/nswork`,
DOSBox copied as `dbns` (a `dosbox` wrapper first in PATH). Scripts: [files/](files/) `2026-11-25-ravager-new-specs-*`.
Test edits in memory, never saved: HP 250 for the four; the right-hand weapon's type made the sequel's Lotulis (61) for
Seneca and Lex and Twohand Sword (101) for Ester (the items keep their names); the left hands' items to the pack.

## Seen: the screens (run on1, the rule on)

Party order: Seneca, Ester, Jenna, Lex. In the Draxans' fight, the screens
([picture](img/2026-11-25-ravager-new-specs-screens.png), [Seneca's Effects](img/2026-11-25-ravager-new-specs-seneca-effects.png)):

- **Seneca** (lotulis spec, the Lotulis): Effects **SPECIALIZED IN / LOTULIS** (the new name); the inventory's line
  `+1 Shadowseeker 1.5x2D4+7` (2d4, 3/2 a round, +1 weapon +2 specialized +4 STR).
- **Ester** (two-handed sword spec, the Twohand Sword): **SPECIALIZED IN / TWO-HANDED SWORD**; `Longsword 1.5x1D10+9`.
- **Lex** (gythka spec, the Lotulis: under #181's fold he counted as specialized): **SPECIALIZED IN / GYTHKA**; his
  Lotulis line `2D4+7` at 1 a round, no specialization bonus (the plain rate): the fold is gone.

## Seen: the fight (dice log, `ravdice.py --numbers`)

The build in memory (`files/2026-11-25-ravager-new-specs-nscheck.py`): the first 40 bytes of spec_get, spec_kind,
spec_kinds_own, missile_rate, missile_halves, kind_of_type, large_dice, class_forbids_one, kit_to_hit, ef_kinds and
ef_lines_of the same as dos/DSCLOG2.EXE; kind_of_type for types 35 38 39 43 59 61 100 101 read
17 22 19 22 21 18 20 17. Rules word 0xFB45 (RULE_SPECIALIZE on), the control's 0xEB45.

**on4, the rule on** (12 rounds, Computer Control, about 4 minutes):

| Member, weapon (type) | Swings by round | Damage lines |
|---|---|---|
| Seneca, lotulis spec, the Lotulis (61) | 2, 1, 2, 1 ... (3/2) | `2d4 = [4 + 4] +1 weapon +2 specialized +4 STR 18`; THAC0 "+1 specialized" |
| Ester, two-handed sword spec, the Twohand Sword (101) | 2-3 a round with her off hand | `1d10 = [8] -1 obsidian +2 specialized +8 STR 20`; her off-hand long sword `1d8 ... +8 STR 20`, no bonus (not her spec) |
| Lex, gythka spec, the Lotulis (61) | **1 a round** (rounds 1-11) | `2d4 = [1 + 3] -1 stone +8 STR 20`: no bonus (the fold would have made him specialized) |
| Jenna, ranger, the long sword | 3, 2, 3, 2 (the game's) | no bonus (a ranger's expertise) |

DSCLOG2's counters at the end: spec_hits 28, spec_damages 28, spec_rates 42 (Lex's cut swings among them).

**ctl1, the control** (`RAV_RULES_OFF=0x1000`, 9 rounds): no "specialized" line; Seneca's Lotulis 2, 1, 2, 1 with no +2
(`1d4 = [3] +1 weapon +4 STR 18` her off hand); **Lex's Lotulis 2, 1, 2, 1** (the game's 3/2 for every warrior),
`2d4 = [3 + 4] -1 stone +8 STR 20`; Ester `1d10 = [5] -1 obsidian +1 Battle Dancer +8 STR 20`. spec_hits, spec_damages,
spec_rates all 0.

Run on3 ended after one round: `ns-fight.sh` tested the DOSBox's name as `dosbox` (here `dbns`), took it for gone and
stopped the dice log (fixed in the script); its one round showed Seneca's "+1 specialized" and Lex's single swing too.
On2 found no DOSBox window 6 s after the start (the display just started): started again.

**The merged build** (after merging #181's tip 3ae499f: DSCLOG2.EXE 46112 bytes): the same eleven routines the same in memory, kind_of_type as above, and Seneca's Effects screen still
**SPECIALIZED IN / LOTULIS**. **Memory** (`dosmem.py`): DSCLOG2 takes **45584 bytes** in upper memory (MCB CA0Ah),
**109872 bytes** free after it (110016 in 2 pieces); the branch's build before the merge 45056, 110400 free.

## Not played

- **The creation pick window offering the six**: the sequel has no weapon window (WEAPON-SPECS.md: nobody picks new
  specs there); the PROBE_WP_* ports there are the kit pages' disciplines and spheres windows. Nothing to extend.
- The javelin's and darts' rates of fire in play (tests only: test_ravspecialize's MISSILE_RATE against
  specialize.missile_attacks for types 38, 43, 59); a psionicist with the sequel's Darts (test_ravrestrict).
- The lotulis's, double spear's and trikal's own traits: SL's only.

No new area: no water noted. Test edits in memory only, nothing saved; ravNS thrown away after.
