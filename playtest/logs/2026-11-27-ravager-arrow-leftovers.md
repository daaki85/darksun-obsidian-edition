# 2026-11-27: the spell arrows' leftovers in Wake of the Ravager

**Under test:** branch `claude/ravager-arrow-leftovers` (on claude/ravager-spell-arrows): a new Spellarcher's
starting spell arrows (`ravarrows.starting_arrows` from `ravkitstart.fine_bow`), spell arrows kept from the other
members (`ravarrows.return_strays`, RavDiceLog._strays_pass), the dice log's names for the Loader's own items
(`RavGameData.item_name`), and the pointer's light on the buttons beside Turn Undead's (`ravager.PATCHES`
arrows_lit_on, arrows_lit_off: the program's own bytes). **No DSCLOG2 change** (0 bytes added: the helper is at its
one-segment limit).

**Set-up:** `ravAL`, a throwaway copy of `$WORK/rav` (game.gog hard-linked, the rest copied, the roster and DARKSAVE
from __support/save, no saves): `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh
/tmp/playtest/ravAL`, the dice log `RAV=/tmp/playtest/ravAL RAV_NO_SAVES=1 ravdice.py 7000 /tmp/playtest/al-dice.txt
--numbers` (quick saves and autosaves off). The DOSBox lock held by this session's holder throughout; the watchdog on.

## Steps

1. **A new Spellarcher.** CREATE CHARACTERS (160,92), the first slot's right-click (70,56), NEW (110,57); the big
   portrait (40,60) six times (race 4, a male half-elf), PRESERVER (255,45), KITS (234,138), NO KIT (250,106),
   SPELLARCH (250,114): `ravkits.py page` race 4, classes [3, 5], kit byte 0x01. Named Magramar (the default).
   DONE (272,182); CHOOSE A SPELL: Chill Touch (170,71) and Shocking Grasp (189,91), EXIT (205,147), YOU HAVEN'T
   CHOSEN's EXIT (112,92); the powers' EXIT (201,140), YOU HAVE MORE's EXIT (112,92); the weapon window: the bow
   (109,100). The dice log:
   ```
   Magramar starts with a bow for the weapon specialization chosen
       Magramar has +1 arrows with it
   Magramar's Shield is left behind: a Spellarcher fights without a shield
   Magramar's Ring Armor is left behind: a Spellarcher wears no armour   (x3)
   Magramar starts with a Fine Bow (+1 to hit): a Spellarcher's
   Magramar starts with 24 chill arrows in the quiver: Chill Touch picked
   Magramar starts with 24 shocking arrows in the pack: Shocking Grasp picked
   ```
   **The known spells are already in the member's bitset at DONE** (selector 320h), so the picks are read there.
   The VIEW CHARACTER screen showed the bow and the chill arrows' picture in the missile slots.
2. **The party.** Empty slot 2 (120,54) right-click, ADD (160,66); the ADD list: Clk'whrr (row y 57), ADD (253,46);
   slot 3 (65,117) right-click, ADD (107,129), Zontorra (y 78); slot 4 (120,117), ADD (193,129), Borzak (y 89).
   The bottom bar's right-hand icon (266,171), S, the narrated opening (80 s), 3 and Return x4.
3. **The ambush** with HP 250 for the four (a test edit, never saved: the #223 script) and Computer Control (C, the
   lower small icons at 47,53 / 98,53 / 47,113 / 98,113; Escape with the USE screen up).
   Won by the others (Magramar under Computer Control took up the Obsidian Dragonsbane +4 the new character's
   pack held and fought in melee). Out of it, Return through the level-ups, Zontorra's weapon window: EXIT
   (230,175), YOU HAVE MORE's EXIT (112,92).
4. **The light on the pointer.** USE (23,18), Magramar (70,56): CHILL ARROWS (157,147) and SHOCKING ARROWS
   (176,147). The pointer on the second lit **the second** (its yellow frame), the first left plain; on the first,
   the first alone; off them, neither ([the three](img/2026-11-27-ravager-arrow-leftovers-hover.png), top to
   bottom). In #223's play the pointer on a button lit Turn Undead's place (the first) too.
5. **A full stack.** CHILL ARROWS pressed with 24 in the quiver: the screen closed and the dialogue window said
   "Magramar's chill arrows are a full stack (24)." ([the screen](img/2026-11-27-ravager-arrow-leftovers-full.png));
   WIZ 4/4 after (no slot used). Its PRESS CONTINUE wants a click on Continue (22,157): Return didn't shut it.
6. **Strays.** The inventory (USE's bottom row, the second icon, 75,171), Magramar (25,25): the shocking arrows
   picked up from the first backpack cell (195,27), dropped on Clk'whrr's portrait (25,75), put in his first
   pack cell (195,27). With the inventory up nothing moved (`ravitems.py 1`: item 4, slot 14, Clk'whrr's). Escape:
   > The shocking arrows go back to Magramar from Clk'whrr: only a Spellarcher carries them (24)

   (`ravitems.py`: a copy, item 213, in Magramar's pack; none with Clk'whrr.)
7. **Vampiric arrows made.** Vampiric Touch (38) made known (a test edit, never saved: the bit in selector 320h's
   bitset, [the script](files/2026-11-27-ravager-arrow-leftovers-know38.py) `--write`): a third button, VAMPIRIC ARROWS (195,147); pressed:
   > Magramar makes one of the vampiric arrows in the pack (1 of 24 now): a 3rd-level slot used; it casts Vampiric
   > Touch on what it hits, at Magramar's preserver level, and lasts until shot
8. **Shooting** (the thieves' fight after the first ambush: Magramar never shot; DOSBox restarted on the same
   copy, the roster's four ADDed again, a second ambush won, the thieves' street). Shocking arrows in the quiver
   (a test edit of the two stacks' slots: [the script](files/2026-11-27-ravager-arrow-leftovers-quiver.py) `2 3`), the bow +15 (`ravitems.py 0 --bow15`), the melee weapons given to
   Borzak in the inventory (else Computer Control takes them up), Computer Control on for Magramar. The dice log:
   ```
   Magramar attacks Thief#17 with Wooden Fine Bow +15 (1d8+15): d20 = 5, hits on anything but a 1 (95%) ... -> HIT
     Magramar hits Thief#17 for 21: 1d8 = [2] +16 weapon +3 mastery
   Shocking Grasp damage: 1d8 = [3] +6 = 9 (1d8 + 1 for each caster level: 6 at caster level 6)
   ```
   **"Wooden Fine Bow", not "Wooden item 305"**, and Tab's line "Fine Bow +15 hits on anything but a 1". Seven of
   eight shots hit, each casting Shocking Grasp at caster level 6 (24 to 17). A swap of the stacks in the quiver
   between two of its attacks (the vampiric arrow in) didn't take: the next shot was still a shocking arrow, and the
   fight ended. **The Vampiric Arrow wasn't shot**: no other fight was found in reach (the townspeople made hostile
   in memory walked off; the sword pointer barred on them).
9. Not tried this play: a control run with `RAV_SKIP=arrows_lit_on,arrows_lit_off` (#223's play saw the fault).

## What was learned

- At DONE a new character's known wizard spells are already in its party slot's bitset (selector 320h): the
  starting arrows read the picks there.
- The new Spellarcher's pack holds an Obsidian Dragonsbane +4 (item 206) and its left hand a Longsword +1;
  Computer Control equips and swings them rather than shoot. Hand them to another member to have it shoot.
- With a foe beside it a party member attacks with its bare hands though a bow is readied; **Tab and Enter
  also walked up and punched**, at range too. Computer Control shoots (no melee weapon carried).
- The game picks a shot's arrows before the round: a stack moved into the quiver between its attacks waits.
- A PRESS CONTINUE window after a refusal shuts with a click on Continue (22,157), not Return.
- The thieves leave the map after their fight (none of their records stays), so a second shot test needs a new
  game: the roster keeps the new character with its starting arrows; ADD the four again.

## Water

No new area.

## Clean-up

DOSBox, the dice log, the watchdog and the lock's holder stopped by pid (another agent's flock was waiting and
took the lock); `ravAL` thrown away (game.gog's link count back to 7); nothing written into `rav` or `ravK`; nothing
saved (quick saves and autosaves off, no save made).
