# Reviewing Codex's Ravager branches in play (map controls, Whirlwind)

What was under test: `codex/ravager-map-controls` at 03ca9b23 and `codex/ravager-whirlwind` at 82d66d2a, each
from its own worktree (the tools run the worktree's `obsidian-edition/`), the Loader way (`ravload.sh
ravager-after-ambush`), `settings.json` with `autosave` and `quick_save` off. Memory edits were never saved.
The review itself is in the project's files (ravager/codex-review/2026-11-26-review-of-codex-break-work.md).

## Map controls

- Both builds of `dsclog2.asm` match the committed DSCLOG2.EXE; the full suite with both games' files passed.
- **Drag**: the window pointer at 400,150, middle button held, then ten moves of (-16, +12): `ravtab.py` read the
  view from (1080, 1280) to (1224, 1192), `pan_moves=8`, the pointer at (90, 143). The map followed the pointer.
  Released, the view stayed; the first arrow-key step put it back on the leader (1080, 1280).
- **Tyr's thieves** (Up 8, Right 40, answer 2, Space; C, then the USE screen's four lower icons for Computer Control,
  Escape): the fight won itself in about 25 s, and the four stood together on screen after it.
- **The fight camera**, the view and whose turn read every 0.5 s (`ravtab.py`): within one turn the view moved in 10
  of 28 samples with the patch, 29 of 83 with `RAV_SKIP=camera_still`. No difference to call at this rate; much of
  it may be the game's own centring at a turn's start.

## Whirlwind

- The second member made an air cleric of 18th level in the fight ([the edit](files/2026-11-26-codex-review-air-cleric.py)).
  On the USE screen (C), LEVEL pressed five times shows level 6: Whirlwind (Sandstorm's icon), Restore Youth (a
  fountain) and Blade Barrier, with "3 LEVEL 6 SPELLS TO CAST". **The icon row's middle is game y 58**: clicks at
  y 48 and 50 did nothing; at 175,58 the screen closed with the spell's pointer and its range ring.
- Aimed at the two thieves (212,45): the funnel drawn and turning; 2d8 to each creature in it, a save for half
  (Ar'Anda saved 17 against 10 and took 4 of 9), again at the next round's start. It struck Thy'rokh, Ar'Anda and
  the caster (Terrannus, at 1 HP, to 0), as SL's guide says it does. No line in the dice log says anyone was swept.
- In the dice log the damage line comes one roll after its save (a thief's "takes 11" printed after the next roll).

Water: none looked for (no new area).
