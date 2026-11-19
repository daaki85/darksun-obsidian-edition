# 2026-11-19 (4): Scare in Wake of the Ravager, unfixed against fixed: the saving throw's fixes at work

**Under test:** Scare's record fix (`scare_save`: its save bit, so the save code's rules run) and
the saving throw's signed compare (`save_signed`, found by hand), in the sequel's first fight. Unfixed,
Scare's record allows no save: everyone in its reach is scared. Fixed, 6th level and up always save
(below 6th can't, and with the signed compare that "can't" fails).

1. **Spells known** are a bitset: the `SPST` chunk of a roster character (15 bytes, bit n spell n,
   wizard spells only; priests get their spheres'). Ar'anda's in the roster: 0, 3, 8, 11, 13, 17, 24,
   27, 29 (Armor, Chill Touch, Magic Missile, a fourth 1st-level, Detect Invisible, Invisibility,
   Web, Fireball, Haste). In memory, after START GAME: the 15 bytes at 3F3DCh (09 29 02 29 ...).
   Scare is 21: byte 2 bit 5 set (02h to 22h), a test edit, never saved. The USE screen then offers
   Scare on her LEVEL 2 page at once.
2. **The fixed copy** (ravfix): the talk, the party walked up the street, the fight. Thy'rokh's turn
   ended from his figure's menu; on Ar'anda's turn Scare (USE, LEVEL 2, the third icon): its reach a
   ring of dots round the aim; aimed at the Draxan by Gerakis, the ring took in Gerakis and Thy'rokh.
   Cast. Then a Draxan hit Gerakis (165 to 140): it wasn't scared (a level 8). On Gerakis's turn, and
   on USE: **all four Okay**. No creature record's +18h changed.
3. **The game as it is** (rav): the same steps, but the turn order differed (Ar'anda first), so the
   script's clicks went astray; then by turns: **Q** brings the END menu and **E** is END TURN (the
   manual's hot keys: C cast, G guard, W wait, N/P next/previous foe, 1-4 the leader; Esc with nothing
   up quits). On her turn every icon was crossed out: **a caster hit in a round can't cast in it**
   (the cluebook). Next round (Terrannus Out Cold by then) Scare aimed at the Draxan by Thy'rokh, the
   ring over Thy'rokh, two Draxans and most of Gerakis. Cast: **Thy'rokh Afraid** (the panel: "Thy'rokh
   45/72 Afraid", running up the street), a fighter/druid 6/6; his record's +18h 00 to 60h, and
   Terrannus's too (7th level).
4. So: unfixed, a 6th-level member in Scare's reach is scared, with no save; fixed, members of 6th
   and 7th level in its reach stay Okay. The difference is the fixes', not luck: neither result has a
   roll in it (no save allowed; an automatic save). The Draxans weren't seen scared either way (none
   fled; their +18h unchanged), not explained: perhaps immune, or out of the ring's real reach.
5. **Tools:** `ravfight.py` (state, end, until N, wait, cast): whose turn (DS:426Dh), the map
   objects (25h-byte records from DS:67BBh, x +3, y +5, less the camera at DS:1408h; a figure's body
   about +12, +18 of it); `ravscare.sh` now gets to Ar'anda's LEVEL 2 page by turns and leaves the aim
   by hand. A party member under the pointer is drawn yellow, a foe red.

**Stalls:** the turn order varies from run to run (scripted clicks for one order land on the wrong
member in another); an E sent when the END menu had already gone opens the Effects screen (Escape
closes it); a click meant for the LEVEL button while no screen was up walked Ar'anda.

**Water:** a shop by the street's north end with jugs and sacks (not tried).
