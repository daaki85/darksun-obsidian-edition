# 2026-11-20: "Paralyzed ends on Templar" after an untimed hold

**The oddity**: in [the F10 real-pin play](2026-11-20-f10-real-pin.md), run 1, the dice log printed
`Paralyzed ends on Templar` after Lex's turn in round 12, though the Templar's hold was a memory
edit with no timer (`foeset.py 25 eff=34`, then `foeset.py 25 eff=44:48` for Spell Turning). In
round 13 the Templar cast Hold Person at Lex, in round 14 he hit Ester: the hold had really ended.

**Build**: branch `claude/paralyzed-ends-oddity` from `origin/obsidian-edition` 7b545bb (2.19.2).
DOSBox 0.74-3, window 320x240, `buildcheck.py` OK. `settings.json`: `autosave` false, `quick_save`
false, before `loadsave.sh`. Save `fountain-user`, `dismiss.sh` into Pehtucl's ambush. A watcher on
the effect table and the event queue's kind-7 entries (an effect's end: owner, handle, due time),
printing both at each change with the game time. Nothing saved (the `SAVQ*` files are 2026-11-19's),
DOSBox, the dice log, the watcher and the watchdog stopped by pid.

## The answer

**Rainbow Pattern caught the Templar.** A held creature fails every save without a roll, so the
log had no save line for him, and the game put Rainbow Pattern's Paralyzed on him **in place of** the
memory edit's: the effect routine (DSUN.EXE 78480h, 786D1h-786FEh) takes out a creature's record of
an effect it already has (598:4Dh) before the new one is added (76442h: at the owner's first place,
the lowest handle the owner has free, the new spell's timer as a kind-7 event). The count stays the
same; owner, caster (on the ground: the owner) and effect stay the same, so the dice log, which
compared (owner, caster, effect), saw nothing. Rainbow Pattern's time (9 rounds at level 9) ran
out at the end of round 12, and that end was real.

So the line was right, the game was right (as AD&D: the later hold rules), and the memory edit
wasn't the cause: any Paralyzed already on a creature is replaced that way. What the log got wrong,
in real play too:

- **Same owner, caster and effect** (Rainbow Pattern over another hold from the ground or of its
  own; a caster's second Hold Person on its own target): nothing said, though the hold now ends at
  another time.
- **Another caster** (Hold Person on someone held by someone else's, Rainbow Pattern over a Hold
  Person): `X gives Paralyzed to Y` and **`Paralyzed ends on Y`** in one look, though Y stays held.

Fixed in the dice log: records are told apart by their spell and handle too, and an effect started
and ended on one owner in one look is `..., in place of the one it had` with no end line.

## Run A: the two foeset.py edits alone

`foeset.py C eff=34` on every foe 17-47 (handle 200 each, charges 0, no event), `foeset.py 25
eff=44:48` (spell 48, Minor Spell Turning's number, effect 44, handle 201, charges 0), both in round
1. `passn.sh 20` and `40`: rounds 1-16, owner 25's two records unchanged throughout, no kind-7 event
for owner 25, no end line. The game doesn't end an untimed record by itself: no timer, no end.
(A charge-spending effect with 0 charges is skipped by the charge routine, 76803h, so Spell
Turning's 0 doesn't end it either.)

## Run B: the Web and Rainbow Pattern, as in run 1

The foes held, `spellsetup.py 0=9 2=9`.

- Lex, round 1: Web at the Templar (240,124). The game's Stuck went on him as a new record before
  his Paralyzed (owner 25, caster 25, spell 24, effect 51, handle 0, charges 15: 9999's low byte, no
  event), and was taken off again at t=3265 (`Stuck ends on Templar`, round 2). The Paralyzed
  untouched.
- `spellsetup.py 0=9 50`; Lex, round 3: Rainbow Pattern at the floor (145,150), `2d3 = 3`; Jenna and
  Ester failed. The Templar's record, with no save line:
  ```
  114.41 t=3266   [10] owner 25 caster 25 spell 0  eff 34 handle 200      (foeset's: no event)
  114.61 t=3266   [10] owner 25 caster 25 spell 50 eff 34 handle 0
                       event at 3806 owner 25 handle 0                   (540 s: 9 rounds)
  ```
  The dice log (2.19.2's) printed nothing for it.
- Round 4: Seneca and Lex failed their turn-start saves too: **the whole party Paralyzed, the game
  jumped its clock to the next event** (t=3326 to 3806 at once) and at 3806 ended the three holds
  due then: `Paralyzed ends on Jenna, Ester, Templar`; then `Templar's turn`, `Templar gives Afraid
  to Lex` (Cause Fear, spell 78). (The dice log also printed a `Round 1` with about 50 combatants,
  most of them `?`, at the jump: not chased.)

## Run C: the fixed dice log, both cases

`loadsave.sh fountain-user` again (start.sh runs the dice log from the branch), the foes held,
`spellsetup.py 0=9 2=9`, `0=9 50`.

- Ester, round 1: Hold Person (priest level 2, 176,79) at the Templar (240,128):
  ```
  Ester gives Paralyzed to Templar, in place of the one it had: loses its turns, can't move, fails every saving throw
     [9] owner 25 caster 2 spell 86 eff 34 handle 0       event at 4284 owner 25 handle 0
  ```
  No `Paralyzed ends on Templar` (2.19.2 would have printed it). The Hold Person pointer stayed up
  for a next target (passuntil.sh's click on a member: `can't cast Hold Person there`); RETURN TO
  GAME (266,171) and a right-click passed the turn.
- Lex, round 1: Rainbow Pattern at (145,150), every member saved:
  ```
  Paralyzed on Templar, in place of the one it had: loses its turns, can't move, fails every saving throw
     [9] owner 25 caster 25 spell 50 eff 34 handle 0      event at 3744 owner 25 handle 0
  ```
  Hold Person's event (4284) was gone with its record: **the shorter Rainbow Pattern hold (9
  rounds) replaced the longer Hold Person (18)**, so the Templar would go free 9 rounds sooner. The
  game's own rule, reported, not changed.

## Learned

- An effect put on a creature that has it already replaces the old record (its spell, handle, time;
  the old timer taken out with it): a foe held with `foeset.py`/`addeffect.py` (no timer) gets a
  timer from any later hold that reaches it, Rainbow Pattern's area included (no save line: it fails
  without a roll).
- The game's handles: the lowest free for the owner (76AE6h), a new record at the owner's first
  place (76A99h's binary search). Untimed spells' records hold 15 in their charges (9999's low byte).
- With the whole party Paralyzed the game skips to the next event at once. (Not so: it plays the
  rounds through in a blink, 60 s on the clock each; and the `Round 1` was the dice log's: [the
  next play](2026-11-20-round-one-oddity.md).)
- Water: none new (`fountain-user`, as in ROUTE.md).
