# 2026-11-16: the Spellarcher's Fine Bow and starting arrows, Burning Arrows retired

Under test (commit ea6857d): a new Spellarcher (half-elf fighter/preserver) starts with a Fine Bow
(+1 to hit) and 24 Chill or Shocking Arrows for each touch spell picked at CHOOSE A SPELL (both:
24 of each), else 24 plain arrows; no Burning Arrows button; the Fine Bow's item box "Hit +1".

## Set-up
- start.sh: DOSBox restarted with the current build.
- Main menu, CREATE CHARACTERS, NEW: portrait stepped to race 4 (six clicks), PRESERVER added,
  KITS: NO KIT off, SPELLARCH on. buildcheck.py fine_hit ib_material arrow_knows: same as the EXE.

## A: Elstar, Shocking Grasp picked (not Chill Touch) — PASS
- CHOOSE A SPELL came first at DONE (four picks): Armor, Shield, Shocking Grasp, Burning Hands
  (the icons in spell-number order, closing up; Shocking Grasp the 10th). Then the weapon window
  (the bow alone), then the psionic powers.
- Dice log: "Elstar starts with a plain wooden bow for the weapon specialization chosen, in place of
  the bone long sword", the armour and shield left behind, then **"Elstar starts with a Fine Bow
  (+1 to hit): a Spellarcher's"**, **"Elstar starts with 24 shocking arrows in the quiver:
  Shocking Grasp picked"**, then the fuller gear's short sword.
- carried.py: Wooden Shocking Arrows (slot 1, 24, name 366), Bone Short Sword, Wooden Fine Bow
  (slot 2, name 371). No plain arrows; no Burning Arrows for Burning Hands.
- Inventory: the weapon lines "Fine Bow 3x1D8+2 T16" (THAC0 18, +1 DEX, +1 fine) and "Short Sword
  T18"; the bow's item box (right-click) "2 handed Wooden / Fine Bow / 2x1D8 / **Hit +1**".

## B: Rick th'Untamed, Chill Touch and Shocking Grasp picked — PASS
- Picks: Chill Touch, Shield, Shocking Grasp, Armor. Dice log: "starts with a Fine Bow",
  **"24 chill arrows in the quiver: Chill Touch picked"**, **"24 shocking arrows in the pack:
  Shocking Grasp picked"**. carried.py: Chill Arrows slot 1 (24), Fine Bow slot 2, Shocking
  Arrows slot 14 (24), Short Sword.

## C: Garn, no touch spell — PASS
- Picks: Armor, Burning Hands, Charm Person, Color Spray (Chill Touch skipped: (140,71) after the
  list closed up). Dice log: "starts with a Fine Bow", **"starts with 24 arrows: no touch spell
  picked"**. carried.py: Wooden Arrows (name 54, value 1) slot 1, **24**; Fine Bow; Short Sword.
- (A third, "Plainarch", INT 15, had only two picks and a mis-click took Shocking Grasp: it repeats
  A, 24 Shocking Arrows.)

## Noted: a gear pass before DONE
For Plainarch and Garn the dice log has an extra "starts with a Fine Bow / 24 arrows: no touch
spell picked / more gear: Short Sword" *before* the picks, while the creation screen was up (the
stand-in record is New, so a regular pass fits it out). The game replaces that gear at DONE (the
"plain wooden bow ... in place of the bone long sword" comes after), and the final items are right.
Not from this change (the fuller gear's Short Sword line shows it too); a cosmetic double in the log.

## USE screen: no Burning Arrows button — PASS
START GAME with the four: at the arena gate, U. **Elstar** (knows Armor, Burning Hands, Shield,
Shocking Grasp): one arrow button, the blue Shocking one; no red Burning one. **Rick**: Chill (light
blue) and Shocking. (Shots: use-elstar.png, use-rick.png.)

The arena's first wave then beat the party (2nd-level fresh characters, Tab + Return in melee:
no bow shot was made). "YOUR PARTY HAS BEEN DEFEATED".

## A Fine Bow shot — PASS
`tofight.sh 10` (fountain-user, every foe held, Ester's turn); Ester's bow (item 10, missile slot)
renamed Fine Bow in memory for the test (+12h 2 -> 173h; put back after, nothing saved).
`pointer.py attack`, the Templar at (240,134): "Ester attacks Templar with Wooden Fine Bow (1d8):
d20 = 2, needs 11+ (50%) ... target AC 4", **"THAC0 19, +4 DEX, -1 Battle Dancer, +1 fine = 15"**:
the game's own need (11 against AC 4) is THAC0 15, so FINE_HIT took the 1 off (16 without it), and
the breakdown has no "off-hand and other" left over. Both shots of the volley the same.
