# Wake of the Ravager port: an audit of what came across

Daaki asked (2026-11-26), after the Elementalist's spell-slot cost turned out to be missing from the
sequel, for an independent check that everything the Obsidian mod does in Shattered Lands (SL) is
either in Wake of the Ravager (WotR) or knowingly listed as not yet there.

**The short answer:** the rules, fixes, screens and controls came across well and are mostly played.
**The kits did not.** About half of what the kits do is in the sequel, and the half that isn't is
mostly their spells, powers, hit dice and gear limits, which is where most kits keep either their gift
or their cost. Twelve of the 37 kits do nothing, or nothing but harm, in the sequel; about fifteen more
keep their gift and lose their cost. All 37 are offered on the sequel's KIT page with no warning, and
the docs for players don't say which work. Outside the kits there are a few real gaps (the lotulis,
double spear and trikal traits, Whirlwind and Restore Youth, a handful of controls, part of the dice
log), listed below by how much a player would notice them.

## How this was checked

Read against the code, not the port's notes: the combined test branch `claude/combined-playtest` (PR
#180) with the open PRs #198 to #204 merged on top in a scratch tree; #204, #206 and #207 read on their
own branches (they conflict with the rest on CHANGELOG.md and DSCLOG2.EXE only). For each feature:

- the SL side: FEATURES.md, KITS.md, WEAPON-SPECS.md, ITEMS.md, GAME-BUGS.md and DSCLOG's
  (`dos/dsclog.asm`) routines;
- the WotR side: DSCLOG2 (`dos/dsclog2.asm`) and its own "Not here (yet)" comments, the Loader's
  sequel modules (`ravager.py`: `PATCHES`, `RULES_PORTED`; `ravlog.py`: what `RavDiceLog._after_rolls`
  runs), and the play logs in `playtest/logs/*-ravager-*`;
- a mechanical cross-check: every DSCLOG routine name against DSCLOG2's, and every step of SL's
  `DiceLog._after_rolls` against `RavDiceLog._after_rolls`, each miss then read by hand.

Status words used below:

| Status | Meaning |
|---|---|
| **Played** | in the sequel and seen working in a play log |
| **Tests only** | in the sequel, covered by an emulated or unit test, never seen in play |
| **Untested** | in the sequel's code, neither played nor tested |
| **Partly** | some of the feature came across; what is missing is named |
| **Not ported** | nothing of it in the sequel |
| **Open PR** | ported on a PR not yet merged |
| **N/A** | Shattered Lands' story, art or data, or the sequel doesn't need it |

## The gaps, ranked by how much a player would notice

1. **Twelve kits do nothing, or only harm, in the sequel, and the KIT page still offers them.** Scholar,
   Arcanist, Shinobi, Healer, Lifebinder, Mind Bender, Kineticist, Titan Mind, Spirit Caller and
   Wasteland Seer have no working part at all; the Poisoner keeps only its weapon-spec limit (no
   poison); the Battle Mage keeps its warrior THAC0 and expertise but can't hold its chosen weapon
   unless a preserver could anyway, has no d6 hit die, can't wear leather or cast in it, and is stopped
   by a hit like any preserver. A player who makes one of these in the sequel gets a plain character
   with a kit's name on it. ([The kits, one by one](#the-kits-one-by-one).)
2. **About fifteen kits keep their gift and lose their cost**, because no gear limit and no spell or
   PSP cost came across: the Ravager wears plate and a shield and shoots; the Twin-blade and Brute hold
   anything; the Stalker, Assassin, Shadowblade and Poisoner wear any armour; the Seeker and Grove
   Warden ignore their sphere's weapons; the Battle Dancer, Ghetto Fighter and Rescuer carry shields;
   the Mind Warrior has full PSP; the Crusader keeps every spell slot; the Wilderness Avenger keeps its
   healing spells; the Justifier and Seeker cast from the plain ranger's slot table. This is the
   Elementalist's case, many times over, and nothing in the port's notes said so as plainly.
3. **The lotulis's and double spear's second foe and the trikal's trip and reach are not in the
   sequel**, though the sequel has its own Lotulis, Double Spear and Trikal and a specialist can pick
   them. Only WEAPON-SPECS.md says so; the port plan doesn't list them at all.
4. **Whirlwind and Restore Youth were decided in (2026-11-19) and are not ported.** Nothing in the
   sequel's code adds them; the plan's table still says "are added". With them go the Healer's two
   6th-level cosmos spells and aging's one cure.
5. **The docs promise sequel behaviour that isn't there.** KITS.md's "Past 13th level" (from #199)
   describes the Seeker's, Shinobi's and Justifier's slots past 13th, a Spellarcher's arrows at +3 and
   the Elementalist's 7th-level slot as the sequel's, but the sequel has none of the base those rows
   build on. The Options tab's Kits switch and KITS.md never say that kits are partly in the sequel.
   ([Docs that overstate](#docs-that-overstate).)
6. **Controls a player uses all the time are missing in the sequel:** dragging the map with the mouse
   wheel, the view in fights (it still drifts after every walker), the pointer in scenes and where it
   starts, the whole party in view after a load or fight, and steady pace. None is listed as "not
   ported" in the plan's progress table (they appear only in its first list of what goes in).
7. **The dice log is thinner in the sequel**: no lines for an effect starting or ending, PSP spent or
   kept up, or ability scores changing (`RavDiceLog._after_rolls` doesn't run `effect_changes`,
   `psp_changes` or `ability_changes`); the "Arrows: 17 left" and "Out of arrows" labels are missing; the
   item report (an item vanishing) never runs; and the freeze report has no record of where the game was
   (DSCLOG2 leaves DSCLOG's TICKS fields zero).
8. **Smaller rule gaps**: a lock a thief failed can be tried again at once (SL's LOCK_BARRED; DSCLOG2's
   header says "none here"); a new character's starting weapon isn't made its first weapon spec's kind,
   its gear isn't fitted to its kit, and gear its class can't use isn't left behind (SL's
   `weaponchoice.finish_new`, `kit_gear`, `class_gear` are never run in the sequel); no weapon-spec
   picks after DUAL; the DUAL window doesn't grey classes a kit bars; a thri-kreen's extra chatkcha
   throw; Erdlu Claw counting as a +1 weapon; XP for high prime requisites; the creation screen's least
   scores.
9. **More saves (40 and QUICK)** in the sequel's LOAD/SAVE window: still the game's ten.
10. **GAME-BUGS.md, as PR #206 has it**, marks 13 engine fixes "not checked yet" in the sequel, and
    leaves four of SL's item fixes out of the sequel table (Alagorn's stories, the Sling +1, the Great Axe
    +3, the Quicksilver Glove) without saying whether they apply.

A possible bug, not a gap, found on the way: **a Justifier of 8th or 9th ranger level** has the plain
ranger's first priest slot (its own table, which starts at 10th, isn't ported) and a casting level of
its ranger level less 9, which DSCLOG2's RANGER_LEVEL clamps to 0 and the caster-level routine's
`sub dx,9` (site 61, KIT_RANGER_CAST) makes negative. What a spell does at caster level 0 or below
hasn't been seen. Unplayed; worth one look when the kits' slots are ported.

## The kits, one by one

What DSCLOG2 has for the kits (its KITS section, 2026-11-26): AC, to hit, damage, attacks a round, the
weapon specs' kit parts, saves, thief skills, from behind and backstab, movement, the two-weapon
penalty, initiative, the Seeker's and Justifier's casting level, the Elementalist's second sphere, the
KIT page at creation and the kit menu after DUAL, and the Effects screen's kit lines. Its own comment
lists what it hasn't: "spell slots, casting levels, PSP costs, cures, a spell's damage, spells known,
poison, arrows, gear (KIT_FORBIDS, KIT_ALLOWS), hit dice". Two of those have come since in part (the
Seeker's and Justifier's casting level; the Elementalist's slots on #207). The Loader's side for the kits
in the sequel (`_kit_tick`: the dance, Wild Fighting, under the open sky, the Swashbuckler's bad luck)
is in; its new-character side (`kit_gear`, `cosmos_spells`, `avenger_heals`) never runs.

Played means seen in `playtest/logs/2026-11-25-ravager-kits.md`, `-kit-choice.md`, `-sphere.md`,
`-thieves.md` or `2026-11-26-ravager-high-levels.md` / `-own-party.md`. The emulated tests
(`tests/test_ravkits.py`) cover KIT_IS, the thief-skill table, expertise's attacks, the rangers' drop,
KIT_MELEE, the tables and the Wanderer's spells; the other kit routines have no test of their own in
the sequel.

| Kit | Gives (in WotR) | Costs (in WotR) | Overall |
|---|---|---|---|
| Myrmidon | polearm spec, mastery: **played** (specs) | −4 vs charms: tests only (the charm list); initiative 2 worse: **played** | **Ported**; its starting polearm not given |
| Sentinel | AC 2 with a shield: untested | −1 saves vs spells, −1 to hit without shield: untested | **Ported, untested** |
| Ravager | +1 hit/damage, base AC: **played** | no missile, no shield, leather only: **not ported** | **Gift only** |
| Arena Champion | +1/+1, AC 1 with shield: untested | −1 to hit without: untested | **Ported, untested** |
| Twin-blade | no two-weapon penalty in light armour: untested | no shield, no two-handed: **not ported** | **Gift only** |
| Brute | +2 with two-handed melee: untested | two-handed melee only: **not ported** | **Gift only** |
| Stalker | +2 move: **played**; +15 hide/silent, not halved indoors: untested | leather only: **not ported** | **Gift only** |
| Justifier | spec made specialization: **played**; two weapons in any armour: untested; casting level −9: tests only | its own slot table (1 at 10th): **not ported** (gets the ranger's) | **Partly** (see the possible bug above) |
| Seeker | priest slots from 6th: **not ported**; casting level −5: tests only | sphere weapon limits: **not ported**; no bow expertise: untested | **Partly**: no early slots, no limits |
| Swashbuckler | warrior THAC0 with weapon of choice: untested | bad luck on thief skills: untested | **Ported, untested** |
| Assassin | backstab a step deadlier: **played**; hiding not halved in daylight: untested | −15 pick pockets/locks: tests only; light armour: **not ported** | **Partly**: armour limit missing |
| Shinobi | preserver spells from its list: **not ported** | spells only its own from scrolls, few weapons, light armour, no shield: **not ported** | **Nothing**: a plain thief |
| Scholar | more spells learnt: **not ported** | −1 to hit (and spells' to hit): **not ported** | **Nothing** |
| Battle Mage | warrior THAC0 and expertise: tests only (expertise); casts after a hit, d6 hit die, light armour and casting in it, its weapons allowed: **not ported** | one slot fewer, nothing in the off hand: **not ported** | **Partly, and broken**: its expertise is with weapons it may not hold |
| Arcanist | spells a level higher: **not ported** | d3 hit die: **not ported** | **Nothing** |
| Elementalist | second sphere's spells: **played**; its weapons: **not ported** | slots a level behind: **open PR #207** (tests; not played for an Elementalist) | **Partly** (whole once #207 merges, but for the weapons) |
| Healer | cosmos spells, cures +1 a die: **not ported** | water only: **played** (KIT page); never harming spells, no off-hand weapon: **not ported** | **Only the cost of water**: a plain water cleric |
| Crusader | warrior THAC0, expertise, extra attacks: tests only (expertise) | one slot fewer: **not ported** | **Gift only** |
| Grove Warden | AC by druid level: untested (Thy'rokh's version on #207: played) | sphere weapon limits: **not ported** | **Gift only** |
| Lifebinder | cures a die more: **not ported** | blunt weapons only, never harming spells: **not ported** | **Nothing** |
| Wanderer | +3 saves vs fire and cold: tests only (the spell list); half damage from them: **not ported** | AC 1 worse: untested | **Partly**: cost in, half the gift |
| Mind Bender | telepathy 2 PSP less: **not ported** | psychokinesis 2 more: **not ported** | **Nothing** |
| Mind Warrior | warrior THAC0, expertise: tests only | a fifth fewer PSP: **not ported** | **Gift only** |
| Kineticist | psychokinesis 2 PSP less: **not ported** | telepathy 2 more: **not ported** | **Nothing** |
| Battle Dancer | the dance, two weapons in light armour: **played** | long swords and bows only, no shield: **not ported** | **Gift only**; its starting second sword and bow not given |
| Shadowblade | +10 hide, +5 silent: tests only (table); hides beside an enemy: untested | −10 pick pockets: tests only; no shield, light armour: **not ported** | **Partly**: gear costs missing |
| Military Scout | skills, initiative, missiles outdoors: **played** | −5 under a roof: **played**; never backstabs: **played** (one backstab taken back) | **Ported** |
| Wilderness Avenger | +1 hit/damage: untested; Cause spells stronger: **not ported**; hides as a ranger: untested | no healing spells: **not ported** | **Gift only** (part of it) |
| Rescuer | +2 move: untested; cures +1 a die: **not ported** | from behind +1 not +2: untested; no shield: **not ported** | **Partly** |
| Ghetto Fighter | dagger +1/+1, two daggers easier, skills: **played** | −5 traps, −1 with other weapons: **played**; no shield: **not ported** | **Partly**: shield allowed |
| Wayfinder | Path-finder initiative, skills: untested (table: tests) | −10 pick pockets: tests only | **Ported, untested** |
| Spellarcher | spell arrows cast on a hit: **played** (transferred arrows); making arrows on USE, their +1 to +3, the Fine Bow's +1: **not ported** | bow-only spec: untested; no armour, helm or shield: **not ported** | **Partly**: no new arrows, ever |
| Titan Mind | psychometabolism 2 PSP less: **not ported** | telepathy 2 more: **not ported** | **Nothing** |
| Poisoner | first hit poisons: **not ported** | dagger or short sword spec only: untested; light armour: **not ported** | **Cost only** |
| Spirit Caller | cleric spells 2 levels higher outdoors: **not ported** | 1 lower indoors: **not ported** | **Nothing** |
| Wasteland Seer | druid spells higher, powers cheaper outdoors: **not ported** | the reverse indoors: **not ported** | **Nothing** |
| Wild Fury | Wild Fighting's attack and +3 damage: untested (Gerakis's on #207: played) | −3 to hit, AC 3 worse: untested | **Ported** |

Across all kits:

| Kit feature | Status |
|---|---|
| The KIT page at creation, the kit byte | **Played** |
| The kit menu after DUAL, its bans | **Played** |
| A kit asleep after DUAL, waking | Untested |
| The DUAL window greying classes a kit bars | **Not ported** |
| A kit's hit die or PSP rolled again when it is chosen; at each level up | **Not ported** |
| Starting gear fitted to the kit (`weaponchoice.kit_gear`) | **Not ported** (never run in the sequel) |
| The Effects screen's kit lines and pages | **Played**; the Shinobi's READ LANG. line not ported |
| The dice log naming a kit's part | **Played** (to hit, initiative, saves); the kits' parts of the DAM lines **not ported** |
| Gear a kit forbids or allows (KIT_FORBIDS, KIT_ALLOWS) | **Not ported** |
| Spell slots (Battle Mage, Crusader, Elementalist, Seeker, Justifier, Shinobi) | **Not ported**, but the Elementalist's on **open PR #207** |
| Casting level (Arcanist, Spirit Caller, Wasteland Seer, Shinobi) | **Not ported**; Seeker's and Justifier's **tests only** |
| PSP costs and PSP (Mind Bender, Kineticist, Titan Mind, Wasteland Seer, Mind Warrior) | **Not ported** |
| Cures and Cause spells' dice (Healer, Lifebinder, Rescuer, Wilderness Avenger) | **Not ported** |
| Spells never known, spells granted (Healer, Lifebinder, Wilderness Avenger, Healer's cosmos) | **Not ported** |
| Casting after a hit (Battle Mage) | **Not ported** |
| The Poisoner's poison, spell arrows made, the Fine Bow | **Not ported** |
| Past 13th level (#199): Ravager AC to 0, experts' 5/2, casting caps | Ravager AC and 5/2 **played**/tests; the slot rows **not applicable yet** (no kit slots in the sequel) |

## The character sheet (72 bytes)

Daaki's rule is that per-character data lives in the sequel's sheet. It does:

| SL data | Sequel sheet | Status |
|---|---|---|
| Kit byte (two bits a class place, OWN_BIT 40h, Friends known 80h) | +3Dh | **Played** (the game's two sound words read by their low byte only, `sound_3c`/`sound_3e`) |
| Elementalist's second sphere, new spells known (bits 3-7) | +3Fh | **Played** |
| Age | +41h (a byte the sequel never reads) | **Played** |
| Weapon specs, starting roll, flag bits (SL +14h to +16h) | +42h to +44h | **Played** |
| Four more weapon specs past SL's levels | +45h to +47h (#199) | **Played** |
| SL's +0Eh, +0Fh, +3Ch | none | **N/A**: the game's own fields, not the mod's |

Nothing the mod needs per character lives outside the sheet in the sequel. The pockets and locks a
thief was caught at stay the Loader's memory of a save, as in SL. Nothing is missing here.

## Rules

Characters, weapons and armour, magic: everything in `RULES_PORTED` was played (each row of the port
plan's progress table has its log). The only gaps:

| Rule | Status |
|---|---|
| Class restrictions | **Played**; a new character's gear its class can't use isn't left behind (`class_gear` never runs) |
| Multiclass HP, hit dice best of two, rolled scores, AD&D's tables, CON, dual-classing, ages, level cap by XP | **Played** |
| The creation screen's dice log of each try (RL_TRY, 4d4) | **Played** (DSCLOG2's site 81; DEVELOPMENT-RULES.md's "not ported" is out of date) |
| Ages: Restore Youth curing magical aging | **Not ported** (the spell isn't in the sequel) |
| Two weapons, half-giants' two-handed weapons, creature size, held targets, helms, item saves, rings and cloaks of protection | **Played** |
| Weapon traits: cahulaks, stinkpots, polearm reach | **Played** |
| Weapon traits: lotulis and double spear's second foe, trikal's trip and reach | **Not ported** |
| Rangers' casting level, preservers' INT, spell save, DEX vs fire/cold/electricity, Enlarge, spells roll to hit, resting | **Played** |
| Thieves as in AD&D: the table, the backstab's dice | **Played** |
| Thieves as in AD&D: a failed lock waits for a level | **Not ported** (LOCK_BARRED: DSCLOG2's header leaves it zero) |
| Hiding in shadows to backstab, Elvenkind, worn cloak/boots/belt | **Played** |
| Picking pockets | **Open PR #204** (played); a cleric/thief's purse beside Turn Undead not ported |

## Spells and psionics

| Feature | Status |
|---|---|
| SL's spells and monsters as the manual has them (`gamepatch.SPELLS_MANUAL`, 49 patches) | 33 **ported** (most played, the rest in SPELL_FIXES' records); Bestow Curse, Ironskin, Free Action and the paralysis words **N/A** (the sequel's own, or Daaki's choice); 9 are SL monsters (Babau, Blue Slaad, Styr, Djinn, Tari, shadows): **not ported**, and whether the sequel has those monsters isn't recorded |
| The six new wizard spells | **Open PRs #200 to #202** (cast, learnt, books: played); a new spell's book has no INT roll or dice-log line; Erdlu Claw isn't a +1 weapon |
| 6th-level priest spells: the sequel's own eight | In, as the sequel's; "the mod's rules where they differ to be checked one by one" (the plan): **not checked** |
| Whirlwind and Restore Youth | **Not ported** (decided in, 2026-11-19) |
| Preservers' first spells, psionic powers at creation | **Played**; a Scholar's extra spell not ported |
| Spells kept on the Effects screen, Psionic Blast's wounds | **Played** |
| Defilers' scrolls | **N/A** by decision ("later, if wanted": the sequel has defilers) |

## Items

| Feature | Status |
|---|---|
| Every SL item with the transferred party (effect groups B to G: protection, robes, Veiled Robe's slots, girdles, amulet, Elvenkind, Boots of Speed, the Tome) | **Played** (party-transfer report) |
| The Fine Bow's +1 to hit | **Not ported** (no FINE_HIT in DSCLOG2: it is a plain bow in the sequel) |
| The mod's plain weapons, Bone Helm, 14 magic weapons for every spec placed in a new game | **Played** (#191, #193) |
| Spellbooks of the new spells at Notaku's | **Open PR #202** |
| The mod's other new items (Bracers of Defense, robes, Elvenkind, thief belts/boots/cloaks, the Warden's Plate...) in a new sequel game | **N/A** by decision: they come only with a transferred party |
| Unique Ravager items kept to Ravager | Kept: nothing goes the other way but the weapons backport Daaki approved |
| Magic items' shine in shops | **Open PR #203** (played) |

## Weapon specs

| Feature | Status |
|---|---|
| Specialization, mastery, grand mastery, the 22 kinds, the sequel's own weapons mapped | **Played** |
| Picked at creation (the weapon window) | **Played** |
| Picked at a level up, past 13th (#199) | **Open PR #199** (played) |
| Picked after DUAL | **Not ported** |
| A kit's own weapons offered first | **Not ported** |
| The starting weapon made the first pick's kind | **Not ported** (a new fighter keeps the sequel's long sword) |
| A thri-kreen's extra chatkcha throw (OWN_THROWS) | **Not ported** |
| The sequel's own party's specs | **Open PR #207** (played) |

## The Loader and its Options

| Feature | Status |
|---|---|
| Play Wake of the Ravager, the folder, the patched copy | **Played** |
| Window size, picture, game speed | **In** (`write_conf_wotr` writes the same display and CPU lines) |
| Steady pace | **Not ported** (no PROBE_PACE in DSCLOG2; the switch does nothing for the sequel) |
| Music device | **N/A** (the sequel's music is CD audio) |
| DOSBox-X as the engine | **Open draft PR #185** |
| Rule switches (helms, half-giant hands, best hit die, kits, new spells) | **In**, through RULES_PORTED; nothing tells the player that "Kits" is only partly in the sequel |
| In-game switches (Look box, names over figures, chance to hit, squares, F10, Alt) | **Played** |
| Quick save, quick load, autosave, named saves | **Played** (the sequel's ten slots) |
| More saves (40 and QUICK) | **Not ported** (needs the save window's pictures made) |
| More characters | **N/A** (the sequel's roster holds 40) |
| Characters, Spells, Memory, Dialogue, Journal tabs | **Played**; the journal doesn't follow the sequel's saves |
| Crash report | Untested in the sequel |
| Freeze report | **Partly**: no record of where the game was (DSCLOG2's TICKS zero) |
| Item report (an item vanishing) | **Not ported** (`itemwatch.check` never runs) |

## Screens, controls and graphics

| Feature | Status |
|---|---|
| Combat log, Look box, names over figures, chance to hit, squares in reach, F10, Alt | **Played** |
| Names over figures: arrows left, out of arrows | **Not ported** (the sequel's ammunition code not found) |
| THAC0, saves, thief skills on the inventory; View Character; the creation screen; spell slots on USE; charges in item boxes; the Effects screen; what a scroll says; no manual check | **Played** (no manual check: not yet seen in play) |
| Tab, Enter and the rings; T and Shift+T; S; M, U, I | **Played** |
| Scrolling the map (wheel drag) | **Not ported** |
| The view in fights | **Not ported** |
| The pointer in scenes, and where it starts | **Not ported** |
| The whole party in view | **Not ported** |
| Shadows, dust, see-through figures, shine | **Open PR #203** (played; an invisible creature not seen) |
| Spells on the ground | **N/A** (the sequel's own pictures), but Whirlwind's funnel with Whirlwind |
| Elves' and half-elves' figures, what the party wears | **N/A** (SL's figure art; Codex's redraws are a separate job) |

## The dice log

| Lines | Status |
|---|---|
| Attacks, damage, saves and their modifiers, spells' damage, initiative, turns, hiding, kits' parts, creation tries | **Played** |
| An effect starting or ending | **Not ported** (`effect_changes` never runs in the sequel) |
| PSP spent and kept up; ability scores changing | **Not ported** (`psp_changes`, `ability_changes`) |
| The DAM lines' kit parts; Hasted and Slowed attacks in the mod's DAM lines | **Not ported** |
| A Battle Dancer's first swing of the round she starts dancing | Known to fall back (the plan) |

## The game's bugs (GAME-BUGS.md, PR #206)

PR #206's table for the sequel matches the code: 22 fixed (most played), 3 not needed, 8 not yet, 13
not checked yet. The ones a player would notice among "not yet" are the quiver running dry, the DAM
lines of a hasted or slowed character, View Character's DAM line with a weaker material, XP for high
prime requisites, and the creation screen's least scores. The four item fixes (Alagorn's stories, the
Sling +1, the Great Axe +3, the Quicksilver Glove) are left out of the sequel table without a word;
they are SL data, so they likely don't apply, but the table should say so. The six sequel-only bugs it
lists are fixed and played.

## Docs that overstate

- **KITS.md**, "Past 13th level" (on #199): its rows for the Seeker's and Shinobi's slots, the
  Justifier's, the Spellarcher's +3 arrows and the Elementalist's 7th-level slot describe the sequel,
  where none of those kits' spells or arrows work yet. The Battle Mage's row is the only one that says
  "not yet".
- **KITS.md** as a whole and the **Options tab's Kits line** say nothing about the sequel; a player
  reads that a Shinobi casts preserver spells and makes one in the sequel.
- **The port plan's progress table** marks "Customization: kits" as "in (fights and play), played"; its
  "Not ported" list is accurate but sits at the end of a long cell. It also still says Whirlwind and
  Restore Youth "are added" (and DEVELOPMENT-RULES.md lists RL_TRY as not ported, though it is in), and doesn't list the lotulis, double
  spear and trikal traits, the four missing controls, or steady pace as not ported.

## What to do, in order

These are recommendations for the port thread; nothing was changed here.

1. **Say it now.** Until the kits are whole, mark in KITS.md (a "In Wake of the Ravager" column or
   section) and on the sequel's KIT page or Options line which kits work there; or grey the twelve
   that do nothing out of the sequel's KIT page. Correct KITS.md's "Past 13th level" rows.
2. **Gear limits (KIT_FORBIDS, KIT_ALLOWS)**: one port fixes the cost of about twelve kits at once and
   lets the Battle Mage and Elementalist hold their weapons. Then the kit starting gear (`kit_gear`).
3. **Spell slots** for the Battle Mage, Crusader, Seeker, Justifier and Shinobi beside #207's
   Elementalist (the same ADND_SLOTS site), and look at the Justifier's caster level 0.
4. **PSP costs and PSP**: five kits, one routine each way (use and upkeep).
5. **Casting level, cures, spells known**: the Arcanist, Spirit Caller, Wasteland Seer, Healer,
   Lifebinder, Wilderness Avenger, Rescuer.
6. **Kit hit dice** (Battle Mage, Arcanist) and the Battle Mage's casting after a hit.
7. **The Shinobi's spells, the Poisoner's poison, spell arrows made**: the biggest single pieces, last.
8. Outside the kits: the lotulis/double spear/trikal traits; Whirlwind and Restore Youth; the four
   controls and steady pace; the dice log's effect, PSP and ability lines; the lock rule.
9. Finish GAME-BUGS' 13 "not checked yet" and say what the four item fixes mean for the sequel.
