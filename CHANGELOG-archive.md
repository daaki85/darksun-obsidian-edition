# Changelog archive

Pull requests #1 to #73 (Obsidian Edition 1.0.0 to 2.12.0) as the [changelog](CHANGELOG.md) recorded them, newest first; newer ones are in the changelog. A release's line is its entry's **Release** bullet.

## Pull request #73 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/73))

**Release**
- **Obsidian Edition 2.12.0**: the version is 2.12.0, with its notes in `release-notes/v2.12.0.md`,
  for #70 to #72.

## Pull request #72 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/72))

**Docs**
- **ITEMS' Every mundane armour piece gives each piece's AC:** how many points it takes off AC 10,
  read from the game's item types (the byte that gives plate's 3, 2 and 2 and the shields' 1); helms
  0, or 1 with Helms give AC 1.
- Small pass after the review: the guide's "Making a party" points to KITS' Choosing a kit instead
  of repeating it; its Starting gear links KITS' for the kits' weapons; the Shinobi's Effects screen
  picture is in KITS only; each class's dual-class line links the kits that rule a change out. KITS:
  a shorter introduction, no quoted Loader strings in The kits in play and Changing class.

## Pull request #71 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/71))

DSCLOG's image 61,040 bytes (about 4.4 KB of the helper's room spare).

**New**
- **U and I close their screens again,** as M does the overhead map. U on the inventory or I on USE
  still switches screens (the game's), the other key then closing it. The game reads a key with a
  peek and then the read, so the key is kept only on the read: kept on the peek, I on USE switched
  and was then read as Escape. (DSCLOG's `MAP_KEY`, `OVERHEAD`, `MK_READ`. Seen in DOSBox: U, I and
  M each opening and closing their screens, U and I switching between USE and the inventory.)
- **The whole party in view** as a game starts or loads and after each fight, as the game's 5 does;
  6 still gathers it. DSCLOG calls the game's own spreading routine on the map, out of a fight,
  after a load or a fight's end (not after 6). A 5 put in the BIOS's keyboard buffer was tried first
  and never read, as the game reads keys only in its keyboard interrupt. (Options: "The whole party
  in view", on; `party_spread`. `gamepatch.PARTY_SPREAD`, DSCLOG's `SPREAD_LOAD`, `SPREAD_GATHER`,
  `SPREAD_TICK`. Seen in DOSBox: the "Kalzith test" save loading with the whole party in view, a new
  game's opening fight ending so, 6 gathering it and it staying gathered. Test:
  `test_party_spread`.)

**Fixed**
- **No "(15 CHARGES)" on a magic item's power on the Effects screen** (Shadowseeker's Detect
  Invisibility). The game adds an item's power as it does a permanent effect, leaving a stray value
  in its record's charges byte, and charges showed unless the spell's own time was permanent. They
  show now only for a spell lasting a number of uses or a timed effect, as Armor's. The same rule
  gives the dice log's and the Characters tab's effects. (DSCLOG's `EF_CHARGES`, `NS_CHARGES`;
  `game.effects_left`. Tests: `test_item_power_has_no_charges`, `test_time_and_charges`.)
- **Two Whirlwinds on the map both turn.** DSCLOG kept one funnel, so with two each one drawn
  replaced the other and only the last drawn turned. Each Whirlwind has its own entry now, up to
  four, emptied at each round's start and each cast. (`WT_TABLE`, `WHIRL_PICK`, `WHIRL_TICK`,
  `WHIRL_CLEAR`. Seen in DOSBox: two Whirlwinds in Scar's fight, both funnels changing in each of 9
  frames in a row.)
- **Restore defaults keeps the combat log on** (the Loader set it off).

**Docs**
- The new work in FEATURES (Controls: M, U and I; The whole party in view), the guide's Controls and
  Effects screen rows, PATCH-NOTES, the Loader README's summary and Effects screen, and DEVELOPMENT
  (M, U and I; the whole party in view; charges on the Effects screen; Whirlwind's funnels; the
  helper's room).
- **Full documentation review** (with reviewers per document group). PATCH-NOTES: a stray
  parenthesis, the two game-speed lines merged, the party-in-view line's switch, four more kit
  changes. Root README: name history dropped, a note on what is new since 2.11.0. Loader README:
  Fastest "nearly every frame", GOG's 7,000 cycles, the jerky-walking text, the Controls and Game
  speed summaries, the defaults sentence. FEATURES: M, U and I simpler, Whirlwind's two funnels,
  item powers' charges, the old Healer's cosmos spells (moved from KITS). DEVELOPMENT: stale names
  (`PP_EXTRA_DRAW`, no `WP_TWO`), history trimmed, two missing contents entries. The guide: the
  whole party in view in the Options table, psionicist weapons as the game's lists allow, Gythka +2
  and Kreenfang marked as the mod's, no place name in the Poisoner's text, multiclass kits in the
  Kits intro, Magic's "Effects" renamed "Status effects". KITS: the Loader's once-a-second check and
  version history out. No helm has Gaze Reflection, so the item-power example is Shadowseeker's
  alone. Screenshots checked: `options.png` opens only sections that have not changed.
- **Doc review, part 3.** The guide: Quality of life's running-the-game table and Loader-window list
  cut to two paragraphs linking the README; the New items weapon table loses its "who can wield it"
  column (each class's list says that); the Spellarcher's arrows added to Other magic items; casting
  when hit explained once, under Initiative, and linked from the preserver, Worth knowing and KITS.
  ITEMS: **Every mundane armour piece**, a new table of plain armour and shields with who sells and
  carries each (read from the game's data, as the weapon table).

## Pull request #70 ([merged 2026-10-27](https://github.com/daaki85/darksun-obsidian-edition/pull/70))

DSCLOG's image 60,528 bytes (4.9 KB of the helper's room spare).

**New**
- **The whole party walks at full speed on the map,** shadows and dust on, at the default 20,000
  cycles (in the slave pens 249 to 278 pixels a second, where it was 152 to 175; the leader alone
  about 220 to 260). When a frame would be drawn late the next one isn't drawn: the game's step for
  everything still runs, and the frame after draws what moved in both. DSCLOG keeps a schedule of 70
  frames a second on the game's clock, in place of the map frame's two far calls; fights draw every
  frame. An earlier try that caught up only figures' animation steps did nothing, as the "think"
  that starts a figure on its next square runs once a frame. (Options, under Game speed: "Walking at
  full speed on the map", on, from the next start; `steady_pace`. `gamepatch.STEADY_PACE`, DSCLOG's
  `PROBE_PACE_PASS`, `PROBE_PACE_DRAW`, `FAR_PACE`; DEVELOPMENT-SCREENS § Game speed. Seen in
  DOSBox: walking, two arena fights with no frame skipped, the view scrolling with frames skipped in
  the arena and in the pens at 6,700 cycles, and the arena-to-pens change, each followed by a full
  redraw that matched the screen but for braziers and figures mid-step. Tests: `SteadyPaceTests`,
  `test_steady_pace`.)

**Docs**
- Steady pace in FEATURES' and DEVELOPMENT's Game speed, the requirements table's Fastest, the
  guide's Game speed and Options rows, and the patch notes. FEATURES' Game speed has
  `steady-pace.gif`, the whole party walking in the slave pens with steady pace off and on side by
  side (recorded at 70 frames a second, shown at half speed).
- **FEATURES' pictures shown a second, measured** by counting the game's page flips while the whole
  party walks in the slave pens: about 37 with steady pace off, about 27 with it on (it said about
  40). DEVELOPMENT says how to count them.
- Doc review: the patch notes' two game speed lines made one (the old one gave the party's walking
  to the cycles setting), and four "fixes" of the mod's own bugs taken out of them (shadows lost in
  big fights, figures vanishing, the Weapon Merchant and Jark, the spell arrows' level: the
  Spellarcher's line says it); FEATURES' bug table gains "Out of memory in OEOpenGraph" and Slay
  Living's description; the guide's backstab (it said STR's bonus is multiplied, the game's own
  rule) and its hit-die kits (two, not three); the gladiator's AC line as the game's own;
  HOW-THE-GAME-WORKS gains "How fast the party walks", linked from FEATURES' Game speed;
  DEVELOPMENT's room in the helper and memory map brought up to date; ITEMS' acid table without
  Dunesong (bows are never at risk); the README's feature list and troubleshooting mention steady
  pace; Jark is in Kel's caravan (#64's entry said Tyr).

## Pull request #69 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/69))

**Release**
- **Obsidian Edition 2.11.0**: the version is 2.11.0, with its notes in `release-notes/v2.11.0.md`,
  for #68.

## Pull request #68 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/68))

**Changed** (kit balance)
- **Arcanist** keeps two preserver spells a turn but loses its spell slot more at each level; the
  **Scholar** has it now. (`kits.slots`, DSCLOG's `PROBE_SLOTS`.)
- **Mind Warrior:** the psionicist's d6 hit die, not a d8; its tenth fewer PSP stays.
  (`kits.hit_die`, `PROBE_HIT_DIE`, `PROBE_CR_DIE`.)
- **Rescuer:** its cures heal 1 more a die anywhere, not only under the open sky, and it has 2 more
  Move in a fight. It may no longer hold a shield (a new one's starting shield is left behind).
  (`KIT_MOVE`, `KIT_FORBIDS`, `kits.forbids`.)
- **Wilderness Avenger:** +1 to hit and damage against anything, not only undead. Its cost, a druid
  slot fewer at each level, became light armour only for a while, which cost a druid nothing; it is
  now **no healing spells**. Cure Light, Serious and Critical Wounds, Blood Flow, Heal and Water of
  Life are kept from it as it is made, in the routine giving a priest its spheres' spells and for
  the 6th-level two (a level up marks no priest spells), and one in an older save loses them when it
  is loaded. In return its Cause Light, Serious and Critical Wounds do 1 more a die. (`KIT_EXTRA`,
  `AV_HEAL`, `AV_KNOW`, `AV_GRANT`, `NS_PRIEST_KNOWS`, `kits.avenger_heals`, `AV_CAUSE`, the dice
  log's `_harm_bonus`; `LIGHT_KITS` and `KIT_LIGHT` dropped. Seen in DOSBox: a new Avenger with no
  cures known and the causes known, one through a level up given no cures, and its Cause Wounds'
  extra die.)
- **Assassin:** a backstab's multiplier one more, x3 to x6. (`STAB_TIMES`, `kits.backstab_times`.
  Seen in DOSBox: x5 at 9th level.)
- **Poisoner:** every melee weapon hit poisons, not a shot or a throw, the target's save as before;
  no −1 to hit; its weapon spec the dagger or the short sword only. The poison works only on damage
  with no spell or power behind it, as the poison's own damage comes back through the same routine
  and, once a fight no longer stopped it, poisoned again and again. (`KIT_SHOT`, `PROBE_ATTACKS`,
  `PROBE_POISON`, `KIT_POISON_KINDS`, `kits.POISONER_KINDS`. Seen in DOSBox: hits, one save each.)
- **Healer:** no ranger of air, earth or fire, either way of DUAL (the game already bars a cleric
  from becoming a cleric or druid, and a druid a cleric). After DUAL the sphere menu is WATER ONLY
  for a Healer, as the DUAL window keeps a ranger's row open while the water ranger is allowed.
  (`DUAL_BANS`, `DUAL_SPHERES`, `PROBE_SPHERE`. Seen in DOSBox: DUAL both ways, and which classes
  the game itself bars.)
- **Spellarcher:** spell arrows only into an empty quiver (else nothing is made and no slot used),
  and kept there as a Flame Blade is kept in the hand. The drop at the party's feet is gone.
  (`PROBE_TAKE`, `QUIVER_KEPT`; `ARROWS_DROP`, `Attempt.drop` removed. Seen in DOSBox: all four
  cases. Tests: `QuiverTests`, and the kits' slots, move, to-hit, poison and kinds tests and the
  Rescuer's shield for the rest.)

**Docs**
- Doc review: the dice log's hit-die line names the Battle Mage and Arcanist (the Mind Warrior has
  the psionicist's die now), and the guide's hit points list them; the item report's example names
  Inixhide as the log does; the guide's Spellarcher entry is flavour and a link, as the other kits'
  are; the patch notes' new spells by level, and Kalzith's scrolls said once; a repeated clause gone
  from the Military Scout's row; long lines wrapped. Screenshots checked: none out of date.

## Pull request #67 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/67))

**Release**
- **Obsidian Edition 2.10.0**: the version is 2.10.0, with its notes in `release-notes/v2.10.0.md`,
  for this pull request and #64 to #66.

## Pull request #66 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/66))

**Docs**
- The patch notes no longer say a save already in Teaquetzl stays without the Weapon Merchant (the
  user's save has him); the fix is under Bug Fixes instead.

## Pull request #65 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/65))

**Fixed**
- **Dunesong counts at the Bowyer's archery target.** Script 178 counted the bows in hand by their
  objects, the game's three. A jump to code at the script's end now counts Dunesong as Phrain's Bow
  is counted, and the rest of the jumped-over command is a filler command, so the script still reads
  command by command and nothing moves (the roll is still where the dice log looks).
  (`bowyer.with_dunesong`; DEVELOPMENT-SCREENS § The Bowyer's archery target. Seen in DOSBox: a
  centre shot with Dunesong from 15 squares, and the Bowyer's arrows.)

**Docs**
- Dunesong's line in the patch notes is its row in the Items table (no second bullet under World),
  and FEATURES' New items says it counts at the Bowyer's target, linking to the target's rules.
- From a review of the docs: the front page's first caption describes its picture (round 7,
  K'ratchek's turn, a Slig's hits on Cermak); DEVELOPMENT says "a few hundred" of the game's
  changes, not a count that goes stale; #64, #63 and #61 have their merge dates; the patch notes say
  they follow the repository (a change since the current version is in them before its release); the
  front page's "What's new" has the latest release only; and the tests workflow runs when only
  `CHANGELOG.md` or `release-notes/` change, as the link tests read them.
- `creation-store-recall.png` retaken: the creation screen as it is now, KITS where it showed the
  WEAPON SPEC label the mod no longer draws (the spec is picked after DONE).

## Pull request #64 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/64))

**New**
- **The scripts' own ability checks in the dice log.** 13 conditions compare the scripts' random
  command with an ability of the character acting instead of using the ability check command:
  Chahl's CHA (181), the chains' STR (76), secret doors' INT - 10 (69)... The Loader finds them in
  its GPLDATA.GFF and evaluates each with the roll and the score of whoever's turn it is: `Daaki CHA
  check: 0-19 = 15, always made (CHA 20) -> success`. (`scriptchecks.py`, `_script_check`;
  DEVELOPMENT-SCREENS § Ability checks in the scripts' conditions.)
- **Nineteen of the game's magic items shine** in their icons, as the Parting Staff's gem does: the
  Chameleon Gloves, the Hornblade, Cahulaks +1, Dag's Dagger, the Terror Blade, Blackmace, the
  Shimmer, Drake and Silk Armor, Tanelyv's and Grey's arms and legs, the Living Cloak, the Golden
  Torque, Light of Dawn, El's Ring and the Orb of Knowledge. Their metal, gems or leather take the
  water's or the fire's cycling colours, every other pixel (a leaf's greens for the silk and the
  cloak). Cahulaks +1, Light of Dawn and El's Ring shared their icon with plain items, so they get
  pictures of their own (BMP 2653-2655). (`icons.SHINE`.)
- **The Bowyer's archery target in the dice log** (script 178): each shot's roll, what it needed
  (DEX - distance / 2), the distances from the target and the Bowyer (the game's distance command
  ported) and the result: a miss, a ring, the centre, and whether it earns the arrows. (`bowyer.py`,
  `bowyer.distance`, `GameData.thing_square`, `things_of`; DEVELOPMENT-SCREENS § The Bowyer's
  archery target.)

**Fixed**
- **The Weapon Merchant was missing from Teaquetzl's market** (since 1.2.0), and Jark from Kel's
  caravan. The game's routine reading an object's records keeps them in a table of 80 and gives up
  on an object with more, and the person's map entry was then freed: the merchant had 89 records
  with the Loader's 11 weapons, Jark 95 (the game's largest has 74). The table has room for 120 now.
  A save already in the village has him too (checked in the user's save). (`gamepatch`'s
  `records_*`. Test: `test_records_fit` keeps every object the Loader adds under it.)

**Docs**
- **Documentation review.** FEATURES has a section on the magic items' icons (and its Graphics intro
  and contents say so), DEVELOPMENT how `icons.SHINE` works and its three own pictures,
  HOW-THE-GAME-WORKS the Bowyer's archery target (the three bows its script names: not the Loader's
  Dunesong, as ITEMS now says), the Loader README's summary the gear's glint and the icons' shine;
  the patch notes' long dice-log line is three.

## Pull request #63 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/63))

**Release**
- **Obsidian Edition 2.9.0**: the version is 2.9.0, with its notes in `release-notes/v2.9.0.md`, for
  this pull request and #62.

## Pull request #62 ([merged 2026-10-26](https://github.com/daaki85/darksun-obsidian-edition/pull/62))

DSCLOG's resident part 56,496 bytes (7.1 KB of its 64 KB segment spare).

**New**
- **Charges left, in the dice log and on the Effects screen.** Each charge used says how many are
  left (`Improved AC on Slig: one charge used, 7 left`, "none left: it ends" for the last). The
  charge routine's 2d4, a bare "Dice: 2d4" line, is told by its arguments. On the Effects screen the
  name under the pointer says them too, for any effect with charges: IMPROVED AC (10 CHARGES),
  MIRROR IMAGES (3 CHARGES), REFLECTED IMAGE (2 CHARGES); not for a permanent effect.
  (`count_charges`, `_overlay_charge`; DSCLOG's `EF_CHARGES`, `EF_TEXT`, `REFLECT_ENTRY`,
  `ns_reflect_entry`.)
- **A charge used floats over its creature,** as "Miss" does: "Armor: 7 left", "Reflected Image: 2
  left", "Armor ends", in light blue, from each charge line of the dice log. The image-lost line
  says what is left too. These stay 3 seconds, and a "Miss" or a spell's name doesn't take their
  slot. (`labels.CHARGE_INK`, `_charge_spells`, `CHARGE_FOR`, `priority`.)
- **Up to four floating labels at once** (were two). (`LBL_SLOTS`, `labels.SLOTS`.)
- **M opens the overhead map,** and M again closes it. (DSCLOG's `MAP_KEY`, `OVERHEAD`.)
- **A Shinobi's read languages on the Effects screen,** under its kit: `READ LANG. 40%`.
  (`RL_LINE_OF`, from the Loader's `READ_LANG`.)
- **Scar's henchmen carry bone axes,** dropped when they die. (`worldgear.GIFTS`, object 229.)
- **The Parting Staff shines** as the game's magic weapons do: its gem's blues in the water's
  cycling colours. (`icons.SHINE`, its own icon, picture 2157.)
- **A Battle Dancer can't use a shield,** as it already fought with long swords and bows only.
  (`KIT_FORBIDS`, `kits.forbids`.)
- **A scroll's answer on the inventory screen.** What the item box says (YOU LEARN THE SPELL, YOU
  ALREADY KNOW THIS SPELL, YOU CAN NOT READ THE SCROLL, THAT IS NOT A SHINOBI SPELL, CANNOT LEARN
  FROM THIS ITEM, the tome's) was never seen: the game writes it to the line under the paper doll
  while the box runs, and nothing written then reaches the screen. DSCLOG keeps the text and for 5
  seconds puts it on that line, and tells the game's mouse handler the pointer moved, so it shows
  with the mouse still; as the game's own messages there, it stays till the pointer is on something
  else. (`BOX_SAID`, `LINE_SAID`, `LINE_CLEARED`, `BOX_NUDGE`.)

**Changed**
- **A backstab's dice log line shows the sum:** `+2 backstab (the dice 1 x3 = 3)`, not `(the dice
  x3)`. The die's 1 is already in the line, so the backstab adds 2 more.
- **The helper's big buffers moved to the HMA:** the dice log's ring, the combat log panel's
  picture, the shadows' cache, the text buffer, the shadows' spans and the dust's last places
  (57,800 bytes), with A20 on, else a block of their own. Upper memory has about 57.8 KB free in one
  piece, from 0.5 KB. (DSCLOG's `FAR_INIT`, `FAR_SEG`; `textlog.TBUF_SEG`,
  `combatlog.TSR_PANEL_OFF`. Seen in DOSBox: the dice log, the text log, the panel, shadows, dust
  and the arena's fight, with and without `UMBPLUS.COM`.)

**Fixed**
- **A Shinobi couldn't learn from a scroll:** clicking the spell's picture in the scroll's box did
  nothing. The game makes the picture a button only for a class the item type allows, and the scroll
  type allows wizards only. (`SCROLL_USE` passes a scroll for a Shinobi.)
- **Spells cast by weapons were at caster level 6** whoever struck. A Spellarcher's spell arrows now
  go at the archer's preserver level (a 2nd-level archer's Shocking Grasp did 1d8+6); a weapon's own
  spell stays at 6. (`ARROW_LEVEL`.)
- **A backstab multiplied the round's second attack too** (an off-hand one after a miss): the game
  multiplies while fewer than two attacks are made. With the dice-only rule, only the first.
- **Immunity in the dice log.** The HP line matched hits to the HP lost from the first, so a hit the
  creature was immune to (a slime and a club) was counted and the next one dropped. The hits that
  sum to the loss are taken, and each passed-over hit gets "takes none of the N damage: <reason>".
  (`_hits_matching`.)
- Smaller: "Bracers/Defense+4" ran past the item box (now `Bracers/Defns`); a preserver's scroll
  line in the dice log showed the last Shinobi's read-languages roll, left in the header
  (`INT_LEARN` clears `LEARN_READ` now); the cooked vulture used on a party member no longer says it
  is tough and bland (`vulture.use` removed; eating it is the game's, with the meal's rest from the
  Loader as before).

**Docs**
- The Loader README's In the game has a section for the Effects screen (kits, a Shinobi's read
  languages, charges under the pointer, the click fix) with `effects-charges.png`, and Names over
  figures a picture of a charge label beside a "Miss" (`floating-charges.png`). FEATURES gives M its
  own Controls section; the guide's screens table gains the scroll's answer.

## Pull request #61 ([merged 2026-10-25](https://github.com/daaki85/darksun-obsidian-edition/pull/61))

**Release**
- **Obsidian Edition 2.8.0**: the version is 2.8.0, with its notes in `release-notes/v2.8.0.md`, for
  this pull request and #60.

**New**
- **The glow in each item's own colour.** The game's palette cycles four runs on the map (1-5 green,
  6-10 violet, 11-15 the water's blue, 240-248 fire), the same in every area's palette but for a
  step.
- **A cloak from the front no longer looks held.** The cloak is fitted from the human woman's, which
  swings out to one side as she walks; on the elves and the half-elf man that showed as a dark panel
  by one hand.
- **The glow on every magic item a figure shows:** armour (in place of picking its light shades,
  which the human and half-elf women's dark clothes hadn't), bracers, cloaks, helms, boots and
  belts. After a magic piece is drawn, every fifth pixel of those it changed, on a diagonal, is
  marked in `GLINT` (every ninth on a piece as large as a cloak; at least every other on a small
  one). (`spritegear.sparkle`.)
- **The pointer at the desktop's speed in a window.** Captured, DOSBox 0.74 moves the driver's
  pointer a game pixel for each desktop pixel the mouse moves, three screen pixels in the usual
  window: too fast and coarse for placing items.
- **Magic weapons, shields and armour glow on figures:** a weapon or shield with a plus or a power,
  and magic armour (Kreenfang and the Flame Blade keep their own colours). (`sprites.worn`,
  `spritegear.MAGIC`, `MAGIC_ARMOUR`.)
- **Shadows kept for figures whose pictures the game lets go of.** In the arena's fight every figure
  but one had its picture out of the game's cache as the floor was drawn, so no shadow was drawn
  (`SHADOW_OF` won't load one mid-drawing).
- **The game's music buffer in upper memory: 12 KB more of the 640 KB.** A research build of the
  helper logged the far heap's calls: 134 KB of it is taken before the main menu and kept, never
  freed or resized through a load, an area change and a fight (music 12,001 bytes, sound effects
  24,001, tables).
- **28 KB more upper memory.** DOSBox 0.74 starts its upper memory block at D000h, but C800h-CFFFh
  is RAM too, and DOSBox's own tables use only its start.

**Changed**
- **Removed, to free the helper's memory: scrolling by holding the right button.** The right button
  goes straight to the game again; the wheel's drag stays. (`MOUSE_EVENT`; `SCROLL_RIGHT`,
  `DRAG_START` gone; `scrolling.DRAG_MIDDLE` the only bit.)
- **Removed: rings under all the enemies.** Only the enemy chosen with Tab gets one (or none), and
  an older `"rings": "all"` reads as the chosen one's. (`rings.ring_table`.)
- **Removed: the combat log strip below the map.** The panel over the map (L) is as it was.
  (`PROBE_STRIP`, `PROBE_PALETTE`, `PROBE_COLOURS`, `STRIP_*`, gamepatch's eight `STRIP` patches and
  `combatlog.STRIP` gone.)

**Fixed**
- **A shorter pause after picking up or putting down an item.** The pointer stood still 56-103 ms
  (85 on average, in the user's save, at 20,000 cycles) while the game redrew the inventory: its
  mouse handler only queues the moves, and the pointer is drawn again once the redraw is done.
- **A shorter wait for the Loader after picking up or putting down an item.** Each time an item
  moves on the inventory screen the helper has the game stand still until the Loader brings the
  THAC0, saves and thief skills up to date, so an item just put on counts. (`STATS_SYNC`.)
- **The Loader's own magic items glowed blue on figures.** Each item's object and icon were looked
  up in the game's SEGOBJEX.GFF, which has none of the Loader's items (the Hayneedle, Kreenfang,
  Thornwall, Inixhide, the Ashen Robe...), so they fell back to blue whatever their icon.
  (`sprites.item_glow`.)
- **No thief skill above 95.** With **Thief skills from AD&D's table** a skill had no ceiling: a
  13th-level thief with DEX 24 showed move silently 121 and pick pockets 117.
- **The pointer put back where it was as screens changed,** not in the middle. A video mode set
  (each scene's start, the menus, loading a save) leaves the pointer at the right edge, and it was
  put in the middle; it goes now where it was last seen. (`MOUSE_SET`, `CINE_MOUSE`, `CINE_WHERE`,
  `MP_X`, `MP_Y`, `MOUSE_EVENT`.)
- **"Regains 1 HP from Fire attack."** A hit point regenerated (CON 20 or more) just after a spell
  or attack was put down to it, as the spell's healing was tested first; regeneration is tested
  first now.
- **"Script: a creature changes sides" in runs of a dozen** as a fight's scripts set up: request 18
  shows only with "Show unlabelled rolls". (`REQUESTS_SHOWN`.)
- **An archer's pointer with shots left.** The game marks a combatant's attacks as all made once
  they are, but the pointer's missile test refused any count but none, so after a shot that killed
  it showed "can't shoot", though a click still shot.
- **Cermak's Arcanist slot at the start of a new game.** The game fills the party's spell slots
  before the Loader makes Cermak an Arcanist, so the USE screen showed WIZ 1/2 until his first rest.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #60 ([merged 2026-10-24](https://github.com/daaki85/darksun-obsidian-edition/pull/60))

**New**
- **A pointer in scenes, and a click skips one.** The intro, its logos and the game's other scenes
  had no pointer, and only a key skipped them. DSCLOG draws the game's own arrow there, as the
  scenes' unchained VGA mode is one the mouse driver's pointer can't draw in: ICON 6001 and its
  colours, read from the player's game by the Loader into `dos\POINTER.BIN` (without it a plain
  arrow of DSCLOG's own), each colour as the scene palette's nearest. A button pressed ends the
  scene as a key does. (Options: "A pointer in the intro and the game's other scenes", on;
  `scene_pointer`. `scenepointer.py`, DSCLOG's `CINE_STEP`, `CINE_END`; DEVELOPMENT-SCREENS § The
  pointer in scenes, and where it starts.)
- **The pointer starts in the middle and moves as far up and down as across.** The game's ranges
  left the pointer at the right edge after a video mode set, and it is put in the middle there; the
  driver's 16 mickeys a pixel up and down are made 8, as across, from the game's start. (Options:
  "The pointer starts in the middle of the screen", on; `mouse_start`. `MOUSE_SET`, `MOUSE_INIT`.)

**Changed**
- **The freeze report keeps 16 records, every 32nd timer strike** (were 32, every 16th; the same 4
  seconds), to make room in upper memory for the above.

**Docs**
- The guide's tables list the scenes' pointer and the pointer's start and speed; the README's
  troubleshooting says how to let go of the mouse (Ctrl+F10) and the freeze report's 4 samples a
  second; the patch notes' pointer line reads better; a picture of the pointer in scenes in
  FEATURES.
- **Organisation and trims.** The Loader README gathers Troubleshooting, Known issues, the reports
  and Reporting a problem under **When something goes wrong**; its How the game works and Item
  tables indexes become one **More pages** list; the character card's contents move into **The
  Characters tab**; the game window's command-line options and the practice program move to
  DEVELOPMENT.md; a shorter Requirements, game window and item-report text. FEATURES follows the
  Options tab's order, with the game's bugs fixed last. The guide's quality-of-life table is grouped
  (screens, controls, saves, running the game), and its intro points to the features page for the
  rules.
- **A line-by-line audit of every page.** Corrected: the guide's backstab multipliers (×4 at 9-12,
  ×5 at 13, as the game has them), DEVELOPMENT's room in upper memory (1 paragraph spare, not 54),
  its patch count (some 320), the helper's added item types (30), Negative Plane Protection's record
  (211) and the timer's rate (about 120 a second); the switch the 6th-level priest spells come with
  named everywhere (**New wizard spells**, with AD&D's class tables). Repeats removed (the README's
  save note, its window size in the start steps, the combat log's EMS aside, the guide's note on the
  game's own party's spells); "started from the Loader" and "pointer" used throughout; unclear
  sentences rewritten (preservers' starting spells, the pens' new people, the Items and Kits
  headers); DEVELOPMENT's contents list the pointer section; every page's prose wrapped at 80
  columns.

## Pull request #59 ([merged 2026-10-24](https://github.com/daaki85/darksun-obsidian-edition/pull/59))

**Release**
- **Obsidian Edition 2.7.2**: the version is 2.7.2, with its notes in `release-notes/v2.7.2.md`,
  listed on the front page with the others.

DSCLOG in upper memory: 54 paragraphs spare (none before).

**Fixed**
- **Sunstroke ends the caster's turn.** Its record kept Hold Person's aim (several targets: after
  the first the spell stayed armed and the turn went on); it has Slay Living's now (one creature),
  as meant. (Seen in DOSBox: Grog's Sunstroke on Scar, and the turn passed straight on.)
- **Wall of Thorns counts a monster's armour.** For anyone but a party member the game had seen
  attacked, it took the sheet's base AC, 10 for an armed man, as the game adds armour in an AC
  routine the damage's code can't call. It now counts as that routine does: each worn item's plus
  and its type's AC, a fifth of a gladiator's level and the DEX adjustment; spells' AC still not.
  The ring is 64 entries (65 before) to make room. (DSCLOG's `THORNS_AC`. Seen in DOSBox: Scar, in
  leather arm and chest armour with DEX 17, took 8 + AC 5 = 13, not 18; his henchmen 18 (AC 10); the
  party their own ACs.)
- **The Look box's AC counts a monster's armour.** Before anything had attacked a monster, the Look
  box (and its `Look:` line) gave its sheet's base AC, as Wall of Thorns did. It now counts as the
  game does. (`GameData.counted_ac`, the Loader's twin of `THORNS_AC`; `_worn`. Seen in DOSBox:
  Scar's Look box AC 5 at the fight's start, where it said 10; his henchmen 10.)
- **Room in upper memory.** DSCLOG's shadow table is a bit for each of the game's 520 things, not a
  byte, and its 46 extra names are kept in 16 bytes each (15 letters at most), padded to the game's
  25 as they are copied: 455 and 414 bytes saved. (`SHADOW_TAB`, `shadows.casting`, `EXTRA_NAMES`,
  `NAME_KEPT`, `PROBE_NAMES_FILL`. Seen in DOSBox: all 46 names in the game's table as before, and
  the figures' shadows drawn.)
- **Heartseeker's and Slay Living's descriptions.** A creature that saves still takes half of 4d8, 2
  to 16: Heartseeker's said only that it slays, and Slay Living's said 3 to 17 (the book's 2d8+1,
  not what the game rolls). (`spelltexts.py`, SPIN 209 and 137; the spellbook line, FEATURES, the
  guide and the patch notes say so.)

**Docs**
- **Documentation review.** The Loader README lists the Options tab's Wake of the Ravager section;
  DEVELOPMENT describes how `THORNS_AC` now counts a monster's AC; How the game works keeps the
  manual's column the manual's (Slay Living); two sentences in the patch notes untangled. Two
  screenshots retaken: `options.png` (with the Wake of the Ravager section) and Heartseeker's tile
  in `new-priest-spells.png` (its new description).

## Pull request #58 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/58))

**Release**
- **Obsidian Edition 2.7.1** (pull request #57): the version is 2.7.1, with its notes in
  `release-notes/v2.7.1.md`, listed on the front page with the others.

## Pull request #57 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/57))

**New**
- **Wake of the Ravager found in more places, or chosen:** any folder beside Shattered Lands (GOG
  Galaxy installs them as `Dark Sun` and `Dark Sun 2`, so a Galaxy install was never found), GOG's
  usual folders on any drive, and a folder inside each. The Options tab's new **Wake of the
  Ravager** section says where it was found, or that it wasn't, and **Choose its folder...** keeps
  one installed anywhere else. Before, the Loader looked beside Shattered Lands only and said
  nothing, so a player whose copy was elsewhere saw the Loader's own icons without knowing why. GOG
  Galaxy's `Dark Sun` is among the places the Loader looks for Shattered Lands too.
  (`wotrart.find_resources`, `wotr_dir`, `launch.GOG_SUBDIRS`.)

**Changed**
- **Monsters' powers named in the dice log** by what their records do: the effect a power puts on
  (`Paralysing attack`, `Disease attack`, `Entangling attack`, `Poison attack`), else its damage's
  kind (`Fire attack (6d6 fire)`), else its number as before. The dice rolled before the save
  against one that puts on an effect are its duration, and the log says so (`Paralysing attack:
  lasts 7 rounds unless saved against (2d4 = [4 + 3] = 7)`; the Red Slaad's 182 was `special attack
  182: 2d4 = [4 + 3] = 7`). (`game._power_name`, `POWER_EFFECT_NAMES`.)

**Docs**
- Wake of the Ravager described as what it is for nearly every player, the game GOG sells with
  Shattered Lands, rather than an optional extra (the Loader README's requirements, FEATURES, the
  patch notes); the patch notes list this pull request's changes as coming after 2.7.0.

## Pull request #56 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/56))

**Release**
- **Obsidian Edition 2.7.0** (pull requests #55 and #56): the version is 2.7.0, with its notes in
  `release-notes/v2.7.0.md`, listed on the front page with the others.

**Changed**
- **The 6th-level priest spells' descriptions in the game's own style:** the name, then a terse line
  with damage as ranges ("Inflicts 8 to 64 pts of damage"), and no level or sphere, which none of
  the game's own descriptions give. Harm's text no longer says the target is diseased: the Diseased
  effect here lowers nothing, it only keeps a STR lowered by something else from coming back (see
  Cause Disease in HOW-THE-GAME-WORKS); the docs say so too. The priest spells screenshot retaken.
  (`spelltexts.py`.)

**Docs**
- A fourth review. The root README says what the repository has beyond 2.6.0 (the patch notes
  already did). FEATURES moves Harm's Diseased note out of its table row into the spell's notes,
  linked to Cause Disease. DEVELOPMENT gives the 6th-level priest spells' description chunks (SPIN
  203-211), the game's description style and the box's size. The patch notes' memory figure matches
  the latest measure (85 KB). Links, anchors and every screenshot checked; none out of date.

## Pull request #55 ([merged 2026-10-23](https://github.com/daaki85/darksun-obsidian-edition/pull/55))

**New**
- **6th-level priest spells** (with **New wizard spells**, slots with AD&D's tables): Heal, Harm,
  Blade Barrier, Wall of Thorns and Sunstroke (cosmos: druids and Healer clerics), Fire Seeds
  (fire), Heartseeker (earth, water), Water of Life (water) and Whirlwind (air), spells 202-210.
  Each is built on a record the game already casts (Cure and Cause Critical Wounds, the priest's
  Wall of Fire, Hold Person, Flame Strike, Slay Living, Lend Health) with its own changes.
  (`NS_PATCH`.)
- **The 6th-level priest spells closer to the books and Wake of the Ravager.** Wall of Thorns does
  8 + the creature's AC (at least 1), not 1d10 + 8; a monster's AC is its sheet's, a party member's
  as the game last worked it out, and the dice log shows it. (`THORNS_AC`, `PROBE_AC`, `AC_SEEN`.)
- **The ground pictures checked live:** the blades and the thorns standing as walls, Fire Seeds'
  fireball, and Whirlwind's entry holding the dust (8403) after its cast, the other entries back to
  the game's.
- **Spheres:** Blade Barrier is air's, Wall of Thorns earth's and Sunstroke fire's, not the
  cosmos's; the cosmos keeps Heal and Harm. (`P6_MASKS`, `game.PRIEST6_MASKS`: `AIR_MASK`,
  `EARTH_MASK`, `FIRE_MASK`.)
- **Whirlwind lasts and sweeps:** built on Stinking Cloud (a lasting ground entry whose spell acts
  each round on those in it) with Sand Storm's picture: 1d4 rounds and 1 more from 7th level, 2d8
  crushing each round, a save vs spell for half. (`ns_templates`, `AREA_NEW 8`.)
- **Whirlwind's funnel, drawn once, blocking sight:** its own picture, a funnel of dust in ground
  ellipses, object 8433 in the Loader's SEGOBJEX copy. (`whirlart.py`, `NS_SETUP`.)
- **Sunstroke's heat:** 1d4 of fire at the start of each round on a creature Sunstroke holds.
- **Backstabs multiply the weapon's dice only:** a hit's dice are added again for each time past the
  first, in place of the game multiplying the whole damage by x2-x5. (Options: "A backstab
  multiplies the weapon's dice only", on; `backstab_dice`. `RULE_BACKSTAB`, DSCLOG's
  `RULE_HI_BACKSTAB`, `STAB_ROLL`, `STAB_TIMES`.)
- **Acid Arrow burns each round.** In the game its acid never burned after the hit: the routine
  spending an effect's charges was called for Acid only on chance events, and Acid Arrow's time was
  a timer on the game clock that only ended it, with no charges to spend.
- **Names over figures: no leftover sliver.** When a label went away the game's redraw of its
  rectangle drew only whole bytes of the VGA planes inside it, so a label starting mid-byte left its
  first columns on the map (a "[" left on the sand after Prayer's cloud). The rectangle is widened
  to whole 4-pixel columns. (`LABEL_ERASE`. Seen in DOSBox: Prayer cast in the Scar fight, and
  nothing left after it.)
- **Walls of their own.** Blade Barrier, Wall of Thorns, Fire Seeds and Whirlwind each have an entry
  of their own in the table of ground pictures, so walls no longer share Wall of Fire's (a Wall of
  Fire cast while a Blade Barrier stood made both burn as Wall of Fire).
- **Pictures on the ground for the 6th-level priest spells,** Wake of the Ravager's: Blade Barrier's
  circling blades and Wall of Thorns' thorns (its objects 8432 and 8425, added to the Loader's
  SEGOBJEX copy and recoloured; without it the fire wall tinted grey or dark brown), Fire Seeds'
  fireball (8405) and Whirlwind's Sand Storm dust (8403). (`wotrart.area_chunks`.)
- **Names over figures.** A spell's name floats over its caster for 1.5 seconds as it is cast (any
  cast: the party's, the monsters', a weapon's on a hit), and "Miss" over the target of an attack
  that missed, in the game's font with a dark edge; at most two at once.
- **Spellarcher spell arrows.** Outside a fight, a Spellarcher's USE screen has a button for each
  touch spell it knows (Burning, Chill, Shocking and Vampiric Arrows) in the row of class abilities,
  the first where a priest's Turn Undead is, the rest beside it.
- **Three new magic items** (with New items on), each with its own icon: the **Girdle of Back
  Defense** (no enemy gets the bonus for attacking its wearer from behind, nor a backstab; the Troop
  Leader carries it), the **Golden Girdle of Urnst** (AC 3 better against long and short swords;
  Wyrmias) and the **Amulet of Magic Resistance** (15% magic resistance; it never shatters; sold by
  Kel).
- **The Crusader and Mind Warrior have expertise in one melee weapon spec of their choice** (with
  weapon specialization), as the Battle Mage has: 3/2 attacks a round, 2 from 7th level, picked on
  the weapon window after DONE.
- **The dice log names a refused cast's reason** (`can't cast Fireball there: no line of sight`;
  DSCLOG's `AIM_SITE`) **and the scripts' requests** (`Script: random monsters come`; `REQ_SITE`,
  all 20 named, from the yuan-ti project's notes on the game).
- **The Wanderer halves fire and cold spells' damage,** as Resist Fire and Resist Cold do (it had
  their saves only), at the game's own test of what a creature is guarded from; the log says
  `(halved: Wanderer)`. (DSCLOG's `WANDER_DMG`.)
- **The Myrmidon's initiative is 2 worse,** a second drawback beside its −4 against charms; the
  log's initiative line names it. (`PROBE_INIT`.)
- **Cleric spells against the manual.** HOW-THE-GAME-WORKS has a table of every cleric spell: the
  manual's text, what the game's records and code do, and what the log shows.
- **The log names a protection that halves a spell's damage.** The game halves a spell that is all
  fire under Resist Fire or Protection from Fire, all cold under Resist Cold, all electricity under
  Protection from Lightning, fire or cold under Fire Shield: `takes 9 from Fireball (halved: Prot
  Fire)`.
- **A party member's ability scores changing** get a line once the change holds: `Cilla's STR 12 ->
  16` (Strength, Remove Curse, Raise Dead's CON, the Tome).
- **Psionic powers checked against the manual.** A table in How the game works, power by power: the
  manual's text, what the game's code does (Detonate hits only its target, no save; Cell Adjustment
  heals 2 and cures nothing; Biofeedback gives AC -1 and takes no damage off; Inertial Barrier makes
  missile attacks miss and does nothing else; Psionic Blast takes real HP down to a fifth; Control
  Body and the dominations are a charm; Mass Domination's record targets one creature) and what the
  log shows.
- **The psionic defence in the dice log.** An attack mode's target rolls 1 to its defence twice,
  each over the attacker's power check d20, to resist; the log skipped both rolls: `Gerakis's
  psionic defence: d6 = 5 and 6, both need over 4 (the attacker's power check d20) -> resisted`.
- **What more powers do, in the log's effect lines:** Inertial Barrier (missile attacks miss),
  Energy Containment (no damage from fire, cold, electricity or magic alone), Synaptic Static,
  Enhanced Strength (STR 24, read from the game's stats code), Adrenalin Control (STR + 1d6) and
  Share Strength's lender (STR - twice the amount); Detonate's 1d10 named "Detonate's blast".
- **Detonate's blast on an item in the dice log.** The power (a daggoran's too) destroys the
  target's worn item with the lowest item +10h (under 6) on a 1d20 under 15 less its plus (one of a
  stack), and nothing showed it. (DEVELOPMENT-SCREENS § Detonate's blast on an item.)
- **Find in the dice log and the dialogue.** A box above each (Ctrl+F): every match (any case)
  highlighted, the one shown in amber with `n of N`, Enter / **Next** and Shift+Enter / **Previous**
  round the end, Escape to clear; details hidden aren't searched, and the log stops following its
  newest line while a match is shown. (`viewer.Viewer._find_bar`, `palette.TEXT_PAIRS`. Tests:
  `tests/test_find.py`.)
- **The psionic power check in the dice log.** `Zulak uses Graft Weapon: power check d20 = 14, needs
  11 or less -> it fails`, with the score's parts (`16 CON - 5 Graft Weapon`), and the Synaptic
  Static contest when someone else keeps it up.

**Changed**
- **Axes and maces on figures look like the game's own:** the axe was a thin stick in its metal with
  a hollow hook for a head (it read as a fork), the mace the same with a thin diamond.
- **Level cap by XP.** The levels-up-to-10 rule is now an XP cap: a class goes up while its next
  level needs no more than 749,999 XP, the whole of it for a character of one class, an even share
  for each class of a multiclass character (as the game shares out XP), and for a human who changed
  class the cap less what its old classes' levels needed (the game starts the new class at 0).
- **Weapons spells make count for weapon specialization,** for its attacks, to-hit and damage alone.
  The Flame Blade counts as a long sword (AD&D's scimitar, which Athas hasn't), Shillelagh as a
  club, Spiritual Hammer as a mace (the war hammer's nearest). (DSCLOG's `SPEC_KIND`,
  `specialize.spec_kind_of`.)

**Fixed**
- **Whirlwind lasts a round a caster level,** as AD&D has it (11 rounds or more for a priest who can
  cast it), not Stinking Cloud's shape of 1d4 + 1 for each 7 levels. (`NS_PATCH`.)
- **Three of the game's script bugs mended,** always on, in the Loader's copy of GPLDATA.GFF: each
  re-points one trigger or call to the handler it was meant to have, applied only where the script
  holds the expected bytes. (`scriptfixes.py`; DEVELOPMENT-CONTENT § The game's script bugs.)
- **The Spells tab's 6th-level priest spells** were described from the records they are built on, so
  Harm read as 3d8+3 draining, Heartseeker as 4d8 halved by a save, Wall of Thorns as 1d10+8, Heal
  and Water of Life as next to nothing, Sunstroke without its heat and Whirlwind as "can't move".
- **The USE screen's spell slots line ran off its panel** with a 6th spell level: the panel shows
  the slots of the level and list on show only (`SPELLS LEFT`, then e.g. `PRI 2/1`: `WIZ` on MAGE,
  `PRI` on CLERIC, none on PSIONIC).
- **Spell arrows fade at the game's own rest.** They faded only at a script's rest request and the
  vulture meal; camping at a fire ring runs the game's rest routine without one.
- **Spell arrows (and Pick Pockets, and the vulture meal) work with the party spread out.** The
  Loader's fight check read a flag of the game's that stays up while the party walks uncollapsed
  with no one to fight, so it answered "can't be made in a fight".
- **The pointer on a spell arrow button lights that button.** Turn Undead's handler, which the
  buttons beside it share, lit and unlit the frame at Turn Undead's place, so the Vampiric Arrows
  button lit the Burning Arrows one; the button's own place lights now, as its press already did.
- **Every magic item of the Loader's shines.** The game shines a magic item by cycling palette
  colours (11-15, the water's, and 224-255, fire's among them), so icons tinted in colours it
  doesn't cycle stood still: the Chill, Shocking and Vampiric Arrows, Shadowseeker, the Cloak of
  Protection +1, Pehtucl's ring, the Girdle of Back Defense, the Amulet of Magic Resistance, the
  Veiled Robe, the Cloak and Boots of Elvenkind and the Golden Girdle of Urnst.
- **A Fireball no longer floods the dice log.** The filter for `random(low, high)`, kept for psionic
  ranges, also recorded the eleven picture-point calls a spell burst makes, so a Fireball filled the
  ring ("148 rolls came too fast to record").
- **More room in the helper's upper memory:** 3.8 KB of the upper memory block spare rather than 224
  bytes, for features to come. Its text buffer is 2 KB, not 4 (251 bytes came between two of the
  Loader's reads at most), and the descriptions of the new spells, Pick Pockets and the spell arrows
  are SPIN chunks in the Loader's copy of RESOURCE.GFF, not the helper's text. (`spelltexts.py`,
  `PROBE_CHUNK_ID`.)
- **An item the game destroys gets its crash-log report.** The game frees a destroyed item
  (Detonate's blast, acid, a script) by zeroing only the first word of its record and linking it
  into the free list: its type and name stay.
- **A party's thief skill roll goes to its best member.** Where the game asks the whole party (a
  trap's find/remove traps, all 50 trap triggers with the arena prisoner's among them, and hear
  noise by the wagon), its pick was to keep the highest chance but kept the lower of a best starting
  at 0, so the first party member always rolled.
- **Random monsters come in the right numbers and can't crash the game.** The scripts' request for
  random monsters (8; scripts 99 and 106) sends 2 x the party's strength / the monster's, 1 to 6,
  but took the strength of the slot after the one picked: from the next region's record after the
  tenth, and 0 after the last in regions 6, 13, 14, 27, 39, 40, 44 and 255, a division by 0 that
  ends the game ("Divide error").
- **A likely cause of figures vanishing and then a freeze.** A freeze report (2.6.0, 49 minutes into
  an arena trip) had the game's picture row decoder unpacking a figure's picture from garbage: never
  meeting the row's end, it copied on from its 5,408-byte buffer over the code after it, itself
  included, and the game's data segment was then overwritten by its own stack.
- **Magic items shine in a shop.** The palette's colour cycles turn only in the map's main loop,
  when the timer asks; a shop, opened from a conversation, runs its own event loop and waits in the
  game's wait for an event, and neither turned them, so its items stood still.
- **Freeze reports with the game's memory overwritten.** The report found DSCLOG only through the
  dice log, which had lost the game with its data segment. It now finds DSCLOG by its signature and
  the game's load segment from its DOS block, so where the game was still shows.
  (`freeze.find_header`, `load_from_block`.)

**Docs**
- **Reviews, pictures and the since-2.6.0 list:** the patch notes' list of what comes after 2.6.0
  brought up to date; the XP cap, the 6th-level spells and the new switches in the Loader README,
  the guide's Options summary and the dice log table; Wake of the Ravager as an optional install; a
  link and anchor check over every page (none broken, no picture unused).
- A review of every page.
- A second review: the patch notes say which of their changes come with the next release, not 2.6.0,
  and name the Battle Mage's, Crusader's and Mind Warrior's weapon expertise (the release steps now
  drop that line); the README's known issues add the vanishing figures and freeze, and lose a
  class-letter table that repeated its sentence; spell arrows left on the ground fade at the first
  rest after they're picked up (KITS, and the guide, whose paragraph is rewritten).

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #54 ([merged 2026-10-21](https://github.com/daaki85/darksun-obsidian-edition/pull/54))

**Release**
- **Obsidian Edition 2.6.0** (pull requests #52 and #53): the version is 2.6.0, with its notes in
  `release-notes/v2.6.0.md`, listed on the front page with the others.

## Pull request #53 ([merged 2026-10-21](https://github.com/daaki85/darksun-obsidian-edition/pull/53))

**New**
- **A warning when the game's memory runs low.** With the map open, below 24 KB spare the dice log
  says so and to save and restart soon (a new start has it all back); once, then again only after it
  has recovered. If upper memory had no room for the overlay buffer (another DOSBox, other settings)
  the dice log says that too, and crash reports say where the buffer is. The helper's build fails if
  what it puts in upper memory outgrows it, and its signature is now `DSCLOGva`. (`UMB_NEED`, also
  checked by a test.)
- **Enlarge shows in the damage line.** A melee hit by someone under Enlarge reads e.g. `(1d8 = [5]
  +12 STR 24) x140% Enlarge (level 4)`, as the game works it out: the dice, weapon and STR bonus
  together, times 100% + 10% a level, rounded down, before a backstab's multiplier. The level is the
  caster's level for the spell (as Dispel Magic weighs it), each Enlarge on the attacker added up.
  Missiles don't get it. (DEVELOPMENT-RULES § Enlarge's dice. Tests: `test_dicelog.py`.)
- **Crash reports tell the game's memory.** "Out of memory in OEOpenGraph" is the game failing to
  open the map's view again, which needs one block of 60,000 bytes from the game's heap each time.
  On the map with a long game's save there are about 53 KB of DOS memory to spare (the unmodded
  game: 57 KB). Making characters over and over uses none of it (35 made in a row). What used it up
  in a 97-minute game isn't known yet, so the Loader reads the heap every few seconds, and a crash
  report gives the last reading and the session's lowest. (`heapcheck.py`.)

**Changed**
- **The arena's count of fights shows by itself,** with no button: between fights in the slave pens
  and the arena (regions 29h and 2Ah) the combat log panel's header says `Arena fights: N` (docked
  or expanded); in a fight it says the round, and anywhere else (the party escaped) it's gone. The
  header's **A** is dropped, as the game's own A key turns animations on and off, so a button A read
  as a key it wasn't. This replaces #52's A button; `combat_log_arena` is no longer saved.
  (`combatlog.ARENA_REGIONS`.)

**Fixed**
- **The game ran out of memory in long sessions** ("Out of memory in OEOpenGraph"). Each time the
  map's view opens it needs 60,000 bytes in one piece from the game's heap, and with the map open
  only about 53 KB were left over. The game's largest block for good, the overlay manager's buffer
  (32,992 bytes), is now in upper memory, and DSCLOG lays out its own blocks so the room is in one
  piece. With the map open about 86 KB are now left over (the unmodded game: 57 KB). Without upper
  memory the game takes it from its heap as before. (DSCLOG's `PROBE_OVR_BUF`, the patch
  `overlay_umb`. Tests: `test_dsclog.py`.)
- **Dinos's talk lost its upper box after the vulture meal:** the XP's words go to the narration
  window, which takes the portrait and his words away, and his menu came back under an empty screen.
  After the XP his script sets his portrait again and he says a line before the menu.
  (`pensasks.AFTER_MEAL`. Tests: `test_pensasks.py`.)
- **The Characters tab showed noise for items before the game had its item tables** (at the main
  menu or creating characters: "Wooden GF╨╢...", "Attacks: 120 a round with item 2"). Items count
  only when every name reads as plain text; until then a card shows no equipment and the sheet's
  attacks, and an item's name is never noise. (`GameData.items_readable`, `game.plain_name`,
  `item_name`. Tests: `test_equipment.py`, `test_names.py`.)
- **An item couldn't be put down on another in a character's pack** (the swap was refused, for any
  items and anyone's pack; the original game swaps them). The cause was an object numbered 2563 in
  the Loader's copy of SEGOBJEX.GFF, the slave pens' weapon rack with Thornwall on it, numbered so
  since 1.2.0: with any object of that number in the file, the game refuses the swap. The rack is
  now 2599, and 2563 is never used. In a save that has already been to the pens, the game leaves the
  old rack off the map; renumbering it in the save doesn't bring it back, as something else in the
  save still names 2563. (`worldgear.PENS_RACK_OBJECT`, `NOT_AN_OBJECT`. Tests:
  `test_worldgear.py`.)
- **The Ashen Robe (and the Veiled Robe) gave no AC under the Armor spell.** Worn on the chest, the
  robe's plus went into the game's armour value, and the Armor spell puts its 6 in that value's
  place, so the robe added nothing. Its plus now counts with the AC's other bonuses, as a ring's,
  still only without armour on the arms, legs or head. (DSCLOG's `PROBE_RING_AC`;
  DEVELOPMENT-CONTENT § Robes. Seen in a save: AC 0 with the robe off, -1 with it on, the spell and
  a shield on. Tests: `RobeTests` in `test_dsclog.py`.)
- **The Trustee stood still for good after a load** (the game's own way too). His rounds are his "no
  orders" script, which runs only while he has no order, and a walk is an order that ends when he
  gets there. A save made while he walked keeps the order but not the way, so once loaded he stood
  with it forever, and after a talk he was busy for good. The Loader takes such an order back
  (anyone with a no-orders script, standing still with a walk order for 30 game seconds, out of
  fights), and his script sends him on; the dice log says "Trustee walks on". (`stuckwalk.py`. In
  the save it was found in, he walked his rounds again about 20 s after loading. Tests:
  `test_stuckwalk.py`.)

## Pull request #52 ([merged 2026-10-20](https://github.com/daaki85/darksun-obsidian-edition/pull/52))

**New**
- **The arena's count of fights, on the combat log panel's A.** A button left of the header's L puts
  "Arena fights: N" in the header instead of the round (lit while on, saved as `combat_log_arena`;
  not in the strip, which has no buttons). N is the game's own count, its global number 12, which
  script 3 adds one to each time the party leaves the arena after a call, however many waves came;
  the announcer's speech changes with it (for the first five fights, the 1000th and the 5000th).
  (`GameData.number`, `game.NUMBERS_PTR`, `ARENA_FIGHTS`, `combatlog.arena_rect`, `arena_line`.)

**Changed**
- **The Healer has the sphere of the cosmos, and is a water cleric's only** (with kits on). The
  cosmos's spells are those every druid casts and no cleric (the game gives Cure Serious and
  Critical Wounds, Raise Dead, Neutralize Poison and the other common 4th and 5th-level priest
  spells to druids alone, so a Healer's extra healing on the two cures never came into play). A
  Healer knows them from the start and casts them at its cleric level. On the KIT page its row is
  greyed unless WATER is the sphere marked, the sphere stays while the kit is taken, and taking
  WATER back takes the Healer back too, as choosing another class does. After DUAL the kit menu
  offers it to a water cleric only. A Healer from an earlier version keeps its sphere, and the
  Loader marks its element's cosmos spells known when the game is loaded (the game marks a priest's
  spells only when the character is made or changes class), with a line in the dice log. KITS.md,
  the guide and the patch notes say so. (DSCLOG's `HEALER_COSMOS`, `HEALER_BARRED`, `EL_CLICK`,
  `DK_BANNED`; `kits.spell_spheres`, `kits.dual_kit_banned`, `kits.cosmos_spells`. Tests: the water
  cleric's DUAL menu, `cosmos_spells`.)

**Fixed**
- **More of the game's own bugs,** whatever the Options (from yuan-ti's notes, each checked in the
  code): Negative Plane Protection saved as against Vampiric Touch, which allows no save, so it
  never worked (`NS_NPP`); Cloak of Bravery's +4 against fear asked for a mark no spell had (now on
  the fear spells, Spook's record too); Absorb Disease gave 1d6 STR too; Bless and Aid's check for
  an enemy beside an ally measured from (x, x); a berserk or confused member could end it on the
  monsters' side (`NS_SIDE`); the fire elementals' resistances were swapped; the computer cast its
  walls as a single point (`NS_WALL`). The dice log's saves show Cloak of Bravery's +4 and name
  Negative Plane Protection's.
- **The Loader's changes to the game's item lists could land mid-load.** The game gives every item a
  new number as an area loads, and a change made across that, from numbers read before it, could cut
  an item out of its list (a likely way for an item to vanish without a trace). Every write to the
  item lists now goes through one gate: it waits until the game's free lists, area and item table
  have stayed as they were for 60 ms, pauses DOSBox, looks again, and writes with the game held
  still; anything changed and the pass's item writes wait for the next. Kalzith's stock and loot,
  the arena ring, buyback and defilers' scrolls had no such check before, and the others' left a gap
  between the look and the writes. Rolls and queues taken before a refused write are kept for the
  next try. (`itemgate.py`, `GuestMemory.write`, `ProcessMemory.suspend`, `resume`, `itemgate.hold`;
  DEVELOPMENT § Changing the game's item lists. Tests: `test_itemgate.py`.)
- **Item reports through a change of area.** The game renumbers every item then, and this pull
  request's first way of telling a load (most items gone at once) took it for one and started
  afresh, so an item lost in the change passed unseen. A bulk change now waits until the new numbers
  hold still, matches old items with new by owner, slot and item, and reports one with no match;
  under half matched, or nothing settled in time, is a load. A number another item took over is no
  longer read as the old item still there. (`itemwatch._settle`, `renumbered`, `BULK_MATCH`,
  `BULK_WAIT`.)
- **Item reports, smaller:** a later save of the same party loaded no longer reports the items it
  doesn't have (the clock moving on more than `CLOCK_JUMP` with the party somewhere else is a load;
  a rest, with the party where it was, isn't, so an item gone as the party rests is still reported:
  `GameData.party_position`); money is taken for a sale only when it rose by what a shop pays for
  the item (its price, or 60%), so a purse picked or a reward no longer hides a vanish; an item
  handed over is remembered for 10 seconds (`ARRIVED_KEEP`), so a busy Loader doesn't report it.
- **A new character's gear fitted while the weapon window was still up:** the class restrictions,
  the kit's gear and the fuller starting gear now wait for it, as the starting weapon did, since a
  slow pick could leave a Titan Mind without its weapon, or a Ravager's two hands holding different
  weapons. (`_weapons_asked`.)
- **The arena's next wave** (a new fight by the fight flag, the clock not yet past `FIGHT_GAP`): the
  Poisoner's poison ready again, the rounds counted from 1, and the last wave's monsters' ACs
  forgotten, as the dances and Wild Fighting already were. (`_new_fight`.)
- Smaller: Pick Pockets could lose an item taken from someone when the thief's backpack list
  couldn't be made (the list is made first now); the freeze report after 2.3 hours of play listed
  only a few places once DSCLOG's count of them wrapped past 65535 (all 32 now); the combat log
  between fights kept a roll's detail lines arriving in a later batch than the line they belong to
  when that line was left out; `Play Dark Sun (in-game rolls).bat` said only "Something went wrong"
  when a crash report couldn't be written, and says why now, with how DOSBox closed.

**Docs**
- **Crash, freeze and item reports** are one section of the README, with a table of when each is
  written and what it holds (what all three share said once); closing DOSBox's window while the game
  runs is a crash report, as the code has it.
- **Draft release notes for 2.6.0** (`release-notes/v2.6.0.md`) and a "Coming in 2.6.0" line on the
  front page; How the game works notes that clerics never have the common 4th and 5th-level priest
  spells.
- How the game works has **the arena's count of fights:** what the announcer says at each count, the
  1000th trip's gifts and the 5000th's war won. DEVELOPMENT.md has the item gate, the item watch's
  area changes and the rings and cloaks of protection; the README's item reports say what an area
  change does.
- The damage numbers over creatures are off the README's known issues: seen in fights with the panel
  collapsed, docked and hidden since the panel's slowdown was fixed; the README says the expanded
  panel covers those under it. `tests/test_doclinks.py` checks the docs' links and the README's "How
  it works" links.
- **The original game's code, checked against yuan-ti's findings** (a new engine for the game,
  github.com/CalvinRodo/yuan-ti): How the game works has the psionic defence as the code has it
  (only defence modes already raised count, their cost paid again) and Enhanced Strength's and the
  Dominations' costs (worked out as used, not 0); armour with a magical power rolls against acid
  (always coming through). Hold Undead never held the living: every spell's targets are sifted
  before it lands, and the guard the mod added there stays; the claim is gone from the docs. A
  target turning to face its first attacker each round and the backstab multiplying only the first
  attack were confirmed in the code.
- **Features and rules, a page of their own** (`obsidian-edition/FEATURES.md`): the README's rule
  changes, character customization, expanded features, new content, graphics, controls, bug fixes,
  saves and game speed (about 1,800 lines) moved there, the README (about 1,000 lines) keeping
  installing, running, the Loader's window and the dice log, with a line pointing to the new page;
  every link to the moved sections points there now.

## Pull request #51 ([merged 2026-10-19](https://github.com/daaki85/darksun-obsidian-edition/pull/51))

**Release**
- **Obsidian Edition 2.5.0**: the version is 2.5.0, with its notes in `release-notes/v2.5.0.md`,
  listed on the front page with the others.

**New**
- **Item reports:** the Loader watches the party's items and, when one is gone from the whole party
  for two seconds, saves `crash-logs\item-<time>.txt` (the item, who had it and where, what its
  record says now, the game's time and region, the fight, the party's items before and after, the
  switches, and the dice log's and dialogue's last lines) and says so in the dice log, so a vanished
  item can be looked into as a crash is.
- **Four more magic weapons** for the kits that had too few (the dagger fighters, the archers, the
  thri-kreen), each with its icon, its name in DSCLOG's table (now 39 names) and a story from
  Alagorn. **Hayneedle,** a bone dagger +1 (a water cleric's too), early: hidden in Merzol's
  haystack in the slave pens with his sack of ceramic pieces.

**Changed**
- **Weapon specs picked after DONE** (with weapon specialization on): the creation screen's WEAPON
  SPEC pages are gone.
- **Claws cut:** the game makes every unarmed attack crushing, so a creature crushing weapons can't
  hurt (the mastyrials) took nothing from a thri-kreen's claws.
- **A Shinobi learns its own spells from scrolls too** (with kits on): it first reads the scroll, a
  d100 against its read languages, and then, with the rule for INT on, learns the spell at INT's
  chance.
- **A Pick Pockets button for thieves** in place of Thieves' Tools: on the USE screen, where a
  priest's Turn Undead is, a character with thief levels has a purse (outside fights; a cleric/thief
  has both, the purse beside Turn Undead, and Turn Undead alone in a fight).
- **Coins from a picked purse grow with the thief:** 2 to 5 ceramic pieces for each thief level (a
  4th-level thief takes 8 to 20) instead of 2 to 5 in all.

**Fixed**
- **Gerakis's Wild Fighting damage logged as the weapon's:** the game added his +3 (DSCLOG gives it
  to whoever's check passed), but the dice log credited Wild Fighting only to a Wild Fury's kit, so
  a passed check showed as "+2 weapon" (a bone sword's −1 and the +3), and a failed one's −3 to hit
  went unexplained.
- **A Battle Dancer's dance and Wild Fighting not rolled at a fight's start:** the Loader rolled
  them only for a fight's round 1, and it took a fight to be new only when the game's clock had run
  two minutes past the last one's last round.
- **Turn Undead's right click showed a new spell's description** (Fogbolt's, for an earth cleric;
  seen in 2.3.0 on): the game describes Turn Undead by numbers the new spells took.
- **Pick Pockets' right click showed nothing:** it now shows the purse and what it does.
- **A Shadowblade or Ghetto Fighter could start with a shield in the backpack:** the kit's gear left
  a shield behind only from a hand, so one already moved to the backpack stayed.
- **White ability labels on the inventory screen** (STR: to CHR:, among the yellow): the fix that
  drew the creation screen's labels in its white drew the inventory's in it too, as both screens
  draw them with one routine.
- **The Trustee stuck in the pens** (again): his rounds' two pauses took their corner from numbers
  any script in the pens could change, and once another had, he set off for a spot that doesn't
  exist and stood still for good, busy.
- **Figures hold the Loader's own weapons:** the bone and obsidian short swords and axes a new
  warrior starts with, the metal daggers, maces, great axes, picks and polearms, and the other new
  weapons were drawn as nothing, so a figure carrying one swung empty-handed (the game's own weapons
  were drawn).
- **Dinos's talk after the cooked vulture:** once he had given the meal's XP, his menu came back
  with only "Goodbye.", and a stray "Goodbye." followed in a window with no portrait.
- **Mirror Image works as it says** (seen in 2.4.0).
- **Armor lasts as long as it should:** it used a charge each time any spell or blow landed on its
  wearer, as well as for the damage, so each hit cost two and a friend's Bless one.
- **Share Strength's strength goes when the power ends:** the game looked for it under the
  psionicist rather than the one who got it, who kept it (and could end another of the psionicist's
  own effects instead).
- **The preserver's Dispel Magic no longer silences:** it laid "No spell use" on everyone it caught,
  the party too, which Dispel Magic can't remove.
- **Hold Undead holds only the undead:** it held living creatures too.
- **Cause Serious and Critical Wounds do 2d8+1 and 3d8+3,** as AD&D has them and the Cure spells
  heal; their records had 2d9 and 3d9.
- **A new game's arena could be left without its announcer, and new characters without their gear**
  (seen in 2.4.0): the Loader's starting gear, fitted just as START GAME rebuilt the game's item
  records, could use up the game's free records.
- **A Brute started with no weapon:** its long sword and club, which the game puts in the backpack,
  were left behind.
- **No crash report when DOSBox closed while the game still ran** (a freeze, DOSBox stopping with an
  error of its own, or its window closed): a report was saved only for an error code or the game's
  own error.
- **A crash after Continue on a monster's whole description** (the window that follows a Look box
  with more to say): the dialogue window can load other parts of the game's code over the routine
  that closed the Look box, and DSCLOG went back into it without a way back the game's overlay
  manager could mend.
- **The Loader's item-list changes made safer** (found in review): taking an item out of a list
  while the game's own free list moved could leave the item in no list at all; it now goes back
  where it was.
- **Defilers' scrolls on creatures that aren't defilers** (one of Scar's henchmen dropped one): the
  Loader knew a defiler by the class on its character sheet, which the game hands on from one
  creature to the next.

**Docs**
- **Kits, a page of their own** (`obsidian-edition/KITS.md`): the README's kit tables and rules
  moved out, as Items were, the README keeping a table of the kits' names with links; each kit fact
  repeated across the section (the Shinobi's spell list, the Seeker's and Justifier's casting
  levels, the Battle Mage's weapon pick, the Arcanist's two spells, Wild Fighting) is now said once.
- **A documentation review:** the Options tab's Weapon specialization switch no longer names the
  weapon pages; the mod's items are "the mod's", not "the Loader's"; the guide says weapon spec, as
  the game's screens do; the Effects-screen click among the bug fixes; item reports and thri-kreen
  claws in the guide and the README's bug fixes; the acid table in ITEMS.md ("Items against acid");
  the dice log's attack and save rows shortened, their detail under the tables; the front page's
  "What it does" a paragraph; install advice said once.
- **New:** "Where to start" and "Known issues" in the README, a glossary in the guide (THAC0, AC,
  PSP, the saves' letters and more), and in DEVELOPMENT.md the folders and how a release is made.
- **Items, a page of its own** (`obsidian-edition/ITEMS.md`): the README's item tables (every magic
  item, the magic weapons by weapon spec, every mundane weapon) moved out, as How the game works
  was; the README keeps a short section linking to it, and the front page, the guide and the
  docicons test name it.
- **Draft release notes for 2.5.0** (`release-notes/v2.5.0.md`), this pull request's changes for
  players, and a "Coming in 2.5.0" line on the front page.
- **The Warden's Legs' chest is the Wagon Train's,** not the Gemfields' (its chest, object 1065, is
  in region 8, with the magera and their prisoners; the Gemfields are region 6).
- **Patch notes:** the six new spells and the nineteen magic weapons as tables; the air cleric's
  dagger line says what the game had (none); acid on armour with the other Combat rules; the
  Loader's accessibility (larger text, the keyboard, contrast, logs as text).
- **The Loader's Options tab:** Picking pockets says a click on anyone in sight (it said "talk to
  someone"); the hiding switch reads more plainly; "...
- **Credits** on the front page: the code and documentation written by Claude, the direction and
  testing, the game and its makers, the rule books, and the tools.
- **The Loader's items in bold italics** in the item tables.
- **One item catalogue:** the README's New items tables merged into the item tables, which list the
  game's items and the Loader's together.
- **`patch-notes.html` made from `PATCH-NOTES.md`** by `python -m dsloader.patchnotes`, as the
  guide's page is (a test fails when it falls behind); its Copy as Markdown button gives the
  Markdown itself.
- **The front page tidied:** a list of the documents in place of the contents, the fan-project and
  license notes at the end, and the release notes listed once.
- **DEVELOPMENT.md opens with how to test, build and run** from a command prompt, then how it works;
  it says how the two web pages are made.
- **The README's "What it changes on your computer"** points to the files table instead of listing
  them twice; the patch notes' first line split in two.
- **GPL-3.0:** the project's code and documentation are licensed under the GNU General Public
  License v3.0 (`LICENSE`, in the release zip too), with a note that the game's own art in the pages
  isn't covered.
- **How the game works** moved out of the README into `obsidian-edition/HOW-THE-GAME-WORKS.md` (the
  original game's own rules, about 490 lines), the README keeping a list of its sections.
- **One source for the kits' numbers:** the README's kit tables.
- **[The game's bugs, fixed](obsidian-edition/FEATURES.md#the-games-bugs-fixed):** a README section
  with every bug of the game's own the Loader mends, the spells' among them, and a line for them
  under What it does on both front pages.
- **Rules the game got wrong** (the README's bug fixes, and a paragraph under the patch notes' Bug
  Fixes): the spell save, the doubled d20, two weapons, warriors' attacks, class restrictions,
  multiclass hit points, rangers' spells, acid, the class tables and thief skills, each with what
  the game did and the rule that puts it right; the thief skills' equipment penalty among the bugs
  always fixed.
- **The player's guide as a web page,** `obsidian-edition/player-guide.html`, in the patch notes'
  look with its sections as an index, made from PLAYER-GUIDE.md by `python -m dsloader.guidepage` (a
  test fails when it falls behind the guide).
- **Your saved games** (the patch notes, and the README's bug fixes): no new game needed for the
  fixes, which work from loading; what the old bugs already did to a save stays (Share Strength's
  kept strength, a Dispel Magic silence until it wears off, a 2.4.0 arena without its announcer); a
  new game still the way to see kits, fuller starting gear and the early new content.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file
as it
was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md),
and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #50 ([merged 2026-10-16](https://github.com/daaki85/darksun-obsidian-edition/pull/50))

**Release**
- **Obsidian Edition 2.4.0** (pull requests #48 and #49): the version is
  2.4.0, with its notes in `release-notes/v2.4.0.md`, listed on the front
  page with the others.

## Pull request #49 ([merged 2026-10-16](https://github.com/daaki85/darksun-obsidian-edition/pull/49))

**New**
- **The game's own party have features of their own:** Gerakis fights wild (the Wild Fury's Wild
  Fighting). K'ratchek casts as a Wasteland Seer, and her chatkcha comes back as if she had
  several (one more throw a round). Cilla is an Elven Wanderer, her hiding never halved in
  daylight. No character made on the creation screen can have them. (Kits. The Effects screen
  lists them as WILD FIGHTING, OPEN SKY SPELLS and CHATKCHA 2/ROUND, and KIT: E-WANDERER; the
  Characters tab beside the kit; the dice log as a new game starts.)
- **Six new multiclass kits:** the **Spellarcher** (half-elf fighter/preserver: its arrows 1
  better and at least +1, magical; its weapon spec the bow only), **Titan Mind** (half-giant
  fighter/psionicist: psychometabolism 2 PSP less, telepathy 2 more), **Poisoner** (halfling
  fighter/thief: its first hit in each fight poisons, a save or 10 damage; −1 to hit), **Spirit
  Caller** (halfling cleric/psionicist), **Wasteland Seer** (thri-kreen druid/fighter: spells
  cast 2 levels higher under the open sky, 1 lower under a roof) and **Wild Fury** (mul
  druid/fighter). (Kits.)
- **Wild Fighting** (the AD&D proficiency), the Wild Fury's: as each fight starts, a d20 against
  CON − 4, a natural 20 always failing. Passed, 1 more attack a round in melee and +3 damage for
  the fight; failed, −3 to hit and AC 3 worse. (Kits. The dice log shows the check.)
- **Crash reports say why the game quit:** the game prints its own error while the screen is in
  graphics, then clears it switching back to text, so the message was lost (as after the opening
  arena fight, "return code 01h" and a blank screen). The helper now keeps what the game last
  wrote, with the calls that led there, for the Loader's crash report.
- **Monsters' powers told apart in the dice log:** the game has no name for them, so the log adds
  the power's damage dice and kinds, as in "special attack 195 (1d10 crushing)" (Daggoran's).
- **A freeze report:** when the game stops but DOSBox stays open, the Loader's **Freeze report**
  button saves a zip in `crash-logs`. It holds where the game was running for its last few
  seconds (noted by the helper from the game's timer), the helper's state, the switches, the end
  of the dice log and dialogue, and a copy of the game's memory. (DEVELOPMENT § The freeze
  report.)

**Changed**
- **The Battle Dancer's dance rolls at −4:** a d20 against DEX − 4, a natural 20 always failing,
  as a proficiency check and as Wild Fighting's. It lasts that less the roll in rounds. (Kits.)
- **More for three multiclass kits:** the Military Scout, under the open sky, has +2 initiative
  and +1 to hit with a bow, sling or staff sling, and its hiding isn't halved in daylight. The
  Shadowblade tries to hide in shadows even with an enemy right beside it. The Wayfinder gets
  **Path-finder**: while it's up, every party member has +1 initiative and +1 Move in a fight.
  (Kits; the first two with hiding to backstab.)
- **Stronger costs for six multiclass kits:** the Shadowblade can't use a shield. The Military
  Scout never backstabs (from behind is still +2 to hit). The Wilderness Avenger has 1 fewer
  druid spell slot at each spell level. The Rescuer gets +1 to hit from behind, not +2. The
  Ghetto Fighter is −1 to hit with anything but a dagger and can't use a shield. While a
  Wayfinder is down (and no other is up), the party has −1 initiative and −1 Move in a fight.
  (Kits.)
- **Thieves' Tools are Mirlon's** (in the slave pens), for a party that kills him, as well as
  Kel's to sell. No thief starts with a set any more, and none is put in a thief's backpack
  later.
- **The leather helm keeps its own name,** no more `Helm (AC 1)`: its box shows `AC BONUS:1`
  with the helms rule, which says the same.
- **Thieves wear light armour only** (leather, hide, silk). Before, a thief of one class could
  wear any armour. A multiclass thief, or a human thief who was a fighter, gladiator, ranger or
  cleric, may wear the heavier armour its other class allows, but has no thief skills (all 0, on
  the inventory screen too) and no backstab in it. A human who has been a preserver and a warrior
  (either order) may wear the warrior's armour too, and casts no spells in it. (Class
  restrictions.)
- **Light armour only for the Assassin, Shinobi, Shadowblade, Poisoner and Spellarcher,** even
  with the kit asleep after changing class. (Kits.)
- **Starting gear for the kits:** a Battle Dancer starts with two long swords (the second in the
  left hand, in place of the shield). A Myrmidon has its second weapon in the left hand when it's
  a one-handed melee weapon (a bow still in the missile slot, a two-handed weapon in the
  backpack). A Poisoner has a dagger in each hand (its long sword made one, its shield left
  behind), and a Ghetto Fighter a dagger in its hand, whatever its weapon spec. Weapon specs
  start as the chatkcha for a thri-kreen whose classes allow it, the dagger for a Ghetto Fighter
  or Poisoner and the long sword for a Battle Dancer, unless the player picks another on the
  weapon pages. (Kits.)
- **Smaller starting gear changes:** a multiclass preserver's armour is left out, not put in its
  backpack. Fuller starting gear no longer adds a dagger to every backpack (a character whose
  classes start with one keeps it).
- **A ranger's bow is listed** on the Effects screen and the Characters tab (`EXPERT IN / LONG
  SWORD / BOW` for a cleric/ranger). Every ranger is an expert with the bow, chosen or not, but
  only the chosen weapons were listed.

**Fixed**
- **A Battle Dancer whose cleric sphere bars long swords couldn't specialize in one** on the
  creation screen, and started with a bow and a shield. The weapon pages left out what the kit
  allows whatever the classes do. It now starts with a long sword in each hand.
- **The game slowed down with the combat log's panel shown** (2.3.0). The helper put the panel
  on screen again on almost every pass of the game's main loop, with a slow byte-at-a-time copy.
  It is now put again at most once a BIOS tick, and the Loader stores the picture so each plane's
  part of a row is copied whole. (Measured in a fight: the idle loop ran 1,100 to 1,500 times a
  second with the panel, against 3,600 without; now 3,500 to 3,600.)
- **A multiclass preserver could cast in armour** (class restrictions on, since 2.0.0). The USE
  screen said NO SPELLS IN ARMOUR, but the spells stayed in use: the helper read the character
  from a register the game's own test had changed. It now reads the character the game asked
  about.
- **Copies of the combat log's panel were left on the map** (2.3.0) when the view scrolled by the
  game's own scrolling, which copies the screen, the panel with it. When the view has moved, the
  helper now has it drawn again whole, round the panel.
- **A patch of map showed under the pointer on the combat log's panel** (2.3.0). In a fight the
  game moves its pointer on the screen not on show and copies the box round it to the one on
  show. The panel was only on the one on show, so the copy brought the map back. It is now put on
  both.
- **A new character's bow was listed as "Arrows 1D6",** with no THAC0, on the inventory screen.
  The mod gave the arrows after the bow, which put them first in the character's items, and the
  game lists whichever comes first. The bow now goes first, and an "Arrows" line the game still
  shows gets the bow's THAC0.
- **Yellow text on the character creation screen** (since 2.3.0): the scores, the lines below
  them and the labels STR: to CHR:. The creation screen never sets its own colour, so after a
  character screen it took that screen's yellow. Its white is now set as it rolls, and the labels
  are drawn in it.
- **The combat log's panel showed on the USE screen,** hiding its right side and taking its
  clicks (2.3.0). It now shows on the map only.
- **A new character's weapon specialization carried over** from the character made before it.
  The game keeps one sheet for every character it creates, and changing the classes cleared the
  kit but not the specs. The specs are now cleared with the kit.
- **The dice log's damage for a STR 18 character was 2 short:** it added +2 for STR 18, but the
  game's own table adds +4. The Loader now reads the game's table, as it does STR's to-hit.

## Pull request #48 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/48))

**New**
- **Multiclass kits:** seven kits for two classes taken at once, each for one race only, chosen
  on the creation panel's KIT page as a class's kit is. (Kits.)
  - Elf cleric/fighter: **Battle Dancer**, which dances as each fight starts (a d20 against DEX:
    +1 to hit, damage and AC for DEX less the roll in rounds, or −1 for 1d8 rounds). Long swords
    and bows only, but any of them, whatever its cleric's sphere allows.
  - Half-elf fighter/thief: **Shadowblade** (+10 hide, +5 move, −10 pick pockets) and **Military
    Scout** (+10 to traps, move, hide and climb under the open sky, −5 under a roof).
  - Half-elf druid/fighter: **Wilderness Avenger** (+1 to hit and damage against undead; hides
    and moves as a ranger).
  - Half-elf cleric/ranger: **Rescuer** (cures heal 1 more a die under the open sky).
  - Dwarf fighter/thief: **Ghetto Fighter** (+1 with a dagger; two weapons at 0 and −2; +5 pick
    pockets and hide, −5 traps) and **Wayfinder** (+10 hide and move, −10 pick pockets).
- **The combat log below the map:** the game's screen is 320 × 222 and the log a strip under the
  map, always shown, covering none of it; the game's speed and the map's shape are as ever. In a
  fight it shows the round and the newest line, between fights the two newest lines. The mouse
  wheel scrolls it, with a **Latest** chip while scrolled back. (In the game, off by default. It
  is kept up through the arena's opening show; in the panel's darker shade, blue-grey under a
  screen in other colours, black on the title, the main menu and in character creation.)
- **Rolls out of fights in the combat log:** a thief's skills, a scroll learned, a new level's hit
  points, in the panel and the strip alike.
- **An L in the panel's top line,** a button that hides it as the key does.

**Changed**
- **The combat log's panel is shown and hidden with L:** 2.3.0 opened it in each fight and closed
  it at the end. **L** on the map shows or hides it, in a fight or out of one, to read back over
  the last fight or the rolls since. It stays as it was left, from one game to the next too. (L
  used to collapse it to one line; **-** does.)
- **Fuller starting gear for the game's own party too,** in the first moments of a new game:
  Gerakis a sling, leather chest and leg armour and a dagger; Cermak and Cilla a dagger.
  K'ratchek, a thri-kreen, keeps the game's own chatkcha and gets nothing more.
- **Fuller starting gear gives no belt or boots, and a cloak only to a Stalker, an Assassin or a
  Shinobi** (2.3.0 gave everyone a belt and boots, and a cloak to every ranger).
- **The inventory screen's `HIDE` and `MOVE` count a worn cloak and boots,** for thieves, rangers
  and their kits, as the rolls do: 10 each, to no more than 95, or the Cloak or Boots of
  Elvenkind's 95. The Characters tab's skills too. A worn belt's 5 was already in `PICK` and
  `LOCK`. (Hiding to backstab, with the cloak, boots and belt switch.)
- **The view in a fight** no longer drifts after each figure that walks near the screen's edge. It
  moves only to bring back one that has walked off the screen. (A switch, on by default.)

**Fixed**
- **The backpack's dagger was fought with** (fuller starting gear, 2.3.0). The Loader put the
  backpack's items (the dagger, Thieves' Tools, the arena's Ring +1, what's lifted from pockets) in
  the list of what a character wears and holds, where the game counts every weapon as in hand. So
  Gerakis fought with the dagger, not his long sword, and Cermak struck with it as a second
  weapon. Backpack items now go in the backpack's list, what the Loader takes in hand or puts away
  moves between the lists, and games where it happened are put right next time out of a fight
  (the dice log says `... is put away in the backpack`).
- **The game quit ("Return code 01h") or froze in fights with the combat log on** (2.3.0): the
  redraw routine, drawn in parts round the panel, went on from a way back the parts' drawing had
  overwritten (a variable the other probes share). The game ran on from the wrong place, writing
  over its memory (garbled names, stripes) until it quit. The way back is now kept on the stack.
- **A new thri-kreen was given gear** it can't wear or use (fuller starting gear, 2.3.0): armour,
  a belt, boots, a cloak, and a weapon and a dagger where its claws serve better. It now gets
  nothing more than the game's own starting gear.
- **The pointer over the combat log's panel** was hidden by it, and moving across the panel could
  leave a patch of map or no pointer (2.3.0). The panel is now put on before the game draws its
  pointer, the pointer is drawn again after the panel, and the panel's refresh leaves the
  pointer's box alone. (Checked: held still for 48 frames and moved across, the pointer showed
  every time and no map came through.)

## Pull request #47 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/47))

**Release**
- **Obsidian Edition 2.3.0** (pull requests #44 to #46): the version is
  2.3.0, with its notes in `release-notes/v2.3.0.md`, listed on the front
  page with the others (tag `v2.3.0`).

## Pull request #46 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/46))

**New**
- **Fuller starting gear:** before a new character is first played, the Loader adds plain gear it
  can use and hasn't got. That is a weapon in an empty right hand (from the backpack, as a
  cleric's club, else a plain one of its weapon spec or a short sword, club, mace, dagger or
  quarterstaff), a sling if it has no missile weapon (an earth or fire cleric a chatkcha), leather
  chest, arm and leg armour in empty places, a belt, boots, a dagger, and a cloak for a ranger or
  Stalker. A thief/psionicist and an air or fire cleric had started with no melee weapon. (More
  character customization, on by default. With the class restrictions, a multiclass preserver's
  armour goes into the backpack, so it can cast.)

**Changed**
- **An air cleric of one class may use daggers,** as its sphere allows. None of the game's daggers
  had the air cleric in its class list, so only Galefang would do. DSCLOG now adds it to every
  dagger type, the game's and the Loader's.

**Fixed**
- **The combat log's panel flickered and lost pieces** as figures moved and fought: the game drew
  the map over it a rectangle at a time, and DSCLOG only put it back afterwards. The rectangles
  are now drawn round the panel, and before the screens flip the panel is put on the one about to
  show. (The old way, through the redraw routine's way back, could also go stale if the game moved
  that code.)
- **A fighter/druid kept the shield it can't use.** Starting gear its classes can't use is left
  behind, but the last item of a list was kept (as a container's must be), and with the druid's
  armour gone that was the shield. A character's list may now empty, for the kits' gear too (a
  Ravager's shield, a Brute's club).

**Docs**
- **The docs said a multiclass character gets each class's gear:** the game gives one class's, the
  first of fighter or ranger, cleric, thief, psionicist, preserver and druid. (Seen in play for
  each two-class combination a half-elf can take.)
- **The documentation reviewed for clarity and repetition:** DEVELOPMENT.md's kits chapter moved
  after weapon specialization, as in the README; the README's new-item prices in a table, a
  preserver's first spells under a heading of their own, the requirements naming the GOG release
  only, and repeated "ticked by default" notes cut.

## Pull request #45 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/45))

**Changed**
- **The combat log in the game is on by default** (it was off until ticked). In a fight its panel
  shows the rolls over the map's lower right; **L** or its **-** button folds it to one line, and
  the Options tab's switch turns it off. Settings saved by an earlier version have it turned on
  once; after that the player's choice stands. (`settings_version` 2 in `settings.json`.)

## Pull request #44 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/44))

**New**
- **A combat log in the game:** in a fight, a panel over the map's lower right shows the dice
  log's lines as they come, in the game's font and the Ledger's colours, with the round and who
  acts next above them. At the least, in short (the default) or in detail.
- **Saves under their names:** the Ledger keeps a second copy of every save in its **Named saves**
  folder, named as in the game (`Page 2 slot 05 - Before Scar's battle.SAV`). The Options tab's
  new **Saves** section opens the folder and puts a named save back in a slot of the game's list.
- **Two magic shields:** **Gutterward**, a wooden shield +1, on a skeleton in the Tari's warrens,
  and **Ironbulwark**, a metal shield +3 (a type of the Ledger's: the game has no metal shield),
  carried by the Guardian of Balkazar's fortress.
- **Three new wizard spells,** all 1st level. **Reflected Image** (on the caster): one image,
  struck instead of the caster half the time; it and Mirror Image replace each other. **Spook**:
  one creature flees for 3 rounds unless it saves, at -1 for every 2 caster levels, at most -6;
  undead aren't affected. **Friends** (on the caster): CHA + 2d4, at most 25, for 1d4 rounds and
  1 a level, for better prices. (New wizard spells.)
- **Defilers' scrolls:** each defiler in a fight has a 5% chance of carrying a scroll of a random
  preserver spell (the game's 69, and the new spells with them on), found on its body when it
  dies. Rolled once a fight, and kept out of the dice log so it isn't given away.
- **Buying back magical items:** a magical item sold to a merchant (a plus, or a power: rings,
  wands, scrolls) stays in the merchant's stock to buy back. The game destroys everything sold,
  and still does other items.

**Changed**
- **Templar's Ledger is now the Dark Sun Obsidian Edition Loader** (the Loader for short): the
  window's banner and title, the crash message in the game, and every page of the docs, which now
  call it what starts the game with the mod rather than a companion window.
- **The folder is `obsidian-edition` and the Python package `dsloader`** (they were
  `darksun-companion` and `dscompanion`). `python -m dsloader` runs the command line, and the
  tests workflow is `tests.yml`.
- **More kits that can't go together:** the Grove Warden can't dual to gladiator, nor a gladiator
  who duals to druid take it (its AC would add to the gladiator's own). The Swashbuckler,
  Crusader, Battle Mage and Mind Warrior, each giving a warrior's THAC0, can't go with one
  another. The Ravager and the Grove Warden can't go together: each has an AC of its own that
  betters with level, and they would stack. (Kits.)
- **The Stalker and the thief:** a human Stalker can't dual to thief, and a thief who duals to
  ranger isn't offered the Stalker kit, whose +15 to hiding would add to a thief's own skills.
  (Kits.)
- **EMS is off in the launcher's DOSBox settings:** GOG's settings turn it on, and its 64 KB page
  frame left the helper 1 KB of upper memory. The game uses XMS instead, and the helper gets a
  64 KB block more, with conventional memory unchanged (632 KB).
- **The leader's CHA at shops:** 5% off from CHA 18 and 5% more for each point after, to 40% at
  25 (it was 5% at 16 to 25% from 20). Shops pay 60% of an item's price when the party sells: the
  game paid all of it, which with the discount let anything bought be sold at a profit.
- **Fogbolt's icon is grey,** its cloud on Armor's grey tile rather than Charm Person's purple.
- **The Shinobi can learn Fogbolt,** a 1st-level spell on its list beside the game's five,
  offered at a level up and cast at the thief level less 5 as the others are. (Kits, with New
  wizard spells.)
- **The bone and obsidian axes weigh 30** (35 and 70 before), the most a weapon can weigh without
  being HEAVY. Either can now go in the off hand with another weapon, and both can backstab.
- **Removed: each turn's rolls in the game's dialogue window,** since the combat log shows them
  without stopping the game. (The "Show each turn's rolls" switch and `--popups` are gone.)

**Fixed**
- **The dice log stopped in a fight whose round order named someone it couldn't match** (the
  Defiler and a Slig in the arena's opening show). The turn's lines now pass over that entry.
- **The new spells' records shared memory with a stack:** the game kept a small stack where Cat's
  Grace, Erdlu Claw and Fogbolt's records are. The helper now moves it (and the monster kinds
  table) into its own memory as the game starts, which also makes room for the three new spells.
- **New preservers weren't offered their spells:** DONE on the creation screen gave the game's own
  starting spells instead of CHOOSE A SPELL. The check meant to leave START GAME's ready-made party
  alone read the character's status, which says Okay for a character being made too.
- **Stuck on the creation panel's KITS page:** a warrior given a second class on the last weapon
  page kept its KITS button, which opened a page with no kits whose KITS button opened it again.
- **A kit was lost on a new roll:** the die's new roll takes a kit away when the classes aren't
  the ones the panel last saw, which it learns from a click on a class.
- **The panel after a new race or sex:** the creation screen puts the default class back without a
  click, so a fighter was left with the game's VIEW SPHERES (which did nothing) where WEAPON SPEC
  belongs.
- **Starting gear the classes can't use:** a character of several classes started with each
  class's gear, what it couldn't wear in the backpack (a fighter/druid/thief's leather armour).
- **A missile weapon's line on the inventory screen** showed the weapon's own rate of fire and no
  specialization bonus (a staff sling specialist's `1D4`).
- **A helm's item box said AC BONUS:0** (beside its name's "(AC 1)") until it had been worn: the
  rule set the helms' AC only as the game added up a character's.
- **Doors with charges:** a door's box (or a mirror's, a crank's) could say `Charges: 10`, read
  from bytes that hold something else in scenery.
- **The Cloak of Protection was forbidden to druids:** its type counts for AC as armour does, so
  class restrictions took it for armour.
- **A polearm's item box ran out of the box:** the game's Polearm picture is 36 pixels tall where
  every other is 22 at most, so the damage line (Thornwall's, Linebreaker's, the bone polearm's)
  fell outside.
- **The Trustee stuck at "I have to get back to work":** the game makes him busy after a talk
  until his rounds bring him back to their first corner. When his rounds stalled, he stayed busy
  for good and never talked again.
- **Rows of the creation panel's weapon and kit pages took clicks only at their left:** each row
  is a copy of the game's AIR row, a button 33 pixels wide, so a click on the rest of a longer
  name (MYRMIDON, LNG SWORD) did nothing.

**Docs**
- **Kits in the docs, class by class:** the README's one table of kits is a table for each class,
  under its own heading, with the level each part of a kit comes at, its starting gear and what
  else a player should know (the classes and kits it rules out, where its choices are made). The
  player guide's class sections have the same rows.
- **The player's guide is now `PLAYER-GUIDE.md`** (it was `GUIDE.md`); the links follow.
- **A review of every page for this pull request's changes:** the Trustee's key in picking
  pockets, a cloak isn't armour, a new roll keeps the kit, the axes' weight, the Saves section,
  `cloud_saves` under More saves, and STORE and RECALL in the More character customization table.
- **A second review, after the combat log:** the overviews name the combat log, the six wizard
  spells, buying back and defilers' scrolls; the top README's overview is a short list linking to
  the full one; the turn pop-up's last mentions are gone; the kits' starting gear is said once, in
  each class's table; the Options tab's new spells box names all six, and its screenshot is
  retaken.
- **A third review, after the rename:** the full README puts **In the game** (the combat log
  first) before the Loader's window, its overview a list; the player's guide starts with the
  combat log; the patch notes put the game's changes before the Loader's; DEVELOPMENT.md has the
  combat log under How each part works and Room in the helper as its own section (they were in
  Kits), a split Shinobi table is whole again, and "viewer" is gone from the docs.
- **The polearms' icons** in the README's item tables (the bone and metal Polearm, Thornwall,
  Linebreaker) are redrawn at the 22 pixels the game now shows them at.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file as it was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md), and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #43 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/43))

**Release**
- **Obsidian Edition 2.2.1:** the version is 2.2.1, with its notes in
  `release-notes/v2.2.1.md`, listed on the front page with the others.

**New**
- **A switch for the elves' and half-elves' looks:** "Elves have pointed ears, and half-elves
  figures of their own", in Graphics, on by default, from the next start. Off, elves are as the
  game draws them and half-elves the human figures in their own colours, as before 2.2.0.
- **A switch for Cilla's elf figure** in Graphics, on by default: off, she keeps the game's
  half-elf woman's figure, from the next start.
- **A switch for STORE and RECALL** under More character customization, on by default: off, the
  creation screen is the game's, from the next start.
- **Restore defaults** at the bottom of the Options tab sets every switch back, after asking.

**Changed**
- **The Options tab's headings are plain names** (In the game, Rule changes, More character
  customization, Expanded features, New content, Graphics, Controls, Game speed). One line above
  them says that everything applies in games started from the Ledger and that a switch marked
  "from the next start" waits for the game to be started again. The elves' and half-elves' looks
  come first in Graphics.

## Pull request #42 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/42))

**Release**
- **Obsidian Edition 2.2.0:** the version is 2.2.0, with its notes in
  `release-notes/v2.2.0.md` (pull requests #39 to #42), listed on the front
  page with the others; the patch notes say 2.2.0.

## Pull request #41 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/41))

**New**
- **STORE and RECALL on the creation screen,** as Baldur's Gate has them. STORE keeps the roll on
  screen (the six scores and the die's total, the hit points and PSP); RECALL brings it back
  however many times the die has been rolled since, AC and damage with it. Changing the race,
  sex, classes or kit forgets it. (The two buttons are carved like the game's own, under the hit
  points. The dice log's ring is 84 entries, was 88, to make room in upper memory.)
- **Half-elves have their own figures** on the map and in fights, where the game drew the human
  ones. The man is built on the elf's figure, a little broader, with short fair hair, a linen
  shirt under a leather jerkin, green trousers, brown boots and small pointed ears. The woman is a
  little slimmer than the human woman, her golden hair in a bun, with pointed ears, a purple
  cloak, purple wristbands and red boots. Worn gear is drawn over them as on the figures they were
  made from (armour on his clothes, a worn cloak in place of her purple one, a shield on the
  forearm in a fight).
- **Elves have pointed ears,** walking and fighting, beside any helm.

**Changed**
- **The Options tab in four groups:** **Rule changes** (the game's rules closer to AD&D), **More
  character customization** (weapon specialization, kits, levels up to 10), **Expanded features**
  (the leader's CHA at shops, and **Improved thieving**: AD&D's thief skills, hiding to backstab,
  the cloak, boots and belt, picking pockets) and **New content** (now with the new wizard
  spells). The Thieves section is gone, its switches under Improved thieving; each switch keeps
  its setting.
- **Removed: P in a conversation** for picking pockets: Thieves' Tools are the way to pick a
  pocket. The game is no longer patched where the conversation window passes on a key, and
  DSCLOG's handler for it is gone.

**Fixed**
- **Cilla looks like the elf she is:** the game's own party gave her the half-elf woman's figure.
  She has the elf woman's now, in a new game and (from the next area) in one already begun.

**Docs**
- **Graphics** is the README's section for what the Ledger draws on the map (was "On the
  screen"), with a part for elves and half-elves. The Options tab's section has the same name,
  and DEVELOPMENT.md a section on how elves and half-elves are drawn.
- **The patch notes have a table of contents,** as their web page does.
- **The README in the Options tab's groups,** STORE and RECALL under More character
  customization and the new wizard spells first in New content. The guide's Options table and both
  READMEs' overviews follow, and the Options tab's screenshot is new.
- **Smaller:** the game's own party is under More character customization (its weapon specs and
  Cermak's kit) and points to Cilla's elf figure; the bracers and robes are parts of New items;
  "hiding to backstab" where the README said "the stealth rule"; DEVELOPMENT.md's "How each part
  works" follows the README's order; the patch notes' Thieves section is **Improved Thieving**.
- **The patch notes' items, one by one,** in four groups: magic weapons (fifteen, each with what
  it is, and the Elven Leader's Gythka +2), magic armour and worn items (Inixhide among them,
  missing before; Arrowbane and the Sunking Crown said not to be armour), other magic items (the
  Tome and Kalzith's six scrolls, by name) and mundane items (Thieves' Tools among them).
- **"Weapon type" throughout,** where the pages said "kind of weapon" or "weapon kind"; the item
  tables' Kind column is Type.

## Pull request #40 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/40))

**Docs**
- **Semyon as the game tells him:** the README called him "of the Veiled Alliance". In the game he
  is a slave tied up for asking after it, "much more of a scout than a warrior", who takes the
  party for the Alliance and asks to join. His section now says so, in his own words from the
  arena, as does the description in the Ledger's code.

## Pull request #39 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/39))

**New**
- **Two new wizard spells, Erdlu Claw and Fogbolt, and Cat's Grace is a spell of its own.** Erdlu
  Claw (1st level): for 5 rounds a caster level, natural and unarmed attacks do 1d6+1 where that's
  better (or Body Weaponry's and Animal Affinity's dice +1), are +1 to hit and count as a +1
  magical weapon. Fogbolt (1st level): a dark grey bolt of its own that needs a clear line to its
  target; for 2d4 rounds unless saved against, -3 to the fogged creature's attacks and +2 to
  attacks on it. (New wizard spells, was Cat's Grace.)
- **The three spells are spells 196-198,** learnt, listed, cast and shown on the Effects screen
  like the game's own, each with its icon, description and sounds (Cat's Grace Haste's, Erdlu
  Claw Shocking Grasp's, Fogbolt Fog Cloud's). Cat's Grace no longer takes Flaming Sphere's
  place, and Magic Missile's bolt stays blue. Who knows them is kept in the character's sheet.
  (The dice log's ring is 88 entries, was 96, so the helper still fits in upper memory.)

**Changed**
- **Multiclass hit points follow Demihuman Deities (TSR 1998):** CON's bonus goes on every hit die
  (a warrior's +3, +4 if one of the classes is a fighter, gladiator or ranger, else at most +2),
  and the running total is divided by the classes. The rule had divided CON's bonus, which the
  game counts once a level of the highest class, by the classes again. (A fighter 9 / preserver
  10 / thief 10 with CON 18 got 12 hit points from CON, now 38.)
- **The level-up weapon window shows the weapons:** a bigger window with each weapon type's
  inventory picture, six to a row, in place of the names, those the character can't pick greyed.
  Pointing at one names it (SPECIALIZE IN / DAGGER, or EXPERT IN for a ranger or Battle Mage), as
  CHOOSE A SPELL names a spell. (Also on becoming a warrior by DUAL.)
- **View Character labels the saves and adds MOVE:** the five saves each have their label (PPD,
  RSW, PP, BW, SP, as on the inventory screen) in place of one SAVE line. THAC0 moves down beside
  PSI, and MOVE is new, beside HP.
- **Rangers and Twin-blades fight with two weapons at no penalty only in light armour:** every
  piece worn, a helm too, of leather or of no material. In other armour they take AD&D's -2 and
  -4, as anyone does; the dice log and the Characters tab say the same. A Justifier has no penalty
  in any armour, a bonus of its own. (The two-weapon rule.)
- **Cermak is an Arcanist** in the game's own party, his gear and hit points as the game gives
  them. Gerakis has no kit. (Kits.)
- **Removed: boots no longer give a move in a fight.** The rule was a leftover from trying out
  changes to items. Its switch is gone, boots are plain "Boots" again (games with "Boots
  (Speed+1)" get the game's names back), and the Characters tab's move shows only a kit's extra
  (the Stalker's).

**Fixed**
- **A save line read as if the save succeeded** ("Thrikreen saves vs Fogbolt ... -> failed"). It
  is now the creature's saving throw, then the result: `Wild Mul's saving throw vs Fogbolt from
  Daaki (spell): d20 = 16, needs 14 (35% to save) -> saved`. "Cannot save" and "saves
  automatically" read `none allowed (cannot save) -> failed` and `not needed (saves
  automatically) -> saved`.
- **The dice log showed XP for every kill,** from the creature's sheet, even where the party gains
  none (the arena's opening fight). A kill now reads "Rampager is killed"; XP shows only on the
  "XP: ..." line, when the party's XP really goes up.
- **EXIT on CHOOSE A SPELL did nothing** when a new preserver picked its starting spells (or a
  human its spells on becoming a preserver): the window only opened again. EXIT now ends the
  picking, and the spells left are the game's own starting spells, less any picked.
- **The game's own party had to pick spells:** starting with no party made, Cermak and Cilla were
  put on CHOOSE A SPELL. They keep the game's spells again; only a character made on the creation
  screen (still New) picks.

**Docs**
- **The new spells' screenshots:** their three descriptions, the Effects screen with Cat's Grace
  and Erdlu Claw, and Fogbolt's bolt replace the two Cat's Grace pictures. The Options tab and a
  spell's end-of-turn window (a Fogbolt, where it was a Cone of Cold save) are retaken.
- **A review of every page:** the README's main screenshot (the arena's opening show's dice log)
  is retaken without the kill XP, and the Options tab's with every rule switch. The README gains a
  Characters tab section, the missing "Scores and hit points as rolled" in its contents, a clearer
  list of what play writes to the game folder, and the kits' details in one list; notes on how
  things were tested and the old release names are gone. The guide has its first pictures (the
  dice log, the weapon window) and no longer says the game's own party has no weapon specs.
  DEVELOPMENT.md points to the README for the kits' table, says what the helper's memory is now,
  and drops the kits' build diary.
- **Screenshots retaken where they had fallen behind:** the inventory, the tome, the game's own
  party (the off hand at one attack a round, not 1.5), the creation screen's weapons page (the
  scores' total under CHR), the gear boxes (plain boots), the figures' gear (now with shadows),
  Kalzith's shop (the CHA discount) and the Options tab (no boots switch).

## Pull request #38 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/38))

**Release**
- **The release zip is `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`,** unzipping to
  a folder of that name, to match the releases' title (it was `Obsidian-Edition-<version>.zip`).

## Pull request #37 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/37))

**Release**
- **Obsidian Edition 2.1.1:** the version is 2.1.1, with its notes in
  `release-notes/v2.1.1.md`, listed on the front page with the others.
- **Releases are titled "Dark Sun: Shattered Lands - Obsidian Edition"** and the version, rather
  than "Obsidian Edition" alone.

**Fixed**
- **The dice log missed character creation rolls:** the die rolls a whole character many times
  while it tumbles, more than the log could read, so abilities often came as "its rolls came too
  fast to record". The helper now keeps each ability's last four 4d4, and the log reads them when
  the die stops; the rolls missed meanwhile are no longer mentioned.
- **Raising CON on the creation screen didn't raise the hit points** (lowering it could lower
  them): the game only kept them within the new range. A change of CON now adds or takes off its
  bonus for every level, as the game counts it. (Scores and hit points as rolled.)

## Pull request #36 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/36))

**Release**
- **Obsidian Edition 2.1.0:** the version is 2.1.0, with its notes in
  `release-notes/v2.1.0.md` (pull request #35), listed on the front page with
  the others.

## Pull request #35 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/35))

**New**
- **Scores and hit points as rolled:** on the creation screen a click raises a score only while
  the six add up to no more than the die gave, so lowering one frees points for another, and a
  click on the hit points does nothing. Under CHR the screen shows the six's total and the die's
  (`SUM:99/101`); a new class that raises a score to its minimum raises the die's total with it.
  The dice log adds each roll's total. (A new rule, on by default, with its own box on the Options
  tab. No interrupt vectors were left, so the new sites share the one for choosing a preserver's
  spells, with a site number after the `INT`.)

**Changed**
- **Removed: turning the mouse wheel no longer scrolls the map** (the Ledger's Windows mouse hook
  is gone); pressing the wheel and dragging still does.

**Fixed**
- **A click on a score on the creation screen stopped the game** (since 2.0.0): the Mind Warrior's
  PSP check at the end of the game's PSP routine returned with interrupts off, and nothing turned
  them on again. The flags are now put back.

**Docs**
- **Patch notes** (`PATCH-NOTES.md`, and `patch-notes.html` as a page with a copy-as-Markdown
  button): every change from the original game, laid out as patch notes to share online. Linked
  from the front page.

## Pull request #34 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/34))

- This changelog: pull request #33 marked as merged, with its date and link.

## Pull request #33 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/33))

**Release**
- **Obsidian Edition 2.0.0:** the version is 2.0.0, the first release under
  the new name, with its notes in `release-notes/v2.0.0.md` (pull requests #31
  and #32), listed on the front page with the others.

## Pull request #32 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/32))

**Docs**
- **All the documents reviewed:** the front page and the README name AD&D's class tables, the
  leader's CHA and the robes among the rules and items. The README's rule count (21), item and
  price tables and Kalzith's shop are up to date. The guide's gladiator AC (with or without
  armour) and the game's priest THAC0 are corrected, and its "What the Ledger shows you" (which
  the quality of life table covers) is gone. DEVELOPMENT.md's kits are no longer "being built",
  its parts follow the README's order, and the shop's NO DEAL! and the CHA rule's check are there.

## Pull request #31 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/31))

**New**
- **Kits:** a character of one class may take one of three kits for its class, or none, on the
  creation panel's new KIT page (KITS, at the end of the panel's pages), NO KIT first, the rows
  not chosen greyed as the spheres' are. (DEVELOPMENT.md has how they are built, each effect's
  hook among them; the probes are listed in `gamepatch.py`.)
- **What the kits do:** the Myrmidon, Sentinel and Ravager (fighter); the Arena Champion,
  Twin-blade and Brute (gladiator); the Stalker (ranger); the Assassin (thief); the Grove Warden
  and Wanderer (druid); the Lifebinder's weapons, and the Shinobi's weapons and armour.
- **Kits' THAC0:** the Swashbuckler, Crusader, Battle Mage and Mind Warrior get a warrior's THAC0,
  the Scholar's is 1 worse (a new probe at the end of the game's THAC0 routine). The
  Swashbuckler's −10 to every thief skill is named in the dice log's thief skill lines, as the
  Assassin's now is.
- **Kits' spell slots:** the Arcanist's wizard slots are 1 more at each spell level, the Battle
  Mage's and Crusader's 1 fewer, the Elementalist's a level behind, and the Seeker's and
  Justifier's priest slots their own tables. The Ledger's Spells tab counts them the same way.
- **Kits' PSP:** the Mind Bender's telepathy powers (the defence modes too) cost 2 PSP less to use
  and keep up and its psychokinesis 2 more; the Kineticist's the other way about.
- **Kits' healing:** the Healer's Cure Light, Serious and Critical Wounds heal 1 more a die, and
  the Lifebinder's cures heal a die more. The dice log shows each.
- **The Battle Mage** casts though hit earlier in the round (the game stops anyone else), and holds
  nothing in the off hand.
- **Kits' casting level:** the Seeker casts at its ranger level less 5 and the Justifier less 9 (a
  ranger's: less 7), which also lets a 6th-level Seeker choose 1st-level priest spells.
- **Rangers' casting level:** a ranger's spells last and do damage as cast at its level less 7, as
  the spell levels it may cast already count it. The game took the whole ranger level. (A rule, on
  by default.)
- **The Shinobi's spells:** preserver spells from 6th thief level on the Seeker's slots, cast at
  the thief level less 5, from its own list of 14. One is learnt at each level up from 6th, on
  CHOOSE A SPELL, which shows its spells only; none from scrolls.
- **The Scholar** learns a spell more at each level up: CHOOSE A SPELL comes up twice.
- **The Battle Mage's weapon and armour:** it wears light armour (leather, or none) and casts in
  it. With weapon specialization it chooses one weapon spec (long sword, club, dagger, short
  sword, mace, axe or pick) on the weapon pages, may use those weapons as well as a preserver's,
  and attacks with them at expertise's rate, 3/2 a round (2 from 7th level).
- **The Elementalist's second sphere,** chosen on the CLERICAL SPHERE list once the kit is taken:
  its spells known from the start, cast at its cleric level, and its weapons allowed as well as
  its own sphere's.
- **The Seeker's weapons** are its sphere's, as a cleric's of that sphere, but for the bow.
- **Kits' hit dice and PSP:** the Battle Mage rolls a d6 for hit points, the Mind Warrior a d8 with
  a tenth fewer PSP (rounded down), and the Arcanist a d3, at each level up and on the creation
  screen. Choosing or taking back one of these kits rolls the hit points and works out the PSP
  again, which the game did only on a click on a class.
- **A kit sleeps when a human dual-classes** (DUAL on a portrait's menu), as the class it came
  with does, and wakes, gifts and costs, once the new class's level passes the old one's.
- **Classes a kit bars on dual-classing are greyed on the DUAL window:** a Seeker or Justifier
  can't become a cleric or druid, nor a Shinobi a preserver (their slot tables would replace the
  new class's). The Swashbuckler, Crusader, Battle Mage and Mind Warrior take no warrior class
  (they have a warrior's THAC0). An Arena Champion or Sentinel takes no druid or preserver (no
  shield), and a Brute no psionicist or air cleric (no two-handed melee weapon).
- **Weapon specs are weapons learnt for good,** while the class or kit that gave them is awake: no
  kit forbids a weapon type the character specialized in (but for the off hand's rules).
- **A human who becomes a preserver picks its two spells** on CHOOSE A SPELL (1st level only), not
  Grease and Magic Missile.
- **Kits for a human's new class:** after DUAL, the game's three-choice menu asks for the new
  class's kit (**KIT: NONE**, then its kits, leaving off one barred by the other classes or kits),
  and a new Elementalist's second sphere. With weapon specialization, a new fighter, gladiator,
  ranger or Battle Mage then picks the weapon types it is due.
- **The Effects screen a page at a time:** its lower panel has room for five lines, too few for
  three kits and a gladiator's weapon specs.
- **A new preserver picks its starting spells** on CHOOSE A SPELL when DONE is clicked on the
  creation screen (two 1st-level at 1st level, four at 2nd, four and two of 2nd level at 3rd; a
  Scholar one more a level), in place of the ones the game handed out.
- **The Stalker hides in shadows indoors** with its full chance (the stealth rule halves a
  ranger's indoors).
- **Starting gear fitted to the kit,** changed while the character is new: a Shinobi's long sword
  becomes a bone short sword, a Brute's a bone great axe, a Seeker's one of its sphere's material.
  A Ravager's shield is taken away, an Arena Champion's off-hand club becomes a shield, and a
  Battle Mage's quarterstaff its weapon spec's weapon. A Myrmidon also gets a plain weapon of its
  second weapon spec (in the backpack; a bow in the missile slot, with arrows), a Ravager a second
  of its weapon for the hand its shield left (none for a two-handed one), and a Brute's club is
  left behind.
- **Two magic robes** for preservers, psionicists and druids, worn on the chest and not armour
  (they cast in them; their AC with no armour worn, as bracers'). The **Ashen Robe** (+1 AC, +1 on
  saves against spells) is Kalzith's, worn, sold and left when he is killed. The **Veiled Robe**
  (+2 AC, +1 on every save, a wizard slot more at spell levels 1-3) is sold by Kel.
- **Charges in an item's box:** a wand, the Storm Ring or a necklace shows the charges left
  (`Charges: 50`).
- **Preservers' INT:** AD&D's table gives a preserver a chance to learn a spell from a scroll (35%
  at INT 9 to 100% at 24; a failed try uses the scroll up) and caps the spells of each level it may
  know (6 at INT 9, all from 19), which also limits CHOOSE A SPELL at a level up. (A rule change,
  on by default.)
- **The leader's CHA at shops:** the party leader's CHA lowers what shops ask, as Baldur's Gate's
  table has it (5% at CHA 16 to 25% from 20), in the price shown, the price charged and the
  greying of what the party can't afford; selling unchanged. (A rule change, on by default.)
- **AD&D's class tables:** AD&D's XP tables (a gladiator's and ranger's 2nd level 2,250, a
  thief's 1,250; the game had a gladiator on the fighter's), priests' THAC0 (2 better every 3
  levels from 4th; the game's from 3rd) and spell slots (AD&D's priest table for clerics and
  druids, its wizard table for preservers). (A rule change, on by default.)

**Changed**
- **The mod is now Obsidian Edition.** Templar's Ledger stays the name of its companion window.
- **Kalzith wears his Ashen Robe, Cloak and Quarterstaff from the start** and sells them with his
  scrolls (the game's shops sell all a merchant carries, worn or not).
- **The helper loads into upper memory again,** leaving the game 62 KB more conventional memory
  (632 KB free, was 570). The dice log's ring buffer now follows the helper in a segment of its
  own, so the helper's image is 40 KB (was 63).
- **Two weapons:** the off hand attacks once a round, whoever holds it; the extra attacks (the
  game's 3/2 for warriors, specialization's, the kits') are the main hand's.
- **A kit for each class:** the kit byte keeps two bits for each of a human's classes, so a human
  who changes class can have up to three kits. Every kit rule asks for each kit the character has
  awake, and the Effects screen lists them all.
- **The Arcanist casts two preserver spells in a turn** in a fight: its first doesn't end the turn
  (a hit still keeps it from a second). Its drawback is a d3 hit die (a preserver's is a d4), in
  place of −2 CON.
- **The Crusader and Mind Warrior** have a warrior's extra attacks in melee, 3/2 a round from 7th
  level of the kit's class, with weapon specialization on or off (the DAM lines and the Ledger's
  party view show them too).
- **The Ravager's base AC** is described only up to 10th level, the highest the game goes.
- **Room in the helper:** the dice log's ring holds 96 entries (was 128) and the text buffer is 4
  KB (was 8), for the kits' code. The helper's interrupts are now 8Ch to FEh (and 60h to 65h); the
  message when they are in use says so.

**Fixed**
- **A kit or a second sphere could change a sound:** the game reads two sound numbers on the
  character sheet as words, and the kit and second sphere sit in their high bytes. They are read a
  byte each now.
- **Arena crash after a kill (hardened):** DOSBox could close as a creature died in a fight.

**Docs**
- **The player's guide** (`GUIDE.md`), new: the game's rules as its code works them and the mod's
  changes, laid out like the game's rule book, with the tables, and no spoilers. It was rewritten
  to tell how the mod plays, with its default options and a "Without the mod" note where a switch
  changes the game's own; the manual's comparisons, race and class list and unchecked hot keys
  are gone.
- **The player's guide, more:** the quality of life changes in a table; each kit's starting gear;
  the kits' spell slots and the Shinobi's spell list; the preservers' and priests' spells by
  level, sphere and class (from the game's spell records); things worth knowing in play; the
  races' ranges of scores and why a half-giant's penalties give the Dark Sun book's caps; a short
  description of who takes each kit on Athas; the Battle Mage's 3/2 attacks (2 from 7th level).
- **The player's guide by class:** for each class, how it plays, what the mod changes, its weapons
  and armour, its kits, starting gear and races, every multiclass combination (from the game's
  creation tables: gladiators never multiclass), how a human dual-classes into or out of it (from
  the game's DUAL check) and the magic weapons it can wield.
- **The README reorganised:** what the game does on its own under How the game works, every rule
  change under Rule changes, sub-headings for Kits, the item box charges under In the game,
  addresses left to DEVELOPMENT.md, and every section in the contents.
- **Kits that can't go together** lists only pairs that can meet: the Arena Champion and Sentinel
  clash only with the Shinobi (README, guide).
- **Smaller:** the Warden's Plate's AC explained (12 points better as a set, not "AC 11"); the
  Kits switch no longer says half the kits work; the front page names the kits and INT among the
  rules, and what has changed since 1.2.0; DEVELOPMENT.md has how kits are built (room in the
  helper, the sheet's kit byte, the creation page, each effect's hook) and a summary of the
  patched game's interrupts, with `gamepatch.py` as the list.

*Shortened: each change's full notes (addresses, measurements, how it was found) are in [this file as it was](https://github.com/daaki85/darksun-obsidian-edition/blob/7e18e937e583d95fc493d89cf157b7f8463ba85f/CHANGELOG.md), and how each part works now in the [development notes](obsidian-edition/DEVELOPMENT.md).*

## Pull request #30 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/30))

**Release**
- **Templar's Ledger 1.2.0:** the version is 1.2.0, with its notes in
  `release-notes/v1.2.0.md` (pull requests #19 to #29), listed on the front
  page with the others.

## Pull request #29 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/29))

**Changed**
- **A ranger's bow is its own:** a multiclass ranger may use bows whatever its cleric sphere allows
  (a fire cleric/ranger, whose sphere allows only obsidian). A human ranger turned cleric gets the
  bow back with its chosen weapon spec once the cleric level passes the ranger's. Before, its bow
  expertise was there but no bow could be readied. (Class restrictions.)

**Docs**
- **What it does,** on the front page and in the guide alike: what the Ledger shows of the game's
  hidden rolls, how it brings the rules closer to AD&D, what it adds to Athas and on the screen,
  and its quality of life changes.
- **Two weapons** is a section of its own, beside Thieves and Saving throws (the game's rule, then
  AD&D's penalties), rather than under The dice log.

## Pull request #28 ([merged 2026-10-08](https://github.com/daaki85/darksun-obsidian-edition/pull/28))

**Changed**
- **Warriors shoot faster from 7th level** with a missile weapon they haven't specialized in, as
  their melee goes from 1 to 3/2: a bow 3 a round (was 2), a sling, staff sling or chatkcha 3/2
  (was 1). Specialists keep their rates, a step ahead at every level.
- **The Options tab:** a **Thieves** section of its own, after Rule changes, with AD&D's thief
  skills, hiding to backstab (and the cloak, boots and belt) and picking pockets (and the P key);
  the weapon specialization box is shorter. The arena's ring goes with New items, magical and
  mundane, its own box gone. The red rings are under Controls, with Tab and Enter; scrolling with
  the right button is a line under the mouse wheel's.
- **The Ledger's window:** Show details and Show unlabelled rolls are on the Dice log tab, above
  the log. Save layout and Reload layout are on the Memory tools tab, leaving the top row to
  starting the game, its window, the text size and Reconnect. A byte's decoding has its own line.
- **Smaller:** "Not connected" says to start the game with Start the game, not a command-line
  option; a character's card leaves out empty lines (a non-warrior's weapon specs).

**Docs**
- **The guide reorganised:** Every magic item and Every mundane weapon under Item tables;
  Suggested system requirements under Requirements, linked from Game speed; Picking pockets moved
  to Thieves; weapon specialization tidied ("weapon spec" throughout, every ranger's bow expertise
  said first); the two Two weapons sections one; the Effects screen's click under Controls.
- **The guide read through:** the game's own saving throws explained once, under Saving throws;
  the crash sections one; Show Save with the practice program under Without the game; the
  Characters tab's card as a list; the backstab table with the new weapons (a bone axe and a pick
  can backstab); sixteen rule changes, not fifteen; technical notes moved to DEVELOPMENT; old-save
  notes gone.
- **Screenshots retaken with the game installed** (its title lettering, portraits and figures):
  the dice log, the Dialogue tab, the practice program and a thief's card. The backstab table is
  checked against the game's item data (named long swords weigh 10 to 40).

## Pull request #27 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/27))

**Changed**
- **No bow to choose for a ranger** at creation, nor in the catch-up pick at a level gained:
  every ranger has expertise with the bow already.

**Docs**
- Where a ranger's bow expertise and missile weapons' rates show, and the Options tab's weapon
  specialization box, mention them.

## Pull request #26 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/26))

**Changed**
- **Missile specialists shoot faster:** a fighter or gladiator with a chosen bow shoots 3 a round,
  then 4 from 7th level; a sling, staff sling or chatkcha 3/2, then 2 (AD&D's specialist's rate
  for the sling, a step above it for the others). A grand master shoots once more a round, as in
  melee. Before, missiles kept the game's rate. (Weapon specialization. The Characters tab shows
  each missile weapon's rate.)
- **Rangers and the bow:** every ranger has expertise with the bow on top of the weapon type it
  chooses, and a ranger's expertise with a missile weapon gives the same rate of fire, with no
  other bonus.

**Docs**
- **Attacks a round:** a table in the guide by skill (non-warriors, a weapon type not chosen,
  expertise, specialized, mastery, grand mastery) and level, for melee, bows and the other missile
  weapons.

## Pull request #25 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/25))

**New**
- **Bone and obsidian great axes and a bone dagger,** each with an icon. A warrior's starting
  great axe is now bone (obsidian for a fire or earth cleric), and a water cleric's starting
  dagger bone. Water and fire clerics' warriors can now choose the great axe, and water clerics'
  the dagger.
- **Replacements for what breaks:** the Weapon Merchant sells great axes in all three materials,
  the metal pick and the bone dagger. Jark sells bone and obsidian great axes and the bone dagger,
  and every Wild Mul carries a bone great axe. Kel sells two sets of Thieves' Tools.
- **Defilers leave a body:** each of the game's two kinds of defiler carries a dagger, one
  obsidian and one bone. The game leaves no body for someone who carried nothing.
- **Mindshard from Maris's pocket:** a thief can lift it, as Shadowseeker and Gutterknot, for 200
  XP.

**Changed**
- **One box for the new items:** the Options tab's four item boxes are one, **New items, magical
  and mundane**. The arena's ring keeps its own box, and the "Give thieving tools now" button is
  gone (Kel sells them).
- **Weapons off the allies:** Krikor's bone axe, Uskuye's metal great axe and Lt. Kwerin's metal
  pick are gone; the Weapon Merchant sells the metal ones.
- **The Sunking Crown** gives Protection from Evil, not the 10' Radius one.

**Fixed**
- **The game's Sling +1** (in a chest) showed a blank icon: its picture was missing from the
  game's data. It now has one, the Sling's with a glow.

**Docs**
- **Item icons** in every item table of the guide.
- **[Every magic item](obsidian-edition/ITEMS.md#every-magic-item)** and **[Every mundane
  weapon](obsidian-edition/ITEMS.md#every-mundane-weapon):** each item, the game's and the
  Ledger's, with its bonus or power and who sells or carries it; the magic weapons of each weapon
  type for weapon specialization.
- **Mundane items** in a table of their own in New items, and the Ledger's weapons in the acid
  saving throw table.

## Pull request #24 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/24))

**New**
- **Magic weapons for the classes that had too few,** each with an icon and a story from Alagorn:
  - **Galefang,** a metal dagger +2 an air cleric can wield (a new item type: none of the game's
    daggers are an air cleric's), on the Rogue Shaman;
  - **Mindshard,** an obsidian short sword +1, on Maris, and **Stillwater,** a bone short sword
    +1, in the chest Chaya gives as her apology: a psionicist's, alone or with a cleric's;
  - **Linebreaker,** a metal polearm +2, on the Troop Leader, and **Thornwall,** a bone polearm
    +1, on the slave pens' weapon rack in place of one of its two plain ones (the rack gets an
    object of its own: the Lower Castle's is the same object).
  - Alagorn's weapons menu now has more items than a script has locals: the last are kept in the
    Ledger's flags.

**Fixed**
- **Drakejaw** (pull request #23) was never on its Magera: the game read its own Gemfields region,
  not the Ledger's copy, which DSCLOG now opens instead.

## Pull request #23 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/23))

**New**
- **Three magic axes,** each with an icon and a story from Alagorn:
  - **Drakejaw,** a bone axe +1, on one of the Magera guarding the wagon's prisoners (he gets an
    object of his own);
  - **Glasshewer,** an obsidian axe +2, on the elven slavers' Templar;
  - **Headsman,** a metal great axe +2, in the arena Announcer's stash.
  - Alagorn's weapons are told by a copy of his script 213 (222), so no script overflows the
    game's script buffer.

**Changed**
- **The Elven Leader's Gythka is +2** (was +1). It also no longer takes Kreenfang's icon, which
  any Gythka +1 did.

## Pull request #22 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/22))

**Changed**
- **Cermak, of the game's own party, specializes in the long sword and the axe** (was the club),
  which count once his gladiator levels do again.

## Pull request #21 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/21))

**New**
- **The Tome of Understanding:** Father Garyn's gift when the party brings him the ranike pith.
  Read like a scroll (right-click it, click its icon), it gives the reader a point of WIS for good
  (at most 25) and is used up. It is the game's book, with a night-steel cover and an emblem in
  the fire colours of its magic items.
- **The game's own party is made ready for the rule changes,** for a new player who presses START
  GAME. Gerakis specializes in the long sword and the gythka and carries a bone gythka in place of
  his club; K'ratchek specializes in the chatkcha; Cermak in the long sword and the club. Cilla, a
  druid who can't wear armour, has her leather armour taken away and knows Armor instead.
- **The Warden's Plate,** plate mail +1 in four pieces: the Helm on Dagolar's body (Cloak of
  Bravery while worn), the Arms in the Lower Castle's treasure chest with Dark Flame, the Legs in
  the Gemfields' chest, the Chest on Balkazar's body (Resist Fire while worn). Plate is AC 3 chest,
  2 arms, 2 legs (DSCLOG's new item types), each +1; the helm is the game's metal helm +1. Each
  piece has an icon of its own and is drawn on the figures. (The magic weapons' switch.)
- **The Cloak and Boots of Elvenkind,** for thieves and rangers only (multiclasses too). The cloak
  is the Elven Leader's gift with his Gythka +1; the boots are in the buried chest of Kel's
  caravan. With the hiding rule, the cloak's wearer hides in shadows on 95 or less under the open
  sky and 90 under a roof (not halved by the light), and the boots' wearer moves silently on 95 or
  less. Their item boxes say so (`Hide 90-95%`, `Move 95%`). (The magic weapons' switch.)
- **The Flame Blade,** an obsidian long sword +1 in the pack of the Hot Springs' Templar. Its
  blade casts the fire clerics' Focus Heat on what it hits (2d6 fire, a save for half), as the
  game's Dark Flame does Burning Hands. Obsidian, so a fire cleric can wield it. (The magic
  weapons' switch.)
- **Alagorn knows every new magic item,** each in the menu the game would put it in: the Flame
  Blade, the Warden's Plate (a part of Haldren's story for each piece), the Cloak and Boots of
  Elvenkind, the Bracers of Defense, Arrowbane, the Sunking Crown, Inixhide, the Rings and Cloak of
  Protection and the Tome of Understanding. There is one story for each kind, as with the game's
  own items: the four pairs of bracers share one, and so do both rings. His clothes, rings and
  other items are told by copies of his script 212 (220 and 221), so no script overflows the
  game's script buffer.

**Changed**
- **The world's new items are in the game's own data,** not added while you play. The launcher
  writes them into their people's and chests' objects, so a new game makes them where they belong.
  The slave pens' items (Kurzak's Shadowseeker and helm, Legcrusher's armour, Pehtucl's cloak and
  ring) and Kreenfang (the arena's dead body's gythka) are in the data too. The Boots of Elvenkind
  are in the buried chest when it is dug up; the bone scale set's arm and leg pieces and helm are
  in the slave pens' chest with its chest piece; one Castle Guard and one Undermountain miner have
  objects of their own for their items. The Options tab's switches take effect from the next
  start, in regions not yet visited.
- **The Elven Leader gives the Cloak of Elvenkind himself,** after his Gythka +1, with a line of
  his own. When it can't be carried he leaves it on the ground beside him, as with the Gythka.
- **Grey's Scale's arm and leg armour are AC 3** (the game's are 2).
- **A new warrior with a staff sling keeps its shield,** as with a bow. Both go in the missile
  slot, and the game asks nothing of the hands for them; the shield went into the backpack before.
- **The magic weapons and Legcrusher's leather have names:** the Club +1 is Gutterknot, the Pick
  +1 Deepbiter, the Staff Sling +1 Windlash, the Short Sword +2 Greenbright and the Leather Chest
  Armor +1 Inixhide, each with a story from Alagorn. Greenbright is now on Arant, who holds the
  captured gladiators (the Elite Guards are only in the final fight). A thief can lift Gutterknot
  from Churrr's pocket for 200 XP, as Shadowseeker from Kurzak's.
- **A circlet and a crown, worn on the head and not armour:** Arrowbane, a silver circlet sold by
  Kel, keeps Protection from Normal Missiles on its wearer; the Sunking Crown, worn by Keldar,
  Protection from Evil, 10' Radius. Neither gives AC, nor stops bracers of defense or a
  preserver's spells. Each has an icon of its own and is drawn on the figures (a silver band with a
  stone; a gold band with points). (The magic weapons' switch.)
- **Bracers of defense give nothing with a helm on,** as with any armour. A shield and rings and
  cloaks of protection still go with them.

**Fixed**
- **Alagorn's clothes with none carried:** he said "no magic clothes", then "Ah, magic clothes",
  and showed an empty menu. The game's two nested tests for clothes are now kept.
- **Armor, spell 0, was missing from the Ledger:** the Spells tab left it out and the dice log
  would have named it "spell 0". The game numbers its spells from 0.
- **No manual check:** the dragon asking for a word from the manual when the party first leaves
  the sewers (the game's copy protection) no longer comes. The game goes on as if it had been
  answered.
- **The Ledger's window started with an error,** from an indentation slip in its Options code
  since pull request #20. A test now compiles every module.

**Docs**
- **The documents are shorter and better organised:** the front page gives an overview and only
  the latest pull request's news. The guide's dice log lines are grouped by topic, its internals
  moved to DEVELOPMENT.md (with the command-line use), and its new items described once. Released
  pull requests here are summarised.
- **The README's new items** are one item to a row, with the prices and the Options tab's boxes
  after the table. The ranger's row no longer names a fighter/ranger (the game has none).

## Pull request #20 ([merged 2026-10-07](https://github.com/daaki85/darksun-obsidian-edition/pull/20))

**New**
- **The new plain weapons in the world** (a new content switch, on by default). The Weapon
  Merchant and Jark sell the bone and obsidian short swords and axes and the obsidian mace, and the
  Weapon Merchant a plain metal short sword. Merzol, Krikor and Chaero carry one, and every Tari in
  the warrens, Renegade and Wild Mul has one as loot.
- **Bracers of defense** (a new content switch with the magic weapons, on by default): AC 6 on
  Mikquetzl, AC 5 on Wyrmias, AC 4 on Balkazar and AC 2 on Dagolar, 20,000 to 40,000. Worn on the
  arms, they give nothing while armour is worn on the arms, legs or chest, and are not armour to
  the class rules (a preserver casts in them).
- **Magic weapons of the weapon types the game has none of:** a Club +1 on Churrr in the warrens,
  a stone Pick +1 on one of the Undermountain folk, a Staff Sling +1 sold by the Bowyer and a metal
  Short Sword +2 on an Elite Guard. Each has an icon of its own and is priced as the game prices
  its own: the melee ones as its Obsidian Bloodwrath +1, 20,800 a plus; the staff sling as its
  Sling +1, 2,800.
- **Metal daggers, maces, great axes, picks and polearms,** which the game has none of plain: one
  each on Tobrian, a Templar of the slavers' camp, Uskuye, Kwerin and a Castle Guard. An earth
  cleric may now take the great axe and the polearm, and starts with a metal one.
- **Weapon specialization** (a new rule change, on by default). Fighters and gladiators specialize
  in weapon types (+1 to hit, +2 damage), fighters on to mastery at 5th level (+3, +3) and grand
  mastery at 9th (the damage die a size larger and an attack more); rangers take expertise. A
  warrior with a weapon of another type attacks at AD&D's plain rate.
  - Sixteen weapon types, chosen on the creation screen's new WEAPON SPEC pages, greyed as the
    game's disciplines are. A multiclass warrior's are limited to the weapon types it may use some
    weapon of, in any material (a fire cleric's obsidian long sword).
  - A new warrior starts with a plain weapon of its type in a material it may use. New bone short
    swords and axes, and obsidian ones for fire and earth clerics, since the game has only Kurzak's
    short sword and a metal axe; an obsidian mace pictured without Blackmace's glow; a plain great
    axe without the Great Axe +3's gem. A two-handed weapon puts the starting shield in the
    backpack.
  - A gladiator's 3rd and 4th (and any warrior's from before the rule) are picked at a level
    gained, in the game's own pop-up for a psionicist's new power.
  - The weapon types are listed on the Effects screen and counted on the DAM lines and in the dice
    log. The Characters tab lists each character's weapon types (`Weapons: long sword (grand
    mastery)`) and the attacks a round with each weapon held (`Attacks: 3/2 a round with Long
    Sword, 1 with Axe`).
- **Class restrictions** (a new rule change, on by default): psionicists, multiclass thieves,
  preservers, druids and clerics are held to their own limits on armour, shields and weapons
  whatever their other classes allow, the strictest winning. A multiclass preserver casts no
  spells in armour: its spell slots are headed NO SPELLS IN ARMOUR on the USE screen, and the
  Characters tab says "(no spells in armour)".
- **Multiclass hit points** (a new rule change, on by default): each level's die and CON's bonus
  are divided between a character's classes, as in AD&D, at creation and at every level. The dice
  log shows the share. Meant for a new game: ticked during one, a character's next level shares
  CON's bonus for all its levels.
- **Hit dice, the better of two** (a new rule change, on by default): every character's hit die is
  rolled twice, at creation and at each level, and the better roll kept. The dice log shows both.

**Changed**
- **The Ledger's magic items are priced as the game's own:** the Rings and the Cloak of Protection
  +1 15,000 (were 5,000), Leather Chest Armor +1 6,000 (was 3,000), Kreenfang 20,800 (was 18,000),
  as the game's Gythka +1. Ones already given are repriced.

**Fixed**
- **The Characters tab read the game as if every rule were off** in its THAC0, attacks and
  specialization lines. It now uses the rules ticked.
- **Character creation in the dice log logged every roll:** one click on the die rolls a whole
  character several times while it tumbles, and the log gave every one. When rolls came too fast
  to record, the hit point line took CON from an earlier one (37 logged where the game had 40).
  Now only the character the die stops on is logged, each ability and the hit points checked
  against the screen (`DEX 19 (its rolls came too fast to record)`).
- **"No hit point roll" on a level gained:** the dice log said the game rolls hit points only when
  a character's highest class level rises. It rolls for every new class level; a level that leaves
  the most hit points unchanged only added a fraction (the game divides the whole total by the
  classes).

**Docs**
- **The README is shorter** (2,974 lines to about 2,300). How each part works (the helper's
  interrupts, the game's offsets and flags), how the dice log works, what's known of the game's
  data and the development notes are in a new `obsidian-edition/DEVELOPMENT.md`, each README
  section linking to its part. "What it does" is a short overview. The thieves' skills and
  backstabs, and the saving throws, are each one section with their rule changes; the two-weapon
  rule sits with the dice log's two weapons. The new items are one section with a table, Kalzith
  and Semyon one of new people told as a player meets them, and the helms' and boots' rules one.

## Pull request #19 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/19))

**New**
- **View Character names the class that levels up next:** for a character of more than one class,
  the XP in brackets on the experience line names the class that reaches its next level there
  (`EXP:87230 (90000 Pr)`). A letter for each class, but Pr and Ps for preserver and psionicist;
  both are named when two level up at the same XP (`(20000 Pr/T)`), and a class already at the
  highest level never. One class is as before. (The patched game's `INT D2h`, where the game adds
  the bracket.)

**Changed**
- **Kalzith sells Shield and Burning Hands** in place of Magic Missile and Color Spray (3,000
  each), so none of his scrolls is one the game has (Color Spray's is in the sewers). Magic Missile
  and Color Spray scrolls he stocked before become Shield and Burning Hands, wherever they are.

**Fixed**
- **Kalzith's prices:** Blur 6,000 (was 3,000) and Haste 9,000 (was 12,000). They were taken from
  the game's scrolls with the spell numbers read one off (Wall of Fog's and Flame Arrow's). The
  game has no scroll of either, so they're its price for the spell's level, 3,000 a level. His
  stock is repriced when the Ledger next sees the game.

## Pull request #18 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/18))

**Release 1.1.0:** the version, its notes, and pull request #17 marked merged in the READMEs.

## Pull request #17 ([merged 2026-10-06](https://github.com/daaki85/darksun-obsidian-edition/pull/17))

**New**
- **Searching junk, hay and wardrobes in the dice log:** each search's roll, what it found, and
  how far the count of finds has got. A rat's bite or a falling pot shows its damage roll.
- **More saves:** 40 instead of the game's 10, on four pages of ten in the save and load window.
  PAGE 1 to PAGE 4 buttons sit under EXIT, and PgDn and PgUp go to the next page and the one
  before.
- **More characters:** 29 saved characters instead of the game's 19.
- **Rule change, items saving against acid:** a worn piece of armour or a held melee weapon the
  Rampager's acid or the Babau's corroding touch could destroy needs the easier of the game's
  number and AD&D's save against acid for its material, less its plus and 1 more for a magical
  power.
- **Rule change, rings and cloaks of protection as in AD&D:** of two rings only the better counts,
  and a ring gives no AC with magical armour. A cloak of protection does nothing with magical
  armour, metal armour or a shield in either hand; natural armour is fine.
- **A worn belt helps a thief:** +5 to picking pockets and opening locks, counted by the game's
  own lock picking and by the Ledger. Its item box says `Pick +5, Lock +5`.
- **Kreenfang and Shadowseeker:** the 2 handed Bone Gythka on the dead body by the stone arch in
  the arena is Kreenfang, a gythka +1. Kurzak's short sword is Shadowseeker, a short sword +1
  whose wielder sees the invisible.
- **Alagorn knows Kreenfang and Shadowseeker:** the Painted Badlands wizard who identifies magic
  items has each in his menus when the party carries it, with a story of its own.
- **200 XP for lifting Kurzak's sword:** the conversation says the thief lifts "a metal short
  sword" and receives 200 experience points, with the quest's sound, given by the game's own
  routine for a quest's XP.

**Changed**
- **Kalzith's scrolls at the game's prices,** 3,000 to 12,000 ceramic: the game's own price for a
  scroll of the same spell, else its price for the spell's level.
- **A monster's alignment in the Look box:** `THAC0 17 AL TN`, the alignment in two letters. The
  description in the dialogue window and the dice log's `Look:` line name it in words.
- **The Options tab's sections open and close:** each group of switches is under a heading to
  click, so the tab is short. Which are open is remembered.
- **The whole party walks as fast as the leader alone at the fastest game speed:** the Ledger's
  shadows and dust are drawn much more cheaply, and look the same.
- **Cloaks and boots say what they do:** with the cloak and boots bonuses on, their item box says
  `Hide +10` or `Move +10` under the name.
- **Boots are named "Boots (Speed+1)"** for the boots rule, so their extra move in a fight isn't
  mistaken for the item box's `Move +10`.
- **Plain cloaks, boots and belts cost 24** (the Leather Cloak was 20). Magic ones keep their
  prices.

**Fixed**
- **DELETE in the roster deleted the wrong character,** a bug of the game's own. It counted the
  row clicked from the top of the list, not of what was shown, so with the list scrolled down
  another character was deleted.
- **Kalzith's and Semyon's questions are asked once a talk:** a reply that doesn't end the talk
  leaves the list once chosen, as the game's own people's do, and is back the next time you talk
  to them.
- **The load window shows an empty page:** PAGE 2 to PAGE 4 did nothing in the load window when
  that page had no saves.
- **A shield on a figure walking side-on showed nowhere.** It is now held forward of the chest,
  its near half showing.
- Smaller: a character not yet played counted as not Okay, so a new thief's skills all showed 0
  on the inventory screen. The Look box showed an AC the Ledger worked out for another creature:
  the arena's first fight comes too soon after the opening one to tell them apart by the game's
  time, and a Slig showed the opening fight's Defiler's AC -9. The Ledger's new item pictures
  wiped an item's spell: changing an icon cleared four bytes of the item where the game's picture
  cache is two.

## Pull request #16 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/16))

**New**
- **Semyon breaks out with Scar:** recruit Semyon before the fight with Scar and take up Scar's
  offer to break out, and Semyon comes along to the slave pens with Scar's men. He fights the
  guards on the party's side and has a line of his own for the breakout.
- **Game speed on the Options tab:** the launcher gives DOSBox 20,000 cycles by default; GOG's own
  speed and 30,000 can be chosen. The companion's README suggests system requirements for each.
- **Faster walking with gear shown:** the party's figure pictures keep only the room their gear
  needs while walking.
- **New content switches:** Kalzith, Semyon, the cooked vulture, the slave pens' gear, a worn
  cloak's and boots' bonuses to hiding, and the Effects screen's click keeping a spell can each be
  switched off on the Options tab.
- **Crash reports:** when DOSBox crashes or the game stops with an error, the game's message stays
  on screen. The Ledger saves a report in `crash-logs` with how it closed, what was on screen, the
  switches, and the end of the dice log and dialogue.
- **The Trustee knows Semyon got away:** if Semyon broke out with the party and lived, the Trustee
  says so after the escape, instead of "Every single one" for all the pens.

**Changed**
- **Kalzith and the alarm:** while the escape's alarm sounds he has a line for the party and no
  talk, as the pens' other slaves do.
- **A vanished bone scale piece is written up:** the set is still given once a game and never
  again. Should the Bone Helm, or the arm or leg piece, vanish, the Ledger saves a report on what
  became of it in `crash-logs`, and the log says so.
- **Finding the Ring +1 is worth 50 XP** to whoever searches the Tied-up Prisoner's body, given as
  the game gives a quest's, once.
- **Picking pockets is with the Thieves' Tools only, by default:** the Options tab's switch is now
  about the tools, and P in a conversation is a choice under it, off unless ticked.

**Fixed**
- **A crash in the opening fight:** when the game couldn't make the first of two drawing areas of
  the map's view, it freed the second one anyway with a number it had never set.
- **The bone scale set in a second new game:** the Ledger remembered it as given across games, so
  a later new game never had it. It is now kept for each game.
- **Thieves' Tools clicked between turns** (as an area changes) stopped the dice log with an error.
- **The game's flags** were read and written through a null pointer at times. The Ledger's guard
  stopped the writes.
- **Crash messages readable:** a game that stopped in graphics mode left its error message
  invisible. The screen goes back to text before the message.
- From a review of the code:
  - **Clicks after Tab + Enter:** for a few seconds after Enter, anything the next character
    clicked could still count as the enemy chosen before.
  - **Kalzith and Semyon in fights:** people past the map's 256th thing were missing from the
    Ledger's list of who is in a fight, so they had no ring, no Tab, no HP lines and no "killed"
    line.
  - **A thief who went last and is next** after someone first who can't act lost their turn line
    and hiding roll.
  - **Two halved hits seen together** were put down to the first, and the second later logged as
    doing nothing.
  - **The mouse wheel's watch** (Windows) was started again on every reconnect without stopping
    the last one.
  - **Kalzith only with his object:** a copy of the game whose objects lack what he is made from
    no longer gets his scripts, and a clash over his scrolls' pictures no longer loses every icon.
  - **Speed:** the rings' and dust's colour tables are worked out once for a palette, not every 30
    seconds.

**Docs**
- **The READMEs reorganised,** each with a table of contents: the guide's sections grouped as the
  Options tab is, the window's guide beside how to start it, the memory-mapping steps under
  Development. This changelog moved out of the main README into its own file.

## Pull request #15 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/15))

**READMEs after pull request #14:** the changelog, the cooked vulture quest and its screenshot, and
the new log lines.

## Pull request #14 ([merged 2026-10-04](https://github.com/daaki85/darksun-obsidian-edition/pull/14))

**New**
- **What the party wears, on the map:** each character's figure shows their weapons and shields,
  bow and quiver on the back, armour, helms as circlets, cloaks, boots and belts, walking and
  fighting. It changes as soon as their gear does.
- **Kalzith, a defiler in the slave pens:** a slave the templars put in the arena now and then,
  kept in a pen of his own, with a face of his own.
- **Semyon in the slave pens,** once he has left the arena: in a pen of his own above Kalzith's,
  with his own conversation.
- **Dinos and the Trustee know about them:** their "who else is in here" questions also ask about
  Kalzith, and about Semyon once he is in the pens. If either is killed, they speak of him as of
  the game's dead.
- **Shadows under every figure on the map:** each living creature's outline, laid down toward the
  lower right, see-through and in the floor's own colours. They are drawn on the floor before the
  walls and figures, so everything in front stands on them.
- **Scrolling the map with the mouse:** pressing the wheel and moving drags the map with the
  pointer, in fights too, and in Windows turning the wheel scrolls it.
- **Dust behind walking feet:** puffs on sand and dirt behind anyone walking, spreading and fading
  in about a second, under the walls and figures.
- **Tab chooses an enemy, Enter attacks it:** on a party member's turn in a fight, Tab picks an
  enemy, marked by a red ring, with the view scrolled to it. Enter attacks it as a click on it
  would, even when someone stands in front of it.
- **Hits that do less than rolled** in the dice log: a weapon hit that took part of its damage, or
  none, with what the monster's defences say.
- **The quest sound for the vulture:** giving Dinos the cooked vulture plays the sound the game
  plays when a quest is done.
- **Cloaks and boots help thieves and rangers hide:** with the stealth rule, a worn cloak adds 10
  to hiding in shadows and worn boots 10 to moving silently, up to 95.
- **Regeneration in the dice log:** a hit point back by itself, which the game gives anyone with
  CON 20 or more, is logged as such.
- **A safety net against stray writes:** the Ledger never writes over the start of memory or the
  first bytes of the game's data. A write stopped there is named in the dice log.

**Changed**
- **The Effects screen no longer ends a spell's effect when its icon is clicked.**
- **Windows' security warning only once:** after the first `.bat` file is let through, the Ledger
  takes the download mark off the files in its own folder, so the others start without asking.
- **The vulture quest is part of Dinos's talk:** while the party carries the cooked vulture, his
  first menu has "We cooked the vulture from the arena." just before "Goodbye." His answer is in
  his own dialogue window, with his portrait, and the XP comes as the game's quests give it, in
  the game's own window. The vulture is no longer used on him from the inventory.
- **Cat's Grace's icon** is a cat's paw print instead of a cat's face.
- **Dinos's vulture lines** are his own words, without narration (the game's conversations are
  people speaking).

**Fixed**
- **DOSBox crashes, garbled figures, freezes and "Null pointer assignment":** the gear writer kept
  writing a party picture over memory the game had freed and given to something else.
- **Kalzith said he had nothing left to sell** after one purchase: while a save loaded, the Ledger
  could read the new game's flags with the last game's Kalzith and mark it sold out.
- **The vulture's reward came in the dice log when a game was loaded,** and its XP and rest were
  given then. The flag was read from memory still being loaded.
- **A thief first in a round didn't hide:** someone who had the last turn of one round and the
  first of the next got no new turn in the log, so no hide in shadows or move silently roll.
- **Tab + Enter froze the game:** after Enter, the walk to the chosen enemy stalled, sometimes
  until a mouse click.
- **The party's gear showed late after an area change:** the Ledger looked for the area's newly
  loaded pictures only every 10 seconds, and dressed the party with its slower checks. A party
  walking off as the area loaded stayed plain meanwhile.
- **Cat's Grace was missing from the Effects screen:** its effect had no icon in the game's table
  of effects, and the screen shows only effects with one.
- **Kalzith's scrolls cast their spell instead of teaching it:** the game teaches only from scroll
  objects numbered 1400 to 1499, and his were 1001 to 1006.
- **Figures' shadows fell the wrong way,** toward the lower left, while the walls', bones' and
  stones' shadows on the maps fall toward the lower right.
- **Kalzith's and Semyon's Look box** sometimes lacked the HP, AC and THAC0 lines: the Ledger only
  looked among the map's first 256 things, and the game numbers them anew, sometimes past that.
- **The slave pens broken by Kalzith:** Kurzak vanished after leading the party in, people were
  missing, Merzol didn't stop the party, the doors' "pick the lock" and "knock" and the main
  door's "Summon Kurzak!" were gone, and the water jug couldn't be filled.
- **Figures took extra steps after their turn in a fight:** to have figures drawn again with their
  shadows, the Ledger marked them "changed", which in a fight could set one walking again.
- **"Killed" lines for everyone in an area the party left:** walking from the slave pens into the
  arena logged most of the pens as "is killed".
- Smaller: Kalzith's scrolls taught the spell before their own; "Who are you?" hung the game when
  asked of Kalzith; picking pockets said "won't get another chance" to everyone in a new game with
  the same party, since the last game's tries were remembered.

## Pull request #13 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/13))

**The Release workflow can be run by hand,** making the version's tag.

## Pull request #12 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/12))

**Release 1.0.0:** the version, its release notes, and a workflow that builds the release zip.

## Pull request #11 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/11))

**New**
- **Cat's Grace looks like itself:** its own icon and its own description in the spell box,
  instead of Flaming Sphere's.

**Changed**
- **Getting started:** open the Ledger first, pick the options, then Start the game from it.

**Fixed**
- **The slave pens' gear was given twice** to a game loaded after it was given. None of it is
  given where it is already in the game.
- **The bone scale set was added twice** to a game loaded after it was added. It is now added only
  where none of its pieces is.
- **Prices:** Leather Chest Armor +1 is worth 3000, the Cloak of Protection +1 5000 and the Rings
  of Protection +1 5000, as magic items. Ones already in a game are repriced.
- **Dinos takes the vulture as soon as a fight is over:** the Ledger now reads the game's own
  combat flag.
- **Thieves' Tools can't be used in a fight,** only out of one.
- **The dice log and the Dialogue tab keep up with the newest lines;** scrolling up to read back
  still holds the place.
- **No more log lines for the Ledger's items** handed out: they're there to be found.
- **The Bone Helm** can only be worn by those who can wear bone scale armour (not thieves).

## Pull request #10 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/10))

**Fixed:** half-giants' two-handed weapons in one hand. The rule didn't take effect.

## Pull request #9 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/9))

**New**
- **Rule change, thief skills from AD&D's table:** a skill is AD&D's average for the thief level,
  plus the race's adjustment, plus Dark Sun's DEX adjustment.
- **The bone scale set:** where the Bone Scale Chest Armor is found, its arm and leg pieces and a
  new Bone Helm, coloured to match, are found with it.
- **Rule change, half-giants wield two-handed weapons in one hand,** with a shield or a light
  weapon in the other.
- **Names in colour in the dice log:** each party member's in a colour of their own, monsters' in
  red, bold, all at 4.5:1 contrast or more.

**Changed**
- **The Options tab scrolls** when the window is too small to show it all.
- **Options:** the Ring +1, picking pockets and the thieving tools button sit under Rule changes,
  with the other changes to play.

**Fixed**
- **A game that stops with an error** leaves its message on screen, and the dice log says how
  DOSBox closed, telling a crash of DOSBox's own apart.
- **Picking a pocket after loading a save:** a try made after the save is forgotten when it's
  loaded, so that person can be tried again.
- **XP taken away and given back between areas** is no longer logged as a loss and a gain. A loss
  that stays is logged after a minute.
- **A monster's AC in its Look box** could be an earlier fight's creature's: a slig in the first
  arena fight showed the opening fight's Defiler's AC −9.

## Pull request #8 ([merged 2026-10-02](https://github.com/daaki85/darksun-obsidian-edition/pull/8))

**New**
- **Rule change, levels up to 10:** every class can reach 10th level, at AD&D's XP.
- **Gear for the slave pens' bosses,** given once a game with the Ledger running. Kurzak has a
  metal Short Sword (1d6, a new item type; a thief can lift it) and a leather Helm; Legcrusher,
  Leather Chest Armor +1; Pehtucl, a Cloak of Protection +1 (a new item type: +1 AC and +1 on
  saves, as the ring) and a Ring of Protection +1 (a thief can lift it).
- **Rangers hide in shadows and move silently too,** with AD&D's ranger chances: the full chance
  outdoors and half indoors, the reverse of thieves.
- **Item icons of their own** for the Short Sword, Leather Chest Armor +1, the Cloak of Protection
  +1 and the two Rings of Protection +1, made from the game's plain ones.

**Changed**
- **Thief skills have no equipment penalty:** the game took 5 to 10 off some thief skills for
  anything in the legs slot, the quiver or either hand. It no longer does in games started with
  the dice log.
- **The inventory screen shows hide in shadows** in hear noise's place. The Ledger's own screens
  show both.
- **Pick pockets lifts a short sword** too, though it weighs more than other small things.

## Pull request #7 ([merged 2026-10-01](https://github.com/daaki85/darksun-obsidian-edition/pull/7))

**New**
- **Rule change, AD&D's two-weapon penalties:** a non-ranger with a melee weapon in each hand
  attacks at −2 with the main hand and −4 with the off hand, offset by the DEX reaction
  adjustment.
- **Rule change, the spell save:** spells are saved against with the spell save, not
  petrification/polymorph.
- **Rule change, DEX instead of a doubled d20:** on saves against fire, cold and electricity, the
  DEX defensive adjustment counts instead of a doubled d20.
- **Cat's Grace,** a new 2nd-level wizard spell in Flaming Sphere's place: +1d6 DEX, at most 24,
  working exactly as Strength does for STR. Untick the rule and Flaming Sphere is back.
- **REAC and DEF on the inventory screen:** REAC sits beside SP, DEF on the AC line.
- **Rule change, hiding in shadows to backstab:** a thief whose turn comes with no enemy beside
  them rolls hide in shadows, then move silently.
- **The cooked vulture quest:** take the cooked vulture to Dinos in the slave pens. He cooks it
  for the party, who eat with him.
- **32 new entries in the game's item name table,** for the Ledger's own items.

**Changed**
- **Turn pop-ups in the game are off by default,** and have three levels: at the least, in short,
  or in detail.
- **Spell slots** only show the spell levels the character can cast.

**Fixed**
- **Item names numbered past 255** were read wrongly by the Ledger (for example, Serpent Boots).

## Pull request #6 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/6))

**Fixed**
- **Boots gave no extra move:** the rule looked at the wrong equipment slot.

**Docs**
- README screenshots retaken (move silently, boots, Thieves' Tools, Options).

## Pull request #5 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/5))

**New**
- **A Give thieving tools now button** on the Options tab.
- **Thieves' Tools** get a name of their own and a leather satchel's picture instead of a key's.

**Fixed**
- Smaller: the arena ring, and the backpack cell the thieving tools went into; only one set of
  tools per thief; long lines on the Options tab wrap to the window.

## Pull request #4 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/4))

**New**
- **Picking pockets:** press P in a conversation, with a thief leading. Small things only; a move
  silently roll decides whether a fumble is noticed; a few coins when there's nothing else to take.
- **Thieving tools:** every thief starts a new game with a set.
- **Ring of Protection +1,** found on the Tied-up Prisoner in the arena.
- **Items named for the rule changes** ("Helm (AC 1)", "Boots (+1 Move)").
- **Thief skills as they stand:** equipment penalties and effects, in the game and in the Ledger.
- **Start the game from the Ledger's window,** and a triple-size game window.

**Fixed**
- Smaller: fights restarting or crashing after a pop-up's Continue; the arena's opening show; the
  Announcer's name being replaced by one learned mid-fight.

## Pull request #3 ([merged 2026-09-30](https://github.com/daaki85/darksun-obsidian-edition/pull/3))

**New**
- **In the game:** THAC0, saves and thief skills on the inventory and View Character screens;
  spell slots on the USE screen; each turn's rolls in the game's own window, with monsters' turns
  in a pop-up of their own; monsters' defences in the Look box.
- **Spells tab:** what every spell and psionic power does.
- **Launchers:** one for the game alone with the in-game additions, and one for the game and the
  Ledger together.
- **Script decoder:** every thief and ability check in the game's scripts.
- **The first rule changes:** helms give AC 1; boots give a move more in a fight.
- **Saving throws** with each modifier named.
- **THAC0** shown with each weapon, fresh on every redraw.
- **The Ring +1** (+1 AC and saves).

**Changed**
- **No packaged .exe:** the .bat files offer to install Python instead.

## Pull request #2 ([merged 2026-09-29](https://github.com/daaki85/darksun-obsidian-edition/pull/2))

**New**
- **The game's own portraits and font,** read from your install at run time.
- **A Characters tab** laid out like the game's View Character screen: each character's equipment
  by slot, effects with rounds or charges left, and spell slots.
- **Spell detail in the dice log:** damage formulas, durations and what a save does; rules for 20
  more effects; healing, Magic Missile and Slay Living dice labelled; Dispel Magic per effect.
- **Thief skill rolls,** with what each chance is made of.
- **Psionics:** powers named, PSP spent logged, magic resistance changes.
- **Saves:** the chance to save, and what the save left.
- **Dialogue:** the reply you picked, and named speakers.
- **The log at a glance:** round headers, hit chances, HP left, and a details switch.

## Pull request #1 ([merged 2026-09-28](https://github.com/daaki85/darksun-obsidian-edition/pull/1))

**New**
- **The party viewer,** reading Shattered Lands' character records live.
- **The dice log:** attack bonuses, weapons, saving throws, spells and buffs; kills and XP, weapon
  breaks, level-up HP and AC make-up; attacks from behind and backstabs (with the damage
  multiplier); each round's initiative order and how each score was made up; the two-weapon
  adjustment, and character creation rolls.
- **A dialogue tab.**
- **Accessibility** (AODA / WCAG 2.0 AA): contrast checked in tests, text size controls, full
  keyboard access, and logs you can save.
- **Double-click launchers** and a step-by-step Windows guide.
- **The name *Templar's Ledger*,** and a window in the game's colours.
