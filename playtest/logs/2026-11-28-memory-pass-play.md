# Memory pass play check (2026-11-28)

Under test: branch claude/helper-memory-pass. Shattered Lands: DSCLOG's one walk of a creature's items
(WORN_ALL/WORN_ON in PROT_SCAN, ARMOUR_WORN, THORNS_AC, WORN_SCAN). Wake of the Ravager: DSCLOG2's
kit names in its tail (EF_KIT_LINE, KIT_NAME_PTR). Check: the same screens under the old build
(origin/obsidian-edition's DSCLOG.EXE / DSCLOG2.EXE) and the new one.

## Shattered Lands (pens-after-arena)

- New build: buildcheck.py OK; WORN_ALL, WORN_WALK, PROT_SCAN, PROT_ITEM, ARMOUR_WORN, AW_ITEM, WORN_SCAN and
  THORNS_AC the same in memory as the EXE. Inventory (I) of each member, each reached twice (the AC line one
  change behind): Gerakis AC 6, K'ratchek 0, Cermak 6, Cilla 5. Gerakis's arm piece and chest armour to his
  backpack: AC 8.
- Old build (origin's DSCLOG.EXE): the same five screens. Each pair differs in four pixels only, the bag
  icon's dot at (196,189), which cycles its colour by itself (six grabs 0.7 s apart: six colours). So the
  same screens.

## Wake of the Ravager (ravager-after-ambush, ravdice.py attached)

- New build: ravtail.py, the tail as built (tail_paras F55h). Rules words set by the dice log (rules_hi
  0xFF3F: the kits on). ravkits.py show: Terrannus's kit byte 43h (Crusader).
- E (no menu up) opened the Effects screen; each portrait (70,56), (117,56), (70,127), (117,127) clicked
  and the window grabbed. Terrannus: "KIT: CRUSADER", "EXPERT IN LONG SWORD"; the others no kit line.
- Test edits (never saved; the game was stopped after): Terrannus 41h, "KIT: ELEMENTAL" (the short
  name); Gerakis 42h, "KIT: TWIN-BLADE" (the long name, read through the tail).
- Old build (origin's DSCLOG2.EXE; ravtail: tail_paras F7Ah, so the old one ran): the same six
  screens, pixel for pixel (ImageMagick's AE 0 for each pair).
- Not reached in play: the dual class's kit menu (DK_ASK's rows now point into the tail); the new
  test_ravkits.test_kit_names checks KIT_NAME_PTR's names there for every kit.

Result: both helpers' changes show the same screens as before. No saves made.

## Second pass: Shattered Lands' routines in the tail, and the shadow cache (fountain-user)

Under test: ten of DSCLOG's routines moved to its tail behind TAIL_GO (BUILD_DARK, SPANS_FLUSH, DUST_UNION,
MISSILE_RATE, PAGE_SETUP, KIT_PSP_OF, LOOT_KEY, GR_SHADOWED, ADND_NEEDED, TH_CAHULAKS).

- buildcheck.py OK: the tail, its code with it, the same as the EXE (kit_names to tail_end).
- The ambush's speech came on loading; msgbox.sh only says whether a box is up, so eight clicks on the box
  (click.py 160 30, 2.5 s apart) took it away and the fight began (turn 3).
- `KEEP_HP=1 fightout.sh` fought it with the foes' hit points as they were: about five minutes, then YOUR
  PARTY HAS BEEN DEFEATED (no save made). The figures' shadows and the dust were drawn throughout (the moved
  BUILD_DARK, SPANS_FLUSH, DUST_UNION), the dice log's 362 lines had no error, and the attacks and Tab's
  chances read as before.
- scwatch.py (new) on the shadow cache: 21 of its 80 slots filled at the fountain before the fight, all 80
  filled two minutes into the fight, and the filling went round once by five minutes. So a big fight uses the
  whole cache: fewer slots would mean a shadow given up sooner, not room for free. The pass leaves it at 80.
