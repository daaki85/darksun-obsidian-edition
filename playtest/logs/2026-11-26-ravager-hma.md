# 2026-11-26: DSCLOG2's far block and the HMA (PR #203, claude/ravager-graphics)

**Under test:** where DSCLOG2's FAR_INIT puts the far block now that #203 grew it to FD00h (the
see-through tables in it), whether the HMA is really free and A20 safe, and the fallback when the
HMA is taken. GOG's DOSBox 0.74-3, the Loader's start (`RAV_LOADER=1 ravstart.sh`), a throwaway
copy `/tmp/playtest/ravHMA`; nothing saved.

## FAR_INIT against the XMS spec

- `4300h`/`4310h` (XMS there, its entry), then **01h** with DX=FFFFh (the whole HMA).
- **90h** ("no HMA"): what DOSBox 0.74's XMS always answers (01h and 02h are stubs there), though A20
  and the memory at 100000h work. FAR_INIT then uses the HMA only if FAR_RING to FAR_TOP is all zero
  (DOSBox clears memory; nothing else uses it there). Seen in play: the answer 90h (`HMAGRAB.COM`
  below printed `AX=00 BL=90`), and DSCLOG2's stale install bytes show `hma_given` 0.
- **91h** (in use: DOS=HIGH, DOSBox-X's default `dos=high`) and **92h**: straight to a block, no A20
  call. Right.
- **03h, global enable**: the spec gives global enable to the HMA's owner (others use 05h, local).
  FAR_INIT calls it only after 01h gave the HMA or said there is none, so it is the owner's call. Then
  the wrap test (FFFFh:0010h no longer 0000h:0000h, a word NOTed and back with interrupts off; NOT
  keeps the flags) before a byte is written.
- **Nothing releases A20 or the HMA**: right for a TSR that stays for the session. SL's DSCLOG checks
  A20 each main-loop pass (A20_CHECK, A20_LOST); DSCLOG2 has no such check (the sequel's XMS calls
  are its memory layer's moves, not A20's; nothing seen turning it off).
- **The bug, fixed:** with the HMA *given* (01h AX=1) but A20 refused by 03h, or still wrapping, the
  old code went to upper memory and kept the HMA, never to use it: nobody else could have it. Now it
  is handed back (XMS 02h) first. Never seen in DOSBox (A20 always comes on there).
- **Room:** FAR_PARAS 4048 (FD0h) paragraphs. DSCLOG2's MZ header asks for only its image plus 256
  bytes, so DOS has memory left for 48h's fallback. Too little anywhere: CF, `DSCLOG2: no memory for
  its ring. Not loaded.`, exit 4C01h, no vector hooked; the game then runs without the helper.

## Emulator tests (`tests/test_far_init.py`, unicorn + nasm)

XMS (INT 2Fh and its entry) and DOS's 48h/58h played by the test; DSCLOG2's and DSCLOG's FAR_INIT:
the HMA given (FFFFh, cleared, `[1, 3]` XMS calls); 90h and all zero (FFFFh); 90h with something
there (upper memory, the HMA left as it was); 91h (upper memory, FAR_SEG a paragraph below the block,
cleared, link and strategy restored); 91h without upper memory or with too little (conventional);
no XMS (upper memory); too little anywhere (CF, FAR_SEG 0, nothing allocated); A20 refused or
wrapping (DSCLOG2: the HMA handed back, the vectors untouched). INSTALL (DSCLOG2): no room says so and
exits 4C01h with no vector set; with the HMA or upper memory it stays resident (31h) with the header's
FAR_SEG right. The two A20 cases failed before the fix.

## In game, GOG's DOSBox, the Loader's normal start (title menu)

`dosmem.py`: DSCLOG2 loaded high at CA0Ah (55,296 bytes), its see-through block at EE9Fh (5,632),
upper memory free 94,512 bytes (D78Bh); **far_seg FFFFh**, the far block FFFF:0010-FD00 all zero
before the game's first use, the HMA past FD00h zero; **A20 on**; conventional memory free after the
game 126 KB (129,728 bytes the largest).

## The HMA taken, GOG's DOSBox

A throwaway config (`$WORK/ravHMA.conf`: the Loader's, with `c:\hmagrab.com` before `lh
d:\dsclog2.exe`). `HMAGRAB.COM` ([its source](files/2026-11-26-hmagrab.asm)) asks XMS for the HMA
(answer 90h, as above: in 0.74 nobody can be given it, so "taken" here is the other way it can be:
something's bytes in it), turns A20 on and writes `HMA TAKEN (TEST)` at FFFF:0010.

- DSCLOG2 saw the bytes and went to upper memory: its block at CA0Ah, the see-through block DECEh,
  **the far block E02Fh** (4,048 paragraphs, the top of upper memory: strategy 42h, last fit);
  FAR_SEG E02Fh in the header; the marker still in the HMA, untouched. DOS's MEM: 632 KB
  conventional, 29 KB upper free (29,728 bytes the largest).
- The game ran: the intro, START GAME, the cinematic, Tyr's first scene (the Veiled Alliance's
  woman). `ravfig.py`: fig_shadows 1, 11 passes, **57 shadows cast**, 22 frames kept (the shadows'
  slots are in the far block). `ravdice.py 25` (the Loader's dice log): GHOST_ON 1, the see-through
  block DECFh, the Loader's BLEND (24 x 256) written into the far block in upper memory (6,144
  bytes, all set), GHOST_TAB empty (nobody see-through in that scene), draws 0. So the Loader follows
  FAR_SEG wherever it is.
- Conventional memory after the game 139 KB free (this run's title-menu figure 126 KB was at a
  different point; not a like-for-like comparison).

## DOSBox-X

Not run: no DOSBox-X in this container (the earlier ones were built in sessions now gone). From
`claude/ravager-dosbox-x`'s and `claude/dosbox-x-default`'s notes and `dosboxx.conf_lines`: DOSBox-X's
default is `dos=high, umb` (its DOS in the HMA): XMS answers 01h with 91h, and DSCLOG's far block went
to upper memory (HISTORY.md, "With DOSBox-X's default dos=high"), leaving the game's buffers short of
room. The Loader's DOSBox-X settings set `[config] dos=umb`, so DOS is not in the HMA and the HMA goes
to the helper (logs/2026-11-25-dosbox-x-upper-memory.md: "the HMA already holds DSCLOG's far block").
The sequel's start there uses the same lines. Under `dos=high` DSCLOG2 would need about 7,920
paragraphs of upper memory (itself, the far block, the see-through block): DOSBox-X's CC00h-FBFFh
(the Loader's) has 12,288, its default CC00h-EFFFh 9,216, so it fits either way.

## Still to do

- DOSBox-X in game with #203's DSCLOG2 (a build of DOSBox-X first).
- A see-through figure drawn with the far block in upper memory (none in Tyr's first scene).
