# 2026-11-28: the sequel's last quality-of-life rows played by hand

**Under test:** `obsidian-edition` at 9e333d74 (PR #311 merged: the saves worked out again at each load,
no save under 2, the tail-read check). DSCLOG2.EXE the repository's (`buildcheck`).

**Set-up:** throwaway copies of `$WORK/rav` with the Loader's files (`ravager-after-ambush` loaded for the
town rows; `RAV_LOADER=1 RAV_MENU=1 ravstart.sh` and NEW for the creation screen). The DOSBox lock held
throughout; one DOSBox. Nothing saved after a memory edit.

## The saves at a load

The `ravager-after-ambush` party's saves were the game's own old table's; at the load the dice log said
whose changed ("...'s saving throws worked out again: ..."), and a read of the four sheets against
`savemend.routine_saves` then gave the same numbers for all four. Shattered Lands' `pens-after-arena`:
no line, all the same already.

## The rows

| Row | Seen | Picture |
|---|---|---|
| Shine in shops | Notaku's dagger and staff: their pixels cycling | [shop](img/2026-11-28-ravager-shop-shine.png) |
| Dialogue and dice log tabs | Notaku's talk in the Dialogue tab; the dice log tab attached | |
| Saves under their names | sync made "Page 1 slot 02 - notaku check" | |
| Look box | Notaku: HP 27/27 AC 2 THAC0 18 AL TN (no monster looked at, so no defences line) | |
| F10 | Move 10 back to 12, the figure where it started | |
| Miss labels | MISS over the foe in the alley fight | [labels](img/2026-11-28-ravager-miss-labels.png) |
| Dust | puffs behind a walker on a dirt floor | [dust](img/2026-11-28-ravager-dust.png) |
| Creation screen | THAC0 (M11 R11), SUM 97/97, AGE, the HP and PSP lines; the ability labels white (the sequel's own colour: CR_LABELS not needed); STORE, the die (SUM 103), RECALL: 19/19/15/15/15/14 back; KITS opens NO KIT, MYRMIDON, SENTINEL, RAVAGER | [creation](img/2026-11-28-ravager-creation.png) |
| Scroll text kept | already played ([2026-11-25](2026-11-25-ravager-shops-scrolls.md)) | |

**Not seen here:** the spell name label (the one cast was from USE out of a fight); the combat log panel's
scrollbar and wheel (the wider window, and the wheel is Windows only); see-through figures; the manual
check (its GPL 331 fix wasn't reached in play).

## Learned

- **KITS shows for the first look after NEW only if the dice log was attached before NEW**: it sets
  DSCLOG2's rules (kits are the second word). Attached after (as `ravcreation.py` does), the panel shows the
  game's VIEW SPHERES, which does nothing for a fighter; take the class off and on again and KITS comes.
  A test-setup thing, not a bug: the Loader attaches before the game starts.
- The sequel's USE screen read "PRI 7/5" unchanged after a cast while the casts left went 7 to 6: not
  followed up (it may be the level's slots, not what's left).

Water: none new.
