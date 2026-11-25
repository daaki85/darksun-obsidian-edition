# Test log: Wake of the Ravager's metal and magic weapons (2026-11-25)

**Under test:** branch `claude/ravager-magic-metal` (cb73b37): three metal types (two-handed sword,
lotulis, javelin: DSCLOG's EXTRA_TYPES 154-156), the magic ones (Double Spear +1/+2, Trikal +1/+2,
Lotulis +1/+2, Two-hand Sword +2/+3, Javelin +1) and their icons, and the slave pens' weapon rack's
metal javelin.

**Build:** `dos/DSCLOG.EXE` built from the branch; the Loader's copies prepared by `start.sh`.

## 1. A new game to the slave pens (the rack)

`start.sh`, `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh`, so the pens' people and things are
made from this build's data.

Done in 4.5 minutes (00:24:46 to 00:29:14), in the pens at (1816, 440) with Kurzak's greeting up.
The party moved in memory (`teleport.py 800 568 640 470`) beside the rack (square 48, 34) and
Kurzak's talk answered Goodbye (scrolled with the talk box's down arrow, 312,192; Goodbye at
30,189). `rackcheck.py`: the rack (object 2599, thing 217) holds Polearm, Quarterstaff, Polearm,
Axe and Javelin; the javelin's record (item 216) is type 156, plus 0, picture 2700: **the metal
javelin**, as `icons.which` names it. (Before the talk was answered, `rackcheck.py` found no thing
of the rack: the things are there only once the talk is done.)

## 2. Each new item's icon, name and box

All twelve given in memory (`givenew.py`, a scratch copy of `giveitems.py` taking worldgear's
specs; **not saved after**): Gerakis the metal two-handed sword, metal lotulis, metal javelin,
Two-hand Sword +2 and +3 and Javelin +1; Kilra the Double Spear +1/+2, Trikal +1/+2, Lotulis +1/+2.
On the inventory screen (I) each shows its own icon in the backpack, and a right-click on each opens
its box with the small copy of the icon (BOX_SMALL: no text pushed off the box) and the game's
own wording:

| Item | Box |
|---|---|
| metal two-handed sword | 500$, "2 handed Metal Two-hand Sword", 1D10/3D6 |
| metal lotulis | 150$, "2 handed Metal Lotulis", 1D10/1D12 |
| metal javelin | 150$, "Metal Javelin" |
| Two-hand Sword +2 / +3 | 41,600$ / 62,400$, "2 handed Metal +2 (+3) Two-hand Sword" |
| Javelin +1 | 2,800$, "Obsidian +1 Javelin" |
| Double Spear +1 / +2 | 20,800$ / 41,600$, "2 handed Wooden +1 (+2) Double Spear", 1D8+1 |
| Trikal +1 / +2 | 20,800$ / 41,600$, "2 handed Wooden +1 (+2) Trikal" |
| Lotulis +1 | 20,800$, "2 handed Stone +1 Lotulis" |
| Lotulis +2 | 41,600$, "2 handed Metal +2 Lotulis" |

The bottom bar names the item under the pointer ("METAL TWO-HAND SWORD", "METAL LOTULIS").
`buildcheck.py`: OK (extra_types and extra_names the same as the EXE).

## Not played

- The magic weapons in their places (the Fields, the Elven Slavers, the Hot Springs, the Silt Sea
  Ssurans, the Lower Castle, the Upper Castle, the Ssuran Ruins, the gladiators' camp, the Wyrm
  School) and Melkor's two: no save reaches those regions, and a carrier is made from the data only
  the first time its region is entered. Checked by the tests: each placement in the data
  (`RavagerMagicTests`), every copied region named in DSCLOG's table of copies
  (`test_regions_opened`), the records each object gets (`test_records_fit`).
- The metal lotulis' second foe: by the emulated routine (`test_second_foe`), not in a fight.

## Lessons

- A right-click on an inventory item opens its box; a left-click on the box closes it. Escape
  closes the whole inventory, and right-clicks after that land on the map and cycle the pointer
  (`pointer.py walk` puts the arrow back). The box stands lower for a lower backpack cell.
- Kurzak's greeting in a new game holds the pens' things back: answer it before reading them.

**Water**: no new area.

## 3. The two-handed sword renamed Great Sword

The game puts "2 handed" before any two-handed weapon's name ("2 handed Bone Gythka"), so the
name "Two-hand Sword" read twice ("2 handed Metal +3 Two-hand Sword"); the sequel's own,
"Twohand Sword", would read the same. Renamed **Great Sword** (as the game's Great Axe). From
`pens-after-arena` (loaded, both given in memory, not saved): the boxes read "2 handed Metal Great
Sword" (500$) and "2 handed Metal +3 Great Sword" (62,400$). The other eleven read in the game's
own order (kind of hand, material, plus, name), as its "2 handed Bone +1 Gythka", with nothing
twice.
