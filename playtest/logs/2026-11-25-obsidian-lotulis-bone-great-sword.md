# Test log: the obsidian lotulis, the bone great sword and their +1s (2026-11-25)

**Under test:** branch `claude/ravager-magic-metal`: two new types (DSCLOG's EXTRA_TYPES 157, 158:
an obsidian lotulis for fire clerics, a bone great sword for water clerics), sold by Melkor, and
their +1s (the Obsidian Lotulis +1 on Dagger, the Bone Great Sword +1 on Dakaren), with icons of
their own (pictures 2718-2725).

**Build:** `dos/DSCLOG.EXE` built from the branch; the Loader's copies prepared by `start.sh`.

## Each new item's icon, name and box

From `pens-after-arena` (autosave and quick save off), `buildcheck.py` OK (extra_types the same as
the EXE). All four given to Gerakis in memory (`givenew.py`; **not saved after**). On the inventory
screen each shows its own icon in the backpack, the bottom bar names it, and a right-click opens
its box:

| Item | Box |
|---|---|
| obsidian lotulis | 30$, "2 handed Obsidian Lotulis", 1D10-1/1D12-1, Hit -2 (the game's obsidian penalties) |
| bone great sword | 100$, "2 handed Bone Great Sword", 1D10-1/3D6-1, Hit -1 (the game's bone penalties) |
| Obsidian Lotulis +1 | 20,800$, "2 handed Obsidian +1 Lotulis", 1D10+1/1D12+1 |
| Bone Great Sword +1 | 20,800$, "2 handed Bone +1 Great Sword", 1D10+1/3D6+1 |

The +1s' icons burn (the lotulis' blades in the fire colours) and shine (the sword's blade in the
water's), every other pixel, as the other +1s.

## Not played

- Melkor's shop (Gedron), Dagger (the White Sand Outlaws) and Dakaren (the Silt Sea): no save
  reaches them. Checked by the tests (`RavagerMagicTests.test_places`, `test_metal_sold`).
- A fire cleric choosing the lotulis, a water cleric the two-handed sword, on the creation screen:
  DSCLOG's KINDS_ALLOWED reads kind_of_type over every type, so the new types let those kinds in;
  checked by the tests (`test_cleric_materials`, the kind table against specialize.py's).

## Lessons

- `click.py X Y right` at game pixels (320x200) opens an item box; an `xdotool` click with
  `--window` doesn't reach the game (DOSBox holds the mouse: the pointer never moved).

**Water**: no new area.
