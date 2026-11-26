# 2026-11-26: picking weapon specs at creation in Wake of the Ravager

**Under test:** branch `claude/ravager-spec-pick` (on `claude/ravager-new-specs`): DSCLOG2's WEAPON PICKS (sites
120-125: CR_WEAPONS at DONE 6E2ECh; PK_WIN, PK_TITLE, PK_FILL, PK_CLICK, PK_HOVER in the psionicists' pop-up),
the Loader's weapon window for the sequel (weaponpages.rav_chunks: RESOURC2.GFF's WIND 3021, BMP 3022, ICON/BUTN
8C0h-8D5h, PLNR pictures). DSCLOG2.EXE 48064 bytes.

**Set-up:** a throwaway copy `ravWP` of `$WORK/rav` (game.gog hard-linked, the roster reset from __support/save),
`RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 sh ravstart.sh /tmp/playtest/ravWP`, the dice log `ravdice.py 6000`, the DOSBox
lock held throughout.

## Steps

**1. A fighter (Borzak, slot 1, human, 7th level).** CREATE CHARACTERS, a right click on slot 1, NEW, the default
FIGHTER, DONE (279,183). First the powers' pop-up (CR_PICKS: Kinetics, three picks at 121,62). Then the **weapon
window**: four rows of six slots, the sequel's own weapons' pictures, the double spear and trikal greyed (a
gladiator's only), EXIT with the picks left (1) beside it; off the slots its title "PICK A WEAPON SPECIALTY, /
Borzak" under them. The pointer on the lotulis slot (245,100): the slot lit, "SPECIALIZE IN / LOTULIS" ([the picture](img/2026-11-26-spec-pick-fighter.png)). A click:
the window closed (one pick due), the Loader's gear ("Borzak starts with more gear: Sling"), View Character.
`ravspecs.py`: sheet 0 specs `65c4c9` (V3, the roll 4 kept by the Loader's age pass): **lotulis**; wp_asks 1,
wp_picked 1, wp_filled 0; lv_avail after 0x31FFFF (all but the double spear, trikal and the lotulis taken).
Effects: **MASTER OF LOTULIS** (a 7th-level fighter: mastery from 5th).

**2. A gladiator (Killer, slot 2, human, 7th level).** FIGHTER off, GLADIATOR (255,37), DONE, the powers' three
picks, then the weapon window with **three picks** (a gladiator's two, a third at 6th level: the sequel's new
characters are 7th), the double spear and trikal in use ([the pointer on the double spear](img/2026-11-26-spec-pick-gladiator.png)).
The double spear (75,134): its slot greyed, the window up (lv_left 2); the two-handed sword (211,100): greyed, the
window up (lv_left 1); the long sword (75,32): the window closed. Sheet 1 specs `f6cbc9`: **double spear, long
sword, two-handed sword** (V3 keeps the first picked first, the rest in kind order); wp_picked 4. Effects:
**SPECIALIZED IN / DOUBLE SPEAR / LONG SWORD / TWO-HANDED SWORD**.

**3. A thief (Cromwell, slot 3): offered nothing.** FIGHTER off, THIEF (255,69), DONE, the powers' picks, then
straight to View Character: no weapon window (wp_asks still 2), sheet 2 no specs.

**4. EDIT keeps the picks (Hamonde, slot 4, a fighter).** NEW (162,117), DONE, the powers, the weapon window: the
**club** (109,32). In View Character (Hamonde still "New") a right click on his portrait gives **EDIT** / DROP /
DUAL (EDIT NAME once a character is "Okay": the game offers EDIT only while the creature's status is 0); EDIT
(170,117) opened the creation screen (editing 3). DONE with nothing changed: no weapon window (wp_asks still 3),
sheet 3 specs `4554cd`: the club as it was.

**5. EDIT into a gladiator: the rest asked, EXIT filling them.** EDIT again, FIGHTER off, GLADIATOR, DONE: the
weapon window, **PICK A WEAPON SPECIALTY, / Hamonde**, the club greyed (his already), the double spear and trikal in
use, two picks left (3 due at 7th level, 1 had). EXIT (228,176): "YOU HAVE MORE" / EXIT / CANCEL; EXIT (112,92):
WP_FILL gave the **long sword** and then the **dagger** (the club his: the first left), wp_filled 2. Sheet 3:
classes [10], specs club, long sword, dagger.

`ravspecs.py check`: the first 40 bytes of the WEAPON PICKS routines in memory the same as dos/DSCLOG2.EXE;
DSCLOG2's rules 0xFB45 (RULE_SPECIALIZE on). STDOUT.TXT empty so far.

**6. The four in Tyr: the specs in the dice log.** START GAME from View Character's bar (270,171): DOSBox (the
dynamic core) died during the opening cinematic, nothing saved but the roster (CHARSAVE.GFF, written at the
character screen's close). Started again with `RAV_CORE=normal`, `RAV_MENU=1`: the party empty, so CREATE CHARACTERS
and ADD (right click, ADD at the menu's second line; the roster list from (100,45), 11 a row; ADD 253,46) for
Hamonde, Borzak, Killer and Cromwell. `ravspecs.py`: **the picks came back from the roster as made** (Hamonde
`5d54cd` club, long sword, dagger; Borzak `65c4c9` lotulis; Killer `f6cbc9`; Cromwell none). The bar's (270,171) to
the title, S: START GAME, the cinematic, the Veiled Alliance's talk: (100,171) twice and the Draxans' ambush. The
dice log `RAV_NO_SAVES=1 ravdice.py --numbers` attached in Tyr (no saves in this run: memory edits follow);
Computer Control (C, then 47,53 / 98,53 / 47,112 / 98,112), HP 250 each (`ravkits.py hp M 250`, a test edit).
- **Killer and Hamonde** (each two Longswords +1, the right hand's and slot 10's, both specialized): **3 swings a
  turn every round** (9 rounds each), the first at -1/-2 ("THAC0 14 base, -2 in bonuses, +1 specialized = 15"),
  each hit "1d8 = [8] +1 weapon +2 specialized +1 STR 17".
- **Borzak** (lotulis): his right hand holds a type 91 (flags 4: not a weapon), his Longsword +1 in slot 10: one
  swing a turn, no spec line. A test edit (never saved) made the slot 10 sword's type the Lotulis (61): "Borzak
  attacks Draxan#27 with Stone Longsword +1 (2d4+1) ... THAC0 14 base, +2 in bonuses, **+3 mastery** = 9" and
  "2d4 = [3 + 3] +1 weapon **+3 mastery** +1 STR 17" (the item keeps its name; the type's 2d4). Still one swing a
  turn (that slot's attacks). The fight won in round 10 (10,000 XP each).
- Cromwell (thief) 2 swings a turn (dagger and sword), no spec lines.

**7. The control: `RAV_SKIP=cr_weapons,pk_win,pk_title,pk_fill,pk_click,pk_hover`.** DOSBox stopped by pid, started
again with the skip (DSUNLOG2.EXE's six places hold the sequel's own bytes, checked), the dice log attached (rules
0xFB45: RULE_SPECIALIZE on), CREATE CHARACTERS, NEW in slot 2, the default FIGHTER (Elstar), DONE: the powers'
pop-up as before (its picks at 118,59), then straight to View Character: **no weapon window**, wp_asks 0, no specs.
(A fighter made before the dice log was attached, T'Sharr, also none: DSCLOG2's rules word is 0 until the Loader
writes it, so a check of the pick needs the Loader or the dice log attached.)

**8. Memory.** `dosmem.py` in the control's DOSBox (the same DSCLOG2): DSCLOG2's block 47,536 bytes; **upper memory
free 108,064 bytes, the largest piece 107,920** (about 109,800 before: 1,952 bytes more resident). Conventional
free 88,816 (the largest 85,696). STDOUT.TXT empty throughout.

## Gaps

- No picks after DUAL (SL asks for the new class's due there); no kit weapons as defaults, no KIT_ALLOWS or
  KIT_FORBIDS (the sequel's kits have none yet); the starting weapon isn't the first pick's kind.
- The order is spells, powers, then the weapons (SL: the weapons before the powers).
- The count label by EXIT is faint (the game's own colours for the powers' count).
- An EDIT that takes the warrior class away keeps the specs it had.
- The dice log prints "Loader error in the dice log: TypeError ... (ravlog.py:1142)" at its attach in these
  sheets (it carries on); not this branch's.

## 9. A new fighter's attacks a round with his one specialized weapon (later the same day)

**Under test:** the same branch (tip 28c84e5, DSCLOG2.EXE rebuilt from dsclog2.asm: the same bytes). Does a fighter
who picked his spec at creation get the specialist's attacks a round with one weapon? Borzak (above) swung once a turn
only because his sword was in the left hand.

**Set-up:** a throwaway copy `ravSP3` of `$WORK/rav` (the roster reset from __support/save), `RAV_LOADER=1 RAV_MENU=1
RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh /tmp/playtest/ravSP3`, the DOSBox lock held throughout, the dice log
`RAV_NO_SAVES=1 ravdice.py --numbers` (attached **before** the picks: Ulf, made first without it, got no weapon window,
DSCLOG2's rules word 0). Three 7th-level human fighters made with NEW, the default FIGHTER, DONE (279,183), the
powers' three picks (121,62), then the weapon window: **SeanBoy long sword** (75,32: "SPECIALIZE IN / LONG SWORD"),
**Dag club** (109,32), **Ulf none** (made before the dice log). `ravspecs.py`: SeanBoy `434dcf` ['long sword'], Dag
`4554c1` ['club'], Ulf `4146c1` [] (wp_asks 2, wp_picked 2). On the creation screen the human fighter shows `1/1`.
(At the roster's right-click menu NEW is game y 57, ADD 69 on slot 1; slot 3's NEW 115,117. The roster's own four,
Clk'whrr, Meggyn, Zontorra, Borzak, are the list's last.)

**The gear a new fighter starts with** (`items.py`, scratch: each member's items and slots): bone arm, chest and legs,
a **+1 shield (91) in slot 3, the right hand**, and the **+1 Longsword (97) in slot 10, the left hand**; party member
0 also an Obsidian Dragonsbane +4 (73) in slot 14, which Computer Control put in his left hand in the first round (a
second weapon: 1 more swing a turn). So **a new fighter's sword is in the off hand, one swing a round whatever his
skill**, until the player moves it to the right hand. Test edits (never saved): each one's sword to slot 3, the shield
to slot 14 (Computer Control put it back in the left hand: no weapon), the Dragonsbane's type made the shield's (91),
HP 250. The sheet's attacks a round (+24h) read **4 halves (2 a round)** for all three: the game's own rate for a
7th-level fighter (the specialist's, as SL's).

**Run 1** (Ulf member 0, the Dragonsbane his second weapon) and **run 2** (DOSBox stopped by pid and started again,
CREATE CHARACTERS, ADD SeanBoy, Dag, Ulf, START GAME from the bar, one weapon each), the Tyr ambush under Computer
Control, both won (10,000 XP each), nothing saved (SAVE01.SAV's time unchanged). Swings a turn from the dice log's
"X attacks Y with Longsword +1" lines, by round:

| Round | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SeanBoy, long sword spec (mastery), run 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Dag, club spec, the long sword (not chosen), run 2 | moved | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 1 (the last foe killed) |
| Ulf, no spec, run 2 | 2 | 2 | 2 | 2 | 2 | down | | | | | | | | |
| SeanBoy, run 1 | moved | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | | |
| Dag, run 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | down | | | | | | |
| Ulf, run 1 (+ the Dragonsbane, 1 a turn) | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | | |

- **SeanBoy**: every swing "THAC0 14 base, +2 in bonuses, **+3 mastery** = 9" and "1d8 = [8] +1 weapon **+3 mastery**
  +1 STR 17" (28 swings in run 2: 14 rounds x 2). **2 a round: the specialist's rate at 7th-12th level** (WEAPON-SPECS.md's
  table: a chosen weapon spec 3/2 at 1st-6th, 2 at 7th-12th, 5/2 at 13th; the 3/2 at 7th-12th is a warrior's with a
  kind not chosen). The game's 4 halves kept.
- **Dag** (a spec, not this kind: SPEC_PLAIN): "THAC0 14 base, +2 in bonuses = 12", "1d8 = [7] +1 weapon +1 STR 17",
  no spec line; **2, 1, 2, 1: 3/2**, SPEC_ATTACKS' half an attack less.
- **Ulf** (no spec: SPEC_NONE): no spec line, the game's **2 a round** kept (as SL's rule: a creature with no kinds
  chosen, a monster or the sequel's own pre-made characters, keeps the game's rate).
- DSCLOG2 at run 2's end: rules 0xFB45, spec_hits 32, spec_damages 32, spec_rates 24, two_count 0, off_count 0.
  STDOUT.TXT empty.

**So the specialization's attacks work for a new character**: the specialist keeps 2 a round, a fighter with a spec in
another kind drops to 3/2, no special handling needed for picks made at creation (the V3 bytes the pick writes are what
SPEC_OF_SHEET reads, as for a transferred party). What hides it in play is the starting gear: the sequel puts a new
fighter's sword in the left hand behind a shield, and the left hand swings once a round. Not fixed here (the gear
routine, 6F197h, is the game's; with the port plan's "the starting weapon of the first pick").

No new area: no water noted. ravSP3 thrown away after.
