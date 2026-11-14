# Test log: an archer's turn ending when the quiver runs dry (2026-11-14)

**Under test:** the user's report that a character's turn ends as soon as its quiver runs out of
arrows mid-turn, when it should still be able to move or ready more arrows.

**Plan:** find where the game ends the turn after a shot with no ammunition left (DSUN.EXE's weapon
attack routine 5883Ah and its ammunition routine 58C8Fh, from DEVELOPMENT-RULES.md), see the
behaviour in a fight (save `fountain-user`, an archer with one arrow and 2 shots a round), fix it in
DSCLOG, and test again.

## Steps
1. Game set up from the user's installer; `fountain-user` loaded; buildcheck OK. Fight started.
2. Found the cause in DSUN.EXE: the weapon attack routine (5883Ah) cuts a shot's attacks to the
   arrows left (5899Ah, "Out of ammo" with none) and, once that cut-down count is made, writes 63h
   (99) to the attacker's +181h (58C45h), which ends the turn (5844Eh). So the turn ends with shots
   still due, and a shot tried with an empty quiver ends the turn with nothing done.
3. Fix: DSCLOG sites AMMO_CAP (5899Ah, keeps the round's attacks before the cut) and AMMO_TURN
   (58C38h, compares a party member's attacks made with the uncut count). Built (70,208 bytes);
   unit tests OK.
4. First play with the fix (fountain-user, every foe Paralyzed, Ester's quiver set to 1 arrow in
   memory before the ambush speech was clicked): she shot the Templar (34/41 left), "Out of ammo",
   and the turn passed. Watched with `turnwatch.py`: +181h went to 1 (not 99: the fix held), but the
   caller (58456h) ends an attack command when its **target is still standing** (creature +1Ch
   Okay), whatever attacks are left: the game's own rule (an attack spends the turn unless it
   kills), not the arrows'.
5. So the arrows' bug is the **kill** case. Templar set to 1 HP (`foeset.py 25 hp=1`), Ester with 1
   arrow and 2 shots: the arrow killed him, +181h stayed 1, **the turn stayed Ester's**, and a walk
   click moved her (872,1528 to 904,1512) on the same turn.
6. Baseline, the two patches left out of a scratch build: the same kill passed the turn to Jenna at
   once (+181h straight to 99, then 0). The fix is what keeps the turn.
7. An empty quiver at the click: the game didn't try the bow at all; Ester walked up and struck with
   her long sword (turn over after the melee, as normal).
8. Unit tests 1905 OK. No save made (memory edits throughout).

## Result
Fixed and checked: an archer (a party member) that kills its target with its last arrow keeps its
turn, as after any kill, to walk, ready more arrows or strike again. Against a target still standing
the turn ends after the shots, with arrows or without: that is the game's rule for every attack.

## Part 2: the turn kept against a target still standing (the user's follow-up)
9. DSCLOG sites AMMO_OKAY (5843Fh, 584A4h, 5850Eh: the attack command's "target still Okay"
   tests answer "fallen" for a member whose volley its quiver cut short, attacks left), with
   NEW_AS_OKAY's jbe/ja kept in the same patches. Ester, 1 arrow, 2 shots, Templar at full HP: shot
   (41 to 37), "Out of ammo", **the turn stayed hers** (+181h 1, +1D5h kept).
10. Readying more arrows then: the game's inventory works mid-turn (Jenna's 68 arrows given to
    Ester's quiver: portrait, quiver, Ester's portrait, quiver), but **the shot is refused**: the
    pointer shows the sword (its check, 1D5AEh, builds its item list afresh) yet a click does
    nothing, on that turn and on her next. A stack the archer had in its quiver when the fight began,
    moved to the backpack and back on her turn, shoots (two shots, 41 to 31). So the attack works
    from the fight's own per-combatant item list (58C8Fh walks it), which doesn't take in an item
    that came to the archer during the fight: a stack given by another member, or one made in
    memory. (The mod's `shots_left` patch already lets a shot follow a kill, +181h under 63h.)
11. A memory-made stack (npcitems.add_to) is no test of readying: it never shoots.

## Part 3: why arrows readied after running dry don't shoot (2026-11-14, later)
12. Handing arrows over works in itself: Jenna's 68 given to Ester's quiver on a fresh turn shot
    twice (41 to 30).
13. Tried keeping the emptied stack instead of the game deleting it (a site AMMO_KEEP at 58DA9h):
    the stack stayed at 0, Jenna's arrows merged into it (the very item Ester began the fight
    with, 68 arrows), and the shot was **still refused** on that turn. So the deletion isn't the
    cause; the experiment was dropped.
14. What remains: after a volley at a target still standing, a second shot at **the same target**
    in that turn does nothing (the pointer shows the sword; nothing in her turn bytes changes on the
    click). After a kill, the game does allow a second shot (at another target: the mod's
    `shots_left` notes). The click's own handler wasn't found (the attack-mode pointer code at
    1D66Ah picks only the icon; 5786Dh is the monsters' turn routine).

## Part 4: the quiver topped up from the pack, and the count over the archer (the user's choice)
15. `quiver.py`: as a party archer's turn starts in a fight, a quiver under 5 is topped up to 20
    from the pack's stacks of the same kind (by count: the quiver stack the game knows stays); after
    each party shot "Arrows: N left" floats over the archer.
16. Ester with 3 arrows, Jenna's 68 handed into Ester's **pack** on her turn; two shots (one left):
    "Arrows: 69 left" over her. Her next turn: "Ester fills the quiver from the pack: +19, 20
    Wooden Arrows ready" (quiver 20, pack 49), and both shots went off: "Arrows: 67 left".
