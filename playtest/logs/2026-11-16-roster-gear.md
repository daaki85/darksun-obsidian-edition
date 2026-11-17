# 2026-11-16: the Loader's creation gear in the roster, weapon specialization off and on

Under test: DSCLOG's GEAR_MARK (CR_WEAPONS with the rule off names the new member for the
Loader's gear, GEAR_HOLD holds DONE's roster write for it), on top of kit-rebalance's GEAR_HOLD.
Settings: weapon_specialization off; kits, class restrictions, fuller starting gear on (defaults).

## Steps
1. Weapon specialization off. New human thief, Swashbuckler kit, "Swashroll", slot 1. gearpoll: GEAR_DUE
   set at DONE (1.66 s; GEAR_MARK), the Loader's "Swashroll starts with more gear: Arm Armor, Leg Armor"
   at 1.71 s, CHARSAVE.GFF written at 22.71 s (after the four psionic powers). In memory: leg, arm and
   chest armour, sling, bone long sword (a Swashbuckler may use the long sword: no kit swap).
2. Worker restart killed Xvfb and DOSBox (the restart this check needs anyway); start.sh, CREATE
   CHARACTERS, right-click slot 1, ADD (112,66), Swashroll (row 6, 70,100), ADD, EXIT.
   carried.py: Leather Leg Armor, Leather Arm Armor, Leather Chest Armor, Leather Sling, Bone Long
   Sword; status Okay; no Loader gear lines this session, so all from the roster. **PASS.**
3. Weapon specialization on (default settings). New human fighter, Myrmidon, "Myrmroll", slot 1; the
   weapon window: long sword (72,46). gearpoll: window up 1.66 s, GEAR_DUE 12.63 s, the Loader's
   "starts with a plain bone polearm in the backpack too: a Myrmidon's second weapon spec" and "more
   gear: Sling" at 12.68 s, CHARSAVE.GFF written at 28.53 s. In memory: shield, leg/arm/chest armour,
   sling, bone long sword, bone polearm (backpack 14); specs long sword, polearm.
4. start.sh (DOSBox restarted), CREATE CHARACTERS, ADD Myrmroll (row 6). carried.py: the same seven
   items, the polearm in backpack cell 14; sheetinfo.py: Myrmidon, specs long sword, polearm; status
   Okay; no Loader gear lines this session. **PASS** (the case of logs/2026-11-15 part 6).

Notes: on a fresh start the main menu needs about 30 s after the two title clicks; a CREATE CHARACTERS
click before it does nothing (shoot first, then click again).
