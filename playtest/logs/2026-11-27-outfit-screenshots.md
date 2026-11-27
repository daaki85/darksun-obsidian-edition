# Doc screenshots retaken with the class outfits (2026-11-27)

Under test: nothing new; the docs' pictures that predate the class outfits (#205, #231; the docs
audit's section 5, reports/docs-review-2026-11-27.md) retaken on `obsidian-edition` at a8e63347
(after merge train #241), so the party wears its outfits.

## Setup
- Fresh container: apt `dosbox xdotool innoextract nasm python3-tk`, `setup_game.sh` from the
  private checkout.
- `loadsave.sh pens-after-arena`: window 320x240; the default party dressed on load (Cermak in the
  plum mantle, Gerakis the mul gladiator bare-chested, K'ratchek the game's own thri-kreen).

## Pehtucl's ambush (`loadsave.sh fountain-user`, `dismiss.sh`)
The user's party (Lex, Jenna, Ester, Seneca) dressed on load. No memory edit; the fight's end
autosaved into the game folder (the kept save untouched).
- `combat-log-live.gif`: from the fresh load, `scroll.py -60 -80`, DOSBox's Ctrl+F5 in a loop
  (13 a second) while `untilturn.sh` played Lex, the guards, Ester and Seneca (Ester's hits on the
  Templar, Seneca's seen hide). 425 frames, every other one kept, `-delay 15 -scale 200%`: 775 KB.
  **Seen**: while the game scrolls the view to a guard, the docked panel's title row is drawn
  several times along the row ("Needs Needs Needs"), for a frame or two; gone once the view stops.
- `combat-log.png`, `-expanded.png`, `-detail.png`: round 4, Jenna's turn (she couldn't hide: a
  guard beside her), `camera.py 1042 1418` so the party stands left of the panel; + expands,
  the level button once gives Detail (Ester's miss with THAC0 19, +3 STR, -1 bone, +1
  specialized, -1 Battle Dancer = 17).
- `hit-chance-hover.png`: the same turn, panel hidden, the pointer on the guard: 13+ (40%).
- `squares-in-reach.png`: a reload, played to Seneca's turn in round 1, two walks east (Move 5
  left), Tab: an Arena Guard ringed outside the crosses.
- `floating-names.png`: further turns with the camera on the party (`camera.py 856 1338`),
  captures in a loop: "Miss" over Jenna (a guard's arrow) and over an Arena Guard.
- (`gear.png` came later, from the pens.)

## The arena (`start.sh`, `topartyfight.sh`: the ready-made party's first fight, then its waves)
Gerakis (mul gladiator), K'ratchek (thri-kreen), Cermak (human preserver/gladiator, the plum
mantle), Cilla (elf preserver/druid/thief: Druid keeps the game's own figure). Memory edits from
Whirlwind on: nothing saved after (but see the autosave below).
- `shadows.png`: K'ratchek's turn; DSCLOG's `shadows_on` (header +220) written 0 (`shadowsw.py`,
  new), the view scrolled a pixel and back, a shot; 1 again, the same, a shot; 194x132 crops side by
  side at 200%.
- `rings.png`: the same turn, Tab: a Slig ringed; 320x132 at 200%.
- `default-party-armor.png`: Cilla's turn, U: her 1st-level mage spells, ARMOR in the bar, WIZ 2/2,
  the party's small figures dressed on the left. (No Pick Pockets purse under the counts now, so
  the caption lost it.) Armor cast on herself (a click on her figure).
- `floating-charges.png`: nobody struck Cilla in three rounds (hidden), so her second Armor went to
  Gerakis: on the USE screen the spell stays on the pointer and is **dropped on a portrait** (66,62).
  A Slig's hit then: "Improved AC on Gerakis: one charge used, 9 left" and "Armor: 9 left" over him,
  with a Screamer Beetle's "Inertial Barrier" beside it (frames of a Ctrl+F5 loop).
- `whirlwind.gif`: Cilla's druid class made air (`sheetbyte.py 3 0x22 5`; memory) and her levels 12
  (`spellsetup.py 3=12`): CLERIC, LEVEL five times to 6 (Heal, Blade Barrier, Whirlwind at 230,59,
  Restore Youth), Whirlwind on a Daggoran; the funnel stays for rounds: `camera.py` 30 left, 70 up,
  117 frames in 8 s, 240x180 at 200%: 179 KB.
- **`spellsetup.py` can't teach the mod's new spells**: the known row is 8Ah bytes a member, so a
  spell of 196 and up wrote into the next member's row. New wizard spells are known by the sheet's
  bits (`game.NEW_KNOWN`: +45h 40h Fogbolt), a new 6th-level priest spell by the caster's sphere.
  spellsetup.py now skips them with a line saying so.
- **Fogbolt** (`fogbolt.png`): Cermak taught it (`sheetbyte.py 2 0x45 or0x40`), but "can't cast
  Fogbolt there: no line of sight" at a Wild Mul twice (click and Tab + Return), across open sand
  with the Whirlwind's funnel standing; later in Pehtucl's ambush Lex (`sheetbyte.py 0 0x45 or0x40`)
  cast it on the Templar (he saved), but the bolt was gone before the first capture. **Not
  retaken**: the old picture stays (a party of the user's, no outfit in the way of the bolt).
- **The arena's Announcer** speaks in a party turn ("Such poor quality creatures..."): `toturn.sh`
  kept pressing Tab under the box for 200 s. It now clicks a waiting message away first.
- **Autosave** went off after a wave ("Auto - Day 1, 00:09 - after a fight") though
  `"autosave": false` had been written to settings.json during the run: the running dice log had
  read the settings at its start. Set it before `start.sh` (it only wrote the game folder's slot 9;
  nothing of it was kept).
- `dust.png`: after the waves, a click far across open sand with the pointer moved off at once,
  Ctrl+F5 every 0.04 s: frames 1, 4, 7 and 13 (150x120 each, 200%).
- `magic-glint.gif`: Gerakis's long sword made the Searing Blade (`setitem.py 0
  rec=worldgear.SEARING_BLADE`), his leather pieces +2 (`itemplus.py 27|28|2 2`, new): blue sparks on
  him within a few seconds. 50 frames in 4 s, 76x80 at 400%. (`camera.py` out of a fight changes the
  memory but the view isn't drawn again until something moves; `scroll.py` moves it at once.)
- Two more waves came after the "Yell something back?" question (N).

## The slave pens (`loadsave.sh pens-after-arena`)
- `see-through.png`: `ghostchk.py 0` marks Gerakis; a shot before and after, 180x120 at 200%.
  `ghostchk.py 511` (a thing that isn't there) clears the mark.
- `show-usable.png`: retaken by its recipe, but it has none of the party in it: **left as it was**.
- `picture-modes.png`: `picstart.sh plain|scanlines|tv 3`. **Without the dice log the party wore
  the copy's older looks** (Gerakis and Cermak in dark gear): the outfits and the gear are dressed by
  the attached Loader. picstart.sh now starts the dice log too (and stops it). Crops 294x270 at the
  window's size.
- `steady-pace.gif`: `PT_CYCLES=20000 pacerec.sh off|on`, the guide's ffmpeg line: 514 KB. The puffs
  of dust show on the pens' floor too.
- `gear.png`: a walk west and back south-east from Kurzak, the party standing apart: 76x88 at 400%.

## The creation screen (`start.sh`, the title, CREATE CHARACTERS, NEW)
- `creation-store-recall.png`: a human fighter (101/101), STORE (113,191), the die (155,97) for
  103/103, RECALL (175,191): 101/101 again; the pointer parked at (228,62). The small figure wears
  the fighter's outfit.

## Left as they were
- `half-elves.png`: the race figures the outfits are drawn on (made from the pictures, not a play);
  FEATURES now says the party shows them bare only outside the outfits' roster.
- `use-slots.png` (icons only), `show-usable.png` (no party), `fogbolt.png` (above).
- The Loader's windows (`dicelog.png`, `dicelog-readable.png`, `dialogue.png`, `viewer.png`): no
  party in them; their old bar is a separate retake.

Water: no new area (the pens, the fountain, the arena).
