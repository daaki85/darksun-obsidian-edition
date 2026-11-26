# 2026-11-26: a new warrior's starting weapon a +1 of its first pick, and an air cleric's dagger, in Wake of the Ravager

**Under test:** branch `claude/ravager-first-pick-weapon` (3a2cc69, then with `weapon_first` and the missile picks' change below, on obsidian-edition 13592be + claude/start-tests-both-games):
`dsloader/ravfirstweapon.py` in ravlog's `_gear_pass` (DSCLOG2's GEAR_DONE) before startgear.fill; the sequel's daggers
37 and 72 given the air cleric's class bit (ravager.mod_types_table); ravgear's obsidian mace a fire cleric's
(ravlog.RAV_PLAIN_NEW). No DSCLOG2 change.

**Set-up:** a throwaway copy `ravFW` of `$WORK/rav` (FLIs, VOCs, PDFs and game.gog hard-linked, the rest copied, the
roster reset from __support/save, no saves), `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh
/tmp/playtest/ravFW`, the dice log `RAV_NO_SAVES=1 RAV=/tmp/playtest/ravFW ravdice.py --numbers` attached at the title
menu, the DOSBox lock held throughout.

## Steps

**Run 1 (3a2cc69).** A fighter (Ulf) picking the **lotulis**: dice log "Ulf starts with a lotulis +1 ... in place of the
Longsword", "Ulf's Shield goes into the backpack: the weapon takes both hands"; `ravitems.py 0`: type 61 plus 1 in slot 3,
the shield (91) in slot 14; View Character DAM 2x2D4+5; the inventory "+1 Lotulis 2x2D4+5", the box "2 handed Stone +1
Lotulis 2D4+1", 15000. A gladiator (Dag) picking the **double spear, long sword, club**: the double spear +1 (39) in slot 3,
the second Longsword +1 to slot 14; **but View Character's DAM 2x1D1+1 and the inventory listed no double spear** (its line
"(2x1D1+1)", the bare hand). Picked up and put back in the inventory: "+1 Double Spear 1D6+3". A second gladiator (Shaggy)
the same; its held list (creature +0Ah) the Loader's Sling first, the spear second; a test edit putting the spear first
(the records' contents swapped, never saved) made the line "+1 Double Spear 1D6+3" with nothing moved by hand. So the
sequel's weapon lines take a double spear that isn't first in its list for no weapon (a lotulis behind the sling was
taken). Fixed: `ravfirstweapon.weapon_first`, after startgear's items, puts the weapon in hand first in its list. A ranger
(Magramar) can't pick the bow (greyed: his already); his long sword pick made his plain 603 the Longsword +1 (97, plus 1):
"Metal +1 Longsword 1D8+1", 30000, DAM line "+1 Longsword 2x1D8+2". Missile picks changed after: the slot's old missile
weapon (a ranger's bow, a thri-kreen's chatkcha) goes to the backpack, not made over. DOSBox and the dice log stopped, the
roster reset.

**Run 2 (the fixed code; DOSBox and the dice log started again, the roster reset).** CREATE CHARACTERS (160,92 twice:
the first click only captures the mouse), each made with NEW, its class, DONE (279,183), the powers' three picks
(121,62) and the weapon window's picks (columns x 75, 109, 143, 177, 211, 245; rows y 32, 66, 100, 134, in
specialize.KINDS' order: the bow 109,100, the two-handed sword 211,100, the lotulis 245,100, the double spear 75,134):

| Character | Picks | The dice log | `ravitems.py` (hands) | The inventory / the box |
|---|---|---|---|---|
| Lanthazar, fighter | lotulis | "starts with a lotulis +1 ... in place of the Longsword", "Shield goes into the backpack: the weapon takes both hands" | 61 +1 in 3, the shield (91) in 14 | "+1 Lotulis 2x2D4+5"; box "2 handed Stone +1 Lotulis 2D4+1", 15000 ([the picture](img/2026-11-26-first-pick-lotulis.png)) |
| Aticus, gladiator | double spear, long sword, club | "double spear +1 ... in place of the Longsword", the left hand's "Longsword goes into the backpack" | 39 +1 in 3 (first in its list), the Longsword +1 (97) in 14 | "+1 Double Spear 1D6+3" over "(2x1D1+1)", as after a hand equip; box "2 handed Wooden +1 Double Spear 1D6+1", 15000; View Character's DAM 2x1D1+1 (below) |
| Aticus (the game's name again), fighter | bow | "starts with a bow ...", "has +1 arrows with it" | the Longsword +1 in 3, the shield in 10, the bow (18) in 2, the +1 arrows (6) in 1 | "Bow 4x1D6+1", "+1 Longsword 1.5x1D8+2" |
| HookBoldt, fighter | two-handed sword | "two-handed sword +1 ... (a plain one made +1: the game has no two-handed sword +1)", the shield to the backpack | 101 +1 in 3, the shield in 14 | "+1 Twohand Swor(d) 2x1D10+5"; box "2 handed Obsidian +1 Twohand Sword 1D10+1", 20800 |
| Balthbeorn, air cleric | none (no window) | "starts with more gear: Dagger (in hand), Sling" | the obsidian dagger (72) in 3, the shield +1 in 10, the club (29) in 14, a sling in 2 | box "Obsidian Dagger 1D4-1 Hit -2", 10 ([the picture](img/2026-11-26-air-cleric-dagger.png)); DAM 1x1D4+1 |

The other clerics (slot 4 dropped and made again; the sphere: AIR clicked off at 240,106, then EARTH 114, FIRE 122,
WATER 130): **fire** (MadDog) "Mace (in hand), Chatchka": ravgear's obsidian mace (74) in 3, box "Obsidian Mace 1D6
Hit -2", 15, a chatkcha in the pack, the club in the pack; **earth** (SeanBoy) the same, the obsidian mace and a
chatkcha; **water** (Lanthazar, the game's name again) "Mace (in hand)": the bone mace (67) in 3. **The game's club
went to the pack for the earth and water clerics too**: the sequel's club (type 29) has no material (+4 40h), which
the class restrictions' sphere rule (restrict.material, DSCLOG2's SPHERE_ALLOWS) refuses to every sphere, though the
sequel's own class lists give it to earth and water clerics; their mace, a weapon of their sphere, takes its place
(Shattered Lands' club is wood). Open.

**DOSBox died** once at the title menu (an Escape from View Character, then CREATE CHARACTERS: the DOSBox log's last
line "Failed to open window"); started again, the party empty: ADD (a right click on an empty slot, ADD on its
second row; the list's rows from y 45, 11 apart, newest first; ADD 252,47) brought the lotulis fighter back with his
lotulis (DAM 2x2D4+5): the roster's copy has the new weapon (GEAR_DONE holds DONE before the roster write).

**The fight.** Lanthazar (fighter, lotulis), Aticus (gladiator, double spear), Balthbeorn (air cleric) and the water
cleric added, START GAME from the title (S), the cinematic, "Lead on!" (100,171) twice: the Tyr ambush. HP 250 each
(`ravkits.py hp M 250`, a test edit, never saved: no SAVE file written), C on a member's turn (USE), the inventory
(75,171), Computer Control on its small icons (6,17 / 6,65 / 6,113 / 6,161). Won in round 9 (10,000 XP each).

```
Lanthazar attacks Draxan#23 with Stone Lotulis +1 (2d4+1): d20 = 16, needs 8+ (65%), hits AC -7, target AC 1 -> HIT
    THAC0 14, +1 STR, +1 weapon, +3 mastery = 9
  Lanthazar hits Draxan#23 for 9: 2d4 = [3 + 1] +1 weapon +3 mastery +1 STR 17
Aticus attacks Draxan#23 with Wooden Double Spear +1 (1d6+1): d20 = 14, needs 10+ (55%), hits AC -3, target AC 1 -> HIT
    THAC0 14, +1 DEX, +1 weapon, +1 specialized = 11
  Aticus hits Draxan#23 for 5: 1d6 = [2] +1 weapon +2 specialized
Balthbeorn attacks Draxan#27 with Obsidian Dagger (1d4): d20 = 18, needs 16+ (25%), hits AC -1, target AC 1 -> HIT
```

Lanthazar swung **2 a round, every round 1-8** (16 swings, 7 hits), each with "+1 weapon, +3 mastery". Aticus swung
**once a round** (rounds 2-8) with the double spear; Balthbeorn the dagger twice, then the sling.

**The control: the dice log with `RAV_NO_FIRST_WEAPON=1`** ("first pick weapon off"; DOSBox started again, the same
copy). A fighter (Morbad) picking the lotulis: "starts with more gear: Sling" only; **the Longsword +1 in 3, the
shield in 10** ("+1 Longsword 1.5x1D8+2"). A gladiator (MadDog) picking the double spear, long sword, club: **the two
Longswords +1 in 3 and 10**. The ambush (HP 250, Computer Control on the USE screen's small icons 47,53 / 98,53;
an earlier C pressed on a foe's turn did nothing, and the clicks after it moved MadDog, whose END MOVE menu's END TURN
is 205,100): Morbad **2, 1, 2, 1, 2, 1** with "THAC0 14, +1 STR, +1 weapon = 12" (no mastery: not his kind), MadDog
**3 a turn** (two long swords, his second spec). Stopped at round 7 (DOSBox killed by pid), nothing saved.

## What was learned

- The sequel's weapon lines (View Character's DAM, the inventory's) and its attack take a **double spear** that isn't
  first in its item list for no weapon (the Loader's sling, given after it, went first): a weapon made over in place
  must be put first in its list (`ravfirstweapon.weapon_first`, as the inventory screen's equip leaves it).
- **A double spear specialist swings once a round** (the inventory "1D6+3" with no rate, "(2x1D1+1)" under it,
  View Character's DAM the bare hand's 2x1D1+1), the same after the game's own equip: a gladiator whose first pick is
  the double spear trades the game's two long swords (3 a turn) for 1 a round. Not this change's (the port's double
  spear rate); open, for the owner.
- A ranger can't pick the bow (greyed: his expertise); a fighter's bow pick goes to the missile slot with +1 arrows.
- The earth and water clerics' club goes to the pack (no material in the sequel: above).
- Two characters may get the same name from the game (Aticus, Lanthazar twice): the dice log's `--numbers` tells
  them apart in a fight, the ADD list by its order.

## Tests

`DSUN_WOTR=/tmp/playtest/rav python3 -m pytest -q tests`, `python3 -m unittest discover -s tests` and the start-up
tests on both games' files: 2841 passed, 96 skipped; 2655 OK (133 skipped); 2 passed.

No new area: no water noted. ravFW kept for now (no saves in it).
