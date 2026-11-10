# 2026-11-10: memory pass 3, Emberlash and Ironwhirl, the retaken Loader pictures

The build under test is commit 78533d2 (DSCLOG.EXE 68,032 bytes). No game was saved.

## Memory pass 3 (`fountain-user`)

What moved:
- the AD&D XP, slot, thief and DEX tables, and the kits' names, into the tail;
- SEG_MOVE's two tables of the game's into the tail;
- the helper's zero buffers (the Look box, the USE screen's slot lines, the item box line, NS_SCRATCH, SHADOW_TAB, the Effects name) laid over the install code.

Results:
- **`buildcheck.py`:** OK once its tail check skips SEG_MOVE's tables (between the names and the kits' names), which the game fills as it runs. The tool now compares `extra_types`, `extra_names` up to `seg_space`, and `kit_names` to the tail's end.
- **`memaudit.py`:** the helper's block is 68,256 bytes with its PSP and tail (4,266 paragraphs), and the overlay buffer follows it at once.
- **SEG_MOVE:** `seg_moved` (header +306) is 1, with `tail_seg` D85Ch.
- **Effects screen:** Lex shows "KIT: SPELLARCH" (a short name) and Jenna "KIT: STALKER" (a long one), both read from the tail (`img/2026-11-10-kit-names-from-tail.png`).
- **View Character** (the inventory's first bottom icon, 168,187):
  - Lex "EXP:4677 (5000 Pr)", the preserver's AD&D 3rd level;
  - Seneca "EXP:3577 (4000 F)".
- **Seneca's inventory panel:** PICK 73, LOCK 69, TRAP 52, SLNT 77, HIDE 67, CLMB 75 (the thief and DEX tables).

## Emberlash and Ironwhirl
Set up in memory (`/tmp/playtest/magic.py ITEM OBJECT TYPE NAME PLUS`, with the inventory closed and +0Ch cleared): Lex's right-hand item 43 made each in turn.

Right-click boxes (`img/2026-11-10-emberlash-ironwhirl-boxes.png`):
- **Emberlash** (object 2676, type 147, name 0x171, +1): "2 handed Obsidian +1 Emberlash / 1D6+1".
- **Ironwhirl** (object 2678, type 146, name 0x172, +2): "2 handed Metal +2 Ironwhirl / 1D6+2".

Both pictures are drawn as the box's small copies and fit, and the two new names read right.

Not seen in play (regions this save can't reach; the data tests cover them):
- Uzoma carrying Emberlash;
- the Subterranean Temple's rack with Ironwhirl;
- the two shops' new cahulaks.

## The Loader's pictures, retaken
- **The opening:** a new game from `start.sh`, its text dice log stopped, the window (`python3.12 -m dsloader view`, Xvfb :57, 1320x780) attached before START GAME, and the opening played by hand.
- **`docs/dicelog.png` and `docs/dialogue.png`:** K'ratchek's features read "Open sky spells and psionics" alone, and the Help button shows.
- **The status line** showed "Save copied: Page 1 slot 01 - ..." (the named-saves sync of the scratch game folder) in place of "Connected".
- **`docs/hit-line-box.png`:** Gerakis's right hand made a Stone Dagger (type 33). Its box reads "Stone Dagger / 1D4-1/1D3-1 / Hit -2", cropped 116x76+70+57 and scaled 200%. It no longer repeats `large-dice.png`'s long sword.
