# 2026-11-25: Tab's follow-ups and the small ports joined in one build of the sequel's helper

**Under test:** branch `claude/ravager-join-tab-small` (PR #171), the join of
[Tab's follow-ups](2026-11-25-ravager-tab-followups.md) (PAN, the foes' sides 7-11, a gladiator's armour in
the chance to hit) and [the small ports](2026-11-25-ravager-small-ports.md) (site 78 `rg_two`, the charges'
labels), each played alone before. DSCLOG2.EXE rebuilt from the joined source: **41744 bytes**. A smoke play:
nothing new built.

The build in place: `ravstart.sh` from this worktree's `playtest/` mounts its `obsidian-edition/dos`;
DSCLOG2's segment in memory (CA1Bh, the INT F5h vector's, header `DSCLOGR1`) compared with the load images over
its first 24 KB: the joined file **23846** bytes alike, the small ports' 23838, Tab's follow-ups' 21647, the
earlier join's 21647. The dice log set rules 0xFB45, rules_hi 0xFF3F (as in the earlier runs).

One run: [the small ports' run script](files/2026-11-25-ravager-small-ports-run.sh) from this worktree (tag J,
`RAV_PREDICT=1`): `ravSM`, a fresh copy of `ravK`, the transferred party, a new game, HP 250 for the four (a
test edit, never saved; the copy thrown away), `ravdice.py --numbers`, the Draxans' ambush in Tyr. Test edits
by hand: Jenna's leather (item 44) and the type-1 armour in her pack (item 53) traded slot bytes (+13h), as in
the small-ports log; Armor taught to Lex (`ravknow.py 0`). About 10 minutes of play.

## What was seen

- **Memory** (`dosmem.py`, in the fight): DSCLOG2 **41216 bytes** in upper memory (MCB CA0Ah), **114240
  free** after it in one piece (MCB D41Bh, the chain's Z: whole). The earlier join had 41008 and 114448: the
  file's 208 bytes more. DOS memory free after the game 72 KB (73408 bytes).
- **Tab list**: `Tab list: 4: Draxan#21 (side 7), Draxan#23 (side 7), Draxan#26 (side 7), Draxan#27 (side 7)`.
  Jenna's turn, Tab x5: `0x1b 0x1a 0x15 0x17 0x1b`, the four only. At 0x1a (#26 in the west doorway, at the
  view's top left edge) the view moved from 1016,1368 to 952,1312 (`pan_moves=1`), the ring under him
  ([picture](img/2026-11-25-ravager-tabsmall-pan.png)).
- **A ranger's two weapons in armour not light** (Jenna, DEX 20, the armour swapped before Tab): the line
  `Chosen with Tab: Draxan (140 HP), Obsidian Longsword needs 17+ (20%); Obsidian Longsword needs 16+ (25%); Bow
  needs 17+ (20%)` (`RAV_PREDICT`: the off hand's "two weapons, off hand at DEX 20, -1"). Enter on #27:
  `needs 17+` (THAC0 18, +0 in bonuses), then `needs 16+` twice (+1): **the line and the game match**, the
  small-ports log's run B row 2 to the number. `ravkits.py count`: `two_count=2 off_count=1 rg_heavy=2`.
  Counts after: `tab_seq=5 attack_seq=1 attack_clicks=1`.
- **The charges' labels**: Lex cast Armor on Jenna from USE (`Armor has 10 charges (caster level 2 ... 8d1)`);
  the Draxans' hits used five: `9 left` ... `5 left`. A grab every 0.2 s caught **"Armor: 5 left"** over her
  ([picture](img/2026-11-25-ravager-tabsmall-charge.png)); the others not caught (two in one Draxan turn, or
  between grabs: as the small-ports log says, a label shows only once the map is drawn again).
- **No Illegal Op, no quit**: `STDOUT.TXT` empty, the watchdog quiet (no STUCK or GONE from 11:30 to 11:39),
  DOSBox up to the end, stopped by pid.

No new area (Tyr's ambush street): no water.

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-tabsmall-pan.png`,
`-tabsmall-charge.png`.
