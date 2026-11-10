# 2026-11-09: DSCLOG memory pass 2, checked in DOSBox

Under test: DSCLOG with
1. the sites after VEC_CR_SPELLS's INT (`rl_sites`) dispatched through a table (`site_tab`),
2. the rings' outlines kept as one quarter each (`ring_points` mirrors them, `ring_dot`),
3. the tail (`tail_seg`, the header's +1834: paragraphs after the image, kept with it) holding the
   labels' slots (`lbl_slots`, its offset at +1838; the header's +374 to +1813 hold other buffers),
4. the companion's names (`extra_names`) and `ticks` in the tail,
5. the item types in the tail (no FAR_DATA copy), LIGHT, the puffs and DARK in the far block (the
   HMA), and the crash report's stack written from where it is.

Code space spare in the helper's segment: 2,032 bytes before, 6,032 after (image_len 63,504 ->
59,504; resident_end 61,840 -> 58,096; FAR_END 64,842 -> 64,784, the HMA's free 694 -> 752;
UMB_NEED 6,065 -> 5,995 paragraphs, UMB_KEPT 7,687 -> 7,617, spare 495 -> 565). Unit tests: the
whole suite after each step, 1,549 tests OK (26 skipped).

DOSBox under `/tmp/playtest/dosbox.lock` (another agent's hold waited out; this session's DOSBox,
dice log and watchdog stopped at the end, the lock let go).

## Build in place (`buildcheck.py`, new)

`loadsave.sh pens-after-arena`: header C91B0h, far_seg FFFFh, tail_seg D7A2h (C91Bh + 0E87h:
right). 40 bytes of each of rl_sites, site_tab, ring_points, ring_dot, ring_outer, label_tick,
label_stamp, label_put, probe_names_fill, probe_types_fill, probe_tick, dust_tick, puff_raise,
puff_draw, dust_pass, spans_flush, build_dark, dos_quit the EXE's; all 134 vectors of the table at
their handlers; the tail's item types and names the EXE's, byte for byte. (far_init differs, as it
should: AFTER_INSTALL's buffers are laid over the install code.)

## Upper memory (memaudit.py, pens-after-arena, the map open)

The build before (HEAD's DSCLOG.EXE put in `dos/` for one load) and this one:

| Block | before | after |
|---|---|---|
| DSCLOG (with its PSP; after: and its tail) | 63,760 | 62,640 |
| free, between DSCLOG and the overlay buffer | 704 | 288 |
| overlay buffer | 32,992 | 32,992 |
| free, in one piece | 35,856 | 37,392 |
| see-through tables, music buffer | 14,160, 12,016 | 14,160, 12,016 |

DOS memory free after the game: 97 KB (99,008 bytes in one piece) both times. umb_need 6,065 ->
5,995 paragraphs.

## Walking (pens-after-arena)

walkto (1500, 344): shots mid-walk show the shadows under the figures and the dust's pale puffs
behind the walkers. In memory: 138 puffs raised (header +240), LIGHT in the far block made by the
Loader (17 colours), DARK built there (256), TICKS being written in the tail (tick_seq 357).
`dacwatch.py 3`: one palette, read. The freeze report's text (`freeze.report_text`) lists the
timer's notes from the tail: the game's code places, DS 44F8 (the game's) in each.

## A fight (fountain-user)

- **The ring**: Tab chose an Arena Guard, a red ring under him. The same with the build before
  (another load): the 36 x 20 pixels round the ring identical in both shots (the other differences
  are the status box and the party's places: the first turn was another's).
- **Labels**: Ester's attack missed the Templar: "Miss" floated over him (the tail's slot 0 written
  by the Loader, number 3). Ester's Magical Stone: "Magical Stone" over her, "Miss" over the Guard.
- **Turn Undead** (`turnsetup.py 3 4 22=1`: Seneca cleric 4; combatant 25, the fight's Templar, an
  undead of 1 HD): U, the TURN UNDEAD button showed (157,146), the aiming box, a click on him:
  `Seneca turns Templar: turned: flees 3d4 = 10 rounds (Afraid), automatically (T) (priest level 4
  vs 1 HD, AD&D's table)`, then `Seneca gives Afraid to Templar: turned, it flees`.
- **A spell's to-hit** (Ester, `spellsetup.py 2=9`, Magical Stone at an Arena Guard, three throws):
  `attack d20 = 7, needs 11+ (50%) (THAC0 19, +4 DEX; target AC 4) -> MISS`, then 18 HIT (2 damage),
  then 10 MISS.
- **Seneca's item names and types**: the inventory's bar METAL SHADOWSEEKER on her hand; the panel
  "+1 Hayneedle 1D4+5", "+1 Shadowseeker 1.5x1D6+7".
- **The Effects screen**: Lex "KIT: SPELLARCH" (the short names), "SPECIALIZED IN" / "BOW"; Jenna
  "KIT: STALKER", "EXPERT IN" / "LONG SWORD" / "BOW".
- **The Look box** (the eye on Legcrusher): GUARD, LEVEL 3, CLUB, CLUB, HP 150/150 AC 10, THAC0 17
  AL CG; the dice log's Look line.
- Not a fault of this build: Lex's USE screen's LEVEL button stayed on LEVEL 1 after
  `spellsetup.py 0=10 33 28`, with the build before too (checked on its load). Ester's level-1
  Magical Stone stood in for the to-hit test.

## The creation screen (start.sh, CREATE CHARACTERS, NEW)

The scores rolled (each best of four 4d4 in the dice log), SUM 101/101, the age (15 + 1d8), THAC0,
the KITS label; STR lowered (17 -> 16), CON raised (16 -> 17), the die rolled again (six new
scores, SUM 98), the class changed to gladiator (hit points rolled again, THAC0 M18 R18). The
RL_* and CR_* sites all through the new table.

## A shop sale (pens-after-scar)

walkto (1816,408), (1704,408), (1592,440), `viewto.py 1592 520`, a click at (184,172) through
Kurzak's entryway, `route.py 1560 880`; the eye on Kalzith (262,124): his Look box; talk (163,150),
1 ("We mean no harm"), two box clicks, 1 ("Show us what you have"), a box click: his shop. Gerakis's
Leather Sling (66,48) to SELL (273,62): "I'll give you 1$" (SELL_PRICE), TAKE IT: "SOLD!", 1$.

## Not done

- The recompiled program: not tried (its `ds1o` would need lifting from this helper; the tail is
  a new segment it reaches).
- The crash report in the game (GAMEMSG.BIN): only its unit test (the file's bytes as before).
- Nothing saved; every memory edit died with DOSBox.
