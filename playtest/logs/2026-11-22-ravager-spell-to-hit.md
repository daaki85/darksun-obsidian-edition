# Test log: spells that roll to hit, Wake of the Ravager (2026-11-22)

Under test: DSCLOG2's SITE 16, TH_SITE (SL's spell_hit, "Spells roll to hit", always on): the missile
spells (Acid Arrow, Pebble to Boulder, Magic Stone, Condense, Minute Meteors) and the hostile touch
spells roll the caster's attack against the target's AC; a miss and the spell does nothing.

## Found first

- **The sequel has no to-hit stub.** SL's routine of what a spell does to one target (7A085h) sends five
  missile spells to an always-hit stub (78BA0h, `mov ax,1`) that SL's mod answers 0 on a miss. The
  sequel's routine (8451Ah, stub 475Ah:9Dh) has no such table: it answers 0 (not immune) only through
  `xor ax,ax / pop di` at 84AAFh, and 1 (immune) makes the damage and effect routine (651A0h) skip
  both. So the site is there: a miss answers 1.
- The routine is also called by the computer's look ahead (5F2D2h, the spell negated: `[bp-4]` 1);
  those calls never roll.
- The sequel's pieces: the cast routine 80580h (608h:89h; `[bp+6]` caster, `+8` target, `+0Ah` spell,
  `+0Ch` level), its one call from a weapon's spell on a hit at 5D2CCh (level 6; the cast is not armed
  when the way back's bytes are 5D2D1h's), the attack's to-hit adjustments 628h:66h, STR's and DEX's
  parts 98h:2C0h and 2D9h, the AC 4671h:7Ah (5D520h), the difficulty DS:143Ah, a creature's side +15h
  and THAC0 +16h. Spell numbers: Acid Arrow 18, Pebble to Boulder 53, Magic Stone 121, Condense 169,
  Minute Meteors 33; Chill Touch 3, Shocking Grasp 10, Vampiric Touch 38, Cause Light Wounds 118,
  Cause Disease 149, Cause Serious Wounds 171, Poison 179, Cause Critical Wounds 195.

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 17:10-17:45 UTC)

Ar'anda taught Acid Arrow and Chill Touch, her wizard casts left 3 a level, the party's HP 250
(scratch asetup.py); later sheet 16's (six Draxans) base AC (sheet +21h) -10 and the party's -10, so
the Draxans stop hitting the casters (a caster hit that round has every spell crossed out on USE: "YOU
WERE HIT"). Test edits; DOSBox stopped after, nothing saved.

- **Acid Arrow, a hit**: "Ar'Anda's Acid Arrow at Draxan: attack d20 = 18, needs 10+ (55%) (THAC0 15 (a
  fighter's of the caster's level), +4 DEX; target AC 1) -> HIT"; the Draxan took the 6 and burned on.
- **Acid Arrow against AC -19**: a natural 20 hit ("only a 20 hits"); the next, "d20 = 15 ... -> MISS:
  the spell does nothing, the 2 damage rolled lost". The Draxan's HP stayed 59, and its Acid charges
  stayed those of the earlier arrow (no new effect).
- **Cause Light Wounds (Terrannus), a touch**: "touch attack d20 = 11, only a 20 hits (5%) (THAC0 16, +3
  STR; target AC -19) -> MISS: the spell does nothing, the 7 damage rolled lost"; the Draxan's HP stayed
  43.
- The helper's count 3 after the three rolls; no hang, the fight went on.

## Still to do

- A touch spell's hit; a weapon's spell on a hit (no roll); Magic Stone's several throws.

Water: none new (the same street).
