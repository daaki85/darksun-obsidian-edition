# 2026-11-25: choosing a kit in Wake of the Ravager (creation and DUAL)

**Under test:** branch `claude/ravager-kit-choice` (from `claude/ravager-kits`): the creation panel's KIT
pages ported to the sequel (DSCLOG2's KIT PAGE, sites 62-69: the disciplines' and spheres' windows, their
clicks, the rows marked, the classes and race changed, NEW's kit byte; the pages' pictures from
`kitpages.rav_chunks`, the sequel's planar form) and a kit asked for after DUAL (DSCLOG2's DUAL_KIT, site
76). DSCLOG2.EXE built from this branch (`buildcheck`: the copy's DSCLOG2.EXE the same bytes as
`obsidian-edition/dos/DSCLOG2.EXE`).

**Set-up:** a copy `ravKC` of `$WORK/rav` with the Loader's files (`ravfixes.py`, `ravager.write_resources`),
`RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 sh ravstart.sh /tmp/playtest/ravKC`, the dice log `ravdice.py 2900
kc-dice.txt` (rules_hi 0xFF2F: kits on). The DOSBox lock held throughout; one DOSBox. Every reading below is
`ravkits.py page` (the sheet being made, at far DS:1429h) or `ravkits.py show` (the party's sheets).

## What was seen

**1. A kit chosen at creation (JohnBoy, slot 1, a human fighter).** CREATE CHARACTERS, a right click on the
empty slot, NEW. The disciplines' window came up as the KIT PAGE's 3022 with a **KITS** button in VIEW
SPHERES' place ([picture](img/2026-11-25-ravager-kit-choice-kits.png)). KITS opened page 3028: NO KIT
(marked), MYRMIDON, SENTINEL, RAVAGER, VIEW PSIONICS.

| Step | Kit byte (+3Dh) | Window |
|---|---|---|
| NEW | 0x00 | 3022 |
| KITS | 0x00 | 3028 |
| NO KIT clicked off | 0xFF (KIT_OPEN) | 3028 |
| RAVAGER clicked ([picture](img/2026-11-25-ravager-kit-choice-page.png)) | 0x03 | 3028 |
| VIEW PSIONICS | 0x03 | 3022 |
| the dice rolled again | 0x03 | 3022 |
| FIGHTER clicked off (classes 0) | 0x00 | 19504 (the game's own: no class, no kits) |
| GLADIATOR | 0x00 | 3022 |
| GLADIATOR off, FIGHTER, KITS, RAVAGER | 0x03 | 3028 |
| DONE | sheet 0: classes [9], kit 0x03 | |

View Character: AC -3 (with the kits rule off later in the same session, the same JohnBoy showed AC 3: the
Ravager's own AC table at work). Effects: **KIT: RAVAGER** ([picture](img/2026-11-25-ravager-kit-choice-effects.png)).

**2. No kit picked (Swat, slot 2, a human fighter).** NEW gave kit 0 (the template's last byte, 3 from
JohnBoy, cleared at NEW: site 69). KITS, NO KIT clicked off (0xFF), DONE without a kit: sheet 1 kit
**0x00** (NEW_SHEET turns KIT_OPEN into none). The character plays as one without a kit.

**3. DUAL with a kit pick (Swat).** The roster's inventory, a right click on Swat: EDIT / DROP / DUAL; DUAL,
THIEF. A menu **KIT: NONE** came up with ASSASSIN and SHINOBI
([picture](img/2026-11-25-ravager-kit-choice-dual.png)); Swashbuckler is left out (DUAL_BANS: a fighter's
dual class into thief). ASSASSIN: sheet 1 classes [17, 9], levels [1, 7], kit byte **0x08** (Assassin, the
thief's second kit, in bits 2-3: the first class's two bits lowest, the class taken by DUAL the next two, as
`kitpages.kit_byte`); `dual_asks=1 dual_kits=1`. Effects: **KIT:
ASSASSIN** (the new class's place is always awake).

**4. The control: the kits rule off.** The rule's bit cleared in DSCLOG2's header (rules_hi 0xFF2F to
0xFF2E: a test edit, nothing saved after it). Slot 3, NEW (Killer, a human fighter): the game's own
disciplines window **19504**, VIEW SPHERES and no KITS button
([picture](img/2026-11-25-ravager-kit-choice-off.png)); DONE: sheet 2 kit 0x00. DUAL to PRESERVER: no kit
menu, `dual_asks` still 1, classes [11, 9], kit 0x00; the inventory came back as the game's own. JohnBoy's
AC read 3 there against -3 with the rule on.

STDOUT.TXT stayed empty all session (no "Illegal Op"). The session's DOSBox and dice log were killed by pid
and the lock let go.

## Not done

- A kit's hit points and PSP: SL rolls them again when the kit is taken at creation (CR_KIT_HP); the
  sequel's sheet keeps what the dice gave.
- The Elementalist's second sphere (SL's ELEM_SPHERE on the spheres' window).
- EDIT of a made character gives its kit back only while its classes stay as they were; SL also gives it
  back after the classes are changed and changed back.
- After DUAL: a new warrior's weapon picks, and greying the classes a kit bars in the DUAL window.
- Items a kit forbids or allows (KIT_FORBIDS / KIT_ALLOWS): the port plan's next step.
- No EDIT of JohnBoy was played (the kit kept on EDIT is the code's `kp_first` path, read but not played).

**Water:** none (the creation screen and the roster only).
