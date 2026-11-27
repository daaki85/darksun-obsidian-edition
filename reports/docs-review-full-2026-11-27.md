# Documentation review, full pass (2026-11-27)

A full review of the documentation on `obsidian-edition` (after #263), done with the project skill
`/documentation-review`: its twelve parts, then the findings ranked. Fixes are on branch
`claude/docs-review-full`; what needs a decision (moving or merging whole sections between pages) is
marked **(owner)** and was brought to the coordinator with a recommendation. It follows
[the first review](docs-review-2026-11-27.md) and [the follow-up](docs-review-followup-2026-11-27.md),
and doesn't repeat what they fixed. Work left to the audit thread by agreement: splitting
`playtest/RESEARCH.md`, and the sequel's side of FEATURES, DICE-LOG and CREATURES.

**Read in full**: the project README, `obsidian-edition/README.md`, FEATURES.md, RAVAGER.md, PLAYER-GUIDE.md's
longest sections (the Options tab at a glance, Quality of life), PATCH-NOTES.md's headings and its Wake of the
Ravager section, CHANGELOG.md's Unreleased head, the five `.bat` files, DEVELOPMENT.md's manual section, the
startup procedure and the pictures recipes of `playtest/PLAYTESTING.md`. **Checked by tool**: every picture in
`obsidian-edition/docs/` (opened, dated, and searched for references); every label in the guide's Options
tables against `viewer.py`; the manual's page list against `manual.PAGES`; the README's default engine,
window size and version against the code. The rest of the pages (ITEMS, KITS, CREATURES, PEOPLE, GAME-BUGS,
HOW-THE-GAME-WORKS, WEAPON-SPECS, DICE-LOG, the DEVELOPMENT pages) were read in full by the follow-up
review this afternoon; here they were checked by search for the stale terms below (GOG's DOSBox as the
engine, "experimental", page counts, the sequel's gaps), not reread.

## The twelve parts

### 1. Redundancy

- **Fixed**: PLAYER-GUIDE's "Quality of life" (640 words) restated FEATURES' screens, keys, saves,
  graphics and engine in a third copy (with its own keys table and engine paragraph). Cut to 94 words of
  links.
- **(owner)** The list of what is always on is kept in four places: FEATURES' intro and its "Always on"
  section, the guide's "Options tab at a glance" (a 20-line list before its tables), and the README's
  "Loader's window" paragraph (`obsidian-edition/README.md:315-320`). Proposal: FEATURES' "Always on" is the
  home; the guide's list becomes one line linking it.
- The project README and `obsidian-edition/README.md` both carry the licence and credits. Kept: the zip
  ships only the second, the first is GitHub's front page.

### 2. Irrelevancy

Nothing new. FEATURES' engine section dates its Windows status ("2026-11-27"), which will want updating as
the Windows play reports in, not removing.

### 3. Bloat

- **Fixed**: the guide's Quality of life (above).
- **RAVAGER.md "The mod in the sequel"**: 23 bullets, the first 45 lines long, several 10 to 20. Each
  bullet is a section's worth. Proposal (for the audit thread, which is writing the sequel's side): one
  `###` per feature group, in FEATURES' order, each a few lines and a link.
- FEATURES' "New items" entry is one 25-line paragraph naming every sequel weapon's place; ITEMS.md has the
  table. It could keep the first and last sentences and link the table.

### 4. Inconsistency

- **Fixed**: FEATURES' gear picture called Gerakis "the mul gladiator"; he is the half-giant
  (`FEATURES.md` "The game's own party" table, and the picture).
- **Fixed**: `obsidian-edition/README.md:212` said the game starts "through GOG's own DOSBox"; the
  default is DOSBox-X (`dosboxx.py`, FEATURES' engine section).
- **Fixed**: the README's two Linux requirements said opposite things (**Play Shattered Lands** "Windows
  only", then "works on Linux"). Now one line: DOSBox-X on Linux first, the GOG-DOSBox fallback after.
- **Fixed**: FEATURES' Picture and music opened "Two choices for DOSBox (the DOSBox 0.74 that comes with
  GOG's game)"; they hold in both engines.
- **Fixed**: `DEVELOPMENT.md:166` said the manual has twelve pages and left out `ravager.html`; it has
  thirteen (`manual.PAGES`).
- **Fixed**: CHANGELOG's Unreleased head said "#146 to #254" though #260 and #263 are in it, and those two
  named a branch instead of their pull request.

### 5. Clarity and reorganisation (is each item where it belongs?)

- **Fixed (moved)**: FEATURES' "Magic weapons for every spec, and the mod's gear" was all about Wake of the
  Ravager (its 14 magic weapons, the plain ones in its shops, Notaku's spellbooks), filed under Shattered
  Lands' "Expanded features" with a title that didn't say so. Now RAVAGER.md's "The mod's gear in the
  sequel"; its one link updated.
- **(owner)** FEATURES still holds three other sequel-only passages: the sequel's own party table (in "The
  game's own party"), the sequel's quick saves paragraph, and its Named saves paragraph. Recommendation:
  move them to RAVAGER.md too, so FEATURES is Shattered Lands and RAVAGER the sequel's differences, each
  FEATURES entry ending with one line, "In Wake of the Ravager: yes / see RAVAGER.md / not yet". That is
  the audit thread's sequel-side work, so not done here.
- **(owner)** PLAYER-GUIDE's "The Options tab at a glance" (1,900 words, the guide's longest section) is the
  Loader's reference, not a rule: a player looks for it under the README's "Loader's window", which now
  links to it. Recommendation: move it to the README after "The Loader's window" (both ship, both are
  manual pages; anchors would change from `PLAYER-GUIDE.md#the-options-tab-at-a-glance` to
  `README.md#...`, 7 links). Not done: a move between pages goes to the coordinator first.
- **Fixed**: the README described the Options tab's Wake of the Ravager section as only "for the 6th-level
  priest spells' icons"; it also says where the sequel is for **Play Wake of the Ravager** and holds the
  "Shattered Lands' screens and icons" switch.
- **Fixed**: the project README's Wake of the Ravager link went to FEATURES' stub; it now goes to RAVAGER.md.

### 6. Patch notes

PATCH-NOTES.md (2.19.2 plus unreleased), `patch-notes.html` and `manual/changes.html` agree
(`test_patchnotes`). Every merge since #240 that a player would see has a line in PATCH-NOTES' Wake of the
Ravager section or elsewhere (the sequel's figures #250, furniture #253, SL screens #255, weights #260).
The CHANGELOG head fixed (part 4). Nothing else found.

### 7. The loader

The five `.bat` files read: each runs what the README says (`view`, `launch`, `launch --ravager`, `play`,
`save FILE`). PR #264 (in flight, the audit thread) adds the sequel's in-game-rolls start and takes
those lines off RAVAGER's gap list. The README's default engine fixed (part 4). The Loader's labels in the
guide's Options tables all match `viewer.py`.

### 8. The other documentation

See the scope above. Searches across every shipped page for "GOG's DOSBox" as the engine, "experimental"
and page counts found only the lines fixed in part 4.

### 9. Missing

- **Fixed**: RAVAGER.md never mentioned the combat log in the game (L), which the sequel has (PATCH-NOTES
  says so; `ravlog.py:301`).
- **Fixed**: RAVAGER.md's "Not in the sequel yet" lacked **scrolling the map with the mouse wheel**:
  `RavDiceLog.PASS` has no `scroll` step and `ravlog.PASS_LEFT_OUT` says "not ported"; DSCLOG2 has no wheel
  code. Now listed (a gap under the both-games rule).
- **Settled for the sequel** (in neither of RAVAGER's lists at first; the follow-up PR, from the sequel's
  patches, `ravager.PATCHES`): the Effects screen's click is there (`effects_click_low/high`), now listed;
  more save pages (2 to 4), 29 characters in the roster, steady pace, the view in fights, the pointer in
  scenes and the whole party in view have no patch in the sequel (Shattered Lands' `save_page`,
  `characters_*`, `pace_pass`, `camera_still`, `cine_step`/`mouse_set`, `party_spread`), now on "Not in the
  sequel yet". Game speed itself applies to both games (`launch.cpu_lines`).
- **ITEMS.md had nothing of the sequel** (the user's ask, after the review): it now has every Wake of the
  Ravager item, from the sequel's data, with its icons.

### 10. Screenshots

All 65 pictures in `docs/` opened. None is an orphan (each is referenced by a shipped page).

- **Retaken**: `fogbolt.png` (the user's own party, before the outfits): Lex casting Fogbolt at a Templar
  in Pehtucl's ambush, the bolt in flight, the party in its outfits
  ([the play](../playtest/logs/2026-11-27-docs-review-pictures.md)). A loop of window grabs caught the bolt
  that the last pass's Ctrl+F5 loop missed (now in the guide's pictures recipes).
- **Current** (checked): `show-usable.png` has no party in it; `half-elves.png` shows the bare race figures
  on purpose and its text says so; the Loader's window pictures were retaken this morning.
- **Before the outfits, retaken** (the follow-up PR): `kalzith.png`'s talk (its shop half kept: no map
  figures) and `kalzith-body.png`. **Corrected**: this pass first listed nine pictures; the Effects,
  inventory and USE screens' portraits aren't dressed by the outfits (only the map figures and the creation
  figure are), so `new-spells-effects.png`, `effects-weapons.png`, `effects-charges.png` and
  `default-party-gerakis.png` were current, and the figures in `pens-asks*.png` and `semyon-escape.png` are
  the Trustee, Dinos, Scar's gladiators and Semyon, not the party.
- `new-priest-spells.png` is 1920x1600, ten USE-screen boxes too small to read on the page at its shown
  width. A table of the ten spells (the guide has one) does that job; the picture could shrink to two or
  three boxes as a sample.

### 11. Tables

Checked: the guide's Options tables (every label against `viewer.py`; defaults against FEATURES' intro), the
README's suggested requirements (the three speeds' cycles against FEATURES), FEATURES' new wizard spells
(Fogbolt's 2d4 rounds against the dice log in play: "Fogbolt lasts 6 rounds ... dice 2d4 = [3 + 3]"), the
sequel's magic weapons table (moved unchanged). Nothing wrong found.

### 12. Features

FEATURES, the README's eight families, PATCH-NOTES' At a Glance and the manual's features page agree on
what is listed. The README's "What it does" names graphics as "the party's gear on its figures" where
FEATURES leads with the class outfits; PATCH-NOTES' At a Glance has the same gap ("The figures show the gear
they wear") though its Graphics section has the outfits. Small; left for the release pass, which rewrites
At a Glance.

**Is anything missing?** The sequel's side of several features (part 9), the scrolling gap (now listed),
and a fresh look at the small pre-outfit figures one day. **Are items where they belong?** Mostly; the
sequel-only passages still in FEATURES and the Options reference in the player's guide are the two that
aren't (part 5, owner).

## Findings, ranked

1. **Wrong** (fixed): README's start "through GOG's own DOSBox"; README's contradictory Linux lines;
   FEATURES' "mul" Gerakis; Picture and music tied to GOG's DOSBox; DEVELOPMENT's twelve manual pages.
2. **Missing** (fixed): the sequel's combat log on RAVAGER.md; the mouse-wheel scrolling gap; the seven
   features unverified for the sequel (part 9: six more gaps listed); the sequel's items in ITEMS.md.
3. **Structure**: sequel gear moved to RAVAGER.md (fixed); the guide's Quality of life cut (fixed);
   **(owner)** the Options reference to the README, the other sequel-only passages to RAVAGER.md, and one
   home for the always-on list.
4. **Links**: the project README's sequel link (fixed). `test_doclinks` and `test_manual` pass.
5. **Pictures**: `fogbolt.png`, `kalzith.png` and `kalzith-body.png` retaken; `new-priest-spells.png`
   too big to read.
6. **Reader tasks**: none new.
7. **Bloat**: RAVAGER's long bullets, FEATURES' New items paragraph (proposals above).

## Checked and correct

The `.bat` files; the Options labels; `manual.PAGES`; the version (2.19.2) in the README, PATCH-NOTES and
`dsloader/__init__.py`; the default window size (Triple, `DEFAULT_SCALE` 3); the doc tests and the full suite.

## Not verified

The ITEMS, KITS, CREATURES, PEOPLE, GAME-BUGS, HOW-THE-GAME-WORKS,
WEAPON-SPECS and DICE-LOG pages beyond the searches (the follow-up review read them today).
