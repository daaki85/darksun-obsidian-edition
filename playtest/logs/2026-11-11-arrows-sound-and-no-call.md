# Spell arrows' sound, and a save where resting brings no call (2026-11-10/11)

## The Spellarcher's arrows: their cast sound
Build: obsidian-edition at "Spell arrows play their cast sound at once, from the USE screen".
From `pens-after-scar` with `PT_AUDIO`: Cermak's (member 2) sheet made a half-elf fighter/preserver
(race +18h 4, classes +21h 9, 11, levels 5, 5, kit byte +43h 1: multiclass group 14's first kit,
the Spellarcher, 57) and taught the four touch spells (`spellsetup.py 2=5 10 1 3 39`), in memory.
U, his portrait (66,108): the USE screen's top row is the spells themselves (a click there aims
Burning Hands: right-click cancels); the four arrow buttons are the row under SPELLS LEFT (157,147
the first). A slow press on Burning Arrows: "Cermak makes 25 burning arrows (5 a preserver level,
5): a 1st-level slot used ..." and the USE screen closed. One sound 0.47 s after the press; matched
against sound 81 (Burning Hands' cast, `playsound.py 81` recorded after) at correlation 1.00, and
78 (Chill Touch's) at 0.01. Before the fix the sound waited for the map's main loop.
Escape after the screen closed opened EXIT: SAVE GAME? (CANCEL at 145,116).

## The user's "rest no call" save (`saves/rest-no-call-user`)
The fire room, by the ring (leader 1960,840, camera 1728,736). A rest there passed 8 h 00 min 08 s
(the clock at DS:9B72h's far pointer, seconds: 118,324 to 147,132) and healed, but no call came.

Kurzak's call (GPL 136, from 1h): only when flag 20, local 32 and **flag 497** are 0; then the clock
(local 41) against global 4 (the last trip) + 60 x 485 (8 h 05 min); flags 498-500 skip it. The save
has flag 497 = 1 before any rest (a rest in `pens-fire-count4` leaves 497 at 0 throughout).

Flag 497: GPLI 1 (the index of named routines: id, offset, script) has routine 752 = 137:0001h, which
sets 497 and puts watches on three guard kinds (objects 90, 293, 317 within 8 squares: the alarm),
and 753 = 137:0085h, which clears 497 and takes the watches off. 752 is run by script 138 at 2B6h,
after "The key glides into the lock. The door opens." (door object 2155), and by script 143 at 328h
(a talk that opens door 2141). The save has flag 55 = 1 (the Trustee's key picked) and the key in
no one's pack: the party opened a door with it. 753 is attached by command 101 (a talk handler)
to objects 55, 260 and 261 in MAS 29 (the pens' master script, `KIND='MAS ' dec.py 29 0 140`);
script 17's routine at A4Ah (MAS 29 at 12Ah, while flag 88 is 0) makes two 260s and a 261 at squares
90-93, 57-59 with a 70% chance while flag 67 is 0 (or 94 is 1), with 753 on them. None of them was
on the map in the save. So the game's own escape state, not the rest: the call stays off until one
of those guards is talked to. Not tried in play (the walk from the fire room is long).
