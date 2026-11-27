# Full Elf figures in the Ravager catalogue

The shipped character records contain seven entries with Elf race code 3, spread across six picture numbers. The male Elf creation slot (object 304) also belongs in this audit. Its template leaves race unset. The tables below cover all seven picture numbers. The published party sheets, the dress definitions and the approved archive were checked separately.

## Party figures and the Preserver

| Figure | Finding | Corrected artwork |
| --- | --- | --- |
| 599, female Elf party slot (305) | All 15 walking pictures and the three side-strike pictures shown in the published party row match retail Shattered Lands after palette conversion. | [Obsidian female party Elf](proposals/599-obsidian-party-elf.zip) |
| 691, male Elf party slot (304) | The same 18 displayed pictures match retail. Ten Human merchants share the shipped picture. | [Obsidian male party Elf on picture 3961](proposals/3961-obsidian-party-elf.zip). Only object 304 moves in the approved import. |
| 2426, Preserver (12) and VA Member (169) | The outfit used the class-outfits branch’s Elf woman, but the export stopped before the loader drew the ears. The preceding proposal and its comparisons remain in the catalogue. | [Corrected dressed Elf](proposals/2426-obsidian-ears.zip) |

The mod uses the same underlying walking and combat poses as retail. Its final layer adds the ears after dressing. The front and rear poses show two ears, the profile shows the near ear, and a raised arm or weapon can hide one. The corrected 2426 export uses the loader’s pose coordinates and occlusion rules before mapping the ear colours into Ravager’s palette. [Obsidian ear definitions](https://github.com/daaki85/darksun-obsidian-edition/blob/a8c762add0ed76174c9d5a35c63915645b709296/obsidian-edition/dsloader/figures.py#L139) · [Loader draw order](https://github.com/daaki85/darksun-obsidian-edition/blob/a8c762add0ed76174c9d5a35c63915645b709296/obsidian-edition/dsloader/sprites.py#L325)

Both approved party figures reproduced the mod’s expected ear treatment pixel for pixel in all 15 walking and 14 combat pictures per Elf after palette conversion. The approved 2426 package passed all 72 animation steps. Two imports tested the ten Human merchants. The first used the shipped 691 artwork. The second started with Elf pictures and a replacement script on 691. After each import, all ten merchants retained 691, and its base, combat and script chunks matched the shipped originals byte for byte. The male player split still needs verification in character creation and on the final game installation. All three revisions are registered in the approved manifest. The importer also restores the shipped merchant resources at 691 when an earlier build used the party art there.

[Previous and corrected heads](img/elf-ears-audit.png) · [Movement on the two 2426 map floors](img/elf-ears-motion.gif)

## Other characters recorded as Elf

| Figure | Shipped assignments | Artwork and review decision |
| --- | --- | --- |
| 2409 | Notaku (58), Elf | The approved shop comparison uses Notaku’s own Shattered Lands NPC artwork, picture 384. The Obsidian party-ear routine targets pictures 2061 and 2059. Keep his named likeness and evaluate any ear edit against his own frames. |
| 2432 | Wren (75), Elf | The [approved green tunic](img/2432-wren-review.png) uses the full Elf man with the Obsidian ear layer. The earlier half-elf study remains in the catalogue. |
| 2438 | Drisha (196), Elf. Guards 244 and 246, Human | Approved split. Drisha uses the Obsidian Elf woman on 2438. Both guards use the Shattered Lands Human woman on 3967. [Same-facing comparison](img/2438-drisha-comparison.png) |
| 2456 | Silvain (171), Elf. Dariya (81), Halfling | [Split approved](README.md#2456-dariya-and-silvain). Dariya uses the female Halfling. Silvain uses the revised Human water druid artwork following the official cluebook (p. 24). The catalogue preserves the pointed-ear Elf alternative. |

## Other uses of Elf artwork

An Elf body or comparison image also occurs in the earlier catalogue material for 721, 2410, 2430, 2439, 2458, 2460, 2461, 2467 and 3612. None has a shipped user recorded as Elf. Figures 2526 and 3866 cite the Elf woman as a visual comparison. Those references alone do not establish a race. The separate party Half-elf packages 779 and 780 already use their Obsidian models. Their base, combat and script chunks matched their approved packages in the test archive.
