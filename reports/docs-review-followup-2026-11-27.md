# Documentation review, follow-up (2026-11-27)

The follow-up to the [first docs review](docs-review-2026-11-27.md), done with the project skill
`/documentation-review` in full (its twelve parts below, then the findings ranked). Scope, from the
[audit plan](https://claude.ai/artifact/G7XEUJhSTH8trfQqiR7uRM)'s items 4 to 6, on `obsidian-edition`
after #257 and #260:

- **Part 8, the pages the first review didn't read**: ITEMS, CREATURES, PEOPLE, HOW-THE-GAME-WORKS,
  WEAPON-SPECS, DEVELOPMENT-RULES, -SCREENS, -CONTENT and -KITS.
- **Part 7, the start scripts**: the five `.bat` files and the README's lines on them.
- **Area 6, bloat in the long pages.**
- **Both games**: the user's rule (2026-11-27) that whatever changes, both games get it. Every page in
  scope was read for what one game has and the other lacks.

Fixed on branch `claude/followup-docs-audit`; what needs the owner's call is marked **(owner)**.

## The twelve parts

### 1. Redundancy

Nothing new found beyond the first review's list. Checked: RAVAGER.md's list of the mod in the sequel
against FEATURES.md (each item links its FEATURES section rather than restating it), and the new "Not in
the sequel yet" list against DEVELOPMENT-KITS.md's own line (that line now names only what is left, and
RAVAGER.md links KITS.md for the kits).

### 2. Irrelevancy

The class-outfits gallery (`docs/class-outfits/`, 338 files, left out of the release zip by
`release.yml:68`) holds four pictures that no page shows: `half-giant-shoulder-fit.gif`,
`body-detail-comparison.png` and `half-giant-belt-tab.png` (referenced nowhere), and
`elf-human-reference.png` (only by `prototypes/elfoutfits.py`). They are working pictures from the
outfit fits. Not removed: they don't ship and cost nothing to keep. **(owner)**: delete, or link them
from the gallery's README.

### 3. Bloat

See area 6, below.

### 4. Inconsistency

- **Fixed**: `DEVELOPMENT-KITS.md:787` said "Not in the sequel yet: what kits do to spells and powers (the
  Shinobi's spells and casting), the cast sound ... and `ARROWS_FORBID` ... DSCLOG2 is at its one-segment
  limit". All three are in: `dos/dsclog2.asm:3383` `shinobi_mage` (site 190), `:4592` `kit_cast_level`
  (205), `:4578` `psp_use` (191), `:23276` the cast sound (`ARROWS_SOUND`), `:8045` `arrows_forbid`. The
  line now names what is left: a Scholar's THAC0 (`kits.py:310` has it, DSCLOG2 only the kit's name at
  `:11649`) and the kits' part of the DAM lines (`dsclog2.asm:11127-11135` says so).

### 5. Clarity and reorganisation

- **Fixed**: RAVAGER.md listed everything the sequel has from the mod, and nothing of what it lacks, so a
  player couldn't tell a missing feature from a broken one. It now ends with **Not in the sequel yet**, each
  line checked against the code (below, "Both games").
- DICE-LOG.md says nothing about the sequel (0 mentions), though the dice log runs there with its own steps
  (`RavDiceLog.PASS`, `ravlog.py:2433`) and leaves some out (`ravlog.PASS_LEFT_OUT`, `:2479`). The new RAVAGER.md list
  names what the sequel's log leaves out; DICE-LOG.md's intro could link it. Proposal, not done.

### 6. Patch notes

CHANGELOG.md has this pass's entry under Unreleased, beside #260's. PATCH-NOTES.md is the release's and
waits for the release step (the first review's plan).

### 7. The loader (start scripts)

All five `.bat` files read:

| File | Runs | Both games? |
|---|---|---|
| `Start Obsidian Edition.bat` | the Loader's window | both (its two Play buttons) |
| `Start Game with Dice Log.bat` | the game and the Loader | both |
| `Play Wake of the Ravager.bat` | `-m dsloader launch --ravager` | the sequel |
| `Play Dark Sun (in-game rolls).bat` | `-m dsloader play` (no `--ravager`) | **Shattered Lands only** |
| `Show Save.bat` | `-m dsloader save FILE` (`__main__.py:156`, SL's `Layout`) | **Shattered Lands only** |

- **Fixed**: `README.md:241` and `:260` didn't say the in-game-rolls start and Show Save are Shattered
  Lands only. They do now, and say where the sequel's equivalents are.
- Both are **gaps** under the both-games rule (in the list below). A sequel `Show Save` needs the sequel's
  save reader (`ravtransfer`'s) behind `cmd_save`; a sequel in-game-rolls start needs `play` to take `--ravager`.
  **(owner)**: whether to add them.

### 8. The other documentation

Read in full, with these claims spot-checked against the code or the real game files (both games'
copies, `/tmp/playtest/inst` and `/tmp/playtest/rav`):

- **HOW-THE-GAME-WORKS, Weight and carrying**: a dagger 10, a long sword 30 or 40, a mace 100 (the real
  SL files: dagger types 17 and 33 at 10, long swords 45 and 63 at 30 and 40, mace 20 at 100; a bone long
  sword, type 81, is 20); "SSI left 71 of its 102 item types weighing 0" (counted: 71 of 102). Correct.
- **WEAPON-SPECS, Attacks a round**: the bow and darts' 3, 4 and grand mastery's 5 at 7th-10th, the
  sling's 3/2, the unchosen warrior's band lower, all as `specialize.MISSILE_RATES` and
  `missile_attacks` (`specialize.py:204-230`). Correct.
- **DEVELOPMENT-KITS**: the kit sites 62-69, 73, 76, 190-199 (`dsclog2.asm:4449-4586`). Correct.
- **DEVELOPMENT-RULES**: each "`RULE_x` in `RULES_PORTED`" (seven of them) against `ravager.py:95-101`.
  Correct.
- **CREATURES, PEOPLE**: generated pages; `test_doccreatures` and `test_people` pass. Correct, but
  **Shattered Lands only** (CREATURES has no word of the sequel; PEOPLE one). A sequel creatures page is a
  gap: `doccreatures` would need the sequel's monster records. **(owner)**.
- **ITEMS**: 20 sequel mentions, where the backported weapons are. Nothing wrong found; no weights on the
  page (they are in HOW-THE-GAME-WORKS).

### 9. Missing

The sequel's side, on almost every page: FEATURES.md has 73 sections and 57 of them say nothing of the
sequel, either way. RAVAGER.md now has both lists (in, and not yet). The per-section notes in FEATURES are a
bigger job: **(owner)**, whether each section should say "both games" or link RAVAGER.md.

### 10. Screenshots

Not in scope this pass beyond part 2's orphans (the first review covered them).

### 11. Tables

WEAPON-SPECS' attacks table (part 8) checked against the code. Its columns stop at 10th level (Shattered
Lands' cap); the sequel's band past 13th (`specialize.py:224`) is in the page's own "Past 13th level"
section.

### 12. Features

FEATURES.md: see part 9.

**Is anything missing?** Yes: the sequel's side of most pages, and three things only Shattered Lands has
docs for (creatures, the save viewer, the in-game-rolls start). **Are items where they belong?** Yes, now that
RAVAGER.md has the list of what the sequel lacks.

## Area 6: bloat in the long pages

| Page | Words | Note |
|---|---|---|
| `playtest/RESEARCH.md` | 42,000 | 324 dated notes; not shipped |
| `PLAYER-GUIDE.md` | 26,000 | |
| `DEVELOPMENT-RULES.md` | 25,000 | lines up to 632 characters |
| `playtest/PLAYTESTING.md` | 23,000 | 135 dated notes; not shipped |
| `DEVELOPMENT-SCREENS.md` | 22,000 | lines up to 820 characters |
| `DEVELOPMENT-CONTENT.md` | 21,000 | |
| `DEVELOPMENT-KITS.md` | 11,000 | lines 754-787 are 400 to 1,000+ characters each |

Proposals **(owner)**, in order of value:

1. **RESEARCH.md** split by subject (memory edits, sounds, the picture store, the sequel, the recompiled
   program): one file per recipe family, each under 10,000 words, with the dated "2026-11-xx: found that"
   notes folded into the recipe they changed.
2. **DEVELOPMENT-KITS.md:754-787**, the sequel's kits, rewritten as one short section per kit part with a
   table of sites, instead of six paragraph-long lines.
3. **DEVELOPMENT-RULES** and **-SCREENS**: wrap the long lines (no content change), so diffs and reviews
   can be read.

None done here: each is a structural change, which goes to the coordinator first.

## Both games: what one has and the other lacks

The new RAVAGER.md section lists, from the code:

- class outfits and the creation figure (`ravlog.PASS_LEFT_OUT`: "the sequel has no class outfits");
- the in-game-rolls start and Show Save (part 7);
- Restore Youth, the mod's Whirlwind damage and Sunstroke's heat, and a Healer's two cosmos spells
  (`dsclog2.asm:365`, `:969`);
- a Scholar's THAC0 and the kits' part of the DAM lines;
- the DAM lines' chatkcha throws, Hasted and Slowed, a weak material on View Character
  (`dsclog2.asm:11133-11135`);
- defilers' scrolls (the sequel's stand-in: Notaku's books and three wizards' one more, `ravgear.py:27-31`),
  and the people's gear (`people.py`'s watch, not in the sequel's pass);
- the dice log's XP-per-kill and level-up lines (`ravlog.py:2306`), the missing-item report (`itemwatch`),
  the initiative scores' line (`PASS_LEFT_OUT`);
- and GAME-BUGS' list of Shattered Lands fixes not yet in the sequel (linked).

And the other way: nothing the sequel has that Shattered Lands lacks, beyond what the user's rules keep
there (the sequel's unique items, its levels past Shattered Lands' cap).

## Findings, ranked

1. **Wrong** (fixed): `DEVELOPMENT-KITS.md:787` called three ported kit parts missing.
2. **Missing** (fixed): `README.md:241`, `:260` didn't say two start scripts are Shattered Lands only;
   RAVAGER.md had no list of what the sequel lacks.
3. **Missing** (owner): the sequel's side of FEATURES (57 of 73 sections), DICE-LOG, CREATURES.
4. **Structure** (owner): RESEARCH.md's size; DEVELOPMENT-KITS' sequel lines.
5. **Irrelevant** (owner): four unused outfit-gallery pictures.

## Checked and correct

Every claim listed under part 8; the five `.bat` files against `__main__.py`; the doc tests
(`test_doclinks`, `test_manual`, `test_manualcheck`, `test_doccreatures`) and the full suite.

## Not verified

The rest of the nine pages' claims were read for sense, not each checked against the code. The sequel's
DAM line and initiative panel were read from the code only, not played.
