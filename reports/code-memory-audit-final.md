# Final code and memory audit before the release (2026-11-19)

*Status: applied on branch `claude/final-audit-fixes` (2026-11-19), all three risks and the eight
cleanups. R2: the Loader's off-branches removed and their tests reworked to the rules' numbers (8
tests that ran only an off path removed); the kits' `spec` and `adnd` arguments kept, their tests
driving both. R1: the four literal offsets in code made constants, the docstrings' +368 and +1852
left as text. R3: the copies also set 0644 (mkstemp's are 0600). C1: `wp_redraw` gone, the room
unchanged (the image is padded to the paragraph). C6: `theme.py`'s re-exports were already marked
`# noqa`. The two still open from the last audit (the stats thread's idle step, `crash-logs/`) are
not in this list; they were fixed after, on `claude/older-loader-bugs` (their status lines below). Below is the audit as it was made, findings only. The code audited is `claude/final-code-audit`, made from
`origin/claude/backstab-str-line` at `f1f8972`: `origin/obsidian-edition` (#110 to #115) plus the
unmerged REAR_FRESH backstab fix. Line numbers are at that commit. The previous audit is
`reports/code-memory-audit.md` on `origin/claude/code-memory-audit`; its fixes are #111 and #112.*

## The short version

| Severity | Count |
|---|---|
| Bug | 0 |
| Wrong result | 0 |
| Risk | 3 |
| Cleanup | 8 (and 2 still open from the last audit) |

No bug and no wrong result found in #115, in the backstab fix or in the rest of what was looked at.
Every finding below is latent or tidying:

- **Risk 1.** `test_header_offsets` checks that each `TSR_*` constant is *some* field's offset,
  not *its own* field's: a constant naming the wrong field passes.
- **Risk 2.** `DiceLog.rules` and `game.RULES_IN_FORCE` start at 0 (stock rules): before
  `use_settings` runs, the Loader's reference models (about 65 branches on always-on bits) would
  model rules DSCLOG no longer has an off path for.
- **Risk 3.** `gff.write_atomic` uses one fixed temporary name (`DEST.tmp`): two Loader processes
  writing the same copy share it.
- **Cleanup.** 15 labels left unreferenced by #115; stale comments and docs (the memory table's
  69,936 and 26,304 are the build before REAR_FRESH); always-on content keys nothing reads; the
  Loader's dead off-branches and the tests that still run them; unused imports; a SyntaxWarning in
  a test; temporary save files left behind on a failed replace.

**Memory.** Every room figure in DEVELOPMENT-INTERNALS' limits table matches the build. Measured in
the game: upper memory's free piece was 26,256 bytes everywhere (the doc says 26,304), and
conventional memory had 99,008 bytes free in one piece with the map open. The DSCLOG block measured
69,984 bytes (the doc says 69,936).

**Tests.** 1,982 tests, both runs OK. Without the game's files 60 were skipped; with
`DSUN_OBJECTS`, `DSUN_GPLDATA` and `DSUN_RESOURCE` set to `/tmp/playtest/inst/`, 17 were skipped,
all needing tkinter.

## 1. #115 and the backstab fix

### What was checked and found clean

- **Removed branches unreachable.** Every bit whose test #115 took out of DSCLOG is in
  `game.RULES_ALWAYS` (`game.py:485`), and `rules_from_settings` always ORs it in (`game.py:489`):
  22 distinct bits, no two the same (checked: `sum` equals `OR`, 0xFF3E7DD0), and none overlapping
  the five switches still on the Options tab. The only bits DSCLOG still tests are HELMS,
  HALF_GIANT, NEW_SPELLS, HP_BEST and KITS. Those five are exactly `RULE_SETTINGS`.
- **No dead code behind removed jumps.** Each of the 15 labels #115 left unreferenced (listed in
  C1) was checked: each is a fall-through, with nothing reachable only through it. `two_cahulaks`,
  `worn_scan` and `ring_plus` are still called. `war_hit` loses its `push ax`/`pop ax` around
  `spec_get`, which is safe because AX is reloaded by `kit_level` before use. `probe_xp_next`
  loses `mov cl, 9`, which is safe because `level_room` keeps all registers and CL isn't read after.
- **Flags at `retf 2` exits unchanged.** `probe_level`, `probe_hd_con` and `probe_wp_shown` still
  end on the game's own compare. `save_sum`'s new `cmp ax,20 / je .sum` equals the old
  path with RULE_NO_DOUBLE set. `probe_item_skip` still clears ZF in the IRET frame.
- **REAR_FRESH (`dsclog.asm:23439-23468`).** The game's code was disassembled from DSUN.EXE
  58113h to 58353h. Between the load `mov [bp-20h],ax` (58124h, the creature's +1Fh, `cbw`) and
  the probe at 58353h, the only writes to `[BP-20h]` are the game's two `sub word [bp-20h],2`
  (58304h, 58335h), each paired with setting `[BP-1Ah]` or `[BP-24h]`. The one other DSCLOG site
  in that stretch, NS_FIST at 58226h, doesn't touch `[BP-20h]` (`dsclog.asm:22840-22880`). Every
  attack of the round goes back through 58113h (`jmp 0x8113` at 584CAh), so the THAC0 is reloaded
  each time and "+1Fh less `[BP-20h]`" is exactly what the game took off for this attack. AX, BX
  and ES are pushed. The flags are the INT's, restored by the IRET of `s_fl`. DS is the game's
  (the INT comes from its code). `buildcheck.py rear_fresh probe_stealth stab_first` matched the
  EXE in memory.
- **Loader side of #115.** No reader is left for any attribute it removed (`pickpockets`,
  `show_gear`, `combat_log` and the rest: nothing in `obsidian-edition/` or `playtest/`). No caller
  passes the removed arguments (`write_resources`, `new_chunks`, `Pictures`, `for_game`,
  `set_pickpockets`). `pickpocket.attempt`'s `caught` can't be None (`caught_key` always returns a
  string). `viewer.py` reads `rule_vars` only by iterating its own five keys (`viewer.py:438`, 603,
  1138, 1174); `content_vars` only by keys it made (457). No other `rule_vars[...]` or
  `settings["..."]` lookup of a gone key is left (`dicelog.py:1004` is guarded by its `in`).
- **Flags the Loader now always sets.** PICK_BUTTON (`dicelog.py:763`) and all three SKILLS_* bits
  (`dicelog.py:1025`) are still tested by DSCLOG (`dsclog.asm:21462`, 22082, 27702-27717, 27979).
  That is right: they are 0 until a Loader connects, so they now mean "a Loader is there".
- **DSCLOG without the Loader.** The always-on rules now apply even before the Loader writes the
  rules word. The rules that need the Loader still check for it: the buyback and GEAR_HOLD test
  `loader_beat` (`dsclog.asm:22458` and 21848), stealth needs the Loader's bits, and creation's age is
  worked out by DSCLOG itself (`cr_age_draw`, 9339).
- **`upgrade_settings` with old files** was run on samples:
  - a version-1 file with `combat_log`, `stealth` and `helm_ac` false keeps only `helm_ac`;
  - `"settings_version": "x"` or `true` reads as 1 and is upgraded;
  - a version-3 file is left alone (its gone `aging: false` dropped in memory and ignored);
  - a misshapen `speakers` is dropped;
  - a list is read as `{}`.

  The rules came out right each time (0xFF3FFFF5 less the unticked bit).
- **Tests.** StealthTests' search pattern now needs the `call rear_fresh`, and
  `test_later_attack_flags_its_own` covers neither, from behind only, both, and the next round.

### Findings in #115

**C1 (cleanup). Labels left unreferenced.** A label-reference scan of the build before and after
#115 shows these 15 local labels newly unreferenced:

| Label | Line |
|---|---|
| `probe_spec_damage.done` | 3761 |
| `probe_dam_line.done` | 3813 |
| `probe_view_dam.done` | 3974 |
| `probe_slots.level` | 7322 |
| `probe_dual_kit.done` | 8301 |
| `cr_names.back` | 9182 |
| `probe_wp_class.ret` | 10566 |
| `probe_race_panel.ret` | 10606 |
| `save_sum.not` | 16436 |
| `size_dice.ret` | 17345 |
| `size_spared.ret` | 17380 |
| `held_now.ret` | 17723 |
| `rest_hp.game` | 17757 |
| `con_share.ret` | 18895 |
| `thief_heavy.no` | 28045 |

Each is a fall-through, so they are harmless. The far pointer `wp_redraw` (11768) is filled in
but never called (older than #115). **Fix:** delete the labels, and `wp_redraw` with its
`WP_CALL_REDRAW` entry (6 bytes).

**C2 (cleanup). Stale comments.**

- `game.py:298`: "Their off paths are still in DSCLOG and here": since #115 they are gone from
  DSCLOG.
- `dsclog.asm:22414`: "With RULE_HI_CHA_PRICES (Shops as in AD&D)".
- `dsclog.asm:17038`: "the game's 4 without".
- 12 comments that say "with RULE_x" or "without RULE_x" for a rule that is always on now
  (`dsclog.asm:8627`, 9669, 9791, 12081, 12298, 18058, 18079, 18080, 18786, 22387, 22414, 27952).

**Fix:** reword them as always on.

**C3 (cleanup). Content keys nothing reads.** `launch.CONTENT` (`launch.py:525-527`) still lists
11 always-on keys: `effects_kept`, `stealth_gear`, `elf_looks`, `roll_store`, `cilla_elf`,
`camera_still`, `scene_pointer`, `mouse_start`, `party_spread`, `spells_manual` and
`spell_to_hit`. `content()` forces them True, and no `on["..."]` reads any of them (every read is
one of the 9 keys still switched). The patch groups `EFFECTS_KEPT`, `ROLL_STORE`, `CAMERA`,
`SCENE_POINTER`, `MOUSE_START` and `PARTY_SPREAD` are read only by `test_gamepatch.py`. **Fix:**
drop the keys from CONTENT; keep the groups as names for the tests, or drop them too.

## 2. The rest of the code base

**R1 (risk). The header test can't catch a constant naming the wrong field.**
`test_loader_constants_name_fields` (`tests/test_header_offsets.py:110-117`) asserts that each
`TSR_*` value is in the set of all fields' offsets. `test_same_name_same_field` only compares one
name across modules. So `TSR_X` set to field Y's offset passes. Today all 122 constants are right:

- 98 have a field of the same name (`TSR_FOO` and `foo:`) at that offset;
- the other 24 were matched by meaning (`TSR_ATTACK` and `attack_seq`, `TSR_ON` and `shadows_on`,
  `TSR_TABLE` and `shadow_tab_off` ...), each the only field at its offset;
- the 6 literal offsets in the Loader (`hdr + 8`, `+ 22`, `tsr_hdr + 32`, `+ 238`, and the
  docstrings' +368 and +1852) are `seq`, `seed_off`, `nfilt`, `dac_off`, `ovr_given` and
  `sell_seq`.

**Fix:** have the test map `TSR_NAME` to field `name` (with a 24-entry alias table for the rest),
and replace the literals with constants.

**R2 (risk). The reference models start with the stock game's rules.** `DiceLog.rules` is 0 in
`__init__` (`dicelog.py:594`), and `game.RULES_IN_FORCE` is 0 at import (`game.py:499`). Both get
`RULES_ALWAYS` only from `use_settings` or `set_rules`. Meanwhile the Loader keeps about 65
branches on always-on bits:

| File | Branches |
|---|---|
| `dicelog.py` | 24 |
| `game.py` | 24 |
| `startgear.py` | 3 |
| `defaultparty.py` | 2 |
| `weaponchoice.py` | 2 |
| `restrict.py` | 1 |
| `sell.py` | 1 |
| `locks.py` | 1 |
| `greyhair.py` | 1 |
| `tables.py` | 1 |
| `spelltexts.py` | 1 |

Some examples:

- `dicelog.py:3404`: the backstab's dice without RULE_BACKSTAB;
- `dicelog.py:3422`: a held target's x2 without RULE_HELD;
- `dicelog.py:1131`: no ranger skills without RULE_STEALTH;
- `greyhair.py:154`: `getattr(gd, "rules", 0)`.

Their off sides model what DSCLOG no longer does. Every production path checked sets the rules
first (`viewer.py:1040-1041`, `__main__.py:192-202` and 345-347; `viewer._rules()` goes through
`rules_from_settings`). So no wrong number is shown today, but a new caller, a tool or a test that
makes a `GameData` or `DiceLog` first gets stock-game answers silently. In `__main__.py:193` the
stats thread is already running while `use_settings` waits for a readable settings file; it does
nothing until attached. **Fix:** start both at `game.RULES_ALWAYS` (or
`rules_from_settings({})`), and in time drop the off-branches (C4).

**R3 (risk, Windows). One temporary name for every writer.** `gff.write_atomic` writes
`dest + ".tmp"` (`gff.py:160`). It is called for DSUNLOG.EXE, SEGOBJEX, RESOURCE, GPLDATA and the
regions (`gamepatch.py:1405`, `icons.py:1044`, `icons.py:1112`, `kalzith.py:860`,
`worldgear.py:716`). The window and *Play Dark Sun (in-game rolls)* both run
`prepare_patched_game` (`launch.py:1156`, 1175). If they ever overlap, both open the same `.tmp`
and one can put the other's half-written file in place. `save_settings` uses `mkstemp` for exactly
this reason (`launch.py:253-260`). It is unlikely: both would have to be started at once.
**Fix:** `tempfile.mkstemp(dir=os.path.dirname(dest))`, as `save_settings` does.

**C4 (cleanup). Dead off-branches, and tests that only run them.** These are the branches of R2.
Some tests still pin their off sides, code no player can reach:

- `test_sell.py:53`, 66, 96 and 120 clear RULE_CHA_PRICES and check the full price. In play it is
  always 60%; only `test_shops_as_in_add` covers that.
- `test_now.py:289` (no ranger skills), 313 (the game's base sum) and 326 (above 95) set rules to 0.

DSCLOG's "bit clear changes nothing" tests are different: they check the always-on paths ignore
the bit, which is worth keeping. **Fix:** remove the Python off-branches, and make those tests run
with the rule on (the 60% price and the AD&D table).

**C5 (cleanup, docs). The memory table is one build old.** `DEVELOPMENT-INTERNALS.md:224` gives
DSCLOG's block as 69,936 bytes and upper memory's free piece as 26,304. With REAR_FRESH they are
69,984 ((10h + `KEPT_PARAS` 1106h) paragraphs, measured) and 26,256 (measured): 48 bytes,
REAR_FRESH's 48. The backstab commit updated the limits table below it but not this row.
**Fix:** 69,984 and 26,256, and link this audit's log.

**C6 (cleanup). Unused imports** (pyflakes; none from #115):

- `pickpocket.py:31` `itemgate`;
- `kurzakdoor.py:19` `struct`;
- `gamepatch.py:29` `os`;
- `kalzith.py:855` `os`;
- `worldgear.py:710` `os`;
- `dicelog.py:32` and `spellbook.py:8` `EFFECT_RULES`;
- the five names in `theme.py:17` look like re-exports.

**Fix:** remove them, or mark the re-exports `# noqa`.

**C7 (cleanup, tests).**

- `tests/test_worldgear.py:445` has `D:\ ` in a plain docstring: a SyntaxWarning now, an error in
  a later Python. No module in `dsloader/` has one: compiled with SyntaxWarning as an error.
- `tests/test_namedsaves.py:107` leaves a file open (a ResourceWarning in the run); on Windows an
  open handle stops the temporary folder being removed.

**Fix:** a raw docstring, and `with open(...)`.

**C8 (cleanup, Windows). Named saves leave a `.tmp` behind on a failed replace.**

- `namedsaves.sync` (`namedsaves.py:137-142`) catches OSError and goes on, leaving
  `"... .SAV.tmp"` in the Named saves folder.
- `restore` (`namedsaves.py:194-197`) leaves `SAVEnn.SAV.tmp` in the game's save folder, and has
  no retry when an antivirus holds the slot for a moment (the window shows the error,
  `viewer.py:593`, and nothing is lost). `gff.write_atomic` does both, a retry and the cleanup.

**Fix:** remove the tmp in a `finally`, and retry `os.replace` 5 x 50 ms as `write_atomic` does.

### Still open from the last audit (cleanup)

- The stats thread still wakes every millisecond while no game is attached.
  `_answer_stats` returns without raising when `tsr_hdr` is None (`dicelog.py:1164-1165`), so
  `STATS_ANSWER_IDLE` (`dicelog.py:1191`, used only on an exception) never applies. **Fix:** return a flag, and take the idle
  step when unattached.
  *Status: fixed on branch `claude/older-loader-bugs` (2026-11-19): `_answer_stats` returns False
  while unattached, and the thread then waits `STATS_ANSWER_IDLE`
  (`test_stats_thread_idles_while_unattached`).*
- `crash-logs/` is never pruned: freeze reports are about 1 MB each (`freeze.py:150`).
  **Fix:** keep the newest 20.
  *Status: fixed on branch `claude/older-loader-bugs` (2026-11-19): `freeze.write_report` keeps the
  newest `KEEP_REPORTS` (20) `freeze-*.zip` and removes the older; the crash reports' text (a few
  KB each) and anything else in the folder are left (`test_old_reports_pruned`).*

### Checked and found clean

- **Item gate and `ring.held()`.** Every caller that unlinks, links or pops a record holds the
  gate before it reads the lists: `ring.unlink` and `give_ring` re-read them after
  `held()` (`ring.py:184`, 264), as do `sell`, `loot`, `pickpocket`, `npcitems`, `semyon.ship`,
  `spellarrows`, `buyback`, `kalzith`'s loot and `champions`.
  - Field-only writes to records read before the hold (`icons.fit`, `icons.repaint`,
    `names.migrate`) still open the gate through `GuestMemory.write`. An area reload changes the
    heads, so they are refused then.
  - `lines()` always ends the gate in `finally` (`dicelog.py:1398-1405`).
  - The stats thread writes nothing the gate covers (the STATS table and header fields in upper
    memory).
  - `viewer.py` makes no item writes.
- **Interrupt hygiene** (#112's checks stand):
  - `probe_tick` starts with `cld` (`dsclog.asm:2314`);
  - `test_interrupt_hygiene` passes;
  - REAR_FRESH adds no `sti`, `retf 2` or far call.
- **Build asserts.** `image_len`, `FAR_END`, `UMB_NEED`, `UMB_KEPT`, the spell records and rows
  (`dsclog.asm:19566-19568`, the last audit's overrun), `SEG_SPACE`, `TICK_SIZE` and the
  site-table limits all fail the build when passed. `kept_end` is covered by `image_len`'s assert,
  since the image is padded to `AFTER_INSTALL`.
- **Header offsets.** All 155 commented fields sit at their `+N` (test). By name or meaning all 122
  `TSR_*` constants are right (R1), and so are the 6 literal offsets. Five header labels carry no
  `+N` comment (`swap_match`, `swap_text`, `pick_text`, `stats`, `look_full`). The Loader reaches
  each through its `*_off` field, never by a literal.
- **The build.** DSCLOG.EXE assembles byte for byte from `dsclog.asm` with NASM 2.16.01, with and
  without a symbol map.

## 3. Memory

### 3.1 The room figures against the build

The source was assembled with `[map all]` and every figure in the room table of
`DEVELOPMENT-INTERNALS.md` (lines 224-241) was read against the map:

| Figure | Build | Doc | Right? |
|---|---|---|---|
| `resident_end` | F6E0h = 63,200 | 63,200 | yes |
| `AFTER_INSTALL` | 3E0h = 992 | 992 | yes |
| `kept_end` | FAC0h = 64,192; 1,344 spare | 64,192; 1,344 | yes |
| install code (`install` to `all_vectors_end`) | 3BBh = 955; 37 padding | 955; 37 | yes |
| `FAR_END` | FFDCh = 65,500; 36 spare | 65,500; 36 | yes |
| `UMB_NEED` | 1936h = 6,454 ¶; 1,728 spare of `UMB_ROOM` 8,182 | 6,454; 1,728 | yes |
| `UMB_KEPT` | 1F8Ch = 8,076 ¶; 106 spare | 8,076; 106 (1,696 bytes) | yes |
| `KEPT_PARAS` | 1106h = 4,358 ¶, so the block is (10h + 1106h) x 16 = 69,984 bytes | "69,936 bytes" | **no** (C5) |
| `TAIL_BYTES` | 15A0h = 5,536 | 5,536 | yes |
| DSCLOG.EXE | 32 + 64,192 + 5,536 = 69,760 | 69,760 | yes |
| `NAMES_EXTRA` | 32h = 50 of 50 | 50, 0 spare | yes |

### 3.2 Measured in the game

The startup procedure was followed in full: lock holder, `loadsave.sh`, window 320x240,
`buildcheck.py` OK (129 vectors at their handlers, plus `rear_fresh`, `probe_stealth` and
`stab_first` the same as the EXE), the watchdog, and a test log. No save was made and no memory was
written. The log is `playtest/logs/2026-11-19-final-audit-memory.md`.

| Moment | Conventional, largest free piece | Game heap | Upper memory free |
|---|---|---|---|
| `pens-after-arena`, map open | 99,008 bytes | 201 KB, 0 free | 26,256 in one piece (E330h) + 144 at CA00h |
| `fountain-user`'s ambush, 10 combatants | 99,008 | 201 KB, 0 free | 26,256 + 144 |
| Lex's USE screen up (map shut) | 134,848 | 157 KB | 26,256 + 144 |
| Ester's Curse, 0.4 s in, its picture drawing | 99,008 (+1,008) | 201 KB, 0 free | 26,256 + 144 |
| Kalzith's shop up (`selling-junk-user`, `openshop.sh`) | 124,608 (+5,104) | 171 KB | 26,256 + 144 |
| His talk after the shop | 100,032 | 201 KB, 57,328 free in one piece | 26,256 + 144 |
| The map open again after the shop | 100,032 (+1,008) | 196 KB | 26,256 + 144 |

What this shows:

- Upper memory never moved, and the four DSCLOG blocks add up to `UMB_KEPT`:
  4,374 + 2,062 + 885 + 751 paragraphs + 4 MCBs = 8,076.
- UMBPLUS's block starts at CA00h, 144 bytes above DOSBox's tables, as the last audit proposed.
- The HMA test passes (FFFF:0010 differs from 0:0) and the overlay buffer is in upper memory
  (`ovr_given` DB22h).
- The map's 60,000 bytes always had a piece of 99,008 or more.

## Recommended order

1. R2: start the rules at `RULES_ALWAYS`. It is one line each and takes away the trap the dead
   branches set.
2. R1: tie each `TSR_*` constant to its own field in the test.
3. C5: the memory table's two figures, before the release notes quote them.
4. R3 and C8: the Windows temporary files.
5. The rest of the cleanup (C1 to C4, C6, C7) when convenient, C4 with its tests.
