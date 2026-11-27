# Obsidian Edition: development

The developer's entry point: what the mod is inside, the words these pages use, how to build, test
and release it, every module of the Loader with the section that explains it, and what to do when
adding to it. How each part of the [README](README.md) and the [features page](FEATURES.md) is done
is on the pages under [How each part works](#how-each-part-works).

Technically, Obsidian Edition is two programs and a set of data files around the GOG release of
*Dark Sun: Shattered Lands*, a 16-bit real-mode Borland C++ program (`DSUN.EXE`) run in DOSBox
0.74. **The Loader** (`dsloader/`, Python, tkinter for its window) writes a patched copy of the
game and copies of its data files, starts DOSBox, and then reads and writes the game's memory from
outside, through DOSBox's process. **DSCLOG** (`dos/dsclog.asm`, NASM, built to `DSCLOG.EXE`) is
a small DOS program that stays in upper memory beside the game and answers the interrupts the
patched game calls: it records the dice, draws the in-game additions and makes the rule changes
count. The two talk through DSCLOG's header in the game's memory. Nothing of the game's own files
is changed.

DOSBox-X is the default engine whenever the Loader finds one (it comes with the Windows release;
on Linux and macOS it is the player's own; `dosboxx.py`), and GOG's DOSBox 0.74 is used when none is
found or when it is chosen. Under DOSBox-X the Loader writes it a configuration of its own and reads
and writes the game's memory through DOSBox-X's memory file, not its process; DSCLOG and the patched
game are the same under both ([the engine](DEVELOPMENT-SCREENS.md#the-engine-gogs-dosbox-or-dosbox-x)).
Where these pages say "DOSBox" alone they mean 0.74, the engine the mod was built and measured on.
DOSBox-X has been played on Linux; on Windows the game has started under it (it loads and its music
plays) and a fuller play is under way; on macOS its side of the Loader is written and unit-tested
but not yet run.

## Contents

- [Architecture](#architecture)
- [Glossary](#glossary)
- [Requirements](#requirements)
- [The folders](#the-folders)
- [Build](#build)
  - [Generated pages](#generated-pages)
- [Tests](#tests)
- [Making a release](#making-a-release)
- [From a command prompt](#from-a-command-prompt)
- [Module map](#module-map)
- [Contributor checklist](#contributor-checklist)
- [How each part works](#how-each-part-works)
- [Unverified](#unverified)
- [Acknowledgements](#acknowledgements)

## Architecture

The steps are told in full in [How the dice log works](DEVELOPMENT-INTERNALS.md#how-the-dice-log-works).

```
 the Loader (dsloader/, Python)
   |  writes, before DOSBox starts (launch.py, gamepatch.py, icons.py, dataitems.py ...):
   |    dos/DSUNLOG.EXE    the game's DSUN.EXE with a few hundred INTs in place of its code (PATCHES)
   |    the Loader's copies of SEGOBJEX.GFF, RESOURCE.GFF, GPLDATA.GFF and some regions' files
   |    the DOSBox config: EMS off, then UMBPLUS.COM, then lh DSCLOG.EXE, then DSUNLOG.EXE, GAMEEND.COM
   v
 DOSBox 0.74 (GOG's)
   |  UMBPLUS.COM     moves upper memory's start down to CA00h
   |  DSCLOG.EXE      loads into upper memory and stays: its 64 KB segment, its tail, its far block (HMA)
   |  DSUNLOG.EXE     the game: each patched place calls DSCLOG (INT 60h-65h, 80h-FFh, sites of INT 98h);
   |                  DSCLOG also hooks INT 21h (the Loader's copies of files), 33h (mouse), 16h (keys)
   |  GAMEEND.COM     after the game: an error kept on screen for the crash report
   v
 DSCLOG's header (found by its signature, HDR_SIG) in the game's memory
   |  DSCLOG -> Loader: the dice ring, the text buffer, requests (pick a pocket, a stats update ...)
   |  Loader -> DSCLOG: answers, the combat log's picture, labels, kit bytes, switches (RULES words)
   v
 the Loader again, every 20-50 ms (dicelog.DiceLog)
      reads: the ring and the game's records (guestmem.GuestMemory over process.py)
      writes: the game's records; any write to the item lists through the item gate (itemgate.py),
              which waits until the game leaves them be and holds DOSBox still while it writes
```

## Glossary

- **The Loader**: the Python program in `dsloader/` (its window, the dice log, the command line);
  "the Dark Sun Obsidian Edition Loader" in full. `dsloader` is its package's name.
- **DSCLOG**: the DOS program in `dos/dsclog.asm`, built to `DSCLOG.EXE`, which stays in memory
  beside the game. Its routines and variables are named in capitals on these pages (`SC_FIND`,
  `FAR_SEG`); in `dos/dsclog.asm` their labels are lower case (`sc_find`, `far_seg`). Its constants
  (`equ`) are in capitals in both.
- **DSUNLOG.EXE**: the patched game, written by the Loader into `dos/` at each start
  (`gamepatch.py`'s `PATCHES` applied to the player's `DSUN.EXE`).
- **The Loader's copy**: a game data file (`SEGOBJEX.GFF`, `RESOURCE.GFF`, `GPLDATA.GFF`, a
  region's file) as the Loader writes it into `dos/`, with the mod's items, pictures, texts and
  script repairs; DSCLOG's `INT 21h` hook opens it in place of the game's. The game folder's own
  files are never changed.
- **Probe**: a patched place in DSUNLOG.EXE that calls DSCLOG through an interrupt vector of its
  own (`PROBE_X`, `VEC_X`).
- **Site**: a patched place that shares a vector (`INT 98h`, `VEC_CR_SPELLS`) with a site number
  after the `INT`; DSCLOG finds the routine in `site_tab`.
- **The far block**: DSCLOG's big buffers (the dice ring, the text buffer, the panel's picture,
  the shadows' tables), in the HMA above 1 MB: [the far block](DEVELOPMENT-INTERNALS.md#the-far-block).
- **The tail**: the part of `DSCLOG.EXE` after its 64 KB segment, loaded and kept with it, for
  tables only one routine reads: [DSCLOG's segment](DEVELOPMENT-INTERNALS.md#dsclogs-segment).
- **The header**: the fields DSCLOG and the Loader share, at the start of DSCLOG's image:
  [DSCLOG's header](DEVELOPMENT-INTERNALS.md#dsclogs-header).
- **The item gate**: the one way the Loader writes to the game's item lists (`itemgate.py`):
  [the item gate](DEVELOPMENT-INTERNALS.md#the-item-gate).
- **The dice log**: the Loader's account of every roll and what it was for (`dicelog.py`); the
  player's page is [DICE-LOG.md](DICE-LOG.md).
- **A helper**, on these pages, is a helper function; the DOS program is always DSCLOG.

## Requirements

- **Python 3.8 or later, 64-bit** (32-bit Python can't read 64-bit DOSBox's memory), with tkinter
  for the window; no other package to play. `dsloader/find-python.bat` looks for one and offers to
  install it. The workflows test on Windows with Python 3.12, x64.
- **NASM 2.16.01** to rebuild DSCLOG and the other DOS programs: the committed files are built with
  it and the workflows install it (NASM 3 encodes DSCLOG otherwise, so the rebuild checks fail and
  the emulated tests read the wrong symbols). `DSUN_REQUIRE_NASM=1` makes its absence a failure
  rather than a skip.
- **unicorn 2.1.4** (`pip install unicorn==2.1.4`) for the tests that run DSCLOG's code in a CPU
  emulator.
- **The GOG release** of the game (`DSUN.EXE` of 611,408 bytes) to play, and for the tests that
  read its files ([Tests](#tests)). Never from a public link: see the playtest kit's rule.

## The folders

| Folder or file | What it holds |
|---|---|
| `dsloader/` | the Loader: one module for each part ([Module map](#module-map)) |
| `dsloader/find-python.bat` | what every `.bat` calls first: finds a 64-bit Python 3.8+ with tkinter (`PY`, `PYW`) or offers to install it with winget |
| `dsloader/fonts/` | the Latin sets of the web pages' fonts, with their licences (`pagefonts.py`) |
| `dsloader/sound-data/` | the samples of the sounds for hiding and picking pockets (`hide.wav`, `pick.wav`), and `make.py`, which made them (`sounds.py`) |
| `dsloader/pagestyle.css` | the web pages' look, the manual's and the patch notes' |
| `dos/` | DSCLOG (`dsclog.asm`, built to `DSCLOG.EXE`), `umbplus.asm` (`UMBPLUS.COM`), `gameend.asm` (`GAMEEND.COM`), `least_scores.asm` and its table (assembled into a patch); the Loader writes DSUNLOG.EXE and its copies of the game's files here |
| `layouts/` | the game's memory layout (`shattered_lands.json`), for the Loader's window and Memory tools |
| `tests/` | the unit tests, and `make_fake_party.py` for [practising without the game](DEVELOPMENT-INTERNALS.md#practising-without-the-game) (not in the release zip) |
| `docs/` | the screenshots the documentation shows; `docs/items/`, the item icons (`docicons.py`), and `docs/creatures/`, the creatures' figures (`doccreatures.py`) ([Generated pages](#generated-pages)) |
| `*.bat` | what players double-click: `Start Obsidian Edition.bat` runs `view`, `Start Game with Dice Log.bat` `launch`, `Play Dark Sun (in-game rolls).bat` `play` (no console), `Play Wake of the Ravager (in-game rolls).bat` `play --ravager`, `Play Wake of the Ravager.bat` `launch --ravager`, `Show Save.bat` `save` on the file dropped on it |
| `README.md`, `PLAYER-GUIDE.md`, `FEATURES.md`, `KITS.md`, `WEAPON-SPECS.md`, `ITEMS.md`, `PEOPLE.md`, `CREATURES.md`, `GAME-BUGS.md`, `DICE-LOG.md`, `HOW-THE-GAME-WORKS.md` | the player's pages (made into the manual's web pages; `CREATURES.md` by `doccreatures.py`) |
| `DEVELOPMENT*.md` | these pages (not in the release zip) |
| `manual/` | the manual: the player's pages and the patch notes as web pages, made by `manual.py` ([Build](#build)); the Loader's **Help** opens `manual/index.html` |
| `../PATCH-NOTES.md`, `../patch-notes.html`, `../CHANGELOG.md`, `../CHANGELOG-archive.md`, `../release-notes/` | the repository's root: the patch notes and their web page, the record of every pull request (#73 and older in the archive), and each release's notes |
| `../.github/workflows/` | `tests.yml` (the tests on Windows at every push and pull request), `release.yml` ([Making a release](#making-a-release)) and `test-package.yml` (a pull request's test download: the release's zip with DOSBox-X, as a run artifact); `../.github/scripts/add_dosbox_x.py` is the step both put DOSBox-X in with |
| `../playtest/` | the in-game test kit: tools that drive the game in DOSBox, saves, logs and [its guide](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/PLAYTESTING.md); outside this folder, so never in the zip |
| `../reports/` | research and reviews, each with a status line; `reports/archive/` for the finished ones |

## Build

After changing `dos/dsclog.asm`, rebuild DSCLOG with NASM 2.16.01:

```
nasm -f bin -I dos/ -o dos/DSCLOG.EXE dos/dsclog.asm
nasm -f bin -I dos/ -o dos/DSCLOG2.EXE dos/dsclog2.asm
```

Both include `dos/save_bands.inc` (the saving throws' code and tables), hence `-I dos/`. The build fails if DSCLOG outgrows its 64 KB segment or the room it has in upper memory ([Room
and memory](DEVELOPMENT-INTERNALS.md#room-and-memory)). The header's signature (`DSCLOGvf` now:
after Z, lowercase) goes up whenever DSCLOG and the Loader must change together (`HDR_SIG` in
`dsloader/dicelog.py`), so a Loader never talks to an older DSCLOG.

The creation screen's least scores routine is assembled into `gamepatch.py`'s `least_scores` patch
bytes from `dos/least_scores.asm` and its table `dos/least_scores_table.inc` (`test_least_scores`
and `test_audit_builds` check the bytes match). The post-game check that keeps an error on screen
for the crash report, and the program that moves upper memory down before DSCLOG loads, are built
the same way:

```
nasm -f bin -o dos/GAMEEND.COM dos/gameend.asm
nasm -f bin -o dos/UMBPLUS.COM dos/umbplus.asm
```

The web pages are made from Markdown. Edit the Markdown, then run the module:

- **The manual**, `manual/` (`python -m dsloader.manual`): thirteen pages, each from its Markdown, which
  stays the source and reads the same on GitHub. `index.html`, the start page the Loader's
  **Help** button opens, is made from `README.md`; then `player-guide.html`, `features.html`,
  `kits.html`, `ravager.html`, `weapon-specs.html`, `items.html`, `creatures.html`, `people.html`,
  `game-bugs.html`, `dice-log.html`, `how-the-game-works.html` and `changes.html`
  (`../PATCH-NOTES.md`, read by `patchnotes.py`). `manual.PAGES` lists them (every player's page
  of `obsidian-edition/`, the DEVELOPMENT pages aside: `test_manual` checks). Each page has a bar
  of all thirteen (the spoiler pages marked) and an index
  of its own sections; the pages share `manual/manual.css` (`pagestyle.css` and the fonts). The
  generator rewrites the links, not the Markdown: a link to another of the pages (`KITS.md#x`,
  `README.md`, `../PATCH-NOTES.md` or its GitHub address) goes to its HTML file with the same
  anchor, a picture to `../docs/`, and anything else of the repository (these pages, the
  changelog) to its GitHub address at the release's tag. Headings keep GitHub's anchors (a
  repeated one `-1`, `-2`), so the Markdown's own links land. A page needing Markdown the generator
  doesn't know shows it raw: `tests/test_manual.py` looks for that, and for links that don't land.
- **The patch notes' page**, `../patch-notes.html`, from `../PATCH-NOTES.md`
  (`python -m dsloader.patchnotes`): one page to share, with a button that copies the Markdown,
  attached to the release.

Both carry their fonts (`pagefonts.py`), so they load nothing from the internet and work opened
straight from the unzipped folder.

### Generated pages

Two more are made from the game's own data, so they need its folder (the one holding `DSUN.EXE`):

```
python -m dsloader.docicons GAME_FOLDER [--ravager WOTR_FOLDER]  # docs/items/*.png, the icons in ITEMS.md
python -m dsloader.doccreatures GAME_FOLDER   # CREATURES.md and docs/creatures/*.png
```

`docicons` reads the Loader's copy of `SEGOBJEX.GFF` in `dos/` (start the game from the Loader once
first, so it is there with the mod's icons) and the game's palette; it says which icons it
couldn't draw (a new item needs its line in `docicons.ICONS`: [New
items](DEVELOPMENT-CONTENT.md#new-items)). `doccreatures` reads the game's `SEGOBJEX.GFF` and
palette, and takes each creature's size from `sizes.py`, whether it can be tangled from
`cahulaks.why_not`, and where a name more than one kind of creature has is met from
`doccreatures.NOTES` (found from the regions' ETAB and named as the cluebook names the regions): run
it again after changing any of them. (CREATURES.md itself says nothing of how it is made.)

## Tests

From `obsidian-edition/`, all of them, or one module, class or test:

```
python -m unittest discover -s tests
python -m unittest tests.test_kits
python -m unittest tests.test_kits.KitEffectTests
```

With the game's files (the Loader's patched copies are made from them; a game folder such as the
one the playtest kit's `setup_game.sh` installs):

```
G=/path/to/game; DSUN_GPLDATA=$G/GPLDATA.GFF DSUN_OBJECTS=$G/SEGOBJEX.GFF \
    DSUN_RESOURCE=$G/RESOURCE.GFF python -m unittest discover -s tests
```

Some tests need more, and are skipped without it (each skip says what it needs, which is the list
to trust when a test file is added):

- **unicorn**: the tests that run DSCLOG's interrupt handlers in a CPU emulator (`test_dsclog`,
  `test_gamepatch`, `test_shadows`, `test_dsclog_drawing`, `test_squares_drawing`, `test_cahulaks`, `test_sizes`,
  `test_held`, `test_least_scores`, `test_manual_spells`, `test_manual_group3`, `test_group4`,
  `test_interrupt_hygiene`, `test_squares_drawing`, `test_quicksave`'s `QS_KEY` and `SAVE_TICK` among them).
- **NASM**: the rebuild checks (`test_audit_builds`, `test_header_offsets`, `test_least_scores`,
  `test_dsclog_drawing`, `test_squares_drawing`, `test_scroll_interrupts`, `test_interrupt_hygiene`).
- **tkinter**: the window's tests (`test_theme`, `test_partyview`, `test_find`,
  `test_viewer_options` (the Engine section among them), `test_journal`'s and `test_quests`' tab, and `test_compiles`' window part; `test_viewer_settings` also needs a
  display, so run it under `xvfb-run` on a machine without one). Linux's Python often lacks it.
- **The game's files**, named by environment variables: `DSUN_GPLDATA` (its `GPLDATA.GFF`:
  `test_scriptnumbers`, `test_scriptfixes`, `test_pehtuclchest`, `test_champions`,
  `test_audit_flags`, `test_journal` (no script uses the journal's numbers), `test_quests` (the quest table held to
  the scripts), `test_sounds`, which reads the `RESOURCE.GFF` beside it, and `test_reach` and
  `test_stinkpots`, which read the `DSUN.EXE` beside it), `DSUN_OBJECTS` (its `SEGOBJEX.GFF`, with
  `GPLDATA.GFF` beside it: `test_figures`, `test_pehtuclchest`, `test_worldgear`,
  `test_audit_objects`, `test_cahulaks`, `test_sizenames`, `test_icons`, `test_scriptfixes`,
  `test_group4`, which falls back to `/tmp/playtest/inst/SEGOBJEX.GFF`, the playtest kit's game)
  and `DSUN_RESOURCE` (its `RESOURCE.GFF`: `test_kitpages`, `test_spelltexts_fit`,
  `test_spellgrid`, `test_hitchance`'s header fit, `test_hover`'s label fit).

The **Obsidian Edition tests** workflow (`.github/workflows/tests.yml`) runs them on Windows, with
unicorn 2.1.4 and NASM 2.16.01, on every push to `obsidian-edition` and every pull request that
touches the mod or the root's pages.

Tests that guard the whole project rather than one module:

| Test | What it checks |
|---|---|
| `test_doclinks` | every relative link and anchor in the Markdown pages goes somewhere; what the release zip leaves out; and each section of the player's pages that a DEVELOPMENT page explains links to its explanation |
| `test_compiles` | every module of the Loader compiles, the window's too |
| `test_flagrange` | the Loader's game flags are in 756-807 and no two share one ([the table](DEVELOPMENT-INTERNALS.md#the-loaders-game-flags)) |
| `test_audit_flags` | every module constant from 756 up, Alagorn's overflow flags and aging's count among them, found by itself: no two share a number, and (with `DSUN_GPLDATA`) the scripts copy uses no flag the modules don't have |
| `test_audit_objects` | each object and picture the Loader adds to its SEGOBJEX copy is made by one module only |
| `test_scriptnumbers` | the Loader's scripts have a number each, their calls land inside them, and each fits the game's script buffer |
| `test_dsclog`'s `test_fits_upper_memory` | what DSCLOG puts in upper memory fits the room DOSBox gives it |
| `test_header_offsets` | every field of DSCLOG's header is at the offset its comment gives, in a fresh build; every `TSR_*` constant of the Loader's is a field's; the spell arrows' table and names are `spellarrows.ARROWS`' and the names' room `names.EXTRA` |
| `test_interrupt_hygiene` | DSCLOG's handlers leave interrupts as their caller had them, INT 33h's handler forgotten when the game removes it, the timer's tick with the direction flag clear, the scenes' arrow off the screen during a latch copy, A20 turned on again |
| `test_version` | the version is the same in `__init__.py`, the patch notes and the front page, and its release notes exist |
| `test_release` | the Release workflow zips and publishes as below, what the zip leaves out (and that nothing shipped imports it), and the patch notes' page's links work |
| `test_manual`, `test_patchnotes` | the web pages are up to date with their Markdown (every player's page of `obsidian-edition/` one of the manual's), and their links work: each of the manual's lands on a file in the zip and an anchor its page has, with no link to a Markdown file and no id twice; Help opens the manual's start page |

The unit tests don't play the game. For anything DSCLOG or a script touches, check it in the game
too: [the playtesting guide](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/PLAYTESTING.md)
has the tools and how to use them.

## Making a release

The **Release** workflow (`.github/workflows/release.yml`) runs the tests on Windows, zips the
`obsidian-edition` folder as `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip` with `git
archive` (so only what is committed goes in), and publishes the zip and `../patch-notes.html` with
`release-notes/v<version>.md` as its notes (`tests/test_release.py` checks it does). It adds
DOSBox-X's own 64-bit Windows program to the zip's `dosbox-x` folder, with its licence and a
`SOURCE.txt`, and puts DOSBox-X's source archive beside the zip
([DOSBox-X in the release](DEVELOPMENT-SCREENS.md#the-engine-gogs-dosbox-or-dosbox-x)).

The release zip is the `obsidian-edition` folder as `git archive` makes it, less what
`obsidian-edition/.gitattributes` marks `export-ignore`: the developer pages (`DEVELOPMENT*.md`),
`tests/`, `docs/viewer.png` and the developers' tool `dsloader/questdraft.py` (no module that ships
imports it: `test_release` checks), which stay in the repository and are linked from the manual at
the release's tag (and from the Markdown pages at `main`), and git's own `.gitattributes` and
`.gitignore`. It holds the player's pages, the manual (whose `changes.html` is the zip's copy of
the patch notes), the Loader, `dos/`, `layouts/`, `docs/` and the .bat files. The top-level
`patch-notes.html` is not in the zip; it is attached to the release as an asset of its own.

Before it:

1. Set the version in `dsloader/__init__.py` (`__version__`), the patch notes' "Current version"
   and the version in their italic status line ("These notes describe version X, … not yet in a
   release": `test_patchnotes` needs "not yet in a release"), and the front page's "**Obsidian
   Edition ...** is out"; `tests/test_version.py` checks they agree and that the release notes
   exist.
2. Finish `release-notes/v<version>.md` and the CHANGELOG's entry, and rebuild `DSCLOG.EXE` if its
   source changed, and the web pages (`python -m dsloader.manual` and `python -m
   dsloader.patchnotes`) if their Markdown did; `test_manual` and `test_patchnotes` fail until they
   are.
3. Run the tests with the game's files too (they never run in CI: the game isn't in the
   repository), from `obsidian-edition/`, the game folder `G` an unmodded GOG install (the
   playtest kit's `setup_game.sh` makes one at `/tmp/playtest/inst`):
   `DSUN_GPLDATA=$G/GPLDATA.GFF DSUN_OBJECTS=$G/SEGOBJEX.GFF DSUN_RESOURCE=$G/RESOURCE.GFF python -m
   unittest discover -s tests`. 43 tests more run than without them (the number claims, the patched
   copies, the script repairs against the real bytes); only the window's tests may be skipped then
   (tkinter).
4. Check in the game anything DSCLOG or a script touches ([the playtesting
   guide](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/PLAYTESTING.md)).
5. As the last commit before the merge, rename the CHANGELOG's "## Unreleased (branch
   `obsidian-edition`)" to "## Pull request #N (merged DATE)", with the release pull request's
   number, the day it is merged, and "merged DATE" a link to the pull request, as the other headings
   have it (2.17.1 and 2.18.0 were done so). Start a release's entry with the line "Obsidian
   Edition X", its release notes (`release-notes/vX.md`) linked after it in brackets, and use only
   the section labels New, Changed, Fixed, Docs and Dev. Point the release's link in the list of
   releases at the top of the CHANGELOG to the new heading's anchor (`#pull-request-N-merged-DATE`;
   `test_doclinks` fails otherwise).
6. Merge to `main`, then push the tag `v<version>`, or run the workflow by hand (Actions → Release
   → Run workflow), which makes the tag.

The zip's pages link to what stays outside it (the root's patch notes, CHANGELOG and release
notes, these pages) by their GitHub address.

## From a command prompt

What the `.bat` files do, from a command prompt (`dsloader` is the program's internal name):

```
python -m dsloader launch                        # the game with the dice log, and the Loader's window
python -m dsloader launch --ravager [FOLDER]     # Wake of the Ravager, and the Loader's window
python -m dsloader view                          # the Loader's window only, game not started
python -m dsloader play                          # the game with the in-game additions, no window
python -m dsloader dicelog                       # the dice log in the command prompt
python -m dsloader checks                        # the scripts' thief skill and ability checks (spoilers)
python -m dsloader save C:\path\to\SAVE01.SAV   # the party stored in a save
python -m dsloader processes                     # is DOSBox found?
```

After `launch` or `play`, `--window-scale 1` to `4`, `--fullscreen` or `--windowed` choose the
game's window as **Game window** does, and `--recompiled PROGRAM` runs Dark Sun Recompiled in place
of DOSBox from then on (`--dosbox` goes back: [the README](README.md#dark-sun-recompiled)).
`--game-dir` names the game's folder (for `launch`, `play` and `checks`; remembered after the first
time). `dicelog --all` also shows the rolls the log can't label (as **Show unlabelled rolls**), and
`dicelog --raw` records every `rand()` call, not just rolls. If more than one DOSBox is running,
add `--pid <number>` (from `processes`; a DOSBox-X beside a DOSBox 0.74 is told from it by the
Options tab's engine, and `processes` says which is read through its memory file). The memory tools (`find-text`, `dump`, `search`, `next`)
are in [Command-line mapping tools](DEVELOPMENT-INTERNALS.md#command-line-mapping-tools).

## Module map

Every module of `dsloader/` opens with a docstring saying what it does; this is its first line,
and the section that explains it. INTERNALS, RULES, KITS, CONTENT and SCREENS are the
`DEVELOPMENT-*.md` pages.

**Core: starting the game, DSCLOG's side, memory**

| Module | What it does | Section |
|---|---|---|
| `__init__.py` | the package, its `__version__` | [Making a release](#making-a-release) |
| `__main__.py` | the command line, `python -m dsloader <command>` | [From a command prompt](#from-a-command-prompt) |
| `launch.py` | starts the GOG release in DOSBox with the dice log: the config, the copies, the crash report | [INTERNALS: crash report](DEVELOPMENT-INTERNALS.md#the-crash-report) |
| `midiout.py` | the music device: where DOSBox sends the game's General MIDI music (the picture's lines are `launch.display_lines`) | [SCREENS: picture and music](DEVELOPMENT-SCREENS.md#picture-and-music) |
| `gamepatch.py` | the patched game, DSUNLOG.EXE: `PATCHES` | [INTERNALS: the dice log](DEVELOPMENT-INTERNALS.md#how-the-dice-log-works) |
| `dicelog.py` | the dice log: reads DSCLOG's ring and labels each roll; each pass's steps | [INTERNALS: the dice log](DEVELOPMENT-INTERNALS.md#how-the-dice-log-works) |
| `textlog.py` | the dialogue and message boxes DSCLOG copies | [SCREENS: the Dialogue tab](DEVELOPMENT-SCREENS.md#the-dialogue-tab) |
| `journal.py` | the journal: what was said and done in a game, kept on disk and following the game's saves | [SCREENS: the Journal tab](DEVELOPMENT-SCREENS.md#the-journal-tab) |
| `quests.py` | the game's quests, for the Journal tab: which are open and which are finished in the game being played | [SCREENS: the quests](DEVELOPMENT-SCREENS.md#the-quests) |
| `questdraft.py` | a draft of the quest table, read from the game's scripts: for developers (`python -m dsloader.questdraft`; not in the release zip) | [SCREENS: the quests](DEVELOPMENT-SCREENS.md#the-quests) |
| `guestmem.py` | finds DOSBox's guest memory in its process | [INTERNALS: reading and writing memory](DEVELOPMENT-INTERNALS.md#reading-and-writing-memory) |
| `process.py` | reads, writes and pauses another process's memory (Windows, Linux); `FileMemory`, the same through DOSBox-X's memory file | [INTERNALS: reading and writing memory](DEVELOPMENT-INTERNALS.md#reading-and-writing-memory) |
| `dosboxx.py` | DOSBox-X as the game's engine: its configuration, its memory file, its version | [SCREENS: the engine](DEVELOPMENT-SCREENS.md#the-engine-gogs-dosbox-or-dosbox-x) |
| `itemgate.py` | the Loader's item-list writes, only while the game leaves the lists be | [INTERNALS: the item gate](DEVELOPMENT-INTERNALS.md#the-item-gate) |
| `itemwatch.py` | the party's items watched, a report when one goes missing | [INTERNALS: the item watch](DEVELOPMENT-INTERNALS.md#the-item-watch) |
| `heapcheck.py` | the game's far heap and DOS memory, for crash reports and the low-memory warning | [INTERNALS: low memory in play](DEVELOPMENT-INTERNALS.md#low-memory-in-play) |
| `freeze.py` | the freeze report, from DSCLOG's notes of the timer | [INTERNALS: the freeze report](DEVELOPMENT-INTERNALS.md#the-freeze-report) |
| `unblock.py` | takes Windows' "downloaded from the internet" mark off the Loader's files | [README](README.md#one-time-setup) |
| `namedsaves.py` | the game's saves kept a second time under their names in the game | [SCREENS: more saves](DEVELOPMENT-SCREENS.md#more-saves) |

**Game data: the game's files and records**

| Module | What it does | Section |
|---|---|---|
| `game.py` | where the game keeps things in memory: offsets, tables, `GameData` | [INTERNALS: what's known](DEVELOPMENT-INTERNALS.md#whats-known-of-the-save-and-records) |
| `gff.py` | reads SSI's GFF files (the game's data and saves) | [INTERNALS: what's known](DEVELOPMENT-INTERNALS.md#whats-known-of-the-save-and-records) |
| `gpl.py` | reads and decodes the game's scripts (GPLDATA.GFF) | [INTERNALS: ability checks](DEVELOPMENT-INTERNALS.md#ability-checks-in-the-scripts-conditions) |
| `savefile.py` | the party stored in a save (`Show Save.bat`) | [INTERNALS: what's known](DEVELOPMENT-INTERNALS.md#whats-known-of-the-save-and-records) |
| `layout.py` | the memory layout files (`layouts/`) | [INTERNALS: mapping memory](DEVELOPMENT-INTERNALS.md#mapping-memory) |
| `values.py` | the value types layouts and searches use (u8 to s32, str) | [INTERNALS: mapping memory](DEVELOPMENT-INTERNALS.md#mapping-memory) |
| `search.py` | the Memory tools' value search | [INTERNALS: command-line mapping tools](DEVELOPMENT-INTERNALS.md#command-line-mapping-tools) |
| `monsters.py` | what the game knows of a monster but never shows (what hurts it) | [SCREENS: the Look box](DEVELOPMENT-SCREENS.md#what-hurts-a-monster-the-look-box) |
| `sizes.py` | AD&D's size for each creature | [RULES: creature size](DEVELOPMENT-RULES.md#creature-size) |
| `tracker.py` | kills, XP and level-ups noted | [DICE-LOG](DICE-LOG.md) |
| `searches.py` | searching junk, hay and wardrobes: the rolls' lines | [INTERNALS: searching](DEVELOPMENT-INTERNALS.md#searching-junk-hay-and-wardrobes) |
| `bowyer.py` | the Bowyer's archery target: each shot's line | [INTERNALS: the Bowyer](DEVELOPMENT-INTERNALS.md#the-bowyers-archery-target) |
| `scriptchecks.py` | the scripts' ability checks made with the random command | [INTERNALS: ability checks](DEVELOPMENT-INTERNALS.md#ability-checks-in-the-scripts-conditions) |

**Rules**

| Module | What it does | Section |
|---|---|---|
| `restrict.py` | class restrictions: what a character's classes may not equip | [RULES: class restrictions](DEVELOPMENT-RULES.md#class-restrictions) |
| `tables.py` | AD&D's class tables: XP, priests' THAC0, spell slots | [RULES: AD&D's class tables](DEVELOPMENT-RULES.md#adds-class-tables) |
| `aging.py` | ages and magical aging | [RULES: ages](DEVELOPMENT-RULES.md#ages-and-magical-aging) |
| `greyhair.py` | grey hair on the map figures as they age | [RULES: grey hair](DEVELOPMENT-RULES.md#grey-hair-on-the-map) |
| `cahulaks.py` | the cahulaks' tangle, and who is too big for it | [RULES: cahulaks](DEVELOPMENT-RULES.md#cahulaks) |
| `intlearn.py` | a preserver's INT and the spells it learns | [RULES: preservers' INT](DEVELOPMENT-RULES.md#preservers-int) |
| `specialize.py` | weapon specialization: the kinds and the item types in each | [RULES: weapon specialization](DEVELOPMENT-RULES.md#weapon-specialization) |
| `weaponchoice.py` | new characters' weapon kinds and starting weapon | [RULES: weapon specialization](DEVELOPMENT-RULES.md#weapon-specialization) |
| `weaponpages.py` | the weapon window and the creation panel's lettering | [RULES: weapon specialization](DEVELOPMENT-RULES.md#weapon-specialization) |
| `startgear.py` | new characters' starting gear filled out | [RULES: fuller starting gear](DEVELOPMENT-RULES.md#fuller-starting-gear) |
| `defaultparty.py` | the game's own party made ready for the rules | [RULES: the game's own party](DEVELOPMENT-RULES.md#the-games-own-party) |
| `rollstore.py` | STORE and RECALL on the creation screen | [RULES: STORE and RECALL](DEVELOPMENT-RULES.md#store-and-recall-on-the-creation-screen) |
| `prices.py` | the leader's CHA and shop prices | [RULES: CHA at shops](DEVELOPMENT-RULES.md#the-leaders-cha-at-shops) |
| `buyback.py` | magical items sold kept, to buy back | [RULES: buying back](DEVELOPMENT-RULES.md#buying-back-magical-items) |
| `stealth.py` | hiding in shadows and moving silently in a fight | [RULES: hiding to backstab](DEVELOPMENT-RULES.md#hiding-in-shadows-to-backstab) |
| `locks.py` | a failed lock out of reach until the thief's next level | [RULES: another try a level later](DEVELOPMENT-RULES.md#a-lock-or-a-pocket-failed-another-try-a-level-later) |
| `pickpocket.py` | picking pockets, and giving and moving the party's items | [RULES: picking pockets](DEVELOPMENT-RULES.md#picking-pockets) |
| `tools.py` | the thieving tools older Loaders gave, taken back | [RULES: picking pockets](DEVELOPMENT-RULES.md#picking-pockets) |
| `sounds.py` | the mod's sounds for hiding and picking pockets | [RULES: sounds](DEVELOPMENT-RULES.md#sounds-for-hiding-and-picking-pockets) |

**Kits**

| Module | What it does | Section |
|---|---|---|
| `kitpages.py` | the creation panel's KIT page, the kit byte and the kits' names | [KITS: choosing one](DEVELOPMENT-KITS.md#choosing-one) |
| `kits.py` | the kits' effects, as DSCLOG makes them | [KITS: where each effect goes](DEVELOPMENT-KITS.md#where-each-effect-goes) |
| `dance.py` | a Battle Dancer's dance, rolled and counted down | [KITS: multiclass kits](DEVELOPMENT-KITS.md#multiclass-kits) |
| `wild.py` | Wild Fighting, a Wild Fury's and Gerakis's | [KITS: multiclass kits](DEVELOPMENT-KITS.md#multiclass-kits) |
| `spellarrows.py` | the Spellarcher's spell arrows and starting gear | [KITS: spell arrows](DEVELOPMENT-KITS.md#spell-arrows) |

**Content: items, people, scripts**

| Module | What it does | Section |
|---|---|---|
| `dataitems.py` | the new items written into the game's objects (SEGOBJEX) | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `worldgear.py` | new weapons and bracers in merchants' stock and people's packs | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `npcitems.py` | the Loader's items on people in the slave pens | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `arms.py` | two plain weapons made magic | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `ring.py` | the Ring +1 on the arena's prisoner | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `names.py` | names for the Loader's items past the game's 322 | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `alagorn.py` | Alagorn tells of the Loader's magic items | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `elvenleader.py` | the Elven Leader's gift, the Cloak of Elvenkind | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `garyn.py` | Father Garyn's gift, the Tome of Understanding | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `tome.py` | the Tome of Understanding, +1 WIS | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `haystash.py` | Merzol's hay stash, Hayneedle | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `bonescale.py` | the rest of the bone scale armour, in the chest with its chest piece | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `robes.py` | two magic robes for those who go without armour | [CONTENT: robes](DEVELOPMENT-CONTENT.md#robes) |
| `pehtuclchest.py` | Pehtucl's chest, locked and trapped | [CONTENT: Pehtucl's chest](DEVELOPMENT-CONTENT.md#pehtucls-chest) |
| `kalzith.py` | Kalzith, the defiler in the slave pens | [CONTENT: Kalzith](DEVELOPMENT-CONTENT.md#kalzith) |
| `kalzithface.py` | Kalzith's portrait | [CONTENT: Kalzith](DEVELOPMENT-CONTENT.md#kalzith) |
| `semyon.py` | Semyon in the slave pens after his fight | [CONTENT: Semyon](DEVELOPMENT-CONTENT.md#semyon) |
| `pensasks.py` | Dinos and the Trustee asked about Kalzith and Semyon; the Trustee's script fixes | [CONTENT: Dinos and the Trustee](DEVELOPMENT-CONTENT.md#what-dinos-and-the-trustee-say-about-them) |
| `champions.py` | the champions' bout after Scar | [CONTENT: the champions' bout](DEVELOPMENT-CONTENT.md#the-champions-bout) |
| `bodyart.py` | the dead Tohr-kreen champion's picture | [CONTENT: the champions' bout](DEVELOPMENT-CONTENT.md#the-champions-bout) |
| `vulture.py` | the cooked vulture, a meal at last | [CONTENT: the cooked vulture](DEVELOPMENT-CONTENT.md#the-cooked-vulture) |
| `defilerscrolls.py` | defilers' scrolls, dropped where they die | [CONTENT: defilers' scrolls](DEVELOPMENT-CONTENT.md#defilers-scrolls) |
| `people.py` | the game's people wearing their gear from the start | [CONTENT: the game's people's gear](DEVELOPMENT-CONTENT.md#the-games-peoples-gear) |
| `scriptfixes.py` | bugs in the game's scripts, mended in the Loader's copy | [CONTENT: script bugs](DEVELOPMENT-CONTENT.md#the-games-script-bugs) |
| `kurzak.py` | Kurzak notices Legcrusher is gone; Legcrusher at the fountain | [CONTENT: script bugs](DEVELOPMENT-CONTENT.md#the-games-script-bugs) |
| `kurzakdoor.py` | Kurzak's door, open but barring the way, opened on the walk map too | [GAME-BUGS](GAME-BUGS.md#scripts-that-stuck-or-ran-twice) (its docstring) |
| `stuckwalk.py` | people whose scripted walk stopped for good set walking again | [GAME-BUGS](GAME-BUGS.md#scripts-that-stuck-or-ran-twice) (its docstring) |
| `psiblast.py` | Psionic Blast's imagined wounds healed as the fight ends | [CONTENT: Psionic Blast](DEVELOPMENT-CONTENT.md#worn-items-the-gladiators-armour-and-psionic-blast) |
| `quiver.py` | a party archer's arrows left, over its figure | [CONTENT: an archer's last arrow](DEVELOPMENT-CONTENT.md#an-archers-last-arrow-and-a-dry-quiver) |
| `manualcheck.py` | no manual check: the copy protection's question taken out | [SCREENS: no manual check](DEVELOPMENT-SCREENS.md#no-manual-check) |
| `spelltexts.py` | the descriptions the game reads from RESOURCE.GFF for what the mod adds | [CONTENT: new spells](DEVELOPMENT-CONTENT.md#new-spells-wizard-and-6th-level-priest) |

**Graphics and sound**

| Module | What it does | Section |
|---|---|---|
| `icons.py` | inventory and spell icons of the Loader's own; writes its RESOURCE.GFF copy | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `wotrart.py` | Wake of the Ravager's spell icons, from the player's copy | [CONTENT: new spells](DEVELOPMENT-CONTENT.md#new-spells-wizard-and-6th-level-priest) |
| `sequelicons.py` | Wake of the Ravager's weapon and great axe icons, from the player's copy | [CONTENT: new items](DEVELOPMENT-CONTENT.md#new-items) |
| `whirlart.py` | Whirlwind's picture on the ground | [CONTENT: new spells](DEVELOPMENT-CONTENT.md#new-spells-wizard-and-6th-level-priest) |
| `sprites.py` | the party's map figures with what each wears | [CONTENT: what the party wears](DEVELOPMENT-CONTENT.md#what-the-party-wears) |
| `spriteparts.py` | where each part of a figure is, frame by frame | [CONTENT: what the party wears](DEVELOPMENT-CONTENT.md#what-the-party-wears) |
| `spritegear.py` | worn gear drawn on the figures | [CONTENT: what the party wears](DEVELOPMENT-CONTENT.md#what-the-party-wears) |
| `figures.py` | the elves' ears and the half-elves' own figures | [CONTENT: elves and half-elves](DEVELOPMENT-CONTENT.md#elves-and-half-elves) |
| `halfelf.py` | half-elves' own colours on the map | [CONTENT: elves and half-elves](DEVELOPMENT-CONTENT.md#elves-and-half-elves) |
| `shadows.py` | shadows under the figures | [CONTENT: shadows](DEVELOPMENT-CONTENT.md#shadows) |
| `dust.py` | dust raised by walking figures | [CONTENT: dust](DEVELOPMENT-CONTENT.md#dust) |
| `ghost.py` | see-through figures | [CONTENT: see-through figures](DEVELOPMENT-CONTENT.md#see-through-figures) |
| `labels.py` | names floating over figures | [SCREENS: names over figures](DEVELOPMENT-SCREENS.md#names-over-figures) |
| `rings.py` | the ring under the enemy chosen with Tab, and the gold ones under what can be used | [SCREENS: choosing an enemy](DEVELOPMENT-SCREENS.md#choosing-an-enemy-tab-enter-and-the-rings) |
| `combatlog.py` | the combat log's panel in the game | [SCREENS: the combat log](DEVELOPMENT-SCREENS.md#the-panel) |
| `smallfont.py` | the panel's small font | [SCREENS: the combat log](DEVELOPMENT-SCREENS.md#the-panel) |
| `art.py` | the game's portraits and font, read from the installed game | [SCREENS: the combat log](DEVELOPMENT-SCREENS.md#what-the-game-allows) |
| `spellgrid.py` | CHOOSE A SPELL's icons in a centred grid | [SCREENS: CHOOSE A SPELL](DEVELOPMENT-SCREENS.md#choose-a-spells-grid) |
| `scenepointer.py` | the game's own pointer in the scenes | [SCREENS: the pointer](DEVELOPMENT-SCREENS.md#the-pointer-in-scenes-and-where-it-starts) |

**UI: controls and the Loader's window**

| Module | What it does | Section |
|---|---|---|
| `targeting.py` | Tab and Enter: choosing an enemy and attacking it | [SCREENS: choosing an enemy](DEVELOPMENT-SCREENS.md#choosing-an-enemy-tab-enter-and-the-rings) |
| `hitchance.py` | the chance to hit shown before the swing, worked out as the game's attack does | [SCREENS: the chance to hit](DEVELOPMENT-SCREENS.md#the-chance-to-hit-before-the-swing) |
| `hover.py` | the chance to hit floating over the enemy under the game's pointer, on a party member's turn | [SCREENS: under the pointer](DEVELOPMENT-SCREENS.md#under-the-pointer) |
| `squares.py` | squares in reach: in a fight, a mark on each square the party member whose turn it is can still walk to, counted by the game's rules | [SCREENS: squares in reach](DEVELOPMENT-SCREENS.md#squares-in-reach) |
| `keywatch.py` | the keys pressed in the game, read from the BIOS keyboard buffer: R, which shows and hides the squares in reach, at no cost to DSCLOG | [SCREENS: squares in reach](DEVELOPMENT-SCREENS.md#squares-in-reach) |
| `moveback.py` | F10 after the last step: the move taken back can be walked again | [SCREENS: F10 takes a whole move back](DEVELOPMENT-SCREENS.md#f10-takes-a-whole-move-back) |
| `usable.py` | showing what can be used: while Alt is held, a ring under every door, container, body, item and person in view, and the nearest ones' names | [SCREENS: showing what can be used](DEVELOPMENT-SCREENS.md#showing-what-can-be-used-alt) |
| `scrolling.py` | scrolling the map with the mouse | [SCREENS: scrolling the map](DEVELOPMENT-SCREENS.md#scrolling-the-map) |
| `wheel.py` | the mouse wheel, for the combat log's panel | [SCREENS: the combat log](DEVELOPMENT-SCREENS.md#the-panel) |
| `loot.py` | T and Shift+T: looting a body in one go | [SCREENS: looting](DEVELOPMENT-SCREENS.md#looting-a-body-t-and-shiftt) |
| `sell.py` | S: selling plain gear in one go | [SCREENS: selling](DEVELOPMENT-SCREENS.md#selling-plain-gear-s) |
| `savepages.py` | PAGE 1 to PAGE 4 and QUICK in the save window | [SCREENS: more saves](DEVELOPMENT-SCREENS.md#more-saves) |
| `quicksave.py` | quick save, quick load and autosave: the QUICK page that fills itself | [SCREENS: quick save](DEVELOPMENT-SCREENS.md#quick-save-quick-load-and-autosave) |
| `viewer.py` | the Loader's window | [INTERNALS: practising without the game](DEVELOPMENT-INTERNALS.md#practising-without-the-game) |
| `partyview.py` | the Characters tab's cards | [README](README.md#the-characters-tab) |
| `spellbook.py` | the Spells tab: what each spell really does | [RULES: spells as the manual describes them](DEVELOPMENT-RULES.md#spells-and-psionics-as-the-manual-describes-them) |
| `ledger.py` | the dice log's lines laid out for reading | [DICE-LOG](DICE-LOG.md) |
| `fighttally.py` | a fight's tally as it ends | [DICE-LOG](DICE-LOG.md) |
| `theme.py` | the window's look | `test_theme` |
| `palette.py` | the Loader's colours, sampled from the game's screens | `test_theme` |

**Docs generation**

| Module | What it does | Section |
|---|---|---|
| `manual.py` | the manual's web pages | [Build](#build) |
| `patchnotes.py` | the patch notes' web page | [Build](#build) |
| `pagefonts.py` | the web pages' fonts, inside the pages | [Build](#build) |
| `docicons.py` | the items' icons for ITEMS.md | [Generated pages](#generated-pages) |
| `doccreatures.py` | the creatures' table, CREATURES.md | [Generated pages](#generated-pages) |

## Contributor checklist

**A probe or a site** (a new place in the game that calls DSCLOG):

1. In `dsloader/gamepatch.py`, a `Patch(name, offset, original, replacement)` in `PATCHES`: the
   DSUN.EXE file offset, the bytes there, and an `INT` the same length (`_interrupt(VEC_X, n)`,
   NOPs after it), or, with every vector taken, a site of the shared one (`_site(X_SITE, n)`: the
   `INT`, the site's number, NOPs). Keep the game's far calls and their relocations where they are.
2. In `dos/dsclog.asm`: a new vector's handler in `ALL_VECTORS` (`vector VEC_X, probe_x`), or a
   site's routine in `site_tab` (`site X_SITE, x_site`, in number order: the build fails
   otherwise), with the number as an `equ` beside the Python constant of the same name. Say in the
   routine's comment what it replaces, at which address, and what it keeps. Code in overlays that
   can move needs its way back in a frame the overlay manager fixes up (`OVR_BACK`). The INT turns
   interrupts off: a handler that ends with `RETF 2` (keeping its flags for the caller) or calls
   the game's code starts with `call if_frame`, which sets them as the caller had them (not `STI`:
   DSCLOG's own drawing calls the game's routines with them off, `DRAW_MASKED`); one that ends
   with `IRET` gets the caller's back anyway. Code that copies with string instructions from the
   timer, the mouse or a site of the game's unknown state clears the direction flag first (`CLD`;
   `PROBE_TICK`, `RECORD` and `STUB` do). A site's code reads `RL_SITE` before anything turns
   interrupts on ([RL_SITES' comment](dos/dsclog.asm)).
3. A test in `tests/test_dsclog.py` that runs it in the emulator (`run_vector` or a site run), a
3. A test in `tests/test_dsclog.py` that runs it in the emulator (`run_vector` or a site run), a
   rebuild with NASM 2.16.01 within [the limits](DEVELOPMENT-INTERNALS.md#the-limits), then a check
   in the game with the build in place (the playtest kit's `buildcheck.py`).

**A game flag** (state a save keeps): all of 0-807 are in use, so find room first (a flag freed, or
the save's flags made longer, if the game allows it). Then a module constant, a row in [the flags'
table](DEVELOPMENT-INTERNALS.md#the-loaders-game-flags), and `tests/test_flagrange.py`'s `FLAGS`
(or `_ranges`); `test_audit_flags` finds it by itself.

**A header field** (shared by DSCLOG and the Loader): add it at the end of `hdr:` in
`dos/dsclog.asm` with its offset in the comment (`+1892` after `SQUARES_ON`'s `+1890`), so the
others never move; name it `TSR_*` in the module that reads it (`test_header_offsets` checks both:
the field at the offset its comment says, the constant a field's offset). If both sides must change
together, take the signature up (`sig` in `dsclog.asm` and `HDR_SIG` in `dicelog.py`). See
[DSCLOG's header](DEVELOPMENT-INTERNALS.md#dsclogs-header).

**A page of the manual**: a row in `manual.PAGES` (its HTML name, its Markdown, its name in the
bar, and "spoilers" if it has them), `test_manual`'s count of pages, a link to it from the README,
and `python -m dsloader.manual`. A page that should not ship goes in `.gitattributes` with
`export-ignore` instead (and in `test_doclinks`' list of them).

**A section a player's page explains**: its explanation goes under a `##` heading of the same name
on a DEVELOPMENT page, and the player's section links to it (`test_doclinks` checks).

## How each part works

How each part of the [features page](FEATURES.md) and the [README](README.md) is done, on pages of
its own:

- [Internals](DEVELOPMENT-INTERNALS.md): the dice log and labelling rolls, DSCLOG's header, room and
  memory, the crash, freeze and item-watch reports, reading and writing memory, the records
- [Screens, controls and saves](DEVELOPMENT-SCREENS.md) (its Contents lists each section)
- [The rules](DEVELOPMENT-RULES.md) (its Contents lists each section)
- [The kits](DEVELOPMENT-KITS.md) (the kits, the kit's byte, choosing one, multiclass kits, where
  each effect goes, spell arrows, how they're checked)
- [Spells, items, people, graphics and the game's bugs](DEVELOPMENT-CONTENT.md) (its Contents lists
  each section)

What was checked in the game, and how, is in the [playtest logs](https://github.com/daaki85/darksun-obsidian-edition/tree/main/playtest/logs);
the pages link the log where one was kept ("Verified: log").

## Unverified

Read from the game's code and held by unit tests, but not yet seen in play (checked against the
playtest logs and HISTORY, 2026-11-17):

- The script repairs past the slave pens taken from OpenDS's darkfix: Darkhold's triggers, the Lava
  Rifts ranger, Linara ([script bugs](DEVELOPMENT-CONTENT.md#the-games-script-bugs)).
- Script 46's "Who are you?" menu: Goodbye returning rather than arresting (from OpenDS's triage).
- Pehtucl's ambush making its five guards one by one, and the fountain's alarm zone taking in the
  passage (the save `fountain-user` loads with the ambush about to fire).
- Kurzak's own lines once Legcrusher is dead and the party is late for a fight (`kurzak.py`; the
  fountain scene itself is verified).
- Pick Pockets' timeout falling while the Loader is already moving the item ([picking
  pockets](DEVELOPMENT-RULES.md#picking-pockets)): a known race, not seen.
- An item deleted at 67401h (675B4h) when a new class can't use a piece and the pack is full ([the
  item watch](DEVELOPMENT-INTERNALS.md#the-item-watch)).
- A weapon breaking in a fight: the check's rolls are logged, but none has broken in testing.
- The arena's 1000th trip ([the champions' bout](DEVELOPMENT-CONTENT.md#the-champions-bout)): as
  its script reads; the 5000th was played with the count set in memory.

## Acknowledgements

The project's credits are in [the root README](https://github.com/daaki85/darksun-obsidian-edition/blob/main/README.md#credits).
What these pages owe to others:

- **[yuan-ti](https://github.com/CalvinRodo/yuan-ti)**, CalvinRodo's new engine for the game (facts
  only, each checked in DSUN.EXE; none of its code is used): most of the [script
  repairs](DEVELOPMENT-CONTENT.md#the-games-script-bugs) (the halfling's greeting, the ranger's
  tracking, the sewer grate, the Rebel Mindhome, region 9's messenger; the pages mark each
  "yuan-ti's"), the thief skill routine's Slowed test, Scare's resist fear, the party's thief skill pick among [the
  game's spells](DEVELOPMENT-CONTENT.md#the-games-spells) and its bugs, Psionic Blast (its issue
  #129), the priest's tending of the party at a rest, and the names of the scripts' requests
  (`REQUEST_NAMES`).
- **[OpenDS](https://github.com/VirInvictus/opends)**: the darkfix script repairs (Darkhold, the
  Lava Rifts ranger, Linara), its triage's rows (script 46, region 9's messenger), and [worn
  items](DEVELOPMENT-CONTENT.md#worn-items-the-gladiators-armour-and-psionic-blast).
- **SSI's note 2712** for Wake of the Ravager (the same engine): [graphics disappearing in a busy
  area](DEVELOPMENT-CONTENT.md#graphics-disappearing-in-a-busy-area).
- **The X11 misc-fixed 5x7 font** (public domain): the combat log panel's lines (`smallfont.py`).
- **DOSBox 0.74's source**, which comes with the game: [where DOSBox's memory
  is](DEVELOPMENT-INTERNALS.md#where-dosboxs-memory-is).
- **The user**, daaki85: the designs credited "the user's" on these pages (Legcrusher at the
  fountain, the grate's weapon search, looting and selling, the sounds chosen).
