# The champions' new gear: the elf's Fine Bow and Chill Arrows, DEX 22, the halfling's staff sling, the defiler's bracers (2026-11-18)

Build: branch `claude/elf-champion-fine-bow`, last at 0a6087b (champions.py: the elf's bow named Fine Bow,
24 Chill Arrows in its quiver, DEX 22). DOSBox, the Loader's patched game, the dice log.
Save: `pens-after-scar` (count 5, flags 19 and 759 set, 807 clear: the bout due on the next trip).

1. Route: arenatrip.sh (toalarm.sh: the save, Cilla's thief level raised in memory, never saved;
   the fire room, rests till Kurzak's call, toarena.sh, Y).
   (Stopped early for the defiler's bracers, b829a74: Mikquetzl's Bracers of Defense AC 6 worn on
   the defiler champion's arms. Started again on that build.)
   (Stopped again for the halfling's staff sling and DEX 22 for the Tohr-kreen and halfling;
   rebased onto origin/obsidian-edition (#106 merged, its rebuilt DSCLOG.EXE). Build 0a6087b.)
2. arenatrip.sh: two rests in the fire room, Kurzak's call, toarena.sh, Y: the arena at (488, 200).
   (No water seen on this route beyond what ROUTE.md lists: the fire room has none.)
3. In the arena: scroll.py 0 -100 twice, a click on the bone wall's gap (screen 176, 110): the
   party at (504, 360). A click at screen (160, 260) (meant for map 488,420, off the view) opened
   EXIT: SAVE GAME? and an empty red view (camera 344,1360): CANCEL, viewto.py 504 360, then
   clicks at screen (144, 145) (map 488, 425): the platform, the Announcer's champions' speech,
   fight_on 1.
4. Initiative, round 1: three Champions "+4 DEX" (DEX 22: the Tohr-kreen, halfling, elf), two
   "+2 DEX" (18: mul, defiler), one none (the half-giant, 15). The game's tables in memory:
   DEX AC 15/18/22 = -1/-4/-5, missiles and initiative 0/+2/+4.
5. The champions' lists (memory, creatures 6-11, objects 2660-2665, DEX 22/15/18/22/22/18):
   - Tohr-kreen: held Bone Kreenfang +1.
   - Half-giant: worn Bone Helm, bone scale leg, arm and chest, Leather Shield; held Metal Great Axe.
   - Mul: worn Bone Helm, bone scale set; held Metal Cahulaks.
   - Halfling: worn Leather Shield, Helm, Leg, Arm and Chest Armor; held Bone Short Sword (slot 3)
     and **Leather Staff Sling** (type 0, slot 2, the missile slot). No ammunition.
   - Elf: worn the same leather and shield and helm, **Wooden Chill Arrows** (type 62, name 16Dh,
     slot 1, count 24); held Obsidian Long Sword and **Wooden Fine Bow** (type 1, name 173h).
   - Defiler: worn **Bracers/Defns +4** (type 123, name 149h, slot 0, the arms); held Bone Dagger;
     pack: Scroll (the guaranteed one).
   The Loader's THAC0s (weapon_hits): the elf's Fine Bow 9 (14, +4 DEX, +1 fine), the halfling's
   staff sling 11 (15, +4 DEX). The Loader's AC count (counted_ac): Tohr-kreen -2 (3, DEX -5),
   defiler 2 (10, bracers -4, DEX -4), halfling and elf 1, mul 2, half-giant 4.
6. The champions renamed in memory (Kreen, HalfGiant, Mul, Halfling, Elf, Defiler) so the dice log
   tells them apart (memory only: never saved). Party turns passed (passn.sh).
   - `Halfling attacks Cermak with Leather Staff Sling (1d3): d20 = 12, needs 5+ (80%), hits AC -1,
     target AC 6 -> HIT` / `THAC0 15, +4 DEX = 11`, then the stinkpot: Cermak's save failed,
     nauseated 2 rounds. The staff sling shoots with no ammunition.
   - `Elf attacks K'ratchek with Wooden Fine Bow (1d8): d20 = 20 (natural 20), needs 9+ (60%), hits
     AC -11, target AC 0 -> HIT` / `THAC0 14, +4 DEX, +1 fine = 9` / `Elf hits K'ratchek for 6:
     1d8 = [6]`. No Chill Touch cast and no save (a non-party archer: DSCLOG's AMMO_ARCHER); the
     arrows went 24 -> 23.
7. fightout.sh: the party lost (YOUR PARTY HAS BEEN DEFEATED; the defiler's Ice Storm took its own
   half-giant and mul with it at 1 HP). Seen on the way: Cermak attacks HalfGiant, target AC 3.
   No party attack reached the elf or the defiler: a second run for their AC.
8. Second run, the same way up (arenatrip.sh, then scroll.py 0 -100 twice, the gap's click,
   viewto.py 504 360, clicks at screen 144,145): the bout. The champions renamed again; the
   Tohr-kreen, half-giant, mul and halfling put at 1 HP and the elf and defiler at 200
   (foeset.py, memory only); a copy of fightout.sh without hp.py and with healparty.py each pass
   (in the work folder, not kept). The game's AC in the party's attacks:
   - `K'ratchek attacks Defiler with a claw (1d4): ... target AC 2`: 10, the bracers' -4, DEX 18's
     -4 (without the bracers, 6: logs/2026-11-05-champions.md). The bracers count.
   - `Cermak attacks Elf with Wooden Quarterstaff (1d6): ... target AC 0`: DEX 22's -5 (at DEX 18 the
     elf was AC 1: 10, -3, -4, -2).
   - `Cermak attacks Mul ... target AC 1` (as before).
   - The halfling again with its staff sling (`THAC0 15, +4 DEX = 11`) and the elf eight shots with
     the Fine Bow (`THAC0 14, +4 DEX, +1 fine = 9`), hits for 1d8, never a Chill Touch.
9. The bout won (`DONE after 21`). The bodies (bodyitems.py): the elf's holds the **Wooden Fine Bow**
   (name 173h), **Wooden Chill Arrows, 14 left** (10 shot), the long sword, the leather and shield;
   the defiler's the **Bracers/Defns +4** (20,000), the Bone Dagger and its Scroll; the halfling's the
   **Leather Staff Sling**, the short sword, the leather and shield; the Tohr-kreen's Kreenfang. So all
   are there for the party to take (not picked up in this run).
10. Nothing saved (memory edits: Cilla's thief level, the names, the HP). DOSBox and Xvfb stopped.
