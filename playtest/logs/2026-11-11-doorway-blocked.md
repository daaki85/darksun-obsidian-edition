# Kurzak's door: open, but the doorway barred (2026-11-11)

The user's save ("Page 1 slot 02 - error doorway blocked", `saves/doorway-blocked-user`): the
party in the corridor south of Kurzak's entryway (leader 1576,600). "The doorway is open but the
party cannot move into it", and after a rest Kurzak's "Legcrusher! Get gladiators!" came, but
Legcrusher stayed where he stood (1704,328, north of the door).

## What was found

- The live walk map (DS:0556h): square 99,33 0, **99,34 192** (shut). `doors.py` lists 99,34 as a
  closed door. A breadth-first walk on the map: Kurzak's door is the only way between Legcrusher
  (106,20) and the party (98,37), and between him and the fire room (118,54).
- The leaves (objects 2145 and 2146, map things 96 and 225 in this save): +12h = **08h** on both,
  open (a shut leaf has 20h, 2145, or 10h, 2146; seen in `pens-after-scar`, `pens-fire-count4`,
  `pens-after-arena`). +11h 03h open, 00h shut. +17h a frame: 07h shut and drawn as the spiked
  gate; 04h open; 00h in the user's save, drawn as nothing (the doorway looks open).
- Legcrusher's order (DSUN 3972:08AAh table): 0Dh, script 136 at 4D2h, his fetching routine; it
  ends in an approach (3Ah) that has no way to walk, so he stands for good. Writing 0 and 0Dh again
  doesn't run the routine again.
- Square 99,34 set to 0 in memory: Legcrusher walked to the party at once and said his line.
- **The game's own call, watched** (`doorwatch.py` in the background, `pens-fire-count4`, two
  `ringrest.sh`, the boxes dismissed): the square opened as the call came (Kurzak walking to his
  stop, 1592,504), "Legcrusher! Get gladiators!" a minute of game time later, and Legcrusher walked
  through the door to the fire room, said his line, and went back. So the game's call needs no
  help.
- **A first fix that was wrong**: a door action (22h: 2, -2145, 1, 1) put before Legcrusher's
  approach and before Kurzak's line. With it the call's open door **shut** as the line came (the
  same action Kurzak's script uses to open it; on an open door it closed it, or it is an order the
  speaker carries out), and Legcrusher stood still on a fresh call too. Dropped (kept in `git stash`
  in that container only).

## The fix

`dsloader/kurzakdoor.py`: in the pens, out of fights, both leaves open (+12h bit 08h) and square
99,34 shut for 10 game seconds: the square is set to 0. The dice log says "Kurzak's door: open, but
its doorway was barred on the map; opened".

On the user's save, loaded as it is: the line at once; Legcrusher walked through (1704,328 to
1576,584), "Kurzak told me to bring you to the arena...", and went back north. Left alone, Kurzak
ran out of patience ("Help! Somebody sound the alarm!") and a fight began, as the game does. Loaded
again and `route.py 1592 520`: the party walked through the doorway to Kurzak's stop, "I'm glad you
listened to Legcrusher. ... The crowd is waiting! Get moving!".

How the leaves and the map came apart is not known (the save holds the result only).

Water: none new (the pens' corridor and Kurzak's stop, places already noted).
