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

## Not done

- The tangle (a hit that does damage, a save against petrification or the next turn lost).
