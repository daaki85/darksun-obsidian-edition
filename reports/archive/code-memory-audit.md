# Code and memory audit (2026-11-18)

*Status: archived. Every finding was fixed in #111 and #112; the last audit before 2.19.0 is
[code-memory-audit-final.md](../code-memory-audit-final.md). Written as findings only. The code audited is `claude/spell-arrows-note` at
`a4f5768` (`obsidian-edition` plus the spell arrows' INFO heading). Six areas: DSCLOG's entry and
exit, DSCLOG against its Python twins, DOS memory, the Loader's access to the game's memory, the
Loader's core, and the content that rewrites the game's files. Line numbers are at that commit.
Throwaway scripts that reproduce findings are under the session's scratchpad (`auditwork-1` to
`-6`); the ones named below are worth turning into tests.*

## The short version

The code is in good shape for its size (29,800 lines of NASM, 37,700 of Python). The tests pass
(1,942), DSCLOG.EXE builds byte for byte from its source, every memory limit but one is guarded by
a build assert, the Loader never changes the game's own files, and over a long session its memory
doesn't grow. But the audit found **three bugs that can corrupt the game or lose items**, and a
handful of smaller ones:

| # | Bug | Effect | Checked |
|---|---|---|---|
| 1 | Negative Plane Protection's saved spell record is written 32 bytes past the new spells' room | overwrites a game segment and picture slot 0 | arithmetic, by hand |
| 2 | A magic item sold while the Loader isn't running is lost | the item vanishes | the code, by hand |
| 3 | The item gate misses list changes the game makes during its wait | an item in two lists, another lost | simulated |
| 4 | The Elven Leader's Gythka +1 drawn as Kreenfang with world magic off | wrong picture | run on the game's data |
| 5 | A Ravager at kit level 0: DSCLOG gives AC 3, the dice log explains AC 7 | wrong numbers shown | emulated |
| 6 | On Windows, a virus scan holding the patched game for a moment starts the game without the dice log | no dice log that session | likely, not run on Windows |

## 1. Corrupts the game or loses items

**1.1 Negative Plane Protection writes past the spells' room** (`dos/dsclog.asm:21391-21412`) —
CONFIRMED. SEG_MOVE frees 200h bytes for the new spells' records (16 records, 196-211, from offset
18B0h in segment 3CB4h). `NPP_SAVE` is record `NS_FIRST + NS_COUNT` = 212, at 30h + 212×20h =
1AB0h: all 32 bytes past the room's end. `NS_NPP` copies Vampiric Touch's record there whenever an
undead's negative-energy attack meets Negative Plane Protection, overwriting the game's 12-byte
segment 3E5Fh and the 16 bytes of the game's picture table slot 0 (3E60h). It began when Restore
Youth took record 211 and the copy moved to 212. Effect in play: not seen; likely a wrong or
missing picture, or a bad far read. **Fix:** set the save byte in Vampiric Touch's own record
around the call and restore it, or use a spare record below 196; add a build assert tying the
records to the room (see 3.1).

**1.2 Sold magic items lost without the Loader** (`dos/dsclog.asm:22657` `sell_keep`,
`dsloader/buyback.py:80-121`) — CONFIRMED. With *Shops as in AD&D*, DSCLOG keeps a sold magic item
back from the game's free and queues it for the Loader to put in the merchant's pack. It doesn't
check the Loader is there (GEAR_HOLD does, through `loader_beat`). Closing the Loader's window
leaves the rule switches set, so every magic item sold afterwards is lost. Also: the Loader drops
the whole queue when more than 4 sales are pending or on its first look after reconnecting, and if
the player picks another item up onto the pointer before the Loader acts, that item goes to the
merchant. **Fix:** `sell_keep` falls through to the game's free unless `loader_beat` is fresh; the
queue records the item number and the Loader checks it's still the pointer's first item.

**1.3 The item gate's re-check misses moves within lists** (`dsloader/itemgate.py:122-147`, with
`ring.py:229-261`, `spellarrows.py:243-288`) — CONFIRMED in a simulation of the game's memory
(`auditwork-4/toctou.py`). Before writing item lists the Loader waits up to 60 ms, pauses DOSBox
and checks only the free-list heads, the item count, the region and two table pointers. A move the
game makes in that window between existing lists (an inventory drag, a GIVE) changes none of
those. In the simulation, unlinking item 3 after the game moved item 2 left one list running into
the free list (`1, 3, 7`), item 3 on the free list too, and nothing refused. Callers that read the
lists before the pause: `spellarrows.return_strays` and `starting_gear`, `semyon.ship`,
`loot.take`, `pickpocket.attempt`. How likely in play: lower than it looks (several of these only
run with the inventory shut), but a GIVE or a pick-up isn't excluded. **Fix:** every item-changing
step calls `itemgate.hold()` before it reads any list, then builds `ring.Items`.

**Related, smaller (all LIKELY):**
- Records popped from the free list before they're linked (`ring.give_ring`, `npcitems`,
  `pickpocket`): an exception between the two leaks a record; `pickpocket.attempt` unlinks before
  it gives, so a failed give loses the item. Link first, pop last.
- `spellarrows._to_archer` copies the arrows to the Spellarcher, then ignores a failed unlink: the
  arrows exist twice. Unlink first.
- Item indices from the game are accepted up to 9,998, but the table has 400 records: a torn
  pointer sends writes up to 200 KB past it, outside the gate. Bound them by `ITEM_RECORDS`.
- `SHEETS_PTR` (and other table pointers) used without a null check: during an area load a null
  pointer plus a sheet index of 22 or more passes the 600h low-memory guard and writes into DOS's
  memory (`aging`, `tracker`, `weaponchoice`, `defaultparty`, `kits`). Whether these pointers go
  null like the item and creature ones do is unverified.
- A write refused by the low-memory guard is silent, so a two-write change can be half done
  (`guestmem.py:67-75`). Raise instead.
- After the game restarts inside the same DOSBox, up to ~40 passes keep writing through the old
  data segment and header (`viewer.py:1225`, the stats thread). Check `still_patched()` every pass.
- Kalzith's loot sets LOOTED before removing the scrolls, and a scroll lying alone on the ground
  can't be removed (`kalzith.py:771-785`).
- On Windows, `NtSuspendProcess` can return before DOSBox's threads stop, and a pause can land
  inside the game's own allocator: a record popped by both. Only DSCLOG can make this airtight
  (an "in item routine" flag, or applying the edits itself).
- If the Loader is killed while it holds the gate (Task Manager), DOSBox stays frozen; holds also
  last to the end of the pass, including drawing. Release after each block of writes.
- Two Loader folders can follow one DOSBox: their gates are independent and both answer DSCLOG's
  requests. A lock keyed on the DOSBox, or a mark in DSCLOG's header.

## 2. Wrong results

- **Kreenfang's picture on another gythka** (`dsloader/icons.py` `which()`, ~1250) — CONFIRMED on
  the game's SEGOBJEX: any Gythka +1 counts as Kreenfang, and the Elven Leader carries one (made
  +2 only with world magic on, or not yet in an older save). Also require Kreenfang's name entry.
- **Ravager AC at kit level 0** (`dos/dsclog.asm:6918-6924` against `kits.py:233-235`) —
  CONFIRMED in the emulator: DSCLOG's `dec` then unsigned compare clamps to the table's last entry
  (AC 3); Python's `max(level, 1)` gives the first (AC 7). Treat 0 as 1 in the asm; test level 0.
- **Gear for a second character lost** (`dicelog.py:1683-1697`, GEAR_DUE/GEAR_WHO) — LIKELY: the
  Loader clears GEAR_DUE at the end of a pass without checking GEAR_WHO still names the character
  it worked on; a second character finished meanwhile keeps the game's gear. Clear it only if
  GEAR_WHO is unchanged.
- **The Searing Blade and water clerics**: the obsidian short sword's class word lets earth, fire
  and water clerics use it; only the class-restriction rule's material check keeps water clerics
  off. With class restrictions off a water cleric can wield it, unlike ITEMS.md says.
- **Windows file locks** (`gff.py:149-162` `write_atomic`) — LIKELY: one `os.replace`, no retry,
  no fsync. A virus scanner holding the new DSUNLOG.EXE for a moment makes the game start with no
  dice log. Retry as `save_settings` does (5 × 50 ms), and fsync.
- **Settings written by two processes** (`launch.py:176`): the window and *Play Dark Sun (in-game
  rolls)* can both rewrite settings.json; a lock only within one process. Rare lost update (a
  pocket picked twice). A lock file.
- Smaller: a vanished DSUN.EXE gives a TypeError crash on start (`launch.py:477`, `_find_file`);
  a hand-edited settings key like "²" breaks name lookups (`launch.py:283`: `isdecimal`);
  `dicelog` and `play` commands end with a generic error where the window carries on
  (`__main__.py:200-258`); with Kalzith off, a failed scripts copy also drops the pens' gift
  without saying so (`launch.py:466-501`).

## 3. Memory

### 3.1 The DOS side

| Limit | Used | Room | Spare | Guarded by | Docs right? |
|---|---|---|---|---|---|
| DSCLOG's segment (`kept_end`) | 64,944 | 65,536 | 592 | build assert; CI rebuilds and compares | yes |
| Install code in `AFTER_INSTALL` | 959 | 992 | 33 | build asserts | yes |
| Far block (`FAR_END`) | 65,500 | 65,536 | 36 | build assert | yes |
| Upper memory as DSCLOG loads (`UMB_NEED`) | 6,501 ¶ | 8,182 | 1,681 ¶ | assert and test | yes |
| Upper memory once installed (`UMB_KEPT`) | 8,123 ¶ | 8,182 | **59 ¶** (944 bytes) | build assert only | yes |
| Upper memory with UMBPLUS | 8,133 ¶ | 9,984 | 1,851 ¶ | nothing (falls back quietly) | yes |
| DSCLOG's block as kept | 4,421 ¶ = 70,736 bytes | — | — | — | **no**: DEVELOPMENT-INTERNALS says 70,624 |
| DOSBox's own tables below UMBPLUS's C900h | to C8C0h | C900h | 64 ¶ | **nothing** | about (doc says 63) |
| **New spells' records** | **17** | **16** | **−32 bytes** | **nothing** | **no** (DEVELOPMENT-CONTENT:607) |
| New spell rows (4010h:188h) | 112 | 463 | 351 | nothing | yes |
| `SEG_SPACE` (stack + kinds) | 1F2h | 200h | 14 | checked at run time | — |
| Name entries (`NAMES_EXTRA`) | 50 | 50 | **0** | only fails with fewer | — |
| Extra item types | 33 | 33 | 0 | build assert | — |
| Dice ring (63 × 192) | 43 in 2 s at most | 63 | — | wraps | yes |
| Text buffer (2 KB) | 251 between reads at most | 2,048 | — | wraps | yes |
| Records per object | Jark 95 | 120 | ~25 | test | — |
| Conventional memory, the map open | 60,000 in one piece | ~100 KB free | ~39 KB | heapcheck warns under 24 KB | yes |

(¶: paragraphs of 16 bytes.)

**Findings:**
- **3.1.1** The spell-record overrun (1.1). Nothing ties `NS_COUNT` or extra records to the room;
  add `%if SPELL_RECS + (NS_FIRST+NS_COUNT)*20h > (SEG_STACK-SEG_RECORDS)*16 + SEG_BYTES %error`,
  and the same for the spell rows and `SEG_SPACE`.
- **3.1.2** The name table is full: the next new item's name needs `NAMES_EXTRA` raised (and
  breaks loading its saves in older versions). A test that fails at the limit.
- **3.1.3** DOSBox hands out its private tables up to D000h without knowing UMBPLUS put a block at
  C900h: 64 paragraphs apart. A CD mount, a program asking for many file handles, or running the
  game twice in one DOSBox could write DOSBox's tables over DSCLOG. Start UMBPLUS higher (CA00h).
- **3.1.4** A20 is checked once, at install; if anything turned it off later, the far block's
  writes would land on the interrupt vectors. A cheap check per frame.
- **3.1.5** `heapcheck` warns on total free memory, but the map needs 60,000 bytes in one piece:
  a fragmented heap fails with no warning. Warn on the largest block too.
- Docs: DEVELOPMENT-INTERNALS:217 (70,736 bytes, not 70,624); DEVELOPMENT-CONTENT:607 (the
  record ends at 3E610h, past the room); dsclog.asm:19723 ("three wizard spells … 96 bytes": 16,
  200h); hard-coded `TICK_SIZE` and name count without asserts.

**What the mod adds to the game's memory:** 207 pictures (377 KB, in the game's XMS picture store
of 741 KB and its 300 slots, managed by the Loader and DSCLOG), 98 objects, and about 10 KB of
records; the conventional heap pays a few KB per area. 39 KB stays free with the map open.

### 3.2 The Loader's own memory

Bounded: 22,000 simulated passes grew it by under 2 KB; every history is capped (3,000 lines of
dice and dialogue, 200 combat log lines, 200 refused writes). Resource use worth fixing:
- the stats thread wakes every millisecond for the whole run, also after a game restart when it
  has nothing to do, and holds Windows' 1 ms timer (laptop battery) (`dicelog.py:1205`);
- a 0.33 s CPU-bound thread per new palette with no limit on how many run (`ghost.py:186`);
- `crash-logs` (freeze reports are ~1 MB each) and `play.log` are never pruned;
- on reconnect, the stats thread is given 0.2 s to stop before the process handle is closed; a
  late write could reach a new DOSBox that reuses the handle (`viewer.py:856`, LIKELY).

## 4. DSCLOG's entry and exit

No crash, hang or wrong result found; 85 sites whose replaced instruction sets flags a later jump
uses were checked against their handlers' exits, and the register-keeping, overlay returns and
nested probes are sound. Latent:
- `probe_tick` runs before the game's timer handler has cleared the direction flag or switched
  stacks, and it can call the game's mouse handler (a box nudge) from there. Add `cld`; move the
  nudge out of the tick.
- 14 handlers end with `sti … retf 2`, turning interrupts on whatever the caller had; not proven
  safe for the pointer drawing and the chunk loader. Restore the caller's flag, as `probe_hit` does.
- The arrow pointer's redraw reads video memory from the timer, which can upset a latch copy in
  progress (cosmetic).
- `int33` keeps the game's mouse handler after the game removes it; a pending nudge calls the stale
  pointer. Clear it on removal.
- Several handlers call into the game with interrupts off (the figure drawing every frame among
  them): the game's 120 Hz clock loses ticks, and a future call to a routine that waits would hang.
  `sti` at their start.
- Nothing clears the direction flag at DSCLOG's entry points (`record`, `stub`); sound today
  because only the tick enters with an arbitrary flag.

## 5. The content writers

Two Loader runs give byte-identical copies; all 9 patched files read back with no chunk lost or
overlapping; **no two modules claim the same new object, picture, script or name number**; every
script repair checks the game's original bytes first. Latent:
- `icons.with_chunks` silently drops an added chunk of a type the file doesn't have (none today).
- `scriptfixes.repaired` drops every repair to a script if one would push it past 11,376 bytes,
  silently (script 139 is at 10,793). Apply them one at a time and report any skipped.
- Repairs pad with EXIT without checking command boundaries (they're all right today against the
  GOG files); several script modules read the game's chunks, not the previous module's output
  (no overlap today); a region entry not matching silently drops a gift; with Kalzith off, see 2.
- `mend_searing_blade` can't misfire (name entry 0x156 is the mod's own), but walks all 520 things
  every 3 s where once per region would do.

## 6. Tests

- 43 tests that need the game's files (the number-claims audit, the patched copies, the script
  repairs against the real bytes) never run in CI. A documented pre-release step with the three
  environment variables, or a private runner.
- No test pins DSCLOG's header offsets as a whole (152 fields and 120 `TSR_*` constants were all
  right by a scratch script: `auditwork-2/hdrcheck.py` is worth keeping), the spell arrows' table
  against `spellarrows.ARROWS`, the six name entries used in `icons` and `pickpocket`, or Ravager
  AC at level 0.
- Constants with the same name and different meanings on the two sides (`TSIZE`, `NO_MATERIAL`,
  `THINGS`, `WILD_TO_HIT`, `STINK_TO_HIT`, `MAP_THINGS`): rename the Python ones.

## Recommended order

1. The three corrupting bugs: the spell-record overrun (with its build assert), `sell_keep`'s
   heartbeat check, and `hold()` before every item-list read.
2. The wrong results: Kreenfang's picture, Ravager AC at 0, GEAR_DUE, the Windows retry.
3. The smaller item-list hardening (link before pop, index bounds, null pointers, refused writes
   raising, `still_patched` each pass).
4. DSCLOG's interrupt hygiene (`cld` in the tick, restore the caller's interrupt flag, clear the
   stale mouse handler) and UMBPLUS's margin.
5. Tests: the header offsets, the name table's limit, the game-file tests before a release.
6. Docs: the room figures and the record's end; Named saves aren't a backup.

## What is sound

- The Loader never writes the game's own files; saves are only replaced by the player's own
  restore, after copying the old one aside.
- `gamepatch` checks DSUN.EXE's size and all 455 patches' original bytes before writing; another
  release starts the game plain.
- settings.json is written atomically with retries; an unreadable one is kept aside.
- No tkinter call from a thread; the Loader's memory stays bounded.
- The Loader attaches only to the right DOSBox (signatures checked) and can't write outside it.
- DSCLOG builds byte for byte from source and CI checks it; its header (152 fields), rule bits,
  kit numbers, item types and name entries agree with the Loader's.
- Every DOS-side table is bounded before it's indexed; the ring and text buffer wrap.
- Two Loader runs produce identical patched files; no numbering collisions.
