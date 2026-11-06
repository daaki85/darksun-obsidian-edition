# 2026-11-06: memory audit (the game's side measured in DOSBox; the Loader's read and measured)

Build: `obsidian-edition` at the review's fixes (DSCLOG 65,504-byte image, 32 bytes spare). Save
`pens-after-scar`. Tools: `memaudit.py` (every DOS block), `memsample.py` (one line: heap and DOS
memory free), `dacwatch.py` (DSCLOG's palette copy over time).

## The game's side, measured

**Conventional memory, on the map (map flag 1):** the game's block (DSUNLOG) 548,864 bytes; its
heap 206,496 bytes, no free block in it; DOS memory free after it 100,016 bytes (largest piece
99,008). The map's view needs 60,000 in one piece: 39 KB to spare. (DEVELOPMENT.md says 97 KB:
right.)

**Upper memory (chain from 9FFFh):** DOSBox's system block to C900h; 9 paragraphs free; DSCLOG
64,000 bytes; the overlay buffer 32,992; **free 36,336** (DEVELOPMENT.md: about 35.6 KB, right);
the see-through tables 14,160 (885 paragraphs); the music buffer 12,016. `UMB_NEED` 6,190
paragraphs (DEVELOPMENT.md said 6,186: put right). HMA: DSCLOG's far block there (FAR_SEG FFFFh).

**Over a session** (free DOS memory after each, on the map):

| After | Free (bytes) |
|---|---|
| the load | 100,016 |
| inventory opened and closed, three times | 100,016 each time (131,760 while open) |
| USE screen, twice; Effects screen | 100,016 each time (137,904 while open) |
| walking to the fire room | 100,016 |
| five rests, Kurzak's call, the alarm fight begun | 100,032 |
| the fight fought out (fightout.sh) | 100,016 |

Nothing lost: every screen gives its memory back, and a fight and rests leave it as it was. An
area change (pens to arena and back) wasn't measured: the arena gate asks nothing before Kurzak's
call (stepping on and off the gap at 1816,440 did nothing, 2026-11-06).

## The Loader's side

- The `dicelog` process: 45 MB resident after 6 minutes and after 8 (steady). The README's
  "about 100 MB" is with the window.
- **`ghost.Ghosts._made` grows all session:** keyed on DSCLOG's whole palette copy, which changes
  every 30 s where the game cycles colours (`dacwatch.py` in the fire room: 4 different palettes
  in 75 s; colours 16-223 the same throughout). Each new one is about 13 KB more (up to about
  1.5 MB an hour), and a 0.2 s rebuild in a thread **with GHOST_ON 0 meanwhile: a hidden thief or
  an invisible figure can be drawn solid for that moment every 30 s.**
- The sprite dresser keeps whole game files for the session (about 16 MB, made once).
- Error lines in the viewer and `play` mode are told apart by their text: one with an address in
  it would be a new line each pass (play.log could grow fast).
- Everything else is bounded (the log panes 3,000 lines, the panel 200, the dialogue drained).
