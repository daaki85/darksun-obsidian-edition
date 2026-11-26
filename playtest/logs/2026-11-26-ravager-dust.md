# Test log: dust, and the figures' shadows in a fight, in Wake of the Ravager (2026-11-26)

Under test: DSCLOG2's DUST (`dos/dsclog2.asm`: SL's DUST_TICK, DUST_NUDGE, DUST_UNION, DUST_PASS, PUFF_DRAW and
DUST_BUILD on the figures' shadows' walkers; DUST_FLOOR in the walls' floor pass), the Loader's `_dust_pass`
(`dsloader/ravlog.py`: LIGHT from the palette, then `dust_on`), and the figures' shadows' new counters
(`fig_other` +1978, `fig_missed` +1980). The Loader's way (`RAV_LOADER=1 sh ravstart.sh /tmp/playtest/ravGX`, a new
game on a throwaway copy of the sequel), `ravdice.py` attached. No memory edit; nothing saved.

## Steps

1. Held the shared DOSBox lock (`gx.held`). A new game: the opening talk (3, Return x4), the Draxans' ambush.
2. **The fight** (Computer Control on for all four: C, the USE screen's four lower small icons, Escape; the
   first `ravclick.py` of the run moved nothing until a click in the window took the mouse): four of the party,
   three Draxans and a templar, about 70 s to "Each party member receives 10000 experience points!". Every
   living figure cast its shadow, on the street and in the house the fight went into; the dead none
   (`img/2026-11-26-ravager-shadows-fight.png`). `ravfig.py` after it: 586 floor passes, 2,753 shadows cast,
   1,556 from kept frames, 79 frames kept (the 64 slots went round once), **2 from another frame of the
   picture and 2 none for want of one, both before the fight** (as the first frames came in): 64 slots are
   enough for an eight-figure fight. A bigger fight wasn't in reach. On the dark floors (the street's grey,
   the houses' brown) the shadow is a faint darker streak, as SL's on dark ground.
3. **Dust, first build** (SL's table): `dust_on` 1 and puffs counted (107 after a walk in the house), but none
   seen. `lightchk` (scratch: LIGHT and DAC from DSCLOG2's far block against a grab's colours): the house
   floor's and the yards' browns (56,44,28; 69,56,36; 85,73,52 of 255) had no lighter colour: below
   `dust.is_ground`'s least value 0.4. The street's grey has no hue. No floor in Tyr took dust.
4. Found the dirt with the area map (the game menu's maze icon at game 184,100): the brown ground west of the
   streets. Walked there (`ravgo.py y 1230 x 600`, world 600, 1226: Shadow Square, a stall of jars by it).
5. **The sequel's table**: least value 0.2. The puffs showed, but near white (SL's step of 0.45 toward white
   took the dark browns to pale greys). With a step of 0.2 they go one or two up the dirt's own ramp (230 to
   88, 95 and 229 to 228): soft pale-brown puffs behind Ar'Anda's feet and the townsfolk's, fading
   (`img/2026-11-26-ravager-dust.png`, left).
6. **Control**: the dice log again with `RAV_NO_DUST=1`: `dust_on` 0, the puffs' count stood at 2,006 over the
   same walk, and no puffs (`img/2026-11-26-ravager-dust.png`, right). Back on: the count rose again (2,135)
   and the puffs came back.
7. Memory (`dosmem.py`): DSCLOG2.EXE 55,072 bytes; its upper memory block 54,544 bytes, **100,912 bytes of
   upper memory left** (its largest piece); 74,432 bytes free in the 640 KB; the far block in the HMA.

## Found

- The squares' LIGHT was made from the wrong place in the sequel: `squares.py` read LIGHT's and DAC's offsets as
  one pair at the header's +1926 (SL's +236 and +238 are side by side), but the sequel's +1928 is `square_draws`.
  Now read apart.
- Water (ROUTE.md's water section): Shadow Square's stall at world ~560, 1200 has clay jars by its keeper; not
  looked at.

## Left

- See-through figures: about 14 KB more of upper memory would leave about 84 KB, under the coordinator's 85 KB
  line: asked before committing.
