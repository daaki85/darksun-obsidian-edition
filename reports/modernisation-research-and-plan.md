# Modernising the game further: research and plan

Research of 2026-11-16 into nine additions the owner chose, and the plan that follows from it.
Everything here was read from the mod's code, the two games' files and the DOSBox sources;
**nothing was run in the game**. "Verified" means read in source or disassembled; the rest is
marked inferred or unknown, and each item lists the experiment that settles it. DSUN.EXE numbers
are file offsets unless written `segment:offset`.

## What the research changed

- **No memory pass is needed.** All the helper work together is about 250-300 bytes of the
  segment's 960 spare and about 136 bytes of the tail's 1.3 KB. The far block (36 bytes) is not
  used.
- **F5 and F9 are already keys of the game** on the map (its key table at file 1BC5Bh: F5 to
  1B811h, F9 to an overlay at 810DCh). What they do is not established.
- **A save just before a story fight is risky**: it would be taken inside the script that starts
  the fight, and the script interpreter's state was not seen among the things a save writes.
  Autosave on entering an area and when a fight ends instead.
- **GOG already plays General MIDI** (SOUND.CFG: `mt32mpu.adv`, music type 4), through Windows'
  own synth. The gain is a better synth (a soundfont) or a real MT-32 score, not a new device.
- **DOSBox-X can keep the game's memory in a shared file** (`[dosbox] memory file=`), which
  DOSBox Staging can't. The Loader could map that file instead of reading another process: the
  only practical route to macOS, and a way round sandboxes on the Steam Deck.
- **Wake of the Ravager is the same engine a year on**, smaller in maps and larger in script
  than Shattered Lands; about 40% of the mod's code patch sites are recognisable in it.

## 1. Quick save, quick load, autosave

**Findings**
- More saves: the page is one letter poked into two game strings (DS:1DCFh `SAVE??.SAV`,
  DS:1DDAh `SAVE%.2d.SAV`; `sp_page`, `sp_letters db 'EBCD'`, `PAGES equ 4`). A fifth page is one
  letter in the helper, a fifth button in `savepages.py`, and `PAGES` and the copy pattern in
  `namedsaves.py`.
- The game's save is the overlay entry 560:89 (file 6912Dh), `save(far char *file, far char
  *description)`: checks disk space ("Disk Space Low !!!" under about 1.33 MB), writes the SAVE
  chunks and STXT 1 into DARKRUN.GFF and copies it to `file`. It reads nothing from the save
  window. The window's wrapper (7468Bh) adds an optional 11-byte PREF chunk.
- Load is 560:8E (69218h). The window's overlay has entries that open LOAD (590:20) and SAVE
  (590:25) with no arguments.
- The game refuses a save only in a fight (word 377E:0019h; "CAN'T SAVE DURING COMBAT", 714E5h).
- The helper's main-loop hook `PROBE_SCROLL` already serves Loader requests (`sound_req`,
  `view_redraw`, `panel_on`) and the helper already calls an overlay stub (`give_xp`).
- Keys: `our_key` in the INT 16h hook; a counted key costs 10-65 bytes.
- The Loader sees the region (DS:117Ch) and the fight flag within 50 ms, at no helper cost.

**Design** (helper: about 110-130 bytes)
- The Loader holds the policy: ten slots on a page Q (`SAVQ01.SAV`...), the name ("Quick 3 -
  Day 47, 14:20"), rotation, autosave on a new area once its item lists settle and when a fight
  ends, never with a window up; what happened goes to the dice log and a floating name.
- The helper gets two counted keys, one "save now" request in `PROBE_SCROLL` (the two strings
  written by the Loader into `pick_text`), and the fifth letter.
- Quick load opens the game's own LOAD window on page Q (590:20) rather than calling 560:8E, which
  would skip the window's steps.

**Experiments, in order**
1. What F5 and F9 do in the unmodded game. If either matters, use other keys.
2. A save by 560:89 called from `PROBE_SCROLL`, compared chunk by chunk with a window save of the
   same moment, then loaded and played on (the window runs 1587:22BA, 1587:2CCB and 191F:0B36
   first; their part is unknown).
3. How long a save takes (85,680 bytes), and memory at that moment (`heapcheck`).
4. Whether rotating slots are copied to `Named saves` at all.

**Tests like**: `test_savepages`, `test_namedsaves`, `test_dsclog` (Unicorn), `test_gamepatch`,
`test_loot`.

## 2. Showing what can be used

**Findings**
- `ring_pass` rings every thing in the draw list whose `RING_TAB` byte is set (520 entries, no
  limit on how many) and never tests the kind: items, bodies and scenery can be ringed if they
  are in the draw list.
- The ring's colour table (`RED`, 256 bytes) is written by the Loader, so another tint costs the
  helper nothing, but the Tab ring shares it. A true second colour is 256 bytes in the tail and
  about 30 of code.
- Floating names: 4 slots; each more costs 360 bytes of upper memory, so 3 more at most.
- The Loader can read the BIOS shift flags (0:0417h; Alt is bit 3) every 50 ms. Alt alone sends
  the game no key.
- The Loader can list things (table at load+3972h:0C36h), items and their types (+08h = 60h is
  scenery), bodies (objects 1101 and 2666), creatures, and doors as squares.
- Unknown: where the game keeps which objects have a script. Fallback: read the region's MAS
  script with `gpl.py`.

**Design** (helper: 0 bytes)
- While Alt is held outside a fight, the Loader rings doors, containers, bodies, ground items
  and people in a gold tint, and names the four nearest the pointer.

**Experiments**
1. Whether doors and ground items are in the draw list, and where a ring falls on them.
2. Frame time with 20-30 rings.
3. A stuck Alt flag after Alt+Tab.

**Tests like**: `test_targeting`, `test_labels`, `test_shadows`, `test_dsclog_drawing`.

## 3. The journal

**Findings**
- `textlog.py` already captures every dialogue, the reply chosen and every message box; the
  Dialogue tab shows them with a find bar, 3,000 lines at most, and nothing is kept on disk.
- Speaker names are learned, not stored by the game; the area is a number only (a table of the
  34 regions' names has to be written); the game's day and time are known.
- Quest state: 754 global flags in use (all 808 are taken) and 137 global numbers of 200. Quest
  XP goes through script 74 (57 call sites in 40 scripts, 78,510 XP: about 45-55 rewarded
  steps); 37 of the 57 set a flag within a few commands. All talk is inline in the scripts, so a
  tool can draft a table of flag, script, nearby text and XP.
- "... receives N experience points!" already passes through the text buffer.
- Loads: the Loader misses a later save of the same party loaded mid-play (DEVELOPMENT.md).

**Design** (helper: 0 bytes)
- `journal.py`: an append-only file of entries (id, parent, day and time, region, speaker,
  text, reply, XP), fed by the dialogue and message boxes.
- The newest entry's id is kept in two spare global numbers (198-199), which the game saves:
  when the id in memory differs from the last written, a save was loaded, and the journal shows
  that save's branch. Old saves fall back to cutting at the clock.
- A Journal tab: by day, person and area, with the find bar and a filter.
- Later: open and finished quests from a table of the project's own wording, drafted by a tool
  from the scripts and named by hand (a day or two).

**Experiments**
1. That numbers 137-199 survive save and load and no engine code touches them.
2. How often the numbers pointer is null (the Loader must wait and retry).

**Tests like**: `test_textlog`, `test_namedsaves`, `test_flagrange`, `test_audit_flags`,
`test_gpl`, `test_viewer_settings`.

## 4. Chance to hit before the swing

**Findings**
- `GameData.weapon_hits` already gives THAC0 for each ready weapon before a target is known
  (strength or dexterity, effects, the weapon, two weapons, kits, specialisation).
- The target's side is in `_thac0_breakdown` (Blur, a held target, "can't see"...), and AC in
  `counted_ac` or, once attacked, `last_ac`.
- The Loader knows whose turn it is and who is chosen (`targeting.py`).
- Missing: the target's facing (from behind and backstab), a not-yet-attacked monster's AC as
  the game counts it, and which weapon swings at range.

**Design** (helper: 0 bytes)
- `predict(attacker, target)`, shown on the Tab line ("needs 14+ (35%)") and in the panel's
  header. Where a term is unknown, say so ("14+, less from behind") rather than guess.

**Experiments**
1. Predictions against the log's own "needs N+" over several fights, by kit and weapon.
2. Where the facing is kept.

**Tests like**: `test_targeting`, `test_combatlog`, `test_dicelog`, `test_ledger`.

## 5. Where a figure can walk this turn

**Findings**
- Movement points are Move x 10 a turn (a word for each combatant, 37BD:022Bh). A step costs 10
  straight and 14 diagonal (table at DS:055Ch; the one `sub` at 59194h). Under 10 left is
  zeroed.
- The grid is 128 x 98 squares of 16 pixels, live at the far pointer DS:0556h; bit 80h blocks.
- Not read: the path finder's own test (22339h) for edges, doorways, corners and allies.
- No existing channel draws at arbitrary squares: rings, shadows and names all belong to
  things.
- A blow covers the 8 squares round each of the attacker's squares; with a polearm, also those
  2 away in a clear line.

**Design** (helper: about 100-150 bytes in the segment, about 136 in the tail)
- The Loader works the squares out (shortest paths at 10 and 14 on the live grid, within the
  points left) and writes a 32 x 32 bitmap; a new `tint_pass` after `ring_pass` marks each set
  square with a few tinted dots through the ring's own routines (a solid fill would be slow).
- Second step: the squares enemies' blows cover, in another pattern.

**Experiments**
1. The path finder's rules, by disassembly and then in a fight.
2. Whether attacking ends movement.
3. Drawing time.

**Tests like**: `test_dsclog_drawing`, `test_shadows`, `test_reach`, `test_stuckwalk`,
`test_fits_upper_memory`.

## 6. Music

**Findings**
- The game has three scores for each tune: General MIDI (GSEQ), MT-32 (LSEQ) and PC speaker.
  The choice is in `SOUND.CFG` (59 bytes). The mod's sounds and music buffer don't depend on it.
- GOG's DOSBox 0.74 has no built-in synth: music goes to a Windows MIDI device
  (`midiconfig=` picks which). DOSBox Staging and DOSBox-X have FluidSynth (a soundfont) and
  MT-32 emulation (the player's own ROMs) built in.
- Soundfonts: GeneralUser GS is about 30 MB under its own permissive licence; smaller and larger
  free ones exist. Licences need a second look before anything is bundled.

**Design**
- Now: a choice of Windows MIDI device on the Options tab.
- With a second engine: a soundfont picker (one named in the docs, not bundled), and MT-32 by
  writing a changed copy of SOUND.CFG.

**Experiment**: run the game's SOUND program choosing MT-32, then General MIDI, and compare the
two SOUND.CFG files.

## 7. Picture

**Findings**
- The Loader offers full screen or a window at 1x to 4x.
- 0.74 can also do scanlines (`scan2x/3x`, `tv2x/3x`) and a sharp OpenGL output (`openglnb`).
  It has no whole-number scaling in full screen, no borderless window and no shaders.
- Staging: `integer_scaling`, `shader=crt-auto` or `sharp`, `fullscreen_mode=forced-borderless`.
  DOSBox-X: `output=openglpp`, `glshader`.

**Design**: scanlines and sharp now; whole-number scaling, borderless and CRT with the second
engine. **Experiment**: one picture of each new mode at 3x, checking the pointer still tracks.

## 8. A second engine, Linux, Steam Deck, macOS

**Findings**
- The Loader finds the game's memory by the BIOS date and the interrupt table, which Staging
  and DOSBox-X write the same way (untested on either).
- Staging's upper memory and missing HMA match 0.74's, so the helper should load as now.
  DOSBox-X has a real HMA and movable upper memory: to be measured.
- The Loader insists on `DOSBOX/DOSBox.exe` in the game folder; `--recompiled` already shows the
  pattern for starting another program. For another engine the Loader should write a whole
  configuration of its own.
- Fixed cycles on another build won't give the same speed: steady pace needs measuring again.
- Linux: the Loader's memory reading, patched game and configuration already work
  (`playtest/start.sh` is in effect a Linux start). With DOSBox started as the Loader's child,
  no root should be needed (Yama allows a parent its descendants; not testable in a container).
  The distribution's 0.74-3 has no overlay mount: the starting saves must be copied.
- Steam Deck: tkinter on SteamOS and a Flatpak DOSBox are unknowns. A Steam Input layout
  (trackpad as mouse, buttons as the mod's keys) is sturdier than DOSBox's mapper. Use the
  start without the Loader's window in Gaming Mode.
- macOS: reading another process is not practical for an unsigned program. Only the
  memory-file engine gets there.

**Design**
- Engine choice on the Options tab: GOG's (default) or a DOSBox-X the player has installed, the
  Loader mapping its memory file. Staging only if DOSBox-X fails.
- `start.sh` for Linux beside the `.bat` files; a Deck layout; macOS after, if someone can test.

**Experiment**: the mod's configuration under DOSBox-X with a memory file: map it from Python,
find the BIOS date and the helper's header, read one dice-log line, and write one byte the game
then acts on (the dynamic core may cache code the Loader patches).

## 9. Wake of the Ravager

**Measured, the two installs side by side**

| | Shattered Lands | Wake of the Ravager |
|---|---|---|
| Install | 36 MB | 287 MB (speech, CD music, films) |
| Game data | 16.2 MB | 16.4 MB |
| Regions | 33 | 20 |
| Scripts | 250 (0.89 MB) | 350 (1.48 MB) |
| Words of text | about 117,000 | about 197,000 |
| Creatures / items | 291 / 755 | 352 / 1,233 |
| Spell and power records | about 196 | 320 |
| Spell levels / level cap | 1-5 / 9 | 1-7 / 15 |

**The engine**
- The same: real mode, Borland's overlays, the same memory layer, GFF and GPL. `gpl.py` decodes
  349 of its 350 scripts once given Shattered Lands' field types.
- Changed: every address; the creature (49 bytes), sheet (66) and item (23) records; spells
  moved from the program into a data file.
- Of the mod's 426 code patch sites about 170 are recognisable (122 strictly). Carried over:
  the dice roll, message box, View Character, heap, overlay buffer, picture slots. Rewritten:
  attack and damage, saving throws, AC, level-up, spells, rest, prices.
- The mod is 457 patches, 134 hook vectors and about 84 data addresses, all to be found again.

**Carrying a party over**
- The game's own tool, CHARTRAN.EXE, reads a Shattered Lands save and writes the Ravager's
  character file, translating items through a table of 234 pairs.
- The mod's kit (sheet +43h) and specialisations (+14h..+17h) have no place in the Ravager's
  shorter sheet, and the mod's own items aren't in the table: they would be lost or turned to
  coin. The Loader must do the transfer, or finish it, and keep kit and specialisations in spare
  bytes proven unused, or in a file of its own.

**Phases, by value for effort**
1. Recognise the game; party and dice log (the roll and the message box match exactly).
2. Engine bugs whose sites match (picture slots, the overlay buffer, the record table).
3. The transfer that keeps kits and specialisations.
4. Script tools, then its script bugs.
5. Rules and kits. 6. The panel, screens and graphics.

**Effort against the Shattered Lands work**: phases 1-2 perhaps 15-25%; everything, 60-80%
(medium confidence: nothing was run, and its free memory with speech loaded is unmeasured).

**Experiments**
1. Patch only the roll (5A22h) and the message box (59A0Bh) into a copy, load the helper, and
   see the Loader find the party; measure free memory.
2. Run CHARTRAN on a mod save with a kit and specialisations and compare the records.

## Order of work

| Release | What | Helper bytes |
|---|---|---|
| A | Journal (talk, search, rolled back with saves); chance to hit; scanlines and sharp picture; MIDI device choice | 0 |
| B | Quick save, quick load, autosave; showing what can be used | about 130 |
| C | Squares in reach; quests in the journal | about 150 + 136 in the tail |
| D | DOSBox-X as an engine; soundfont and MT-32; whole-number scaling, borderless, CRT; Linux start; Deck layout | 0 |
| E | Wake of the Ravager, phases 1-3, as a build of its own | its own helper |

Each feature has a switch on the Options tab, tests, a play check with the playtest kit, and
its pages in the player's and developer's documentation.
