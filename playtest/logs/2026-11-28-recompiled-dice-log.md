# 2026-11-28: the dice log on the recompiled program, both games, against DOSBox

Under test: darksun-recompiled with real return addresses at the call sites the helper reads (its
branch claude/dice-log-returns: `tools/lift.py` dice_return_sites), the mod's obsidian-edition after #325.

- Before: the program's dice log had the saves, hit points, XP and kit lines, but no initiative, no
  "X's turn", no attack lines, no level-up hit-point roll and no fight summary. Those come from the
  helper's ring entries, which hold the code after the call to rand() and after the call to rand()'s
  caller; the program's lifted calls pushed FFFFh there, so the Loader read garbage as the calling code.
- **Wake of the Ravager**, `ravload_recomp.sh ravager-after-ambush`, Tyr's thieves (`ravgo.py y 1224`,
  `y 1232 x 1839`), answer 2, Space, `ravlevel.py set 0 45707 3 11,12,17 5,6,7` (a test edit, never saved),
  Computer Control for all four. The program's log now has `Round 1:` with every combatant's
  initiative and tie-breaks, "Thief's turn", "Thief attacks Terrannus with Obsidian Dagger (1d4): d20 = 20 (natural 20),
  needs 17+ ...", the THAC0 lines, damage dice, Gerakis's Wild Fighting, "Ar'Anda's 6th Preserver level: hit points
  d4 = 4 and 1, the better 4 ...", and "Fight over: 3 rounds, 3 kills; the party dealt 249 damage and took 51" with
  each member's tally. DOSBox's log of the same fight (earlier today) has the same kinds of line; the
  rolls differ from run to run in both.
- **Shattered Lands**, `fountain-user` (`PT_TARGET=recomp loadsave.sh`, the speech clicked away, `fightout.sh
  120`) on both: initiative, turns, the mod's "Chosen with Tab: ..." line, attacks with THAC0, damage,
  "Fight over: 3 rounds, 6 kills" and the tallies on the program; DOSBox's run the same kinds (12 passes
  to the program's 8, different rolls).
- On the way, the helper took paths it had never taken on the program (now that it sees real addresses,
  as in DOSBox): misses at C1570h and BEEC5h (SL, the Tab key's routine on Ester's turn: fightout stalled
  there until a relift took them in) and B1E94h (the sequel, a level up's message in a fight). A
  convergence round on both builds keeps them.
- Differences left: the program's log has no opening speech (its dice log attaches after the load, the
  guide's rule), and "Memory: upper memory had no room for the game's overlay buffer" shows on the
  program only (its overlays fill the upper memory; the program's own issue, noted in its STATUS).
- Tooling: `start_recomp.sh` now passes `--build` (the program found no build/ds1o when started from the
  game folder); the program's window, like DOSBox's, takes clicks only when focused (`xdotool windowfocus`).
- Water: no new area.
