# 2026-11-24: weapon specialization in Wake of the Ravager

**Under test:** Shattered Lands' weapon specialization (RULE_SPECIALIZE) ported to the sequel, branch
`claude/ravager-specialize`. DSCLOG2's SPEC_ATTACKS (called from OFF_HAND at the attack routine's store of
the attacks a round, 5CEE8h) and SPEC_DAMAGE (site 51, the strength bonus's `add [bp-14h],ax` at 5CF6Dh), with
`RULE_SPECIALIZE` in `ravager.RULES_PORTED`. Copy `ravSP` of `ravG48` (the `fountain-user` party transferred:
48h sheets, the specs at +42h..+44h):

| Member | Classes | Spec | Skill (rule on) |
|---|---|---|---|
| Lex | fighter 3 / preserver 2 | bow | specialized with the bow; its short sword not chosen |
| Seneca | thief 3 / fighter 2 | short sword | specialized |
| Ester | fighter 2 / druid 3 | long sword | specialized |
| Jenna | human ranger 3 | long sword | expertise (a ranger's: the attacks only), and every ranger's bow |

Each run (scratch `sptrial.sh`, `spgo.sh`): ravstart with the Loader (`RAV_LOADER=1`), the four ADDed, a new
game, the dice log (`ravdice.py --numbers`), the opening talk, Computer Control for all four in the Draxans'
ambush. The controls ran with `RAV_RULES_OFF=0x1000` (the rule's bit off in the Loader and DSCLOG2's header:
`rules` 0x6844 against 0x7844). Most runs were given a test edit in memory, never saved (`spsafe.py`): HP 250
and base AC -10 for the four (so the fight lasts), and in some Lex's short sword put in the pack (so the AI
shoots with the bow).

## What was seen

**+1 to hit and +2 damage, rule on** (each damage line matches the HP lost):

```
Ester attacks Draxan#26 with Obsidian Longsword (1d8): d20 = 20 (natural 20), needs 16+ (25%), hits AC -3, target AC 1 -> HIT
    THAC0 19 base, +1 in bonuses, +1 specialized = 17
  Ester hits Draxan#26 for 11: 1d8 = [2] -1 obsidian +2 specialized +8 STR 20
  Draxan now 129/140 HP (-11)
Seneca attacks Draxan#21 with item 261 +1 (1d6+1): d20 = 19, needs 8+ (65%), hits AC -4, target AC 7 -> HIT
    THAC0 19 base, +3 in bonuses, +1 specialized = 15
  Seneca hits Draxan#21 for 10: 1d6 = [3] +1 weapon +2 specialized +4 STR 18
  Draxan now 104/120 HP (-10)
Lex attacks Draxan#26 with Wooden Bow (1d8): d20 = 17, needs 15+ (30%), hits AC -1, target AC 1 -> HIT
    THAC0 18 base, +1 in bonuses, +1 specialized = 16
  Lex hits Draxan#26 for 6: 1d8 = [6] -2 wooden +2 specialized
```

**The control (rule off)**: the same swings with no specialization: Seneca's short sword "THAC0 19 base, +3 in
bonuses = 16" (needs one more), "1d6 = [5] +1 weapon +4 STR 18" for 10; Lex's bow "THAC0 18 base, +1 in
bonuses = 17", "1d8 = [4] -2 wooden" for 2.

**Attacks a round** (`sptally.py`: each member's swings and shots a round, by weapon):

| | Rule on | Control |
|---|---|---|
| Lex, the bow (specialized) | **3 a round** (on5 round 1, on6 rounds 3-5, on7 round 14, on8 rounds 2-4, on9 round 1) | 2 a round (ctl1 rounds 2-7) |
| Jenna, the bow (a ranger's expertise) | 3 a round (on6, on7: 13 rounds; on8) | 2 a round (ctl5 rounds 1-5) |
| Ester, the bow (not chosen, fighter 2) | 2 a round: the bow's own (below 7th level) | 2 a round |
| Seneca, the short sword (specialized) | 2, 1, 2, 1 ... (3/2), the off-hand dagger 1 | the same |
| Lex, the short sword (not chosen) | **1 a round** (on4: 35 rounds; on10) | 2, 1, 2, 1 ...: the game's 3/2 for every warrior (ctl2, ctl3, ctl5) |
| Jenna, the long sword (expertise) | 3, 2, 3, 2 ... (as the game has her), no to-hit or damage bonus | the same |

DSCLOG2's counters at the end of on4 (36 rounds): `spec_hits` 53, `spec_damages` 53 (every specialized swing),
`spec_rates` 90 (Lex's cut swings, the archers' raised rates); in the controls all 0.

## The game quitting: not this rule

Many runs ended with the game quitting 30 s to 2 minutes into the fight, mostly at Ester's turn:
`RAV_STDOUT=1` gave **"Illegal Op (gpl=49)"** and `RAV_MARK=1` wrote ENDED.TXT. It happened with the rule off as
often as with it on: **rule on, 5 of 9 runs quit** (on1, on5, on6, on8, on9; on2, on4, on7, on10 played on to
defeat, victory or the 4.5-minute watch); **controls, 4 of 5** (ctl2, ctl3, ctl5 "Illegal Op (gpl=49)", ctl4 with
no message; ctl1 played on). The quit hunt's sound fix
(logs/2026-11-24-ravager-quit-hunt.md) left 8 runs alive on the 42h-sheet copy; this is the 48h copy
(ravG48), and the cause is not yet looked into. On3's dice log is void: another agent's Loader test attached
its dice log to this DOSBox and wrote its own rules word (0xEA05, the rule off) into DSCLOG2's header.

The container restarted once between ctl3 and on9 (Xvfb and the lock holder gone with it); the runs went on
after Xvfb was started again and the lock taken.

## Not ported

The inventory's and View Character's DAM lines with specialization (SL's PROBE_DAM_LINE and PROBE_MISSILE_LINE
have no likeness in the sequel's code; PROBE_VIEW_DAM a lead at 6CAC9h), the Effects screen's list of specs, a
thri-kreen's chatkcha (OWN_THROWS, a rule of its own), and the kits' parts (a Battle Mage's, Crusader's, Mind
Warrior's expertise, a Justifier's, a Myrmidon's second kind, a Seeker's bow): they wait for the kits.

No new area: no water noted.
