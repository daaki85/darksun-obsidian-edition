# 2026-11-27: Wake of the Ravager's combat log panel: clicks and L

**The report** (the owner, in DOSBox-X): the in-game log took no clicks, and L showed it but didn't hide it.

**Setup**: plain DOSBox 0.74 on `:55` (DOSBox-X 2025+ isn't in this container), `RAV_LOADER=1 sh ravload.sh
ravager-after-ambush`, `ravdice.py 3000` for the Loader's side, L on the map.

## Before (obsidian-edition at 01b8b7fe)

- L shows the panel and L hides it, in DOSBox 0.74.
- Clicks on the panel's header buttons: the first was counted by DSCLOG2 (`panel_hits` 1), the next ones
  not, and **every one walked the party** to the place clicked (once into the shop, whose keeper's talk
  opened). DSCLOG2 looked for the press in the main loop's call for the pointer (PROBE_SCROLL's
  `panel_mouse`), which sees it only if the button is still down as the loop runs; the game's own mouse
  handler had the press anyway.
- The page test (`panel_page` against DS:118Eh) held on the map all through 25 s of walking (500 samples,
  no mismatch); it was off only under the talk window. Why L fails to hide in DOSBox-X couldn't be seen
  here: L and clicks were both gated by that test, the one thing they share.
- Note: ravclick.py takes game pixels; the 640x480 window is 2 across and 2.4 down per game pixel (the
  header's buttons at window y 303 are game y 126).

## After (DSCLOG2's PANEL_EVENT in MOUSE_EVENT, PANEL_HERE for L and presses)

- Three clicks on the header: all counted (`panel_hits` 3); the first pressed + (expanded), the party
  didn't move.
- The Party filter: on ([picture](img/2026-11-27-ravager-log-clicks.png)), no walk.
- L hides it, L shows it again.

## Water

Nothing new (Tyr's street and the shop beside it).
