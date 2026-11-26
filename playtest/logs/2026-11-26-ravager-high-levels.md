# Test log: weapon specs past 13th level in Wake of the Ravager (2026-11-26)

Under test (branch `claude/ravager-high-level-kits`): DSCLOG2's LV_WEAPONS (site 150, the level up's
psionicist pop-up compare at 957BEh: the weapon window at a level up, as Shattered Lands' LV_CHECK),
`lv_due` (a gladiator's 5th-8th weapon specs at 13th, 17th, 21st and 25th; a fighter's second at 13th, a
Myrmidon's third), SPEC_MORE (the four more specs in the sheet's +45h-+47h, five bits each), SPEC_OF_SHEET
(the second spec specialized at 13th, mastery 17th, grand mastery 21st) and EF_LINES_OF (eight lines).
The owner's choices of 2026-11-26 (proposal: "Classes and kits past 13th level in Wake of the Ravager").

## Before the play

- Tests: test_ravweaponpicks (lv_due for levels 1-30, the eight slots' SPEC_GET/SPEC_SET), test_ravspecialize
  (SPEC_OF_SHEET against specialize.skill with fighters at 17th and 21st and a gladiator at 25th), test_ravlog;
  the whole suite passes (2,821).
- `files/2026-11-26-ravager-high-levels-start.sh` (RAV_LOADER=1 ravstart.sh on a throwaway copy
  `/tmp/playtest/ravLC`, ravdice.py attached, the opening talk, the party up the street) and
  `files/2026-11-26-ravager-high-levels-specs.py` (a member's eight specs shown or set: a test edit).

## The play

Test edits, never saved (DOSBox stopped unsaved): `ravlevel.py set 1 1245000 1 9 12` (Terrannus, human
fighter 12th, long sword), `ravlevel.py set 3 1495000 5 10 12` (Gerakis, half-giant gladiator 12th, long
sword, club, dagger, mace), the Draxans' HP 1, Computer Control for all four, the XP boxes clicked through.

| Member | Before | Seen |
|---|---|---|
| Terrannus, fighter | 12th, long sword | 13th; **the weapon window**, "PICK A WEAPON SPECIALTY, Terrannus", the long sword, double spear and trikal greyed; dagger picked: specs `long sword, dagger`; Effects: **GRAND MASTER OF LONG SWORD, SPECIALIZED IN DAGGER** |
| Gerakis, gladiator | 12th, four specs | 13th; the window with his four greyed (the double spear and trikal open: a gladiator's); trikal picked: the sheet's +45h `14` (kind 20); Effects: SPECIALIZED IN LONG SWORD, CLUB, DAGGER, then (MORE) MACE, **TRIKAL** |
| Thy'rokh, thri-kreen fighter/druid | the sequel's own, no specs | druid 7th: the window too (no spec at all, so one due, as a Shattered Lands game begun before the rule); chatkcha picked. The pointer on a greyed slot names it (SPECIALIZE IN / DOUBLE SPEAR) |

Screenshots (the project's `ravager/` folder): `2026-11-26-ravager-levelup-weapon-window-fighter13.png`,
`...-gladiator13.png`, `...-sequel-own-member.png`, `2026-11-26-ravager-effects-fighter-second-spec.png`,
`2026-11-26-ravager-effects-gladiator-fifth-spec.png`.

**What a play needs to know**: the sequel's 640x480 window maps to ravclick.py's game coordinates as x / 2,
y / 2.4 (the weapon window's slots at game x 75 + 35 a column, y 37, 70, 100, 133 by row). The sequel's own
party has no specs, so the weapon window comes at any of their level ups once the port's rules are on
(ravdice.py attached). A level up's box is clicked at (160,100); a slot under it can take the click, so
grab the screen between clicks.

## Gaps

- No control run (RAV_SKIP=lv_weapons): without the site the level up never asks (the game's compare is
  only the psionicist's).
- Not played: 17th's mastery and 21st's grand mastery of the second spec, a gladiator's 6th-8th, a Myrmidon's
  third (the tests cover them); the Ravager's AC at 15th, expertise at 13th, the Seeker and Justifier tables
  past 10th (the sequel doesn't have the kits' slots yet).
