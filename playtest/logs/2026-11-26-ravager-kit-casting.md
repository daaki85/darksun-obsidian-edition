# Test log: kit casting levels, cures and spells known in Wake of the Ravager (2026-11-26)

Under test (branch `claude/ravager-kit-casting`, merged with `origin/obsidian-edition` after the merge train):
DSCLOG2's KIT_CAST_LEVEL (site 205 at 629FEh, the end of 628AFh's class loop: the level a spell is cast at),
KIT_CURE (site 206 at 66545h, the cure handler's heal) and, in EL_SPHERE (sites 90-92 after the calls to
62B45h), HEALER_COSMOS and KIT_BARS (spells known). AVENGER_AREA/AVENGER_ONE (sites 207, 208) and CELL_MORE
were not played (tests/test_ravkitcast.py covers them).

Setup: Xvfb :55, the DOSBox lock held by this session (flock holder `kc.held`; another agent's holder before
it, about 20:14-20:42 UTC), a throwaway copy `/tmp/playtest/ravKCL` of `rav`, `RAV_LOADER=1 sh ravhold.sh
/tmp/playtest/ravKCL` (the Loader's copy with this branch's DSCLOG2; the Tyr ambush, Ar'Anda's USE screen at
LEVEL 3), `RAV_NO_SAVES=1 ravdice.py` attached. Test edits only (ravkits.py set / levels, the creature's hit
points by hand): nothing saved.

## Steps

### 1. An Arcanist's Fireball (about 20:43-20:50 UTC)

Ar'Anda made a single-class preserver 6 (`ravkits.py set 0 3 3 11`, `levels 0 6`: kit byte 03, the
Arcanist, kitpages.kit_ids 23). Fireball (the first LEVEL 3 icon, game 175,60) at the Draxan up the street
(game 165,22):

    Fireball damage: 7d6 = [2 + 4 + 2 + 1 + 5 + 2 + 2] = 18 (1d6 for each caster level: 7 at caster level 7)

three times (Thy'rokh and two Draxans in the blast). `kc_levels 202` after (KIT_CAST_LEVEL counts each call of
628AFh that changes a level, and the game asks it many times a cast).

Then every turn ended with Q (`ravfight.py until 0`) to reach her next turn: the Draxans beat the party
("YOUR PARTY HAS BEEN DEFEATED"). DOSBox restarted (my own pids, killed by pid).

### 2. The control, and a Healer's spells known (about 20:52-21:05 UTC)

`ravhold.sh` again; Ar'Anda the same preserver 6 with **kit byte 0**. Fireball at the Draxans by the left wall
(game 60,78):

    Fireball damage: 6d6 = [2 + 4 + 6 + 6 + 5 + 4] = 27 (1d6 for each caster level: 6 at caster level 6)

four times; `kc_levels 0`.

Terrannus (earth cleric 7, the party's Crusader, kit byte 43h) made a **Healer** (`ravkits.py set 1 0x42`:
kitpages.kit_ids 6). His USE screen (C), against the Crusader (43h) at once:

| LEVEL | Healer | Crusader (control) |
|---|---|---|
| 1 | 11 spells: Bless, Curse, Cure Light Wounds, ..., Magic Stone, Protection from Evil, Remove Fear, ..., Shillelagh; **no Cause Light Wounds** | 12: Cause Light Wounds (the dark icon after Cure Light Wounds) there |
| 4 | **13** spells, PRI 2/2: Abjure, Cloak of Bravery, Cloak of Fear, Dust Cloud, Free Action, Neutralize Poison, Intensification of Weather, Return to Earth, Thorns of Binding and others (the cosmos's druid spells) | 4 spells, no level 4 casts left |

Counters after: `kc_cosmos 71`, `kc_barred 19` (the Crusader's lists ask too, but count nothing).

### 3. A Healer's cure and the control (about 21:05-21:15 UTC)

Gerakis's hit points 100 of 165 and Thy'rokh's 40 of 72 (the creature's +0, a test edit). Terrannus, Healer,
Cure Light Wounds dropped on Gerakis's portrait on the USE screen:

    Cure Light Wounds: 1d8 = [3] +1 Healer = 4
      Gerakis regains 4 HP from Cure Light Wounds, now 104/165 HP

`kc_cures 1`. On his next turn, made the Crusader again (43h; Cause Light Wounds back in the list), Cure Light
Wounds on Thy'rokh (6 of 72 by then):

    Cure Light Wounds: 1d8 = [2] = 2
      Thy'rokh regains 2 HP from Cure Light Wounds, now 8/72 HP

`kc_cures` still 1. DOSBox and the dice log killed by pid, the lock let go.

## Result

Each part works against its control: an Arcanist casts a wizard spell one level higher (7d6 against 6d6), a
Healer's Cure Light Wounds heals one more a die and is labelled in the dice log, and a Healer's list loses
Cause Light Wounds and gains the druid spells of the cosmos (13 level 4 spells against 4).

## What a play needs to know

- On the USE screen a spell is cast on a party member by clicking its icon and then the **member's portrait**
  in the screen (it doesn't close for a pointer on the map): `ravfight.py cast ... OBJECT` with a member
  picks the icon up and leaves it on the pointer. A right-click on an icon shows the spell's description
  (its name too), a left-click closes it.
- The USE screen opens at the LEVEL it was last left at, not at 1: `ravfight.py cast X Y LEVELS` counts
  LEVEL presses from there.
- The hover name in the bottom bar comes only for the first three icons of a row in a quick sweep (the
  fourth and fifth show "N LEVEL N SPELLS TO CAST"): name those with a right-click.
- Ending every turn with Q to wait for a member's next turn loses the Tyr ambush: let the others attack
  (`ravfight.py attack` on each other member's turn).
- `ravkits.py set` takes the kit byte as two bits a class place from the oldest class; Ar'Anda's three classes
  have no kits, so she must be made single-class first.

## Gaps

- A Lifebinder's cure, a Rescuer's, Cell Adjustment's more and the Wilderness Avenger's Cause dice not
  played (tests); nor a Spirit Caller's or Wasteland Seer's sky levels (the ambush is outdoors: KIT_OUTDOORS
  0Fh).
- Whirlwind and Restore Youth for the Healer wait for those spells' port (COSMOS_MORE kept 0FFFFh).
- Water: nothing new (Tyr's street, as before).
