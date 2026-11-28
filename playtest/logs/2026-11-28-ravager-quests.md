# 2026-11-28: Wake of the Ravager, the Journal tab's quests

Under test: the sequel's flags (`ravlog.ADDRESSES["FLAGS_PTR"]`, DS:15F2h), `ravquests.py` put in quests.py's
place by the sequel's layout, and the dice log's `quest_look` in the sequel's pass (branch `claude/ravager-quests`).

## The flags in memory

`ravload.sh ravager-after-ambush`: the far pointer at DS:15F2h is 6D83:0004, and its 101 bytes are the save's SAVE
chunk 30 byte for byte (one bit set, flag 354). The numbers' pointer (DS:15F6h) is 6D8A:0004, 70h bytes on, as
the journal's work found. The roost's save holds flags 74, 354 and 369 (none of them a quest's).

## The quests read by the Loader

`ravload.sh ravager-roost`, then `ravlog.RavDiceLog` attached (quick saves and autosaves off, a scratch journal)
and its pass run for a few seconds: `quest_state` read flags 74, 354 and 369, and the Quests list was empty (open
none, finished none). Flag 104 (Dmitri's word for the Veiled Alliance) set in memory: the next passes listed
"dmitri" finished. The byte put back: the list empty again. DOSBox stopped without a save (the rule: no save after
a memory edit).

## The scripts

`gpl.py` now reads all 350 of the sequel's scripts (257 before): with no GPLX, a query's test takes a value when
the next byte can start one, and the sequel's term B3h (GPL 37 only) is read as a field, as B1h. Every jump in them
lands on a command. `python -m dsloader.questdraft` on the sequel's GPLDATA.GFF: 125 calls of script 27's reward
routines in 60 scripts (857,150 XP) and 103 of the scripts' own awards; the table is 42 quests, the other 82
calls left out with a reason each.

Water: none new.
