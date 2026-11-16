# In-game look at the outfit prototype (2026-11-16)

**Under test:** the class-outfit pictures from `prototypes/outfits.py` (with the corrections by
hand), seen in the game itself for the first time: one figure per outfit.

**How:** the pictures are put into the Loader's copy of SEGOBJEX.GFF by `playtest/outfitgame.py`
after the Loader writes it and before DOSBox opens it (`PT_AFTER_PREPARE` in `start.sh`), with no
Loader attached (`PT_NO_LOADER`), so nothing dresses the figures again. Save: `pens-after-arena`
(the ready-made party in the slave pens).

## Steps
1. `PT_NO_LOADER=1 PT_AFTER_PREPARE="python3 outfitgame.py 300=Mage,305=Thief,307=Thief,308=Priest" sh loadsave.sh pens-after-arena`.
   The save loaded (region 29h, leader 1672,344), but **the party was drawn as the game draws it**:
   the pictures had gone into each party object's own pair (2450 and on, which the copy's OJFF
   records name), and the game with no Loader attached did not draw those. The copy did hold the
   dressed pictures (decoded back: the mage's blues in 2450, the priest's reds in 2466).
2. `outfitgame.py` changed to replace the game's own pictures of each figure too (the human man's
   2095/2096, the elf woman's 2059/2060, the half-giant man's 2072/2073). Loaded again: **the
   outfits show**. The party: a human man (Mage), an elf woman (Thief), a half-giant man (Priest),
   a thri-kreen (nothing to wear). Kurzak, a half-giant with a picture of his own, is unchanged.
3. Walked the party down, left and up-right (clicks at 150,185; 60,150; 200,60), grabbing the
   window as it went. Seen: front, side (both ways: the game mirrors it) and the three-quarter
   stop. No picture was cut off, misplaced or flickering; the bigger pictures (8 pixels of room
   each side) draw where the game's own do.
4. Loaded again with `all=Warrior`: all three as warriors, standing and after a walk down.
5. A click on the wall (165,40) only shows the no-walk pointer: nothing moves.

## What was seen

- **At the game's size the outfits are told apart at once by their mass of colour and their
  outline**: the priest's red robe, the mage's blue cloak over a brown tunic, the thief's green
  hood and cloak. Single pixels (most of what the corrections by hand change) cannot be made out.
- **Priest** (half-giant man): the best. One solid robe from the front and the side.
- **Mage** (human man): reads as a blue-cloaked figure; from the front the brown tunic with the
  cloak behind is clear. From the side the cloak is a dark blue mass with a patch of the leggings'
  green in it.
- **Thief** (elf woman): the hood and cloak are clear from every side seen; the face under the
  hood is two or three pixels and still reads as a face.
- **Warrior** (all three): readable as dark leather on the half-giant and the elf woman. On the
  human man it is close to his own picture (a black harness then, dark brown now): the weakest.

## Not seen

- Fighting frames (attacks, the bow, hit, dead): no fight was started.
- The back view head on (the party stopped three-quarters on).
- The other ten figures.
- The outfits with the Loader attached: it would dress the figures again from the game's own
  pictures, so this look ran without it. No dice log, and none of the Loader's running features.

## Water

No new area: the slave pens' entry hall, as in earlier logs.
