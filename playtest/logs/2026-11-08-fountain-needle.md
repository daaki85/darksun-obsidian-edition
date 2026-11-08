# 2026-11-08: the fountain ambush's guards, and the needle avoided, in DOSBox

**The fountain** (`saves/fountain-user`; the built GPL 145 at E7Dh jumps to the repair's detour at F3Bh):
the guards' creature records and map entries read before the ambush and 3 s after it fired.
- With the fix: five new guards on squares of their own (1112,1512; 1112,1528; 1160,1512;
  1128,1512; 1128,1528); round 1 theirs and the Templar's; no other guard's record or map entry
  changed but bytes 12-13 of each map entry (and Guard 39's walk, as without the fix).
- With the game's script (scriptfixes.py at HEAD, rebuilt by loadsave.sh): the same five, and
  Arena Guard 17, 55 squares off at (872,632), set out at once (its map entry's place and frame
  changed, its record's +56), on to (856,632). In a fight the game waits on the party's turn, so
  the far guards' walk in wasn't watched further.

**The needle** (`saves/trap-user`, the chest shut by the Loader): beside it, Lex's bash
(`bashloop.sh 25`) broke the lock on the third try: "...a poisoned needle springs from it!", the
party's best roll "Seneca tries to find/remove traps: d100 = 22, needs 52 or less -> success",
flag 795 set by the Loader before the click; after it "The needle is seen in time, and it hurts no
one."; the next click opened the chest.
