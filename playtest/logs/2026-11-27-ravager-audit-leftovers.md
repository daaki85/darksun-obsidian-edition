# 2026-11-27: PR #232's leftovers in Wake of the Ravager (Berserk's end, ability items, the Effects screen's charges, the dice log's kills)

**Under test:** branch `claude/ravager-audit-leftovers` (on #232): DSCLOG2's BERSERK_ADD and BERSERK_END (sites 245, 246);
the dice log's kills (RavDiceLog._kills_pass) and a killed creature's last fall (hp_changes).

**Set-up:** `ravAL`, a throwaway copy of `$WORK/rav` (game.gog hard-linked, the rest copied, the roster and DARKSAVE
from __support/save, no saves); the DOSBox lock held by this session's holder; Xvfb started by hand.

## Run 1 (before the dice log's fix: the bug seen; the ability items)

1. `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh /tmp/playtest/ravAL`; the dice log with a
   scratch trace of the tracker (never called: RavDiceLog's pass has no tracker step). `ravaudit.py`: berserk_sides 0,
   berserk_ends 0 (the build's words, not 9090h).
2. A new game (a click, S, the dragon: Escape, Return twice; 3, Return x4): the ambush. RESOURC2.GFF's ten spells of
   effect 20 (Controlled) made 7 (Berserk) for the test (Charm Person, Domination...). Computer Control (C, the four
   lower icons): COMPUTER CONTROL IS ON.
3. The fight: nobody cast a charm. **The summary said "Fight over: 4 rounds, 0 kills"** with three Draxans dead; the
   last blow on Draxan#23 (6 HP, Gerakis's 21) had no HP line. A scratch watch of the combatants: **a killed creature
   leaves the fight's table** (Draxan#21, #26 gone from it before any look saw them below 1 HP).
4. **Ability items** (test edits, never saved): Gerakis's leg armour (item 11) made power 144h (WIS), 2: in the pack
   (slot 21) and Armor cast on him: WIS 15. Put back in its slot by the inventory (the ready routine 77C5Ah
   recomputes for powers 140h-147h): **WIS 15 -> 17**. Taken off to the pack: still 17 (the unready's recompute,
   77D07h, runs while the item still counts); another item's unready recomputed: **WIS back to 15** with item 11 in
   the pack. The sequel's ability routine (0628h:0039h, 8527Bh) counts only items whose top place is 10h (worn: the
   pack's is 4, as the AC routine skips): SL's bug not shared.

## Run 2 (the fixes in: the kills, Berserk; with #232's rest, the arrows' fixes and #235 merged)

1. ravAL's roster, DARKSAVE and DARKRUN put back from `__support/save`; the same start. DSUNLOG2.EXE has `cdf5f5`
   at 822A1h and `cdf5f6` at 827D6h; `ravaudit.py`: berserk_sides 0, berserk_ends 0, **hdr_len 2128** (the header's
   end). The real `ravdice.py` (no scratch trace), `RAV_NO_SAVES=1`: quick saves and autosaves off.
2. RESOURC2.GFF's effect-20 spells and Armor (spell 0) made Berserk (7) after the start. A new game, the ambush,
   Computer Control for all four.
3. **The kills**: "Draxan is killed" after each death, and **"Fight over: 4 rounds, 4 kills"** (run 1: 0 kills).
   Each last blow had its HP line (`Draxan now 0/70 HP (-25)`, `Draxan now 0/60 HP (-25)`). A "Preserver is
   killed" line came at the game's start, before the fight (the story's preserver), not in the fight's tally.
4. **Berserk**: Thy'rokh's Charm Mammal (a test Berserk) on Draxan#21 (a natural 1): "Thy'rokh#2 gives Berserk
   to Draxan#21". Its record's +9 held **7, the Draxan's own side** (without the fix the game leaves the byte as
   the record had it); **berserk_sides 1**. Gerakis killed it on his turn: "Berserk ends on Draxan#21",
   **berserk_ends 1** (the end sent to the case 120Dh; the game went on).
5. After the fight, Armor (now Berserk) from Ar'Anda's USE on Gerakis: the record's +9 **0**, his side;
   berserk_sides 2. A test edit (never saved: no saves on) set his side to 1 and the effect's charges to 1;
   standing and some minutes' walking didn't run the effect down, so the end with a changed side was **not seen**.
6. Ended: DOSBox, the dice log, the watcher and the guard killed by pid; ravAL's game never saved.

**Water**: no new area (the Draxans' ambush in Tyr's street).

**Left**: a living creature's Berserk ending after its side changed (the unit tests run the end routine's case
on a CPU emulator: the side back from +9).
