# 2026-11-21: Wake of the Ravager's dressed people, in game

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
