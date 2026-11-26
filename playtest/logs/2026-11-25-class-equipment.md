# Weapon and armor tests in the slave pens

Tested the class-outfits branch at `d37475e` with disposable copies of the `pens-after-arena` save.

## Live equipment changes

With the party on the map in DOSBox, attached the Loader's Dresser. Recorded each subject's empty-slot walking and combat pictures. Equipped an ordinary sword in the right hand, removed it, then equipped and removed a chest plate. At each step read both BMP chunks from the Loader's live SEGOBJEX copy and compared them byte for byte with the normal picture builder for that character and equipment. The test temporarily set inventory records in the running test game. All original item records and temporary figure/class edits were restored, and the session was discarded without saving.

The save supplied the human man (Mage), elf woman (temporarily set to Preserver), half-giant man, and Thri-kreen directly. The other ten used one party slot with the corresponding figure and race, the Fighter class, and its map picture. The human woman selected Warrior, both dwarves and the elf man selected Fighter, and the seven study figures selected their default appearance.

| Live check | Result |
|---|---|
| Sword | Changed the picture set on 14 of 14 figures. |
| Chest plate | Changed the picture set on all 13 humanoid figures. The Thri-kreen retained its shell. |
| Removal | Both picture chunks returned byte-for-byte to their empty-slot versions after all 28 equip/remove cycles. |

This exercises the live inventory-to-picture update. The seven studies still require an imported class outfit for that same test to exercise the new art.

## Staged map comparison

In two further sessions, wrote the equipped study pictures to the four party slots of temporary game-file copies. Verified both picture chunks in each slot and loaded the save in DOSBox. The screenshots below show the parties on the map. The equipment in these two sessions was fixed.

![Two native DOSBox windows showing the staged parties in the slave pens](../../obsidian-edition/docs/class-outfits/equipment-staged-map.png)

| Group | Pictures staged in party-slot order |
|---|---|
| Left | Half-elf man Fighter with full plate, half-elf woman Cleric with Ashen Robe, half-giant man Fighter with sword and shield, half-giant woman Fighter/Psionicist with Warden’s Plate |
| Right | Halfling man Thief with sword and shield, halfling woman Fighter with full plate, Mul Fighter with full plate, retail Thri-kreen with gythka |

The side-by-side floor tiles and per-pose data show details too small to identify in a map screenshot. [Equipment report and measurements](../../obsidian-edition/docs/class-outfits/equipment-tests.md)

## Half-elf Fighter and Preserver

Repeated the live check after registering the four half-elf builds. With the Loader's Dresser attached to a disposable DOSBox session on the slave-pens map, used one party slot for each sex and class in turn. The Dresser selected Fighter or Preserver from the sheet. Verified the empty walk picture differed from the default half-elf.

For each build, equipped full plate, magical chest plate, a club, sword with shield, bow alone, ammo alone, bow with ammo, sling, and chatkcha. Read the walking and combat picture chunks back from the Loader's on-disk game copy on every change. Each equipment state matched the normal picture builder and differed from the empty set. Both chunks returned byte-for-byte to their empty state on all 36 removals. Restored the original inventory records, sheet, figure and map picture and discarded the session without saving. The animations in the gallery use the encoded Loader pictures. [Equipped half-elves](../../obsidian-edition/docs/class-outfits/half-elves.md#equipped-fighter-and-preserver)

## Magical worn equipment

Loaded a disposable copy of `pens-after-arena` in the patched DOSBox game and attached the Loader. For each figure below, equipped one item at a time, read back the Loader's walking and combat pictures from the active copy of SEGOBJEX.GFF, then removed the item and read both pictures again.

| Party picture | Sheet race | Sheet class | Loader outfit |
| --- | ---: | ---: | --- |
| 300, human man | 1 | 9 | Warrior |
| 304, elf man | 3 | 11 | Preserver |
| 307, half-elf woman | 4 | 9 | Fighter |

The five items were Legcrusher's Inixhide +1, Bone Scale Chest Armor, the Cloak of Elvenkind, Bracers of Defense AC 5 and the Boots of Speed. For the bone test only, the slave-pen chest item's bonus was set to +1 on a copy. Its icon and type stayed retail. The worn-item reader chose the fire cycle for Inixhide, bracers and boots, blue for bone, and green for the cloak. [Item records used by the gallery](../../prototypes/magicgearitems.py)

Repeated all 15 equip/remove cycles in a fresh session after the cloak, foot and wrist corrections. All 30 equipped picture chunks matched the Loader build byte for byte. All 30 chunks read after removal matched their empty-slot originals. Across the 29 poses, the human Warrior and half-elf Fighter showed chest glints in every pose. The elf Preserver showed them in 26, with three poses hiding the chest. Restored the party records and discarded the session without saving.

Separately decoded Inixhide and bone on all 118 registered class appearances and all 14 default figures, with 29 poses each. Of 7,656 equipped frames, 6,458 showed shine and 1,198 matched the empty figure. That includes the original Thri-kreen, which cannot wear either item. All 13,480 pixels that differed between enchanted and ordinary armor used the item's cycling colors. Silhouettes matched throughout. On registered class outfits, the changes stayed on chest-owned pixels and preserved the protected class trim and drawn bow.


For the playback timing check, a disposable Slave Pens session displayed the four indexed palette strips. Screen samples about 30 ms apart after the load fade showed color moving toward higher indices. Approximate times between steps were 84 ms for blue, 167 ms for fire and violet, and 209 ms for green. A separate unmodified-speed screen capture used staged outfit pictures for a leather-clad female half-elf Fighter, an elf Preserver/Ranger in the cloak, a dwarf Cleric/Fighter with bracers and boots, and a human Priest in bone. [Watch the idle map capture](../../obsidian-edition/docs/class-outfits/magic-gear-dosbox.gif)
