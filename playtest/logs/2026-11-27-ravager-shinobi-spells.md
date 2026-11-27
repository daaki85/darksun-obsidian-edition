# The Shinobi's wizard spells in Wake of the Ravager (2026-11-27)

Under test: DSCLOG2's THE SHINOBI'S SPELLS (branch claude/ravager-shinobi-spells). A Shinobi (a thief kit)
casts the wizard spells it knows through EL_SPHERE's sites 90-92 (SH_SPHERE_DI/BP). Its casting level
is its thief level less 5, at most 11 (site 209, SHINOBI_CAST_LEVEL, at 97DF1h in the caster level routine
97DC5h). The levels the USE screen offers follow from that: (casting level + 1) / 2, 3rd at most before
thief 13th. The build: DSCLOG2.EXE from the branch (`RAV_LOADER=1`, the Loader's copy from this worktree).

Set-up: a throwaway copy of the sequel, `/tmp/playtest/ravSHN` (never /tmp/playtest/rav). Then
`RAV_LOADER=1 sh ravhold.sh /tmp/playtest/ravSHN`: the Draxans' ambush in Tyr, with Ar'Anda taught Hold
Person by a test edit, and her USE screen up on her turn. The dice log ran with `RAV_NO_SAVES=1` (no quick
saves or autosaves). Every change below is a test edit and nothing was saved. The DOSBox lock was held
from about 00:47 to 01:01 UTC.

The window was 640x480 here (ravstart's), not 320x240. None of the raw-pixel tools were used, and
`ravclick.py` goes by the game's own pointer.

## 1. A Shinobi's MAGE list and the levels it offers (about 00:50 UTC)

Ar'Anda (preserver 6, psionicist 6, thief 7) was made a single-class thief at 13th with the Shinobi kit:
`ravkits.py set 0 0x43 - 17` and `ravkits.py levels 0 13`. She keeps the wizard spells she knew: 0, 3, 8,
11, 13, 17, 24, 27, 29 and 30 (Hold Person). `ravknow.py 44` added a 4th-level spell (Improved
Invisibility, on the Shinobi's list).

- **USE has a MAGE list**, with "SPELLS LEFT WIZ". Pressing LEVEL went 1, 2, 3, 4 and back to 1, and the
  4th level held spell 44. The slots shown were 3, 3, 2, 1 (the Shinobi's table at thief 13th, SHINOBI_MAGE).
- DSCLOG2's counters rose with every redraw (`ravlevel.py counts`): `sh_mages` and `sh_levels_n` (the
  game's "no" made "yes" for her thief class, and the casting level made hers).
- **At thief 10th** (`ravkits.py levels 0 10`: casting level 5, so 3rd at most), LEVEL went only 1, 2, 3
  and back to 1, although she knew a 4th-level spell (`img/2026-11-27-ravager-shinobi-levels-thief10.png`).
- The list shows **every wizard spell she knows**, not only her list's spells. Spells 0, 3, 8, 24 and 27
  are not Shinobi spells, and they were offered because the test edit left them known. SH_YES makes a
  thief class cast any known wizard spell; only learning (level-up, creation, scrolls) keeps to the
  Shinobi's list. So a Shinobi made in the game only ever knows its own spells.

## 2. Hold Person at her casting level (about 00:53 UTC)

She was back at thief 13th (casting level 8). On USE, LEVEL 3, the third icon is Hold Person.

- **Aiming**: a member of the party coloured yellow under the pointer, and a click there gave
  INVALID TARGET (twice, on Terrannus and Gerakis). On the Draxan behind her, a red edge showed and the
  pointer became the spell's own icon (`ravclick.py 164 86 none`, with the party bunched as ravhold.sh
  leaves it). That is the one to press.
- The dice log: "Draxan's saving throw vs Hold Person from Ar'Anda (spell): d20 = 12, needs 13 (40% to
  save) -> failed".
- The effects table (scratch: `ravlog.RavGameData(g, ds, 0).effects_left()` after `ravlog.apply_layout()`)
  showed **Paralyzed (69) on combatant 27, cast by 0, 960 game seconds left: 16 rounds, 2 a level at
  casting level 8**. Her thief level (13) would have given 26 rounds. Without the hook she has no
  casting level at all.
- After the cast the spell pointer stayed up on her turn. A right-click on bare floor dropped it, and the
  turn passed to Thy'rokh.

## 3. The control: a thief 13th with no kit (about 00:58 UTC)

In step 2 the USE screen in a fight showed "ONLY ACTIVE CHAR CAN CAST" when I picked another member's
portrait, so the control needed her turn again. Then I pressed Escape twice: one closed USE and the
second, with nothing open, brought the game's EXIT (rule 7). The keys that followed (ravfight.py's
Q and E) quit it, and DOSBox ended. Nothing was saved: SAVE01.SAV kept its 00:46 time, from ravstart's
widening. The fight was started again with ravhold.sh (dice log `shn-dice2.txt`).

On Ar'Anda's turn, with USE closed (Escape once, USE up):

- **Control**: `ravkits.py set 0 0x40 - 17` and `levels 0 13`, a thief 13th with no kit. USE showed only
  PSIONIC (Kinetics). The list button stayed on PSIONIC, and the counters stayed 0
  (`img/2026-11-27-ravager-shinobi-control.png`, upper row).
- **Then the Shinobi** (`set 0 0x43 - 17`, same turn): USE opened on PSIONIC, the button went to **MAGE
  LEVEL 1** with four spells and "WIZ 4/3", and the counters were at 2 (`img/2026-11-27-ravager-shinobi-use.png`).

My DOSBox (pid 2742) and dice log (2813, 2814) were stopped by pid, and the lock let go at 01:01 UTC.

## Result

- In the sequel, a Shinobi has a MAGE list on USE, its spell levels capped by its thief level, and it casts
  at its thief level less 5. Hold Person at thief 13th lasted 16 rounds (casting level 8).
- With the kit off, the same thief has no MAGE list.
- **Not played**: a level-up pick (site 210), creation's first spells, a scroll (READ LANG. and the INT
  chance) and Spook's save. The emulated tests (`tests/test_ravshinobi.py`) cover them.
- No water: the street in Tyr only.
