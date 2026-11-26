# For yuan-ti: corrections to our notes of 20 October, and what we found since (2026-11-25)

*Status: not posted. For `.github/instructions/ref_notes_from_obsidian.md` in yuan-ti (written 20
October 2026 against yuan-ti 9c1952b; yuan-ti's newest commit is still f61c5bd, 7 November). Facts and
DSUN.EXE file offsets (GOG 1.10) only, free to use as the notes were. Spell numbers here are ours,
from 0; yuan-ti's SPIN numbers are one higher.*

## 1. Corrections: what the notes say that isn't so

1. **Hold Undead does not hold the living** (notes 1.3 and the section 5 row). The landing routine's
   `or al,al / je` at 7A333h does go on for any spell, but every spell's targets, one creature's too,
   are gathered by the area code (846D0h) and sifted by 7A897h, whose case for Hold Undead asks the
   undead test (7BE20h) as well, so a living target is dropped before it lands. yuan-ti's
   undead-only whom-table is the original's behaviour, not a fix: it belongs out of `CombatFixes`.
   (OpenDS reached the same reading independently.)
2. **Slowed rules out pick pockets only** (notes section 4: "Slowed stops all but pick pockets").
   yuan-ti's `dsun-exe-reference.md` already has it right (−1000 to pick pockets at 80425h); our
   notes had it backwards.
3. **Scare allows no save at all in the original** (notes section 5's Scare row, and "Against
   Scare" in section 6). Scare's record has its save byte (+1Fh, file 4222Fh) at A0h, with bit 0
   ("a save is allowed") clear. So the saving throw (79A71h) answers "not saved" at its first test
   (79A89h), before any modifier. The level test (6th and up +100, below −100) and the
   elf-and-half-elf test the notes describe sit behind it and never run. When they do run (with the
   save bit set), the test reads "a priest whose race is 3 and is 4" (79FEAh, 7A011h). yuan-ti's
   resist-fear reading of it is the one we now use.
4. **Cure Critical Wounds heals 3d8+3** (notes section 5, Cause Serious/Critical row). This still
   stands, and we have since checked it against the code because OpenDS's docs say 3d8+1. The
   spell switch at 7957Dh (spell 112: 2d8, then `inc ax`) and 7958Fh (spell 127: 3d8, then
   `add ax,3`) settles it.

## 2. Added to what the notes say

- **Facing and missiles** (notes 1.1): a missile also counts as from behind by the target's facing,
  at any distance (+2 to hit, the target's DEX and shield lost), so a ranger's arrows from across
  the room each get it. We count only melee that way now.
- **Two weapons** (notes 1.4): unchanged.
- **Level cap:** the game stops class levels at 9 (the level-up compare at 87BE6h, View Character at
  67D08h), although its XP, HP, THAC0 and save tables go on to 20. (OpenDS, from our code.)
- **The dice log as a test oracle** (notes section 8): the notes say "replay ... from the same seed
  and compare". What exists is a live labelled log, with no seed capture and no replay. The RNG call
  (5C22h) goes through a hook that records the caller, and each roll is labelled by the calling
  code. A replay would need the seed captured and set (the RNG's state at DS:4124h, unchecked) and a
  diff step. Neither side has built it yet.

## 3. Original bugs found since 20 October

Each is in our `obsidian-edition/GAME-BUGS.md` (what the game does and our fix), with the code in
`DEVELOPMENT-CONTENT.md` and `DEVELOPMENT-RULES.md`. Check them against `CombatFixes` and `GplRepairs`.
Some of these were yuan-ti's finds to begin with (marked).

- **Cloak of Bravery:** its +4 against fear and its charge apply only to a spell with 100h in its
  record's +11h word (the test at 7B140h, from the save modifiers at 79EBDh), and no spell has it.
- **Bless and Aid:** the "enemy within reach" filter (7B03Dh) pushes the creature's x twice in
  place of x and y.
- **Absorb Disease** (power 147): runs on into Strength's case (7943Eh into 79470h), giving the
  psionicist 1d6 STR. (yuan-ti's.)
- **Most PSP:** the WIS bonus is read from the creation screen's record, and the bonus tables stop
  short of 22-25. (yuan-ti's.)
- **Missiles from behind** (above), **Acid Arrow**, **Psionic Blast on a party member** (real
  wounds; yuan-ti's issue #129), **walls cast by monsters**, **random monsters** (a vanishing body,
  a survivor's warning), **resting while poisoned with a druid of 7th level or more**, **XP for high
  prime requisites**, **the thief skills' equipment penalty**, **View Character's DAM line** with a
  wooden, bone, stone or obsidian weapon, **graphics disappearing in a busy area** (300 picture
  slots never freed until the next area).
- The scripts: **the sewer grate** (yuan-ti's repair names the wrong weapon: the weapon search goes
  round once more after its find and copies the next item over it; leave the loop on the find, its
  RETURN at 137:A96h), **Kurzak's door**, **Kurzak calling for Legcrusher once he is dead**,
  **Legcrusher sent to a party at the fountain**, **Pehtucl's ambush**, **Alhena's campfire**
  (reachable: GF[123] is set only when the caravan turns on the party), **Dagolar's slime book**.
