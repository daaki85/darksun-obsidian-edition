# Play test: switches always on, with an old settings.json that unticks them (2026-11-18)

Under test: branch `claude/fewer-switches`. The Options tab's switches removed by the owner's
decision are always on (`game.ALWAYS_ON`): an old settings.json with them `false` must not turn
them off. Before `loadsave.sh`, `obsidian-edition/settings.json` was written with `false` for
shadows, dust, weapon specialization, thieves as in AD&D, spells rolling to hit, spells as the
manual, hiding in shadows, see-through figures, the combat log, choosing an enemy, held targets,
what the party wears, ages, class restrictions and the merged-away halves `no_doubled_save` and
`backstab_dice`; and `helm_ac` (a switch the tab keeps), which had to stay off.

DOSBox, the Loader's patched game, dice log `$PLAYTEST_WORK/dice.txt`, the DOSBox lock held, the
watchdog up (no STUCK or GONE). Save: `fountain-user`. Nothing saved; memory edits
(`spellsetup.py`, `hp.py`) lost with DOSBox stopped.

## Summary

| Check | Seen | Verdict |
|---|---|---|
| settings.json after start.sh's read and save | only `settings_version`, `window_scale`, `helm_ac: false`, `game_dir`: every always-on key dropped, the kept switch's `false` kept | OK |
| DSCLOG's rules words (header +170, +270) | `rules 0xfff4`, `rules_hi 0xff3f` = `0xff3ffff4`, `game.rules_from_settings({"helm_ac": False})` exactly: every gone rule's bit set, two weapons too, helms' off | OK |
| The patched copy | `SPELLS_MANUAL` (49 patches), `SPELL_TO_HIT`, `EFFECTS_KEPT`, `ROLL_STORE`, `CAMERA`, `SCENE_POINTER`, `MOUSE_START`, `PARTY_SPREAD` all applied in `dos/DSUNLOG.EXE` (7A15Ah `cd987d`) | OK |
| Shadows, dust, gear on the figures | the opening shot: a dust trail behind Pehtucl running, soft shadows under the party, their gear drawn (`img/` not kept: the doc pictures show the same) | OK |
| The combat log | L showed the panel over the map (Round 1: Lex) | OK |
| Choosing an enemy | Tab: `Chosen with Tab: Templar (150 HP) - Enter attacks it`, the red ring under him | OK |
| A spell rolling to hit | `Lex's Acid Arrow at Templar: attack d20 = 10, needs 4+ (85%) (THAC0 12 (a fighter's of the caster's level), +4 DEX; target AC 4) -> HIT` | OK |
| Weapon specialization | Ester's and Seneca's attacks `+1 specialized` to hit, `+2 specialized` damage | OK |
| Hiding in shadows, the cloak and boots | `Seneca hides in shadows: d100 = 30, needs 67 or less (57 +10 cloak = 67, out of the sun) -> hidden`, `Seneca moves silently: ... needs 77 (67 +10 boots)` | OK |
| Thieves as in AD&D | Seneca's hide 57 and move silently 67 are AD&D's table (`thief_skill_parts`); the game's would be 66 and 71 | OK |

## Steps

- The lock taken (`flock` on `/tmp/playtest/dosbox.lock` in the background, held by a file).
- `loadsave.sh fountain-user`: the window 320x240; `buildcheck.py` OK (DSCLOG unchanged on the
  branch); `guard_start.sh` and a Monitor on `guard.log`.
- The rules words read with a scratch script (`live.py` exec'd; `hdr + 170`, `hdr + 270`), as
  `setmem.py` reads `rules_hi`.
- `boxclick.sh` past Pehtucl's speech: the fight, Lex's turn. `spellsetup.py 0=9 hp=200 18`,
  `hp.py 150`. L (the panel), L again, Tab (the ring), U, LEVEL (196,171) to page 2, Acid Arrow's
  icon (176,59), a click on the Templar (238,128): the attack line above.
- `toturn.sh 0` played the round: the hide, move-silently and specialized lines above.
- Seneca's skills both ways from `GameData.thief_skill_parts` with the rules word, the thief bit
  cleared in the script only.
- DOSBox, the dice log, the watchdog and Xvfb stopped by pid; the lock let go.
- Then `docs/options.png` retaken from `python3.12 -m dsloader view` on Xvfb `:56` (1400x2400):
  settings.json with `options_open` listing every section, `xdotool windowsize` 1320x2300, the
  Options tab (1061,132), cropped x 608-1314 from y 116 to under Restore defaults (706x1536),
  256 colours. settings.json removed afterwards (there was none before).
- Water: no new area.
