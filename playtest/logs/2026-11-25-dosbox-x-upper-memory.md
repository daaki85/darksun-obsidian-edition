# 2026-11-25: more upper memory under DOSBox-X

The question: can DOSBox-X give Shattered Lands' helper DSCLOG more upper memory than GOG's
DOSBox 0.74 does (about 944 bytes spare there)? DOSBox-X 2026.10.01, built here, the Loader's
own configuration (`start_dosboxx.sh`), save `fountain-user`.

## What sets the upper memory in DOSBox-X (its source, src/ints/xms.cpp and src/dos/dos.cpp)

- The VGA BIOS takes C000-C3FF (16 KB, `svga_s3`).
- With `kernel allocation in umb=true` (the Loader's) DOS's own tables take C400-CBFF, so upper
  memory starts at CC00. `private area in umb=false` and a smaller `private area size` change
  nothing while the kernel is in upper memory. Only `kernel allocation in umb=false` plus
  `private area in umb=false` moves them: upper memory then starts at C400 (+32 KB) but the
  game loses the same 32 KB of conventional memory (MEM: 632 KB down to 586 KB free).
- `umb start` can't go below C000 or below the private area: it buys nothing here.
- The top is the ROM BIOS, 64 KB from F000 by default. `umb end` past EFFF alone turns upper
  memory **off** (MEM shows 0 K). With `[dosbox] rom bios allocation max=16` and
  `rom bios minimum size=16` the BIOS fits in FC00-FFFF and `umb end=FBFF` works.
- EMS stays off; the HMA already holds DSCLOG's far block.

MEM with no game: today's settings 144 KB upper (CC00-EFFF), with the three BIOS/UMB lines
192 KB (CC00-FBFF), 632 KB conventional either way.

## In the game, with `extra=dos|umb end=FBFF extra=dosbox|rom bios allocation max=16 extra=dosbox|rom bios minimum size=16`

- The save loaded, the fountain ambush was fought out with `PT_NO_EDIT=1 fightout.sh` (won,
  19 passes), nothing looked wrong.
- `memaudit.py` after loading: the free upper block grew from 16,368 bytes (E59A, today's
  settings, the same save) to 65,520 bytes (E59A-F599): **48 KB more**. DSCLOG's blocks are the
  same; its ghost block moved up (E99B to F59B). Conventional memory unchanged (94,880 free).

Not tried: sound, a long play, older DOSBox-X versions (whether 2025.01.01 has the two BIOS
options is unchecked), Windows and macOS.
