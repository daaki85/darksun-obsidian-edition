# 2026-11-25: three small ports to Wake of the Ravager (music device, charges' labels, a ranger's two weapons)

**Under test:** branch `claude/ravager-small-ports` (on `claude/ravager-shops-tab`): DSCLOG2's RG_TWO (site 78, at
the sequel's two-weapon routine's test for a ranger, 5DE67h: "test word es:[bx+10h],200h", SL's RG_TWO at
5961Fh) and the patch `ranger_two`; RavDiceLog's charges pass (DiceLog.count_charges, until now a stub) with the
sequel's event queues (DS:2A63h far pointers, DS:2A6Bh counts; SL's 2FBEh, 2FC6h; `ravds.py --fuzzy`), so the
labels "Armor: 7 left" name the spell and count right; the Options tab's music device hint. DSCLOG2.EXE **41600
bytes** (the joined build's 41536 + RG_TWO).

## The music device (row 4): nothing to port

`launch.write_conf_wotr` leaves the `[midi]` lines out on purpose (its docstring, `test_launch`'s
`write_conf_wotr` test): the sequel has no MIDI music. Checked again in the user's copy: its README.TXT ("Since
there is no MIDI music (just off the CD)"), SOUND.INI's header `[MidiNotEnabled]`, GOG's SOUND.CFG naming only
the Sound Blaster Pro II's FM and digital drivers (`sbp2fm.adv`, `sbpdig.adv`), and `MUSIC/Track02.ogg`... 40 CD
tracks. The music device can't apply to it. Changed: the Options tab's hint under the Music device box now says
"Shattered Lands only: Wake of the Ravager's music is its CD's audio, not MIDI" (FEATURES.md said so already).
No play (nothing to see).

## The runs

[files/2026-11-25-ravager-small-ports-run.sh](files/2026-11-25-ravager-small-ports-run.sh): `ravSM`, a fresh copy
of `ravK` (the `fountain-user` party transferred), the Loader's start (`RAV_SKIP=ranger_two` for the control),
the four ADDed, a new game, the opening talk into the Draxans' ambush, HP 250 for the four (a test edit, never
saved; the copy thrown away), `ravdice.py --numbers` (`RAV_CHARGES_OFF=1` for the control). By hand: Lex
(member 0, fighter/preserver) taught Armor (`ravknow.py 0`), cast it from USE (C, the first icon at game
175,58, then Jenna's portrait 120,117) on **Jenna** (member 3, human ranger 3, Stalker kit, sheet flags 0200h,
an Obsidian Longsword in each hand, leather on chest, arms and legs); her turns Tab and Enter, every other
turn ended (`ravfight.py end`). Test edits for the armour: her leather chest piece (item 44) and a type-1 armour
of material 1 in her pack (item 53) traded slots (+13h) to put her in armour that isn't light, and back; her
DEX (creature +1Ah) 20 or 14. A grab every 0.3 s and DSCLOG2's label slots watched (time, number, width,
thing) to see the labels.

A first try from `ravager-after-ambush` (the opening party, Gerakis given the ranger flag) didn't reach Tyr's
thieves: the arrow keys left the leader at world (2112, 1632), not the alley (1839, 1224). Given up for the
ambush.

## What was seen

**A ranger's two weapons (row 25).** DSCLOG2's counters by `ravkits.py count` (two_count, off_count, rg_heavy now
among them); every attack the game's own ("THAC0 18 base, +N in bonuses", the dice log's reading of the attack):

| Run | Armour | DEX | Jenna's attacks | Tab line (the Loader's prediction) | rg_heavy, two_count |
|---|---|---|---|---|---|
| B (rule on) | leather (light) | 20 | +1, +1, +1: needs 16+ | 16+ | 0, 0 |
| B | type 1, material 1 (not light) | 20 | +0 (17+) and +1 (16+) | 17+ and 16+ | 2, 2 |
| B | not light | 14 | -3 (20+) and -1 (18+), -1 | 20+ and 18+ | 4, 4 |
| B | leather again | 14 | +1, +1, +1: 16+ | 16+ | 4, 4 (none added) |
| C (control: ranger_two left out) | not light | 20 | +1 (all five): 16+ | 17+ and 16+ (the rule's) | 0, 0 |
| C | not light | 14 | +1, +1: 16+ | 20+ and 18+ (the rule's) | 0, 0 |

So in armour that isn't light the ranger takes AD&D's -2 in the main hand and -4 in the off hand, plus DEX's
reaction adjustment (+3 at 20: 0 and -1; 0 at 14: -2 and -4), no more than 0, as SL's RG_TWO; in leather none;
without the site the game's ranger keeps no penalty in any armour (the Loader's line, which models the rule,
then disagrees with the game: the control's point). The DEX edit didn't hold in C: Armor cast on Jenna made the
game read her DEX 20 again; edited once more after the cast.

**The charges' labels (row 5, charges half).** Run B: Armor on Jenna, 10 charges (`Armor has 10 charges (caster
level 2 ... 8d1)`); each damaging Draxan hit used one: `Armor on Jenna#3: one charge used, 9 left` ... `3 left`
(7 hits, 7 lines). The slot over thing 3 written each time (width 66, held 3 s), and **"Armor: 9 left" and
"Armor: 5 left"** in blue over her ([picture](img/2026-11-25-ravager-charge-label.png),
[first](img/2026-11-25-ravager-charge-label-first.png)). A label is put on screen only as the game draws the
map: a charge used during a Draxan's blow shows once the blow's picture is done, and two in one turn (8, 7 left;
4, 3 left) were over before the map was drawn again, so not seen though written. **Control** (run C, the
charges pass off): the same lines and the same label ("Armor: 9 left",
[picture](img/2026-11-25-ravager-charge-label-control.png)): the sequel's charge routine came back to its
caller each time (CHARGE_USED_RETURN matched), which the dice log reads without the pass. What the pass adds
(the unit tests: `test_ravlog.ChargeLabelTests`): the spell's name where its effect's differs, a charge whose
return the overlay manager turned into its INT 3Fh stub, and the count right with several charges in one poll.
None of the three came up in these two fights.

No Illegal Op (`STDOUT.TXT` empty), DOSBox up to the end of both runs. Not run: the watchdog (the fights
watched turn by turn instead); the window is the sequel's 640x480.

No new area (Tyr's ambush street): no water.

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-charge-label.png`, `-charge-label-first.png`,
`-charge-label-control.png`.
