# 2026-11-24: the Girdle of Back Defense and the Amulet of Magic Resistance in play (sequel)

**Under test:** branch `claude/ravager-stealth` (8aa2680), the dice log knowing the sequel's girdle and
amulet types (bc4e5df). Test edits in memory, never saved. Scratch tools in `/tmp/playtest`:
`girdlerun.sh`, `girdletest.py`, `amuletrun.sh`, `amulettest.py`, `rgear.py`, `ravdice_items.py`.

## The girdle: SEEN WORKING

The transferred party's Tyr ambush (freshly transferred, the sound-word fix in), computer control for
all four, every thief and ranger hiding (`RAV_STEALTH_ROLL=1`), party HP 250.

- Run g1 (`foes --except 21`): the only hidden attack fell on Draxan#21, the control without the
  girdle: `Seneca attacks Draxan#21 BACKSTAB with Bone item 291 +1 ... target AC 7`, `stealth_used`
  0 -> 1, `girdle_count` unchanged. As it should be without the girdle.
- Run g2 (`foes`: every Draxan wears the girdle, type 129, slot 5):
  - Seneca hidden and unheard, then `Seneca attacks Draxan#26 with Bone item 291 +1 ... target AC 3`:
    no BACKSTAB, no rear bonus (AC 3, as from the front); `girdle_count 0 -> 2` (the backstab and the
    rear both taken back), `stealth_used 0 -> 1`.
  - Jenna hidden and unheard, then `Jenna attacks Draxan#27 ... target AC 2`: no rear bonus;
    `girdle_count 2 -> 3`, `stealth_used 1 -> 2`.

## The amulet: NOT YET SEEN

The opening party's Draxan fight (`ravhold.sh`), the amulet on every foe, Stinking Cloud and Hold
Person taught to Ar'anda. 20 automatic rounds cast nothing: the USE screen showed the spell picked
("HOLD PERSON" at the bottom) but no aiming followed, and the box read "NO SPELLS IN ARMOUR" for
Ar'anda (the dice log's slot lines: `game.no_spells`, the class-restriction rule for a multiclass
preserver in armour). Setting her base AC back from the test's -10 didn't change it. To try next: a
priest's Hold Person from Terrannus, or find what the sequel counts as Ar'anda's armour.

Water: none new (no new area).
