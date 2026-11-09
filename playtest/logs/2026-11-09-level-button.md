# The USE screen's LEVEL button (2026-11-09)

Under test: whether the LEVEL button (196,171), the spell-level pager, has a real fault. The earlier
report (logs/2026-11-09-memory-pass-2.md) was that Lex's button stayed on LEVEL 1 in `fountain-user`
after `spellsetup.py 0=10 33 28`, with that build and the one before. Build: the branch as it stood
(f5d9e3d's DSCLOG, the memory pass 2 build), DOSBox, the default rules (settings.json has none set).

## Result

**No fault found, in the game or the mod.** The button paged as the game's rule says in every case
tried, with and without memory edits, in and out of a fight, and with the relevant rules switched
off. The earlier "stuck on LEVEL 1" did not come back with the same save and the same spellsetup
arguments (three loads). Its cause is unknown: this run's notes don't say what else had been
written to Lex before. The likeliest cause is a memory edit that left Lex with a caster level of 0.
spellsetup.py now prints the pages the button will offer and warns of the one case the game's
rules leave on 1 (below). It also sets each casting class, not always the sheet's second place.

| Case | Seen | Verdict |
|---|---|---|
| Ester (#2, fountain-user, fighter 2 / cleric 3, no edits), in the ambush fight | LEVEL 1, 2, 1, 2 (PRI 5/5, 4/4) | OK: cap (3+1)/2 = 2 |
| Lex (#0, half-elf fighter 3 / preserver, `spellsetup.py 0=10 33 28` in the fight) | 1, 3, 1, 3 (WIZ 9/4, 9/3) | OK: no 2nd-level spell known, so 2 is skipped |
| The same, spellsetup run before the ambush's speech was clicked away | 1, 3, 1, 3 | OK: the fight's start doesn't undo the edit |
| The same with `kits`, `ranger_casting_level`, `int_learning`, `adnd_tables`, `new_spells`, `level_10`, `class_restrictions` off | 1, 3, 1, 3 (WIZ 9/5: the game's tables) | OK: no mod rule involved |
| Cermak (#2, pens-after-scar, human preserver 3 / gladiator 3, no edits), out of a fight | 1, 2, 1, 2 (WIZ 2/2, 0/1) | OK: a page with no slot left is still offered |
| K'ratchek (#1, pens-after-scar, priest page, no edits), out of a fight | 1, 2, 1, 2 (PRI 5/5, 3/4) | OK |
| Cermak after the new `spellsetup.py 2=9` (preserver 9) | from the remembered 2: 3, 4, 5, 1, 2 | OK: as the tool predicted |
| Cermak with his classes swapped in memory (gladiator 3 first, preserver 9 second: a human) | no MAGE page at all (only PSIONIC); spellsetup.py warns | the game's dual-class rule, below |

Pictures: img/2026-11-09-level-ester-fight.png, -lex-spellsetup.png, -cermak-out-of-fight.png,
-cermak-preserver9.png.

## How the game decides (DSUN.EXE)

- The button (88A94h): kind byte [member + 4AE8h] (1 wizard, 2 priest, 3 psionic), page DS:4AECh
  (each member's kept at +4AE0h). next = 5F8:4Dh (81664h)(member, kind, page); if next == page, page
  = 0 and ask again; page = next, or 1 if 0.
- 81664h: the first level above the page (to 22) where 500:2Fh (5DE88h: spells known of that kind
  at that level, the known byte & 0Fh) and 500:52h (5E0ACh: the slots its classes give on resting,
  not the slots left) are both non-zero. Unless DS:1164h (the game's test switch: 19 of everything)
  is set, that level is then cut to (caster level + 1) / 2. The caster level is 5F8:61h (81B16h) for
  spell 0 (wizard) or 45h (priest): the best level over classes 1-19 whose magic mask (2F8:118h +
  4 x class) shares a bit with the spell's (408:19Dh + 7 x spell), rangers (13-16) 7 less (the
  mod's PROBE_RANGER_CAST there, PROBE_CAST_LEVEL at its end: a Shinobi's).
- The level of a class is 508:25h (5E7CFh): the sheet's +24h at the class's place; **a human's
  class in place 2 or 3 counts 0 unless its level is below the first place's** (AD&D's dual class:
  the old class comes back once the new one passes it). 5E0ACh (the slots) has the same test at
  5E130h. The mod's PROBE_ADND_SLOTS (5E240h) only changes the counts.
- So the button stays on 1 when the caster level is 0 or 1 (cap 0/1), or when no other level has
  both a known spell and a class slot. In normal play the cap is never below the levels the slots
  reach, so a player can't be stuck. A dual-classed human's old class only comes back once the new
  class has passed it, so it can't sit at or above the first class in play.

## Steps

- `loadsave.sh fountain-user`, `dismiss.sh`, `passuntil.sh 2`, U, five shots of LEVEL clicks
  (196,171); Escape, `spellsetup.py 0=10 33 28`, `passuntil.sh 0`, U, the clicks.
- `loadsave.sh fountain-user`, spellsetup before `dismiss.sh`, the same.
- The rules off with `launch.save_settings` (settings.json backed up and put back afterwards), a
  new load, the same.
- `loadsave.sh pens-after-scar`, U, Cermak's portrait (66,108), clicks; K'ratchek (112,62), clicks;
  Escape, the new `spellsetup.py 2=9 1=9`, Cermak again; then his classes swapped in memory.
- Never saved. The watchdog's GONE line (03:06) was loadsave.sh restarting DOSBox.

## Tool changes

- `spellsetup.py`: raises every casting class (wizard or priest bit in its magic mask, any of the
  three places), not the second place alone (Cermak's preserver is first: the old tool raised his
  gladiator level). It prints `M Wizard: LEVEL pages [...]` by the game's rule above, and warns
  when a human's casting class in place 2 or 3 is at or past the first class's level. Slots are
  counted with the rules from settings.json.
