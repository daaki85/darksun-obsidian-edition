# 2026-11-24: Shattered Lands' stealth in Wake of the Ravager, and a crash hunt

*Branch `claude/ravager-stealth` (built on `claude/ravager-party-transfer`, PR #151). The user's ask
(2026-11-23): "Port stealth?", so the Boots and Cloak of Elvenkind work in the sequel.*

## The build

- **DSCLOG2's MISSILE_REAR** (5C99Fh, the attack's set-up) takes SL's PROBE_STEALTH: with RULE_STEALTH,
  a party member whose bit the Loader set in STEALTH (header +204; +206 counts them) has the attack made
  one from behind (`[BP-19h]`, 2 off THAC0 `[BP-1Eh]`) and, on the game's own conditions (5C952h-5C983h:
  a thief, melee, a weapon type whose byte +2 is 28h or less), a backstab (`[BP-21h]`, 2 more). A
  hidden archer's shot stays from behind. **REAR_FRESH** first: the routine runs all of a round's
  attacks in one call but clears the flags once, so a flag an earlier attack left is cleared when this
  attack didn't pay for it (THAC0 vs the creature's +16h).
- **The Loader**: RULE_STEALTH in RULES_PORTED; RavDiceLog runs SL's `turn_lines` (whose turn, the
  hiding rolls: `stealth.turn`) and writes only the STEALTH word. Sequel layout: positions at
  DS:67C5h, 25h apart; the footprint byte; dying and dead 4 and 7; the Elvenkind types 121 and 122.
  Regions under the open sky by each RGNxx.GFF's own name (its `RNME` chunk): forest (01), Tyr (32),
  Jann (3B), Silt Giants (41), Cloud (42), Limbo (FF); the rest are roofed or underground.
- **Found on the way**: the thief skills' blocking effects were SL's numbers. The sequel's 25 is Detect
  Invisible (Seneca's worn item), SL's 25 Mirror Images, so Seneca hid at 0. Now mapped by name.
- Unit tests: `test_ravprotect.test_stealth` (15 cases), `test_ravlog.StealthPortTests`.

## In the game (the transferred fountain-user party, Tyr's opening ambush, Computer Control for all four)

- **Hiding rolls**: `Jenna hides in shadows: d100 = 28, needs 37 or less (37, a ranger under the open
  sky) -> hidden`, `Seneca hides in shadows: ... (57 +10 cloak = 67, halved in daylight)`, and
  "can't hide in shadows: Draxan is right beside them".
- **A hidden shot**: `Seneca attacks Draxan#21 unseen with Wooden Sling`; DSCLOG2's `stealth_used` 1,
  `rear_taken` 0 (the hidden shot kept from behind).
- **A backstab and a hidden ranger** (`RAV_STEALTH_ROLL=1`, Seneca's sling put in the pack: test edits,
  never saved): `Seneca attacks Draxan#26 BACKSTAB with Bone item 291 +1 ... target AC 5` (its DEX and
  shield out; AC 1 otherwise), `Jenna attacks Draxan#27 from behind with Obsidian Longsword ... target
  AC 5`, her next two swings at AC 1 (REAR_FRESH: no stale flag). `stealth_used` 2.
- **Elvenkind** (Seneca's worn cloak and boots made types 121 and 122, a test edit): `Seneca hides in
  shadows: d100 = 1, needs 95 or less (Cloak of Elvenkind, under the open sky)`, `moves silently: ...
  needs 95 (Boots of Elvenkind)` (stealth.turn run on the live game, the enemy-beside test passed by:
  in the fight a Draxan always stood beside her).

## The crash hunt

DOSBox (the whole program, not only the game) died in about half of the runs of this fight, in round
1 to 3; just before, the dice log read creature records as garbage. Ruled out, each by a run that died
anyway: the stealth code (the helper before it: died once), the spell arrows' sites (`RAV_SKIP=
weapon_cast,plain_arrow`), the dice log (no Loader attached: died), DOSBox's dynamic core
(`RAV_CORE=normal`: died), the game's own exit (`RAV_NOEXIT=1`: DOSBox gone all the same). Found on
the way and fixed (PR #151): a melee hit cast the quiver's arrows' spell (Shocking Grasp from Lex's
sword: PLAIN_ARROW now keeps a melee hit to the weapon's own spell). Runs with the worn items' spells
cleared, with strace attached, and most runs made in one long command lived. Open: whether it is
this cloud DOSBox (0.74-3; CLAUDE.md: it dies when the session sits idle) or the game.

No new area, no water noted.
