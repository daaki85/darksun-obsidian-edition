# Wake of the Ravager's scripts: a bug sweep (2026-11-28)

All 350 of the sequel's scripts (GPLDATA.GFF of the GOG release 1.1, 104,572 commands) were read with the
Loader's reader (`dsloader/gpl.py`, which reads every one of them since #308) and swept for the kinds of
slip Shattered Lands' scripts had (`dsloader/scriptfixes.py`, DEVELOPMENT-CONTENT.md's "The game's script
bugs"). What each finding meant to do was checked against the scripts around it and, where a walkthrough
says what happens in play, against the owner's private walkthrough (nothing of it is quoted here).

Branch `claude/ravager-script-bugs`. The fixes are in `dsloader/ravager.py`'s `SCRIPT_FIXES`, each a change
of the same length: the sequel's script buffer is the game's 10,000 bytes and its largest script 9,985, so
no fix may grow a script until the buffer is raised (being done in `claude/ravager-engine-fixes`).

Not yet seen in play: each fix is checked against the game's bytes as the copy is made, and the tests
decode every fixed script whole (`test_ravager`'s `test_script_fixes_decode`, `test_ptar_key_is_taken_once`).

## Fixed, by severity

| # | Severity | Where | The bug | The fix |
|---|---|---|---|---|
| 1 | High | GPL 143 at C54h, GPL 144 at AE7h (the ore voucher cashiers) | The total, vouchers times 100, is a 16-bit number: past 327 vouchers it goes negative, and the city's share is worked out from it, so a big stack paid a negative sum (460 vouchers: -9,768) and cashing in took money away. | The share and the pay are each the vouchers times their rate (144: 50 and 50, or 70 and 30 once flag 377 is set; 143: 60 and 40): right up to 655 vouchers at once. The grand total the cashier names still wraps past 327 (only words). |
| 2 | High | GPL 47 at 374h, GPL 29 at 352h, GPL 46 at 215h (Ptar, Humbleton) | The sleeping giant's pocket picked gives the key to Magnolia's chains and 2,000 XP and sets flag 131 (the Journal's "key taken"); but what asks whether the key is gone reads flag 82, which no script sets: the giant's menu, his body's key and his "I no find key" when asked for it. So the pocket could be picked again and again, a key and 2,000 XP each time, and he still had the key. | The three read 131. |
| 3 | Medium | GPL 25 at Dh and 35h; GPL 254 at 9Fh; MAS 52 at A8h | Developers' messages printed in play: "DEBUG : got to here!" and "DEBUG : here we are now!" as one of GPL 81's creatures sees the party, "DEBUG: sur_main" in Surrakina's talk, "DEBUG: Killer is defiled." in Kalak's pyramid. | Each print jumped over (the jump and fill the `inn_rest` fix uses). |
| 4 | Low | GPL 46 at 1114h (Ptar) | "I will not kill you for saying this, warrior" tested the class bits against 606 (25Eh: ranger, gladiator, druid and the earth, fire and water clerics), a slip for 608 (260h: fighter, gladiator, ranger, the warriors as GPL 11 at E97h tests them): a fighter wasn't called a warrior, a druid was. | 608. |
| 5 | Low | GPL 46 at 4Ch (Ptar) | "I let Magnolia go!" is offered when global number 41 is `10 or 10`; GPL 40 sets 10 or 11 as she is freed (46Fh, 477h), so one way of freeing her never got the taunt. | `10 or 11`. |
| 6 | Low | GPL 45 at CDBh (a camp's leaders and peons) | Each peon kind is given its look handler (the leaders -137, -131, -135, -133, their peons -138, -132, -136, -134); the last peon's went to -133, its leader, so peon -134 had no look text. | -134. |

## Found, waiting for room (they make a script longer)

- **Race and sex read from the combat record** (low): the same bug the Loader's sweep and yuan-ti found in
  Shattered Lands. The sequel's scripts read a character's race and sex through field 15 (the character's
  own record: `.15.41`, `.15.42`, over 140 times), but 17 places read field 41 or 42 straight off the active
  member (or the actor), whose record has neither, so they always read 0: a thri-kreen is never called a
  "bug" or told of its mandibles, a woman never "lass", "girl", "her" or "woman", the halfling's "you're a
  halfling, too" and the races' insults never fit. GPL 31 at 975h, 35 at 1E3h, 46 at 2AEh, 64 at 8E7h,
  103 at 340h, 104 at F4Dh, 111 at 60Dh, 115 at 2086h, 125 at 9A5h, 126 at 339h, 149 at 78Fh, 219 at FBAh
  and 1569h, 248 at 25D3h, 254 at FC7h (next to a `.15.42` test of its own), 295 at A79h, 307 at BA5h. Each
  needs one byte more (the `.15`): Shattered Lands' detour (`scriptfixes.repaired`) once the buffer is
  bigger. GPL 248 is already 9,982 bytes.
- **Typos in the text** (low): a fix that changes a string's length needs a detour too. The clear ones:
  acquaintence (GPL 134, 261), adressed (69), aliance (34, twice), aproached (60), aquaintance (242),
  artristry (161), awfull (65), bracelt (18), bretheren (110), businees (136), ceremaic and Bohumir for
  Bohimur (128; Bohumir in 134 too), chadelier (105), clorored and headress (60), comissioned (221),
  competion's (155), cretures (88), embarassing (83), encorcelled (60), endebted (330), formidible (129),
  infomation, ingrediant(s), memmories, neclace, occaisionally, occurances, parargraph, perhpass,
  persistant, poisonus, recieve(s), reknowned, responsibilites, ressurect (256), resetd (127), saftey,
  somone, somthing, sorrounded, soutwest, stangers, suddlenly, synposis, thier, tourquoise, unmistakeable,
  vengance, villian, volunteeer, waitng, weilded, wthout, Noretmus for Nortemus, Solurnus beside Solurnis.
  (The sweep's word list, with each script and place, is easy to make again: every string through a
  dictionary; the dialects, hisses and the mind flayer's victim's run-together words are meant.)

## Probable, left as the game has them

- **GPL 254 at B30h**: "I'm not scared to have a magician along" tests the class bits against 398 (18Eh:
  psionicist, preserver and three of the four clerics), leaving out the air cleric and the druid, who hear
  "another sword-arm"; most likely 415 (19Fh, the casters, as GPL 195 at B80h and 46 at E36h test them),
  but not a one-digit slip like #4, so left for a decision.
- **Unreachable talk**: 56 global flags are tested but set by no script (Shattered Lands has 42 such:
  mostly leftovers). The ones that hide something whole: 288 (the psurlon's "I've seen psurlons there
  already", GPL 112; it sets 287 as the party agrees, which nothing reads), 688 (the plague's sufferer
  feeling better, GPL 304; it sets 687 there, which nothing reads, and that talk's two replies print
  "Debug. Info.", so it is best left unreached), 106 (Dmitri's "with my mother dead", GPL 34), 111 and
  112 (Humbleton after the yuan-ti are beaten, GPL 36), 439 (the temple's quake, GPL 195 and 203). Which
  event was meant to set each is not in the scripts.
- **An item no object file has**: GPL 283 at 3EEh first tries to pay with item -911, which isn't in
  OBJEX.GFF, so the party always pays 100 coins.
- **Triggers pointed at a lone exit** (GPL 24 at 1): 41 registrations, the sequel's way of switching a
  trigger off (the creature's attack, talk or look then does nothing). Shattered Lands' Darkhold bug was a
  story beat re-pointing a live handler there; the ones spot-checked here are the end of their scene.

## Looked for and not found

- Every trigger and call lands on a command of an existing script (apart from GPL 24 above); every IF,
  ELSE and loop jump on a command (the reader's own check).
- No test of the form `x != a or x != b` (Shattered Lands' GPL 44) and one `x == a or x == a` (#5).
- No class bit compared whole (`== 80h`); the class masks are the casters, warriors, thieves and rangers
  but for #4 and GPL 254's 398.
- Rewards: of the 125 calls of script 27's award routines and the scripts' own awards, only Ptar's (#2)
  sets a flag that nothing reads; the others are behind a test of their own or end their talk.
- Things players report that aren't the scripts: Bohimur stuck if not followed closely (his walk), a mines
  area saying NO PATH FROM HERE, two of the Bloodletter coffer's six golems not attacking (GPL 326 makes
  all six and sets them all hunting).

## Shattered Lands (both games' parity)

Shattered Lands' scripts had the race and sex bug, the always-true test and the class masks, all mended
already (`scriptfixes.py`); none of the sequel's fixed bugs is in them (no DEBUG text, no voucher sums, no
flag beside a reward that nothing reads). The same flag-pair sweep there lists flags set and never read
beside flags read and never set (GPL 12's 84 and 89, 50 and 51's 237 and 238, 62's 272 and 276, 143 and
144's 550 and 552, 159 and 160's 587 and 588, 194 and 195's 688 and 689, 216's 742 and 743); those read so
far (216) are different events, not slips. A later pass can read the rest.
