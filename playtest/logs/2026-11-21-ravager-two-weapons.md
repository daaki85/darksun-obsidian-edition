# Test log: two weapons, Wake of the Ravager (2026-11-21)

Under test: SL's two-weapon rule (RULE_TWO_WEAPONS, always on: game.RULES_ALWAYS) as DSCLOG2's
PROBE_TWO (INT E1h at 5DE7Ch, SL's 59634h) and OFF_HAND (INT E2h at 5CEE8h, SL's PROBE_ATTACKS site
58892h). The sequel's two-weapon routine (5DE34h, called from the attack at 5C78Ch) is SL's byte for
byte; its attacks a round are stored by "mov ah,0 / mov [bp-0Ah],ax" (SL's "cbw / mov [bp-8],ax").

## The run

The Draxans' ambush (a new game to Tyr, the talk, the party walked up the street), the dice log with
the ported rules (`rdice.py 0x80008005`), the game's Computer Control on for all four (in a fight: C
for USE, then **the lower small icon left of each character box**: game 47,53 / 98,53 / 47,113 /
98,113; the bar says COMPUTER CONTROL IS ON), Escape, and the fight left to the game. About 06:40 UTC.

- **First try, nothing counted**: the helper's walk of a creature's item lists stopped at thing 400
  (copied from HELD's combatant check). The party's lists are things 201h-207h (creature +8, +0Ah;
  +0Ch none): the walk now stops only at 9999. A temporary INT at 5DE3Ah showed the game's count of
  weapons ready ([BP+6]) 2 for Ar'anda and Gerakis, 1 for the others, so the routine was reached.
- **Fixed**: Gerakis (gladiator, Dragonsbane +4 in the right hand, Longsword +1 in the left) attacked
  twice a round with Dragonsbane at +8 in bonuses (+10 before: -2) and once with the Longsword at +3
  (+7 before: -4). The game's HIT and miss agreed with the d20 against the dice log's "needs" each
  time. The off hand's cut (OFF_HAND reads the item's slot itself, so it worked in the first try
  too): a 7th-level gladiator has 3 halves a round in each hand by the game; the Longsword now gets 2
  (one a round), the Dragonsbane keeps its 3.
- The helper's counters: two_count 4, off_count 2 after the first party round.

## Notes

- The dice log's attach writes its own rules (0) to the helper's header: a second dice log attached
  for a look turns the rules off. Set them again after attaching (`log.set_rules`).
- `ravfight.py fight` didn't get Ar'anda or Gerakis to strike (they walked about); Computer Control
  does.
- SL's ranger part (RG_TWO: no two-weapon ease in heavy armour) and the kits' and cahulaks' parts are
  not ported: a ranger keeps the game's no penalty in any armour.
- No water: the street in Tyr only.
