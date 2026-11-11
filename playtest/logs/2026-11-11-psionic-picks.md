# Psionic powers picked at creation (2026-11-11)

The user: "The standard psionics on character creation that characters get - let the player pick
them, too. They always get one of the three, even if they aren't a full psionicist, and the powers
they get are always the same. Let the player pick which ones they want. For full psionicists and
for others."

## What the game does (read from DSUN.EXE and memory)

- DONE calls 66CF1h for the new member (from 6654Ch): the disciplines' words from DS:4980h
  (selector 2F0h, member x 7 + discipline x 2), all 34 powers cleared, then a row of the table at
  selector 338h given: a psionicist +1Ch + 11 x level, anyone else +6 + 11 x discipline. The rows,
  read live: psychokinesis Detonate, Ballistic Attack, Control Body, Inertial Barrier, Mind Blank;
  psychometabolism Life Draining, Biofeedback, Graft Weapon, Flesh Armor, Mind Blank; telepathy
  Superior Invisibility, Ego Whip, Psionic Blast, Intellect Fortress, Mind Blank; a psionicist 5 at
  1st, 6 at 2nd, 11 at 3rd.
- PICK A PSIONIC POWER (620:57h(member)) lists the powers of the discipline at DS:9CE2h + member
  (a power's record, selector 408h, +3 bits 0-5), known ones too (to raise their own number); its
  button (2C38h) turns the discipline; a click gives the power and counts DS:4AECh down, closing
  at 0; EXIT asks "YOU HAVE MORE" (EXIT / CANCEL).

## Checked in the game (the new DSCLOG, 70,128 bytes)

- A human fighter, TELEPATHY: after the weapon window, "PICK A PSIONIC POWER, HookBoldt", count 4,
  Telepath. The first build gave no Mind Blank (the branch left ZF set: fixed) and so listed 14.
  Two picked (Domination, Intellect Fortress): count 2, both out of the list. The discipline
  button: still Telepath. EXIT, then EXIT at YOU HAVE MORE (140,91): Superior Invisibility and Ego
  Whip added (the game's first two not known).
- A human psionicist, 3rd level (4,400 XP): Mind Blank known, count 10, Kinetics 6 powers; the
  button turned to Metabolic (14) and Telepath; ten picked across the three, the window closed
  itself: 11 powers.
- EDIT on it, DONE unchanged: no window, the 11 kept.
- START GAME (key S at the menu) with no party made: the game's own four with the game's powers
  (5, 7, 5, 5).
- A psionicist with ten picks, a second character made (EXIT: exactly the game's four and Mind
  Blank), the psionicist DROPped and ADDed back from the roster: its picks kept.
- Cosmetic: under a warrior's power window the weapon window's edges still show on the creation
  screen until VIEW CHARACTER draws its own.

Water: no play in a region.
