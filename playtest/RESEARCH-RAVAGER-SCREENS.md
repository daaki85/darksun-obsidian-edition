# Research recipes: Wake of the Ravager's pictures, screens, fights and items

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The sequel's picture cache, figures, shadows and shine, what's on screen where, its fights and spells,
its screens, item boxes, item types and weapons, its map and its combat log's panel. Setting up and
driving the sequel: [RESEARCH-RAVAGER.md](RESEARCH-RAVAGER.md).

**Its picture cache** (2026-11-20): the loader at 2A568h (SL's 25FA6h) keeps SL's 300 slots, 16 bytes each
(number, length, store place, memory, flags), the count at DS:265Dh, the table at load + 42A2h:0CA8h;
253 taken at the start of Tyr (`cache.py`-style dump: the count, then each slot). Its one caller is the
map things' routine (2A388h: DS:67BBh, 25h bytes a thing, up to 141h, the slot at +10h); the walls don't
come through it. `ravsites.py [NAME...]` finds SL's patch sites in the sequel by likeness (about 8 minutes
for all 454; its finds are leads to read by hand).

**Shattered Lands' figures in the sequel** (2026-11-20, logs/2026-11-20-ravager-sl-figures.md):
`darksun-recompiled/tools/sl_figures.py build SL_DIR WR_DIR OUT.GFF` writes the sequel's `OBJEX.GFF`
with the party's 14 figures taken from SL (the walking `BMP n`, the combat `CBMP n`, the script `SCMD
n`; the study is that repository's `docs/FIGURES.md`). To play it, **copy the install for real**
(`cp -a $WORK/rav $WORK/ravsl`, 287 MB): with hard links the game's writes (DARKRUN.GFF, saves)
would change the original too. Put the built file in the copy and `sh ravstart.sh $WORK/ravsl`.
Seen working: standing, walking, the swing, hits and deaths, the anchors right. **`sh ravburst.sh
NAME SECONDS X Y W H`** grabs the window as fast as `import` goes (about 15 a second) while an action
plays, and makes a sheet of 24 of them cropped to X Y W H (window pixels); look at single grabs
(`$WORK/burst/NAME-NNN.png`) round a moment at full rate. For a death on cue, set members' HP to 1
(the creature records at DS:19C9h, +0; `ravcreatures.py` lists them): a test edit, never saved.
SL's standing side frame has the legs apart: it isn't a walk frame left on screen.
**The dressed people** (`people_dress.py build`, 2026-11-21, logs/2026-11-21-ravager-dressed-people.md) are
quickest seen at the start: the blonde woman of the opening talk is picture 2426, and answer 3 brings
the Draxans' ambush, whose two Draxans are 2428 (walking, then fighting round the party). Which
regions hold which pictures: each RGN's ETAB objects (negated) through OBJEX's OJFF (+PIC).
To see a figure that stands elsewhere, build a test OBJEX with its dress put in a slot the opening
shows (dress['2428'] = dress[N]): writing the camera (DS:1408h) in a fight doesn't redraw and snaps
back, and HP 0 on the Draxans doesn't end the fight.
A **restyled creature** goes in the same way, its own chunks written over the slot's (BMP, CBMP
and SCMD of 2428 or 2426 replaced by the creature's from `restyle.py`/`loosen.py`'s `build(pic)`, then
`write_ranged` on the built OBJEX): the creature then walks the Draxans' route and fights, its own
script driving it (2026-11-22, logs/2026-11-22-restyled-creatures.md). Tyr's street is grey: a grey
creature (the soulshard) is hard to see there.
`sl_figures.py build-ui` does the same for the interface (`RESOURCE.GFF`: pictures and icons; put it
in the copy beside the patched OBJEX.GFF). Its screens in a fight: **Q** the END menu (Escape closes
it); a click on the status box (window 560,50) captures the mouse harmlessly; USE at game 22,17;
VIEW INVENTORY 74,171 on USE (47,171 opened the inventory too, not the character sheet); Escape in
the inventory closes it and USE together. The game writes its run files (DARKRUN.GFF and the like)
into the folder it runs from, so copy `__support/save`'s three files back into the copy between
runs for the same start.
`sl_figures.py regrade SL_DIR WR_DIR RGN032 STRENGTH OUT.GFF` regrades a region (Tyr is RGN032,
the opening street); put it in the copy as `RGN032.GFF`. **The sequel cycles palette entries 16-23 at
run time** (torches, fire): a colour put there shows in the game's glow colours, not the file's.
To check a colour on screen, sample the grab's pixels and match them to the region's PAL (in its
`RGNxxx.GFF`). Shattered Lands draws region N in `GPLDATA.GFF`'s PAL N (the pens, RGN29, in PAL 41).
**What's on screen where:** the camera is DS:1408h (x, y), in map pixels; the screen shows map
pixels minus the camera. The ground: **`MAP ` (or `RMAP`) is 98 rows of 128 tile numbers** (not 112 x
112), tile (c, r) at map pixel (16c, 16r); `GMAP`, the same shape, holds per-cell flags. A region's
entities (its `ETAB`, 8 bytes each: x, y, height, flags, the object negated) stand at map pixel (x, y). An object's record (`OJFF`) anchors its picture by +2 (x) and +4 (y):
the bottom centre. `sl_figures.py squash` lowers a region's structures for SL's angle.
**An exact frame from a grab:** the sequel's 320x200 frame shows in DOSBox's 640x480 window with every
pixel doubled across and rows repeated 2 or 3 times (2, 2, 3, 2, 3...), no blending: the first row of
each repeat, every other pixel, is the frame exactly, and each pixel matches a palette colour shown as
v x 4 + v / 16 (`darksun-recompiled/tools/proto/frame.py`). Sampling rows at (r + 0.5) x 2.4 instead
picks the wrong row now and then, enough to spoil tile matching. The frame isn't in guest memory as a
320x200 buffer.

**Wall shadows at run time** (2026-11-20, logs/2026-11-20-ravager-shadows.md): DSCLOG2's WALL SHADOWS
darkens the floor right of and below each wall cell (GMAP C0h, DS:0538h far, 128 a row) as the game
draws it, as DSCLOG's SHADOWS does SL's figures': site 40 at 2B81Ch (the view's floor: page, camera x,
y) and site 41 at 2B97Fh (a rectangle's: page, x0, y0, x1 + 1, y1, camera x, y), their way back made
FLOOR_POST; the page table (SL's layout) in segment load + 0BF3h, FLOOR_ON DS:29EAh, DGROUP 47E0h.
Retuned to SL's own shadows (the owner: the first try "didn't look as good"): each wall square swept
45 degrees by a full cell, so an open cell with a wall NW is all dark, W only x <= y, N only x > y;
the walk map pads each wall a cell into the room (drawn as floor), so a wall-marked cell is darkened
only when wholly in shadow. DARK was SL's tone (Lab L x 0.73, a + 11, b x 0.82), which read maroon on the sequel's grey cobbles;
the owner chose a neutral one: lightness x 0.73, a and b kept (x 0.74 a channel in 6-bit values), the
nearest of colours 32-255 (240-255 are the sequel's only greys, its ramp), made from the DAC when
the palette changes (once a second at most, not in a fade). The sequel cycles colours 1-31 (blues,
magentas, greens, flame, water, the turn marker's flash): they map to themselves and stay out of the
change check, else DARK is made again every second. `ravtone.py warm|neutral [FLAG]` swaps the tone
in guest memory (a test edit: WS_GAIN at header + 5F8Bh, WS_DAC_SUM at + 5FD1h in the 2026-11-22 build:
check the listing) for a same-view comparison. Same-view toggle: write the
header's +1872, press C then Escape (the left half redrawn). The header (signature `DSCLOGR1`) has
wall_shadows at +1872, the passes drawn at +1874, DARK's builds at +1876 (DSCLOG2's own, past DSCLOG's
header; +148 to +152 were theirs before the port's fields took them): find it in guest memory to check it ran. `RAV_LOADER=1 sh ravstart.sh FOLDER`
loads it; rebuild with `nasm -f bin -o dos/DSCLOG2.EXE dos/dsclog2.asm`.

**The figures' shadows at run time** (2026-11-26, logs/2026-11-26-ravager-figure-shadows.md): DSCLOG2's FIGURE
SHADOWS draws in the walls' floor pass. **The sequel lets a picture go from memory whenever it wants room**: a picture
cache slot (load + 42A2h:0CA8h + 16 x slot) has +0 the number, +2 the length, +6 its place in the store (XMS), +0Ah
its memory (far) and +0Eh bit 2 "in memory", which the freeing loop (2AB90h on, each through 2AD2Ah) clears; the thing
drawer (2A28Fh, SL's 25E0Ch: SI the slot, DI the thing) loads it again through 2A1F7h and draws it through `call far
1D40:3BEC` (2A347h). So a floor drawing mostly finds a figure's picture out (Tyr's street: the leader's at nearly
every one): read a picture only at the drawer's call (FIG_KEEP, site 162). The draw list's entries are SL's (8 bytes;
flag 10h not drawn, 20h placed by the entry: x less the map thing's byte +7, y less its **word** +8 and the height;
else the map thing's +3, +5); the map thing's picture slot +10h, frame +12h. Out of a fight only the leader is on the
map. `ravfig.py [0|1]` reads (or switches) the header's +1960 to +1971; a same-view toggle through VIEW_REDRAW lands a
frame late and the street's walkers move, so make the control a RAV_SKIP run (`fig_wide_all,fig_wide,fig_keep`) and
the same walk (`ravgo.py x 1180` from `ravager-after-ambush`). A throwaway copy of the sequel needs no 200 MB
`game.gog` of its own: link it to the plain install's (DOSBox only reads it).

**A shadow's feet** (2026-11-27, logs/2026-11-27-ravager-shadow-feet.md): the sequel draws a figure from its frame's
top left (the draw list's place less the map thing's +7 and +8), so a frame with clear rows under the feet (Codex's
redraws have a margin all round: 10 rows under Ar'Anda's 599, up to 22 under the big creatures') stands right but
cast its shadow that far below. FEET_ROW (both helpers) takes the frame's last listed row as the feet. To see which
picture and frame a party member is drawn with, the log's probe reads the draw list and the cache.

**Planar figures and big ones** (2026-11-28, logs/2026-11-28-ravager-shadows-review.md): the drakes (RESOURCE 11005-11007)
and the Tarrasque (11001, 11002) are planar pictures (FFh "PLNR"), drawn through the same call as the others (FIG_KEEP
sees them); DSCLOG2 now unpacks such a frame there to keep its shadow. `ravfig.py`'s "none for want of one" counts
a planar figure never drawn yet. The Tarrasque is two map things: the back half (thing 41, 11001), the creature, and the
front half with the claws (thing 252, 11002), kind 0 in the things table; a map thing's +21h names its part, +23h the
thing it is part of (FFFFh none). To see what the Loader adds to a view, switch the header's +1872 (walls) and +1960
(figures) off and on and press U then Escape (logs/files/2026-11-28-ravager-shadows-onoff.sh).

**Dust, and the figures' shadows in a fight** (2026-11-26, logs/2026-11-26-ravager-dust.md): **Tyr's ground is
darker than SL's sand**: the dirt of the squares and yards (Shadow Square, world ~600, 1226 on, west of the ambush
street by y 1230) is colours 230, 95, 229, 228 (56,44,28 to 113,105,77 of 255), below `dust.is_ground`'s least value
0.4, and the grey cobbles have no hue: with SL's table no floor in Tyr took dust (the puffs were raised and counted,
none seen). The sequel's table (least 0.2, a step of 0.2 toward white, `ravlog.DUST_LEAST`, `DUST_LIGHTER`) takes the
dirt one or two up its ramp; 0.45 gave near-white trails. The house floors (the same browns) take it too. **The squares'
LIGHT read the palette from the wrong place** before (squares.py read LIGHT's and DAC's offsets as one pair at +1926,
SL's +236/+238 side by side; the sequel's +1928 is `square_draws`), so LIGHT was made from whatever lay at that
counter's value. **In a full fight** (the Draxans' ambush under Computer Control, four of the party and four foes,
then the bodies): 2,753 shadows cast in 586 floor passes, 1,556 of them from kept frames, 79 frames kept over the
fight (the 64 slots went round once), 2 cast from another frame of the picture and 2 none for want of one (both
before the fight, as the first frames came): 64 slots are enough for that. On the dark floors (the street's grey,
the houses' brown) the shadow is a faint darker streak, as SL's on dark ground. `ravfig.py` reads both features'
counters; find a dirt square with the area map (the game menu's maze icon, game 184,100: the brown ground west of the
grey streets). DSCLOG2 with dust: 55,072 bytes, 54,544 of upper memory, 100,912 left (its largest piece).

**Comparing two dice logs on the sequel** (2026-11-27, the pass as named steps): a second `ravdice.py` on
the same running game says nothing of the stock, the own party or the ages, which the first wrote into the
game (once a game). To compare two builds of the Loader, start the game afresh from the save for each
(`ravload.sh`, then `ravdice.py --all 25 OUT`): only the age rolls differ between runs.

**DSCLOG2's upper memory, measured for the audit's R3** (2026-11-27, claude/combined-playtest at 9c8dc0b3,
`ravload.sh ravager-after-ambush` with and without `RAV_SOUND=1`, the same both ways; the chain walked from 9FFFh):
upper memory is CA00h-EFFFh, 9,718 paragraphs past the first 9-paragraph scrap. DSCLOG2's block at CA0Ah is 4,151
paragraphs (66,416 bytes, with its PSP), the see-through figures' block at EE9Fh 352 (5,632 bytes), and **5,212
paragraphs (83,392 bytes) are free between them**. The game itself puts nothing in upper memory (no overlay or music
buffer there, unlike SL's), so DSCLOG2's limit is the 9,718 paragraphs less its own two blocks and their MCBs.

**The magic items' shine in the sequel** (2026-11-26, logs/2026-11-26-ravager-shine.md): the sequel cycles colours
1-31 in five runs (1-5 blue, 6-10 pink and violet, 11-15 green, 16-23 fire, 24-31 the water's blue-greys) with SL's
cycler (2CFDCh, 2796h:047Ch), called only from the map's loop (1CF0Eh, when byte DS:1424h is set; the main loop
clears it), so **a shop's screen stood still**, as SL's did. The shop's loop (88D52h, while byte [143Dh] is 1) and the
game's wait (its "or di,di / jz" at 2F7BEh, the jump to 2F777h) are SL's (7DDE4h, 2AFA6h). To check an icon shines,
burst-grab it (`ravburst.sh`) and count the frames its box changes in. A survey of OBJEX.GFF's magic items: an item
record (+0 its picture negated, +10h a power, +16h the plus, +14h its name, `ravitems.sequel_names`) in any RDFF,
its object's icon decoded with `sequelicons.decode` (PLNR, PLAN or SL's runs); most magic weapons have 2-8 cycled
pixels, twelve items none or one or two (`dsloader/ravshine.py`). A picture of Shattered Lands' kind put in the
copy of OBJEX.GFF for one of the sequel's own icons is drawn as its own.

**See-through figures in the sequel** (2026-11-26, logs/2026-11-26-ravager-see-through.md): `ghost_draws` (DSCLOG2's
header +1994) counts the figures drawn see-through, `ghost_on` (+1986) is 1 once the Loader has written the tables,
`ghost_seg` (+1984) the upper memory block; the STEALTH word (+204) has a bit for each party member hidden. To see
one without waiting for a thief's lucky roll, a **test edit** of STEALTH to 1 (member 0) out of a fight draws the
leader see-through at the next redraw (a step: the map isn't drawn again while nothing moves, so a write alone
changes nothing on the screen); write it back to 0 and never save. In the Draxans' ambush under Computer Control
Ar'Anda tries to hide each turn (`hides in shadows` in the dice log), but in daylight her chance is halved
(36%): one hide in the fight. **The
leader** (DS:426Dh, whose turn) is the same after every load of a save (Thy'rokh, 2, in ravager-after-ambush:
three loads); the number keys 1-4 on the map make member 0-3 the leader, so a talk's answer keys that land
on the map before the talk is up change it (the shop's prices with it: CHA 18 is 5% off). The shop's portraits
change whose inventory is shown, not the leader.

**The Loader's window on the sequel**: `apt-get install -y python3-tk`, Xvfb `:56` 1440x900 (`:55` is
smaller than the window), `python3.12 -m dsloader view --pid $(cat $WORK/rav.pid)` from `obsidian-edition/`;
stop `ravdice.py` first and the window (by pid) before running it again (the game's lock). Its party tabs
use the sequel's layout made from SL's. No moment out of a fight at the start: the opening talk ends in
the ambush, so the inventory screen (to check the gear's slot names) waits for a later save.

**Its first fight** (logs/2026-11-19-ravager-fight.md): the opening talk (3, Return) ends in the
Draxans' ambush, a fight at once; in a fight USE opens for the one whose turn it is (DS:426Dh, SL's
4979h). Right clicks on bare floor cycle the pointer: arrow, sword, look (the mode at DS:1440h: 1 the arrow; a talk's end sets it back to the arrow, and the arrow keys walk only with the arrow); a figure under it turns
red; a look opens a box (name, level, weapons) that a click on it closes. Creature records: 31h
bytes at the far pointer DS:19C9h, +0 HP, the region's people all listed (`ravcreatures.py`).
`ravds.py HEX` finds the WotR address of an SL data-segment offset by the code before its uses.
Of the opening party's spells only Chill Touch is a fixed one (Ar'anda's); its aimed click wasn't
taken on a Draxan 1.5 squares off (a touch spell: too far, likely).

**Fights and spells, for a test** (logs/2026-11-19-ravager-scare.md): the manual's hot keys: **Q**
brings the END menu (**E** in it is END TURN), C the cast screen, G guard, W wait, N/P the next or
previous foe, 1-4 the leader; Esc with nothing up quits. `ravfight.py until N` ends the others' turns
until member N's (the order varies run to run). A caster hit this round has every icon crossed out.
**Spells known**: a 15-byte bitset a member (bit n, spell n; wizard spells only), the roster's `SPST`
chunk; Ar'anda's at 3F3DCh after START GAME (a set bit is offered on USE at once: a test edit, never
saved). An area spell's reach shows as a ring of dots round the aim (on bare floor or a foe, not on a
party figure). A creature record's +18h is 60h while Afraid. **Spell slots**: DS:446Ah + 22h a
member, wizard casts left by level, the priest's 0Bh on: a cast went off if its level's count
dropped (logs/2026-11-19-ravager-cant-save.md). **A creature's level** for the saves (1987:154 in
build_image's image): a human's first level (sheet +1Eh), else the best of its class levels. In the
file, an overlay's far call names an overlay-manager selector (98h), not a segment: follow it in
the image.

**Its spells, and the fixes carried over** (2026-11-19, logs/2026-11-19-ravager-fixes.md): no
spell table in its program; each spell is `RESOURCE.GFF`'s `DATA` 0-319, 73 bytes (SL's 32-byte
record, then the name and an 8-letter short name), read one at a time as the spell is used
(choosing Bless on USE loaded `DATA` 115 whole; nothing else held). In Tyr: Return pages a talk,
the number keys pick a reply, the top-left icon opens USE, a right click cancels a spell's aim.
**`ravfixes.py [OUT]`** makes a copy of the sequel (`$WORK/ravfix`) with the mod's fixes that
carry over unchanged: five of the program's at their twins' offsets, the spell records' by name.

**Its USE screen and spell slots** (2026-11-20, logs/2026-11-20-ravager-use-slots.md): SL's code at other
addresses: the LEVEL button labelled at 7950Dh (its "add sp,0Ch" 79543h), a window brought to the front
ending 303BEh; the window on show DS:1431h (SL's 11A4h), the level on show DS:43ECh, the list a byte a
member DS:43E8h (1 MAGE, 2 CLERIC, 3 PSIONIC), the character on show selector 370h:0B44h (load + 3E71h), the
USE screen's window selector 4D8h:0 (load + 45C9h), the text routine 301Bh:172h (SL's 2B7Ah:16Dh, its one
far caller 221E3h). **The slot routine** is 626B7h (SL's 5E0ACh): the same but for its test switch (a byte,
DS:13F8h) and which classes cast, asked of 62B45h (spell, class): wizard spells classes 11 and 18, priest
spells by a jump table of spheres (1-8, 13-16, and 19 all of them; the spheres a byte a spell at selector
3D0h:7D3h, load + 41F1h). **Finding a far data address**: SL's selector (the segment table at load +
4137h, + the selector; the sequel's at load + 45E8h) and the code using it, then the same code in the
sequel (`b8 SEL 8e c0 26 ...`). **On USE out of a fight**: MAKE <NAME> LEADER (the small top button left of a
portrait) doesn't change whose spells show, but a click on that portrait then does; a spell is cast by
clicking its icon (it hangs on the pointer) and then the target's portrait. The roost's second doorway's
steps were at game (253, 90) in one run (the view differs from run to run): look at a grab first.

**Its items and item boxes** (2026-11-20, logs/2026-11-20-ravager-item-box.md): an item record (17h bytes,
DS:19C1h) keeps SL's fields to +0Eh (the charges, read as a word), then **the power, spell + 1, a word at
+10h** (SL's byte at +0Fh; +0Fh unused), then SL's +10h on two bytes later (the slot +13h, the name +14h, the
plus +16h). Counting each field's uses in the two programs (the code `imul ..,15h/17h; les bx,[items];
add bx,..; <op> es:[bx+N]`) matches the fields where a running game has nothing to show. The item box
routine ends at 9A4FEh (SL's 8C1A1h); the box has an INFO button at the right of its last row, so a line
drawn there must stay short. **Opening a box**: I (inventory), a portrait on the left for the member, a
right click on the item (Ar'anda's left hand at game 174,92, chest 174,67); a second right click closes
it. The material to-hit routine is 1D401h (SL's 5EB31h), the same table.

**Its inventory panel** (2026-11-20, logs/2026-11-20-ravager-inventory.md): SL's code at the same
distances, ending the weapon lines at 91286h (SL's 6F6BFh); the thief tables at load + 449Bh (race rows
from +8, DEX's low/high/top at +A0h/+A8h/+B0h, the armour penalty +B8h), the DEX reaction and defence
tables at DS:084Ch and DS:0866h. The thief routine (8C647h) gets DEX and the level from functions; for a
check run `ravthief.py MEMBER` (it needs `ravfixes.py` run first, for `$WORK/ravfix`). **Reading the
panel's numbers**: zoom the screenshot, the small font's 6 looks like a 5. Portraits are at game x 30,
y 21, 67, 112 and 158.

**Its View Character screen** (2026-11-21, logs/2026-11-21-ravager-view-character.md): SL's screen and
code, ending its panels at 987FBh (SL's 8A471h), the text routine, window and character at SL's distances
(-1A9h, -1B4h, -19Bh); the creature's movement +13h. The game's text routine changes ES: read what you
need before drawing. Opened by the bar's top-left icon (22,17), then VIEW CHARACTER (47,171).

**Its creation screen** (2026-11-21, logs/2026-11-21-ravager-creation.md): SL's code and boxes (DS:11F4h
on, the hit points' DS:1224h); the sheet, creature and window at DS:1429h, 142Dh, 1431h (SL's 119Ch,
11A0h, 11A4h); the creature's THAC0 (+16h) follows the classes as they change; the hit points drawn by
6C87Bh, PSP after them (6D6AEh, 6B79Ch); the labels' ink DS:2D14h, F0h white there. Title menu's CREATE
CHARACTERS (160,92), right-click a slot (70,56), NEW (110,57); EXIT (280,160).

**Its creation screen's clicks** (2026-11-22, logs/2026-11-22-ravager-rolled.md): after `ravcreation.sh`, a score
answers a click on its number (`ravclick.py 40 Y`, Y 140, 147, 154, 161, 168, 175 for STR to CHR; left +1,
right -1, going round past the least and most), the hit points on the line below their numbers (`ravclick.py
100 176`). The screen's numbers: the creature being made DS:142Dh (scores +19h), the sheet DS:1429h (hit
points +8), the least and most score DS:42D4h and 42D2h, the hit points' most and least DS:42D6h, 42D8h.

**Its rules and hit dice** (2026-11-21, logs/2026-11-21-ravager-hit-dice.md): DSCLOG2's header has
DSCLOG's RULES (+170) and RULES_HI (+270), written by the Loader with only ravager.RULES_PORTED; a
dice log started without settings (`ravdice.py`) writes 0. The hit-die rolls: 9501Dh (94F60h's: creation's
die and the level-up from XP, called from 9574Bh), into the sheet's +0Ah, the class table's +38h by CON
a floor; and 95CCEh, a level lost (the XP set lower, the rolls taken off). The most hit points from
+0Ah: 95193h (SL's 874B0h), which the sequel calls only in the level-up (957E0h): creation's fix,
logs/2026-11-21-ravager-creation-hp.md.

**Its item types are OBJEX.GFF's ALL 4** (2026-11-22, logs/2026-11-22-ravager-item-types.md): 102 types,
read into memory at the chunk's own length, so a longer chunk adds types (the Loader's OBJEX2.GFF adds the
mod's 33 as 102-134). A test edit of an item's type (the word at item +0Ah, items from DS:19C1h) shows in
the item box at once (material and dice).
Its item names (RESOURCE.GFF's TEXT 1000, 255 lines; an item's +14h word) can't be added to by
lines: 4 more broke the inventory screen (wrong items shown, AC -12), with a control: the lines
run past the game's table of 256 far pointers (DS:56F3h). DSCLOG2's SITE_NAME at the table's 7 reads gives
names 256-415 from its ITEM_NAMES, which the Loader writes as it attaches (logs/2026-11-22-ravager-item-names.md).

**Its item types and helms** (2026-11-21, logs/2026-11-21-ravager-helms.md): the types' table at DS:19CDh,
15 bytes a type (AC +0Eh, 80h at +0Bh counts for AC, slot +05h); the items' types and names can be listed
from OBJEX.GFF's RDFF records (kind 1, 17h bytes, as in memory) without a save that has them. Helms: type
55 (AC 0, hats too) and 56 (AC 1). The AC function's worn list is at [BP-324h], 10 bytes an entry.

**Its two weapons** (2026-11-21, logs/2026-11-21-ravager-two-weapons.md): SL's two-weapon routine at
5DE34h (called from the attack, 5C78Ch: [BP+6] the weapons ready, [BP+8] the combatant, [BP+0Ah] the
item; the ranger test on the sheet's +10h 200h), the attacks a round stored at 5CEE8h ([BP-0Ah]; the
attack's item [BP+12h], range [BP+16h]). A creature's item lists (+8, +0Ah, +0Ch) are things in the
combatants' table numbered from 201h for the party, not below 400. Computer Control in a fight: C, then
the lower small icon left of each character box (game 47,53 / 98,53 / 47,113 / 98,113).

**Its inventory's two hands** (2026-11-21, logs/2026-11-21-ravager-half-giant.md): the routine that
puts an item in a hand at 7761Bh (SL's), the character on show at (load + 3E71h):0B44h, an item type's
two-handed bit +0Bh 40h (SL's +0Fh), tested at 77976h (the other hand's: "Two handed weapon in use") and
77A0Dh (the new one's: "Need two free hands"). The far "has effect" routine 608h:20h and "take it off"
608h:4Dh (SL's 598:20, 598:4D; the bytes in a call are `08 06`).

**Its weapons and the attack's frame** (2026-11-21, logs/2026-11-21-ravager-cahulaks.md): from
OBJEX.GFF's items, Cahulaks 24, Double Spear 39, Gythka 52, Polearm 80, Sling 93, Staff Sling 98,
Trikal 100. The attack routine's frame: [BP-0Ah] the round's swings, [BP-16h] the swing, [BP+12h] the
item, [BP+14h] its type, [BP+16h] the range, [BP+18h] the attacker, [BP+0Ah] - [BP+0Ch] what the d20
must reach; each swing starts at 5D052h; a hit's damage done at 5D1FEh ("mov byte [bp-19h],0").

**Its far calls and stubs** (2026-11-21, logs/2026-11-21-ravager-stinkpots.md): a far call names a
selector (388h, 598h, 608h...), a row of the word table at file 4B080h, 8 bytes a selector, its first
word the segment less the load (388h: 3F49h, 598h: 46A7h, 608h: 473Bh, 628h: 475Ah). Overlay routines
are reached through a stub segment in the root (`CD 3F 00 00`, the overlay's place from file 57580h as a
dword, its size; then 5 bytes an entry from +20h: `CD 3F` and the routine's offset). The saving throw
66D26h is 598h:75h (target, thrower, power, level; AL 0 failed), the damage resistance 85052h 628h:25h,
the effect adder 7F9E6h 608h:3Eh (target, thrower, spell, effect, a dword time: seconds a timer, negative
charges; a last byte). DSCLOG2 calls them as DS + (segment - 47E0h) : entry. The effects' records (31
bytes: name, icon ICON 21000 + spell) have two empty ones, 12 (now Nauseated) and 88. **To throw by
hand in a fight**: walk two squares off, one right-click (the sword), hover a foe until red shows under
it (yellow is a friend), mousedown / mouseup. Web from the Draxans gives a webbed member an END menu and
turns its Computer Control off: E ends it; taking effect 66 off the party in memory keeps the fight going.

**Its distance routine** (2026-11-21, logs/2026-11-21-ravager-reach.md): 1D40:35EFh (file 25BEFh),
[BP+6] and [BP+8] two combatants, the squares between in [BP-1Ch] at its end (25CDDh); its melee
callers' ways back 20617h (the sword pointer), 1EADCh (the attack click), 1E2AAh (the walk arrow on a
foe), 1FF39h and 260CBh (the walk to attack), 2420Ah (the step switch), and the combat overlay's IP
14A2h and 1A72h (the computer's). The line test 0B0Bh:00A4h (10354h); the map things' feet DS:67C5h.
The pointer cycles on a right-click (walk arrow, sword, eye); "no" on the floor in sword mode is
normal. **To place a figure for a test**: move its map thing's top left (+3/+5) and feet (+0Ah/+0Ch,
sixteenths of a square, `shr 4` the square) by the same amount; the game draws it there at its next
redraw and its distance and line tests use the new place (logs/2026-11-21-ravager-reach.md). The
game's dice for each item type: +08h the sides, +09h the count, +0Ah the bonus (signed). A creature's item lists are things 201h and on in the combatants' table.

**Creature size in it** (2026-11-21, logs/2026-11-21-ravager-size.md): the swing's dice at [BP-10h]
count, [BP-12h] sides, [BP-14h] bonus; the call's first swing [BP-0Ch]. The Draxans are people (race
1 to 8), so medium; the Giant Skeletons up the street are large. A spell test: aim Hold Person with
`ravclick.py X Y none` until red shows under the pointer (yellow is the pointer itself), then mousedown
/ mouseup; a right-click on bare floor drops the pointer and ends the turn. To make a medium foe large
for a test, patch `sizes.large_by_table` in the dice log's own process (RAV_NAMES alone won't do for a
people: its race wins).

**Its Look box and damage resistance** (2026-11-21, logs/2026-11-21-ravager-look.md): the box's
routine at 640FBh (the combatant in DI, the lines' count [BP-0Ah], the text routine -20h); its damage
resistance (85052h) by a class byte at the creature's +0Fh, the classes' immune kinds at DS:2588h (18
words; weapon kinds only below the magic bits B000h) and halved kinds at DS:25ACh (7). To Look in a
fight: right-click to the eye (arrow, sword, eye) and a slow press on the figure.

**Its map and names over figures** (2026-11-21, logs/2026-11-21-ravager-labels.md): the map things
from DS:67BBh, 25h bytes each, their feet at +0Ah/+0Ch (`ravfight.py`'s +3/+5 is the top left, about 30
above); the object list's far pointer DS:67B7h (8 bytes an entry, +6 the thing), its count DS:264Eh;
the view DS:1408h/140Ah; DS:0DABh 1 on the map. The view's rectangle routine 21E0:128Ch (SL's
1DF3:142Fh), the cast routine 80580h, the main loop's pointer call 20230h, the timer 3DA2Ch. **To catch
a label**: capture frames (`import` every 0.2-0.4 s) during `ravfight.py fight` or a cast, then look for
the label's ink in them (a Miss is about RGB 239,239,223, a spell's name 251,223,93) rather than by eye.
A label written by a script of its own stays until cleared (its byte +0 zeroed): only the dice log
ticks them off.

**Choosing an enemy, the ring, the pointer** (2026-11-25, logs/2026-11-25-ravager-tab-target.md): the
routine lighting the thing under the pointer is 21060h (SL's 1E126h; found by its pushes of the pointer
DS:A109h and the view DS:140Ah/1408h before the finder's far call), keeping that thing in **DS:0DADh**
(SL's 0BCBh; FFFFh none) beside DS:0DABh (1 on the map); the finder is 21E0:2DBD (file **29DBDh**, SL's
25B52h: "push bp / mov bp,sp / sub sp,0Eh", DSCLOG2's site 77 there), reading a map thing's flags +0
(10h drawn), left +3, top +5, rise +0Eh, picture +10h, width +13h and height +14h (unsigned bytes). The
pointer's mode is **DS:1440h** (1 walk, 2 look, 4 attack; the routine setting it 2037Bh, SL's 11B8h), the
facing byte a creature at +5Eh of the round's segment (load + 3C4Fh; SL's +5Bh), the eight directions'
flag a byte at DS:0442h (the direction routine 1109Dh, SL's word DS:01F8h). `ravtab.py` prints DSCLOG2's
Tab words and these; `ravtab.py feet` each combatant's feet and screen place. **Clicks** reach the game
through the handler it sets with INT 33h 0Ch (its mouse routines at 35B9:0000 on: 35B9:0034 is INT 33h 3,
the pointer's place for edge scrolling only; the button bits it returns aren't the clicks): to give the game
a click, find that handler (INT 33h 14h, swapped and given back) and call it with event 2 then 4 (DSCLOG2's
TARGET_MOUSE). **Tab** without the Loader opens the game's own menu (the save/load/options panel), with the
Loader on a party member's turn in a fight it is the Loader's. **A DSCLOG2 routine must go above
RESIDENT_END**: code after it is freed as the helper goes resident, and the next allocation writes over it
(the upper memory chain "broken" just past DSCLOG2's block in `dosmem.py`; it ran by luck until then). **DSCLOG2's room** (2026-11-27, claude/dsclog2-segment-room): the helper is three parts, the segment
(CS: the header and the code, to IMAGE_END, under 64 KB), the tail (TAIL_PARAS on: tables and buffers, read
through FS = CS + TAIL_PARAS, `TAIL_FS`; the Loader at the header's +1834 x 16 + the buffer's word) and the
install (INSTALL_PARAS on, the EXE header's CS:IP, freed). With #218-#223 joined the segment had reached
FF1Fh and the install wrapped past FFFFh (nasm's "word data exceeds bounds"); now `test_dsclog2_room.py`
fails on a warning or under 2 KB free, and names a tail label read through `cs:`. In memory (`dosmem.py`
after `RAV_LOADER=1 RAV_UMB=1 sh ravstart.sh`) the helper's block is the segment and the tail together
(10h + KEPT_PARAS paragraphs with its PSP). To read a tail table: the header's +1836 x 16 past the image, or +1834 x 16 in the
running game; `ravtail.py` checks the tail in play (logs/2026-11-27-dsclog2-segment-room.md: with #218-#223
joined, 84,160 bytes of upper memory free, the helper's block 65,792 with its PSP). Details: DEVELOPMENT-INTERNALS.md, DSCLOG2's segment,
tail and install.
**The view to the chosen enemy, and a monster's gear before it fights** (2026-11-25,
logs/2026-11-25-ravager-tab-followups.md): the sequel's centring routine 1C5F:01F3 (file 219E3h; x, y the
view's middle, then 1 to draw) sets the view's top left to (x - 160, y - 100) rounded down to 8 and keeps it
inside the map's limits itself (DS:14D7h, 14D9h the least, 14DBh, 14DDh the most, right and bottom edges), so
DSCLOG2's PAN_TICK (PROBE_SCROLL's, DSCLOG's PAN_X/PAN_Y at +230/+232) only adds the Loader's pixels to the
view and calls it; `ravtab.py` prints PAN and `pan_moves`. **To scroll the view off a fight's figures for a
test**: `ravclick.py 319 100 none`, then `xdotool mousemove_relative -- 20 0` a few times (the game's edge
scrolling: about 500 pixels in 3 s); `ravclick.py 160 100 none` stops it. **A monster's items are unplaced
until it first fights**: their slot bytes (item +13h) run 14, 15, ... in list order (a Draxan's brigandine in
14-16, its weapons in 17-19); by its first attacker's swing the game has put them on (chest 9, legs 6, arm 0,
right hand 3, missile 2, ammo 1), and the AC routine weighs them so. The Draxans are gladiators of level 8
(sheet flags 40h, class 10): AC 1 better in armour, which the Loader's armour_worn (by the slots) missed
before their first fight (`game.armour_ready`). `ravdice.py` with `RAV_PREDICT=1` takes a Tab line's chance
apart; `RAV_NO_PAN=1` is the control for the view. Enter on an enemy out of reach (in a room behind the
doorway) gives the click and the game does nothing. **The sequel's sides** (the creature's +15h): an index into
bit masks, not SL's "same or not": the game colours the figure under the pointer as a foe when `1 << side` is in
**0F80h** (sides 7-11; 21112h: "shl ax,cl / test ax,0F80h", then side 1 another colour), and its combat code
tests them too (near 5B649h "test ax,0F80h" and "test ax,0C58h"; at 5C29Dh and 8664Eh a mask of 0F80h made for
side 0, the party's; at 5F027h 71h).
In the Tyr ambush the party is 0, the four ambushing Draxans 7, and everyone else on the map 1 (the Caravan
Master, Notaku, Templar, Boric, the soldiers, the pedestrians, the Giant Skeletons up the street, other
Draxans): SL's rule (another side than the leader's, not 4) made 31 of them foes for Tab; `rings.HOSTILE_SIDES`
(0F80h, set by ravlog) makes 4. `ravtab.py sides` lists every combatant's side through the dice log's reading
and Tab's list both ways; `ravdice.py` with `RAV_FOES_SL=1` is the control.

**Its combat log's panel** (2026-11-21, logs/2026-11-21-ravager-combat-log.md): the fight flag is a
byte at DS:13FAh, the fight's state 3C10h:19h, the clock DS:9C0Ah (scale) and DS:9C0Ch (far pointer);
the flip 16974h (pages segment 0BF3h, [118Eh]), the pointer routine 2D72:0942 and its DS:332Ch, A10Dh,
A115h, A155h, 3330h, 33B6h, 33B8h; the view centred again by 1C5F:01F3. The view moves by that routine (its end 21A5Ah) or by following
a figure (262C:0D80 given CAM_X/CAM_Y's addresses, then drawn by 262C:06C4: calls at 1E3E7h, 2018Eh,
21439h); the game's drawing scrolls the screen, panel and all, so DSCLOG2 draws the view again after
each (INT D7h, D8h). The interface's blue-greys are palette 232 to 239 (combatlog.LAST 253). To count
copies: `import -window` in a loop (about 20 frames a second), the well colour (56,56,77) outside the
panel. **To play with it**:
`ravdice.py` running, L on the map (the dice log starts with the panel closed); the collapsed panel's
line sits at game y about 190. A copy of the panel after a scroll lasts one frame: check by frames
(`import` every 0.4 s) for the panel's well colour left of x 134.

**The panel's copies in Shattered Lands** (2026-11-27, logs/2026-11-27-panel-scroll-autosave.md): `framegrab.sh
DIR SECONDS` in the background while `untilturn.sh` plays, then `panelcopies.py DIR` counts the frames with the
panel's colours left of or above it and their runs. The game's moves of the view: following a figure (2191:0BE3
writes CAM_X/CAM_Y, 2191:0648 draws, from 1B278h, 1CA32h, 1E439h) and centring (191F:01FF on a thing, 191F:0281
on (x, y)); 2191:0648 scrolls when the view moved 40h or less. Redrawing the whole view after a move leaves the
copy up as long as before (the top is drawn first): draw again only where the copy went.

## The talk portraits (2026-11-27, logs/2026-11-27-ravager-small-portraits.md)

- **The face's routine** is 88E67h (Shattered Lands' 7DEDFh, the same code): it loads `PORT` n into DS:6558h
  (88DA2h; n 0 loads BMP 12000 instead, and only while es:[4] of selector 480h, a fight, or es:[3Ch] of 3A0h,
  the shop, is set: a talk out of a fight with no speaker draws nothing), then draws it by C8h:3BECh (1, x,
  y, 0, the picture, the frame number). The face is frame 0 at (0, 0), the shop's at (0EEh, 6); with no
  speaker, **BMP 12000's frame 1** (the frame round a grey wash: the XP at a fight's end). The shop (908B9h)
  draws 12000's frame 0 (the frame with a clear middle) at (0EEh, 6) first. A picture chunk with one frame
  where the game asks for frame 1 draws nothing (the first try of the smaller frame, 2026-11-27).
- **The talk window** is WIND 12500 (Shattered Lands' 3007): its height at head +0C0h, its places 30 bytes
  from +105h (BUTN 12300 the 300 by 58 click area at (0, 0), EBOX 12400 the text at (75, 6), the scroll
  buttons 2093/2094 at x 305). WIND 12501 is the replies' window (Shattered Lands' 3008, the same), 12502 a
  58-high box with its text at (56, 6) (Shattered Lands' 3500). Shattered Lands' talk window has its frame
  as BUTN 2090 at (8, 6) and the face drawn at (16, 13); the sequel draws its frame inside the face.
- **The sequel's PORT** faces are 72 by 72 in the PLNR form (one 73 by 72, PORT 24), the frame drawn in
  (8 left and right, 7 top and bottom: the face 56 by 58 at (8, 7)); BMP 12000 is 73 by 73, two frames.
  The Loader's copy makes them 48 by 46 (`ravportraits`); new art for the faces goes in as the game's own
  PORT chunks (72 by 72, frame drawn in), and the Loader cuts it down the same way.
- **Shattered Lands' no-speaker picture and shop panel** (2026-11-27, logs/2026-11-27-ravager-no-speaker-shop.md):
  its 7DEDFh draws BMP 12000's frame 1 for no speaker too, and there that is a 32 by 32 stone dark-sun
  emblem at the face's place (16, 13), inside the window's own frame (BUTN 2090); 12000's frame 0 is the
  48 by 47 frame, which its shop (836F1h) draws at (0FCh, 0Bh) with the face at (104h, 12h). Both games'
  shop window is WIND 13500, the same but for SELL (BUTN 13304: Shattered Lands' (255, 59), under the face;
  the sequel's (277, 159)) and MORE (13303: (255, 159); the sequel's (235, 159)). The panel is BMP 13004
  (86 by 170). **To see the no-speaker picture without a fight**: `RAV_POKE=88E6F=33f690` (every face the
  empty one) and a shop: the shop's flag loads 12000 for it, frame 1 drawn at the shop's place.
- **The first fight won quickly for a test** (the XP message): `ravstart.sh` (a new game), the talk (3,
  Return, four times), a click up the street (160,45), then in memory (never saved) the party's creature
  records' HP (+0, ids 8016h-8019h, `ravcreatures.py`) 250 and the foes' (side 7 at +15h, HP above 0) 1,
  and `ravfight.py fight`. The party misses a lot: one run took 8 minutes, another left the last Draxan
  standing after 20 (`fight` and `tabfight` both). Computer Control then won it in under two minutes: in
  the fight, the top-left icon (22,17) opens USE, the small lower icon by each living member's figure (98,53;
  47,113; 98,113), Escape.
