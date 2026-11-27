# Figure catalogue audit

**All 225 numbered entries approved.** The original register had 195 figures. The census and follow-up comparison added 30, including the two Limbo stills that exactly mirror Crypt body 2931.

[Approved 2489 in its mine placement](img/audit-mines2-2489.png) · [All numbered entries and installation sources](#entry-register) · [Inventory of every stock picture](stock-picture-census.csv) · [Labelled stock contact sheets](img/stock-picture-sheets.zip)

## What the character list missed

| Artwork | Game evidence | Review decision |
| --- | --- | --- |
| Ten standing people, 2480–2489 | Object records 5900–5909 each place one still in Mines2, RGN039. They occupy ten different positions. Six match a catalogued walker frame pixel for pixel, including a mirrored profile. Two more match the outline with different colours. The last two closely resemble the mirrored profiles of 2476 and 2429, both of which have character-specific splits. | All ten stills were reviewed at their map placements. The scenery records supply no race or personal name. Approved still 2480 uses the approved Halfling 2455 because its shipped toward idle matches pixel for pixel. Still 2481 uses the Human fitting of 2422, and 2482 uses the mirrored Dwarf profile from 2423. Still 2483 uses the right-facing 2434 Dwarf. Still 2484 uses the Dwarf woman from 2475, and 2485 uses the Human miner from 2476. Still 2486 uses the recoloured half-giant woman, and 2487 uses the half-giant with the green bandana. Still 2488 uses the rear-facing Halfling villager with grey hair, and 2489 uses the grey-haired Human civilian from 2435. [All ten originals](img/audit-mines2-people.png) · [2480 before, proposal and same-facing SL reference](img/audit-mines2-2480.png) |
| Four fallen figures, 2931–2934, and two fallen mine figures, 3648–3649 | Four bodies cluster at four separate positions in RGN043. Both mine pictures occur repeatedly in RGN039 and once each in Limbo. Four of these six match individual shipped character poses exactly, including a mirrored fallen pose from 2416. | Match the prone pose and clothing in the scene. Several original NPCs share the same fallen drawing, so an exact drawing alone cannot identify a person or their race. [Originals by number](img/audit-map-figures.png) |
| Mirrored fallen figures 1117 and 2533 | A comparison of single-frame OBJEX banks against the fallen silhouettes identified two exact horizontal copies of 2931. Objects 5066 and 2216 have three placements between them in Limbo. | Both use the approved 2931 drawing, mirrored. [Installed comparisons](img/audit-exact-figure-stills.png) |
| 1115, 1142, 1571 and 1602 | The rack includes a captive in both drawings. A stationary golem matches 2394, the rear of an Umber Hulk matches 2555, and the sixth drawing of the rising skeleton matches 1753. All four have map placements. | The approved captive has a matching empty rack. The golem and rear-facing Umber Hulk use their approved drawings. The approved six-frame rise ends on the standing pose of Giant Skeleton 1753. [Original poses](img/audit-map-figures.png) |
| Sickbed 3668 | Its entire three-frame picture bank matches Sicky 917 byte for byte. It has its own seven-step script, drawing anchor and RGN045 placement. | Reused all three approved patient-and-cot drawings. The original canvas, two sequences and timing fit the approved artwork. This records an exact-art reuse and leaves the patient’s identity open. [Original and installed poses at the cot](img/audit-3668-bed.gif) |
| 2779 and 2780 | Each serpent has one frame, an object and a Limbo placement. | The approved stills preserve their lowered heads and use the approved adult snake treatment. [Comparison and Limbo placements](img/audit-serpent-stills.png) Their item records suggest fallen Kartang. Placement after a kill remains unverified. [Original artwork](img/audit-related-art.png) |
| 734, 735, 3130, 3425 and 3426 | These five pictures have no direct shipped object assignment. The first two reproduce the front pose of 2900. The axe wielder has three drawings. The last two reproduce shipped serpent figures 2843 and 1755. | The four exact copies use the approved pictures. The axe wielder uses the approved three-pose redraw. Runtime use and character identity remain open. [Original artwork](img/audit-related-art.png) |

## Import handoff

The 2026-11-27 mod import used asset snapshot `b447d39a0db2a896e0cde11bdfd57a6067e85cdf` in `daaki85/darksun-installation-files`. The tested importer is `013a4e0ee28b56d6fd0f1347938ef35858f7c30f` on the `claude/catalogue-import` branch of `daaki85/darksun-recompiled`. Fresh checkouts supplied the manifest, packages, importer and GFF reader. [Asset manifest](https://github.com/daaki85/darksun-installation-files/blob/b447d39a0db2a896e0cde11bdfd57a6067e85cdf/ravager-figure-redraws/catalogue/approved.json) · [Tested importer](https://github.com/daaki85/darksun-recompiled/blob/013a4e0ee28b56d6fd0f1347938ef35858f7c30f/tools/proto/import_catalogue.py)

For subsequent imports, use the manifest and packages from this revision or later. The baseline archive now carries Notaku’s corrected combat transparency. Only the 2409/combat.chunk member changed. The 12 corrected masks match Shattered Lands picture 385 and survive the mod loader’s edge cleanup pixel for pixel. The proposed Aurumvorax side bite is a separate review package. [Current baseline archive](approved/catalogue-base-figures.zip) · [Mod import #250](https://github.com/daaki85/darksun-obsidian-edition/pull/250)

Apply the catalogue as the last figure-build step. Run the command below from the tested code checkout. Supply the asset checkout’s catalogue directory, the target build’s game data, a separate output directory and the original Ravager game data, in that order. The fourth argument supplies shipped scripts and combat pictures where a package contains only new base drawings. The importer selects packages from all three archive directories in manifest order.

```sh
python3 tools/proto/import_catalogue.py "$CATALOGUE_DIR" "$BASE_DIR" "$OUT_DIR" "$STOCK_DIR"
```

The import produces three files. Deliver all three together.

| Output | Contents checked |
| --- | --- |
| `OBJEX.GFF` | 275 picture IDs and 32 object-to-picture reassignments, including the separate Greater Elementals |
| `RESOURCE.GFF` | Both Tarrasque combat halves, all three drakes and the three Tarrasque cinematic banks containing 33 frames |
| `RGN03A.GFF` | Mines3 dining-room placement table, ETAB 58. The package replaces this table in full. Relative to stock, 25 of its 842 records change. If the destination build has its own edits in that table, reconcile them with those 25 changes. |

Four trial imports passed using stock, the output from the stock trial, an earlier elemental build and an earlier drake build. The importer reported `275 pictures from 149 packages, 32 objects moved, 2 region file(s); 0 problems` each time. The two-file count includes RESOURCE and RGN03A in addition to OBJEX. A separate comparison reopened each output and matched every indexed data payload to the expected input or manifest replacement, excluding archive indexing metadata. Repeating the import produced the same effective payloads. The stock census matched all 3,974 OBJEX and RESOURCE picture rows, the 4,479 object assignments and the placement counts across 20 regions. These checks cover archive integration. Encounter playback observations are tracked separately. [In-game checks](in-game-checks.md)

## What the import now installs

The new baseline package makes nine party pictures, dressed Halflings 650 and 651, and Notaku 2409 explicit. A second manifest entry selects regular Air 2538 and Fire 2540 from the already reviewed elemental package, including their Ravager-compatible scripts. Previously these **14 approved figures** depended on an earlier stage building the right artwork. The baseline package also protects the three approved originals 849, 1736 and 2395 when importing over an older build. The Human merchants on 691 and Mordenk’s Sword on 3238 already had explicit stock packages. [Baseline assets](approved/catalogue-base-figures.zip) · [Regular elemental assets](proposals/elemental-tiers.zip) · [Manifest and precedence](approved.json)

Notaku’s donor contained one extra action pointing past the end of its combat bank. His shipped Ravager script has no action in slot 32. The installed version leaves it empty and retains every valid donor step, including all four standing facings. The raw donor scripts for regular Air and Fire also contained out-of-range references. Their previously approved elemental-tier scripts resolve them.

Three full imports passed, starting from the stock archives, the result of the first import, and an earlier elemental build. Each produced the selected artwork for **275 OBJEX pictures** plus **five RESOURCE encounter pictures and three cinematic banks**. The OBJEX count includes scenery components and separate pictures for shared characters. It is a different measure from the number of catalogue entries.

- Reopened each archive and compared the effective package contents, including stock fallbacks, in manifest order. **5,249 stored frames** decoded and **11,050 script records** resolved across OBJEX and the eight RESOURCE pictures. Every populated action slot landed inside its script.
- Checked all 4,479 shipped object definitions. Exactly the 32 registered picture assignments changed. The 1,643 shipped character and item data records remained byte-identical. The dining-room placement chunk and the Tarrasque and drake encounter chunks matched their packages.
- Compared the first displayed idle in each available cardinal facing with its shipped counterpart, applying its mirror flag and trimming transparent margins. Exact stock matches occurred only on the five explicitly retained pictures, 691, 849, 1736, 2395 and 3238. This checks for an accidental return to an original idle. The visual review of fit, texture and posture still rests on the individual comparisons.
- Checked local catalogue media and package links, repaired three old heading links, decoded 10,089 frames in 622 GIFs and 615 PNGs, and tested all 267 ZIPs for read errors. Historical before-and-after studies are preserved. An entry’s installation source below identifies the effective package when its earlier studies show different artwork.

## How coverage was checked

The census started again from the installed game archives, independently of the catalogue list. OBJEX contains **3,727 base pictures, 538 animation scripts and 130 combat banks**. Every combat bank already had a numbered entry. All 4,479 object definitions resolve to a base picture. Of 410 combat and small-character records, 402 have a direct object definition, pointing to 189 distinct pictures. All 189 were in the original catalogue.

The other eight character-data records have no same-number object definition. They are Prisoner (93), Jumper (101), Jhathar (193), and unnamed records 216, 231, 232, 233 and 450. They establish no additional picture assignment. A different Prisoner record, 238, already uses 2414.

The placement pass read all 20 shipped region files, including Limbo. The regions store tiles and placements and draw these objects from OBJEX. The installed character-save and runtime-state archives supply no additional sprite banks. For the 3,534 OBJEX base pictures outside the original entries, the review used first-frame sheets, final-frame sheets for all 360 multi-frame banks, targeted intermediate poses, and comparisons of decoded indexed pixels and silhouettes against all stored frames of the original entries. A static placement establishes where a picture can be drawn. Script activation, palette changes and visibility in an actual encounter still require playback.

The CSV records the archive name, picture ID, base and combat frame counts, script length, stock object IDs, map placement counts and review disposition for every OBJEX and RESOURCE picture. Counts in Limbo are shown separately from other regions. [Machine-readable census](stock-picture-census.csv) · [Original-picture contact sheets](img/stock-picture-sheets.zip) · [Live checks already performed](in-game-checks.md)

## Tarrasque and other RESOURCE art

The approved fight uses RESOURCE 11001 and 11002. The stock OBJEX silhouette 269 belongs to object 430 in Limbo. RESOURCE also contains **11012 (15 frames), 11013 (13 frames) and 11014 (five full-screen frames)** depicting the Tarrasque. They are separate from both halves of the approved combat actor. The shipped executable loads the three banks in this order and iterates through their frames. The whole creature faces the viewer as its tail sweeps overhead, the framing closes on the head, and the red eye fills the screen. The approved seventh cinematic pass uses the battle figure and is installed by the catalogue importer. Its exact gameplay trigger and display palette still need confirmation. [All 33 original frames in playback order](img/269-cinematic-frames.png) The sheet uses a common encounter palette for identification. [Side-by-side animation](img/269-cinematic-and-battle.gif) pairs all 33 cinematic frames with the approved forward-facing idle, walk and strike. Both panels use the RGN044 encounter palette and the same magnification. The preview holds each cinematic drawing for 240 ms and pauses on the last frame for inspection. [Five banks side by side](img/audit-tarrasque-resources.png) · [Approved combat playback](img/269-package-playback.gif)

The approved cinematic preserves the dimensions, drawing count, packed format and bit depth of every original frame. The comparison was decoded after inserting the three replacement chunks into a test copy of RESOURCE.GFF. All 33 indexed frames matched the drawings supplied to the encoder. Live playback still needs to confirm the flash, palette and pacing. The third pass follows the original eye-only movement after the exact hold in frames 16–17, the burst beneath the jaw in frame 23 and the roll across the white field. [Frame-by-frame comparison](269-cinematic-review.md) · [Third proposal](img/269-cinematic-redraw-v3.gif) · [Second proposal](img/269-cinematic-redraw-v2.gif) · [First proposal](img/269-cinematic-redraw.gif)

The fourth pass repairs the holes above both shoulders, gives the second tail drawing an uninterrupted taper, and reduces the red in frame 19 to four pixels. All fourteen opening silhouettes each form one connected component after decoding. Frames 27–30 let the white field break through the head along its turn. The final frame uses the original unfiltered pupil and reflection edges. [Fourth pass playback](img/269-cinematic-redraw-v4.gif)

The fifth pass removes the curved band introduced by the shoulder repair. The packed opening frames were decoded and compared on a light background. The tail and body form one connected silhouette across frames 01–14, and the interiors of both shoulders remain opaque through the held crouch. [Enlarged shoulder comparison](img/269-cinematic-shoulders-v5.gif) · [Fifth pass playback](img/269-cinematic-redraw-v5.gif)

The sixth pass retouches the trailing tail in frames 10, 11, 13, 15 and 23 and carries the held curl across 16–22. The tail tips were checked for connectivity in the decoded sprites, and frames 16 and 17 still display the same drawing. [Five enlarged comparisons](img/269-cinematic-tail-v6.png) · [Sixth pass playback](img/269-cinematic-redraw-v6.gif)

The seventh pass fills pinholes in the mane shadow and removes a detached pixel in each of frames 22 and 23. All 33 drawings round-tripped through a rebuilt test archive. Frames 16 and 17 retain their exact hold. Frames 24–33 match the sixth pass pixel for pixel. [Detail sheet](img/269-cinematic-final-detail.png) · [Current playback](img/269-cinematic-redraw-v7.gif) · [Approved banks](proposed/269-tarrasque-cinematic-v7.zip)

RESOURCE contains 247 base pictures, six combat banks and five animation scripts. All five scripted actors are packaged, including drakes 11005–11007. The sixth combat bank, 13009, accompanies a small front-facing body and body-part drawings among interface resources. It has no RESOURCE action script. The archive also includes character-selection art, maps and full-screen illustrations. These remain identified separately from the in-world actors.

## Other artwork to check in context

The following picture IDs are retained in the census. Their subject, purpose or independent use needs different evidence from a character’s standing or walking figure. They do not add to the numbered figure count.

| Pictures | What the stored drawings show and what still needs checking |
| --- | --- |
| 795, 1259, 1361, 1572, 1720–1723 | An occupied burrow or nest, a coloured fixture, a red humanoid silhouette, dark tendrils, and four poses of a sculpted figure holding objects. Check the placement and palette before assigning a creature or redrawing the furnishing. |
| 2404, 2547, 2728, 3221, 3308–3309 | A fragmenting pink shape, a spectral or flame-shaped effect, a sprawled coloured figure in Limbo, a three-frame stump-and-figure picture, and two coloured silhouettes. The census records which have direct game objects. |
| 3486, 3738 | A vertical fixture with two head-like shapes, and a five-frame stone-ring assembly with a moving central detail. Inspect the assembled scenes before deciding whether the central detail represents a person. |
| 1143, 1328–1333, 1337, 2545, 3126–3128, 3298, 3740, 3744–3751, 3897 | Figure-shaped scenery includes stone figures, wrapped forms on posts and a transformation ending on a statue. Review them with their plinths, props and scene scale where appropriate. |
| 582–588, 627, 2219, 2574, 3427, 3787 | Beds, coverings and an empty chair deserve continuity checks beside changed occupants. Unassigned 3427 matches the empty-chair frame 8 of Melantha 2783. A matching bed outline alone is insufficient evidence that it depicts the same patient. |
| 619–621, 1094–1096, 1603, 1878–1879, 2717–2719, 2782, 3428–3429, 3561–3573 | Rope or tendril shapes, skeletal remains, branches, stone and moving props. Several are animated. The six dark shapes 3568–3573, for example, share the bright tip of the surrounding fixture designs. |

[Selected ambiguous and related drawings](img/audit-related-art.png)

## Entry register

Each row links to its catalogue review. Frame counts are base drawings / combat drawings / script records from the reopened archive. A zero in the last column of counts means the picture is stored without an action script. The installed package column follows the last applicable manifest entry for that picture. Object-specific variants appear after the numbered entries.

| Figure and review | Decision | Frames / combat / steps | Installation source |
| --- | --- | ---: | --- |
| [25 Human male party figure (object 300)](README.md#25-human-male-party-figure-object-300) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [269 Tarrasque](README.md#269-tarrasque) | Approved battle | paired banks | [269 encounter](approved/269-tarrasque-encounter.zip) |
| [448 Human female party figure (object 301)](README.md#448-human-female-party-figure-object-301) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [592 Dwarf male party figure (object 302)](README.md#592-dwarf-male-party-figure-object-302) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [593 Dwarf female party figure (object 303)](README.md#593-dwarf-female-party-figure-object-303) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [594 Halfling male party figure (object 310)](README.md#594-halfling-male-party-figure-object-310) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [595 Halfling female party figure (object 311)](README.md#595-halfling-female-party-figure-object-311) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [596 Mul party figure (object 312)](README.md#596-mul-party-figure-object-312) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [598 Half-giant male party figure (object 308)](README.md#598-half-giant-male-party-figure-object-308) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [599 Elf female party figure (object 305)](README.md#599-elf-female-party-figure-object-305) | Approved | 15 / 14 / 70 | [599-obsidian-party-elf](proposals/599-obsidian-party-elf.zip) |
| [649 Cleave on his sickbed](README.md#649-cleave-on-his-sickbed) | Approved | 1 / 0 / 0 | [649-cleave-sickbed](proposals/649-cleave-sickbed.zip) |
| [650 small villager, green shirt (halfling-sized)](README.md#650-small-villager-green-shirt-halfling-sized) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [651 small villager, red (halfling-sized)](README.md#651-small-villager-red-halfling-sized) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [691 Elf male party figure (object 304)](README.md#691-elf-male-party-figure-object-304) | Approved | 14 / 13 / 73 | [691-human-merchants-stock](approved/691-human-merchants-stock.zip) · [player 3961](proposals/3961-obsidian-party-elf.zip) |
| [692 Half-giant female party figure (object 309)](README.md#692-half-giant-female-party-figure-object-309) | Approved | 15 / 14 / 70 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [693 Magma Golem](README.md#693-magma-golem) | Approved | 18 / 6 / 52 | [693-magma-golem](approved/693-magma-golem.zip) |
| [714 innkeeper, teal (behind a counter, no walking)](README.md#714-innkeeper-teal-behind-a-counter-no-walking) | Approved | 2 / 0 / 3 | [714-human-woman-hair](proposals/714-human-woman-hair.zip) |
| [715 shopkeeper, dark (no walking)](README.md#715-shopkeeper-dark-no-walking) | Approved | 2 / 0 / 3 | [715-sl-shoulder](proposals/715-sl-shoulder.zip) |
| [716 beggar, seated](README.md#716-beggar-seated) | Approved | 7 / 0 / 8 | [716-seated-gesture](proposals/716-seated-gesture.zip) |
| [718 man, teal, holding cloth (no walking)](README.md#718-man-teal-holding-cloth-no-walking) | Approved | 4 / 0 / 5 | [718-angle](proposals/718-angle.zip) |
| [719 merchant woman, purple robe (no walking)](README.md#719-merchant-woman-purple-robe-no-walking) | Approved | 2 / 0 / 3 | [719-merchant](proposals/719-merchant.zip) |
| [720 merchant, black (no walking)](README.md#720-merchant-black-no-walking) | Approved | 2 / 0 / 3 | [merchant-batch](proposals/merchant-batch.zip) |
| [721 woman, pink dress (no walking)](README.md#721-woman-pink-dress-no-walking) | Approved | 2 / 0 / 3 | [merchant-batch](proposals/merchant-batch.zip) |
| [722 merchant, black (no walking)](README.md#722-merchant-black-no-walking) | Approved | 2 / 0 / 3 | [merchant-batch](proposals/merchant-batch.zip) |
| [734 Unassigned front pose, copy A](README.md#734-unassigned-front-pose-copy-a) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [735 Unassigned front pose, copy B](README.md#735-unassigned-front-pose-copy-b) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [745 Donno](README.md#745-donno) | Approved | 1 / 0 / 0 | [merchant-batch-contrast](proposals/merchant-batch-contrast.zip) |
| [746 Snake](README.md#746-snake) | Approved | 1 / 0 / 0 | [merchant-batch](proposals/merchant-batch.zip) |
| [747 Leaftop](README.md#747-leaftop) | Approved | 2 / 0 / 3 | [747-leaftop-sl](proposals/747-leaftop-sl.zip) |
| [779 Half-elf female party figure (object 307)](README.md#779-half-elf-female-party-figure-object-307) | Approved | 15 / 14 / 70 | [779-obsidian-half-elf](proposals/779-obsidian-half-elf.zip) |
| [780 Half-elf male party figure (object 306)](README.md#780-half-elf-male-party-figure-object-306) | Approved | 15 / 14 / 70 | [780-obsidian-half-elf](proposals/780-obsidian-half-elf.zip) |
| [787 Pavis](README.md#787-pavis) | Approved | 3 / 0 / 4 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [788 Tantris](README.md#788-tantris) | Approved | 2 / 0 / 3 | [alternate-pose-continuity](proposals/alternate-pose-continuity.zip) |
| [818 Helmine](README.md#818-helmine) | Approved | 3 / 0 / 10 | [helmine-matched](approved/helmine-matched.zip) |
| [849 Garzak, Psurlon](README.md#849-garzak-psurlon) | Approved | 18 / 6 / 52 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [914 beast-headed giant, skull head, loincloth](README.md#914-beast-headed-giant-skull-head-loincloth) | Approved | 30 / 22 / 123 | [914-ptar](approved/914-ptar.zip) |
| [915 Regular Water Elemental](README.md#915-regular-water-elemental) | Approved | 15 / 9 / 60 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |
| [917 Sicky](README.md#917-sicky) | Approved | 3 / 0 / 4 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [918 Blick's Uncle](README.md#918-blicks-uncle) | Approved | 3 / 0 / 3 | [918-blick-second-pass](proposals/918-blick-second-pass.zip) |
| [1115 Captive on the upright rack](README.md#1115-captive-on-the-upright-rack) | Approved | 2 / 0 / 3 | [Captive and rack](proposals/1115-captive-and-rack.zip) |
| [1117 Mirrored fallen figure in Limbo](README.md#1117-mirrored-fallen-figure-in-limbo) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [1142 Stationary Obsidian Golem picture](README.md#1142-stationary-obsidian-golem-picture) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [1160 Nnamdi](README.md#1160-nnamdi) | Approved | 4 / 0 / 23 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [1161 Aleka](README.md#1161-aleka) | Approved | 4 / 0 / 16 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [1247 Sultan](README.md#1247-sultan) | Approved | 3 / 0 / 4 | [1247-sultan](proposals/1247-sultan.zip) |
| [1249 Heroga](README.md#1249-heroga) | Approved | 5 / 0 / 7 | [1249-heroga-storyteller](proposals/1249-heroga-storyteller.zip) |
| [1268 beast-headed giant, crouched](README.md#1268-beast-headed-giant-crouched) | Approved | 3 / 0 / 4 | [four-giant-figures](approved/four-giant-figures.zip) |
| [1269 Magnolia](README.md#1269-magnolia) | Approved | 4 / 0 / 5 | [merchant-batch](proposals/merchant-batch.zip) |
| [1412 beast-headed giant, horned, loincloth](README.md#1412-beast-headed-giant-horned-loincloth) | Approved | 34 / 19 / 124 | [1412-horned-beasthead](proposals/1412-horned-beasthead.zip) |
| [1475 Asquire](README.md#1475-asquire) | Approved | 4 / 0 / 5 | [1475-asquire-stance](proposals/1475-asquire-stance.zip) |
| [1476 Ludwig](README.md#1476-ludwig) | Approved | 5 / 0 / 13 | [1476-ludwig-stance](proposals/1476-ludwig-stance.zip) |
| [1477 Fletch](README.md#1477-fletch) | Approved | 2 / 0 / 5 | [1477-fletch-chair](proposals/1477-fletch-chair.zip) |
| [1478 Parrot](README.md#1478-parrot) | Approved | 1 / 0 / 0 | [merchant-batch-contrast](proposals/merchant-batch-contrast.zip) |
| [1479 Ikibod](README.md#1479-ikibod) | Approved | 4 / 0 / 10 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [1571 Rear-view Umber Hulk picture](README.md#1571-rear-view-umber-hulk-picture) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [1602 Skeleton rising from scattered bones](README.md#1602-skeleton-rising-from-scattered-bones) | Approved | 6 / 0 / 6 | [Rising skeleton](proposals/1602-rising-skeleton.zip) |
| [1617 Kovar](README.md#1617-kovar) | Approved | 4 / 0 / 5 | [1617-kovar](proposals/1617-kovar.zip) |
| [1736 Bit o'Tarrasque](README.md#1736-bit-otarrasque) | Approved | 1 / 0 / 36 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [1753 skeleton (white bones)](README.md#1753-skeleton-white-bones) | Approved | 34 / 12 / 71 | [1753-giant-matched](proposals/1753-giant-matched.zip) |
| [1754 skeleton warrior, red cloak, sword](README.md#1754-skeleton-warrior-red-cloak-sword) | Approved | 33 / 17 / 79 | [1754-warrior](proposals/1754-warrior.zip) |
| [1755 yuan-ti (purple serpent)](README.md#1755-yuan-ti-purple-serpent) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [1756 giant snake (white)](README.md#1756-giant-snake-white) | Approved | 15 / 12 / 56 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [1757 snake (orange)](README.md#1757-snake-orange) | Approved | 15 / 12 / 56 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [1758 snake (teal)](README.md#1758-snake-teal) | Approved | 15 / 12 / 56 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [1759 Int. Devourer, Int.Devourer](README.md#1759-int-devourer-intdevourer) | Approved | 11 / 0 / 44 | [1759-intellect-devourer](proposals/1759-intellect-devourer.zip) |
| [1881 Regular Earth Elemental](README.md#1881-regular-earth-elemental) | Approved | 15 / 9 / 66 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |
| [2022 big woman, orange hair](README.md#2022-big-woman-orange-hair) | Approved | 15 / 14 / 72 | [2022-melody-shoulder](proposals/2022-melody-shoulder.zip) |
| [2345 sundew (plant blob)](README.md#2345-sundew-plant-blob) | Approved | 2 / 18 / 34 | [2345-sundew-fibres](proposals/2345-sundew-fibres.zip) |
| [2394 obsidian golem (black)](README.md#2394-obsidian-golem-black) | Approved | 20 / 9 / 52 | [2394-obsidian-golem](proposals/2394-obsidian-golem.zip) |
| [2395 Dust devil](README.md#2395-dust-devil) | Approved | 5 / 3 / 52 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [2403 snappersaw (spiky plant)](README.md#2403-snappersaw-spiky-plant) | Approved | 1 / 5 / 52 | [2403-snappersaw](proposals/2403-snappersaw.zip) |
| [2405 greater air elemental (white cloud)](README.md#2405-greater-air-elemental-white-cloud) | Approved | 16 / 29 / 84 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |
| [2408 Caravan Master, Miner and Guard (purple sash)](README.md#2408-caravan-master-miner-and-guard-purple-sash) | Approved | 22 / 16 / 72 | [2408-texture-motion](proposals/2408-texture-motion.zip) |
| [2409 Notaku, elven merchant in Tyr](README.md#2409-notaku-elven-merchant-in-tyr) | Approved | 15 / 12 / 69 | [catalogue-base-figures](approved/catalogue-base-figures.zip) |
| [2410 Fayina, the woman who owes Acar](README.md#2410-fayina-the-woman-who-owes-acar) | Approved | 18 / 16 / 72 | [2410-fayina-level-motion](proposals/2410-fayina-level-motion.zip) |
| [2411 Thief, man with a red headband and white shoulder wrap](README.md#2411-thief-man-with-a-red-headband-and-white-shoulder-wrap) | Approved | 24 / 16 / 72 | [2411-thief-fitted-motion](proposals/2411-thief-fitted-motion.zip) |
| [2412 dark-skinned man, black shorts](README.md#2412-dark-skinned-man-black-shorts) | Approved | 22 / 16 / 72 | [2412-cape-windup-motion](proposals/2412-cape-windup-motion.zip) |
| [2413 jann (blue skin, yellow trousers)](README.md#2413-jann-blue-skin-yellow-trousers) | Approved | 26 / 14 / 72 | [2413-jann-gait-motion](proposals/2413-jann-gait-motion.zip) |
| [2414 man, red shirt (Draxan soldier)](README.md#2414-man-red-shirt-draxan-soldier) | Approved | 16 / 18 / 72 | [2414-draxan-rear-motion](proposals/2414-draxan-rear-motion.zip) |
| [2415 man, purple and red](README.md#2415-man-purple-and-red) | Approved | 16 / 14 / 64 | [2415-human-halik-open-neck](proposals/2415-human-halik-open-neck.zip) |
| [2416 dark-skinned woman, orange robe](README.md#2416-dark-skinned-woman-orange-robe) | Approved | 15 / 14 / 70 | [2416-half-elf-woman](approved/2416-half-elf-woman.zip) |
| [2417 blonde woman, green skirt](README.md#2417-blonde-woman-green-skirt) | Approved | 18 / 12 / 64 | [2417-human-halfling](approved/2417-human-halfling.zip) |
| [2419 dark-skinned man in black](README.md#2419-dark-skinned-man-in-black) | Approved | 22 / 21 / 72 | [2419-hanging-folds-motion](proposals/2419-hanging-folds-motion.zip) |
| [2420 Templar, Boric, Kovar and Kalaobuta (Human)](README.md#2420-templar-boric-kovar-and-kalaobuta-human) | Approved | 16 / 18 / 72 | [2420-violet-mantle-motion](proposals/2420-violet-mantle-motion.zip) |
| [2421 Warrior and Tyrian Soldiers (Mul)](README.md#2421-warrior-and-tyrian-soldiers-mul) | Approved | 16 / 18 / 72 | [2421-turned-hem-motion](proposals/2421-turned-hem-motion.zip) |
| [2422 Miners, Winchester, Slave, Ladel and Warrior (Human and Dwarf)](README.md#2422-miners-winchester-slave-ladel-and-warrior-human-and-dwarf) | Approved | 15 / 17 / 64 | [2422-human-dwarf-hipfit](proposals/2422-human-dwarf-hipfit.zip) |
| [2423 Mug, Arslan and Slave (Dwarf)](README.md#2423-mug-arslan-and-slave-dwarf) | Approved | 15 / 17 / 64 | [2423-dwarf-red-wrap](proposals/2423-dwarf-red-wrap.zip) |
| [2424 Receptionist (Human)](README.md#2424-receptionist-human) | Approved | 27 / 0 / 0 | [2424-receptionist-sash](proposals/2424-receptionist-sash.zip) |
| [2425 Fermin and Defiler (Human)](README.md#2425-fermin-and-defiler-human) | Approved | 18 / 13 / 72 | [2425-defiler-charcoal](proposals/2425-defiler-charcoal.zip) |
| [2426 Preserver and VA Member (Elf)](README.md#2426-preserver-and-va-member-elf) | Approved | 17 / 14 / 72 | [2426-obsidian-ears](proposals/2426-obsidian-ears.zip) |
| [2427 Draxans, Templars, Kranix, Jumah, Zorani and Deathraker](README.md#2427-draxans-templars-kranix-jumah-zorani-and-deathraker) | Approved | 18 / 13 / 72 | [2427-fitted-mantles](proposals/2427-fitted-mantles.zip) |
| [2428 Draxans and Gladiators (Mul), with a separate Human Draxan](README.md#2428-draxans-and-gladiators-mul-with-a-separate-human-draxan) | Approved | 18 / 14 / 72 | [2428-ochre-wraps](proposals/2428-ochre-wraps.zip) |
| [2429 huge muscular man, green bands (half-giant)](README.md#2429-huge-muscular-man-green-bands-half-giant) | Approved | 15 / 14 / 72 | [2429-elevator-miner-tunic](proposals/2429-elevator-miner-tunic.zip) |
| [2430 woman, teal dress](README.md#2430-woman-teal-dress) | Approved | 18 / 13 / 72 | [2430-human-teal-dress](proposals/2430-human-teal-dress.zip) |
| [2431 man, blue shirt](README.md#2431-man-blue-shirt) | Approved | 18 / 13 / 72 | [2431-ulbin-blue-shirt](proposals/2431-ulbin-blue-shirt.zip) |
| [2432 man, green tunic](README.md#2432-man-green-tunic) | Approved | 19 / 13 / 72 | [2432-wren-elf-tunic](proposals/2432-wren-elf-tunic.zip) |
| [2433 man, purple robe](README.md#2433-man-purple-robe) | Approved | 18 / 13 / 72 | [2433-blick-plum-tunic](proposals/2433-blick-plum-tunic.zip) |
| [2434 dark-haired man, bare chest](README.md#2434-dark-haired-man-bare-chest) | Approved | 19 / 11 / 64 | [2434-dwarf-work-wrap](proposals/2434-dwarf-work-wrap.zip) |
| [2435 grey-haired man](README.md#2435-grey-haired-man) | Approved | 21 / 10 / 64 | [2435-granger-civilian](proposals/2435-granger-civilian.zip) |
| [2436 bald man, pink loincloth](README.md#2436-bald-man-pink-loincloth) | Approved | 20 / 11 / 72 | [2436-rose-work-wraps](proposals/2436-rose-work-wraps.zip) |
| [2437 Slave and Brainsniffer, Human man in teal](README.md#2437-slave-and-brainsniffer-human-man-in-teal) | Approved | 16 / 15 / 72 | [2437-fitted-bandana](proposals/2437-fitted-bandana.zip) |
| [2438 woman, red top, teal skirt](README.md#2438-woman-red-top-teal-skirt) | Approved | 23 / 8 / 64 | [2438-drisha-and-guards](proposals/2438-drisha-and-guards.zip) |
| [2439 woman, purple](README.md#2439-woman-purple) | Approved | 18 / 13 / 72 | [2439-victim-rose-mantle](proposals/2439-victim-rose-mantle.zip) |
| [2451 small dark-haired man](README.md#2451-small-dark-haired-man) | Approved | 16 / 15 / 72 | [2451-halfling-walkers](proposals/2451-halfling-walkers.zip) |
| [2452 Runner, Firegazer and Axestopper](README.md#2452-runner-firegazer-and-axestopper) | Approved | 15 / 14 / 72 | [2452-humbleton-halflings](proposals/2452-humbleton-halflings.zip) |
| [2453 Dmitri and the Veiled Alliance member](README.md#2453-dmitri-and-the-veiled-alliance-member) | Approved | 15 / 14 / 64 | [2453-dmitri-alliance](proposals/2453-dmitri-alliance.zip) |
| [2454 Halla, Glade, Irma and Dodger](README.md#2454-halla-glade-irma-and-dodger) | Approved | 15 / 14 / 72 | [2454-humbleton-halflings](proposals/2454-humbleton-halflings.zip) |
| [2455 Sureshot, Ash and the unnamed Halfling](README.md#2455-sureshot-ash-and-the-unnamed-halfling) | Approved | 15 / 14 / 72 | [2455-humbleton-halflings](proposals/2455-humbleton-halflings.zip) |
| [2456 Dariya and Silvain](README.md#2456-dariya-and-silvain) | Approved | 15 / 14 / 72 | [2456-dariya-silvain-texture](proposals/2456-dariya-silvain-texture.zip) |
| [2457 jann (blue skin, yellow)](README.md#2457-jann-blue-skin-yellow) | Approved | 27 / 14 / 72 | [2457-jann-camp-family](proposals/2457-jann-camp-family.zip) |
| [2458 jann (blue skin, orange)](README.md#2458-jann-blue-skin-orange) | Approved | 27 / 14 / 72 | [2457-jann-camp-family](proposals/2457-jann-camp-family.zip) |
| [2459 jann (blue skin, grey)](README.md#2459-jann-blue-skin-grey) | Approved | 27 / 14 / 72 | [2457-jann-camp-family](proposals/2457-jann-camp-family.zip) |
| [2460 jann (blue skin, green)](README.md#2460-jann-blue-skin-green) | Approved | 27 / 14 / 72 | [2457-jann-camp-family](proposals/2457-jann-camp-family.zip) |
| [2461 Surrakina](README.md#2461-surrakina) | Approved | 15 / 14 / 72 | [2461-surrakina](proposals/2461-surrakina.zip) |
| [2462 Warrior at El’s Temple](README.md#2462-warrior-at-els-temple) | Approved | 18 / 13 / 72 | [2462-warrior-woman](proposals/2462-warrior-woman.zip) |
| [2463 Raenika and the Merchant](README.md#2463-raenika-and-the-merchant) | Approved | 18 / 13 / 72 | [2463-raenika-white-gown](proposals/2463-raenika-white-gown.zip) |
| [2464 man, blue shirt](README.md#2464-man-blue-shirt) | Approved | 18 / 13 / 72 | [2464-blue-shirt](proposals/2464-blue-shirt.zip) |
| [2466 white-haired old man, purple robe](README.md#2466-white-haired-old-man-purple-robe) | Approved | 15 / 9 / 64 | [alternate-pose-continuity](proposals/alternate-pose-continuity.zip) |
| [2467 Romila Parthian](README.md#2467-romila-parthian) | Approved | 18 / 16 / 72 | [2467-romila-detail](proposals/2467-romila-detail.zip) |
| [2468 Matthias Morthen](README.md#2468-matthias-morthen) | Approved | 21 / 10 / 64 | [2468-matthias](proposals/2468-matthias.zip) |
| [2469 huge bald muscular man](README.md#2469-huge-bald-muscular-man) | Approved | 27 / 15 / 120 | [2469-village-giant-planted-idles](proposals/2469-village-giant-planted-idles.zip) |
| [2470 big woman, red hair, purple](README.md#2470-big-woman-red-hair-purple) | Approved | 27 / 15 / 120 | [2469-village-giant-planted-idles](proposals/2469-village-giant-planted-idles.zip) |
| [2471 big woman, dark hair, teal](README.md#2471-big-woman-dark-hair-teal) | Approved | 15 / 14 / 72 | [helmine-matched](approved/helmine-matched.zip) |
| [2472 Melantha standing](README.md#2472-melantha-standing) | Approved | 18 / 15 / 72 | [2472-melantha-fitted-robe](proposals/2472-melantha-fitted-robe.zip) |
| [2473 Aravinda](README.md#2473-aravinda) | Approved | 23 / 8 / 64 | [2473-aravinda](proposals/2473-aravinda.zip) |
| [2474 El and the Silt Sea Leader](README.md#2474-el-and-the-silt-sea-leader) | Approved | 18 / 13 / 72 | [2474-el-leader](proposals/2474-el-leader.zip) |
| [2475 woman, purple](README.md#2475-woman-purple) | Approved | 15 / 14 / 60 | [2475-dwarf-open-collar](proposals/2475-dwarf-open-collar.zip) |
| [2476 Human and Dwarf miners](README.md#2476-human-and-dwarf-miners) | Approved | 19 / 11 / 60 | [2476-human-and-dwarf-miners](proposals/2476-human-and-dwarf-miners.zip) |
| [2479 Miner](README.md#2479-miner) | Approved | 2 / 0 / 3 | [2479-miner](proposals/2479-miner.zip) |
| [2480 Mines2 standing figure 1](README.md#2480-mines2-standing-figure-1) | Approved | 1 / 0 / 0 | [2480-mines2-still](proposals/2480-mines2-still.zip) |
| [2481 Mines2 standing figure 2](README.md#2481-mines2-standing-figure-2) | Approved | 1 / 0 / 0 | [2481 mine still](proposals/2481-mines2-still.zip) |
| [2482 Mines2 standing figure 3](README.md#2482-mines2-standing-figure-3) | Approved | 1 / 0 / 0 | [2482 mine still](proposals/2482-mines2-still.zip) |
| [2483 Mines2 standing figure 4](README.md#2483-mines2-standing-figure-4) | Approved | 1 / 0 / 0 | [2483 mine still](proposals/2483-mines2-still.zip) |
| [2484 Mines2 standing figure 5](README.md#2484-mines2-standing-figure-5) | Approved | 1 / 0 / 0 | [2484 mine still](proposals/2484-mines2-still.zip) |
| [2485 Mines2 standing figure 6](README.md#2485-mines2-standing-figure-6) | Approved | 1 / 0 / 0 | [2485 mine still](proposals/2485-mines2-still.zip) |
| [2486 Mines2 standing figure 7](README.md#2486-mines2-standing-figure-7) | Approved | 1 / 0 / 0 | [2486 mine still](proposals/2486-mines2-still.zip) |
| [2487 Mines2 standing figure 8](README.md#2487-mines2-standing-figure-8) | Approved | 1 / 0 / 0 | [2487 mine still](proposals/2487-mines2-still.zip) |
| [2488 Mines2 standing figure 9](README.md#2488-mines2-standing-figure-9) | Approved | 1 / 0 / 0 | [2488 mine still](proposals/2488-mines2-still.zip) |
| [2489 Mines2 standing figure 10](README.md#2489-mines2-standing-figure-10) | Approved | 1 / 0 / 0 | [2489 mine still](proposals/2489-mines2-still.zip) |
| [2526 mushroom lady, crouched](README.md#2526-mushroom-lady-crouched) | Approved | 2 / 0 / 4 | [2526-rattlenook-mushroom-seller](proposals/2526-rattlenook-mushroom-seller.zip) |
| [2533 Mirrored fallen figure in Limbo](README.md#2533-mirrored-fallen-figure-in-limbo) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [2536 revenant (grey ghostly man)](README.md#2536-revenant-grey-ghostly-man) | Approved | 17 / 10 / 64 | [2536-revenant](proposals/2536-revenant.zip) |
| [2537 aurumvorax (small golden beast)](README.md#2537-aurumvorax-small-golden-beast) | Approved | 15 / 6 / 58 | [2537-aurumvorax-revised](proposals/2537-aurumvorax-revised.zip) |
| [2538 Regular Air Elemental](README.md#2538-regular-air-elemental) | Approved | 15 / 9 / 52 | [elemental-tiers](proposals/elemental-tiers.zip) |
| [2539 soulshard (grey stone man)](README.md#2539-soulshard-grey-stone-man) | Approved | 21 / 10 / 64 | [2539-soulshard-strike](proposals/2539-soulshard-strike.zip) |
| [2540 Regular Fire Elemental](README.md#2540-regular-fire-elemental) | Approved | 15 / 9 / 52 | [elemental-tiers](proposals/elemental-tiers.zip) |
| [2541 Unidentified combat sprite](README.md#2541-unidentified-combat-sprite) | Approved | 20 / 13 / 72 | [2541-settled](proposals/2541-settled.zip) |
| [2554 great feyr (tentacled maw)](README.md#2554-great-feyr-tentacled-maw) | Approved | 20 / 11 / 64 | [2554-a-teal-crown](proposals/2554-a-teal-crown.zip) |
| [2555 umber hulk](README.md#2555-umber-hulk) | Approved | 20 / 12 / 66 | [2555-umber-hulk](proposals/2555-umber-hulk.zip) |
| [2556 shambling mound (green)](README.md#2556-shambling-mound-green) | Approved | 22 / 21 / 80 | [2556-shambling-mound](proposals/2556-shambling-mound.zip) |
| [2557 Greater Fire Elemental (flames)](README.md#2557-greater-fire-elemental-flames) | Approved | 5 / 12 / 49 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |
| [2558 Butler and Leader](README.md#2558-butler-and-leader) | Approved | 23 / 14 / 72 | [2558-green-shoulder-cloak](proposals/2558-green-shoulder-cloak.zip) |
| [2570 Zorani, seated cross-legged](README.md#2570-zorani-seated-cross-legged) | Approved | 2 / 0 / 2 | [2570-zorani-matched-mantle](proposals/2570-zorani-matched-mantle.zip) |
| [2572 Utella](README.md#2572-utella) | Approved | 2 / 0 / 3 | [2572-utella-revised](proposals/2572-utella-revised.zip) |
| [2573 Snaggletooth](README.md#2573-snaggletooth) | Approved | 1 / 0 / 0 | [2573-snaggle-sickbed](proposals/2573-snaggle-sickbed.zip) |
| [2575 lord warrior, black armour](README.md#2575-lord-warrior-black-armour) | Approved | 17 / 10 / 64 | [2575-lord-warrior](proposals/2575-lord-warrior.zip) |
| [2577 White Knight](README.md#2577-white-knight) | Approved | 4 / 0 / 5 | [2577-platform-standing](proposals/2577-platform-standing.zip) |
| [2578 Black Knight](README.md#2578-black-knight) | Approved | 4 / 0 / 5 | [2577-platform-standing](proposals/2577-platform-standing.zip) |
| [2727 Baby Snake](README.md#2727-baby-snake) | Approved | 12 / 0 / 13 | [2727-2772-baby-snakes](proposals/2727-2772-baby-snakes.zip) |
| [2772 Baby Snake](README.md#2772-baby-snake) | Approved | 12 / 0 / 9 | [2727-2772-baby-snakes](proposals/2727-2772-baby-snakes.zip) |
| [2778 tavernkeeper, green (no walking)](README.md#2778-tavernkeeper-green-no-walking) | Approved | 4 / 0 / 5 | [merchant-batch](proposals/merchant-batch.zip) |
| [2779 Orange serpent still](README.md#2779-orange-serpent-still) | Approved | 1 / 0 / 0 | [Serpent stills](proposals/2779-2780-serpent-stills.zip) |
| [2780 Turquoise serpent still](README.md#2780-turquoise-serpent-still) | Approved | 1 / 0 / 0 | [Serpent stills](proposals/2779-2780-serpent-stills.zip) |
| [2783 Melantha](README.md#2783-melantha) | Approved | 9 / 0 / 10 | [2783-giant-and-bed](proposals/2783-giant-and-bed.zip) |
| [2843 yuan-ti (red and gold serpent)](README.md#2843-yuan-ti-red-and-gold-serpent) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2844 yuan-ti (red serpent)](README.md#2844-yuan-ti-red-serpent) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2845 serpent (purple)](README.md#2845-serpent-purple) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2846 serpent (teal)](README.md#2846-serpent-teal) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2847 serpent (orange)](README.md#2847-serpent-orange) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2849 serpent (green)](README.md#2849-serpent-green) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2850 verini (tan ape-lizard)](README.md#2850-verini-tan-ape-lizard) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2852 verini (yellow)](README.md#2852-verini-yellow) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2853 verini (dark red)](README.md#2853-verini-dark-red) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2854 verini (grey)](README.md#2854-verini-grey) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2855 verini (white)](README.md#2855-verini-white) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2858 verini (green)](README.md#2858-verini-green) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2859 verini (orange)](README.md#2859-verini-orange) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2860 verini (purple)](README.md#2860-verini-purple) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2861 verini (red)](README.md#2861-verini-red) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2863 verini (brown)](README.md#2863-verini-brown) | Approved | 15 / 16 / 61 | [2850-verini-monster-pass](proposals/2850-verini-monster-pass.zip) |
| [2884 mind flayer, green robe](README.md#2884-mind-flayer-green-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2885 mind flayer, pink robe](README.md#2885-mind-flayer-pink-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2887 mind flayer, orange robe](README.md#2887-mind-flayer-orange-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2888 mind flayer, red robe](README.md#2888-mind-flayer-red-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2889 mind flayer, teal robe](README.md#2889-mind-flayer-teal-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2890 mind flayer, black robe](README.md#2890-mind-flayer-black-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2891 mind flayer, purple robe](README.md#2891-mind-flayer-purple-robe) | Approved | 19 / 15 / 69 | [2884-mind-flayer-robes](proposals/2884-mind-flayer-robes.zip) |
| [2895 yuan-ti (white serpent)](README.md#2895-yuan-ti-white-serpent) | Approved | 15 / 9 / 52 | [approved-yuan-ti-and-snakes](proposals/approved-yuan-ti-and-snakes.zip) |
| [2900 Unidentified combat sprite](README.md#2900-unidentified-combat-sprite) | Approved | 17 / 6 / 26 | [2900-clean-contours](proposals/2900-clean-contours.zip) |
| [2931 Fallen figure in RGN043, pose 1](README.md#2931-fallen-figure-in-rgn043-pose-1) | Approved | 1 / 0 / 0 | [2931 Crypt body](proposals/2931-crypt-body.zip) |
| [2932 Fallen figure in RGN043, pose 2](README.md#2932-fallen-figure-in-rgn043-pose-2) | Approved | 1 / 0 / 0 | [2932 Crypt body](proposals/2932-crypt-body.zip) |
| [2933 Fallen figure in RGN043, pose 3](README.md#2933-fallen-figure-in-rgn043-pose-3) | Approved | 1 / 0 / 0 | [2933 Crypt body](proposals/2933-crypt-body.zip) |
| [2934 Fallen figure in RGN043, pose 4](README.md#2934-fallen-figure-in-rgn043-pose-4) | Approved | 1 / 0 / 0 | [2934 Crypt body](proposals/2934-crypt-body.zip) |
| [3130 Unassigned axe wielder](README.md#3130-unassigned-axe-wielder) | Approved | 3 / 0 / 4 | [Axe wielder](proposals/3130-axe-wielder.zip) |
| [3170 Prisoners](README.md#3170-prisoners) | Approved | 3 / 0 / 4 | [3170-cavern-prisoners](proposals/3170-cavern-prisoners.zip) |
| [3220 Gilad](README.md#3220-gilad) | Approved | 2 / 0 / 3 | [four-giant-figures](approved/four-giant-figures.zip) |
| [3231 Mindflayer](README.md#3231-mindflayer) | Approved | 3 / 0 / 4 | [3231-dining-room](proposals/3231-dining-room.zip) |
| [3238 Mordenk's Sword](README.md#3238-mordenks-sword) | Approved | 11 / 0 / 45 | [3238-original-sword](approved/3238-original-sword.zip) |
| [3312 Air Drake](README.md#3312-air-drake) | Approved | 1 / 0 / 0 | [3312-drakes-raptor-fire](proposals/3312-drakes-raptor-fire.zip) |
| [3313 Fire Drake](README.md#3313-fire-drake) | Approved | 1 / 0 / 0 | [3312-drakes-raptor-fire](proposals/3312-drakes-raptor-fire.zip) |
| [3314 Earth Drake](README.md#3314-earth-drake) | Approved | 1 / 0 / 0 | [3312-drakes-raptor-fire](proposals/3312-drakes-raptor-fire.zip) |
| [3425 Unassigned red and gold serpent](README.md#3425-unassigned-red-and-gold-serpent) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [3426 Unassigned violet and red serpent](README.md#3426-unassigned-violet-and-red-serpent) | Approved | 1 / 0 / 0 | [Exact pose copies](proposals/exact-figure-stills.zip) |
| [3461 Sirah, crouched](README.md#3461-sirah-crouched) | Approved | 4 / 0 / 5 | [3461-sirah-lyceum](proposals/3461-sirah-lyceum.zip) |
| [3509 Rope-vine tree](README.md#3509-rope-vine-tree) | Approved | 2 / 0 / 2 | [3509-rope-vine-tree](proposals/3509-rope-vine-tree.zip) |
| [3511 Elderbrain](README.md#3511-elderbrain) | Approved | 1 / 0 / 0 | [3511-elderbrain](proposals/3511-elderbrain.zip) |
| [3597 Abelard](README.md#3597-abelard) | Approved | 3 / 0 / 7 | [3597-abelard](proposals/3597-abelard.zip) |
| [3605 white knight, silver armour](README.md#3605-white-knight-silver-armour) | Approved | 18 / 13 / 72 | [3605-knights-front-and-rear](proposals/3605-knights-front-and-rear.zip) |
| [3606 black knight, black armour](README.md#3606-black-knight-black-armour) | Approved | 18 / 13 / 72 | [3605-knights-front-and-rear](proposals/3605-knights-front-and-rear.zip) |
| [3612 woman, purple (miner)](README.md#3612-woman-purple-miner) | Approved | 4 / 0 / 5 | [3612-purple-miners](proposals/3612-purple-miners.zip) |
| [3613 miner with pick](README.md#3613-miner-with-pick) | Approved | 2 / 0 / 3 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [3648 Fallen mine figure in grey](README.md#3648-fallen-mine-figure-in-grey) | Approved | 1 / 0 / 0 | [Fallen mine pair](proposals/3648-3649-fallen-miners.zip) |
| [3649 Fallen mine figure in violet](README.md#3649-fallen-mine-figure-in-violet) | Approved | 1 / 0 / 0 | [Fallen mine pair](proposals/3648-3649-fallen-miners.zip) |
| [3668 Patient on the RGN045 cot](README.md#3668-patient-on-the-rgn045-cot) | Approved by reuse | 3 / 0 / 7 | [3668-sickbed](approved/3668-sickbed.zip) |
| [3690 Miric](README.md#3690-miric) | Approved | 1 / 0 / 0 | [3690-miric](proposals/3690-miric.zip) |
| [3777 Wounded Citizen](README.md#3777-wounded-citizen) | Approved | 4 / 0 / 4 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [3778 Wounded Soldier](README.md#3778-wounded-soldier) | Approved | 4 / 0 / 4 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [3779 Sick Guy](README.md#3779-sick-guy) | Approved | 4 / 0 / 5 | [scenery-and-miner](proposals/scenery-and-miner.zip) |
| [3855 Rybochka](README.md#3855-rybochka) | Approved | 28 / 0 / 48 | [3855-directional-pulse](proposals/3855-directional-pulse.zip) |
| [3866 Generoe in his rocking chair](README.md#3866-generoe-in-his-rocking-chair) | Approved | 4 / 0 / 9 | [3866-generoe-chair](proposals/3866-generoe-chair.zip) |
| [3893 Shadow](README.md#3893-shadow) | Approved | 15 / 9 / 64 | [3893-shadow](proposals/3893-shadow.zip) |
| [3917 Thri-kreen party figure (object 313)](README.md#3917-thri-kreen-party-figure-object-313) | Approved | 15 / 14 / 61 | [3917-party-thri-kreen](proposals/3917-party-thri-kreen.zip) |
| [3918 Duplicate of the party Thri-kreen](README.md#3918-duplicate-of-the-party-thri-kreen) | Approved | 15 / 14 / 61 | [3917-party-thri-kreen](proposals/3917-party-thri-kreen.zip) |
| [3954 Greater Earth Elemental (project figure)](README.md#3954-greater-earth-elemental-project-figure) | Approved | 15 / 11 / 66 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |
| [3955 Greater Water Elemental (project figure)](README.md#3955-greater-water-elemental-project-figure) | Approved | 15 / 15 / 60 | [elemental-motion-earth-steady](proposals/elemental-motion-earth-steady.zip) |

### Object-specific variants

| Project picture | Source picture | Object IDs assigned | Installed package |
| --- | --- | --- | --- |
| 3956 | 2415 | 236 | [2415-human-halik-open-neck](proposals/2415-human-halik-open-neck.zip) |
| 3957 | 2417 | 480 | [forest-victim-olive](proposals/forest-victim-olive.zip) |
| 3958 | 2435 | 479 | [forest-victim-olive](proposals/forest-victim-olive.zip) |
| 3959 | 2429 | 481 | [forest-victim-olive](proposals/forest-victim-olive.zip) |
| 3960 | 2422 | 133, 187, 259, 292 | [2422-human-dwarf-hipfit](proposals/2422-human-dwarf-hipfit.zip) |
| 3961 | 691 | 304 | [3961-obsidian-party-elf](proposals/3961-obsidian-party-elf.zip) |
| 3962 | 2427 | 185 | [2427-fitted-mantles](proposals/2427-fitted-mantles.zip) |
| 3963 | 2428 | 367 | [2428-ochre-wraps](proposals/2428-ochre-wraps.zip) |
| 3964 | 2429 | 370 | [2429-fitted-bandanas](proposals/2429-fitted-bandanas.zip) |
| 3965 | 2429 | 237, 243, 249, 299, 492, 509, 510, 511 | [2429-fitted-bandanas](proposals/2429-fitted-bandanas.zip) |
| 3966 | 2436 | 138 | [2436-rose-work-wraps](proposals/2436-rose-work-wraps.zip) |
| 3967 | 2438 | 244, 246 | [2438-drisha-and-guards](proposals/2438-drisha-and-guards.zip) |
| 3968 | 2451 | 99 | [2451-halfling-walkers](proposals/2451-halfling-walkers.zip) |
| 3969 | 651 | 94 | [alternate-pose-continuity](proposals/alternate-pose-continuity.zip) |
| 3970 | 2452 | 83 | [3970-cleave-halfling](proposals/3970-cleave-halfling.zip) |
| 3971 | 2453 | 168 | [2453-dmitri-alliance](proposals/2453-dmitri-alliance.zip) |
| 3972 | 2454 | 88 | [2454-humbleton-halflings](proposals/2454-humbleton-halflings.zip) |
| 3973 | 2456 | 171 | [2456-dariya-silvain-texture](proposals/2456-dariya-silvain-texture.zip) |
| 3974 | 2476 | 491 | [2476-human-and-dwarf-miners](proposals/2476-human-and-dwarf-miners.zip) |

The 32 auxiliary OBJEX pictures comprise 31 scene components listed as “packaged companion” in the stock census and empty rack 1116, listed as “approved captive and rack”. The two Greater Elemental project entries, 3954 and 3955, have their own numbered reviews.
