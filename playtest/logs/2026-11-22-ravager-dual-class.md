# Test log: dual-classing as the manual has it, Wake of the Ravager (2026-11-22)

Under test: SL's dual-classing (game.RULE_DUAL_CLASS, always on in SL; DSCLOG's DUAL_LEVEL and
DUAL_PRIMES) in DSCLOG2: DUAL_LEVEL (site 37 at 7926Ch, 7948Bh, 94BCCh) and DUAL_PRIMES (sites 38 and
39 at 94B70h, 94BA5h), each with the rule (RULE_HI_DUAL, 2048) and the game's compare without.
RULE_DUAL_CLASS added to ravager.RULES_PORTED.

## Found first

- The sequel's DUAL code is SL's (86E94h's class test is its 94B20h on) with its records: the sheet's
  first level +1Eh (SL's +24h), classes +1Bh, the creature's scores +19h (SL's +22h, 31h bytes a
  creature), the class map 360h:9Dh (SL's 338h:CAh), the ability table 360h:153h (SL's 338h:180h); its
  jumps are unsigned (jc, jnc where SL's are jl, jnl). `cmp byte [es:bx+19h],11h` is also at 82D28h:
  not the DUAL window's.
- The sequel's classes 18 and 19 (a wizard's and a priest's) are given INT and WIS in DUAL_PRIMES_OF.

## In the game (ravload.sh ravager-roost, the Loader, the dice log on; about 20:55-21:05 UTC)

Test edits, DOSBox stopped after, nothing saved: Terrannus (member 1, a human cleric, dead in this
save) given 30 HP and Okay (creature +14h 1), STR 17, DEX 14, WIS 17, CHA 12 (creature +19h on and
sheet +15h on; CON 18, INT 12 his own). The inventory (I), a right-click on his portrait (game 30, 69),
DUAL (70, 98); EXIT (219, 146).

- **The rule on** (rules_hi FE2Eh), 7th level: FIGHTER, GLADIATOR and PSIONICIST white; DRUID, PRESERVER,
  RANGER (DEX 14 under 17) and THIEF grey. DUAL_PRIMES counted 43.
- **Control, the rule off** (F62Eh): **RANGER white** too (the game's one ability, WIS 17); the rest the
  same. Nothing counted.
- **2nd level** (sheet +1Eh 2): control, the portrait menu has **DUAL**; the rule on, **CANCEL** in its
  place (the manual's third level).
- Water: nothing new.

## The View Character menu's test (ravager-after-ambush, about 21:45 UTC)

DUAL_LEVEL's second place (7948Bh): the portrait menu of the View Character screen (the inventory's bar,
VIEW CHARACTER at game 170, 185; a right-click on Terrannus's portrait, 120, 56). Test edits, nothing
saved: Terrannus a human cleric (classes 2, class bits 0002h, dualset.py's scores), his level written.

- **2nd level, the rule on** (rules_hi FF2Eh): EDIT NAME / DROP / **CANCEL**.
- **Control, the rule off** (F72Eh): EDIT NAME / DROP / **DUAL** (and DUAL opens the window).
- **3rd level, the rule on**: **DUAL**.
- Water: nothing new.

Result: dual-classing as the manual has it works in the sequel as in Shattered Lands.
