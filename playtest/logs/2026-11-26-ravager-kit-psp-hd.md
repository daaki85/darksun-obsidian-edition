# Test log: kits' PSP costs, hit dice and casting after a hit in Wake of the Ravager (2026-11-26)

Under test (branch `claude/ravager-kit-psp-hd`, on `claude/ravager-kit-slots`, PR #214): DSCLOG2's PSP_USE,
PSP_TABLE, PSP_DEFENCE, PSP_KEEP, PSP_KEEP_DX (sites 191-195), KIT_HIT_DIE, KIT_HIT_GAIN, KIT_MAX_PSP (196-198)
and HIT_ROUND (199).

Setup: Xvfb :55, the DOSBox lock held by this session (a flock holder), a throwaway copy `/tmp/playtest/ravPH`
of `rav` (cp -a, no hard links), `ravload.sh ravager-after-ambush /tmp/playtest/ravPH`, RAV_NO_SAVES=1. Test
edits only: nothing saved.

## Steps

### 1. Tyr's thieves (about 20:20-20:45 UTC)

`ravager-after-ambush` loaded, the dice log attached (RAV_NO_SAVES=1). Test edits (never saved): Ar'Anda a
preserver 10 (XP 374,000), **Battle Mage** (byte 02); Terrannus a psionicist 7, **Mind Bender** (byte 01),
Psionic Blast known (`ravkits.py power 1 31`); Thy'rokh a human preserver 5 (XP 39,900), **Arcanist** (byte
03); Gerakis a half-giant preserver 10 (XP 374,000), no kit (80h: the control); HP 250 each. Up 8, Right 40
(`ravgo.py`), answer 2, Space: two thieves, two thugs.

- **Psionic Blast, Mind Bender** (the hover reads "PSIONIC BLAST 18 10": 10 PSP): the power check failed
  ("Message: psionic power check fails"); PSP **200 to 196**, half of the Mind Bender's 8 (the plain cost's
  half is 5).
- **The hit's mark** (308h:0B2h + creature; the helper's `hr_seg` names the segment): Gerakis, the plain
  preserver, hit: **1**; Ar'Anda, the Battle Mage, hit: **0** (`bm_hits` counted each).
- **The Battle Mage hit, then casting**: Ar'Anda's DEX made 3 (creature +1Ah, sheet +16h) so she acts last.
  Round 3: a thief hit her twice (244, then 238 HP) before her turn; on her turn USE showed her 2nd-level
  spells (Detect Invisible, Invisibility, Web) **not crossed out**, WIZ 2/3, and Detect Invisible was cast
  (2nd-level casts 2 to 1): `img/2026-11-26-ravager-battle-mage-hit-cast.png`.
- **The control, in the same fight**: her kit byte made 80h (no kit). Round 4: a thief hit her (236, 233)
  before her turn; mark **1**; on her turn USE showed the three **crossed out** (and WIZ 1/4: without the
  kit her wizard slots are the preserver's, one more than the Battle Mage's):
  `img/2026-11-26-ravager-battle-mage-control.png`. Kit byte back to 02.
- **Psionic Blast's cost, the kit changed between turns** (Terrannus's kit byte; PSP read from the creature's +2):

  | Kit (byte) | The power | PSP | Paid | kits.psp_cost |
  |---|---|---|---|---|
  | Mind Bender (01) | check failed | 200 to 196 | 4 | half of 8 |
  | Mind Bender (01) | used (the thief saved) | 59 to 51 | 8 | 10 - 2 |
  | Kineticist (03) | used | 51 to 39 | 12 | 10 + 2 |
  | none (80h, control) | check failed | 39 to 34 | 5 | half of 10 |
  | none (80h, control) | used (the thief failed its save, 36 damage) | 34 to 24 | 10 | 10 |

  (ravkits.py's 200 PSP were held to his most, 59, at a round's start.) The USE screen's hover still shows
  the table's cost ("PSIONIC BLAST 18 10") whatever the kit.
- **The level ups at the fight's end** (the foes' HP made 1, `ravlevel.py foes 1`; Terrannus made a **Mind
  Warrior** (byte 02), XP 99,900, his most PSP (sheet +0Ch) made 1 so the level's is written whole):

  | Member | Level | Base HP (sheet +0Ah) | Expected |
  |---|---|---|---|
  | Ar'Anda, Battle Mage | preserver 10 to 11 | **102 to 104** | the gain past the dice: 2 (kits.hit_gain) |
  | Gerakis, no kit (control) | preserver 10 to 11 | **123 to 124** | the preserver's 1 |
  | Thy'rokh, Arcanist | preserver 5 to 6 | **87 to 89** | a d3 (twice, the better: `kit_hds` went up 2 for his two rolls) |
  | Terrannus, Mind Warrior | psionicist 7 to 8 | 50 to 55 ("hit points d6 = 5 and 2, the better 5") | most PSP **104** |

  `kit_hds` 3 after them (Ar'Anda's gain, Thy'rokh's two dice). The Battle Mage's level up asked for a
  weapon of expertise (the window; long sword taken). The dice log's "hit points dN" line came only for
  Terrannus's roll.

### 2. The control for the level ups, and a Battle Mage's d6 (about 20:50-21:15 UTC)

DOSBox and the dice log of step 1 stopped by pid, `ravager-after-ambush` loaded again into the same copy,
the dice log attached (RAV_NO_SAVES=1). Test edits, never saved: Ar'Anda a preserver 10 (XP 374,000), no kit
(80h); Terrannus a psionicist 7 (XP 99,900), no kit (80h), his most PSP made 1; Thy'rokh a human preserver
5 (XP 39,900), no kit (80h); Gerakis a half-giant preserver 5 (XP 39,900), **Battle Mage** (02); HP 250. The
thieves' fight again, the foes' HP 1 (`ravfight.py fight` got "NO PATH FROM HERE": the foes clicked by hand).

| Member | Level | Base HP | Step 1 (the kits) |
|---|---|---|---|
| Ar'Anda, no kit | preserver 10 to 11 | **102 to 103** (the preserver's 1) | Battle Mage: 102 to 104 |
| Terrannus, no kit | psionicist 7 to 8 | 50 to 54 (d6 = 4 and 3) | most PSP **129** here, **104** for the Mind Warrior: 129 less its fifth (25) |
| Thy'rokh, no kit | preserver 5 to 6 | 87 to 90 ("hit points **d4** = 3 and 2, the better 3") | Arcanist: 87 to 89, two d3 rolls |
| Gerakis, Battle Mage | preserver 5 to 6 | 123 to 131: the d6's best of two, doubled for a half-giant (the game's 95059h); `kit_hds` 2 | - |

`kit_hds` 2 (Gerakis's two d6 rolls), `kit_psps` 0 (no kit with a PSP part in this run). DOSBox and the dice
log stopped by pid, nothing saved, the lock let go.

### 3. The creation screen: a kit's hit points and PSP (about 21:00-21:16 UTC; PR #218's review)

Under test: DSCLOG2's CR_DIE (site 200, 6D28Fh), CR_PSP (site 201, 6D85Eh with the WIS test's `jna` at 6D842h
sent to it) and KIT_REROLL on the kit page (KIT_ROW). Set-up: a throwaway copy `/tmp/playtest/ravCG` of `rav`,
`RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 sh ravstart.sh /tmp/playtest/ravCG`, the dice log `ravdice.py`
(RAV_NO_SAVES=1, rules_hi 0xFF3F: kits on), the lock held throughout. The helper's code in memory checked
against the build (cr_die, cr_psp, kit_reroll, kit_row, kit_made, wp_harvest: the same bytes). CREATE
CHARACTERS, NEW, a human of 7th level; each reading is `ravkits.py page` (now with the hit points, their range,
the PSP and the creation counters).

The first run found the kit byte left none (00, not KIT_OPEN) after a kit was taken back, so another kit's row
took no click: the hit points' routine copies the sheet back from the party's stand-in (6EE5Eh), whose copy
made KIT_OPEN none. KIT_REROLL now puts the kit byte back after it; the run below is after that fix.

**A preserver (SeanBoy; CON 18):**

| Step | Kit byte | Hit points (least, most) | PSP |
|---|---|---|---|
| PRESERVER clicked (control) | 00 | 31 (21, **42**: 7 d4) | 27 |
| BATTLE MAGE | 02 | **46** (21, **56**: 7 d6) | 27 |
| taken back | FF | 38 (21, 42) | 27 |
| ARCANIST | 03 | 30 (21, **35**: 7 d3) | 27 |
| taken back | FF | 35 (21, 42) | 27 |
| SCHOLAR (control: no roll again) | 01 | 35 (21, 42) | 27 |
| Scholar back, BATTLE MAGE | 02 | 48 (21, 56) | 27 |
| CON lowered to 15, then 14 | 02 | 41 (14, 49), 34 (7, 42) | 26 |

`kit_rerolls` 5, `kit_hds` up 14 a roll (seven levels, two dice each: the better of two). Pictures:
[the preserver's page](img/2026-11-26-ravager-creation-battle-mage-control.png) and
[the Battle Mage's](img/2026-11-26-ravager-creation-battle-mage.png) (JohnBoy, CON 19: 38/38 and 44/44).
DONE (no spell picked, no powers, the weapon window's defaults): member 0 **34/34**, kit 02. With CON 14 a
preserver's most is 28: 34 is past it. **EDIT** of him: kit 02 kept, hit points 34 (7, **42**), the d6's range
(a preserver's 28 would have cut them to 28).

**A psionicist (Killer):**

| Step | Kit byte | Hit points (least, most) | PSP |
|---|---|---|---|
| PSIONICIST clicked (control) | 00 | 32 (7, 42) | **98** |
| MIND WARRIOR | 02 | 29 (7, 42) | **79** (98 less its fifth, 19) |
| taken back | FF | 33 | 98 |
| MIND BENDER (control: no roll again) | 01 | 33 | 98 |
| Bender back, MIND WARRIOR | 02 | 28 | 79 |
| INT lowered | 02 | 28 | 78 (the routine run again, `cr_psps` up) |
| the die rolled | 02 | 49 (21, 56) | 78 |

The screen showed 79/79 ([picture](img/2026-11-26-ravager-creation-mind-warrior.png)). DONE: member 1 49/49 HP,
**78/78** PSP, kit 02. A second psionicist (JohnBoy, slot 3): no kit **109**, Mind Warrior **88** (109 less 21:
[control](img/2026-11-26-ravager-creation-mind-warrior-control.png)); then left without DONE (EXIT).

STDOUT.TXT empty (no "Illegal Op"). Nothing saved; DOSBox and the dice log stopped by pid, the copy deleted,
the lock let go. Not played: a stale kit taken away on a multiclass click (CR_KIT_STALE: the tests cover it;
a human must click a class off first, which KP_CLASS already clears). The dice log's lines for the kit page's
rolls name the rolls of the class click only (its creation lines aren't the kit's).

**Transferred and own characters**: the new sites are on the creation screen's routines only (the hit points'
routine 6D1EDh, the PSP routine 6D75Dh, the kit page), which a party brought from Shattered Lands or the
sequel's own party never runs: their hit points and PSP stay as they come (SL's kit rolls already in them); the
own party has none of these kits (kits.OWN_FEATURES). An EDIT of one runs the screen's routines on a click as
before, with its kit's range.

## Result

In the sequel now, as in Shattered Lands: the Mind Bender's and Kineticist's PSP costs (a power used and a
failed check's half), the Mind Warrior's fifth fewer PSP at a level up, the Battle Mage's d6 and Arcanist's
d3 hit dice, the owner's 2 (Battle Mage) past 10th against a preserver's 1, and a Battle Mage casting
though hit before her turn (a plain preserver's spells crossed out in the same fight); and on the creation
screen a Battle Mage's d6 and Arcanist's d3 range and roll, and a Mind Warrior's fifth fewer PSP, as the kit
is chosen, taken back, on a score's click and on EDIT.

## What a play needs to know

- The USE screen's hover shows a power's table cost, not the kit's.
- ravkits.py's 200 PSP are held to the sheet's most at a round's start.
- `ravfight.py fight` in the thieves' alley stalls on "NO PATH FROM HERE"; click the foes by hand (the walk
  arrow over one shows its to-hit).
- To have a member hit before her turn, DEX 3 (she acts last); a kit byte changed between turns takes at
  once, so the control can share the fight.

## Gaps

- Not played: the Titan Mind's and Wasteland Seer's costs, a power kept up, a defence raised (the tests
  cover them, `test_psp_cost`), an Arcanist past 10th (the same gain as a preserver's).
- The creation screen's kit hit die and PSP: in since step 3 (the die read is at 6D28Fh, `mov al,es:[bx+11Dh]`:
  ravsites' likeness search missed it for its other displacement). Shattered Lands' 11th still gives a Battle
  Mage the preserver's 1.
- Water: nothing new (Tyr's streets, as before).
