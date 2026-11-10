# Group 4 research (2026-11-09): monsters against the manual, dual-classing, resting

Read-only research: code and data reading, no DOSBox. Addresses are DSUN.EXE file offsets (as
in the disassembly and the mod's docs). The tables were read from the unpatched
`/tmp/playtest/inst/DSUN.EXE` and `SEGOBJEX.GFF` (the mod's `obsidian-edition/dos/SEGOBJEX.GFF`
has the same records for these monsters). Data offsets used below:

- Monster kinds table (selector 3C0h, segment 3E45h): file **43850h**. Properties dword per kind at
  43850h + 4 x kind; resistance class byte at 438F8h + kind; class rules: masks (4 words) at
  43922h + 12 x class, percents (4 bytes) at 4392Ah + 12 x class.
- Spell/power records: file 3CB40h + 5400h + 30h + 20h x n (game.py `spell_record`).
- Special-action table (one turn in four, 5A90Fh): bits at DS:05D0h, powers at DS:05DBh (file
  48B30h / 48B3Bh): bit 26 -> 27 Fireball, 20 -> 181 (6d6 fire breath), **31 -> 185 (3d6 fire,
  breath save, a save halves)**, 30 -> 30 Hold Person, 6 -> 138 Detonate, 12 -> 175 (Stuck, webs),
  18 -> 179 (paralysing gaze), 19 -> 180 (spines), 21 -> 182 (Red Slaad's paralysis), 22 -> 183 (a
  gaze record with no effect and no damage), 29 -> 43 Fear. Only for kind != 0 (5A954h), a
  1-in-4 roll (5A95Bh-5A975h).
- Powers on a hit (7A6BAh-7A7C5h, through 7A9A7h(target, attacker, bit, power) -> 790D2h): only
  for kind != 0 or a thri-kreen (7A6BAh-7A6DBh). On the FIRST natural attack set ([BP+1Ah] = 0):
  bit 2 -> 172 (2d6 cold), 3 -> 173 (Paralyzed 2d6 rounds), 4 -> 174 (2d6 acid), 24 -> 186 and 187
  (corroding touch: armour, weapon), 16 -> 178 (20 acid), and on a d10 of 1 (7A739h) 25 -> 184
  (Diseased, permanent, save vs poison). On the LAST natural set ([BP-0Ah]): 13 -> 176 (10 poison),
  14 -> 177 (30 poison), **15 -> 119 (the priest's Poison: Poisoned, save vs poison; harmless in a
  fight, 1000 damage once time passes)**; a thri-kreen's bite 189.
- Unused kinds (no SEGOBJEX creature has them; no code sets +16h to a constant): 2, 10, 18, 28,
  29, 34-40. Unused resistance classes: 12, 15.

## 1. Monsters

### The manual's text

- **Shadow** (p. 33, the short list): "Shadows are undead creatures that drain strength from their
  victims with their touch. Their chilling grasp does light damage to their victims, in addition to
  weakening them." No stat block.
- **Greater Shadow** (p. 41): AC 4, MV 18, HD 6, THAC0 15, 2 attacks, "2-12 (touch)+Special",
  special attacks "Strength drain", special defences "+1 or better weapon to hit", MR nil, XP
  1,400. "The chilling touch of a greater shadow inflicts 2d6 points of damage and drains 1
  strength point from its victim. The greater shadow is immune to sleep, charm, and hold spells,
  and it is unaffected by cold-based attacks. They can be turned by clerics."
- **Babau** (p. 34, short list): "... long, wicked claws covered with dirt, blood, and decaying
  flesh. ... Beware of their deadly poison." No stat block.
- **Blue Slaad** (p. 34, short list): "two razor-sharp bone rakes ... immune to normal weapons ...
  Beware of their deadly poison." No stat block.
- **Tari** (p. 52): AC 6, MV 12, HD 3, THAC0 17, 1 attack, "1-3 (bite), or by weapon", special
  attacks Disease, MR nil, size S, XP 175. "... bite for 1d3 points of damage. The Tari tend to
  carry diseases, so a Tari bite has a 5% chance of infecting its intended victim with a serious
  disease, unless a save versus poison is made."
- **Genie** (p. 33, short list; the game's Djinn): "They pummel their victims with a powerful
  tornado-like force. Their ability to use illusions and become invisible makes them virtually
  impossible to capture." **No magic resistance is promised** (the earlier table's "magic
  resistance" is not in the manual; "resistant to magic attacks" is the Dune Reaper's, p. 39).
- **Styr** (p. 51): AC 0, MV 6, HD 14, THAC0 7, 4 attacks "2-20 (fist)", special attacks Fire
  breath, "+1 or better weapon to hit", MR 30%, size L, XP 13,000. "... attack four times for 2d10
  points of damage each. The styr can also breathe fire inflicting 3d6 points of damage."

### The game's records (SEGOBJEX RDFF: creature +16h kind, +1Fh THAC0; sheet +18h race, +24h level, +27h AC, +29h MR, natural sets +2Bh..)

| Monster (objects) | Kind, bits, class | Level, HP, AC, THAC0, MR, XP | Attacks | What its hits/turns do |
|---|---|---|---|---|
| Shadow (153, 265; RGN27, Summon Shadow's RGNFF) | 15: bits 2, 5, 9, 10; class 4 | 3, 18, 7, 17, 0, 650 | 1 x 1d4+1 | +2d6 cold (172) each hit; +1 weapons only; undead; not cold-immune |
| Greater Shadow = the 6-HD "Shadow" (154) and Shadow Guard/King/Prince/Worker (120, 121, 244, 245, 250), Cragg, Tanelyv, Tristram (RGN2B) | 13: bits 3, 5, 9, 10; class 11 | 6, 30, 4, 15, 0, 1400 | 2 x 2d6 | Paralyzed 2d6 rounds (173, save) each hit; +1 weapons only; **not cold-immune** (class 11's 100% rule holds the MAGIC bit, so a cold spell's 0204h always counts 100%) |
| Babau (70, 287; RGN0D) | 3: bits 10, 22, 24; class 11 | 8, 54, -3, 13, 50, 42500 | 2 x 1d4+8, 1 x 2d4+7 | corroding touch on the claws (186/187: armour and weapon may be eaten); gaze 183 one turn in four (no effect in its record) |
| Blue Slaad (278; RGNFF) | 17: bits 10, 25, 28; class 11 | 8, 44, 2, 13, 40, 16500 | 4 x 2d6, 1 x 2d8 | disease on 1 rake hit in 10 (184); +1 weapons only |
| Tari (60, 65, 243; RGN28) | **0** (people), race 1 human | fighter 2, 10, 10 (+gear), 18, 0, 65 | 1 x 1d2 or a weapon | none: kind 0 never reaches the hit-power code |
| Djinn (122; RGNFF) | **0**, race 14 | fighter 10, 50, 4, 11, 0, 6000 | 1 x 3d8 | none |
| Styr (99; RGN0D x5, RGNFF) | **0**, race 12 | 10, 70, 0, 11, 30, 13000 | 4 x 2d10 | none; any weapon hurts it (class 0) |
| (for comparison) Animated Statue (35) | 21: bits 28, **31**; class 5 | 10, 150, -2, 5, 20, 15000 | 4 x 4d8+8 | 3d6 fire breath (185) one turn in four: the Styr's power exists |

So, against the earlier table: **confirmed** Shadow/Greater Shadow (no STR drain; also not
cold-immune), Babau (no poison), Blue Slaad (no poison: the game's disease is AD&D's own Blue
Slaad, the manual's "deadly poison" is the departure), Tari (no disease; also HD 2 not 3, AC 10,
THAC0 18, 1d2 bite), Styr (no breath, and no "+1 weapon" defence). **Corrected:** the Djinn's MR 0
is no gap (the manual promises none; AD&D's djinni has none either); its gap is invisibility and
illusions only.

### Changes (each a "monsters as the manual describes them" patch group, like gamepatch's SPELLS_MANUAL)

1. **Blue Slaad: deadly poison** - data only, 1 dword. Kind 17 props at 43894h: 12000400h ->
   12008400h (bit 15): its last attack set (the 2d8 bite) casts 119 Poison. Keeps AD&D's disease.
   Look box text follows by itself (monsters.SPECIAL_ATTACKS has bit 15 "deadly poison").
2. **Babau: deadly poison** - data only, 1 dword. Kind 3 props at 4385Ch: 01400400h -> 01408400h:
   the horn (2d4+7, its last set) casts Poison. Keep the corroding touch (the "dirt, blood and
   decaying flesh" claws). AD&D's babau has no poison (its gaze weakens; unverified from memory):
   the manual is the source here.
3. **Styr: fire breath 3d6 and +1 weapons** - data: give object 99 an unused kind, e.g. **38**
   (creature +16h: 0 -> 38 in the Loader's copy of SEGOBJEX, 1 word), and kind 38's props at
   438E8h: 00000601h -> 80000400h (bit 31: power 185, 3d6 fire, breath save halves, one turn in
   four; bit 10 as the other class-11 monsters). Kind 38's class byte (4391Eh) is already 11 (+1
   or better weapons only). Optional stats: level 10 -> 14 (sheet +24h), THAC0 11 -> 7 (+1Fh).
   No DSCLOG code.
4. **Tari: disease** - data: an unused kind with only bit 25, e.g. kind **40** props (438F0h)
   00000020h -> 02000000h (class 0 kept), and objects 60, 65, 243 creature +16h 0 -> 40; bite sides
   2 -> 3 (sheet +31h). The game's roll is 1 in 10 (7A739h "push 0A0001h", shared with the Blue
   Slaad, which AD&D gives 10%); the manual's 5% needs a DSCLOG check (small: a site at 7A739h, d20
   for kind 40). Risk to check in DOSBox: a non-zero kind on a human with gear (whether it still
   puts its club and leather on at its first action, and its Look box); kind 0 is "people".
   Optional: HD 3 (sheet +24h 2 -> 3), THAC0 17. The hit-power code runs on attack set 0, so a
   Tari's club hit would carry the disease too (the weapon takes set 0's place).
5. **Shadow and Greater Shadow: STR drain (DSCLOG) and cold immunity (data)**.
   - Cold: class 4's first mask (43952h) 0139h -> 013Dh (adds cold, 0%); kind 13's class byte
     (43905h) 11 -> 4. Both shadows then: +1 weapons only, immune to poison, draining and cold.
     2 bytes + 1 byte, data only.
   - Drain, AD&D's reading of both entries: each hit drains 1 STR (no save), back after 2d4 turns
     (AD&D 2e shadow; a human at 0 STR dies, optional: the game's Weakened stops at 3). The
     shadow's "light damage" is its 1d4+1; the 2d6 cold (172) goes; the Greater Shadow's
     paralysis (173, not in the manual) goes; its 2d6 touch stays.
   - How: the game's own **Weakened** effect (68: "STR - the amount, at least 3", the ability
     routine reading the amount at the effect's +10Fh, as PROBE_GRACE_ABILITY shows). Nothing in
     the game adds effect 68 (no record has it), so it is added by code: 76442h (598:3Eh, TU_STUB
     428Fh) takes (target, caster, spell, effect, time dword, amount byte) - DSCLOG's tu_site
     already calls it for Afraid. Site: 7A9ABh "mov si,[bp+8] / mov al,[bp+0Ah]" (6 bytes, inside
     7A9A7h, every hit power): with the rule, when the power is 172 and the attacker's kind 15, or
     173 and kind 13, add Weakened (amount 1, 2d4 x 600 s, the power as its spell), record it
     (a new KIND for the dice log: "Shadow drains 1 STR from Gerakis: Weakened 2d4 = 5 turns, STR
     17 -> 16"), and set AL to an unused bit (8) so the game queues nothing. ~100-120 bytes; the
     same helper serves the spells report's Chill Touch (Weakened 1) and Cause Disease (1d4).
   - To check in DOSBox: that the creature's STR (+22h) is recomputed when the effect is added
     and when it ends, and that several Weakened effects add up (each hit its own entry; the
     effects table holds 0C0h). A rest ends it (8 hours pass; the rest also puts STR back from the
     sheet unless Diseased, 8091Ch-8095Fh).
   - Look box: monsters.SPECIAL_ATTACKS (bits 2, 3) to say "1 STR drained (2d4 turns)" with the rule.
6. **Djinn: invisibility and illusions** - no data route (no special-action entry casts on the
   caster itself; 5A99Eh aims at a foe). DSCLOG, medium: give the Djinn an unused kind (e.g. 39,
   props 0, class 0) and, at its first turn of a fight (the turn-start site VEC_MOVE, or the
   special-action pick 5A90Fh), add Improved Invisibility (Invisible 23, timed, as spell 46) and
   Mirror Images (25, charges, as spell 19: "illusions") to itself through 76442h, once a fight.
   ~80 bytes + a dice log line. The manual is vague ("ability to use illusions and become
   invisible"); AD&D's djinni casts invisibility and illusions at will, MR nil.

## 2. Dual-classing

**The manual:** p. 12 (the menu before adventuring): "DUAL is only available when viewing a human
character, because only humans may become dual-classed. **You must be at least third level in your
current class before you can dual class.** Selecting this option allows you to choose a new class."
p. 13 repeats it without the level. p. 21: "A dual-class character is one who starts in a single
class, advances to a moderate level, and then changes to a second class, starting all over again
from level one. The benefits and abilities of the first class are lost until he exceeds the level of
his first class in his second. The character can never again advance in that class. Only humans can
be dual-class characters. A human character may do this process twice, potentially allowing a total
of three classes." The manual says nothing of 15/17 ability scores.

**What the game enforces:**

- The menu (70CE4h and 70F03h, the two portrait menus): DUAL (DS:1BBBh) is offered only if the
  sheet's first level (+24h) is **2 or more** and the race (+18h) is human (1).
- The DUAL window (866C7h) greys each class 1-17 by **86E94h(member, class)**, which returns 1 only if:
  1. human (86EB2h);
  2. the current class's (+21h) prime requisite on the creature (+22h + ability) is **15+** (86EFCh);
  3. the new class's prime requisite is **17+** (86F31h);
  4. the third class slot (+23h) is empty (86F43h): at most two changes, three classes;
  5. the current class level (+24h) is **2+** (86F58h);
  6. the new class is in no group the character already has (86F62h-86F9Ah; groups 40B1h:24h +
     class: priest 1 for clerics and druids, warrior 2 for fighter, gladiator and rangers, wizard 4,
     psionicist 8, rogue 16): no fighter -> ranger, cleric -> druid;
  7. a ranger (13-16) needs a good alignment (LG, NG, CG: 86FA9h-86FDDh); a druid (5-8) true
     neutral (86FE2h-86FFCh).
  "NO OTHER CLASSES AVAILABLE" (DS:3075h) when none passes.
- One prime requisite a class, from 38D4h:0180h + row x 3 (the row from 38D4h:00CAh + class x 2;
  the same table the creation screen's game code read, which least_scores.asm replaced for creation
  only): cleric WIS, druid WIS, fighter STR, gladiator STR, preserver INT, psionicist WIS, ranger
  WIS, thief DEX. The manual's primes (pp. 22-24): ranger STR, DEX, WIS; druid WIS, CHA;
  psionicist CON, WIS. So a ranger, druid or psionicist is checked on WIS alone, either way.
- The new class's ability requirements (the manual's creation minimums, game.CREATION_MINIMUMS) are
  not checked beyond that one prime (a druid at CHA 9, a gladiator at CON 10 are allowed).

**The mod:** gamepatch `dual_ban` (866FFh, VEC_DUAL_BAN: kits bar classes), `dual_spells` (86DE4h,
a preserver picks its two spells), `dual_kit` (86D90h, the kit menu after DUAL), and DSCLOG's
sleeping classes/kits (CU_DUAL, kit sleep). Nothing changes the level or ability checks.

**Gaps:** the manual's 3rd level (the game: 2nd, both at the menu and the window); multi-prime
classes checked on WIS only. AD&D 2e (from memory, unverified): 15+ in the old class's primes, 17+
in the new class's, humans only - the game has those for one prime each.

**Recommended:** (a) the 3rd level: 3 bytes of data in code, `cmp byte [es:bx+24h],2` -> 3 at
70CE8h, 70F07h and 86F5Ch (the immediate byte of each 5-byte compare; 1 byte each), in a
"manual" patch group; KITS.md's "2nd level or more" to change with it. (b) all primes: a DSCLOG site
in 86E94h replacing the two single-ability compares (86EFCh and 86F31h, 5 bytes each: `cmp byte
[es:bx+22h],0Fh/11h`) with a check of every prime (a small table: ranger STR/DEX/WIS, druid
WIS/CHA, psionicist CON/WIS) - small, ~60 bytes, two sites. Optionally the new class's creation
minimums too (the least_scores table already in the mod).

## 3. Resting

### What the game's rest does (8066Dh(mode [BP+6], hours [BP+8]))

The only call in DSUN.EXE: 62C2Ch, `rest(0, 8)` when the party uses a fire ring (objects 51Bh or
51Eh); the dice log's requests 0/1 name the script's rests (1, "the fallen get up", is mode 1).

- In a fight: "NO RESTING DURING COMBAT" (DS:2524h, 80689h), nothing else. 806A0h: 88:2914h
  (1D584h); "THE PARTY RESTS" (DS:253Dh).
- **Pass 1** (806BCh-8074Fh, each party member through A0:2E5h): 530:93h (62AB5h) **refills its
  wizard and priest slots** to the most (DS:4B09h/4B12h + member x 1Eh, from 500:52h); then
  **REST_SITE (806C3h, the mod's: records a REQUEST)**; mode 1, or Stunned/Out Cold -> Okay; for an
  Okay member, its cleric level (5B8:B1h = 7BE59h), druid level (5B8:B6h = 7BF3Bh) and class-11
  level (4F8:84h, unused after) kept as the party's best.
- **Pass 2** (80758h-80984h, each member): its effects as a bitset (598:25h = 76944h, into
  [BP-0Ah]); if the best cleric is 5th+: Cure Disease (96), Remove Curse (103), Remove Paralysis (105)
  cast on it through **809A2h(spell, target, caster, level) -> 5B8:20h (78BA8h)**, the game's cast,
  free (no slot); the same for the best druid, and at 7th+ Neutralize Poison (118); mode 1: Poisoned
  removed, Okay, HP at least 1; Acid (effect 1) removed (598:4Dh = 766ABh); an Okay member: **HP =
  the sheet's most (808AFh, `mov [es:bx],ax`)**, **PSP = the sheet's most (808F3h)**, STR back from
  the sheet unless Diseased (8091Ch-8095Fh); **Poisoned -> 1000 damage (80963h-8096Dh)**.
- After: 4E0:EDh (59E59h), **the clock +8 x 60 x 60 s** (5A8:57h = 78AC2h: DS 2C0h:35Bh += hours x
  60 x 60; a rest is 8 hours), D0:348h (27DB8h).
- Note (by reading; check in DOSBox): the poison check reads the bitset taken at 8075Dh, before the
  druid's Neutralize Poison, so the druid's cure seems not to save a poisoned member that rest.
- Timed effects end when the 8-hour clock jump is next processed (not in 8066Dh).
- Regeneration (227E5h, from the main loop when 300+ s passed, DS:1654h): PSP +1 a 300 s for every
  member; CON 20+: HP +1 a 300 s (the mod's REGEN_SITE, 228BFh, with RULE_HI_CON: AD&D's (26 - CON)
  x 600 s a point). After a rest it sees the 28,800 s: 96 HP at the game's rate, 8 at CON 20 with
  the mod's rule - today moot, as the rest has filled HP.

### Where the mod already hooks rest

REST_SITE (806C3h, dsclog.asm `rest_site`: a REQUEST record, REQ_REST, for the spell arrows),
REGEN_SITE (228BFh, `regen_site`, RULE_HI_CON), the dice log's "regenerates 1 HP (CON 22)"
(dicelog.py ~1859).

### Design: "priests cast their remaining cures at rest", then natural healing

Rule bit: a new RULES_HI bit ("rest as in AD&D"), off: the game's rest untouched. Mode 1 rests
(scripts restoring the party) keep the game's full refill.

1. **Pre-pass site, before any slot is refilled:** 80675h `mov word [bp-10h],0` (5 bytes,
   C7 46 F0 00 00, the rest's first instruction after its frame; no overlay fixup in it - not
   806A0h's `lcall 88:2914h`, whose segment word the overlay manager writes as it loads the code).
   The handler does the move, then, with the rule, mode 0 ([BP+6]) and no fight (the word the game
   tests at 80689h, selector 2B8h:19h), the pre-pass, for the party:
   - casters: Okay (status 1), no Feeblemind / No spell use / Paralyzed / Charmed (the 76944h bitset);
   - remaining priest slots: DS:4B11h + member x 1Eh + level (game.SLOTS_LEFT; used here, refilled
     by pass 1 anyway); known spells: the byte at far [DS:132Ah] + member x 138 + spell; Heal (202)
     by ns_priest_knows with PRIEST6 on; a Wilderness Avenger never its cures (av_heal); the spell's
     level from 3FB9h:019Ch + spell x 7;
   - caster level: 5B8:B1h / 5B8:B6h for that member (the game's own, as its rest uses);
   - order: (a) Neutralize Poison (118) on the Poisoned (this, unlike the game's free one, comes
     before the bitset: it saves them); (b) Cure Blindness (94) on the permanently Blind (Cause
     Blindness, 95, is -9999); (c) HP: the members (Okay, Stunned, Out Cold; Dying too if the heal
     routine lifts them - to check) by HP missing after the night's natural healing, most first;
     for each, the lowest-level cure whose average fits the wound (Cure Light 71, Serious 112,
     Critical 127, Heal 202 for 30+ missing), else the smallest left; stop when none is wounded or
     no cure slot is left. Cure Disease, Remove Curse and Remove Paralysis stay the game's free pass
     2 casts (a priest able to cast Cure Disease is 5th level, which gets them free anyway);
   - psionicists with Cell Adjustment (151; known: selector 2F0h + 77h + member x 22h + 13, bits
     3-7; PSP 5, the powers table 3FB9h:0000h + 13 x 8 + 1): on the Diseased first (no priest 5th+),
     then the wounded, while PSP last; PSP taken off by DSCLOG (the pass 2 refill gives them back);
     no power check out of a fight (or the game's 5D59Dh, an option);
   - each cast through **5B8:20h with 809A2h's arguments** (caster, target, spell, 0, &local, 0, 0,
     0, 8, 63h, level, the target's side +1Dh & 7): the game's own landing, as its rest uses -
     the cures' dice and kits (PROBE_CURE, Lifebinder, Healer), Heal's handler, effects removed by
     the records (-35, -8, -13), the dice log's spell lines - rather than writing HP and effects
     (that would duplicate every cure rule). Called through 5B8h's stub (42ABh) with th_far, and
     the way back to the rest overlay in a frame the overlay manager can fix up (ovr_back, as
     tu_site does): the spell's overlay can push the rest's out.
   - ~300-400 bytes of DSCLOG.
2. **HP site:** 808AFh `mov [es:bx],ax` (3 bytes: INT + site number; ES:BX the creature, AX the
   sheet's most, SI the member). With the rule and mode 0: HP + natural healing, at most AX, at
   least 1, instead of AX. Natural healing (AD&D 2e: 1 HP a day of rest, CON's hit point adjustment
   added after a week): proposed **1 + CON's hit point adjustment** a night (the game's table at
   40B1h:52h + CON, warriors' up to +4, others at most +2; none below 0), then CON 20+ regeneration
   for the 8 hours from the game's own 227E5h once the clock jumps (the mod's AD&D rates with
   RULE_HI_CON: 8 HP at CON 20 ... ; the game's own 96 without it). ~60-80 bytes.
3. **Kept as the game does:** slots (pass 1), PSP (808F3h), STR, the free cures, Acid, the poison
   death, 8 hours on the clock.
4. **Dice log:** two new record kinds: REST_CAST (caster, target, spell, slot level left) ->
   "At rest: Seneca casts Cure Light Wounds on Gerakis (1st-level slots: 2 left)", the game's heal
   then logged by the HP watcher as "regains 6 HP from Cure Light Wounds"; REST_HEAL (member, before,
   natural, CON part, after) -> "Gerakis rests 8 hours: +1, +2 (CON 16) = +3, now 33/40 HP". The
   regeneration after it shows as "(+8)" today: a line naming it (CON 20) would help. DICE-LOG.md,
   FEATURES.md and HOW-THE-GAME-WORKS.md "Resting" to change.
5. **Risks:** the overlay swap on the way back (above); casts at rest playing a cast's picture or
   sound (the game's own rest casts don't seem to: same arguments); a caster's level and spheres
   for a ranger or kit caster (5B8:B1h/B6h count clerics and druids only); a member Stunned or Out
   Cold at the pre-pass (Okay only in pass 1) must not be a caster; HP never left at 0 for an Okay
   member; saves made after a rest are ordinary (no memory edits).
