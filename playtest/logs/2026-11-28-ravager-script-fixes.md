# Ravager script fixes: play checks (2026-11-28)

Under test: PR #310 (branch `claude/ravager-script-bugs`), the sweep of the sequel's scripts
(`reports/ravager-script-bugs-2026-11-28.md`). Build: the branch at its head, started by `ravload.sh
ravager-roost` (the Loader's `dos/GPLDAT2.GFF` checked: GPL 143 at C54h jumps to the cap after the script's
end, D5Ah takes `v2[0]`; GPL 47 at 374h reads flag 131). Never saved.

## The ore voucher sale: seen working

The cashiers are in the mines, far from any save, so the sale ran as a probe in Reyhan's talk
(`ravprobe.py`, the commands in `files/2026-11-28-ravager-voucher-probe.hex`): give the party 460 ore
vouchers, run the game's own sale (GPL 143's count, total, share and pay, unchanged), then give 460 again and
run the Loader's (the same commands with the 327 cap before the total and the take of the counted vouchers),
printing what is left after each.

| | Vouchers | Total | City's share | Paid | Left |
|---|---|---|---|---|---|
| The game's sale | 460 | -19,536 | -11,718 | **-7,818** | 0 |
| The Loader's | 327 | 32,700 | 19,620 | **13,080** | 133 |

Money 5,000 before, 10,262 after (5,000 - 7,818 + 13,080): the game's sale took money away, the fixed one
pays 40 a voucher and leaves the rest for the next sale. (The report had -9,768 worked out by hand; the game
pays -7,818, now in the report, GAME-BUGS.md and the code's note.)

## Ptar's pickpocket: not reached in play

`ravjump.py 1 20 20` (RGN001, the square GPL 30 moves the party to inside Ptar's cave) did land the party in
the cave, but half there as ravjump.py warns: the leader stuck at (322,308) at the cave's east wall, the view
garbled, Ptar (-445, ETAB at map 75,357) out of reach, and his look trigger (857 of GPL 47) is set by GPL 30
only as the party comes in by the cave's own exit. So the pickpocket was checked on the bytes only: the three
places that ask whether the key is gone (GPL 47 at 374h, 29 at 352h, 46 at 215h) read flag 131, the one the
pickpocket sets at 451h (`test_ptar_key_is_taken_once`), which is what the walkthrough's "he has the key on
him even if you pick his pocket" says went wrong. Seeing it in play needs a save in Humbleton.

## Learned

- `ravprobe.py HEX`: a script probe run by Reyhan's talk, for what a fixed script does in the game's own
  interpreter (its prints read back by `ravtext.py`). The ETAB's object is the number unnegated (Ptar,
  -445, is stored BD01h at +6).
- After a jump to a region whose story scene is entered by an exit (Ptar's cave), the scene's triggers aren't
  set: the jump's place is no substitute for the exit.
