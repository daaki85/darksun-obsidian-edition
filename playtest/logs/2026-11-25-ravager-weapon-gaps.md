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
and fighting with one. The Bone Helm gave no AC in the sequel (DSCLOG2's helm probe knew type 55 only): **fixed**
after the play, PROBE_HELM_AC and PROBE_BOX_AC count its type, 104, as 1 with RULE_HELMS (tests/test_ravgear.py
runs both probes).

## After the fix (the old save, test edits, nothing saved)

`ravload.sh ravager-after-ambush` with the rebuilt DSCLOG2 and the dice log:

- **How the name shows**: Thy'rokh's +1 gythka (item 9) made the Short Sword +1 in memory (entity -19900, type 109,
  name 258): the pointer's line "METAL SHORT SWORD"; its item box "Metal / **+1 Short Sword** / 1D6+1", 20800; the
  panel's line "+1 Short Sword" ([picture](img/2026-11-25-ravager-short-sword-box.png)). The sequel identifies
  nothing: every magic item shows its plus so (the game's own "+1 Gythka" beside it), as Shattered Lands' plain
  magic weapons ("+1 Short Sword") do.
- **The Bone Helm's AC**: Terrannus' worn item 6 put on his head (slot 7, the head: `game.EQUIP_SLOTS`) as type 55
  named as a hat: **AC 3**; as type 104 (the Bone Helm's): **AC 2**; as type 55 named Helm: **AC 2**. The Bone
  Helm counts AC 1 as the game's Helm does.

## Water

No new area: Tyr's streets and Shadow Square only (nothing new to add).

## A saved game's shops stocked (2026-11-26)

`shopstock.py` (the dice log's `_stock_pass`): a seller loaded (a person whose creature's +6 is one of
ravgear's shops, negated) and not yet marked gets the new items OBJEX2.GFF gives it, then its mark (the
creature's +30h, the last byte of its name). `ravload.sh ravager-after-ambush`, `ravdice.py` attached:

- at once, **"Notaku stocks 1 of the mod's new items"**: his list's first item now 19900 (the Short Sword
  +1), slot 21; his creature's +30h 01.
- Walked to him (`ravgo.py x 1176 y 1224 x 560 y 1130 x 420 y 1000 x 300 y 900`), "Show me your goods":
  the Short Sword +1 on the first page at 20800, "METAL SHORT SWORD"
  ([picture](img/2026-11-26-ravager-old-save-notaku.png)).
- **Bought it** (money 50,000 by a test edit, never saved): 29,200 left, the sword in Thy'rokh's pack, gone
  from Notaku's list; six seconds on, still gone (no second "stocks" line): the mark holds.
- **The ranged stall** (the Limbo seller 323): the Staff Sling +1 at 2940 with no line from the Loader: the
  game makes a Limbo seller afresh from OBJEX.GFF's copy when its talk starts, so it has the items already.
- Clicking an item in a shop buys it at once ("NOT ENOUGH MONEY" if it can't).
