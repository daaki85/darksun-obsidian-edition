# Test log: Rainbow Pattern's hold ended by damage, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 13, RAINBOW_HURT (SL's rainbow_pattern_damage): at the start of the routine
taking hit points off a combatant (5CBE4h, SL's 5859Ah; "mov di,[bp+6] / mov dx,[bp+8]" at 5CBECh), any
damage to a combatant Paralyzed (the sequel's 69) by Rainbow Pattern (49) ends that hold, through
608h:48h (7FB63h: the combatant and the entry's handle, its +7, as SL's 598:48h), the helper's first
far call made from a site (the way back in a frame the overlay manager can fix up, as ACID_ROUND's).
Rainbow Pattern's time (1 round a level, the record's dice) was already in the Loader's SPELL_FIXES.

## Found first

- 608h:48h (7FB63h) finds the entry by its owner and its +7 (7FF07h compares +7 with its second
  argument), calls 618h:48h for the effect, takes the entry out (7FBD3h) and works the abilities out
  again (628h:39h).

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 20:20 UTC)

Ar'anda taught Rainbow Pattern (scratch rsetup.py); the party's HP 250. The party had walked apart
from the Draxans (out of the spell's reach on screen), so the holds were put in the effects table
instead: Paralyzed by Rainbow Pattern on Draxan 26 (`eff.py 26 69 49`), Paralyzed by Hold Person on
Draxan 21 (`21 69 30`) for a control; test edits, DOSBox stopped after, nothing saved. The four under
Computer Control.

- Ar'anda's Fireball took both: "Draxan takes 60 from Fireball (Paralyzed: the most the dice can do),
  now 0/60 HP" (Draxan 21, held by Hold Person: no line, its hold left alone), then for Draxan 26
  "Draxan takes 60 damage: Rainbow Pattern's hold on it ends / Draxan takes 60 from Fireball, now
  10/70 HP". The helper's count 1. The far call came back and the fight went on (Draxan 26, charmed by
  Thy'rokh, hit another after).

## Still to do

- A real Rainbow Pattern cast (its time at the caster's level, its hold) and a blow on the held one.

Water: none new (the same street).
