# 2026-11-26: Wake of the Ravager's item weights

**Under test:** branch `claude/ravager-item-weights`: the Loader's weights for the sequel's 102 item types
(`ravager.RAV_WEIGHTS`, option B of `reports/wake-of-the-ravager-item-weights.md`), written into its copy
`OBJEX2.GFF` (`ALL 4` at +2, and each object's `RDFF` type copy). The original `OBJEX.GFF` is never touched.

**Set-up:** a throwaway copy `/tmp/playtest/ravwt` of `$WORK/rav` (the original folder never written);
`sh ravload.sh ravager-after-ambush /tmp/playtest/ravwt` (the Tyr ambush won, the party in the street); the dice
log with `RAV_NO_SAVES=1` (nothing was saved; every memory edit a test edit); the DOSBox lock held throughout.
The new reader [`ravweights.py`](../ravweights.py) prints each member's items with their type weights, the total,
STR and maximum press; `--str N=S` sets a member's STR (a test edit), `--types` prints all 102 weights. The
control runs used `RAV_SKIP=weights`. The play stayed in Tyr's street and alley: no new area, no water news.

## Steps

**1. The weights in memory.** `ravweights.py --types`: all 102 types as `RAV_WEIGHTS` (the long sword 97 at 40,
the polearm 8 at 70, the brigandine chest 30 at 175). The control's run showed SSI's zeros.

**2. The load check (the probe).** A member's STR set to 1 (maximum press 3 lb), then items moved onto them up to
45 lb: **all taken**, no "TOO HEAVY A LOAD TO CARRY". The program says why: the total (77893h) sums GPL field
59h, which only the item-type class has (class 4, offset 2); an item (class 1) has offset -1 for it, so each item
adds 0. **Shattered Lands' check is the same**: Cilla at STR 1 took Gerakis's long sword in SL too
([SL](img/2026-11-26-sl-str1-sword.png)). The check never refuses in either game; the plan and the docs were
corrected.

**3. Two heavy weapons.** A second long sword (type 97, 40) put in Ar'Anda's left hand with her +1 Longsword in the
right: **"CANNOT USE TWO HEAVY WEAPONS"** ([the screen](img/2026-11-26-rav-weights-two-heavy.png)). The control
(`RAV_SKIP=weights`): "CANNOT USE THIS ITEM" instead ([the screen](img/2026-11-26-rav-weights-control.png)), a
later check met because the swords weigh 0 there.

**4. The party's own pairs.** Gerakis's Dragonsbane (30) and Longsword (40) taken out and put back in his hands:
taken. Ar'Anda's dagger and long sword: taken.

**5. HEAVY.** The long sword's item box shows HEAVY ([the screen](img/2026-11-26-rav-weights-heavy.png)).

**6. Pick pockets.** Ar'Anda on the Caravan Master with `RAV_PICK_ROLL=1`: "Ar'Anda lifts 20 ceramic pieces from
Caravan Master's purse, all there was to take" ([the screen](img/2026-11-26-rav-weights-pick.png)); his Obsidian
Longsword (30) was not lifted, where before the weights the try's log had it lifted
([the pick pockets log](2026-11-26-ravager-pick-pockets.md)).

**7. Backstab with a heavy weapon: not played.** Ar'Anda's weapon set to a polearm (type 8, 70) in memory for the
Tyr thieves fight; the fight went badly and she couldn't hide, so no backstab was tried. Checked from the program
instead: the backstab test (5C978h) reads the type's +2 byte, which holds 70 in memory.

## Results

The weights are in and do what SL's do: two heavy weapons refused, HEAVY shown, long swords out of reach of a
pickpocket, the party's own pairs fine. The load check is dead in both games (it sums a field items don't have), so
no load is ever refused; a real carry limit would be a new rule port (the plan's choice 5). Nothing was saved; all
processes of the play were stopped by pid and the lock released.
