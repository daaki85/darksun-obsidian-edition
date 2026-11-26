# 2026-11-18: the six additions on the current branch, checked together

Under test: the branch `claude/modernisation-integration`: the journal, the picture and music
device, the chance to hit, quick save with autosave, the quests and "showing what can be used",
rebased onto `origin/obsidian-edition` (d74b15f: 2.18.0, the item glows, the champions' gear, spell
arrows for archers outside the party). The helper is the merged `dos/dsclog.asm` built with NASM
2.16.01: `DSCLOG.EXE` 70,688 bytes, signature `DSCLOGvc`, quick save's four header fields at +1868
to +1879 (after `GEAR_WHO`, +1867; on the old branch they were at +1860, where this branch has
the Poisoner's `POISON_USED`).

A private game: a scratch copy of the kit and of the game, its own Xvfb (`:60`), DOSBox copied as
`dbint`, the dice log attached by pid, everything stopped by its pid file at the end. The shared
game's display and the other agents' games were not touched. No memory edit anywhere, so the
autosave and the quick save below are saves of the game as played.

## The build

- `nasm -f bin -o dos/DSCLOG.EXE dos/dsclog.asm`: no limit passed. From the map file: `kept_end`
  65,008 (`resident_end` 64,016 + 992), 528 bytes of the segment spare; the tail 5,648 bytes;
  `FAR_END` 65,500 (36 spare, unchanged); `UMB_NEED` 6,512 paragraphs (1,670 spare); `UMB_KEPT`
  8,134 (48 spare, 768 bytes).
- The suite with the game's files (python 3.13): 2,085 tests, OK, 27 skipped (tkinter). The window
  tests under `/usr/bin/python3.12` on `:60`: OK once `test_viewer_options` looked for the status
  line's new words ("from the next start").

## In the game (`fountain-user`, then the quick save made there)

1. `loadsave.sh fountain-user`: the window 320x240; `buildcheck.py` OK (129 vectors at their
   handlers; the tail's `extra_types`, `extra_names` and `kit_names` the same as the EXE).
2. `memaudit.py` with the ambush's speech up: DSCLOG 70,912 bytes in upper memory, nothing between
   it and the overlay buffer, 29,424 bytes free in one piece; `umb_need` 6,512; DOS memory free
   after the game 94 KB, the largest piece 96,960 bytes.
3. Their side, the item glows: Seneca's inventory in four captures 0.4 s apart: the pixels of the
   Hayneedle's and the Shadowseeker's icons change among the water's blues ((170,162,255),
   (125,117,231), (85,85,255)), nothing else on the screen but four pixels at its bottom edge. THAC0, saves
   and thief skills on the screen as before.
4. Ours, the chance to hit and the Tab ring: `tabhit.sh 1 nohit` on Seneca's turn: `Chosen with
   Tab: Templar (41 HP), Bone Hayneedle +1 needs 12+ (45%); Metal Shadowseeker +1 needs 11+ (50%);
   Leather Sling needs 11+ (50%) - Enter attacks it`; `altflag.py`: 1 ring marked. Jenna's turn:
   `Obsidian Long Sword needs 13+ (40%); Bone Long Sword needs 12+ (45%)`, and her swings' own
   lines said `needs 13+ (40%)` and `needs 12+ (45%)`.
5. The fight fought out with `PT_NO_EDIT=1 sh fightout.sh 200` (no foe's HP changed): 6 rounds, 6
   kills. Their side's kit fields beside ours: Seneca's poison (`Guard's saving throw vs Poison (10
   damage) from Seneca ... -> saved`; the Poisoner's `POISON_USED` is the header's +1860), Ester's
   dance, the hiding rolls.
6. Ours, the autosave: 4 seconds after the fight `Autosave: "Auto - Day 1, 00:58 - after a fight"
   (the QUICK page, slot 6)`, `SAVQ06.SAV` 89,621 bytes.
7. Ours, the quick save: F5 on the map: `Quick save: "Quick - Day 1, 00:58" (the QUICK page, slot
   1)`, `SAVQ01.SAV` 89,621 bytes (`qsave.py state` before it: keys 3F00 4300, `save_req` 0).
8. Ours, showing what can be used: Alt held: `flags 08h (Alt held), rings marked 8, names up 4`,
   gold rings under the bodies and "Dead Body" over the four nearest the pointer in the window's
   grab; let go: 0 and 0.
9. Ours, the quick load: F9: the LOAD window on the QUICK page, row 1 `Quick - Day 1, 00:58`
   chosen, row 6 `Auto - Day 1, 00:58 - after a fight`, the QUICK button greyed; Return loaded it
   (the party where it was saved, the dice log attached throughout).
10. M opened the overhead map and M closed it: no "Out of memory in OEOpenGraph" in the dice log or
    DOSBox's log; with the map up the largest free piece of DOS memory read 161,472 bytes.

## Not seen

- The champions' bout (the elf's Chill Arrows cast by `PROBE_ARROW`, the staff sling, the
  bracers) and Greenbright's green: their own logs of 2026-11-18 saw them on their build;
  here only the emulator's tests ran those routines on the merged helper.
- The journal's tab and the quests in a window (the window tests cover them); the journal wrote
  `Journal/journal.jsonl` during this play.
- The picture and the music device (a Single window is always plain), an area change's autosave,
  the pens' hall with Alt held, anything on Windows.

## Learned

- A private game's display, DOSBox name and pid files as the guide's "a second game beside the
  shared one" has them; `:60` and `dbint` here. `pgrep -a dosbox` also lists another agent's
  `dosbox-x`: only `pgrep -x` tells them apart.
- `fountain-user` ends with the bodies beside the fountain: Alt there marks 8 things, four of them
  named "Dead Body".
- Water: the fountain itself (already in ROUTE.md's list); nothing new.
