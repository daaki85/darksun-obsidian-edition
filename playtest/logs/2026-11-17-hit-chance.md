# The chance to hit before the swing, against the swings (2026-11-17)

Under test: `dsloader/hitchance.py`: with an enemy chosen with Tab, the dice log's `Chosen with
Tab` line and the combat log's header say what the member whose turn it is must roll to hit it.
Each prediction is held against the dice log's own line for the attack that followed (`needs N+`,
the game's THAC0 and AC as DSCLOG recorded them). DOSBox 0.74-3 on Linux, the dice log without the
window (`start.sh`), save `fountain-user` (the ambush: a Templar, Arena Guards, a Guard; nobody
held), the rules as the Loader's defaults. Tools: `tabhit.sh` (Tab, the line, Return, the attack's
lines) and `hitcheck.py` (what a number is made of), both new in the kit.

The party: Lex (fighter/preserver: bone short sword, bow, specialized), Jenna (ranger, a Stalker:
two long swords, bow; she hides), Ester (fighter/cleric, a Battle Dancer: two bone long swords,
bow), Seneca (thief, a Poisoner: Shadowseeker +1 and Hayneedle +1, sling; she hides).

## First session: the code as first written

| Attacker, weapon | Target | Predicted | The swing | |
|---|---|---|---|---|
| Lex, bone short sword (walked up) | Templar, not attacked yet | 11+ | 12+ (THAC0 16, AC 4) | **1 off** |
| Seneca hidden, Hayneedle +1 | Templar | 9+ from behind | 7+ BACKSTAB (THAC0 12, AC 5) | **2 off** |
| Seneca hidden, Shadowseeker +1 | Templar | 6+ a backstab | 12+ from behind (THAC0 17, AC 5), twice | **6 off** |
| Ester, bone long sword (stumbled dance, -1) | Templar, attacked | 13+ | 13+ (THAC0 17, AC 4), three swings | same |
| Jenna hidden, obsidian long sword | Templar | 10+ from behind | 10+ from behind (THAC0 15, AC 5) | same |
| Jenna, bone long sword | Guard, not attacked yet | 6+ | 6+ (THAC0 16, AC 10), twice | same |
| Jenna, obsidian long sword | Guard | 7+ | 7+ (THAC0 17, AC 10) | same |
| Lex, bone short sword | Guard | 6+ | 6+ (THAC0 16, AC 10) | same |
| Seneca (not hidden), Hayneedle +1 | Guard | 6+ | 6+ (THAC0 16, AC 10) | same |
| Seneca (not hidden), Shadowseeker +1 | Guard | 5+ | 5+ (THAC0 15, AC 10) | same |

What the three misses were, and what was changed:

1. **The Templar wears a Ring of Protection +1.** DSCLOG's `PROBE_RING_AC` has the game count a
   ring's plus; `GameData.attack_ac` didn't. Now it does (every ring's, or with AD&D's protection
   rule the better one's and none over magical armour). From the second attack on, the first
   session's Loader had it right anyway: the dice log keeps what the game's AC was above the
   Loader's count (`ac_gap`), which is how Ester's and Jenna's numbers on the Templar agreed.
2. **The game swings the weapons in the order of the creature's item list**, not the right hand
   first: Seneca's Hayneedle (left hand) before her Shadowseeker, Jenna's obsidian sword before
   her bone one. The first swung is the backstab. `WeaponHit.order` now carries the place.
3. **A hidden thief's second weapon is 2 worse than a plain swing.** The attack set clears its
   from-behind and backstab flags once, at its start; DSCLOG's hidden bit is used up by the first
   weapon. For the second weapon the game lowers THAC0 by nothing (by the target's facing Seneca
   was in front) but the flags are still up, so the AC is the one from behind (no shield: 5), the
   log says "from behind", and DSCLOG's `STAB_FIRST`, seeing the backstab flag on a later attack
   of the round, adds back a backstab's 2 that this swing never had: THAC0 17 where her plain
   swing is 15. `predict` now gives what the game does; the 2 is a fault of the helper's to look at.

## Second session: after the three changes (the game loaded again)

| Attacker, weapon | Target | Predicted | The swing | |
|---|---|---|---|---|
| Lex, wooden bow (the attack pointer, a click on the figure) | Templar, not attacked yet | 9+ | 9+ (THAC0 13, AC 4), three shots | same |
| (Lex, bone short sword, not swung) | Templar | 12+ | (12+ in the first session) | same |
| Seneca hidden, Hayneedle +1 | Templar | 7+ a backstab | 7+ BACKSTAB (THAC0 12, AC 5) | same |
| Seneca hidden, Shadowseeker +1 | Templar | 12+ from behind | 12+ from behind (THAC0 17, AC 5), twice | same |
| Jenna, obsidian long sword | Templar | 13+ | 13+ (AC 4) | same |
| Jenna, bone long sword | Templar | 12+ | 12+ (AC 4), twice | same |
| Ester, bone long sword (dancing, +1) | Guard, not attacked yet | 5+ | 5+ (THAC0 15, AC 10), twice | same |

The line as it read: `Chosen with Tab: Templar (32 HP), Bone Hayneedle +1 needs 7+ (70%) a
backstab; Metal Shadowseeker +1 needs 12+ (45%) from behind; Leather Sling needs 8+ (65%) unseen -
Enter attacks it`. The header with the Templar chosen on Lex's turn: `Needs 11+ (50%)` (first
session; a grab of the panel was looked at), the round's line back when the turn passed.

No error in the dice log in either session.

## Also seen

- `DS:01F8h` is 1 in the fight (the game's eight directions); the Templar's facing byte read 5
  (south-west) after Lex, south-west of it, attacked first, and nothing (FFh) before.
- With the target facing a way already and the member farther off, the line gave both numbers
  (`Bone Long Sword needs 13+ (40%), from behind 10+ (55%)`); the swing that followed was from
  the front, 13+.
- Two bone long swords with the same numbers were listed twice on the line (Ester): now once.
- Tab scrolls the view to the chosen enemy; `state.py`'s camera doesn't show it (DSCLOG's pan), so
  a click worked out from the camera misses. A grab shows where the figure is.
- A click on bare floor with the walk arrow, made to move the pointer off the panel, walked Lex
  (Move 12 to 8). Use `xdotool mousemove`, not a click.
- `hitcheck.py` is not the session's Loader: it has no dance, no Wild Fighting and no AC gap, so
  Ester's THAC0 read 16 there while the Loader (and the game) had 17 with her stumbled dance.

## Not seen

- A melee attack from behind by the target's facing with the attacker already next to it (the
  line's `from behind` without hiding), and a backstab that way.
- A held target's `hits whatever the roll`, a target with Blur, Fogbolt or the Golden Girdle of
  Urnst, a Girdle of Back Defense, an invisible target, any of the armour spells on an enemy.
- An enemy with a kit's AC, a cloak of protection, bracers or the Boots of Speed before its first
  attack (the dice log's gap covers them from the second on; only the gap's working was seen, on
  the Templar's ring).
- A member with only a bow next to an enemy (fists), and a bow out of range.
- The header's other forms (`Behind:`, `Backstab:`, `14+ 35%, behind 10+`, `Hits (Paralyzed)`):
  tested for width against the game's font, not looked at in the game.
- The Options tab's switch on a real window in the game (the window's tests pass).

## Water

No new area: the fountain's ambush, in the slave pens.
