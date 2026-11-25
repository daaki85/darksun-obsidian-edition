# 2026-11-25: preservers' first spells and psionic powers at creation in Wake of the Ravager

**Under test:** branch `claude/ravager-first-spells` (from `claude/ravager-join-loot-tabs`): DSCLOG2's FIRST
SPELLS AND POWERS, SL's PROBE_CR_SPELLS and PSI_GRANT/PSI_ASK/PSI_LIST/PSI_CYCLE on the sequel's own
grants: sites 87 CR_PICKS (6ED55h), 88 PSI_GRANT (6E9C9h, 6E9F7h), 95 PSI_COUNT (93B95h), 96 PSI_LIST
(93E1Bh), 97 PSI_CYCLE (93FF1h), 98 PSI_CLICK (94245h), 99 PICK_TOP (93831h); PICK_ANY and PICK_PAGE heed
CR_CAP; KP_OPEN snapshots an EDIT's powers (PSI_SNAP). No header fields. DSCLOG2's code in memory checked
against `obsidian-edition/dos/DSCLOG2.EXE` (40 bytes of five routines, by the symbols from `nasm`).

**Set-up:** a throwaway copy `ravFS` of `$WORK/rav` (game.gog hard-linked, the rest copied), `RAV_LOADER=1
RAV_MENU=1 RAV_STDOUT=1 sh ravstart.sh /tmp/playtest/ravFS`, the dice log `ravdice.py 6000` (the kits' rules:
the KITS button on the panel), the DOSBox lock held throughout. Readings by `ravfirst.py` (new: a member's
spells, powers, disciplines and DSCLOG2's counts and the game's grants it took back).

## The sequel's own grants (read in its code, then seen)

A new character on the sequel's creation screen is a 7th-level human (64,000 XP; 60,000 as a preserver,
55,000 as a psionicist). DONE (6E0B9h) calls the powers' routine (6E906h) and then the preserver's spells'
(6EA10h). Not SL's Grease and Magic Missile: a preserver of 2nd level on gets Fireball, Haste, Detect
Invisible, Magic Missile, Wall of Fog and four drawn by rand() (one each of {Armor, Shield, Grease, Color
Spray}, {Burning Hands, Charm Person, Chill Touch, Shocking Grasp}, {Blur, Glitter Dust, Invisibility, Mirror
Image}, {Flaming Sphere, Acid Arrow, Stinking Cloud, Web}), Ice Storm too at 7th: 4 of 1st level, 3 of 2nd, 2
of 3rd, 1 of 4th; a 1st-level one Wall of Fog alone. The powers from a fixed table (selector 360h): a
psionicist 16 and Detonate and Mind Blank; anyone else its discipline's row (P-Kinesis: Disintegrate,
Ballistic Attack, Inertial Barrier + Detonate, Mind Blank; P-Metab: Life Drain, Adrenalin Control,
Biofeedback, Lend Health + Detonate; Telepathy: Superior Invisibility, Psychic Crush, Ego Whip, Psionic Blast
+ Mind Blank). Detonate (power 0) is never listed by the pop-up (its discipline routine 93DA6h gives -1 for 0).

## What was seen

**1. A preserver (Jaardoon, then again in a second start; human, INT 17, P-Kinesis).** DONE: CHOOSE A SPELL
at LEVEL 1, 12 spells ([picture](img/2026-11-25-ravager-first-spells-choose.png)); the game's 10 taken back
(`cr_defs`: Armor, Burning Hands, Magic Missile, Wall of Fog, Detect Invisible, Glitter Dust, Stinking
Cloud, Fireball, Haste, Ice Storm; `cr_due` [4, 3, 2, 1]), the powers then only Detonate and Mind Blank.

| Step | Window | Known after |
|---|---|---|
| Shield, Grease, Color Spray, Chill Touch | LEVEL 1, a window each, closing up | 4 of 1st |
| LEVEL 2 (cr_cap 2): the LEVEL button | 2, 1, 2 (the preserver casts 4th: PICK_TOP keeps it at 2) | |
| Blur, Fog Cloud | LEVEL 2 | + 2 of 2nd |
| EXIT, "YOU HAVEN'T CHOSEN", EXIT | | + Detect Invisible, Fireball, Haste, Ice Storm (CR_FILL by level: 1 of 2nd, 2 of 3rd, 1 of 4th) |

`cr_windows` 7, `cr_picked` 6, `cr_filled` 4: 10 spells, as the game gives. (In the first start the fill took
the game's spells in spell order and gave two of 1st level for a 3rd and a 4th: fixed to fill each level's
picks still due first.)

**2. Its powers (P-Kinesis): the first start died here.** The pop-up came up "Kinetics", count 3, with five
empty frames; a click on the first quit the game with **Illegal Op (gpl=49)** (STDOUT.TXT). The list
(DS:9C20h) was empty and the hover named Detonate: SITE's way back is the byte after the site's number, so
for a 4-byte site the NOP, and PSI_LIST's, PSI_COUNT's and PSI_CLICK's jumps were counted one byte late
(PSI_LIST's into the middle of an instruction). Counted from the NOP: fixed.

**3. A psionicist (T'Sharr, slot 1, after the fix).** DONE: PICK A PSIONIC POWER, Kinetics, **16**, the
powers' icons ([picture](/mnt/project-files/ravager/first-spells-psi16.png)); Disintegrate and Project Force
clicked (15, 14: the list closing up, the known left out); the discipline button: Metabolism, Animal
Affinity clicked; again: Telepath, 13 icons (Mind Blank, known, left out;
[picture](img/2026-11-25-ravager-first-spells-powers.png)), Domination clicked; EXIT, "YOU HAVE MORE", EXIT:
12 filled from the game's own in its order less any known (Control Body ... Intellect Fortress). 18 powers,
as the game gives: Detonate, Disintegrate, Project Force, Control Body, Inertial Barrier, Animal Affinity,
Energy Control, Life Drain, Biofeedback, Cellular Adjustment, Displacement, Flesh Armor, Domination, Superior
Invisibility, Tower of Iron Will, Ego Whip, Intellect Fortress, Mind Blank (`psi_filled` 12).

**4. A fighter, Telepathy (Morbad, slot 2).** The pop-up: Telepath, 4; the discipline button did nothing
(PSI_CYCLE: its own only); four clicks: Domination, Mass Domination, Psychic Crush, Superior Invisibility,
the window closing at none. Powers: those and Mind Blank.

**5. EDIT of T'Sharr, nothing changed, DONE:** no window, the 18 powers kept, the picks among them
(`psi_kept` 1). Without PSI_KEEP the game's DONE would have given the table's again.

**6. The control** (`RAV_SKIP=cr_picks,psi_grant,psi_grant_psionicist,psi_count,psi_list,psi_cycle,
psi_click,pick_top`, the same copy): a preserver (Garn, slot 3) DONE gave no window and the game's 10 at once
(Armor, Chill Touch, Magic Missile, Wall of Fog; Detect Invisible, Glitter Dust, Acid Arrow; Fireball, Haste;
Ice Storm: the draws differ from run to run) and Detonate, Disintegrate, Ballistic Attack, Inertial Barrier,
Mind Blank ([picture](/mnt/project-files/ravager/first-spells-control.png)); a psionicist (slot 4) the table's
18 (Psionic Blast, Synaptic Static, Thought Shield among them), DSCLOG2's counts all 0.

STDOUT.TXT empty after the fix. Each DOSBox and dice log was killed by pid, the lock let go.

## Not done
- A Scholar's one more spell each level (SL's KIT_MADE): not ported.
- EDIT of a preserver: the game's own (its spells given again, at random, when its preserver level changed
  from the screen's opening; then picked again, as a new one's are not: only a new member picks).
- A multiclass preserver, and a 1st-level one (the sequel's new characters are 7th level), not played.

**Water:** none (the creation screen only).
