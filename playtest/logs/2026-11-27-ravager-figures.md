# Wake of the Ravager's redrawn figures in the Loader's copies (2026-11-27)

**Under test:** branch `claude/ravager-figure-import`: `dsloader/ravfigures.py` and `ravager-figures.zip`
(Codex's approved catalogue at b447d39 in the private installation files, put through darksun-recompiled's
`tools/proto/import_catalogue.py` at 013a4e0), written by `ravager.prepare` into `OBJEX2.GFF`, `RESOURC2.GFF`
and the new `RGN03A2.GFF`; DSCLOG2's new redirect of `RGN03A.GFF` (COPIED bit 8).

**Save:** `ravager-after-ambush` (`ravload.sh`, the Loader's way). No memory edit.

1. **The import reproduced.** `import_catalogue.py CATALOGUE rav OUT rav` on the stock files: "275 pictures from
   149 packages, 32 objects moved, 2 region file(s); 0 problems", as Codex's handoff says. `python -m
   dsloader.ravfigures pack OUT rav`: 558 OBJEX chunks, 18 RESOURCE, 1 RGN03A (ETAB 58), 32 objects; 1.8 MB.
2. **Loaded with the figures** (`ravload.sh ravager-after-ambush`): the copies made (`OBJEX2.GFF` 10.2 MB,
   `RESOURC2.GFF`, `RGN03A2.GFF` 106 KB), the game loaded, Tyr's street drawn; the shop's thief in his red cloak
   on the Shattered Lands body. COPIED `0b111` (Tyr doesn't open RGN03A). [On](img/2026-11-27-ravager-figures-on.png)
3. **The control** (`RAV_SKIP=figures ravload.sh ravager-after-ambush`): no `RGN03A2.GFF` written, the
   sequel's own figures. [Off](img/2026-11-27-ravager-figures-off.png) (the people mid-walk, so not the same frame).
4. **The region redirect through a scratch helper** (DSCLOG2 built with `RGN032.GFF` named in place of
   `RGN03A.GFF`, its copy `D:\RGN0322.GFF` a copy of the stock RGN032): loaded the same save, COPIED `0b1111`, so
   the game opens a region file through INT 21h 3Dh by that name and reads the Loader's copy. The real helper
   put back and checked byte for byte against a fresh build.

**Not seen:** the Mines3 dining room itself (RGN03A), the Tarrasque's fight and its cinematic, the drakes:
no save near them. Water: none new (Tyr's street only).
