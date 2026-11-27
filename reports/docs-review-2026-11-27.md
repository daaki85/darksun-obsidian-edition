# Documentation review, 2026-11-27

A review with the project skill `documentation-review`, against the combined test branch
`claude/combined-playtest` (PR #180, at `fc865f90`: every open PR, #217 to #232, docs PRs #224-#226
among them). The previous full review was 2026-11-19 ([docs-review-final.md](docs-review-final.md)).
Order of work, from the audit plan: which kits work in the sequel, the DOSBox-X wording (now the
default, and bundled on Windows), the outfit docs, and screenshots taken before the outfits; then the
release record and a sweep of the rest.

Fixes went on the open PR whose subject they belong to, so they merge with it:

| PR | Fixes added |
|---|---|
| #225 (DOSBox-X wording) | README requirements, macOS line, saves line, credits, front page, "other engine", the button's name |
| #232 (Ravager audit rest) | KITS' sequel table (Crusader), the kits' sequel list said once, a garbled Spellarcher sentence |
| #230 (outfit colours) | FEATURES: the outfits keep their colours in every area |
| #231 (creation-screen outfit) | FEATURES: the creation screen's figure wears the outfit |
| this branch | the Options tab picture retaken, the outfit galleries' dead and branch links, this report |

## Findings, ranked

### 1. Wrong statements

1. **README's requirements said the Loader runs the game in GOG's DOSBox**
   (`obsidian-edition/README.md:113`), on every branch, after DOSBox-X became the default and came
   with the Windows release (#146, #178, #185). Checked against `dsloader/dosboxx.py` `engine()`
   (DOSBox-X when usable, else GOG's) and `bundled()`. *Fixed on #225.*
2. **KITS' sequel table called the Crusader "in part"** (`KITS.md:808`) while naming everything it
   does as working. The merge train (#216, commit 6f6d4002) changed the row from "in part: ...; not
   one slot fewer" to "in part: its THAC0, expertise and one slot fewer" and left "in part". Checked
   in `dos/dsclog2.asm`: `war_hit` (its THAC0), `war_kit_is` (expertise), `slot_behind` (one slot
   fewer), `LV_DUE` (its weapon spec after DONE), `DUAL_BANS` (its dual limits). *Fixed on #232:
   "whole".*
3. **Both prose copies of the sequel kit list said the kits' spell and power rules don't carry
   over** ("what else they do to spells and powers doesn't yet, but for the Shinobi",
   `KITS.md:29-30` and `FEATURES.md:1202`), though #218-#223 brought the casting levels, cures,
   spells known, PSP costs and hit dice; only the Scholar's extra spells and −1 to hit are missing
   (checked: no `KIT_SCHOLAR` rule in `dsclog2.asm`, only its name). *Fixed on #232.*
4. **"macOS isn't supported"** (`obsidian-edition/README.md:126`) against FEATURES' engine section
   and the patch notes ("on Linux and macOS choose your own"; written, never run). *Fixed on #225:
   "on macOS nothing has been run yet", linked to what was tried.*
5. **`**Start the game**`** (`README.md:129`, `FEATURES.md:995`): the button is **Play Shattered
   Lands** now. *Fixed on #225.*
6. **"GOG's DOSBox keeps the saves in `cloud_saves`"** (`README.md:259`): both engines mount it
   (`dosboxx.py:516`, `launch.py:568`). *Fixed on #225.*

### 2. Missing documentation

1. **The front page never mentioned Wake of the Ravager** (`README.md`), the mod's largest new
   part since 2.19.2. *Fixed on #225: one sentence and a link.*
2. **The credits left out DOSBox-X**, which the Windows release carries under the GPL. *Fixed on
   #225.*
3. **The player's page said nothing of #230 and #231** (the outfits' steady colours, the creation
   screen's dressed figure); only DEVELOPMENT-CONTENT did. *Fixed on #230 and #231.*
4. **#217 has no CHANGELOG line** (docs only, GAME-BUGS rows): a **Docs** line when #224 lands.
5. **#227's message** (a whole sentence for a missing DOSBox-X) is in the CHANGELOG but not in the
   PATCH-NOTES; a Loader message, so left out on purpose is fine.

### 3. Duplication and structure

1. **The sequel kit list stood three times** (KITS' introduction, KITS' table, a 30-line FEATURES
   bullet) and had drifted (finding 1.3). *Fixed on #232: the table is the one home; the other two
   are a sentence and a link.*
2. **FEATURES' "Taking the party to Wake of the Ravager" is 230 lines in 27 bullets** and covers the
   whole port (rules, screens, kits, levels, weapon traits, the engine), not the party transfer its
   heading names. FEATURES is 1,888 lines. *Done on #234:* a player's page of its own, `RAVAGER.md`
   (starting it, the party transfer, the mod there), with FEATURES keeping a paragraph and a link,
   and the manual a page.
3. **CHANGELOG.md is 2,813 lines**; PR #95 and older (2.18.0 and before) could go to the archive at
   the next release, as #73 and older did.

### 4. Links

1. **The outfit galleries linked to branches**: twelve links to `blob/claude/class-outfits/...`
   (merged; it goes when the user deletes the branch) and one to `blob/claude/import-class-outfits/`,
   **already gone** (`half-elves.md:25`). The galleries don't ship, so they now link relatively to
   the repository's files (all nine targets checked present). *Fixed here.* No other `blob/claude/`
   link is left in the docs.
2. `tests/test_doclinks.py`, `test_manual.py`, `test_patchnotes.py`, `test_manualcheck.py`,
   `test_docicons.py`, `test_doccreatures.py`: 33 passed on #180; the doc tests pass on every
   branch changed here.

### 5. Screenshots, tables, feature lists

Every one of the 64 pictures in `obsidian-edition/docs/` predates the outfits (2026-11-26): the
newest is from 2026-11-19.

- **`options.png`: retaken here.** It lacked the Engine and Picture and music sections, the Journal
  tab, five In the game switches and the Saves switches. Taken from the Loader alone, with every
  section open and DOSBox-X found as a Windows player has it (the recipe is in PLAYTESTING.md's
  pictures for the docs). It shows a Linux path in the Engine line.
- **Loader pictures with the old bar** (title font, **Start the game**, no **Play Wake of the
  Ravager**, no Journal tab): `dicelog.png`, `dicelog-readable.png`, `dialogue.png` (README), and
  `viewer.png` (a developer page). Retake with a game attached.
- **Figures the outfits now dress, where the picture is about the figure** (retake first):
  `gear.png`, `magic-glint.gif`, `see-through.png` (FEATURES, Gerakis), `half-elves.png` (its
  caption describes the half-elves' undressed look, which a party member no longer shows),
  `creation-store-recall.png` (the creation figure is dressed now).
- **Figures in the background** (retake when convenient): `combat-log.png` (front page),
  `combat-log-*.png|gif`, `dust.png`, `shadows.png`, `picture-modes.png`, `steady-pace.gif`,
  `squares-in-reach.png`, `hit-chance-hover.png`, `floating-names.png`, `floating-charges.png`,
  `rings.png`, `fogbolt.png`, `whirlwind.gif`, `show-usable.png`, and the USE screens with the
  party's pictures (`default-party-armor.png`, `use-slots.png`).
- Unchanged by the outfits (item boxes, text screens, portraits): the other 30.
- **The gear table in FEATURES' "What the party wears"** was written before the outfits: "the game
  draws each race and sex the same whatever they carry", the Armour row's "figures drawn mostly bare
  (the mul, the dwarf man)" and the Cloaks row's "the human woman's cloak" need checking against the
  dressed figures. *Unverified: needs a play.*
- KITS' sequel table: every row checked against `dsclog2.asm` by its kit's code (rows the PRs
  #218-#223 and #229 wrote were taken as their PRs' tests have them).

### 6-7. Reader-task gaps, bloat

- KITS' introduction was a 17-line sentence listing the sequel's rules; now four lines.
- The FEATURES sequel bullet was 33 lines; now 10.

## The twelve parts

1. **Redundancy**: the sequel kit list (fixed); the DOSBox-X rules, checked in README, FEATURES,
   PLAYER-GUIDE, DEVELOPMENT, PATCH-NOTES and CHANGELOG: in step after #225 and the fixes above.
2. **Irrelevancy**: nothing new found in the pages read; the outfit galleries carry process notes,
   but they are a developer's gallery left out of the zip.
3. **Bloat**: 3.2, 3.3 above.
4. **Inconsistency**: macOS (1.4), the button's name (1.5), Crusader (1.2).
5. **Clarity and reorganisation**: 3.2 (`RAVAGER.md`, #234).
6. **Patch notes**: PATCH-NOTES (with #226) has every user-visible change of #146-#232 checked by
   subject (Shinobi spells, weapon traits, Poisoner, spell arrows, outfits and their colours, the
   creation figure, PSP costs, hit dice, Fine Bow, Spirit Caller, levels to 30th); `patch-notes.html`
   matches (`test_patchnotes`). It still says "version 2.19.2", right until the release.
7. **The loader**: the engine, its requirements and the start buttons (fixed); the Options tab
   picture (retaken). The `.bat` files were not re-read.
8. **The other documentation**: KITS, FEATURES (outfits, sequel, engine), README, DEVELOPMENT and
   DEVELOPMENT-INTERNALS (engine lines), the playtest guides (engine lines), the outfit galleries'
   links. Not read this time: ITEMS, CREATURES, PEOPLE, HOW-THE-GAME-WORKS, WEAPON-SPECS beyond its
   sequel section, DEVELOPMENT-RULES, -SCREENS, -CONTENT, -KITS in full.
9. **Missing**: 2.1-2.5.
10. **Screenshots**: section 5.
11. **Tables**: KITS' sequel table (fixed); the gear table (unverified).
12. **Features**: the front page's list now names the outfits and the sequel.

**Is anything missing?** The front page's sequel line, DOSBox-X in the credits and the two outfit
lines were; they are added. Still missing: retaken figure and Loader pictures, and a CHANGELOG line for
#217.

**Are items where they logically belong?** Mostly. The sequel's material in FEATURES had outgrown
the subsection it sat in; it has a page of its own now (3.2, #234).

## Not verified

- The FEATURES gear table under the outfits (5).
- The Scholar, Wanderer and Spellarcher rows beyond the code read; no play.
- Windows: the Options tab picture is from Linux, with a stand-in DOSBox-X answering its version.

## Follow-up after merge train #241 and #242-#254

- The CHANGELOG's Unreleased section is by subject again, with every entry naming its pull request
  (#146 to #254); #217's line and the docs PRs' lines (#224-#226, #233, #234, #252) are in. The sequel's
  interface art (#255) has its entry under New, and RAVAGER.md its bullet.
- The patch notes' Wake of the Ravager section links to RAVAGER.md (not FEATURES' short paragraph),
  and has the figures (#250, #251, #253) and the Effects screen's lines (#245, #249); the Scholar's
  −1 to hit is named with its extra spells as still to come, as KITS' table has it.
- Still open, both need a play: the **Loader pictures with the old bar** (`dicelog.png`,
  `dicelog-readable.png`, `dialogue.png`, `viewer.png`), the figure pictures #252 didn't retake
  (`half-elves.png` is now captioned as the bare race figures; `fogbolt.png`, `show-usable.png`,
  `default-party-armor.png`, `use-slots.png`), and **FEATURES' gear table** under the outfits.
