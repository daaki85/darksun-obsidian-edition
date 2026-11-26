# Test log: the mod's item types in Wake of the Ravager (2026-11-22)

Under test: the Loader's copy of the sequel's OBJEX.GFF (D:\OBJEX2.GFF, opened in place of OBJEX.GFF by
DSCLOG2's PROBE_DOS_OPEN, bit 4 in COPIED). The copy has the mod's 33 item types after the sequel's own
(`ravager.objects_fixed`). This is the first step of the party transfer
([the design](../../reports/wake-of-the-ravager-party-transfer.md)).

## Found first

- **The sequel's item types are data, not program**: OBJEX.GFF's chunk ALL 4, 1,530 bytes, which is 102
  types of 15 bytes. The far pointer DS:19CDh points at it in memory (72B9:0004 in ravager-roost), and
  the item names' block (ALL 5, "Tombstone", "Olive Branch"...) follows it there.
- **The game reads the chunk at its own length**: in a copy of the game folder with 3 types added (copies
  of type 97 with a marker byte), memory held 105 types and the names after them. So the Loader needs no
  hook to add types: it writes a longer chunk.
- Shattered Lands' 20-byte types convert to the sequel's 15 bytes: the words at +2, +4 and +6 become
  bytes (none of the mod's is over 250), and +8 to +12h move up 4. The mod's SL types 115-147 become the
  sequel's 102-134 (`ravager.mod_type`).

## In the game (ravager-roost, about 22:55 UTC)

- `ravload.sh ravager-roost` started the Loader's way. Memory held 135 types, and 102-134 were byte for
  byte the converted mod types.
- Test edit (never saved): Ar'anda's +1 Longsword (item 2, type 97) given type 107 (the mod's obsidian
  short sword, SL's 120). Inventory (I), her portrait, a right click on the sword: the box reads
  **"Obsidian +1 Longsword 0.5x1D6+1"** and the name line "OBSIDIAN LONGSWORD"; the stats column
  "+1 Longsword 1D6+5". ![](img/2026-11-22-ravager-type-107.png)
- Control: the type set back to 97, the box reopened: **"Metal +1 Longsword 0.5x1D8+1"**, "METAL
  LONGSWORD", "1D8+5". ![](img/2026-11-22-ravager-type-97-control.png)
- So the game reads a type past its own 102, its material and its dice. DOSBox stopped by pid, nothing
  saved.

Not seen yet: a fight with a mod type (the dice log's damage), and the class bits (who may use it).
Those come with the transferred items.

Water: no new area.

## The item names: no room by adding lines (about 23:10 UTC)

- The item record's name (+14h) is a word, as SL's +12h is, but the sequel's TEXT 1000 (RESOURCE.GFF, a
  name a line from 1) already has 255 names, and 236 of them are used by OBJEX's items.
- A copy of the game folder with 4 names added to TEXT 1000 ("Testname 256" on) loaded ravager-roost, but
  the inventory was wrong: Ar'anda's hands showed empty, her pack held armour pieces and a staff, her AC
  read -12, though memory still had her +1 Longsword in her hand (slot 3). This was the same with the
  test name edit (257) put back. ![](img/2026-11-22-ravager-names-added.png)
- Control: the same copy with the game's own RESOURCE.GFF, the same steps: her inventory as it should
  be (sling, dagger, +1 Longsword, AC 4). ![](img/2026-11-22-ravager-names-control.png)
- So a longer name list breaks something. The likely cause is a buffer of a fixed size, or a block
  after the names. The mod's names will go in the way DSCLOG does it in Shattered Lands instead: the
  helper makes room after the game's names as they are read in, and fills it (names.py). That is the
  next piece of work. DOSBox stopped by pid both times, nothing saved.
