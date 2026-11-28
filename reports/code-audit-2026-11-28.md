# Code audit, round two (2026-11-28)

*The code audited is `origin/obsidian-edition` at `4926cb69` (#309 merged), read with the project skill
`thermo-nuclear-code-quality-review`. It covers everything merged since [the follow-up audit](code-audit-followup-2026-11-27.md)
(at `b6027f9`): #257 to #309, 125 files, about 9,900 lines added. Most of it is the sequel's port of
Shattered Lands' features (the both-games rule): `dsloader/` +2,673 lines (new: `ravdress.py`, `ravportraits.py`,
`ravquests.py`, `inventoryart.py`), `dos/dsclog2.asm` +2,526, `dos/shared_routines.inc` +247. Open PRs #310 and
#311 belong to other threads and are not covered. Fixes are on branch `claude/code-audit-round-two`.*

## The short version

| # | Finding | Severity | Done here |
|---|---------|----------|-----------|
| 1 | Shattered Lands' helper DSCLOG is full on all three counts (segment, upper memory, HMA) | blocker for the next SL change | no: owner's choice (below) |
| 2 | `ravager.resources_fixed`: eleven copy-pasted "maker" blocks | structural | yes |
| 3 | The sequel's dresser copied SL's copy-file code, and missed its reconnect guard | structural + bug | yes |
| 4 | `tracker.CAP`/`SHARE`: `None` fallbacks wrapped in two functions | boundary | yes |
| 5 | `ravlog`: the "make this range writable" idiom written out 22 times | spaghetti | yes |
| 6 | `__main__._sequel_party` re-ran `Layout.__init__` on its caller's object | magic | yes |
| 7 | The sequel's dresser doesn't check the picture store's room as SL's does | risk, unverified | no: noted in the gap list's spirit |
| 8 | DSCLOG2 repeats about 500 instructions of DSCLOG in runs of 10 to 47 | acceptable | no |
| 9 | Two ways to switch off a group of patches (`ravportraits.PATCH_NAMES`, `gamepatch.STEADY_PACE`) | nit | no |

No file crossed 1,000 lines in this range. The four big Loader files that were already past it grew a little
(`ravlog.py` 2,498 to 2,633, `ravager.py` 2,051 to 2,304); the sequel's new work went into new modules, which is
the right shape.

## 1. Shattered Lands' helper is full

Measured on `4926cb69` with nasm's symbol map (`tests/test_dsclog_room.py`'s `build_map`):

| Limit | Used | Free | Test margin |
|-------|------|------|-------------|
| The 64 KB segment (`kept_end`) | 65,280 | 256 bytes | 256: **at the margin** |
| Upper memory (`UMB_KEPT` of `UMB_ROOM`, paragraphs) | 8,143 of 8,182 | 624 bytes | 32 paragraphs (512 bytes) |
| The far block in the HMA (`FAR_END`) | 65,500 | 36 bytes | none |

DSCLOG2 (the sequel's) has room: its segment 2,325 bytes free past its 2,048 margin, and its upper memory 5,009
of 8,182 paragraphs.

So under the both-games rule, the next change that needs a byte of Shattered Lands' resident code fails the
build. #311 (open) already lands exactly on the segment margin. Text is not the lever any
more: earlier passes left only about 300 bytes of strings in the resident part. Moving code to the tail frees the
segment but not upper memory (`KEPT_PARAS` counts the tail).

What does help is in upper memory's own sum, `UMB_KEPT = helper + overlay buffer + music pool + see-through
tables`. The music pool (751 paragraphs, 12 KB) and the see-through figures' tables (885 paragraphs, 14 KB) are
already taken only if there is room when the helper loads. It's the build that insists they fit without
`UMBPLUS.COM`, which gives 24 KB more. **Recommendation (the owner's call)**: let the build count the see-through
tables against the room `UMBPLUS.COM` gives, and have DSCLOG fall back to conventional memory for them, as
`FAR_INIT` already does for the far block. That gives Shattered Lands about 14 KB of upper memory back. The cost
is 14 KB less for the game's heap on a machine where `UMBPLUS.COM` can't move the block, which is 58 KB free at
the fountain today. The segment still needs its own pass (cold creation-screen code to the tail).

## 2. `ravager.resources_fixed`: one table, one loop

The function had grown to eleven blocks of the same shape: check the skip name, parse the whole copy again,
call a maker, catch its errors, add its chunks, note the name. Each new sequel feature added another.

It is now a table of `(name, maker, errors)` and one loop. Each maker keeps its own error tuple, and runs in the
order it did before. Checked on the real files: the copy is **byte-identical** to before. That was tested with and
without the Shattered Lands folder, with steps skipped, and with no `OBJEX.GFF` (seven combinations, the same MD5
each). `objects_fixed` has the same shape on a smaller scale and was left alone.

## 3. One copy writer for both dressers, and a reconnect leak

`ravdress.RavDresser._check_copy` and `_write` were copies of `sprites.Dresser`'s, re-keyed by chunk type. Both
now use **`gff.CopyIndex`**, which:

- keeps each chunk's place and its room in the copy;
- reads the file's index again when the file has changed;
- writes chunks in place and updates their lengths;
- tells whether the copy already holds a chunk (`holds`).

The copy itself showed a missing piece. SL's Dresser checks `_same_in_copy` and skips a figure the copy already
holds, so a dice log that connects again doesn't reload every party picture. The sequel's had no such check. Each
reconnect marked every party picture STALE, and the game gave it a new slot in its 300-slot cache. It now skips
those figures the same way (`test_a_reconnect_loads_nothing_anew`).

## 4. `tracker.CAP` and `SHARE`

#278 gave the tracker `CAP: Optional[int] = None` and `SHARE = None`, plus `xp_cap()` and `xp_share()` wrappers
that fell back to Shattered Lands' values. That is a second rebinding scheme beside `ravlog.apply_layout`'s.
They are now plain values (`game.XP_CAP`, `game.xp_share`) that `apply_layout` rebinds and `restore_layout` puts
back, the same way it handles `quests.QUESTS`. The two wrappers are gone.

## 5. `ReadOnlyGuest.allow`

The block below appeared 22 times in `ravlog.py`, in three spellings (one put the range first):

```python
if r not in self.guest.writable:
    self.guest.writable = self.guest.writable + [r]
```

It is now one method, `self.guest.allow(ranges)`. The temporary form (`_writable`, a context manager) is
unchanged.

## 6. `_sequel_party`

To read a sequel save, Show Save ran `sl_layout.__init__(...)` on the layout its caller held, which changed it in
place. It now returns a new `Layout` beside the party.

## 7. The sequel's dresser and the picture store (not fixed)

SL's Dresser won't load a picture anew without room in the game's picture store (`_room_for`, `STORE_SIZE`). It
also reuses STALE cells (`Store`). The sequel's dresser does neither: it marks the cache slot STALE and the game
loads the picture again. Outfits change rarely there (only when a member's classes change), and finding 3 removes
the reconnect case. Still, a long session of class changes could fill the sequel's store as Shattered Lands' did
before its fix (30 to 60 changes). This needs the sequel's store measured in play first.

## 8. DSCLOG2 and DSCLOG

A sliding comparison of the added DSCLOG2 lines against DSCLOG finds about 500 instructions repeated in runs of
10 or more. The longest is 47, in `cp_vga`, which differs only in the chained-mode test. The big routines already
share code through `SHARED_*` macros. What's left differs by addresses and register choices, so moving more into
`.inc` files would cost readability for little gain. No action.

## 9. Two ways to switch off a group of patches (nit)

`ravager.patched_exe` turns `ravportraits.SKIP` into its patch names. `launch` turns the steady pace switch into
`gamepatch.STEADY_PACE`. A third such group would be the time to make one `{switch: patch names}` table.

## Checked and found sound

- `ravquests.py`: data only. `test_ravquests` holds it to the scripts, so every award is either in the table or
  in `LEFT_OUT` with a reason.
- `ravportraits.py`, `inventoryart.rav_chunks`: one job each, no shared-path branching.
- `freeze.py`'s sequel constants: tested against `ravager.DGROUP`.
- The site table in `ravager.PATCHES`: each new site carries its game address and Shattered Lands' counterpart.

## Tests

The full suite passes (3,258 tests, 249 skipped, `DSUN_REQUIRE_NASM=1`). So do the start-up tests on both
games' real files (3 passed).
