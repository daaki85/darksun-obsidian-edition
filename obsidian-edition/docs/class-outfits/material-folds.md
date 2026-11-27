# Cloth folds and Gladiator contrast

## Oiled Gladiator leather

The three rows in each view show the retail party picture, the Gladiator from `34563951`, and the revised Gladiator. All three use the same pose, palette and patch of arena sand. The stock half-elves share the game’s human pictures. The revised figures use the Loader’s fitted half-elves. The thri-kreen is included as a retail control.

[Compare every figure at game size in colour](gladiator-leather-game-size.png) · [Compare the same pixels in greyscale](gladiator-leather-greyscale.png) · [Inspect the human front and profile at 3×](gladiator-leather-humans.png)

The standing views and middle strikes show the contrast at rest and as the body turns. Across the human poses, the sampled kilt has a median greyscale value of 38 on a 0–255 scale. Nearby exposed skin measures 86 and the same arena sand measures 174. Follow the lower edge of the diagonal strap where it meets the ribs, then the bottom of the kilt where it crosses the near thigh. The lighter turn of the leather is wider on the half-giants. On the halflings the metal fastening takes only a single pixel when visible.

The animations show all 29 distinct poses. Each cell includes an unscaled copy beside the 3× view. Watch the belt and its fastening turn with the hips through the four steps, and the forward arm cover the strap in the strikes.

[Humans and dwarves](gladiator-leather-humans-dwarves.gif) · [Elves and half-elves](gladiator-leather-elves-half-elves.gif) · [Half-giants and halflings](gladiator-leather-half-giants-halflings.gif) · [Mul and thri-kreen](gladiator-leather-mul-thri-kreen.gif)

[See the pens party in DOSBox with the Loader attached](../../../playtest/logs/2026-11-27-material-folds.md#oiled-gladiator-leather-in-the-pens)

Regenerate these comparisons with `python prototypes/gladiatorleatherreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT`, using a checkout of `34563951`.

## Earlier body and cloth studies

The body comparisons use `c351a52f` for the earlier art. The cloak shoulder comparisons use `17aaacef`. The wider cloth comparison starts at `fee30cff`. The outfit columns show the Loader’s walking and combat pictures with empty equipment slots. The body columns show the cleaned art used to fit each garment. In the animations, the small copy is game size. Each pair shares the same ground line, pose and floor.

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

Watch the elbow fold as the hand rises, then watch the light move down the near knee and calf as the foot takes weight. Both marks are easiest to see beside the far limb in the same frame. The skin beside the Gladiator’s strap and kilt shows how much of the new shading remains visible in the outfit.

[Examine seven poses beside their retail sources at 4× and game size](bare-body-closeups.png)

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

Regenerate the gallery with `python prototypes/materialfoldreview.py GAME_DIR OUTPUT_DIR --previous-checkout BODY_CHECKOUT --previous-cloth-checkout CLOTH_CHECKOUT`. Use `17aaacef` and `fee30cff` respectively for the two cloak and cloth comparisons. Then run the same script with `--previous-checkout` set to `c351a52f` and `--bodies-only` to regenerate the current bare bodies and Gladiators.
