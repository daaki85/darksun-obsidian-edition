# Wake of the Ravager: the new wizard spells, part 1 (2026-11-26)

Branch `claude/ravager-new-spells`. The six new wizard spells (Cat's Grace, Erdlu Claw, Fogbolt, Reflected
Image, Spook, Friends) in the sequel: their numbers, records, icons and texts. Their casting is not done.

## Their numbers

- The sequel's RESOURCE.GFF has DATA 0-319, all in use: wizard 0-114 (Armor to Wall of Ash), priest
  115-234, psionic 235-268, monsters' powers 269-319 (MONS269...). No six free wizard numbers below 120:
  115-119 are Bless, Curse, Cure Light Wounds, Cause Light Wounds and Entangle; only their five known bits
  are unused.
- So the six are **320-325** (past the table, as SL's 196-201 past its 196): DATA 320-325, ICON 21320-21325,
  SPIN 321-326. The game holds ICON 21000-21268 and SPIN 1-269, so none of those numbers is taken.
- Who knows them: the sheet's bits SL already keeps (+3Fh 08h-80h, +3Dh 80h), which the party transfer
  carries. Nothing new is needed on the sheet, and +45h-47h are not used.

## The copy

- `dsloader/ravspells.py` builds the records from the sequel's own Strength (23), Enlarge (5), Charm Person (2)
  and Mirror Image (19) records with DSCLOG's NS_PATCHES. The landing sounds come from Haste's, Shocking
  Grasp's and Fog Cloud's, Fogbolt's cast sound from Fog Cloud's and its flight from Magic Missile's. Spook's
  effect is the sequel's Afraid (35).
- Icons: SL's drawn ones (icons.py), each colour the nearest of those the sequel's own spell icons use, in the
  PLNR form. Without SL, the template's own icon.
- With `"new_spells": false` they are left out.

## Played

- `RAV_LOADER=1 sh ravstart.sh /tmp/playtest/ravSP` (a throwaway copy): the copy with DATA 320-325 starts
  through the Loader to Tyr ("Hurry! You must come with me to the Veiled Alliance!"), the same as before.
  RESOURC2.GFF holds the six records, icons and texts.
- Not played: learning and casting. The game never asks for a spell past 319 until DSCLOG2 answers for these.

## Not done (DSCLOG2, sites 140-149)

- The known test (6260Ah) and teaching (scroll, level up, creation) on the sheet bits.
- The wizard-spell compares (`cmp ..,73h` about 15 sites, `0EBh` about 30; SL's NS_CMP), the spell levels and
  the slots.
- The effects: the sequel has one empty effect record (88), and Erdlu Claw, Fogbolt, Cat's Grace and Friends
  each need one.
- Each spell's rule (SL's PROBE_GRACE_*, NS_CLAW, NS_FIST, NS_HIT, IMAGE_SPELL/IMAGE_BLOW at 50, Spook's save)
  and the dice log's names.
