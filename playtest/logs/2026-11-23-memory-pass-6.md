# 2026-11-23: memory pass 6 in the game

**Under test:** DSCLOG built from claude/memory-pass-6 (on PR 149's branch, 55beeaa): GAME_FAR (35 far
calls into the game), FRAME_UP / FRAME_DOWN (interrupt frames moved a word), OVR_FRAME (11 overlay-frame
handlers), EXTRA_TYPES packed (XTYPE). DSCLOG.EXE 70,320 bytes (71,424 before).

## Setup
- loadsave.sh fountain-user; window 320x240.
- buildcheck.py far_game frame_up frame_down ovr_frame probe_types_fill th_hit tu_site probe_spell_text: all same; 129 vectors at their handlers; tail extra_types/extra_names/kit_names as the EXE. OK.
- The game's item type table after the load (types and names chunks read: PROBE_TYPES_SIZE/FILL, PROBE_NAMES_SIZE/FILL): DSCLOG's 39 types at 115 on, byte for byte npcitems.TYPES. **PASS** (XTYPE unpacked right; the frame code of the four probes ran).

## The ambush (fountain-user, dismiss.sh): PASS
- Jenna (hidden, from behind) at the Templar with both swords: to-hit lines as before.
- Ester: U, the USE screen with its spell slots (SPELLS LEFT PRI 5/5); Curse at the Templar: "Ester gives Cursed to Templar: -1 to hit", its time line; the Templar's attack later "-1 Cursed".
- Lex walked beside the Templar, then Shocking Grasp: "touch attack d20 = 18, needs 11+ (50%) (THAC0 18, +3 STR; target AC 4) -> HIT", 7 damage (TH_HIT: OVR_FRAME, and its three GAME_FAR calls into the game's STR, AC and to-hit routines).
- Seneca hidden: BACKSTAB with the Bone Hayneedle, the poison saves, the second weapon (Shadowseeker) twice; natural 1 and natural 20 as such.
- Archers' shots at Jenna and Seneca, HP lines.
- Lex's inventory: weapon lines (Bow 3x1D8+2 T13, Short Sword 1D6+7 T16); right-click the arrows: "7 Wooden Shocking Arrows" box (BOX_LINE: GAME_FAR); INFO: "SPELLARCHERS: Lex" (INFO_HEAD: FRAME_DOWN twice). Box shut, inventory shut, the map back.

## The creation screen (a new game, CREATE CHARACTERS, NEW): PASS
- The screen: SUM 89/99, HP and THAC0 lines; KITS, NO KIT off, MYRMIDON marked; VIEW PSIONICS (the disciplines' window: PROBE_WP_DISC_WIN, FRAME_DOWN, GAME_FAR WP_TO_DISC) and KITS again: MYRMIDON still marked.
- Fighter off, cleric on: the CLERICAL SPHERE window (PROBE_WP_SPHERE_WIN), HP and THAC0 drawn again; AIR off, WATER on, KITS: HEALER offered and taken.
- Back to fighter, DONE: PICK A WEAPON SPECIALTY with the Ravager kinds in it (PROBE_PK_WIN, PROBE_PK_TITLE: FRAME_DOWN); the gythka picked: "SPECIALIZE IN GYTHKA", the dice log's gear lines (a plain bone gythka in place of the bone long sword, the shield to the pack). PICK A PSIONIC POWER, three picked; VIEW CHARACTER with Magramar, 30/30 HP, THAC0 17.
- No hang, no wrong text, the watchdog quiet throughout (its one GONE was start.sh's restart).

## Not played
Turn Undead, Chill Touch on undead, Shadow Drain, the Djinn, Rainbow Pattern, stinkpots, Negative Plane Protection, Mirror Images, the level-up spell pick, quest XP and dropping the held item: their GAME_FAR / OVR_FRAME calls are the same routine and macro the played ones use (each site's two words checked against the old build's segment and offset, all 35), and test_dsclog runs most of them in the emulator.
