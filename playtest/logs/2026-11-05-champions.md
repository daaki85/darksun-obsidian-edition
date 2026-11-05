# The champions' bout: their gear, their attacks, the Tohr-kreen's body (2026-11-05)

Build: `obsidian-edition` with the champions' bout (champions.py, bodyart.py, DSCLOG's body case).
DOSBox, new games with the ready-made party, in the arena's first visit.

## Do the game's people use what they carry?

1. In the pens (`pens-thornwall-rack`): every person's gear is in the backpack list (+0Ch), none
   worn (+08h) or held (+0Ah): Kurzak, the Arena Guards, Scar, the Templars.
2. Arena, first visit, second wave: the two Tohr-kreen given Headsman (a metal great axe +2) in
   the held list, right hand (slot 3). Next attack: "Tohr-kreen attacks Cermak with Headsman +2
   (1d10+2) ... +2 weapon", twice, then its natural 1d6. So the melee routine uses an NPC's held
   weapon.
3. The same two given Scale Chest Armor in the worn list (slot 9): K'ratchek's attacks then read
   "target AC -2" (before: 3). The game counts NPC armour. (The Loader's own count said 1: a gap
   to look at.)
4. Killed: each left a Dead Body (object 1101) with its Headsman and armour.
5. A body's map record has a picture number (+18h, 495). Changing it to the Tohr-kreen's picture
   changed nothing on screen, so the body's object is changed instead (DSCLOG at 59412h).

## The champions

6. The arena's flags and numbers have no place in memory between script runs, or even while a
   script waits on a message, so the bout couldn't be made due from outside. Test build: the
   bout's test forced true (script 2's parts of ours), the module put back afterwards.
7. Fifth wave of the visit (the wave maker's call for waves past the fourth): six "Champion" came
   on (objects 2660-2665). Their lists, by the Loader:
   - Tohr-kreen: Kreenfang held (3). AC 3.
   - Half-giant: Great Axe held (3); Scale Chest/Arm/Leg Armor and Shield worn (9, 0, 6, 10). AC 5.
   - Mul: two Axes held (3, 10); Scale Chest and Arm worn. AC 3.
   - Halfling: Short Sword (3) and Sling (2) held; Chest Armor worn. AC 5.
   - Elf: Long Sword (3) and Bow (2) held; Chest Armor and Arrows (1) worn. AC 9.
   - Defiler: Dagger held (3); a Scroll in the backpack. AC 10.
8. Their attacks: the mul with both bone axes (1d8 each), the halfling with the Leather Sling
   (1d4, at range), Kreenfang "+1 (2d4+1)" twice then a 1d6, the elf with the Wooden Bow (1d8),
   the half-giant with the Great Axe (1d10 +8 STR 20).
9. The party (level 1) was defeated. Before that: the Tohr-kreen champion's body was object 2666
   with Kreenfang in it; the others' were Dead Bodies (1101) with their gear; the dead body by the
   arch had a plain Gythka.

## Second run: the body on screen

10. The same test build, the party's hit points raised to 250 in memory: the champions killed
    (fightout.sh). The Tohr-kreen's body, object 2666, is drawn with its own picture, a dead
    Tohr-kreen on its side, in the heap where the six fell (`img/2026-11-05-kreen-body.png`, the
    heap five times its size; `img/2026-11-05-kreen-body-picture.png`, the picture alone). The
    human Dead Bodies of the others lie over part of it.

Not seen yet: the Announcer's speech (a visit past the fifth) and the bout after a real kill of
Scar.

## Third run: the AC with full armour and helms

11. The same test build, with full armour sets and helms (the halfling and the elf with leather
    shields), the sheets keeping their kinds' AC (10, the Tohr-kreen's 3). Each champion renamed in
    memory (Kreen, HalfGiant, ...) so the dice log tells them apart. The game's AC against the
    party's attacks, and the Loader's count (`counted_ac`):

    | Champion | Game | Loader |
    |---|---|---|
    | Tohr-kreen | 3 | 3 |
    | Half-giant (DEX 14) | 4 | 5 |
    | Mul (DEX 18) | 1 | 2 |
    | Halfling (DEX 18) | 1 | 2 |
    | Elf (DEX 12) | 5 (once 6) | 6 |
    | Defiler | 10 | 10 |

    (The Loader's figures here were read before its pass had put the last pieces on: see 13.)
12. Found: the halfling's and elf's helm was Dapartea's Helm, the game's first item of the leather
    Helm's type. Now the plain Helm's own record.
13. Fourth run, DEX now 15 (half-giant) and 18 (elf, defiler), the dice log with `--all`: the
    game's AC with its parts ("armour" is the body pieces, [BP-6]; "other" the helm, shield and
    the rest): half-giant 3 (10, -4, DEX -1, other -2), mul 1 (10, -4, -4, -1), halfling 1, elf 1
    (10, -3, -4, -2), Tohr-kreen 3, defiler 6 (10, 0, -4). The mul's armour copied onto the
    tied-up prisoner (base 10, DEX 12): the Loader's count 10, 8, 7, 6, 5 as the chest, arm, leg
    and helm went on, the game's sum. The earlier gap was the reading: the script read the AC,
    then the lists, and the Loader's pass put the helm (and the shields after it) on between.

## Aside: a time-of-day palette tint, mocked up

An arena view (outdoors) captured and every colour tinted as a palette tint would tint it (the
same thing: each pixel is a palette colour): dawn (R 1.0, G 0.78, B 0.72), noon (1.04, 1.02,
0.95), dusk (1.0, 0.70, 0.48), night (0.36, 0.44, 0.74). `img/2026-11-05-tint-mockup.png`. The
game writes its palette at 144DCh (all 256, from a buffer, 8-bit values shifted to 6), 288ADh (a
block: the colour cycling's) and 1168Ch (one colour), and reads it back at 116A7h and 288C4h (its
fades): a tint in the game would take all five.
