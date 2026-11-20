---
name: documentation-review
description: Run a strict review of the project's documentation for accuracy, completeness, structure, and reader usefulness. Use when the user asks for a documentation review, docs review, docs audit, or doc quality check.
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
4. **Run what can be run.** Run the commands, open the links, and check the paths and anchors the
   docs give. Run any doc-consistency tests the repository has.

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

Report findings in this order, highest first:

1. Factually wrong or contradicted statements (with the evidence: file and line of the doc, and
   the source it disagrees with).
2. Missing documentation for changed or existing behaviour.
3. Duplicated facts and structural problems (merge, split, move, delete).
4. Broken links, paths, anchors, commands.
5. Reader-task gaps (missing steps, prerequisites, results).
6. Writing quality.

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
- the repository rules above are respected.
