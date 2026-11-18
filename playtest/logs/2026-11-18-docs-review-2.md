# The second documentation review's fixes: the Elvenkind picture and the upper memory (2026-11-18)

Under test: none of the code; two in-game jobs for the docs fixes of `claude/docs-review-2-fixes`
(from origin/obsidian-edition at 1051ee3): fix 25, `docs/elvenkind.png` retaken so the Cloak and
Boots of Elvenkind show the green shimmer they have had since #106; fix 12, upper memory's free
piece measured with `memaudit.py` for DEVELOPMENT-INTERNALS.
Build: the tree's `dos/DSCLOG.EXE` (unchanged by this branch), the Loader's patched game.

Steps:

1. Container: DOSBox and Xvfb not running; `/tmp/playtest/inst` there. `flock
   /tmp/playtest/dosbox.lock` held for the session. `loadsave.sh pens-after-arena`: loaded,
   region 29h, leader (1672, 344). Window 320x240. `buildcheck.py` OK (129 vectors at their
   handlers, the tail same as the EXE). Watchdog started, its Monitor on; no STUCK or GONE.
2. **Upper memory (fix 12)**, `memaudit.py` in the pens with the map open: from CA00h, 144 bytes
   free, DSCLOG 71,104 (4,444 paragraphs), the overlay buffer 32,992, **25,136 free in one piece**,
   the see-through tables 14,160, the music buffer 12,016. Conventional: 99,008 bytes free after
   the game (97 KB). DEVELOPMENT-INTERNALS's 29,616 (2026-11-16, before UMBPLUS's CA00h and the
   newer builds) replaced with 25,136.
3. **The Elvenkind picture (fix 25)**: Gerakis's Arm Armor (item 25) made the Boots of Elvenkind
   in memory (`setitem.py 25 rec=` with `worldgear.ELVEN_BOOTS.hex()`, then its slot byte +11h set
   to 13, the feet, by a scratch script through `live.py`'s `g.write`), the inventory (I), a
   right-click on the feet place (174,147), the pointer off (280,190), four `shot.sh` captures 0.4 s
   apart. **The box closes on its own within about a second of the pointer moving off**: only the
   first capture has it. Then the inventory shut, item 25 made the Cloak of Elvenkind
   (`worldgear.ELVEN_CLOAK`, slot 12: the cloak place, the right column's top, 174,48), the same
   again. Both icons show green pixels (13 in the cloak's, 29 in the boots'), the old picture's
   blue shine gone.
4. The old picture's crops, found by matching its pixels against the new captures: the cloak's
   box 93x66 at +184+18, the boots' 112x66 at +173+95 (not +183+95 as the 2026-11-09 log says),
   each scaled 200%, side by side, a black row under them: 410x133, as before. Viewed, then put in
   `obsidian-edition/docs/elvenkind.png` (256 colours); its alt text names the green shimmer.

No new area, so nothing for ROUTE.md's water section. Memory edits only; the game was not saved.
DOSBox, the dice log and Xvfb stopped by pid, the watchdog stopped, the lock released.
