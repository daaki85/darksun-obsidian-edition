# Documentation review, second pass (2026-11-18)

*Status: acted on (#113, from its verified version). Findings only, nothing changed at the time. A second full review after the restructure (pull
requests #97-#105) and the item and bout changes (#106-#108, and the unmerged spell arrows' INFO
heading). Read against `claude/spell-arrows-note` at `a4f5768`; line numbers are at that commit.
The first review is on `claude/docs-review`; the code audit is
[code-memory-audit.md](code-memory-audit.md).*

## The short version

The restructure held. Every link and anchor resolves across all pages; FEATURES follows the
Options tab label for label; the Options table, every kit number, the attack and slot tables, the
champions' gear and all 189 creature rows match the code; all 118 modules are in the module map;
TOOLS.md, the logs index and the manual are current; no public download links. What came back:

1. **A handful of things that are wrong** against the code (below), the most important being the
   multiclass rule for using items.
2. **One fact lost in the move**: the Cloak and Boots of Elvenkind's numbers.
3. **The change records drifting again**: three pull requests missing, new entries long and
   technical, "the user's request" back.
4. **Dated history creeping back** into references (about 15 places).
5. **Some repetition** between pages that should link.

## 1. Wrong against the code

| Where | What it says | What's true | Fix |
|---|---|---|---|
| PLAYER-GUIDE.md:329, 1788 | a character of several classes uses only what every class allows | the game's own class lists count if **any** class allows (`restrict.usable`: the class mask is any-of); only the mod's limits (spheres, psionicists' weapons, armour) take the strictest. A fire cleric/fighter can wield the Terror Blade; a water cleric/fighter Swiftbite, Draketooth and Hornblade; a fighter/psionicist Greenbright, Shadowseeker, the maces and slings | say it as it is; fix the Magic weapons by class table's notes (they're right for single-class clerics only) |
| PLAYER-GUIDE.md:1786-1816; ITEMS.md:52-83, 241 | "a fire or earth cleric can wield it" and the class table | true only with **Class restrictions** on; with it off a water cleric can wield the Searing Blade, Mindshard, Nightsliver, Glasshewer, Emberlash | one line each: "with Class restrictions" |
| PLAYER-GUIDE.md:1805-1816 | the class table | leaves out the multiclass kits (the Battle Dancer: long swords and bows, any sphere) and the psionicist with a warrior or thief class | add them |
| obsidian-edition/README.md:105 | a non-GOG DSUN.EXE starts "without the dice log" | it starts the **original game**, none of the mod | correct it |
| obsidian-edition/README.md:31 | patch-notes.html "also in the release's folder" | the zip's copy is `manual/changes.html`; patch-notes.html is beside the zip on the Releases page | correct it |
| obsidian-edition/README.md:112-118 | on Linux the dice log follows a DOSBox you start yourself | it needs DSCLOG and the patched game, which only `launch` prepares | say only the party view works, or how |
| README.md:15 (root) | "a 64-bit Python, which the Loader offers to install" | the `.bat` files offer it | correct it |
| PATCH-NOTES.md:136 | nineteen magic icons shimmer | twenty (Tanelyv's chest) | twenty |
| PATCH-NOTES.md:110 | the Fine Bow among "other magic" | it's not magic | move it |
| PATCH-NOTES.md:188; GAME-BUGS.md:87 | random monsters could crash the game ("Divide error") | the shipped data has no zero divisor (reports/opends-bug-comparison-2026-11-18.md) | drop the crash clause, or show it |
| PATCH-NOTES.md:207 | "Out of memory in OEOpenGraph" a game bug | the 2026-11-18 report calls it the mod's (more memory used) | move it out of Bug Fixes, or confirm the original game fails too |
| DEVELOPMENT-CONTENT.md:1342 | the defiler champion's scroll is one of the game's spells | it's Fogbolt, Spook or Reflected Image with the new spells on, else a game spell | correct it |
| DEVELOPMENT-INTERNALS.md:222 | DSCLOG kept: 70,624 bytes, 69.0 KB; 29,616 free | 70,736 bytes (4,421 paragraphs), 69.1 KB; ~29,520 free | correct, or say which build |
| DEVELOPMENT-CONTENT.md:588-610 | the last record ends at 3E5E0h; "room for 199-201" | records 196-211 fill the room exactly and NPP's 212 lies past it (the audit's bug 1.1); the room is for 196-211 | correct with the fix |
| DEVELOPMENT.md:121, 155-160 | the manual has ten pages | twelve (WEAPON-SPECS, PEOPLE); the folders table lacks them too | update |
| DEVELOPMENT-KITS.md:703 | strays put away only with no Spellarcher | also when the Spellarcher's pack is full; the sentence is garbled | rewrite |
| WEAPON-SPECS.md:33 | "the Flame Blade a long sword" | reads as the old item: it means the spell's blade | "the Flame Blade spell's blade" |
| KITS.md:439 | Military Scout: +1 with a bow or sling | the staff sling too (`kits.SCOUT_MISSILE_KINDS`) | add it |
| GAME-BUGS.md:119 | "AC 1 better a 5 gladiator levels" | "for each 5" | typo |
| `.claude/hooks/session-start.sh:14` | flags `claude/class-outfits-2` as a handed random name | CLAUDE.md's own `-2` suffix is a proper name | require a 6-character last part with a digit |
| `playtest/RESEARCH.md:58` | making a Spellarcher in memory: race, classes, kit | also the class mask (+12h, the fighter's bit), or the game bars the arrows | add the step (PLAYTESTING.md:581 has it: keep one) |
| `playtest/setitem.py:7` | names logs/2026-11-17-item-glows.md | it's 2026-11-18 | correct |

## 2. Lost or missing

- **The Elvenkind numbers** (the cloak's hide 95 outdoors, 90 under a roof, not halved by light;
  the boots' move silently 95) are in no prose now, and ITEMS and FEATURES link to each other for
  them. Put them in PLAYER-GUIDE#hiding-in-shadows and point both there.
- **`docs/elvenkind.png`** shows the boots' old blue shine (now green): retake it.
- **Named saves** are copied only while the Loader's window is open (*Play Dark Sun* keeps none):
  say so in the README and the guide.
- **The README's troubleshooting**: the "Started without …" and settings.json-unreadable messages;
  the commands should suggest `py -3-64 -m dsloader` (a Python installed by the `.bat` isn't on
  PATH); Updating should mention a Dark Sun Recompiled unzipped into the folder.
- **"Elsewhere in the Loader"**: the game folder, Recompiled or DOSBox, speakers' names, the Spells
  tab's choices are remembered and not reset by Restore defaults.
- **DICE-LOG**: a weapon's or spell arrow's spell cast on a hit (the archer named as caster), and
  two of the pickpocket's put-away lines.
- **ITEMS**: Alagorn's exceptions leave out the spell arrows; the icon colours list leaves out the
  Cahulaks +2 and Shadowseeker.
- **CREATURES**: a line saying the mod's own people (Kalzith, the champions) are on PEOPLE.md.
- **DEVELOPMENT.md**: `kurzakdoor.py` and `stuckwalk.py` have no section; the game-file test lists
  leave out five tests.
- **Reports**: the five OpenDS reports have no status line.
- **Tests**: nothing checks every player page has a manual page; CHANGELOG-archive.md isn't
  link-checked or in the tests workflow's paths.

## 3. The change records

- **CHANGELOG Unreleased** lacks #99, #100 and #103; six entries have no number (#102, #104-#108);
  its section order differs from the header's.
- The newest entries break the header's rule: addresses and byte counts, 600-character lines,
  file-move inventories (#102, #104, #105), and **"The user's request."** at the end of three.
  Cut each to two lines of what and why.
- DEVELOPMENT.md's release steps tag before renaming Unreleased; the 2.18.0 tag shows the rename
  is done first. Swap the steps.
- `.gitattributes` says the player pages link the developer pages at the release's tag: only the
  manual's links are; the Markdown's go to `main`. `.gitattributes` and `.gitignore` ship in the zip.

## 4. History back in references

Cut to the current rule (the history is in the CHANGELOG, its archive and HISTORY.md):
DEVELOPMENT-CONTENT.md:746, 970, 1303, 1322, 1355 ("…the user's report"); DEVELOPMENT-RULES.md:1019,
1639 ("the user's rule, 2026-11-11"); DEVELOPMENT-SCREENS.md:885; DEVELOPMENT-INTERNALS.md:422-432
(the changelog's old sizes: move beside those entries); ITEMS.md:79 (the Searing Blade's 2.18.0
note); RESEARCH.md:153, ROUTE.md:180, 212 (dated play accounts); dsclog.asm:19723 (the stale
"three wizard spells … 96 bytes").

## 5. Repetition that should be a link

- The documentation list in both READMEs, nearly word for word.
- Magic weapons by weapon spec in PLAYER-GUIDE and ITEMS.
- Spell slots and the DEX AC table in the README's Characters tab and the guide.
- The game window, readable layout and defaults in the README and the guide's tables.
- The spell arrows' rules in ITEMS (three times the INFO heading) and KITS; ARCHER_LEVEL three
  times across the developer pages.
- KITS restating WEAPON-SPECS' mastery and attack numbers, despite saying they're there.
- The robes three times on ITEMS; the bone scale pieces, Grey's Scale and the bracers' price twice.
- The game's own party in FEATURES and the guide (and they word K'ratchek's throws differently).
- FEATURES' "Rules the game got wrong" table repeats each entry; GAME-BUGS and FEATURES link to
  each other in a circle for those rules.

## 6. Smaller

- FEATURES: two Rules links land in the wrong section (psionic powers at creation, preservers'
  first spells); three headings don't match their Options labels as the code's comment says they
  should (the spell save, the CHA at shops, thief skills); "Spells on the ground" contradicts the
  Wake of the Ravager entry on what needs WotR; "three keys" (five); acid also takes the held
  weapon; at 1,279 lines it's still long (the combat log, THAC0 panel and Effects formulae could
  move to the guide).
- PEOPLE: the elf's cell has grown into a paragraph; the paragraph after the table is two
  unwrapped 400-character lines.
- ITEMS: glow notes in three Bonus cells (the rest are in Icons and names); links to the bout go to
  FEATURES' stub, not PEOPLE; "Leather helm +1" lower-case; a stray full stop.
- PLAYER-GUIDE: the spoiler-free promise should name the champions' bout; the classes table and the
  Preserver section name the preserver's weapons differently; Kits' "takes effect" should add DUAL.
- GAME-BUGS: two rows are features, not bugs (the people's worn gear; Legcrusher's scene).
- DICE-LOG: one link to the wrong FEATURES anchor; one line's indent.
- DEVELOPMENT.md: the glossary's "site" is only VEC_CR_SPELLS; source comments still say "helper"
  and "launcher" (22 and 14 times); two module-map links are weak.
- CLAUDE.md: `pgrep -x Xvfb` against the guide's `-a`; the Xvfb restart command; a broken wrap.
- PLAYTESTING.md: "Other sessions push to this branch" is stale; the foe-AC recipe needs a
  throwaway copy of fightout.sh (give it an option); HISTORY's date index misses the 2026-11-18
  bout lessons; six pictures in logs/img are unreferenced.
- Code messages: the dice log tells players to restart with "Start Game with Dice Log.bat" while
  the READMEs make Start Obsidian Edition the main way; Show Save.bat finds Python before saying
  to drag a save onto it.

## Suggested next step

One pull request for sections 1-6, after merging the spell arrows' INFO heading
(`claude/spell-arrows-note`, which several of these touch). Section 1's multiclass rule is the one
to settle first: whether the docs should describe the code (any class's list counts), or whether
the code should change to every class's.
