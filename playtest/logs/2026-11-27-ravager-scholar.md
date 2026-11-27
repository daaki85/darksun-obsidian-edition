# The Scholar kit in Wake of the Ravager, 2026-11-27

**Under test**: the Scholar's part in the sequel (DSCLOG2's SCHOLAR_THAC0, site 248 at 953A1h;
SCHOLAR_LEVEL_UP on site 210; CR_SCHOLAR in the creation spells). Branch `claude/sequel-scholar`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session; the sequel from `ravload.sh` with the Loader's
copies, the dice log by `ravdice.py`. Memory edits were made for the test only and nothing was saved.

**Steps and what was seen**

1. **THAC0 at a level up.** A human preserver set to 5th level, one XP short of 6th, and made a Scholar
   (`ravkits.py set`, `ravlevel.py set`; test edits). Equipping something does not rewrite THAC0 in the
   sequel: it is written only when a character is made and at a level up. So the level up came in a fight
   (`2026-11-26-ravager-new-spells-run.sh`, Computer Control on all four, then Escape). Escape once brought
   EXIT GAME; CANCEL (120,117) and the Computer Control clicks again. After the fight the member's THAC0
   was 20 (the preserver's 19 at 6th, one worse), and `scholar_thac0s` was 1.
2. **One more spell at the level up.** The same level up brought CHOOSE A SPELL twice. The second window
   had one spell fewer (the first pick gone). `scholar_picks` read 0 while the second window was up and 1
   after the pick: it counts when the window closes. The game carried on as usual afterwards.
3. **A new Scholar.** CREATE CHARACTERS, a human preserver, the Scholar kit, DONE. The new member is
   7th level: `scholar_made` was 7 and `cr_left` 17, and 17 CHOOSE A SPELL windows came up and were
   picked. On View Character the THAC0 was 19 (a 7th-level preserver's 18, one worse), `scholar_thac0s` 1.
4. **Seen, not changed**: the creation screen's own THAC0 line (PROBE_CR_HP) shows the preserver's 18,
   without the kit. That line has no kits in the sequel yet, so it goes on RAVAGER.md's gap list with the
   DAM lines.

**Result**: a Scholar in the sequel has its THAC0 one worse, one more spell at each preserver level up, and
one more for each level when made new, as in Shattered Lands. Every DOSBox and dice log of this test was
closed by pid.
