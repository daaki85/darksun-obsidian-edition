# Rest kills the Poisoned even after the druid's free Neutralize Poison (8066Dh): proposed fix

## The game's code (DSUN.EXE file offsets; overlay 5E8h, code at 7FF30h, 140Bh bytes, 121 fixups)

Pass 2, one member (SI), loop head 80758h, entered only from 80984h (`jmp 80758h`):

| at | what |
|---|---|
| 80758h-80764h | `lea ax,[bp-0Ah]; push ax; push si; lcall 598:25h (76944h); add sp,4`: the member's effects as a 10-byte bitset at [bp-0Ah] (bit n = effect n; 76944h zeroes it, then ORs in a bit for each of the owner's records in the table at 390h:106h) |
| 80765h-807A0h | best cleric ([bp-10h], caster [bp-16h]) 5+: 809A2h(96 Cure Disease), (103 Remove Curse), (105 Remove Paralysis) |
| 807A1h-807D6h | best druid ([bp-12h], caster DI) 5+: the same three |
| 807D7h-807ECh | best druid 7+: 809A2h(118 Neutralize Poison) -> 5B8:20h (78BA8h), the game's cast: removes effect 35 from the table |
| 807EDh-80840h | mode 1 ([bp+6] = 1) and not status 8: `push 23h; push si; lcall 598:4Dh` (766ABh: remove effect 35), status 1, HP at least 1 |
| 80841h | Acid (1) removed |
| 80864h | status Okay (the mod: <= 1): HP = most (808AFh), PSP = most (808F3h), STR back from the sheet unless bit 13 Diseased ([bp-9] & 20h, 8092Eh) |
| **80963h** | **`test byte [bp-6],8` (bit 35, Poisoned) of the bitset read at 8075Dh; set -> `push 3E8h; push si; lcall 4E0:61h` (5859Ah: 1000 damage, HP + 10 or more: status 5 dead, HP 0)** |

The bitset is never read again after 8075Dh, so neither the druid's Neutralize Poison (807E7h) nor
the mode-1 removal (80808h) saves anyone: both take effect 35 out of the table, and the kill reads
the stale bit. The same stale bitset stops STR coming back on the rest that cures a disease
(Cure Disease at 80777h/807B1h, the test at 80929h). The mode-1 removal immediately followed by a
kill on the same effect shows the intent: the test should see the cures.

(Combat's per-turn effect routine, 78223h, has the same shape with the kill dead: `test [bp-10h],8 /
je; lcall 598:57h (a charge used); test [bp-10h],8 / jne skip` - so poison does nothing in a fight.)

## The fix: cast the cures before the bitset is read (a byte-level reorder, no DSCLOG)

Move the 7 casts (80765h-807ECh) ahead of the read. The read's `lcall 598:25h` has an overlay
fixup on its segment word (80760h) and cannot move; the casts are `nop; push cs; call near 809A2h`
(no far call, no fixup: the overlay's fixup list, 121 words at 8133Bh, has none in 80765h-807ECh or
80984h-80986h), so they can. Dropping the 7 `nop`s pays for the two jumps.

- **80984h** (3 bytes): `E9 D1 FD` (jmp 80758h) -> `E9 E1 FD` (jmp 80768h, the casts).
- **80765h-807ECh** (136 bytes, the same length), was
  `837ef0057c368a46f050ff76ea566a60900ee8280283c4088a46f050ff76ea566a67900ee8160283c4088a46f050ff76ea566a69900ee8040283c408837eee057c308a46ee5057566a60900ee8ee0183c4088a46ee5057566a67900ee8de0183c4088a46ee5057566a69900ee8ce0183c408837eee077c108a46ee5057566a76900ee8b80183c408`
  becomes
  `e98500837ef0057c338a46f050ff76ea566a600ee8260283c4088a46f050ff76ea566a670ee8150283c4088a46f050ff76ea566a690ee8040283c408837eee057c2d8a46ee5057566a600ee8ef0183c4088a46ee5057566a670ee8e00183c4088a46ee5057566a690ee8d10183c408837eee077c0f8a46ee5057566a760ee8bc0183c408e96cff90`

  i.e.
  ```
  80765 jmp 807EDh          ; after the read: on to mode 1 / Acid / HP / the poison test
  80768 (the 7 casts, as before, without their nops; jl targets 807A1h, 807D4h, 807E9h)
  807E9 jmp 80758h          ; then read the bitset
  807EC nop
  ```
  Source: `restfix/rest_order.asm` beside this file (nasm, org 0765h); a patched copy for checks
  `restfix/DSUN.restfix.EXE` (from the GOG DSUN.EXE).

As a gamepatch entry (two Patch()es, a rule group of its own or with the other fixes; nothing in
the mod touches 80765h-807ECh or 80984h: the mod's are game_rest 806C3h, new_okay_806fa,
new_okay_80864):

```python
# The rest's pass 2 (8066Dh) read each member's effects (76944h, 8075Dh) before the free cures and
# killed the Poisoned (1000 damage, 80963h) from that copy, so a 7th-level druid's Neutralize Poison
# saved no one: the 7 casts (near calls, no fixups) moved ahead of the read, their nops dropped
Patch("rest_cures_first", 0x80765, bytes.fromhex("837ef0057c36...b80183c408"), bytes.fromhex("e98500837e...e96cff90")),
Patch("rest_cures_loop", 0x80984, bytes.fromhex("e9d1fd"), bytes.fromhex("e9e1fd")),
```

Side effects (both the manual's way): a member cured of disease at a rest gets STR back that rest
(not the next); the poison kill now happens only to the Poisoned with no druid of 7th+ among the
Okay (the game's design, as the Player's Guide says: "Cure poison before resting").
Mode 1 rests still kill the Poisoned (their removal at 80808h is after the read); 8066Dh has one
caller, 62C2Ch, with mode 0, so mode 1 never runs in DSUN.EXE.

## Alternative (if a reorder is unwanted)

A DSCLOG site at 80963h (`test byte [bp-6],8 / je 80975h`, 6 bytes): INT + site + 3 nops, the
handler looking up effect 35 for SI in the live table (load seg + 3BF6h:0106h, DS:1E24h count) and
setting ZF / jumping to 80969h or 80975h. Bigger, and it needs the live-table walk in DSCLOG.

## DOSBox evidence (2026-11-09, playtest/logs/2026-11-09-rest-poison.md)

pens-fire-count4, K'ratchek a druid of 7th level in memory, Gerakis given Poisoned (addeffect.py):
- game's code: "Poisoned ends on Gerakis", then "Gerakis now 0/54 HP (-21)", status 5 (dead).
- the fix written into the loaded overlay (restfixmem.py fix): "Poisoned ends on Gerakis", status 1,
  54/54 HP.
- the fix, druid back to 2nd: Gerakis dead, Poisoned still on him (death leaves effects, so the
  first run's removal was the druid's cast).
