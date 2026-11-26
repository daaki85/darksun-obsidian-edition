# 2026-11-26: the kits' starting gear in Wake of the Ravager

**Under test:** branch `claude/ravager-kit-start-gear` (claude/ravager-first-pick-weapon with claude/ravager-kit-gear
merged): `dsloader/ravkitstart.py` (Shattered Lands' `weaponchoice.kit_gear` on the sequel's items) and
`weaponchoice.class_gear` in ravlog's `_gear_pass` (DSCLOG2's GEAR_DONE), after `ravfirstweapon.fill` and before
`startgear.fill`. No DSCLOG2 change.

**Set-up:** a throwaway copy `ravKSG` of `$WORK/rav` (FLIs, VOCs, PDFs, MUSIC, DOSBOX and __support hard-linked, the
rest copied, the roster and DARKSAVE from __support/save, no saves), `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1
RAV_CORE=normal sh ravstart.sh /tmp/playtest/ravKSG`, the dice log `RAV_NO_SAVES=1 ravdice.py --numbers` (restarted
by pid after each code change below; its rules the Loader's, the kits on), the DOSBox lock held throughout (after
another agent's session, about 20:05-20:35 UTC). Nothing saved; no memory edits.

**The clicks** (game pixels): CREATE CHARACTERS (160,92); a right click on a party slot (70,56 / 120,56 / 70,117 /
120,117), NEW on its menu 40 to the right and level (110,57 for slot 1; 160,57; 140,117; 160,117); a class off or on
in the class list at x 255 (FIGHTER y 29, GLADIATOR 37, THIEF 69); KITS (232,138), then NO KIT (250,106) clicked off
and the kit's row (250,114 / 122 / 130); `ravkits.py page` shows the kit byte. DONE (279,183), the powers' three picks
(121,62), the weapon window's picks (x 75, 109, 143, 177, 211, 245; y 32, 66, 100, 134). DROP on a member's right-click
menu (140,129), then YES (140,117). On View Character the bottom bar's (75,171) is the inventory; on the inventory
(170,187) is View Character.

## What was seen

| Character | Kit, picks | The dice log | `ravitems.py` |
|---|---|---|---|
| Balthbeorn, fighter | Ravager, long sword | (the first build, class_gear first) "Ring Armor is left behind: a Ravager can't wear it" x3, "Shield is left behind", "a second Longsword in the left hand", "more gear: Armor, Armor, Armor" | Longsword +1 in 3 and 10, leather (32, 3, 64) worn from the fuller gear |
| Cyrus the Great, fighter | Ravager, long sword | (kit_gear first, the armour looked for in its worn slot) "Ring Armor is left behind: a Ravager wears no armour" x3 | the same |
| Deestan, fighter | Ravager, axe | "starts with a axe +1 ... in place of the Longsword" (ravfirstweapon), the same armour lines, "a second Axe in the left hand" | Axe +1 (8) in 3 and 10 |
| Magramar, thief | Shinobi | "**starts with a short sword +1 in place of the Longsword: a Shinobi can't use it**", "more gear: Armor, Armor, Cloak" | the mod's Short Sword +1 (109) in 3, DAM 1x1D6+2 ([View Character](img/2026-11-26-ravager-kit-start-shinobi.png)); the dagger (72) in the pack, the sling in 2 |
| JohnBoy, fighter (the fixed build) | Ravager, long sword | "Shield is left behind", "**starts with leather armour in place of the Ring Armor: a Ravager wears light armour only**" x3, "a second Longsword in the left hand"; no "more gear" | leather 32/3/64 in 9/0/6, Longsword +1 in 3 and 10 |
| Aticus, gladiator | Arena Champion, long sword, club, dagger | "**starts with a shield +1 in place of the Longsword: an Arena Champion fights with one**", "more gear: Sling, Armor" | Longsword +1 in 3, Shield +1 (91) in 10; the inventory: the shield in the left hand, AC 1, "+1 Longsword 2x1D8+4" ([the inventory](img/2026-11-26-ravager-kit-start-champion.png)) |
| Lanthazar, fighter: **the control**, `RAV_NO_KIT_START=1` | Ravager, long sword | "more gear: Armor, Armor, Armor" only | the Shield +1 in 17 and the Ring Armor (33, 4, 65) in 16, 15, 14: **the game's give routine drops what the equip test refuses (DSCLOG2's KIT_FORBIDS) into the backpack**; no second sword |

## Found and fixed during the play

- **The game's give routine (6EF49h, its item put by c8:288Ch) puts what the kit refuses in the backpack**, as SL's
  does for the classes: a Ravager's ring armour and shield were in cells 14-17, not worn. The kit's step looked for the
  armour's leather by the item's slot and found none (Cyrus, Deestan: "wears no armour"); it now goes by the type's place
  on the body (the type's +9 as the dice log's view serves it, the sequel's +5: 1 the chest, 3 the arms, 0Ah the legs, 5
  a hand) and puts the leather in its slot.
- **Shattered Lands' order (class_gear, then kit_gear) left the armour behind** before the kit's step could make it
  leather (Balthbeorn: the leather came only from the fuller gear, so with that off a Ravager would wear none). The kit's
  step now runs first, then class_gear.

## Not played

A Brute, a Myrmidon, a Poisoner, a Ghetto Fighter, a Battle Mage, a Battle Dancer (tests/test_ravkitstart.py has the
Brute, Myrmidon and Battle Mage); no fight with the gear. A Spellarcher's Fine Bow is not ported (the sequel's DSCLOG2 has
no FINE_HIT).

## Tests

`tests/test_ravkitstart.py` (12, one with `DSUN_WOTR`); the full suite and the start-up tests on both games' files before
the push.

No new area: no water noted. ravKSG kept for now (no saves in it).
