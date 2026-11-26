# The elf champion's Chill Arrows cast Chill Touch (2026-11-18)

Build: branch `claude/champion-chill-arrows`, fc92a58 (DSCLOG: anyone not in the party casts its
spell arrows' spell; ARCHER_LEVEL: a non-party archer's highest level for the plus and the cast).
DOSBox, the Loader's patched game, the dice log. Save: `pens-after-scar`.

1. `arenatrip.sh` (toalarm.sh: the save, Cilla's thief level raised to 12 in memory, never saved;
   two rests in the fire room, Kurzak's call, toarena.sh, Y): the arena at (488, 200). Window
   320x240. `buildcheck.py probe_arrow arrow_plus_now archer_level arrow_level arrow_hit`: all the
   same as the EXE (70,400 bytes), 129 vectors at their handlers, OK.
2. `scroll.py 0 -100` twice, a click on the bone wall's gap (176, 110): the party at (504, 360);
   `viewto.py 504 360`, clicks at (144, 145): the platform, the Announcer's champions' speech,
   fight_on 1 at the third click (the leader at 504, 408).
3. `foeset.py`: the elf champion is combatant 45, creature 10, sheet 11: race 3, class 9
   (fighter) level 7, DEX 22. So its Chill Arrows go at level 7: caster level 7, and +1 (5th level
   or more, under 9th). The champions renamed in memory (Kreen, HalfGiant, Mul, Halfling, Elf,
   Defiler; never saved); every champion but the elf Paralyzed (`foeset.py C eff=34` on 40, 41, 42,
   44, 46) and the elf at 200 HP; party turns passed (`passn.sh 1`, `healparty.py` each pass).
4. Third pass, the elf's turn, two shots at Cermak (dice log, as written):
   ```
   Elf attacks Cermak with Wooden Fine Bow (1d8): d20 = 15, needs 3+ (90%), hits AC -6, target AC 6 -> HIT
       THAC0 14, +4 DEX, +1 fine = 9
     Elf hits Cermak for 8: 1d8 = [7] +1 weapon
   Chill Touch damage: 1d4 = [3] = 3
       Chill Touch lasts 60 rounds (caster level 7: 1 from the dice; dice 1d1)
   Cermak's saving throw vs Chill Touch from Elf (spell): d20 = 3 +4 DEX 18 dodging = 7, needs 12 (65% to save) -> failed: full damage, 3
     Cermak now 37/45 HP (-8)
   Elf attacks Cermak with Wooden Fine Bow (1d8): d20 = 12, needs 3+ (90%), hits AC -3, target AC 6 -> HIT
       THAC0 14, +4 DEX, +1 fine = 9
     Elf hits Cermak for 7: 1d8 = [6] +1 weapon
     Cermak now 34/45 HP (-3: 3 of the 7 rolled)
       Cermak's STR 19 -> 18
   Elf gives Weakened to Cermak: STR - the amount, at least 3
   Chill Touch damage: 1d4 = [1] = 1
       Chill Touch lasts 60 rounds (caster level 7: 1 from the dice; dice 1d1)
   Cermak's saving throw vs Chill Touch from Elf (spell): d20 = 11 +4 DEX 18 dodging = 15, needs 12 (65% to save) -> saved: no damage (not 1)
     Cermak takes 7 from Chill Touch, now 27/45 HP
   ```
   PASS: each hit casts Chill Touch (before the fix: none, logs/2026-11-18-champions-gear.md), at
   caster level 7 (the elf's fighter level: ARCHER_LEVEL), the arrows +1 ("+1 weapon": 7th level),
   Cermak's save rolled against it, a failed one takes 1 STR (19 -> 18, Weakened: the effects
   table's owner 2, caster 45, spell 3, effect 68, amount -1) and the damage, a saved one none. The
   lines are the party Spellarcher's (logs/2026-11-15-kit-rebalance-checks.md: "saving throw vs
   Shocking Grasp from Halton (spell)"), the elf's name in the archer's place.
   - The HP lines lag a hit behind when two shots come close together (the second hit's "-3: 3 of
     the 7 rolled" is the first's Chill Touch; "takes 7 from Chill Touch" is the second arrow's): the
     dice log's HP poll, the same for any weapon's spell. Not changed. ("Cermak regains 18 HP from
     Chill Touch" after it is `healparty.py`'s memory write.)
5. A party Spellarcher's arrows not played again (no Spellarcher in this save; a stack made in
   memory never shoots): the party rule is unchanged in the code and held by the emulated tests
   (`test_spell_arrows`, `test_spellarcher_arrows`).
6. Nothing saved (memory edits: Cilla's thief level, the names, the paralysis, the HP). The
   watchdog, the dice log, DOSBox and Xvfb stopped by pid. No water seen beyond ROUTE.md's.
