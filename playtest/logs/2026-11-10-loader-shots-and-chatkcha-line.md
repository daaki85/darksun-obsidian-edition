# 2026-11-10: the Loader's screenshots retaken; K'ratchek's chatkcha line taken off

**Under test.** Three things:
- the Options picture (`docs/options.png`);
- the dice log picture (`docs/dicelog.png`), in the readable layout;
- the Effects screen without `CHATKCHA 2/ROUND`. The user asked for this: the 2/1 rate is every thri-kreen's now, so it isn't K'ratchek's own feature.

## Options picture

- **Setup:** Xvfb `:57` at 1400x3400, with `python3.12 -m dsloader view`. The window was resized to 1320x3300 with `xdotool windowsize`.
- **What was open:** the Options tab, with Rule changes and New content open. The window remembers which sections are open; Graphics had been open and was closed with a click on its header.
- **The crop:** the right panel from its tabs (x 608, y 116) to under Restore defaults, 706 x 2426.
- **What it shows:** 25 rule switches.
- **Watch the screen size:** at 2400 rows, Xvfb cut off the window's bottom (Controls to Restore defaults).

## Dice log picture

- A new game, played by hand from `start.sh` on `:55`. The window Loader was attached (Reconnect) before START GAME.
- After the opening show (round 4, the Rampager's acid kills the Defiler), the window was grabbed at 1320x780.

## The two-Loaders lock in a test

- The window Loader holds `game.lock`. Started beside it, start.sh's text dice log stops at once, and nothing more happens:
  - `dice.txt` stays empty;
  - nothing sets the party's own features (kit byte +43h stayed 0), so the Effects screen showed no WILD FIGHTING at all.
- To fix it: stop the window (kill its pid), then `start.sh` again.

## Effects screen

- New game; I, the Effects button (243,187), then the portraits Gerakis (66,62) and K'ratchek (112,62).
- **Gerakis:** WILD FIGHTING, specialized in long sword and gythka.
- **K'ratchek:** OPEN SKY SPELLS/PSI, specialized in chatkcha. No chatkcha rate line.
- The picture is `img/2026-11-10-kratchek-effects.png`.
- `buildcheck.py`: OK.

## The Options picture again (after the switch merges)

The same recipe:
- Xvfb `:57` at 1400x3400; `python3.12 -m dsloader view`; the window found with `xdotool search --onlyvisible --name .` (the window title is "Dark Sun Obsidian Edition Loader ..."), resized to 1320x3300 and moved to 0,0.
- The Options tab (1061,132).
- The window had kept Graphics and Controls open. Clicking the headers at x 700, bottom-up so the ones above stay put: Controls closed, then New content and Rule changes opened. The header rows were found by scanning x 640 for the headers' borders.
- The crop: x 608, y 116, 706 wide, to 12 rows under the last dark row of Restore defaults (y 2577). That gives 706 x 2473, taller than before with fewer switches, since the merged ones' texts are longer.
- The Loader window was closed by its pid.
