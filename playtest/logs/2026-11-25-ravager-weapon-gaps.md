# 2026-11-25 Ravager weapon gaps: the new items in a game

Build: branch `claude/ravager-weapon-gaps` (on PR #184's `claude/ravager-join-gear-spells`): `dsloader/ravgear.py`'s 14
magic weapons and 15 plain items, put into OBJEX2.GFF by `ravager.prepare` with Shattered Lands' folder
(`ravstart.sh`, RAV_LOADER=1, `$GAME` the Shattered Lands install). DOSBox 0.74 on Xvfb :55, the window 640x480.

## An old save

`ravload.sh ravager-after-ambush`, then `ravshop.py thing 33` (Notaku): his seven items, no Short Sword +1. As
expected: a save keeps the people and things it has made; the new items come with a new game only.

## A new game

The title menu's START GAME (game 159,75), the opening talk (3, Return x4), the ambush won by Computer Control
(C, the four small icons, Escape; about 90 s). Notaku's list (`ravshop.py thing 33`) ends with **item 125: entity
-13000, price 20800, type 109, name 258, plus 1** (the Short Sword +1), and a Draxan of Tyr (thing 44) carries the
Short Sword +2 (41600, type 107).

**The ranged-weapon stall** (its seller at world ~536, 1100, on the way: the Limbo seller 323): the second page has
the Staff Sling +1 at **2940** (2800 and the stall's 5% markup), Windlash's picture, its name "LEATHER STAFF SLING"
(the game's own name; the plus isn't in a name, as the game's own +1 arrows show "ARROW").

**Notaku** ("What kind of substances do you sell?", "Yes, that was me", "I'm not interested", "Show me your goods",
MORE): the Short Sword +1 last on the second page at 20800, but:

1. **Its picture was a grey ring**, not a sword. Its BMP was right (the same as the plain metal short sword's, at
   22427): the game draws objects 13000-13999 as something else. **Fixed**: the Loader's drawn pictures moved to
   19900 on (`ravgear.OWN_ICONS`; the transfer's numbers end at 16003 for Shattered Lands' highest object, 32003).
2. **Its name read "METAL"**: the mod's names (256 on) are written into DSCLOG2 by the dice log, which wasn't
   running. With `ravdice.py` attached: **"METAL SHORT SWORD"** (the game adds the material). Not a bug: the
   Loader always runs the dice log.
3. After the first fix, **a bright blue pixel** on the blade: palette 2 (PAL 1000's light blue) shows pure blue
   on the inventory screen. **Fixed**: `ravitems.stable_colours` leaves out 1-15 (the screens' own); that pixel
   is now a blue-grey, as Shattered Lands' blade highlight.

After both fixes, a new game again: the Short Sword +1 at **19760** (the leader's CHA discount, the dice log on),
a short sword with a few fire-coloured pixels ([picture](img/2026-11-25-ravager-notaku-short-sword.png)).

A scan of every item record in Tyr (entities -14000 to -29999) found the Loader's items there: Short Sword +1
(Notaku), Short Sword +2 (a Draxan), Great Axe +1 (Headsman's picture, a Draxan), metal mace (a templar), metal
dagger (Dhukkar), metal pick (Arslan), metal polearm (a Draxan).

**A slip**: the sword pointer, taken for the look, clicked on Notaku and started a fight; the game was restarted
(nothing saved). The pointer's barred forms over bare ground look alike: take a picture before a click on a person.

## Not tested in play

The weaponer's 13 plain weapons, the armourers' Bone Helm, the carriers outside Tyr and the containers (built and
checked by `tests/test_ravgear.py` with the game's files: every object's pack ends with its new items), buying one,
and fighting with one. The Bone Helm gives no AC in the sequel (DSCLOG2's helm probe knows type 55 only).

## Water

No new area: Tyr's streets and Shadow Square only (nothing new to add).
