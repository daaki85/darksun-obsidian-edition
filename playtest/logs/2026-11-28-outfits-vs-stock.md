# Class outfits beside the stock figures (2026-11-28)

**Under test:** how the class outfits look next to the games' own people, in both games. Read-only: no figure
changed. Build: `obsidian-edition` at 3eee1388 (after #300), the Loader's patched copies (`start.sh`,
`ravload.sh`).

## Steps

1. `loadsave.sh pens-after-arena`; window 320x240. `shot.sh`: the ready-made party in the pens' yard beside Kurzak
   and a slave. Then `KEEP=1 outfitlive.py 2 classes=1,0,0` (member 2, the human man: Priest) and `KEEP=1
   outfitlive.py 3 classes=9,17,0` (member 3, Cilla, elf woman: Fighter/Thief): both redrawn in the next frames, no
   area change needed. Member 1 is the thri-kreen (object 313: no outfit). Not saved.
2. `loadsave.sh fountain-user`, `dismiss.sh 4`: the ambush's fight starts; `shot.sh` with Pehtucl beside the party.
3. The DOSBox stopped by pid, then `ravload.sh ravager-after-ambush` (Tyr's street) and `ravload.sh
   ravager-roost` (the Harbinger's Roost: the dressed leader, a half-giant in the teal Psionicist outfit, beside a
   woman of the inn). Their grabs are `ravload.sh`'s own (`$WORK/rav-loaded.png`).
4. Sheets made offline from the game files, on floor tiles cut from those shots: project files
   `class-figures/stock-comparison/` (the assessment in its README).

## What was seen

- The outfits sit in the game at game size: same size, outline and density as the stock people. They are lighter
  inside the outline (34% dark pixels against 42%), most of all the Cleric and Psionicist robes.
- Stand-outs: the human man's Priest robe is speckled white and near-black; leather Fighter outfits melt into the
  skin on dwarves, halflings, half-giants and the Mul; the robes follow the body where stock robes reach the floor.
- In the Roost the dressed half-giant shows black gauntlets and boots under the teal (not in the offline build of the
  same outfit). Not looked into.

## Lessons (in the guide)

- `shot.sh` is Shattered Lands' capture only: with the sequel running it finds no capture. Use `ravload.sh`'s grab or
  `import -window`.
- An `import -window` grab of the sequel is 640x480: each game pixel twice across and 2.4 times down, and its palette
  is ImageMagick's, not the game's. For the game's own picture take every second column and row `int((y+0.5)*2.4)`;
  for the game's colours use the region palette (`ravitems.region_palettes`) with each 6-bit value as `v*4+v//16`
  (region 1 matched every colour of Tyr's street and the Roost exactly; `v*255//63` matched a third).

## Water

No new area (the pens and Tyr's street and Roost, all noted before).
