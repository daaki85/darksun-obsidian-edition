# Six issue texts for OpenDS (draft, 2026-11-18)

Nothing here has been posted. Each issue stands alone and is written for github.com/VirInvictus/opends (they
ask for an issue before a PR, and record new bugs in `docs/known-bugs.md`). Facts only, in new words: this
repository is GPL-3.0 and OpenDS is MIT, so no text is copied; no game data and nothing from the private
installation-files repository goes with them.

**Checked today** (2026-11-18) against the stock GOG 1.10 DS1 `DSUN.EXE` (611,408 bytes): the bytes quoted
below are at the file offsets given. They are *not* in the Wake of the Ravager `DSUN.EXE` at those offsets.
**Credit line for each:** the Obsidian Edition (github.com/daaki85/darksun-obsidian-edition), a mod; the fix is
ours, the finding is credited where it isn't.

---

## Issue 1: DS1 random-monster encounters divide by zero in eight regions ("Divide error")

**Bug.** The random-monster request (REQUEST 8, routine at file `0x80BE4`) reads the region's record from
`MONR` 1 of `RESOURCE.GFF` (42-byte records: region, then ten {OJFF, strength} slots). It searches the slots
for the monster, then works out the count as 2 x the party's strength / the monster's strength (1 to 6). The
search leaves SI one slot past the match, so the divide uses the *next* slot's strength: the next record's first
OJFF after the tenth slot, and **0** after the last slot in records with seven or nine slots.

**Where.** `idiv word es:[bx+4]` at file `0x80CD8`, bytes `26 f7 7f 04`. With a zero divisor DOS ends the game
("Divide error"). By our reading of `MONR` 1 the regions with a short record are 6, 13, 14, 27, 39, 40, 44 and
255.

**Fix (ours).** `[bx+4]` becomes `[bx+0]` (`26 f7 7f 00`): the matched slot's own strength. Same length, in place.
The count is then worked out from the monster that comes.

**Evidence.** From reading the code and the record layout, and a fix in the Loader; **we have not hit the crash
in play**, so treat the region list as derived, not observed. This is a crash with a static anchor, which your
3.3(5) "random crashes" row says it lacks.

## Issue 2: DS1 stat-boost gear counts anywhere it is carried (your 3.3(4)): the cause and a fix

**Bug.** Items that raise or lower an ability score change it wherever the creature carries them: a ring in the
backpack counts like one worn. (Your row has "grant keyed to possession, strip keyed to slot removal"; the
mechanism is simpler.)

**Where.** The ability routine (file `0x7B758`, `80F5:2BB8`) goes through every item in the creature's list and
applies each item's ability byte (+0Fh, values FAh to FFh) with no look at its slot. The read is `mov al,
es:[bx+0Fh]` at file `0x7B8AB` (`26 8a 47 0f`).

**Fix (ours).** The read returns the byte only for an item in a worn slot (slot byte +11h below 14), else 0,
which the routine's switch passes over. (It is a hook in our helper, not an in-place patch.)

**Evidence: seen in play** (2026-11-01, dice log): a sling given +2 DEX in memory, in the worn missile slot: DEX
15 -> 17; moved to the first backpack cell: back to 15. Note: an item's +0Fh is also the spell the game casts on
the wearer as it goes on, so editing it in memory leaves a lasting effect; that is an artefact of the test.

Found by OpenDS (credited in our notes); we add the cause and a play result.

## Issue 3: DS1 gladiator AC bonus with no armour (your 3.4): the site and a fix

**Bug.** The gladiator's armour optimisation (AC 1 better for every 5 gladiator levels) is given with no armour
on; Dark Sun gives it to a gladiator wearing armour.

**Where.** The AC routine (file `0x58DD3`, `612E:2113`) takes a fifth of the gladiator level and tests a flag
word: `test word es:[bx+12h],0040h` at file `0x58F86` (`26 f7 47 12 40 00`). Your row names "0x4E0:0x7F / ovr46";
this is the test itself.

**Fix (ours).** The test answers true only when the creature also wears armour (arms, legs, head or chest; not a
shield, bracers or a robe). A hook in our helper.

**Evidence: seen in play** (2026-11-01): a 10th-level gladiator with no armour, DEX 18 (-4), was hit at target AC 6,
so no bonus; a gladiator in arm, leg and chest armour was hit at 6, and at 8 with its gladiator flag cleared in memory: the bonus (2) is given in armour. (The flag edit is a test device.)

## Issue 4: DS1 fire elementals' resistance classes are swapped against the clue book (your 3.4)

**Bug.** The lesser fire elemental should need +1 weapons and the greater +2 (the clue book); the game has them
the wrong way round: the fire elemental (kind 32) is hurt by +1 and takes nothing from fire, and the lesser one
(kind 33) needs +2 and is hurt by fire.

**Where.** The monster kinds' table of resistance classes, `3E45h:00A8h` + the kind: file `0x43918` (kind 32) and
`0x43919` (kind 33) hold `0e 0d` (14, 13). Class 14 is "+1 weapons, nothing from fire", class 13 "+2 weapons,
fire hurting". This is the "EXE-side enum record" your row mentions; the data key isn't needed.

**Fix (ours).** `0f 0e`: kind 32 gets class 15 (a class the game has that no kind used: +2, nothing from fire),
kind 33 gets 14. Two bytes, in place. (Our helper copies the table, so ours is applied there; the bytes are the
same.)

**Evidence.** Static, from the table and the classes' meaning; **not tested in play on the Lava Rifts**.

## Issue 5: DS1 Psionic Blast makes real wounds on a party member (your 3.4): the site and our fix

**Bug.** Psionic Blast on a creature that fails its save takes its hit points down to a fifth of its most; on a
party member that loss is real and stays, where the power is meant to give imagined (temporary) wounds.

**Where.** The effect routine's case 169 (file `0x796CB`, `80F5:0B2B`): the loss goes into `[BP-18h]`, the damage
routine (`0x79A01`) deals it, then `or byte [si],1` at `0x79707`. The death test in the damage routine is `cmp
ax,dx` at `0x5860B` (`612E:194B`, before a `jg` to the Out Cold case): damage reaching HP + 10 kills (status 5),
reaching HP knocks out (status 3).

**Fix (ours).** For a party member we record the loss, give it back when the fight ends (only to one still
Okay), and in the meantime a blow that would kill knocks out instead. Hooks in our helper, so not an in-place
patch; the plain description is the useful part here.

**Evidence.** From reading the code (yuan-ti's issue #129 first). **We did not see a party member blasted in
play** (no one in our test party knew the power), so the give-back text is untested against a real blast.

## Issue 6: DS1 "doorway and item graphics disappear": the 300-slot picture table (your 2.2 and 3.3(1))

**Bug.** Your 2.2 ("graphics for doorways or items vanish as the camera scrolls", deferred as a renderer
limitation) and 3.3(1) (the Gem Fields' three-gem ceiling) may be one cause.

**Where.** The game keeps every picture it loads in a table of **300 slots** and a picture store of a fixed
**741,376 bytes**. It appends a slot (and room in the store) for each picture number it doesn't already have and
gives neither back until an area loads. Once a visit has used 300 slots (many kinds of item dropped, bodies, spell
effects, new monsters), a new picture has nowhere to go and is not drawn. Our sites: slot-full test file
`0x26009`, placement `0x260CC`, count `0x2612B`. SSI's own note 2712 for Wake of the Ravager describes the same
engine limit.

**Fix (ours).** A new picture goes in a slot already out of memory that no wall or map thing names, in the first
gap of the store it fits; a search that goes round from the last slot reused (it churned when it began at slot 0).

**Evidence: seen in play** (2026-11-09): dropping items of many kinds in the slave pens filled 300 slots at the
ninth cycle; with the fix, cycles 10 to 13 reused 8, 13, 17 and 18 slots, the store's end did not grow, and the
slots checked afterwards were intact. **Not tested:** whether the Gem Fields' three-gem ceiling is this limit;
it is a hypothesis.
