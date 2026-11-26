# S and a merchant's thank-you in Shattered Lands (2026-11-25)

**Under test**: whether Shattered Lands has the sequel's bug fixed on `claude/ravager-loot-keys` (f9152ee):
a merchant's script keeps the party's money (GPL variable 85h 0) before the shop and tests it as the
shop returns, so the Loader's S, which pays only after the shop has shut, gets the no-sale line.

**Result: SL doesn't have it (from the scripts; no play yet).** No SL shop script reads the money
after its shop.

## The scripts (decoded, the game's GPLDATA.GFF and the Loader's built copy)

Every script decoded in full (`gpl.load_scripts`, then `_op` over each; no errors). The shop command
is GPL op 24h (36; Kalzith's `s.op(0x24, SPEAKER)`). It is in nine places, and what follows each:

| Script | Merchant | After the shop |
|---|---|---|
| 23 0x1D0 | Jark (weapons wagon) | "I hope you found things to your liking." always |
| 25 0x44E | the artifacts-and-talismans wagon | the merchant's item count (op 51 on 137,39) before (7,33) against after: fewer, "Thank you for your business. I'm sure your purchase will be to your liking." |
| 25 0x590 | the same | "Look as you please..." always |
| 61 0x3BE | the fruit seller | "Nothing but the finest!" always |
| 71 0xE90, 0x13E6 | Melkor of Gedron | "You see? No finer merchandise..." / "I hope we can do business again, friend." always |
| 166 0x3DA | the teacher | "Good luck in your studies." always |
| 185 0xDFE | the archery seller | the party's item count (op 51 on 32766) after against before (7,27): more, "Enjoy your purchase, it will serve you well." |
| 218 0x92D (the Loader's) | Kalzith, the pens | "Learn them well, and burn the hide when you're done." always |

The scripts that test 85h 0 (2, 24, 65, 88, 135, 149, 152, 206) never open a shop. They are price
checks (`137,42 < 133,0`, can the party pay) for a fine (24), Toonuu's salt (65), the statue piece
(88) and the like. The only post-shop tests (25, 185) count items to spot a *purchase*. S takes
items from the party after the test, so it can't hide a purchase. A hand sale before the test can
(buy one, sell one by hand, and the counts are level), the game's own quirk; S never does.

## Play

Not played: the DOSBox lock was held by other agents the whole time, and the session was paused.
Every save in `playtest/saves/` is in the slave pens, where the only shop is Kalzith's (script 218,
an unconditional line). The merchants in 25 and 185 aren't reachable from those saves.
The next step, if a play is wanted: `loadsave.sh selling-junk-user`, `openshop.sh`, S, and read the
line after the shop ("Learn them well..." expected, as with no sale).

No fix needed in DSCLOG or the Loader.
