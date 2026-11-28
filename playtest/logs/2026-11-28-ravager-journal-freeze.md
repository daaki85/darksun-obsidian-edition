# 2026-11-28: Wake of the Ravager, the journal's place in the saves and the freeze report

Under test: `ravlog.RAV_NUMBERS_PTR` (the journal's head in the sequel's global numbers) and DSCLOG2's TICKS
(branch `claude/ravager-journal-freeze`).

## The global numbers

`ravload.sh ravager-after-ambush`. A sequel save's chunks: SAVE 31 is 400 bytes (200 words: 22 = 1, 29 = 9999,
87 = 100 in every test save; the roost's and a later quick save's 82 = 1 too). Those 400 bytes are once in
memory after the load (6D8A:0004, the same bytes as the chunk), and the one far pointer to them in the game's
DS is at **DS:15F6h** (SL's 1356h); DS:15F2h points 70h bytes before them (SL's flags pointer is 1352h).

Words 198 and 199 written (12345678h) and read back through the pointer, then put back to 0 and DOSBox stopped
without a save (the rule: no save after a memory edit). The game's own saves carry the block as it is in memory
(the quick save with word 82 set), and a load fills it from the chunk, so a head written by the Loader goes
with each save. Not played: the Loader's dice log attached with the journal following a load.

The sequel's scripts: 257 decode, using numbers up to 150; in the 93 that don't, the bytes 87h C6h (number 198)
come 11 times, and 27 times in the 257 where no script uses 198: chance bytes.

## The freeze report

DSCLOG2 with TICKS at its header's +356/+358: `freeze.report_text` on the running game (no DS given): "Wake of
the Ravager", DSCLOG2's segment CA1B, the load segment 01A2 from the DSUNLOG2 block, 31 notes in a second (the
sequel's timer strikes about 1,000 times a second), the map's main loop 371 times, places such as
`2382:1D0A game 21E0:1D0A (DSUN.EXE 28D0Ah)` (the view's routine).

Water: none new.
