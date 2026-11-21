# Test log: the cahulaks' two heads, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's CAHULAKS (Weapon traits, always on: RULE_HI_CAHULAKS): the off head's one more
attack a round (CAH_MORE in OFF_HAND), the main head's -2 (PROBE_TWO's CAH_ADJUST, the routine let in
by CAH_TWO, INT E5h at 5DE6Fh) and the off head's -4 on the round's last swing (CAH_SWING, INT E6h at
5D052h).

## Found first

- The sequel's weapons, from OBJEX.GFF's items (type +0Ah, name +14h; the names in RESOURCE.GFF's list
  from "Tombstone"): Cahulaks 24, Double Spear 39, Gythka 52, Polearm 80, Sling 93, Staff Sling 98,
  Trikal 100. The Cahulaks' type: 1d6, two-handed (+0Bh 40h), melee.
- The attack's frame against SL's: the round's swings [BP-0Ah] (SL's [BP-8]), the swing [BP-16h] (SL's
  [BP-14h]), the item [BP+12h], its type [BP+14h], the range [BP+16h], the attacker [BP+18h], what the
  d20 must reach [BP+0Ah] less [BP+0Ch] (the hit test after 5D088h). The two-weapon routine's "two
  weapons ready?" bytes are SL's own (`837e06017e11`); its "none" way 5DE86h.
- The tangle's place (SL's CAH_HIT, "mov byte [bp-15h],0"): the sequel's "mov byte [bp-19h],0" at
  5D1FEh, after "or si,si / jl" (the item there).

## In the game (ravhold.sh, RAV_LOADER=1, about 09:45 UTC)

Gerakis's right-hand weapon made the Cahulaks in memory (type 24: its name stays the old item's, "Bone
Dragonsbane +4"), the four given 250 HP (test edits; DOSBox stopped after, nothing saved), Computer
Control for all four, the dice log with 0xA0008205.

- Each round: three swings with the cahulaks (the game's two a round, one more), the first two at
  "+8 in bonuses" (+4 weapon, +6 STR 24, -2 main head) and the last at **+6** (-4 off head); then the
  Longsword in the other hand, +3 (its own -4 off hand: a half-giant may hold both). Three rounds alike.
  The helper's count of off-head swings went to 3.
- The first try with `ravfight.py attack` never struck (the street's bunched figures, as in the held
  test): the party was beaten. Computer Control fights properly.
- The dice log names no head yet (its THAC0 line falls back to "+8 in bonuses").
- No water: the street in Tyr only.

## The tangle (about 10:20 UTC)

Under test: DSCLOG2's CAH_HIT (INT E7h at 5D1FEh, where a weapon's hit has done damage) and CAH_MOVE (INT
E8h at 5B838h, where a creature's turn starts: its movement stored, SL's PROBE_MOVE site), with
SWEPT_NOW, GAME_DIE and MN_REC ported from DSCLOG. The same set-up as above (ravhold.sh, Gerakis's
Cahulaks, 250 HP each, Computer Control).

- Found first: the sequel's initiative is SL's 3 bytes on, (load + 3C4Fh):0DCh (4 bytes a creature,
  -1 once it has acted) and the turn's movement +22Eh (SL's +0D9h, +22Bh); the turn's start at 5B838h
  ("mov es:[bx+22Eh],ax", DI the combatant, BX the creature x 2), then Slow's and Haste's changes.
  The save against petrification is the sheet's +33h.
- Round 1, Gerakis last: "Gerakis's cahulaks tangle Draxan? Save against petrification: d20 = 2, needs
  11+ -> tangled: loses its next turn"; another hit, "d20 = 20 ... -> saved". Round 2: four Draxans in
  the initiative, three acted (5 blows: 2 + 2 + 1); the helper's count of turns taken went to 1.
  Round 2's second tangle (d20 2 against 9) went on a Draxan killed before its turn. The fight was won
  ("Each party member receives 10000 experience points"); DOSBox stopped, nothing saved.
- A Draxan struck another Draxan in round 2 (48/60 HP after), with no Hold Person or Charm in the
  log; the only odd line before it was an unnamed "Dice: 1d20 = [1] = 1" in round 1, Terrannus's
  turn. Perhaps a charm-like power the dice log doesn't name: a lead for the held-target question
  (logs/2026-11-21-ravager-held.md).
- Not ported: a large monster can't be tangled in SL (cahulaks.py's list, the Enlarged): only
  half-giants are spared here until the sequel's creature sizes are done.
