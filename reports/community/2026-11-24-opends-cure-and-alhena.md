# For OpenDS: Cure Critical Wounds pays 3d8+3, and GF123 is only the hostile-caravan flag (2026-11-24)

*Status: not posted. Checked against the stock GOG 1.10 Shattered Lands install. Answers the two open disagreements in OpenDS's `docs/reports/daaki85-crossread-2026-11-23.md`.*

**1. Cure Critical Wounds pays 3d8+3, not 3d8+1** (`spell-effects.md` line 144, `known-bugs.md` §3.7 row 8)

In the casting module (ovr32, file 0x78BA0) the spell switch is the value table at module offset 0xD96 (38 spell keys, targets at 0xDE2):

- spell 112 (your SPIN 113) -> 0x9DD = file 0x7957D: `push 80002h; call 538:89 (dice 2d8); add sp,4; inc ax` -> 2d8+1
- spell 127 (your SPIN 128) -> 0x9EF = file 0x7958F: `push 80003h; call 538:89 (dice 3d8); add sp,4; add ax,3` -> **3d8+3**

Both then go to the heal at 0x7BC1D, which only caps the amount at the target's maximum HP. So the game text "Heals 6 to 27" is correct. There is no text-vs-code gap.

**2. GF123 is never set in a normal playthrough, so Alhena isn't unreachable** (`fix.ds1.alhena-campfire`, sweep-triage row 2)

GF123 has exactly one write in GPLDATA: GPL-21 @0x28A, the start of sub 650 (it spawns the -105 guards around the party). Sub 650 is called only from these places:

- GPL-21 @0x51, 0x254, 0x25D: caravan people attacked ("Help!", "No! Oh, please, no!" / "HE-E-ELP! Murder! Fire!")
- GPL-24 @0x428: "How dare you!" / "Guards!"
- GPL-28 @0x480: "You were told to leave!" (coming back after being sent away)

So GF123 means the party made the caravan hostile. The ambush in the Elvish Caravan area doesn't set it. In a normal ending GF123 is 0, the exit at GPL-28 @0x298 doesn't fire, and Alhena spawns at GPL-28 @0x52A. The fix as written changes only the hostile-caravan case (Alhena would then come back to a caravan the party attacked). The QA site A2 setup ("with the caravan raided earlier") is that case. A quick check: play through the caravan peacefully and win the war. Alhena should appear without the fix.

