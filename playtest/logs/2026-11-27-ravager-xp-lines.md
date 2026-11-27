# Wake of the Ravager's dice log: XP lines, the prime requisites' bonus, level-ups, 2026-11-27

**Under test**: the sequel's dice log running Shattered Lands' tracker whole (`ravlog._tracker_pass`:
`tracker.PartyTracker.check`), the sequel's XP cap in it (`tracker.CAP`, `SHARE`), and the round's
initiative step taken. Branch `claude/sequel-xp-lines`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session. The fight route
(`logs/files/2026-11-26-ravager-new-spells-run.sh TAG 0 0`: the Draxans' fight up Tyr's street, every
member's HP 250, a test edit; `RAV_NO_SAVES=1`), then `c` and Computer Control on all four (47,53 98,53
47,112 98,112) and Escape. Nothing was saved.

**Steps and what was seen**

1. **First run, tracker ported but writing nothing.** After each kill: `Draxan is killed`, then `XP: Ar'Anda
   +366 (+33 for Preserver, INT 18; ...), Terrannus +1100 (+100 for Cleric, WIS 19), Thy'rokh +525 (+25 for
   Fighter, STR 19), Gerakis +1100 (+100 for Gladiator, STR 24) (for Draxan 4000)`. But the next look
   said `XP: Ar'Anda -30, Terrannus -91, ...`: the bonus taken back. The sheets showed the game's XP alone
   (Terrannus 55,000 to 58,000 for three kills). **Found**: the sequel's dice log reads through a view that
   drops every write but to the ranges a feature names (`ReadOnlyGuest.writable`): the bonus never landed.
   A sheet's XP edited by hand (`ravlevel.py set`) is taken for an award too, and given the bonus: set XP
   before the dice log attaches.
2. **Fixed**: the party's sheet XP dwords (+0) writable while the tracker runs. Second run: the same XP lines,
   no taking back, and the sheets kept the bonus: Terrannus 55,000 + 3 x 1,100 + 11,000 = 69,300.
3. **The fight's award** (`Each party member receives 10000 experience points!`, the message box clicked
   away): `XP: ... Terrannus +11000 (+1000 for Cleric, WIS 19) ...`, then `Thy'rokh's 7th Druid (fire) level:
   hit points d8 = 7 and 1, the better 7, +5 CON 19, into the total shared by 2 classes`, `Thy'rokh is now a
   7th level Druid (fire)` and `max HP 250 -> 78` (the 250 the test edit's).
4. **Seen, not changed**: each run began with `Preserver now 0/27 HP (-27)` and `Preserver is killed`, a
   creature record of that name in the fight's table at the start (the kills step said it before this
   change too). And a sheet's +4 holds a copy of its XP after an award in a fight (3,000 in the save): the
   game adds the award to both. The tracker writes +0 alone, as in Shattered Lands, and the bonus stayed
   through later awards.

**Not distinguished in play**: the initiative step. The sequel's round lines came before (at the round's
first other roll); the step only says them sooner, 0.3 s after the rolls.

**Result**: the sequel's dice log has the XP lines with the bonus, which now sticks, and the level-ups. Every
DOSBox and dice log of this test was closed by pid.
