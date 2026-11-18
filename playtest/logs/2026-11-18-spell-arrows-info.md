# 2026-11-18: the spell arrows' INFO headed SPELLARCHERS:, and no one else readies them

Under test: the user's request, a note in the Spellarcher's arrows' item box that only a
Spellarcher can use them, and (their second request) that no one else can ever have them readied.
Final build: DSCLOG's `INFO_HEAD` (site `NS_IMAGE+121` over "push ds / push 3493h" at DSUN.EXE
8C1E0h, where the item box's INFO routine pushes its heading USEABLE BY:) pushes SPELLARCHERS:
instead for the four spell arrows' names; `spellarrows.return_strays` puts spell arrows a
non-Spellarcher has readied back in its pack when no Spellarcher is in the party. `dos/DSCLOG.EXE`
70,512 bytes, byte-for-byte from `dos/dsclog.asm` (NASM 2.16.01). Save `pens-after-arena`; window
320x240; `buildcheck.py info_head`: same as the EXE, every vector at its handler.

## What the box's INFO is

The item box (right-click an item on the inventory screen) has one button, INFO. It toggles the
box (DS:0846h) to the game's list (8C1B8h): "USEABLE BY:" and the name of each party member the
game's can-use routine (the one equipping asks, its mask test at DSUN.EXE 6EF34h; here with no
message) allows, else "NO ONE". That routine runs through DSCLOG's `PROBE_CAN_USE`, so the mod's
kits, its class restrictions and `ARROWS_FORBID` already shape the list: before this change a stack
of spell arrows already listed no one but a Spellarcher. A second click on INFO shuts the box.

## Before (the committed build)
- Cilla's sling (item 16) made 24 Chill Arrows in her pack (slot 14) in memory
  (`spellarrows.arrows_item`, its link and flags kept). The Loader: "Cilla's Chill Arrows is put
  away in the backpack (it had been counted as held)". Its box: the picture, "24 Wooden / Chill
  Arrows", INFO; no damage line, no price ([img](img/2026-11-18-chill-arrows-box.png)).
- INFO: "USEABLE BY: / NO ONE" ([img](img/2026-11-18-chill-arrows-info-before.png)). Cilla's Bone
  Long Sword's: "USEABLE BY: / Gerakis / Cilla" ([img](img/2026-11-18-long-sword-info.png)).

## First tries (given up)
An extra row under the list (`INFO_ONLY`, over "mov ax,[bp-2]" at 8C282h): "SPELLARCHERS ONLY"
ran into the box's right edge, and "SPELLARCHER ONLY" still touched the frame (about 15 letters fit
a row; the user saw it). The user chose the heading instead: one row, whatever the names below.

## The heading — PASS
- No Spellarcher in the party, the Chill Arrows in Cilla's pack: **"SPELLARCHERS: / NO ONE"**
  ([img](img/2026-11-18-spellarchers-heading-no-one.png),
  [zoomed](img/2026-11-18-spellarchers-heading-no-one-zoom.png)): clear of the frame.
- Cermak made a Spellarcher in memory (race half-elf, classes fighter 9 and preserver 11, kit byte
  1; his class mask, sheet +12h, 0080h to 00A0h: with the preserver's bit alone the game's own test
  bars arrows before DSCLOG's). With the inventory shut the Loader moved the arrows to him ("The
  chill arrows go back to Cermak from Gerakis: only a Spellarcher carries them (24)"). His INFO:
  **"SPELLARCHERS: / Cermak"** ([img](img/2026-11-18-spellarchers-heading-cermak.png),
  [zoomed](img/2026-11-18-spellarchers-heading-cermak-zoom.png)).
- Plain Arrows (Gerakis's gythka, item 21, made 24 Wooden Arrows in his pack): **"USEABLE BY: /
  Gerakis / K'ratchek / Cermak / Cilla"**, the game's heading ([img](img/2026-11-18-plain-arrows-heading.png),
  [zoomed](img/2026-11-18-plain-arrows-heading-zoom.png)).

## Readying them: every way (no Spellarcher in the party first)
- **Into the holder's own quiver**: Cilla's stack picked up from her pack and clicked on her ammo
  slot (66,26): **CANNOT USE THIS ITEM** on the line under the paper doll, the stack stays on the
  pointer ([img](img/2026-11-18-spell-arrows-refused-cilla.png)). (Cilla uses plain arrows.)
- **Through another member's portrait**: the stack on the pointer, Gerakis's portrait (22,20),
  then his ammo slot: **CANNOT USE THIS ITEM** ([img](img/2026-11-18-spell-arrows-refused-gerakis.png)).
- **Into another member's pack**: accepted (195,26 of Gerakis's pack): the game asks nothing of a
  backpack, and with no Spellarcher the Loader leaves them there.
- **SPLIT**: SPLIT (205,147) with nothing on the pointer, then the stack: a stack on the pointer;
  on Gerakis's ammo slot, **CANNOT USE THIS ITEM** ([img](img/2026-11-18-spell-arrows-refused-split.png)).
  (Put back, the stack was one 24 again.)
- **Already readied** (as an old save could have them): Gerakis's stack put in his ammo slot in
  memory (`pickpocket.place`, the inventory shut): within the dice log's next pass, **"Gerakis's
  chill arrows are put away in the backpack: only a Spellarcher readies them (24)"** (`carried.py`:
  slot 14). The new `return_strays` step; before it they would have stayed readied.
- **With a Spellarcher**: the next pass moved them from Gerakis to Cermak (the line above), and
  Cermak readied them in his quiver with no message ([img](img/2026-11-18-spell-arrows-cermak-quiver.png)).
- **Loot**: not played (no body at hand). The T loot (`loot.py`) puts what it takes in backpack
  cells only (its code); whatever puts them anywhere, `return_strays` takes them out of a
  non-Spellarcher's quiver, or to the Spellarcher, out of fights with the inventory shut.

## Notes for the guide
- The box's INFO button is at the box's bottom right: for an item in the pack's first cell (195,26)
  about (291,57) (a box with a price line: (289,54)); for the right hand (66,92) about (160,115).
  Zoom the box to find it (`convert -crop 120x70+200+0 -scale 400%`). A click just after the box
  opens can be lost: point first (`click.py X Y none`), wait a second, then click.
- Nothing saved; the memory edits went with DOSBox, stopped by pid.

## Water
No new area.
