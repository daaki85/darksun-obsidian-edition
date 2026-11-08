# 2026-11-08: the helper's buffers over its install code, in DOSBox

Under test: DSCLOG with `seg_space`, `area_space` and `dark` (1,664 bytes) laid over the install
code (`AFTER_INSTALL`), zeroed by `KEEP`; DSCLOG.EXE 63,824 bytes (was 65,472).

1. `loadsave.sh pens-after-arena`: loaded, the dice log attached.
2. `memaudit.py`: DSCLOG in upper memory at C90Ah, 63,952 bytes (PSP + kept to F8D0h); the
   overlay buffer at D8C9h, the see-through tables and the music pool after it; the HMA the far
   block's (far_seg FFFF). DOS memory free after the game 97 KB (the largest piece 99,008 bytes),
   as before.
3. The three buffers in the running helper (header C91B0h + F250h, F450h, F7D0h): seg_space 148
   bytes set, area_space 676, dark all 256; the header's SEG_MOVED 1. The party's shadows drawn on
   the map.
4. Walked (1672,344) to (1704,344) and back: no fault.

Result: the helper installs and runs as before, with 1,744 bytes of its segment spare (was 96).
