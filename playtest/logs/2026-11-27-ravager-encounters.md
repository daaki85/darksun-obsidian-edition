# 2026-11-27: Wake of the Ravager's redrawn drakes and Tarrasque in their own fights

Codex asked for a look at the encounters the Tyr play never reaches: the three drakes (RESOURCE
11005-11007) moving and attacking on their own floors, the Tarrasque's halves (11001/11002) staying joined,
and the palette and changes of its cinematic (11012-11014). Build: obsidian-edition with PR #251 and #253
(the figures from the catalogue at e33bc2e, Tyr's furniture lowered). Folder: a copy of `$WORK/rav`
(`$WORK/ravjump`). No save written.

## The jump (`ravjump.py`)

1. **A save edited to another region doesn't do.** SAVE 18 and 45 are the region's number: changed to 0x42 the
   load drew the Cloud's tiles under Tyr's people and things (a save holds the region's map objects, SAVE 1,
   records of 25h bytes as at DS:67BBh), the party where it stood. The leader's +3/+5 there is its picture's
   corner; the place is the record's +0Ah/+0Ch (the foot), and the load put the party back where it was
   either way.
2. **The game's own move does.** The script command 5Eh is "move WHO to REGION, column, row" (GPL 4, the
   doors' shared script, runs it with its parameters; 255 as the region is Limbo). `ravjump.py REGION COL ROW`
   writes it for the party into Reyhan's talk (GPL 140 from +45, the part a talk runs) in the Loader's
   `dos/GPLDAT2.GFF`, after `ravload.sh ravager-roost`: the look pointer (two right clicks) on Reyhan
   (game 150,128), the region's picture, Space, and the party is there with the region's own creatures and
   scripts (MAS N is region N's: its area triggers, 6Ah, are x, y, w, h, an offset and the GPL script).
   ravstart.sh writes the copy afresh, so each start needs the jump again.

## What was seen

3. **Air drakes** (`ravjump.py 0x42 85 15`, the Cloud): four air drakes come at once, a fight. They walk,
   circle and swallow ("Thy'rokh is swallowed!", "... escapes!"); every frame clean, no box, the white
   bodies and teal wings whole on the clay floor. [Air drakes](img/2026-11-27-air-drakes.png)
4. **Fire drakes** (`0x3E 36 9`, Volcano 1): two, a fight at once. The long raptor walking and the one
   rearing, their attacks (damage 21, 13), clean on the black rock; the party died in three rounds.
   [Fire drakes](img/2026-11-27-fire-drakes.png)
5. **The Tarrasque** (`0x44 33 43`, then Down onto the steps: the area trigger at 31-36, 46 runs GPL 124):
   the cinematic plays (the hooded Ravager, the ground breaking, the beast rising), then a fight with the
   Tarrasque, greater elementals, skeleton warriors and a Lord Warrior. Its record has 11001 at +25 and
   430 at +27. The redraw shows facing the party (attacking: claws, 41 damage) and from the side (walking,
   swallowing): the tail half and the body half joined in every frame looked at.
   [Tarrasque](img/2026-11-27-tarrasque-redraw.png) With `RAV_SKIP=figures` the game's own Tarrasque in
   the same fight, for comparison.
6. **The Tarrasque vanishes, and it's the redraw** (the stock comparison below): on its turns the redraw is
   missing for one or two grabs about every 20 (3 of 48, 23 of 379, 7 of 323 in three runs) while it stands
   and swings, and while "X is swallowed!" shows. Its map record (object 41 here: +12h the frame drawn and
   its size, +18h the script step) puts the missing grabs on step 44 (2Ch), the first of the run 44-49.
   Neither the stock script's 04h step bit copied onto the redraw's steps nor its frames wider than stock's
   widest (154) taken out stopped it: for Codex (notes in the project's review folder).
7. **The cinematic**: its pictures and changes match the game's own frame for frame by eye, and the white
   flashes in the clouds (the lightning) come at the same points with the same pixel counts in the control.
8. **The earth drake** (RGN043, the rock object 6541 at square 85, 13): after `ravjump.py 0x43 87 10` (the
   square GPL 16's own move uses) the view stays where the Roost's was. Writing the camera (DS:1408h) to the
   leader's foot less (152, 88) and opening and closing USE (the top-left icon, game 24,20, then Escape)
   redraws it there. The look on the rock then runs GPL 16: "the large rock begins to move!" and the redrawn
   earth drake (picture 11007, object -541) rises and stands, clean; the look on it shows Earth Drake, level 25.
   **Its fight didn't start**: a sword click on it, or H, sends the view to (752, 288) and the game stops
   answering. After a jump the other members stay at (2112, 1632), off the map, and the game's place for the
   party isn't the leader's (a save and load there keep it). Tried without luck: actions 52 and 37 round the
   move (as GPL 16's own), a call into GPL 16's rising (695), keys 3, 5 and H, the members written beside the
   leader. A jump straight into a fight (the Cloud, Volcano 1, the Tarrasque) is fine.

## The stock game beside the redraw

9. The same jumps with `RAV_SKIP=figures`. [Stock and redraw](img/2026-11-27-ravager-stock-vs-redraw.png):
    - **Air drakes**: the same size; the stock drakes pile onto the swallowed man just the same, so monsters
      overlapping each other is the game's own.
    - **Fire drakes**: the stock one is a big orange dragon standing over a man; the redraw is a small raptor
      about a man's height. For Codex.
    - **Tarrasque**: the stock one was drawn in all 77 grabs of its turns (no vanish). Its side view stands
      higher, head forward; the redraw's side view is lower, so the damage number of a hit shows on its
      chest (the user saw it). The redraw's script has other offsets (steps' bytes 5 and 6) and none of the
      stock's 04h bits. For Codex. Stock elementals stand on the Tarrasque as ours do.

## Also seen

10. **The screen's lightning patches** in the Tarrasque's region (rectangles of the sky drawn over the
   floor as the view redraws) are in the game without the figures too.

## Codex's fixes re-imported (catalogue 865a5e4, evening)

11. **Re-packed** from the installation files at 865a5e4 (squash, `import_catalogue.py`, `ravfigures pack`):
    only the Tarrasque's halves (BMP, CBMP, SCMD 11001/11002) and the fire drake (11006) changed. The
    Tarrasque's attack run (steps 38-49) now uses the stock script's frames and flags (43: base frame 9;
    44-49: combat 3, 3, 4, 4, 5, 5), with offsets within a few pixels of stock's.
12. **The walk** (`ravjump.py 0x44 33 43`, Down x7, the cinematic, then its turns read live): the side walk
    steps through its three poses square by square (script steps 0Ch, 0Dh, 0Eh in turn, a dozen strides),
    and the toward walk through its six. [The walk](img/2026-11-27-tarrasque-walk-fixed.png) No vanish in
    about 500 grabs of its turns over four runs.
13. **The swing** (a fifth run): in four runs the elementals and skeletons crowded round the party at the foot
    of the steps and the Tarrasque stood (step 0Fh) every turn. With the party written beside it at the
    fight's start (map records 0-3 at foot 1464-1480, 456-472, right of its 1416, 456; a test-only edit,
    never saved) it attacked from the side every turn: 22 swings, the side attack run (script steps 38-43,
    the record's +18h 27h-2Bh, then 08h), three hits and swallows ("Ar'anda is swallowed!"). In 762 grabs of
    its turns it was never missing, the swallow included. [Swallow](img/2026-11-27-tarrasque-swallow.png)
    The damage numbers show where the one hit stands: at its claws for a member in front of it (21), on its
    flank for members the edit had put inside its outline (29, 28). [Side hits](img/2026-11-27-tarrasque-side-hits.png)
    Step 44 (the attack run 44-49, the other facing) didn't come up from this side.
14. **The fire drake** (`0x3E 36 9`) is now the stock dragon's height over the party.
    [Fire drakes](img/2026-11-27-fire-drake-resized.png) Once, grey-blue rock with magenta edges showed
    on the cave floor left of the party; not in the next run of the same build, nor in the stock control.
