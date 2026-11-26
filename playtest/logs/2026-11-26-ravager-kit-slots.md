# Test log: kit spell slots in Wake of the Ravager (2026-11-26)

Under test (branch `claude/ravager-kit-slots`, on `claude/ravager-own-party`, PR #207): DSCLOG2's ADND_SLOTS
(site 34) with SLOT_BEHIND's new parts (a Battle Mage's wizard slots 1 fewer, SB_TABLE), KIT_TABLE (the
Seeker's, Justifier's and Shinobi's own tables, WIS left out), SHINOBI_MAGE (site 190, 627D6h: the slot
routine's "casts wizard spells" yes for a Shinobi's thief class) and VEILED_SLOT for a Shinobi.

Setup: Xvfb :55, the DOSBox lock held by this session (flock holder), a throwaway copy `/tmp/playtest/ravKS`
of `rav`, `ravload.sh ravager-roost /tmp/playtest/ravKS` (the Loader's copy with this branch's DSCLOG2),
`ravdice.py` attached. Test edits only (ravkits.py set / levels): nothing saved.

## Steps

### 1. Battle Mage, Shinobi, Justifier at 9th: a rest at the Roost (about 19:55-20:05 UTC)

`ravager-roost` loaded, the dice log attached (RAV_NO_SAVES=1: no quick saves or autosaves). Test edits
(`ravkits.py set` / `levels`, never saved):

| Member | Made | The game's casts left after the rest (DS:446Ah + 22h a member) | kits.slots |
|---|---|---|---|
| 0 Ar'Anda | thief 13, **Shinobi** (byte 03) | wizard **3 3 2 1** | the Seeker's 13th row: 3 3 2 1 |
| 1 Terrannus | ranger 14, Seeker | not rested: **dead in this save** (status 7; the rest skips him) | - |
| 2 Thy'rokh | ranger 9 (class 14), **Justifier** (byte 02) | priest **0 0 0 0** (was 6 4 3 1) | none before 10th |
| 3 Gerakis | preserver 9, **Battle Mage** (byte 02) | wizard **3 2 2 1 0** | AD&D's 4 3 3 2 1, each 1 fewer |

The Roost's route (RESEARCH.md): Reyhan, keys 1 3 4, Space, one right-click (the arrow), Left 4, Down 9,
Right 14, the second doorway's steps at game (253,90), Up 6, two right-clicks (the look), the ring at game
(267,121). The dice log: the rest's Cell Adjustments, then THE PARTY RESTS. DSCLOG2's counters after:
`sb_count 5` (the Battle Mage's five 1 fewer), `kt_count 4` (the Shinobi's four spell levels from the table),
`sh_mages 9` (SHINOBI_MAGE's yes), `slot_count 18`.

USE for the Shinobi: only her PSIONIC list (no MAGE list: the USE screen offers spells by class, so a Shinobi
still can't cast in the sequel; its spells and casting level are the audit's step 7). Gerakis, a preserver
with no wizard spells known, likewise.

### 2. Seeker, Justifier at 12th, and two controls: a second rest (about 20:10-20:20 UTC)

`ravager-roost` loaded again (DOSBox and the dice log of step 1 stopped by pid first), the dice log attached
(RAV_NO_SAVES=1). Test edits, never saved; Terrannus made alive for it (creature +14h 7 -> 1, HP 40).
Kit byte 80h (Friends known, no kit) for the controls, so the Loader doesn't give the own party's features
back.

| Member | Made | Casts left after the rest | Expected |
|---|---|---|---|
| 0 Ar'Anda | ranger 14 (class 13), **Seeker** (byte 03) | priest **3 3 3 1** (WIS left out) | the owner's Table 51, 14th: 3 3 3 1 |
| 1 Terrannus | ranger 9 (class 14), **no kit** (control) | priest **2 0 0 0** | AD&D's ranger 9th (and WIS's) |
| 2 Thy'rokh | ranger 12 (class 14), **Justifier** (byte 02) | priest **2 1 0 0** | Table 46, 12th: 2 1 |
| 3 Gerakis | preserver 9, **no kit** (control) | wizard **4 3 3 2 1** | AD&D's preserver 9th (the Battle Mage of step 1: 3 2 2 1 0) |

DSCLOG2's counters: `kt_count 8` (the two tables' rows read at spell levels 1-4), `sb_count 0`, `sh_mages 0`.
All four rested ("... rests 8 hours").

USE (the top-left icon) after the rest, the Loader's SPELLS LEFT lines and the game's crossings-out:
- the Seeker: CLERIC LEVEL 1 **PRI 3/3**, LEVEL 4 **PRI 1/1**, LEVEL 5 every spell crossed out and no line (her
  casting level 9 reaches 5th-level spells, her table none): `img/2026-11-26-ravager-seeker-use-slots.png`;
- the Justifier: CLERIC LEVEL 1 **PRI 2/2**: `img/2026-11-26-ravager-justifier-use-slots.png`.

DOSBox and the dice log stopped by pid, nothing saved, the lock let go.

## Result

The sequel's own rest now gives the kits' slots as Shattered Lands does: the Battle Mage's wizard slots 1
fewer, the Seeker's and Justifier's priest slots their own tables (WIS left out), the Shinobi's wizard slots
the Seeker's table by thief level; the controls the plain classes' AD&D slots.

**The Justifier at 8th or 9th** (the audit's possible bug): real before this. The caster level routine
(97DC5h) starts its best at 0 and compares signed, so a Justifier's "ranger level - 9" (site 61) of -1 or 0
became caster level 0, and RANGER_LEVEL held the spell's duration and damage level at 0; with the plain
ranger's first slot (AD&D's from 8th) he could cast at level 0. Now he has no slot before 10th (seen: 0 0 0 0
at 9th), as in Shattered Lands, so nothing is cast at level 0.

## What a play needs to know

- In `ravager-roost` **Terrannus is dead** (creature +14h 7): a rest skips him (no HP, no slots). Make him
  alive for a slot test (+14h 1 and some HP, a test edit).
- The USE screen offers a MAGE or CLERIC list by class and spells known, not by slots: a Shinobi (a thief)
  with slots and the wizard spells Ar'Anda knows still shows only PSIONIC.
- In the rented room the ring was at game (267,121) in one run and (267,110) in the other: grab the screen
  after Up 6 and click the ring where it is.

## Gaps

- The Shinobi's slots are counted at a rest, but it can't cast in the sequel yet (no MAGE list, no casting
  level, no spells learnt: the audit's step 7).
- The Veiled Robe on a Shinobi (VEILED_SLOT's new case) not played (the tests cover it through KIT_TABLE's
  SB_TABLE; VEILED_SLOT itself unchanged but for the class test).
- Water: nothing new (the Roost, as before).
