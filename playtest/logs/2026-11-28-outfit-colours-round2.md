# Codex's outfit colours, round 2, checked in both games (2026-11-28)

**Under test**: branch `codex/fitted-linen-and-leather` (6749a281), Codex's answer to
`codex-notes/2026-11-28-outfit-colours-round2.md`, against `obsidian-edition` with round 1 (PR 305).

## Offline (every figure, every class and multiclass)

- 236 dressed walking sets built with both Loaders: **no outfit pixel on an area-swapped slot**; 79 changed.
- Dark pixels (Lab L < 25, pens palette; stock 42%): Fighter 41 -> 43%, Cleric 24 -> 27%, multiclasses
  38 -> 39%. Mean lightness of the outfit pixels: Cleric 45.1 -> 43.4, Psionicist 35.1 -> 32.7, the human man's
  Priest 40.9 -> 43.6 (lighter, but in big flat areas: the speckle is gone).
- The five points: half-giant man Fighter now dark like the woman's; elf and half-elf Fighters dark (560 to 890
  pixels each); Psionicist lit teal one step deeper; human man Priest smooth cream and brown panels; Cleric
  one step deeper, still the lightest outfit.
- Sheets: project files `class-figures/codex-review/2026-11-28-colours-r2-*.png`.

## In DOSBox

- Shattered Lands, `pens-after-arena`: the half-giant set to Fighter and the human man to Cleric (Priest) with
  `outfitlive.py` (KEEP=1, put back after, nothing saved): "as built [True, True]" for both, so the game's
  copy is the build (the palette fix of round 1 works).
- Wake of the Ravager, `ravager-roost`: the leader's Psionicist teal deeper; the sequel's dress pass
  (`ravdress.recoloured`) gives new pictures for every class tried.
- Start-up tests, both games: 3 passed. Outfit, sprite and gear tests with the game files: 229 passed.

No new area was reached (water: nothing new).
