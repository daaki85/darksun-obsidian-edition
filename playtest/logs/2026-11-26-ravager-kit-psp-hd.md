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

## Result

In the sequel now, as in Shattered Lands: the Mind Bender's and Kineticist's PSP costs (a power used and a
failed check's half), the Mind Warrior's fifth fewer PSP at a level up, the Battle Mage's d6 and Arcanist's
d3 hit dice, the owner's 2 (Battle Mage) past 10th against a preserver's 1, and a Battle Mage casting
though hit before her turn (a plain preserver's spells crossed out in the same fight).

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
- Not ported: a new character's kit hit die and PSP on the creation screen (SL's creation die read has no
  likeness in the sequel). Shattered Lands' 11th still gives a Battle Mage the preserver's 1.
- Water: nothing new (Tyr's streets, as before).
