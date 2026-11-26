# Test log: see-through figures in Wake of the Ravager (2026-11-26)

Under test: DSCLOG2's SEE-THROUGH FIGURES (SL's code: `ghost_wanted`, `ghost_draw` in FIG_KEEP at site 162,
`ghost_union` in the redraws widened at site 160), its blend tables in the far block (the HMA) and only the
figure's pixels and runs in an upper memory block (5,632 bytes), and the Loader's `RavGhosts` writing the tables
(`dsloader/ravlog.py`). A new game in the throwaway copy `ravGX`, then `ravload.sh ravager-after-ambush
/tmp/playtest/ravGX`, the dice log attached. The test edits (STEALTH) were never saved.

## Steps

1. **Memory** (`dosmem.py`, the game running): DSCLOG2.EXE 55,840 bytes, its upper memory block 55,296 bytes,
   the ghost block 5,632 bytes (segment EEA0h), **94,512 bytes of upper memory left** in the largest piece (94,656
   in all; the shine's build left 100,832). The far block in the HMA now ends at FD00h (768 bytes free there).
2. **The Draxans' ambush** (a new game, Computer Control for all four): `ghost_on` 1 (the Loader's tables
   written). Ar'Anda hid in shadows once (the dice log's `hides in shadows: d100 = 10, needs 36 or less ... ->
   hidden`), STEALTH 1, and `ghost_draws` went 0 -> 18 -> 39 while she was hidden; at her next turn the hide
   failed (95, `-> seen`), STEALTH 0 and no more draws. Her figure in the fight
   (`img/2026-11-26-ravager-see-through-fight.png`): the floor's pattern through her.
3. **Against a control**, the same view: out of the fight, a test edit of STEALTH to 1 and a step down and back
   (the map is drawn again only when something moves), a grab; then STEALTH 0, the same step, a grab
   (`img/2026-11-26-ravager-see-through.png`: solid left, see-through right). The floor's dark grain shows
   through her hair, back and legs, the purple of her clothes dimmed; the look of Shattered Lands'
   (`obsidian-edition/docs/see-through.png`: the same 32-colour blend, unshrunk).

## Found

- The Loader's pass first failed unseen: the sequel's dice log has no `effects` (the `_step` wrapper swallowed the
  AttributeError); `RavGhosts` reads the game's own (`gd.effects()`).
- **The leader after a load**: three loads of ravager-after-ambush all gave Thy'rokh (DS:426Dh = 2). The number
  keys 1-4 on the map make member 0-3 the leader: the talk's answer keys (3, 1, 3, 2), sent when Notaku's talk had
  not come up, left Terrannus (2) the leader. That is what happened in the shine's run.
- **Notaku's prices**: Thy'rokh (CHA 15) 45,000, 20,800, 15,000 (the game's); with Terrannus (CHA 18, 5% off by
  the shops' CHA rule) 42,750 and 19,760, as the shine's picture shows ("2750", "9760": its crop cuts the first
  digit). No bug. The shop's portraits change whose inventory is shown, not the leader, so not the prices.

## Left

- Invisible creatures drawn see-through (effect 53) and Detect Invisibility (25) making them solid: only in the
  emulator tests (`tests/test_ravghost.py`); no invisible creature met in play.
- Without an HMA (not a GOG start) the far block, 8.5 KB bigger now, goes to upper memory: about 86,000 bytes left.
