# Test log: AD&D's class tables, Wake of the Ravager (2026-11-22)

Under test: SL's AD&D class tables (game.RULE_ADND_TABLES, always on in SL; DSCLOG's XP_NEED,
PROBE_PRIEST_THAC0, PROBE_ADND_SLOTS) in DSCLOG2: XP_NEED (site 32 at the XP table's eight reads),
PRIEST_THAC0 (site 33, 95391h) and ADND_SLOTS (site 34, 62893h), with the sequel's tables to 20th
level (tables.RAV_XP, RAV_PRIEST_SLOTS, RAV_WIZARD_SLOTS). RULE_ADND_TABLES added to
ravager.RULES_PORTED.

## Found first

- The XP table is RESOURCE.GFF's DATA 1000: 8 rows (cleric, druid, fighter, gladiator, preserver,
  psionicist, ranger, thief) of 20 words, in hundreds, read by 5C8:20 (6F640h: the resource, the
  row, the index; the word at row x 40 + index x 2) at eight places, each followed by `push dx / push
  ax / pop eax / add sp,6 / imul eax,eax,64h`: 6C3E4h, 6C48Ah, 6C4CCh (the creation screen), 6FB8Bh,
  958E3h, 95931h, 9597Ah, 95C84h (the level up 9581Ch: the XP, the sheet's +0 dword, capped at the
  level 3 above's; no level past 15th). The class to row map is 360h:9Dh + class x 2.
- Against AD&D's: the thief's 2nd level 1,200 (1,250), the gladiator's and ranger's 2,200 (2,250), the
  druid's from 11th the cleric's (Dark Sun's druid 200,000, 300,000, 750,000, 1,500,000, then 3,000,000
  and 500,000 a level), the gladiator's 16th 2,000,000 and up the fighter's (AD&D's 300,000 a level
  from 1,800,000), the psionicist's 18th and 19th 1,400,000 and 1,700,000 (2,400,000, 2,700,000).
  Everything else is AD&D's, past 14th too.
- The THAC0 routine (9534Ch) and the slot routine (62A10h, its call at 62893h, the class byte the low
  byte of a word whose high byte is left over) are SL's byte for byte. THAC0 is the creature's +16h,
  worked out only at a level up (its one caller, 95792h). The slot rules (DS:670h, 684h) are SL's.
- The dice log's slot counts (SL's GameData.max_spell_slots) used SL's AD&D tables (to 12th level,
  spell level 5) in the sequel without the rule: now `RavGameData.adnd_slots`, the sequel's tables
  with the rule and the game's own rule without.

## In the game (the Loader, the dice log on; about 19:25-20:05 UTC)

Test edits, DOSBox stopped after each, nothing saved.

### The Draxans' ambush (ravhold.sh, then the party's HP 250 and AC -10, the Draxans at 1 HP, Computer Control)

Thy'rokh (fighter/druid) made 12th in both (best 12 too), XP 800,000; Terrannus (cleric) 11th, XP
950,000 (the first run 700,000: an 11th-level cleric needs 900,000, the index the level, so no level).

- **The rule on** (rules_hi F22Eh): after "Each party member receives 10000", Thy'rokh's druid level
  **13** at 807,000 XP (AD&D's 750,000), the fighter's 12 (1,250,000 needed); Terrannus 12th with
  THAC0 **14** (AD&D's 2 per 3 levels). XP_NEED counted 4.
- **Control, the rule off** (F226h): the druid stays **12** (the game's 1,125,000); Terrannus 12th with
  THAC0 **13** (the game's 11 x 8 / 12 = 7 off 20). XP_NEED counted 0.

### A rest at the Roost (ravload.sh ravager-roost, the route in RESEARCH.md)

Ar'anda's preserver level 6 made 12 (best too), Thy'rokh's druid 7 made 12. The slots left (the game's
memory at DS:4469h/4474h + a member x 22h) after the look at the ring:

- **The rule on**: Ar'anda WIZ **4 4 4 4 4 1** (AD&D's 12th), Thy'rokh PRI **9 8 7 4 2 2** (AD&D's 6 5 5
  3 2 2 and WIS 19's 3 3 2 1). ADND_SLOTS counted 18. USE showed WIZ 4/4 at level 1 (the Loader's).
- **Control, the rule off**: Ar'anda WIZ **5 5 4 3 2 2**, Thy'rokh PRI **9 8 6 4 2 2** (the game's
  rule). ADND_SLOTS counted 0.
- Water: nothing new (the Roost, the ambush's street).

Result: AD&D's class tables work in the sequel as in Shattered Lands, to 20th level.
