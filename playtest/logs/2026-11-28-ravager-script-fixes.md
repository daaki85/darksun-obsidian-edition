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

## Ptar's pickpocket: seen working

A first try, `ravjump.py 1 20 20` (the square GPL 30 puts the party on inside the cave), left the party half
there and Ptar's look unset: GPL 30 sets it only as the party comes in by the cave's mouth. The mouth is MAS 1's
area (73,83), 2 by 1, whose handler (GPL 30 at 31Ah, the case of the party's column 73 or 74) runs the entry at
72Fh. So (`files/2026-11-28-ravager-to-ptar.sh`): the jump to square (73,86) below the mouth, the camera put
on the party (`files/2026-11-28-ravager-camera.py set`, USE opened and closed), key 1 to make Ar'Anda (member
0, preserver, psionicist and thief) the leader, Up into the mouth, "Use the tunnel?" Yes: the party whole in
the cave, Ptar asleep at its west end. Ar'Anda walked to him with a Space between steps (each step "Ar'Anda
moves silently..."), and the look on Ptar:

1. "The giant is sleeping." WHAT DO YOU DO? Pick his pockets / Wake him up / Do nothing
   (`img/2026-11-28-ptar-menu.png`). 1: "You found a key!" (`img/2026-11-28-ptar-key.png`), Ar'Anda's XP
   45,582 to 46,248 (the 2,000 split over her three classes).
2. The look again: no menu; Ptar wakes, "Err -- umpf! Who is that? Thief! Assassin!"
   (`img/2026-11-28-ptar-second-look.png`). In the game as shipped the menu came back every time (the
   walkthrough's "he has the key ... even if you pick his pocket"), since the menu read flag 82.

## Learned

- `ravprobe.py HEX`: a script probe run by Reyhan's talk, for what a fixed script does in the game's own
  interpreter (its prints read back by `ravtext.py`). The ETAB's object is the number unnegated (Ptar,
  -445, is stored BD01h at +6).
- After a jump to a region whose story scene is entered by an exit (Ptar's cave), the scene's triggers aren't
  set: jump to open ground beside the exit's area instead (MAS N's 6Ah areas; GMAP 0 squares) and walk in. Out
  of the Roost's talk the party is then whole (all four drawn, walking with the arrow keys).
- In Ptar's cave each step of a thief leader brings a Move Silently message: Space, then the next step.
