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
  'magic'). Gerakis's figure showed no boots at all, in any colour, so no glint either: his figure's
  feet aren't where `draw_boots` looks (not looked into further; his plain gear isn't drawn on the
  feet either). Moved through the inventory (click the item, the other portrait, the feet place),
  the boots went to Cilla: her feet are drawn red and a few pixels at them change from frame to
  frame, the glint (logs/img/2026-11-09-silent-glint.png, eight grabs 0.2 s apart).
- Doc pictures retaken: plain Leather Boots (the game's first plain type-68 record) and the Boots
  of Elvenkind (worldgear.ELVEN_BOOTS) put on item 25 in memory, each box shot and cropped
  112x66 at +183,+95, scaled 200%, into docs/gear-boxes.png's middle panel and
  docs/elvenkind.png's right one.

Memory edits only; the game was not saved. The helper's sizes are unchanged (resident_end 61,392,
kept_end 62,800, UMB_KEPT 7,825).
