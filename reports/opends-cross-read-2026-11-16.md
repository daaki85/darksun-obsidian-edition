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

**Correction (same day):** CHANGELOG.md (2.x, "yuan-ti's v0.1.52 repairs", about line 1472) already
records that the Mindhome's "Have you killed the spiders yet?", the Hound Necklace killing prisoners,
Alhena and the army count were *looked at and left*. My first search only covered the `.md` files in
`obsidian-edition/`, `reports/` and `research_notes/`, so it missed that entry: those four are a
decision already taken, not gaps. The CHANGELOG doesn't say why. Nothing in it or in the docs
mentions the elven leader's goodbye or the Keldar/Dagolar clones, so those two are still open.

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

Confirmed. GF123 (`gflag 123`) is set in one place, GPL 21 at 28Ah (`16 1 gflag123`, behind a test at 278h
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

Confirmed as OpenDS describes. At 155h a search of the party for item 2019 worn (`... -2019 ... 8`), and if
found, 16Eh prints "The necklace you are wearing glows! The prisoner's life force drains away.", then
at **1C6h** `0B (var 137,39) (n 1000)` (their "p damage": 1000 points to the prisoner, object 137/39),
and goes on. No condition on anything but wearing the necklace, so a prisoner dies whatever his
hit points. The repair is the immediate 1000 (3E8h) to a smaller number. It is a balance change, so it
would get a switch (our Rules tab), off by default, like our other balance rules. Their word
"prisoners": I did not check which prisoners the script serves.

### 3.4 Keldar fight drags in Dagolar (GPL 48)

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
