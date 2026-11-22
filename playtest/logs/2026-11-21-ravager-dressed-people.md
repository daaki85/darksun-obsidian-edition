# 2026-11-21: Wake of the Ravager's dressed people, in game

(The pictures this log links to show the games' art: they are kept in the owner's private repository, not
in this public one, so the links here lead nowhere.)

Under test: OBJEX.GFF from darksun-recompiled `people_dress.py build` (branch claude/ravager-own-figures,
73 people dressed on SL bodies), in a real copy of the install ($WORK/ravsl), started with ravstart.sh.
The opening street (RGN032) holds 715, 721, 2410, 2421, 2422, 2423, 2426, 2427, 2428, 2464, 2558.

## Set-up

- This container had no `dosbox` or `xdotool`: `apt-get install -y dosbox xdotool nasm` (Xvfb and
  ImageMagick were there). The sequel was already in `$WORK/rav`.
- `cp -a $WORK/rav $WORK/ravsl`, the built OBJEX.GFF in it, `__support/save/*` copied back in,
  `sh ravstart.sh $WORK/ravsl` (about 90 s to Tyr). The lock held by a background flock.

## Seen

1. **The opening talk**: the blonde woman who calls the party to the Veiled Alliance is 2426, now on
   the SL elf woman (body 305): bright blonde hair, tan skin, light brown dress, the right size and
   standing on the floor (`img/2026-11-21-rav-blonde-woman.png`).
2. **Talk answer 3, Return**: the Draxans' ambush. The two Draxans who come out of the house on the
   left are 2428, the bald fighters now on the SL mul (body 312): gold loincloth, dark green bands,
   no topknot or harness left. Seen walking sideways (`img/2026-11-21-rav-muls-walking.png`) and in
   their fighting stance round the party (`img/2026-11-21-rav-muls-fighting.png`); anchors right.
3. Q then E ends a turn; one E press opened the EFFECTS screen instead (Escape closed it).

Not seen this time: the other dressed people (they stand in other regions or further up the
street). DOSBox stopped by pid afterwards; nothing saved.

## Second play: the half-elves and the miners (stand-ins)

The half-elves and the miners stand in later regions (miners RGN039; half-elves at the far ends of
RGN032), and two ways of reaching them failed:
- **Writing the camera** (DS:1408h) in a fight: the value takes, but nothing redraws, and the
  camera snaps back to the member whose turn it is at the next menu.
- **HP 0 on the Draxans** (creature records 25, 26, 29, 31, the ones with +16h = 07): the fight
  goes on and they keep their turns; HP alone doesn't end a fight.

So a test OBJEX put the figures in question into the opening's own slots instead (`people_dress.build`
with dress['2428'] = dress['2464'] and dress['2426'] = dress['3612']; the slot's own script kept):
1. **The miner with her pick** (3612 on the elf woman) as the woman of the opening talk: the pick in
   her hand, the right size, on the floor (`img/2026-11-21-rav-miner-pick.png`).
2. **The half-elf man** (2464) as the Draxans: walking out of the house and standing round the party,
   the right size beside the party's half-giant (`img/2026-11-21-rav-halfelf-man.png`).
Not seen: the half-elf woman (her body is the same build pipeline as the man's), 3613's pick on
the half-giant. A save in a later region would let the real ones be checked.

## Third play: the half-elf woman and 3613's pick (stand-in slots)

dress['2426'] = dress['2427'] and dress['2428'] = dress['3613']:
1. **The half-elf woman** (2427) as the woman of the opening talk: red hair in its bun, the cape
   behind, the right size (`img/2026-11-21-rav-halfelf-woman.png`).
2. **The half-giant miner with his pick** (3613) as the Draxans: walking out of the house with the
   pick held in his hands, a head taller than the party (`img/2026-11-21-rav-halfgiant-pick.png`).
Every body in this round has now been seen in game.

## Fourth play: the mind flayers (stand-in slots)

Seven mind flayers (2884, 2885, 2887-2891) dressed on SL's hooded robe (body 24) with face tentacles
(darksun-recompiled `tools/proto/flayer.py`, branch claude/ravager-flayers). dress['2426'] = 2884
(green) and dress['2428'] = 2891 (purple):
1. The green flayer stands in the opening talk, lavender head and hands, the purple collar
   (`img/2026-11-21-rav-flayer-green.png`).
2. The purple flayers walk out of the house sideways and fight round the party
   (`img/2026-11-21-rav-flayers-walking.png`). Anchors right.
This container needed `apt-get install dosbox xdotool` again and Xvfb was gone: ravstart.sh starts it.
