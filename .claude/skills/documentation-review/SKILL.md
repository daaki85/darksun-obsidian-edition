---
name: documentation-review
description: Run a strict full review of the project documentation: redundancy, irrelevancy, bloat, inconsistency, placement and reorganisation, patch notes, loader docs, missing content, outdated screenshots, tables, and features. Use when the user asks for a documentation review, docs review, docs audit, or doc quality check.
disable-model-invocation: true
---

# Documentation Review

A strict review of the documentation (README, PLAYER-GUIDE, FEATURES, DEVELOPMENT*, ITEMS, KITS,
CREATURES, PEOPLE, GAME-BUGS, HOW-THE-GAME-WORKS, WEAPON-SPECS, manual/, docs/, CHANGELOG,
PATCH-NOTES, release-notes/, and playtest/ guides) for the state of the current branch, or for the
files or area the user names.

Be ambitious about the structure of the docs, not just their typos. Look for pages that should be
merged, split, deleted or moved, so the reader needs fewer places to look.

## Method

1. **Scope.** Default to the docs touched by the current branch's diff plus every doc that describes
   the same feature. If the user names a file or area, review that. List what you read.
2. **Verify, don't trust.** For each factual claim in scope (numbers, item and creature stats, rules,
   key bindings, file names, commands, defaults, version numbers), check it against the source of
   truth: the code, the data tables, the tests, the changelog, or a play (follow the startup
   procedure in `playtest/PLAYTESTING.md` before any in-game check). Say which claim was checked
   against what. A claim you could not verify is reported as unverified, not as correct.
3. **Read as the target reader.** Player docs are read by a player who has the game and has never
   seen the code. Development docs are read by a contributor who has the repository. Check each page
   serves its reader and does not mix the two.
4. **Cover the full pass** below, in that order, and keep a list of every file read, every
   picture opened, and every claim checked so the report can show its coverage.
5. **Run what can be run.** Run the commands, open the links, and check the paths and anchors the
   docs give. Run any doc-consistency tests the repository has.

## The full pass

The user's usual request is: *a full review of the documentation for redundancy, irrelevancy,
bloat, inconsistency, and opportunities for clarity and reorganization; are items in the places
where they logically belong; review the patch notes, the loader and the other documentation; is
anything missing; review screenshots for anything outdated, tables, and features.* Unless the user
narrows it, a documentation review answers every one of these, each under its own heading in the
report, even when the answer is "nothing found" (say what was checked):

1. **Redundancy**: the same fact, table, list or explanation in more than one place (README,
   PLAYER-GUIDE, FEATURES, `manual/*.html`, DEVELOPMENT*, patch notes, changelog, release notes).
   Which copy is canonical, and what to delete or turn into a link.
2. **Irrelevancy**: content that no reader of that page needs (process history, superseded designs,
   notes to self, details of removed features, material that belongs in the changelog or the
   playtest guide).
3. **Bloat**: pages, sections, paragraphs and sentences that can shrink without losing a fact.
   Give the size of the page and the cut you propose.
4. **Inconsistency**: the same thing named, numbered or described differently across pages (item
   and creature names, stats, class and kit names, key bindings, version numbers, option names,
   menu wording, capitalisation, units); tables whose columns or order differ for the same data.
5. **Clarity and reorganisation**: pages to merge, split, rename or move; sections in the wrong
   page; headings that do not say what is below; an order that does not follow the reader's task.
   Ask of every item: is it where a reader would look for it, and is it where it logically belongs
   (player-facing vs contributor-facing vs release record vs playtest procedure)?
6. **Patch notes**: `PATCH-NOTES.md`, `patch-notes.html`, `CHANGELOG.md`, `CHANGELOG-archive.md`,
   `release-notes/`, and the manual's changes page. Do they agree with each other and with the
   shipped version? Are entries in the right release, in the same style and level of detail, free
   of duplicates, and written for the player (not the developer)? Is every user-visible change in
   the diff or the git log since the last release in them? Does the HTML match the Markdown?
7. **The loader**: the documentation of `dsloader/` and the start scripts (`.bat` files, dice log,
   Show Save): what each does, its options, its files, how to start, and what a user sees.
   Check the docs against the loader's code and its `tests/`, and run the commands the docs give
   where they can run here.
8. **The other documentation**: every remaining page in scope (README files, DEVELOPMENT*,
   ITEMS, KITS, CREATURES, PEOPLE, GAME-BUGS, HOW-THE-GAME-WORKS, WEAPON-SPECS, DICE-LOG, manual/,
   `playtest/` guides, `reports/`). Check each page's claims, links and place in the index.
9. **Missing**: features, options, rules, files, commands, known bugs and fixes that exist in the
   code, data or patch notes but have no documentation, and pages a reader would expect and cannot
   find. Compare the code and the changelog against the docs, not only the docs against
   themselves.
10. **Screenshots** (`obsidian-edition/docs/*.png|gif`, `docs/items`, `docs/creatures`, and any in
    the manual): open each picture (Read the image) and compare it with the text around it and
    with the current game. Flag a screenshot that shows an old layout, old numbers, old names, an
    old version, a changed screen or a removed feature; one the text no longer describes; one that
    nothing references (orphan) or that is referenced but missing; duplicates that show the same
    thing; and a picture that would do better as a table. Check size and format (the
    docs convention is in the playtest guide's "pictures for the docs"). To retake one, follow the
    startup procedure in `playtest/PLAYTESTING.md` first.
11. **Tables**: every table in scope. Are the figures right (spot-check against the data or code,
    all rows when the table is short), the columns and order consistent with the sibling tables,
    nothing missing or extra, the sort sensible, and does it render (Markdown pipes, HTML)? Is
    there a table of the same data elsewhere (redundancy)? Would prose be better, or a table
    instead of prose?
12. **Features**: `FEATURES.md`, `manual/features.html`, the README's feature list and the
    player's guide. Is each listed feature real, current, described the same way everywhere,
    in a sensible group, and documented where the reader is told to look? Is any shipped feature
    (from the changelog and the code) not listed? Is any listed feature changed, merged or removed?

## Standards

1. **Accuracy first.** A wrong statement is worse than a missing one. Flag anything the code, data
   or a play contradicts, and anything a recent change made stale (renamed things, changed numbers,
   removed features, old version numbers).
2. **One home per fact.** Each fact lives in one canonical page; other pages link to it. Flag
   copied tables and paragraphs that can drift apart, and facts that appear in three places.
3. **Complete for the reader's task.** A reader must be able to do the thing the page promises
   (install, start, play a class, build, test, release) with no unstated step. Flag missing
   prerequisites, missing "what you should see", missing failure cases.
4. **Changes are documented.** A user-visible change has a changelog or patch-notes entry, and the
   feature docs it touches are updated in the same branch. Flag a diff that changes behaviour and
   leaves its docs behind.
5. **Structure and findability.** The README and index pages point to every page that matters. No
   orphan pages, dead links, broken anchors, or pages whose title does not say what is inside.
   Headings are in a sensible order and tables beat prose for lookup data.
6. **Direct, plain writing.** Short sentences, concrete nouns, the same word for the same thing
   everywhere. Flag filler, hedging, marketing tone, history that no reader needs ("we used to"),
   and pages that explain the writer's process instead of the reader's task.
7. **Size and sprawl.** Flag a page that has grown into several documents, or a page that is a
   stub. Prefer splitting by reader and task, not by whatever order it was written.
8. **Repository rules.** No links to, or copies of, the game, Wake of the Ravager or the walkthrough
   (they are not distributed here); nothing from the private installation-files repository is
   quoted or committed. `playtest/` must stay outside `obsidian-edition/` so it never ships in a
   release zip. Docs that ship in the zip must not point to files that do not ship.
9. **Dates and versions.** Every version, date and "current" claim matches the latest release and
   the changelog. Flag "latest", "new" and "recently" with no date.

## What to flag aggressively

- A documented number, rule or behaviour that the code or a play contradicts.
- The same table or explanation maintained in two places.
- A feature or change with no documentation, or documentation for something removed.
- Dead links, broken anchors, wrong paths, commands that do not run.
- Pages that mix player and contributor material.
- Instructions with a missing step, an unstated prerequisite, or an unexplained jargon term.
- A screenshot that no longer matches the game or its text, an orphan or missing picture.
- A table with a wrong, missing or inconsistent row; a feature list that differs between pages.
- Patch notes, changelog and release notes that disagree, or that omit a user-visible change.
- Loader or start-script documentation that does not match what the loader does.
- Bloat: material no reader needs, or that can be cut without losing a fact.
- Long pages with no summary at the top and no way to find the one thing the reader came for.

## Preferred remedies

- Delete the duplicate and link to the canonical page.
- Merge or split pages so each has one reader and one job.
- Replace prose with a table when the content is lookup data.
- Add the missing step, the expected result, or the failure case.
- Move contributor detail out of player pages, and the reverse.
- Cut history, filler and hedging.

Do not stop at "rephrase this" when the real problem is that the fact is in the wrong place, is
duplicated, or is wrong.

## Output

Answer the twelve parts of the full pass under their own headings (with "nothing found, checked
X" where that is the result), and end with a plain answer to "is anything missing?" and "are items
where they logically belong?". Then rank the findings, highest first:

1. Factually wrong or contradicted statements (with the evidence: file and line of the doc, and
   the source it disagrees with).
2. Missing documentation for changed or existing behaviour.
3. Duplicated facts and structural problems (merge, split, move, delete).
4. Broken links, paths, anchors, commands.
5. Outdated screenshots, wrong or inconsistent tables and feature lists.
6. Reader-task gaps (missing steps, prerequisites, results).
7. Bloat, irrelevance and writing quality.

Cite `file:line` for every finding and give the concrete fix. Prefer a few high-conviction findings
over a long list of nits. List separately what was checked and found correct, and what could not be
verified. If the user asks for fixes, make them on a `claude/<task>` branch, in the same pass, and
keep the changelog and the docs in step.

## Approval bar

Do not approve because the docs read well. Approve only when:

- every checked claim matches its source of truth, and unverified claims are listed;
- every user-visible change in scope is documented, in one canonical place;
- no dead links, wrong paths or non-running commands remain;
- no fact is duplicated where it can drift;
- the screenshots, tables, feature lists, patch notes and loader docs in scope were each checked;
- the repository rules above are respected.
