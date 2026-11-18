# What we can give OpenDS back: drafts (2026-11-17)

Nothing here has been sent. Each item is a draft for an issue at github.com/VirInvictus/opends (their
CONTRIBUTING asks for issues first, and the beta QA packet asks for `beta QA: <site> <pass/fail>`). The
owner decides what is posted, and from which account.

**Rules for what goes out.** Facts, offsets and observations only: they are ours to give, and OpenDS
already takes that form (its CREDITS "facts cited" rows). No game data, no walkthrough text or link (the
private installation-files repository stays private), no personal details. **No code**: this repository is
GPL-3.0 and OpenDS's tools are MIT, so code can't be copied across unless the owner says so; a design
described in words is fine.

Ordered by how much it is worth to them.

## 1. Beta QA for site G (the sewer grate), the first runtime result they have

Their packet says nobody has run these. We have, with our Loader's own bytes at the same sites
(GPL 137 at A65h, A14h, 9E0h, B5Ch), not their zip, on GOG 1.10, in DOSBox:

- **(a) offered:** with a weapon in hand the grate's menu offers "Hack the lock off": **pass**
  (`playtest/logs/2026-11-01-sewer-grate.md`, `2026-11-11-grate.md`).
- **(b) a successful hack opens it:** "<name> successfully hacks the lock off with his Bow. The grate
  opens.": **pass**, the grate opened.
- **(c) the attack roll: not tried by us.** (The rip-open path, the roll their fix copies, was seen:
  "hurts his hand trying to open the grate. It's still locked.", -3 HP.)
- **New, for their fix:** the weapon the game *names* is wrong. With an Axe in the weapon hand the line named
  the **Bow** ("...with his Bow", and on a failed hack "Cromwell's Bow rings off the grate"). Cause, from
  reading memory: command 49h copies each carried item into one scratch object; on a match the game names
  it, then goes round the loop once more, and that step copies the *next* item over it. Flipping the offer
  gate (their A65h edit) alone exposes this, since the hack was never reachable before. Our repair leaves
  the loop on the find (a jump to the loop's return at A96h). QA step to add to (b): "the weapon named is the
  one in hand".
- **Also seen, and not in their fix:** a failed hack says the weapon breaks and keeps it. We changed it: a
  weapon that can break (as in a fight) is taken, a metal or magic one "rings off the grate, unharmed"
  (our detour at A31h). Observed: "Cromwell's Axe rings off the grate, unharmed."
- **Our departure to tell them about:** we offer the hack only for a melee weapon in either hand (not a bow,
  sling, chatkcha or shield): a choice of ours, kept off their list.

## 2. Corrections to four of their triage rows (docs/ds1-sweep-triage-2026-10-07.md)

Each checked against `GPLDATA.GFF` of the GOG 1.10 install.

- **3.2(11) Keldar / Dagolar: the reading is wrong.** They say the reveal clones Dagolar at the party's
  tile (GPL 48 at 393h, 442h, 47Eh). `137/33`, `137/34` are the square of the object the preceding `09`
  (locate) found, here `09 137/39`, the creature the blow was aimed at. The script removes it (`5E`) and puts
  Dagolar in its place: the disguise reveal ("Foolish guards! You have foiled my deception!", "Dagolar
  turns to you."). 47Eh and 48Fh are already fixed-tile clones at (16, 24). Evidence for the field meaning:
  the same pair after a `09` in GPL 21 (the actor's square) and in elvenleader-type scripts. The row's
  "FIX-CANDIDATE" should read "not a bug in this respect"; the "sometimes" is the x < 22, y < 34 test at 118h
  and 201h.
- **3.2(2) Alhena:** flag 123 is not a story flag. It is the wagon train's alarm: set only by GPL 21 entry
  650 (28Ah), called from GPL 21 (51h, 254h, 25Dh), GPL 24 (428h) and GPL 28 (480h, after "You were told to
  leave!"); it also makes object -105 three times and calls routines on the camp's people. Read only by
  GPL 21 to 36 (the whole wagon train) and MAS 26 (region 26). No other camp sets or reads it. Alhena's absence
  after the alarm is the game's, so the "needs control-flow edit" candidate would put her in a camp that has
  turned on the party. (Static only.)
- **3.2(10) Hound Necklace:** the 1000 damage (GPL 55 at 1C6h) follows the script's own text, "The necklace you
  are wearing glows! The prisoner's life force drains away.": deliberate, so not a fix candidate.
- **3.2(6) Elven slavers' leader: the site is 4FAh, not 58Dh.** The first menu ("Who are you?", called from
  313h) has "Sorry to bother you. Goodbye." to 898h (the arrest); its other three replies return to the caller.
  The menu at 58Dh has two replies to 898h ("Ally against Draj!", "You're mistaken. I've never been in Draj.")
  that may be meant. 898h ends in "Do you consent to go?": yes is captured, no is a fight (call of script 94
  entry 1). Our repair: Goodbye to 583h, the routine's own return (same length). Medium confidence.

## 3. An engine fact their detour/grow path needs: the script buffer

The game reads each script into one buffer allocated as `push dword 10000` (DS1 file offset 6A692h), and a
script called from another is read in over it. We measured: a script of 9,800 bytes ran; one of 10,000 ended
with "BAD GPL EXIT". The largest shipped scripts are GPL 2 (9,792), GPL 7 (9,762) and GPL 72 (9,751), so
they can grow by about 208, 238 and 249 bytes at most. Their detour and chunk-growth design
(docs/detour-repairs.md) and the applier's growth check should carry this limit (we enlarge the buffer to
11,776 with a patch, so scripts of ours go beyond; a plain darkfix can't). We found no mention of it in their
docs.

## 4. Cross-check of their overlay documentation, from an independent implementation

Our recompile (`darksun-recompiled`) loads every overlay by the format in their docs/overlay-formats.md
(segment table from the exeinfo block, per-module relocation words replaced by segtab segments, stubs rewritten
from `INT 3Fh` to `JMP FAR`). On the GOG 1.10 files: DS1 **52 modules, 935 stubs**; DS2 **49 modules, 854
stubs**; the build refuses marker-form relocations as theirs do. DS1's 52 matches their Ghidra script's 52
blocks. It plays the intro, menu and the arena's scripted fight, which would not work if the format were
wrong. Their module index in `syms/*.toml` is the same index (checked on `save_game_to_disk`, ovr13+7CCh: its
string push at file 6146Ch falls inside module 13).

## 5. Feedback on their symbol catalogue (`tools/ovr-map/syms/ds1.toml`), from naming a lifted program with it

Mapped onto our image, all 142 DS1 rows land inside their segment; 138 start at a function (a Borland frame,
`inc bp` + frame for far functions, or a frameless start after a return). The four that don't, by byte
pattern, are `gpl_handler_longdivideequal` (resident A2ECh), `gpl_handler_sourcetrace` (A953h),
`gpl_handler_passtime` (AB68h) and `gpl_opcode_dispatch` (99C5h: `shl ax,1 / mov bx,ax`, mid-function, so a
label, not an entry). For DS2 the catalogue mixes data labels (`gmel_*`) into the function table; a `kind`
field would help consumers. The mapping we use: resident row, linear = load segment x 16 + file offset - MZ
header size; overlay row, linear = the module's load segment x 16 + offset, with the module index as their
segment number.

## 6. Our fixed-bug list as input to their catalogue (the bigger give-back)

Going through `GAME-BUGS.md` row by row against their docs (`reports/opends-bug-comparison-2026-11-18.md`)
shows 66 rows, of which about 38 are absent from their catalogue and six answer an open row of theirs with a
mechanism and a fix: random monsters' divide error (a crash with an address), the 300
picture slots, ability items counting anywhere carried, the gladiator's AC, the fire elementals' swapped classes
and Psionic Blast. This is likely worth more to them than items 1 to 5; send it first.

## 7. Offers, if they want them

- **Our verification status of the engine-bug catalog they relay** (their community-crossread §1, "pending our own
  verification"): seen in play with the dice log: ability items counted only when worn and the gladiator's
  armour-less bonus (`playtest/logs/2026-11-02-dsun-fixes.md`). The others (Mirror Image, the armour charge,
  Share Strength, the preserver's Dispel, thri-kreen claws, Scare, the acid check) are fixed in the Loader; a
  per-item list of what has a play log would take a pass over `playtest/logs/` (not done).
- **The Legcrusher guards** they can't ship without a "movable assembly" mode: we wrote our own version
  (`kurzak.py`: Kurzak and Dinos notice Legcrusher is gone, with our own lines). The method, no code: append the
  new commands after the script's end after an exit, replace the site with a jump there and pad the rest with
  exits, end the appended block with a jump back, and add the block's start to every address written inside it
  (`relocate` offsets). They have this as "detours"; what ours adds is a label-based builder for the block.
- **Play-test recipes** (xdotool under Xvfb, the 320x240 window, dice-log reading, memory edits that never
  get saved): `playtest/PLAYTESTING.md`, for their `repro` harness if they want a second opinion.
