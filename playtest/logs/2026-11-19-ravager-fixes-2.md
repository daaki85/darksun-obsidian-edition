# 2026-11-19 (2): the saving throw found by hand, and the thief skills' fix seen at work

**Under test:** the fixes with no clear twin in Wake of the Ravager's program, found by reading its
code; and one fix seen working in the sequel's own code. Follows logs/2026-11-19-ravager-fixes.md.

1. **The saving throw** (SL 79B65h-79BC4h): SL's last lines "mov al,[bp-2] / cmp al,[bp-1] / jae
   saved". The sequel's at 66EA6h, found by the six bytes of SL's `save` patch ("8a46fe3a46ff",
   twice in WotR's file: 61E76h is another routine, signed already, with a natural 20): "cmp
   al,[bp-1] / jb fail / jmp saved", the same unsigned compare. The fix: `jb` made `jl`, 66EACh `72
   03` to `7c 03`, no relocated word (in ravfixes.py as OWN_FIXES).
2. **Negative Plane Protection** (SL 7A7E9h: "push 6 / push 27h", the save against Vampiric Touch,
   its effect 2Ah): WotR 84DDAh "push 4Fh ... push 6 / push 26h", 26h WotR's Vampiric Touch (DATA
   38; NPP is DATA 153, 99h). The same bug; both records' save byte (+1Fh) a0. Not fixed: SL's fix
   is a new record that allows a save.
3. **ravfixes.py** now copies the files the game writes (DARKRUN.GFF, DARKSAVE.GFF, CHARSAVE.GFF,
   SAVE*.SAV) instead of linking them: DOSBox writes in place, and a link wrote the original's too.
4. **Starting without the mouse:** S on the main menu is START GAME (ravstart.sh: Shift twice,
   S, 80 s). Through the opening talk: 3, then Return, a few times.
5. **The party** (the sheets at the far pointer DS:19C5h, 42h bytes): 0 an elf
   preserver/psionicist/thief 6/6/7 (Ar'anda), 1 a human earth cleric 7, 2 a thri-kreen
   fighter/druid 6/6 (Thy'rokh, the leader), 3 a half-giant gladiator 7.
6. **The mouse:** the pointer is DS:A109h (x) and A10Bh (y) in 320x200 game pixels (found by moving
   the mouse and diffing the data segment); the game is 320x200 shown at 640x480, so game y =
   window y / 2.4. `ravclick.py` (new) moves there and presses slowly. The first clicks went
   wrong for that reason (aimed at window y / 2).
7. **The USE screen** (top-left icon, 22,17): out of a fight it acts for the leader; a portrait
   click doesn't change who. Hovering names a button in the bar below. The small top button left
   of a portrait is MAKE <NAME> LEADER (47,43 for the first); the bottom row: VIEW CHARACTER
   (47,171), VIEW INVENTORY (74,171); LEVEL (197,171) steps the spell level. The inventory has the
   portraits down the left (30,23 the first): Ar'anda a sling, a dagger and a +1 long sword. View
   Character shows no thief skills: the game never shows them.
8. **The thief skills, emulated:** `ravthief.py` (new). The routine (8C647h) and its overlays
   were swapped out (only a copy in XMS, at 2C82F3h), so: the live memory below A0000h, every
   overlay above it from Dark Sun Recompiled's build_image.py (its PSP set to the live 0192h), and
   that image's stubs. The first runs gave the same numbers both ways: the emulator's stack had its
   own segment, but the routine reads its stack buffers through DS (Borland: SS is DS). With SS = DS:
   pick pockets 81/86, move silently 70/80, hide in shadows 70/75, climb walls 96/106 (the game's
   list / the fix), the rest equal: SL's penalties, 5, 10, 5 and 10.

**Stalls:** none; the clicks missed until the y scale was known.

**Water:** none seen beyond the pot and jug in Tyr's opening room.
