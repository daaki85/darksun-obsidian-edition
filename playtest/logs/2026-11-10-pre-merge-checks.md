# 2026-11-10: checks before the pull request

The build under test is commit 2337474.

## The tests that need tkinter
`/usr/bin/python3.12` has tkinter but not unicorn, so only the five files whose tests need it were run with it, on the Xvfb display:
- `test_compiles`, `test_find`, `test_partyview`, `test_viewer_options`, `test_viewer_settings`;
- `DSUN_*` set to the game's files.

16 ran and all passed. They were the 17 skipped under the default Python (15 "needs tkinter", 2 "no tkinter or no display").

## The release zip on a clean install
- **The zip:** made as the Release workflow makes it (`git archive --format=zip HEAD:obsidian-edition`, 6.66 MB). It holds only committed files: no `settings.json`, saves or crash logs. No file of 2.14.1's is missing.
- **The setup:** unpacked as `obsidian-edition/` in a scratch folder, beside the kit (`git archive HEAD playtest`), with a new `innoextract` of the GOG installer as its game.
- **First run:** the game quit at START GAME. `dos/GAMEEND.TXT` said "DARKSAVE.GFF to DARKRUN.GFF failed". The installer puts the starting `DARKSAVE.GFF` only in `__support/save`. GOG's own install copies that folder into `cloud_saves`, and its DOSBox overlays it on C:.
  - The Loader writes that overlay mount when `cloud_saves` exists (`launch.write_conf`), so a real install is fine.
  - Linux's DOSBox 0.74-3 has no overlay mount: a second try with `cloud_saves` failed the same way.
  - So this is the container's unpacking, not the mod. `setup_game.sh` now copies `__support/save/*` into the game folder.
- **With the save files in place:**
  - `start.sh` (the zip's Loader prepared the patched game from the clean install: `problem: None`);
  - `topartyfight.sh`: the opening, then the arena's first fight;
  - `buildcheck.py` OK, and the zip's `DSCLOG.EXE` is the repository's;
  - `fightout.sh` finished the fight (54 attack lines in the dice log, Wild Fighting rolled).

## An earth cleric-warrior's obsidian cahulaks
In the same clean install:
- **The character:** CREATE CHARACTERS, then NEW. One click on the portrait made the character a dwarf. Then CLERIC (fighter/cleric), and EARTH (AIR clicked off first).
- **DONE** opened the weapon window, and I chose the cahulaks.
- **The dice log:**
  - "Cromwell's Shield goes into the backpack: the weapon takes both hands";
  - "Cromwell starts with a plain obsidian cahulaks for the weapon specialization chosen, in place of the bone long sword";
  - "Cromwell starts with more gear: Chatkcha". An earth cleric can't use the sling, so fuller starting gear gives the chatkcha, as `startgear.py` does for a fire cleric.
- **The inventory:** the right hand holds **OBSIDIAN CAHULAKS**, and the panel gives "Cahulaks 2.5x1D6+5" (`img/2026-11-10-obsidian-cahulaks-start.png`).
