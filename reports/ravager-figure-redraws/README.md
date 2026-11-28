# Wake of the Ravager figure redraws

The final import uses the approved catalogue manifest. The handoff records the tested importer revision, command and three output files. [Import handoff](catalogue/figure-audit.md#import-handoff)

## Source sheets for rebuilding figures

Codex's redrawn figures (2026-11-22), drawn from Wake of the Ravager's art. darksun-recompiled's code (`tools/proto/restyle/figure_walks.py`, `knight_melee.py`)
reads them from `tools/proto/restyle/walks/` and `knights/`: copy or link these folders there
(git-ignored) before a build.

- `walks/`: indexed, foot-aligned walk sheets: 1753, 1754, 2555 and 2850 (all ten verini, recoloured
  per variant) as toward, side and away rows of 4 cells of 72x52; 2411 (thief) and 2539 (soulshard)
  side only; `2539-standing.png` the soulshard's side stand.
- `knights/`: `profile.png` the plate knights' side stand and walk (5 cells of 40x32, silver; the
  black knight is a recolour), `3605.png` and `3606.png` their side strikes (4 cells of 40x32).

## Where this lives, and what was left out

This folder moved here from the owner's private installation files on 2026-11-27 (the owner's rule:
only the games' installation files and the walkthroughs stay private). Everything Codex drew, every
review picture and every note came across. What did not: any chunk that was a byte-for-byte copy of
a chunk in the shipped game's files (SSI's own picture or script, unchanged). Those were found by
hashing every chunk of Wake of the Ravager's GFF files against every chunk in the packages, and taken
out. `tools/proto/import_catalogue.py` in darksun-recompiled takes any bank a package lacks (and any
package whose zip is gone) from the player's own game, so the build is byte-for-byte the same as with
the full packages (checked 2026-11-27: OBJEX.GFF, RESOURCE.GFF and RGN03A.GFF identical).

| Package | What happened | Stock chunks taken out |
|---|---|---|
| `catalogue/approved/3238-original-sword.zip` | zip removed (every chunk was stock) | 3238/base.chunk, 3238/script.chunk |
| `catalogue/approved/691-human-merchants-stock.zip` | zip removed (every chunk was stock) | 691/base.chunk, 691/combat.chunk, 691/script.chunk |
| `catalogue/approved/catalogue-base-figures.zip` | kept, 36 file(s) left in the zip | 849/base.chunk, 849/combat.chunk, 849/script.chunk, 1736/base.chunk, 1736/script.chunk, 2395/base.chunk, 2395/combat.chunk, 2395/script.chunk |
| `catalogue/proposals/1249-heroga-storyteller.zip` | kept, 1 file(s) left in the zip | 1249/script.chunk |
| `catalogue/proposals/1475-asquire-detail-restored.zip` | kept, 1 file(s) left in the zip | 1475/script.chunk |
| `catalogue/proposals/1475-asquire-second-pass.zip` | kept, 1 file(s) left in the zip | 1475/script.chunk |
| `catalogue/proposals/1475-asquire-stance.zip` | kept, 1 file(s) left in the zip | 1475/script.chunk |
| `catalogue/proposals/1476-ludwig.zip` | kept, 1 file(s) left in the zip | 1476/script.chunk |
| `catalogue/proposals/1477-fletch-chair.zip` | kept, 1 file(s) left in the zip | 1477/script.chunk |
| `catalogue/proposals/2409-notaku-stall-66.zip` | kept, 3 file(s) left in the zip | 2371/base.chunk, 2374/base.chunk, 2375/base.chunk, 2376/base.chunk, 2377/base.chunk, 2379/base.chunk |
| `catalogue/proposals/2409-notaku-stall.zip` | kept, 3 file(s) left in the zip | 2371/base.chunk, 2374/base.chunk, 2375/base.chunk, 2376/base.chunk, 2377/base.chunk, 2379/base.chunk |
| `catalogue/proposals/2469-village-giant-planted-idles.zip` | kept, 4 file(s) left in the zip | 2469/combat.chunk, 2470/combat.chunk |
| `catalogue/proposals/2469-village-giant-recovery.zip` | kept, 4 file(s) left in the zip | 2469/combat.chunk, 2470/combat.chunk |
| `catalogue/proposals/2526-rattlenook-mushroom-seller.zip` | kept, 1 file(s) left in the zip | 2526/script.chunk |
| `catalogue/proposals/2570-zorani-campfire.zip` | kept, 1 file(s) left in the zip | 2570/script.chunk |
| `catalogue/proposals/2570-zorani-matched-mantle.zip` | kept, 1 file(s) left in the zip | 2570/script.chunk |
| `catalogue/proposals/2577-white-and-black-knights.zip` | kept, 8 file(s) left in the zip | 2577/script.chunk, 2578/script.chunk |
| `catalogue/proposals/3170-cavern-prisoners.zip` | kept, 1 file(s) left in the zip | 3170/script.chunk |
| `catalogue/proposals/3238-force-blade.zip` | kept, 1 file(s) left in the zip | 3238/script.chunk |
| `catalogue/proposals/3461-sirah-lyceum.zip` | kept, 1 file(s) left in the zip | 3461/script.chunk |
| `catalogue/proposals/3509-rope-vine-tree.zip` | kept, 1 file(s) left in the zip | 3509/script.chunk |
| `catalogue/proposals/3597-abelard.zip` | kept, 1 file(s) left in the zip | 3597/script.chunk |
| `catalogue/proposals/3612-purple-miners.zip` | kept, 1 file(s) left in the zip | 3612/script.chunk |
| `catalogue/proposals/3855-rybochka.zip` | kept, 1 file(s) left in the zip | 3855/script.chunk |
| `catalogue/proposals/918-blick-second-pass.zip` | kept, 1 file(s) left in the zip | 918/script.chunk |
| `catalogue/proposals/alternate-pose-continuity.zip` | kept, 7 file(s) left in the zip | 788/script.chunk |
