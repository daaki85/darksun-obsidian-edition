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
6. **One thing for Codex**: in one grab of the redraw's attack (of 91 taken on its turns, and once in an
   earlier run) the Tarrasque isn't drawn at all for a moment between two swings; and while "Ar'anda is
   swallowed!" shows it is gone for about 20 grabs. Not yet checked whether the game's own Tarrasque does
   the same (its frames and script steps all decode, none empty).
7. **The cinematic**: its pictures and changes match the game's own frame for frame by eye, and the white
   flashes in the clouds (the lightning) come at the same points with the same pixel counts in the control.
8. **Not reached**: the earth drake (object 6541, RGN043 square 85, 13, a talk or look runs GPL 16): the
   jump to 0x43 leaves the camera on another part of the map (the region's opening keeps it), and the
   walk there needs the camera put by hand.

## Also seen

9. **The screen's lightning patches** in the Tarrasque's region (rectangles of the sky drawn over the
   floor as the view redraws) are in the game without the figures too.
