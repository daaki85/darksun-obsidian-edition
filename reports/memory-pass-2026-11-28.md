# Memory pass and memory audit (2026-11-28)

*Both resident helpers were read for memory: DSCLOG (Shattered Lands') and DSCLOG2 (Wake of the Ravager's), on
`origin/obsidian-edition` after #314, #312 and #289. The audit followed the project skill
`thermo-nuclear-code-quality-review`, with memory as its focus. The owner asked to leave DSCLOG's build rule
(everything must fit without `UMBPLUS.COM`) as it is for now. The fixes are on branch `claude/helper-memory-pass`, and the play check is in
[the test log](../playtest/logs/2026-11-28-memory-pass-play.md).*

## The short version

| # | Finding | Saves | Done here |
|---|---------|-------|-----------|
| 1 | DSCLOG walked a creature's items with the same 25 instructions in four routines | 208 bytes of segment and upper memory | yes |
| 2 | DSCLOG2 kept the kits' names in its segment (DSCLOG keeps them in its tail) and had two copies of the lookup | 592 bytes of segment | yes |
| 3 | DSCLOG's see-through tables must fit upper memory without `UMBPLUS.COM` | 14,160 bytes of upper memory | no: the owner's call, deferred |
| 4 | DSCLOG's music pool, the same rule | 12,016 bytes of upper memory | no: the same |
| 5 | DSCLOG's shadow cache: 80 slots of 208 bytes in the HMA, the sequel's 64 of 152 | HMA room (1,456 bytes for 7 slots), which could take `LBL_SLOTS` (1,440 bytes) out of upper memory | no: needs the cache's hits measured in play |
| 6 | Code repeated in short runs, both helpers | at most ~1,100 bytes in DSCLOG, ~1,300 in DSCLOG2 on paper; realistically a few hundred | no: low yield for the risk, run by run |
| 7 | Dead code | none found | - |
| 8 | Install code kept after install | none: the after-install buffers lie over it (43 bytes of padding) | - |

## Measurements

Measured with nasm's symbol map (`tests/test_dsclog_room.build_map`):

| Limit | DSCLOG before | DSCLOG after | DSCLOG2 before | DSCLOG2 after |
|-------|---------------|--------------|----------------|---------------|
| The 64 KB segment | 65,280 (256 free, at the test's margin) | 65,072 (464 free) | 63,392 (2,144 free, 96 past the 2 KB margin) | 62,800 (2,736 free) |
| Upper memory once installed (`UMB_KEPT` of 8,182 paragraphs) | 8,143 (624 bytes free) | 8,130 (832 bytes free) | 5,033 | 5,032 (~50 KB free) |
| The far block in the HMA (of 65,520) | 65,500 (36 free) | the same | 64,768 (~750 free) | the same |

The sequel's HMA is nearly full too: its see-through figures' tables (8.5 KB) are there, where DSCLOG keeps
them in upper memory. With 50 KB of upper memory to spare, the sequel can move a buffer there when it needs
to. Conventional memory is unchanged by this pass: both helpers load into upper memory. Shattered Lands'
game heap had 58 KB free at the fountain when it was last measured.

## 1. One walk of a creature's items (DSCLOG)

`PROT_SCAN`, `ARMOUR_WORN`, `THORNS_AC` and `WORN_SCAN` each walked the creature's item lists the same way. Each
read the creature's list words from `CREATURES` and the things table, followed each item's next link, and capped
a list at 100 items. Only the part that weighs an item differed. The new `WORN_ALL` walks all three lists and
`WORN_ON` walks the worn list alone. Each calls a visit routine (`WE_VISIT`) with ES:BX set to the item's
record and DX to its number. A visit that sets CF ends the walk, which is what `ARMOUR_WORN` needs once it has
found armour. Each routine now holds only its visit.

The existing emulator tests reach all four paths. A changed list range made 62 tests fail for `WORN_ALL`, and
`test_wall_damage` fail for `WORN_ON`.

## 2. The sequel's kits' names in its tail

`kit_names_table.inc` now holds the kits' names and short names once, and each helper includes it in its tail.
DSCLOG's bytes are unchanged. DSCLOG2's `EF_KIT_LINE` (the Effects screen's kit line) and the dual class's kit
menu both read the names through `KIT_NAME_PTR`, as DSCLOG's do. The two copies of the lookup are gone, and the
menu's rows point into the tail. DSCLOG2's label slots moved to the tail's start, after the item names. That
way the emulator tests' return spot at CS:FFF0 still lands in a buffer, as it does in DSCLOG; otherwise the
smaller segment would have put it in a table. The new `test_ravkits.test_kit_names` checks every kit's line and
name against `kitpages`.

## 3 and 4. The optional tables in upper memory (not done)

DSCLOG's upper memory (`UMB_KEPT`) is the helper (4,425 paragraphs with its tail) plus the game's overlay buffer
(2,062), the music pool (751) and the see-through tables (885), each with its MCB. The pool and the tables are
already taken only if there is room as the helper loads. The build, though, insists that they fit without
`UMBPLUS.COM`. Two ways out remain:

- Count the see-through tables against the room `UMBPLUS.COM` gives, falling back to conventional memory as
  `FAR_INIT` does for the far block. This gives back 14,160 bytes, at the cost of 14 KB of the game's heap on a
  machine where `UMBPLUS.COM` can't move the block.
- Do the same for the music pool: 12,016 bytes back.

The owner chose to wait (2026-11-28). Until then, DSCLOG has 832 bytes of upper memory for new resident
code and data, and the segment has 208 bytes past its margin.

## 5. The shadow cache and the HMA (not done)

DSCLOG's far block is full. The shadows' cache is its second-largest part (80 slots x 208 = 16,640 bytes, after
the panel's picture at 23,400); the sequel's is 64 x 152. Seven slots fewer would free 1,456 bytes. That is room
for the labels' slots (`LBL_SLOTS`, 1,440 bytes), which now sit in the tail and so in upper memory: 90
paragraphs back there. The Loader finds them through a header word, so only the helper and that word would
change. The cost is more cache misses, so more shadows worked out again per frame. Measure the cache's hits at
a busy place first (the fountain fight) before choosing the count.

## 6. Repeated code (not done)

A scan of each build's listing for repeated instruction runs (no labels inside, at least 10 bytes, counted once
each) finds about 1,090 bytes that could be saved in DSCLOG after this pass, in 74 runs, and 1,320 in DSCLOG2.
Most runs are 3 to 8 instructions saving 10 to 30 bytes each. Many push or pop a return frame (`cr_ip`,
`cr_cs`, `cr_fl`) that a call can't take, and others differ in a register. The walk in finding 1 was the one
run long and common enough to be worth a routine. The previous audit's finding stands: DSCLOG2 and DSCLOG
share about 500 instructions in short runs that differ by address and register.

## 7 and 8. Dead code and the install

Every label in either helper is read somewhere. The only exceptions are the header's fields (`*_off`,
`*_count`), which the Loader reads by offset. DSCLOG's install code (949 bytes) is not kept after install: the
buffers used once the game runs (`LOOK_TEXT`, `SLOTS_TEXT`, `BOX_TEXT` and the others, 985 bytes) are laid over
it.

## DOSBox-X's memory

The Loader's DOSBox-X settings (`dsloader/dosboxx.py`) make the BIOS 16 KB and end upper memory at FBFFh, with
DOS's own structures in DOSBox-X's private area. Upper memory then runs from CC00h to FBFFh, 192 KB, against
0.74's D000h-EFFFh (128 KB, or about 150 KB from CA00h with `UMBPLUS.COM`). With DSCLOG loaded, `fountain-user`
had 65,520 bytes of upper memory free under DOSBox-X, against about 25 KB under 0.74.
The HMA is 64 KB on any PC, and DSCLOG's far block takes it in both (`dos=umb` keeps DOS out of it).
Conventional memory is about the same: the game loads at 0224h, 2 KB higher than 0.74's 01A2h.

The helpers still have to fit plain DOSBox 0.74, so DOSBox-X's extra room can hold only what is already
optional (the music pool, the see-through tables), not code the mod needs. The 64 KB segment is the same in
every emulator.

## Checked in play

[The test log](../playtest/logs/2026-11-28-memory-pass-play.md): in Shattered Lands, every member's inventory
and AC, and Gerakis's AC with his armour off; in the sequel, the Effects screen's kit lines, including a short
and a long name after test edits. Both were taken with the old and the new build and compared pixel for pixel.
They were the same, apart from the inventory's bag icon, whose dot cycles its colour by itself.

## Tests

The full suite passes (3,296 tests, 263 skipped, `DSUN_REQUIRE_NASM=1`), as do the start-up tests on both
games' real files.
