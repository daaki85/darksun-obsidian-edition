# 2026-11-28: Wake of the Ravager, the quality-of-life port's checks by hand

Under test: `obsidian-edition` at 02bc9ba5 (#308 merged), then branch `claude/ravager-play-checks` for the
fixes below. `ravPC`, a fresh copy of `rav` for each run (thrown away after): `ravager-after-ambush` loaded
through the Loader's start (`ravload.sh`), `RAV_NO_SAVES=1 ravdice.py` attached; for the creation screen
`RAV_LOADER=1 RAV_MENU=1 ravstart.sh` and the steps of `ravcreation.sh` by hand. Memory edits were test edits
only (never saved: no SAVE file written, every DOSBox stopped unsaved). The control for the saves: the same
copy narrowed (`python -m dsloader.ravager narrow`) and started plainly.

## Played and working

- **Shift+T** on body 211: "Ar'Anda takes Bone Ring Armor (3)", "Plain weapons left: Bone Mace", the window
  shut. **T** on body 209 (game 98,124 with the eye): "Ar'Anda takes Wooden Bow, Stone Lotulis, Bone
  Brigandine Armor (2), Arrow", the window shut.
- **Alt** held on the street: gold rings under the three bodies, the scroll, the sandals and a passer-by
  (RING_TAB 6 marks), names under the four nearest the pointer (labels.SLOTS is 4); let go, all gone
  ([picture](img/2026-11-28-ravager-alt.png)).
- **Item box**: the Stone Lotulis "2D4-1/2D6-1, Hit -2". No charged item in the save (charges were seen with
  a test edit on 2026-11-20). The sequel's armour comes in pieces (types 33, 65 and 4 are all "Bone Ring
  Armor"): a curved arm piece's icon looks like a lotulis, its box says armour, as the game's own.
- **Effects screen**: Terrannus cast Protection from Evil on himself (USE from the inventory's bottom
  icon at 218,188; the spell at 214,77, his portrait 120,57; EFFECTS 120,171); two clicks on its icon
  (175,58) and it stays ([picture](img/2026-11-28-ravager-effects-kept.png)).
- **Load window** (F2): a click on an empty row picks nothing (the save chosen stays chosen); Enter loads
  the chosen save, no hang. The party's ages are rolled again at each load of a save made before ages
  existed (nothing kept them): as designed.
- **Characters tab** (`python3.12 -m dsloader view --pid` on Xvfb :56 at 1440x900; this container needed
  `apt-get install python3-tk`): the four cards with age, THAC0 by weapon, saves, move, attacks, gear and
  spells left, ages as the dice log rolled them.
- **S at Notaku** (route y 1224, x 296, y 936; the eye on him at 176,13; the Look box's first button
  196,64; talk 3, 1, 3, 2): with nothing plain in the pack, "Ar'Anda has no plain gear in the backpack to
  sell." and the shop shut back to his talk, as Shattered Lands' S does. (A sale was seen on 2026-11-25.)
- **EDIT on the creation screen**: a new 7th-level human fighter made (AGE 21), DONE, five psionic powers
  picked (the first icon is greyed: 138,59 five times), then EDIT (right-click the slot 70,56, EDIT
  110,57): AGE 21 kept, and kept through a roll of the die.

## Found and fixed

- **Every saving throw worked out with AD&D's tables was nonsense.** A new character's View Character read
  PPD 81, RSW 2, PP G5, BW 0, SP D8: the sheet's +31h-35h were 81, 2, 235, 0, 208, written by the die and by a
  click on CON; the same with the game started for real. The stock game's (the control) were 11, 12, 11, 13,
  13. The game's save routine (954D2h) runs at creation and at every level up; its site SAVE_BASE (116) reads
  its bands through TAIL_SEG, but DSCLOG2's bands stayed in the segment when its tail moved out (48b3673e,
  2026-11-27): it read the tail's bytes at the segment's offsets. The bands are now the tail's. After: 10, 12,
  11, 12, 13 for the fighter, the Player's Handbook's ([before and after](img/2026-11-28-ravager-new-saves.png)).
  The level-cap rig set TAIL_SEG to the helper's own segment, which hid it; it now sets the tail's and
  fails on the old code (506 of its subtests).
- **View Character's DAM line one too many**: the Obsidian Dagger 1x1D4+4 beside the inventory's 1D4+3.
  Shattered Lands' VIEW_MATERIAL (a weak material's damage off) was never ported; now DSCLOG2 has it. After:
  1x1D4+3 on both ([picture](img/2026-11-28-ravager-view-dam.png)).
- **The arrows label** read "Arrow: 24 left" (the Wooden Bow in the missile slot, 24 arrows in the ammunition
  slot above the figure's left; `quiver.left_label` through the dice log's own reading): the sequel names its
  arrows "Arrow". `quiver.word` makes the name plural: "Arrows: 24 left", in both games.

## The quests that show while open

Each quest's reward script was read for flags tested before the reward and set by another script, and the
talk beside them: most of the sequel's deeds are finds, fights and puzzles no one asks for. Two more errands:
Fayina's debt (flag 325, set as she asks the party to see Acar; cleared if the fight in the street kills her)
and the hermit's student (585, set as he refuses help till she is home; cleared beside 584 when she is
freed). Dariya's reward (32 at 1014, flag 94) is given as she judges the party and sends it for the root,
not when the root comes back: the quest now says so ("Dariya's judgment"). Halla's flag (525) is cleared in
another script and was left out.

Water: none new (Tyr's street, Shadow Square).
