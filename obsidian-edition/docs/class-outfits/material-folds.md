# Cloth folds and Gladiator contrast

The earlier columns use revision `fee30cff`. The outfit columns show the Loader’s walking and combat pictures with empty equipment slots. The body columns show the cleaned art used to fit each garment. In the animations, the small copy is game size. Each pair shares the same ground line, pose and floor.

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

The first two columns show how the shoulder, ribs and loaded thigh turn before the garment is added. The next two show the same figure wearing the Gladiator straps and kilt. Follow the cut edge of the leather where it touches skin. The right column shows the retail Warrior when the game supplies a corresponding pose.

| Figures | Where to look |
|---|---|
| Humans | The kilt lap catches the light, and the short underside darkens against the thigh. Follow the rear step and the woman’s side walk as the hem changes angle. |
| Elves and half-elves | In the men’s first side strike (21), the reflected light follows the ribs below the raised arm. Watch the half-elf woman’s exposed shoulder blade beneath her bun during the rear walk. |
| Half-giants | Follow the narrow shoulder strap under the guard through the front strikes, then the leather skirt against the forward thigh. The flank takes a shorter reflection than the outside of the calf. |
| Halflings and Mul | Inspect the halfling woman’s belt under her hair during rear idle and the rear walk. The Mul’s strap turns toward the light as he winds up for a rear strike. In side bow (26), his exposed flank narrows above the hip. |
| Dwarves | The existing bronze guard, strap and hem separate clearly at this scale. Both dwarves are included as comparisons. The thri-kreen uses its original retail figure. |

Across the 29 poses, the median brightness difference between adjacent leather and skin on the half-giants rose from about 16 to 29 on the man and 28 on the woman (0–255 scale). In the first side strike, the largest flat patch on the bare torso fell from 27 to 7 pixels on the elf man and from 29 to 10 on the half-elf man.

[Human, dwarf and elf Gladiators through all 29 poses](gladiator-contrast-original-six.gif) · [Half-elf, half-giant, halfling and Mul Gladiators through all 29 poses](gladiator-contrast-later-seven.gif) · [Compare all 13 bodies and outfits on paving](gladiator-contrast-stone.png)

[Gerakis wearing the revised Gladiator art in DOSBox](../../../playtest/logs/2026-11-27-material-folds.md)

Regenerate the gallery with `python prototypes/materialfoldreview.py GAME_DIR OUTPUT_DIR --previous-checkout BASELINE_CHECKOUT`. Use a checkout of `fee30cff` for the earlier pictures.
