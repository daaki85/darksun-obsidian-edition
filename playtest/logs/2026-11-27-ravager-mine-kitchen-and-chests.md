# Mines 3 kitchen, loot chests and loose furniture in play

The whole-map render covers RGN03A. Gold squares mark the chest by the lava pool and the chef’s locked chest. Blue marks the kitchen crates. The Shattered Lands reference is the upper castle (RGN1C), chest picture 168 at (1033, 1349). [Whole maps and castle chest](../../reports/ravager-furniture/mine-kitchen-whole-maps.png)

All Ravager close-ups come from 320 × 200 DOSBox captures through the Loader. A private Roost save used Reyhan’s travel jump with the destination sector and its usual camera bounds. The stock control used the original figures. The middle kitchen panel uses the preceding PR package. The other revised panels use the new package or, for the six chair and table placements checked earlier, the identical pictures from the preceding build.

## Kitchen boxes

From square (72, 91) in sector 2, Look at the little box at (1112, 1441). It reads “Cooking poisons -- use sparingly!” Object 5164 uses picture 3364, already lowered in the first pass. The other three boxes in the room are copies of object 5099, picture 1135, at (1151, 1438), (1199, 1454) and (1152, 1503). Their original 24-pixel-wide drawings stood 31 pixels high. The revision brings the top down ten pixels while keeping the floor row.

Use the green hand on each crate’s card. All three responded in both builds. In the revised visit the first two held preserved brains and the third smelled of rotting flesh. A control crate held cooking spices. The script narrates lifting the lid. The crate has one picture frame. [Stock, previous and revised crates](../../reports/ravager-furniture/mine-kitchen-crates-live.png)

## The two hinged chests

Both wooden chests use 50-pixel-wide artwork. The closed drawing changes from 41 to 27 visible rows and the raised drawing from 60 to 40. The existing floor rows and both original animation scripts remain in the package’s installed result.

| Chest | Object / picture | World position | Party square | Sector |
|---|---|---|---|---:|
| Plate armor | 3145 / 1113 | (175, 92) | (10, 7) | 12 |
| Chef’s locked chest | 5102 / 1136 | (776, 1365) | (48, 86) | 2 |

Open the chest by the lava pool. The party found a very heavy set of plate armor. Once the message cleared, the game drew the raised lid. Both stock and revised drawings matched the installed open frame at the same screen origin.

For the chef’s chest, the travel fixture gave the party the real chef’s key, object 3140, before entering the room. Choose “Unlock it with the chef’s key.” In both builds the key opened the lock, the party member earned 2,500 experience, and the chest yielded an unusual triangular-shaped key and a scroll. The chest still displayed its closed drawing afterward. To see its second stored drawing, a separate private visit copied the stock raised animation step into the initial step for picture 1136. Both raised screenshots use that fixture. The shipped mod changes only the pictures. [Closed and raised chest comparisons](../../reports/ravager-furniture/mine-armor-and-chef-chests.png)

## Loose furniture already lowered

| Piece | Picture | World positions |
|---|---:|---|
| Front-facing stone chairs | 2789 | (903, 929), (885, 1153) |
| Side-facing stone chairs | 2790 | (690, 989), (751, 1485) |
| Stone table | 2793 | (971, 1145) |
| Small individual chair | 3276 | (1075, 1149) |

Each of the six furnishings matched every opaque pixel of its installed drawing in the stock and mod captures, with the same drawing origin. The red bowl (3285) at (758, 1500) and loose blue orb (1077) at (926, 1155) are separate floor objects. [All six placements in DOSBox](../../reports/ravager-furniture/mine-loose-seats-live.png)

Five other worktables still use original artwork. Each consists of two touching pieces. Pictures 3766/3767 form a table at (1407, 994), 3770/3771 at (1503, 996), 3772/3773 at both (1727, 837) and (1936, 1014), and 3774/3775 at (1508, 1444). Check their joins and any objects resting on them together. The laboratory floor safe (5104, picture 1138) at (1610, 828) has three stored frames and needs its own interaction check.
