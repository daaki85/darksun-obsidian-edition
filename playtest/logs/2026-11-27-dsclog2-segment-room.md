# 2026-11-27: DSCLOG2's segment room, played (claude/dsclog2-segment-room)

Under test: DSCLOG2 in three parts (segment, tail, install). The joined build: obsidian-edition +
#218-#223 (claude/combined-playtest + claude/ravager-spell-arrows) + claude/dsclog2-segment-room, a
local merge (/home/claude/wt-dsclog2-join, not pushed). DSCLOG2.EXE 66,368 bytes: segment 56,912
(resident_end DE46h, 8,624 of 64 KB free), tail 8,624 bytes, install 800 (freed).

Game: a throwaway copy of the sequel, /tmp/playtest/rav-room (cp -a of rav).
Lock: waited for another agent's holder (al.held) before starting.

## Steps
1. `RAV_LOADER=1 RAV_UMB=1 sh ravstart.sh /tmp/playtest/rav-room` (the join's playtest/, so the join's
   dos/DSCLOG2.EXE, md5 cf07ba0b...): the sequel started and reached Tyr ("Hurry! You must come with me
   to the Veiled Alliance!"), the helper loaded high.
2. `python3 ravtail.py` (new): helper segment CA1Bh, `tail_seg` D800h = CA1Bh + DE5h (TAIL_PARAS, as
   built), the tail's signature there; SITE_TABLE (482 bytes), NS_CMP_TABLE (630), RAV_SLOTS (810),
   LARGE_DICE (66), RAV_XP (972) in memory exactly as built.
3. `dosmem.py`: upper memory from 9FFFh: CA00h free 144 bytes, **DSCLOG2 65,792 bytes** (4,112
   paragraphs: its PSP, the segment and the tail; the install's 800 bytes freed), DA1Bh free 84,016,
   EE9Fh DSCLOG2's see-through block 5,632; **84,160 bytes free in upper memory, the largest piece
   84,016**. (claude/combined-playtest's log, #218-#222 without the room change: 85,376 free.) The
   free MCB at DA1Bh, just past the helper's block, is where the install was: its name field is the
   install's old bytes, as any free block's. The HMA: A20 on, the far block there.
4. `ravdice.py 380` attached (RAV=the copy): the dice log's lines, then the Loader's writes into the
   tail read back by `ravtail.py`: SLOTS_TEXT "SPELLS LEFT|WIZ 3/4|WIZ 2/2|WIZ 2/2" (Ar'Anda's), the
   item names past 256 ("Ring/Protection", "Thieves' Tools", ... "Short Sword"), and later LBL_SLOTS
   (a label over a figure).
5. "Lead on!" (the first click only captures the mouse: one click on the window first, then
   `ravclick.py 75 168`), the talk, then the Draxans' ambush: Draxan's attack on Thy'rokh in the dice
   log with its THAC0 and damage lines; Thy'rokh's turn, the squares in reach drawn.
6. **The USE screen** (`ravclick.py 22 17`) on Thy'rokh's turn: "SPELLS LEFT / PRI 6/6" under his
   spells: USE_DRAW's lines, read through FS from the tail's SLOTS_TEXT and drawn from the tail's
   U_LINE (a far pointer with the tail's segment). Escape closed it (the screen up).
7. Stopped: the dice log and DOSBox killed by pid, the lock's held file removed (the lock free).

Not done in this short play: the watchdog (a few minutes in Tyr), the Look box's whole description
(LOOK_FULL, the tail's; its path is covered by the tests), a quick save (SAVE_TEXT). Water: none
seen on the street in Tyr's first scene (the opening's table had a jug-like pot, not looked at).
