# 2026-11-25: the shops and Tab joined in one build of the sequel's helper

**Under test:** branch `claude/ravager-shops-tab` (PR #168), the join of
[the shops and the scroll's messages](2026-11-25-ravager-shops-scrolls.md) (DSCLOG2's sites 54-59) and
[choosing an enemy with Tab](2026-11-25-ravager-tab-target.md) (site 77, TARGETING and RINGS), each played
alone before. DSCLOG2.EXE rebuilt from the joined source: **41536 bytes**. A smoke play: nothing new built.

The build in place: `rav.conf` mounts the joined worktree's `obsidian-edition/dos`; DSCLOG2's segment in
memory (CA1Bh, the INT F5h vector's, header `DSCLOGR1`) compared with the three builds' load images over its
first 24 KB: the joined file 23848 bytes alike (the rest the variables), the Tab branch's 9246 (its code at
other offsets). The dice log set rules 0xFB45, rules_hi 0xFF3F (as in both earlier runs).

Two runs, each its own fresh copy of `ravK`:
- **Tab** (`ravJT`): [the Tab log's run script](files/2026-11-25-ravager-tab-target-run.sh) with this
  worktree's `playtest/` and the copy's name changed: the transferred party, a new game, HP 250 for the four
  (a test edit, never saved), `ravdice.py --numbers`, the Draxans' ambush in Tyr.
- **The shop and a scroll** (`ravJS`): `ravload.sh ravager-after-ambush`, `ravdice.py`, the arrow keys to
  Notaku's stall ([a walk helper](files/2026-11-25-ravager-shops-tab-join-walk.py): Up to y 1224, Left to
  x 296, Up to y 936, about 80 presses), the leader's CHA 22 and a scroll (`ravshop.py`: test edits, never
  saved).

## What was seen

- **Memory** (`dosmem.py`, in the fight): DSCLOG2 **41008 bytes** in upper memory (MCB CA0Ah), **114448
  free** after it in one piece (MCB D40Eh, the chain's Z: whole). The Tab branch had 40352 and 115104: the
  shops' 656 bytes on top. DOS memory free after the game 72 KB (73408 bytes).
- **Tab** (`ravtab.py`, the dice log): Seneca's turn: Tab `hit_target=0x1a`, the red ring under the Draxan
  in the west doorway ([picture](img/2026-11-25-ravager-join-tab-ring.png)); the line `Chosen with Tab:
  Draxan (140 HP), Bone item 291 +1 needs 14+ (35%); Metal item 261 +1 needs 13+ (40%); Sling needs 16+
  (25%)`. Enter: she walked up and attacked Draxan#26: `needs 15+ (30%)` with the Bone weapon, `needs 14+
  (35%)` (x2) with item 261: **one off**, the walk-up case the Tab log left open, the same numbers as there.
  Ester's turn: Tab to the same Draxan (132 HP): `Obsidian Longsword needs 15+ (30%), from behind 9+
  (60%)`; Enter: `Ester attacks Draxan#26 with Obsidian Longsword (1d8): d20 = 6 / 9 / 15, needs 15+ (30%)`:
  **matches**. Counts after: `tab_seq=2 attack_clicks=2 hit_answers=50 ring_draws=33`.
- **The shop at CHA 22** (Thy'rokh, the leader): Notaku's list, MORE twice: **225, 187, 131, 33750, 11250,
  18750** ([picture](img/2026-11-25-ravager-join-shop.png)), the shops log's numbers to the coin (the game's
  300, 250, 175, 45000, 15000, 25000 less 25%); `cha_prices=17`, the inventory's CHR 22.
- **The scroll's message**: item 1 (Ar'Anda's left hand) made a scroll of spell 1, its icon clicked:
  **YOU LEARN THE SPELL** on screen for its five seconds ([picture](img/2026-11-25-ravager-join-learn.png));
  the dice log `Ar'Anda reads the scroll of Burning Hands: d100 = 30, needs 85 or less (INT 18) -> learnt`;
  `msg_windows=1 msg_waits=1 learnt_tries=1`, spell 1 in her known list, the scroll used up.
- **No Illegal Op, no quit**: both copies' `STDOUT.TXT` empty, the watchdog quiet, DOSBox up to the end
  of each run (about 12 minutes of play in all).

No new area (Tyr's street and Shadow Square: their water is in the shops log).

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-join-tab-ring.png`, `-join-shop.png`,
`-join-learn.png`.
