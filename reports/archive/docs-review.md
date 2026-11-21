# Documentation review (2026-11-17)

*Status: acted on (#100 to #105). A review of every document in the repository: the
player pages, the reference pages and their tables, FEATURES.md and its screenshots, the patch
notes, release notes, CHANGELOG and HTML manual, the developer pages against the Loader's code, and
the playtest kit, reports and CLAUDE.md. Line numbers are as of `obsidian-edition` at `44f6b60`.*

## The short version

The documentation is **accurate** but **heavy and repetitive**. Almost nothing is wrong against the
code: every Options tab label and default, every screenshot of the Loader, every link and anchor,
every module and symbol named in the developer pages checks out, and the HTML manual is in sync. The
problems are:

1. **One release problem**: 2.18.0 is announced everywhere, but never released (no tag).
2. **The same facts in three or four places**, which have started to drift apart.
3. **Pages that grew past their purpose**: FEATURES.md (2,838 lines) is a rule book, PATCH-NOTES.md
   is a second features list, the CHANGELOG (4,824 lines) is an engineering diary, and the playtest
   guide's "read in full before every test" part runs to hundreds of lines.
4. **Developer material in player pages, and developer pages in the player's zip.**

What checked out and needs nothing: see [What is fine](#what-is-fine) at the end.

## 1. Fix now (small, clear-cut)

| # | Where | Problem | Fix |
|---|---|---|---|
| 1 | `PATCH-NOTES.md:3`, `README.md:72`, `dsloader/__init__.py:3` | 2.18.0 "is out", but there is no `v2.18.0` tag: the newest release is 2.17.1, so the "Download: releases/latest" link gives 2.17.1 under 2.18.0's notes. | Run the Release workflow on `main` (step 4 of DEVELOPMENT.md's "Making a release" was skipped). |
| 2 | `release-notes/v2.18.0.md:47,57` | Every link points at `blob/v2.18.0/…`, which 404s until the tag exists. | Fixed by #1. |
| 3 | `DEVELOPMENT.md:245` vs `CHANGELOG.md:49` | The release checklist renames "## Next pull request (not opened yet)", but the CHANGELOG's heading is now "## Unreleased (branch `obsidian-edition`)". | Use one name. |
| 4 | `DEVELOPMENT.md:868` | `GuestMemory.LOW_MEMORY` doesn't exist; it's the module constant `guestmem.LOW_MEMORY` (as line 839 says). | Correct it. |
| 5 | `DEVELOPMENT.md:595` vs `:603` | Two sizes for the same DSCLOG.EXE build (70,496 and 70,416 bytes); the committed file is 70,416. | Keep one. |
| 6 | `CLAUDE.md:72-73` | Says to note water in PLAYTESTING.md; the guide says ROUTE.md, which is where the notes are. | Point to ROUTE.md's water section. |
| 7 | `playtest/chestuse.sh` vs `ROUTE.md:200-208`, `HISTORY.md:392` | The script makes blind clicks and presses (161,72); ROUTE and HISTORY say the working way is `pointer.py look` and (163,70), and that the script's press opened the USE screen. Its header points to a section now in ROUTE.md. | Fix the script to match (a tool fix), its header, then rerun `tools_index.py`. |
| 8 | `PLAYTESTING.md:886` | A recipe depends on a scratch `setitem.py` that isn't in the kit. | Add it to `playtest/` or rewrite the recipe around `itemedit.py`. |
| 9 | `PLAYER-GUIDE.md:1939-1944` | Says graphics and steady pace are described "in the README"; they're in FEATURES.md#graphics and #game-speed. | Repoint. |
| 10 | `PLAYER-GUIDE.md:2008-2011` | "Restore defaults sets every switch back": it doesn't reset the Wake of the Ravager folder, the window size or the dice log's checkboxes (`viewer.py:741-759`). | Say so. |
| 11 | `PLAYER-GUIDE.md:107` | Only warriors and the Swashbuckler are said to pick weapon specs after DONE; the Battle Mage, Crusader and Mind Warrior do too (the guide's own 861-864). | Add them. |
| 12 | `PLAYER-GUIDE.md:95-98` | Priests cure at rest; the Resting section and the option say priests **and psionicists**. | Add psionicists. |
| 13 | `PLAYER-GUIDE.md:1934` | "Spells on the Effects screen (a bug fixed)", but it has a switch (`effects_kept`). | Drop "(a bug fixed)". |
| 14 | `PLAYER-GUIDE.md:2024-2030` | The "always on, no switch" list reads as complete but leaves out at least the magic item icons, spells on the ground, 40 saves / 29 characters, preservers' first spells, psionic powers at creation and material penalties. | Complete it, or say "among them" and link FEATURES. |
| 15 | `PATCH-NOTES.md:185` | "The player's guide has all 37 [kits]": the tables are on the Kits page. | "The Kits page". |
| 16 | `PATCH-NOTES.md:11` | `[patch-notes.html](patch-notes.html)` opens raw HTML source on GitHub. | Link the release asset. |
| 17 | `KITS.md:137-141` | The multiclass intro names which race takes which kit for 6 of 13 kits only. | Drop the partial list; the table's column says it. |
| 18 | `ITEMS.md:145` | Tanelyv's chest piece is a footnote, with no Body armour row, though the acid table lists it as chest armour. | Give it a row. |
| 19 | `ITEMS.md:97, 152` | Empty Bonus cells (Arrows +3/+2/+1, Leather helm +1). | Fill them. |
| 20 | `ITEMS.md:13-21` | The Contents names "weapons, missile weapons, by weapon spec…" and "items against acid…", but they're bold text, not headings, so they can't be linked. | Make them `###` headings. |
| 21 | `DICE-LOG.md:135` vs `GAME-BUGS.md:112` vs `FEATURES.md:332` | The thief equipment penalty: "None" with the Loader (GAME-BUGS), shown as `-5 equipment` (DICE-LOG), "none in games started with the dice log" (FEATURES); `dicelog.py` still prints it. | Say in all three when it still appears. |
| 22 | `GAME-BUGS.md:189-190` | Two rows name the same switch, "Saving throws against spells", but link to two different FEATURES headings. | Use each heading's name. |
| 23 | `FEATURES.md:1788-1793` | The ranger hide/move-silently table stops at level 10; the code goes to 13 (`game.py:1037`), as PLAYER-GUIDE's table shows. | Extend it or link. |
| 24 | `FEATURES.md:1458-1463` | The Kits row doesn't mention taking a kit after DUAL (the switch's own text, and KITS.md:334, do). | Add it. |
| 25 | `FEATURES.md:2505` (docs/gear.png) | Alt text "Gerakis on the sand", but the picture shows the slave pens' tiled floor. | Re-caption. |
| 26 | `FEATURES.md:374` (docs/creation-store-recall.png) | "AGE, above RECALL": in the picture it's to the right of the PSP line. | Reword. |
| 27 | `HOW-THE-GAME-WORKS.md:780-782` | Links `blob/obsidian-edition/…`, a branch that is deleted on every merge. | Use `blob/main/…`. |
| 28 | `README.md` and `FEATURES.md:2835` | "Some fifty" bug fixes; GAME-BUGS has about 65 rows. | Recount or say "dozens". |
| 29 | `CHANGELOG.md` | Pull request #96 (the branch-naming rule) has no entry. | Add a line, or say tooling-only PRs are skipped. |
| 30 | `reports/combat-log-design-handoff.md:7-9` | Names three mock-up PNGs as "not in this folder yet"; they never were. | Drop the sentence. |

## 2. Decisions for you (structure)

These change how the documentation is organised. Each is a recommendation; none is done.

### A. One home for each fact

The biggest problem. The same table or rule is written out in several places, and the copies have
started to disagree:

| Fact | Written out in |
|---|---|
| Attacks a round, and who picks which weapon spec | KITS.md:380-424, PLAYER-GUIDE.md:961-993, FEATURES.md:1466-1478 (the two tables have different rows) |
| The new items | ITEMS.md, PLAYER-GUIDE.md:1829-1910, FEATURES.md:2097-2160 (Ironbulwark is "the first" metal shield in one, "the only" in another) |
| Turn Undead | HOW-THE-GAME-WORKS.md:502-583, DICE-LOG.md:93-94, GAME-BUGS.md:192 |
| Spells as the manual describes them | FEATURES.md:1325-1351, HOW-THE-GAME-WORKS.md:678-760, DEVELOPMENT-RULES.md:972-1215 |
| CON regeneration, ages, ranger skills, creature-size dice, two weapons, resting, class restrictions, prime requisites, level cap | FEATURES.md and PLAYER-GUIDE.md (and KITS.md for the dice) |
| Spell slots | KITS.md:272-286, PLAYER-GUIDE.md:1397-1411 |
| The warrior's THAC0 for kits | KITS.md:99, 111, 130, 229-237, PLAYER-GUIDE.md:986-992 |
| The class minimum scores | GAME-BUGS.md:104, HOW-THE-GAME-WORKS.md:55-58 |
| The Bowyer's rules | HOW-THE-GAME-WORKS.md:913-935, DEVELOPMENT-SCREENS.md:71-91 |
| Getting started | README.md:19-38, obsidian-edition/README.md:143-198, PLAYER-GUIDE.md:66-88 |
| Docs index | README.md:39-66, obsidian-edition/README.md:16-31 |
| "What it changes on your computer" | README.md:68-72, obsidian-edition/README.md:98-100 and 340-346 |
| The fight summary | obsidian-edition/README.md:528-534, DICE-LOG.md:165 |
| A complete list of changes from the game | PATCH-NOTES.md (463 lines) and FEATURES.md (2,838) |
| No public links / the private repository | CLAUDE.md and PLAYTESTING.md (five times) |

**Recommendation:** KITS.md and ITEMS.md hold the numbers for kits and items; PLAYER-GUIDE.md holds
the rules a player needs, spoiler-free; HOW-THE-GAME-WORKS.md holds the game's own rules in depth;
FEATURES.md becomes a short entry per switch that links to them. The others link instead of
restating.

### B. What each page is for

| Page | Today | Recommended |
|---|---|---|
| **FEATURES.md** | 2,838 lines: rule tables, story walkthroughs (Kalzith, Semyon, the Trustee: ~140 lines of quoted dialogue at 2171-2310), test measurements (2736-2776), implementation notes. | One entry per Options switch, in the tab's order, plus an "Always on" section: what it does, the switch, a picture, links. About 800-1,000 lines. Story content to a spoiler page beside ITEMS.md. |
| **PATCH-NOTES.md** | A second full catalogue, and it also carries mod-to-mod history ("(was …)" in the kits list means an earlier version of the mod, not the original game; "fixes to the mod's own earlier versions"). | Strictly "the mod against the original game", short, linking into FEATURES. Version-to-version news only in `release-notes/`. Consider renaming to CHANGES.md (its title and its manual page, changes.html, already say "changes"). |
| **CHANGELOG.md** | 4,824 lines: byte counts, offsets, test names, research write-ups (the Unreleased section, 51-99), "the user's call" ×67, mixed section labels. | One short entry per pull request (what and why). Detail stays in commits and DEVELOPMENT*.md, research in `reports/`. Move entries before about 2.12.0 to a frozen CHANGELOG-archive.md, extending the "Shortened" practice already used five times. |
| **HOW-THE-GAME-WORKS.md** | Says it covers the original game's rules, but also holds the mod's rule change in full, and code addresses (79BBAh, 7ADB7h, SEGOBJEX.GFF, `python -m dsloader checks`). | Player-relevant rules only; addresses to DEVELOPMENT-RULES. |
| **GAME-BUGS.md** | Bugs, plus a "Rules it got wrong, with a switch" table (180-206) that duplicates FEATURES' rule changes. | Bugs only. |
| **KITS.md** | "Kits and weapon specs": about 40% is weapon specialization, which isn't a kit; table cells are paragraphs (the Spellarcher row is ~330 words). | Split out WEAPON-SPECS.md, or at least a separate part. Short one-line cells, with each kit's long rules in a subsection under the table. |
| **obsidian-edition/README.md** | Ships in the zip and becomes the manual's front page, but has no version, credits or licence; version-by-version save compatibility (272-323); developer tools (Memory tools, layouts, `.asm` sources) on the player's first page. | The one full entry point: requirements → install (back up saves as a setup step, now at 260-270 under Updating) → play → the Loader → troubleshooting → version, licence, credits. |
| **README.md** (root) | A second install guide and docs index. | A pitch, three steps linking the folder README, and credits. |

### C. Developer pages out of the player's zip

The release zip is `git archive` of `obsidian-edition/` with nothing excluded, so it ships the five
DEVELOPMENT pages (~6,100 lines), `tests/` (2.3 MB), the `.asm` sources and `docs/viewer.png`
(used only by DEVELOPMENT.md). The manual already links the developer pages on GitHub, so the
copies in the zip are never used. **Recommendation:** an `export-ignore` list in
`obsidian-edition/.gitattributes` (DEVELOPMENT*.md, tests/, maybe viewer.png), or move the
developer pages to the root beside `playtest/` and `reports/`. `test_doclinks`' check that shipped
pages stay in the zip needs updating either way.

Related: the manual inside a release links to `blob/main/`, so an older zip's links describe newer
rules (`manual.py:42`); `blob/v{version}/` would pin them.

The zip also carries the patch notes twice (`manual/changes.html` and a top-level
`patch-notes.html`). Keep one.

### D. The developer pages

- **DEVELOPMENT.md has no architecture overview or module map.** The real overview is buried as
  numbered steps in "How the dice log works" (line 328), and the module list is a 22-line run-on
  sentence. Every one of the 123 Loader modules is named somewhere, but about 45 only once, in
  passing. **Add:** a five-box architecture (Loader → DOSBox config → patched DSUNLOG.EXE → DSCLOG
  → the Loader reading and writing memory), requirements (Python version), a glossary, and a module
  table (module → one line → section).
- **Terms drift**: "launcher" ×12 against "the Loader" ×211; "helper" ×126 against "DSCLOG" ×135;
  "dice log" against "dice-log". A glossary fixes this.
- **Sections in the wrong file**: "Spell arrows" (RULES:1754) is all Spellarcher → KITS; the
  Trustee's script fixes (RULES:1883-1906) → CONTENT's script bugs; the searches, the Bowyer and
  ability checks (SCREENS:58-113) are about labelling rolls → DEVELOPMENT.md's dice log section;
  the item-watch internals (DEVELOPMENT.md:878-930) → their own section beside the crash reports;
  bug-fix sections are scattered through CONTENT (top, middle, end); SCREENS is half controls and
  saves, against its title.
- **DEVELOPMENT-KITS' effect table** has duplicate rows ("a spell's damage" twice, "initiative" /
  "initiative in a fight", "gear allowed" / "gear the kit allows") and the Sentinel is missing from
  "to hit" (180-219).
- **History in the reference**: about 51 dates, 41 "seen in DOSBox" passages and 26 credits across
  the five pages, and version narratives ("an earlier version…", "2.8.0 to 2.13.0…"). Keep the
  current rule; move the story to the CHANGELOG or `playtest/HISTORY.md`.
- **"Not yet seen in play"** notes (CONTENT:48, 120, 206; RULES:1860; DEVELOPMENT.md:928) may be
  stale: saves and logs for some of them now exist. Recheck and keep one "unverified" list.
- `guidepage.py` is a one-line shim for `manual.py`, documented twice; delete it.

### E. The playtest kit and CLAUDE.md

- **The startup procedure is out of order.** CLAUDE.md says start → load → build check → watchdog;
  the guide's sections say start → build check → window → watchdog, with loading in §5; and its
  §3.3 ("the window must be 320x240") comes before any load, though §3.1 says the window stays
  640x400 until a save is loaded, so a reader following it in order fails the check. Make it one
  numbered checklist in the order actually run, and have CLAUDE.md use the same order.
- **The must-read part is too long**: §2 holds things that aren't startup steps (unit tests, the
  release zip, the walkthrough, Wake of the Ravager: 69-118), and the recipes carry ~200 lines of
  memory offsets (437-557, 900-1097) and ~60 dated anecdotes, against the guide's own rule
  (recipes for current practice, HISTORY for stories). Moving these would bring the guide toward
  700 lines.
- **Git and branches**: CLAUDE.md's Git paragraph ("rebase onto `origin/obsidian-edition`; GitHub
  deletes the branch when its pull request merges") and the new Branch names rule don't say how they
  fit together. One paragraph: work on `claude/<task>`, rebase onto `obsidian-edition`, pull request
  into `obsidian-edition`. The note about the old remote name is stale.
- **HISTORY.md** says it's by topic, but has a date index in the middle and seven dated sections
  appended after it; one stub has no content (218-219).
- **playtest/logs/** (99 entries, 2.1 MB): no index; 18 logs referenced nowhere; about 11 PNGs in
  `img/` used by no log; script and diff files mixed in. Add a `logs/README.md` (or make HISTORY's
  date index that), and move the artefacts to `logs/files/`.
- **saves/README.md** matches the folder (15 saves), but one sentence is repeated seven times and
  the lines aren't wrapped; it names two Loader modules as if they were kit tools.
- **TOOLS.md** is complete and current, but its 220-character cap cuts many descriptions
  mid-sentence. Shorten those scripts' first header lines.

### F. reports/ and research_notes/

`reports/Combat log design across games.md` and `research_notes/Combat log design across games/`
(its four source notes) share one name with spaces, link to nothing and are linked from nothing; their
recommendations have since been built. Rename to kebab-case, move the notes beside the report (and
drop the top-level `research_notes/`, which holds only this), and give each report a status line.
One note (`classic_crpgs.md:96-99`) links a university software directory that may host another
game's files: check it and drop it if it's a download.

## 3. Tables

- **KITS.md**: cells are paragraphs (Myrmidon ~90 words, Spellarcher ~330); a one-column, four-row
  table (434-439) that should be a sentence; blank cells (418) where other tables use "—"; the sphere
  weapon limits written out three times (79, 119, 493-496); the Brute's row (365) carries UI detail.
- **ITEMS.md**: game items terse ("+1", "a chest") and the mod's items full sentences; "a chest"
  tells a spoiler reader nothing; the Prices table packs several items into one row with
  semicolon-separated prices (300-322); "The mod's" column mixes a **new** flag, placement notes and
  rules (rename to Notes, give the Fine Bow its own row); "By weapon spec" (102-122) re-lists the
  table above it; `short-sword.png` should be `metal-short-sword.png` like the other metal weapons.
- **CREATURES.md** (generated by `doccreatures.py`, and in sync): the Race column says "monster" in
  60 of 76 rows; three rows are just "Guard"; "M (man-sized)" repeats the legend in every row; no
  "Spoilers" lead line unlike the other pages; a developer note in the intro. Fix in the generator.
- **DICE-LOG.md**: Meaning cells are paragraphs with several example lines joined by " / "; one
  example per row would read better.
- **HOW-THE-GAME-WORKS.md**: the 65-row cleric spell table (428-498) has a mostly-redundant "The
  log" column and no wizard counterpart; `reports/spells-against-the-manual.md` covers the same.
- **PLAYER-GUIDE.md**'s Options table: correct, but each radio choice is its own row with the same
  link repeated (2036-2039, 2135-2136, 2148-2150); one row per choice group is enough. It also
  leaves out the Loader's other remembered settings (Game window, Text size, Readable layout, Show
  details, Show unlabelled rolls).

## 4. Screenshots

All 60 top-level pictures were viewed against their captions and the code. **None is outdated.**
The four Loader pictures (`options.png`, `viewer.png`, `dialogue.png`, `dicelog.png`) were retaken
on 2026-11-16 and match `viewer.py` label for label. No picture is missing; none is unreferenced
(`viewer.png` is used only by DEVELOPMENT.md, so it ships for developers only). `docs/items/` (147)
and `docs/creatures/` (189) are all referenced.

- **Re-caption**: `gear.png` (not on the sand), `creation-store-recall.png` (AGE isn't above RECALL).
- **Weak**: `look-box.png` shows only the HP/AC and THAC0/AL lines, not the MR and defence lines
  the text describes, and is shown smaller than the others.
- **Heavy**: `whirlwind.gif` (548 KB), `steady-pace.gif` (492 KB, 701 frames, "the difference is
  small" by its own caption), `combat-log-live.gif` (448 KB). Trim them or use a still.
- `new-priest-spells.png`: the text says the mod's Heal cures Feeblemind; the in-game description
  pictured says only "damage, disease and blindness". Say whether that's intended.
- Many pictures' dates are a mass re-commit on 2026-11-10, so when they were taken can't be told from
  git; nothing in them shows a label or option that no longer exists.

## 5. Missing

- **Player troubleshooting**: how to change the remembered game folder (`--game-dir`, or delete
  `game_dir` from settings.json); "Python is installed but the .bat says it isn't" (32-bit, or no
  tkinter); "Out of memory" under Known issues rather than Crash reports.
- **Linux**: no command given for following a DOSBox you start yourself (`python3 -m dsloader
  view`), and nothing says tkinter (`python3-tk`) is needed.
- **The root README** doesn't link Requirements (GOG `DSUN.EXE` 611,408 bytes, 64-bit Python,
  Windows).
- **The folder README** (the one that ships) has no version, licence or credits.
- **DEVELOPMENT.md**: architecture, module map, glossary, Python version, how to run one test
  (`python -m unittest tests.test_x` from `obsidian-edition/`), a contributor checklist, and the
  `.bat` → subcommand mapping ("Start Obsidian Edition.bat" runs `view`, not `launch`).
- **FEATURES.md**: taking a kit after DUAL; the Wilderness Avenger's ranger stealth.
- **playtest/**: `setitem.py`; an index of `logs/`.

## 6. Smaller points, by page

- **README (folder)**: the Python install step says to start the .bat again, but it usually carries
  on by itself (152-159); "Start Game with Dice Log.bat" suggests the other ways don't log (every
  way does); "drag a `SAVEnn.SAV`" omits `cloud_saves` and pages 2-4 (`SAVB/C/D`); the security
  note's paragraph on unblocking (161-167) could be three lines; the Dark Sun Recompiled part
  (220-246) is long for an add-on.
- **PLAYER-GUIDE**: 48 repeated blocks across the eight classes ("Multiclass: … in More than one
  class" ×8, "Some kits rule out a change of class" ×8, magic-weapon lists that say "every one"):
  one cross-class table would do; Equipment's sub-topics (size, cahulaks, stinkpots, protection)
  are linked as `#equipment` because they aren't headings; "Bracers of defense/Defense".
- **PATCH-NOTES**: "A few of them:" introduces 25 kit bullets; some kits' costs are incomplete
  against KITS.md (the Sentinel's −1 on saves, the Ravager's +1 and armour limit, the Assassin's
  daylight hiding); the paragraph explaining [Fixed]/[Changed] sits at the end of Bug Fixes (455)
  instead of the opening; "weapon spec" used without explanation (65); it says it "follows the
  repository", which is untrue of the copy in a zip.
- **release-notes/v2.18.0.md**: "Two weapons is always on" sits under the kits; "the documentation's
  two reviews" is internal process.
- **FEATURES.md**: its intro says it follows the Options tab's order, but has sections the tab
  doesn't ("Always on", "More saves and characters"); "on by default" is said four different ways,
  and "How it works" is "How it is done" three times; "either `.bat` file" when there are four;
  Legcrusher at the fountain (2344) is an always-on script fix under New content; "Saves under their
  names" (2802) is the only section without a "How it works" link; implementation detail at 984,
  1155, 1890, 2497, 2702; a sources paragraph (1052-1060) that is design rationale.
- **ITEMS.md / DICE-LOG.md**: notes about saves from 2.13.4-2.14.0 inside reference tables (ITEMS
  183, DICE-LOG 206): move to the changelog.
- **KITS.md**: "(ASLEEP)" explained three times (250, 312, 343); the Myrmidon's charm list should
  say "Domination (spell and power)" (the code counts both).
- **HOW-THE-GAME-WORKS.md**: "the game never shows thief skills" (785) reads as contradicting
  GAME-BUGS (the mod's screens do); the junk pile's scorpion outcomes (899-903) are unclear.
- **CHANGELOG**: four 2.9.0-2.12.0 releases lack the **Release** bullet the header promises; 2.16.0,
  2.16.1 and 2.18.0's entries don't start with the release line it promises; a paragraph about
  DSCLOG's image size sits before any entry (9-14); entries that only record a changelog edit.
- **CLAUDE.md**: the after-play paragraph repeats the guide (link instead); the essentials list
  leaves out "the look pointer pauses the game", which silently stalls waits.
- **PLAYTESTING.md**: "restart only the dice log" twice (255, 266); one control given two sets of
  coordinates (327-333); the Water note under "Loading and saving" belongs under "After a play"; a
  recompiled-program note tacked onto the git paragraph (200); "SendUserFile" named as if every
  session has it; the setup script tied to an environment by its name ("Google Drive").

## What is fine

- **The Options tab table** in PLAYER-GUIDE.md: every label, order, section and default matches
  `viewer.py` and `launch.py` word for word.
- **Links**: every relative link and `#anchor` in every page resolves (`test_doclinks` passes, and
  separate checks of the player, reference and playtest pages agree).
- **The HTML manual and patch-notes page** are in sync with their sources (the generator's tests
  pass), and every player page has a manual page.
- **Release notes**: no version is missing from v1.0.0 to v2.18.0, and the format is consistent.
- **The developer pages against the code**: every module exists and is named somewhere, every
  backticked `module.attr` exists, all but two of 876 capitalised DSCLOG symbols are found (the two
  are explained), header offsets match `dsclog.asm`, the CLI commands exist, and the tool pins match
  the workflows.
- **CREATURES.md** is in sync with its generator (sizes and the cahulaks column checked row by row).
- **TOOLS.md** lists every tool in `playtest/`, and `saves/README.md` every save.
- **No link** to a public download of the game, Wake of the Ravager or the walkthrough anywhere in
  the repository's non-shipping folders (one research note's link is to check: see F).
