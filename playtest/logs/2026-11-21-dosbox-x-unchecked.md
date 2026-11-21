# 2026-11-21: DOSBox-X engine, the unchecked items

Under test: the branch `claude/dosbox-x-engine` at e840d02 (obsidian-edition up to #144 merged in),
the game in DOSBox-X 2026.10.01 (built here from its source, SDL2, Linux 64-bit), a game of its
own (display :59, work folder /tmp/claude-0/dbxwork with a copy of the game folder).
What [the last play](2026-11-19-dosbox-x-engine.md) left unseen: spells cast in a fight, a won
fight and its autosave, F10 after the last step, a shop, the inventory, the creation screen.

## Steps
1. **Start**: `PT_SAVE=fountain-user sh start_dosboxx.sh` (DOSBox-X pid 10366, memory file in
   /dev/shm). The window 320x240 at 0,0. `buildcheck.py`: OK. The start script turns the autosave
   off; `settings.json`'s `autosave` set back to true and the dice log restarted (it reads the
   settings once, at its start), so a won fight can autosave. No memory edit at any point.
2. **The ambush**: `dismiss.sh`, round 1 (Seneca, Ester, Templar, two Arena Guards, Jenna, Lex,
   a Guard, two Arena Guards). Seneca Tab + Return: three misses on the Templar.
3. **A spell in a fight (Ester)**: U, Entangle (248,59) aimed: its box is as wide as the view's
   lower half and took the party in from every place tried, so cancelled with a right-click (the
   turn stayed Ester's, the walk arrow back). Then U, Bless (176,59), a click on Jenna:
   `Ester gives Blessed to Jenna, Ester: +1 to hit, +1 on saves`, `Bless lasts 6 rounds (caster
   level 3 ...)`; the next save (Lex's against the Templar's Hold Person) carries `+1 Blessed`.
4. **Lex's spells**: U on his turn: every icon crossed out (an Arena Guard's two arrows had hit him
   just before his turn: the guide's "crossed-out icons"); Escape, Tab + Return.
5. **The rest of the fight**: `PT_NO_EDIT=1 sh fightout.sh` (no foe's HP changed).
6. **The fight won**, with no memory edit: `Fight over: 5 rounds, 6 kills; the party dealt 249
   damage and took 32` (Pehtucl the Templar, a Guard, four Arena Guards), each kill's XP lines,
   Seneca's 3rd fighter level ("Seneca is now a 3rd level Fighter", max HP 21 -> 25), then
   **`Autosave: "Auto - Day 1, 00:57 - after a fight" (the QUICK page, slot 6)`**, the game's
   "Autosave" label over the party, `inst/SAVQ06.SAV` 89,621 bytes.
7. **The autosave loaded**: `quick_save` set back to true and the dice log restarted; the party
   walked to (1016, 1512); F9 opened LOAD on the QUICK page with "Auto - Day 1, 00:57 - after a
   fight" in row 6; Return: the leader back at (1112, 1496).
8. **F10 after the last step**: `fountain-user` again (a fresh start), Lex's turn at square
   (55, 94) with 120 points. The view dragged west (`scroll.py 240 0`), `squarewalk.py 43 94`:
   twelve squares, points 120 -> 0, flags 0x3EE (bit 0, the walk, off). F10: Lex back at (55, 94),
   points 120, flags 0x3EF, and the dice log's `F10: Lex's move taken back (can walk again)`.
   A walk after it: `squarewalk.py 49 94`, points 120 -> 60. (An Escape before the F10 brought
   EXIT GAME?: squarewalk had left no END menu up; CANCEL at 125,116.)
9. **A shop** (`selling-junk-user`, `openshop.sh` unchanged): Kalzith's shop up, Gerakis on show
   with 35 ceramic pieces. **S**: `Gerakis sells 9 things for 95 ceramic pieces: Wooden Club 1,
   Bone Axe 4, ...`, the shop shut back to his menu as on 0.74 (logs/2026-11-11-selling.md; the
   Wooden Arrows of that log stay: ammunition is never sold since). 1 again: the shop, 130 pieces.
   **A purchase**: a click on the Wooden Quarterstaff (1 piece, the shop's first item, 256,88):
   "SOLD!", the staff on the pointer, 129 left; a click on a backpack cell (193,62) put it there
   (`carried.py Gerakis`: thing 202, slot 16).
10. **The inventory**: Escape (Kalzith's menu), 4 Farewell, I. The paper doll with the Loader's
    THAC0, saves and weapon lines. The staff picked up (195,62), K'ratchek's portrait (20,58): his
    twelve cells full, so Cermak's portrait (20,110) and a cell (213,80): `carried.py Cermak` shows
    thing 202 in his pack (slot 23), Gerakis no longer has it.
11. **The creation screen**: a start with no save, two clicks past the title, 32 s, CREATE
    CHARACTERS (165,92), a right-click on the first slot (NEW/ADD/CANCEL), NEW (110,57): a human
    fighter "Cromwell" with the dice log's score lines ("best of four 4d4 ... +4"), hit points and
    psionic lines. The big die (155,97) rolled him again (new lines, AGE 22). KITS (232,138), NO
    KIT off (240,106), MYRMIDON (240,114). DONE (279,183): PICK A WEAPON SPECIALTY, the first icon
    (72,46); `Cromwell starts with a plain bone polearm in the backpack too: a Myrmidon's second
    weapon spec`, `starts with more gear: Sling`, `Cromwell is 22 (a human: 15 + 1d8 = 7, as the
    creation screen rolled)`, the same age as the screen's. PICK A PSIONIC POWER: (123,62) four
    times, then VIEW CHARACTER with Cromwell (`powers.py`: Detonate, Disintegrate, Project Force,
    Ballistic Attack, Mind Blank; `carried.py`: leather armour and shield, bone long sword, sling,
    the polearm in the pack).
12. **The end**: the guard, the dice log, DOSBox-X and the Xvfb :59 this session started, killed
    by pid. A killed DOSBox-X leaves its memory file in /dev/shm (removed by hand; the start script
    removes the last one at its next start).

## Water

The slave pens only: nothing new.

## Not seen

- Windows and macOS (the owner's `dosboxx_memtest.py`), sound, full screen on a real screen.
- A damage spell in a fight: Lex's icons were crossed out on his one turn (hit just before it),
  and Entangle's box would have caught the party; only Bless was cast.
- The lost first menu click when the Loader itself starts the game (the last play's): this play
  started every game with `start_dosboxx.sh`, where it never happens.
- Nothing differed from 0.74 in what was played here.
