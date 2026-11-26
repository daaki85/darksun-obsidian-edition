# 2026-11-19 (3): Wake of the Ravager's first fight, looking for a fixed spell to cast

**Under test:** a fix at work in a real fight: a fixed spell cast, or a save against a "can't
save" spell, in the fixed copy (`ravfixes.py`, 6 program fixes, 23 spell fixes).

1. `ravstart.sh /tmp/playtest/ravfix` to Tyr; the talk with 3 and Return (four times). Its end is
   the cluebook's ambush: **the Draxans kill the woman** (her record, "Preserver", at 0 HP) and a
   fight starts at once, which is why USE stayed on Thy'rokh: **in a fight USE opens for the one
   whose turn it is**, and MAKE <NAME> LEADER and a portrait click change nothing then. The
   cleric Terrannus was 52/64 by then.
2. **Whose turn**: WotR DS:426Dh (SL's 4979h, `ravds.py`); written to 0, the game put it back to
   2 at once (the turn's own). No save after that edit.
3. **The pointer** cycles with right clicks on bare floor: the arrow (walk), the sword, the look
   icon. A figure under the pointer turns red. The look on a figure opens a box (Draxan, LEVEL: 8,
   Bow, Lotulis), closed by a click on it (not Escape). Thy'rokh's sword click on the Draxan
   ended his turn; Ar'anda walked beside it (Move 12 to 8).
4. **The party's spells** (hovering each icon names it in the bar): Thy'rokh (druid) Bless,
   Curse, Cure Light Wounds, Invisible to Undead, Protection from Evil, Remove Fear, Shillelagh /
   Aid, Altruism, Barkskin, Flame Blade, Hesitation, Hold Person, Resist Cold, Silence 15', Spiritual
   Hammer / Create Smoke, Cure and Cause Blindness, Spike Growth, Dispel Magic, Heat Exhaustion,
   Magic Vestment, Strength of One, Prayer, Protection from Fire, Remove Curse, Summon Insects.
   Ar'anda (mage) Armor, Chill Touch, Magic Missile / Detect Invisible, Invisibility, Web /
   Fireball, Haste. Terrannus (earth cleric) the same 1st and 2nd plus Magic Stone, Sanctuary, Find
   Traps; 3rd Bramblestaff, Stone Shape, Negative Plane Protection, Bestow Curse, Remove Paralysis;
   4th Condense, Dust Cloud, Return to Earth. **Of the fixed spells only Chill Touch** (Dispel Magic
   and Bestow Curse SSI fixed; Negative Plane Protection's bug is there, unfixed); no "can't save"
   spell.
5. **Chill Touch** on the Draxan: the aiming icon up, the target red under it, and the click taken
   by nothing, three ways (a slow press, again, a double click): no cast, no record changed. Too far
   for a touch, most likely (about 1.5 squares across). **Magic Missile** on it: Ar'anda's turn
   ended, and a Draxan (record 25, outside the first snapshot's 24) was at 62 of 70 afterwards:
   Thy'rokh's blow or the missile, not told apart. Then Terrannus's turn; stopped there.
6. **Records**: the creature records list all the region's people (37 at Tyr's start: Draxans,
   templars, Arslan, Notaku, the giant skeletons...), not only those present (`ravcreatures.py`);
   SL's map-object table (DS:6694h) is WotR's 67BBh, its stride not SL's 32 (not decoded).

**Next:** teach a member a fixed ranged spell in memory for a test (Scare, Minute Meteors; the
spells-known table not found yet: SL's far pointer DS:132Ah; WotR's far pointers so far are SL's
+364h), or step the aim click against the game's own pointer state; then a save against a "can't
save" spell for the saving throw's fix.

**Water:** none seen beyond the pot and jug in the opening room.
