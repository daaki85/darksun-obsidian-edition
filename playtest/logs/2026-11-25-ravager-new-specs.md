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

## Seen (run on1, the rule on) — WIP, paused for the usage limit

Party order: Seneca, Ester, Jenna, Lex. In the Draxans' fight, the screens
([picture](img/2026-11-25-ravager-new-specs-screens.png), [Seneca's Effects](img/2026-11-25-ravager-new-specs-seneca-effects.png)):

- **Seneca** (lotulis spec, the Lotulis): Effects **SPECIALIZED IN / LOTULIS** (the new name); the inventory's line
  `+1 Shadowseeker 1.5x2D4+7` (2d4, 3/2 a round, +1 weapon +2 specialized +4 STR).
- **Ester** (two-handed sword spec, the Twohand Sword): **SPECIALIZED IN / TWO-HANDED SWORD**; `Longsword 1.5x1D10+9`.
- **Lex** (gythka spec, the Lotulis: under #181's fold he counted as specialized): **SPECIALIZED IN / GYTHKA**; his
  Lotulis line `2D4+7` at 1 a round, no specialization bonus (the plain rate): the fold is gone.

## Not yet done

- The fight under Computer Control with the dice log (`ns-fight.sh on1`): the attacks a round and "+1/+2 specialized"
  lines; DSCLOG2's counters; `nscheck.py` (the build in memory) and `dosmem.py` (upper memory).
- The control run (`RAV_RULES_OFF=0x1000`).
- No creation pick window to play: the sequel has no weapon window (WEAPON-SPECS.md); the PROBE_WP_* ports there
  are the kit pages' disciplines and spheres windows.
