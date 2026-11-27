# In-game checks of the approved figures

## 2026-11-27 mod import

The import review compared 64 new pictures on their area floors. The first loader run reached Tyr. A second playtest on installation files e33bc2e reached the encounters below and repeated the jumps with stock figures. [Campaign encounter log and stock controls](https://github.com/daaki85/darksun-obsidian-edition/blob/96b675e80045a98aac3f15f81faf4845daf14740/playtest/logs/2026-11-27-ravager-encounters.md)

| Encounter | Observation in the campaign | Source follow-up |
| --- | --- | --- |
| Air Drake 11005 | Walked, circled and swallowed in the Cloud. Size matched stock. The pile-up on a swallowed party member also occurred in the control. | Existing artwork confirmed. |
| Fire Drake 11006 | Two raptors walked and attacked on Volcano rock. The stock dragons stood taller beside the party. | Enlarged all 21 base and 14 combat drawings and updated their anchors. [Compare the revised scale](img/11006-encounter-scale.gif) |
| Tarrasque 11001/11002 | The visible halves joined in battle. The side posture was too low and the redraw periodically disappeared at step 44. Stock stayed visible in 77 samples. Elementals overlapped the creature in both versions. | Rebuilt the paired combat banks and grounded the profiles at the stock offsets. The replay below checks visibility during the corrected attack. [Compare the corrected sequence](img/269-encounter-correction.gif) |
| Tarrasque cinematic 11012–11014 | The stairs in RGN044 triggered the cinematic. Frame changes and lightning flashes matched the stock control. | Cinematic confirmed. |
| Earth Drake 11007 | After the rock moved in RGN043, the drake rose and stood cleanly. Look identified it as a level 25 Earth Drake. | Combat still needs a playthrough with the party together in the region. |

**Corrected packages in DOSBox.** A temporary change to the opening dialogue used the game’s move command to enter the Volcano and final-battle regions. The encounter actors, attacks and map triggers used the game’s own logic. Two enlarged Fire Drakes appeared at the Volcano encounter. A visible side idle matched the revised 11006 frame at native pixel scale. In the final battle, all 299 screen samples carrying the Tarrasque’s turn label contained a match to the corrected artwork, including the side swing and recovery. Each sample was checked against the registered silhouettes and palette pixels. The lowest match covered 315 of 500 sampled body pixels, including frames partly covered by other actors. In the captured side hit, the damage number appears over the struck party member below the Tarrasque’s chest. Script inspection independently verified the 43–50 sequence. The replay tracked visible poses without reading the live step counter. [Fire Drakes in the Volcano](img/11006-volcano-replay.gif) · [Tarrasque taking its turn](img/269-encounter-replay.gif) · [Damage placement](img/269-encounter-impact.png)

A second pass deliberately routed every melee facing to the forward attack in a temporary test copy. Only three slot entries in each half’s script changed for this test. The released frame banks and all 57 step records were used as packaged. The Tarrasque was visible in all 293 samples of its turns. The image comparison identified each of the three attack drawings in 28 samples, covering the held pairs at steps 44–45, 46–47 and 48–49. [Watch the targeted forward attack](img/269-forward-attack-check.gif)

**Tarrasque walk in RGN044.** In the earlier replay, screen samples 16–48 show the same side drawing while the Tarrasque advances four squares relative to the floor. Each side-walk record moved the primary actor by 16 pixels. The revised primary script divides one square into 5, 6 and 5 pixels across the three side poses. The away and toward runs also total one square, across four and six poses respectively. Only the walk displacement bytes in SCMD 11001 changed. In a fresh final battle, all 96 samples of the approach matched the packaged art. Samples 19–95 show six consecutive cycles of base drawings 4, 5 and 6. The archive check covered all eight movement directions. [Watch the revised approach](img/269-encounter-walk.gif)

The scale review accepted regular Air 2538 and Fire 2540 at their native Shattered Lands size, about one and a half times human height. Unassigned axe wielder 3130 retains its approved Ravager scale.

## Earlier playtests

2026-11-24 (Claude). Build: `approved.json` through darksun-recompiled's `import_catalogue.py` (PR #8).
Method and grabs: the Obsidian Edition repository's `playtest/logs/2026-11-24-ravager-catalogue-import.md`.

**Walked and fought in the opening ambush (Tyr), drawn on their anchors and in their colours:**
779, 780, 914, 915, 1412, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1881, 2022, 2394, 2405, 2408,
2469, 2470, 2471, 2557, 2843, 2844, 2845, 2846, 2847, 2849, 2895, 3954, 3955.

**Rooted plants, drawn right:** 2345, 2403.

**Still figures:** seen drawn in Tyr in a stand-in slot; their own scenes are still to be visited
(a still figure can't stand in for the opening's walking people without stalling the scene).

**Subsequent archive checks.** The catalogue importer now installs the [Tarrasque encounter resources](README.md#269-tarrasque) and the [Magma Golem](README.md#693-magma-golem). All 57 paired Tarrasque steps and 52 Magma Golem steps were checked in the rebuilt files. The later campaign results above cover the Tarrasque. The Magma Golem still needs a Volcano Core playtest.
