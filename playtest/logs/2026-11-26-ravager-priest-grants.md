# Sixth-level priest grants in Wake of the Ravager

A clean DOSBox run loaded the after-ambush save. DSCLOG2 occupied 52,992 bytes in upper memory, leaving a largest free block of 102,464 bytes.

A 16-bit emulator ran the patched known-spell and spell-list routines (file offsets 0x6260A and 0x62500) against a copy of the loaded game state. At class level 18 the air cleric and air druid received spells 326 and 327, the earth cleric received only 327, and the preserver received neither. With the rule off, none of the four received either spell. No modified state was saved. These checks cover eligibility and listing. Combat casts, funnel art and the logged age change still need play verification.

A separate check attached RavDiceLog to a copy of the DOSBox snapshot. Haste aging took Terrannus to 19. A constructed cast event for spell 327 targeted Terrannus, with the system shock roll fixed at 1. The log reported “Terrannus grows younger 1 year (Restore Youth): now 18.” The sheet also read 18 afterward. This exercises the event consumer and the sheet write. The event still needs to be produced by a live player cast.

In a second snapshot replay the patched cast entry at 0x80580 ran under a 16-bit emulator through its INT D2h and back. DSCLOG2 recorded kind 8, spell 327, caster 0 and target 1. RavDiceLog polled that record, made the successful system shock roll with the same fixed die, and took Terrannus from 22 to 21. The spell-selection UI and the remainder of the DOS cast were outside this replay.

The sequel’s ground-area table begins at file offset 0x47110. Its 112 records are 18 bytes each. Entry 8 identifies Stinking Cloud and entry 80 Sandstorm. The next bytes at 0x478F0 already contain data. Assigning Whirlwind record 326 to entry 8 would dispatch Stinking Cloud’s spell number on later rounds. A dedicated entry and verified round dispatch are still needed.
