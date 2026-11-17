# 2026-11-16: DSCLOG memory pass 4, checked in DOSBox

The kit rebalance had left the helper's segment 320 bytes spare (960 at 2.17.0) and upper memory
once installed 43 paragraphs (83). Measured from a scratch build with a `dd` of the limits appended
(`kept_end`, `UMB_KEPT` and the rest read back from the EXE).

## What changed

- `ES_THINGS` (mov ax, ds / add ax, THINGS_SEG / mov es, ax) called at its 23 sites;
- `SHEET_OF_AX` (imul ax, ax, 47h / les bx, [1661h] / add bx, ax) at 19, the `[bp+N]` forms with a
  `mov ax, [bp+N]` first; `CREATURE_SHEET_AX` (a creature's sheet, AX as the inline code left it) at
  2 more. Each a drop-in: the same registers and flags at the end;
- the table of the Loader's file copies: the name once, its `D:\` path made in `COPY_PATH` as the
  file is opened (each entry had a 16-byte path of its own).

Found by a count of repeated instruction sequences in the resident code (3 to 6 lines). The
prologue `mov bx, sp / push word [ss:bx+36] / push word [ss:bx+34] / push bp / mov bp, sp` (15
sites) and the push/pop runs were left: a routine can't push to its caller's frame cheaply.

Result: DSCLOG.EXE 70,768 to 70,464 bytes; the segment 624 bytes spare, `UMB_KEPT` 62 paragraphs
spare, `UMB_NEED` 1,684. The tests: 1922, OK (three byte patterns brought up to date).

## In the game (`fountain-user`)

- `buildcheck.py` OK; DSCLOG's `objects_on` (+218) 1: the game opened the Loader's SEGOBJEX copy by
  the new path.
- The ambush: Lex's hit ("THAC0 18, +3 STR, -1 bone"), the guards' shots, Seneca hidden (the cloak's
  +10), moved silently, a backstab with Hayneedle and the Templar's save against its poison
  (KIT_SAVE: ES_THINGS), Shadowseeker "+1 specialized", the kill and its XP; Seneca drawn
  see-through while hidden.
- View Character (saves, MOVE, THAC0) and Effects ("KIT: STALKER / EXPERT IN LONG SWORD / BOW") for
  Jenna.

No game was saved.
