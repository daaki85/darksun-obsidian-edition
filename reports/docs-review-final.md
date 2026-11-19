# Documentation review, final pass before a release (2026-11-19)

*Status: applied on branch `claude/final-audit-fixes` (2026-11-19), every numbered item, with
these as they stand: item 6's GAME-BUGS row not added (in the original game a round's attacks are
all from behind or none, by the target's facing, so the carry-over never showed there; the patch
note's "was" names the attack routine's way instead); item 30 no change, as the review says;
item 32 made "(the kit's die)"; item 25's option taken (the second review and its verified version
in `reports/archive/`). Below is the review as it was made: a review of the player pages, the change records and the
generated manual and patch notes, the developer pages, the playtest kit, `reports/`, CLAUDE.md, the
Loader's text and the pictures in `docs/`, at `f1f8972` (branch `claude/backstab-str-line`:
`origin/obsidian-edition` at `412bbf3`, #115, plus the unmerged backstab fix). Line numbers are at
`f1f8972`. Every finding was checked against the code or the files, each side cited; what could not
be shown was dropped.*

## The short version

30 findings in 33 numbered items (three point back to another or keep a thing as it is), in the groups the verified second review used. The worst:

- **The CHANGELOG lost its header and its Unreleased heading in #113** (`CHANGELOG.md:15-17`): the
  Headings rule stops mid-sentence, the Sections rule and the list of releases are gone, and the
  Unreleased entries sit under no heading. The release steps (`DEVELOPMENT.md:295-302`) rely on
  both.
- **The multiclass rule is still wrong in three places**: the patch notes say every class must allow
  an item (`PATCH-NOTES.md:64`), and FEATURES' table and entry say the strictest class replaces the
  game's one-class lists (`FEATURES.md:155`, `:173-174`).
- **The root README says "Nearly every rule change and addition has a switch"** (`README.md:7-8`);
  five rules and the new content have one.
- **About 40 places on the player pages still write an always-on rule as a switch** ("on by
  default", "with X on", "with Weapon specialization ticked", "with [the rule]"), and the dice log
  page lists lines that only a game without the rule could show.
- **The developer pages and the playtest kit still describe DSCLOG's off paths, which #115
  removed**: "DSCLOG still tests the bit" (`DEVELOPMENT-RULES.md:472-473`), "puts it back when the
  rule is unticked" (`:882`), and `setmem.py ruleshi=-N` to turn a rule off (`RESEARCH.md:211`,
  `:213`, `:312`), which now changes nothing.
- **The backstab branch's patch-notes line** (`PATCH-NOTES.md:105`) gives the mod's 2.18 behaviour
  as "was", not the original game's. Its "(were ...)" also misses the old-value style on the web
  pages.
- **DSCLOG's size in the memory table is one build behind** (`DEVELOPMENT-INTERNALS.md:224`: 69,936
  bytes; the backstab build is 69,984).
- **`docs/dicelog-readable.png` shows a line the backstab fix changes**: a later swing "from
  behind" with no "+2 STR".

The tests pass. The generated manual, patch notes and TOOLS.md are current. Every picture is
referenced. The Options tab's picture matches the code.

## How it was checked

- **The switches.** The code's list is `game.RULE_SETTINGS` (`dsloader/game.py:294-295`: `helm_ac`,
  `new_spells`, `half_giant_hands`, `best_hit_die`, `kits`) and `game.ALWAYS_ON` (`:312-315`). The
  Options tab's content is `viewer.py:374-470`.
- **DSCLOG.** It now tests five rule bits only: `grep "test .*\[cs:rules"` in `dos/dsclog.asm`
  finds `RULE_HELMS` (3047, 3068), `RULE_HALF_GIANT` (4354, 18990), `RULE_HP_BEST` (18635),
  `RULE_NEW_SPELLS` (9625 ...) and `RULE_HI_KITS` (3530 ...). The only other read of the word is
  `ns_setup`'s `mov al,[cs:rules] / and al,RULE_NEW_SPELLS` (19810). Anything a page says DSCLOG
  does "with the rule off" for another rule is gone. Examples: `held_damage` is `mov ax,[bp-4] /
  iret` (17633-17635), and `stab_times` has no rule test (14391-14415).
- **The memory figures.** DSCLOG was rebuilt with `[map all]`: the build is byte-identical to
  `dos/DSCLOG.EXE`. The map gives `KEPT_PARAS` 1106h, `UMB_KEPT` 1F8Ch, `UMB_NEED` 1936h,
  `FAR_END` FFDCh, `kept_end` FAC0h and `resident_end` F6E0h.
- **The generated files.** `manual.outputs()` and `patchnotes.build()` were compared with the
  committed files: all 13 manual files and `patch-notes.html` are identical. `tools_index.py` was
  run on a copy: TOOLS.md is identical.
- **The tests.** `python3 -m unittest discover -s tests` ran 1,982 tests, OK, 60 skipped. With
  `DSUN_GPLDATA`, `DSUN_OBJECTS` and `DSUN_RESOURCE` (from `/tmp/playtest/inst`) it ran 1,982, OK,
  17 skipped: 43 more ran, as `DEVELOPMENT.md:290` says. `test_doclinks`, `test_manual*`,
  `test_patchnotes`, `test_optionstable`, `test_release`, `test_version`, `test_doccreatures` and
  `test_docicons` are among those that passed.
- **The pictures.** Each was judged from its file and its last commit (`git log -- docs/`). Each
  top-level picture was searched for by its file name, and the item and creature pictures by
  `items/NAME` and `NAME` in their pages. DOSBox was not started.

## The fixes

### Wrong against the code

1. **The CHANGELOG's header and Unreleased heading, lost in #113.**
   - What is there now: `CHANGELOG.md:15-17` reads `**Headings.** Work on the branch
     \`obsidian-edition\` not yet merged to \`main\` is / under "## Unreleased (branch
     \`obsidian-edition\`)`, and the next line is `**New**`.
   - What was lost: `git show ea06199^:CHANGELOG.md` lines 15-61 had the rest of the Headings rule
     ("when its pull request is merged, that heading becomes ..."), the **Sections** rule (New,
     Changed, Fixed, Docs, Dev), the list of releases with their anchors, and the heading
     `## Unreleased (branch \`obsidian-edition\`)` itself. `grep "^## " CHANGELOG.md` now starts
     at "Pull request #96".
   - What depends on it: `DEVELOPMENT.md:295-302` (release step 5) says to rename that heading
     and to "point the release's link in the list of releases at the top"; neither exists.
   - The fix: restore those lines from `ea06199^`, keeping the Unreleased entries under the
     heading.
2. **The multiclass rule, still wrong in three places.**
   - The rule: the game's own lists need only one class, and the mod's limits apply to every
     class, the strictest winning. Both the code (`dsloader/restrict.py:1-4`: "on top of the
     game's own class lists ..., of which one of the character's classes is enough") and the guide
     (`PLAYER-GUIDE.md:330-331`) say so.
   - `PATCH-NOTES.md:64`: "every one of a character's classes must allow an item *(was any
     one)*". That is the wrong rule, and it reaches `patch-notes.html` and `manual/changes.html`.
   - `FEATURES.md:155` (the table): the game's "Any one class allowing an item is enough" against
     the mod's "The strictest class wins".
   - `FEATURES.md:173-174`: "the strictest winning, where the game let any one class allow an
     item".
   - The fix: say it as the guide does. "The strictest class decides" (`PLAYER-GUIDE.md:246-248`)
     is loose too, but it links the table, so it can stay.
3. **`README.md:7-9` (the root README)**: "Nearly every rule change and addition has a switch on
   the Loader's Options tab". The code has five rule switches, the new content's six, fuller gear,
   the Look box, names, the ring, the log's level and the speed (`viewer.py:384-470`); over twenty
   rules are always on (`game.RULE_SETTINGS_GONE`). The fix: as the folder README has it
   (`obsidian-edition/README.md:64-65`): most is always on; the new content and a few rules have a
   switch.
4. **`obsidian-edition/README.md:186-189`**: "pick what you want: the rule changes, the new content,
   picking pockets, the combat log in the game and so on". Picking pockets (`pickpockets`) and the
   combat log (`combat_log`) are in `game.ALWAYS_ON`, and so are most rule changes. The fix: "the
   new content, a few rules, the combat log's level ...".
5. **`obsidian-edition/README.md:218-220`**: Play Dark Sun "uses the switches ... (the combat log,
   monster descriptions, picking pockets, the rule changes)". Picking pockets has no switch, and
   the combat log has only its level.
6. **`PATCH-NOTES.md:105`** (the backstab branch's line): "*(were 2 worse to hit than a plain
   attack, yet treated as from behind)*".
   - The "2 worse" came from DSCLOG's `STAB_FIRST`: `DEVELOPMENT-RULES.md:1763-1782` and
     `playtest/logs/2026-11-19-backstab-str-line.md` §2. That is the mod's 2.18 behaviour, but the
     patch notes record changes from the original game (`PATCH-NOTES.md:1-3`, `:23`).
   - "(were" isn't "(was": `patchnotes.py:42` styles only `<em>(was ...)</em>`, so on
     `patch-notes.html` and `manual/changes.html` the line has a plain `<em>` where every other has
     `span.was`.
   - The fix: keep only what the original game did. By the log's §2 that is the later swings
     treated as from behind: the target's DEX and shield ignored, with no +2. Write it as "*(was
     ...)*" and leave the −2 to the CHANGELOG. If that carry-over is the game's own, GAME-BUGS needs
     a row too; it has none (`grep -i backstab GAME-BUGS.md`).
7. **`DEVELOPMENT-RULES.md:472-473`**: "DSCLOG still tests the bit" (`RULE_TWO_WEAPONS`). It doesn't:
   the bit appears only in comments and `equ`s (`dsclog.asm:3477`, `3665`, `8627`, `18056`,
   `18122`).
8. **`DEVELOPMENT-INTERNALS.md:224`**: "DSCLOG 68.3 KB (69,936 bytes with its PSP and its tail, (10h
   + `KEPT_PARAS`) paragraphs)".
   - The backstab build's `KEPT_PARAS` is 1106h: (16 + 4358) × 16 = **69,984** bytes.
   - The free piece "26,304 bytes ... (this build)" was measured on #115's build
     (`logs/2026-11-19-free-dsclog-room.md`), and DSCLOG is 48 bytes (3 paragraphs) bigger now.
   - The fix: correct the figure, and re-measure the free piece (or date it).
   - The limits table under it (`:238-241`) is right: it matches the map.
9. **The window rule's reason** (`CLAUDE.md:28-29`, `playtest/PLAYTESTING.md:94-99`): "at 960x720
   every pixel check (msgbox.sh, levelup.sh, panel.sh) then fails".
   - Those three go through `pixmatch.py`, which samples any grab down to 320x240 first
     (`pixmatch.py:18-20`; `msgbox.sh:8-9`); the guide's own next sentence says so.
   - What does need 320x240 is the raw grabs: `figcheck.py:29` clips at 320x240 with the 1.2 row
     scale, and `walkprobe.py`, `figwatch.py` and `ghostturn.py` grab too.
   - The fix: keep the rule and correct its reason, in both places.
10. **Memory edits that no longer do anything** (the playtest kit):
    - `RESEARCH.md:210-211`: "`setmem.py ruleshi=-16384` / `=16384` turns the size rule off and
      on".
    - `RESEARCH.md:212-214`: "with `held_hit` off, the game's damage routine ... A `setmem.py
      ruleshi=-32768` changes DSCLOG".
    - `RESEARCH.md:311-313`: "`setmem.py ruleshi=-2048` turns the rule off in DSCLOG's header for a
      comparison".
    - `TOOLS.md:101` and `setmem.py:2-3`: the example bits "2048 dual-classing, 4096 resting".
    - `PLAYTESTING.md:580`: "AD&D's when the header's rules_hi, +270, has 8".
    - What the code does: since #115 only `RULE_HI_KITS` (1) is read in `rules_hi`
      (`dsclog.asm:3530` ...), and `PLAYTESTING.md:534-538` already says so ("changes nothing").
    - The fix: point these at that note or at "an older build"; for setmem.py, edit its header and
      run `tools_index.py`.

### Rules always on, still written as switches: the player pages

11. **`PLAYER-GUIDE.md:936`**: "its XP tables go on to 20th (with AD&D's off, druids by a table of
    their own)". `adnd_tables` is in `ALWAYS_ON`, so there is no "AD&D's off".
12. **"(a rule change, on by default)"**: `PLAYER-GUIDE.md:1446` (spells roll to hit),
    `:1463-1464` (spells as the manual describes them) and `:1638` (resting). `spell_to_hit`,
    `spells_manual` and `rest_heal` are all in `ALWAYS_ON`. The fix: "(a rule change, always on)".
13. **"With X on" for an always-on rule**: `PLAYER-GUIDE.md:1613` ("with ages on", Hasted),
    `PATCH-NOTES.md:137` ("with ages on, hair greys") and `PATCH-NOTES.md:151` ("with shadows and
    dust on"). `aging`, `shadows` and `dust` are in `ALWAYS_ON`. The fix: drop the condition.
14. **KITS, WEAPON-SPECS and ITEMS**:
    - `KITS.md:204`: "with the rule for INT on" (`int_learning`).
    - "with the stealth rule" (`stealth`): `KITS.md:438`, `FEATURES.md:561` and `ITEMS.md:193`.
    - "With **Weapon specialization** ticked" (`weapon_specialization`; the tab has no such box):
      `KITS.md:740` and `WEAPON-SPECS.md:8`.
15. **`HOW-THE-GAME-WORKS.md:437` and `:684`**: Spells and psionics as the manual describes them,
    "on by default" (684 also "from the next start"); `spells_manual` is in `ALWAYS_ON`.
16. **Weapon traits written as conditional**:
    - "with [the rule](FEATURES.md#polearm-reach)" or "#staff-sling-stinkpots": `ITEMS.md:56`,
      `:57`, `:73`, `:96`, `:265`, `:266`, `:275` (`cahulaks` is in `ALWAYS_ON`). The fix: "(its
      reach: [polearm reach](...))".
    - `FEATURES.md:1128`'s alt text has "(with creature size on: ...)".
17. **The dice log page lists lines only a game without the rule shows.** No game the Loader starts
    lacks these rules, and a game started without it has no dice log (`obsidian-edition/README.md:211-214`).
    - `DICE-LOG.md:67`: Biofeedback's "the game takes 2 off (to 0 ...; with the manual's spells at
      least 1 is left)".
    - `DICE-LOG.md:145`: magic resistance "halved by one ..., or, with the manual's spells, 30% +
      1%", and "(the game's rule; with the manual's spells, the bigger of the two)".
    - `DICE-LOG.md:150`: the whole "Turn Undead, the game's own rule" bullet; the game's d20 behind it
      (7AE4Dh) "is never reached" with the manual's spells in the copy (`DEVELOPMENT-RULES.md:1092`),
      which they always are now.
    - `DICE-LOG.md:159-163`: "With the rule changes off, the game uses petrification/polymorph ...;
      with them on (always, with the mod)".
    - `DICE-LOG.md:207`: "only in a game that still takes the game's equipment penalty".
    - `DICE-LOG.md:212`: "(with hiding to backstab on)".
    - `DICE-LOG.md:234`: "every 5 minutes of game time in the game, or at AD&D's rate by CON with
      CON as in AD&D".
    - `GAME-BUGS.md:111`: "the dice log's `-5 equipment` ... shows only for a game that still takes
      it".
    - The fix: give the mod's line only, and link HOW-THE-GAME-WORKS for the game's way.

### Off paths still described: the developer pages and the playtest kit

18. **DEVELOPMENT-RULES' sections describe the "rule off" paths that #115 took out of DSCLOG.**
    - The note at `:116-117` asks the reader to read every "with the switch off" below as the
      game's own way, "which DSCLOG no longer has".
    - The sections still state it as DSCLOG's behaviour:
      - `:173`: multiclass HP, "or the rule off: the game's own".
      - `:272`: the class tables, "or with the rule off, the routine as it was".
      - `:629`: `HELD_DAMAGE` "doubled only without the rule"; the code never doubles.
      - `:880-882`: the spell save, "puts it back when the rule is unticked"; `set_rules`
        (`dicelog.py:1027-1032`) writes `kind_to_save` with the bit always in.
      - `:981-982`: resting, "the game's own instruction with the rule off".
      - `:1092-1093`: Turn Undead, "the old dice log line ... is only the switch-off one".
      - `:1739-1745`: "Part of the switch Thieves as in AD&D ... applied whatever the switch, the
        rule's bit read at the time": `stab_times` reads no bit.
      - `:1757-1760` and `:1784-1786`: "without the rule".
    - The fix: say the rule's way as the only way and drop the note; where the game's way matters,
      name it as the game's (as `:615-621` does).
19. **`DEVELOPMENT-SCREENS.md:175-177`**: "The Loader sets `panel_on` ... in a fight with the switch
    on". The combat log has no switch, and the panel shows out of fights too (`combatlog.py:897-900`;
    `FEATURES.md:46`). **`:750-751`**: Effects kept "with the switch on (`gamepatch.EFFECTS_KEPT`,
    from the next start)": `effects_kept` is in `ALWAYS_ON`, and `launch.py:567-569` leaves out only
    Steady pace's patches.
20. **`PLAYTESTING.md:894`**: "with `spell_to_hit` on"; **`:527`**: "with weapon specialization on
    or off". Both are always on (`:534`).

### The change records

21. **`CHANGELOG.md:90-93`**: "DSCLOG's room freed (no pull request yet: branch
    `claude/free-dsclog-room`)". It merged as #115 (`412bbf3`): number it.
22. **`CHANGELOG.md:54-57`** (the backstab fix):
    - It has no pull request or branch marker; the rule is a number on every entry, and the #115
      entry shows the form ("no pull request yet: branch ...").
    - It is four lines of mechanism (the +2s, "THAC0 17 for 15", the dice log's "-2 STR"); the
      header asks for what and why in a few lines (`:10-11`), and the detail is already in
      `DEVELOPMENT-RULES.md:1771-1782`.
    - The fix: "A thief's later attacks in a round after a backstab are judged on their own (no
      pull request yet: branch `claude/backstab-str-line`)", and a clause on what the player saw.
23. **The sections' order and labels** in Unreleased (New, Changed, Fixed, Docs, Dev) are right. The
    rule that defines them is lost with item 1, so restore it there.

### Lost or missing

24. **`docs/dicelog-readable.png`** (`README.md:403`; last changed `605f728`, 2026-11-10) shows
    Seneca's Shadowseeker swing after her backstab as "from behind": "to hit: THAC0 19, +2 from
    behind, +1 weapon, +1 specialized = 15". There is no "+2 STR", though her first line has one.
    That is the carried-over flag the backstab branch fixes (`logs/2026-11-19-backstab-str-line.md`
    §1-3: after the fix the swing reads "THAC0 19, +2 STR, +1 weapon, +1 specialized = 15"). The
    fix: retake it once the fix is merged.
25. **Statuses in `reports/`**:
    - `reports/archive/docs-review.md:3` says "findings only, nothing changed yet", and
      `reports/archive/docs-proposal.md:3` says "a proposal, nothing done". Both were acted on in
      #100-#105 (CHANGELOG:62-74).
    - `reports/opends-rules-comparison-2026-11-18.md:7-8` calls the "Rules the game got wrong"
      table's rows "each with a switch"; all are always on since #110.
    - Optional: the second review and its verified version, which #113 acted on, live only on
      `origin/claude/docs-review-2`. `DEVELOPMENT.md:127` says `reports/` keeps the reviews.

### History in references

26. **FEATURES' "whose switches are gone"**: `FEATURES.md:7-8`, `:793-794` ("the Options tab's
    **Expanded features** section ... are gone"), `:870-871`, `:956-957` and `:1035` ("The switches
    gone from the Options tab"). Readers of a release never saw those switches. The fix: "always on"
    alone, keeping the page's order note ("then the sections that are always on").
27. **`DEVELOPMENT-INTERNALS.md:231-233`**: "The always-on switches' off paths, taken out on
    2026-11-19, freed 1,168 bytes of it". That is a change record, already in the CHANGELOG
    (`:90-93`). The fix: cut it, or link #115.
28. **`dsloader/game.py:296-299`**: "(after 2.18, the owner's call ...) ... Their off paths are
    still in DSCLOG and here". The second half is wrong since #115 (see How it was checked), and
    `:482-484` ("the user's call") is a story. The fix: the rule without the history.

### Repetition and things in the wrong place

29. **The backstab patch-notes line** (item 6): the mod's own regression belongs in the CHANGELOG
    only.
30. **`DEVELOPMENT-RULES.md:84-107`** ("What went (2026-11-19 ...)"): a list of removed symbols,
    which the commit messages of #115 hold too. It agrees with them, so it is kept as it is; only
    the date heading is history (a candidate for item 27's treatment).
    The copies of "every switch on by default, the three choices, the rest always on"
    (`FEATURES.md:14-21`, `README.md:278-286`, `PLAYER-GUIDE.md:2048-2085`, `PATCH-NOTES.md:21`,
    `:164`) agree with each other and with the code: no change.

### Smaller: the code's text and the Loader's messages

31. **Docstrings that still call always-on rules the Options tab's**: `restrict.py:1` ("Class
    restrictions (the Options tab's rule)"), `specialize.py:1` ("Weapon specialization (the Options
    tab's rule)") and `monsters.py:219` ("(its spells' switch)").
32. **The dice log's user-visible "(the helper's roll)"** (`dicelog.py:3325`, documented at
    `DICE-LOG.md:95-96`): a Lifebinder's extra die. "Helper" is opaque to a player. Optional:
    "(DSCLOG's roll)" or "(the kit's die)", with the page. `launch.py:1158`'s "runs the game with
    the helper" and the README's "the dice log helper" are kept: the player pages use the word
    consistently.
33. **`README.md:25-26`** (the root README): "[the full list of pages](obsidian-edition/README.md)"
    goes to the same place as "The full documentation" on the line above. The fix: link the folder
    README's `#contents`, or drop it.

## Checked and clean

- **Generated files**: the manual's 13 files and `patch-notes.html` match their Markdown; TOOLS.md
  matches the tools' headers; the creature and item pages' tests pass.
- **Tests**: the doc and link tests and the full suite pass, with and without the game's files (43
  more run with them, as DEVELOPMENT.md says).
- **Pictures**:
  - Every picture in `docs/` is referenced: 58 top-level, 148 items and 189 creatures, and no link
    points at a missing one.
  - `options.png` matches `viewer.py`'s sections and labels word for word.
  - `viewer.png`, `elvenkind.png` (retaken in #113) and `look-box.png` match what their captions
    say.
- **The Options tab at a glance** (`PLAYER-GUIDE.md:2028-2159`): it matches the code
  (`test_optionstable`). Its always-on list covers `game.ALWAYS_ON`; "Which Options sections are
  open: all closed" is right (`viewer.py:363-370`); Restore defaults leaves the Elsewhere settings
  be.
- **FEATURES' "Rules the game got wrong"**: every row is in `RULE_SETTINGS_GONE` or always on.
- **Counts and constants**:
  - "Twenty-two new magic weapons" (PATCH-NOTES:17, :113; FEATURES:681): 19 in the weapons table
    (21 bold, less the re-plused Gythka +2 and Cahulaks +2), and Windlash, Skycutter and Dunesong.
  - `DSCLOGvc` (`dicelog.py:40`, `dsclog.asm:191`, DEVELOPMENT.md:138, DEVELOPMENT-INTERNALS:194).
  - The room table's `kept_end`, `resident_end`, `UMB_NEED`, `UMB_KEPT` and `FAR_END`.
  - `DSCLOG.EXE`'s 69,760 bytes, and the 43 extra tests.
- **The developer pages' coverage**: every `dsloader` module is in DEVELOPMENT.md's module map;
  DEVELOPMENT-RULES' "The switches always on" matches `game.py`; `.gitattributes` matches
  DEVELOPMENT.md's zip paragraph.
- **The playtest kit**: every save in `playtest/saves/` is in its README, and every log in
  `logs/README.md`. The backstab branch's additions to PLAYTESTING, RESEARCH and HISTORY are in
  place and agree with its log.
- **CLAUDE.md and the guide**: CLAUDE.md agrees with the guide's checklist (pgrep forms, the Xvfb
  restart, the lock, the branch rule, the 320x240 rule), but for item 9's reason.
- **The second verified review's fixes**, spot-checked, are in:
  - the twenty shimmering icons (PATCH-NOTES:136);
  - "for each 5 gladiator levels" (GAME-BUGS:119);
  - "Started without ..." in Troubleshooting (README:538);
  - `py -3-64` (README:245-251);
  - the guide's multiclass sentence (PLAYER-GUIDE:330);
  - DICE-LOG's "can't break" indent (:313, :322);
  - the Elvenkind numbers (PLAYER-GUIDE:1171-1174);
  - the OpenDS reports' status lines.
- **Fine as they stand**: the player pages' use of "the helper" and the root README's "What's new"
  (2.18.0, the current version).

## The fix list

### Wrong

1. CHANGELOG.md:15-17: restore the header lines and the `## Unreleased (branch
   \`obsidian-edition\`)` heading from `ea06199^` (lines 15-61), so DEVELOPMENT.md's step 5 can be
   followed.
2. The multiclass rule: PATCH-NOTES.md:64, FEATURES.md:155 and FEATURES.md:173-174 as PLAYER-GUIDE
   :330 has it (the game's lists need one class; the mod's limits hold for every class, the
   strictest winning). Then rebuild the manual and the patch notes.
3. README.md:7-9 (root): most is always on; the new content and a few rules have a switch.
4. obsidian-edition/README.md:186-189: not "picking pockets, the combat log", and not "the rule
   changes" as switches.
5. obsidian-edition/README.md:218-220: the same list for Play Dark Sun.
6. PATCH-NOTES.md:105: the original game's behaviour as "*(was ...)*" (the styled form), the mod's
   −2 left to the CHANGELOG; a GAME-BUGS row if the carry-over is the game's.
7. DEVELOPMENT-RULES.md:472-473: DSCLOG no longer tests `RULE_TWO_WEAPONS`.
8. DEVELOPMENT-INTERNALS.md:224: 69,984 bytes, and the free piece re-measured (or marked as #115's
   build).
9. CLAUDE.md:28-29 and PLAYTESTING.md:94-99: 320x240 for the raw grabs (figcheck.py and the like);
   the pixmatch checks sample down.
10. RESEARCH.md:210-211, :212-214 and :311-313, TOOLS.md:101 and setmem.py:2-3 (then
    `tools_index.py`), and PLAYTESTING.md:580: no rule bit but `RULE_HI_KITS` changes anything in
    `rules_hi`.

### Rules always on, still written as switches

11. PLAYER-GUIDE.md:936: drop "with AD&D's off ...".
12. PLAYER-GUIDE.md:1446, :1463-1464, :1638: "(a rule change, always on)".
13. PLAYER-GUIDE.md:1613, PATCH-NOTES.md:137 and :151: drop "with ages on" and "with shadows and
    dust on".
14. KITS.md:204, :438 and :740, WEAPON-SPECS.md:8, FEATURES.md:561 and ITEMS.md:193: no "with the
    rule for INT on", no "with the stealth rule", no "Weapon specialization ticked".
15. HOW-THE-GAME-WORKS.md:437 and :684: "always on".
16. ITEMS.md:56, :57, :73, :96, :265, :266, :275 (Weapon traits) and FEATURES.md:1128's alt text: no
    conditional.
17. DICE-LOG.md:67, :145, :150, :159-163, :207, :212, :234 and GAME-BUGS.md:111: the mod's line
    alone.

### Off paths in the developer pages and the kit

18. DEVELOPMENT-RULES.md:173, :272, :629, :880-882, :981-982, :1092-1093, :1739-1745, :1757-1760,
    :1784-1786: the rule's way as the only way; drop the blanket note at :116-117.
19. DEVELOPMENT-SCREENS.md:175-177 and :750-751.
20. PLAYTESTING.md:527 and :894.

### The change records

21. CHANGELOG.md:90: #115.
22. CHANGELOG.md:54-57: a branch marker, and a few plain lines.
23. The Sections rule restored with item 1.

### Lost or missing

24. docs/dicelog-readable.png: retake after the backstab fix merges.
25. reports/archive/docs-review.md:3 and docs-proposal.md:3: "acted on (#100-#105)";
    opends-rules-comparison-2026-11-18.md:7-8: "(each with a switch then)". Optional: bring the
    second review and its verified version into `reports/archive/`.

### History in references

26. FEATURES.md:7-8, :793-794, :870-871, :956-957, :1035: "always on", without "is gone".
27. DEVELOPMENT-INTERNALS.md:231-233: cut the dated note, or link #115.
28. dsloader/game.py:296-299 and :482-484: correct "still in DSCLOG", and drop the stories.

### Repetition and wrong place

29. With item 6.
30. No change (the copies agree).

### Smaller

31. restrict.py:1, specialize.py:1, monsters.py:219: not "the Options tab's rule" or "switch".
32. Optional: dicelog.py:3325's "(the helper's roll)" and DICE-LOG.md:95-96.
33. README.md:25-26 (root): link the folder README's `#contents`, or drop the duplicate.
