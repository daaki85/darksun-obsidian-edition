# Turn Undead out of a fight: the target's name (2026-11-09)

Under test: DSCLOG's TURN_SITE record now carries the priest's and the undead's creatures (+16h, +18h),
so the dice log names them even though the turning starts a fight, which renumbers the combatants
before the Loader reads the record (they read "?"). Build: commit 039ea02 (the "never save" fix in
too); `buildcheck.py` OK, every vector at its handler.

Steps:
1. `loadsave.sh pens-after-scar`; walkto (1816,408), (1704,408), (1592,440); `route.py 1592 584`;
   `route.py 1560 860` (stopped at 1576,904 beside Kalzith: "NO CLEAR SQUARE", close enough).
2. `turnsetup.py 2 4 220=1`: Cermak a 4th-level cleric in his second class place, Kalzith
   (combatant 220 out of the fight, creature 33, sheet 12) undead of 1 HD. Memory only, not saved.
3. `panel.sh hide`, `scroll.py 0 -80`; U, Cermak's portrait (66,108), the TURN UNDEAD button
   (158,146, a slow press: the name shows in the bottom bar on hover), then a click on Kalzith's
   figure (184,66) with the aiming box.

Seen in the dice log:

    Cermak turns Kalzith: d20 = 4, needs 13+ (priest level 0 vs 1 HD, AD&D's table) -> not turned: can't try again on it this fight
    Round 1: Cilla 31, Zombie 27, Kalzith 27, K'ratchek 25, Gerakis 25, Arena Guard 22, Cermak 22

Both names right; the fight that the turning started had renumbered Kalzith (220 before). Fixed.

Notes:
- "priest level 0": Cermak is human (race 1) though party.py lists two classes for him: a human who
  dual-classed shows both. A human's added class in place 2 counts 0 (the guide's rule). Pick the
  priest by race (sheet +18h), not by the number of classes.
- The natural-20 change (a natural 20 no longer saves against "can't save") was in this build but
  not provoked in play (a natural 20 on demand needs the seed); its two sites are covered by the
  Unicorn tests in tests/test_manual_group3.py (test_save_natural).
