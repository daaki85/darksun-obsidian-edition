# Documentation review, round two (2026-11-28)

*Done with the project skill `documentation-review` on `origin/obsidian-edition` at `4926cb69` (#309 merged).
It covers what changed since [the full review](docs-review-full-2026-11-27.md) (after #275). That is mostly
the sequel's side, written PR by PR: RAVAGER.md (+127 lines), FEATURES.md, CHANGELOG.md (+156),
DEVELOPMENT-SCREENS and DEVELOPMENT-CONTENT, the playtest guide and research pages, and 71 changed pictures.
The draft release notes (a Claude Doc, not in the repository) were brought up to date too. Fixes are on branch
`claude/code-audit-round-two`, beside [the code audit](code-audit-2026-11-28.md).*

**Read in full:** RAVAGER.md's "The mod in the sequel" and "Not in the sequel yet"; FEATURES.md's sequel
lines (every "In Wake of the Ravager:" line); CHANGELOG.md's Unreleased part to "Pull requests #146 to #268";
the release notes draft. **Checked against code or data:** `ravquests.QUESTS`/`LEFT_OUT` (counts),
`ravdress.RavDresser` (what it draws), `sprites.Dresser` (grey hair), `RESEARCH-RAVAGER-RECORDS.md`'s roster
finding, each merged PR's files against CHANGELOG (#284 to #309). **Run:** `test_doclinks`, `test_manual`,
`python -m dsloader.manual`, and an orphan-picture scan of `docs/`.

## 1. Redundancy

Nothing new found. Each FEATURES entry ends with an "In Wake of the Ravager:" line that points to RAVAGER.md's
gap list, so the gap list is the one record (2026-11-27's rule). But the lines drift from it (part 4).

## 2. Irrelevancy

Nothing found in the player pages. CHANGELOG's sequel entries carry helper site numbers and addresses
("DSCLOG2's sites 235-237"), as every entry there does. That is the house style for the changelog. The
release notes keep them out.

## 3. Bloat

CHANGELOG.md is 3,208 lines and its Unreleased part 650 lines. That is long for one release, but the release
step rewrites it into patch notes, so it isn't cut here. RAVAGER.md is 415 lines, with no cut proposed.

## 4. Inconsistency (fixed)

| Where | What it said | What is true | Fix |
|-------|--------------|--------------|-----|
| FEATURES.md "What the party wears", sequel line | "not yet" | The class outfits are drawn on the map, in fights and on the small figures (#292, #298). Worn gear and a second member with the same figure are not. | Line rewritten |
| RAVAGER.md gap list "More characters" | the sequel keeps its own limit, not 29 | The sequel's roster holds 40 already (`RESEARCH-RAVAGER-RECORDS.md`, its eight 28h compares). FEATURES says "not needed". | Bullet removed |
| RAVAGER.md gap list, quests | 62 of the scripts' awards "not in the table yet" | `test_ravquests` holds every award either in the 42 quests or in `LEFT_OUT` with a reason: 92 left out, 8 of them because their cause wasn't established | Line rewritten |
| CHANGELOG, two sequel entries | titled "New: Wake of the Ravager." with no branch; one said "the small figures are still to come" | The entry above it is the small figures (#298) | Titles and branches added, the stale clause cut |

## 5. Clarity and reorganisation

The sequel's gap list, the FEATURES sequel lines and the release notes' known gaps all say what the sequel
lacks. The list stays canonical. The release notes now name its items and link to the page, not their own
reading. Nothing to move.

## 6. Patch notes

There have been no new releases since 2.19.2, so the patch notes are unchanged. **Missing from CHANGELOG
(fixed):** nine merged PRs with player-visible changes had no entry:

- #285, #287, #291 and #296: the inventory's class pictures in both games;
- #294: the creation picture;
- #295: the sequel's mouse;
- #297: the log panel's clicks and L;
- #293 and #307: shadows from the feet.

They are added as five entries in the changelog's own style. #284, #288 and #301 are docs or catalogue work,
with entries or none needed. The draft release notes dated from 2026-11-25. They now cover the sequel's whole
port, a "Both games" section, and current known gaps (the DOSBox-X Windows test, the sequel's gaps, Shattered
Lands' full helper).

## 7. The Loader

Nothing new found. The sequel's start scripts (`Play Wake of the Ravager (in-game rolls).bat`, Show Save for
its saves) are in CHANGELOG (#264), and the Options tab's reference is unchanged.

## 8. The other documentation

- The playtest guide and its research pages grew by each PR's notes (+64, +53, +48 lines). They are read by
  contributors, and their own index (RESEARCH.md) lists them.
- The defilers' play log had a wrong claim, that the Pyramid jump "closed DOSBox". It was a wrong region
  number (corrected in #283).
- `reports/` gained the figure catalogue and the furniture review (#280, #265). Both are linked from
  RAVAGER.md.

## 9. Missing (fixed)

- **The hair greying with age** is Shattered Lands' (`sprites.Dresser` reads `greyhair.stage_of`). The sequel's
  dresser doesn't draw it, and neither page said so. It is now in the gap list and on FEATURES' ages line.
- The CHANGELOG entries in part 6.

## 10. Screenshots

The 71 changed pictures are the creature figures (regenerated by `doccreatures`, #276 and #307) and four new
sequel pictures. All four were opened. `ravager-small-portraits.png`'s "after" shows the empty frame's grey
wash, from before the emblem (#279). Its caption now says so, and `ravager-no-speaker.png` below it shows the
emblem. Six orphan pictures remain in `docs/class-outfits/` (Codex's studies from 2026-11-22 to 11-25). Nothing
links them, and the zip leaves that folder out. They could move to `reports/` or go.

## 11. Tables

The new tables (RAVAGER's sequel items, the figure catalogue's) were spot-checked against the data in the
earlier review. No new player tables appeared in this range.

## 12. Features

FEATURES' sequel lines were read against the gap list and the code. The two that disagreed are fixed (part
4). Every feature in this range's CHANGELOG has its FEATURES or RAVAGER entry.

## Is anything missing? Are items where they belong?

After these fixes, no: every player-visible PR in the range has its changelog entry, and every gap found in
the code is on the list. Items are where they belong. The one open structural question is the six orphan
studies in `docs/class-outfits/`.

## Ranked findings

1. **Wrong:** RAVAGER.md's quests line (62 awards), its "More characters" bullet, and FEATURES' "What the party
   wears" sequel line. All three are fixed.
2. **Missing:** CHANGELOG entries for nine PRs, and the grey hair gap. Both are fixed.
3. **Stale:** the draft release notes (updated) and one screenshot's caption (fixed).
4. **Nit:** six orphan studies (left for the owner).

**Not verified:** the gap list's remaining items (spells, cahulaks, DAM lines, the game's people, the game's
bugs) were checked against their code by name only, not in play.
