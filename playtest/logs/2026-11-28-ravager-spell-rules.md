# 2026-11-28: Wake of the Ravager's spells as Shattered Lands'

**Under test** (branch `claude/ravager-spell-rules`): the 6th-level priest spheres as Shattered Lands' (Blade Barrier
air, Sunstroke fire, Wall of Thorns earth), Whirlwind and Restore Youth in the sequel (Codex's work taken over), a
weapon's spell on a hit spending no charge (`hit_spends_none`), and Energy Control letting other spells through
(`energy_kinds`, both games). Water of Life and Produce Fire are checked by the tests only.

**Set-up:** `RAV_LOADER=1 ravstart.sh`, the dice log (`ravdice.py`), the talk and the walk into the Draxans' ambush,
then test edits never saved: the party's base AC -10 (sheet +21h), Terrannus made an air cleric (class 1, sheet +1Bh)
of 18th level and Thy'rokh a fire druid (7) of 18th, with three priest casts a level. The scripts:
`files/2026-11-28-ravager-rules-*.sh`, `-setup.py`, `-charges-run.sh`, `-energy-run.sh`, `files/2026-11-28-charge.py`.

**The 6th-level lists.** The air cleric's LEVEL 6 page: Whirlwind (Sand Storm's icon, tinted) and Blade Barrier, no
more (img/2026-11-28-ravager-air-cleric-6th.png). The fire druid's: five, Restore Youth (the fountain), Fire Seeds,
Heal, Harm, Sunstroke; no Blade Barrier or Wall of Thorns, which the game gave a druid of any element
(img/2026-11-28-ravager-fire-druid-6th.png).

**Whirlwind.** Cast by Terrannus at the Draxans beside the party: the funnel drawn and turning
(img/2026-11-28-ravager-whirlwind.png), 2d8 to each creature in it as cast and again at the next round's start,
half on a save, a failed save logged "is swept off its feet: loses its next turn" and the turn lost. It caught the
party too (as meant: aimed beside them) and ended the fight on its own over the next rounds.

**A weapon's charges.** Gerakis's Dragonsbane given Magic Missile (power 9) and one charge, +15 to hit. With the fix
three hits each cast Magic Missile and the charge stayed 1, the sword in his hand. The control
(`RAV_SKIP=energy_kinds,hit_spends_none`): the first hit's Magic Missile spent the charge and the sword was gone
(its record cleared, slot FFh).

**Energy Control.** Ar'anda given the power (`ravkits.py power 0 7`) and using it ("Protected vs Energy on
Ar'Anda"), her HP set to 20, then Thy'rokh's Heal on her portrait. Control (`RAV_SKIP=energy_kinds`): the Heal was
cast and she stayed at 20. With the fix: 47/48 (+27). A first try set the creature record's +9 bit 4 by hand
instead of the power: that blocked nothing even in the control, so that bit is not the protection's.

**Mishap:** Escape pressed with nothing open, then `ravfight.py` keys, quit the game (the EXIT prompt answered);
the guide's rule, broken.

**Water:** no new area.
