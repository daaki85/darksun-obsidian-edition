# Test log: the Ravager weapons' follow-ups (2026-11-24)

Branch `claude/ravager-weapons-followups` (on the memory pass, `claude/memory-pass-6`): the trikal's
polearm reach, a specialist's rate of fire with the javelin and darts, and people who carry the new
weapons. DOSBox with the Loader's patched game, window 320x240, `buildcheck.py` OK. Nothing saved
(autosave and quick save off).

## 1. The trikal's reach (`fountain-user`, the ambush): first try, by Tab (proves nothing: section 3)

Before the speech: Ester's right-hand Bone Long Sword (item 35) made a trikal (`setitem.py 35
rec=` + `worldgear.weapon(worldgear.TRIKAL)`), her left-hand sword (31) a potion (`setitem.py 31
60`), her bow left in the missile slot. The speech clicked; on her turn every foe held (`foeset.py
C eff=34`), the Templar (combatant 22) put two squares west of her (`placefoe.py 22 -2 0 2`: 840 to
her 872, both at y 1528) and her Move made 0 (37BD:022Bh + creature x 2).

- The figure stays drawn where it was (the game draws it again only when it moves), so a click on
  the new square found nothing (the red sign); **Tab** chose it: `Chosen with Tab: Templar (16 HP),
  hits whatever the roll (Paralyzed) - Enter attacks it`.
- Return: `Ester attacks Templar with Wooden Trikal (1d10): d20 = 3, needs 10+ ... -> HIT / Ester
  hits Templar for 14: 1d10 = [5] +1 Battle Dancer +8 STR 20`: a melee swing from two squares
  with Move 0, the trikal, not the bow.

## 2. A dart specialist's rate of fire (`fountain-user`)

Before the speech: Jenna (member 1) a gladiator 9 (`kitset.py 1 10 9 0`), her weapon spec darts
(`specset.py 1 darts`), her bow (item 25, the missile slot) made darts (`setitem.py 25 rec=` +
`worldgear.weapon(worldgear.DARTS)`). Every foe held; on her turn the attack pointer and a click on
the Templar in view (combatant 25, `foepos.py`).

- **Specialized, 9th level: four throws** (the specialist's 4/1 at 7-12, the darts' own 2/1 one
  more): `Jenna attacks Templar with Wooden Darts (1d3) ... Jenna hits Templar for 5: 1d3 = [3] +2
  specialized`, four times in her turn, `Templar now 24/41 HP`.
- **Not specialized** (`specset.py 1 long_sword`, the next round): **three throws**, no bonus (`hits
  Templar for 3: 1d3 = [3]`): a warrior's weapon of a kind not chosen from 7th level, the
  specialist's 1-6 rate, as for the bow.

## 3. Control runs (`origin/claude/memory-pass-6`, a worktree, its own `loadsave.sh`)

The same save and set-up, `buildcheck.py` OK against the control's own DSCLOG.

- **Darts, specialized, 9th level: two throws** (the weapon's own 2/1): `Jenna attacks Templar
  with Wooden Darts ... +2 specialized`, twice, then Round 2.
- **Tab and Return from two squares: a swing, in the control too.** The Templar moved in memory
  two squares west of Ester, Move 0, Tab, Return: `Ester attacks Templar with Wooden Trikal ...
  hits for 13` with no reach in the build. So section 1's swing proves nothing: the Tab + Return
  attack doesn't ask the distance routine the way the pointer's click does (or the moved figure's
  place isn't the one the game measures). Noted for later; the reach test is redone by the click.
- **The click, two squares off, the control**: Ester walked to square (58,94), two west of the
  held Templar at (60,94) (combatant 25, drawn where it stands), Move 0, the attack pointer and a
  click on its figure (240,134): **the bow shoots** (`Ester attacks Templar with Wooden Bow`, twice).

## 4. The trikal's reach by the click (this branch)

Section 3's click again in this branch's build (`buildcheck.py` OK): Ester walked to (58,94), two
squares west of the held Templar (60,94), Move 0, the attack pointer, a click on its figure:
`Ester attacks Templar with Wooden Trikal (1d10): d20 = 19, needs 13+ ... -> HIT / Ester hits
Templar for 16: 1d10 = [9] -1 Battle Dancer +8 STR 20`: **the trikal swings from two squares**,
where the control's click shot the bow.

## 5. The people who carry them (a new game to the slave pens)

A new game in this branch's build (`start.sh`, `topartyfight.sh`, `arenawaves.sh`,
`leavearena.sh`: the arena's waves fought, then the pens, region 29h), so the pens' people are made
from the new data (an older save keeps the people it was saved with: in `pens-after-arena` the
gladiators still hold the Wooden Club). `npcgear.py` in the pens:

- `Gladiator  worn: Bone Brgnd. Arm Armor  held: Wooden Double Spear  pack: Leather Shield`, twice,
  and the third `held: Wooden Trikal` (its own object, 2610): a two-hander in the hands, the shield
  left in the pack (people.py: nothing in the left hand beside a two-handed weapon).
- `Scar's henchman ... held: Obsidian Two-hand Sword` (its own object, 2611); the other two `held:
  Bone Great Axe`, each with leather chest and arm armour.
- `Templar ... held: Stone Lotulis  pack: Leather Shield` (the pens' Templar, 321).

The rest (Teaquetzl's Village Heroes and Elite Guards, the Silt Runners, the White Sand Outlaws,
the Drajian Guards, the pens' weapon rack) are checked in the data by `test_ravager_weapons_carried`.

## What was learned (in the guide)

- A reach test goes by the click, never Tab: Tab + Return swings a melee weapon at a foe two
  squares off in a build without reach too, and a foe moved in memory stays drawn where it was
  (RESEARCH.md).
- `placefoe.py THING DX DY MEMBER` (new in the kit) puts a foe beside, or two squares from, a member.
- People are made from the data when their region is first entered: an older save keeps theirs, so
  a carrier test needs a new game to the place (or a save from before it).

No new area: no water to note.
