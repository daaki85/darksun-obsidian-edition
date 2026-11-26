# Test log: Wake of the Ravager's own party fitted to the rules (2026-11-26)

Under test (branch `claude/ravager-own-party`, on `claude/ravager-high-level-kits`): defaultparty.rav_ready
(RavDiceLog's _party_pass), kits.own_features, DSCLOG2's OWN_RACE_B / OWN_DRUID (KIT_AC), OWN_LIGHT
(CAST_ARMOUR), SLOT_BEHIND / BEHIND_LEAST (ADND_SLOTS). The owner's choices of 2026-11-26.

## The play

`files/2026-11-26-ravager-high-levels-start.sh` (HL_TAG=-own) on a fresh throwaway copy, no edits. Within
seconds of the dice log attaching:

```
Ar'Anda is an Elven Shadow-walker who casts in light armour.
Terrannus specializes in the long sword.
Terrannus is a Crusader, his cleric's spell slots a level behind (not one fewer).
Thy'rokh specializes in the gythka.
Thy'rokh has a Grove Warden's AC: 1 better for every 3 druid levels.
Gerakis specializes in the long sword and the gythka and the trikal.
Gerakis fights wild: Wild Fighting, as a fight starts.
Gerakis fights wild: d20 = 3, needs 18 or less (CON 22 -4) -> 1 more attack a round and +3 damage, ...
```

`ravspecs.py`: kit bytes 0x40, 0x43 (Crusader + OWN_BIT), 0x40, 0x40; the specs as above. The Ambush fight:
DSCLOG2's `kit_acs` 12 (Thy'rokh's AC, Gerakis fighting wild).

| Ar'Anda (leather armour) | Seen |
|---|---|
| her feature on | USE: her spells plain; Armor cast ("Armor has 14 charges") |
| control: kit byte 0x80 (no OWN_BIT; a 0 is given back by the Loader at once) | USE: every spell crossed out, **NO SPELLS IN ARMOUR** |

Screenshots: `2026-11-26-ravager-own-arAnda-casts-in-leather.png`, `...-control-no-spells.png` (the project's
`ravager/` folder).

**What a play needs to know**: the Loader gives the own party's features back whenever it finds a kit byte of
0 or FFh on one of them, so a control clears OWN_BIT with another value (80h, Friends known). Escape on the map
with no screen up brings EXIT GAME (CANCEL at ravclick.py 145 117).

## Gaps

- Terrannus's slots a level behind not seen in play (they're counted at a rest; `sb_count` stayed 0 in the
  fight): the emulated tests run SLOT_BEHIND and BEHIND_LEAST against kits.slot_level and kits.slots.
- Thy'rokh's AC read only by the helper's count, not on View Character.
