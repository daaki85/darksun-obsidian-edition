# Skin beneath the stock outfits

[Watch all eight figures through all 29 poses](https://github.com/daaki85/darksun-obsidian-edition/blob/d7f2076f5fa3bc4458c55bf5a81dd9237b0c3129/obsidian-edition/docs/class-outfits/body-texture.gif). Each group shows the original, the cleaned body, the Gladiator and the Fighter on the same arena tile. The small copy is game size. Use the original to locate the light on surviving skin, the Gladiator to see whether it continues under a strap, and the Fighter to judge how much shape survives beside a fully clothed figure. The two humans, dwarves and elves use empty-slot Loader outfit renders. The half-elf outfits are art-study renders.

[Watch the previous and revised bodies through the four profile steps](https://github.com/daaki85/darksun-obsidian-edition/blob/d7f2076f5fa3bc4458c55bf5a81dd9237b0c3129/obsidian-edition/docs/class-outfits/body-profile-detail.gif). Each row places them beside the original and Gladiator. The enlarged detail columns below compare the same patch of skin with revision `1da9371`.

![The ribs, hip, shoulder blade and calf in the earlier and revised frames, with details enlarged eight times](body-shading-detail.png)

| Figures | Where to look |
|---|---|
| Human | In rear idle and the four rear steps the man's shoulder blade catches a short diagonal light. It tapers beside the spine and returns at the hip. Rear walk 4 (10) shows the shading above the Gladiator's kilt. The woman's near hip now turns into shadow above the thigh through rear idle, the four rear steps and all three rear strikes. Compare the back of the leg below her hair in rear strike 2 (19). In profile, the ribs turn into a short shadow and a separate highlight picks up the hip. Follow those marks through the three side strikes and side bow as the arm crosses them. The man's front idle and walk also have a small lit plane beside the sternum. |
| Dwarf | The near shoulder, bent elbow and lit knee already read beside the Gladiator's straps. The rebuilt areas are small. The man's entire 29-pose sequence has only 196 eligible 2×2 squares wholly inside newly exposed skin. A short sloping light across the near shoulder and its shadow on the ribs now give the reconstructed areas a turn at game size. Rear walk 2 (08) is particularly clear between the Gladiator's strap and upper arm. |
| Elf | The light on the near ribs now turns down toward the waist, leaving a separate, shorter light on the far side. The highlights on the thigh, knee and calf follow each foot's height. A smaller highlight crests the ribs, and the lower edge turns toward the waist. In the extended side steps the calf light narrows and darkens towards the ankle. Compare the forward shins in side steps 2 and 4 (12, 14). On the woman's hit (27), a short light follows the upper edge of the raised thigh as it swings sideways. |
| Half-elf | The male figure inherits the elf's rib and thigh shading. On his widened torso the near ribs, waist and loaded hip now take separate highlights, with a shorter turn across the knee. [Compare the male half-elf fitting in all 29 poses](https://github.com/daaki85/darksun-obsidian-edition/blob/d7f2076f5fa3bc4458c55bf5a81dd9237b0c3129/obsidian-edition/docs/class-outfits/half-elf-man-body.gif) The woman inherits the human woman's revised hip and thigh beneath her shorter hair. Check the highlights beside the strap in the man's rear walk and along the woman's ribs and hip in her side walk and strike. |

## Locating flat areas

These percentages count uniform 2×2 squares among squares entirely inside the body's skin-color mask, pooled across all 29 poses within the original picture bounds. The last two columns restrict the mask to body skin where the aligned original had another color or transparency. The baseline is the preceding detail pass at `1da9371`. The skin range (palette indices 128–153) overlaps some hair and leather. Judge flagged patches against the pictures before deciding what to repaint.

| Figure | Whole base before | Whole base now | Reconstructed area before | Reconstructed area now |
|---|---:|---:|---:|---:|
| Human man | 7.9% | 6.0% | 12.8% | 9.0% |
| Human woman | 4.2% | 3.7% | 2.2% | 1.8% |
| Dwarf man | 2.2% | 1.3% | 13.8% | 4.1% |
| Dwarf woman | 2.7% | 1.5% | 11.8% | 6.9% |
| Elf man | 8.3% | 8.3% | 14.8% | 14.8% |
| Elf woman | 5.4% | 5.3% | 12.8% | 12.3% |
| Half-elf man | 7.7% | 5.0% | 14.0% | 8.5% |
| Half-elf woman | 4.3% | 3.9% | 6.1% | 5.6% |

To regenerate the current comparison from an installation, run `python prototypes/bodyreview.py GAME_DIR OUTPUT_DIR` at the repository root. The human man's indexed body edits are in the human outfit archive under `Study/walk-body` and `Study/combat-body`.
