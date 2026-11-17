# 2026-11-16: checks before the 2.18.0 pull request

The build under test is the branch with version 2.18.0 (DSCLOG.EXE 70,416 bytes).

## The tests
- `python3 -m unittest discover -s tests` with the game's files: 1,929 run, OK (17 skipped).
- The tkinter ones with `/usr/bin/python3.12` on Xvfb (`test_compiles`, `test_find`,
  `test_partyview`, `test_viewer_options`, `test_viewer_settings`): 16 run, OK.

## The release zip on a clean install
- **The zip**: `git archive --format=zip HEAD:obsidian-edition`, 6.79 MB, unpacked as
  `obsidian-edition/` in `/tmp/clean/kit` beside the kit (`git archive HEAD playtest`); no
  `settings.json`, saves, crash logs or playtest files in it.
- **The game**: a new extraction (`PLAYTEST_WORK=/tmp/clean/work`, `PT_INSTALL_FILES` the private
  repository's checkout, `setup_game.sh`).
- **start.sh** from the kit: `problem: None`, DOSBox mounting the zip's `dos/`; `buildcheck.py
  fine_hit fine_item ns_flags_iret` OK; the zip's DSCLOG.EXE the same as the repository's.
- **A Spellarcher** ("Magramar", half-elf fighter/preserver, SPELLARCH): CHOOSE A SPELL in the new
  grid, Shocking Grasp at (189,91) first, then Armor, Burning Hands, Charm Person at (113,71); the
  bow on the weapon window. Dice log, all after DONE: the plain bow, armour and shield left behind,
  "starts with a Fine Bow (+1 to hit)", "24 shocking arrows in the quiver: Shocking Grasp picked",
  the short sword. carried.py: Shocking Arrows 24, Fine Bow, Short Sword.
- **A new game** (start.sh again, `topartyfight.sh`): the opening, then the arena's first fight;
  `fightout.sh`: DONE after 7 turns, 23 attack lines, "Gerakis fights wild: d20 = 18, needs 18 or
  less (CON 22 -4) -> 1 more attack a round and +3 damage, -3 to hit and AC 3 worse for the
  fight", Cermak an Arcanist.
