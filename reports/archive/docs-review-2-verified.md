# Documentation review, second pass: verified (2026-11-18)

*Status: acted on (#113). Every finding of [the second review](docs-review-2.md)
re-checked against the code and pages at `1051ee3` (after #109-#112), each rederived rather than
taken from the review. Only what holds is listed below, with the fix corrected where the review
was off. Line numbers are at `1051ee3`.*

## How the review held up

| | Confirmed | Partly | Moot (since fixed) | Refuted |
|---|---|---|---|---|
| 1. Wrong against the code (22) | 14 | 4 | 3 | 1 |
| 2-3. Missing, change records (21) | 17 | 1 | 2 | 0 |
| 4-6. History, repetition, smaller (23) | 13 | 7 | 2 | 1 |

Mostly right on substance. Its errors: **overreach** (the multiclass rule: only one sentence is
wrong, not the table), **a stale snapshot** (several findings fixed by #110-#112; its own
"corrected" memory figures out of date too), **missing places** (the divide-by-zero claim is also
in a developer page and a code comment), **loose counts**, **repetition taken as harmful without
checking the copies disagree**, and one finding made by grepping only full file names. It also
**understated** in places, and the check found new problems: text still treating now-always-on
rules as switches.

**Refuted** (no change): "the Flame Blade a long sword" in WEAPON-SPECS is clear in context; the
six logs/img pictures are referenced (by short forms like `-hits.png`).
**Moot**: class restrictions now always on; the spell records' end and the overrun (#111); the
start-up hook (#112); Named saves in the README (#112); the manual-page and CHANGELOG-archive tests
(#112); the Options labels' headings (#110); dsclog.asm's stale comment.

## The fixes

### Wrong

1. PLAYER-GUIDE.md:330 and the Magic weapons by class intro (:1790): one class's place on the
   game's list is enough; the mod's limits take the strictest. New wording: "A character may use an
   item if the game lets any one of its classes use it, and none of its classes' limits below
   forbids it: of those limits, the strictest wins." The intro: "A character of several classes may
   wield those any of its classes may, less what any class's limits forbid (a cleric's sphere, a
   psionicist's weapons)." The table rows and single-class notes stay.
2. The Magic weapons by class table: add the Battle Dancer (long swords and bows, any sphere) and
   the psionicist with a warrior or thief class (also Greenbright, Shadowseeker, the maces, slings).
3. obsidian-edition/README.md:107: a non-GOG DSUN.EXE starts **the original game, without the mod**
   (and says why), not "without the dice log".
4. obsidian-edition/README.md:32: the zip's copy of the patch notes is `manual/changes.html`;
   `patch-notes.html` is beside the zip on the Releases page.
5. obsidian-edition/README.md:113: on Linux only the party view can follow a DOSBox you start
   yourself (the dice log needs DSCLOG and the patched game, which only `launch` prepares).
6. README.md:16: the `.bat` files offer to install Python, not the Loader.
7. PATCH-NOTES.md:135: twenty shimmering icons, not nineteen.
8. PATCH-NOTES.md:115: the Fine Bow isn't magic.
9. The random monsters' "Divide error": the game's data has no zero divisor (checked in RESOURCE.GFF:
   empty slots are (0,1)). Drop the crash clause in PATCH-NOTES.md:188, GAME-BUGS.md:87,
   DEVELOPMENT-CONTENT.md:259-266 and gamepatch.py:489's comment; keep the wrong-count fix.
10. "Out of memory in OEOpenGraph" (PATCH-NOTES.md:202, GAME-BUGS.md:145): it came with the mod's
    memory use (release-notes/v2.6.0.md: 53 KB with the mod against the original's 57 KB); nothing
    shows the original game failing. Move it out of the game's bugs, to the mod's own memory work.
11. DEVELOPMENT-CONTENT.md ~1350: the defiler champion's scroll is Fogbolt, Spook or Reflected Image
    with the new spells, else a game spell (`defilerscrolls.spells`).
12. DEVELOPMENT-INTERNALS.md:225: "29,616 bytes free in one piece" is stale (and the review's
    ~29,520 too): with UMBPLUS at CA00h at most ~25,300. Re-measure with `memaudit.py`.
13. DEVELOPMENT.md:121: the folders table's player pages lack WEAPON-SPECS.md and PEOPLE.md.
14. DEVELOPMENT-KITS.md:703-705 (and spellarrows.py:18, PLAYTESTING.md:596): strays come out of the
    quiver when there's no Spellarcher **or no room in its pack**; the sentence is also garbled.
15. KITS.md:389: the Military Scout's +1 includes the staff sling (as :429 already says).
16. GAME-BUGS.md:119: "for each 5 gladiator levels".
17. playtest/RESEARCH.md:59: making a Spellarcher in memory also needs the class mask (+12h, the
    fighter's bit), as PLAYTESTING.md:593 has it.
18. playtest/setitem.py:7: the log is 2026-11-18-item-glows.md.

### Rules now always on, still written as switches (found by the check)

19. obsidian-edition/README.md:330 and PLAYER-GUIDE.md:1365-1367: AD&D's class tables "on (the
    default)" / "only with": always on.
20. FEATURES.md:551-552: the game's own party "with weapon specialization, kits, class restrictions
    … on".
21. DICE-LOG.md:68: "with Thieves as in AD&D off" (always on); also the link should go to
    FEATURES#thief-skills-from-adds-table.
22. PLAYER-GUIDE.md:871 vs FEATURES.md:558: K'ratchek's throws: 5/2 specialized (the guide's "2
    throws a round … AD&D's 2/1" reads as her rate). One account, the guide linking FEATURES.
23. viewer.py: the "New spells" label matches no FEATURES heading (two: New wizard spells, 6th-level
    priest spells); fix the code comment or the label.

### Lost or missing

24. The Elvenkind numbers (stealth.py:135: the cloak's hide 95 outdoors, 90 under a roof, never
    halved by light; the boots' move silently at least 95) are in no prose: add them to
    PLAYER-GUIDE#hiding-in-shadows, and point ITEMS (:187, :191) and FEATURES (:850) there.
25. docs/elvenkind.png: retake it (the boots and the cloak both show the shine before #106).
26. README Troubleshooting: the "Started without …" message (launch.py:553) and the settings file
    held by a scan or backup (__main__.py:396).
27. README commands: `py -3-64 -m dsloader …` (or note it): a 32-bit `python` installed beside the
    64-bit one can be first on PATH.
28. README Updating: a Dark Sun Recompiled unzipped into the old folder (launch.py:97-104).
29. PLAYER-GUIDE's Elsewhere in the Loader: add the game folder, Recompiled or DOSBox, speakers'
    names and which Options sections are open (remembered; not reset by Restore defaults). The
    Spells tab's choices are per session (not remembered, as the review had it).
30. DICE-LOG: a weapon's or spell arrow's spell on a hit (cast by the wielder or archer, at level 6
    or the archer's level, no attack roll); the pickpocket's two other put-away lines
    (pickpocket.py:278-284).
31. ITEMS: Alagorn's exceptions also leave out the spell arrows and Kalzith's scrolls; the icon
    colours list leaves out the Cahulaks +2 (water), Shadowseeker (night steel) and the spell arrows;
    move the glow notes in cells :61, :62, :74 there.
32. CREATURES: a line saying the mod's own people are on PEOPLE.md, in `doccreatures.py`'s intro
    (then regenerate).
33. DEVELOPMENT.md: a short section for `kurzakdoor.py` and `stuckwalk.py` (or keep the docstring
    pointer); the game-file test lists lack test_reach, test_stinkpots, test_icons,
    test_scriptfixes, test_spellgrid.
34. reports/: a status line on the five OpenDS reports.

### The change records

35. CHANGELOG Unreleased: entries for #99, #100 and #103; a number on every entry (ten have none);
    sections in the header's order (New, Changed, Fixed, Docs, Dev); each entry cut to a few lines of
    what and why (no addresses, byte counts or file inventories); drop "the user's request".
36. DEVELOPMENT.md's release steps: rename Unreleased (the PR's number and merge date) as the last
    commit before tagging, as 2.17.1 and 2.18.0 were actually done.
37. `.gitattributes`: only the manual's links go to the release's tag (the Markdown's to main); and
    `.gitattributes`/`.gitignore` ship in the zip: `export-ignore` them (or say they're harmless).

### History in references (reword; four carry a current rule, so don't just cut)

38. Cut: DEVELOPMENT-CONTENT.md:754, :978, :1330, :1363 ("…the user's report"); DEVELOPMENT-RULES.md
    :1053; RESEARCH.md:154's play account.
39. Keep the rule, drop the date or story: DEVELOPMENT-CONTENT.md:1311 (old saves keep Mikquetzl's
    bracers); DEVELOPMENT-RULES.md:1680 (the message doesn't name the level); DEVELOPMENT-SCREENS
    .md:885 ("The drawing's savings:"); ITEMS.md:79 ("an older save's Flame Blade becomes the
    Searing Blade"); ROUTE.md:180 (the warning without the date).
40. Move DEVELOPMENT-INTERNALS.md:439-447 ("The CHANGELOG's older sizes") beside entries #83-#88.

### Repetition worth fixing (most copies agree; these are the useful ones)

41. KITS restating WEAPON-SPECS' mastery and attack numbers (:61-63, :241, :302, :363): keep the
    gain, link the numbers.
42. ITEMS' spell arrow rows (:103-105): the INFO heading and plus rule once under the table, with a
    link to KITS; DEVELOPMENT-KITS.md:716-718 links :687 for ARCHER_LEVEL.
43. The README's Characters tab (:317-338): keep what the line shows, link guide#spell-slots.
44. The root README's documentation list: a few links and "the full list" in the folder README.
45. ITEMS: prices out of the Robes table (the price table has them) and :377's bracers' price.
46. FEATURES:141's link to GAME-BUGS' pointer stub: point at GAME-BUGS' top or drop it.
    (Kept as they are, on purpose: the spoiler-free guide's weapon list, FEATURES' index table.)

### Smaller

47. FEATURES: Rules links for preservers' first spells (→ guide#preserver) and psionic powers at
    creation (→ guide#psionicist); "Spells on the ground" needs Wake of the Ravager for Blade Barrier
    and Wall of Thorns (else the fire wall recoloured); "its keys (T, S, M, U and I)"; acid also takes
    a held weapon.
48. PEOPLE: shorten the elf's cell (link ITEMS for the arrows); wrap :146 and :150.
49. ITEMS: bout links (:60, :103, :180, :268) straight to PEOPLE#the-champions-bout; "Leather Helm
    +1"; the stray full stop at :190.
50. PLAYER-GUIDE: the spoiler-free promise names the champions' bout; the classes table's preserver
    weapons as the section words them; Kits takes effect "new characters, and a human's DUAL".
51. GAME-BUGS.md:86: the extra gear the mod puts on people is a feature, move that sentence to
    FEATURES (the row stays).
52. DICE-LOG.md:311: the "can't break" line's 4-space indent.
53. DEVELOPMENT.md:79: the glossary's site is `INT 98h` (`VEC_CR_SPELLS`) only.
54. CLAUDE.md: one `pgrep` form for Xvfb with the guide; the Xvfb restart command
    (`setsid nohup Xvfb :55 -screen 0 1024x768x24 &`); the broken wrap at :67.
55. PLAYTESTING.md:144: "Other sessions push to `obsidian-edition` too"; give fightout.sh an option
    (keep HP, heal each pass) so the foe-AC recipe needs no copy of it; HISTORY's date index gains the
    2026-11-18 bout lessons.
56. Code messages: dicelog.py:699-707 "restart with Start Game with Dice Log.bat" → "start the game
    from the Loader"; Show Save.bat checks for a dropped file before looking for Python.
57. Optional: "launcher"/"the helper" in source comments (10 and ~75) → the Loader / DSCLOG.
