# 2026-11-18: the spell arrows' INFO says SPELLARCHER ONLY

Under test: the user's request, a note in the Spellarcher's arrows' item box that only a
Spellarcher can use them. DSCLOG's `INFO_ONLY` (site `NS_IMAGE+121` over "mov ax,[bp-2]" at
DSUN.EXE 8C282h, the end of the routine drawing the item box's INFO list) adds SPELLARCHER ONLY
under the game's USEABLE BY list for the four spell arrows' names. Build: `dos/DSCLOG.EXE` 70,512
bytes, assembled byte-for-byte from `dos/dsclog.asm` (NASM 2.16.01). Save `pens-after-arena`; the
window 320x240; `buildcheck.py info_only`: same as the EXE, every vector at its handler.

## What the box's INFO is

The item box (right-click an item on the inventory screen) has one button, INFO. It toggles the
box (DS:0846h) to the game's list (8C1B8h): "USEABLE BY:" and the name of each party member the
game's can-use routine (the one equipping asks, its mask test at DSUN.EXE 6EF34h; here with no message) allows, else
"NO ONE". That routine runs through DSCLOG's `PROBE_CAN_USE`, so the mod's kits, its class
restrictions and `ARROWS_FORBID` already shape the list: before this change a stack of spell
arrows already listed no one but a Spellarcher. A second click on INFO shuts the box.

## Before (the committed build) — seen
- Cilla's sling (item 16) made 24 Chill Arrows in her pack (slot 14) in memory
  (`spellarrows.arrows_item`, its link and flags kept: a scratch script like `setitem.py rec=`).
  The Loader: "Cilla's Chill Arrows is put away in the backpack (it had been counted as held)".
- Its box: the picture, "24 Wooden / Chill Arrows", INFO; no damage line, no price (worth 0).
- INFO: **"USEABLE BY: / NO ONE"** (no Spellarcher in the party):
  [img](img/2026-11-18-chill-arrows-info-before.png).
- Cilla's Bone Long Sword's INFO: "USEABLE BY: / Gerakis / Cilla" (names in mixed case):
  [img](img/2026-11-18-long-sword-info.png).

## After (INFO_ONLY) — PASS
- The same Chill Arrows in Cilla's pack: the box itself as before
  ([img](img/2026-11-18-chill-arrows-box.png)); INFO: **"USEABLE BY: / NO ONE / SPELLARCHER
  ONLY"** ([img](img/2026-11-18-chill-arrows-info-no-one.png)). A first try with the 17 letters of
  "SPELLARCHERS ONLY" ran to the box's right edge (the box at the screen's right, beside the pack's
  first column): cut to "SPELLARCHER ONLY", which fits with a few pixels to spare.
- Cermak made a Spellarcher in memory (race half-elf, classes fighter 9 and preserver 11, kit byte
  1: `kitpages.kit_ids` [57]; and his class mask, sheet +12h, 0080h to 00A0h, the fighter's bit
  added: with the preserver's alone the game's own test barred him from arrows). With the inventory
  shut the Loader moved the arrows to him: "The chill arrows go back to Cermak from Cilla: only a
  Spellarcher carries them (24)". His pack's arrows, INFO: **"USEABLE BY: / Cermak / SPELLARCHER
  ONLY"** ([img](img/2026-11-18-chill-arrows-info-spellarcher.png),
  [zoomed](img/2026-11-18-chill-arrows-info-spellarcher-zoom.png)): Gerakis, K'ratchek and Cilla,
  who may use plain arrows, are left out (`ARROWS_FORBID`).
- Plain Arrows (Gerakis's gythka, item 21, made 24 Wooden Arrows in his pack): INFO "USEABLE BY: /
  Gerakis / K'ratchek / Cilla", no added line ([img](img/2026-11-18-plain-arrows-info.png)).

## Notes for the guide
- The box's INFO button is at the box's bottom right: for an item in the pack's first cell (195,26)
  the box is at the screen's top right and INFO at about (291,57) (a plain stack of arrows, its box
  a row taller with the price: (289,54)); for the right hand (66,92) at (160,115). The tall label
  is easy to misread from a full shot: zoom the box (`convert -crop 120x70+200+0 -scale 400%`).
  A click just after the box opens was lost twice: point first (`click.py X Y none`), wait a
  second, then click. A click outside the button, or on INFO again, shuts the box.
- Nothing saved; the memory edits went with DOSBox, stopped by pid.

## Water
No new area.
