# 2026-11-19: DSCLOG's room freed (the always-on switches' off paths removed): a broad in-game check

Branch `claude/free-dsclog-room`. Under test: DSCLOG with the off paths of every switch gone
after 2.18 removed (the rules' tests, the game's ways behind them, MANUAL_ON), and the Loader's
off branches (the patch groups always applied but Steady pace, the dice log's switch attributes).
The behaviour must be the same as origin/obsidian-edition's with every always-on rule on.

## Set-up

- Lock taken (`flock /tmp/playtest/dosbox.lock`, held by a background loop), `loadsave.sh fountain-user`:
  window 320x240, `buildcheck.py` OK (the routines, 129 vectors at their handlers, the tail), watchdog on.

## 1. The ambush's fight (`fountain-user`)

All as the rules have it, with every switch's bit now untested in DSCLOG:

- Stealth: `Jenna hides in shadows: d100 = 92, needs 52 or less (52, a Stalker: not halved indoors) -> seen`;
  `Seneca hides in shadows: d100 = 60, needs 67 or less (57 +10 cloak = 67, out of the sun) -> hidden`,
  `Seneca moves silently: d100 = 42, needs 77 (67 +10 boots) or less -> unheard` (the cloak and boots: stealth gear).
- Backstab, the dice only (Thieves as in AD&D): `Seneca hits Templar for 11: 1d4 = [3] +1 weapon +4 STR 18 +3 backstab (the dice 3 x2 = 6)`;
  her second attack that turn `from behind` only, no backstab (STAB_FIRST).
- Weapon specialization: `THAC0 19, +3 STR, -1 bone, +1 specialized, +1 Battle Dancer = 15`, damage `+2 specialized`;
  three attacks a round for the 2nd-level fighter/cleric specialist (3/2 + two weapons).
- Two weapons: the guard's `-4 two weapons, off hand at DEX 14` and `-2 two weapons, main hand`.
- A ring of protection on a save: `d20 = 10 +1 Ring of Protection = 11` (Templar's poison save).
- Creature size: `1d12 = [2] -1 bone +2 specialized (1d12 for 1d8: a large target)` on the Guard (a half-giant).
- Spells rolling to hit (Ester's Magical Stone, `spellsetup.py 2=9`, a memory edit: not saved):
  `Ester's Magical Stone at Arena Guard: attack d20 = 12, needs 11+ (50%) (THAC0 19, +4 DEX; target AC 4) -> HIT`,
  and two misses `-> MISS: the spell does nothing, the 4 damage rolled lost`.
- A save against a spell with the spell save: `Arena Guard's saving throw vs Hold Person from Ester (spell): d20 = 6 +2 WIS 16 = 8, needs 16 (35% to save) -> failed`.
- Held targets (foes paralysed with `foeset.py C eff=34`): `Paralyzed: hit automatically, for normal damage (AD&D's held target)`,
  then `Lex hits Arena Guard for 13: 1d6 = [6] -1 bone +8 STR 20` (no x2).
- The combat log panel (L): `Round 4: Ester...`, its lines; Tab chose `Templar (41 HP) - Enter attacks it`, Return attacked.
- The Effects screen (E): Jenna `KIT: STALKER / EXPERT IN LONG SWORD BOW`, Ester `KIT: B-DANCER / SPECIALIZED IN LONG SWORD`.

### The same fight on origin/obsidian-edition's build (its DSCLOG.EXE put in `dos/` for one load)

The rolls differ from run to run (the game's dice aren't the save's), so lines were compared by form:
the same THAC0 and damage parts (`+1 specialized, +1 Battle Dancer`, `-4 two weapons, off hand at DEX 14`,
the large target's `1d3 for 1d4`, the backstab's `(the dice 3 x2 = 6)`, the stealth gear's `+10 cloak`).
One line looked odd in the new build: Seneca's second attack after a backstab,
`Seneca attacks ... from behind with Shadowseeker +1 ...: THAC0 19, +2 from behind, -2 STR, +1 weapon, +1 specialized = 17`
(her STR's +2 shown as -2: 4 off). The old build gives the very same:
`Seneca attacks Guard from behind with Shadowseeker +1 (1d6+1): d20 = 2, needs 7+ (70%), hits AC 15, target AC 10 -> miss`
`    THAC0 19, +2 from behind, -2 STR, +1 weapon, +1 specialized = 17`, so it isn't this change's
(STAB_FIRST's backstab taken back from a later attack; left for its own look). The new build put back after.

## 2. The inventory (`pens-after-arena`): class restrictions

Gerakis's Leather Chest Armor (type 6) taken off and put on Cilla's chest (an elf preserver/druid/thief,
`restrict.usable` False for it): `CANNOT USE THIS ITEM` on the bar, the armour left on the pointer; put back
on Gerakis (slot 9). OK.

## 3. Kalzith's shop (`selling-junk-user`, `openshop.sh`)

- CHA prices: with Gerakis (CHA 14) leading, the game's prices (1$, 9000$, 6000$, 24$); Cermak (CHA 18) made
  leader before the shop opened: 1$, 8550$, 5700$, 22$ (5% off, `prices.price`). OK.
- Selling at 60%: Cermak's Leather Chest Armor (value 10) `I'll give you 6$`; the Slavepen key (1) `1$`
  (never below 1). LEAVE IT both times. (No magical item in the party to try the buyback in play: the unit
  tests of SELL_KEEP cover it, its bit clear too.)

## 4. Resting (`pens-fire-count4`, `ringrest.sh`): AD&D's healing

The priests spend their slots first (`At rest: K'ratchek casts Cure Serious Wounds on Gerakis (4th-level slots: 0 left)`,
then Cure Light Wounds on the most wounded, Cilla's too), then `Message: THE PARTY RESTS` and the natural healing:
`Gerakis rests 8 hours: +3, +6 (CON 22) = +9 (+5: no more than the most), now 54/54 HP`,
`Cilla rests 8 hours: +3, +2 (CON 17) = +5 (+0: no more than the most), now 15/15 HP` (a non-warrior's +2 at most). OK.

## 5. The creation screen (start.sh, CREATE CHARACTERS, NEW)

- Scores as rolled: SUM 96/96, STR raised with nothing spare stays 15; DEX lowered 19 -> 18, then STR 15 -> 16.
- STORE (112,189), a new roll (`the six scores add up to 94`: 14/17/17/15/17/14), RECALL (160,189):
  16/18/14/17/16/15 back, the dice log `Rick th'Untamed's STR 14 -> 16, DEX 17 -> 18, ...`.
- Hit dice the better of two (a switch kept): `10 (the better of 2 and 10) + 3 (the better of 2 and 3) + 9 ...`.
- Ages: `AGE: 17` on the screen, `Rick th'Untamed is 17 (a human: 15 + 1d8 = [2]); middle-aged at 40.`
- The THAC0 line `THAC0: M18 R15`; the KITS page (NO KIT, MYRMIDON, SENTINEL, RAVAGER, VIEW PSIONICS).
- DONE: PICK A WEAPON SPECIALTY (CR_WEAPONS, its window now always), the long sword (`sheetinfo.py`:
  specs ['long sword']), `starts with more gear: Sling`, PICK A PSIONIC POWER, then VIEW CHARACTER. OK.

## 6. The scene pointer

START GAME's decree with DSCLOG's arrow; `xdotool mousemove_relative -- 25 8` moved it (shots 0.7 s apart). OK.

## 7. The map: shadows, dust, dressed figures, see-through tables (`pens-after-arena`)

A shot zoomed: shadows under every figure, Gerakis in his leather armour (the gear on the figures), Cilla drawn
as an elf (the half-elf woman's figure). A walk click and shots 0.6 s apart: dust behind the walkers. `ghostchk.py`:
`ghost_seg E99B on 1` (the see-through tables in place; a hidden figure wasn't caught on a shot this time).

## 8. Room in play (`memaudit.py`, `pens-after-arena`, the map open)

Upper memory: DSCLOG 69,936 bytes (4,371 paragraphs: was 71,104), the overlay buffer 32,992, **26,304 bytes free
in one piece** between the overlay buffer and the see-through tables (was 25,136), 144 bytes below DSCLOG as
before. Conventional: 99,008 bytes free after the game (unchanged). `umb_need 6451` paragraphs (was 6,524).

## Results

Every thing exercised behaved as the rules have it, and as origin/obsidian-edition's build does (the one odd
THAC0 line is the old build's too). Nothing saved: the only memory edits (Ester's spells and levels, foes held)
were in `fountain-user`, never saved. DOSBox, Xvfb, the dice log and the watchdog stopped by pid; the lock let go.
