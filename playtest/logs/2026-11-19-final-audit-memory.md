# 2026-11-19: the final code and memory audit's in-game memory measurement

Under test: the build of `claude/final-code-audit` (= `origin/claude/backstab-str-line`, f1f8972:
obsidian-edition with #115 and the REAR_FRESH backstab fix), DSCLOG.EXE 69,760 bytes, rebuilt
byte for byte from dsclog.asm. Tools: playtest/memaudit.py. DOSBox under /tmp/playtest/dosbox.lock.

## Steps
- pens-after-arena loaded (region 0x29), 320x240, buildcheck OK (rear_fresh, probe_stealth, stab_first same as the EXE; 129 vectors at their handlers). memaudit with the map open: DSCLOG block 69,984 bytes (4,374 paras), upper memory free in one piece 26,256 bytes (E330h, between the overlay buffer and the see-through tables), 144 bytes free at CA00h; conventional free 99,008 bytes in one piece (heap 201 KB, 0 free in it); UMB blocks 4374+2062+885+751 paras + 4 MCBs = 8,076 = UMB_KEPT.
- fountain-user, the ambush's fight on (round 1: 10 combatants, 30 creature records; foes Arena Guards, Templars, Guard, Legcrusher, Scar...): memaudit as on the map (conventional 99,008 in one piece, upper memory 26,256). Lex's USE screen up (map shut): heap 157 KB, DOS free 134,848 in one piece, upper memory unchanged. Ester's Curse cast at the Templar, memaudit 0.4 s after the click with its picture drawing (shot aud-cast2.png): conventional 99,008 + a 1,008-byte piece, heap 201 KB 0 free, upper memory unchanged. (Lex's first icon was Shocking Grasp: too far away.)
- selling-junk-user, openshop.sh: Kalzith's shop up (map shut): heap 171 KB, DOS free 124,608 in one piece (+5,104), upper memory unchanged. Escape (back to his talk, Farewell): heap 201 KB with 57,328 free in one piece; the talk clicked away, the map open again: DOS free 100,032 in one piece (+1,008), heap 196 KB, upper memory unchanged (26,256 at E330h, 144 at CA00h).
- Not done: no save made; nothing written to memory. Stopped by pid afterwards: the watchdog,
  the dice log, DOSBox and Xvfb; the lock released.

## Against the docs

- DEVELOPMENT-INTERNALS' memory table (its CA00h-EFFFh row) still gives DSCLOG's block as 69,936
  bytes and upper memory's free piece as 26,304: both are the build before REAR_FRESH. This build:
  69,984 bytes ((10h + `KEPT_PARAS` 1106h) paragraphs) and 26,256, 48 bytes (3 paragraphs) apart,
  REAR_FRESH's 48. The limits table (`kept_end` 64,192, `UMB_NEED` 6,454, `UMB_KEPT` 8,076,
  `FAR_END` 65,500) agrees with the build's map and with the blocks measured.
- Conventional memory with the map open: 99,008 bytes in one piece (the table's "97 KB": 96.7).

## Learned

- With the session's background lock holder running, a step's own `flock` on the same lock waits
  for the holder until its timeout (200 s here): run the steps without it (PLAYTESTING.md rule 11).
- A quick spell's picture: `fountain-user`, Ester's priest icon (194,59) is Curse, aimed; the
  Templar on the view's right is in reach (PLAYTESTING.md, Casting spells for a test).
- No new area reached: nothing for the water notes.
