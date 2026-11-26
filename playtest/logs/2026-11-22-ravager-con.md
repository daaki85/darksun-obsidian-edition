# Test log: CON as in AD&D, Wake of the Ravager (2026-11-22)

Under test: SL's CON as in AD&D (game.RULE_CON, always on in SL; DSCLOG's REGEN_SITE and CON_SAVE) in
DSCLOG2: REGEN_SITE (site 35, `regen_rate` at 26599h) and CON_SAVE (site 36, `con_save` at 1D36Bh).
RULE_CON added to ravager.RULES_PORTED; the dice log's save modifiers now drop CON's adjustment for a
dwarf or halfling only with the rule (SL: always on, so unchanged there).

## Found first

- Regeneration is SL's routine at 264BFh (SL's 227E5h): once the clock (3C13h:35Bh) is more than 300
  s past the last (DS:19B8h), each Okay member gets a psionic point per 300 s and, with CON (the
  creature's +1Bh) 20 or more, a hit point per 300 s, at most its most (sheet +8). The site is the
  second `div ebx`'s `mov dx,cx / imul dx,dx,31h`.
- CON's save adjustment is 1D35Bh (`push 2 / push [bp+6] / call` the ability getter, then `mov
  bx,ax / mov al,[bx+880h]`: DS:880h, SL's 810h + 70h). Its callers: the save modifiers (83A81h, for
  the paralysis/poison/death save, kind 1, after a dwarf's or halfling's CON x 2 / 7) and 8E092h
  (the same, a poison check). Its argument is a thing (3F49h:C33h, 3 bytes: kind 2 a creature),
  DSCLOG2's FIGHTER_CREATURE. Hold Person's save is the spell save: it never reaches this.

## In the game (the Loader, the dice log on; about 20:15-20:45 UTC)

Test edits, DOSBox stopped after each, nothing saved.

### Regeneration (ravload.sh ravager-roost)

Gerakis (CON 22) set to 50 HP and the regeneration's last time (DS:19B8h) put 3600 s back.

- **The rule on** (rules_hi F62Eh): at once **51** HP (3,640 s: one hit point each (26 - 22) x 600 =
  2,400 s, 1,240 kept for next time); REGEN_SITE counted 1.
- **Control, the rule off** (F22Eh, the same edit): **62** HP (3,631 s / 300 = 12, the game's).

### A dwarf's poison save (ravhold.sh, the Draxans' ambush)

The four Draxans made dwarves (their sheets' race +12h 2) with CON 20 (sheet +17h, creature +1Bh;
DS:880h + 20 is +1). Class restrictions turned off (rules 4804h) so Ar'anda could cast in her armour;
Stinking Cloud taught (`ravknow.py 22`), cast on the Draxans from USE level 2 (213, 60).

- **The rule on**: "Draxan's saving throw vs Stinking Cloud (paralysis/poison/death)": d20 11, total
  **16** (+5: CON 20 x 2 / 7 alone); CON_SAVE counted 1. Thy'rokh (a thri-kreen, CON 19) in the cloud:
  d20 4, total 5 (+1, his CON's adjustment kept).
- **Control, the rule off** (rules_hi F22Eh), the next cast: d20 17, total **23**; d20 12, total **18**
  (+6: the racial +5 and CON's +1). CON_SAVE counted nothing more.
- On the way: an Escape with nothing open brought EXIT GAME (CANCEL at game 120, 117).
- Water: nothing new.

Result: CON as in AD&D works in the sequel as in Shattered Lands.
