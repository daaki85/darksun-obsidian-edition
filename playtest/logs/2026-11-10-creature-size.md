# 2026-11-10: the creature size rule in the game

Under test: DSCLOG's SIZE (commit 605f728), the Loader's `creature_size` switch (on by default).
- A weapon hit on a large target rolls AD&D's large dice (a long sword 1d12...).
- Hold Person / Charm Person on a large target: "too big", unaffected.

## Steps
Build: `buildcheck.py` OK (routines same as the EXE, 134 vectors at their handlers, the tail as
built). Save `fountain-user` (Pehtucl's ambush), all rules on (the default).

1. **Setup** (memory only, never saved): every foe Paralyzed (`foeset.py C eff=34`), and the foes'
   sheets 10, 12, 13, 14, 16 made race 5 (half-giant: large) with `foeset.py C race=5`. The Guards
   (sheet 15, Legcrusher's kind) are half-giants already.
2. **Large dice, a dagger**: Seneca's Bone Hayneedle +1 on the Templar (large):
   `1d3 = [1] +1 weapon (1d3 for 1d4: a large target) +4 STR 18`. Again as a backstab on an Arena
   Guard: `1d3 = [2] ... +2 backstab (the dice 2 x2 = 4)`.
3. **Large dice, a long sword**: Ester's Bone Long Sword on the Templar, two misses then a natural
   20 (the call's third swing: the dice set at its first held): `1d12 = [11] -1 bone +2 specialized
   +1 Battle Dancer (1d12 for 1d8: a large target) +8 STR 20`.
4. **The switch off** (`setmem.py ruleshi=-16384`): Jenna's Bone Long Sword on a large Arena Guard
   rolled the game's `1d8`. Back on (`ruleshi=16384`).
5. **Hold Person on a large foe**: Lex taught Hold Person (`spellsetup.py 0=9 30`), U, LEVEL to page
   3, the icon, a click on a half-giant Guard (freed of its Paralyzed first: a Paralyzed target got
   no save line at all, the game's "fails every saving throw"): `Guard's saving throw vs Hold Person
   from Lex (spell): Guard is too big for Hold Person -> unaffected`, and no Paralyzed on it
   (`effects.py`).
6. **Hold Person on a man-sized foe** (the Arena Guards' sheet set back to race 1, freed), the same
   cast's next target: `d20 = 12 +2 WIS 16 = 14, needs 16 (35% to save) -> failed`, then "Lex gives
   Paralyzed to Arena Guard". The game's way, as before.

## An open finding (not this rule)

Held (Paralyzed) foes lose more HP than the dice log shows: Seneca's hit for 6 took 12 and her next
swing, a miss, took 10 (the Templar 41 -> 29 -> 19); the same on an Arena Guard made man-sized
again (a hit for 8 took 16, a miss 10: 30 -> 4, read from memory before and after); and with the size
rule off Jenna's hits of 10 and 12 killed a 30-HP guard. So it comes with the target being held, not
with the size rule. Not followed further here.

Memory edits only; the game was not saved.
