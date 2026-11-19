# Obsidian Edition in Wake of the Ravager, and taking the party across

A study (2026-11-19) of what it would take to make the mod work in *Wake of the Ravager* (WotR),
and of a simple way to carry a modded *Shattered Lands* (SL) party into it. Everything below was
measured on the GOG 1.1 releases of both games (SL `DSUN.EXE` 611,408 bytes, WotR 634,416 bytes)
and on the user's own saves in `playtest/saves/`. How to repeat each check is at the end.

## In short

- **The party transfer is close to done already.** WotR ships SSI's own transfer program,
  `CHARTRAN.EXE`. It takes a modded save without complaint (four tested, the user's kit
  parties among them). It keeps names, scores, classes, levels, XP, hit points, psionics and the
  spells it knows. It even keeps the mod's **kit** byte, which lands in a byte WotR never reads.
  It loses three things: the **weapon specializations**, the **mod's own items** (each becomes a
  money bag) and the **mod's new spells**. A small Loader step before and after CHARTRAN can fix
  all three. That is the recommended first piece of work: [the transfer](#the-transfer).
- **The mod itself does not carry over as it is.** About 450 patches to SL's program and a
  29,000-line resident helper are written against SL's exact code addresses and record layouts.
  WotR is the same engine, recompiled with different record sizes. Only about half of the patch
  sites can be found in WotR's program by byte likeness, and every one would still need
  re-checking. Porting it for DOSBox would mean doing the mod a second time, site by site.
- **The way to carry the rules is the recompiled program**, not DOSBox. Dark Sun Recompiled
  already runs WotR as far as Tyr, and runs CHARTRAN. Its Phase 7 plan ("the mod's rules shared,
  an address table per game") is the route where one rule is written once and pointed at each
  game's addresses. Until then, a WotR edition would be a short list of chosen features, not the
  whole mod: [porting the mod](#porting-the-mod).

## The transfer

### What CHARTRAN does

`CHARTRAN.EXE` (24,761 bytes, LZEXE-packed, SSI 1994) is a text-mode DOS program in WotR's
folder. It asks for the two game folders, which it calls `C:\DSUN` and `C:\RAVAGER`. It lists the
`SAVE*.SAV` files in the SL folder, and the letter pressed picks one. The party is then written
into WotR's roster, `CHARSAVE.GFF`, in free `CHAR` slots (32-35 in the install's roster), and
WotR's CREATE CHARACTER screen offers them.

It reads three files from WotR's folder: `ITEMS.BIN` (936 bytes: 234 pairs of words, an SL
object number and the WotR object to give in its place), `OBJEX.GFF` and `CHARSAVE.GFF`. Anything
missing from `ITEMS.BIN` becomes object 900, a money bag. The command line takes `DEBUG`, which
writes `DEBUG.DAT`: each item as `OLD: -<SL object>, NEW: <WotR object>`, and each spell and
psionic aptitude it could not carry (`STATS` and `NOSPELL` are its other switches, untried).

Dark Sun Recompiled already runs CHARTRAN as a third built-in program (`dsun --transfer`), with
output identical byte for byte to DOSBox's (that repository's `docs/PLAYING.md`, "Taking a party
to Wake of the Ravager").

### What a modded party keeps and loses

Measured with `playtest/chartran.sh` on `selling-junk-user` (the game's own party, played),
`trap-user` (Lex, Jenna, Ester, Seneca) and `rest-no-call-user` (Cromwell, Balthbeorn, Finster
and Cenna, all with kits):

| The mod's data | Where SL keeps it | After CHARTRAN |
|---|---|---|
| Kit (and Friends known, the own-party mark) | sheet `+43h` | **kept**, at WotR's sheet `+3Dh`. No `es:[...+3Dh]` access anywhere in WotR's program (the same scan finds none for `+43h` in SL, which the kit pages already state), so it rides along unread |
| An Elementalist's second sphere | sheet `+45h` | **kept**, at WotR's `+3Fh`, unread the same way |
| Weapon specializations | sheet `+14h` to `+17h` | **lost**: WotR's sheet has no such field, and CHARTRAN skips those four bytes |
| The mod's items (Inixhide, Ring of Protection +1, Shadowseeker, the Ring +1, Kalzith's scrolls, the new arms and armour) | new object numbers (2419-2448, 2580-2637 and so on) | **a money bag each** (object 900): no entry in `ITEMS.BIN`. Some of the game's own items go the same way (`DEBUG.DAT` lists 114 in `rest-no-call-user`'s save) |
| The new spells (Cat's Grace ... Friends, 196-201; the 6th-level priest spells, 202-211) | the helper's own table past the game's 138 | **lost**: CHARTRAN translates spells 0-137 only. WotR has 6th-level priest spells of its own, so most of the ten have a counterpart |
| Age, the creation roll kept for RECALL, the dice log | the Loader's own files and spare bytes | not part of a character in WotR; nothing to carry |

The sheet itself moves with a fixed pattern (found by aligning the bytes of each SL record with
the record written). WotR's `CHAR` record holds the creature record at `+0Ah` (its name at
`+2Bh`) and the sheet at `+45h`. The sheet is SL's with seven bytes taken out: `+00h`-`+0Dh` stay
in place, `+10h`-`+13h` move to `+0Eh`, `+18h`-`+3Bh` to `+12h` (so the class is at `+1Bh` and the
levels at `+1Eh`, as `playtest/RESEARCH.md` already had), and `+3Dh`-`+46h` to `+37h`. SL's
`+0Eh`, `+0Fh`, `+3Ch` and the four weapon-spec bytes are dropped.

### A simple way: "Take the party to Wake of the Ravager" in the Loader

The Loader already finds WotR (Options tab, **Wake of the Ravager**, for the 6th-level priest
spells' icons) and reads SL saves (`savefile.py`, `Show Save.bat`). So the simple version is one
button, on the Loader's Saves section, that does this:

1. **Pick a save** from SL's folder (the list the Loader shows already).
2. **Before CHARTRAN**, on a *copy* of the save (the original is never touched):
   - each of the mod's items is swapped for the nearest item of the game's own that `ITEMS.BIN`
     knows: the Ring of Protection +1 for the game's ring of protection, Shadowseeker for a
     magical long sword of the same plus, Inixhide for leather armour, and so on. That turns
     money bags into real gear. The table is written once, from the mod's items in `ITEMS.md`
     ("The mod's new items" and the new entries of its lists);
   - each new spell known is noted, to give back afterwards.
3. **Run CHARTRAN** on the copy, out of sight: in the DOSBox that comes with WotR's GOG release
   (as the Loader starts SL's), with Enter and the save's letter typed in, as `chartran.sh` does
   here. Or through Dark Sun Recompiled's `--transfer` where the Loader already starts that
   program.
4. **After CHARTRAN**, in the `CHARSAVE.GFF` it wrote:
   - the weapon specializations go back into the sheet's spare bytes, in the same way as the kit
     (a free run of four bytes in WotR's 42h-byte sheet; which ones still needs the same check as
     `+3Dh`: no access in WotR's code);
   - the new 6th-level priest spells known become WotR's own of the same name, where it has one;
   - a short report: who went across, what each item became, anything that became money.
5. **Back up** WotR's `CHARSAVE.GFF` first, as the Loader does SL's saves.

The kit and the specs then sit in the WotR characters unused. They come alive only if a WotR
build of the mod ever reads them, but they are not lost on the way.

**The longer-term alternative** is to leave CHARTRAN out and write the transfer in Python
(`dsloader/transfer.py`): read the SL save (done already), write WotR's `CHAR`, `CACT`, `SPST`,
`PSST` and `PSIN` chunks, with `ITEMS.BIN` read from the player's own copy plus the mod's table.
It needs neither DOSBox nor Windows, and CHARTRAN gives a perfect test: on every save at hand the
Python result must equal CHARTRAN's byte for byte before the mod's additions are switched on. It
is more work: the item records' conversion, the psionics and the spells must be read out of
CHARTRAN's code (303 functions, already translated in Dark Sun Recompiled, which helps).
**Recommendation: the CHARTRAN wrapper first** (a few days, and most of it is the item table).
Then the Python transfer if DOSBox in the middle proves awkward for players.

## Porting the mod

### How the mod is built, and what that means for WotR

| Part | What it is | Carries to WotR? |
|---|---|---|
| `gamepatch.py` | 454 patches to SL's `DSUN.EXE` at fixed file offsets: a few bytes each, most an `INT` the helper answers | **No.** Each must be found again in WotR's program |
| `dos/dsclog.asm` (DSCLOG) | the resident helper, 29,000 lines: every rule, the dice log's records, the combat log, the see-through figures, the kits | **Partly.** Its logic is the mod; but it reads SL's records by their SL offsets (creature 3Ah bytes, sheet 47h) and SL's data segment by address, and both differ in WotR |
| The Loader's data changes | GPLDATA scripts, item types, `SEGOBJEX`/`RESOURCE` pictures, new people, shops, the slave pens' quests | **Mostly no.** WotR's data is laid out otherwise (`OBJEX.GFF`, a `RGNnnn.GFF` a region), and the content (Kalzith, Semyon, the pens) is SL's story |
| The Loader's window, dice log reader, Characters tab | Python, reading memory through `layouts/shattered_lands.json` and the helper's ring | **Yes, with a WotR layout** and a helper that writes the same ring |

**The patch sites in numbers.** For each of the 454 patches, the 48 bytes of SL's program
round the site were looked for in WotR's program, allowing for differences:

| Found in WotR's program | Patches |
|---|---|
| exactly (the same 32 or 16 bytes, once) | 43 |
| closely (at least 75% of the bytes alike, a clear best place) | 147 |
| probably (55-75% alike, a clear best place) | 76 |
| not found | 231 |

So about half the sites have a likely twin, and even those must each be read and checked by
hand: a twin with different record offsets needs its helper code changed too. The other half
sit in code WotR rewrote, or in its 49 overlays, which are laid out otherwise.

**Memory: room enough** (measured 2026-11-19, `playtest/logs/2026-11-19-ravager-memory.md`).
The helper lives in upper memory with the game's overlay buffer, its music buffer and the
see-through figures' tables, and the game needs one free 60,000-byte piece each time the map opens.
Both games unmodded, with the map open, in the mod's DOSBox setup (EMS off, `UMBPLUS.COM` first):

| | Shattered Lands (the arena) | WotR (Tyr) |
|---|---|---|
| Conventional memory free after the game | 59,072 bytes | 64,192 bytes |
| Free in the game's own heap | none | 48,656 bytes, one piece |
| Upper memory free | 159,728 bytes | 159,728 bytes |
| Overlay buffer (twice the largest overlay) | 32,992 bytes | about 2.4 KB more (largest overlay 16,732 against 15,537) |

WotR runs without EMS (its memory layer takes XMS), `UMBPLUS.COM` gives it the same 156 KB of
upper memory, and it leaves about 110 KB spare in the 640 KB against SL's 57 KB. A helper of
DSCLOG's size with WotR's buffers would fit with room over. What stays tight is the helper's own
64 KB segment (688 bytes spare): one helper for both games would need room for a second table of
addresses, so a WotR helper would be its own build. Not yet checked: whether WotR has a music
buffer (its music is CD audio), and memory deeper into the game than its opening scene.

**What WotR already has.** Some of the mod's reasons to exist are fixed or done in WotR itself:
levels past SL's caps, 6th-level priest spells (the mod borrows their pictures already), the
"graphics disappear" limit noted in WotR's own README (the same picture store the mod enlarged).
A WotR edition would not need those.

### Three ways to go

1. **A full DOSBox port** (the mod as it stands, again for WotR): the 454 sites found and
   checked, the helper given a WotR table of offsets for every record and variable it reads, the
   data changes redone for WotR's files, and the playtest kit taught WotR's routes. In effort,
   close to the mod's own history so far. **Not recommended.**
2. **A short WotR edition** (DOSBox): a chosen few features that matter most, each ported and
   tested on its own. The dice log first: of its four sites, `rand` has a clear twin in WotR's
   program (40 of 48 bytes alike, at file offset 5A22h, its code the same but for one data
   address). The save, AC and text-window sites have none by likeness (their best places score
   no better than the second best) and must be found by hand, by what the code does. Then the
   combat log, the Look box, and the rules that live mostly in the helper (multiclass hit
   points, the spell save, resting, thieves). No new content. A reasonable project if WotR play
   is wanted soon.
3. **Through Dark Sun Recompiled** (Phase 7 of its plan): the mod's rules as C hooks, with an
   address table for each game, so a rule is written once. The recompiled program already runs
   both games and CHARTRAN, and functions matched between the two games (its Phase 6) give the
   address table almost for free. **Recommended as the real port.** It waits on that project
   reaching further into WotR (today: the opening in Tyr).

### Recommendation

1. Now: **the transfer button** ([above](#a-simple-way-take-the-party-to-wake-of-the-ravager-in-the-loader)),
   with the item table and the specs kept in spare bytes, so that a party made and played with
   the mod reaches WotR whole.
2. If WotR play with the mod's rules is wanted before the recompiled program gets there: **the
   short WotR edition**, starting with the dice log (one site found already, three to find by
   hand).
3. Long term: **the rules through Dark Sun Recompiled**, one rule for both games.

## Repeating the checks

- Both games: `playtest/setup_game.sh` and `playtest/setup_ravager.sh` (the user's own
  installers, from the private repository; never a public link).
- The transfer: `sh playtest/chartran.sh SAVE.SAV OUTDIR DEBUG` (WotR's own CHARTRAN in a headless
  DOSBox of its own). The roster it wrote is `OUTDIR/C/RAVAGER/CHARSAVE.GFF` (read it with
  `dsloader.gff.read_gff`), the item mapping `DEBUG.DAT`.
- The patch sites: each `gamepatch.PATCHES` entry's 48 bytes round `offset` in SL's `DSUN.EXE`,
  scored against every place in WotR's (bytes alike, best against second best).
- The sheet bytes: a linear disassembly (capstone, 16-bit) of each `DSUN.EXE` for
  `es:[reg+disp]` with the offset in question.
- The test log: `playtest/logs/2026-11-19-ravager-transfer.md`.
