# Research recipes: Wake of the Ravager

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
Setting up, starting and driving the sequel, its rules as the port found them, and its dice log. The rest
of the sequel's notes: [its pictures, screens, fights and items](RESEARCH-RAVAGER-SCREENS.md), [its
records, the transfer, kits, saves and gear](RESEARCH-RAVAGER-RECORDS.md), and [the port audit's notes
and its spells in a fight](RESEARCH-RAVAGER-AUDIT.md).

## Wake of the Ravager

For comparing (its code, data and README; nothing in the kit plays it): `sh setup_ravager.sh` puts
the user's GOG installer (from the private repository, as the game's: the guide's [rule
10](PLAYTESTING.md#1-the-rules), or put at `$WORK/dl/rav.exe`) into `$WORK/rav`. Its DSUN.EXE is
laid out otherwise:
the creature/sheet records 42h bytes at the far pointer DS:19C5h, a class's level at +1Eh, its class
at +1Bh; the XP table is RESOURCE.GFF's DATA 1000 (8 rows of 20 words, in hundreds, looked up by
`lcall 5C8:20` with 3E8h); much of the code is in overlays, so a far call's segment isn't a place in
the file. Its level-up (95860h on) caps XP at the table's entry 3 levels past each class's own, then
raises a class under 15 (2026-11-08: no race limits, whatever its README says).

**Playing it in DOSBox** (2026-11-19, logs/2026-11-19-ravager-memory.md): GOG's settings are in
`__support/app/dosbox_darksun2.conf` (memsize 16, cycles fixed 15000, XMS, EMS and upper memory
on); it runs as `DSUN -W0 -L` (RAVAGER.BAT) from its folder as C:, with `CHARSAVE.GFF` and
`DARKSAVE.GFF` copied in from `__support/save` as SL's are. The CD is D:: Linux's DOSBox 0.74 can't
take GOG's `game.ins` (its music tracks are .ogg files), so mount a cue of the data track alone
(`FILE "game.gog" BINARY` / `TRACK 01 MODE2/2352` / `INDEX 01 00:00:00`) with `imgmount d data.cue
-t iso`; the music is then silent, nothing else missing. Shift held a second skips the intro (the
menu at 6 s). Its window is 640x480 (SVGA). **The first click only captures the mouse**: click once
anywhere harmless, then `xdotool mousemove_relative`, checking with a grab (START GAME at window
310,170). START GAME, the narrated cinematic (about 60 s, no skip), then Tyr: "Hurry! You must
come with me to the Veiled Alliance!" over the map. It runs with `ems=false` and `UMBPLUS.COM` too.
**`dosmem.py [PID]`** reads the memory of any DOSBox (no helper needed): both MCB chains, the
program's far heap (load + 0FE7h in SL, **+ 135Bh** in WotR) and DOS memory after it.

**The Loader's way** (the port, `dsloader/ravager.py`): `RAV_LOADER=1 sh ravstart.sh FOLDER` makes the
Loader's copies (DSUNLOG2.EXE, RESOURC2.GFF in the mod's dos folder) and starts DSUNLOG2.EXE from D:
(the mod's folder) with the game as C: and the CD as **F:**: the game finds its CD through MSCDEX
whatever its letter (2026-11-19: to Tyr with the CD on F:, as on D:). The copy reads its data from the
current folder (C:) by its "path" patch (DS:44F2h, SL's 4B81h).

**Driving it** (2026-11-19, logs/2026-11-19-ravager-fixes-2.md): `sh ravstart.sh [FOLDER]` starts
it to Tyr with no mouse (Shift twice, **S** on the menu is START GAME, 80 s). The game is 320x200
shown at 640x480: **game y = window y / 2.4**. Its pointer is DS:A109h (x) and A10Bh (y) (SL's
A133h); `python3 ravclick.py X Y [left|right|none]` moves there and presses slowly (0.3 s). The USE
screen (the top-left icon, 22,17) acts for the leader out of a fight (a portrait click doesn't
change who); the small top button left of a portrait is MAKE <NAME> LEADER (47,43 the first);
hovering names a button in the bar below; VIEW CHARACTER 47,171, VIEW INVENTORY 74,171, LEVEL
197,171. Out of a fight the keys **U** (USE) and **I** (the inventory) open them straight (2026-11-27), and the top-left icon
opens the screen last used; a click on an inventory slot takes up its item (AC changes when it is armour): click the
same slot again to put it back (logs/2026-11-27-ravager-sl-interface.md). The opening party: Ar'anda (elf preserver/psionicist/thief 6/6/7), an earth cleric 7,
Thy'rokh (thri-kreen fighter/druid, the leader), a half-giant gladiator 7; its sheets at the far
pointer DS:19C5h. **Running one of its routines on the live game** (`ravthief.py`, the thief
skills): most of its code is in overlays swapped out to XMS, so lay every overlay above A0000h from
Dark Sun Recompiled's `build_image.py` (its PSP set to the live one) with that image's stubs, the
live memory below; and give the emulator SS = DS (Borland reads stack buffers through DS).

**Running a routine through the helper** (2026-11-22, logs/2026-11-22-ravager-class-restrictions.md): an
overlay routine the Loader has patched with INT F5h (DSCLOG2's sites) can't run in the emulator as above,
which stops at an INT and lays the overlays over C0000h-FFFFFh, where DSCLOG2's upper memory block is
(CA1Bh:0 in that run). `ravthief.py --helper` shows the way: patch the site's bytes in the emulator's
copy, copy DSCLOG2's segment (the INT F5h vector's) to A01Bh:0 (A0000h-BFFFFh is free in the image) and
point the vector there, and dispatch every INT as real mode does (FLAGS, CS, IP pushed; CS:IP from the
vector table). **Moving items on the inventory screen**: a click on an item picks it up (the backpack's
cells light where it may go), a click on a slot puts it down ("CANNOT USE THIS ITEM", "ILLEGAL
PLACEMENT", "NEED TWO FREE HANDS", "THRIKREEN CAN'T USE" leave it on the pointer); a click on another
portrait shows that character with the item still held, so it can be carried across. Window to game:
x / 2, y / 2.4 (Ar'anda's right hand game 65,92, the left 172,92, the legs 172,127, the backpack's first
cells 195,27 and 207,27; the portraits 25 by 25, 69, 117, 165).

**Forcing a case in a fight** (2026-11-22): an edit of the game's own overlay code in memory doesn't hold:
the fight's overlays are reloaded from XMS several times a round, each time at another address (the
attack set-up was found at 5B865h, 5C215h, 5E445h, 5F3D5h and 60025h within one fight), so a loop
re-patching it every 50 ms still missed most attacks. Edit DSCLOG2's own code instead (it stays put in
its upper memory block, its segment the INT F5h vector's; offsets from `nasm -l`): for the backstab test
MISSILE_REAR's first 25 bytes (914h, the class restrictions' version) became `or si,si / jnz .out / mov
byte [bp-19h],1 / mov byte [bp-21h],1 / sub word [bp-1Eh],4` and NOPs, so every attack of the first
member is from behind and a backstab, as the game makes one. **Tyr's thieves for a fight**: from
`ravager-after-ambush`, the arrow keys Up 8 and Right 40 (world 1839, 1224), answer 2 ("Run along now,
pip"), Space: two thieves and two thugs; Computer Control for all four on the USE screen in the fight
(the lower small icon by each box, game 47,52 / 100,52 / 47,112 / 100,112), Escape to close it.

**Items saving against acid in the sequel** (2026-11-22, logs/2026-11-22-ravager-item-saves.md): the acid checks
(7CEC0h the weapon, 7D02Ah the armour) are reached only from the power handler's switch (656ECh, the power at
[BP+0Eh], 81 cases at CS:28C1h): Crystal Brittle 103 and the monster powers 275, 283, 284. To play one,
`ravknow.py 103 18` and cast it from USE (level 9) on a foe; the armour loop takes only the worn slots 0, 6
and 9, and Tyr's street thieves had their armour in slots 14-16 at the fight's start (`ravitems.py N
--worn` moves it). A foe under the spell's pointer shows red; `ravclick.py` takes 320x200 game pixels, and
a foe was taken about (8, 5) off its `ravfight.py state` place. A rule-off control records nothing in
the helper: read the dice log's plain d20 and the items gone (`ravitems.py`). Casting the last of a
level's slots shows "ZERO LEVEL 9 SPELLS TO CAST": write the slots again and press LEVEL round.

**Weapon specialization in the sequel** (2026-11-24, logs/2026-11-24-ravager-specialize.md): the weapon attack routine (5CE80h, SL's 58780h) has SL's frame with its locals two lower: the attacks a round in halves `[BP-0Ah]` (stored at 5CEE8h from the sheet's +24h in melee, the type's +7 for a missile), the damage dice `[BP-10h]` (type +9), sides `[BP-12h]` (+8), bonus `[BP-14h]` (+0Ah; the item's plus +16h added unless an Enlarge-like effect 4 is on either side, then the strength bonus, 98h:42Bh, at 5CF6Dh); `[BP+0Ah]` the THAC0 the d20 is held against (less `[BP+0Ch]`), `[BP+10h]` the sheet, `[BP+12h]` the item, `[BP+14h]` the type, `[BP+16h]` above 1 a missile. After the store the game doubles the halves for a status 4, halves them for 1, a ninth for 7 (628h:5Ch), then (the round's parity + halves) / 2, and cuts a shot's attacks to the ammunition left (5D007h-5D046h: "Out of ammo"). The sequel gives every warrior 3 halves (sheet +24h) as SL does. **A specialist's line in the dice log** reads "THAC0 19 base, +3 in bonuses, +1 specialized = 15" (the sequel's set-up frame isn't SL's, so the bonuses aren't itemized) and "1d6 = [3] +1 weapon +2 specialized +4 STR 18". DSCLOG2's `spec_hits`, `spec_damages`, `spec_rates` count what it did (scratch `spcount.py`: the symbols from `nasm`, the helper found by its `DSCLOGR1` header). **The transferred party in Tyr's ambush** under Computer Control: give the four HP 250 and base AC -10 in memory (48h sheets: `sheet * 48h + 21h`; never saved) so the fight lasts 30 rounds or more; put an archer's melee weapon in the pack (an item's +13h 14) to have the AI shoot, though it may take it up again. **"Illegal Op (gpl=49)"**: 9 of 14 of those fights (ravG48's 48h party: 5 of 9 with the rule on, 4 of 5 with it off) end with the game quitting so (`RAV_STDOUT=1` shows it, `RAV_MARK=1` writes ENDED.TXT), mostly at Ester's turn; not yet looked into. **Another agent's dice log** attached to this DOSBox (a Loader test of its own) wrote its rules word into DSCLOG2's header: a run whose `rules` (header +170) isn't the Loader's is void (`spcount.py` prints it).

**The lotulis', double spear's and trikal's traits in the sequel** (2026-11-26, logs/2026-11-26-ravager-weapon-traits.md): the attack's set-up (5C5E1h) takes `[BP+0Eh]`, its caller's distance to the target (the computer's at 5C0D7h, from the distance routine 1D40:35EFh), and passes it on as the hit routine's `[BP+16h]`: **above 1 is a shot** (5C77Dh: the set-up's missile way, the type's range +6 held against it at 5C8A9h). So a melee weapon of range 2 (the sequel's Double Spear 39, alone among the weapons; type 22's +6 is 2 too) swung from 2 squares took the type's +7 halves (the double spear's 2: one a round), DEX to hit, no STR damage, and the computer (5BDC2h: its target's distance against the weapon's range) swung it from there; the DAM lines (7B0B4h: "cmp byte es:[bx+6],1 / ja") show such a type as a missile weapon. The hit routine's frame: `[BP+0Ch]` the target's AC (the set-up's `[BP-6]`, from the AC routine 5D520h: target, attacker, the behind flag `[BP+20h]`, a far routine called "push cs / call near" at 5C9A7h), `[BP+0Eh]` the attacker's creature, `[BP+18h]` its combatant, `[BP+1Eh]`/`[BP+20h]` the backstab and behind flags. The swing loop's "cmp ax,[bp-0Ah]" (5D308h, after "inc [bp-16h]") is passed by every swing and once before the first (SL's AMMO_TURN site). A creature's +15h is its group: the game's friends by the bit mask 71h, its foes F80h (23838h); +14h 1 Okay, 3 out cold. An overlay routine called from DSCLOG2 by its address (the INT's way back's CS, its IP + the distance) needs the INT's way back in a BP frame below it, as the stinkpots' far calls do, for the overlay manager to fix up. The game keeps a combatant's hand weapons in a copy of its own: moving the off-hand weapon to a pack slot in the sheet (a test edit) left its off-hand swing in place (2026-11-27), so for a test of one weapon alone, put the other in the pack from the inventory screen before the fight.

**An archer for a test, and the quiver's last arrow** (2026-11-28, logs/2026-11-28-ravager-engine-fixes.md): make the edit **before** the fight starts: a fight sets each combatant's ready weapon as it begins, so a bow given mid-fight is swung as a melee weapon (1d1 + STR) and the pointer stays the sword. Before the thieves' fight on the way to the Harbinger's Roost (`ravager-after-ambush`, `ravgo.py` to about 1841,1253, answer 2, Space), Gerakis's long sword (his item 13) made a bow (type 18, +13h slot 2) and his left-hand item (14) one arrow (type 6, slot 1, +2h count 1). With a bow ready the right-click cycle is walk arrow, bow, talk; with no arrows left it is walk arrow, a barred bow, a barred talk. DSCLOG2's `ammo_out` (sym in the build) holds the archer whose round was cut, -1 when none.

**The creatures' own scripts, the creation screen's least and the attack's speed** (2026-11-28, logs/2026-11-28-ravager-engine-fixes-2.md): the table of creatures' own scripts (SL's 3972:08AAh, stuckwalk.py) is at the load + 3F49h:08A7h, 13h bytes an object as SL's (the walk order 15 stored at 1E194h); in Tyr's street objects 15 and 16 are pedestrians walking by script file 147 (`/tmp` scratch: the entry's order, +8 the file). The least each score may be at creation is the overlay routine 6F12Dh (SL's 67399h; the creation sheet's classes at +1Bh, the game's table 360h:153h); after a click on a score DS:42D4h holds the least for it. The attack's speed is 628h:5Ch (the stub at file 4C7A0h maps its entries: 5Ch to 85899h, 66h to 8599Eh, A7h to 83606h, 39h to 8527Bh): Paralyzed (69) 0, effect 66 5, effect 56 6, Slowed (91) or Impeded (50) 1, Hasted (42, 51) 4, Slowed (52) 1, else 2; the attack doubles for 4, halves for 1, and its "a ninth for 7" never comes. **A walk copied onto a creature freezes input**: giving object 17 in Tyr's street (a creature with no script of its own) object 15's entry of that table in memory (order 15, script file 147) stops every click and key reaching the game within a minute (the game's pointer, DS:A109h, stays put; game time goes on; the game itself takes the order back to 0), with or without the dice log, the same on the code before PR #315 (2026-11-28). A test of stuckwalk wants a real save made mid-walk instead (F5 with the dice log while the pedestrians walk, then that save loaded): no edit, no false reset, input fine.

**The sequel's own six weapon specs** (2026-11-25, logs/2026-11-25-ravager-new-specs.md): a spec for a test made in the
**Shattered Lands save** before the party transfer (`game.with_specs` on a copy's `SAVE 6` sheets, written back with
`icons.with_chunks`), then `python -m dsloader.ravtransfer SAVE COPY SL_FOLDER DOS_FOLDER`: the roster's 48h sheets
carry it (V3 at +42h..+44h). A weapon of a kind for a test: the held item's type word (+0Ah of its 17h record) made
the sequel's type in memory (never saved; the item keeps its name, so the dice log's "Obsidian Longsword (1d10)" is
the Twohand Sword's type), its left hand's item to the pack (+13h 14). The sequel's own types of SL's six kinds: the
Twohand Sword 101 and Crystal sword 35 (two-handed 1d10: the type's +0Bh 40h), Lotulis 61, Double Spear 39,
Trikal 100, Javelin 59, Darts 38 and 43 (the type's dice: count +9, sides +8). **A second sequel game** when the
shared DOSBox is busy: a copy of the kit with `:57` in env.sh, paths.py, ravclick.py, ravfight.py and ravstart.sh's
Xvfb line, `PLAYTEST_WORK` its own folder (rav.pid, rav.conf there) and a `dosbox` wrapper first in PATH that runs
a copy named `dbns`; a script testing `/proc/PID/comm` must then look for `dbns`, not `dosbox`.

**The sequel's screens: DAM lines, Effects, the Look box's close** (2026-11-25, logs/2026-11-25-ravager-screens.md): the inventory's DAM line routine is SL's at 7AF9Eh (its item DI, type SI, the creature far at `[BP-6]`, 0 in an item box): the melee branch reads the sheet's +24h at 7B19Eh, the missile branch the type's +7 at 7B124h, each then "mov ah,0" and the push for the line's routine (7B1D9h); the bonus, sides and count are pushed under it. View Character's line is at 6CA43h on (`[BP-6]` the attacks, `[BP-2]`/`[BP-4]` the dice, `[BP-0Ah]` the item, the bonus stored at 6CAC9h); it took Ester's left-hand weapon. The likeness search missed both (the sheet's and types' sizes differ): search for the sheet read (`26 8A 47 24`) instead. **The Effects screen**: the cells' routine 8AC6Fh (ends 8AFA9h, `[BP-4]` the cells used), the handler 8AB13h (its redraw "call 140:60Dh" at 8AC62h, way out 8AC6Ah); USE, then EFFECTS (122,171), the portraits at (70,56), (117,56), (70,127), (117,127), the lower panel's lines from (150,108). **The dialogue window**: its stub 476Ch (SL's 42CAh, entries 25h the input and 34h the wait), found by its callers' likeness (SL's 42CA:2Ah calls at 1BC2Ch/1BE74h, the sequel's 476C:2Ah at 1F063h/1F2D6h). **To see the Look box's description** a monster needs more than HP, AC and THAC0 to say: Draxans have no defences, so set their resistance class (the creature's +0Fh) to 2 in memory for a test (never saved). **A spec edit for a test** must write the packed SPEC_V2 form (the kinds base 17 in the low 17 bits of +42h..+44h): the Loader's age pass rewrites plain bytes there. The Effects screen's kit line needs RULE_HI_KITS (1) in DSCLOG2's rules_hi (header +270), which the Loader doesn't set until the kits' rules are ported. **The opening talk** of a new game with the transferred party runs into the Draxans' fight after three Continues (100,171); the screens open in the fight: the top-left icon (22,17), then VIEW INVENTORY (74,171); on the inventory its bar's first icon (170,187) is VIEW CHARACTER; on View Character and Effects the bar is (47,171) VIEW CHARACTER, (74,171) the inventory, (122,171) EFFECTS; the inventory's portraits at (25,25), (25,69), (25,117), (25,165).

**The new wizard spells' numbers** (2026-11-26, logs/2026-11-26-ravager-new-spells.md): DATA 0-319 are all the
sequel's (wizard 0-114, priest 115-234, psionic 235-268, MONS269-319); the known bitset's free bits 115-119 are priest
records' numbers. So the mod's six are 320-325 (`dsloader/ravspells.py`: DATA 320-325, ICON 21320-21325, SPIN 321-326
in RESOURC2.GFF; the game's own ICON stop at 21268, SPIN at 269), known by the sheet's +3Fh/+3Dh bits (as SL's). The
game never asks for them until DSCLOG2 does. The sequel's spell icons are PLNR or PLAN, and a few of its ICON and BMP
chunks are SL's kind; `sequelicons.decode` reads all three.

**Casting the new spells in the sequel** (2026-11-26, the same log, part 2): the spell handler's switch at 656D0h
(81 cases at CS:28C1h of the module from 642E0h; Strength 23 and Adrenalin Control F5h share 6623Bh, the effect in
`[BP-12h]`, its 1d6 pushed at 6624Eh, the adder at 65AFBh); the abilities routine 8527Bh (`[BP-9]` 0 under
Anti-Magic 4: no wizard or priest spell's effect), its effect switch at 85351h (9 cases at module 83400h + 2386h;
STR `[BP-348h]`, DEX `-346h` ... CHA `-33Eh`; out at 8543Bh); a natural attack's dice 86A45h (DX the attack, far
`[BP+0Eh]`/`[BP+12h]`/`[BP+16h]` count, sides, bonus); the effect records (31 bytes at the load + 3C870h) end
with 112, zeros after for 3169 bytes, and the creature's effect bits are 15 bytes (7FE93h: 0-119), so 113-116 are
free for data. The swing's `[BP+0Ah]` THAC0 holds for the call's swings (5D052h is each swing's start; the first
when `[BP-16h]` = `[BP-0Ch]`). In play: a spell dropped on a member's portrait on USE is cast on that member, a
drop on the list's panel brings the aim pointer up; the USE screen keeps its LEVEL between openings.

**Learning the new spells in the sequel** (2026-11-26, the same log, part 3): CHOOSE A SPELL's pick sets the bitset bit
at 936B4h (`mov es,ax / or es:[bx+39Ch],dl`, ES 370h before, the spell `[370h:7 + SI]`, the member `[370h:0B44h]`);
the page's list is words at 370h:7 (room for 20: 370h:2Fh is a dword of the game's). A spellbook's read (from the
item box's spell icon, outside a fight) is 999A9h on: `[BP-4]` the power - 1, objects 7918h-79DFh and 7AA8h-7B0Bh
(31000-31199, 31400-31499) learn, any other (a one-use scroll, 313xx) goes to the cast at 9B7Dh; the bit test from
999F8h, YOU LEARN THE SPELL at 99A5Ch (the book used up), YOU ALREADY KNOW THIS SPELL at 99A86h. An item's power is
the spell + 1, compared with 140h at 77CF9h, 9A7D4h and 9A9C5h. **The overlay manager fixes up segment words in
overlay code** (`mov ax,370h` at 999F8h, as `mov dx,338h` in least_scores): none of them is in the MZ relocation
table (`gamepatch.relocated` doesn't see them), so a site whose INT number or NOPs land on one runs another INT
(here: DS:4 and DS:4Ch written, the Borland signature broken, the Loader's `find_data_segment` then None). Put a site
after such a `mov` (999FBh). **The hit routine's frame**: NS_SWING's BP is the hit routine's; the set-up's locals
(the natural attacks' set `[BP-20h]`, which the dice log reads as the d20's parent) are at `[bp]`'s frame.
**A party member with nothing in hand** (a thri-kreen too) can't attack after a slot edit in memory alone (a
barred sword over a foe); moved to the pack on the inventory screen (pick the hand's item, click a pack square) the
foe turns red and a thri-kreen fights with its claws and bite (the inventory's DAM "<4x1D6+8>" with Erdlu Claw). A
spellbook for a test: `logs/files/2026-11-26-ravager-new-spells-scroll.py ITEM POWER 60` (the record of item 60, a
spellbook, over a carried item; the box's spell icon then teaches). A level up for CHOOSE A SPELL: the log's
`-levelup.sh`; creation's: `-create.sh` (a throwaway copy's roster).

**The sequel's first spells and powers** (2026-11-25, logs/2026-11-25-ravager-first-spells.md): the creation
screen's DONE (6E0B9h, 5C0:57h; SI the member) calls 6E6D8h, the powers (6E906h, 5C0:2Ah), a preserver's spells
(6EA10h, 5C0:2Fh), 6ED7Dh, then 98:0Fh, all from DONE only (no START GAME path as in SL). The wizard spells known
are a bitset (selector 320h, the load + 3D62h: 39Ch + 15 a member, bit n spell n; SPELL_STARTS at DS:0656h: 1st
level 0-11, 2nd 12-24, 3rd 25-38, 4th 39-55); the powers a byte each (selector 370h, the load + 3E71h: 9CDh + 22h a
member, bits 1-7 the number, 580:39h gives one as 2), the disciplines' bits A55h + the member; the pop-up's
discipline shown DS:9D7Bh + the member, its picks left DS:43ECh (CHOOSE A SPELL's page level too), its list DS:9C20h
(words, 0 the end). Selector 360h holds the screen's snapshot (+0 the preserver level at an EDIT's opening, the
spells given again only when it differs) and the powers' table (+6 three rows of 5, +15h the psionicist's 20). The
level up's windows take a member and run until closed: CHOOSE A SPELL 688:66h (93160h; one spell a call), the
psionicists' pop-up 688:61h (93B62h; its count from the psionicist level, closed at none); module 40's stub segment is
DS - 30h, module 15's DS - 103h. The overlay layout (modules, stubs, entries) from Dark Sun Recompiled's
`tools/build_image.py DSUN.EXE --out DIR` (its layout.json: a module's `record` x 8 is its selector). **SITE's way
back** is the byte after the site's number: for a 4-byte site the NOP, so a site that stands for a jump adds the
target less that address (one byte late, PSI_LIST jumped into an instruction: "Illegal Op (gpl=49)" on a click).
`ravfirst.py` reads it all. In the creation screen the pop-up's discipline button is (115,140), EXIT (202,140), its
icons from (121,62) 19 apart; CHOOSE A SPELL's icons five a row from (124,74), 19 by 17 apart, LEVEL (107,147), EXIT
(205,147); "YOU HAVEN'T CHOSEN"/"YOU HAVE MORE"'s EXIT (112,92).

**With STORE/RECALL and the starting gear** (2026-11-25, logs/2026-11-25-ravager-join-gear-spells.md): DONE's
windows (CHOOSE A SPELL, then the powers' pop-up, which every class gets: everyone has a discipline) all come before
GEAR_DONE (6E2F2h), so its hold for the Loader starts only once the last window is closed, however long they stay up
(gear_timeouts stays 0). CHOOSE A SPELL's LEVEL button does nothing while the level being picked is 1 (CR_CAP is that
level). A stored roll outlives NEW: it is forgotten only at the first button after a change of race, sex, classes
or kit, so a new character like the stored one could RECALL it (SL's DSCLOG the same). Making more than one: View
Character's bar's right icon (270,171) goes back to the title menu, then CREATE CHARACTERS again; a right-click on
slot 2 (117,56) puts its menu top right (NEW 160,57), on slot 3 (70,127) beside the slot (NEW 110,118). PSIONICIST
on the classes' list is (265,53).

**The level up, the XP table and the saves in the sequel** (2026-11-25, logs/2026-11-25-ravager-level-cap.md): the
level up (95820h on: SI the member, DI the class's place; `[BP+6]` nonzero levels without the XP) holds the
sheet's XP to the table's entry level + 3 (958AAh-95940h: "add ax,3" at 958BDh, the reads at 958E3h and
95931h), then reads entry level (9597Ah: the next level's XP) and at 959A5h holds the level below 15; it
loops on the same place while a level comes (95A85h "dec di"), a human only on place 0 (9587Fh). The XP
table is read only through 5C8:20 (6F640h: the resource DATA 3E8h loaded by 128:4ABh, the word at row x
40 + index x 2, let go by 1D0:92h each call): nothing stays in memory, so DSCLOG2 keeps its own copy
(RAV_XP_AT). Out of range it reads on into the next row (row 7, the thief's, past the resource). The
class-to-row map is 360h:9Dh (a word a class: 1-4 cleric 1, 5-8 druid 2, 9 fighter 3, 10 gladiator 4, 11
preserver 5, 12 psionicist 6, 13-16 ranger 7, 17 thief 8). View Character's next XP (6FB21h): its copy's
classes are rows, the least next XP at `[BP-6]`, "push 1383h" "(" and "push 1386h" ")" around it (6FBDFh,
6FC08h). Creation (6C3A4h-6C4E7h) puts a class at 6th or 7th (XP the most of their needs), then one
level more where the XP allows: 8th at most. **Hit dice**: the class-to-group bytes 4D0h:10h + class
(0 priest, 1 warrior, 2 wizard, 3 rogue: psionicist 12 and thief 17), the groups 4D0h:0 four bytes each
(die, levels rolled, fixed gain after, CON's most): (8,9,2), (10,9,3), (4,10,1), (6,9,2). **Saves**:
954D2h, the per-group levels from 953A9h (`[BP-0Ah]` + group x 2), the table 4D0h:6Ch + group x 15 + save x 3
(1st level's, a rate in hundredths, AD&D's last row), save = first - min((level - 1) x rate / 100, last); a
dwarf's or halfling's CON x 2 / 7 is added for the warrior group (it tests the group, CX, for 1 or 4: SL's
the same). **Spell slots**: 62A10h by a formula (DS:0670h + class: a nibble list of DS:0684h words: start
level, odd/even, most), a ranger's 3 2 1 at 12th, 3 2 2 at 13th, 3 3 2 at 14th, AD&D's 2 2 1, 3 2 1, 3 2 2
(ADND_SLOTS now gives the Handbook's). `ravlevel.py` shows the party's levels, XP, saves and the helper's
counts, and sets a member for a test. **Played** (2026-11-25, logs/2026-11-25-ravager-level-cap.md): without the fix the game's XP clamp reads
past the table's end for a class at 17th or more and sets the XP to 0; the saves are the least of each group's
(954D2h's loop); a fight's XP goes a third to each class of a triple class. On View Character a click on a
portrait at the Effects screen's spots (70,56) (117,56) (70,127) (117,127) shows that member; level-up messages
come one a click of the box (160,100), the dice log's "Message:" lines list them all. **Levels 21-30**
(2026-11-26, the same log): the game's XP table has 20 entries a class and its reads past them run on into
the next row; THAC0 (creature +16h) is read signed (`cbw` at 5C6E9h, 7CFF7h, 844B6h) and View Character
shows "THAC0: -9"; hit points take the group's fixed gain past its rolled levels (94FF2h); the level up's
message (959A5h on) pushes "th" (DS:2B7Eh) for every level past 3rd, and "%Fs gains a level" (DS:2B87h)
when the long one passes 29 characters (a preserver's "is 22nd level Preserver"). The wizard spells run
to a 10th level (DS:0656h's starts: 111-114 Dome of Invulnerability, Magical Plague, Rift, Wall of Ash),
and CHOOSE A SPELL opens on level / 2 from 10th, so a preserver's level up from 20th offers those first.
The psionicists' pop-up (688:61h; its picks 1, 2 at odd levels and at 4th, from 98:C1h's psionicist
level, root code at 1D111h) lists known powers too: a pick adds 2 to the power's byte (bits 1-7 its
number), so it never runs out. The slots left are set only by a rest (the Roost: `ravload.sh
ravager-roost`, Reyhan "1 3 4", the corridor, the second doorway's steps at game (262,93), Up 6, the look
pointer on the ring at (265,113); the pointer mode DS:1440h, 1 the arrow, 4 the sword, 2 the look). The
level up's hold (3 levels on) raises a class four levels an award at most. Without PICK_ANY the game's own CHOOSE A SPELL counts from the class level (a 22nd-level preserver's
window opened on "LEVEL 11", the priest spells' empty page, and no pick closed it); with it the page is
level / 2, now 9 at most (PICK_MOST). The THAC0 routine (9534Ch) runs PRIEST_THAC0's site for every
class group (CX 0-3), so a group's limit goes there.

**Stealth in the sequel** (2026-11-24, logs/2026-11-24-ravager-stealth.md): the attack's set-up (5C5E1h)
keeps the attacker's creature in `[BP-0Eh]` (records 31h bytes, its THAC0 at +16h, taken into `[BP-1Eh]`
at 5C6EEh each attack), the sheet in `[BP-12h]`, the weapon type in `[BP-4]`, the target-is-an-object
byte `[BP-1Ah]`, from behind `[BP-19h]` and backstab `[BP-21h]` (both cleared once a call, 5C5FEh, while
the loop back to 5C6DDh runs a round's attacks); melee is `[BP+0Eh]` 1 there and `[BP+16h]` 1 in the hit
routine (5D1D6h). Map objects' x, y at DS:67C5h, 25h apart. Each RGNxx.GFF names itself in an `RNME`
chunk (forest, Tyr, VA Headquarters, Pyramid, Yuan-ti Tunnels, El's Temple, Mines1-3, Jann, Mosaic,
Volcano Level 1-3, Silt Giants, Cloud, Crypt, Cosmos, UnderTyr, Limbo). The sequel's effect numbers
are not SL's (its 25 is Detect Invisible): map SL's tables by name (`ravlog.effect_names`).
`ravdice.py` with `RAV_STEALTH_ROLL=1` hides every thief and ranger who can. **DOSBox dying** in the
transferred party's Tyr fight (about half the runs): `ravstart.sh`'s `RAV_CORE=normal` (the CPU core)
and `RAV_NOEXIT=1` (DOSBox stays up if the game quits) ruled out the dynamic core and the game's own
exit; `strace -f -e trace=exit_group,kill,tgkill -p PID` on DOSBox to see how it ends.
**Thieves as in AD&D in the sequel** (2026-11-24, found statically, the sites run on the game's own bytes in
`tests/test_ravthief.py` with `DSUN_WOTR`; played 2026-11-25 on the kits branch, logs/2026-11-25-ravager-thieves.md,
where the two sites became 52 and 53 and STAB_TIMES gives an Assassin one more): the thief skill routine is 8C647h (SL's 8023Bh),
the same code with the sequel's frame: DEX in `[BP-2]` (SL's `[BP-0Ch]`), the skill a dword at `[BP+8]`,
the thief level in SI (580h:61h, class 11h), the tables at the game's segment 4A0h (file 49BB0h, load +
449Bh: the base at +skill, race R's row at 8 + 8R, the DEX limits A0h, A8h, B0h, the armour penalty B8h).
SL's `thief_skill` bytes are at 8C716h ("mov ax,si / shl ax,2 / add dx,ax / mov si,dx", DX base + race),
the game's DEX formula after them to 8C795h ("push di", its armour and effects): DSCLOG2's site 52
(THIEF_SKILL, then "jc" +7Ah) does SL's PROBE_THIEF_SKILL there, and BELT_SITE (8C7C5h) keeps the chance
to 95. The attack's hit routine (5CE80h, SL's 5883Ah) keeps the round's attacks so far in `[BP-16h]` (from
the creature's byte at selector 308h, +184h; SL's `[BP-14h]`), the damage roll's bonus in `[BP-14h]`; the
backstab multiply (SL's 58A80h) is 5D11Bh, the same 10 bytes, after the game's test (`[BP+1Eh]` and
`[BP+20h]` bytes, the attacks at most 1, 5D0F8h-5D112h) and the multiplier routine 5DE0Ch (SL's 595C4h,
the same: x2 to x5 by thief level). Enlarge (628h:57h) runs before it at 5D0D2h, so ENL_SITE's enlarged
dice are the ones multiplied. STAB_FIRST (from MISSILE_REAR) takes back a member's second backstab at the
same game clock (the far pointer at DS:9C0Ch, SL's 9B72h: the timer set-up at 2CB40h writes it). In a play: `ravdice.py` should show a thief's skill check as `"<name> tries to
open locks: d100 = N, needs C or less"` with the second line `open locks C = <AD&D's> thief level L + <race>
+ <DEX>` and no "equipment" part when nothing is worn in the hands, legs or quiver (the old game sum showed a
large "equipment" remainder), the inventory's skills the same numbers before equipment, and a backstab as
`"+M backstab (the dice D xT = D*T)"` with the damage the dice x T plus STR once (DSCLOG2's `stabs` counts
them). **Played** (2026-11-25): Seneca's inventory (USE, VIEW INVENTORY, her portrait at 25,69) is AD&D's
average + the sequel's race row + Dark Sun's DEX (the control, `RAV_RULES_OFF=0x100`, the game's sum); a hidden
backstab in the Draxans' ambush "1d4 = [4] +1 weapon +4 STR 18 +4 backstab (the dice 4 x2 = 8)", 13 HP off
(control "(1d4 = [2] +1 weapon +4 STR 18) x2 backstab", 14); a human thief 3 made an Assassin (`ravkits.py
set 1 2 1 17`: a halfling fighter/thief's only kit is the Poisoner) "+6 backstab (the dice 3 x3 = 9)", x2 with
the kits off (`kit_stabs` in `ravkits.py count`). With `RAV_STEALTH_ROLL=1` the CC AI hides Seneca every turn
but shoots her sling at range: half the runs end without a backstab. The dice log's hiding chance is the
Loader's (stealth.py, the table always), so it doesn't follow a thief-table control.

**Its fights in the Loader's dice log** (logs/2026-11-20-ravager-dicelog.md): `python3 ravdice.py SECONDS
[OUT]` runs dsloader.ravlog.RavDiceLog (SL's dice log on the sequel's layout, its memory read only) on the
running sequel. Addresses found for it: the combatants selector 388h at C33h (load + 3F49h), the
initiative selector 308h at DCh (load + 3C4Fh), the attack's target DS:4206h, the item types 15 bytes
(DS:19CDh), the item names RESOURCE.GFF's TEXT 1000 (a line a name, from 1), the rules' small tables SL's
+70h. A selector's segment: the segment table at load + 45E8h, + the selector. `ravds.py --fuzzy HEX`
maps an SL data address by the code round its uses.
The AC function is the sequel's own (5D520h; its end 5D6E6h, PROBE_AC). `ravdice.py --all` shows every
roll and each AC worked out. **To find an unnamed roll's code**: catch its entry (its frame's first words
are the return address, then the arguments: the dice routine's count and sides) and read the code at
that address at once, before the overlay moves, then find those bytes in DSUN.EXE.
**Playing it** (2026-11-20, logs/2026-11-20-ravager-dicelog.md; the walkthrough: `setup_guide.sh`, then
`$WORK/guide/ravager.txt`, the owner's copy from the private repository):
- **Attacking**: in a fight the **Walk pointer, the plain arrow**, clicked on a foe walks to it and attacks
  (the manual); the sword pointer shows a barred sword in a fight and does nothing. Right clicks on bare
  floor cycle arrow, sword, look: track the pointer by picture, not by count. A foe under the arrow turns
  red. In a crowd a click can take the wrong figure (`ravfight.py attack` aims at a figure's place + 10,
  22). `ravfight.py fight` attacks on every party turn; the ambush was lost that way (Gerakis never
  struck).
- **Computer Control**: the inventory screen (the top-left icon out of a fight; in a fight USE, then the
  second icon of its bottom row), the lower of the two small icons left of each character box (a small
  screen; lit orange when on; the upper one marks the character shown). All four on won the opening
  ambush by itself (3 Draxans, a templar) with the party standing. Once the inventory has been opened in a fight,
  the top-left icon brings it back (the menu keeps its last screen) and its lower icons may miss one
  (2026-11-25): **C** then the USE screen's lower small icons (47,53 / 98,53 / 47,112 / 98,112) is sure.
- **Sides**: creature +15h: 0 the party, 7 the opening's Draxans, 1 the town's people.
- **Saving**: the inventory's GAME MENU (game 267,187), the disk (136,100), SAVE (145,105), a slot
  (127,46), type the name, SAVE (252,47): SAVE01.SAV, CHARSAVE.GFF (DARKSAVE.GFF not rewritten).
  **Loading**: the title menu's LOAD SAVED GAME (159,110), the slot, LOAD (252,47): `ravload.sh NAME`
  (`saves/ravager-after-ambush`, the opening won). Escape with nothing up brings EXIT GAME? (QUIT /
  CANCEL at 145,116): a second Escape after closing a screen does it.
- **Walking**: the **arrow keys** (not the keypad's) walk the leader a step (16 px) a press and the view
  follows; clicks with the arrow walk too but only on screen, and are barred near its edges or on
  walls. Out of a fight only the leader is on the map (its object, 2 for Thy'rokh as leader); world
  pixels are screen pixels from the camera (DS:1408h). Inside a building with its roof cut away the
  leader can be hidden behind the roof's edge. The area map (game menu) shows a marker that doesn't
  follow the party.
- **Any region for a test** (2026-11-27, logs/2026-11-27-ravager-encounters.md): `ravjump.py REGION COL ROW`
  after `ravload.sh ravager-roost`, then the look on Reyhan (game 150,128). The script command 5Eh moves an
  object (7FFEh the party) to a region (255 Limbo) and square; GPL 4 is the doors' shared one. A save edited
  to another region (SAVE 18 and 45) only redraws the map under the old region's objects (SAVE 1); a map
  record's place is its +0Ah/+0Ch, +3/+5 its picture's corner. MAS N holds region N's triggers (6Ah: an
  area x, y, w, h, an offset, the GPL script; 65h/66h/6Fh: an object's look, talk and the like). Regions:
  0x42 the Cloud (air drakes at once), 0x3E Volcano 1 (fire drakes at once), 0x43 (the earth drake, object
  6541 at square 85, 13: after the jump the view stays the Roost's; the camera DS:1408h written and USE opened
  and closed redraws it, the rock rises as the earth drake, but a fight there hangs: the party isn't set up), 0x44 (the Tarrasque: the area 31-36, 46
  runs GPL 124, the cinematic and the fight).
  Region 1 (RGN001, Humbleton) square 20, 20 is inside Ptar's cave (where GPL 30 puts the party as it comes in), but the
  jump leaves the party half there (the leader stuck at the east wall, the view garbled) and the scene's triggers unset
  (Ptar's look, 857 of GPL 47, is set by GPL 30 only through the cave's exit). Jump instead to open ground beside
  the scene's exit area (MAS N's 6Ah areas, a GMAP 0 square) and walk in: `ravjump.py 1 73 86`, the camera set, Up into
  the mouth (73,83) and Yes brings the party whole into Ptar's cave (2026-11-28, logs/2026-11-28-ravager-script-fixes.md,
  files/2026-11-28-ravager-to-ptar.sh).
  The Forest jump can leave the camera behind. The overhead map opens with O, and moving the pointer to the edge scrolls the scenery. Check the room landmarks before treating a capture as evidence for a furniture placement.
- **A script probe** (2026-11-28): `ravprobe.py HEX` puts any commands in Reyhan's talk the way ravjump.py puts the
  move, then return and exit: the game's own interpreter runs them and `ravtext.py` reads back what they print. The
  ore voucher sale was checked that way (460 vouchers given with `39 ...`, the sale's commands copied from GPL 143).
  Both tools find the talk by the copy's GFF index (`ravjump.talk_at`): a copy whose scripts the Loader lengthened
  keeps the old chunks' bytes too, unindexed, so a search by the talk's bytes finds two (2026-11-28).
- **Mosaic museum** ([DOSBox playtest and captures](logs/2026-11-27-ravager-mosaic-museum.md)). Use `ravjump.py 0x3C 39 24` from the Roost fixture to reach the interactive rows. Row 13 lands across the wall. Look at the head of Horace or Ellith, dismiss the name, select the green hand and press 1 to remove the bust. Look picks the detached bust up. Click the empty stand to seat Horace, or open inventory with I and click a backpack slot to store Ellith. The sword breaks Khildril. Pick up the bookcase beside Fletch and set it elsewhere, then pick up the exposed book and click Biblid.
- **Completing the museum mirror** ([playtest](logs/2026-11-27-ravager-mosaic-mirror.md)). Square (40, 34) puts the party near the cloth, hand mirror and bag. Carry them in the backpack to the stands. Drop them on clear floor so Look can pick them up again, then click the appropriate bust with the item. Once the busts match, pick up each of the eight shards and click the wall mirror. After the eighth, walk north through the repaired glass to the Veiled Alliance.
- **Mines shelves and Yuan-ti storeroom.** In Mines 3, use the Bookcase at (35, 71) in sector 10 for the orbs or (93, 11) in sector 4 for the chemicals. In the northeast tunnel storeroom, flags 118 and 119 together open the eastern camera bound for a jump to (115, 6). [Room fixtures and stock controls](logs/2026-11-27-ravager-mine-and-tunnel-shelves.md)
- **Mines 3 kitchen and chests.** From (72, 91) in sector 2, inspect the small poison box and use each of the three larger crates. The chef’s key opens the chest at (48, 86). The armor chest is by the lava pool at (10, 7) in sector 12. [Stock and revised visits](logs/2026-11-27-ravager-mine-kitchen-and-chests.md)
- **Side-facing counters.** Four of the 12 placements of 3485/3486 have bit 80h set in their ETAB flags. Flip the drawing horizontally within its existing canvas when comparing to a native capture. The other eight use the stored orientation. [Placements, travel squares and silver seat joins](logs/2026-11-27-ravager-silver-furniture.md)
- **Forest fruit and sickbeds.** The broad Plant offers acorns and the narrow Plant offers grapes. To replay Cleave’s cure, use square (52, 10), pick up the filled Hero Flask from clear ground and click his occupied bed. The game awards 5,000 XP per party member. [Room fixtures, pose checks and camera bounds](logs/2026-11-27-ravager-forest-plants-and-sickbeds.md)
- **Village giant artwork.** From the Roost, jump to region 41h at (22, 57) for Velden or (91, 32) for Davin. Both show standing picture 2469 in place. At (15, 7), dismiss Generoe’s greeting to see his three rocking poses. [Room cameras and comparison frames](logs/2026-11-28-ravager-silt-sea-giants.md)
- **Volcano Core terrain.** Region 3Fh contains 128 ordinary spires. The seven nearby rocks that can be attacked use separate objects and a shared handler. For a visit to the eastern crossing, jump from the Roost to (88, 24). [Camera positions and placement checks](logs/2026-11-28-ravager-volcano-core-spires.md)
- **Forest dining rooms.** For the northern interiors use a throwaway Forest arrival fixture with GPL 48’s camera calls 33 and 38. The ordinary jump can land in a room while showing outdoor trees. The bench at (1383, 184) sits behind hanging cloth. [All room squares and camera bounds](logs/2026-11-27-ravager-forest-dining.md)
- **Volcano furniture rooms.** Set flag 478 for the eastern Volcano 1 rooms. Volcano 2 flag 442 selects the northern half; clear it for the southern half. The northern storeroom visits at (10, 42) and (94, 42) still need the northern flag. A stock / revised jump to Volcano 1 (50, 59) or Tyr (121, 86) shows the two-piece torn bed. [Region fixtures and shelf checks](logs/2026-11-27-ravager-volcano-furniture.md)
- **Mines 3 laboratory and forge.** Sector 4 square (102, 50) reaches the floor safe. The Inquisitor’s key opens it. Sector 12 square (29, 7) reaches the forge throne. Look at the skeleton and choose the hand on its Throne card. GPL 93 uses story flags 257 and 259 for the release, and 258 records taking the hammer. [Native states and test fixtures](logs/2026-11-27-ravager-mine-worktables-and-forge.md)
- **Mines 3 captive and polearm stands.** For the prisoner, revisit sector 4 at (120, 14), Look at the rack and choose the green hand. Answer Yes and dismiss the rescue and XP messages. A farewell leaves the empty rack. Sectors 6 and 9 show the two Mines polearm stands. For the Volcano 2 stand, set flag 442 before the jump to (16, 27) to select the northern camera bounds. [Room coordinates and stock comparisons](logs/2026-11-27-ravager-racks-and-polearms.md)
- **Mines 3 diners and Elderbrain.** Use sector 2 at (84, 73) for the meal and the serving callback on object 5075 for the slump. Use sector 11 at (14, 45) with the barrier down, then the sword on the tank for the destruction. Its intact and breaking pictures are RESOURCE.GFF 11008 and 11016. [Fixtures, captures and rewards](logs/2026-11-27-ravager-mines-diners-and-elderbrain.md)
- **Pavis and the Mines 3 loot chest** ([playtest](logs/2026-11-27-ravager-basin-and-chests.md)). Temple square (109, 45) brings the party to the scribe. Dismiss Jestris’s greeting and use the sword on Pavis to see him leave his paper at the desk. For the Mines chest, the first-visit script sends the party to the entrance. A revisit to sector 11 at (35, 47) reaches its chamber. If a direct-room fixture leaves the party white, restore the display with the region’s calls 36 (0, 0) and 37 (0, 1) after setting bounds and sector. Look at the chest and choose the green hand on its item card. A second use reports that it has been cleaned out.
- **Tantris’s throne and Ikibod’s workbench** ([DOSBox playtest](logs/2026-11-27-ravager-throne-and-workshop.md)). The Roost travel fixture to temple square (64, 13) frames all six braziers. Look at Tantris on the throne and advance his warning to see the seat after he leaves. Region script GPL 256 exchanges object 562 for the empty throne, 3530, stored in Limbo. In Mosaic, square (18, 37) triggers Ikibod’s greeting. End the conversation to see his counter and its bottles unobstructed.
- **A figure's frame live** (2026-11-27, logs/2026-11-27-ravager-encounters.md): a map record (DS:67BBh + 25h n)
  holds at +12h the frame being drawn with its width and height (a byte each) and at +18h the step of its SCMD
  script (the frame shown is the previous step's): poll it beside window grabs to tie a glitch to a step. The
  stock game (`RAV_SKIP=figures`) at the same jump is the control for any redrawn figure.
- **Seeing a picture no map object uses** (2026-11-28, logs/2026-11-28-ravager-merchants-691.md): Limbo's
  objects (the shopkeepers 152-155, 320-325 on picture 691) are never on Tyr's map. After `RAV_MENU=1
  ravstart.sh` has written the Loader's `dos/OBJEX2.GFF`, set a visible object's picture (its OJFF chunk +12,
  a word) to the one to see, then load: the object shows it, with the object's own colour change applied.
  Test-only: the copy is rewritten on the next start.
- **Looking at any spot of a region** (2026-11-27, logs/2026-11-27-ravager-furniture-review.md): after a
  jump, write the view's top left (DS:1408h, two words) to the spot less (160, 100), then U and Escape (USE
  opened and closed) redraw the map there, the party left where it stands: a picture of any placement
  without walking. Pick the jump's square as the open GMAP square (0) nearest the spot. A jump into Mines 3
  near the throne (3Ah, 15, 46) lands in a fight.
- **Checking the two-piece red bed** ([join playtest](logs/2026-11-27-ravager-furniture-joins.md)). In a private Roost travel fixture, Alliance square (6, 26), Tyr (27, 5) and Mines 1 (122, 83) show the beds. The second Alliance layout requires the destroyed-headquarters story state. For that throwaway visit, set bit 2000h of script variable 87h:55h just before travelling to (70, 26). Region script MAS 51 reads that bit to select the eastern camera bounds. Launch fresh for each fixture if the game reuses the previous talk script. Confirm the scenery against the region map. Never save the fixture state.
- **A new game** (2026-11-25, logs/2026-11-25-ravager-weapon-gaps.md): the title menu's START GAME (game
  159,75), the opening film about 75 s, then the opening talk (3, Return x4) and the ambush: C, the four
  lower small icons (47,53 / 98,53 / 47,112 / 98,112), Escape, about 90 s to "Each party member receives
  10000 experience points!" (Return x4 for the level lines). Everything from OBJEX.GFF (the Loader's new
  items, `dsloader/ravgear.py`) shows only so: a save keeps the people and things it has made.
  **Shadow Square from there** (`ravgo.py y 1224 x 560 y 1130 x 420 y 1000 x 300 y 900`, about 2 minutes):
  a ranged-weapon stall blocks y 1224 at x 536 (its seller in front of it talks: 1 opens the shop: the
  Limbo seller 323, thing 16), Notaku's stall north of the end. **The pointer** over bare ground shows
  its barred form (an orange ring: the sword's, then the eye's); right-clicks go arrow, sword, look, so
  take a picture of it before a click on a person: **the sword on Notaku started a fight**. With the eye on
  him the Look box's first button (left, about game 181,66 when the box is beside him) talks.
- **A creature's object** is its record's +6, negated (as OBJEX.GFF's kind-2 record has it: Notaku -58,
  the weaponer -153): how `shopstock.py` knows a seller in memory. A **Limbo seller** (the stalls: 323 and
  the like) is made afresh from OBJEX.GFF's copy when its talk starts, so it has the Loader's items even in a
  saved game; Notaku, who lives in Tyr, keeps the save's list and is topped up by the Loader. **In a shop a
  click on an item buys it** at once ("NOT ENOUGH MONEY" if it can't); the item goes on the pointer.
- **Item names 256 on** (the mod's, DSCLOG2's ITEM_NAMES) are written by the dice log as it attaches:
  without `ravdice.py` running a mod-named item shows another word ("METAL" for the Short Sword).
- **Objects 13000-13999 draw another picture** (a grey ring) whatever their BMP: the Loader's pictures sit
  at 14000-29999 (`ravitems.own_object`, `ravgear.OWN_ICONS` 19900). **Palette numbers 1-15** are set by the
  inventory and shop screens (PAL 1000's 2, a light blue, showed pure blue there): `ravitems.stable_colours`
  leaves them out.
- **Every item record from a map** (the far DS:19C1h, 17h each, as `ravshop.py` reads them): a scan for
  entities -14000 to -29999 lists the Loader's items loaded in the region (Tyr in a new game: Short Sword
  +1 and +2, Great Axe +1, the metal mace, dagger, pick and polearm).
- **Tyr from the save**: the street runs north-south at x ~1175; its south end is the city gate ("The
  gates are locked."). Uhubito's building east of it (door on the street, y ~1340); an alley east at
  y ~1225 (entered from the street at y ~1225-1240), past Arslan's side and the beggar, along the
  Harbinger's Roost's north wall (no door there: its arches are inside doorways seen through the
  cut-away) to the map's east edge (x ~2020); two thieves stop the party near x 1840 ("Run along now,
  pip" makes them fight: won by Computer Control, the party hurt). Fayina is in the Roost's back room
  (1807, 1352). **The Roost's door**: on its north wall at world x ~1621 (an arched doorway with white
  steps, drawn as if inside): the arrow clicked on the steps takes the leader through (the arrow keys
  stop at the wall line, y 1274). Inside: Reyhan, the owner, behind the counter (the look pointer on him
  talks: 1 rent a room, 3 one night, 25 cp: "the room at the end of the corridor, second door on your
  left": the corridor runs east along the south front, the second doorway is open, its steps clicked
  again). Renting adds one map object, a fire ring (object 156 at 1976, 1352, kind -1317), beside the
  bed (which takes no pointer). **The route** (from `ravager-roost`, about 3 minutes): the look pointer
  (two right-clicks from the arrow) on Reyhan (game 150,128), keys 1, 3, 4 (rent, one night, goodbye: the
  talk ends on Reyhan's "Goodbye.": Space closes it, and in the 2026-11-22 run the pointer was then the look's: one right-click gave the walk arrow; check before the arrow keys: the sword ignores the arrow keys),
  the arrow keys Left 4, Down 9, Right 14 (the corridor, x 1871, y 1465), the arrow on the second
  doorway's steps (game 270,104), Up 6 (beside the ring, 1956, 1335), the look pointer on the ring (game
  267,108: the screen is 2.4 px a game row) and click. **A look at the ring rests the party** (the screen
  dims, 8 hours: HP back, spells, DSCLOG2's REST_POISON per member) only with the Loader's `inn_rest`
  fix: the game's own script loses the one paid night (dsloader/ravager.py SCRIPT_FIXES; logs/
  2026-11-20-ravager-dicelog.md 25-26). A second look takes the spent ring away.
- **How a look reaches a rest** (2026-11-20): the look dispatcher (63174h-63400h) runs the object's look
  trigger scripts (a 66h trigger: trigger list load+3C10h:13h, bit 8 of 28:834's flags), then, if the
  object is still there, the program's own look (5B0h:70h, 69473h), whose kind-525h (1317, fire ring)
  branch calls rest(0, 8, 7FFEh) (6951Ch: the rest routine 8CA7Ah). A script's do_action 1 is rest(1, ...),
  the healers' full heal (status 1 for all, the dead too). do_action 15 is no camp: it sets DS:1440h
  (the pointer mode: 1 the arrow) and DS:4596h to 1, the end of many scripts. `triggers.py`-style dump:
  the six lists' heads at load+3C10h:0Dh-17h, records 13 bytes at the far pointer DS:40C0h (+4 the
  object, +0Bh the next).
- **Keys** (gibberishh's walkthrough, in the private repository's guide/): I inventory, O overhead map, V
  character, C cast, 1-4 leader, 5 the whole party shown, 6 the leader only, F1 save (straight to the save
  screen), F2 load, Tab preferences (difficulty), A animations, H the view back to the party; in a fight
  W wait, G guard, Q end turn; in a talk the number keys, Space to go on. The save screen's name field:
  End, then Backspace, before typing (the cursor starts at its start).
- **Resting**: only at a fire ring (the Look icon on it), or a room at an inn (Tyr's Harbinger's Roost,
  25 cp, southeast of the start). The Mines of Tyr level 1 have a fire ring in the room past exit C
  (the owner's map, 2026-11-20: by the dying miner).

**The inventory's full-length picture** (2026-11-27, logs/2026-11-27-ravager-inventory-portraits.md): the
same engine as Shattered Lands' with other numbers: the selected creature's figure is its +10h (SL's +18h),
its picture preloaded from slot 15h (SL's 12h): "mov ax,[es:bx+10h] / add ax,15h" at 75DD0h (SL's 6D5A3h;
two more such lines, 6B053h and 6DBC8h, are the creation screen's); the preloaded pictures' loader is
7B827h (SL's 73034h), its way out with the picture at 7B89Eh. The sequel's own figures (BMP 20000-20013,
76 by 106) are drawn over a parchment the screen draws, so Shattered Lands' 48 by 95 ones sit on it
as in Shattered Lands. `ravinvfig.py` sets a member's figure and classes for a look.

**Its scenes, pointer and message box** (2026-11-27, logs/2026-11-27-ravager-cutscene-mouse.md): the
films (FLI) are played by 831D4h in mode 13h, chained; after each frame 1E8h:11h returns the Shift
flags and `test ax,3` at 8335Ch decides the skip (at once if [631Bh] is set, else only after frame 240),
so in the stock sequel only Shift held about a second skips the intro. The narrated opening after START
GAME (and any spoken map scene) waits at 69BDDh, `lcall 230:51 / or al,al / jnz` (37B3h:51h, "the
speech still plays"); 37B3h:3A5h stops the speech (segment 3611h with the load segment at 1A2h); its
picture is planar with the CRTC start 0. The game's timer runs at about 1 kHz while speech plays, and
that loop hundreds of times a second: a site in it must not redraw on each pass. The mouse: the reset's
"or ax,ax / jnz" at 39F0Bh (SL's 356F5h), the ranges' "mov word [0A103h],0" at 2F110h (SL's 2A912h);
the game's pointer at DS:A109h, A10Bh. The message box (560h:2Ah, through 466A:2Ah) is SL's but its
wait was empty; the mod's MSG_SHOWN waits the options' time, now ended by a click or key.
**A message box to order**: in the Tyr ambush, a click on game (14,188) (inside the closed room at the
street's lower left) on a party turn says NO PATH FROM HERE. **Where a busy loop spins**: a ring in
DSCLOG2 that the timer fills with the interrupted CS:IP (its frame's return address) found 69BDDh at once.

**The combat log panel's clicks** (2026-11-27, logs/2026-11-27-ravager-log-clicks.md): the press must be
taken in the mouse driver's event handler (DSCLOG2's MOUSE_EVENT, PANEL_EVENT), as SL's is: in the main
loop's pointer call it is seen only while the button is down, and the game's handler walks the party to it
anyway. Click the panel's header at game y 126 (docked), not window y / 2.

**The view, the party and the pace in the sequel** (2026-11-27, logs/2026-11-27-ravager-view-and-pace.md): the view's
place is DS:1408h/140Ah and whose turn DS:426Dh; a creature's feet on the map are its map record's +0Ah, +0Ch
(DS:67BBh + 25h a creature): log the three every 50 ms to see whether the view follows a walker. A turn's start
scrolls the view to that creature in steps of 32 (21341h): not drift. Steady pace's counters `pace_ran`,
`pace_lost`, `pace_skipped` are in DSCLOG2's segment (INT F5h's vector's), offsets from `nasm -l`. **Restart
`ravdice.py` after every `ravload.sh`**: it dies with the DOSBox it was attached to, and without it Tab does
nothing (a `ravfight.py tabfight` then never attacks and the party loses).

**The creation screen's sheet** (2026-11-28, logs/2026-11-28-ravager-creation-age.md): the sheet being made
(DS:1429h) is the game's 42h bytes with the creature being made straight after it (DS:142Dh = sheet + 42h): write
nothing past its +41h. DONE copies it into the party's 48h sheet. The boxes: hit points DS:1224h, PSP DS:122Ch
(x1, y1, x2, y2). STORE (112,230), RECALL (172,230), DONE (271,217) in game coordinates. **Which missile weapons
use ammunition**: bit 3 of the type's first byte (the game's count at 5D3BAh); the sequel's sling and chatkcha
have none.

**Reported bugs' checks** (2026-11-28, logs/2026-11-28-ravager-walkthrough-bugs.md): `ravprobe.py` runs once a
load (Reyhan's talk replaced; reload before the next probe); a psionicist's power bytes (selector 370h +9CDh,
22h a member) hold the power's number times 2 (`ravlevel.py powers`; `forget N` clears one); an XP award is
split between the classes, so level one class by its own share. The active effects: the count a word at
DS:2100h, 10 bytes each at (load + 3E71h):24Dh (owner, caster, spell, the effect's id, ...); an entry added
there with the owner's member number takes effect (Protected vs Fire, id 77, spell 138). The damage
routine's halving is at 85178h (SL's 7B56Fh). Item powers 140h-147h are the game's own effects (77CDBh's
take-off, the box's icon at 9A7D4h and 9A9C5h; the powerstone's 146h tested at 99C56h as it is used): the
mod's new spells' scrolls share 141h-146h, which DSCLOG2's NS_BOOK tells apart by the item's type (77, the
scrolls' and spellbooks'). DSCLOG2's rules are 0 until the Loader or the dice log attaches.

