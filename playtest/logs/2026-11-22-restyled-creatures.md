# 2026-11-22: restyled Ravager creatures in the game

What was tested: the restyled creatures after the shade cut (16 colours, flat bands), the dark-share
loop (8 to 45% near-black) and the looser stands and fuller walks of `loosen.py`
(darksun-recompiled, branch `claude/restyle-shades`).

How: Wake of the Ravager from `$WORK/ravsl`, the OBJEX built with the dressed people and two
stand-in slots overwritten by restyled creatures (RESEARCH.md, the dressed people): first
2428 = skeleton 1753 and 2426 = soulshard 2539, then 2428 = soulshard and 2426 = tan verini 2850.
`ravstart.sh`, answer 3 and Return for the ambush, `ravburst.sh NAME 30 0 40 640 400` while ending
turns with Q then E every 5 seconds.

Seen:
- The skeletons draw, stand (the looser stand, arms a little out) and walk round the party with no
  broken frames ([img](img/2026-11-22-skeletons.png)).
- The tan verini stands in the street with the looser stand toward the camera
  ([img](img/2026-11-22-verini.png)).
- The soulshard walks its new six-beat cycle in the fight; grey on the grey street, it is hard to see.

Water: no new area (Tyr's opening street only).
