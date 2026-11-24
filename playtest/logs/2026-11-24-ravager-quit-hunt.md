# 2026-11-24: why the sequel quit in the transferred party's Tyr fights

**Under test:** Wake of the Ravager with the party transferred from Shattered Lands (the `ravG` copy,
`fountain-user`'s party), the Tyr ambush under computer control, branch `claude/ravager-stealth`. Each
run is the scratch `trial2.sh` (ravGgo, computer control on for the four, the fight watched 6
minutes, a frame every 10 s).

## What was seen

1. **It is the game quitting, not DOSBox crashing.** gdb on DOSBox caught `exit(0)` from `main`;
   with `RAV_MARK=1` the autoexec went on past the game (`ENDED.TXT` written at the moment it closed).
2. **Runs with the conf changed (`RAV_NOEXIT`, `RAV_PAUSE`) all reached "YOUR PARTY HAS BEEN
   DEFEATED" (15 of 15)**: luck. The quits came back with the normal conf: in 11 runs with probes, 4
   quit (es1, mk1, so1, and hg4, hg5, hg8, hg11 in the probe runs), nearly always at the start of
   Ester's turn.
3. **`RAV_STDOUT=1`** (the game's printing to `STDOUT.TXT`): once "Illegal Op (gpl=49)" (the script
   interpreter's message, DSUN.EXE 2140Ch).
4. **Probes (`RAV_POKE`)**: a 26-byte hang that saves SS:SP and BP to 0:4F2h and a flag to 0:4F0h, at
   the illegal-op routine (file 2660Ch), the fatal-error routine (3EFEFh, "Mel Fatal Error #: %d Trap
   #: %d") and `exit` (55DFh); `/tmp/playtest/hangwatch.py` dumped guest memory when the flag came.
   Run hg11 stopped in the fatal routine (flag BEEEh). Its call chain by BP, read in the dump (the
   overlaid code isn't at its file offsets): the sound manager (37F6:04FE, then the fatal error)
   <- B8:0A22 (play sound N) <- the fight's turn code, overlaid at 5EBB:1061 (file 6012Ah):
   `mov dx,[es:bx+3Ch]` of the member's 42h-byte sheet (`les bx,[19C5h]`), 62h when 0.
5. **The sheets in the dump**, +3Ch..+3Fh: Lex `00 81 00 28`, Seneca `00 01 00 28`, Ester `00 01 00 28`,
   Jenna `00 00 00 28`. +3Dh is the mod's kit byte (SL +43h, which CHARTRAN copies there) and +3Fh its
   new-spells byte (SL +45h): the high bytes of the sound words +3Ch and +3Eh (the second read whole
   at 89859h). Sound 100h or 8100h: no such sound, a fatal error. The earlier search had looked only
   for byte reads of +3Dh and +3Fh.
6. **The fix** (`ravtransfer.MOD_SHEET_BYTES`, on `claude/ravager-party-transfer` a09b8c3, merged up):
   the Loader's transfer leaves +3Dh and +3Fh 0. The party transferred again (8 months, the same
   four), **10 runs, none quit** (Ester had 16 turns between them; before, about 1 run in 3 quit).

Kits and the Elementalist's bits are therefore not in the sequel's sheet (nothing there used them).
Water: none new (no new area).

**Later (claude/ravager-sheet-room 26ad495): the kits put back.** The two sound words are now read as
their low bytes only (patches `sound_3c` at file 65333h and `sound_3e` at 8EA59h), so +3Dh and +3Fh
hold the kit byte (SL +43h) and the sphere/new-spell byte (SL +45h) again. The party was transferred
again with its kits kept and the Tyr ambush fought 8 times (`trial2.sh kt1`..`kt8`): **all 8 ALIVE,
none quit**, no fatal message in STDOUT.TXT, Ester taking up to 3 turns a run. Water: none new.
