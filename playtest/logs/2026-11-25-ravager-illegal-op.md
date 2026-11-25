# 2026-11-25: "Illegal Op (gpl=49)" in the sequel's Tyr ambush

**Under test:** Wake of the Ravager with the Loader (`RAV_LOADER=1`), the party transferred from
Shattered Lands (a copy of `ravG48`, the same four as [the quit hunt](2026-11-24-ravager-quit-hunt.md):
Lex, Seneca, Ester, Jenna), the Tyr ambush under computer control. The builds: `claude/ravager-sheet-room`
26ad495 (the kits kept, 42h sheet), 88b50db and its summon fix 02e331e (48h sheet), and the
`claude/ravager-specialize` head. Each run is a scratch trial (`/tmp`'s `rqtrial.sh`, trial2.sh's
steps: ADD the four, a new game, Computer Control for the four, the fight watched 6 minutes) with
`RAV_STDOUT=1`, `RAV_MARK=1` and two probes by `RAV_POKE`; `SAFE=1` set the four's HP (and the sheets'
max HP) to 250 so the fight lasts.

## What was seen

1. **The quit came back after the kit fix**, with every 48h build and the 42h one alike: at the
   start of Ester's turn the game printed "Illegal Op (gpl=49)" (STDOUT.TXT) and ended.

   | Build | HP 250 | Runs | Illegal op or quit |
   |---|---|---|---|
   | 26ad495 (42h) | yes | a1-a3 | 2 (a1 a false hang, below) |
   | specialize head (48h) | no | n1-n8 | 1 quit (n5); n6-n8 alive; n2-n4 false hangs; n1 lost |
   | specialize head | yes | p1-p4, q1, q2 | 6 of 6 |
   | specialize head, no dice log | yes | d1 | 1 of 1 (the dice log isn't the cause) |

   Not the 48h sheet, then, and not the transfer (the same party quit in the 42h build).
2. **The probes.** The illegal-op routine (DSUN.EXE 2140Ch in the image, file 2660Ch, called by the
   INT 6 handler at 2A88h; it prints the message and leaves by puts + `exit(1)`, 344ACh) took a hang
   probe saving SS:SP and BP: the 24 bytes `5031C08EC0268926F20426892EF60426C706F004EFBEEBFE`. The
   first probe there was 26 bytes and covered a relocated far call at +18h (file 26624h): the
   program's relocation added the load segment to two of its bytes, and DOSBox died with "Illegal
   GRP4" (runs sp2, p2). A probe at the fatal routine (file 3EFEFh) hung on every sound warning,
   trap 6Ah, which the routine only reports (below): runs a1, sp3, n2-n4 looked like hangs and were
   not quits, so that probe was dropped.
3. **The fault.** The INT 6 frame held CS:IP 0083:0001 / 0083:0003: SI:DI, with SI 83h (Charm Mammal,
   Ester's druid spell, at a target immune to it). The spell immunity routine (8451Ah) answers
   "immune" at 7F362h in the image, `mov ax,1 / jmp 7F8B1h` (the jump at file 84565h, `e9 49 05`),
   and 7F8B1h is the `pop di` of the routine's end, `xor ax,ax / pop di / pop si / leave / retf`. The
   Loader's `spell_hit` (file 84AAFh, `33 c0 5f` -> `cd f5 10`: DSCLOG2's TH_SITE, spells rolling to
   hit) overwrote that `pop di` with its site number 10h. The jump ran `10 5e c9` (`adc [bp-37h],bl`)
   and then the `retf`, which took DI:SI for the return address: an illegal opcode there, the
   script interpreter's message. Every spell meeting an immune target could do it; Charm Mammal at
   Tyr's foes did.
4. **The same mistake twice more** (a scan of every patch for a near jump from outside landing past
   its first byte, the hits checked against a disassembly):
   - `thief_skill_armour` (file 8C7C5h, `8b c6 5f` -> `cd f5 14`): the thief skill routine's
     `jmp 875C7h` (874C3h in the image, file 8C6C3h, `e9 01 01`) landed on 14h, so the routine
     answered about 5Eh where the game's answer was 0. A wrong skill, no crash.
   - `window` (file 303BEh, `33 c0 5e` -> `cd cf 90`): the window routine's failure exit,
     `jmp 2B1C0h` (2AF11h, file 30111h, `e9 ac 02`), landed on the NOP: SI not restored.
   - Shattered Lands' gamepatch `window` (file 2BBA9h) has the same jump into it (264FCh to 267ABh
     in SL's image): a lead, not changed here.
5. **The fix** (`dsloader/ravager.py`, 71afcd1): each jump sent to the same epilogue elsewhere in
   its segment, unpatched: `spell_hit_immune` (84565h: `e9 96 ff`, to 7F2FEh, `pop di / pop si /
   leave / retf`, the same overlay), `thief_skill_armour_out` (8C6C3h: `e9 7d ff`, to 87443h) and
   `window_fail` (30111h: `e9 dc 05`, to 2B4F0h, `pop si / leave / retf`).
   `tests/test_ravager.py`'s `JumpIntoSiteTests` checks each against the site it left and the
   epilogue it lands on, and scans the patched program's `jmp rel16`s for one landing in a patch.
6. **The summoned ally's sheet** (02e331e, found on the way, not this quit's cause: the probe on its
   routine never hit in q1 and q2): the summoning spells' routine (81515h) and 814A1h write sheet 4
   at constant offsets (`es:[bx+4 x 42h + field]`), which the 48h sheet's stride patches missed;
   five patches, `SHEET4_FIELDS`.

## The sound warning (trap 6Ah)

The fatal routine (39DEFh in the image, file 3EFEFh: "Mel Fatal Error #: %d Trap #: %d") returns at
once for trap 6Ah and stops the game only for 69h. Error 0Bh, trap 6Ah, comes from the sound loader:
its buffer at 4013:B63h is 61A8h (25000) bytes (set at 62042h), and the sounds BVOC 132, 138 and 147
are longer. 138 and 147 are in the female hurt and death sounds (the table at DS:2909h, one of 8
picked at random), so a woman's hurt or death warns now and then. Only a warning: the game goes on
(a sound cut short). `ravstart.sh`'s `RAV_SOUND=1` (01e52f4) keeps DOSBox's sound on, to SDL's
dummy audio device, so the game finds its card and loads them.

## After the fix

The fix's runs (3 controls with the three redirects left out by `RAV_SKIP`, then 10 with them,
HP 250, the specialize head with 71afcd1 merged) are being played; their counts follow here.

Water: none new (no new area).
