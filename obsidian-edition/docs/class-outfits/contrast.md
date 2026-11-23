# Dwarf outfit contrast at game size

The dwarf Cleric and Psionicist read clearly beside both humans. The two places where detail gets lost are the Fighter’s brown jerkin in the side walk and the Thief’s slate hood against dark paving. I would keep the current pale Cleric/Fighter caps and narrow Fighter/Psionicist sash. The larger contrast differences are in the single-class outfits.

## Dwarves, humans, and original game figures in motion

![Five synchronized rows comparing female and male dwarves, female and male humans, and an original Shattered Lands figure on the same paving](dwarf-human-stock-contrast.gif)

Each row follows one outfit through the 27 poses shared by all the comparison figures. The side walk repeats. The four party figures use the branch sprite loader with empty equipment slots. The last column uses original game art, including the stock male dwarf beside the Gladiators and the blue Mage beside the Psionicists as palette references. The original figures retain their depicted gear. All tiles use the same paving and 2× nearest-neighbor enlargement.

- **Cleric.** The dwarf’s cream hem splits into a light panel and a dark fold, much like the human woman’s robe. The split is easy to follow on paving. On bright sand the shaded fold does more to define the hem than the highlight. The original red Priest shows how a saturated color can stand out even with a narrower brightness range.
- **Fighter and Gladiator.** In front view the Fighter’s light stitching and dark jerkin separate the armor from the arms. In side-walk step 3 both dwarves turn far enough that skin, leather, and bronze form a narrow brown strip. The human woman’s light shoulder and the original Warrior’s dark boots and bright weapon remain visible in the same pose. This is the view where the two dwarf classes are easiest to confuse.
- **Psionicist.** The teal tunic stays distinct from the skin on both dwarves, as it does on the humans. The original blue Mage makes a larger patch of color across the back. The teal is clearest from the front, where it runs across the chest and down to the waist.
- **Thief.** The dwarf’s slate hood frames the face on sand and ordinary paving. On dark paving its outer fold starts merging into the background. The human man’s muted hood is close in overall contrast. The human woman has a lighter fold, and the original green Thief has a stronger light-to-dark edge.

## The two restored multiclasses

![Dwarf Cleric and Cleric/Fighter side by side, then Fighter and Fighter/Psionicist, human Fighter, and original Warrior in matching poses](dwarf-multiclass-contrast.gif)

The upper row uses female party figures and the lower row uses male party figures. The same original Warrior appears in both as a reference.

The **Cleric/Fighter** reads as a Cleric first. Look at the outside edge of each shoulder in front idle, where the dark underside separates the pale cap from the arm. In the side walk the cap and cream sleeve nearly merge. Only 8–9 overlapping figure pixels change between Cleric and Cleric/Fighter in each side-walk step.

The **Fighter/Psionicist** is easier to distinguish from the Fighter in motion. The teal line crosses brown leather, and the rear idle exposes more of it than the front idle. In the third front strike the forearm passes over the line, leaving only five overlapping pixels different from the plain Fighter. That brief occlusion gives little reason to widen the sash for the rest of the cycle.

## Terrain at native resolution

![All twelve dwarf outfits, five matched human outfits, and original figures on sand and paving at one game pixel per image pixel, with an enlarged grayscale comparison](dwarf-contrast-terrain.png)

Each party pair shows the woman on the left and the man on the right in front idle. The first three columns are at 1× in the full-resolution image. Sand and ordinary paving are sampled from game captures. The dark-paving column uses the same paving with its RGB values multiplied by 0.48 as a visibility test. Sprite colors stay at their game values. The final column enlarges that composite in grayscale to show which details depend on hue.

## Brightness range across the shared poses

| Outfit | Dwarf woman | Dwarf man | Human woman | Human man | Original figure |
|---|---:|---:|---:|---:|---:|
| Cleric | 149 | 141 | 166 | 146 | 97 · Priest |
| Fighter | 123 | 117 | 120 | 110 | 157 · Warrior |
| Gladiator | 119 | 111 | 108 | 121 | 145 · stock dwarf |
| Psionicist | 122 | 112 | 106 | 112 | 120 · Mage |
| Thief | 97 | 97 | 122 | 100 | 142 · Thief |

For each pose, the range is the difference between the 90th and 10th percentile brightness of opaque figure pixels, using grayscale weights of 0.299 red, 0.587 green, and 0.114 blue on a 0–255 scale. The table gives the median over 27 poses. It includes skin, hair, clothing, and any gear drawn into the original figure. The terrain sheet shows the separate question of how well a particular edge stands out against the ground.
