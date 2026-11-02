# Playtest log: the slave pens, the stalker pen and the sewer grate

Live notes, newest at the bottom. Branch `obsidian-edition`.

## What's under test

Continuing the route from the `pens-after-arena` save: the stalker pen (cluebook #11: break the
door, kill the mountain stalker, the button on the north wall), then the sewer grate (#12) and the
four grate repairs of script 137 (hack offered with a weapon in hand; his/her; a hack that works
opens the grate; a failed hack breaks a breakable weapon, a metal or magic one rings off). Saves at
each milestone into `playtest/saves/`.

## Log
16:01:51
 Container had lost the game and the work folder; setting the game up again (setup_game.sh).
16:06:07
 The user's note: the kit is to help test the recompiled program. The branch's helper (DSCLOG.EXE
 64,464 bytes, 2.13.x) differs from the one the recompiled mod build was lifted from (2.12.3):
 rebuilding build/ds1o from this branch (tools/build_mod.sh), then its convergence runs.
 Meanwhile the kit made target-aware: PT_TARGET=recomp (env.sh WINQ, shot.sh grabs the program's
 window scaled to 320x200, start_recomp.sh starts the program with the Loader's patched game at a
 320x240 window and the dice log attached, loadsave.sh uses it). The DOSBox load of
 pens-after-arena had stopped at the title (state region 2Ah, leader 0,0: not loaded).
16:09:11
 The pens save loads in DOSBox once DARKSAVE.GFF is supplied (the set had a copy of the slot as DARKRUN.GFF and no DARKSAVE.GFF; stand-in added, README says so): region 29h, leader (1672, 344).
16:13:37
 The rebuilt program (this branch's helper) hits two unlifted helper continuations at once (BEF2E at start, BBFD8 at the load): converging in the background (recall and arena scripts, then relift); the pens session restarts on the relifted program.
16:15:35
 Recompiled, pens save loaded: the screen matches DOSBox's. click.py and walkto.py work on it
 (walked 1672 -> 1608, 344). **Fault found:** the middle-button drag (the mod's map scrolling,
 scroll.py) did nothing: the runtime mapped every button but the left to the right button, so the
 driver never saw the middle one. Fixed in runtime/host.c and bios.c (bit 4, events 20h/40h,
 counts for three buttons); in the next rebuild.
16:18:21
 Pointer modes on the recompiled program as in DOSBox: right-click cycles arrow, red sword, red
 look, arrow. Walking west: the party reached the view's left edge (1528, 344) and the view did
 not follow (the camera stays at 1512); the kit scrolls it with the middle button, so nothing
 further until the rebuild with the middle-button fix. The other session's route data (the
 stalker pen door at 256,864-896, the stalker at 187,856, the button at 139,748, the grate at
 46,86) is the plan from here.
16:19:34
 Recompiled: hovering a person with the arrow shows the portrait pointer; a click opens the mod's
 Look box (Legcrusher: LEVEL, HP 50/50, AC 9, THAC0 18, AL CG; the dice log: "Look: Legcrusher:
 HP 50/50, AC 9, THAC0 18, 3/2 attacks a round, chaotic good."); its first button (216, 99) is
 Talk: "It's Kurzak you want to talk to. I'm just the monster trainer." and the WHAT DO YOU SAY?
 menu (lines at y 156, 164, 172); Goodbye clicked on its line.
16:21:44
 Recompiled: M opens the overhead map (the pens' maze, the party's arrow top right) and closes it.
 The combat log panel did not come up on L (panel.sh), to look at later with the Loader window.
 Message boxes, the panel and CHOOSE A SPELL are now detected through pixmatch.py (the program's
 colours are one off DOSBox's and its rows shifted). Guide and CLAUDE.md updated and pushed.
 Waiting for the program's convergence (each round finds one more helper continuation: BEF2E,
 BBFD8, B706F, B6DED so far) before the walk to the stalker pen, which needs the view dragged.
17:05:45
 Program relifted (this branch's helper: continuations BEF2E, BBFD8, B706F, B6DED, B0A27 and the
 die routine's tail D7F98 added; a lifter fix for a link failure, a CMake reconfigure for the
 39th generated file). With the middle-button fix the view drags on the program (camera 1512,240
 -> 1512,160 -> 1712,160). A first set of hops west stopped at (1528, 376) and the view had been
 left at the region's corner (1720, 0) by clicks that said NO PATH; the region picture
 (mapshot.py) is being made to plan the route on it. The RECALL script still ends in "Stack
 overflow!" on this helper, after the die tail runs (the game sent on to 37D2:5861): under study.
17:07:08
 RECALL on this helper (2.13): the helper now reaches the die routine's tail through RS_FRAMED
 (a far call in a frame the overlay manager may rewrite, DX the overlay's segment). On the
 program the first framed call (the scores' routine) comes back to D101:6F88, an address past
 the creation overlay (module 24's ground), and the game ends in "Stack overflow!". The program
 keeps every overlay resident, so the manager's rewriting of the way back must differ here.
 **Open fault on the recompiled program; RECALL worked on 2.12.3's helper.** Parked to keep the
 pens play going; the kit's test of it is the recall script (tools' RECALL input in converge.sh).
17:08:17
 The other session (in DOSBox) has the route: the party starts shut in Kurzak's corridor, follows
 him (follow.py 29) to square (99, 32), where he says to go through the door; route.py walks on
 the live walkability grid; doors open with the look pointer; opening that door sets off the
 alarm. Its save pens-kurzak-door is in the repository. Plan here: load that save on the
 recompiled program (a DOSBox-made save: compatibility), open the door, take the alarm fight with
 fightout.sh, compare with what DOSBox shows.
17:14:15
 pens-kurzak-door (the DOSBox session's save) loads on the recompiled program: same position
 (1592, 520), same six closed doors from doors.py, the same picture. The door Kurzak means is
 (95, 28), west of the corridor behind the gold post: the look pointer on it opens the mod's Look
 box "Door" (INFO only); the arrow and the look click on the door square itself do nothing, as in
 DOSBox. The dice log records (NO LINE OF SIGHT from a look at the guard behind the wall). Two
 Escapes with nothing open brought EXIT: SAVE GAME? (CANCEL at 150,118 each time): the rule holds.
17:16:50
 The sword pointer on the door: nothing, no message (as the arrow and the look click). Saved on the
 recompiled program (Escape, S, slot 1, End + Backspaces, RECOMP1, SAVE: the game quit as the exit
 menu does; SAVE01.SAV and CHARSAVE.GFF written, DARKSAVE.GFF left as loaded): the set is
 playtest/saves/pens-kurzak-door-recomp. Loading it in DOSBox next, for compatibility both ways.
17:19:47
 The recompiled program's save (RECOMP1) loads in DOSBox: same position and picture. Reloaded
 pens-kurzak-door on the program; the sword pointer on Kurzak (square 99,31, north of the leader)
 does nothing, no message: no fight starts from a click on a friendly figure. The dice log attached
 before the load records nothing after it (twice today): loadsave.sh now reattaches it after the
 load. Guide updated and pushed. The door stays the story's blocker for both sessions; next here:
 the USE screen and a spell cast on the program, which need no door.
17:21:36
 USE screen on the program: Gerakis's psionic tabs, Cermak's spells with SPELLS LEFT WIZ 1/2
 (MAGE, LEVEL 1), hovering an icon names it (ENLARGE); a click on the icon then on the lower box
 readies it ("1 LEVEL 1 SPELL TO CAST"); Escape to the map and a click on a figure casts it.
 **Suspect:** the cast on K'ratchek logged "K'ratchek now 0/19 HP (-12)" then "1/19 HP (+1)":
 damage from Enlarge. Repeating the same steps in DOSBox from the same save to compare.
18:41:55
 The same readied-spell steps in DOSBox and again on the program: Escape leaves the spell readied,
 the pointer stays the arrow, and a click on a figure is a walk click (NO PATH FROM HERE); hit
 points unchanged (K'ratchek 12/19) in both. The earlier "0/19 (-12)", "1/19 (+1)" on the
 program did not come back: seen once, cause unknown, kept on the list to watch for.
18:47:29
 Stopped at the user's word. State: the program runs the pens from both saves; open on the
 program: RECALL with the 2.13 helper ("Stack overflow!": after the helper's framed call to the
 scores routine, its frame comes back with the overlay's segment and a helper offset, D101:6F88;
 the trace in /home/user/scratch/rc2/recall_trace2.log). The door Kurzak means stays closed for
 both sessions. Nothing left unpushed.
