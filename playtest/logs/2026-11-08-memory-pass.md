# 2026-11-08: DSCLOG memory pass, checked in DOSBox

Under test: DSCLOG with DAC, RING_TAB, RED and the dust's walked counts moved to the far block,
the item types copied there from the image (FAR_DATA), the vectors set from a table, the AD&D XP
table as words of 50, and the item names NUL-terminated.

## Build in place

`loadsave.sh pens-after-arena`: DSCLOG's header at C91B0h (segment C91Bh), far_seg FFFFh (the
HMA). The code of build_dark, xp_need, ring_pass, dust_tick, probe_names_fill and probe_types_fill
in memory is the new EXE's, byte for byte; all 134 vectors of the table point at their handlers in
segment C91Bh; FAR_DATA (+FAF2h, 600 bytes, the item types) in the far block is the image's.
DAC in the far block (+F2E2h) holds the palette (690 non-zero values); RED (+F7EAh) made by the
Loader (207 non-zero).

## Walking (pens-after-arena)

The combat log panel showed with its usual colours. Walked the party west and took shots mid-walk:
dust puffs behind the walkers, shadows under the figures, as before. `ghostchk.py 0` marked thing 0
see-through: the figure at the back drawn see-through (the floor showing through), the others solid.

## Upper memory, measured (memaudit.py, the map open)

The helper's block 62,208 bytes with its PSP (3,888 paragraphs: 16 + `kept_end` 61,952 / 16), the
overlay buffer 32,992, the see-through tables 14,160, the music buffer 12,016; free 37,392 bytes in
one piece (E078h), 720 bytes between the helper and the overlay buffer, 144 at C900h. DOS memory
free after the game 97 KB (99,008 bytes in one piece).

## A fight (fountain-user)

`loadsave.sh fountain-user`, one click on the message: fight_on 1, the ambush. Tab chose an
Arena Guard: the red ring under it (RING_TAB in the far block marked 1 thing). L showed the panel,
its colours right (it takes its inks from DSCLOG's DAC, now read from the far block).
`fightout.sh` finished it (DONE after 11 turns), the dice log's XP lines as usual (+192 for the
Templar's 1400 and so on).

## XP for the next level (AD&D's tables on, rules_hi 7FFh)

View Character after the fight: Lex Fighter/Preserver 3/2, EXP 4487 (5000 Pr); Jenna Ranger 3,
7998 (9000: the ranger's row, now the gladiator's); Ester Fighter/Cleric 2/3, 3740 (4000 F);
Seneca Thief/Fighter 3/2, 3987 (4000 F). Each as `tables.xp_needed` gives.

## The companion's item names and types

Seneca's held weapons (types 115, the first of the item types now copied from the image into the
far block): the inventory's bar says METAL SHADOWSEEKER on hovering the hand; its panel lists
"+1 Hayneedle 1D4+5" and "+1 Shadowseeker 1.5x1D6+7". Names (now NUL-terminated) and types right.

## Upper memory, the old build against the new (pens-after-arena, memaudit.py)

The old EXE (the build before this pass) put back in `dos/` for one load, then the new one again
(`cmp` with the build: identical):

| Block | before | after |
|---|---|---|
| DSCLOG (with its PSP) | 65,248 | 62,208 |
| free, between DSCLOG and the overlay buffer | 752 | 720 |
| overlay buffer | 32,992 | 32,992 |
| free, in one piece | 34,320 | 37,392 |
| see-through tables, music buffer | 14,160, 12,016 | 14,160, 12,016 |

The small free piece between the helper and the overlay buffer was there before too (47
paragraphs then, 45 now): not new.

## Tools changed

`dacwatch.py` and `ghostwatch.py` read DAC at `far_seg` x 16 + its offset (the far block); checked
`dacwatch.py 3`: one palette, read.

## Unit tests

The vectors now come from a table (`all_vectors`: the vector byte, then the handler's word), so
26 places in tests/test_dsclog.py that found a handler by the install's old bytes
`B8 vec 25 BA` failed (thousands of subtests: slow, about 25 minutes before a timeout). They now go
through `vector_table` / `install_at` (the table read after FAR_DATA's bytes, the header's +144 and
+174). After that: test_dsclog 323 tests OK in 7 s; the whole suite OK with python3 (1523, 26
skipped) and python3.12 (357 skipped); the drawing tests' screens identical to before.

## Last

Reloaded `pens-after-arena` with the new build (the old one had been put in for the comparison):
all 134 vectors at their handlers in the table. DOSBox left running, idle.
