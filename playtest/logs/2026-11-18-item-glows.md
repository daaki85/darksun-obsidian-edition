# 2026-11-18: item glows, the Searing Blade, Tanelyv's chest piece

Under test (branch `claude/item-glows-searing-blade`, the worktree's Loader and its rebuilt
DSCLOG.EXE, the "Searing Blade" name entry):

1. Greenbright's icon in the cycled green (palette 1-5): does it shimmer in the inventory?
2. The Searing Blade (an obsidian short sword +2, name 0x156): its whole name in the item box, the
   inventory's label and the dice log's attack line; its icon.
3. An old save's Flame Blade (an obsidian long sword +1 of the same name entry) made the Searing
   Blade by the dice log (`worldgear.mend_searing_blade`).
4. Tanelyv's chest piece (object 2004, icon 2248) shining with the water's colours as the arm and
   leg pieces do.

Items are put in hands with `setitem.py` (memory only: never saved).

## Steps
- loadsave fountain-user; buildcheck OK (extra_names same as the EXE); window 320x240. setitem 115 (member 1's right hand) the old Flame Blade record (type 45, +1, 22,000): 8 s later the dice log had made it type 0x78 +2 42,800 (mend works). setitem 28 obj=2004 (member 1's chest: Tanelyv's chest piece), setitem 204 Greenbright (member 3's pack).
- Jenna's turn (member 1): I. Label OBSIDIAN SEARING BLADE whole; item box '+2 Searing Blade' whole, 42800, 1D6+2/1D8+2; weapon line '+2 Searing Blade' whole. Chest: METAL TANELYV'S ARMOR, AC BONUS:4, 15000, the chain picture with the water shine (blues change between shots). Seneca (member 3): Greenbright in the pack green, 13 of its 16 green pixels change over four shots 0.4 s apart: it shimmers. Hayneedle in her hand lavender (water).
- Escape, Tab, Return on Jenna's turn: the dice log "Jenna attacks Templar from behind with Obsidian
  Searing Blade +2 (1d6+2)": the whole name; then "Focus Heat damage: 2d6 = [5 + 1] = 6 ... Templar
  takes 12 from Focus Heat" (the weapon's spell as before).
- `sprites.worn`: Jenna's left hand `(120, 3, 'magic', 0)` (the Searing Blade glints in the fire's,
  FIRE_GLOW), Seneca's Hayneedle `(139, 1, 'magic', 3)` (BLUE_GLOW, the water's). Tanelyv's chest
  piece (type 88, no plus) isn't magic to `sprites._magic`, so no sparks on the figure, as before.
- Not saved (memory edits). DOSBox, the dice log, Xvfb and the watchdog stopped by pid.

## Results

- Greenbright shimmers green in the inventory (the cycler's 1-5 turn there, as fire and water do).
- "Searing Blade +2" whole everywhere it shows: the label (OBSIDIAN SEARING BLADE, no plus), the item
  box ("+2 Searing Blade"), the inventory's weapon line ("+2 Searing Blade", to the panel's edge) and
  the dice log ("Obsidian Searing Blade +2 (1d6+2)").
- A saved game's Flame Blade becomes the Searing Blade (type 0x78, +2, 42,800) within a pass.
- Tanelyv's chest piece shows the chain picture with the water's shine, as its arm and leg pieces.

## Pictures

- [The Searing Blade's box and the weapon line](img/2026-11-18-searing-blade-box.png), [its
  label](img/2026-11-18-searing-blade-label.png)
- [Tanelyv's chest piece's box](img/2026-11-18-tanelyv-chest-box.png)
- [Greenbright in four shots 0.4 s apart](img/2026-11-18-greenbright-cycle.png), [the chest piece
  and the Searing Blade in three](img/2026-11-18-chest-blade-cycle.png)

## Learned

- The game's colour cycler turns four runs everywhere the fire's do, the inventory included: 1-5
  green, 6-10 violet, 11-15 the water's, 240-248 fire (icons.py said only water and fire).
- In `fountain-user`, Jenna is member 1 (her slot-10 weapon shows at the inventory's (173,92)) and
  Seneca member 3; on loading, the ambush's speech is up, and items written then are in hand for the
  fight (`setitem.py` before `boxclick.sh`).
- A shimmer is checked by four `shot.sh` captures 0.4 s apart, cropped round the cell: count the
  pixels of the glow's hue that change.
- Tanelyv's chest piece is object 2004 (not 1361, which has a BMP but no OJFF): script 161 creates
  -1362, -1363 and -2004.
