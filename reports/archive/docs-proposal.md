# Documentation: proposed changes (2026-11-17)

*Status: acted on (#100 to #105). It turns [the review](docs-review.md) into changes: the target
layout, what moves where, what each page keeps, the tooling that has to change with it, and the
order to do it in. Section and line references are the review's.*

## Principles

1. **One home for each fact.** Every rule, table and list is written out once; every other page
   links to it in a line.
2. **Each page has one reader and one job**, said in its first line, and holds nothing else.
3. **Players get rules and pictures; developers get offsets, probes and tests.** No memory
   addresses in a player page; no player prose repeated in a developer page.
4. **Current state in references, history in the records.** "An earlier version…", "seen in DOSBox
   on…" and save-compatibility per version go to release notes, the CHANGELOG or
   `playtest/HISTORY.md`.
5. **Ship only what players use.**

## The target layout

| Page | Reader | Its one job | Ships | Change |
|---|---|---|---|---|
| `README.md` (root) | Visitor on GitHub | What the mod is, three steps, links, credits | No | Shorten |
| `obsidian-edition/README.md` | Player | Install, play, the Loader, troubleshooting, version and credits | Yes | Reorder, add |
| `PLAYER-GUIDE.md` | Player | How to play with the mod: classes, rules, the Options tab at a glance (spoiler-free) | Yes | Trim |
| `FEATURES.md` | Player | One short entry per switch and always-on change: what it does, picture, links | Yes | **Rewrite, ~2,800 → ~900 lines** |
| `KITS.md` | Player | The 37 kits: short tables, then each kit's rules | Yes | Split, reshape |
| `WEAPON-SPECS.md` | Player | Weapon specialization: picks, attacks a round, mastery | Yes | **New** (from KITS) |
| `ITEMS.md` | Player (spoilers) | Every item's numbers and where it is | Yes | Tables fixed |
| `PEOPLE.md` | Player (spoilers) | The mod's new people and scenes: Kalzith, Semyon, the champions, the vulture, Legcrusher | Yes | **New** (from FEATURES) |
| `CREATURES.md` | Player (spoilers) | Generated creature tables | Yes | Generator fixed |
| `GAME-BUGS.md` | Player | The game's bugs the mod fixes | Yes | Rule table out |
| `DICE-LOG.md` | Player | Reading the log: colours, layout, every line | Yes | Takes the README's "reading the lines" |
| `HOW-THE-GAME-WORKS.md` | Player | The original game's rules in depth | Yes | Addresses and mod rules out |
| `PATCH-NOTES.md` | Player | The mod against the original game, in brief, linking into FEATURES | Yes (once) | **Trim, ~460 → ~200 lines** |
| `release-notes/vX.md` | Player | What changed since the last version | No (release body) | Takes PATCH-NOTES' version news |
| `CHANGELOG.md` | Developer | One short entry per pull request | No | Archive and trim |
| `CHANGELOG-archive.md` | Developer | Entries before 2.12.0, frozen | No | **New** |
| `DEVELOPMENT.md` | Developer | Entry point: architecture, glossary, requirements, build/test/release, module map | No | **Rewrite, ~970 → ~350** |
| `DEVELOPMENT-INTERNALS.md` | Developer | The dice log, DSCLOG's header and room, memory, reports, the record layouts | No | **New** (rest of DEVELOPMENT.md) |
| `DEVELOPMENT-RULES.md` | Developer | Rule changes, customization, thieving | No | Sections out |
| `DEVELOPMENT-KITS.md` | Developer | Kit mechanics | No | Takes Spell arrows; table deduplicated |
| `DEVELOPMENT-CONTENT.md` | Developer | New spells, items, people, graphics; the bug fixes grouped | No | Regrouped |
| `DEVELOPMENT-SCREENS.md` | Developer | Screens, controls, saves, game speed | No | Retitled; dice-log labelling out |
| `playtest/*`, `CLAUDE.md` | AI sessions | As now | No | Startup reordered, trimmed |
| `reports/` | Developer | Reports with a status line | No | Takes `research_notes/` |

**"Ships: No" for the developer pages** is done with `export-ignore` in
`obsidian-edition/.gitattributes`, not by moving them: their links and the manual's GitHub links
stay as they are.

## Where each shared fact lives

| Fact | Home | Others keep |
|---|---|---|
| Attacks a round, who picks which spec, mastery | WEAPON-SPECS.md | A link (KITS, Player Guide, FEATURES) |
| Kits' gives and costs | KITS.md | Player Guide: one line a kit; PATCH-NOTES: a link |
| Warrior's THAC0 for the Battle Mage, Crusader, Mind Warrior | KITS.md, once | A link from each kit's row |
| Sphere weapon limits | KITS.md, one small table | A link |
| Spell slots | Player Guide (base classes); KITS (the kits' columns only) | — |
| Items' numbers and places | ITEMS.md | Player Guide: spoiler-free list; FEATURES: a paragraph |
| CON regeneration, ages, ranger skills, size dice, two weapons, resting, class limits, prime requisites, level cap | Player Guide | FEATURES: the rule in a sentence and a link |
| Spells as the manual describes them, Turn Undead, the Bowyer, class minimums | HOW-THE-GAME-WORKS.md | A link (FEATURES, DICE-LOG, GAME-BUGS, DEVELOPMENT-*) |
| Rules the game got wrong, with a switch | FEATURES.md (a "corrects the game" mark) | GAME-BUGS: a link |
| Every switch, its default, when it takes effect | Player Guide's "Options tab at a glance" | FEATURES' per-section tables go |
| Getting started, requirements, what it changes on your computer | obsidian-edition/README.md | Root README and Player Guide: a link |
| The fight summary, reading log lines | DICE-LOG.md | README: one example and a link |
| Save compatibility by version | release-notes | README: the rule in two sentences |
| No public links, the private repository | PLAYTESTING.md rule 10 | CLAUDE.md: one line; elsewhere "rule 10" |

## The changes, in seven pull requests

Each goes to `obsidian-edition` from a `claude/` branch, regenerates the manual
(`python -m dsloader.manual`) and patch-notes page, and passes the full test suite
(`test_doclinks`, `test_manual`, `test_patchnotes`, `test_version`, `test_release` above all).
None needs the game except where marked.

### 0. Release 2.18.0 (not documentation)

Run Actions → Release → Run workflow on `main`. This makes the tag, the release, and fixes the
broken links in `release-notes/v2.18.0.md`. Do this first, or say "2.18.0 is coming" until then.

### 1. The small fixes and the gaps (one pull request, low risk)

All 30 of the review's §1, plus:

- **The folder README**: troubleshooting for the remembered game folder (`--game-dir`, or
  `game_dir` in settings.json), "Python is installed but the .bat says it isn't" (32-bit, no
  tkinter), "Out of memory" moved to Known issues; Linux: `python3 -m dsloader view` and
  `python3-tk`; the Python install step ("it carries on; if it says the window doesn't know yet,
  start it again"); `cloud_saves` and `SAVB/C/D` for Show Save; a version, licence and credits
  footer.
- **The root README**: a Requirements link before step 1.
- **FEATURES**: the Wilderness Avenger's ranger stealth.
- **KITS**: "Domination (spell and power)"; "(ASLEEP)" explained once.
- **Player Guide**: "Bracers of Defense" throughout; the Shinobi link text (578); the Cilla and
  Hold Person rows' wording (2063, 2124).
- **HOW-THE-GAME-WORKS**: thief skills (785) and the scorpion outcomes (899-903) made clear.
- **ITEMS**: `short-sword.png` → `metal-short-sword.png` (in `docicons.py`, then regenerate).
- `guidepage.py` deleted, with its two mentions.
- **Pictures**: re-caption `gear.png` and `creation-store-recall.png`; trim the three heavy GIFs
  (fewer frames, same look). Optional, **in the game**: retake `look-box.png` on a creature with MR.

About 150 lines changed. No structure moves.

### 2. What ships (small, touches the build)

- `obsidian-edition/.gitattributes`: `DEVELOPMENT*.md`, `tests/` and `docs/viewer.png`
  `export-ignore`. Saves ~2.8 MB and ~6,100 lines from the zip.
- `release.yml`: stop adding the top-level `patch-notes.html` to the zip (it stays a release asset);
  the zip's copy is `manual/changes.html`.
- `manual.py:42`: GitHub links built with `blob/v{__version__}/` instead of `blob/main/`, so a
  zip's links match its version. (`main`'s own manual keeps working: `test_release` allows either.)
- `test_doclinks.test_shipped_pages_stay_in_the_zip` and `test_release`: updated to the new list.
- `DEVELOPMENT.md` "Making a release": the zip's contents and the CHANGELOG heading.

**Decision:** keep `tests/` in the zip? They're of no use to players, but a player reporting a bug
could run them. Recommended: leave them out.

### 3. The change records

- **PATCH-NOTES.md** (~460 → ~200 lines):
  - Only the mod against the original game. Every mod-to-mod "(was …)" in the kits list, "their
    Options switch is gone" (81) and "Fixes to the mod's own earlier versions" (450-453) go to
    `release-notes/v2.18.0.md` (which already has most) and older release notes.
  - The kits list becomes six lines (one per class group) and a link to KITS.md; "A few of them"
    goes.
  - Bullets capped at about two lines, each ending in a FEATURES link; the [Fixed]/[Changed]
    explanation moves to the opening; the closing Documentation line and the hand-made Contents go
    (the HTML makes its own).
  - "These notes follow the repository" goes; the zip's copy says "as of version X".
  - **Decision:** rename to CHANGES.md? Recommended: **no**. Old release notes link
    `blob/vX/PATCH-NOTES.md`, which stay valid, but people's bookmarks and the README's link
    would break for little gain. Keep the name; fix the content.
- **release-notes/v2.18.0.md**: "Two weapons" moved out of the kits; "the documentation's two
  reviews" out.
- **CHANGELOG.md** (~4,800 → ~1,500 lines):
  - Entries before 2.12.0 (pull request #73 and older) to `CHANGELOG-archive.md`, unchanged; the
    CHANGELOG's release index links there.
  - The section labels fixed at **New / Changed / Fixed / Docs / Dev**, said in the header.
  - Each release's entry starts with "Obsidian Edition X ([release notes](…))", including 2.16.0,
    2.16.1 and 2.18.0; the four bare release bullets get **Release**.
  - The Unreleased section keeps one bullet for the elven leader's fix; the research goes to
    `reports/opends-cross-read-2026-11-16.md`, which it cites.
  - The DSCLOG image-size paragraph (9-14) to DEVELOPMENT-INTERNALS' limits.
  - "the user's call/report/ask" (67) → "(owner's decision)" or nothing.
  - Entries that only record a changelog edit merged into their neighbours; #96 added.
  - Long entries since 2.12.0 (#89 594 lines, #95 289, #86, #90, #55) are **not** rewritten:
    history is history. The rule applies from here on (DEVELOPMENT.md says so).

### 4. The player entry points

- **obsidian-edition/README.md**, in this order: requirements → one-time setup (with "back up
  your saves", now under Updating) → every time you play → the Loader's window (the dice log
  part shortened: "Reading the lines as written" and the colour key move to DICE-LOG) →
  updating → compatibility (two sentences; the per-version detail to release notes) →
  uninstalling (the one copy of "what it changes on your computer") → troubleshooting → known
  issues → version, licence, credits. Memory tools, layouts and the `.asm` sources down to one
  clause. The unblocking paragraph to three lines. Dark Sun Recompiled to its own short section.
- **Root README**: the pitch, three steps linking the folder README's Requirements and Running it,
  the docs list (one list, the folder README's wording), credits. "What's new" to one line and a
  link.
- **PLAYER-GUIDE.md** (~2,160 → ~1,700):
  - Getting started to one line and a link.
  - The eight classes' repeated blocks: the "Multiclass: … in More than one class" and "Some kits
    rule out a change of class" bullets go (said once at the top of Classes); the eight magic
    weapon lists become one "Magic weapons by class" table under Equipment; the backstab figures
    linked, not repeated.
  - Equipment's sub-topics (Size, Cahulaks, Stinkpots, Polearm reach, Armour, Protection, Acid)
    become `###` headings, and the `#equipment` links point at them.
  - **The Options tab at a glance**: one row per radio group; "Elsewhere in the Loader" added
    (Game window, Text size, Readable layout, Show details, Show unlabelled rolls); the always-on
    list complete (or "among them" with a link); the intro's double link made one.
  - Quality of life keeps only the always-on keys (S, T, M/U/I).
  - The attacks a round table, CON, ages and the rest stay here or move to WEAPON-SPECS per the
    table above.

### 5. One home for each fact (the big one; best as two pull requests)

**5a. Kits, items, weapon specs and the reference pages**

- **WEAPON-SPECS.md** (new, ~200 lines, from KITS.md:373-574 and Player Guide 960-993): the 16
  specs, who picks what, attacks a round (one table, the Player Guide's rows with KITS' Justifier
  note), grand mastery dice, starting weapons, the level-up window. A new manual page
  (`weapon-specs.html`, "Weapon specs") in `manual.py`'s `PAGES`; FEATURES#weapon-specialization
  and the Options label's link point at it.
- **KITS.md**: per class, a table of one-line Gives and Costs, then a `####` subsection per kit
  for the long rules (Spellarcher arrows, Shinobi learning, Seeker limits, the Crusader's and
  Mind Warrior's attacks). The warrior's-THAC0 text and the sphere weapon limits written once. The
  four-row specs table becomes a sentence; blank cells "—"; the Brute's UI note under the table;
  the multiclass race list dropped.
- **ITEMS.md**: Contents headings real; one item per Prices row; game items given a place, not "a
  chest"; "The mod's" column → "Notes", with the Fine Bow its own row; the "By weapon spec" table
  kept as the index and the main table's Type column dropped; legacy-save notes out.
- **CREATURES.md** via `doccreatures.py`: the Race column dropped from Monsters; letters only for
  size; a "where met" note for the three Guards, Slave and Worker; the spoiler lead line; the
  generator note to DEVELOPMENT-CONTENT; the double blank line. Needs the game's SEGOBJEX.GFF to
  regenerate (set up with `playtest/setup_game.sh`).
- **DICE-LOG.md**: one example per row; long Meanings to the "in more detail" paragraphs below;
  Turn Undead to a gloss and a link; the option links to FEATURES; takes the README's colour key
  and "reading the lines"; legacy-save note out.
- **GAME-BUGS.md**: "Rules it got wrong, with a switch" and "Two more, with a switch" move to
  FEATURES; the class minimums linked.
- **HOW-THE-GAME-WORKS.md**: addresses and the CLI command to DEVELOPMENT-RULES; the mod's
  rule change detail stays here as the one home for "as the manual describes" (retitle the page
  "How the game works, and the manual's rules"); the cleric spell table's "The log" column becomes
  a legend.

**5b. FEATURES.md and PEOPLE.md**

- **FEATURES.md** rewritten (~2,800 → ~900): the intro says it follows the Options tab, with
  "Always on" and "Saves" at the end. Each entry: what it does in 2-5 sentences, the switch, the
  picture, "Rules:" and "How it works:" links. "On by default" said once in the intro; "How it
  works" everywhere; the per-section summary tables go (the Player Guide's at-a-glance is the
  one). Moves out: rule tables (to the Player Guide), the spells table (to HOW-THE-GAME-WORKS),
  the new items (to ITEMS), story (to PEOPLE), Legcrusher's fix (to GAME-BUGS), the frame-rate
  measurements (to DEVELOPMENT-SCREENS), the sources paragraph and implementation notes (to
  DEVELOPMENT-RULES), picking pockets' edge cases (to HOW-THE-GAME-WORKS).
- **PEOPLE.md** (new, spoilers, ~200 lines): Kalzith, Semyon, the Trustee and Dinos, the
  champions' bout, the vulture meal, Legcrusher at the fountain: what happens, in a paragraph or
  two each, without quoting every line. A manual page (`people.html`, "People", spoilers).

### 6. The developer pages

- **DEVELOPMENT.md** (entry point, ~350 lines): what the mod is technically; an architecture
  diagram (Loader → DOSBox config and UMBPLUS → the patched DSUNLOG.EXE → DSCLOG → the Loader
  reading and writing memory, the item gate); a glossary (Loader, DSCLOG, DSUNLOG.EXE, "the
  Loader's copy", probe, site, the far block, the tail, the item gate; the capitals convention for
  labels); requirements (Python 3.8+ 64-bit, tkinter, NASM 2.16.01, unicorn 2.1.4); build, test
  (including one test: `python -m unittest tests.test_x`) and release; the folder table with
  `.github/`, `reports/`, `find-python.bat` and which `.bat` runs which command; **a module map**
  (all 123 modules, one line each, grouped core / game data / rules / kits / content / graphics /
  UI / docs, each with its section); a contributor checklist (a probe or site, a flag, a header
  field, a new page).
- **DEVELOPMENT-INTERNALS.md** (new, the rest of DEVELOPMENT.md): how the dice log works, with a
  "Labelling rolls" part taking SCREENS' searches, Bowyer and ability-check sections; the header;
  room and memory (one DSCLOG size); crash, freeze and item-watch reports (item watch out of
  "changing the item lists"); reading and writing memory; what's known of the save and records
  (each row naming its `game.SHEET_*` constant).
- **Moves**: Spell arrows → KITS; the Trustee's script fixes → CONTENT's script bugs; the Bowyer's
  Dunesong change → CONTENT's new items; Sounds for hiding and picking pockets → beside Picking
  pockets; CONTENT's bug-fix sections grouped in GAME-BUGS' order; the RULES Kits stub to one line.
- **DEVELOPMENT-KITS**: the effect table's duplicate rows merged, the Sentinel added to "to hit",
  the Kits column dropped (the bullets have it); "split from the rules" gone; "How they're
  checked" names the test classes.
- **DEVELOPMENT-SCREENS** retitled "Screens, controls and saves"; game speed takes FEATURES'
  measurements.
- **Everywhere**: "launcher" → Loader; "helper" → DSCLOG where it means the program; "dice log"
  unhyphenated; version narratives to the CHANGELOG; "seen in DOSBox" passages to one "Verified:
  [log]" link; the credits to one acknowledgements list in DEVELOPMENT.md; the "not yet seen in
  play" notes checked against the logs and gathered in one Unverified list.

`test_doclinks`' "How it works" test and every anchor into DEVELOPMENT.md that moves to INTERNALS
need updating together; the tests will list them.

### 7. The playtest kit, CLAUDE.md and reports

- **PLAYTESTING.md** (~1,170 → ~700):
  - **The startup procedure as one numbered checklist** in the order run: environment → start.sh →
    loadsave → window 320x240 → buildcheck → guard and Monitor → test log. §2's non-startup items
    (tests, the release zip, the walkthrough, Wake of the Ravager) to the recipes and RESEARCH.
  - The memory offset material (437-557, 900-1097) to RESEARCH.md or DEVELOPMENT-INTERNALS, each
    recipe keeping the tool's name; dated anecdotes to HISTORY, the log link kept.
  - Water → "After a play"; the recompiled note → RESEARCH; "restart only the dice log" once; one
    set of coordinates for the level button (**in the game**: measure it); SendUserFile "where
    available"; the environment described, not named.
  - The private-repository rule once, as rule 10.
- **CLAUDE.md**: the essentials in the checklist's order; "the look pointer pauses the game"
  added; the after-play paragraph to a line and a link; water → ROUTE.md; **one Git paragraph**:
  work on `claude/<task>`, rebase onto `origin/obsidian-edition`, pull request into
  `obsidian-edition`, which goes to `main` at a release; the old remote note out.
- **HISTORY.md**: strictly by topic, the dated sections folded in, the empty stub gone, the date
  index last, doubling as the logs' index.
- **logs/**: `logs/README.md` (one line a log); the `.sh`, `.txt`, `.diff`, `.asm` artefacts to
  `logs/files/`; the unused PNGs deleted after a check of wildcard references.
- **saves/README.md** wrapped, the repeated sentence said once, `dsloader/` on the two module names.
- **TOOLS.md**: the scripts whose first header line is cut get a shorter one; regenerate.
- **chestuse.sh** and **setitem.py**: from §1, if not done there.
- **reports/**: `Combat log design across games.md` → `combat-log-design-research.md`, its notes →
  `reports/combat-log-design-research/`, `research_notes/` removed; status lines on each report;
  the handoff and the research into `reports/archive/`; the doubtful link in the notes checked and
  dropped if it's a download.

## Order and size

| # | Pull request | Size | Risk | Needs the game |
|---|---|---|---|---|
| 0 | Release 2.18.0 | — | Low | No |
| 1 | Small fixes and gaps | ~150 lines | Low | Only an optional retake |
| 2 | What ships | ~40 lines | Medium (the build) | No |
| 3 | Change records | ~3,500 lines moved, ~300 rewritten | Low | No |
| 4 | Player entry points | ~600 lines | Low | No |
| 5a | Kits, items, specs, reference pages | ~1,500 lines | Medium (anchors) | Only to regenerate CREATURES |
| 5b | FEATURES and PEOPLE | ~2,000 lines | Medium (anchors, links into FEATURES) | No |
| 6 | Developer pages | ~2,500 lines | Medium (anchors) | No |
| 7 | Playtest kit, CLAUDE.md, reports | ~800 lines | Low | One measurement |

1, 2 and 3 are independent and can go in any order. 4 before 5 (5 links into the guide's new
headings). 6 and 7 are independent of the player pages. Moving text is the bulk of it: nothing is
cut that isn't said elsewhere, except the history noted in 3.

## Decisions needed

| # | Question | Recommended |
|---|---|---|
| 1 | Release 2.18.0 now? | Yes |
| 2 | Developer pages out of the zip, by `export-ignore` (not moved)? | Yes |
| 3 | `tests/` out of the zip too? | Yes |
| 4 | Rename PATCH-NOTES.md to CHANGES.md? | No: fix the content, keep the name |
| 5 | Split weapon specs into WEAPON-SPECS.md? | Yes |
| 6 | Move the story content to a new PEOPLE.md (spoilers)? | Yes |
| 7 | FEATURES as a short catalogue (~900 lines), its rule tables moved to the Player Guide? | Yes |
| 8 | Split DEVELOPMENT.md into an entry point and DEVELOPMENT-INTERNALS.md? | Yes |
| 9 | Archive CHANGELOG entries before 2.12.0? | Yes |
| 10 | "The user's call" in the CHANGELOG: reword or drop? | Drop where it adds nothing, "(owner's decision)" where it matters |
| 11 | Retake `look-box.png` and measure the level button in the game? | Optional; later |
