# OpenDS cross-read, 2026-11-16

What the OpenDS project (`VirInvictus/opends`, read at `fe35c52`, 2026-11-13) has that we can use,
checked against our current scripts (`GPLDATA.GFF` of the GOG 1.10 install; read with
`dsloader/gpl.py`). Offsets are script offsets, as in `scriptfixes.py`. Nothing here is played
in the game yet: "confirmed" means the bytes and the structure are in our data as OpenDS says.

## 1. What we already have from them

Their and Calvin Rodo's script repairs (halfling race, ranger tracking, sewer grate, serf, messenger
trigger, Mindhome award, Legcrusher guards, Linara, hermit/ranger, the Darkhold dead triggers), the
Trustee, and the engine-bug catalog they relayed *from* us (OpenDS records it as unverified). Nothing to
take there.

**Correction (2026-11-17, second check):** the four are already decided, and with reasons. Commit
`7cfeee6` (2026-11-01, "Script repairs from yuan-ti v0.1.52") says, in the CHANGELOG entry it added:
"Looked at and left: the Mindhome's 'Have you killed the spiders yet?' while they live (their own lines
want them dead in every case), the Hound Necklace killing prisoners (its scripted effect), Alhena
(there unless the caravan was made hostile), the army count (a failure marker never lowers it)."
So Alhena's exit on GF123 is the game's way of saying the party made the caravan hostile; OpenDS's
"every normal endgame has GF123 set" is what that session judged wrong, and my section 3.1 below
repeated their reading without checking what sets the flag. The walkthrough (kibbitz) also tells the
player to take the Hound Necklaces off before talking to the prisoners, so that one is a known hazard
with a known workaround, and it says the Keldar fight "sometimes triggers Dagolar and his ten
slimes". My first correction missed all this because I only searched the working tree; the reasons
are in git history (`git log -S`).

Still not in any file, commit or branch (searched all of them): the elven leader's "Goodbye" going to the
arrest (4FAh), and the Dagolar clone sites in GPL 48 as a *repair*. The Keldar one is arguably covered by
the walkthrough's "sometimes", so treat both as unconfirmed bugs, not gaps.

## 2. Checklist: their rows we do not have yet

From `docs/ds1-sweep-triage-2026-10-07.md` (their numbering). "In GAME-BUGS" = a keyword search of our
docs found it described; the four marked **traced** are section 3.

| Row | Bug | In GAME-BUGS | Status |
|---|---|---|---|
| 3.2(2) | Alhena never appears at the campfire (post-war) | looked at and left (CHANGELOG) | **traced**, confirmed; the decision stands unless the user reopens it |
| 3.2(6) | Elven slaver leader: "Goodbye" goes to the slave pen | no | **traced**, confirmed, site differs from theirs |
| 3.2(10) | Hound Necklace kills the prisoner outright | looked at and left (CHANGELOG) | **traced**, confirmed; decision stands |
| 3.2(11) | Keldar fight clones Dagolar at the party's tile | no | **traced**, confirmed, one site of theirs wrong |
| 3.2(8) | Swiftbite chest wiped by the Teaquetzl alliance rewards (rewards cloned at fixed tiles, GPL-183@0xe3e, GPL-184) | no | not traced |
| 3.2(9) | Wyrm Temple Magera spawner clones at the party's arrival tile, second counter GPL-162@0xde5 | no | not traced (they want a runtime capture) |
| 3.2(14) | Slaver-camp alarm is one global flag pair (GF20 / gnum91, GPL-137@0x1084) | partly (Pehtucl's ambush is ours, a different site) | not traced |
| 3.2(4) | Mindhome re-ask half: GPL-204@0xb2/0xd2 never reads GF695 | award half fixed; re-ask looked at and left (CHANGELOG) | decision stands |
| 3.1(5) | Final battle: a stage cleared too fast breaks the next | left out on purpose (see DEVELOPMENT-CONTENT) | nothing to do: the game clock makes the gate wait its window |
| 3.1(6) | "Army still gathering": failure flags 179/182 never cleared | looked at and left (CHANGELOG, "the army count") | they decline to patch (it invents behaviour); same for us unless wanted |

Rows they close as engine-side or "no static site" (messenger's scroll, ally leaving early, enemies not
loading, ghost slot, save mid-event, stat gear while carried) need nothing from us; the engine-side ones
are in the Loader's memory fixes or out of reach.

## 3. The four traces

### 3.1 Alhena never appears (GPL 28, GPL 21, GPL 62)

**Outcome (2026-11-17): not a bug, repair taken out.** Flag 123 is the wagon train's alarm: set only by
GPL 21 entry 650 (28Ah), called from GPL 21, 24 and 28 (480h, after "You were told to leave!"), read
only by GPL 21 to 36 (the whole wagon train) and MAS 26 (region 26). No other camp sets or reads it.
Details in the CHANGELOG's Unreleased entry. The trace below is left as written.

Structure confirmed (but see the correction: the game's intent is that Alhena is absent when the caravan was made hostile, so this is probably not a bug). GF123 (`gflag 123`) is set in one place, GPL 21 at 28Ah (`16 1 gflag123`, behind a test at 278h
that exits when it is already set), and cleared nowhere (a sweep of every script for writes to it finds
only that one). GF138 is set in one place, GPL 62 at 1685h (their "after the final battle"). GPL 28 at
298h tests `GF123 == 1` and exits; everything after it, including the GF138 test at 2C2h and the
registrations of handler 51Ch (1308) at 340h and 37Ch, comes after that exit (no jump lands between
299h and 2A1h). Handler 51Ch is where Alhena (object -212) is cloned, at 52Ah, only when GF138 is set.
So once the raid flag is set, the post-war branch can't be reached through this path.

Not established: where this entry begins, and whether the game reaches 51Ch another way. 51Ch is
registered only from GPL 28 itself (340h, 37Ch), so I found no other way in. A play check is needed:
finish the war with the raid flag set (any normal game) and see whether Alhena is at the camp.

Proposed repair (theirs, needs control-flow editing): make the exit at 298h conditional on `GF138 == 0`
too, i.e. `GF123 == 1 and GF138 == 0`. That is a longer test, so it goes through `scriptfixes.py`'s
detour path (a new test expression, then back). Then Alhena's trigger is registered and she spawns.
Open question for the user: she is meant to appear; I haven't looked at what she says.

### 3.2 Elven slaver leader (GPL 46)

**Outcome (2026-11-17): kept, reworded.** The first menu is called from 313h; its other three replies return
to the caller (the templar's accusation, then the second menu); Goodbye alone jumped to the arrest. The repair
makes it return too: it does not "end the talk". Medium confidence: the shape of the script, not proof.

Confirmed, but **at a different menu than OpenDS names**. They say three replies of the menu at 58Dh go to
898h (2200), the "Guards! Take these strangers to the slave pen!" scene. In our file:

- The menu at **4FAh** ("Who are you?", asked of the leader) has "Join us against Draj!" (to 637h),
  "I want to hire on with you." (to 6C2h), "I wanted to purchase some slaves." (to 756h) and
  **"Sorry to bother you. Goodbye." (to 898h)**. That last one is the wrong branch the report means:
  saying goodbye gets the party arrested.
- The menu at **58Dh** has "No! Kill the templar and side against Draj!" (to 927h), "No! Ally against
  Draj!" (to 898h, only offered if the party has the flag 142.0) and "You're mistaken. I've never been in
  Draj." (to 898h), and "You're going to die for that, templar!" (to B30h). Two of its replies reaching
  the arrest may be intended (he thinks they are Draj's templars); that menu is arguably not a bug.
- 898h says the guards line, then asks "Do you consent to go?" (a yes/no at 8E5h). I did not follow the
  "no" path to the end.

Proposed repair: repoint only the goodbye at 4FAh to an exit. A same-length edit of its goto word.
Need the target: an existing `exit` or the end of this conversation's loop in GPL 46; I haven't picked
one. Our `elvenleader.py` edits this script after the fight (the cloak), not this menu, so the two
don't touch.

### 3.3 Hound Necklace (GPL 55)

**Outcome (2026-11-17): deliberate; repair taken out.** The 1000 damage follows the script's own "The necklace
you are wearing glows! The prisoner's life force drains away.", and the walkthrough says to take the
necklaces off before talking to the prisoners.

Confirmed as OpenDS describes. At 155h a search of the party for item 2019 worn (`... -2019 ... 8`), and if
found, 16Eh prints "The necklace you are wearing glows! The prisoner's life force drains away.", then
at **1C6h** `0B (var 137,39) (n 1000)` (their "p damage": 1000 points to the prisoner, object 137/39),
and goes on. No condition on anything but wearing the necklace, so a prisoner dies whatever his
hit points. The repair is the immediate 1000 (3E8h) to a smaller number. It is a balance change, so it
would get a switch (our Rules tab), off by default, like our other balance rules. Their word
"prisoners": I did not check which prisoners the script serves.

### 3.4 Keldar fight drags in Dagolar (GPL 48)

**Outcome (2026-11-17): OpenDS misread it; repair taken out.** `137/33` and `137/34` are the square of the
object the preceding `09` located (`09 137/39`: the creature the blow was aimed at), not the party's. The
script removes that creature and puts Dagolar in its place: the disguise reveal. See the CHANGELOG. The
trace below is left as written, including its wrong reading.

Confirmed, with a correction. Dagolar (object -26) is cloned at four sites: 393h and 442h at the
party's own tile (`137/33`, `137/34`), and 47Eh and 48Fh at the fixed tile (16,24). OpenDS lists
**47Eh** among the three "at the party's tile" sites; in our file it is already a fixed tile, so only
**393h and 442h** need repointing to `(16,24)` (immediates 16 and 24 in place of the two variables: a
same-length edit is not possible, `8F 10`/`8F 18` and the 2-byte variable words differ, so it is a
detour or a re-encoding). The ten slimes are cloned at (16,26) at AFDh and 138Ah, as they say. I did not
look at what happens in the sanctum at (16,24) (walls, or a party tile), so a play check is needed
before shipping.

## 4. Recommended order

1. The two that are really open: the elven leader's goodbye (4FAh) and Keldar/Dagolar (393h, 442h; look
   at the map at (16,24) first).
2. Alhena, Hound Necklace, Mindhome re-ask, army count: already looked at and left; reopen only if the
   reason for leaving them no longer holds.
3. Swiftbite, Magera and the slaver-camp alarm are untraced; trace only if wanted.

## 5. For the recompile

`tools/syms.py` (darksun-recompiled) names lifted functions from `tools/ovr-map/syms/<game>.toml`. See
that repository's `docs/DESIGN.md`. Besides names, `docs/dispatch-table-ds1.md`, `docs/dsun-exe-re.md` and
`docs/engine-quirks.md` in OpenDS are the readings of the same code the recompile lifts.

## 6. The changelog's account (2026-11-17)

What the CHANGELOG's Unreleased section said of the repairs tried from this cross-read, moved here
when the CHANGELOG was shortened (the CHANGELOG keeps a line for the elven leader's repair, the one
that stayed).

- **One more script repair, from OpenDS's triage; three others tried and left out** (`dsloader/scriptfixes.py`, tests
  `OpenDSTriageTests`; each site checked in the game's file, **none seen in play yet**):
  - The elven slavers' leader (script 46): his first menu ("Who are you?", called at 313h) has four replies:
    "Join us", "hire on" and "purchase slaves" return to the caller, which has the templar accuse the party
    ("These slaves escaped from the slave pens in Draj!") and puts the second menu (58Dh); "Sorry to bother
    you. Goodbye." alone jumped to the arrest ("Guards! Take these strangers to the slave pen!", then "Do you
    consent to go?": yes is captured, no is a fight), skipping the accusation. Now it returns to the caller
    as the others do (583h, the routine's own return), so the accusation and the second menu follow; the
    second menu's replies that reach the arrest are the game's. A judgement from the script's shape, not
    proof of what the authors meant: the least certain of the repairs here.
  - **Alhena: tried and taken out again.** A repair made her arrive after a raid (script 28 at 298h tested
    flag 123 and flag 138); it is not in. Flag 123 is the wagon train's alarm, not a story flag: it is set
    in one place only, GPL 21 at 28Ah (entry 650), which also makes object -105 three times (at the party's
    square, (50,50) and (100,85)) and calls a routine on each of the camp's people that is there. Entry 650 is
    called from GPL 21 ("Help!", "Murder! Fire!"), GPL 24 (428h) and GPL 28 itself (480h, after a guard's "You
    were told to leave!"), and entry 431h of GPL 21 is the attack trigger on five of the camp's people (GPL
    21's own, -104 in 24, -203 in 28, -205 in 30, -210 in 34). Only GPL 21 to 36, the wagon train (Jark's
    wagon, Madame Larissa, Tobrian, the wagon master, the fire circle), and MAS 26 (region 26, RGN1A) read
    it; no other camp's script does (the other scripts that seem to name GPL 21, in MAS 11, 13, 41, 42 and
    43, name it as a coordinate: their entry numbers are not commands in GPL 21). So she is not there
    once the party has been turned on by the wagon train, as 7cfeee6 had it; the flag is never cleared, so
    one alarm keeps her out for good, which may be meant. From the scripts only: not seen in play.
  - **Keldar and Dagolar: tried and taken out.** OpenDS says the reveal in script 48 makes Dagolar "at the
    party's tile" (393h, 442h: `25 -26 ... 137/33, 137/34`). It doesn't: 137/33 and 34 are the square of the
    object located by the `09` just before (as in elvenleader.py's "where 09h puts him"), here `09 137/39`,
    the creature the party's blow was aimed at, which the script removes (`5E`) and replaces with Dagolar in
    the same place ("Foolish guards! You have foiled my deception!", "Dagolar turns to you."). That is the
    game's disguise reveal, as worldgear.py says of Jake and Mow. A repair sending him to (16, 24) would have
    moved him off the creature it replaces. The clones at (16, 24) (47Eh, 48Fh) are another branch. Not a bug
    in the script; why it happens only sometimes (the walkthrough: "positioning after combat") is the x < 22,
    y < 34 test at 118h and 201h of where the creature stood.
  - **The Hound Necklaces (script 55 at 1C6h): tried and taken out.** A prisoner spoken to by a party member
    wearing one is damaged 1000: after "The necklace you are wearing glows! The prisoner's life force drains
    away." The words are the script's own and the walkthrough tells the player to take the necklaces off
    first, so the death is the game's trap, not a slip; the 5 points I tried were my own number.
  - Not done: the Mindhome's re-ask and the army count (their meaning in the scripts is unclear: no
    safe edit found), the Swiftbite chest, the Wyrm Temple Magera spawner and the slaver camp's alarm
    (OpenDS itself wants a play capture for the last two; the first moves six clone tiles whose map has
    not been checked).
- **OpenDS checked to 2026-11-13** (`fe35c52`; the check before was to 2026-11-03, `c25a547`).
  Since then it has had: `darkfix-ds1` 0.1.4 and 0.2.0-beta.1 (the six yuan-ti repairs: halfling race,
  tracking, grate, messenger, Mindhome award, serf; all in the Edition already, taken from yuan-ti, and
  its beta ships them disabled and untested), the detour design for repairs that change a script's
  length (the one `scriptfixes.py` already uses), the GPLX object-field map, a cross-read that records
  our engine-bug catalog and dice-log oracle as relayed and unverified, and `ovr-carve` 0.1.0 and
  `ovr-map` 0.4.0 (for decompiling DSUN.EXE's overlays; the recompile uses its symbol catalogue,
  `tools/syms.py` in darksun-recompiled). Taken from it now: the elven leader's goodbye. Looked into and
  left as the game has them: Alhena, Keldar and Dagolar, the Hound Necklaces (above). Not done: above.
  The triage rows are in `reports/opends-cross-read-2026-11-16.md`.
