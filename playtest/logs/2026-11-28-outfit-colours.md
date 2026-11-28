# Codex's outfit colour pass, checked in both games (2026-11-28)

**Under test**: branch `codex/steady-palette-materials` (0bf4097f, with `codex/priest-fighter-druid-finishes`
under it), Codex's answer to the colour notes of 2026-11-28 (steady colours only, the 51 leather
highlights, darker Fighter leather, a shadow side on the Cleric and Psionicist, the human man's Priest robe).
New: per-outfit `-material` layers in the `*_outfit_layers.zip` archives, composited last in
`classoutfits.frames`, made by `prototypes/outfitpalette.py`.

## Offline (every figure, every class and multiclass)

- Every dressed party picture built with the branch's Loader and with `obsidian-edition`'s, 236 walking
  sets: **no outfit pixel on an area-swapped palette slot** (`spritegear.REGIONAL`). 137 of 236 changed.
- Dark pixels (Lab L < 25, slave pens palette PAL 41; stock people 42%): Fighter 37 -> 41%, Cleric 21 -> 24%,
  Psionicist 28 -> 31%, multiclasses 37 -> 38%; the rest unchanged.
- Sheets (slave pens floor, front, side and back, 5x/6x and the 3x game size): project files
  `class-figures/codex-review/2026-11-28-colours-*.png`.

## In DOSBox

- Shattered Lands, `pens-after-arena`: classes set in memory with `outfitlive.py` (KEEP=1; the half-giant
  Fighter, the human man Psionicist; put back after, nothing saved). The Loader's copy of SEGOBJEX.GFF holds
  exactly what `Pictures.build` makes with the material layers (0 pixels differ).
- **outfitlive.py said "as built [False, False]"** for any dressed figure: it built without
  `spritegear.set_palette`, so the steady remap didn't run on its side (2,203 pixels off for the half-giant
  Fighter). Fixed: it sets the portrait palette as the Loader does.
- Wake of the Ravager, `ravager-roost`: the leader (half-giant Psionicist) in the teal with its new shadow
  side. The sequel's dress pass (`ravdress.recoloured`) gives different pictures with the branch than without
  for every class tried, so the change reaches both games.
- `ravload.sh` leaves the sequel's window at 640x480 with the picture not at the screen's corner: grab it
  with `import -window $(xdotool search --class dosbox | tail -1)`, not a crop of the root window.
- Start-up tests (`test_start_files.py`, both games): 3 passed. Outfit, sprite and gear tests with the game
  files: 227 passed.

No new area was reached (water: nothing new).
