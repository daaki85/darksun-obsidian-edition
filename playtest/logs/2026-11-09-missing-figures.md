# Play test: figures vanishing from the map (2026-11-09)

Under test: the turn-undead session's report (logs/2026-11-08-turn-undead.md, "Not done"): in a long
DOSBox session the party's figures, and at times the foes', weren't drawn though their places were
right, clicks on them missed, and I then Escape brought them back for a while. Was it DSCLOG's
drawing savings (2026-11-08), the game's own drawing, or the memory edits?

**Answer: none of the drawing code. The Loader's dressing of the party's figures (sprites.py) uses
up the game's picture store, and the game then can't load figures back.** Reproduced at will, with
the build of HEAD (0981381, `git archive` into a scratch folder, its own Loader and settings; the
shared repository's working tree was not used), and fixed by a change in sprites.py (a proposed
diff, not committed: obsidian-edition/ was another agent's to edit).

## Setting

- DOSBox under `flock /tmp/playtest/dosbox.lock` throughout (held by a background flock, released
  at the end); DOSBox, its Loader, the watchdog and the watchers were this session's own, stopped by
  pid afterwards. `fountain-user` loaded four times (each load is an area load: see below).
- New tools (playtest/): `figwatch.py` (passive: each member's screen place, map record +0, picture
  slot and that slot's number and flags, the draw list's order, a grab cut round each figure),
  `drawlist.py`, `cachelist.py` (the game's picture slots), `poolfree.py` (the game's picture
  memory), `fillcache.py` (gear changes made fast, in memory), `figcheck.py` (a grab before and after
  DSCLOG's VIEW_REDRAW, the pixels changed round each member).

## Clean play first

`fountain-user`, the ambush fought out (fightout.sh), walks, scrolls, the inventory opened and
closed, with figwatch every 2 s: every figure drawn throughout; the draw list (DS:6690h) stayed in
rising y, each party thing in it, its back index (+1) right. No vanishing.

## What the game does with figures' pictures (DSUN.EXE, read with capstone)

- Each thing on the map names a slot of the game's picture table (thing +0Fh; the table at load
  segment + 3E60h, 16 bytes a slot: +0 the picture's number, +2 its length, +6 its place in the
  store, +0Ah its far pointer while in memory, +0Eh flags 1 stored, 2 in memory; DS:1F84h the slots
  taken, at most 300).
- A picture first needed gets the next slot (25FA6h): read from the GFF, written to a **store of
  fixed size, 741,376 bytes** (0xB5000, allocated at 60D9Bh, memory handle DS:4C33h), its place the
  last slot's place + length. Slots and store room are given back only when an area is loaded
  (the flush at 1DBD:06BEh, called from the region load at 1D4B6h). **25FA6h ignores the store
  write's error** (1187:1FB5h's result unread).
- Pictures are let go from memory when room is short (opening the inventory lets them all go) and
  read back from the store when drawn (25D6Ah). **If that read fails, 25D6Ah returns without
  freeing the memory it just took**, and tries again (and takes more) at every drawing.
- The drawing (1DBD:0002, the call at 23308h) skips a thing whose picture can't be had.

## The Loader's part (sprites.py, unchanged since 2026-11-07, the mechanism since October)

When a member's outfit changes (anything on the figure: a weapon, a shield, armour, a magic +0Fh
on a weapon, grey hair), the Loader writes the new pictures into its SEGOBJEX copy, marks the
loaded ones FFFEh (STALE) in the game's table and empties the member's slot. The game never takes a
STALE slot back: each dressing costs a new slot and about 7 KB of the store (the dressed party
pictures are 5.7 to 7.3 KB; the region's own average 1.4 KB). In the pens, 200 slots and 275 KB are
taken as the area loads: about 64 pictures loaded anew fill the store.

## Reproduced

| Step | Seen |
|---|---|
| Lex's sword moved between her hand and the backpack in the inventory, six times (I, two clicks, Escape) | each move: one more slot (out of a fight, the walking picture), the old one FFFEh (210 to 216 taken) |
| `fillcache.py 0 10 298` (the shield's slot byte toggled in memory, the Loader dressing each time), out of a fight | 298 slots; all drawn |
| one change more, at 300 slots | Lex not drawn at once: her slot FFFFh, none to be had; I then Escape didn't bring her back |
| Reloaded, in the ambush: filled to 300, then one attack | **every figure gone, the party's and the foes'** (only "Miss" and the shadows): every slot "not in memory" (img/2026-11-09-figures-all-gone.png) |
| I then Escape | all back but Lex (her slot past the store's end) (img/2026-11-09-figures-after-i-escape.png); within a minute, with nothing done, the others went again one by one |
| Reloaded, in the ambush: filled to 266 slots only (Lex's slot 265 at 735,717 + 7,312, past 741,376) | all drawn while her picture stayed in memory; I then Escape: Lex gone (img/2026-11-09-figure-gone-past-store.png); `poolfree.py`: the picture memory's free bytes 10,697 after the Escape, 1,386 twenty seconds later with 17 pictures in memory instead of 28, a step at a time as Lex's failed reads kept the memory they took |

So the report's picture, whole: a figure whose picture lies past the store's end can't come back
once let go, its every drawing eats the picture memory, and then nobody's picture can be read back;
the inventory frees that memory (all back for a while, that one excepted), and it runs out again.
Clicks miss because the figure isn't there to be found.

The turn-undead and earlier spell sessions (one DOSBox, `fountain-user` loaded once, hours of tests)
changed the party's gear often, much of it in memory (Jenna's swords given Chill Touch through
+0Fh, items moved by hand; whether a spell's weapon or Magical Stone's stones dress the figure wasn't checked): each change cost the store. In clean play
the same comes from gear changed in the inventory, about 30 to 60 times without leaving the area
(more in a fight, where the walking and the fighting picture are both loaded anew).

## Not the drawing savings, not the game alone

- The store's size is the game's own constant, and the leak is the Loader's STALE marks, older than
  the drawing savings and the memory pass; DSCLOG's drawing never loads or frees a picture
  (shadow_of reads the table only, and skips a picture not in memory). Old DSCLOG builds weren't
  bisected: the vanishing came and went with the slots and the store alone, in HEAD's build.
- The game alone, without the Loader's dressing, takes each picture number once per area; it
  wouldn't run its store out in the pens.

## The fix (proposed: scratchpad figures-fix.diff, not committed)

sprites.py: before dressing a figure anew (not its first dressing), `_room_for` reads the slots
taken and the last slot's place + length, and dresses only if the two pictures' room (the copy's
room for them) still fits with 64 KB and 24 slots spare for the game's own (a monster's, a spell's).
Else the figure is left as it is (drawn) and tried again later: after an area load the store is
empty again and it is dressed. A unit test (test_no_room_in_the_games_store) fails without the
change and passes with it; tests/test_sprites.py 21 OK.

In DOSBox with the change (the copy's Loader restarted, `fountain-user`, the ambush):
`fillcache.py 0 10 290` stopped at 253 slots (the Loader left the figure), I then Escape and the
whole fight with fightout.sh: every figure drawn (img/2026-11-09-figures-with-fix.png), the picture
memory steady (5,813 free at the end, 19 in memory).

A fuller fix would give the slots back: DSCLOG calling the game's own flush (1DBD:06BEh) at a safe
point in the main loop once the store nears its end, as an area load does (everything then loads
anew from the files). Not tried.
