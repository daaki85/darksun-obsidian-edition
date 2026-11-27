# The kits on Wake of the Ravager's DAM lines and creation THAC0, 2026-11-27

**Under test**: DSCLOG2's `DAM_KIT_MELEE` and `DAM_EXPERT` in `DAM_LINE` and `VIEW_DAM` (the inventory's and
View Character's DAM lines), and `CR_KIT_THAC0` in `PROBE_CR_HP` (the creation screen's THAC0 line), with
`SCHOLAR_THAC0` noting whether the creature's THAC0 has the Scholar in it. Branch `claude/sequel-dam-lines`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session. Memory edits were made for the test only and
nothing was saved.

**The creation screen** (`ravcreation.sh 0`: a new human, preserver at 255,45, KITS 234,138, the Scholar
250,114; the die 145,92). M is the THAC0 less STR's to-hit, R less DEX's missile adjustment.

1. A preserver with no kit, rolled: STR 17, DEX 17, "THAC0: M17 R16" (18, the 7th-level preserver's).
2. The Scholar chosen, rolled: STR 14, DEX 17, "M19 R17" (19). The roll works the creature's THAC0 out again
   through the THAC0 routine, so `SCHOLAR_THAC0` (`scholar_thac0s` 12) already puts the kit in, and the line
   adds nothing (`cr_kits` 0). **Found**: the first build of `CR_KIT_THAC0` added the Scholar's 1 on top of
   that ("M20 R18" for a 19), which is why it now asks `CR_THAC0_SCHOLAR`.
3. The Scholar clicked again (taken back: kit byte 0FFh), then the line drawn without a roll (a click at
   40,162): "M17 R17" with STR 17, DEX 16, so 18 (`cr_kits` 1: the kit taken out of the creature's 19).
4. The Scholar chosen again, the line drawn the same way: "M18 R18", so 19.

**The DAM lines** (`ravload.sh ravager-after-ambush`; the USE screen from the top-left icon at 22,17, the
inventory at 75,171, View Character at 170,188). **The dice log must run** (`ravdice.py`): without it the
Loader's rules aren't in DSCLOG2's header (`ravkits.py count`: "rules 0x0000 rules_hi 0x0000"), and no kit
does anything.

5. Gerakis (half-giant, STR 24) set to a 7th-level fighter with the Ravager kit (`ravkits.py set 3 3 5 9`).
   Inventory: "+4 Dragonsbane 2x1D8+17" and "+1 Longsword 1D8+14" (the off hand's one a round), 1 more than
   the game's; View Character "DAM: 2x1D8+17". The kit byte set to 0: "2x1D8+16".
6. Set to a 7th-level preserver Battle Mage (`set 3 2 5 11`) with long sword its chosen weapon (the specs
   bytes copied from Terrannus's) and the sheet's attacks byte (+24h) 2, a preserver's one a round: View
   Character "DAM: 2x1D8+16" (expertise: 2 a round from 7th level). `kit_rates`, the attack's count, stayed
   0. No kit: "1x1D8+16".

**Result**: the DAM lines show the kits' damage and expertise as the attack has them, and the creation
screen's THAC0 line follows the Scholar kit as it is chosen or taken back. Every DOSBox and dice log of
this test was closed by pid.
