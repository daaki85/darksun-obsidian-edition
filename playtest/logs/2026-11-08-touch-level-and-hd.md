# Test log 2026-11-08: touch-spell caster level, and hit dice

## Q1: touch spells' caster level (pens-after-arena, out of a fight, DOSBox)
Party: Gerakis, K'ratchek (fighter/druid fire/psionicist), Cermak, Cilla (preserver/druid earth/thief).
`spellsetup.py 3=9 83 87 117 122 108 133 92` (Cilla's druid level 9), U, Cilla (108,108), CLERIC
page (150,171), LEVEL 4, icon, then a portrait. effects.py right after each cast:
- Free Action (117, druid spheres: in Cilla's) on Gerakis, druid 9: `Free Action (90 rounds)` 5400 s = 9 x 600.
- Protection from Lightning (122, air: not Cilla's sphere) on Gerakis, druid 9: 600 s = 1 x 600 (level 0, taken as 1).
- `spellsetup.py 3=1 117`, Free Action on Cermak, druid 1: 600 s.
So a touch spell takes the caster level; the 0 comes from the sphere (5E25Ch gives 0 when no class of
the caster has the spell's sphere): spellsetup.py taught spells outside the caster's spheres.
- An aimed summon (Conjure Lesser Air Elemental) out of a fight: no cast (red no-sign at the spot).

### Aimed control (fountain-user, clicked into the ambush; `spellsetup.py 2=9 hp=200 ...`, `hp.py 150`)
Ester = fighter / Cleric (fire) 9 in memory.
- Conjure Lesser Fire Elemental (aimed at floor): the elemental came; no duration line, no effect (summons keep no effect timer).
- Hold Person (86, all spheres) aimed at the Guard: `Paralyzed (18 rounds)`, 1080 s = 2 x 9 x 60: level 9.
- Insect Plague's icon crossed out (indoors?); the next turn the level-3 page was all crossed: no aimed
  out-of-sphere cast in DOSBox; the code shows the same level routine for both (below).

## Q1 in the code (DSUN.EXE file offsets)
- A touch spell's portrait click on the USE screen: 88616h (button id - 2C24h = the member), level
  from 5F8h:61h (81B16h), then 598h:89h (772A5h) with [bp+1Ah] = 0, which for a spell below 8Ah sends
  it to 500h:4Dh = 5DFA5h; that drops the level passed and works its own: 5E25Ch(caster, spell).
  The aimed path (map click) goes the same way. 5DFA5h -> 598h:7Fh (750E0h) -> 7511Bh -> 7552Dh
  (5B8h:25h = 78C19h, level [bp+1Ch]) -> 78D13h -> 76CB3h. The dice log reads 76CB3h's own argument.
- 5E25Ch: the best class level whose class mask (2F8h:118h + 4 x class) shares a sphere bit with the
  spell's (408h:19Dh + 7 x spell), **ANDed with 1FFFFCh** (bits 0-1 are "a preserver", "any priest").
  None: 0. 81B16h (the spell levels a caster may cast, Dispel's weighing) has no such mask, so a fire
  cleric may cast an earth spell taught in memory, at level 0.
- Class masks (live): clerics air/earth/fire/water 6/A/12/22, druids 42/82/102/202, preserver 1001,
  rangers 4002/8002/10002/20002. Blood Flow 120222 (water), Ironskin 10808A (earth), Free Action 1003C2
  (druids), Cause Fear 13C3FE (all).
- The Loader's `effect_caster_level` models 81B16h (no mask): it says 9 where the cast took 0.

## Q2: hit dice
- 508h:2Ah = 5E85Fh: the sheet (47h bytes at DS:1661h): race (+18h) 1 (human): +24h (the first
  class's level, even after a dual-class change); else the highest +24h..+26h whose class (+21h..)
  is set. A monster with no class (elementals, slaads, mastyrials, Sand Howler, Rampager, Styr, Fire
  Eel, Dune Reaper, Strine, Slig, Wyvern, Xorn, Otyugh, Bulette...) gets **0**, though its HD is at +24h.
- In memory (fountain-user): Lsr Fire Elem (summoned) race 14, classes 0, levels [4,0,0] -> 0; Templar
  human class 19 level 4 / 8; Arena Guard fighter 3; Guard half-giant gladiator 3; Zombie race 9 fighter 2.
- SEGOBJEX.GFF RDFF sheets: undead all race 9 with class 9 or 12 (Zombie 2, Shadow 6 / 3, Skull Elder 4,
  Aposs 6...): 508h:2Ah is their HD. Mountain Stalker fighter 8 (manual 10 HD), Mastyrial 12 (class 0).
- Level tests the game makes on a target (508h:2Ah): Cloudkill can't be saved at level <= 6 (79F95h);
  Scare always saved at 6+ (79FA4h); Dismissal's save + (target level - caster level) (79F83h);
  psionic Domination's cost by level (5CBA8h); 7A7ACh, 7AA32h (thri-kreen 7+), 87482h.
