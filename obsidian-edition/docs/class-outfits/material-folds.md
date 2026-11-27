# Cloth folds and Gladiator contrast

The body and shoulder comparisons use `17aaacef` for the earlier art. The wider cloth comparison starts at `fee30cff`. The outfit columns show the Loader’s walking and combat pictures with empty equipment slots. The body columns show the cleaned art used to fit each garment. In the animations, the small copy is game size. Each pair shares the same ground line, pose and floor.

## Cloth on the arena floor

| Figure and pose | Where to look |
|---|---|
| Human Psionicists, front idle (00) | The man’s teal shoulder has a short light above a diagonal shadow. On the woman, follow the overlap down the front of the chest during the next four steps. |
| Half-giants, rear walk (07–10) | The man’s teal wrap turns toward his belt as the shoulder rises. On the Ranger, a thin light follows the trough down the green panel below the hair. |
| Male elf and half-elf, side walk (11–14) | The light runs along the lifted edge of the Ranger’s cloak. The half-elf Ranger/Thief carries the same fold through the returning fourth step. |
| Female half-elf Cleric/Thief, rear strike 2 (19) | The cream hood turns at the nape and casts a short shadow on the near shoulder. |
| Halfling Clerics, side walk 3 (13) and front strike 2 (16) | A tan underside separates the thin outer hem from light sand. The knee still lifts inside the linen. |
| Mul Druid/Thief, rear walk (07–10) | Green shades turn from the crown into the neck. The leaf cape has a separate edge beneath the hood. The Druid/Fighter/Thief inherits this change. |

[Compare individual poses with the retail Warrior, Mage, Priest and Thief](cloth-folds.png) · [Watch the teal wraps and rear cloak](cloth-folds-wraps.gif) · [Watch the trailing cloaks, robe and hoods](cloth-folds-cloaks.gif)

## Gladiators and exposed skin

Read the body and Gladiator columns together. The same patch of exposed skin should keep its light as the strap crosses the chest or the kilt lifts past the knee. The last two columns show the corresponding retail source figure and the retail Warrior where its picture supplies that pose. The half-elves use their retail parent figures for this comparison.

| Figures | Where to look |
|---|---|
| Humans | Follow the light across the near shoulder and the short shadow under the ribs. At the waist the leather crosses into that shadow, and the forward thigh catches light below the kilt. |
| Dwarves | In front idle the lit chest turns into the abdomen just behind the diagonal strap. From behind, the shoulder blades and hip have separate highlights. Watch the bent knee move out of the kilt’s shadow. |
| Elves and half-elves | Watch the near ribs under the raised arm in the first side strike (21). In the rear walk, compare the exposed back beside the strap with the same area on the bare body. |
| Half-giants | The chest and shoulder blades have the largest exposed surfaces. Follow their light toward the narrower waist during the strikes, then compare the nearer and farther knees as the kilt swings. |
| Halflings and Mul | On the smaller bodies, use the side walk to follow the light under the arm into the waist. On the Mul, the shadow beneath the ribs sets off the warm leather at the hip. |

[Human, dwarf and elf Gladiators through all 29 poses](gladiator-contrast-original-six.gif) · [Half-elf, half-giant, halfling and Mul Gladiators through all 29 poses](gladiator-contrast-later-seven.gif) · [Compare all 13 bodies and outfits on paving](gladiator-contrast-stone.png)

[Gerakis wearing the revised Gladiator art in DOSBox](../../../playtest/logs/2026-11-27-material-folds.md)

## Shoulder of the trailing cloak

In side-walk frame 14, six far-shoulder pixels interrupted the green panel on the male elf Ranger and the male half-elf Ranger/Thief. Follow the closed panel back toward the shoulder, then step through the two middle frames where the forward arm extends into view.

[Inspect side walk 4](cloak-shoulder.png) · [Watch all four steps](cloak-shoulder.gif)

Regenerate the gallery with `python prototypes/materialfoldreview.py GAME_DIR OUTPUT_DIR --previous-checkout BODY_CHECKOUT --previous-cloth-checkout CLOTH_CHECKOUT`. Use `17aaacef` for the body and shoulder baseline and `fee30cff` for the wider cloth comparison.
