# 2026-11-26: the lotulis', double spear's and trikal's traits in Wake of the Ravager, and the double spear's swings

**Under test:** branch `claude/ravager-weapon-traits` (3c07858b): DSCLOG2's THE TRIKAL AND THE TWO-HEADED WEAPONS
(SF_SWING from CAH_SWING, site 202 SF_SITE at 5D308h, SF_LESS from ENL_ROLL, the trip in CAH_HIT, TRIKAL_KIND in
REACH_HANDS; header +2020..+2028 its counts) and the Loader's double spear of range 1 (ravager.RAV_RANGES,
RAV_SKIP=melee_range the control).

**Set-up:** a throwaway copy `ravWT` of `$WORK/rav` (FLIs, VOCs, PDFs, game.gog hard-linked, the rest copied, the
roster from __support/save, no saves); `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh
/tmp/playtest/ravWT`; the dice log `RAV=/tmp/playtest/ravWT ravdice.py --numbers`; the DOSBox lock held throughout.

## Steps

**The party** (CREATE CHARACTERS; a class chosen by clicking FIGHTER off first, then GLADIATOR at 245,37; DONE,
the three powers, the weapon window's picks): Halton, fighter, lotulis ("starts with a lotulis +1", DAM 2x2D4+5);
Morbad th'Worst (member 1), gladiator, double spear, lotulis, trikal ("starts with a double spear +1"); Jaardoon,
gladiator, trikal, double spear, lotulis ("a trikal +1 ... a plain one made +1"); Morbad th'Worst (member 3, the
game's name again), gladiator, double spear, trikal, lotulis. **View Character's DAM for a double spear gladiator:
2x1D6+4** (the first-pick play's, before the range fix: 2x1D1+1, the bare hand). In memory the type table's Double
Spear (39) +6 is 1 (the Loader's copy), the Lotulis and Trikal 1 as the game has them.

**The fight** (START GAME, S at the title, the cinematic, "Lead on!" at 100,161, a click at 100,171: the Tyr ambush).
HP 250 each (`ravkits.py hp M 250`, a test edit; the dice log's autosaves and quick saves off, nothing saved), C,
Computer Control on the USE screen's small icons (47,53 / 98,53 / 47,113 / 98,113), Escape. Rounds 1-6 played. A
Draxan's curse turned Morbad#3's Computer Control off ("Cursed" under his portrait; the game waited on his turn):
C and his icon (98,113) again.

```
    Morbad th'Worst#3 turns the double spear's last swing from Draxan#21 to Draxan#27, beside it (a specialist's second foe, 1 less damage)
    Jaardoon#2's trikal trips Draxan#23? Save against paralysis: d20 = 5, needs 10+ -> tripped: loses its next turn
    Halton#0 turns the lotulis's last swing from Draxan#23 to Draxan#26, beside it (a specialist's second foe)
    Jaardoon#2's trikal trips Draxan#21? Save against paralysis: d20 = 18, needs 6+ -> saved
```

- **Second foe**: 4 in six rounds (3 double spear, 1 lotulis; DSCLOG2's header +2020 4, +2022 2 done 1 less,
  +2024 4 first targets put back). The first target took the next round's swings again.
- **Trip**: 7 saves asked, 2 trips (+2026 7, +2028 2); a tripped Draxan#23 lost its turn.
- **The double spear's swings**: each double spear gladiator (7th level, a specialist: 2 a round) swung **2 a round**
  in every round he had a turn (rounds 2-4 and 6: 4 between the two; rounds 1 and 5 one of them stuck on the curse),
  from beside his foe; the first-pick play's build (range 2) swung once a round from 2 squares. Halton's lotulis 2 a
  round (mastery), Jaardoon's trikal 2 a round and his left hand's Longsword +1 once.

## The controls (2026-11-27, a fresh copy, the same ambush)

`RAV_SKIP=melee_range` and `RAV_RULES_OFF=0x20000000` (rules_hi DF3F, RULE_HI_CAHULAKS cleared), the dice log
`wt-ctl.txt`; HP 250 for the four (a test edit), nothing saved:

- View Character's DAM for the double spear: 2x1D1+1 (the fixed run: 2x1D6+4), the game reading a range-2
  weapon as a missile one.
- The two double spear gladiators under Computer Control swung from 2 squares: 2 swings a round between them
  in rounds 1-4 and 1 in rounds 5-6 (each once a round), "+1 DEX" to hit and no STR damage.
- The header's counts (+2020..+2028) all 0; no second foe or trip line in six rounds.

## The trikal's reach by the click (2026-11-27)

The fixed build, no skip, dice log `wt-reach.txt`. Jaardoon (Wooden Trikal +1 in the right hand; the left-hand
Longsword +1 moved to a pack slot, his map thing moved to square (75,91), two squares from Draxan#23 at
(73,91), his Move set to 0; test edits, nothing saved) under the player's control:

- The sword pointer on Draxan#23 was valid ("10+ (55%)"), and the helper's `reaches` went 0 to 3 as it passed.
- The click: "Jaardoon attacks Draxan#23 with Wooden Trikal +1 (1d10+1) ... +1 STR, +1 weapon, +1 specialized"
  twice (both missed, so no trip save), the melee way; he stayed at (75,91); `reaches` 6.
- A third swing came with the Longsword +1 from the off hand: the game keeps the hands' weapons in its own
  copy, which moving the item in the sheet does not change. So this is a side effect of the test edit. The
  reach test (REACH_HANDS) saw no other weapon and let the reach through.

## What was learned

- The game's attack set-up takes a swing from 2 squares as a shot (the type's +7 attacks, DEX, no STR); the sequel's
  Double Spear has range 2, so the computer swung it from there once a round. Range 1 (the Loader's) fixes it.
- A Draxan's curse can turn a member's Computer Control off: the game then waits on that member's turn.
- A creation screen's class: click FIGHTER off first (245,29), then GLADIATOR (245,37).
