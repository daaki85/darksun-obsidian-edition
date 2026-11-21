# Test log: rings and cloaks of protection, and held targets, Wake of the Ravager (2026-11-21)

## Rings and cloaks of protection: nothing to port yet

- Every ring in the sequel's OBJEX.GFF (type 45, name 30h) has plus 0; their powers are spells
  (36) or the game's own effects (320 and up). The cloaks (type 28, StalkerCloak too) have plus 0
  and their type doesn't count for AC (no 80h at +0Bh). The bracers (type 20, some +1 and +3) are
  the sequel's own design.
- So SL's RULE_PROTECTION (AD&D's limits on a ring or cloak of protection worn with magical or metal
  armour or a shield) has nothing to act on. It comes with the party transfer (step 6), which brings
  SL's Ring of Protection +1 and the mod's cloak.

## Held targets: in, not yet seen in play

Under test: SL's held_hit and held_damage as DSCLOG2's HELD_HIT (INT DFh at 5D088h, SL's 589E9h) and
HELD_DAMAGE (INT E0h at 5D1B7h, SL's 58B0Dh). The sequel's attack routine has SL's code at both sites,
byte for byte. Helpless as the game has it: Paralyzed (the sequel's effect 69, its name read from the
program's list) or Out Cold (the creature's +14h 3); the combatants at (load + 3F49h):C33h, 3 bytes
each, kind 2 a creature (the AC function's own reads). The rule's switch is RULES_HI's 8000h.

Tried in the Draxans' ambush (`RAV_LOADER=1 sh ravscare.sh`, about 04:35 UTC), all by memory edits,
never saved:
- A Draxan set Out Cold (creature +14h = 3): the Loader's helpless() said "Out Cold"; the party's
  Walk pointer showed a barred sign over it, and the sword pointer's click did nothing.
- Terrannus set Out Cold: through 10 rounds the Draxans attacked only the others. **The sequel's foes
  don't attack an Out Cold party member.**
- All four Draxans given a Paralyzed record in the effects list (owner, caster, effect 69, 10): the
  game's own Paralyzed is elsewhere too (SL's effects bitset, 76944h): they went on attacking. The
  party's `ravfight.py attack` walked but never struck (the figures bunched in the street), so no
  blow on a "held" Draxan was made.
- Still to do: a real Hold (Hold Person or a monster's paralysing touch) and a blow on the held
  target, the dice log saying "hit (held)" whatever the d20 and the damage not doubled.
- No water: the street in Tyr only.

## Seen in play (later the same day, about 07:50 UTC)

`RAV_LOADER=1 sh ravhold.sh` (new: Ar'anda taught Hold Person by a test edit, never saved), the dice
log with the ported rules. Hold Person (LEVEL 3, the third icon) on the Draxan beside Terrannus: its
save d20 4 against 13, failed. Her turn then waited with the spell pointer up: a right-click on bare
floor and Q ended it. Computer Control for all four.

- The next round a Draxan struck the held Draxan twice (the sequel's foes attack their own held
  comrade): d20 14 and **d20 8 against 11+, both hits**, "Paralyzed: hit automatically, for normal
  damage"; 12 and 11 damage, 2d4 - 1 + 8 STR each, not doubled. The helper's count went to 1.
- So the rule works on a real Hold, both sides alike. A party member's blow on a held foe wasn't
  seen (the fight was stopped there).
- No water: the street in Tyr only.
