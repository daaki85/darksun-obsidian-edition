# 2026-11-28: Wake of the Ravager with the mod, recompiled (build/ds2o) against DOSBox

Under test: darksun-recompiled main after PR #12 (ds2o on DSCLOG2 2e4c72b4), the mod's obsidian-edition after #320.
Both games from saves/ravager-after-ambush; DOSBox by ravload.sh, the program by the new ravload_recomp.sh;
both with the Loader's dice log attached (ravdice.py), side by side through /tmp/playtest/both.sh.

- Load: the DOSBox save loads on the program; the street after the ambush the same (3.7% of pixels differ: the
  program's colours are one step off DOSBox's, as known).
- Inventory (I): **the six ability scores blank on the program** (STR: DEX: ... with no numbers); DOSBox shows
  19/21/19/16/19/15. The plain sequel on the program has the same gap. Cause: the game's printf (1403:612C)
  picks its %d, %s... handler through `repne scasb` and `call [di+table]`; the finder never found those ten
  handlers (Shattered Lands' had only %d, found by a run). Fix in tools/find_funcs.py: such a table's routines
  seeded (ten in the sequel, nine more in Shattered Lands).
- (The black box at the DOSBox grab's top left was the program's window over it: windows moved apart.)
- Inventory again after the fix: the scores show, and the whole stats column is the same as DOSBox's (19/21/19/16/19/15,
  THAC0 15, AC -2, the gythka's 1.5x2D4+11).
- Walk to Tyr's thieves (`ravgo.py y 1224`, then `y 1232 x 1839`): both stop at the same places, (1234, 1220) by a
  passer-by in the gap, then the talk at (1825, 1269); 1.6% of pixels differ on the way.
- Fight (answer 2, Space, Computer Control for all four): **the program stalled on a thug's turn**, its log full of
  `[resume] ds2o_fn_9DB61 -> 9BEA:21DA`, the stack 12 bytes deeper each time. 9E07Ah is the two NOPs after DSCLOG2's
  AMMO_OKAY site (INT F5h, its number, two NOPs over `cmp byte es:[bx+14h],1`; the patch goes on to make the
  following jnz a ja). The program's image builder took the patch's extra byte for a cut instruction (its rule from
  PR #12, for FIG_KEEP's far call) and lifted the site as 5 bytes long, so the handler's way back, the NOPs, was
  mid-instruction. Fixed in tools/build_image.py (cut only when the instruction under the INT and number runs past
  the patch); rebuilt, and the fight ran to its end: kills, XP and autosave as in DOSBox (DOSBox's run: 2 rounds,
  3 kills).
- The program's dice log has no attack, turn or summary lines (the known sentinel return address); saves, HP and
  XP lines are there.
- Save and load: each program's autosave after the fight (slot 6) loaded in the other; the inventories identical,
  including HP after the fight (Thy'rokh 57/75, Gerakis 73/165 from DOSBox's save; 96/165 from the program's).
  (The first look had AGE missing, AC 0 and damage +8 on the program: no dice log attached yet. With it, identical.)
- Level up: `ravlevel.py set 0 45707 3 11,12,17 5,6,7` (a test edit, never saved) as the thieves' fight began, in
  both. Both: "Ar'Anda gains a level" at the first kill's XP, then CHOOSE A SPELL, LEVEL 3 on her next turn, the
  same twelve spells (9% of the window's pixels differ: the pointer and the colour step); the first spell picked
  in both set the same bit (byte 3 of the bitset, 29h -> 2Bh); "Ar'Anda is now a 6th level Preserver, max HP 48 -> 49" in
  both.
- Tooling found on the way (kept in RESEARCH-CODE.md): DOSBox's mouse capture steals the program's pointer
  (Ctrl+F10); DOSBox needs focus for clicks; the program's memory is 66Eh paragraphs above DOSBox's.
- Water: no new area (Tyr's street outside Uhubito's, as before).

Result: the program matches DOSBox on a fight, saves both ways, the inventory and a level up, after two fixes in
the program's builder (darksun-recompiled PR). Left: the dice log's caller-address lines on the program.
