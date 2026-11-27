# Changelog

What changed in Obsidian Edition (called Templar's Ledger up to 1.2.0), pull
request by pull request, newest first: the record for developers and testers.
For what a release brings, read its notes, in [`release-notes`](release-notes);
for every change from the original game in one page, [the patch
notes](PATCH-NOTES.md). Pull request #73 (2.12.0) and older are in [the
archive](CHANGELOG-archive.md).

**Entries are kept short from now on:** what changed and why, in a few lines a
pull request. The detail (addresses, byte counts, test names) is in the commits
and the DEVELOPMENT pages, and research in `reports/`. The longer entries below
were written before this rule and are kept as they are.

**Headings.** Work on the branch `obsidian-edition` not yet merged to `main` is
under "## Unreleased (branch `obsidian-edition`)"; when its pull request is
merged, that heading becomes "## Pull request #N (merged DATE)", with "merged
DATE" a link to the pull request. A release's entry starts with the line
"Obsidian Edition X", its release notes linked after it in brackets.

**Sections**, each a bold line: **New**, **Changed**, **Fixed**, **Docs** (the
documentation) and **Dev** (tests, tools, the playtest kit, the build). A label
may name the part it is about (**Fixed: the game**, **Fixed: DSCLOG**) or say
where the changes came from, in brackets.

Releases, newest first (2.12.0 and older in the archive):
[2.19.2](#pull-request-127-merged-2026-11-20) (#127), [2.19.1](#pull-request-124-merged-2026-11-20) (#124), [2.19.0](#pull-request-119-merged-2026-11-19) (#119), [2.18.0](#pull-request-95-merged-2026-11-16) (#95), [2.17.1](#pull-request-94-merged-2026-11-11)
(#94), [2.17.0](#pull-request-93-merged-2026-11-11) (#93),
[2.16.1](#pull-request-91-merged-2026-11-11) (#91), [2.16.0](#pull-request-90-merged-2026-11-11)
(#90), [2.15.0](#pull-request-89-merged-2026-11-10) (#89),
[2.14.1](#pull-request-88-merged-2026-11-08) (#88), [2.14.0](#pull-request-87-merged-2026-11-07)
(#86 and #87), [2.13.4](#pull-request-85-merged-2026-11-02) (#85),
[2.13.3](#pull-request-84-merged-2026-10-31) (#84), [2.13.2](#pull-request-83-merged-2026-10-30)
(#83), [2.13.1](#pull-request-82-merged-2026-10-30) (#82),
[2.13.0](#pull-request-81-merged-2026-10-30) (#81), [2.12.5](#pull-request-80-merged-2026-10-30)
(#80), [2.12.4](#pull-request-79-merged-2026-10-29) (#79),
[2.12.3](#pull-request-76-merged-2026-10-29) (#76), [2.12.2](#pull-request-75-merged-2026-10-29)
(#75), [2.12.1](#pull-request-74-merged-2026-10-27) (#74),
[2.12.0](CHANGELOG-archive.md#pull-request-73-merged-2026-10-27) (#73),
[2.11.0](CHANGELOG-archive.md#pull-request-69-merged-2026-10-26) (#69),
[2.10.0](CHANGELOG-archive.md#pull-request-67-merged-2026-10-26) (#67),
[2.9.0](CHANGELOG-archive.md#pull-request-63-merged-2026-10-26) (#63),
[2.8.0](CHANGELOG-archive.md#pull-request-61-merged-2026-10-25) (#61),
[2.7.2](CHANGELOG-archive.md#pull-request-59-merged-2026-10-24) (#59),
[2.7.1](CHANGELOG-archive.md#pull-request-58-merged-2026-10-23) (#58),
[2.7.0](CHANGELOG-archive.md#pull-request-56-merged-2026-10-23) (#56),
[2.6.0](CHANGELOG-archive.md#pull-request-54-merged-2026-10-21) (#54),
[2.5.0](CHANGELOG-archive.md#pull-request-51-merged-2026-10-19) (#51),
[2.4.0](CHANGELOG-archive.md#pull-request-50-merged-2026-10-16) (#50),
[2.3.0](CHANGELOG-archive.md#pull-request-47-merged-2026-10-15) (#47),
[2.2.1](CHANGELOG-archive.md#pull-request-43-merged-2026-10-14) (#43),
[2.2.0](CHANGELOG-archive.md#pull-request-42-merged-2026-10-14) (#42),
[2.1.1](CHANGELOG-archive.md#pull-request-37-merged-2026-10-10) (#37),
[2.1.0](CHANGELOG-archive.md#pull-request-36-merged-2026-10-09) (#36),
[2.0.0](CHANGELOG-archive.md#pull-request-33-merged-2026-10-09) (#33),
[1.2.0](CHANGELOG-archive.md#pull-request-30-merged-2026-10-08) (#30),
[1.1.0](CHANGELOG-archive.md#pull-request-18-merged-2026-10-06) (#18),
[1.0.0](CHANGELOG-archive.md#pull-request-12-merged-2026-10-02) (#12).

## Unreleased (branch `obsidian-edition`)

Pull requests #146 to #268 (merged 2026-11-25 to 2026-11-27), by subject. Each entry names its
pull request; [the features page](obsidian-edition/FEATURES.md) and [Wake of the Ravager's
page](obsidian-edition/RAVAGER.md) have the detail.

**Docs: the sequel's creature figures as the game draws them** (branch `claude/ravager-creature-figures`)
- CREATURES.md's Wake of the Ravager figures are the pose each one's animation script stands in, not the
  picture's first frame: a redraw that adds its frames after the game's (Ptar, the Beasthead Giant, the
  village giants, Magnolia and the jann, the great elementals, the Magma Golem) showed the game's figure.
  *Redrawn* now means the figure shown differs from the game's; the four the redrawing kept say *the game's
  (kept)*; the Tarrasque shows its fight's figure; the colours are Tyr's map palette (no magenta).

**Docs: a readable priest spells picture, a shorter Ravager page** (branch `claude/docs-review-trims`)
- `new-priest-spells.png` shows the ten 6th-level priest spells' description boxes at full size, not ten
  whole USE screens shrunk to fit (1920x1600 to 592x840).
- RAVAGER.md's "The mod in the sequel": the 45-line kits entry split into kits, weapon specs, new wizard
  spells, the creation screen, the screens and choosing an enemy; the level cap and first spells entries
  cut to the sequel's own facts. The detail stays on KITS, WEAPON-SPECS and PLAYER-GUIDE, linked.

**Docs: Wake of the Ravager's side of the features, creatures and dice log pages** (branch `claude/ravager-docs-side`)
- CREATURES.md covers both games: the sequel's 198 creatures from its own data, each in the figure the mod
  draws (183 redrawn, marked), its size by the sequel's table and the cahulaks' answer as the sequel decides
  it (`doccreatures.write_ravager`). Six man-sized monsters named in `sizes.RAV_NAMES` (no change in play).
- Every FEATURES entry ends with a line saying whether the sequel has it. Its sequel-only passages (the
  sequel's own party, its quick saves, its named saves) moved to RAVAGER.md; the gaps found (the four
  controls, more saves, steady pace, the arrows left over an archer, the cahulaks sparing only by size) are
  on RAVAGER's "Not in the sequel yet". DICE-LOG.md has a sequel section.

**Changed: the sequel's no-speaker box and shop panel as Shattered Lands'** (branch `claude/portrait-empty-shop`)
- A message with no speaker (the XP at a fight's end) shows Shattered Lands' stone dark-sun emblem in the
  frame, where the sequel had a grey wash (its BMP 12000's frame 1, from the player's Shattered Lands, in
  the sequel's colours; the wash without one, or with `sl_interface` off).
- The shop's right-hand panel is Shattered Lands': the merchant's face in its frame at (252, 11), SELL
  under it and MORE alone at the bottom (WIND 13500's two buttons moved, the face's two shop patches
  pointed there; the item list was already at Shattered Lands' places).
- The panel's picture (BMP 13004, Shattered Lands' since `sl_interface`) keeps its shade: its 16 greys
  were rounded to the sequel's 7 (the top lighter, the foot darker); now each pixel takes the nearest
  of the sequel's colours near its own plus what its neighbours missed (Floyd-Steinberg,
  `ravui.DITHERED`), so the shade holds and the grain reads like Shattered Lands' (a 4 by 4 pattern,
  tried first, showed as a regular checker: the owner asked for the texture too).
- Played against Shattered Lands' own shop and the earlier build. Tests: `test_ravportraits.py`,
  `test_ravui.py`.

**Changed: the sequel's talk portraits at Shattered Lands' size** (branch `claude/ravager-portrait-size`)
- Wake of the Ravager's faces (72 by 72, frame drawn in) made Shattered Lands' 32 by 32 in a 48 by 46
  frame by `dsloader/ravportraits.py`: the faces in GPLDAT2.GFF (each start, from the game's own, the
  frame its own cut down), the empty frame's two pictures (BMP 12000) and the talk window (WIND 12500: 58
  high, the text at x 58, as Shattered Lands' WIND 3007) in RESOURC2.GFF, and five patches to the face's
  routine (88E67h) putting it at (8, 6), the shop's in the middle of its old place. The owner's ask.
  `RAV_SKIP=small_portraits` is the control. Played: Uhubito's and Notaku's talks, the opening talk,
  Notaku's shop, the first fight's XP message, against the control. Tests: `test_ravportraits.py`.

**Docs: the research recipes split by subject** (branch `claude/research-guide-split`)
- The playtest kit's research recipes (`playtest/RESEARCH.md`, 42,000 words in one page) are seven pages
  now: memory edits for a test, sounds and pictures, the game's code and other targets, and four on Wake
  of the Ravager (starting and driving it; its pictures and screens; its records, kits and saves; the port
  audit's notes). The text moved as it was; `RESEARCH.md` is their index, so old links still land, and
  every link into a moved section points at its new page.

**Fixed: weapons keep their material and kind in Wake of the Ravager; the bone great sword 11 lb in both games** (branch `claude/ravager-weapon-materials`)
- A party taken across lost five backported weapons' material: the metal great sword, lotulis and
  javelin, the obsidian lotulis and the bone great sword went as the sequel's one type of their kind (a
  water cleric's Bone Great Sword +1 an obsidian sword it couldn't wield, a fire cleric's Obsidian
  Lotulis +1 a stone one). They are now the mod's own types there (141-145, `ravager.MOD_TYPES` 44).
- The user's wider ask (every SL weapon kind and material in the sequel too): of SL's 337 weapon
  objects, 20 crossed with another material or kind by SSI's `ITEMS.BIN` pairs (bone Long Swords made
  obsidian, the Great Axe +3 obsidian, the Polearm +1 a double spear, Terror Blade stone...). Those pairs
  are dropped and the Loader makes the weapon in a sequel type of its kind and material
  (`ravtransfer.weapon_pairs`, `ravitems.weapon_type`); the sequel had no bone long sword, so SL's is
  added (type 146, `ravager.SL_EXTRA_TYPES`); its club, bow and sling get SL's wood and leather
  (`ravager.RAV_MATERIALS`; SSI's had none, so earth and water priests were refused them). An earlier
  transfer's object of the old type is made anew; saves already in the sequel are not touched.
- The bone great sword weighs 110 (11 lb) in both games (was 150, as the obsidian one).
- SL's darts (wood) go across as the mod's own darts (140), not the sequel's stone ones (43); `game.RAVAGER_TYPES`
  said 38 (of no material). Every backported Ravager weapon is now checked for kind and material on the real files.
- The sequel's item box named a Great Sword "Long Sword": the transfer's keepsakes' names began at 306, over the
  mod's last six (the Ravager weapons' Great Sword to Darts). They begin at 312 now (`ravager.KEEPSAKE_NAMES_FIRST`).
- Tests: every SL weapon object checked on the real files (`test_every_weapon_keeps_kind_and_material`),
  DSCLOG2's class limits on type 146, the materials. Played: logs/2026-11-27-ravager-weapon-materials.md.

**Docs: Wake of the Ravager's items, and pictures and gaps** (branch `claude/docs-pictures-sequel-gaps`)
- ITEMS.md has every item of Wake of the Ravager: its magic weapons, missile weapons, armour, worn and held
  items, scrolls and the like, and its plain weapons and armour by type and material, the mod's among them,
  each with where it is (from the sequel's data, the story's rewards from a play) and the sequel's own icon
  (`docicons --ravager`, which reads its PLNR and PLAN pictures); and what Shattered Lands' items become.
- Kalzith's talk and body pictures retaken with the class outfits.
- RAVAGER.md: the seven features the full review couldn't confirm in the sequel, settled from its patches:
  the Effects screen's click works there; more save pages, the 29-character roster, steady pace, the view
  in fights, the pointer in scenes and the whole party in view are on "Not in the sequel yet".

**Docs: the Options tab's reference in the README** (#268)
- "The Options tab at a glance" (every switch, its default and when it counts) and "Elsewhere in the
  Loader" moved from the player's guide to the README, after the Loader's window, where a player looks
  for the Loader; the links to it follow.
- The list of what is always on is kept once, in the features page's "Always on": the Options reference
  and the README's Loader paragraph link it instead of repeating it.

**Docs: the full docs review** (branch `claude/docs-review-full`)
- Fogbolt's picture retaken in play with the class outfits; the gear picture's caption names Gerakis a
  half-giant, not a mul.
- The README no longer says the game starts in GOG's DOSBox, and its two Linux lines (which
  contradicted each other) are one; the Options tab's Wake of the Ravager section is described whole.
- The sequel's magic weapons and spellbooks moved from the features page to Wake of the Ravager's page;
  that page now mentions the combat log in the game, and lists the mouse-wheel map scrolling as not in
  the sequel yet.
- The player's guide's "Quality of life" (a third copy of the features page) cut to links.
- Report: [the full docs review](reports/docs-review-full-2026-11-27.md).

**Fixed: the same item weighs the same in both games; the follow-up code audit** (#260)
- Shattered Lands' leather chest armour weighs 9.6 lb, as in Wake of the Ravager (the game's 75 lb, five
  times AD&D's whole suit), and the sequel's small things 0.1 lb, as Shattered Lands' (SSI's 1 lb). No
  rule reads either weight, so nothing plays differently. `test_item_weights.py` checks every item both
  games have against their real files; Dragonsbane stays apart (a metal sword in one, obsidian in the other).
- Report: [the follow-up code audit](reports/code-audit-followup-2026-11-27.md).

**Dev**: `ravitems.region_palettes`, the sequel's region palettes read once for the four modules that read
them; `launch._clear_end_files`; `test_dosboxx_pin.py` (the release and the test package bring the same
DOSBox-X).

**New: the kits on Wake of the Ravager's DAM lines and creation THAC0** (branch `claude/sequel-dam-lines`)
- The inventory's and View Character's DAM lines show the kits' part as Shattered Lands' do: a Ravager's 1 more
  damage, a Brute's 2 with a two-handed weapon, a Ghetto Fighter's 1 with a dagger, and a Battle Mage's,
  Crusader's or Mind Warrior's attacks with its chosen weapon (DSCLOG2's `DAM_KIT_MELEE`, `DAM_EXPERT`).
- The creation screen's THAC0 line has a new Scholar's 1 worse as soon as the kit is chosen or taken back
  (`CR_KIT_THAC0`); before, only after the next roll.

**New: the Scholar kit in Wake of the Ravager** (#270)
- A Scholar there is as in Shattered Lands: its THAC0 1 worse (from creation and every level up), one more
  spell on CHOOSE A SPELL at each preserver level up, and, made new, one more 1st-level spell for each of its
  preserver levels (DSCLOG2's `SCHOLAR_THAC0`, `SCHOLAR_LEVEL_UP`, `CR_SCHOLAR`).

**New: Wake of the Ravager with the in-game rolls, no Loader window; Show Save for its saves** (#264)
- **`Play Wake of the Ravager (in-game rolls).bat`** (`python -m dsloader play --ravager`) starts the sequel
  as `Play Dark Sun (in-game rolls).bat` does Shattered Lands: its folder found as for the Loader's button,
  the dice log unseen with the sequel's own rules and lines, a problem in a message box and `play.log`. The
  in-game-rolls start now makes its dice log by the helper the game loaded, as the window does.
- **`Show Save.bat`** (`python -m dsloader save FILE`) shows a Wake of the Ravager save's party too (its
  sheets read as the game wrote them, 42h, or as the Loader widened them, 48h).
- The follow-up code audit's P1 (the sequel figures zip) settled by the owner: it stays in the mod.

**Docs: the follow-up docs review** (#263)
- [Wake of the Ravager's page](obsidian-edition/RAVAGER.md#not-in-the-sequel-yet) now ends with what
  Shattered Lands has from the mod and the sequel doesn't yet, each checked against the code.
- The README says the in-game-rolls start and Show Save are Shattered Lands only; DEVELOPMENT-KITS no
  longer calls the Shinobi's casting, the arrows' cast sound and `ARROWS_FORBID` missing in the sequel.
- Report: [the follow-up docs review](reports/docs-review-followup-2026-11-27.md).

**New: DOSBox-X, the default engine** (#146, #178, #185)
- The Options tab's new **Engine** section chooses DOSBox-X or GOG's DOSBox 0.74. **DOSBox-X is the
  default whenever one is found**: the Windows release brings DOSBox-X's own 64-bit build in its
  `dosbox-x` folder, with its GPL licence and `SOURCE.txt`, and the source archive beside the zip;
  on Linux and macOS the player's own DOSBox-X (2025.01.01 or later; a path the player gives, its
  version shown, an older one refused) counts. GOG's DOSBox is used when none is found or when it
  is chosen; Restore defaults removes the choice; a found recompiled program goes before DOSBox-X
  unless DOSBox-X was chosen. **Played on Linux; on Windows the game starts under it with its
  music (2026-11-27) and a fuller play is under way; on macOS it is not yet run**
  ([known issues](obsidian-edition/README.md#known-issues)).
- With DOSBox-X the Loader writes it a whole configuration of its own and follows the game through
  DOSBox-X's memory file instead of its process's memory, so on Linux it needs no root and no
  ptrace setting. The game window's sizes, full screen, the four pictures, the three speeds
  (measured to walk as on 0.74: 8,000 on the normal core, 22,000 and 42,000 on the dynamic one)
  and the music device each have their DOSBox-X spelling; a new **soundfont file** setting plays
  the music through DOSBox-X's own FluidSynth (#146).
- **48 KB more upper memory under DOSBox-X** for DSCLOG: `[dos] umb end=FBFF` with the BIOS in
  16 KB (`rom bios allocation max` and `rom bios minimum size`), 192 KB in all (0.74: 128 KB)
  (#178).
- Wake of the Ravager starts in DOSBox-X too when it is the engine (#185).

**New: class outfits** (#205)
- Each party member is dressed for their class before any gear goes on: humans in their class's
  outfit (the mage in a plum mantle, the thief hooded, the psionicist in teal), dwarves, elves,
  half-elves (48 outfits each), half-giants, halflings and the mul in one for their whole class
  combination; thri-kreen and combinations outside the roster keep the game's figure ([what the
  party wears](obsidian-edition/FEATURES.md#what-the-party-wears)). The animated galleries are in
  `obsidian-edition/docs/class-outfits/`, left out of the release zip.
- **The creation screen's figure wears the class's outfit**: the small figure at the top shows the
  class outfit of the class (or classes) picked, for every race, and changes with each class, race
  or portrait click; with no class picked it is the game's own. The Loader writes the figure where
  the game reads it, and DSCLOG waits for it and draws the figure again (`creationfigure.py`,
  `FIG_WAIT`). Wake of the Ravager has no class outfits yet, so its screen is unchanged (#231).
- **The outfits keep their colours in every area**: they were drawn in palette entries each area's
  palette changes (in the desert the browns turned grey, the plum robes magenta, the teal red; in the
  slave pens the pinks dark red). Every pixel an outfit or gear adds is now drawn in the nearest
  colour no area changes (#230).

**New: Wake of the Ravager's weapons in Shattered Lands** (#149, #154, #157)
- Six of Wake of the Ravager's weapons the game has none of: a two-handed sword, the lotulis, the
  double spear and trikal (gladiators only, as in the sequel), the javelin and darts, each with a
  name and an icon of its own, sold in Teaquetzl and Kel's caravan. (Not the sequel's net.)
- Six weapon specs for them: the weapon window grows to four rows of six, the
  title under them, and the specs are stored in a new layout (v3) that keeps the first pick first;
  older saves read as before.
- Their traits, for a specialist: the lotulis' and double spear's last swing of a round goes to a
  second foe beside the wielder (the double spear's for 1 less), and a trikal hit trips a man-sized
  foe that fails a save against paralysis, which loses its next turn.
- The trikal reaches two squares, as a polearm does; a specialist throws the javelin (3/2, 2, 5/2
  a round by level) and darts (3, 4, 5) faster, as for the other missile weapons; and people of the
  like carry the new weapons: the arena's gladiators, one of Scar's henchmen, the Drajian Guards, a
  Templar in the pens, the Silt Runners, the White Sand Outlaws, Teaquetzl's Village Heroes and
  Elite Guards, and the pens' weapon rack (#154).
- The sequel's Darts +1, with a shining icon of its own, thrown by the defiler among the arena's
  champions.
- Metal ones of three of the sequel's weapons (a two-handed sword and a lotulis sold by Melkor in
  Gedron, a javelin on the slave pens' weapon rack in place of the obsidian one), and magic ones
  placed along the way through the game, the weaker early: Double Spear +1 and +2, Trikal +1 and
  +2, Lotulis +1 and +2, Great Sword +2 and +3, Javelin +1, each with a shining icon of its own
  ([the table](obsidian-edition/ITEMS.md#weapons)). A metal lotulis strikes a second foe as any
  lotulis (#157).
- Air clerics may use the javelins (a thrown weapon) and water clerics the darts (wood), as their
  spheres allow (the user's).
- An obsidian lotulis (a fire cleric's too) and a bone great sword (a water cleric's too), both
  sold by Melkor, and a +1 of each: the Obsidian Lotulis +1 on Dagger, the White Sand Outlaws'
  chief, the Bone Great Sword +1 on Dakaren at the Silt Sea (the user's).
- The sequel's weapons and the great axes (the game's Great Axe +3 too) take Wake of the Ravager's
  own inventory icons from the player's copy, recoloured to Shattered Lands' wood and each item's
  material; the magic ones shine in the colour the sequel gives its own (green, the water's blue or
  fire), not all in fire; without it, the Loader's own, the double spear, trikal and
  darts redrawn at the sequel's sizes (the user's).

**New: Wake of the Ravager, started from the Loader** (#148 to #249)
- **Play Shattered Lands** and **Play Wake of the Ravager** buttons at the top of the Loader's
  window, and `Play Wake of the Ravager.bat`, start either game with the mod (#156); a sequel start
  no longer repeats Shattered Lands' warning about what it left out (#197).
- **Taking the party across**: the Options tab's **Take the party to Wake of the Ravager...** puts a
  Shattered Lands save's party in the sequel's roster with every item, its effects, their kits,
  weapon specs and spells, and the time between the games (#151, #155; [taking the
  party](obsidian-edition/FEATURES.md#taking-the-party-to-wake-of-the-ravager)).
- **The mod's fixes, rules and displays ported to the sequel** (#148): the dice log, the combat log
  panel, Psionic Blast's imagined wounds (#172); weapon specialization (#158) and the spec pick at
  creation (#194); the kits' rules in fights and play (#161), the Elementalist's second sphere
  (#163) and choosing a kit at creation and after DUAL (#164); thieves as in AD&D, the Assassin's
  backstab (#162) and Shattered Lands' stealth (#152); damage lines and the Effects screen's weapon
  and kit rows (#160); shop prices by the leader's CHA, buying back magic items and scroll messages
  (#166); Tab, Enter, the red ring and the chance to hit (#167, #169); a ranger's two weapons in
  heavy armour (#170); F5, F9, autosaves and saves under names (#173); the Dialogue and Journal
  tabs (#175); T, Shift+T, S and the M, U and I keys (#176); STORE, RECALL and fuller starting gear
  (#182); first spells and psionic powers at creation (#183); R, F10 and Alt (#186); the dice log's
  save modifiers named and attack lines broken down (#188).
- **A level cap by XP of its own**: 5,625,000 XP shared between a character's classes, in place of
  the game's stop at 15th, with levels past the sequel's table (20th) to 30th by AD&D's tables; the
  Player's Handbook's saves, the thief skills to 17th, spell slots to 30th, a druid's stopping at
  15th (#189; [the level cap](obsidian-edition/FEATURES.md#wake-of-the-ravager)).
- **Kits and weapon specs past 13th level** (the owner's choices, 2026-11-26): a gladiator picks a
  weapon spec more every 4 levels past 9th (5th-8th at 13th, 17th, 21st, 25th, in the sheet's spare
  three bytes), a fighter a second at 13th that goes on to mastery at 17th and grand mastery at 21st
  (a Myrmidon a third), and the level up's weapon window is ported to the sequel to ask for them.
  The Ravager's base AC goes on to 0 at 15th; an expert's attacks are 5/2 from 13th; a Seeker's,
  Shinobi's and Justifier's priest slots follow the owner's tables (Table 51, Table 46) to 16th,
  cast at 11th and 7th at most; a Spellarcher's spell arrows are +3 from 13th; an Elementalist's
  7th-level slot comes at 14th, as a cleric's. Shattered Lands' helper has the same tables (#199).
- **All 22 weapon specs**: a spec in one of the six weapon specs Shattered Lands took from the
  sequel (two-handed sword, lotulis, double spear, trikal, javelin, darts) stays that spec in the
  sequel, for its own Twohand Sword and Crystal sword, Lotulis, Double Spear, Trikal, Javelin and
  Darts (before, it counted as the nearest of the first sixteen). The javelin and darts have their
  specialist's rates of fire there, the Effects screen names the six, and a psionicist may still
  use the sequel's darts (#192). The sequel's helper reads the V3 spec layout the Loader now writes,
  and Shattered Lands' new weapon types go across in the party transfer as the sequel's own weapons
  (#181).
- Magic weapons for the specs the sequel had none for, and the mod's plain gear, placed in the
  sequel (#191); a saved game's sellers are stocked with the new items once (#193).
- **The six new wizard spells** (Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image, Spook,
  Friends), as spells 320-325 in the Loader's copy of RESOURCE.GFF, with Shattered Lands' icons in
  the sequel's colours: cast as in Shattered Lands (#200), learnt at a preserver's level up, at
  creation and from a spellbook (#201), and their spellbooks sold by Notaku in Tyr (Cat's Grace
  6000, the others 3000) and carried by three of its wizards (#202). The new spells' switch leaves
  them out (`dsloader/ravspells.py`, DSCLOG2's NEW SPELLS, sites 140-149).
- **The kits' spell slots**: a Battle Mage's wizard slots one fewer at each spell level; a
  Seeker's and a Justifier's priest slots their own tables (Table 51, Table 46), with no WIS bonus;
  a Shinobi's wizard slots the Seeker's table by its thief level (counted, though it can't cast in
  the sequel yet). Beside the Elementalist's and Crusader's, which the sequel already had (#214).
- **The kits' gear**: what a kit forbids is refused there too, and what it allows can be held
  whatever its class, as in Shattered Lands (DSCLOG2's KIT_FORBIDS, KIT_ALLOWS, site 19; KITS.md says
  which kits work in the sequel now, and which in part) (#213). A new character's gear is fitted to
  its classes and kit from the sequel's own items (`dsloader/ravkitstart.py`) (#215).
- **The starting weapon is the first pick's, +1**: a new fighter's, gladiator's or ranger's weapon
  in hand becomes a +1 weapon of its first weapon spec (a two-handed one sends the shield or second
  sword to the backpack, a missile pick goes to the missile slot); an air cleric starts with an
  obsidian dagger, a fire cleric with the obsidian mace (#209).
- **The sequel's own party fitted to the rules**: Gerakis specializes in the long sword, gythka and
  trikal and fights wild; Thy'rokh specializes in the gythka and has a Grove Warden's AC; Terrannus
  is a Crusader at the kit's full cost; Ar'Anda is an Elven Shadow-walker who casts in light armour.
  Given once by the Loader (#207).
- **Picking pockets**: a thief's USE screen out of a fight shows PICK POCKETS with a purse, drawn
  from the sequel's earth Turn Undead icon; a click on a person picks their pocket with Shattered
  Lands' rules (DSCLOG2's PICK POCKETS, sites 180-186) (#204).
- **Shadows, dust, shine and see-through figures** as in Shattered Lands: every living creature's
  shadow on the floor, walkers' dust on dirt and sand, the magic items shining on the shop screens
  (and twelve of the sequel's own that never shone), and the hidden and invisible drawn half
  see-through (DSCLOG2's FIGURE SHADOWS, DUST, SHOP_SHINE, GHOST_DRAW; `ravshine.py`, `RavGhosts`)
  (#203).
- **Kits' PSP costs, hit dice and the Battle Mage's casting after a hit** in the sequel: the psionicist
  kits' PSP costs (a Mind Bender's telepathy 2 less and psychokinesis 2 more, a Kineticist's the other way,
  a Titan Mind's, a Wasteland Seer's by the open sky) and a Mind Warrior's fifth fewer PSP at a level up;
  a Battle Mage's d6 and an Arcanist's d3 hit die at a level up, and past 10th 2 and 1 hit points a level;
  a Battle Mage casts though hit that round. On the creation screen a Battle Mage's, Arcanist's or Mind
  Warrior's hit points and PSP are rolled again as the kit is chosen or taken back, and CON or EDIT keeps
  the kit's range (DSCLOG2's sites 191-201) (#218).
- **Kits' casting levels, cures and spells known** in the sequel: an Arcanist's preserver spells a level
  higher; a Spirit Caller's and a Wasteland Seer's priest spells 2 levels higher under the open sky and 1
  lower under a roof; a Healer's and a Rescuer's cures 1 more a die, a Lifebinder's a die more (Blood Flow
  and Cell Adjustment too); a Wilderness Avenger's Cause Wounds 1 more a die. A Healer's water cleric casts
  the sphere of the cosmos, a Healer and a Lifebinder never the harming spells, a Wilderness Avenger never
  the healing ones; the dice log names the kit's part (sites 205-208) (#219).
- **The Shinobi casts its spells**: a MAGE list on USE, cast at its thief level less 5; one of its own
  learnt at each thief level up from 6th and at creation; from a scroll only its own, after a read
  languages roll and INT's (sites 209-210, header +2076..+2087) (#220).
- **The lotulis', double spear's and trikal's traits**: a lotulis or double spear specialist's last swing
  of a round of two turns on a second foe beside it (the double spear's 1 less damage), a trikal
  specialist's hit trips a man-sized foe that fails a save against paralysis, and the trikal reaches two
  squares (site 202, header +2020..+2028) (#221).
- **The Poisoner's poison, the Spellarcher's arrows' plus and its Fine Bow**: a Poisoner's first melee hit
  of a fight with each hand's weapon poisons (a save or 10 damage); a Spellarcher's spell arrows are +1 to
  +3 by its preserver level; the Fine Bow is +1 to hit, a new Spellarcher's bow is made one and the
  transfer keeps it (sites 214-215, header +2088..+2097) (#222).
- **A Spellarcher makes spell arrows** on its USE screen out of a fight (CHILL, SHOCKING and VAMPIRIC
  ARROWS for the touch spells it knows: a slot for one arrow, stacked to 24, casting on a hit at its
  preserver level); the arrows' objects and icons are made from the player's own Shattered Lands files.
  A new Spellarcher starts with 24 of each it picked; another member's go back to it out of a fight; the
  pointer lights the button it is on; the dice log names the Fine Bow. As one is made its touch spell's
  cast sound plays, and another member can't ready them ("CANNOT USE THIS ITEM", in a fight too; the
  move back stays for arrows readied before) (site 240, header +2098..+2113 and +2130, +2132,
  `ravarrows.py`) (#223, #229, #245).
- **The Effects screen names an effect's charges**, as in Shattered Lands: "ARMOR (14 CHARGES)", Mirror
  Image's images, an effect that runs down by uses; an item's power (Inertial Barrier's) no longer shows the
  stray "(15 CHARGES)" Shattered Lands' fix removed (site 247, header +2128) (#245).
- **The Effects screen's other lines in Wake of the Ravager**, as in Shattered Lands: Enlarge's damage
  ("ENLARGED (+60% DICE)"), Barkskin's, Flesh Armor's and Magical Vestments' AC ("BARKSKIN (AC 5)", from
  the levels the Loader works out), and Reflected Image's Mirror Images named "REFLECTED IMAGE" (EF_CHARGES'
  EC_MOD and EC_REFLECT, header +2134 and +2136). Played: a computer caster's wall at last (Wall of Fog is
  never the computer's choice: its weight is 0; Wall of Fire is) (#249).
- **The dice log** says when an effect starts and ends, a member's PSP going down or back up, and an
  ability score changing, as in Shattered Lands (#232).
- **DSCLOG2 has room again**: its tables and buffers moved to a resident tail past its 64 KB code segment,
  and the install to a segment of its own that is freed, so the ports above fit (#228).

**New: Wake of the Ravager's figures in Shattered Lands' style** (#250, #251, #253)
- The approved redraws of Wake of the Ravager's figures (Codex's catalogue, the owner's private
  installation files, b447d39; 275 OBJEX pictures, 32 objects moved to their own figure, the Tarrasque,
  its cinematic and the drakes in RESOURCE, the Mines3 dining room's placements) shipped as
  `dsloader/ravager-figures.zip` (the owner's choice) and put into the Loader's OBJEX2.GFF, RESOURC2.GFF
  and a new RGN03A2.GFF by `ravfigures.py`; DSCLOG2 opens RGN03A2.GFF for RGN03A.GFF (COPIED bit 8).
  Notaku's combat drawings lose the box their copied Shattered Lands background drew (Codex's own fix
  in the catalogue at e33bc2e, re-packed; the Loader's clean-up kept for older packages). `RAV_SKIP=figures`
  is the control. Played: Tyr's street from `ravager-after-ambush` with and without; the region copy's
  opening seen through a scratch build. Tests: `test_ravfigures.py`, `test_ravager`'s copies (#250, #251).
- Tyr's furniture lowered for Shattered Lands' steeper view, as darksun-recompiled's build had it (the
  owner's choice of 2026-11-20: tables, chairs, beds and the other map artwork two-thirds their height
  toward their base, walls kept): `sl_figures.py squash RGN032 0.66 furniture` on the stock files before
  the catalogue's import, 54 of its 60 pictures (Notaku's stall, 2371-2379, is the catalogue's own); the
  region's placements needed no change. In the same `ravager-figures.zip` (#253).

**New: Shattered Lands' screens and icons in the sequel**
- `dsloader/ravui.py` puts Shattered Lands' 45 interface pictures and 221 icons (130 from another number:
  the sequel renumbered its spells) from the player's own Shattered Lands RESOURCE.GFF into the Loader's
  RESOURC2.GFF, in the colours every region of the sequel keeps, as darksun-recompiled's `sl_figures.py
  build-ui` made them on 2026-11-20 (byte for byte the same chunks on the GOG files); the icon pairs, which
  that tool matched by look, are kept as a table. Put in last, and only where the copy still has the game's
  own chunk; the MORE and scroll buttons stay the sequel's. A box on the Options tab (its Wake of the Ravager
  section, `sl_interface`, on by default) turns it off; `RAV_SKIP=sl_interface` is the test control. Played:
  the USE screen and the inventory from `ravager-after-ambush`, with and without. Tests: `test_ravui.py` (#255).

**Changed**
- **XP stops at the cap** in Shattered Lands: a character's XP is held at its share of the 749,999
  cap (one class all of it, several divided, a human less its old classes'), the share `LEVEL_ROOM`
  caps levels by, so none is banked past the top level; the dice log says what wasn't counted. The
  Loader's (`tracker.py`, `game.xp_share`), no DSCLOG memory (#187).

**Fixed: the game**
- **Saves keep improving past 9th level**: the game's save routine took AD&D's best save as the
  most a save could improve by, so a warrior stayed at 11/11/11/13/11 from 10th level and no save
  went below 8. With AD&D's class tables (always on) a level up now gives the Player's Handbook's
  saves by class group and level (DSCLOG's `SAVE_BASE`, site NS_IMAGE + 123 at 878F7h; the
  sequel's fix ported, one table for both). DSCLOG: the segment's spare 928 to 672 bytes, upper
  memory's 138 to 109 paragraphs (#210).
- **Psionicists save by Dark Sun's own table** (Table 8), not the thief's, in both games: the
  game's group of thieves and psionicists is split by the sheet's classes, a psionicist/thief the
  better of each save (`save_bands.inc`, DSCLOG's and DSCLOG2's `SAVE_BASE` the same code and
  bands) (#210).
- The Military Scout's +1 to hit with a missile under the open sky is the bow's, sling's and staff
  sling's only again: the javelin and darts had it too (#210).
- The window routine's failure exit no longer jumps into the middle of the `window` patch (the
  spell slots on the USE screen): it goes to an identical unpatched "pop si / leave / retf". A new
  test scans the patched program for any other jump into a patch (#159).
- When the view moved to whose turn it is, or followed a figure walking, copies of the docked panel
  (its header in a row, "Needs Needs Needs") stayed beside it until the main loop's next pass. DSCLOG
  now catches the game's moves of the view as they end (`PANEL_FOLLOW`, `CENTRE_THING`, `CENTRE_XY`:
  sites 125-127) and draws again just where the panel was copied to. Played in Pehtucl's ambush, frames
  grabbed through two rounds: copies in runs of up to 49 frames before, 2 at most after. The files with
  copies (`COPIES`) moved to DSCLOG's tail to make room (#254).
- A thief who failed more than four locks at one level in a region could try the latest one again: the
  four kept were the highest thing numbers, not the four failed last (#235).

**Fixed: Wake of the Ravager**
- The Loader's copy of the sequel has most of Shattered Lands' engine fixes, and mends some of the
  sequel's own bugs: a new character's hit points, its weapon in the off hand, the message box that
  never stayed on screen, a worn item's spell that never ended, saving throws held at the table's
  last row, and the Tyr inn's room that never rested ([which, fix by
  fix](obsidian-edition/GAME-BUGS.md#in-wake-of-the-ravager)) (#148 to #195).
- **Items weigh what they do in Shattered Lands**: SSI left 71 of its 102 item types at 0, though
  its program still checks weight as Shattered Lands' does: now two heavy weapons can't be held
  together, the item box says HEAVY, a heavy weapon can't backstab, and pockets go by weight
  (`ravager.RAV_WEIGHTS`; `RAV_SKIP=weights` for a control). No save changes. Study:
  `reports/wake-of-the-ravager-item-weights.md` (#211).
- A new character's weapon starts in the weapon hand: the sequel's own gear put a fighter's +1 long
  sword (and a cleric's, druid's, preserver's or psionicist's weapon) in the left hand, which swings
  once a round, so a new long sword specialist showed 1 attack a round; now 2 (#195).
- A Justifier of 8th or 9th ranger level had the plain ranger's first priest slot there and cast
  with it at caster level 0. Now he has none before 10th, as in Shattered Lands (#214).
- **A double spear swung once a round**: SSI gave the sequel's Double Spear a range of 2 squares, which
  the game takes as a shot (one attack a round, DEX to hit, no STR damage). The Loader's copy gives it a
  range of 1, as Shattered Lands' has (`ravager.RAV_RANGES`; `RAV_SKIP=melee_range` the control) (#221).
- **Shattered Lands' fixes of the game's own bugs** that the sequel shares, carried over: a character's
  most PSP from its own CON, INT and WIS; the computer's walls cast across the line of fire; a party
  thri-kreen's claws and bite edged; the gladiator's armour optimisation only with armour on; an archer's
  pointer after a shot; the roster's DELETE with the list scrolled; Slay Living's description; CHOOSE A
  SPELL's grid past 15 spells ([GAME-BUGS](obsidian-edition/GAME-BUGS.md#shattered-lands-fixes-in-the-sequel)).
  A lock a thief failed is out of reach until the thief gains a level, as in Shattered Lands (#232).
- **A berserk creature fought on for the side its turns rolled** to the end of the fight: Berserk's end
  had no case to give its side back (Shattered Lands' bug, shared). Its side is kept as Berserk starts
  and given back as it ends (DSCLOG2's sites 245, 246). The **dice log said no monster was killed**, so
  every fight's summary said "0 kills", and a killed creature's last blow had no HP line: both said now.
  DSCLOG2's header says its length (+30), and the Loader writes none of its later fields to an older
  helper; a Spellarcher's starting arrows are given only with all three arrows' objects in the copy, and
  its plain arrows taken only once they are in (#240).
- The kit byte's "no kit" marker, 0FFh, is also a legal byte on a human with three classes (kits
  3/3/3, the own party's bit and Friends), so such a character lost its kits. 0FFh now means "no kit"
  only on any other sheet, in the Loader (`game.kit_open`) and DSCLOG2 (`KIT_OPEN_AT`). No save
  changes: no other sheet could hold 0FFh as kits (#239).
- In the sequel, dice the dice log held to learn which spell they belonged to waited for the next roll
  instead of being shown after a second, as in Shattered Lands (#235).

**Fixed: the Loader**
- Every Shattered Lands start failed before the game ran, on either engine: the weapon window's
  `weaponpages.slot()`, changed for the sequel's weapon specs, read its colours before they were
  set (`UnboundLocalError`). `test_start_files` now prepares the patched game from the player's own
  files (#196).
- With DOSBox-X chosen and none found, the Loader's message read "no DOSBox-X program is:", a sentence
  cut short. It now says none was found, names the mod's dosbox-x folder it looked in, and says the
  release zip brings one (a source-code download doesn't) (#227).
- With no Loader window (the dice log on its own, or the game started without one), a change to
  `settings.json`'s `autosave` or `quick_save` is taken within a second, with no restart
  (`DiceLog.follow_switches`; the window's Options tab already did this). Test: `test_dicelog` (#254).
- Shattered Lands started from the Loader's window after a game of Wake of the Ravager started without
  its new items, people and icons (and a changed GPLDATA copy): the sequel's record layout was still on
  while Shattered Lands' copies were written. It is put back first now (#235).

**Docs**
- The engine in FEATURES, the README's requirements, the player's guide, both DEVELOPMENT pages
  (the configuration line by line, the memory's layout under each engine), the patch notes, and the
  DOSBox-X experiment's findings carried into `reports/modernisation-research-and-plan.md` (#146,
  #178).
- The weapon specs page has the twenty-two kinds, who may choose them and their dice; the features
  page, the player's guide, Items and the dice log page have the new weapons and traits (#149).
- The game's bugs page says which fixes Wake of the Ravager has (the saves of #210 too), lists the
  sequel's own bugs mended and the bugs known but not yet fixed; the patch notes' bug fixes have
  the sequel too (#206).
- An audit of what the Wake of the Ravager port brought across, and what it still lacks
  (`reports/`, #208); a folder of notes for OpenDS and yuan-ti (`reports/community/`, #153).
- GAME-BUGS: Reflected Image and the shop glow fixed in the sequel (#217).
- The release record caught up: this section by subject with each entry's pull request (#224); DOSBox-X
  the default engine in the README, DEVELOPMENT and the known issues, started on Windows and untried on
  macOS, in the credits, and the sequel on the front page (#225); the patch notes with what came after
  2.19.2 and a Wake of the Ravager section (#226).
- A documentation review (`reports/docs-review-2026-11-27.md`), the Options tab's picture retaken, and
  the outfit galleries' links made relative (#233).
- **Wake of the Ravager has a page of its own**, [RAVAGER.md](obsidian-edition/RAVAGER.md) (starting it,
  the saves converted, the party transfer, the mod there), with FEATURES keeping a paragraph and the
  manual a page (#234).
- Nineteen pictures of the party retaken with the class outfits, their captions rewritten (#252).
- The code audit of 2026-11-27 (`reports/code-audit-2026-11-27.md`: findings by severity and the 72-byte
  sheet's map) (#237), S1's later stages deferred (#248).
- The sequel's kits, the patch notes and the links brought in step with #218 to #254: the patch notes'
  Wake of the Ravager section links to RAVAGER.md and has the figures and the Effects screen's lines;
  this section's entries each name their pull request (#257).
- The Player's Guide's weapon tables (damage, the clerics' spheres, mundane and magic weapons, who wields which
  magic weapon) and the backstab table in How the game works list Wake of the Ravager's weapon kinds, their
  metal, obsidian and bone ones and their 13 magic ones (#257).
- The Loader's pictures (`dicelog.png`, `dialogue.png`, `viewer.png`) retaken with the new bar; FEATURES'
  table of what the party wears says what shows on a class outfit and the shape of each of Wake of the
  Ravager's weapon kinds (#262).

**Dev**
- DOSBox-X: `dsloader/dosboxx.py`, `process.FileMemory`; `tests/test_dosboxx.py`,
  `tests/test_filememory.py`. The playtest kit: `PT_DISPLAY`, `start_dosboxx.sh`, `dbxadopt.sh`,
  `codepatch.py`, and `dosboxx_memtest.py`, a check without the game that a second program can read
  and write DOSBox-X's memory file, for the owner to run on Windows and macOS. Logs:
  `2026-11-18-dosbox-x.md` (the experiment), `2026-11-19-dosbox-x-engine.md`,
  `2026-11-21-dosbox-x-unchecked.md` (#146).
- The sixth memory pass: 1,104 bytes of upper memory back for DSCLOG (32 were left with the six
  weapons; 1,136 now) and 688 of its segment, by one far call into the game for 35 sites
  (`GAME_FAR`), shared code moving an interrupt's frame (`FRAME_UP`, `FRAME_DOWN`, `OVR_FRAME`) and
  the extra item types packed (`XTYPE`); nothing the player sees changes. Tests find those probes
  through the install's vector table; `test_framecode` runs the shared routines. A play log:
  [memory pass 6](playtest/logs/2026-11-23-memory-pass-6.md) (#150).
- The seventh memory pass: 1,296 bytes of upper memory back for DSCLOG (2,208 free now) and 240 of
  its segment. The Loader's item types and names, and the mends to the game's own types, are in the
  item chunks of its copy of GPLDATA.GFF (`itemtables.py`) instead of DSCLOG's tables; DSCLOG only
  notes where the game put them. A new item now costs no resident memory. Nothing the player sees
  changes. A play log: [memory pass 7](playtest/logs/2026-11-25-memory-pass-7.md) (#179).
- A start-up test for Wake of the Ravager beside Shattered Lands', and a rule to run both before a
  push (#198); tests put the rules back after a test that turns them on (#147).
- `test_ravpickpocket.py`; `ravdice.py`'s `RAV_PICK_ROLL=N` fixes the pick's d100 for a test
  (#204). A play log: [Wake of the Ravager's weapons](playtest/logs/2026-11-23-ravager-weapons.md),
  with control runs; `specset.py` sets a member's weapon specs in memory (#149).
- DSCLOG2's LOCK_SITE, GL_ARMOUR, AI_WALL, KREEN_CLAWS (sites 241-244) and PSP_SCORES, header +2114 to
  +2122; `test_ravgamebugs.py`, `test_ravlocks.py`; `ravaudit.py`, `ravitems.py --bare/--dress` (#232).
- `DiceLog.PASS` is the pass after the rolls as a list of named steps with their phases; the sequel's
  `RavDiceLog.PASS` takes Shattered Lands' by name and adds its own, and `ravlog.PASS_LEFT_OUT` says
  why it leaves each other one out. `test_ravlog.PassStepTests` fails on a new step in neither. Played
  in both games: the same lines as before (Shattered Lands' fountain ambush: initiative, a dance, the
  turns; the sequel: stock, its own party, ages) (#246).
- `spritegear.armed`'s per-figure, per-frame placements for the class outfits are three tables
  (`PART_FIXES`, `GRIP_FIXES`, `CARRY_FIXES`) laid over what the figure finder reads, in place of 17
  branches; `outfit_layer` replaces three copies of one expression. All 88,090 outfit pictures a
  sweep over every figure, class mix, weapon and armour builds are the same, hash for hash (#244).
- `ravlog.apply_layout` rebound a name in any module holding Shattered Lands' value under it; now only
  in its declared holders (`_layout_holders`: game.py, the dice log's signature, the mod's sheet bytes'
  modules). The 16 copies other modules kept (`from .game import` or a constant of their own: kits,
  spellbook, dicelog, champions, ring, itemgate) read `game.NAME` instead. `LayoutHolderTests` fails on
  a new copy. Played in both games: the same lines as before (#247).
- The 65 routines DSCLOG and DSCLOG2 had the same, line for line (1,238 lines), are written once in
  `dos/shared_routines.inc`, each a macro its helper expands where the routine was, so a fix reaches
  both. Both programs build to the same bytes; `test_shared_routines.py` fails on a routine written
  twice again (#243).
- `tests/test_dsclog_room.py`: DSCLOG's segment keeps 256 bytes free and its upper memory 32 paragraphs
  (its build failed only past the limit), as `test_dsclog2_room.py` does for DSCLOG2; and the sequel's
  modules' constants named as DSCLOG2's symbols agree with them (#238).
- DSCLOG2's build fails if the helper outgrows upper memory (`UMB_NEED`, `UMB_KEPT`, as DSCLOG's),
  the room measured in the sequel: 83 KB free today (#242).
- `playtest/ravstart.sh`: several object parts in `RAV_SKIP` each rewrote OBJEX2.GFF from the game's
  file, so only the last was left out; now one write leaves them all out (and `spell_arrows` RESOURC2.GFF's too) (#235).
- `playtest/`: `RAV_SKIP`'s controls listed in one place (#236); the pictures' play kit (`picstart.sh`
  with the dice log, `toturn.sh`, `shadowsw.py`, `sheetbyte.py`, `itemplus.py`) (#252).

## Pull request #144 ([merged 2026-11-21](https://github.com/daaki85/darksun-obsidian-edition/pull/144))

No release: these fixes come with the next one.

**Fixed**
- The Loader stops at startup and names the file if it cannot remove a stale game data override.
  This prevents DOSBox and Dark Sun Recompiled from loading incompatible files together (#137).
- The `dicelog` command stops its stats worker and closes its process handle before reconnecting
  after DOSBox exits. It also releases those resources when the command stops or setup fails (#139).
- Autosaves for a new area or a finished fight wait for any quick-save or quick-load request to
  clear. When the Loader detects a loaded save, it drops any autosave that was waiting (#138).
- The journal commits entries before giving their ID to the game. A Loader window opened
  earlier refreshes its journal before recording, and loading an older save keeps later entries
  with the same game time on their original branch (#135).
- Named Saves checks the party records before restoring a file and refreshes changed saves
  even when their file size and timestamp match (#135).
- Bulk loot (T and Shift+T) restores the container and backpack lists when a transfer write fails.
  It leaves the items in place if it cannot pause the game (#136).
- The dice log reports a timed spell reapplication when the caster and effect handle are reused
  and the scheduled expiration changes (#141).

**Docs**
- The upgrade instructions include the `Journal` folder and ask players to verify their history
  before deleting the old Loader folder (#135).

**Dev**
- A play log: [pull requests #136, #140 and #141 in the game](playtest/logs/2026-11-20-open-prs-checks.md),
  with #140's round count fixed and played again (#142).

## Pull request #143 ([merged 2026-11-20](https://github.com/daaki85/darksun-obsidian-edition/pull/143))

No release: the dice log's fix below comes with the next one.

**Fixed: the dice log**
- DSCLOG records the fight, round and combatant with each initiative tie-break, so the log counts
  the rounds that pass between its looks even when creatures out of the fight have old tie-breaks
  in the game's table, and a long burst of skipped rounds that overruns the log's ring is counted
  from the last round shown (`Rounds 4-383 go by at once`, not `232-383`). The in-game panel keeps
  the skipped rounds' marker at every detail level and under the combat filters (#140).

## Pull request #133 ([merged 2026-11-20](https://github.com/daaki85/darksun-obsidian-edition/pull/133))

No release: the dice log's two fixes below come with the next one (2.19.2 doesn't have them).

**Fixed: the dice log**
- An effect put on someone who has it already (Rainbow Pattern or a second Hold Person on a held
  creature) takes the old one's place in the game: the log said `Paralyzed ends on Y` beside the new
  caster's line though the hold went on, or nothing at all when the caster stayed the same. It now
  says `..., in place of the one it had` and no end (records told apart by spell and handle too) (#131).
- With no one in a fight able to act (the whole party Paralyzed and the foes held) the game plays
  the rounds through in a blink. The log put them all under one `Round 1` heading listing everyone
  once a round, most of them as `?`, and took the fight for a new one (a dance rolled again,
  the foes' ACs forgotten). It now says `Rounds 3-7 go by at once: no one in the fight can act`
  and goes on with the right round's order and number (`Round 8: ...`); the combat log's panel
  and its header follow (#132).

**Dev**
- A play log: [the "Paralyzed ends on Templar" of the F10 real-pin play](playtest/logs/2026-11-20-paralyzed-ends-oddity.md).
- A play log: [the "Round 1" at the whole party's hold](playtest/logs/2026-11-20-round-one-oddity.md).

## Pull request #127 ([merged 2026-11-20](https://github.com/daaki85/darksun-obsidian-edition/pull/127))

Obsidian Edition 2.19.2 ([release notes](release-notes/v2.19.2.md)).

**Fixed**

- **F10 moved a held member**: the game's F10 put a Paralyzed or Stuck party member back on its
  turn's first square, with its points. It now does nothing for such a member (#126).

## Pull request #124 ([merged 2026-11-20](https://github.com/daaki85/darksun-obsidian-edition/pull/124))

Obsidian Edition 2.19.1 ([release notes](release-notes/v2.19.1.md)).

**Fixed**

- **F10 gave a held member its walk back**: a member Paralyzed or Stuck after its last step got
  the walk back on F10 (and took a step before the game ended its turn), since the game's pin
  leaves the turn's flags as the last step did. The Loader now gives no walk to a member with
  either effect on it (#123).

**Docs**

- 2.19.0's release notes: the saved-games section's last bullet split and its repeat removed (#122).
- The first code and memory audit's report archived in `reports/archive/` (#121).

## Pull request #119 ([merged 2026-11-19](https://github.com/daaki85/darksun-obsidian-edition/pull/119))

Obsidian Edition 2.19.0 ([release notes](release-notes/v2.19.0.md)).

**New**
- **Tanelyv's chest piece shines** as its arm and leg pieces do (#106).
- **A journal** (the Loader's new **Journal** tab): every talk with the reply chosen, every reward
  and message, under the game's day and area, kept on disk (`Journal/`) and following the saves
  (its newest entry's id in the game's global numbers 198 and 199).
- **Picture and music device** (Options, from the next start): Plain, Scanlines, TV or Sharp for
  the game's picture (DOSBox 0.74's scalers and `openglnb`), and the music sent to any MIDI
  device of Windows'. Seen on Linux only; the music device not heard.
- **The chance to hit before the swing**: with an enemy chosen with Tab, what the d20 must show
  and the chance, on the dice log's line and in the combat log's header, worked out as the game's
  attack does (`hitchance.py`; DSCLOG unchanged).
- **Quick save, quick load and autosave**: F5 saves at once, F9 opens the load window on those
  saves, and the game saves by itself after an area change and a fight, all on a fifth page of the
  save window, QUICK (`quicksave.py`; DSCLOG's `QS_KEY` and `SAVE_TICK`, four header fields from
  +1878, signature `DSCLOGvd`).
- **Quests on the Journal tab**: open and finished, read from the script flags and numbers the
  story is kept in (45 quests: `quests.py`; `questdraft.py` drafts the table for developers).
- **Showing what can be used**: hold Alt on the map, out of a fight, for a gold ring under every
  door, container, body, item and person a click does something with, and the nearest ones' names
  (`usable.py`; DSCLOG unchanged).
- **Squares in reach**: on a party member's turn a small cross on every square one click can
  still walk to, by the game's own rules of movement (`squares.py`, DSCLOG's `TINT_PASS`; header
  field `SQUARES_ON` +1890, signature `DSCLOGve`). **DSCLOG's room**: #112 left 224 bytes of the
  segment and 36 paragraphs of upper memory, less than quick save and the squares needed, so their
  two long routines run from the tail (`TAIL_CALL`: code in the tail is new) and the squares' map
  lies in DSCLOG's own PSP (71,440 bytes then, 48 bytes and 1 paragraph left). With the room #115
  freed and #116's 48 bytes: 70,304 bytes, 1,184 bytes of the segment and 72 paragraphs of upper
  memory left.
- **The chance to hit under the pointer**: on a party member's turn the roll needed and the chance
  float over the enemy the game's pointer rests on (`hover.py`; DSCLOG unchanged).
- **R hides and shows the squares in reach**, the owner's request: on the map in a fight, kept in
  `squares_shown`, said in the dice log and over the member. Read from the BIOS keyboard buffer
  (`keywatch.py`), so DSCLOG is unchanged; R is in none of the game's key tables (A, which the
  owner named, toggles the game's animations: every key the game binds is now in
  HOW-THE-GAME-WORKS.md).
- **F10 takes a whole move back**, the owner's request (`moveback.py`; DSCLOG unchanged): after the
  last step the game's F10 put a member back unable to walk; the Loader gives the walk back when
  it has seen the last step and then F10's doing in one turn, never after an attack (one that
  kills leaves the member its turn: seen in the game). Switch `move_back`.

**Changed**
- **Fewer switches** (#110), for a simpler Options tab and the mod's rules as meant: the combat
  log, the rule changes but hit dice, half-giants' weapons and helms, weapon specialization, STORE
  and RECALL, the shops and thieving, the graphics and the controls are always on; an older
  settings file's False for one is passed over.
- **Spell arrows' item box heads its list SPELLARCHERS:** (#109), and with no Spellarcher in the
  party, spell arrows another member has readied (an old save) go back into its pack.
- **Spell arrows shot by anyone outside the party cast their spell** (#108), at the archer's
  highest level, so the elf champion's Chill Arrows chill as a Spellarcher's do.
- **The champions' bout** (#107): the halfling's staff sling, DEX 22 for the Tohr-kreen, the
  halfling and the elf, the elf's Fine Bow and 24 Chill Arrows, and the defiler in the Bracers of
  Defense AC 6 that were Mikquetzl's.
- **The Flame Blade is the Searing Blade** (#106), an obsidian short sword +2, so the priest
  spell's weapon alone has the name; a saved game's is remade as the dice log runs.
- **Magic items glow in the colours their stories call for** (#106): the game's colour cycler turns
  green and violet too, not only water and fire (Greenbright green, Mindshard violet).
- **The release zip** leaves out the developer pages, the tests and `docs/viewer.png`; the manual
  links to them at the release's tag (#97).
- **The chance under the pointer shows nothing with the look pointer**, whose click only looks (the
  owner's request).
- **The combat log's panel is put away while the map is not the screen** (the owner's report: it
  covered the save and load windows' QUICK button and list), and comes back with the map.
- **The Loader's tabs show their names whole** ("Dice lo", "Journa" with six tabs): the divider
  leaves the right-hand pane the width the names need. Seen on Linux only, where they were whole
  before too.
- **The new switches** are in the Options tab's In the game section (the chance to hit, the squares,
  F10, Alt) and Saves (quick save, autosave), "Fewer switches" having taken the Controls section.

**Fixed**
- **The code audit, part 1** (#111): Negative Plane Protection's save no longer writes past the new
  spells' records; a magical item sold with the Loader's window closed is no longer lost; the
  Loader moves items only with the game held still, so no list is cut into another.
- **Smaller, from the same audit** (#111): the Elven Leader's Gythka +1 isn't drawn as Kreenfang; a
  Ravager at kit level 0 has the table's first AC; a second new character's gear isn't skipped; a
  file held a moment by a virus scan no longer starts the game without the dice log; settings
  changed by two Loaders at once are both kept; the item lists' writes hardened.
- **DSCLOG's interrupt handling and memory margins** (#112): its handlers leave interrupts as the
  game had them (the game's clock lost ticks), copies clear the direction flag, a removed mouse
  handler is forgotten, A20 is turned on again if found off, upper memory starts at CA00h for more
  room beside DOSBox's tables, and memory in pieces is warned of too.
- **The elven slavers' leader's Goodbye** no longer goes straight to the arrest, from OpenDS's
  triage (no pull request: committed to the branch).
- **The Characters tab with a game attached** stayed empty since "Fewer switches" (`KeyError:
  'stealth'`): `viewer.py` still asked for a switch gone from the tab. Found with the Loader's
  window on a running game and fixed alike by #115 and this branch (one fix kept);
  `test_switch_names`.
- **A thief's later attacks in a round after a backstab** are judged on their own (#116): they
  were 2 worse to hit and still counted as from behind, the target's DEX and shield ignored.
- **Three older Loader bugs** (#118): the dice
  log no longer gives the character being made an age of its own after each roll of the creation
  screen's die (it now says the screen's AGE once, at DONE); on Linux a DOSBox the Loader's window
  didn't start is seen to close (it said "Connected" on), and a reload no longer logs "Loader error
  in the party table" from the closed game's empty memory.

**Docs**
- **The change records** (#98): shorter patch notes, each release's news in its notes, the
  CHANGELOG's older entries archived and its labels made New, Changed, Fixed, Docs and Dev.
- **The player pages' small fixes** (#100): troubleshooting for a Python the `.bat` files don't
  take and for the wrong game folder, Linux's window, every save name Show Save takes, the
  README's version, licence and credits, lighter GIFs.
- **The player's entry points reordered** (#101): the folder README in the order a player needs
  it, the root README a pitch and three steps, the guide's shared notes said once.
- **The developer pages restructured** (#102): `DEVELOPMENT.md` the entry point (architecture,
  glossary, a map of every module, a contributor checklist), the rest in `DEVELOPMENT-INTERNALS.md`.
- **In-game checks of the pages** (#103): the look box's picture retaken, with a creature's
  defence line; the combat log's buttons measured for the playtest guide.
- **One home for each reference** (#104): weapon specialization a page of its own, the kits a line
  and a section each, a place for every item, each rule said in one page.
- **Features a catalogue, and a People page** (#105): FEATURES.md one short entry for each switch,
  in the Options tab's order; the story's people on a spoiler page of their own.
- **Named saves aren't a backup history**, and DSCLOG's room recomputed for this build (#112).
- **The second documentation review's fixes** (#113): the multiclass rule as the code has it,
  rules now always on no longer written as switches, the random monsters' divide by zero and "Out
  of memory in OEOpenGraph" out of the game's bugs, more troubleshooting, the Elvenkind picture
  retaken; this section sorted and numbered; `.gitattributes` and `.gitignore` out of the zip.
- **The final documentation review's fixes** (#117): the CHANGELOG's header back, the multiclass rule, always-on rules no
  longer written as switches, the removed off paths out of the developer pages, the dice log's
  picture retaken.

**Dev**
- **The playtest kit** (#99): one startup checklist, the memory edits in RESEARCH, HISTORY by
  topic, the logs indexed, finished reports archived.
- **The code audit's tests** (#112): DSCLOG's header fields at their offsets, its interrupt
  handling in the emulator, the Loader's names within DSCLOG's room, every player's page in the
  manual; a release step runs the tests with the game's files; the start-up hook no longer takes
  a branch with `-2` on it for a session's handed random name.
- **Tidying** (#102): `dsloader/guidepage.py` taken out, the combat log's design brief archived,
  the rest-order prototype moved to `playtest/logs/files/`.
- **DSCLOG's room freed** (#115): the off paths of
  the switches always on since #110 taken out of DSCLOG (their rules' tests, the game's ways behind
  them, `MANUAL_ON`) and of the Loader, about 1.1 KB freed for what comes next; the rules switched
  still are kept.
- **The final code audit's fixes** (#117): the
  Loader's rules start at the always-on ones and its dead off-branches are gone, the header test
  ties each constant to its own field, temporary files are each writer's own and never left behind.
- **The last audit's two small items** (#118): the
  stats thread takes its idle step while no game is attached (it looked every millisecond), and
  `crash-logs` keeps the newest 20 freeze reports. Tests for these and the three bugs above.
- **`dsloader/questdraft.py` is left out of the release zip**; `test_release` checks the zip and that
  no module that ships imports it.
- **DSCLOG's header fields by name** (`test_header_offsets`): two branches had added fields at the
  same offsets under one signature, and every constant still named a field.
- **The playtest kit**: tools for the additions (`picpattern.sh`, `tabhit.sh`, `qsave.py`,
  `usable.py`, `squarewalk.py`, `hoverlabel.py`, `gamekeys.py` and more), `PT_NO_EDIT=1` for a
  fight and an arena trip with no memory edit, the game's key tables, the Loader's window on a
  second display.

## Pull request #96 ([merged 2026-11-17](https://github.com/daaki85/darksun-obsidian-edition/pull/96))

No release: nothing in `obsidian-edition/` changed.

**Dev**
- **Session branches named after the task** (CLAUDE.md): a cloud session makes `claude/<task>` before
  its first push instead of using the random name it is given, since a session can make branches but
  not delete them.

## Pull request #95 ([merged 2026-11-16](https://github.com/daaki85/darksun-obsidian-edition/pull/95))

Obsidian Edition 2.18.0 ([release notes](release-notes/v2.18.0.md)).

**Changed**
- **DSCLOG's room: a fourth memory pass** (the kit rebalance had taken the helper's segment from 960
  bytes spare to 320, and upper memory once installed from 83 paragraphs to 43). It freed 304
  bytes: two routines in place of sequences written out at each site, `ES_THINGS` (the things'
  segment in ES, 23 sites) and `SHEET_OF_AX` (a sheet by its number, 19), and
  `CREATURE_SHEET_AX` for two more; the table of the Loader's file copies keeps each name once and
  makes its `D:\` path as the file is opened (`COPY_PATH`), not a 16-byte path an entry. Now 624
  bytes of the segment spare and 62 paragraphs of upper memory ([DEVELOPMENT.md's
  limits](obsidian-edition/DEVELOPMENT-INTERNALS.md#the-limits)). Checked in the game
  (playtest/logs/2026-11-16-memory-pass-4.md): the copies opened (`objects_on` 1), a fight (hiding,
  a backstab, poison and its save, specialization), the see-through figure, View Character and
  Effects. Tests: the byte patterns of `test_saves` and `test_shadow_gone`, and
  `test_regions_opened` (the table's names). DSCLOG 70,464 bytes.
- **A warrior's THAC0 with the kit's chosen weapon only** (after The Complete Thief's Handbook's Swashbuckler): the Swashbuckler, Battle Mage, Crusader and Mind Warrior no
  longer have it with every weapon. `PROBE_THAC0` and `CR_THAC0_BASE` leave it out (the sheet's
  THAC0 is the classes'), and the new `WAR_HIT`, in `PROBE_ATTACKS` after `KIT_TO_HIT`, takes the
  creature's THAC0 (+1Fh) less a warrior's (21 less the kit's level, 1 at best) off the attack's
  THAC0 with a weapon of the kit's chosen weapon spec (with weapon specialization; without it the
  kit's kinds: `SWASH_KINDS`, `KIT_BM_KINDS`, melee). The Swashbuckler picks its weapon of choice
  on the weapon window after DONE (`LV_DUE` one, `KINDS_ALLOWED` the long sword, dagger and short
  sword; no specialization's bonus or attacks: a thief's chosen kind is plain); its thief skills'
  −10 went too, for bad luck (below). The Loader's THAC0 for each weapon (`game.weapon_hits`) and the dice
  log (`_kit_attack`) show it as "Swashbuckler (a warrior's THAC0)" (`kits.war_hit`). Tests:
  `test_dsclog`'s `test_war_hit`, `test_thac0`, `test_thac0_line`, `test_swashbuckler`.
- **The Scholar: a spell more learnt, no slot more** (after trying a sure scroll
  learning and INT's bonus slots on this branch): one more spell at each level up (`LV_SCHOLAR`), one
  more for each level at creation (`KIT_MADE` in the picks) and on changing class to preserver
  (`PROBE_DUAL_SPELLS`), as up to 2.17; its slot more at each spell level is gone (`PROBE_SLOTS`,
  `kits.slots`), and it learns from scrolls as any preserver. Its −1 to hit stays, which its touch
  spells, Minute Meteors and Turn Pebble to Boulder roll with, and Acid Arrow too: `SPELL_HIT` makes its
  fighter's THAC0 1 worse for a Scholar (the dice log says so). Test: `test_spell_to_hit`. KITS.md's slot table has
  no column for it. Tests: `test_scholar_picks_one_more`, `test_slots`, `test_int_learn`'s Scholar,
  `test_slots`' `test_kits`.
- **The Arcanist: its preserver spells cast a level higher** (in place of two spells a turn): `PROBE_SPELL_LEVEL`'s new `ARC_LEVEL` adds 1 to a party Arcanist's wizard spells'
  level for their duration and damage (the new wizard spells, 196-201, too; `kits.arc_level`). The
  two-spells probes are gone: `PROBE_CAST_MARK`, `PROBE_CAST_DONE`, `PROBE_END_TURN`,
  `PROBE_ROUND_MARK` (vectors 93h-96h free again) and `ARC_HOLD`'s clearing in `PROBE_SCROLL`. Its
  d3 hit die stays. Test: `test_arc_level` in place of `test_arcanist_second_spell`.
- **The Poisoner: each melee weapon poisons once a fight** (as a dose is used
  up): `PROBE_POISON` poisons a party Poisoner's hit only if that hand's weapon hasn't this fight
  (`POISON_USED`, a new header byte at +1860: bit N main hand, N + 4 off hand, cleared by the dice
  log as each fight starts, `kits.TSR_POISON_USED`); the hand from `KIT_OFF` (+1861), which
  `NOTE_SHOT` sets for a melee attack with the left hand's weapon (its item's +11h 10). Tests:
  `test_poisoner`, `test_note_off_hand`; the dice log's "is poisoned by the hit" follows the same
  doses (`_poison_dose`). Checked in the game (playtest/logs/2026-11-14-quiver-turn.md part 6).
- **One kit a character**: `DK_ASK` asks no kit after DUAL of a human that has a
  kit already (the kit byte's places, its low six bits, not 0; not `KIT_OPEN`; the game's own
  party's `OWN_BIT` isn't a kit); one with none is asked as before. KITS.md's kit pairs stand for
  older saves' characters. Test: `test_dual_kit` rewritten.
- **The Myrmidon: its second weapon spec the polearm** (after *The Complete
  Fighter's Handbook*'s military weapons; in place of melee specs only, tried first): a new
  Myrmidon picks one weapon spec as any fighter (the bow too, not the polearm: `KINDS_ALLOWED`'s
  `MYRM_POLEARM`, `restrict.allowed_kinds`), and the Loader gives it the polearm as its second
  (DSCLOG's `MYRM_POLEARM` at DONE, after the weapon window, so the roster's copy the game writes then
  has it, and `weaponchoice.kinds_for`, `kits.POLEARM`), both going on to mastery and grand mastery as before;
  `LV_DUE` no longer asks for two. Its starting gear's plain polearm goes in the backpack. A
  Myrmidon of an older save keeps its two. Checked in the game (playtest/logs/2026-11-15-kit-rebalance-checks.md,
  with every other kit changed on this branch). Tests: `test_myrmidon_polearm`, `test_myrmidon_polearm_second`,
  `test_myrmidon_two_weapons`, `KindsAllowedTests`.
- **A second documentation review** (five read-only reviews: player pages and the Loader's wording,
  the reference pages, the developer pages, the playtest kit, the pictures): every kit changed since
  2.17 marked "(was ...)" in the patch notes, the Spellarcher's line shortened, the Loader's items in
  order and the mod's own fixes apart; a kit's warrior THAC0 where it shows (not the creation
  screen's), the Swashbuckler's pick, the Fine Bow with the mundane bows, the Spellarcher's dice-log
  lines; the developer pages' sizes after pass 5, STORE and RECALL's ids (8B0h, 8B1h), the stand-in
  rule, the quiver's write-up, the spell grid with the screens, contents lists; the playtest guide's
  creation section regrouped, the unchanged game in RESEARCH.md, `levelup.sh` on the first icon
  (113,71: it clicked the 7th place since the grid changed). The Loader says "from the next start"
  one way, "Connected to the game (process N)" for DOSBox or the recompiled program, and Names over
  figures says it covers the arrows left. Pictures retaken: dicelog, dialogue, viewer (the status
  line), kalzith-body (his Ashen Robe); new-spells-2 without Fogbolt's box, shown in new-spells
  already. Test: `test_doclinks` maps the features page's Kits to DEVELOPMENT-KITS.md. Checked in
  the game (playtest/logs/2026-11-16-doc-review-2.md): levelup.sh at a real level-up.
- **DSCLOG's room: a fifth memory pass** (96 bytes): `NS_FLAGS_IRET` keeps the six-instruction way
  back of 14 sites once (each a jump to it), `FINE_ITEM` the Fine Bow's name look-up for `FINE_HIT`
  and `IB_MATERIAL`, and the never-shown "BURNING ARROWS" is gone. 688 bytes of the segment spare,
  65 paragraphs of upper memory once installed. Code audit: one comment fixed (the Fine Bow's name is
  `spellarrows.FINE_BOW`). Checked in the game (playtest/logs/2026-11-16-memory-pass-5.md): the Fine
  Bow's box and shot, Entangle, the DUAL window. DSCLOG 70,416 bytes.
- **CHOOSE A SPELL's icons centred**: the game fills its window's 21 places
  (WIND 17500) middle five columns first, then the right-hand column, then the left, so past 15
  spells (the game's own 4th level, 16; the 1st with the new spells, 18) the grid sat right of
  centre. Compared with the unchanged game (its window the same; at creation the unchanged game
  offers no picks). The Loader's RESOURCE.GFF has the first 18 places six to a row, filled row by row,
  centred (`spellgrid.py`, from `icons.py`). Tests: `test_spellgrid`. Checked in the game: a
  Spellarcher's 1st-level picks in the new grid, a click on Shocking Grasp's new place taking it.
- **No Loader gear on the creation screen's stand-in**: a character left a while on the creation
  screen with its kit marked had its gear given then too (the dice log's "starts with ..." lines
  before its spell picks), and again after DONE; the game threw the first away. `game.being_new`
  now passes over a New record while the creation screen is up (`GameData.creating`), only the one
  DONE made (`making`). Test: `test_dicelog`'s `test_being_new`. Checked in the game: a Spellarcher
  renamed and left 25 s with its kit marked, no gear lines until after DONE, then once.
- **The Spellarcher: no Burning Arrows, saves as the spells', a Fine Bow and arrows to start** (after the game's manual and The Complete Fighter's Handbook): **Burning Hands**, a
  cone from the caster in the manual, is not a touch, so it makes no arrows (`ARROW_KNOWS` skips the
  first of `ARROW_SPELLS`, its place kept so the Loader's `USE_WHO` stays; `spellarrows.RETIRED`,
  and `SpellArrows.make` refuses it); Chill Touch, a touch in the manual, keeps its arrows. An
  arrow's target saves only as against the spell ("all normal saving throw attempts"): against
  Chill Touch, not Shocking Grasp or Vampiric Touch (`ARROW_SAVE` and `spellarrows.SAVED`, added
  earlier on this branch, gone). A new Spellarcher has a **Fine Bow** (name 173h, DSCLOG's 50th
  extra name: `NAMES_EXTRA` 50): **+1 to hit**, not magic (`FINE_HIT` in `PROBE_ATTACKS`; its item
  box "Hit +1", `IB_MATERIAL`; "+1 fine" in `game.weapon_hits` and the dice log's THAC0 line), and
  **24 Chill or Shocking Arrows** for the touch spells it picked as it was made (24 of each for
  both, no plain arrows), else 24 plain arrows (`spellarrows.starting_gear`, from
  `weaponchoice.kit_gear`; startgear's bow is the Battle Dancer's alone now). The arrow buttons'
  texts say a save stops Chill Touch, and none the others. Tests: `test_spellarrows`'
  `StartingGearTests` and `test_burning_hands_retired`, `test_dsclog`'s `test_fine_bow`,
  `test_item_box_material`, `test_spell_arrows` and `NamesTests`. Checked in the game
  (playtest/logs/2026-11-16-spellarcher-fine-bow.md): Spellarchers made with Shocking Grasp, with
  Chill Touch and Shocking Grasp, and with neither (their arrows as above, the Fine Bow in the
  missile slot, "Hit +1" in its box, "T16" on its weapon line); the USE screen with no Burning
  Arrows button for one knowing Burning Hands; a shot with "+1 fine" in the THAC0 line.
- **The Spellarcher, after *Dragon* #214's "The Complete Half-Elf"**: a spell slot makes
  **one** spell arrow (was 5 a preserver level); one stack of each spell, 24 at most, the arrow
  joining it wherever it is (a new stack in the quiver if empty, else the pack; a full stack takes
  none, no slot used); the arrows **last until shot** (no fading at a rest: the rest hook,
  `vanish` and `REST_REQUESTS` gone); the quiver no longer keeps them (`PROBE_TAKE`, its vector
  F7h, `QUIVER_KEPT` and `QUIVER_LOCKED` gone, and the game patch `take`); only a Spellarcher
  carries them (`ARROWS_FORBID` for readying; the game asks nothing of a backpack move, so
  `spellarrows.return_strays` takes any another member is given back to the Spellarcher, out of
  fights with the inventory shut); its plain arrows no longer 1 better: its
  **spell arrows** are +1 from 5th preserver level and +2 from 9th (`PROBE_ARROW`'s
  `ARROW_PLUS_NOW`, `kits.arrow_plus`); it wears **no armour, helm or shield** (`KIT_LIGHT`'s
  `BARE`, `kits.BARE_KITS`; bracers, robes and a cloak of protection allowed), its class's armour
  left behind at creation (`weaponchoice.kit_gear`). Tests rewritten: `test_spellarrows`,
  `test_dsclog`'s `test_spellarcher_arrows` and `test_spell_arrows_spellarchers_only`
  (`QuiverTests` gone), `test_kits`' `SpellarcherBareTests`, `test_dicelog`'s rest test.
  KITS.md, the player's guide, ITEMS.md, DICE-LOG.md, FEATURES.md, DEVELOPMENT-RULES.md and the
  patch notes say so. DSCLOG 70,256 bytes.
- **The Wayfinder: initiative only**: its Move +2 is gone (`KIT_MOVE`'s path
  block, the viewer's line); its initiative as below (its own +2, no penalty when down). Test:
  `test_scout_and_path_finder`.
- **The Sentinel: no initiative, −1 to hit without a shield**: its +2 initiative
  is gone (`PROBE_INIT`); `KIT_CHAMPION` now takes a Sentinel's melee attack without a shield in a
  hand 1 worse (`kits.champion`); its AC 2 better with one stays. Tests: `test_champion`,
  `test_dsclog`'s Sentinel cases.
- **The Grove Warden: its sphere's weapons** (in place of no metal weapons):
  `KIT_FORBIDS` gives the Grove Warden the Seeker's `SPHERE_ALLOWS` path (no bow kept),
  `KF_SPHERE` now the kit's class less 1, mod 4 (a druid's sphere as a ranger's); `kits.forbids`.
  Its kit gear is fitted as any kit's (`kit_gear`). Tests: `test_kits`' `test_seeker`,
  `test_dsclog`'s `CanUseTests.test_kits` (a Warden of each sphere).
- **The Crusader and Mind Warrior: their extra attacks with the chosen weapon alone**: with weapon specialization on, `WAR_KIT_HALVES` gives no warrior's 3/2 from 7th level
  with every melee weapon; the chosen weapon spec's expertise (3/2, 2 from 7th) is the extra
  attack (`kits.warrior_attacks`' `spec`). Without the rule, as before (their weapon kinds are any
  melee weapon). Tests: `test_warrior_kits_attacks`, `test_war_kit_expertise`.
- **The Mind Warrior: a fifth fewer PSP** (was a tenth): `PROBE_MAX_PSP` and
  `PROBE_CR_PSP` divide by 5 (`kits.MIND_PSP`). Tests: `test_max_psp`, `test_cr_psp`.
- **The Justifier: its chosen weapon spec specialized, the bow at expertise**:
  `SPEC_OF_SHEET`'s ranger bow path (a bow not chosen) skips the Justifier's step up
  (`specialize.skill` the same); a bow it chose is specialized. Test: `test_justifier`.
- **Two weapons: always on** (on purpose: the ranger's, Twin-blade's and Battle Dancer's two-weapon exceptions mean nothing without the rule): the Options switch
  "Two weapons" is gone (`game.RULE_SETTINGS`, the viewer's list, the player's guide's table);
  `game.RULES_ALWAYS` puts `RULE_TWO_WEAPONS` in every rules word, an older settings file's False
  passed over. Test: `test_viewer_settings` uses another switch.
- **The Twin-blade and the Brute: the cahulaks the Twin-blade's**: `KIT_FORBIDS`
  lets a Twin-blade hold them (a blade in each hand) and keeps a Brute from them (`KF_CAHULAKS`;
  `kits.forbids`' `cahulaks`), so a Brute can't dual to air cleric either (`DUAL_BANS`, `dual_bans`:
  no two-handed melee weapon it may use). In light armour a Twin-blade's cahulaks have no penalty
  on either head (`PROBE_TWO` passes it over before `CAH_ADJUST`, as before). Tests: `test_kits`'
  `test_cahulaks` and `test_brute_no_air_cleric`, `CanUseTests.test_kits`.
- **The Seeker: no bow exception, no bow expertise**: its bow follows its sphere
  (a fire Seeker has none; `KIT_FORBIDS`, `kits.forbids`), and it has no ranger's bow expertise unless
  the bow is its weapon spec (`SPEC_OF_SHEET`, `specialize._skill`). A forbidden missile weapon goes
  into the backpack at creation (`weaponchoice.kit_gear`). The weapon window offers it only its
  sphere's weapons, the bow among them where the sphere allows one (`KINDS_ALLOWED`,
  `restrict.allowed_kinds`: no other ranger is offered the bow). Tests: `test_seeker`,
  `test_seeker_bow`, `test_ranger_expertise`, `KindsAllowedTests`.
- **The Swashbuckler: bad luck** (in place of a flat penalty to every skill): each thief skill
  roll 0 to 25 worse, rolled each time: the game's (`PROBE_BELT`, a d26 less 1 from the game's seed,
  kept in the header's `BAD_LUCK`, +1862, and `BAD_LUCK_WHO` for the dice log's line, "-N
  Swashbuckler's bad luck") and the Loader's (`kits.bad_luck`: pickpocket.py, stealth.py). The
  skills shown are without it. Tests: `BeltTests.test_swashbuckler`, `BadLuckTests`.
- **The Lifebinder: Cell Adjustment a d4 more** (a non-psionicist picks four powers of
  one discipline, so a Lifebinder may have it): `CELL_SITE` (`kits.CELL_MORE`); the dice log shows
  "1d4 = 4, +1d4 = 3 (Lifebinder)"; the Healer's and Rescuer's 1 more (`kits.CELL_PLUS`, as their cures
  1 more a die: "1d4 = 3, +1 (Healer)"). Tests: `test_cell_lifebinder`, `test_manual_lines`.
- **The Wild Fury's check at −4 again** (after trying it without): `WILD_CHECK` −4.
- **The Shinobi's spells** are said to be its own short list (21), not every preserver spell.
- **The Wayfinder: its own +2 initiative, no penalty when down**: `PROBE_INIT`
  adds a Wayfinder's own 2 (`WAYFINDER_INIT`, `kits.WAYFINDER_INITIATIVE`) to the party's Path-finder
  1; `PATH_DOWN` and `GameData.path_lost` are gone. Test: `test_scout_and_path_finder`.
- **The Assassin's and Shinobi's light armour sleeps with the kit**: `KIT_FORBIDS`
  tests `KIT_AWAKE` before `KIT_LIGHT`, and `restrict.kit_forbids` and `forbidding_kit` take only
  awake kits'. Test: `CanUseTests.test_kits` (a human Assassin asleep, then awake).
- **The Healer and Lifebinder never know the harming spells**: Cause Light, Serious
  and Critical Wounds, Cause Disease, Poison, Slay Living (`AV_HARM` in `AV_KNOW` and `AV_GRANT`) and
  Harm (`NS_PRIEST_KNOWS`); `kits.NO_HARM`, `knows_heal`; the Healer's cosmos spells given by the
  Loader leave them out, and one made before has them taken away (`kits.avenger_heals`). Tests:
  `test_avenger_spells`, `AvengerHealTests.test_healer_and_lifebinder`.

**Fixed**
- **A code audit of the branch** (its findings, each fixed):
  - The dice log counted a Poisoner's dose only on a helpless target's hit, so after a weapon had
    poisoned an awake foe, its next hit on the same foe, held, was logged "poisoned by the hit"
    though DSCLOG poisons once a weapon a fight: every melee hit counts now (`_poison_dose`).
    Test: `test_poisoner_on_a_helpless_target`.
  - A Poisoner's `POISON_USED` (+1860) was cleared by the dice log at the first round's line, a pass
    after the round began at times (a first hit before it poisoned twice), and never without the
    dice log: DSCLOG clears it itself at a fight's first round (`ACID_ROUND`).
  - The Loader's figures (`game.weapon_hits`, the dice log's THAC0 line) gave the Swashbuckler's,
    Battle Mage's, Crusader's and Mind Warrior's warrior THAC0 with the rule for kits off, which
    DSCLOG doesn't: `kits.war_hit` takes the rule (`kits_on`). Test: `test_war_hit`.
  - `MYRM_POLEARM` put the polearm in a Myrmidon's second spec slot with nothing in the first (the
    weapon window closed without a pick): without the Loader, `LV_DUE` would then take it for the
    one pick and never ask. It waits for a first now (the Loader fills both). Test:
    `test_myrmidon_polearm`.
  - `GEAR_GIVEN` was left set once `GEAR_HOLD` had the gear in, and the Loader ORs into it: a
    needless redraw later. `GEAR_HOLD` clears it. Test: `test_gear_hold`.
  - Left as it is: the dice log reads the Swashbuckler's bad luck (`BAD_LUCK`, the last roll's)
    when it reads the roll, so two thief rolls in one pass show the second's luck on both.
- **The dice log's damage on a held target** (found in the kit checks): a Paralyzed creature takes
  a spell's most (the game's rule, as for one Out Cold), but the dice log said so only for Out Cold,
  so a held Arena Guard's "takes 15 from Magic Missile" stood under a roll of 9 with no word why.
  The line now says `(Paralyzed: the most the dice can do)` too (`_paralyzed`, `game.helpless`).
  Checked in the game (playtest/logs/2026-11-15-kit-rebalance-checks.md part 11): a held Templar,
  8 rolled, "takes 10 from Magic Missile (Paralyzed: the most the dice can do)". Test:
  `test_paralyzed_takes_the_most`.
- **A Brute could still change class to air cleric** (found in the game): the DUAL window greys
  only whole classes, so CLERIC stayed open for earth, fire and water, and the game's sphere menu
  makes its title row, or the menu closed, the air class. `PROBE_SPHERE` now checks the class the
  answer makes against the member's kits (`SPHERE_BARRED`, `KIT_BANS`) and, for a barred one, sends
  the game to the window's close (86B68h) with no change; EARTH, FIRE and WATER as before. Checked
  in the game (playtest/logs/2026-11-15-kit-rebalance-checks.md part 9): before, Cermak (a Brute in
  memory) became an air cleric on closing the menu; after, no change, and EARTH made him an earth
  cleric. Test: `test_sphere_barred`. DSCLOG 70,768 bytes.
- **A new character ADDed in a later session lost the Loader's creation gear** (found in the kit
  checks: a Myrmidon's polearm, a Swashbuckler's armour, a fighter's chosen weapon in place of the
  bone long sword). The game writes the character to the roster (CHARSAVE.GFF) at the end of DONE,
  after the psionic powers; the Loader's gear came after it, in memory only, for three reasons:
  the character reads Okay, not New, until after that write (`finish_new`, `class_gear`, `kit_gear`
  and `startgear.fill` give only to New ones); the Loader cleared `GEAR_DUE` while DSCLOG's weapon
  window was up, giving nothing; and `GEAR_WAIT` (VIEW CHARACTER's) cleared it when STATS weren't
  fresh, which on the creation screen they never are. Now DSCLOG names the character (`GEAR_WHO`,
  +1867; `game.being_new`), the Loader leaves `GEAR_DUE` set while the window is up, `GEAR_WAIT`
  and the new `GEAR_HOLD` (at the end of `CR_WEAPONS`, before the roster write) test for the Loader
  by its heartbeat (`LOADER_BEAT`, +1865, from the dice log's stats thread), and `GEAR_HOLD` waits
  for its gear (up to about ten seconds). Checked in the game
  (playtest/logs/2026-11-15-kit-rebalance-checks.md part 7): two fighters, slots 1 and 2, given a
  short sword and sling, and a bow, arrows and short sword, ADDed after a restart with them. Tests:
  `test_gear_hold`, `test_gear_due`, `test_being_new`. With weapon specialization off,
  `CR_WEAPONS` returned before naming the character, so `GEAR_HOLD` waited for nothing and the kit
  gear and fuller starting gear (which need no weapon specialization) still missed the roster: the
  new `GEAR_MARK` names it there too (not an EDIT that kept its race, classes and kit), and
  `GEAR_HOLD` holds the write. Checked in the game (playtest/logs/2026-11-16-roster-gear.md): a
  Swashbuckler made with the rule off, and the Myrmidon of the kit checks (long sword picked, the
  bone polearm in the backpack, the sling), each ADDed after a restart with all of it and, the
  Myrmidon, both weapon specs. Tests: `test_creation_weapons_site`,
  `test_creation_gear_held_rule_off`. DSCLOG 70,688 bytes.
- **An archer's turn lost with its last arrow** (the game's bug): the weapon
  attack routine (5883Ah) cuts a shot's attacks ([BP-8]) to the arrows left (5899Ah; "Out of ammo"
  with none) and, once that many are made, writes 63h to the attacker's +181h (58C45h), which ends
  the turn (5844Eh). A kill with attacks left lets anyone go on (the caller's loop), so an archer
  that killed with its last arrow lost a turn any other kill keeps. DSCLOG's new sites `AMMO_CAP`
  (5899Ah: the round's attacks before the cut kept) and `AMMO_TURN` (58C38h: a party member's attacks
  made compared with them) keep it; monsters as the game has them. Against a target still standing
  the turn ends as before (the game's rule: an attack command spends the turn unless it kills).
  Checked in the game (playtest/logs/2026-11-14-quiver-turn.md): Ester, one arrow and two shots,
  killed the Templar and kept her turn (walked on); without the two patches the turn went to Jenna.
  DSCLOG 70,208 bytes (+80).

**New**
- **An archer's arrows left, and its turn when the quiver runs dry**:
  `quiver.py`: after each party shot, "Arrows: N left" (the quiver's count) or "Out of arrows"
  floats over the archer (labels.py, the charges' blue and priority). A party member whose volley
  its quiver cut short keeps its turn against a target still standing: DSCLOG's `AMMO_OKAY` sites
  (5843Fh, 584A4h, 5850Eh) make the attack command's "target still Okay" tests answer "fallen" for
  it, NEW_AS_OKAY's jbe/ja kept in the same patches. A top-up of the quiver from the pack at each
  turn's start was built and seen working (the log's part 4), then taken out on purpose:
  reloading stays the player's. Tests: `test_quiver.py`; `test_gamepatch`'s
  `test_new_counts_as_okay` counts the three. DSCLOG 70,272 bytes.

**Changed**
- **Wild Fury's Wild Fighting is The Complete Barbarian's Handbook's again**: fighting wild is −3
  to hit and AC 3 worse (no worse than 10) for the fight whatever the check, and a passed check
  adds the extra melee attack and +3 damage on top; a failed one still gives the penalties alone.
  Before, a passed check gave the gains with no penalty, which made the kit near free at a mul's
  CON (70% to 95%). Gerakis's Wild Fighting, the same code, changes with it. The Loader (`wild.py`)
  sets KIT_WILD's bit N for anyone fighting wild and bit N + 4 as well when the check passed;
  DSCLOG already read the two bits apart, so only its comments changed (DSCLOG.EXE rebuilt
  identical). The Loader's to-hit figures (`game.weapon_hits`) and the dice log (`_kit_attack`)
  count the −3 either way. Tests: `test_wild.py`, `test_dsclog`'s `test_wild_fury` (bits 0x44:
  +1 attack, −3 to hit, +3 damage) and `test_wild_ac`, `test_now`'s `test_unarmed_kits`.
  KITS.md, DICE-LOG.md, DEVELOPMENT-RULES.md and the patch notes say so.

## Pull request #94 ([merged 2026-11-11](https://github.com/daaki85/darksun-obsidian-edition/pull/94))

Obsidian Edition 2.17.1 ([release notes](release-notes/v2.17.1.md)): an audit of 2.17.0 (the
DSCLOG changes, the Loader's Python and the documentation, each read by a reviewer of its own).
DSCLOG unchanged (70,128 bytes). The reviews found no correctness bug in the code.

**Fixed**
- **A manual page's title escaped once** (`manual._page`): a heading with "&" gave "&amp;amp;" in
  the page's `<title>`. Test `test_title_escaped_once`. The release test reads pictures (`src=`)
  as well as links on the patch notes page.

**Docs**
- The player's guide's "Making a party" and KITS.md's "Choosing at creation" name the psionic
  picks after DONE; GAME-BUGS.md has Kurzak's door; PATCH-NOTES.md lists all ten manual pages and
  moves the ranger's window title from Bug Fixes (it was the mod's own window, at creation and at a
  level up) to weapon specialization; the #93 entry has its release line and DSCLOG's figures,
  and DEVELOPMENT.md's limits are 2.17.0's (`UMB_KEPT` 83 paragraphs spare); DEVELOPMENT-RULES.md's
  lock playtest is back with the locks, the pocket tests named in tests/test_pickpocket.py; the
  README says the patch notes page is in the release's folder; the playtest kit's notes: the
  doorway save opens within 10 game seconds, the weapon window's title for the Crusader and Mind
  Warrior, and the walkthrough no longer named by its public source.
- Left as it is: a thief caught at a pocket under 2.16 stays barred from that person for good in
  a save of then; the "until a level" rule counts from 2.17 on.

## Pull request #93 ([merged 2026-11-11](https://github.com/daaki85/darksun-obsidian-edition/pull/93))

Obsidian Edition 2.17.0 ([release notes](release-notes/v2.17.0.md)).

DSCLOG.EXE 70,128 bytes (64,576 in its segment), 960 of its segment spare; `UMB_NEED` 6,477
paragraphs (1,705 spare), `UMB_KEPT` 8,099 (83 spare). 2.16.1's: 69,360 and 1,728 spare.

**New**
- **Psionic powers picked at creation**, for full psionicists and for others. The game gave every new character of a
  discipline the same four powers and Mind Blank, and every psionicist its level's row of a
  table (5, 6 or 11). Now DONE opens the level up's PICK A PSIONIC POWER window for as many picks
  (four; a psionicist 4, 5 or 10), after a warrior's weapon window: one not a psionicist picks from
  its own discipline (the discipline button stays on it), a psionicist from all three. Mind Blank
  is still everyone's; powers known are left out of the list; EXIT leaves the game's own for the
  picks unmade; EDIT with the same classes and discipline keeps the powers; the game's own party
  (START GAME) keeps the game's. DSCLOG's `PSI_GRANT` (66DDEh), `PSI_ASK` (from `CR_WEAPONS`),
  `PSI_LIST` (86143h) and `PSI_CYCLE` (8631Ah), gamepatch `psi_grant`, `psi_list`, `psi_cycle`.
  DSCLOG.EXE 70,128 bytes. Seen in the game: a fighter (telepathy: two picked, two the game's on
  EXIT), a 3rd-level psionicist (ten picked across the three), EDIT, a character dropped and added
  back from the roster with its picks, and START GAME's party with the game's powers
  (playtest/logs/2026-11-11-psionic-picks.md).
- **The manual: the player's pages as web pages that link to each other, in the download.** The
  zip's `manual` folder has ten pages, each made from its Markdown (which stays the source and
  reads the same on GitHub): `index.html`, the start page, from the README; the player's guide,
  features and rules, kits, items (spoilers), creatures (spoilers), the game's bugs fixed (some
  spoilers), the dice log line by line, how the original game works, and the changes from the
  original game (`changes.html`, from PATCH-NOTES.md through `patchnotes.py`). Each page has a bar
  of all ten (the one on show marked, the spoiler pages marked so, their own warnings kept) and an
  index of its sections and subsections; they share `manual/manual.css` (the patch notes' look and
  fonts, loaded once, not in every page). Links between the pages go to the HTML files with the
  same anchors (`KITS.md#x` is `kits.html#x`, the README `index.html`, the patch notes by path or
  GitHub address `changes.html`), pictures to `../docs/`, and the development pages, the changelog
  and the rest of the repository to GitHub. The Loader's **Help** button opens
  `manual/index.html` (`viewer.HELP_PAGE`, `manual.START`); `player-guide.html` beside the Loader
  is gone, now `manual/player-guide.html`.
- **`dsloader/manual.py`** makes them (`python -m dsloader.manual`; `python -m dsloader.guidepage`,
  now its alias, too), from the guide's converter made general: Markdown blocks parsed
  recursively, so a list item can hold tables, code, pictures and paragraphs (the guide's two
  tables inside list items, its CHA prices and DEX modifiers, showed as raw `|` rows), fenced code,
  block quotes (the Announcer's and Legcrusher's lines), `***bold italics***`, `<https://...>`
  addresses, a numbered list's start, table column alignment, lazy continuation lines, and
  GitHub's anchors for repeated headings (`-1`, `-2`), with links' text in a heading's anchor as
  GitHub has it. `patchnotes.body` takes the manual's link rule for its copy; the root's
  `patch-notes.html` is unchanged. Tests `tests/test_manual.py` (replacing `test_guidepage.py`):
  each page and the style up to date (the failure names the command), every relative link and
  picture a file in the zip and every `page.html#anchor` one that page has, no link to a `.md`
  file, no id twice on a page, no Markdown left showing, the converter's pieces, and Help's page
  read from `viewer.py`'s source (no tkinter needed); `test_help_opens_the_manual` in
  `test_viewer_options` with tkinter. The README, its front page's documentation list, the
  player's guide and DEVELOPMENT.md (the folders, Build, the tests, Making a release) say so.

**Fixed**
- **Kurzak's door, open but barring the way** (a save named "error doorway blocked"). The
  pens' entryway (squares 99,33-34) was drawn open and both its leaves (objects 2145-2146) were
  open, but the game's live walk map still had square 99,34 shut: the party could not step into
  the doorway, and Legcrusher, sent to fetch them, stood still for good (his only way to them).
  The dice log now puts it right (`kurzakdoor.py`): in the pens, out of fights, with both leaves
  open (their map record's +12h, bit 08h) and the square shut for 10 game seconds (longer than a
  door's swing), the square is floor again, and the log says "Kurzak's door: open, but its doorway
  was barred on the map; opened". On that save Legcrusher walked through at once and said
  his line, and the party walked through to Kurzak ("I'm glad you listened to Legcrusher"). The
  game's own call was checked too, unchanged: it opens the door, and Legcrusher comes through it.
  Tests `tests/test_kurzakdoor.py` (playtest/logs/2026-11-11-doorway-blocked.md).
- **Kalzith's background fits Athas** (a sorcerer's apprentice doesn't, where wizardry is
  a crime and the sorcerer-kings keep magic to themselves and their templars). He kept the tallies
  for a merchant house in Draj, was taught in secret by a defiler among its caravan hands, and was
  caught by the templars drawing life from a noble's garden; then the arena's line as before, on a
  second page (`kalzith.py`'s "Who are you?"). Seen in the game: both pages fit his window
  (playtest/logs/2026-11-11-kalzith-background.md).
- **A pocket is barred until a level only when the thief is caught**. With **Thieves as in AD&D**, a fumble the thief slipped away
  from barred that thief until a level gained, and the game said "Magramar needs another level to
  try them again", which told the player more than the thief could know. Now a thief who slips away unnoticed may try
  again at once; one caught (the pick and the move silently both failed) is remembered as
  `pickpocket.caught_key` and may try that person again once a thief level is gained, others at
  once (without the switch, caught is for good, as before). The game's words stay in the story:
  "Kurzak catches Magramar's hand!", and a try too soon "Kurzak remembers Magramar, and keeps a close
  hand on their purse."; the rule's reason is in the dice log alone. An older save's fumble keys
  are ignored. Tests `test_caught_with_thieves_as_in_add`, `test_slips_away_with_thieves_as_in_add`.
- **A ranger is asked for a weapon of expertise, not a specialty**. Creation's
  weapon window had a fixed title, "PICK A WEAPON SPECIALTY,", though a ranger (or a Battle Mage, a
  Crusader, a Mind Warrior) takes expertise and each weapon's box already said "EXPERT IN". DSCLOG's
  `LV_TITLE_OF` now gives "PICK A WEAPON OF EXPERTISE," when `PK_WORD` judges the first kind
  expertise. DSCLOG.EXE 69,424 bytes. Seen in the game (a new human ranger); test `test_pick_title`.
- **The release has the patch notes' web page** (2.16.1's didn't). The page is
  made at the repository's root, beside PATCH-NOTES.md, and the zip is the obsidian-edition folder
  alone, so no release had it. The Release workflow now adds it to the zip's folder, next to
  the manual's folder (`.github/add_to_zip.py`), and attaches it to the release on its own too.
  Its links are all web addresses, so it works from the zip. Test `tests/test_release.py`; the
  README's documentation list names it.

## Pull request #92 ([merged 2026-11-11](https://github.com/daaki85/darksun-obsidian-edition/pull/92))

No release: nothing in `obsidian-edition/` changed (it is 2.16.1's, byte for byte).

**Dev** (the playtest kit)
- **The installers from a private repository.** `env.sh` names `INSTALL`, the private
  `daaki85/darksun-installation-files` checked out beside this repository (`PT_INSTALL_FILES` to
  override). `setup_game.sh` and `setup_ravager.sh` run its `join.sh`, which rebuilds both
  installers in `$WORK/dl` and checks their checksums; `setup_guide.sh` takes the walkthrough from
  it. Tried from an empty work folder: game extracted, walkthrough made into text. The guide and
  CLAUDE.md say how.

## Pull request #91 ([merged 2026-11-11](https://github.com/daaki85/darksun-obsidian-edition/pull/91))

Obsidian Edition 2.16.1 ([release notes](release-notes/v2.16.1.md)).

DSCLOG.EXE 69,360 bytes (63,808 in its segment), 1,728 of its segment spare; `UMB_NEED` 6,429
paragraphs (1,753 spare), `UMB_KEPT` 8,051 (131 spare). 2.16.0's: 69,344 and 1,744 spare.

**Fixed** (from a review of the repository by ChatGPT, checked against the code first)
- **S never takes an item without paying for it.** `sell.sell` unlinked every item and paid the
  total at the end, so a failed money write left the gear gone and the purse unchanged (and, with
  the key counted once, never retried). Now each item is paid for, then unlinked, and the pay taken
  back if it can't be. Tests `test_a_failed_money_write_takes_nothing`, `test_a_failed_unlink_is_not_paid`.
- **A save put back in a slot with its old time is copied to Named saves.** `namedsaves.sync`
  skipped a slot whose copy was as new or newer, whatever it held, so a restored older backup left
  the named folder offering the newer save. A copy is now the slot's only with the same time and
  size, or the same bytes. Tests `test_older_backup_put_back`, `test_same_name_other_bytes`.
- **"Copy as Markdown" on the patch notes' page says "Copied" only when it was:** a failed copy
  shows the text selected, with a note to press Ctrl+C.
- **The Help page (player-guide.html):** its index has each section's subsections, as the guide's
  contents do (Fighter, Thief, Saving throws...), and its links to the mod's other pages (KITS.md,
  FEATURES.md...: 37) go to their GitHub copies, whose heading anchors a browser follows (a local
  .md file opens as plain text, or not at all). Test `test_index_and_other_pages`.
- **Links that left the zip:** DEVELOPMENT.md's links to `../playtest/` and `../CHANGELOG.md` go
  to GitHub; `test_shipped_pages_stay_in_the_zip` keeps every shipped page's links inside the
  folder.
- **A failed lock is remembered by what it is, not its map number** (the 2.16.0 audit's leftover).
  `locks.py` kept the thing number the lock's script was started on; the game hands map things'
  numbers out again as it makes and drops them, so a lock could be forgotten, or another barred.
  A failure is now remembered as the lock's object and place (`o1568@201,1402` for Pehtucl's
  chest), and the table DSCLOG reads is made from whatever things are that lock now
  (`locks.things_now`); an older key's bare number is read as before. Seen in the game: Gerakis's
  failure at the chest barred his next try. Test `test_a_lock_by_what_it_is`.
- **A second body's T no longer replaces one not yet taken** (the audit's other leftover). DSCLOG
  kept one pending T; a second, before the Loader had taken the first, overwrote it. Now
  `LOOT_KEY` leaves a T as the game's key (the window stays open, to press again) while
  `LOOT_THING` isn't FFFFh, and the Loader sets it back once it has taken the body
  (`loot.release`). Seen in the game: Pehtucl's body and a guard's, one after the other, both
  taken. Test `test_one_pending_at_a_time`.
- **Caps Lock no longer swaps T and Shift+T** (from the 2.16.0 audit). `LOOT_KEY` took the mode from
  the letter's case, which Caps Lock turns round; it now reads the Shift keys held (the BIOS
  keyboard flags, 0:0417h bits 0-1). S has no mode, so either case already sold the same. Tests
  `LootKeyTests` (test_dsclog_drawing).
- **A T or S whose work fails is counted once** (from the audit): an error other than the game
  being busy with its lists left the key unhandled, so the dice log tried it again each pass.

**Changed**
- **The playtest kit no longer fetches the game, Wake of the Ravager or the walkthrough from public
  links** (sharing them would be piracy). The setup scripts take one's own copies
  put in place by hand, and say so when they're missing; the Drive copies' downloads are
  restricted.
- **Code tidying from the audit:** a stack is priced by its count as stored, as the game's own
  sale (83D6Bh) does (was at least 1). `test_worn_and_held_kept` is now `test_a_body_slot_kept`
  (what it tested: plain_gear's slot test), and `test_worn_and_held_lists_untouched` checks that a
  worn and a held sword are left alone. Old switch names in comments (`RULE_HI_BACKSTAB`,
  `RULE_HI_BUYBACK`, "RULE_HI 64") now the merged rules' (`RULE_THIEF_TABLE`, `RULE_HI_CHA_PRICES`).

**Docs**
- **Reorganised, from the review**:
  - The player's guide's **Options tab at a glance** is a table of every switch: its Loader label,
    default, when it takes effect (at once, next start, new characters, first visit) and where its
    details are; `tests/test_optionstable.py` keeps it in step with the Loader's labels. The guide's
    opening names the places and people the labels show.
  - The packaged README's **What it does** is eight short families with links; its update section
    has Updating, Backing up your saves, **Compatibility with older saves**, What the Loader writes
    and Uninstalling; its documentation index links **Weapon specialization and damage**.
  - The Loader's longest option texts are shortened to the switch's effects (the names kept; the
    detail is in FEATURES.md).
  - DICE-LOG.md: looting and selling under a new **Inventory and shops**. ITEMS.md: the item
    indexes first, the mod's own items' details after.
  - PATCH-NOTES.md is **Changes from the original game**, with an **At a glance** summary, a
    **Documentation** section (How the game works, moved out of The Loader), and a subtitle that no
    longer promises every change; the web page carries the note on unreleased changes.
  - The old combat log design handoff moved out of the shipped `docs/` to
    `reports/combat-log-design-handoff.md` (now `reports/archive/`).
  - The root README's What's new holds the current release only.
  - The playtest guide: a **Startup procedure** first (about 1,900 words, read in full), then
    **Recipes** by job and **The route through the story**; dated incidents moved to
    `playtest/HISTORY.md`. CLAUDE.md's summary cut to the essentials.
- **From the review:** the 2.16.0 release notes said each merged switch keeps its saved choice;
  it does only when the old pair agreed (`game.fold_merged`: one off, the merged one off), now
  said, and in the changelog. The update steps (the release notes, the README) name the **Named
  saves** folder with `settings.json`, and the backup steps the `cloud_saves` folder the game
  reads first. The guide's weapon table gives the bow (1d8) and sling (1d4) their own dice, as the
  game rolls them (was "by the missile"), and its opening names what has no switch (the keys, the
  game's fixed bugs, the footman's pick; was "every rule change"). The patch notes' Spellarcher
  says its arrows fade at the next rest. `docs/viewer.png` retaken (the toolbar's Help button).
- **The combat log's pictures retaken with the panel's present font** (8 pixels a line, 7 lines
  docked, 12 expanded): `docs/combat-log.png`,
  `combat-log-expanded.png`, `combat-log-detail.png` (now from Pehtucl's ambush, not the alarm
  fight) and `combat-log-live.gif`, with their alt texts. The GIF is DOSBox's own 320x200
  screenshots taken about 14 a second (Ctrl+F5 in a loop), not window grabs: the window is 4:3
  (playtest/logs/2026-11-11-combat-log-shots.md).

## Pull request #90 ([merged 2026-11-11](https://github.com/daaki85/darksun-obsidian-edition/pull/90))

Obsidian Edition 2.16.0 ([release notes](release-notes/v2.16.0.md)).

DSCLOG.EXE 69,344 bytes (63,792 in its segment), 1,744 of its segment spare; `UMB_NEED` 6,428
paragraphs (1,754 spare), `UMB_KEPT` 8,050 (132 spare). Before the T and S keys, 69,136 (63,584,
1,952 spare); before the pointer and lock changes, 68,976 and 2,112 spare. The polearm's reach took 384
bytes of the segment (68,592 bytes before it).

**New**
- **Selling plain gear in one go** (the member on show, plain gear only):
  on a shop's screen **S** sells the plain weapons, armour, shields and clothing in that member's
  backpack (no plus, no power; not worn or held; not ammunition or metal; not keys, nor what
  the shop won't buy), each
  at the game's price (its value, times the count for a stack; 60% with Shops as in AD&D, as DSCLOG's
  SELL_PRICE). DSCLOG's `SELL_KEY` (only while the shop's loop has run in the last two BIOS ticks:
  `SHOP_LOOP` now marks the time) makes the key Escape and notes the member on show (the game's
  3931h:25Bh) and the merchant (header +1852 to +1858); `sell.py` sells once the shop is shut. Seen in
  the game with a save (Kalzith's shop, before ammunition and metal were kept: Gerakis 10 things for 119, K'ratchek 12 for 98, the
  magic ones kept: playtest/logs/2026-11-11-selling.md); tests/test_sell.py.
- **Legcrusher at the fountain**: sent to fetch a party that is in the fountain's
  room or the passage before it, he says they are out of their cells, yells for the guards (the
  fountain drowns it) and attacks alone, instead of his warning (`kurzak.with_fountain`, script 136).
  Seen in the game; tests `FountainTests`.
- **Looting a body in one go**: with a body's (or any container's)
  window open, **T** takes everything in it into the party's backpacks and **Shift+T** all but plain
  weapons (no plus, no power); what has no room stays. DSCLOG's `LOOT_KEY` (in the INT 16h hook)
  makes the key Escape, which shuts the window, and counts it with the container (the game's
  DS:05E6h, its map thing while the window is open) and the mode (header +1846 to +1850); the
  Loader's `loot.py` moves the things once the window is shut (each to the first member, in the
  party's order, with a free backpack cell, as a picked pocket's), links the container's list again
  from what stays or gives it back when empty, and logs who took what, with the purse's sound. Seen
  in the game (Pehtucl's ambush: his body with Shift+T, all 11 things taken; a guard's with Shift+T,
  the bow and sword left, then T: playtest/logs/2026-11-11-looting.md); tests/test_loot.py.
- **A lock or a pocket a thief failed is tried again by that thief only after a level gained**
  (*Player's Option: Skills & Powers*' open locks), with **Thieves as in AD&D**. A new
  site, `LOCK_SITE` (803D3h, the game's skill check's chance), makes a lock the member failed at its
  thief level now out of reach (`LOCK_BARRED`, at DSCLOG's header +1844, kept by the Loader's
  `locks.py`); a fumbled pocket (failed, unnoticed) is refused to that thief the same way
  (`pickpocket.fumble_key`). Another thief of the party may try either. Being caught stays final.
  Traps: the mod's only trap, Pehtucl's chest's needle, is spent whether found or sprung, so no
  rule is needed there. DSCLOG.EXE 69,136 bytes. Seen in the game (Pehtucl's chest:
  playtest/logs/2026-11-11-lock-retry.md); tests/test_locks.py.
- **Staff sling stinkpots** (AD&D's Arms and Equipment Guide), under the cahulaks' switch, now
  **Weapon traits** (the setting `cahulaks` as before, so a 2.15.0 settings file keeps its choice;
  `RULE_HI_CAHULAKS`; `game.RULE_STINKPOTS` names it). It had a switch of its own on bit 2 of the
  rules for a while; merged, bit 2 is free again. The staff sling's shot is a clay pot of burning sulphur: 1d3 crushing against any
  size (DSCLOG's `STINK_SIDES` makes item type 0's sides 3 in the game's type table, at its read and
  at each pass of the main loop; 4 again with the rule off), and a hit that did damage (`STINK_HIT`,
  from the cahulaks' `CAH_HIT` site) makes a target that is neither undead (the game's test, 7BE20h)
  nor immune to poison (7B492h's share of the poison damage kind) make the game's own save against
  power 176 (paralysis/poison/death, every modifier counted). A failure is Nauseated, a new effect
  (75), for 1d3+1 rounds, added through 76442h under Stinking Cloud's number: `NS_HIT` takes 2 off the
  nauseated creature's attacks, and `NS_ENTRY` names it NAUSEATED with Stinking Cloud's icon (the
  game's table of effect names ends at 74; its entry is kept past Reflected Image's). The dice log
  names the save for the stinkpot and gives the rounds (`MN_STINK`, `MN_NAUSEA`), and the to-hit
  breakdown `-2 Nauseated`. (Tests: tests/test_stinkpots.py; `test_to_hit_effects`. Seen in the game
  2026-11-10: a held target nauseated, a free one's save, a nauseated attacker's -2,
  playtest/logs/2026-11-10-stinkpots.md.)
  Dispel Magic doesn't end Nauseated: the game's weighs only effects 0 to 73 (its loop, 7936Ch).
- **Polearm reach**, under **Weapon traits** too: a combatant, party member or foe,
  whose hands hold a polearm and no other weapon (a shield beside it, or a bow in the missile slot, is
  fine) strikes in melee at two squares as well as at one. One new site, `REACH_SITE` (`gamepatch`
  "polearm_reach", 2211Fh: the end of the combatant distance routine, 1A0A:2BA5h): a distance of 2 is
  1 for the game's melee tests (the pointer's sword, the attack pointer's click, the walk arrow's
  click on a foe, the walk to attack arriving, the step switch's case 19, and the computer's attack
  choice in overlay 612Eh), told by the way back, when the attacker's hands qualify (`REACH_HANDS`,
  `kind_of_type`'s polearm) and the game's line test (898:00A4h) finds no wall between. The type's
  range byte stays 1 (above 1 the attack routines take a weapon for a missile weapon, playtest/logs/
  2026-11-10-polearm-reach.md). Two squares diagonally count 3 (no reach); the reach goes over a
  creature between; the computer still walks up beside its target and uses the reach only on a foe
  already two away. (Tests: tests/test_reach.py. Seen in the game 2026-11-10: a polearm swung from two
  squares with no movement left, the bow in the missile slot left alone, playtest/logs/2026-11-10-polearm-reach.md.)

**Fixed**
- **From the code audit before 2.16.0:**
  - The stinkpot and the cahulaks' tests at a hit (DSCLOG's `CAH_HIT`, and the cahulaks' second
    swing) read the attack's item type, `[BP+14h]`, which the game leaves unset for a natural
    attack (no item, `[BP+12h]` -1). A claw or fist with a stale 0 there would have been a
    stinkpot. Both now need an item, and the stinkpot a shot (`[BP+16h]` over 1), not a blow with
    the staff sling. Test `test_not_a_natural_attack_or_a_blow`.
  - T could lose things when the game had too few free things to make a member's backpack list:
    they were unlinked from the body before the list was asked for. `loot.take` now makes or finds
    each taker's list while planning, before anything moves. Test `test_no_list_to_be_had`.
  - A game restarted in the same DOSBox keeps DSCLOG's header address: the dice log's lock table,
    and its T and S counts, are now taken afresh on attaching.
  - S cleared the shop's stamp as it counted, so a Loader pass before the shop had shut could
    sell while the shop's code still ran. The dice log now waits `SHOP_FRESH` ticks after it sees
    the S, and the shop's loop re-stamps if it is still running. Seen in the game: the sale comes
    as the shop shuts.
- **The sewer grate's hack wants a melee weapon**. The weapon search (script 137
  at A79h) took whatever was in the weapon hand, a bow too; now the first item in either hand that
  is a melee weapon, and with none no "Hack the lock off." is offered. The scripts can't read an
  item's type, so the test leaves out the kinds held in a hand that aren't melee weapons
  (`scriptfixes.NOT_MELEE`, checked against the game's data by `test_not_melee_kinds`). And the
  hack named the wrong weapon: on a find the game looped once more, and that step copied the next
  item over the found one ("hacks the lock off with his Bow" with an axe in hand); now the search
  ends on the find. Seen with a grate save: the axe used, and with only a bow in hand no
  hack (playtest/logs/2026-11-11-grate-melee.md).
- **Semyon's shipment reaches an emptied weapon rack** (his tip, then an empty rack). A rack the party had emptied has no list of contents, and `semyon.ship` only added to one;
  now it makes the list (`semyon._new_contents`, from the game's free things). Seen with a save (playtest/logs/2026-11-11-semyon-rack.md); test `test_rack_emptied`.
- **Every thri-kreen leaves a thri-kreen's body** (the arena's died as a human's
  Dead Body). DSCLOG's body choice (PROBE_WORN at 59412h) names the dead Tohr-kreen's body (2666) for
  any dying thri-kreen (its sheet's race), once the game has the Loader's objects (OBJECTS_ON), not
  only the champions' Tohr-kreen; the body is added to the Loader's SEGOBJEX copy whatever the
  switches (`champions.body_chunks`). Seen in DOSBox (a guard made a thri-kreen: its body 2666).
  (Test: `test_champion_body`.)
- **Pehtucl's chest spoke with the last face shown** (Kalzith's, after talking
  to him). Its script set no portrait, so the dialogue window kept the last one; it now sets the
  window's emblem first (GPL 54h with 0, `pehtuclchest.EMBLEM`), and the dice log names the lines
  "Narration". The script is the Loader's copy, so saves already past the pens have it too. Seen in
  the game (playtest/logs/2026-11-11-lock-retry.md).
- **The pointer left images of itself on the map** (in a fight, after 2.15.0).
  2.15.0's audit turned interrupts on for the whole of PROBE_SCROLL's pass (the map's main loop), so
  the game, which draws its pointer from the mouse's interrupt (keeping what is under it, to put back
  when it moves), could draw it in the middle of DSCLOG's own drawing. Now they are off again while
  DSCLOG draws (`DRAW_MASKED`: the dust and whirlwinds, the view drawn again, the panel, the labels,
  a drag's or the Loader's scroll), as before 2.15.0, and on for the rest (the sounds, the clicks).
  DSCLOG.EXE 16 bytes larger (68,992). Not reproduced here before the fix (sweeps of the pointer with
  the view drawn again 30 times a second showed none); seen not to recur after it in the same test.
  (Tests: tests/test_scroll_interrupts.py.)
- **The Spellarcher's arrows play their spell's cast sound as they are made** (no sound). The Loader asked for it from the map's main loop (`SOUND_REQ`), which doesn't run while the
  USE screen, where the arrows' button is, is open. Now it hands the sound over with its answer
  (`PICK_SOUND`, as a picked pocket's), and DSCLOG's `ARROWS_ASK` plays it at once (Burning Hands'
  and Shocking Grasp's 81, Chill Touch's 78, Vampiric Touch's 82). DSCLOG's size unchanged (the 8
  bytes in the segment's padding).
- **The stealth rule's "enemy beside" counts a big creature's every square** (a thief hid in shadows next to an otyugh). The test measured from each foe's own square; a creature
  bigger than one square (the sheet's byte +3Dh: & 7 its squares to each side, / 8 its squares north,
  as the game's distance routine, 1A0A:2BA5h through 1A0A:2AB4h, has them) could stand beside the
  thief with its square two away. `stealth.footprint`, `stealth.touching`. (Tests:
  `test_big_enemy_beside`, `test_big_enemy_north`.)

**Changed**
- **The hide and pickpocket sounds about 5 dB louder** (still too quiet). DOSBox plays every
  clip at the same peak (the descriptor's +0Ah, 6Eh, isn't a volume: from 20 to 127 the output
  peaked the same), so `sound-data/make.py` puts each through its soft limiter harder (hide 12 dB,
  was 3; pick 9, was none): in DOSBox's output their loudest 400 ms went from -32.9 and -36.1 dBFS
  to -27.5 and -30.5, against the game's fight sounds' -26.7 to -31.2
  (playtest/logs/2026-11-10-sounds-denser.md).
- **The combat log panel's font a pixel bigger**: the X11 misc-fixed 5x7 glyphs (public
  domain, as the 4x6 were) in a cell 5 wide and 8 high with the shadow, so 7 lines docked (was 8) and
  12 expanded (was 14). `smallfont.py` keeps each glyph's 7 rows as two hex digits.
- **Six switches merged into three**, freeing three of DSCLOG's rule bits with bit 2
  already freed (the Weapon traits merge): four free now, room for the rules to come. Each keeps one
  setting's name, so a saved choice carries over (`game.fold_merged`: if the old pair differed, the
  merged switch is off): **Saving throws against spells** (`spell_save`:
  the spell save and DEX instead of a doubled d20; bit 8, the spell save's, which only the Loader
  acted on, free), **Shops as in AD&D** (`cha_prices`: the leader's CHA and buying back magical
  items; RULES_HI 64 free), **Thieves as in AD&D** (`thief_table`: AD&D's thief skills and the
  backstab's dice; RULES_HI 128 free). `game.RULE_SPELL_SAVE`, `RULE_BUYBACK` and `RULE_BACKSTAB`
  name their switches' bits; the Options texts, FEATURES, the guide and DEVELOPMENT-RULES name the
  switches. A 2.15.0 settings file's `no_doubled_save`, `buyback` or `backstab_dice` unticked unticks the
  switch it joined (`game.setting_on`), and the first save folds it in and drops the old key
  (`game.fold_merged`, from `launch.save_settings`), so a player keeps the game's rule they chose.
  (Test: `test_merged_switches`.)
- **The pick is the footman's pick and the axe the battle axe** (*Player's Option: Skills & Powers*): every pick (the game's type 112, Deepbiter's and the stone picks', and the
  Loader's Metal Pick, 127) 1d6+1, was 1d4+1 (the horseman's); against a large target 2d4 (was 1d4),
  and the axe 1d10 (was its 1d8). DSCLOG's PROBE_TYPES_FILL sets type 112's sides (no switch, as
  the Great Axe's material), `npcitems` the Metal Pick's; LARGE_DICE and `sizes.LARGE_DICE` the
  large dice (with **Creature size as in AD&D**). KITS', FEATURES', the guide's and
  HOW-THE-GAME-WORKS' tables. (Tests: `test_room_and_filled`, `test_sizes`, the KITS table's. The game's
  type table read 1d6+1 for both picks in the game, playtest/logs/2026-11-10-stinkpots.md.)
- **Grand mastery's die is the next greater die size, against every target** (Player's Option:
  Combat & Tactics). It was 2 more sides (a d12 became a d14) and was lost against a large target:
  the creature size rule's large dice (SIZE_DICE, at the swing) replaced the step PROBE_SPEC_DAMAGE
  had made. Now DSCLOG's NEXT_DIE (d2, d3, d4, d6, d8, d10, d12, d20) steps the die at the attack,
  the View Character and inventory lines, and a grand master's large dice: a long sword 1d10, and
  1d20 against a large target. The dice log says `(1d20 for 1d8: a large target, grand mastery)`.
  (Tests: `test_grand_mastery_next_die`, `SizeTests.test_grand_master_on_large`, `NextDieTests`. Seen in
  the game 2026-11-10: a grand master's long sword 1d20 on a large Templar,
  playtest/logs/2026-11-10-grand-mastery-large.md.)

**Docs**
- docs/options.png retaken: the Options tab with the merged switches (Weapon traits, Saving throws
  against spells, Shops and Thieves as in AD&D), Rule changes and New content open; 706 x 2473.
- KITS: a table of every weapon spec's dice, man-sized and large, with and without grand mastery
  ([Grand mastery's damage](obsidian-edition/WEAPON-SPECS.md#grand-masterys-damage); `GrandMasteryTableTests`
  keeps it in step with `sizes.LARGE_DICE` and `specialize.next_die`). The staff sling's row is its
  stinkpot's: 1d3, 1d4 under grand mastery.
- The stinkpots in FEATURES ([Staff sling stinkpots](obsidian-edition/FEATURES.md#staff-sling-stinkpots)),
  DEVELOPMENT-RULES, ITEMS, DICE-LOG, the player's guide and the patch notes; DEVELOPMENT's sizes.
- The polearm's reach in FEATURES ([Polearm reach](obsidian-edition/FEATURES.md#polearm-reach)),
  DEVELOPMENT-RULES, ITEMS, the Options text, the player's guide and the patch notes; DEVELOPMENT's
  sizes.
- The player's guide's magic items: "Six scrolls" named as Kalzith's, and the defilers' scrolls listed
  (any preserver spell; the champions' bout's defiler always has one); ITEMS likewise.

## Pull request #89 ([merged 2026-11-10](https://github.com/daaki85/darksun-obsidian-edition/pull/89))

Obsidian Edition 2.15.0 ([release notes](release-notes/v2.15.0.md)).

DSCLOG.EXE 68,032 bytes (image 68,000: 62,480 in its segment, 5,520 in the tail), 3,056 of its
segment spare.

In short:
- **Three new rules**, each a switch on by default: **held targets** as in AD&D (a blow on a held or
  sleeping creature hits automatically, for normal damage), **creature size** (AD&D's weapon dice
  against large targets; Hold and Charm Person fail on them) and **cahulaks** as Dark Sun has them
  (a head in each hand, and a hit that can tangle).
- **Spells, psionics and monsters as the manual describes them**, Turn Undead by AD&D's table among
  them; the missile and hostile touch spells **roll to hit**.
- **Resting** heals by the priests' spells and natural healing; **dual-classing** as the manual has it.
- **New gear:** the Boots of Speed; more cahulaks (a Cahulaks +2, metal and obsidian cahulaks); the
  game's own Polearm +1, never placed before; foes who fought with their fists are armed.
- **Air clerics may use cahulaks**, and the Brute may dual-class to air cleric; **every thri-kreen**,
  foes too, throws a chatkcha twice a round.
- **The dice log** has a readable layout, a summary as each fight ends, and Turn Undead's rolls.
- **The combat log panel** has a smaller font (8 lines docked, 14 expanded), and its Short lines
  read as the readable layout does.
- **The Loader** has a Help button that opens the player's guide; Fastest is the default speed.
- **Smoother play:** steady pace without the choppy walking; shadows, dust and see-through figures
  drawn for less.
- **Graphics no longer disappear in a busy area** (the game's 300 picture slots reused), nor do
  figures after many gear changes.
- **The creatures' table** (CREATURES.md): every creature, its figure, its size and whether it can
  be tangled.
- **Fixes:** the game's (Scare's save, "can't save" that saved, Pehtucl's ambush, missiles from
  behind, the Quicksilver Glove, Alagorn's stories) and the Loader's and DSCLOG's, from a full code
  audit.
- **Docs:** the game's bugs, the manual's spells, the new items and weapon specialization moved out
  of FEATURES into pages of their own; ITEMS checked against the game's data; screenshots retaken.

**New**
- **Scar fights with a pair of obsidian cahulaks** in place of his obsidian long sword, in the arena and when breaking out with him (`worldgear`'s gift, object 87). The arena's
  people are made at its first visit, so a game already past the first bout keeps the old Scar
  (seen 2026-11-10: `pens-fire-count4`'s Scar still swung his long sword). He also wears a full leather suit with a helm (leggings and
  a helm added to his chest and arm armour: AC 3 with the Helms give AC 1 rule, 4 without, from 5), a
  step above Merzol (chest and arm) and below the champions after him; his henchmen, who wore
  nothing, get Merzol's leather chest and arm armour (AC 8, from 10), and each now swings a bone
  great axe (1d10, two-handed) in place of the mod's bone axe. (Scar's gear and the henchmen's
  armour seen in the game 2026-11-10, playtest/logs/2026-11-10-scar-bout-gear.md; the great axes
  not yet.) Their gladiator peers in
  Merzol's gang wear one brigandine arm piece and a shield.
- **New rule: held targets as in AD&D** (Options, Weapons and armour; on by default; `RULE_HELD`,
  the Loader's `held_hit`, DSCLOG's `RULE_HI_HELD` 8000h and HELD: `HELD_HIT` at 589E9h,
  `HELD_DAMAGE` at 58B0Dh): a blow on a Paralyzed or Out Cold creature hits automatically and does
  normal damage, as the 2nd edition PHB's Table 51 has it ("defender sleeping or held: automatic"),
  where the game rolls the d20 and doubles the damage. Both sides alike; AD&D's killing blow once
  no other fighting is going on is left out. The dice log:
  `    Paralyzed: hit automatically, for normal damage (AD&D's held target)` under the attack.
  With the rule off, the dice log now shows the game's own rule: the hit's line ends
  `x2 Paralyzed: a helpless target takes double` (the attack routine, 5883Ah, doubles the damage at
  58B0Dh when the target's effects have bit 34 or its creature +1Ch is 3; the save routine's same
  test, 79B0Ch, fails such a target with no roll), and a Poisoner's melee hit on a helpless target
  names its poison and puts the 10 down to it when it lands (`GameData.helpless`,
  `DiceLog._poison_taken`). DSCLOG writes the target's state into the ring entry as the dice are
  rolled (+188, `HELPLESS_OF`, which HELD's own test uses too; only in an attack roll's, a save's
  or an AC's entry), so a kill or a Hold ending before the line is written doesn't change it
  (`Entry.helpless`; an older helper's entries: the game's state). The panel's short levels take a
  hit line whose working opens with a bracket (a backstab's or this x2) as the attack's damage.
  How: [Held targets](obsidian-edition/DEVELOPMENT-RULES.md#held-targets). Seen in DOSBox
  (playtest/logs/2026-11-10-held-damage.md): with the rule, d20s of 8, 5 and 9 against "only a 20
  hits" all hit a held Templar for their damage; without it, the misses and the doubled backstab.
  `tests/test_held.py` runs both sites in Unicorn.
- **New rule: creature size as in AD&D** (Options, Weapons and armour; on by default; `RULE_SIZE`,
  DSCLOG's RULE_HI_SIZE and SIZE): a large target takes AD&D's large weapon dice by kind
  (`sizes.LARGE_DICE`, DSCLOG's `large_dice`, SIZE_DICE from CAH_SWING): a long sword 1d12, a short
  sword 1d8, a dagger and a club 1d3, a mace 1d6, a pick 1d4, a great axe 2d8, a polearm 2d6, a
  gythka 1d10 (the Dark Sun weapons guide's 2d4/1d10), a chatkcha 1d4+2 (AD&D's 1d6+2/1d4+2); the
  axe, quarterstaff and cahulaks as against a man-sized one; the Spiritual Hammer 1d4, Shillelagh
  1d6+1 against smaller ones (its 2D4 the large). FEATURES' table names the sources: the Player's
  Handbook (the pick as the horseman's pick), the *Complete Book of Dwarves* for the great axe (its
  two-handed battle axe, 1d10/2d8) and the Dark Sun weapons guide. Hold Person, Charm Person and
  Charm Person or Mammal (a person) are saved against at once by a large target (SIZE_SPARED from
  SAVE_SUM). Large is a half-giant, anyone Enlarged, or a creature large or bigger in sizes.py (the
  Loader's LARGE_BITS, in the tail, the header's +1842, written before the Loader's cosmetic steps
  so a failure in one can't leave it stale). An item box's damage line gives both
  (`1D8-1/1D12-1`; Shillelagh's `1D6+1/2D4`; DSCLOG's SIZE_PRE at 72A8Ah and SIZE_LINE at 72AA7h,
  round the game's damage line at 7286Fh); the inventory and View Character keep the game's lines.
  The dice log notes both ("1d12 for 1d8: a large target", "Guard is too big for Hold Person ->
  unaffected"). How: [Creature size](obsidian-edition/DEVELOPMENT-RULES.md#creature-size). Seen in
  DOSBox: playtest/logs/2026-11-10-creature-size.md.
- **Creature sizes** (`dsloader/sizes.py`, for rules to go by; the game keeps none): AD&D's T to G,
  people by race (half-giants L, halflings S, thri-kreen M, a guess at 7 feet), the rest by name from
  AD&D's and Dark Sun's monster books; judgement calls: the Drummer, the monster Slave, the Xorn,
  the Psurlon and the Psurlon Adept large, and the six of the great tusked figure (the game's race
  12, kind 31: the Magera, Blind One, Slave Leaders, Wagon Guard, Worker and the monster Guard; the
  human Guards stay man-sized); 25 the mod's guesses (UNSURE, marked "?").
- **The creatures' table** (obsidian-edition/CREATURES.md, made by `dsloader.doccreatures` from the
  game's data, tested against sizes.py): every creature the game defines (189, one a name and race,
  the default party left out), its figure as the game draws it standing (docs/creatures/, each its
  own picture; the fighting picture for the Bulette, the Fire Eel and the Silt Horror, which come up
  from the ground or the silt to fight: `doccreatures.BURROWERS`), its size, and whether the
  cahulaks can tangle it (`cahulaks.why_not`).
- **New rule: cahulaks as Dark Sun's rules have them** (Options, Weapons and armour; on by default;
  `RULE_CAHULAKS`, DSCLOG's RULE_HI_CAHULAKS and CAHULAKS): a head in each hand, the off head's one
  attack more a round under AD&D's two-weapon penalties whatever that rule (-2 the main head's
  swings, -4 the off head's, the round's last; DEX's reaction adjustment added, no better than 0);
  a hit that does damage tangles a man-sized or smaller target failing a save against
  petrification: it loses its next turn, as Whirlwind's sweep. Not tangled (CAH_HIT asks IS_LARGE,
  and the far block's bit for each combatant, the header's +1840, written before the Loader's
  cosmetic steps): half-giants, anyone Enlarged, whatever sizes.py makes large or bigger
  (`big_table`, by each creature's race and name), the bodiless (`cahulaks.SHAPELESS`: elementals,
  slimes, swarms, the Shadow and the greater shadows, the game's kind 13: the Shadow Guard, King,
  Prince and Worker, Cragg, Tanelyv, Tristram and Tynan), and, a judgement call, the spiders (Dark
  Spider, Spider Mage, the "-tunk!" princes), the Sand Howler, Screamer Beetle, Xorn, Strine,
  Daggoran, Magera and Alita (`cahulaks.UNTANGLED`). The cahulaks take both hands, a half-giant's too
  (DSCLOG's PROBE_TWO_HANDED, TH_CAHULAKS), so a Twin-blade or a Battle Dancer can't use them
  (KIT_FORBIDS, restrict.py). The figure holds a pair: a short haft and a hooked four-bladed head in
  each hand, both at the hips walking (spritegear's CAHULAKS shape). The dice log names each head's
  penalty and the tangle's save. How: [Cahulaks](obsidian-edition/DEVELOPMENT-RULES.md#cahulaks).
  Seen in DOSBox: playtest/logs/2026-11-09-cahulaks.md. Tests: `test_shadows_shapeless`,
  `test_shadow_kinds_in_data`.
- **More cahulaks in the world** (with the new magic weapons, `worldgear.cahulaks_chunks`):
  Legcrusher's two clubs a **Cahulaks +1** (a copy of the game's with its fire shimmer, its Cause
  Light Wounds taken off: a plain +1; `dataitems.with_items_removed`, new); the elven caravan's
  buried Cahulaks +1 made a **Cahulaks +2** (32,400), with an object and a picture of its own (object
  2672, picture 2673 and its item box copy: its blades in the water's blues); the arena's dead body
  by the stone arch plain bone cahulaks, in place of the game's plain gythka; and the champions' mul
  **metal cahulaks** for his two bone axes.
- **Metal and obsidian cahulaks:** two new item types, the game's Cahulaks in metal (146, DSCLOG's
  METAL_CAHULAKS; its icon 2670/2671 the bone one's heads in the metal polearm's colours) and in
  obsidian (147, OBSIDIAN_CAHULAKS), counted as cahulaks by every rule (the cahulaks' rule, the
  hands, the kits, restrict.py, the dice log, specialization, the figure). Earth clerics may use
  the metal ones, earth and fire clerics the obsidian ones; an earth or fire cleric-warrior who picks
  the cahulaks as its weapon spec starts with obsidian ones (`weaponchoice`).
- **Two magic cahulaks of the new materials**, each named and with its own glow, and a story Alagorn
  tells: **Emberlash**, obsidian cahulaks +1 (earth, fire and air clerics may wield it), carried by
  Uzoma, who leads the Drajian patrol west of the Hot Springs; **Ironwhirl**, metal cahulaks +2
  (earth and air clerics), on the Subterranean Temple's weapon rack. Their names take two more of
  DSCLOG's extra names (49 now). Plain obsidian cahulaks are sold by Jark (15), metal ones by the
  Weapon Merchant (200).
- **The Boots of Speed** (the DMG's), worn on the feet by anyone: in a fight the
  wearer's movement doubled and AC 2 better while it can move (not Stuck, Paralyzed or Slowed);
  nothing out of a fight. DSCLOG's type SPEED_BOOTS (the 31st extra type, the game's Boots'), name
  170h, BOOTS_MOVE (PROBE_MOVE) and BOOTS_AC (PROBE_AC); a red icon, and a glow on the figure.
  Dagger, chief of the White Sand Outlaws, wears them; Hototo, their other chief, carries the
  Gythka +3 (its 1000th-trip gift kept). Seen in DOSBox: movement 240 for 120, foes' shots at AC 0
  for her 2 (playtest/logs/2026-11-09-boots-of-speed.md).
- **The game's Polearm +1 in play:** the game defines it (object 1577, a stand-alone object in
  RGNFF.GFF) but no script creates or gives it and nothing holds one. Seref, the Draj agent at the
  Elven Caravan, where the cluebook puts it, carries it, with the new items on (`worldgear.MAGIC`):
  his object (203), which his encounter on the road copies too.
- **People the party fights who had nothing to fight with** (they struck with their fists), with
  the new mundane items on (`worldgear.fighters`): Seref's Drajian Guards (213) and the slave
  village's (195) the armed Drajian Guard's kit; the Lower Castle's unarmed Guard (281) the other
  Guards'; Arant's lazy guard (267) his guards'; the White Sand Outlaws (Slave Hunters 199 and 201,
  Hototo and Dagger, script 133: "swords readied") a bone long sword and leather, the chiefs leather
  arm armour too; the final battle's Psionicist (257) a stone dagger; the arena's Tohr-kreen (292),
  whose picture holds a gythka in every frame, a bone gythka. (Thri-kreen fight with their claws, as
  their pictures show; Jake and Mow are Dagolar's guises; Egrus is dead.)
- **Spells and psionics as the manual describes them** (a new rule change, on by default, from the
  next start: `spells_manual`, `gamepatch.SPELLS_MANUAL`; the spell records and DSCLOG sites; from
  reports/spells-against-the-manual.md, which now says what was done with each of its points). Tests:
  `test_manual_spells`. Seen in DOSBox: playtest/logs/2026-11-08-manual-spells.md,
  2026-11-08-hd-spells.md, 2026-11-09-group-3.md, 2026-11-09-group-4.md,
  2026-11-09-turn-undead-meteors.md.
  - *The records:* Bestow Curse and Blood Flow allow a save; a save negates Flaming Sphere; Solid
    Fog 1d3 rounds + 1 a level (was until removed); Minor Spell Turning 3 rounds a level (was one
    spell, never ending), turning every 1st- to 3rd-level spell for its whole time; Cause Fear 1d4
    rounds (was 1 a level); Quicksand no save; Turn Pebble to Boulder 3d6+8 (was 6d6); Ironskin a
    blow a caster level (was 1d6). Left as they were, after a DOSBox run: Magical Stone (the game
    already throws three stones of 1d4) and Quicksand's time (its Stuck is put on again while the
    quicksand's own 5d3 rounds last).
  - **Stinking Cloud** 1d4+1 rounds (was 1d6; DSCLOG's STINK_SITE adds the round); **Chaos** lets a
    creature of INT 21+ or 4 or less save as well as warriors (CHAOS_SITE, 79F80h); **Free Action**
    also frees the Stuck (Web, Solid Fog, Quicksand, Entangle, Grease): its handler, shared with
    Remove Paralysis and Protection from Paralysis, made a loop over the effects to remove (a
    Poisoned creature still stays Paralyzed, as the game has it). FEATURES lists what is left as it
    is and why (Protection from Normal Missiles, Deflection and Inertial Barrier: one effect;
    Confusion's and Chaos's one save; Mirror Image's images until struck).
  - **Hold Undead** holds only undead of the caster's level or lower (HOLD_HD_SITE, 7A345h);
    **Color Spray** gives no save to creatures of the caster's level or lower (SPRAY_SITE, 79F83h);
    for saving throws a monster with no class counts its hit dice as its level (HD_SAVE_SITE,
    79D8Ch: the game gave it 0, so a 14-HD Rampager was Scared like a 1st-level one, and Dismissal
    was easy on elementals and slaadi).
  - **Minute Meteors:** five globes of 1d4, each rolling to hit at +2 with spells that roll to hit
    (the record's repeat count 5; was one roll of 1d4 a caster level). **Flame Arrow:** a bolt for
    every 5 caster levels, 5d6 each (FLAME_SITE; was one sum of 5d6, 10d6 at 10th), no attack roll.
    Only the party's casts repeat: a monster's Magical Stone, Minute Meteors or Flame Arrow lands
    once.
  - **Turn Undead the AD&D way** (TURN_SITE, 7AE01h): AD&D 2e's turning table by the undead's hit
    dice and the priest's level, where the game's formula put 2- and 3-HD undead a row easier and
    5 HD a row harder; a turn makes the undead flee, Afraid for 3d4 rounds (the game had no fleeing:
    every success destroyed); D destroys, D* destroys and up to 2d4 more of its kind reached by the
    same turning; "---" no chance. A priest who fails against an undead can't try it again that
    fight. The dice log says which (`turned: flees 3d4 = 9 rounds`, `destroyed automatically (D*)`,
    `can't try again`). The record carries the priest's and the undead's creatures, so a turning out
    of a fight names them.
  - Fire Shield +2 on saves vs fire and cold; Blur +1 on saves; Chill Touch's Weakened lasts an hour
    (its record gave 0 rounds), and undead touched take no damage and flee 1d4 rounds; Cloudkill
    kills under 4 HD with no save and those of 4-5 HD that fail, 6+ HD take its damage; Feeblemind
    stops psionics and Heal cures it; Lower Resistance takes 30% + 1% a caster level off magic
    resistance (was halving it); Strength's die by class (warriors 1d8, priests, rogues and
    psionicists 1d6, wizards 1d4) and the mod's Cat's Grace's (rogues 1d8, wizards, warriors and
    psionicists 1d6, priests 1d4), the best die for a multiclass character, at most 24, neither
    stacking with Adrenalin Control; Rainbow Pattern a round a caster level, ended by damage on the
    creature it holds; Cell Adjustment heals 1d4; Biofeedback's -2 leaves a blow at least 1.
  - **Monsters as the manual describes them:** Shadows and Greater Shadows drain 1 STR a hit (no
    save, for 2d4 turns, stacking) in place of their cold damage and paralysis, and both are
    unaffected by cold; the Babau's and Blue Slaad's deadly poison (save or die) in place of the
    corroding touch and disease; the Tari a 3-HD bite of 1d3 with a 1-in-20 chance of disease; the
    Styr a 3d6 fire breath, +1 weapons to hurt it, HD 14 and THAC0 7; the Djinn turns invisible and
    makes mirror images at its first turn.
- **Spells roll to hit** (a new rule change, on by default, from the next start: `spell_to_hit`,
  `gamepatch.SPELL_TO_HIT`): the missile spells (Acid Arrow, Turn Pebble to Boulder, Magical Stone,
  Condense, each of Minute Meteors' globes at +2; the Strine's spines) roll a d20 against the
  target's AC with the caster's THAC0 (Acid Arrow a fighter's of the caster's level) and DEX, and the
  hostile touch spells (Chill Touch, Shocking Grasp, Vampiric Touch, Cause Light, Serious and
  Critical Wounds, Cause Disease, Poison) with STR, at a creature of another side; 20 always hits, 1
  always misses. A miss does nothing: "Miss" floats over the target and the dice log says
  `-> MISS: the spell does nothing, the 2 damage rolled lost`. Each of Magical Stone's three throws
  rolls on its own. Spells carried by a weapon's hit (spell arrows) don't roll again; Magic Missile
  and the areas are untouched. The panel at Short: `Cermak's Minute Meteors hits Kalzith for 2 (8 vs
  7+)` / `... misses Kalzith (4 vs 7+)`, in the hits' and misses' colours; in the readable layout an
  event row, as a weapon's attack is. DSCLOG's SPELL_HIT_SITE (7A15Ah, armed by CAST_SITE) and
  SPELL_STUB_SITE (78BA3h). Seen in DOSBox (playtest/logs/2026-11-08-spell-to-hit.md). Tests:
  `test_spell_to_hit`.
- **Resting heals by spells and natural healing** (a new rule change, `rest_heal`, on by default):
  before the rest each priest spends the slots left on Neutralize Poison for the Poisoned, Cure
  Blindness, Cure Disease (when no cleric or druid of 5th+ casts it free), and the Cure Wounds
  spells or Heal on the most wounded, and psionicists use Cell Adjustment, each through the game's
  own cast (`At rest: Cilla casts Cure Critical Wounds on Gerakis (5th-level slots: 8 left)`); then
  each heals 3 HP and CON's hit-point bonus (`Gerakis rests 8 hours: +3, +6 (CON 22) = +9`) instead
  of all of them, CON 20+ regeneration coming on top. The HP given back are in the damage colour on
  the panel and in the Loader's log.
- **Dual-classing as the manual has it** (a new rule change, `dual_class`, on by default): at 3rd
  level of the old class, and every prime requisite checked (the old class's at 15+, the new one's
  at 17+; the game checked one, WIS for rangers, druids and psionicists). Seen in DOSBox:
  playtest/logs/2026-11-09-group-4.md.
- **A fight's summary as it ends** (mock-up G's): `Fight over: 2 rounds, 1 kill; the party dealt 28
  damage and took 6`, then each member's attacks hit, damage dealt, kills and damage taken, written
  once the game's fight flag has been down 2 seconds (each arena wave gets its own). A kill goes to
  whoever hurt the creature last. A spell's damage counts for the party only when a saving throw
  against it or its attack roll names a party member as its caster. The readable layout shows it as
  the fight's close. (`fighttally.py`; tests: `test_fighttally`, `test_ledger`.)
- **The dice log window has a readable layout** (mock-up G of the combat log research, on by
  default, **Readable layout** to switch back; `dsloader/ledger.py`). Each event is a line with its
  outcome first (`● Seneca hits Arena Guard for 11 — backstab, Bone Hayneedle +1`), the HP it left
  and the roll in columns at the right, and the working under it, smaller and dim: the to-hit sum
  with the AC it would have hit, the damage dice, the save's line in full, each initiative score.
  Pips for whose line it is, a rule for each round, `▸` for each turn; the outcome coloured by the
  party's view of it (sky blue good, coral bad, dim for misses and monsters' saves, gold for kills;
  each at 4.5:1 or more on the log). A hit's damage and the HP left are filled into its line as
  their own lines arrive. The log's own lines are kept: Save..., the crash and freeze
  reports and the layout switched off use them. (Tests: `test_ledger`.)
- **Help in the Loader's window:** a **Help** button at the top opens the player's guide
  (`player-guide.html`, beside the Loader) in the browser (`viewer.open_guide`), and the status line
  names the guide's place whenever Help is clicked (an opener can report success and find no
  browser, as `gio` did). Tested in `test_viewer_options`.

**Changed**
- **Air clerics may use the cahulaks** with the class restrictions: Dark Sun's
  cahulaks can be thrown, as AD&D's daggers can, and the air sphere's weapons are missile and thrown
  ones and daggers (the game throws neither). The game's own class list already had the air
  cleric's bit; the restriction took it away. An air Seeker goes by its sphere too.
  (`restrict.AIR_KINDS`, DSCLOG's SPHERE_ALLOWS; `test_restrict`.)
- **A Brute may dual-class to air cleric** (was barred, with no two-handed melee weapon the class
  could use): the cahulaks are its two-handed weapon now. A Brute still can't dual to psionicist.
  (`kits.py`.)
- **Every thri-kreen throws a chatkcha twice a round** (AD&D's 2/1): DSCLOG's
  OWN_THROWS and PROBE_MISSILE_LINE go by the sheet's race (8), foes too, whatever the rules
  (`GameData.weapon_hits` the same); was K'ratchek's alone, her own feature with the kits on. Her
  Effects line `CHATKCHA 2/ROUND` and the Characters tab's "One more chatkcha throw" are gone; the
  Attacks line shows the rate for any thri-kreen.
- **The metal pick's and Deepbiter's icons** are drawn from the Hot Springs' stone pick (object
  1381: a whole head, slate grey, gold fittings), not the pick's own object (1210), whose near-black
  head is in two pieces: the metal one in the metal long sword's greys, Deepbiter's head in the
  game's fire (`icons.PICK_PICTURE_FROM`); both in the item box's list of tall pictures (the Loader's
  and the helper's). The item pictures in `docs/items` drawn again.
- **Spell descriptions that said something else:** with the manual's spells, Strength, Ironskin,
  Free Action, Solid Fog, Minor Spell Turning, Bestow Curse, Blood Flow, Chaos, Flame Arrow and Cell
  Adjustment describe what they now do (`spelltexts.MANUAL_TEXTS`); with Creature size, Hold Person
  (both), Charm Person and Charm Person or Mammal say they don't take on a large target
  (`SIZE_TEXTS`). Each fits the game's box (a seven-line box of 128 pixels), and the four spell
  arrows' texts end "casts it on a hit" (Vampiric Arrows' had run past the edge):
  `test_spelltexts_fit` wraps every text the Loader writes in the game's font.
- **The Options tab's texts:** each switch named as FEATURES.md names it, in FEATURES' order within
  each group; the manual's spells' text 1,267 characters to 349. The Graphics and Controls boxes
  open with their FEATURES names too (See-through figures, Choosing an enemy, Scrolling the map,
  The view in fights, The pointer in scenes, Where the pointer starts, Spells on the Effects
  screen).
- **The mod's magic gear with no plus or power glows on the figures:** the Cloak and Boots of
  Elvenkind, the Girdles of Back Defense and of Urnst (and the Amulet of Magic Resistance, should a
  figure ever show the neck), by type (`sprites.MAGIC_TYPES`): the glow had gone by a plus or a
  power only.
- **The move-silently labels say "Silent"**: the inventory screen's thief row reads `SLNT` (it read
  `MOVE`, beside View Character's MOVE, the character's movement), and the item boxes' stealth lines
  `Silent +10` (boots) and `Silent 95%` (the Boots of Elvenkind) for `Move +10` and `Move 95%`. DSCLOG's L_MOVE, IB_QUIET and IB_ELF_QUIET. Seen in DOSBox:
  playtest/logs/2026-11-09-silent-labels.md.
- **Item boxes show a weaker material's to-hit** under a plain weapon's damage: `Hit -3` wood,
  `Hit -1` bone, `Hit -2` stone and obsidian, as the game's attack takes it. Not with a plus, nor
  for the game's exempt weapons (clubs, staves, the chatkcha: type +08h 80h), nor metal (DSCLOG's
  IB_MATERIAL, always on). And the box alone draws a weapon picture taller than 16 pixels (the
  polearms', staves', gythkas', a stone pick's, the cahulaks', the striker's, up to 36) as a copy 16
  high, so the last row no longer sits at the box's edge (`icons.BOX_TALL`, `BOX_SMALL`; DSCLOG's
  BOX_PICS, always on); the inventory and the ground keep the game's own picture (the Polearm's too,
  which the Loader had drawn 22 everywhere). Seen in DOSBox: playtest/logs/2026-11-09-hit-line.md.
- **Turn Undead in the dice log:** `Seneca turns Guard: d20 = 11, needs 7+ (priest level 3 vs 2 HD)
  -> destroyed` / `-> not turned`, and `Zombie is destroyed by Turn Undead` in place of its HP line;
  the floating name over the cleric says "Turn Undead" (was "special attack 190"); the panel colours
  a turning as a hit or a miss. The game's own Turn Undead (spell 190, no slot) tries each undead in
  its area with a d20 against 10 + 3 x (its row - the level's), and a success destroys it, with no
  limit of uses (HOW-THE-GAME-WORKS's new Turn Undead section; playtest/logs/2026-11-08-turn-undead.md).
- **The combat log panel's lines are in a smaller font,** 7 pixels a line where the game's is 9: 8
  lines docked (was 6), 14 expanded (was 11). The glyphs are the X11 misc-fixed 4x6 font's (public
  domain) with the game's drop shadow (`smallfont.py`); the header, buttons and filters keep the
  game's font. `docs/combat-log.png`, `combat-log-expanded.png` and `combat-log-live.gif` retaken.
- **The panel's Short level reads as the readable layout does:** what happened first, the roll in
  brackets after it, the damage on the attack's line (`Seneca hits Slig for 11 (15 vs 4+, backstab)`,
  `Guard misses Lex (6 vs 13+)`, `Slig fails vs Fireball (11 vs 16+)`, `Rampager fails to resist
  Fireball (MR 25%: 28)`, `Cilla hides in shadows: seen (85 vs 25 or less)`); was `Rampager attacks
  Defiler: 20 vs 16+ HIT, 4 damage (2d6)`. (`combatlog.shorten`, `Log.at`.)
- **Steady pace keeps the game's real schedule,** and the choppy walking is gone. The game moves
  everything on the map a step at each tick of its clock (96 a second: DS:1F7Eh), so a tick that
  passes while a picture is drawn is a step lost. Steady pace assumed 70 pictures a second, while
  the map draws only when something moved (about 17), so it left most of them out: 6 shown a second
  at 20,000 cycles. Now it counts the steps lost against an allowance of 1.5 ticks a picture, about
  what the unmodded game's own pictures lose, and leaves a picture out only while more are lost.
  (DSCLOG's STEADY PACE; tests: `SteadyPaceTests`. `playtest/framerate.py` reports the steps run and
  lost and the walking speed.)
- **The helper draws shadows, dust and see-through figures for less.** Shadows are worked out only
  for figures whose shadow can reach the part of the view being drawn; the shadow cache remembers
  each figure's slot; spans and see-through pixels are looked up with XLAT; the lean comes from a
  table; the dust's thickness table is built once; the combat log panel is put back only when the
  redrawn rectangle overlaps it; dust settling after a walk redraws only its rectangle; the floating
  names' timer code returns at once with none shown. A floor pass takes 32% fewer instructions with
  everything on, see-through figures 12% fewer, every screen byte-identical
  (`tests/test_dsclog_drawing.py`). In DOSBox, the whole party walking in the slave pens, everything
  on: 20,000 cycles with steady pace, 15.5 pictures a second and 112 map units a second (was 10.2);
  35,000 cycles, 18.9 pictures and 141 (was 16.0 and 113)
  (playtest/logs/2026-11-08-drawing-savings.md).
- **Fastest (35,000 cycles) is the default game speed** (was Faster, 20,000). With the cheaper
  drawing it shows about all the pictures the game draws while the whole party walks and walks
  fastest, for about 30% of a core in DOSBox. A speed already chosen is kept; Faster stays for older
  computers.

**Changed: DSCLOG's room**
- **The helper's room** ([DEVELOPMENT.md's limits](obsidian-edition/DEVELOPMENT-INTERNALS.md#the-limits)): the
  cheaper drawing made the helper 944 bytes bigger and its far block 2 KB, and the new rules and
  items took more. Three memory passes made room:
  - The first freed 3,136 bytes of the segment and 190 paragraphs of upper memory: the colour, ring
    and dust-walked tables moved to the far block (FAR_DAC, FAR_RING_TAB, FAR_RED, FAR_WALKED: the
    header fields now offsets there, the Loader reading them at far_seg); the AD&D XP table stored in
    fiftieths; the 134 vector installs a table and a loop; the extra names packed
    (playtest/logs/2026-11-08-memory-pass.md).
  - The second freed 4,000: the sites' dispatch a jump table (688 bytes); the rings' outlines kept as
    one quarter and mirrored (336); a new tail section after the image, kept with the helper and
    found through header +1834 (`tail_seg`), holding the floating names' slots, the extra item names
    and types and the timer notes (the Loader's labels.py and freeze.py read them there); the dust's
    LIGHT, puffs and DARK in the far block; the crash report writing the stack straight from SS
    (playtest/logs/2026-11-09-memory-pass-2.md).
  - The third freed about 2,400 more: the AD&D XP, slot, thief and DEX tables and the kits' names
    moved to the tail; SEG_MOVE's two game tables moved to the tail; the helper's zero buffers laid
    over the install code.
  - Each pass checked in DOSBox (shadows, dust, see-through, the ring, the panel's colours, labels,
    to-hit, Turn Undead, item names and types, next-level XP, the Effects screen, Look, creation, a
    shop). Now: `kept_end` 62,480, 3,056 of the segment spare; `UMB_KEPT` 7,968 paragraphs, 214
    spare.
- The helper counts the game's page flips (`flip_count`, header +1832), for a frame rate:
  `playtest/framerate.py` reads it beside steady pace's frames left undrawn.

**Fixed: the game**
- **Graphics disappeared in a busy area** (SSI's technical note 2712 for Wake of the Ravager, the
  same engine): the game's picture cache (DSUN.EXE 25FA6h) has 300 slots for every wall, door,
  figure and item picture drawn and gives none back until an area loads, so past 300 a new picture
  had no slot and wasn't drawn. DSCLOG's PIC_REUSE (sites 26009h, 260CCh, 2612Bh; always on): with
  all taken, a slot out of memory that no wall (DS:574Eh) and no map thing (+0Fh) names is reused,
  the Loader's STALE ones first, searching round from after the last reused; its picture goes in the
  first gap of the store it fits, else past the furthest end. A slot reused for a picture whose read
  then fails is let go again (PIC_FAIL, at the loader's way out, 25FD0h; `gamepatch`'s `pic_fail`),
  not left with the new number and the old place. Seen in DOSBox: 145 items of different kinds
  dropped in the pens, 300 slots at the 9th dozen, then 18 reused, every thing with its own picture
  (playtest/logs/2026-11-09-picture-slot-reuse.md). Test:
  `test_failed_read_lets_the_reused_slot_go`. Dark Sun Recompiled needs `tools/build_mod.sh` again
  for the new sites.
- **Alagorn told two items wrong** (script 212 and the Loader's copies of it): the Quicksilver Glove
  as "Quicksilver Gauntlets" that graft a weapon to the hand (it casts Detonate on every hit), the
  Helm of Contemplation as a shield against psionic attacks (it is Gaze Reflection). His menus name
  the glove as the game does, and the two stories say what they do (`alagorn.retold`, always).
- **The Quicksilver Glove fought as a wooden weapon** (-3 to hit, -2 damage): its type has no
  material (40h, a ring's), and the game's to-hit and damage (DSUN.EXE 5EB49h, 5EBC1h) read only the
  low nibble, 0, wood. Its type made leather, as the Chameleon Gloves' (DSCLOG's
  PROBE_TYPES_FILL): "Leather Quicksilver Glove", 1D6+2.
- **Scare allowed no saving throw at all,** so the 2.14.0 fix (`scare_elves`: an elf or half-elf
  priest's save) never ran, nor the game's own rule that 6th level and up always save: its record's
  save byte (+1Fh) had "a save allowed" clear. The bit set (`scare_save`, 4222Fh A0h -> A1h): 6th
  level and up save, below 6th no one can, but an elf or half-elf priest
  (playtest/logs/2026-11-08-scare-no-save.md).
- **"Can't save" saved:** the game compared a save's total with the number needed unsigned, so
  every -100 (Chaos, Cloudkill, Scare under 6th level, Color Spray with the manual's spells) wrapped
  round and the creature saved (seen in DOSBox: Arena Guards "unable to save" took half Cloudkill's
  damage). The compare made signed (`save_signed`, 79BBDh `jae` -> `jge`), always on: -100 fails,
  even on a natural 20 (`save_natural`; DSCLOG's SAVE_SUM makes a natural 20 a save unless the total
  is the -100's, and keeps the sum in its byte, so a doubled 19 or 20 with Scare's +100 no longer
  wraps round to a failure). The dice log's line for it is `none allowed (cannot save) -> failed`.
- **Resting while poisoned killed a member just cured:** the rest read each member's effects
  before casting its free cures and never again, so a 7th-level druid's Neutralize Poison was cast
  and the member died of the poison anyway (playtest/logs/2026-11-09-rest-poison.md). The cures now
  come before the read (`rest_cures_first`, `rest_cures_loop`: the game's own bytes reordered;
  always on).
- **Pehtucl's ambush brought every guard in the pens:** his script (GPL 145) made its five guards
  at the fountain, then sent the whole kind hunting: up to ten more Arena Guards and Guards from
  across the map (a player's save). Now each of the five is made alone and given the hunt, the
  no-orders handler and the sight trigger itself, Pehtucl his by kind. And the fountain's
  yell-masking zone (GPL 137 at FB5h) takes in the passage before it, where the party stands as he
  turns: a fight there set off the alarm. (`scriptfixes.py`; `test_scriptfixes`; seen in DOSBox with
  the player's save: playtest/logs/2026-11-08-fountain-needle.md.)
- **An arrow or sling stone was from behind by the target's facing, at any distance** (+2, the
  target's DEX and shield lost: a ranger's three arrows from across a room, a player's log), melee's
  rule. A missile is now from behind only as a hidden archer's shot (the stealth rule), and the dice
  log says "unseen" for it. (DSCLOG's `MISSILE_REAR`, first in `PROBE_STEALTH`. Tests:
  `test_missile_from_behind_only_unseen`, `test_unseen_shot`.)

**Fixed: the Loader and DSCLOG** (most found by the code audit, 2026-11-10, each with a test that
failed before)
- **Alagorn told of none of the 14 new weapons:** with every switch on, his weapons copy (222) was
  12,405 bytes, past the scripts' buffer (11,376), and was quietly left out. Their stories are now a
  script of their own (224, 4,047 bytes) the copy calls; 222 is 8,444. A menu left out for length is
  reported (`alagorn.LEFT_OUT`, cleared at each start so an earlier start's lines don't linger).
- **DSCLOG's KEEP never shrank its block** (the resize read the PSP after zeroing it): a
  16-paragraph hole in upper memory; now ES from SS. **PROBE_SCROLL ran each map pass with
  interrupts off** (redraws, the panel, the retrace wait): on when the caller had them on, off only
  round the pointer's read and TARGET_CLICK's calls.
- **A Spellarcher's spell arrows could be swapped out of the quiver:** QUIVER_KEPT (PROBE_CAN_USE)
  read the character's segment 2 bytes off (`CU_MEMBER_SEG` counted from 6EF38h; the INT's way back
  is 6EF36h), so putting other arrows in the quiver wasn't refused (`QuiverTests.test_quiver_kept`).
- **A thief's later attacks in a round could still backstab:** with **A backstab multiplies the
  weapon's dice only**, only the round's first attack is meant to be a backstab, but the count it
  read (`[BP-14h]`) leaves the off-hand swing out, so a thief with two weapons and a weapon spec's
  extra attack whose first swing missed had the off-hand one multiplied, and every swing after the
  first had the backstab's +2 to hit. A later attack in the same round is no backstab now, its +2
  taken back. (DSCLOG's `STAB_FIRST`, in `PROBE_STEALTH`; `test_backstab_first_attack_only`.)
- **VIEW CHARACTER showed a new character's gear from before the Loader's** (a Poisoner's bone long
  sword where it had a bow and daggers) until another member was chosen and this one again. At DONE
  the helper raises `gear_due`; the Loader's next pass (tens of milliseconds) gives the gear and says
  whose items it changed (`gear_given`); VIEW CHARACTER's probe waits for it (at most a second, and
  only with the Loader there) and has the game's own routine draw the screen again. (`GEAR_WAIT` in
  `PROBE_VIEW`; header +1830, +1831; `test_gear_due`. Seen in DOSBox.)
- **In the helper's drawing:** a walker raised a dust puff on nearly every pass, not one per 6
  pixels walked (AX overwritten before the add), so there is less dust now, as designed; walkers off
  the view raised dust and widened the redrawn area; the whole view could be drawn twice in one pass;
  a dark area retried its shadow tables on every pass (now every 9 BIOS ticks); rings alone widened
  the redrawn rectangles by the shadows' 72/44 (now 16/8).
- **Whirlwind's lost turn worked only for the first 64 creatures on the map:** its per-fight table
  had a bit for each of 64 combatants. It and the new ones (Turn Undead's once a creature, the
  Djinn's first-turn tricks) cover every one up to MAP_COUNT (520), in the far block (FAR_SWEPT,
  FAR_TU, FAR_DJ). (Tests at combatants 64, 300, 519 and 520;
  playtest/logs/2026-11-09-audit-fixes.md.)
- **The mod's two sounds were hard to hear** (hiding in a fight, a picked pocket): saved at 55% and
  70% of full scale, and at the lowest priority, so a hide during a fight sound was skipped. Now as
  loud as the game's typical clip (`sound-data/make.py`) and at priority 10, the game's fight
  sounds' highest (DSCLOG's `mod_desc`) (playtest/logs/2026-11-09-sounds-louder.md).
- **Figures vanished from the map after many gear changes in one area:** each new outfit took a new
  slot at the end of the game's picture store (a fixed 741,376 bytes), which the game gives back only
  when an area loads; after some 30 to 60 changes a picture went past the store's end and the party's
  and the monsters' figures weren't drawn. Now a figure dressed anew takes no new slot: the Loader
  puts its pictures into cells the store already has (one holding the very picture; the figure's
  own, out of memory; else the smallest unused cell with room), writing the store (the game's XMS
  block) while DOSBox is paused. A picture with no cell takes a new slot only while the store and the
  table keep room for it and for the game's own pictures (64 KB and 24 slots, measured from the
  slot furthest in the store); else the figure stays as it was until the next area. In DOSBox about
  290 outfit changes took 9 new slots (was one each), every figure drawn. (`sprites.Store`,
  `Dresser._in_store`, `sprites._room_for`; tests: `test_no_room_in_the_games_store` and 6 more;
  playtest/logs/2026-11-09-missing-figures.md, 2026-11-09-picture-store-fix.md.)
- **Reconnecting filled the picture store:** the first dressing after the Loader connected again
  reloaded up to 8 pictures into new slots with no room check. Now a copy that already holds the
  dressed pictures is left as it is, and a first dressing asks for room as any other change does
  (`Dresser._same_in_copy`).
- **settings.json:** read strictly where losing it matters (when the Loader attaches, and the
  pickpocket history before a pick is saved): a file held for a moment by another program is waited
  for, never taken for the defaults, so the pockets tried and the rule switches can't be lost; a
  temporary file of its own per write; a file that can't be read is never saved over with the
  defaults (`SettingsUnreadable`; the Options tab saves only what changed); values of the wrong type
  are dropped as read.
- **Two Loaders on one game:** `game.lock` (an OS lock, by pid where none can be had) is taken by
  `launch`, the window and `dicelog`; a second refuses, naming who has the game. The lock follows the
  game: while a game a Loader started still runs, even with that Loader's window closed, no Loader
  starts it again from that folder and rebuilds the files under it (`running_game`;
  `test_gamelock`).
- **A copy that couldn't be made was silent:** the game then ran on its own objects, scripts or
  texts, which a save made with the mod's may not load. `prepare_patched_game` keeps what it left
  out (`LEFT_OUT`, `left_out_line`), and the window (a warning and a log line), `play` and `launch`
  say it; an objects copy that can't hold Kalzith is kept, and Kalzith reported left out. The copies
  are written whole or not at all, with no stray `.tmp` (`gff.write_atomic`).
- **A `dsun.exe` beside the mod was run in place of DOSBox:** Dark Sun Recompiled is found only in
  the mod's folder or its own, or by `--recompiled`.
- **The window attached by process name:** now the DOSBox it started (its pid) first.
- **The dice log stopped for good on a bad ring read:** reported once, attached again if it lasts.
  An entry being written (seq FFFFh) or read while DOSBox wrote over it (a torn entry) is skipped
  and counted as missed, never taken for a real one.
- **A hit landing mid-pass was later called "takes none of the damage":** the HP were read after
  the ring, so a fall could be seen before its roll; each pass now reads the records first
  (`_records_now`).
- **Pehtucl's chest could be shut for good:** `pehtuclchest.watch` made it the shut type whenever
  the party was in the pens, though only the mod's script ever opens it. Now it is shut only while
  the game's scripts have its USE command (`has_use`); without it, it is the game's plain chest.
- **Pehtucl's chest opened anyway in a game from before 2.14.0** ("You must be next to the chest
  ...", then its window): such a game's plain chest gets the USE command all the same, and the game
  opens a plain chest as a USE script ends. The Loader now shuts a chest that isn't unlocked: locked
  and trapped as in a new game (`test_an_older_games_chest_shut`; seen in DOSBox with a player's
  save).
- **A needle avoided said nothing:** with Pehtucl's chest's needle sprung and the party's best at
  traps rolling clear of it, the game showed nothing, and it read as no trap. The Loader sees that
  roll and sets the needle's flag (DISARMED); the script then says "The needle is seen in time, and
  it hurts no one." (`DiceLog._needle_check`; `test_needle_avoided`; seen in DOSBox.)
- **Put a save in a slot replaced the slot's save with no copy kept:** the save it replaces is now
  kept as `Replaced - Page P slot NN - NAME.SAV` in Named saves (which sync never removes), and the
  slot is written through a temporary file.
- **An item report said a new character's bone long sword "vanished"** when the Loader had made it
  the bow its weapon spec asks for, in the same record. An item made into another where it was is no
  loss (`itemwatch.changed_in_place`; `test_changed_in_place`).
- **A Poisoner's poison was put down to another spell** ("Merzol takes 10 from Shocking Grasp"): the
  list of recent damage rolls kept an earlier fight's. A new fight forgets them, and a poison's
  fixed damage (10 or 30) is its own when its save is the latest (`DiceLog._damage_source`;
  `test_poison_damage_named`).
- The dice log's notes called the "special effect: d10" roll a thri-kreen's bite: it is the
  disease roll, the game's Blue Slaad's (with the manual's monsters, the Tari's, 1 in 20); a
  thri-kreen's bite from 5th level paralyses with no d10.
- **A game or mod folder whose path has letters outside Windows' code page** gave DOSBox a broken
  configuration; the Loader now stops at start-up with a clear message saying what to move
  (`launch.conf_encoding`; README's troubleshooting).
- A game restarted in the same DOSBox gets fresh dressing and its own item gate; a creature
  destroyed outright whose fall wasn't seen is forgotten (no later "destroyed by Turn Undead"). The
  girdles, the amulet and the Boots of Speed take their header numbers from the game's Belt,
  Necklace and Boots (`BASE_TYPES`). The .bat files work from a network share (`pushd`); the layout
  is saved whole; the GFF reader refuses impossible run counts. The window's dialogs open over it
  (parented to it). The freeze report's dump of the helper's header runs to +373 (UMB_NEED; was to
  +361) (`freeze.HEADER_BYTES`). Writing the picture store no longer pauses DOSBox a second time
  while it is already paused.

**Docs**
- **Rules the game got wrong counted as fixes:** twenty-one PATCH-NOTES bullets move from `[Changed]`
  to `[Fixed]` (saves against spells, the doubled d20, the manual's spells, psionics and monsters,
  spells rolling to hit, Enlarge, rangers' casting level, preservers' INT, dual-classing, class
  restrictions, multiclass hit points, the class tables, CON 20 and up, two weapons, warriors' attacks,
  held targets, acid, thief skills and backstabs, the air cleric's daggers, Turn Undead): each a rule
  the game gets wrong against its manual, itself or the Player's Handbook. The mod's own choices
  (helms' AC, resting, the level cap, hit dice, creation scores, half-giants, creature size,
  cahulaks, ages, the bone scale set) stay changes. GAME-BUGS gets a table of them (the game's rule,
  the rulebook's, the switch) and two original-game bugs it lacked (Alagorn's clothes when none are
  carried; the Effects screen's "(15 CHARGES)" on an item's power); FEATURES' Rule changes says
  most are bugs, and Enlarge quotes the Player's Handbook (p. 173).
- **FEATURES.md split:** the game's bugs fixed are a page of their own, `GAME-BUGS.md`, grouped by
  kind (spells and psionics, fights, characters and items, screens and memory, people and quests),
  each topic in tables by kind of bug; the detail of the manual's spells (each spell, AD&D's turning
  table, the monsters, the known differences) is in HOW-THE-GAME-WORKS beside the game's own spells
  and Turn Undead; the new items' prices, the Warden's Plate, bracers of defense, robes, icons and
  names, Alagorn's stories and Pehtucl's chest are in ITEMS.md; weapon specialization is in KITS.md,
  now "Kits and weapon specs" (the attacks a round, the sixteen weapon specs, choosing at creation,
  the starting weapons, a level gained). FEATURES keeps each switch's summary and a link where each
  block was; every link follows, and `test_doclinks` checks the new pages' "How it works" links too.
- **ITEMS.md checked against the game's data** (every item record, item type, region placement and
  script that hands an item out, with the cluebook): the Helm of Contemplation's power is Gaze
  Reflection, and the Quicksilver Glove's Detonate; where the Draketooth, the Belt of Might and the
  Orb of Knowledge lie, the Mace +2, the Bow +2, the Serpent Boots and El's Drinker; the Sling +2's
  chest that isn't; Dag's Dagger's "extra damage" that isn't; the Terror Blade's acid chance; 15
  kinds of magic fruit and 19 spell scrolls; Grey's Scale's arm and leg icons swapped back; the
  Wand of Metal Detection, the plain stone pick, the gloves against acid and the missing finds
  added. Where each script-given item comes from (Dragonsbane, the Teaquetzl rewards, the warrens'
  sewer holes, the Terror Blade, Notaku's payments, Tanelyv's gifts, Laussa's ring and others);
  "—" now only where nothing gives the item (the Golden Torque). The champions' gear in the mundane
  tables; the polearms' doc icons at the game's own 36 pixels. The acid and corroding touch take
  only a held weapon of reach 1 (DSUN.EXE 5900Ah), so chatkchas, slings and bows are out of the acid
  table.
- **The player guide's XP left over at the top:** each class's highest level under the 749,999 cap
  and the XP left over, and for dual-classing humans the room a new class has by the level the old
  class changed at (DSUN.EXE 86D38h); FEATURES links to it.
- **The review's fixes across the pages:** the player's pages, the reference pages and the
  development notes put right where they had fallen behind (air clerics' and air Seekers' cahulaks,
  every thri-kreen's chatkcha, what can't be tangled, the gythka's large die, the Polearm +1 and the
  armed foes in PATCH-NOTES, and more). FEATURES' "Helms" is "Helms give AC 1", the switch's name;
  DEVELOPMENT-SCREENS gives M, U and I, the whole party in view and the view in fights headings of
  their own; DICE-LOG has a row for Spook's save part; PATCH-NOTES' Bug Fixes link GAME-BUGS.md.
- **Screenshots retaken:** `options.png`, `dicelog.png` and the load window (plain save names);
  `inventory.png` and `inventory-ranger.png` (SLNT), `hit-line-box.png` and `shadowseeker-box.png`
  (the large dice), `new-spells.png` (Cat's Grace's by-class text), `tome.png` (the box alone),
  `gear-boxes.png` and `elvenkind.png` (Silent); the small shots at 2x; the GIFs trimmed. `gear.png` is a picture of Gerakis in his gear (it
  was a before-and-after at an uneven 2.5x); `shadows.png` keeps the shadows.
- **PLAYTESTING.md reorganised**, with what each play taught (the item type record's fields, a
  person's new gear reaching only creatures made after it, picture slots while exploring, the
  walkthrough and `setup_guide.sh`, the outstanding checks).
- **CI and tests:** nasm installed on Windows, so DSCLOG.EXE, GAMEEND.COM, UMBPLUS.COM and the
  least_scores patch are checked against their source (failing, not skipping, without nasm); the
  Release workflow's manual run limited to main. New tests: DSCLOG's tables against the Loader's,
  every module's game flags (none shared), every module's objects and pictures (made once each),
  and `prepare_patched_game`'s copies. Two tests that polled against real time (the stats thread's
  and the see-through tables') join the worker thread now (`ghost.Ghosts` keeps it).

## Pull request #88 ([merged 2026-11-08](https://github.com/daaki85/darksun-obsidian-edition/pull/88))

*A note on the DSCLOG sizes in #83 to #88:* up to #84 the figure called its "image" may be the
file's, DSCLOG.EXE (#83's 63,680 and #84's 64,320 are the files' sizes; the image is the file less
its 32-byte header), and the spare room beside it, up to #85, is counted from that figure. #85
names the file's size as such; from #86 on, both are given. The "image" in
[DEVELOPMENT-INTERNALS](obsidian-edition/DEVELOPMENT-INTERNALS.md#room-and-memory) is the file
less its header: from the tail (2026-11-09, after #88) that is DSCLOG's 64 KB segment's part
(`image_len`) and the tail together, and the spare room is the segment's.

Obsidian Edition 2.14.1 ([release notes](release-notes/v2.14.1.md)).

DSCLOG.EXE 63,824 bytes (image 63,792), 1,744 of its segment spare.

**Fixed: the Loader's window**
- **The new spells' switch said "New wizard spells"** and then listed the ten 6th-level priest spells
  it also covers. It is "New spells" now, with the six wizard spells and the priest spells named
  apart; FEATURES and the player guide call it that. (`viewer.py`; the setting is still
  `new_spells`.)

**Fixed: the Loader**
- **A bow the Loader gave couldn't shoot** until it was taken off and put on again: a new character's
  whose weapon spec is the bow (whatever its class), a Myrmidon's second spec's, fuller starting
  gear's for a Battle Dancer or Spellarcher, and any Spellarcher's once it made spell arrows in an
  empty quiver. Each gives the bow to the held list and its arrows to the worn one, as the
  inventory screen keeps them (since #85, 2.13.4), and then `bow_ahead`, which put a bow ahead of
  its arrows when both were in one list, swapped the two records across the lists: the bow in the
  worn list, where the game doesn't look for a missile weapon. It swaps only within one list now,
  and a weapon found in any party member's worn list (or arrows in the held one) is moved back as
  the dice log runs, out of a fight: "Yilballa's Bow is now held, ready to use (it had been counted
  as worn)". (`weaponchoice.bow_ahead`, `pickpocket.mend_lists`. Tests: `test_lists_apart`,
  `test_mend_bow_and_arrows`, both failing on the code before the fix.)
- **Changing the leader just after a fight rolled a thief's hiding:** the dice log took a change
  of whose turn within a minute of game time of the last round for a turn of the same fight, and
  game time barely moves out of fights, so the new leader's "turn" printed ("Alura's turn") and,
  with the stealth rule, rolled hide in shadows and move silently. A turn now also needs the
  game's own test that a fight is on (`game.fight_on`, as its rest and USE screen read it).
  (`DiceLog.turn_lines`. Test: `test_no_turn_out_of_a_fight`, which the code before the fix fails.)

**Fixed: DSCLOG**
- **A melee weapon's item box read "0.5x1D8-1",** whoever held it. With no creature the game's damage
  line takes the rate from the item type's +0Bh, a missile weapon's, which a melee weapon's type has
  at 1 (half an attack); the game hid any rate of one attack or less, until #76's `dam_half` let
  "0.5x" through for Slow. With no creature the rate is now at least one a round, so the box shows
  none, as before #76; the inventory's and View Character's lines are as they were. (`PROBE_MISSILE_LINE`.
  Seen in DOSBox: Gerakis's Bone Long Sword's box "1D8-1", his sling's "1D4". Test:
  `test_item_box_rate`, which the helper before the fix fails.)

**Changed: DSCLOG's room**
- **1.7 KB of the helper's 64 KB segment freed** (96 bytes were left): three buffers that start as
  zeros, the new spells' room (`seg_space`, 512 bytes), their areas' pictures' table (`area_space`,
  896) and the shadows' colours (`dark`, 256), no longer take bytes in the image: they lie over the
  install code, which is done with by the time they're used, and `KEEP` zeroes them before its first
  DOS call. DSCLOG.EXE 63,824 bytes (was 65,472), 1,744 of the segment spare; what stays resident
  one paragraph more (`KEEP`'s zeroing), upper memory 7.5 KB spare. (`AFTER_INSTALL`. Test:
  `KeepTests`, `keep` run with the install code's bytes where the buffers go. Seen in DOSBox: the
  helper in upper memory at C90Ah, 63,952 bytes, the game 97 KB free with the map open, as before;
  the three buffers filled in play, the new spells' room made, and the party's shadows drawn.)

**Fixed: the game**
- **The game's Great Axe +3 had no material:** its type (2) carried the 40h of things with none,
  a ring's, so its name showed none, and under the class restrictions no sphere's cleric could
  wield it. DSCLOG makes it metal as the game loads its types, as its icon (the game's metal axe's
  grey and teal head) and its weight (70, the metal great axe's) have it. (`PROBE_TYPES_FILL`:
  5 bytes, which fit the image's last paragraph's padding. Seen in
  DOSBox: type 2's +8 read 04h, and the game's inventory named it "METAL GREAT AXE".)
- **The creation screen's least scores weren't the manual's:** the die raised the class's prime
  requisite to 17 and every other score to the class's one least (9 to 14), so a fighter's STR was
  never below 17 and a thief's CHA never below 9, while a druid's CHA 15, a ranger's STR 13 and
  DEX 13 and a psionicist's CON 11 went unasked. The least for each score is now the manual's (cleric
  WIS 9; druid WIS 12, CHA 15; fighter STR 9; gladiator STR 13, DEX 12, CON 15; preserver INT 9;
  psionicist CON 11, INT 12, WIS 15; ranger STR 13, DEX 13, CON 14, WIS 14; thief DEX 9), the
  highest of a multiclass character's classes, and the dice log says "raised to 9 (the Thief's
  minimum)". (`gamepatch` `least_scores`: 67399h's 104 bytes replaced by `dos/least_scores.asm`,
  the overlay manager's two segment fixups kept in place; `game.CREATION_MINIMUMS`. Tests:
  `test_least_scores`, run in the emulator. Seen in DOSBox: each class's least for each score,
  read after a lowering click, the manual's, and three multiclass sets the highest of theirs; a
  fighter's STR clicked down 17 to 9.)
- **No XP bonus for high prime requisites:** the manual gives a class whose prime requisites are all
  16 or more 10% more XP (Fighter and Gladiator STR; Ranger STR, DEX and WIS; Preserver INT; Cleric
  WIS; Druid WIS and CHA; Thief DEX; Psionicist CON and WIS); the game's award routine (6B817h)
  has none. The dice log's tracker now adds it to each gain it sees, whatever it came from: 10% for
  each such class, divided by the classes, since a sheet has one XP for all of them (the game adds
  one class's share); a human counts only the class it follows now (slot 0). The character's own
  scores count (the sheet's), not an item's or a spell's. It writes the sheet, remembers the XP
  with the bonus so it isn't seen as a gain again, and shows it: "XP: Dag +137 (+12 for Fighter,
  STR 17)". A level the bonus alone reaches comes with the next award. The game's area change,
  which takes the XP away and gives it back, brings none. The tracker also stands aside while the
  creation screen is up (`game.creating`: DS:119Ch's sheet with DS:11A0h's record straight after
  it): there the party's first slot carries the character being made on a stand-in sheet whose XP
  moves with the class chosen, which the log had shown as "XP: SeanBoy +1500". (`tracker.prime_bonus`.
  Tests: `test_prime_requisite_bonus`, `test_prime_bonus_classes`, `test_no_xp_on_the_creation_screen`.
  Seen in DOSBox: an award of 600 gave Gerakis +660 "(+60 for Gladiator, STR 24)", K'ratchek +213
  (his druid's CHA 15 short), Cermak +660 and Cilla +220, written once, in a game loaded after
  the creation screen too.)

## Pull request #87 ([merged 2026-11-07](https://github.com/daaki85/darksun-obsidian-edition/pull/87))

Obsidian Edition 2.14.0 ([release notes](release-notes/v2.14.0.md)), with #86.

DSCLOG.EXE 65,472 bytes, unchanged (comments only).

**Fixed: the Loader** (a fifth review)
- **Writes through a table pointer gone null mid-pass could land in DOS's own memory:** the item
  gate (since #86) covered only where the tables are and were, and the low-memory guard reaches
  600h, where a null table's writes run to 20D0h (items) and 7400h (creatures). A null table is
  covered from 0 now, and the gate refuses while one is gone. (`itemgate.py`. Test:
  `test_tables_moved_mid_pass`.)
- **The Loader could take the game's last free lists and item records** (the game's people
  dressed in every area): 20 of each are left to the game now. (`ring.RESERVE`. Test:
  `ReserveTests`.)
- Smaller: the Loader's own list writes made the pass's later item steps wait a pass (and counted
  as refusals in the freeze report); a two-hander went in the right hand beside a shield already
  held; a finished see-through palette's thread cleared another's mark; a flag past the 808 a
  save keeps is refused (`game.FLAG_COUNT`, `test_flagrange`). `test_scriptchecks`' file times are whole seconds: at 1-3 ns they were all 0 on Windows (100 ns steps), and the test failed there.

**Fixed: the Loader's window**
- **All fields** widens its columns to the longest label and value shown; the **Memory tools**
  byte view scrolls sideways in a narrow pane; the window keeps a smallest size (1080x640) at which
  every tab and row of buttons fits.
- The Characters card says `Features:` for the game's own party's features (`Features: Wild
  Fighting`), `Kit:` when there is a kit; K'ratchek's `Chatkcha 2 a round` reads `One more
  chatkcha throw`. All fields' `Attacks/round` is `Attacks/round (base)`, the game's number
  before specialization. (Test: `test_kit_label`.)
- Options: the floating names' switch names the charges used (`Armor: 7 left`) as well; the
  shadows' says `(soft, on the floor)`, not see-through, which is the hidden and invisible.
- **The divider stops short of the Memory tools' buttons:** widened to fit the party's columns,
  it could hide Stride's Apply and cut Reload layout. It now leaves room for the widest row of
  buttons, the columns widening as the table fills no longer move it, and the byte view asks for
  less width (it scrolls sideways). (`Viewer._fit_party`.)
- Labels reworded: the saves are copied into Named saves only while the window is open; the
  Options note names the .bat files; the Look switch says what it shows (hit points, AC, THAC0
  and defences); Restore defaults says when a switch marked "from the next start" applies.

**Docs**
- The changelog's #86 heading, its fourth-review fixes and the releases list put right; the patch
  notes, README, FEATURES and the player guide given what #86 left out (Kalzith's face, the
  pickpocket sounds, the Kreenfang in a 2.13.4 save); DICE-LOG's picked pockets and the game's own
  party's opening lines; the developer pages given the gate's cover, the reserve, the people's
  gear's tries and the edge cases of names and shadows; #86's "Room for new code" filed under
  Changed; the playtesting guide's repeated notes merged and its save list completed.
- A docs review: the player pages (the saves list in one place, the release notes in a player's
  words, the patch notes refiled); the feature pages (FEATURES' always-on features apart from its
  switches, item places moved to ITEMS, one summary of the rule changes, DICE-LOG's missing lines,
  HOW-THE-GAME-WORKS kept to the game); the developer pages (Building and testing split into
  Build, Tests and Release steps, with the game-file variables and the project-wide tests; Room in
  the helper with one table of sizes; the kits' effects table cut to effect, kit and probe, each
  mechanism below it; the shadows' cache placed in the far block; the developer detail taken off
  the player pages placed here; every Loader flag in `test_flagrange`); the playtesting guide's
  repeats merged; three Loader screenshots retaken.

## Pull request #86 ([merged 2026-11-07](https://github.com/daaki85/darksun-obsidian-edition/pull/86))

DSCLOG.EXE 65,472 bytes (+880 since #85; its image 65,440, 96 bytes of its segment spare).

**New**
- **Kalzith's own portrait:** a face painted for him in the game's portrait style (an old man,
  white of brow and beard, in his figure's green-teal hood), chosen from three, in
  place of the game's portrait 61. (`kalzithface.py`, portrait 101. Seen in DOSBox in his talk
  and shop; `docs/kalzith.png` retaken.)
- **See-through figures:** a thief or ranger hidden in a fight, and anyone invisible (a party
  member always, a foe while no party member detects invisibility), is drawn half see-through.
  DSCLOG draws such a figure itself, blending its pixels with what is under it through tables the
  Loader makes from the palette. (Options: "drawn see-through", on. `ghost.py`, DSCLOG's
  `PROBE_GHOST` on `INT 80h`; DEVELOPMENT-CONTENT § See-through figures. Seen in DOSBox with a
  real hide and a real Invisibility. Tests: `test_ghost.py`, `test_ghost_draw_many_runs`.)
- **Sounds for hiding and picking pockets:** a soft breath as a thief or ranger hides in a fight,
  and a purse's jingle for a picked pocket (the three weapons worth XP keep the quest's sound). A
  Spellarcher making spell arrows hears the spell's own cast sound. (`sounds.py`,
  `spellarrows.cast_sound`; DEVELOPMENT-CONTENT § Sounds for hiding and picking pockets. Seen in
  DOSBox, DOSBox's output matched with the clips. Tests: `test_sounds.py`, `test_pick_sound`,
  `test_spellarrows.py`.)
- **The champions' bout:** once a party member has killed Scar in the arena, the next visit's
  first wave is six champions from a distant arena, after a speech of the Announcer's, once: a
  Tohr-kreen with Kreenfang, a half-giant, a mul, a halfling, an elf and a defiler, each armed and
  armoured (a defiler with a scroll). The Tohr-kreen leaves a body of its own, with Kreenfang in
  it. (New items. `champions.py`, `bodyart.py`; flags 759 and 807; DEVELOPMENT-CONTENT § The
  champions' bout. Seen in DOSBox: the speech and the bout after Scar's death in a real game,
  every champion's weapons in use, the body's picture. Tests: `test_champions.py`.)
- **Pehtucl's chest, locked and trapped:** the slave pens' head templar's chest, beside him, holds
  the Cloak of Protection +1. A thief checks it for traps (find/remove traps: a poisoned needle
  drawn out, or sprung) and picks the lock (open locks), as often as wanted; anyone else may bash
  it (the game's safe's odds: 5%, +5% for each of STR 18, 20, 22 and 24), which springs the needle
  if it is still there. The needle is 2d6 poison; the party's best at find/remove traps may still
  avoid it, as with every trap in the game. Worked on only from beside it. A new game only.
  (New items. `pehtuclchest.py`, script 223, flags 795 and 796; DEVELOPMENT-CONTENT § Pehtucl's
  chest. Seen in DOSBox: every branch, the disarm on 2026-11-07. Tests: `test_pehtuclchest.py`.)

**Changed**
- **Thornwall comes onto the slave pens' weapon rack once Semyon has told of it,** in a new
  question ("Seen anything useful?": a crate the guards fussed over); then "We found what was in
  that crate" once a party member carries it. It had been on the rack from the start. (New items.
  `semyon.ship`, flags 756-758. Seen in DOSBox, and after a save and load. Tests:
  `test_semyon.ShipmentTests`.)
- **The Cloak of Protection +1 is in Pehtucl's chest,** not on him: worn, it gave him nothing, as
  a cloak counts for nothing with a shield under AD&D's rule. He keeps his ring. (`npcitems.py`. A
  new game only.)
- **The game's people wear the cloaks, belts, boots, amulets and up to two rings they carry,**
  which the game never put on; each counts by the same rules as the party's. (`people.py`, with
  the fix below.)
- **Cilla's own feature is the "Elven Shadow-walker"** (her hiding never halved in daylight), not
  the "Elven Wanderer", which read like the druid kit Wanderer; SHADOW-WALKER on the Effects
  screen. (`kits.OWN_FEATURES`, DSCLOG's `own_lines`.)
- **The freeze report samples every 32nd strike of the timer,** not every 16th (`freeze.py`).
- **Room for new code:** the end shared by seven handlers that return through the overlay
  manager's frame is written once (`OVR_BACK`), and a sheet's classes read by one routine
  (`SHEET_CLASSES`): 112 bytes freed, 128 spare from 16 (96 after the fix to see-through figures in
  the enemies' turns). The build also fails now if the music pool or the see-through tables
  wouldn't fit upper memory (`UMB_KEPT`; they were left out quietly).

**Fixed: the game**
- **The game's people put on their weapons and armour only at their first action in a fight.**
  Until then each was AC 10 with its armour unworn and its Look box listed no weapon, so a first
  round's blow on one who hadn't acted, a backstab, or an opening blow from outside a fight (which
  is struck before the fight starts) met no armour. The Loader now puts each person's gear on as
  it comes on the map, as the game would. (`people.py`; DEVELOPMENT-CONTENT § The game's people's
  gear. Seen in DOSBox: every person with gear in the pens wearing and holding it. Tests:
  `test_people.py`.)
- **Psionic Blast knocks out instead of killing** while a party member's imagined wounds are
  still to come back; one knocked out wakes with them at the fight's end. This replaces #85's
  "only to a member still Okay". Disintegrate still kills. (From yuan-ti's v0.1.55;
  `gamepatch.blast_knockout`; DEVELOPMENT-CONTENT § Worn items. Seen in DOSBox. Tests:
  `WornTests.test_blast_knocks_out`, `test_psiblast.py`.)
- **Scare's save:** below 6th level an elf or half-elf priest got no save (the game tested for
  both races at once). (From yuan-ti's v0.1.55; `gamepatch.scare_elves`. Tests: `ScareTests`.)

**Fixed: the scripts**
- **Eleven of the Loader's changed scripts no longer decoded** (3, 5, 46, 137, 139, 146, 174, 212,
  213, 220, 221): a jump over a longer command left the rest of it in place. The dice log's
  explanations of the scripts' rolls couldn't read them, and the champions' bout never came with
  Semyon on. Each jump now fills what it leaves with a one-byte command. (`gpl.put_jumps`. Test:
  `AllScriptsTests`.)
- **Kurzak spoke of Legcrusher as gone while he lived:** his lines asked whether Legcrusher was on
  the map, and he is made only as Kurzak calls. They ask the Loader's flag 797 now, set once the
  dice log sees him dead. (`kurzak.py`. Test: `WatchTests`.)
- **A save's talk and use commands could point at another script once a switch changed:** the
  Loader's script entries were numbered only for the parts switched on, so with Kalzith off his
  talk's entry was Semyon's. The three entries (Kalzith's, Semyon's, the chest's) and their scripts
  are always there now, in that order. A save made with an earlier version and Kalzith off has
  Semyon's talk run Kalzith's script (the patch notes' saved games say so). (`kalzith.ENTRY_SCRIPTS`.
  Test: `test_scriptnumbers`.)

**Fixed: DSCLOG**
- **It hooked its interrupts before setting up its buffers,** so with no memory for them it
  exited with its vectors pointing into freed memory. The buffers come first now.
- **The floating names and the shadows shared the VGA's kept registers,** so a timer strike in a
  shadow, panel or see-through pass could put the game's registers back wrong (a likely cause of
  rare drawing gone wrong). (`VGA_BUSY`. Test: `test_vga_busy`.)
- **A pocket picked or spell arrows made after DSCLOG had stopped waiting** still happened, unseen.
  Such a request is marked answered now. (`USE_REPLY`. Test: `test_unanswered_marked`.)
- **It waited for the Loader with interrupts off for a Spellarcher's arrows,** so with the Loader
  slow the game's clock and music stopped for up to two seconds. (Seen in DOSBox: loads and runs.)
- **Its message when its interrupts are taken** names them right (60h-65h and 80h-FFh).
- **A floating name could be drawn above the page,** into other video memory, when the view was
  dragged so that its figure was off the top of the screen; it isn't drawn then. And a timer strike
  while a name was being erased could leave its old place on screen (the erase marked busy first).

**Fixed: the Loader** (an audit and four reviews)
- **One write the Loader stopped ended the dice log for the session** (slicing a deque raised every
  pass). It is told once now, and kept for a crash report, which had always shown none. (Test:
  `test_refused_write_said_once`.)
- **One failing step of the dice log's pass stopped all those after it,** every pass. Each step
  is on its own now, and an error is said once, by where it was raised (not its text, which could
  carry an address and was said every pass), in the window and `play` mode too. (`DiceLog._step`,
  `dicelog.error_key`. Tests: `test_each_step_on_its_own`, `test_error_key_by_where`.)
- **An item moved could be lost:** with the game's things all in use it was taken out of its list
  and put in none. The new list is found first now. (`pickpocket.place`. Test:
  `test_no_list_to_be_had`.)
- **A sold magical item could be lost** while the game was busy with its item lists: the gate is
  asked first, and covers the pointer's thing. (`Buyback.keep`, `THINGS_PAST`.)
- **A weapon's 200 XP for a picked pocket could be had again** by selling it and lifting it back.
  Paid once a game now. (Test: `test_sword_xp_once`.)
- **A pocket picked or a speaker's name learned was lost** if settings.json was held at that
  moment (an antivirus, a backup). It is saved at the next pass. (`DiceLog.save_learned`.)
- **A save of the same party loaded wasn't seen as a load,** and the game's own party wasn't made
  ready in a second new game without closing the Loader. (Tests: `LoadSeenTests`,
  `test_default_party_again_in_a_new_game`.)
- **A dressed figure could be written past its room** in the objects' copy after "Elves have pointed
  ears" changed; each picture's room is read from the copy itself. (Test: `test_rooms`.)
- **The dice log named the wrong script checks** after a switch changed and the game started again;
  **the scenes' pointer file** could stop the game from starting; **the combat log level** chosen on
  the Options tab was undone while the panel showed; **the window forgot the panel's size**.
- **The Look box's AC left out Helms give AC 1** until someone wearing such a helm had been
  attacked. (Test: `test_helm_before_dsclog_sets_it`.)
- **A speaker's name was learned wrongly from a script's speech** (Kurzak's call taught "Trustee"):
  a speech with no replies teaches a name only when its speaker stands near the party. (Test:
  `SpeakerTests`.)
- **Writes across an area's loading:** the item gate now also covers where the item and creature
  tables were as the pass began. (`itemgate.py`. Test: `test_tables_moved_mid_pass`.)
- **A failed copy of the objects or resources file left the last start's** for the game to open,
  made with other switches. It is taken away now.
- **Script checks dropped a roll's line** when the scripts' copy was damaged, and found none with no
  copy (the game's own scripts are read then). (Test: `LoadTests`.)
- **Wake of the Ravager's and the whirlwind's pictures could pulse:** a green was matched to a
  colour the game cycles. (`wotrart.stable_colours`, `whirlart.CYCLED`.)
- **The window kept a second copy of the objects' file** (5.4 MB; now 0.46 MB, what differs).
- Smaller: settings.json tried again before it counts as empty; the arena ring's search kept if
  giving the ring fails; a speaker's name, a saved log and the Named saves folder say when a file
  fails; the Memory tools' "... more" row can't be assigned; the Look texts searched for in the
  dialogue are the last 16.
- Smaller: the panel shortened only plain saves; Kalzith's scrolls weren't trimmed when the lists
  were busy, and his stock waits while the flags have no place in memory (it read as not given);
  a monster's or attacker's THAC0 below 0 showed as 255; WIS's save adjustment read past its
  table; Restore Youth's system shock on a creature with no CON; a party member named Kalzith or
  Semyon counted as his death; Cilla's armour, when the game's lists moved under a piece, is taken
  on the next pass; a palette from an earlier start isn't kept when the game's can't be read;
  crash reports show the new spells' old setting name, the ring and the panel's level as used; a
  failure counting effects' charges no longer loses the pass's lines; a script repair too short for
  its jump is left out rather than shifting the script (none is, today).

**Fixed** (before release, in the new work above)
- See-through figures' first vector, 62h, was `PROBE_AC`'s, so every attack's AC went to the
  see-through probe (it is 80h, and `test_vectors_distinct` checks each vector is used once).
- A hidden thief stayed see-through through the enemies' turns after its own (about 1.4 s): the
  whole view is drawn once as one stops hiding. (`GHOST_UNION`. Test: `test_solid_at_turn_end`.)
- Champions made again from a save came on unequipped. (Test: `test_again_after_a_load`.)
- Pehtucl's chest had taken script 220, Alagorn's copy telling of clothes, so his menu called past
  the end of the chest's. The chest is 223, and `test_scriptnumbers` checks no two scripts share
  a number, every call lands inside its script, and every script fits the game's buffer.
- The chest could be worked on from across the room (the game's safe tests the distance first).
- **A figure stayed see-through (or solid) through the enemies' turns** when an invisibility ended
  or began then, until a party member's turn: the view is drawn again from the map's main loop,
  which doesn't run in those turns. The Loader now marks the table changed (`GH_CHANGED`, the last
  byte of GHOST_TAB's room), and `GHOST_UNION` draws the whole view once at the next step of
  anyone's. (Test: `test_whole_view_when_the_table_changes`. Seen in DOSBox: the
  byte cleared 0.06 s into an enemy's 0.36 s turn; playtest/logs/2026-11-07-review-fixes.md.)
- **The sound of the mod's own lent the game's table entry back one byte too far,** over the next
  entry's "loaded" flag (latent: nothing changes it during a play).
- **A see-through figure with no picture yet** was drawn from the interrupt table as if it were
  one; it is left undrawn, as the game's own routine does. (Test: `test_ghost_draw_no_picture`.)
- **See-through figures were drawn solid for a moment every 30 s** where the game cycles colours,
  and their tables were kept all session. They are kept by the colours the game never cycles, the
  last eight. (Seen in DOSBox: GHOST_ON 1 in all 3,722 samples. Test:
  `test_cycling_colours_keep_the_tables`.)
- **See-through tables were kept by too few colours** (224-239 differ between areas) and could
  leave the figures solid after a quick change of palette and back. (Tests:
  `test_area_colours_count`, `test_back_before_made`.)
- **A two-handed weapon was given a shield or a second weapon** among the game's people, and a
  shield went beside one already held at a later visit. (Tests: `test_two_handed_alone`,
  `test_two_handed_already_held`, `test_two_hander_never_second`.)
- Smaller: the chest's watcher no longer scans the item table each pass; Semyon's crate counts a
  Thornwall in a bag.
- The item gate's rule for a null table (in this work) refused every write while the game rebuilt
  its tables, DSCLOG's replies and the see-through tables too, and a refused write could leave
  the tables never made; `ghost.py` marks them only after its write. Floating names near the top
  were hidden under row 40, not only above the page (row 0). A part-dressed person was tried every
  pass for good, each pausing DOSBox (`people.TRIES`: three). The refused writes' "... and N
  more" counts past 200; `GHOST_UNION` reads and clears `GH_CHANGED` in one `xchg`.

**Docs**
- The new work in the patch notes, README, FEATURES, ITEMS, the guide and the DEVELOPMENT pages:
  the champions, the chest and its cloak, the game's people's gear (FEATURES' bug table,
  HOW-THE-GAME-WORKS' Monsters' defences), see-through figures, the sounds.
- FEATURES: Kurzak striking with Shadowseeker in the combat log's detail
  (`docs/combat-log-detail.png`).
- DEVELOPMENT: the room in the helper measured in the running game (`UMB_NEED`, 6,186 at this
  build), the dice log's pass, the flags' ledger in one place (DEVELOPMENT § The Loader's game flags),
  the sounds, `VGA_BUSY` and the unanswered requests.
- From the reviews: `inventory-ranger.png` (it showed a gladiator), `effects-charges.png` and
  `dicelog.png` (Cilla's new name) retaken; the guide's multiclass
  combinations once, in its race table; and many smaller corrections across the pages.

## Pull request #85 ([merged 2026-11-02](https://github.com/daaki85/darksun-obsidian-edition/pull/85))

Obsidian Edition 2.13.4 ([release notes](release-notes/v2.13.4.md)).

DSCLOG.EXE 64,592 bytes (688 bytes of its segment spare).

**Changed**
- **The dice log's `--all` line for each AC gives its parts:** base, armour, DEX and other.
- **The dice log names a thri-kreen's claw or bite:** a party thri-kreen with nothing in hand
  attacks `with a claw (1d4)` (four a round) and `with its bite (1d4+1)`, and the bite's damage
  line shows `+1 bite`, not `+1 weapon`. The claw's dice are the ones it has now, with Erdlu Claw,
  Animal Affinity or Body Weaponry. With weapons in hand a thri-kreen attacks with them and then
  still bites. (`GameData.natural_attack`, `THRI_KREEN_ATTACKS`; DEVELOPMENT-CONTENT § The game's
  spells. Seen in DOSBox with K'ratchek unarmed, and a thri-kreen's attacks put on Gerakis. The
  guide's races table and DICE-LOG say so. Tests: `test_thri_kreen_claw_and_bite`.)
- **Erdlu Claw's talons are the claws alone:** a thri-kreen's four claws become 1d6+1, +1 to hit,
  as a +1 weapon, and its bite stays 1d4+1. Body Weaponry and Animal Affinity already change only
  the first set of natural attacks. (DSCLOG's `NS_CLAW`, `NS_FIST`; the dice log's THAC0 breakdown
  the same. The spell's text, FEATURES, the guide, HOW-THE-GAME-WORKS and the patch notes say so.
  Tests: `test_claw`, `test_fist`, `test_fist_claws_cut`, `test_thri_kreen_claw_and_bite`.)

**Fixed: the game** (from yuan-ti and OpenDS's list, yuan-ti's issue #129; each checked in
DSUN.EXE)
- **A character's most PSP comes from its own CON, INT and WIS.** The level-up check (run for every
  member, and at a game's start) took the WIS bonus from the creation screen's record, in play a
  stray byte, and its tables were 8 scores long (INT 22 gave 0). DSCLOG puts the member's own
  scores in, to 25. The most only rises, so a character's may go up once (Cilla 30 to 43, as the
  game's rules give her). The psionicist's WIS bonus a level is left as it is. (`PSP_SCORES` in
  `PROBE_MAX_PSP`; DEVELOPMENT-RULES. Seen in DOSBox. Tests: `test_max_psp_scores`.)
- **A fight's music level is each creature's own:** an attack starting a fight looked up its
  creature's music level with a word's index, so every creature but the first got another's.
  (`gamepatch`'s `fight_music`. Not heard in play.)
- **Ability items count only when worn:** the game applied every listed item's ability change
  wherever it was carried. (`PROBE_WORN` on `INT 81h`; DEVELOPMENT-CONTENT § Worn items, the
  gladiator's armour and Psionic Blast. Seen in DOSBox: a sling given DEX +2 raised DEX 15 to 17
  worn, not in the backpack. Tests: `WornTests.test_ability_byte_only_worn`.)
- **The gladiator's armour optimisation counts only in armour.** (The same interrupt, with
  `ARMOUR_WORN`; `THORNS_AC` and `counted_ac` follow. Seen in DOSBox: Gerakis at gladiator level 10
  AC 5 in armour, 9 in none (before, 7), and a 10th-level gladiator hit at AC 6 in armour in an
  arena fight; playtest/logs/2026-11-02-dsun-fixes.md. Tests:
  `WornTests.test_gladiator_bonus_needs_armour`, the Wall of Thorns damage's gladiator,
  `CountedAcTests.test_gladiator`.)
- **Psionic Blast's wounds are imagined:** the game took a target that failed its save down to a
  fifth of its most hit points for good. A party member's loss is now kept, and given back as the
  fight ends, up to the most and only to a member still Okay, with a dice log line. A loaded game
  clears it with nothing given. (`gamepatch`'s `psionic_blast`, `PROBE_WORN`, `BLAST_HP`,
  `psiblast.py`; DEVELOPMENT-CONTENT § Worn items. Tests: `WornTests.test_psionic_blast_kept`,
  `test_psiblast.py`.)
- **Checked and left alone:** scores over 25 (capped before the tables are read), the difficulty
  setting (applied as a monster comes, by design), a ghost slot or a vanishing item, and a save
  made mid-scene. Left for a test in the game: bodies after a region is left, and a wall of fire's
  damage twice in one move.

**Fixed: the scripts** (`scriptfixes.py`, always on)
- **yuan-ti's v0.1.49 repairs:** the ranger's tracking at the Wagon Train's bodies (script 210),
  the slave pens' sewer grate (137: "hack the lock off" never offered, his or her, a hack that
  works opens it) and the halfling's greeting and insult (31).
- **The Loader's own sweeps** of every script for a field read from a record that lacks it, every
  RAND comparison and every check on a class, race, sex, item, weapon, thief skill or ability:
  sex in script 42 ("wo"man, "her" purse), race in 80 (a thri-kreen hears the bell) and 203 ("your
  help"), script 44's always-true race test, script 142's class tests, and script 56's slime book
  (its class mask meant every cleric, druid, preserver and psionicist). Every object number and
  every thief skill and ability check was checked.
- **yuan-ti's v0.1.50 and v0.1.51 repairs:** an attack on the grate always broke the lock (it read
  a field no grate has); now it rolls `RAND(30) < STR`, as the rip, and can fail. The Rebel
  Mindhome's leader gave the spiders' 5000 XP at every talk; now once (flag 695). (Tests:
  `test_grate_attack_rolls_strength_and_award_once`.)
- **yuan-ti's v0.1.52 repairs** (OpenDS's triage): region 9's messenger comes when flag 245 is set
  during a stay, not only as the region loads, and the Draj serf comes along from region 38 to
  region 10 from farther away. Looked at and left: the Mindhome's "Have you killed the spiders
  yet?", the Hound Necklace killing prisoners, Alhena, the army count. (Tests:
  `test_messenger_trigger_as_mas_9_registers_it`.)
- **The grate's failed hack:** a weapon that can break "breaks against the grate" and is gone; a
  metal or magic one "rings off the grate, unharmed". The game said it broke and kept it. Which
  can break is the game's rule for a weapon breaking in a fight (`Game.item_breaks`).
- A repair longer than its bytes is a detour after the script's end, with a jump back. (Not seen
  in play. Tests: `test_scriptfixes`.)

**Fixed: DSCLOG**
- **A thri-kreen's bite got the claws' Erdlu Claw bonus:** the game sets a round's natural attacks'
  to-hit and magic once, so what the claws got went on to the bite. A natural attack now starts
  with neither. (`NS_FIST`. Seen in DOSBox: the bite at THAC0 15, the claws 14.)

**Fixed: the Loader**
- **The Loader's starting armour gave no AC:** it put worn things in the held weapons' list
  (`+0Ah`), and the game's AC counts only the worn list (`+08h`), so Fuller starting gear's
  leather armour (and a Stalker's cloak) showed as worn and gave nothing. Items are now filed as
  the inventory screen files them, and what an earlier version put in the wrong list is moved
  ("Gerakis's Leg Armor is now counted as worn"). `counted_ac` and DSCLOG's `THORNS_AC` count
  `+08h` only, as the game. (Fuller starting gear. `pickpocket.list_for`, `mend_lists`. Seen in
  DOSBox: an old save repaired to AC 6, Gerakis hit at AC 6 in a new game, not 8. Tests:
  `ListTests.test_mend_worn`, `test_list_for`, `test_add_to`,
  `CountedAcTests.test_held_armour_doesnt_count`, the Wall of Thorns damage's held armour.)
- **A Slowed thief's skills:** Slow rules out picking pockets alone, as the game's routine does;
  the Loader had it ruling out the other seven. (Tests: `test_now`.)

**Docs**
- **DEVELOPMENT in four pages:** its "How each part works" is three pages beside it, ordered as
  FEATURES: `DEVELOPMENT-SCREENS.md`, `DEVELOPMENT-RULES.md` and `DEVELOPMENT-CONTENT.md`.
  DEVELOPMENT keeps building and testing, the dice log, the helper's room, the reports and memory.
  The 66 "How it works" links in FEATURES, KITS, README and HOW-THE-GAME-WORKS name the page they
  open. (`test_readme_links_how_it_works` reads the three pages.)
- **In the game moves to FEATURES:** the Loader README's **In the game** is FEATURES' first section,
  and the README (58 KB to 38 KB) is installing, running, the window and the dice log.
- **The web pages carry their fonts:** `player-guide.html` and `patch-notes.html` load nothing from
  Google Fonts. (`pagefonts.py`, the fonts and their SIL Open Font Licences in `dsloader/fonts`;
  about 190 KB more a page. Checked in Chromium: no request made.)
- **The changelog's five longest entries shortened** (#55, #31, #51, #44, #61), each linking to
  the file as it was; 278 KB to 246 KB. This entry's groups put in the merged entries' order, and
  the older entries' **Added** and **Documentation** called **New** and **Docs**.
- **Level cap by XP is a rule change:** its switch is in Rule changes, Characters, and FEATURES,
  the README, the guide and `options.png` (retaken) follow. More character customization is
  weapon specs, kits, STORE and RECALL and the starting gear.
- **A review for redundancy:** one copy of each repeated table (thief skills, the highest levels
  under the XP cap, preservers' INT, in the player's guide); saved games in one place (the Loader
  README's **Updating, backups, saved games and the Loader's files**); the README's **The creation
  screen**; FEATURES' Spells on the Effects screen linking to the README; Ages and CON's
  regeneration under Classes and Kits in the patch notes; the root README's What's new the current
  release alone; the Options tab's Kits text and FEATURES' bug table; the weapon window's caption.
- **A second review** (with another chat's review of `main` at 2.13.3): the guide's psionics table
  gave Enhanced Strength, Domination and Mass Domination a cost of 0 (the game works it out when
  used); KITS' slot table shows — for "no spells yet"; the README's bugs-fixed line names the
  scripts' checks. Copied tables, Options texts, old names, links, anchors and images checked.
- **A review after the item-list and Psionic Blast fixes:** the psionic powers' cost table stays in
  the guide alone; DICE-LOG's new lines; the README's bug list and the guide's Psionics and
  Equipment; DEVELOPMENT's helper size and upper-memory figures; the game's own party's armour
  list corrected.
- **Erdlu Claw's and the spell arrows' texts fit their box:** they ran to eight lines and spilled
  over its bottom edge. Each is seven lines now. (`spelltexts.py`. Seen in DOSBox;
  `new-spells.png` retaken.)
- Smaller: ITEMS gives the ability items' amounts and a weapon's spell on every hit;
  HOW-THE-GAME-WORKS' **Resting** gives the priests' cures at a rest; a worn item's helpful spell is
  cast for good, a cursed item's attack spell too, as DEVELOPMENT had it (checked; item 2005's
  swapped lists don't matter, there being no item 2005); DICE-LOG gains the Look box's line, PSP,
  the system shock rolls and ages; the guide's spell slot table shows the priests' 6th-level slots
  and where each class stops; the guide's WIS bonus slot table put right at WIS 23 to 25, with a
  6th-level column (checked against `SLOT_RULES` in DOSBox); the patch notes file the thri-kreen's
  claws and bite under Bug Fixes; the known issues say since when; the release notes keep their
  Getting started.

## Pull request #84 ([merged 2026-10-31](https://github.com/daaki85/darksun-obsidian-edition/pull/84))

Obsidian Edition 2.13.3 ([release notes](release-notes/v2.13.3.md)).

DSCLOG's image 64,320 bytes (960 bytes of its segment spare).

**New**
- **The THAC0 on the creation screen:** `THAC0: M18 R19` right of the hit points, above the age: M
  the character's THAC0 less STR's to-hit adjustment, R less DEX's missile adjustment, drawn again as the scores
  change. (DSCLOG's `CR_THAC0_DRAW`; DEVELOPMENT-RULES. Seen in DOSBox. Tests: `test_thac0_line`.
  The README's inventory THAC0 now says all it counts.)

**Changed**
- **The Shinobi's spell slots go on to 13th level:** 3 2 1 at thief level 11, 3 2 2 at 12th and
  3 3 2 at 13th, as the Seeker table in *The Complete Ranger's Handbook* goes on. The table had
  stopped at 10th, so a Shinobi stayed at 2 2 1 to the XP cap. A Seeker still stops at 10th.
  (Kits. `kits.SEEKER_SLOTS`, DSCLOG's `SEEKER_LAST`. Tests: `test_slots`.)
- **The Shinobi gets 4th-level spells at 13th:** a 4th-level slot (3 3 2 1) and Improved
  Invisibility, Solid Fog and Confusion on its list. CHOOSE A SPELL offers one no sooner than its
  slot; a scroll of one can still be learnt sooner. (Kits. `kits.SHINOBI_SPELLS`,
  `kits.shinobi_pick_level`, DSCLOG's `SHINOBI_PICK_CAST`. Tests: `test_slots`, `test_pick_level`,
  `test_pick_any`.)
- **A Spellarcher adds to the same spell's arrows:** with Chill Arrows in its quiver, Chill Touch
  adds more, and the dice log says how many are there now. Another spell's arrows still stop it.
  (`SpellArrows.make`, `MOST_ARROWS`. Tests: `test_make_more_of_the_same`.)
- **The Wasteland Seer is a thri-kreen druid/fighter/psionicist's,** and a druid/fighter has no
  kit now. A multiclass kit may be three classes. One from an earlier version keeps its kit byte
  but has no kit. (Kits. `kitpages.MULTI`, DSCLOG's `MULTI_FIND`. Tests: `test_multiclass_kits`,
  `test_kit_at`, `test_sky_level`.)
- **The Wasteland Seer's psionics follow the sky too:** every power costs 2 PSP less under the open
  sky and 1 more under a roof, never below 1. K'ratchek, a Wasteland Seer by her own feature, has
  it too. (Kits. `kits.psp_cost`, DSCLOG's `PSI_KIT`. Tests: `test_psp_wasteland_seer`.)
- **An Elementalist has at least 1 slot at each spell level a cleric of its level casts,** its slots
  otherwise a level behind as before. (Kits. `kits.slots`, DSCLOG's `PROBE_SLOTS`; `KITS.md`
  follows. Tests: `test_slots`.)
- **The crash report's two buffers moved out of DSCLOG's 64 KB** into the far block in the HMA
  (6,566 bytes left there). GAMEMSG.BIN is the same. (`FAR_QM_STACK`, `FAR_MSG`; DEVELOPMENT § The
  crash report. Tests: `test_crash_report`.)

**Fixed**
- **EDIT on a party member** (to change a name, say) took its kit away, rolled a new age and asked
  for its weapon specs again. It now keeps the kit, the age and, while its classes and kit are
  unchanged, the weapon specs. (DSCLOG's `CR_OPEN`, `ED_SAME`, `ED_KEEP`. Seen in DOSBox. Tests:
  `test_edit_keeps_its_specs`.)

**Fixed** (before release: a review of the changes since 2.13.2)
- The creation screen's THAC0 left out a kit chosen on the panel; it applies it now, and a kit
  chosen or taken back draws the line again. After a Battle Mage's, Mind Warrior's or Arcanist's
  hit points were rolled again the age went missing. (`THAC0_GAME`, `CR_THAC0_BASE`,
  `KIT_REDRAW`. Seen in DOSBox.)
- EDIT gave a kit back whatever the race (a half-elf Shadowblade made a dwarf came back a Ghetto
  Fighter) and a Healer whatever the sphere. (`ED_RACE`, `HEALER_BARRED`.)
- An Elementalist got a 6th-level slot at 11th without AD&D's tables; only with them now.
- K'ratchek's Effects screen line reads "OPEN SKY SPELLS/PSI". (`OWN_LINES`. Seen in DOSBox.)
- Tidier: the Options tab's rule groups in each rule's own entry (`viewer.py`), and the creation
  THAC0 using `DEX_REACTION` and `CREATURE_SCORES`. (Tests: `test_thac0_line`,
  `test_edit_keeps_its_specs`, `test_slots`.)

**Docs**
- **The rule changes in three groups,** the same in the docs and on the Options tab: Characters,
  Weapons and armour, and Magic. FEATURES has a heading and summary table for each (anchors as
  they were). (`viewer.py`'s `rule_groups`; `options.png` retaken.)
- **Pages reordered:** the Loader README's **When something goes wrong** at the end;
  HOW-THE-GAME-WORKS by subject; the player's guide's **Experience and levels** after the kits,
  with **Hit points** and **THAC0 by level** under it, and **Ages** a heading of its own. Anchors
  as they were.
- **A review after the slot table's gap:** hit points past 10th (a preserver +1 a level, a thief
  +2); EDIT in KITS and Ages; the one three-class kit; the Swashbuckler's THAC0 to 13th; K'ratchek
  "is" a Wasteland Seer, her feature named "Open sky spells and psionics" (`kits.OWN_FEATURES`).
- `KITS.md`'s spell slot table goes on to each class's highest level under the XP cap, with a
  druid column, from the code's own tables; the Grove Warden's AC steps go on to 4 at 12th.
- Screenshots retaken: the dice log and Dialogue tab at the arena's opening show, and the creation
  screen with the THAC0.

## Pull request #83 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/83))

Obsidian Edition 2.13.2 ([release notes](release-notes/v2.13.2.md)).

DSCLOG's image 63,680 bytes.

**Changed**
- **The creation screen's age is rolled on Dark Sun's Table 7 dice,** with each roll of the die, a
  choice or the screen opening, not from the name and race. A click on CON, STORE and RECALL keep
  it, and DONE puts it on the sheet. The game's own party, and a character from before ages, get
  real rolls from the Loader. (Ages and magical aging. DSCLOG's `age_dice`, `age_rand`, `AGE_PUT`;
  `give_ages`; DEVELOPMENT-RULES § The age on the creation screen. Seen in DOSBox: four rolls,
  STORE and RECALL, CON down and up, DONE. Tests: `test_age_dice`, `test_age_put`,
  `test_give_ages_once`.)
- **The starting roll is kept on the sheet,** beside the weapon specs (a new layout, v2), so
  Restore Youth's floor is the character's own start and the magical years it can take back have
  no cap. 2.12 and 2.13 sheets still read; a character aged before keeps its age. A save made with
  this is not for 2.13.1 or earlier. (`SPEC_V2`, `aging.start_age`. Tests: `test_packing`,
  `test_rolls`, `test_older_layouts_read`, `test_spec_layouts`,
  `test_an_age_from_before_keeps_its_start`, `test_true_age_from_the_roll`.)

## Pull request #82 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/82))

Obsidian Edition 2.13.1 ([release notes](release-notes/v2.13.1.md)).

DSCLOG's image 63,360 bytes (1,920 bytes of its segment spare).

**New**
- **Grey hair on the party's map figures:** iron grey streaks when middle-aged, grey when old,
  white when venerable, in each figure's own shades. Dwarves and muls (hairless on Athas) and
  thri-kreen are unchanged. The hair is found apart from the gear, with corrections for each race,
  so helms and cloaks don't move. (Ages and magical aging, and What the party wears.
  `greyhair.py`; DEVELOPMENT-RULES § Grey hair on the map. Seen in DOSBox. Tests:
  `test_greyhair`.)
- **The age on the creation screen,** above RECALL (`AGE: 23`), the age the character will start
  at, redrawn as the name changes; the inventory's line is `AGE: 23` too. Characters already given
  an age keep it. (`aging.natural_start`, DSCLOG's `AGE_ROLL`. Seen in DOSBox: six figures and
  three names, each age the Loader's. Tests: `test_creation_age`, and the redraw as the name
  changes.)
- **Natural aging,** as flavour: a year each time the game's clock passes another 365 days, with
  its score changes, and the dice log says `A year has passed: Gerakis is 35.`. The years counted
  are kept in the game's flags (798-806), so a save keeps them, and none is counted twice or lost
  to a load, the arena or play without the Loader. Restore Youth's floor counts them. (Ages and
  magical aging. `aging.natural_tick`; DEVELOPMENT-RULES § Natural aging. Seen in DOSBox. Tests:
  `test_natural_years`, `test_restore_counts_the_games_years`,
  `test_the_log_counts_each_year_once`.)
- **The game's time on the combat log panel:** out of a fight its top line says how long the game
  has run, `Day 47, 14:20`. In the arena it gives the count of arena fights, once the game has
  shown it. (`combatlog.clock_line`. Seen in DOSBox. Tests: `test_clock_line`,
  `test_arena_count_only_once_known`.)

**Fixed: the scripts**
- **Kurzak notices Legcrusher is gone:** once the party has killed him (at the fountain, with no
  alarm), Kurzak's call, his greetings, his answer to "Who is the half-giant?" and Dinos's warning
  ask first whether Legcrusher is on the map. (Always on. `kurzak.py`. Not yet seen in play.
  Tests: `test_kurzak`.)

**Fixed: DSCLOG** (the second audit, with seven agents: code, memory, documents, pictures)
- **RECALL on the creation screen stopped DOSBox** ("DynrecCore: illegal option") from 2.8.0 on,
  when pressed before the die had been rolled on that visit: its redraw called another overlay's
  routine, whose loading could move the creation screen's, and RECALL then jumped to where it had
  been. Both calls are now made so the overlay manager fixes the way back. (`RS_FRAMED`;
  DEVELOPMENT-RULES § STORE and RECALL. Found by re-shooting the creation screen, narrowed down
  release by release. Seen in DOSBox: STORE, the die, RECALL twice.)
- Smaller: the creation screen's text buffer 12 bytes; no far call through an overlay operand not
  yet fixed up; a build guard for the helper's 64 KB segment; the creation age's handlers keep
  their way back apart from `RL_SUM`'s; a duplicate `EXPERT IN` and an unused word gone. (Tests:
  the creation age with 300 random names.)

**Fixed: the Loader**
- **The game folder search no longer holds the window up:** it looks in the folder given and the
  one saved first, then the drives one at a time, once a run, as does Wake of the Ravager's. An
  empty floppy or a sleeping network drive held it up each time the Options tab was built.
  (`launch.drives`, `find_game_dir`. Tests: `test_drives_searched_once_and_only_when_needed`,
  `test_kept_for_the_run`.)
- **The Loader's settings are saved through one helper** that says so on the status line when
  settings.json is held elsewhere, rather than losing the choice unseen.
- Smaller: the game window box shows Single for a window at its own size; a save cut short is
  reported as such; `find-text` and `checks` cope with any text and a lower-case GPLDATA.GFF; a
  missing DOSBox.exe is a launch error; a named save renamed only in case is no longer deleted on
  Windows; the stats thread is waited for before the memory is let go; defilers' scrolls and new
  items in crash reports; `age_by` kept in range, with no "grows younger 0 years" line; the
  mouse wheel's hook thread can't lose a quit; Windows' millisecond timer asked for once a run;
  refused writes kept to the newest 200; the game's art read once a run; confirmations only when
  saved; a settings.json that isn't an object kept aside; the party's figures tried again every
  30 seconds; no armour drawn on a thri-kreen; the Named saves and crash logs folders left out of
  the download mark's removal; dead code gone.

**Docs**
- **The dice log's reference has a page of its own,** `DICE-LOG.md`, linked from both READMEs and
  the guide. The README's Options sections are one list of links, the guide's Options at a glance
  being the one list of switches; the Kits page is the one description of who may take which kit.
- The new work in the guide, the README, the rule table and the patch notes; Dark Sun Recompiled
  in the patch notes; defilers' scrolls counted at once; Enlarge's rule and CON's poison saves in
  the guide; a spoiler note; DEVELOPMENT's memory figures as built and the Ages section in parts.
- Pictures retaken for the age: `inventory.png`, `inventory-ranger.png`,
  `default-party-gerakis.png`, `creation-store-recall.png`, `creation-weapons.png`, `dialogue.png`
  and `dicelog.png`.

## Pull request #81 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/81))

Obsidian Edition 2.13.0 ([release notes](release-notes/v2.13.0.md)).

**New**
- **Ages:** each party member has an age from Dark Sun's Table 7, rolled the first time the Loader
  sees it. Middle, old and venerable age (Table 8) change the scores once and for good, and the
  most a race lives (a secret roll) kills. Shown on the inventory panel (`AGE 23`) and the
  Characters tab. (Ages and magical aging, on. `aging.give_ages`, `aging.age_by`, DSCLOG's
  `AGE_TEXT`; DEVELOPMENT-RULES § Ages. Seen in DOSBox. Tests: `test_aging`,
  `test_effects_specs`.)
- **Haste ages:** each creature Haste speeds rolls system shock by its CON or dies, and a party
  member who survives is a year older. (The same rule. `aging.hasted`. Seen in DOSBox: a failure
  kills as the game kills, a success ages. Tests: `test_aging`'s HasteTests.)
- **Restore Youth, a 6th-level cosmos priest spell (211):** takes back a year of magical aging a
  caster level, never below the target's true age, after a system shock roll. Its icon is the
  mod's own, a fountain of youth, and it is cast with Cure Disease's sound. Negative Plane
  Protection's save record moves to 212. (`aging.restore`, `NPP_SAVE`, `wotrart.DRAWN`;
  DEVELOPMENT-RULES § Restore Youth. Seen in DOSBox: on a 12th-level druid's page, and cast on a
  character aged by Haste. Tests: `test_aging`'s RestoreYouthTests, `test_grace`, `test_dsclog`,
  `test_wotrart`.)

**Changed**
- **Enlarge multiplies the weapon's dice only:** the game's Enlarge multiplied the whole melee
  damage, STR's bonus included. Now only the dice, rounded up, the rest added once; a backstab then
  multiplies the enlarged dice. The dice log and the Effects screen follow. (Enlarge multiplies
  the weapon's dice only, on. `RULE_ENLARGE`, DSCLOG's `ENL_SITE`; DEVELOPMENT-RULES § Enlarge's
  dice. Seen in DOSBox: three hits by an Enlarged gladiator. Tests: `test_enlarge_dice`,
  `test_enlarge_dice_only`.)
- **CON as in AD&D:** the game gave a member with CON 20 or more a hit point every 300 seconds at
  any CON. Now the Player's Handbook's rate, (26 − CON) × 600 seconds a hit point, the remainder
  kept. A dwarf's or halfling's poison save gets no CON adjustment on top of its racial bonus. (CON
  as in AD&D, on. `RULE_CON`, `REGEN_SITE`, `CON_SAVE`; DEVELOPMENT-RULES § CON as in AD&D. Seen
  in DOSBox: Gerakis at CON 22. Tests: `test_regeneration`, `test_dwarves_poison_saves`,
  `test_modifiers_by_damage_kind_and_con`.)
- **The weapon specs are packed, making room for a character's age** in the sheet's last unused
  byte. A sheet keeps the old layout until its specs are written, and every reader takes both, so
  older saves and roster characters need no conversion. (`SPEC_PACKED`, `SHEET_AGE`,
  `game.spec_kinds`. Seen in DOSBox: both layouts read alike, through a save and load. Tests:
  `test_specslots`, `test_spec_layouts`, `test_specs_packed`.)

**Fixed** (from a code audit of this pull request and the Loader)
- **A new character could keep the last one's age:** DONE cleared the specs but not the age. (Test:
  `test_spec_layouts`.)
- **Haste rolled again after a reload:** the same party loaded again counts as a load now.
- Smaller: Enlarge's dice kept for a melee hit only; a score past 25 not cut by a +1, nor one under
  3 by a −1; a thri-kreen made young "no longer venerable"; no system shock for a creature with no
  scores; a CON past 25 reads no table; the game's Enlarge rounds toward 0 in the dice log; the
  patch notes' page no longer hangs on a "> " line; settings.json with a byte-order mark is read;
  the recompiled program's ordinary exit isn't "cut off"; more errors caught (a short GFF, the
  age, the named saves' folder, Restore Youth's icon). (Tests: `test_settings_with_a_bom`,
  `test_recompiled_exit_is_not_cut_off`, `test_a_plain_quote_is_text`,
  `test_scores_never_cut_the_wrong_way`, `test_every_rule_has_its_box`.)

**Docs**
- A review of every document for the new rules: the patch notes, FEATURES (the whole system shock
  table), the guide, the README and DEVELOPMENT's memory figures. Screenshots retaken: the ten
  priest spells, the inventory panels, the default party's inventory, the Options tab.

## Pull request #80 ([merged 2026-10-30](https://github.com/daaki85/darksun-obsidian-edition/pull/80))

Obsidian Edition 2.12.5 ([release notes](release-notes/v2.12.5.md)).

**New**
- **The Effects screen names Enlarge's damage:** ENLARGED (+90% DAMAGE), 10% a level of its
  caster. The inventory's DAM lines have no room for it. The game lets only one Enlarge on a
  creature. (`GameData.enlarge_level`, `STATS_ENLARGE`, DSCLOG's `EF_CHARGES`. Seen in DOSBox:
  Cermak's Enlarge on Gerakis. Test: `test_enlarge_level`.)
- **The Effects screen names the armour spells' AC:** BARKSKIN (AC 3), FLESH ARMOR (AC 8),
  MAGICAL VESTMENTS (AC 3), from the effect's level as the game has it (a psionic power's is the
  psionicist level). (`GameData.armour_spells_ac`, `GameData.effect_level`. Seen in DOSBox on
  K'ratchek and Cermak. Test: `test_armour_spells_ac`.)

**Fixed**
- **Whirlwind's swept creatures lose their next turn, and it strikes once a round:** a swept
  creature still took the turn that swept it, and a turn lost was a round of 2d8 spared. Now it
  strikes everyone in it at the start of each round, before anyone acts, and those who fail lose
  that round's turn. As it is cast, one swept that has yet to act loses that turn. (`WW_PASS`,
  `WW_GATE`, `SWEPT_NOW`; DEVELOPMENT-CONTENT § The game's spells. Found and seen in DOSBox:
  K'ratchek's Whirlwind on the arena's sligs.)

**Docs**
- A review for 2.12.5: Whirlwind's timing, and the Effects screen's Enlarge and armour lines.
  Links, anchors and pictures checked; `whirlwind.gif` still right.

**Dev**
- `test_to_hit_effects`: THAC0 with each effect the game's attack counts and none from another
  creature's.

## Pull request #79 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/79))

Obsidian Edition 2.12.4 ([release notes](release-notes/v2.12.4.md)): Dark Sun Recompiled, from pull
request #78, in a release.

## Pull request #78 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/78))

**New**
- **The Loader reads the game when it runs as Dark Sun Recompiled**
  ([its page](https://github.com/daaki85/darksun-recompiled); a `dsun` process; its memory found
  by the BIOS date, or by the mark `DARKSUN-RECOMPILED`).
- **The Loader can start that program instead of DOSBox:** `dsloader launch --recompiled <path to
  dsun.exe>` remembers it (`--dosbox` goes back), and `launch`, `play` and **Start the game** run
  it with the game's folder and the mod's `dos` folder. (README, "Other ways to start".)

**Fixed** (before release: a review after main, with 2.12.2, was merged in)
- The game's own DOS `DSUN.EXE` was taken for the program on Windows when the mod was unzipped in
  the game's folder. A program found or named must be a Windows PE or an ELF.
  (`launch.native_program`. Test: `test_the_games_dos_program_is_not_it`.)
- Which one runs is said as the game starts, in the dice log, and the closing line goes by what
  was started, not the settings. (`launch.started_line`, `launch.STARTED`. Test:
  `test_started_and_closed_lines`.)
- The memory search's chunks overlap by the longest mark, so the mark is found across two. (Test:
  `test_recompiled_mark_across_two_chunks`.)
- `--recompiled` and `--dosbox` save with `launch.update_settings`, so a settings file locked for a
  moment is never saved over with only that change. The test's stand-in programs are Windows
  programs.

## Pull request #76 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/76))

Obsidian Edition 2.12.3 ([release notes](release-notes/v2.12.3.md)). Pull request #77 added this heading.

**Fixed: DSCLOG** (from a code audit, and Haste and Slow)
- **Haste and Slow show in the attacks a round:** a fight doubles a hasted character's attacks and
  halves a slowed one's, but neither the DAM lines nor the Characters tab did. The inventory's line
  also showed one half-attack as one a round; a slowed character's reads `0.5x1D8+6` now.
  (Whatever the rules. `GameData.weapon_hits`, DSCLOG's `SPEED_HALVES`, `gamepatch` `dam_half`.
  Seen in DOSBox: Gerakis hasted 5 attacks a turn, K'ratchek 10. Tests: `test_hasted_and_slowed`,
  `test_dam_half`.)
- **View Character's damage matches the fight's:** it left out a non-magical weapon's penalty for a
  weaker material (2 less in wood, 1 in bone, stone or obsidian). The dice log's damage line names
  it (`-1 bone`). (`VIEW_MATERIAL`, `game.MATERIAL_DAMAGE`. Found in DOSBox with Cilla's bone long
  sword. Tests: `test_view_dam_weak_material`, `test_weapon_damage_weak_material`.)

**Fixed: the Loader**
- **The arena's Ring +1 shimmers as soon as it is found:** it got its own picture a pass later, and
  an inventory opened between kept the plain ring's. Every item the Loader makes now gets its own
  picture as it is made. (`icons.fit`, `icons.COPY_OPEN`. Test: `test_its_own_icon_at_once`.)
- **K'ratchek's second chatkcha throw a round shows with weapon specialization on** on the
  Characters tab. (Test: `test_kratcheks_chatkcha_with_specialization`.)
- **The no-window Play mode carries on after an error,** as the window has since 2.12.1, and DOSBox
  closing mid-read counts as a disconnect. Other errors go to `play.log` once each.
- **settings.json is never replaced by a single change:** a failed read (a Windows lock from an
  antivirus or a backup) gave empty settings, and a save then lost every option. Such reads now
  retry and then raise, and the Options tab says if a save can't be made. (Test:
  `test_a_locked_settings_file_is_never_saved_over`.)
- **A roll half seen no longer spoils the next:** dice collected when the rest was missed are
  dropped. (`_forget_partial_rolls`. Test: `test_half_seen_rolls_dropped_when_rolls_are_missed`.)
- **An error after a pass's rolls keeps those rolls,** with one line in the dice log once a kind,
  and the item lists' gate is released whatever happens. (`_after_rolls`. Test:
  `test_rolls_kept_when_a_later_step_fails`.)
- **The arena's Ring +1 never loses an item record:** the backpack's list is checked first. (Test:
  `test_no_list_keeps_the_record_free`.)
- Smaller: the dialogue pane stays at 3,000 lines and a portrait shown many times is one image;
  the game folder is kept as a full path.

**Docs**
- A review for 2.12.3: weaker materials' penalties in the guide, Haste and Slow in FEATURES, the
  backstab example's `-1 bone`, and `docs/dicelog.png` retaken (K'ratchek's chatkcha at 5/2).
  Links, anchors and pictures checked.
- **A thri-kreen Mind Warrior who presses EXIT on the weapon window gets the chatkcha;** KITS.md
  said the club. (Test: `test_mind_warrior_exit`.)

## Pull request #75 ([merged 2026-10-29](https://github.com/daaki85/darksun-obsidian-edition/pull/75))

Obsidian Edition 2.12.2 ([release notes](release-notes/v2.12.2.md)).

**Changed**
- **A thri-kreen Mind Warrior may take the chatkcha as its weapon spec,** as well as its class's
  melee ones: 3/2 throws a round, 2 from a warrior class's 7th level. (Weapon specialization.
  `restrict.allowed_kinds`, DSCLOG's `KINDS_ALLOWED`. Test: `KindsAllowedTests`.)

**Fixed: DSCLOG**
- **The in-game combat log no longer flickers in a fight:** many drawings go to the game's second
  screen and are then flipped, and the panel was only on the first. DSCLOG now puts it on the
  screen about to be shown. (`FLIP_PANEL`, `FLIP_SITE`, `gamepatch` `panel_flip`;
  DEVELOPMENT-SCREENS § The combat log in the game. Seen in DOSBox: 40 seconds of an arena fight
  at 43 frames a second, no frame without the panel but under a game window. Test:
  `test_panel_flip`.)
- **A fight runs as fast with the combat log up as without it:** a rectangle drawn over the panel
  was drawn in parts, each its own flip waiting for the monitor, so a monster's turn took a sixth
  longer (1.03 seconds against 0.89). It is drawn whole now. (Seen in DOSBox: 0.95 seconds with the
  panel against 0.83 without, within how much turns vary.)

**Fixed: the Loader**
- **Shillelagh and Spiritual Hammer shimmer on the party's figures,** as the Flame Blade does,
  drawn whole in the game's animated colours. (`spritegear.SPELL_WEAPONS`. Seen in DOSBox. Tests:
  `test_spell_weapons`, `test_named_weapons`.)
- **A new Poisoner with the short sword as its weapon spec starts with a short sword in each
  hand,** not two daggers. One made before, still New, has both made short swords. (Tests:
  `test_poisoner_daggers`, `test_poisoner_spec_changed`.)

**Docs**
- **Three animated pictures, recorded in DOSBox:** `docs/combat-log-live.gif` in the Loader README,
  `docs/whirlwind.gif` anew in FEATURES and `docs/magic-glint.gif` under What the party wears,
  grabbed at about 48 frames a second and scaled whole.
- A review for 2.12.2: the patch notes' line on magic gear's glow, and the guide's attacks-a-round
  table gains a thri-kreen Mind Warrior's chatkcha. Links, anchors and pictures checked.

## Pull request #74 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/74))

Obsidian Edition 2.12.1 ([release notes](release-notes/v2.12.1.md)).

**Fixed: the Loader** (from an outside audit of 2.12.0)
- **"In a fight" means a fight again.** The Loader read only the game's `IN_COMBAT`, which stays up
  while the party walks spread out, and since 2.12.0 spreads the party after every load and fight,
  it took much of ordinary walking for a fight. Stuck walkers weren't set going again, the Battle
  Dancer's dances and Wild Fighting weren't ended with the fight, defilers were rolled for scrolls
  outside fights, and the combat log's fight state, Tab targeting and an item report's "In a fight"
  went wrong. It now also asks the game's own fight test (the fight state's +19h, as stealth already
  did). (`GameData.in_combat`, `stuckwalk`. Test: `InCombatTests.test_spread_out_isnt_a_fight`.)
- **Settings never lost.** The settings are written to a temporary file and put in place (retried a
  moment on Windows), so a read never sees a half-written file. One that can't be read is set aside
  as `settings.json.bad`, not saved over with only the keys a caller had (the combat log panel's
  level could wipe every option and the game folder). The window and the thread reading the game no
  longer lose each other's changes: each read-modify-write is one step. (`save_settings`,
  `SETTINGS_LOCK`, `update_settings`. Test:
  `test_settings_saved_whole_and_never_over_an_unreadable_file`.)
- **The party table and the dice log keep going** after an error they didn't expect. Both refresh
  loops schedule the next pass whatever happens, and say the error once in the dice log (`Loader
  error in ...`, with the file and line) instead of stopping for the rest of the session. (`_tick`,
  `_dice_tick`.)
- **The combat log's header shows the arena count between fights again.** In the slave pens and the
  arena it had shown the round (the fight above), and where the game's numbers weren't in memory
  (most of the time outside a script's run) it showed nothing. The Loader keeps the count it last
  read, and says `Arena fights: ?` until it has read one. (`combatlog.Panel.update`. Seen in DOSBox:
  `Arena fights: 1` in the pens, the party spread out. Tests: `test_arena_count_in_the_header`,
  `test_arena_count_remembered_for_the_header`.)
- **Defilers' scrolls in every fight.** The rolls were kept for the session by area, slot and name,
  so a later fight's defiler in the same place under the same name (the arena's) got none until a
  game was loaded. They are forgotten as each fight ends. (Test: `test_again_in_the_next_fight`.)
- **No spell arrows in armour:** a Spellarcher in armour casts nothing, and now weaves no arrows
  either. (`restrict.no_spells`. Test: `test_make_in_armour`.)
- Smaller: DOSBox is never left paused (the item gate resumes it if the look after pausing fails);
  DOSBox's process handle is closed on a disconnect, a reconnect and a failed try, and the mouse
  wheel's hook comes off when its dice log closes, where each reconnect added another (`_located`,
  `_drop_guest`, `WheelHook.stop`); the combat log's short attack line for an attack that hits on
  anything but a 1, which showed the long line (test `test_attack_that_hits_on_anything_but_a_1`);
  Dispel Magic's caster level for the 6th-level priest spells (202-210), whose spheres it gave none
  (`effect_caster_level`, `PRIEST6_MASKS`).

**Docs**
- **Psionicists' and thieves' weapons and shields,** checked against the game's item lists and
  `restrict.allowed` for each mix of classes (a human's save holds only its present class, so the
  game's own check sees that one). A psionicist alone: daggers, bone and obsidian short swords,
  clubs, chatkchas and bows, and no shield (the rule takes away the axes, picks, gythka and long
  swords the lists allow). With another class, also the maces, metal short sword and slings that
  class's lists allow, and a leather shield with a fighter, gladiator, ranger or cleric class. A
  thief of any kind: leather shields only, and a multiclass one only with one of those classes. The
  guide's and FEATURES' tables and the guide's psionicist section say so (#71's review had taken
  maces and slings from every psionicist, and both tables gave a psionicist alone a leather shield).
- **Documentation review** (the audit's remaining documentation findings, each checked against the
  code): the front page and the Loader README say the patched game writes page 1's saves and every
  character too, and that a save with the new items wants the Loader; "nearly every" rule change has
  a switch (not the keys or the game's fixed bugs); the Loader README lists `dosbox_dicelog.conf`
  and the Memory tools' layout and search files; FEATURES says its bold switch names are short forms
  of the Options tab's sentences, lists all five thieving switches, gives the thief table's cap (95)
  beside its 99s (the guide too), says which items Alagorn has no story for and when a defiler is
  rolled for; the guide's Options table gains Wake of the Ravager and says kits and starting gear go
  to new characters; KITS: a Twin-blade can't use a bow or the staff sling; DEVELOPMENT:
  `--window-scale` 1 to 4, and a line on each module the sections don't come back to; the combat
  log's HANDOFF no longer points at a section that's gone; the README's level-cap range and Linux
  line made exact (Windows only for the `.bat` files and Start the game; no macOS). Reports now list
  the combat log's level with the other switches (`launch.SWITCH_DEFAULTS`).
- Smaller: the Loader README has three built files, not one, what a report holds, and to read one
  before posting it; FEATURES' Kalzith caption no longer claims a quarter off at CHA 20 (15%); KITS:
  no spell arrows in armour; DEVELOPMENT's party-in-view and camera notes say `IN_COMBAT` is also
  set while the party is spread out; the patch notes put the half-giant and thri-kreen lines under a
  Races heading; the 2.12.1 notes and the front page lead with the fight fix; the Loader README says
  the panel's round once. Screenshots checked: none out of date.
