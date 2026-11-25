# 2026-11-25: preservers' first spells and psionic powers at creation in Wake of the Ravager (WIP, paused)

**Under test:** branch `claude/ravager-first-spells`: DSCLOG2's FIRST SPELLS AND POWERS (sites 87 CR_PICKS,
88 PSI_GRANT, 95 PSI_COUNT, 96 PSI_LIST, 97 PSI_CYCLE, 98 PSI_CLICK, 99 PICK_TOP; PICK_ANY and PICK_PAGE
heed CR_CAP; KP_OPEN snapshots an EDIT's powers). No header fields used.

**Set-up:** a copy `ravFS` of `$WORK/rav`, `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 sh ravstart.sh
/tmp/playtest/ravFS`, `ravdice.py 5000`; DSCLOG2's code in memory checked against DSCLOG2.EXE. Readings by
`ravfirst.py` (new).

## What was seen (paused part-way: usage limit)

- A new character on the sequel's creation screen is a 7th-level human (64,000 XP). Jaardoon made a
  preserver 7 (INT 17), P-Kinesis. DONE: CHOOSE A SPELL came up at LEVEL 1
  ([picture](/mnt/project-files/ravager/first-spells-choose.png)); the game's 10 grants had been taken back
  (cr_due: 4 L1, 3 L2, 2 L3, 1 L4) and the powers held only Detonate and Mind Blank (psi_due 3).
- Four 1st-level picks (Magic Missile, Armor, Burning Hands, Charm Person), the window opening each time and
  closing up; then LEVEL 2 with CR_CAP 2: the LEVEL button cycled 2, 1, 2 (PICK_TOP: the preserver casts 4th).
  Three 2nd-level picks (Blur, Detect Invisible, Flaming Sphere), one 3rd (Blink), then EXIT: "YOU HAVEN'T
  CHOSEN" ([picture](/mnt/project-files/ravager/first-spells-exit.png)), EXIT: the two left filled from the
  game's own grants - **but Chill Touch and Color Spray (1st level)**, not a 3rd and a 4th: CR_FILL takes the
  game's spells in spell order regardless of level. To fix: fill level by level from what is left due.
- Then PICK A PSIONIC POWER, "Kinetics", count 3, five power slots
  ([picture](/mnt/project-files/ravager/first-spells-psi.png)): a click on the first was sent when the play
  was stopped (DOSBox was gone by then; not read).

## Not done yet
- CR_FILL by level (above); the psionic picks read; a psionicist (16 picks, the discipline button); EXIT on
  the pop-up (PSI_FILL); EDIT keeping powers (PSI_KEEP); the control run (`RAV_SKIP=cr_picks,psi_grant,
  psi_grant_psionicist,psi_count,psi_list,psi_cycle,psi_click,pick_top`).
