# 2026-11-28: Wake of the Ravager, the creation screen's age, the flip's wait, the arrows label

Under test: DSCLOG2's sites 235-237 and the Loader's `quiver.shooter` (branch `claude/ravager-creation-age`).

## The creation screen's age

`ravcreation.sh 1` (a human fighter, the ready-made name). Before: no age on the screen, the sheet being
made (DS:1429h, 3FF1:0029) has +41h 0, and the creature straight after it at +42h (3FF1:006B): no room for
the roll beside the age.

After: `AGE: 23` at x 146 on PSP's line (under THAC0), the box widened to 200 (DS:122Ch: 86,179,200,185).
The die four times: the byte 7, 5, 5, 9 (ages 21, 19, 19, 23). A click on CON (40,154): 9 kept. STORE
(112,230), the die (8), RECALL (172,230): 9 again, `AGE: 23` drawn clean. DONE (271,217): the party's
first sheet (48h, 725B:0004) has race 1, +41h 9, +42h..+47h 0 (the Loader's `give_ages` then puts the roll,
7, beside the specs: `aging.screen_roll`). EDIT not tried.

## The page flip's wait

`ravload.sh ravager-after-ambush`: DSCLOG2's `flip_waits` 99 on the map; I (inventory, `SCREEN_IS` 2): 100,
`flip_quick` 1; a click on a member there and I again: 105, quick 1. The inventory looked as before.

## The arrows label

The ambush save's party: Ar'Anda's Leather Sling and Thy'rokh's Obsidian Chatchka +1 in the missile slot,
no ammunition. Before: `quiver.left_label` gave "Out of arrows" for both (after every throw, in a fight).
The sequel's type records: both first byte 02, no bit 3 (its count of a shot's ammunition, 5D3BAh, tests bit
3 of the type's first byte, as SL's 58C97h: none needs ammunition, no end of shots). After: no label. Not
seen with a bow (the test saves have no archer).

Water: none new.
