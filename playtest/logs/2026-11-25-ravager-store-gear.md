# 2026-11-25: STORE and RECALL, and fuller starting gear, in Wake of the Ravager

**Under test:** branch `claude/ravager-store-gear` (from `claude/ravager-join-loot-tabs`): row 16 of the unported
features. DSCLOG2's **RS_CLICK** (site 83 at 6DE85h, SL's PROBE_RS_CLICK at 6625Dh: the creation screen's click
routine's "mov cx,16h") with STORE and RECALL in the sequel's creation window 19503 (`rollstore.rav_chunks`, the
buttons carved from the sequel's own SAVE, LOAD, DROP and DELETE in its packed picture form, `art.decode_packed`);
DSCLOG2's **GEAR_DONE** (site 85 at 6E2F2h, SL's cr_weapons place 666DFh: DONE's "pop cx / push si / nop" between the
game's gear for the new character and its roster write) holding DONE for the Loader's `startgear.fill` on the
sequel's own items (ravlog's `RAV_PLAIN`, `RAV_LEATHER`, `RAV_CLOAK`, `_gear_pass`). Header fields at DSCLOG's
places: GEAR_DUE +1830, GEAR_GIVEN +1831, LOADER_BEAT +1865, GEAR_WHO +1867. DSCLOG2.EXE 43712 bytes.

**Set-up:** [files/2026-11-25-ravager-store-gear-start.sh](files/2026-11-25-ravager-store-gear-start.sh): `ravSG`, a
throwaway copy of `$WORK/rav` (deleted after), started as the Loader starts it (`RAV_LOADER=1`, `RAV_STDOUT=1`), the
dice log (`ravdice.py`), CREATE CHARACTERS, NEW on the first slot. Readings by the new `ravstore.py` (`roll`, `gear`)
and `ravitems.py`. The lock held throughout (15:44-15:50 UTC), one DOSBox. The build in place: DSCLOG2's segment in
memory matched the file over 42235 of 42923 bytes (the rest its variables), RS_CLICK's and GEAR_DONE's first 40
bytes the same. The window the sequel's 640x480. STDOUT.TXT empty in both runs (no "Illegal Op").

## A: the mod

**STORE and RECALL** (HookBoldt, a human fighter, slot 1). The two buttons under the hit points and PSP, left of
DONE ([picture](img/2026-11-25-ravager-store-gear-rolled.png)).

| Step | Scores | HP (sheet/creature) | PSP | most/least HP | RL_POOL | rs_have / stores / recalls |
|---|---|---|---|---|---|---|
| NEW | 19 16 17 18 19 16 | 71 / 71 | 33 | 91 / 28 | 105 | 0 / 0 / 0 |
| STORE (114,192) | the same | 71 / 71 | 33 | 91 / 28 | 105 | 1 / 1 / 0 |
| the die three times | 18 16 15 16 17 17 | 54 / 54 | 25 | 77 / 14 | 99 | 1 / 1 / 0 |
| RECALL (175,192) | 19 16 17 18 19 16 | 71 / 71 | 33 | 91 / 28 | 105 | 1 / 1 / 1 |

After RECALL the screen was drawn again from the stored roll: STR 19 ... CHR 16, SUM:105/105, 71/71, 33/33, AC 8,
DAM 2x1d1+7, THAC0 M11 R13 ([picture](img/2026-11-25-ravager-store-gear-recall.png)). Then FIGHTER off and GLADIATOR
on: the stored roll forgotten at the first click (rs_have 0), and RECALL did nothing (recalls still 1); FIGHTER again.

**Fuller starting gear**, each DONE held for the Loader (gear_holds 1 to 4, gear_timeouts 0, GEAR_DUE 0 after):

| Character | The game's gear | The Loader's (dice log) |
|---|---|---|
| HookBoldt, fighter | bone arm, chest, leg armour (types 4, 33, 65), a +1 shield (91) in slot 3, a +1 metal long sword (97) in slot 10 | `starts with more gear: Sling` (type 93, the missile slot 2) |
| Balthbeorn, thief | leather chest (32), a +1 long sword in slot 3, an obsidian dagger in the pack, a sling | `Armor, Armor` (leather arms 3, legs 64) |
| Kornec, fire cleric (made with the dice log before the hands fix) | leather, the +1 shield in slot 3, a wooden club in the pack (a fire cleric can't use it) | `Chatchka` (no sling for a fire cleric); at the next DONE `Dagger (in hand)` |
| Lanthazar, fire cleric | the same | `Dagger (in hand), Chatchka`: the obsidian dagger in slot 10, DAM 1x1d4+1 ([picture](img/2026-11-25-ravager-store-gear-cleric.png)) |

View Character's first drawing after DONE already showed the sling (HookBoldt) and the dagger (Lanthazar): the hold
makes SL's GEAR_WAIT redraw unneeded.

**Found while playing:** the sequel's armour types come in fives by place: 1-5 worn on the arms (slot 0), 30-34 on
the chest (9), 62-66 on the legs (6); its leather is "Armor" (32, 3, 64). An item's name number is its line in
RESOURCE.GFF's TEXT 1000 counted from 1 (type 91, first taken for a cloak, is the Shield; the cloak is type 28,
object 1615). The sequel gives a new fighter its shield in slot 3 and its weapon in slot 10 (SL's right hand is 3):
so startgear's hand is now either (`HANDS`, the sequel's both), the first free one while no melee weapon is in
either. Every New member is fitted at a DONE (Kornec's dagger came with Lanthazar's), as in SL.

## B: the control (`RAV_SKIP=roll_store,gear_done`, the dice log on)

STORE, the die twice, RECALL: the roll stayed the last one (scores 17 17 19 17 17 15, 97/97 HP), DSCLOG2's counters
0. A fighter's DONE: the game's gear alone (no sling), gear_holds 0. A fire cleric: leather, the shield, the club in
the pack and nothing in hand, DAM 1x1d1+1 ([picture](img/2026-11-25-ravager-store-gear-control.png)).

## Not done

- The roster's copy not read back (an ADD in a later session): GEAR_DONE waits before DONE's roster write
  (6E4D6h), so it should hold the gear, as SL's GEAR_HOLD.
- No bow and arrows for a Battle Dancer (a sling), no short sword (the sequel has none of its own), no
  multiclass preserver played (its armour left behind is SL's code on the sequel's items).
- A DONE with the Loader gone (no hold: LOADER_BEAT older than five seconds) not played.
- No watchdog (guard.sh is Shattered Lands'): DOSBox checked by pid.

**Water:** none (the creation screen only).
