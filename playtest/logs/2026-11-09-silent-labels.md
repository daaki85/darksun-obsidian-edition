# The Silent labels and the magic gear's glow (2026-11-09)

Under test: DSCLOG's L_MOVE ('SLNT', the inventory's thief row), IB_QUIET ('Silent +10') and
IB_ELF_QUIET ('Silent 95%'), and the Loader's `sprites._magic` taking the mod's magic types
(`MAGIC_TYPES`: the Boots of Speed, the Elvenkind cloak and boots, the girdles, the amulet) as magic.
Build: `buildcheck.py` OK (134 vectors at their handlers, the tail same as the EXE).

Steps, from `loadsave.sh pens-after-arena` (nobody wears boots there):

- Gerakis's Arm Armor (item 25, in his worn list) made the Boots of Speed in memory (a scratch
  setboots.py: worldgear.SPEED_BOOTS, slot 13). Inventory (I), right-click the feet place
  (**174,147**): "Leather / Boots of Speed / **Silent +10**".
- Its type made the Boots of Elvenkind (135) in memory, the portrait switched away and back: the box
  reads "**Silent 95%**".
- Cilla's portrait (member 3, 22,160): the thief rows read PICK 70, LOCK 55, TRAP 45, **SLNT 57**,
  HIDE 50, CLMB 87 (logs/img/2026-11-09-silent-slnt.png).
- **The glow**: `sprites.worn(gd, 0)` gave `'boots': (145, 5, 'magic', 0)` (before the fix it had no
  'magic'). **Gerakis's boots are drawn** (corrected the same day): the first shots misread him (a
  red patch at his feet taken for the pointer), and after a later memory change his picture hadn't
  been reloaded yet. Checked: his dressed pictures fit their room (12,303 of 22,826 bytes walking);
  the Loader's copy, the game's store (slot 61) and, after a walk, the game's memory all held the
  new outfit; with the pointer moved off, eight grabs show red boots and a glint changing at his
  feet (logs/img/2026-11-09-silent-gerakis.png). His back foot, raised above the lowest third of
  the legs that `draw_boots` colours, stays plain in some frames. Cilla's boots too
  (logs/img/2026-11-09-silent-glint.png): moved to her through the inventory (click the item, the
  other portrait, the feet place).
- Doc pictures retaken: plain Leather Boots (the game's first plain type-68 record) and the Boots
  of Elvenkind (worldgear.ELVEN_BOOTS) put on item 25 in memory, each box shot and cropped
  112x66 at +183,+95, scaled 200%, into docs/gear-boxes.png's middle panel and
  docs/elvenkind.png's right one.

Memory edits only; the game was not saved. The helper's sizes are unchanged (resident_end 61,392,
kept_end 62,800, UMB_KEPT 7,825).
