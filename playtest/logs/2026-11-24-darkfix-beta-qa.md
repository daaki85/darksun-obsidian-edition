# darkfix-ds1 0.2.0-beta.4 runtime QA (2026-11-24)

Build: the stock GOG 1.10 install, GPLDATA.GFF patched with all 12 darkfix fixes enabled
(OpenDS at 4425eb5; applied with our own applier from their REPAIRS lists; chunks for GPL 31, 58,
204, 210 match their published sha256). Run in plain DOSBox 0.74-3 with GOG's dosbox_darksun.conf,
no Loader. Saves from playtest/saves/ (made with the Loader) loaded into it.

## G: sewer grate (grate-user save)
- Loaded fine in the stock game; party beside the grate.
- (a) PASS: walking onto the grate: "The grate is locked. Do you open the grate?" Y -> "WHAT DO YOU DO? Rip it open. / Hack the lock off. / Leave the grate." (the stock game never offers the hack).
- (b) try 1: 2 (hack) -> "Cromwell's Bow breaks against the grate." That is the script's 1-in-3 branch (GPL 137 @0x9C5: RAND(3) < 2, or the item is -1576, succeeds); reloading to try again.
- (b) PASS (try 3, after waiting 9 s first so the dice differ; a reload replays the same rolls): "Cromwell successfully hacks the lock off with his Bow. The grate opens." Flag 505 = 1; walking onto the grate again: "Do you go into the sewers?"
- (b) note: Cromwell's weapon hand holds a Metal Axe (slot 3) and his Bow is in slot 2 (saves/README, logs/2026-11-11-grate-melee.md), yet both the success and the break lines name the **Bow**. Same fault our Loader hit with yuan-ti's version of this repair (2026-11-11): the weapon search (command 49h into scratch object 2Bh) goes round once more after the find and copies the next item over the found one; our fix leaves the loop on the find (jump to its RETURN, A96h). A hack is also offered for a bow (no melee test).
- (c) attack on the grate (attack pointer, click on it from 4 squares south): 1st attack "Cromwellfails to damage the lock." (FAIL side seen: the stock game always breaks it; note the missing space, the original line 0xB9B has none). 3rd attack: the lock broke (flag 505 = 1) and "Do you go into the sewers?" came up. PASS: a roll, not always.

## The rest (not played)
- T, H: static notes only (reports/community/2026-11-24-opends-darkfix-beta-qa.md).
- R, L next, from the pens' saves.

## Learned
- The stock game runs in plain DOSBox from a copy of inst: `start_stock.sh` (GOG's dosbox_darksun.conf
  is needed: with our conf alone DSUN.EXE dropped straight back to DOS, the SB IRQ check). The intro
  plays (Escape skips it), then loadsave.sh's clicks load slot 1. Saves made with the Loader load in it.
- `click.py`, `walkto.py`, `pointer.py` and `state.py` work on the stock game (they read memory).
- Reloading a save replays the same rolls: wait a different time before the roll to get another.
- The grate's attack: the attack pointer (`pointer.py attack 250 150`), a click on the grate from 4 squares south.
