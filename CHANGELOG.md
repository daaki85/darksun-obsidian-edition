# Changelog

What changed in Obsidian Edition (called Templar's Ledger up to 1.2.0), pull
request by pull request, newest first.
Released pull requests are summarised in a line or two each; the release notes
([2.3.0](release-notes/v2.3.0.md): #44 to #46; [2.2.1](release-notes/v2.2.1.md): #43; [2.2.0](release-notes/v2.2.0.md): #39 to #42; [2.1.1](release-notes/v2.1.1.md): #37; [2.1.0](release-notes/v2.1.0.md): #35; [2.0.0](release-notes/v2.0.0.md): #31 and #32; [1.2.0](release-notes/v1.2.0.md):
#19 to #29; [1.1.0](release-notes/v1.1.0.md): #14 to #18;
[1.0.0](release-notes/v1.0.0.md): #1 to #13) and the pull requests themselves
have the detail.

## Pull request #49 (in progress)

**Changed**
- **A Battle Dancer starts with two long swords** (with kits on): a second
  long sword in the left hand, in place of the shield.
- **A Myrmidon's second weapon starts in the left hand**, in place of the
  shield, when it's a one-handed melee weapon (a bow still goes in the
  missile slot, a two-handed weapon in the backpack).

**Fixed**
- **A multiclass preserver could cast in armour** (class restrictions on,
  since 2.0.0). The USE screen said NO SPELLS IN ARMOUR, but the spells
  stayed in use: the helper asked about the wrong character, reading it from
  a register the game's own test had changed by then. It now reads the
  character the game asked about.
- **Yellow text on the character creation screen** (since 2.3.0). The game's
  screens print in a colour each leaves set; the creation screen never sets
  its own, and the mod's `SUM:` line printed in it, so after a character
  screen (whose selected portrait is yellow) the scores and the lines below
  them came out yellow. The creation screen's white is now set as it rolls.

## Pull request #48 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/48))

**Added**
- **Multiclass kits** (with Kits ticked): seven kits for two classes taken at
  once, each for one race only. Elf cleric/fighter: **Battle Dancer**, which
  dances as each fight starts (a d20 against DEX: +1 to hit, damage and AC
  for DEX less the roll in rounds, or −1 for 1d8 rounds); long swords and
  bows only, but any of them, whatever its cleric's sphere allows. Half-elf fighter/thief: **Shadowblade** (+10 hide, +5 move, −10
  pick pockets) and **Military Scout** (+10 to traps, move, hide and climb
  under the open sky, −5 under a roof). Half-elf druid/fighter: **Wilderness
  Avenger** (+1 to hit and damage against undead; hides and moves as a
  ranger). Half-elf cleric/ranger: **Rescuer** (cures heal 1 more a die under
  the open sky). Dwarf fighter/thief: **Ghetto Fighter** (+1 with a dagger;
  two weapons at 0 and −2; +5 pick pockets and hide, −5 traps) and
  **Wayfinder** (+10 hide and move, −10 pick pockets). Chosen on the
  creation panel's KIT page as a class's kit is.
- **The combat log below the map** (In the game, off by default): the game's
  screen 320 × 222, the log a strip under the map, always shown, in the
  panel's darker shade, covering none of it; the game's speed and the map's
  shape as ever. In a fight it shows the round and the newest line, between
  fights the two newest lines; the mouse wheel scrolls it a line a notch,
  with a **Latest** chip while scrolled back. It is kept up through the
  arena's opening show. Under a screen in other colours it is the panel's
  blue-grey, and black on the title, the main menu and in character
  creation.
- **Rolls out of fights in the combat log:** a thief's skills, a scroll
  learned, the hit points of a new level (the lines with a roll in them), in
  the panel and the strip alike.
- **An L in the panel's top line**, a button that hides it as the key does.

**Changed**
- **The combat log's panel is shown and hidden with L** (2.3.0 opened it in
  each fight and closed it at the end): it no longer opens by itself, and
  **L** on the map shows it or hides it, in a fight or out of one, to read
  back over the last fight or the rolls since. It stays as it was left, from
  one game to the next too. (L used to collapse it to one line; **-** does.)
- **Fuller starting gear for the game's own party too:** Gerakis, K'ratchek,
  Cermak and Cilla get what a new character would, in the first moments of a
  new game, after their other changes (Gerakis a sling, leather chest and
  leg armour and a dagger; Cermak and Cilla a dagger). K'ratchek, a thri-kreen, gets nothing more: she keeps the
  game's own chatkcha (see below).
- **Fuller starting gear gives no belt or boots, and a cloak only to a
  Stalker, an Assassin or a Shinobi** (2.3.0 gave everyone a belt and boots,
  and a cloak to every ranger).
- **The inventory screen's `HIDE` and `MOVE` count a worn cloak and boots**
  (with hiding to backstab and the cloak, boots and belt switch), for thieves
  and rangers and their kits alike, as the rolls do: 10 each, to no more than
  95, or the Cloak or Boots of Elvenkind's 95. The Characters tab's thief and
  ranger skills too. (A worn belt's 5 was already in `PICK` and `LOCK`.)
- **The view in a fight** (a switch, on by default): it no longer drifts after
  each figure that walks near the screen's edge, and moves only to bring back
  one that has walked off the screen.

**Fixed**
- **The backpack's dagger fought with** (fuller starting gear, 2.3.0): the
  Loader put the dagger for the backpack (and Thieves' Tools, the arena's
  Ring +1 and what's lifted from pockets) in the character's list of what it wears and
  holds, where the game counts every weapon as in hand, whatever cell it shows
  it in. So Gerakis fought with the dagger in place of his long sword, and
  Cermak struck with it as a second weapon. Items for the backpack now go in
  the backpack's list, as the inventory screen puts them; what the Loader
  takes in hand or puts away moves between the lists too; and games where it
  happened are put right the next time they're played out of a fight (the
  dice log says `... is put away in the backpack`).
- **The game quit ("Return code 01h") or froze in fights with the combat
  log on** (2.3.0): the routine drawing again all that moved, drawn in parts
  round the panel, went on afterwards from a way back that the parts' own
  drawing had overwritten (a variable the other probes share), so the game
  ran on from the wrong place, writing over its own memory (garbled names,
  stripes across the screen) until it quit. The way back is now kept on the
  stack while the parts are drawn.
- **A new thri-kreen given gear** with fuller starting gear (2.3.0): armour,
  a belt, boots or a cloak it can't wear, and a weapon and a dagger when its
  claws serve it better. A thri-kreen now gets nothing more than the game's
  own starting gear (K'ratchek her chatkcha).
- **The pointer over the combat log's panel** (2.3.0): the panel, put on over the
  pointer, hid it, and moving the pointer across the panel could leave a
  patch of the map or no pointer at all. The game takes its pointer off by
  putting back the map it kept from under it (without the panel). Now the
  panel is put on before the game draws its pointer over it (a probe in that
  routine), the pointer is drawn again after the panel, and the panel's
  regular refresh leaves the pointer's box alone. Held still over the panel
  for 48 frames, and moved across it, the pointer showed every time and no
  map came through.

## Pull request #46 ([merged 2026-10-15](https://github.com/daaki85/darksun-obsidian-edition/pull/46))

**Release**
- **Obsidian Edition 2.3.0** (pull requests #44 to #46): the version is
  2.3.0, with its notes in `release-notes/v2.3.0.md`, listed on the front
  page with the others.

**Added**
- **Fuller starting gear** (More character customization, on by default).
  Before a new character is first played, the Loader adds plain gear the
  character can use and hasn't got: a weapon in an empty right hand (from
  the backpack, as a cleric's club, else a plain one of its weapon spec or a
  short sword, club, mace, dagger or quarterstaff), a sling if it has no
  missile weapon (an earth or fire cleric a chatkcha), leather chest, arm
  and leg armour in empty places,
  a belt, boots, a dagger, and a cloak for a ranger or Stalker. With the
  class restrictions, a multiclass preserver's armour goes into the
  backpack, so it can cast. A thief/psionicist (its long sword left behind)
  and an air or fire cleric (its club) had started with no melee weapon.

**Changed**
- **An air cleric of one class may use daggers**, as its sphere allows:
  none of the game's daggers had the air cleric in its class list, so only
  Galefang would do (or another class's list, for a multiclass one). DSCLOG
  now adds it to every dagger type, the game's and the Loader's.
- **The documentation reviewed** for clarity and repetition: DEVELOPMENT.md's
  kits chapter moved among the other parts, after weapon specialization, as
  in the README; the README's new-item prices in a table, a preserver's
  first spells under a heading of their own, the requirements naming the GOG
  release only, and repeated "ticked by default" notes cut.

**Fixed**
- **The docs said a multiclass character gets each class's gear**: the game
  gives one class's, the first of fighter or ranger, cleric, thief,
  psionicist, preserver and druid (seen in play for each two-class
  combination a half-elf can take).
- **The combat log's panel flickered and lost pieces** as figures moved and
  fought: the game drew the map over it, a rectangle at a time, and DSCLOG
  only put it back afterwards. The rectangles the game draws again are now
  drawn round the panel, never over it, and before the screens flip the
  panel is put on the one about to show. (The old way of putting it back,
  through the redraw routine's way back, could also go stale if the game
  moved that code meanwhile.)
- **A fighter/druid kept the shield it can't use.** A New character's
  starting gear its classes can't use is left behind, but the last item of
  one of its lists was kept (as a container's must be): with the druid's
  armour gone, the shield was that item. A character's list may now empty,
  for the kits' gear too (a Ravager's shield, a Brute's club).

## Pull request #45 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/45))

**Changed**
- **The combat log in the game is on by default** (it was off until
  ticked): in a fight its panel shows the rolls over the map's lower right;
  **L** or its **-** button folds it to one line, and the Options tab's
  switch turns it off. Settings saved by an earlier version have it turned
  on once (`settings_version` 2 in `settings.json`); after that the player's
  choice stands.

## Pull request #44 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/44))

**Added**
- **A combat log in the game.** In a fight, a panel over the map's lower
  right shows the dice log's lines as they come, in the game's font and the
  Ledger's colours, with the round and who acts next above them; at the
  least, in short (the default) or in detail. An Options switch, off by
  default. It scrolls back over the fight: the scrollbar's handle, a page
  at a click on the bar, the mouse wheel over it (on Windows), and a
  **Latest** chip back to the newest lines. Its header has the level and
  - / + buttons: collapsed to one line, docked, or expanded with filters
  (All, Party, Damage, Saves); **L** collapses and opens it.
- **Saves under their names.** The Ledger keeps a second copy of every save in
  its **Named saves** folder, named as in the game (`Page 2 slot 05 - Before
  Scar's battle.SAV`), and the Options tab's new **Saves** section opens the
  folder and puts a named save back in a slot of the game's list.
- **Two magic shields.** **Gutterward**, a wooden shield +1, on a skeleton in
  the Tari's warrens; **Ironbulwark**, a metal shield +3 (the game has no
  metal shield: a type of the Ledger's), carried by the Guardian of
  Balkazar's fortress. Each has its icon, its price (25,000 and 65,000) and
  its story from Alagorn, in his shields' menu.
- **Three new wizard spells,** with the new spells on: **Reflected Image**
  (1st level, on the caster: one image, struck instead of the caster half the
  time; it and Mirror Image replace each other), **Spook** (1st level: one
  creature flees for 3 rounds unless it saves, at -1 for every 2 caster
  levels, at most -6; undead aren't affected) and **Friends** (1st level, on
  the caster: CHA + 2d4, at most 25, for 1d4 rounds and 1 a level, for better
  prices). Each has its icon (Reflected Image's a hand mirror, named on the
  Effects screen) and description; preservers and the Shinobi learn all
  three.
- **Defilers' scrolls:** each defiler in a fight has a 5% chance of carrying
  a scroll of a random preserver spell (the game's 69, and the new spells
  with them on), found on its body when it dies; rolled once a fight, and
  kept out of the dice log so it isn't given away. A New content box, on by
  default.
- **Buying back magical items:** a magical item sold to a merchant (a plus,
  or a power: rings, wands, scrolls) stays in the merchant's stock to buy
  back; the game destroys everything sold, and still does other items. An
  Expanded features box, on by default.

**Changed**
- **Templar's Ledger is now the Dark Sun Obsidian Edition Loader** (the
  Loader for short): the window's banner and title, the crash message in the
  game, and every page of the docs, which now call it what starts the game
  with the mod rather than a companion window. Its settings, named saves and
  crash reports stay where they were.
- **The folder is `obsidian-edition` and the Python package `dsloader`**
  (they were `darksun-companion` and `dscompanion`): `python -m dsloader`
  runs the command line, and the tests workflow is `tests.yml`.
- **More kits that can't go together:** the Grove Warden can't dual to
  gladiator, nor a gladiator who duals to druid take it (its AC would add to
  the gladiator's own); the Swashbuckler, Crusader, Battle Mage and Mind
  Warrior, each giving a warrior's THAC0, can't go with one another.
- **The Ravager and the Grove Warden can't go together:** a human who has
  one isn't offered the other after DUAL (each has an AC of its own that
  betters with level, and they would stack).
- **The Stalker and the thief:** a human Stalker can't dual to thief, and a
  thief (with any thief kit or none) who duals to ranger isn't offered the
  Stalker kit: its +15 to hiding would add to a thief's own skills.
- **EMS off in the launcher's DOSBox settings:** GOG's settings turn on EMS,
  whose 64 KB page frame left the helper 1 KB of upper memory; the
  launcher's config now turns it off (the game uses XMS instead), giving the
  helper a 64 KB block more, with conventional memory unchanged (632 KB).
- **Kits in the docs, class by class:** the README's one table of kits is now
  a table for each class, under a heading of its own, with the level each
  part of a kit comes at (the Myrmidon's mastery at 5th level and grand
  mastery at 9th, the Ravager's AC, the Seeker's and Shinobi's slots, the
  Crusader's, Mind Warrior's and Battle Mage's attacks, the Grove Warden's
  AC), each kit's starting gear and what else a player should know (the
  classes and kits it rules out, where its choices are made); the player
  guide's class sections have the same full rows.
- **The player's guide is now `PLAYER-GUIDE.md`** (it was `GUIDE.md`), so its
  name says what it is; the links to it follow.
- **The leader's CHA at shops:** 5% off from CHA 18 and 5% more for each
  point after, to 40% at 25 (it was 5% at 16 to 25% from 20); shops pay 60%
  of an item's price when the party sells (the game paid all of it, which
  with the discount let anything bought be sold at a profit).
- **Fogbolt's icon is grey** (its cloud on Armor's grey tile, rather than
  Charm Person's purple).
- **The Shinobi can learn Fogbolt,** a 1st-level spell on its list beside the
  game's five, with the new spells on: offered at a level up as the others
  are, and cast at the thief level less 5 as they are.
- **The bone and obsidian axes weigh 30** (35 and 70 before), the game's
  heaviest a weapon can be without being HEAVY: they are no longer HEAVY, so
  either can go in the off hand with another weapon, and both can backstab.
  The metal Axe is the game's own, 70. Drakejaw and Glasshewer, of those
  types, weigh 30 too.

**Removed**
- **Each turn's rolls in the game's dialogue window** (the "Show each turn's
  rolls" switch and `--popups`): the combat log shows them without stopping
  the game. The game is no longer patched in its combat loop for them, and
  DSCLOG is about 1 KB smaller.

**Fixed**
- **The dice log stopped in a fight whose round order named someone it
  couldn't match** (seen in the arena's opening show, the Defiler and a
  Slig): the turn's lines now pass over that entry.
- **The new spells' records shared memory with a stack.** The game kept a
  small stack where Cat's Grace, Erdlu Claw and Fogbolt's records are; the
  helper now moves it (and the monster kinds table) into its own memory as
  the game starts, which also makes room for the three spells above.
- **New preservers weren't offered their spells.** DONE on the creation
  screen gave a new preserver (single or multiclass) the game's own starting
  spells instead of CHOOSE A SPELL: the check meant to leave START GAME's
  ready-made party alone read the character's status, which says Okay for a
  character being made too. It now tells the two apart by where the game's
  spell grants were called from.
- **Stuck on the creation panel's KITS page.** A single-class warrior on the
  last weapon page has KITS for its button; adding a class there (a fighter
  made fighter/thief) kept the button, and pressing it opened a page with no
  kits, titled KITS, whose KITS button opened the same page again. The last
  weapon page now changes its button to VIEW PSIONICS as soon as the
  character can no longer take a kit (and back to KITS if it can again), and
  KITS pressed for a character with no kit class goes back as VIEW PSIONICS
  does.
- **A kit lost on a new roll.** The die's new roll takes a kit away when the
  character's classes aren't the ones the panel last saw, which it learns
  from a click on a class. A new character's default class is never clicked,
  so a fighter given a kit (a Myrmidon, with its two specializations) and
  then rolled again lost the kit, and with it the second specialization. A
  kit chosen now records the classes it goes with.
- **The panel after a new race or sex.** The creation screen empties the
  classes, opens the panel for a character of no class, then puts the default
  class back without a click: a fighter was left with the game's VIEW SPHERES
  (which did nothing) where WEAPON SPEC belongs. The panel now follows the
  class put back.
- **Starting gear the classes can't use.** A character of several classes
  started with each class's gear, what it couldn't wear in the backpack (a
  fighter/druid/thief's leather armour, which a druid can't wear). With class
  restrictions, a new character's weapons, armour and shields its classes
  can't use are left behind, and the dice log says so.
- **A missile weapon's line on the inventory screen** showed the weapon's own
  rate of fire and no specialization bonus (a staff sling specialist's `1D4`).
  It now shows the rate and the bonus the attack uses (`1.5x1D4+2`).
- **A helm's item box said AC BONUS:0** (beside its name's "(AC 1)") until it
  had been worn: the rule set the helms' AC only as the game added up a
  character's. The box now sets it too, and shows 1.
- **Doors with charges.** A door's box (and a mirror's, a crank's) could say
  `Charges: 10`: the charges line read bytes that, in scenery, hold something
  else. Scenery no longer gets the line.
- **The Cloak of Protection forbidden to druids.** Its type counts for AC as
  armour does, so class restrictions took it for armour, which a druid (a
  fighter/druid/thief too) can't wear. It's a cloak, for every class.
- **A polearm's item box ran out of the box.** The game's Polearm picture is
  36 pixels tall, where every other item's is 22 at most, and the box puts its
  lines below the picture: the damage line (Thornwall's, Linebreaker's, the
  game's own bone polearm's) fell outside. The Ledger now writes the polearms'
  picture at 22 pixels.
- **The Trustee stuck at "I have to get back to work".** The game makes him
  busy after a talk until his rounds of the pens bring him back to their first
  corner; when his rounds stall (he can't reach his next corner), he stays busy
  for good and never talks again. What stalls them: a thief with no room for
  his stolen key drops it at his feet, and after each step of his rounds he
  makes for it ("There it is!") without picking it up. In the Ledger's copy he
  leaves the key where it lies (the party can pick it up), and he says the
  busy line once and is free to talk the next time.
- **Rows of the creation panel's weapon and kit pages took clicks only at
  their left.** Each row is a copy of the game's AIR row, a button 33 pixels
  wide: a click on the rest of a longer name (the middle of MYRMIDON or LNG
  SWORD) did nothing. Each row's button is now as wide as its name.

**Documentation**
- **A review of every page for this pull request's changes.** The README's
  picking pockets section tells of the Trustee's key, its class restrictions
  that a cloak isn't armour, its kits that a new roll keeps the kit, its new
  items the axes' weight, its Options list the Saves section and its More
  saves `cloud_saves`; the More character customization table gains STORE and
  RECALL, which has a box too. A backstab's weight limit is a metal long
  sword's 40 (it said a long sword's was 20), and the AC and saves lines point
  to the rings of protection rather than "the Ring +1". The guide's Equipment
  has the obsidian axe backstabbing and cloaks for every class, and its Ledger
  list the named saves; both overviews mention them. DEVELOPMENT.md has the
  scenery and cloak checks, the kit kept through a roll, the rows' width, the
  polearm's picture, the Trustee's two script changes (his script is now
  10,967 bytes), the named saves and the `checks` command.
- **A second review, after the combat log:** the overviews name the combat
  log, the six wizard spells, buying back and defilers' scrolls; the top
  README's overview is a short list linking to the full one; the last
  mentions of the turn pop-up are gone; the kits' starting gear is said once,
  in each class's table, not again in a table and list of its own; the
  Options tab's new spells box names all six, and its screenshot is retaken.
- **A third review, after the rename:** the full README puts **In the game**
  (the combat log first) before the Loader's window, and its overview is a
  list as the top README's is; the player's guide starts with the combat log;
  the patch notes put the game's changes first and the Loader after them;
  DEVELOPMENT.md has the combat log under How each part works and Room in the
  helper as a section of its own (they were inside Kits), and a Shinobi table
  split by a paragraph is whole again; "viewer" is gone from the docs.
- **The polearms' icons** in the README's item tables (the bone and metal
  Polearm, Thornwall, Linebreaker) are redrawn at the 22 pixels the game now
  shows them at.

## Pull request #43 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/43))

**Release**
- **Obsidian Edition 2.2.1:** the version is 2.2.1, with its notes in
  `release-notes/v2.2.1.md`, listed on the front page with the others.

**Added**
- **A switch for the elves' and half-elves' looks:** **Elves have pointed
  ears, and half-elves figures of their own** in the Options tab's Graphics
  section, on by default, from the next time the game is started. Off, elves
  are as the game draws them and half-elves the human figures in their own
  colours, as before 2.2.0.
- **A switch for Cilla's elf figure** in the Graphics section (on by
  default): off, she keeps the game's half-elf woman's figure, from the next
  start.
- **A switch for STORE and RECALL** under More character customization (on by
  default): off, the creation screen is the game's, from the next start.
- **Restore defaults** at the bottom of the Options tab sets every switch
  back, after asking.

**Changed**
- **The Options tab's headings are plain names** (In the game, Rule changes,
  More character customization, Expanded features, New content, Graphics,
  Controls, Game speed), with one line above them saying that everything
  applies in games started from the Ledger and that a switch marked "from the
  next start" waits for the game to be started again. The elves' and
  half-elves' looks come first in Graphics.

## Pull request #42 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/42))

**Release**
- **Obsidian Edition 2.2.0:** the version is 2.2.0, with its notes in
  `release-notes/v2.2.0.md` (pull requests #39 to #42), listed on the front
  page with the others; the patch notes say 2.2.0.

## Pull request #41 ([merged 2026-10-14](https://github.com/daaki85/darksun-obsidian-edition/pull/41))

**Added**
- **STORE and RECALL on the creation screen,** as Baldur's Gate has them:
  STORE keeps the roll on screen (the six scores and the die's total, the
  hit points and PSP), RECALL brings it back however many times the die has
  been rolled since, AC and damage shown with it. Changing the race, sex,
  classes or kit forgets the stored roll. The two
  buttons are carved like the game's own, under the hit points; the dice
  log's ring is 84 entries (was 88) to make room in upper memory.
- **Half-elves have their own figures** on the map and in fights (the game
  draws them with the human pictures). The man is built on the elf's figure,
  a little broader, with short fair hair, a linen shirt under a leather
  jerkin, green trousers, brown boots and small pointed ears. The woman is a
  little slimmer than the human woman, with her golden hair in a bun, pointed
  ears, a purple cloak, purple wristbands and red boots. Worn gear is drawn
  over them as on the figures they were made from: armour on his clothes, a
  worn cloak in place of her purple one (shaded as the human woman's), a
  shield on the forearm in a fight.
- **Elves have pointed ears,** walking and fighting, beside any helm.

**Changed**
- **The Options tab in four groups:** **Rule changes** (the game's rules
  closer to AD&D), **More character customization** (weapon specialization,
  kits, levels up to 10), **Expanded features** (the leader's CHA at shops,
  and **Improved thieving**: AD&D's thief skills, hiding to backstab, the
  cloak, boots and belt, picking pockets) and **New content** (now with the
  new wizard spells). The Thieves section is gone, its switches under
  Improved thieving; each switch keeps its setting.

**Removed**
- **P in a conversation** for picking pockets: Thieves' Tools are the way to
  pick a pocket. The game is no longer patched where the conversation window
  passes on a key, and DSCLOG's handler for it is gone.

**Fixed**
- **Cilla looks like the elf she is.** The game's own party gave her the
  figure for half-elf women; she has the elf woman's now, in a new game and
  (from the next area) in one already begun.

**Documentation**
- **Graphics** is the README's section for what the Ledger draws on the map
  (was "On the screen"), with a part for elves and half-elves; the Options
  tab's section has the same name, and DEVELOPMENT.md a section of its own
  for how elves and half-elves are drawn.
- **The patch notes have a table of contents,** as their web page does.
- **The README in the Options tab's groups:** Rule changes, More character
  customization (STORE and RECALL with it), Expanded features with Improved
  thieving, and New content (the new wizard spells first). The guide's
  Options table and both READMEs' overviews follow, and the Options tab's
  screenshot is new.
- **The game's own party** is under More character customization (its
  weapon specs and Cermak's kit), and points to Cilla's elf figure; the
  bracers and robes are parts of New items; the README says "hiding to
  backstab" where it said "the stealth rule"; DEVELOPMENT.md's "How each part
  works" follows the README's order; the patch notes' Thieves section is
  **Improved Thieving**.
- **The patch notes' items, one by one,** in four groups: magic weapons
  (fifteen, each with what it is, and the Elven Leader's Gythka +2), magic
  armour and worn items (Inixhide among them, missing before; Arrowbane and
  the Sunking Crown said not to be armour), other magic items (the Tome and
  Kalzith's six scrolls, by name) and mundane items (Thieves' Tools among
  them).
- **"Weapon type" throughout,** where the pages said "kind of weapon" or
  "weapon kind": fighters specialize in one weapon type, gladiators in two,
  the level-up window has a picture of each weapon type, and the item tables'
  Kind column is Type.

## Pull request #40 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/40))

**Documentation**
- **Semyon as the game tells him.** The README called him "of the Veiled
  Alliance"; in the game he is a slave tied up for asking after it, "much more
  of a scout than a warrior", who takes the party for the Alliance and asks to
  join. His section now says so, in his own words from the arena, as does the
  description in the Ledger's code.

## Pull request #39 ([merged 2026-10-12](https://github.com/daaki85/darksun-obsidian-edition/pull/39))

**Added**
- **Two new wizard spells, and Cat's Grace is a spell of its own.** Erdlu
  Claw (1st level: 5 rounds a caster level, natural and unarmed attacks do
  1d6+1 where that's better, or Body Weaponry's and Animal Affinity's dice +1,
  are +1 to hit and count as a +1 magical weapon) and Fogbolt (1st level: a
  dark grey bolt of its own, so Magic Missile's stays blue, which needs a clear
  line to its target; 2d4 rounds unless saved against, -3 to the fogged
  creature's attacks and +2 to attacks on it). Each has its own sounds: Cat's
  Grace Haste's, Erdlu Claw Shocking Grasp's, Fogbolt Fog Cloud's (Cat's Grace
  and Erdlu Claw, cast on a party member's portrait, show the game's usual
  star). Cat's Grace no longer takes
  Flaming Sphere's place: the three are spells 196-198, learnt, listed, cast
  and shown on the Effects screen like the game's own, each with its icon and
  description; who knows them is kept in the character's sheet. The switch is
  **New wizard spells** (was Cat's Grace). The dice log's ring is 88 entries
  (was 96), so the helper still fits in upper memory.

**Changed**
- **Multiclass hit points follow Demihuman Deities (TSR 1998).** CON's bonus
  goes on every hit die (a warrior's +3, +4... on every die if one of the
  classes is a fighter, gladiator or ranger, else at most +2) and the running
  total is divided by the classes. The rule used to divide each die on its own
  and then divide CON's bonus, which the game counts only once a level of the
  highest class, by the classes again: a fighter 9 / preserver 10 / thief 10
  with CON 18 got 12 hit points from CON, now 38.
- **The level-up weapon window shows the weapons.** Picking a weapon spec at a
  level up (or on becoming a warrior by DUAL), the window is bigger and has a
  slot with each weapon type's inventory picture, six to a row, in place of the
  names; types the character can't pick are greyed. Pointing at a slot names
  it under them (SPECIALIZE IN / DAGGER, or EXPERT IN for a ranger or a
  Battle Mage, whose picks are expertise), as CHOOSE A SPELL names a spell.
- **View Character: the saves labelled, MOVE added.** The five saves under
  the item icons each have their label (PPD, RSW, PP, BW, SP, as on the
  inventory screen) in place of one unlabelled SAVE line; THAC0 moves down
  beside PSI, and MOVE (the character's movement) is new, beside HP.
- **Rangers and Twin-blades fight with two weapons at no penalty only in light
  armour** (with the two-weapon rule): every armour piece worn, a helm too, of
  leather or of no material. In other armour they take AD&D's -2 and -4, as
  anyone does; the dice log and the Characters tab say the same. A Justifier
  has no penalty in any armour, a bonus of its own.
- **Cermak is an Arcanist** in the game's own party (with kits), his gear and
  hit points as the game gives them. Gerakis has no kit.

**Removed**
- **Boots no longer give a move in a fight.** The rule was a leftover from
  trying out changes to items; its switch is gone, boots are plain "Boots"
  again (games where they were "Boots (Speed+1)" get the game's names back),
  and the Characters tab's move shows only a kit's extra (the Stalker's).

**Fixed**
- **A save line read as if the save succeeded** ("Thrikreen saves vs Fogbolt
  ... -> failed"). It is now the creature's saving throw, then the result:
  `Wild Mul's saving throw vs Fogbolt from Daaki (spell): d20 = 16, needs 14
  (35% to save) -> saved`; "cannot save" and "saves automatically" read
  `none allowed (cannot save) -> failed` and `not needed (saves
  automatically) -> saved`.
- **The dice log showed XP for every kill,** the creature's value from its
  character sheet, even where the party gains none (the opening fight in the
  arena, whoever dies). A kill now reads "Rampager is killed"; the XP shows
  only on the "XP: ..." line, when the party's XP really goes up.
- **EXIT on CHOOSE A SPELL did nothing** when a new preserver picked its
  starting spells (or a human its spells on becoming a preserver): the window
  only opened again. EXIT now ends the picking, and the spells still to pick
  are the game's own starting spells, less any already picked.
- **The game's own party had to pick spells.** Starting a game with no party
  made, Cermak and Cilla were put on CHOOSE A SPELL as a new preserver is.
  They keep the game's own spells again; only a character made on the
  creation screen (still New) picks.

**Documentation**
- **The new spells' screenshots:** their three descriptions, the Effects screen
  with Cat's Grace and Erdlu Claw, and Fogbolt's bolt replace the two Cat's
  Grace pictures; the Options tab and a spell's end-of-turn window (a Fogbolt,
  where it was a Cone of Cold save with the doubled d20) are retaken.
- **A review of every page.** The README's main screenshot (the dice log of
  the arena's opening show) is retaken without the kill XP it no longer shows,
  and the Options tab's with every rule switch. The README gains a Characters
  tab section (spell slots, AC and scores, which had trailed after the Options
  tab), the missing "Scores and hit points as rolled" in its contents, a
  clearer list of what play writes to the game folder, and the kits' details
  in one list; notes on how things were tested and the old release names are
  gone. The guide has its first pictures (the dice log, the weapon window) and
  no longer says the game's own party has no weapon specs. DEVELOPMENT.md
  points to the README for the kits' table, says what the helper's memory is
  now rather than how it got there, and drops the kits' build diary.
- **Screenshots retaken where they had fallen behind:** the inventory, the
  tome and the game's own party (the off hand at one attack a round, not 1.5),
  the creation screen's weapons page (with the scores' total under CHR), the
  gear boxes (plain boots), the figures' gear (now with shadows), Kalzith's
  shop (the leader's CHA discount) and the Options tab (no boots switch).

## Pull request #38 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/38))

**Release**
- **The release zip is `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`**, unzipping to a
  folder of that name, to match the releases' title (it was
  `Obsidian-Edition-<version>.zip`).

## Pull request #37 ([merged 2026-10-10](https://github.com/daaki85/darksun-obsidian-edition/pull/37))

**Release**
- **Obsidian Edition 2.1.1:** the version is 2.1.1, with its notes in
  `release-notes/v2.1.1.md`, listed on the front page with the others.
- **Releases are titled "Dark Sun: Shattered Lands - Obsidian Edition"** and
  the version, rather than "Obsidian Edition" alone.

**Fixed**
- **The dice log missed character creation rolls:** the die rolls a whole
  character many times while it tumbles, more rolls than the log could read,
  so abilities often came as "its rolls came too fast to record". The helper
  now keeps each ability's last four 4d4 itself, and the log reads them when
  the die stops; the rolls missed meanwhile are no longer mentioned.
- **Raising CON on the creation screen didn't raise the hit points** (lowering
  it could lower them): the game only kept them within the new range. With
  Scores and hit points as rolled, a change of CON now adds or takes off its
  bonus for every level, as the game counts it.

## Pull request #36 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/36))

**Release**
- **Obsidian Edition 2.1.0:** the version is 2.1.0, with its notes in
  `release-notes/v2.1.0.md` (pull request #35), listed on the front page with
  the others.

## Pull request #35 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/35))

**Added**
- **Scores and hit points as rolled** (a new rule, on by default, its own box
  on the Options tab): on the creation screen a click raises a score only
  while the six add up to no more than the die gave, so lowering one frees
  points for another, and a click on the hit points does nothing. Under CHR
  the screen shows the six's total and the die's (`SUM:99/101`); a new class
  that raises a score to its minimum raises the die's total with it. The dice
  log adds each roll's total (`Character creation: the six scores add up to
  101`). No interrupt vectors were left, so the new sites share the one for
  choosing a preserver's spells, a site number after the `INT`.

**Fixed**
- **A click on a score on the creation screen stopped the game** (since
  2.0.0): the Mind Warrior's PSP check at the end of the game's PSP routine
  returned with interrupts off, and from a score's click nothing turned them
  on again. The flags are now put back.

**Removed**
- **Turning the mouse wheel** no longer scrolls the map (the Ledger's Windows
  mouse hook is gone); pressing the wheel and dragging still does.

**Documentation**
- **Patch notes** (`PATCH-NOTES.md`, and `patch-notes.html` as a page with a
  copy-as-Markdown button): every change from the original game, laid out as
  patch notes, to share online. Linked from the front page.

## Pull request #33 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/33))

**Release**
- **Obsidian Edition 2.0.0:** the version is 2.0.0, the first release under
  the new name, with its notes in `release-notes/v2.0.0.md` (pull requests #31
  and #32), listed on the front page with the others.

## Pull request #32 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/32))

**Documentation**
- **All the documents reviewed:** the front page and the README name AD&D's
  class tables, the leader's CHA and the robes among the rules and items, and
  the README's rule count (21), item and price tables and Kalzith's shop are
  up to date; the guide's gladiator AC (with or without armour) and the
  game's priest THAC0 are corrected, and its "What the Ledger shows you",
  which the quality of life table already covers, is gone; DEVELOPMENT.md's
  kits are no longer "being built", its parts follow the README's order, and
  the shop's NO DEAL! and the CHA rule's check in the game are there.

## Pull request #31 ([merged 2026-10-09](https://github.com/daaki85/darksun-obsidian-edition/pull/31))

**Added**
- **Kits:** a character of one class may take one of three kits
  for its class, or none, on the creation panel's new KIT page (KITS, at the
  end of the panel's pages: the disciplines' for a class with no sphere, the
  spheres' for a cleric, druid or ranger, the last weapon page for a warrior
  with weapon specialization), NO KIT first and what a new character has, the
  rows not chosen greyed as the spheres' are. The kit is kept with the
  character (sheet `+43h`), and the Effects screen (`KIT: RAVAGER`) and the
  Ledger's Characters tab name it. A new switch on the Options tab, under Rule
  changes.
- **What the kits do:** the Myrmidon, Sentinel and Ravager (fighter); the
  Arena Champion, Twin-blade and Brute (gladiator); the Stalker (ranger); the
  Assassin (thief); the Grove Warden and Wanderer (druid); the Lifebinder's
  weapons, and the Shinobi's weapons and armour. The guide's
  Kits has what each does. The dice log and the Ledger show each kit's part; a
  new probe in the game (INT B8h) makes the Sentinel's initiative.
- **Kits' THAC0:** the Swashbuckler, Crusader, Battle Mage and Mind Warrior
  get a warrior's THAC0, the Scholar's is 1 worse, through a new probe at the
  end of the game's THAC0 routine (INT B7h); the Swashbuckler's −10 to every
  thief skill, named in the dice log's thief skill lines as the Assassin's
  now is.
- **Kits' spell slots:** the Arcanist's wizard slots 1 more at each spell
  level, the Battle Mage's and Crusader's 1 fewer, the Elementalist's a level
  behind, the Seeker's and Justifier's priest slots their own tables, through
  two new probes in the game's slot routine (INT B6h, INT B5h); the Ledger's
  Spells tab counts them the same way.
- **Kits' PSP:** the Mind Bender's telepathy powers (the defence modes too)
  cost 2 PSP less to use and to keep up and its psychokinesis 2 more, the
  Kineticist's the other way about, through new probes where the game prices
  a power (INT B4h, B3h, B2h, B0h, AEh).
- **Kits' healing:** the Healer's Cure Light, Serious and Critical Wounds heal
  1 more a die, and the Lifebinder's cures heal a die more (INT B1h); the dice
  log shows each. The Healer may hold no weapon in the off hand.
- **The Battle Mage** casts though hit earlier in the round (the game stops
  anyone else: INT ADh), and holds nothing in the off hand.
- **Kits' casting level:** the Seeker casts at its ranger level less 5 and the
  Justifier less 9 (a ranger's: less 7), which also lets a Seeker of 6th level
  choose 1st-level priest spells for its slots (INT AFh). The level a
  spell's duration and damage take, which the game works out apart from
  that (with a ranger's whole level), now has the kits' too (INT A6h).
- **Rangers' casting level (a rule, on by default):** a ranger's spells last
  and do damage as cast at its level less 7, as the spell levels it may cast
  already count it; the game took the whole ranger level (a 9th-level
  ranger's spells lasted as a 9th-level priest's). A multiclass ranger casts
  at the better of its classes, the ranger's counted 7 less (INT A6h).
- **The Shinobi's spells:** preserver spells from 6th thief level on the
  Seeker's slots, cast at the thief level less 5, from its own list of 14:
  one learnt at each level up from 6th, on the game's CHOOSE A SPELL screen,
  which shows its spells only, up to the spell level it casts; none learnt
  from scrolls (INT ACh, A8h, A7h, ABh, AAh, A9h, and the level-up's probe).
  The Ledger's Spells tab shows its slots.
- **The Scholar** learns a spell more at each level up: CHOOSE A SPELL comes
  up twice.
- **The Battle Mage's weapon and armour:** it wears light armour (leather, or
  none) and casts in it; with weapon specialization it chooses one weapon spec
  (long sword, club, dagger, short sword, mace, axe or pick) on the weapon
  pages, which the panel now offers it, may use those weapons as well as a
  preserver's own, and attacks with them at expertise's rate, 3/2 a round (2
  from 7th level). The game's equip check, the fight, View Character's and the
  inventory's DAM lines, the Effects screen (EXPERT IN) and the Ledger all
  count it.
- **The Elementalist's second sphere:** chosen on the creation panel's
  CLERICAL SPHERE list once the kit is taken (a second row marked beside its
  own), its spells known from the start, as its own sphere's are, cast at its
  cleric level, and its weapons allowed as well as its own sphere's (INT A1h,
  A0h, 9Fh, 9Eh). The Characters tab names it. Every kit now works.
- **The Seeker's weapons** are its sphere's, as a cleric's of that sphere,
  but for the bow, on the weapon pages and when equipping. **The Justifier's**
  expertise with the bow and its chosen weapon spec is specialization (+1 to
  hit, +2 damage), with weapon specialization.
- **Kits' hit dice and PSP:** the Battle Mage rolls a d6 for its hit points,
  the Mind Warrior a d8 and has a tenth fewer PSP (rounded down), and the
  Arcanist a d3, at each level up and on the creation screen: choosing or
  taking back one of these kits rolls the new character's hit points and
  works out its PSP again (the game did both only when a class was clicked),
  and the screen shows the new numbers (INT A5h, A4h, A3h, A2h). The dice
  log's hit point lines name the kit's die.
- **A kit sleeps when a human dual-classes** (DUAL on a portrait's menu), as
  the class it was chosen with does, and wakes, gifts and costs, once the new
  class's level passes the old one's. The Effects screen adds (ASLEEP) after
  the kit and the Characters tab names the level to pass. Awake, it goes by
  its own class's level; its hit die counts only for its own class. A Battle
  Mage's chosen weapon spec stays the kit's (expertise when awake, nothing
  while asleep), not a new fighter's specialization.
- **Classes a kit bars on dual-classing,** greyed on the DUAL window (INT
  9Dh): a Seeker or Justifier can't become a cleric or druid, a Shinobi a
  preserver (their own slot tables would replace the new class's); the
  Swashbuckler, Crusader, Battle Mage and Mind Warrior no warrior class (they
  have a warrior's THAC0 already); an Arena Champion or Sentinel no druid or
  preserver (no shield); a Brute no psionicist or air cleric (no two-handed
  melee weapon).
- **Weapon specs are weapons learnt for good,** while the class or kit that
  gave them is awake: no kit forbids a weapon type the character specialized in (but
  for the off hand's rules). A dual-classed human's chosen weapon types sleep with
  their class, as before, and come back when it wakes.
- **A human who becomes a preserver picks its two spells** on the game's
  CHOOSE A SPELL window (1st level only), not Grease and Magic Missile (INT
  9Ch).
- **Kits for a human's new class:** after DUAL, the game's three-choice menu
  asks for the new class's kit (**KIT: NONE**, then its kits; one barred by
  the character's other classes or kits left off), and a new Elementalist's
  second sphere; with weapon specialization a new fighter, gladiator, ranger
  or Battle Mage then picks the weapon types it is due, as at a level up. Up
  to three kits, one for each class, each asleep with its class. A human
  who becomes a preserver and takes the Scholar kit picks three spells, not
  two. Kits that can't go together (Arena Champion or Sentinel with Shinobi;
  Twin-blade with Healer; Brute with Shinobi or Lifebinder), and kits a class
  bars, both ways (INT 99h).
- **The Effects screen a page at a time:** its lower panel has room for five
  lines, too few for three kits and a gladiator's weapon specs. A kit takes
  one line (the long names shortened as on the KIT page, "(ASLEEP)" after one
  that sleeps), and when there are more than five lines the panel shows four
  and MORE: CLICK HERE; a click on it shows the next page, a weapon spec's
  heading carried over with its weapons (INT 97h).
- **A new preserver picks its starting spells** on CHOOSE A SPELL when DONE
  is clicked on the creation screen (two 1st-level spells at 1st level, four
  at 2nd, four and two of 2nd level at 3rd; a Scholar one more a level), in
  place of the ones the game handed out (INT 98h).
- **The Stalker hides in shadows indoors** with its full chance (the stealth
  rule halves a ranger's indoors).
- **Starting gear fitted to the kit:** the game's class gear, given at DONE,
  is changed while the character is new where the kit can't use it: a
  Shinobi's long sword becomes a bone short sword, a Brute's a bone great axe
  (its club to the backpack), a Seeker's of its sphere's material, a
  Ravager's shield is taken away (a kit that can't use a shield has no use for it in
  the backpack); an Arena Champion's off-hand club
  becomes a shield, and a Battle Mage's quarterstaff its weapon spec's weapon.
  The dice log names each change. The guide lists each class's starting gear.
- **Two magic robes** for preservers, psionicists and druids, worn on the
  chest and not armour (cast in them; their AC with no armour worn, as
  bracers'): the **Ashen Robe** (+1 AC, +1 on saves against spells), which
  Kalzith wears and sells and leaves when killed, and the
  **Veiled Robe** (+2 AC, +1 on every save, a wizard slot more at spell levels
  1-3), sold by Kel. Drawn icons, Alagorn's stories, the Ledger's saves and
  slots count them.
- **The Warden's Plate's AC explained:** 12 points better as a set (the
  helm 2: a helm's AC 1 and its +1), not "AC 11".
- **Kits' starting gear, more:** a Myrmidon gets a plain weapon of its
  second weapon spec as well (in the backpack; a bow in the missile slot,
  with arrows), a Ravager a second of its weapon for the hand its shield
  left (none for a two-handed one), and a Brute's club is left behind
  rather than carried.
- **Charges in an item's box:** a wand, the Storm Ring or a necklace shows the
  charges it has left (`Charges: 50`) in its item box.
- **Preservers' INT**, a new rule change (on by default): AD&D's table for
  INT gives a preserver a chance to learn a spell from a scroll (35% at INT
  9 to 100% at 24; a failed try uses the scroll up) and the most spells of
  each spell level it may know (6 at INT 9, all from 19), which also limits
  CHOOSE A SPELL at a level up. The dice log shows each try.
- **The leader's CHA at shops**, a new rule change (on by default): the
  party leader's CHA lowers what shops ask, as Baldur's Gate's table has it
  (5% at CHA 16 to 25% from 20), in the price shown, the price charged and
  the list's greying of what the party can't afford; selling unchanged.
  Through two new probes (INT 8Dh, 8Ch).
- **The guide's races:** each race's range of scores, and why a half-giant's
  large penalties give the Dark Sun book's caps.
- **AD&D's class tables**, a new rule change (on by default): AD&D's XP
  tables (a gladiator's and ranger's 2nd level 2,250, a thief's 1,250; the
  game had a gladiator on the fighter's), priests' THAC0 (2 better every 3
  levels from 4th; the game's from 3rd) and spell slots (AD&D's priest table
  for clerics and druids, its wizard table for preservers), through three new
  probes (INT 90h, 8Fh, 8Eh). Hit points were AD&D's already. The guide has
  the tables.

**Changed**
- **The mod is now Obsidian Edition.** Templar's Ledger stays the name of its
  companion window. The launcher is `Start Obsidian Edition.bat`, releases are
  `Obsidian-Edition-<version>.zip`, and crash reports are headed "Obsidian
  Edition crash report".
- **Kalzith** wears his Ashen Robe, Cloak and Quarterstaff from the start and
  sells them with his scrolls (the game's shops sell all a merchant carries, worn
  or not; nothing marks an item not for sale). He is sold out once he carries
  nothing; killed, he leaves what he still has and one of his scrolls.
- **The helper loads into upper memory again,** leaving the game 62 KB more
  conventional memory (632 KB free, was 570): the dice log's ring buffer now
  follows the helper in a segment of its own, so the helper's image is 40 KB
  (was 63) and what it asks for fits DOSBox's upper memory. It also leaves
  room in its segment for the kits' code.
- **Two weapons:** the off hand attacks once a round, whoever holds it; the
  extra attacks (the game's 3/2 for warriors, specialization's, the kits')
  are the main hand's. The game gave each hand the whole rate.
- **A kit for each class:** the kit byte keeps two bits for each of a
  human's classes, so a human who changes class can have up to three kits;
  every kit rule, in the helper and the Ledger, now asks for each kit the
  character has awake, and the Effects screen lists them all. Characters
  made before read as they did.
- **The Arcanist casts two preserver spells in a turn** in a fight: its first
  doesn't end the turn (a hit still keeps it from a second).
- **The Crusader and Mind Warrior** have a warrior's extra attacks in melee:
  3/2 a round from 7th level of the kit's class, whether weapon
  specialization is on or not (the DAM lines and the Ledger's party view show
  them too).
- **The Ravager's base AC** is described only up to 10th level, the highest
  the game goes.
- **The Arcanist's drawback** is a d3 hit die (a preserver's is a d4), in
  place of −2 CON.
- **The dice log's ring holds 96 entries** (was 128), and the helper's text
  buffer is 4 KB (was 8), making room in upper memory for the kits' code.
- **The helper's interrupts** are now 8Ch to FEh (and 60h to 65h); the
  message when they are in use says so.

**Fixed**
- **A kit or a second sphere could change a sound.** The game reads two sound
  numbers on the character sheet (`+42h`, `+44h`) as words, and the kit
  (`+43h`) and second sphere (`+45h`) sit in their high bytes; they are read a
  byte each now (INT 9Bh, 9Ah).
- **Arena crash after a kill (hardened):** DOSBox could close as a creature
  died in a fight. The shadows drew from a list the Ledger refreshes only
  twice a second, so a creature dying since could still be given a shadow,
  and the helper loaded its new death pictures from inside the game's floor
  drawing. The helper now checks the creature's status as it draws and gives
  a dying or dead one no shadow; the Ledger's list leaves out the dying too.
  The crash didn't happen again in testing, but it was never reproduced
  either.

**Documentation**
- **The guide's kits** each have a short description of who takes them on
  Athas, above each class's kit table.
- **The guide's Battle Mage** now says its chosen weapon type gives 3/2
  attacks a round, 2 from 7th level.
- **Kits:** DEVELOPMENT.md has how they are built: room in the helper, the
  sheet byte for the kit, the creation page, and each effect's hook.
- **The player's guide** (`GUIDE.md`), new: the game's rules as its code works
  them and the mod's changes, laid out like the game's rule book (making a
  party, the classes, kits, fighting, magic, psionics, equipment, levels), with
  the tables, and no spoilers: no places past the arena, people, quests or
  items by name. Its spell slot, WIS bonus and XP tables are read from the
  game, which differs from the manual's.
- **The README reorganised:** what the game does on its own (initiative,
  spells, psionics, character creation, monsters' defences, two weapons,
  thief skills, saving throws) is under one heading, How the game works, and
  every rule change under Rule changes (the two-weapon, thief and saving
  throw rules had sections of their own); Kits has sub-headings; the charges
  in item boxes are under In the game; addresses in the game's code are left
  to DEVELOPMENT.md; the contents list every section. Corrected: the Crusader
  and Mind Warrior attack 3/2 from 7th level (no character reaches 13th), a
  backstab is ×4 at 9th and 10th, and an example of the off hand's one attack
  a round is clearer (3/2 + 1).
- **The player's guide rewritten** to tell how the mod plays, with its
  default options, each rule as it is in play and a "Without the mod" note
  where a switch changes the game's own; the manual's comparisons, the race
  and class list and the game's hot keys (not checked against the game) are
  gone. Corrected: a warrior's attacks with weapon specialization, and picking
  pockets (a failed try rolls move silently, never hide in shadows).
- **The player's guide, more:** the quality of life changes in a table;
  each kit's starting gear; the spell slots of the kits that change them
  (Arcanist, Battle Mage, Crusader, Elementalist, Seeker, Justifier, Shinobi)
  and the Shinobi's spell list; the preservers' and priests' spells by level,
  sphere and class (read from the game's spell records: the common 4th and
  5th-level priest spells are druids' alone); and a list of things worth
  knowing in play.
- **The player's guide by class:** a section for each class, with how it
  plays, what the mod changes, its weapons and armour, its kits (what each
  gives, costs and starts with), its starting gear, its races, every
  multiclass combination it can be part of (read from the game's creation
  tables: gladiators never multiclass) and how a human dual-classes into or
  out of it (read from the game's DUAL check: 2nd level, 15 in the old prime
  requisite and 17 in the new, a class of another group, a druid true neutral
  and a ranger good), and the magic weapons it can wield (from the game's
  class lists and the mod's restrictions, kits included). Classes by race,
  and tables of the mod's new items, mundane and magic, by what they are and
  who can use them, never where they are.
- **Kits that can't go together** lists only pairs that can meet: a human
  has one kit for each class, and the game never lets a human change from one
  warrior class to another, so the Arena Champion and Sentinel clash only with
  the Shinobi (the README, the guide).
- **The Kits switch** on the Options tab no longer says half the kits work so
  far.
- **The front page** names the kits and INT among the rules, and what has
  changed since 1.2.0.
- **DEVELOPMENT.md:** the patched game's interrupts are summarised, with
  `gamepatch.py` as the list, in place of a list that had fallen behind.

## Pull request #30 ([merged 2026-10-08](https://github.com/daaki85/darksun-companion-mod/pull/30))

**Release**
- **Templar's Ledger 1.2.0:** the version is 1.2.0, with its notes in
  `release-notes/v1.2.0.md` (pull requests #19 to #29), listed on the front
  page with the others.

## Pull request #29 ([merged 2026-10-08](https://github.com/daaki85/darksun-companion-mod/pull/29))

**Changed**
- **A ranger's bow is its own** with class restrictions: a multiclass ranger
  may use bows whatever its cleric sphere allows (a fire cleric/ranger, whose
  sphere allows only obsidian), and a human ranger turned cleric gets the bow
  back with its chosen weapon spec, once the cleric level passes the ranger's.
  Before, its bow expertise was there but no bow could be readied.

**Documentation**
- **What it does**, on the front page and in the guide alike: what the Ledger
  shows of the game's hidden rolls, how it brings the rules closer to AD&D,
  what it adds to Athas and on the screen, and its quality of life changes,
  in place of the old description and lists.
- **Two weapons** is a section of its own, beside Thieves and Saving throws
  (the game's rule, then AD&D's penalties), rather than under The dice log.

## Pull request #28 ([merged 2026-10-08](https://github.com/daaki85/darksun-companion-mod/pull/28))

**Changed**
- **Options tab:** a **Thieves** section of its own, after Rule changes, with
  AD&D's thief skills, hiding to backstab (and the cloak, boots and belt) and
  picking pockets (and the P key), as the guide's Thieves section has them;
  the weapon specialization box is shorter.
- **Warriors shoot faster from 7th level** with a missile weapon they
  haven't specialized in, as their melee goes from 1 to 3/2: a bow 3 a round
  (was 2), a sling, staff sling or chatkcha 3/2 (was 1). Specialists keep their
  rates, a step ahead at every level.
- **The arena's ring is one of the new items:** New items, magical and mundane
  switches it too; its own box is gone.
- **The red rings are under Controls,** with Tab and Enter, as the guide has
  them; scrolling with the right button is a line under the mouse wheel's.
- **The Ledger's window:** Show details and Show unlabelled rolls are on the
  Dice log tab, above the log, rather than in an Options section of their own;
  Save layout and Reload layout are on the Memory tools tab, leaving the top
  row to starting the game, its window, the text size and Reconnect; a byte's
  decoding has a line of its own.
- **"Not connected"** says to start the game with Start the game, rather than
  naming a command-line option.
- **A character's card** leaves out empty lines (a non-warrior's weapon
  specs), rather than showing a blank one.

**Documentation**
- **Guide reorganised:** Every magic item and Every mundane weapon in a section
  of their own, Item tables (they list the game's items too, not only new
  content); Suggested system requirements under Requirements, linked from Game
  speed; Picking pockets moved to Thieves; weapon specialization tidied
  (repeated notes gone, one table heading for every warrior, "weapon spec" for
  the weapon types throughout, as the creation pages call them, and every ranger's bow
  expertise said first).
- The two Two weapons sections are one; the Effects screen's click (a spell
  left on) has a section under Controls, where its box is.
- **Guide read through:** the game's own saving throws (petrification/
  polymorph, the doubled d20) explained once, under Saving throws; the crash
  sections one; Show Save with the practice program under Without the game;
  the Characters tab's card as a list; the backstab table with the new
  weapons (a bone axe and a pick can backstab); sixteen rule changes, not
  fifteen; technical notes (patch addresses, drawing costs) moved to
  DEVELOPMENT; old-save notes gone.
- **Screenshots retaken** with the game installed (its title lettering,
  portraits and figures): the dice log, the Dialogue tab, the practice
  program and a thief's card; the backstab table checked against the game's
  item data (named long swords weigh 10 to 40).

## Pull request #27 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/27))

**Changed**
- **No bow to choose for a ranger** at creation (nor in the catch-up pick at
  a level gained, for a ranger with no weapon type yet): every ranger has expertise
  with the bow already.

**Documentation**
- Where a ranger's bow expertise and missile weapons' rates show, and the
  Options tab's weapon specialization box, mention them.

## Pull request #26 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/26))

**Changed**
- **Missile specialists shoot faster:** with weapon specialization, a fighter
  or gladiator with a chosen bow, sling, staff sling or chatkcha shoots faster
  by level: a bow 3 a round, then 4 from 7th level; a sling, staff sling or
  chatkcha 3/2, then 2 (AD&D's specialist's rate for the sling, a step above
  it for the others). A grand master shoots once more a round, as in melee.
  Before, missiles kept the game's rate. The Characters tab shows each missile
  weapon's rate.
- **Rangers and the bow:** every ranger has expertise with the bow on top of
  the weapon type it chooses, and a ranger's expertise with a missile weapon now
  gives the same rate of fire, with no other bonus.

**Documentation**
- **Attacks a round:** a table in the guide by skill (non-warriors, a weapon type not
  chosen, expertise, specialized, mastery, grand mastery) and level, for
  melee, bows and the other missile weapons.

## Pull request #25 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/25))

**Added**
- **Bone and obsidian great axes and a bone dagger,** each with an icon of its
  own. A warrior's starting great axe is now bone (obsidian for a fire or earth
  cleric), and a water cleric's starting dagger bone. Water and fire clerics'
  warriors can now choose the great axe, and water clerics' (a water
  cleric/psionicist among them) the dagger.
- **Replacements for what breaks:** the Weapon Merchant sells great axes in
  all three materials, the metal pick and the bone dagger; Jark sells bone and
  obsidian great axes and the bone dagger; every Wild Mul carries a bone great
  axe. Kel sells two sets of Thieves' Tools.
- **Defilers leave a body:** each of the game's two kinds of defiler carries a
  dagger, one obsidian and one bone. The game leaves no body for someone who
  carried nothing.
- **Mindshard from Maris's pocket:** a thief can lift it, as Shadowseeker and
  Gutterknot, for 200 XP.

**Changed**
- **One box for the new items:** the Options tab's four item boxes are one,
  **New items, magical and mundane**. The arena's ring keeps its own box, and
  the "Give thieving tools now" button is gone (Kel sells them).
- **Weapons off the allies:** Krikor's bone axe, Uskuye's metal great axe and
  Lt. Kwerin's metal pick are gone; the Weapon Merchant sells the metal ones.
- **The Sunking Crown** gives Protection from Evil, not the 10' Radius one.

**Fixed**
- **The game's Sling +1** (in a chest) showed a blank icon: its picture was
  missing from the game's data. It now has one, the Sling's with a glow.

**Documentation**
- **Item icons** in every item table of the guide.
- **[Every magic item](obsidian-edition/README.md#every-magic-item)** and
  **[Every mundane weapon](obsidian-edition/README.md#every-mundane-weapon):**
  each item, the game's and the Ledger's, with its bonus or power and who
  sells or carries it; the magic weapons of each weapon type for weapon
  specialization.
- **Mundane items** in a table of their own in New items, and the Ledger's
  weapons in the acid saving throw table.

## Pull request #24 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/24))

**Added**
- **Magic weapons for the classes that had too few,** each with an icon of its
  own and a story from Alagorn:
  - **Galefang,** a metal dagger +2 an air cleric can wield (a new item type:
    none of the game's daggers are an air cleric's), on the Rogue Shaman;
  - **Mindshard,** an obsidian short sword +1, on Maris, and **Stillwater,** a
    bone short sword +1, in the chest Chaya gives as her apology: a
    psionicist's, alone or with a cleric's;
  - **Linebreaker,** a metal polearm +2, on the Troop Leader, and
    **Thornwall,** a bone polearm +1, on the slave pens' weapon rack in place
    of one of its two plain ones (the rack gets an object of its own: the
    Lower Castle's is the same object).
  - Alagorn's weapons menu now has more items than a script has locals: the
    last are kept in the Ledger's flags.

**Fixed**
- **Drakejaw** (pull request #23) was never on its Magera: the game read its
  own Gemfields region, not the Ledger's copy, which DSCLOG now opens instead.

## Pull request #23 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/23))

**Added**
- **Three magic axes,** each with an icon of its own and a story from Alagorn:
  - **Drakejaw,** a bone axe +1, on one of the Magera guarding the wagon's
    prisoners (he gets an object of his own);
  - **Glasshewer,** an obsidian axe +2, on the elven slavers' Templar;
  - **Headsman,** a metal great axe +2, in the arena Announcer's stash.
  - Alagorn's weapons are told by a copy of his script 213 (222), so no
    script overflows the game's script buffer.

**Changed**
- **The Elven Leader's Gythka is +2** (was +1). It also no longer takes
  Kreenfang's icon, which any Gythka +1 did.

## Pull request #22 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/22))

**Changed**
- **Cermak, of the game's own party, specializes in the long sword and the
  axe** (was the club), which count once his gladiator levels do again.

## Pull request #21 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/21))

**Added**
- **The Tome of Understanding,** Father Garyn's gift when the party brings
  him the ranike pith: read like a scroll (right-click it, click its icon),
  it gives the reader a point of WIS for good (at most 25) and is used up.
  The game's book, with a night-steel cover and an emblem in the fire colours
  of its magic items.
- **The game's own party made ready for the rule changes,** for a new
  player who presses START GAME: Gerakis specializes in the long sword and
  the gythka and carries a bone gythka in place of his club, K'ratchek
  specializes in the chatkcha, Cermak in the long sword and the club, and
  Cilla, a druid who can't wear armour, has her leather armour taken away
  and knows Armor instead.
- **The Warden's Plate,** plate mail +1 in four pieces (with the magic
  weapons' switch): the **Helm** on Dagolar's body (Cloak of Bravery while
  worn), the **Arms** in the Lower Castle's treasure chest with Dark Flame,
  the **Legs** in the Gemfields' chest, the **Chest** on Balkazar's body
  (Resist Fire while worn). Plate is AC 3 chest, 2 arms, 2 legs (DSCLOG's new
  item types), each +1; the helm is the game's metal helm +1. Each piece
  has an icon of its own and is drawn on the figures.
- **The Cloak and Boots of Elvenkind** (with the magic weapons' switch): the
  cloak is the Elven Leader's gift with his Gythka +1, the boots are in
  the buried chest of Kel's caravan. Thieves and rangers only (multiclasses
  too). With the hiding rule, the cloak's wearer hides in shadows on 95 or
  less under the open sky, 90 under a roof (not halved by the light), and the
  boots' moves silently on 95 or less; their item boxes say so (`Hide 90-95%`,
  `Move 95%`).
- **The Flame Blade,** an obsidian long sword +1 (with the magic weapons'
  switch) whose blade casts the fire clerics' Focus Heat on what it hits (2d6
  fire, a save for half), as the game's Dark Flame does Burning Hands: in
  the pack of the Hot Springs' Templar. Obsidian, so a fire cleric can wield
  it.
- **Alagorn knows every new magic item,** each in the menu the game would put
  it in: the Flame Blade, the Warden's Plate (a part of Haldren's story for
  each piece), the Cloak and Boots of Elvenkind, the Bracers of Defense,
  Arrowbane, the Sunking Crown, Inixhide, the Rings and Cloak of Protection
  and the Tome of Understanding.
  - One story for each kind, as with the game's own items: the four pairs of
    bracers share one, and so do both rings.
  - His clothes, rings and other items are told by copies of his script 212
    (220 and 221), so no script overflows the game's script buffer.

**Fixed**
- **Alagorn's clothes with none carried:** he said "no magic clothes", then
  "Ah, magic clothes" and showed an empty menu. The game's two nested tests
  for clothes are now kept.
- **Armor, spell 0, was missing from the Ledger:** the Spells tab left it
  out and the dice log would have named it "spell 0"; the game numbers its
  spells from 0.
- **No manual check:** the dragon asking for a word from the manual when the
  party first leaves the sewers (the game's copy protection) no longer
  comes; the game goes on as if it had been answered.
- **The Ledger's window started with an error** (an indentation slip in its
  Options code since pull request #20); a test now compiles every module.

**Changed**
- **The world's new items are in the game's own data,** not added while you
  play: the launcher writes them into their people's and chests' objects, so a
  new game makes them where they belong. The slave pens' items (Kurzak's
  Shadowseeker and helm, Legcrusher's armour, Pehtucl's cloak and ring) and
  Kreenfang (the arena's dead body's gythka) are in the data too. The Boots
  of Elvenkind are in the buried chest when it is dug up; the bone scale
  set's arm and leg pieces and helm are in the slave pens' chest with its
  chest piece; one Castle Guard and one Undermountain miner have objects of
  their own for their items. The Options tab's switches take effect from the
  next start, in regions not yet visited.
- **The Elven Leader gives the Cloak of Elvenkind himself,** after his
  Gythka +1, with a line of his own; when it can't be carried he leaves it on
  the ground beside him, as the Gythka.
- **Grey's Scale's arm and leg armour are AC 3** (the game's are 2).
- **A new warrior with a staff sling keeps its shield,** as with a bow: both
  go in the missile slot, and the game asks nothing of the hands for them (the
  shield went into the backpack before).
- **The magic weapons and Legcrusher's leather have names:** the Club +1 is
  **Gutterknot**, the Pick +1 **Deepbiter**, the Staff Sling +1 **Windlash**,
  the Short Sword +2 **Greenbright** and the Leather Chest Armor +1
  **Inixhide**, each with a story from Alagorn. Greenbright is now on **Arant**, who holds the captured
  gladiators (the Elite Guards are only in the final fight). A thief can
  lift Gutterknot from Churrr's pocket, for 200 XP, as Shadowseeker from
  Kurzak's.
- **A circlet and a crown, worn on the head and not armour** (with the magic
  weapons' switch): **Arrowbane**, a silver circlet sold by Kel, keeps
  Protection from Normal Missiles on its wearer; the **Sunking Crown**, worn
  by Keldar, Protection from Evil, 10' Radius. Neither gives AC, stops bracers
  of defense or a preserver's spells. Each has an icon of its own and is
  drawn on the figures (a silver band with a stone; a gold band with points).
- **Bracers of defense give nothing with a helm on**, as with any armour; a
  shield and rings and cloaks of protection still go with them.
- **The documents are shorter and better organised:** the front page gives an
  overview and only the latest pull request's news; the guide's dice log lines
  are grouped by topic, its internals moved to DEVELOPMENT.md (with the
  command-line use), and its new items described once; released pull requests
  here are summarised.
- **The README's new items** are one item to a row, with the prices and the
  Options tab's boxes after the table; the ranger's row no longer names a
  fighter/ranger (the game has none).

## Pull request #20 ([merged 2026-10-07](https://github.com/daaki85/darksun-companion-mod/pull/20))

**Added**
- **The new plain weapons in the world** (a new content switch, on by default):
  the Weapon Merchant and Jark sell the bone and obsidian short swords and axes,
  the obsidian mace and (the Weapon Merchant) a plain metal short sword; Merzol,
  Krikor and Chaero carry one, and every Tari in the warrens, Renegade and Wild
  Mul has one as loot.
- **Bracers of defense** (a new content switch with the magic weapons, on by
  default): AC 6 on Mikquetzl, AC 5 on Wyrmias, AC 4 on Balkazar and AC 2 on
  Dagolar, 20,000 to 40,000; worn on the arms, nothing while armour is worn on the arms, legs or
  chest, and not armour to the class rules (a preserver casts in them).
- **Magic weapons of the weapon types the game has none of:** a Club +1 on Churrr
  in the warrens, a stone Pick +1 on one of the Undermountain folk, a Staff
  Sling +1 sold by the Bowyer and a metal Short Sword +2 on an Elite Guard,
  each with an icon of its own and priced as the game prices its own: the
  melee ones as its Obsidian Bloodwrath +1, 20,800 a plus; the staff sling as
  its Sling +1, 2,800.
- **Metal daggers, maces, great axes, picks and polearms** (the game has none
  plain): one each on Tobrian, a Templar of the slavers' camp, Uskuye, Kwerin
  and a Castle Guard; an earth cleric may now take the great axe and the
  polearm, and starts with a metal one.
- **Weapon specialization** (a new rule change, on by default): fighters and
  gladiators specialize in weapon types (+1 to hit, +2 damage), fighters
  on to mastery at 5th level (+3, +3) and grand mastery at 9th (the damage
  die a size larger and an attack more), rangers take expertise; a warrior
  with a weapon of another type attacks at AD&D's plain rate. Sixteen weapon types,
  chosen on the creation screen's new **WEAPON SPEC** pages (greyed as the
  game's disciplines are, a multiclass warrior's limited to the weapon types it may
  use some weapon of, in any material: a fire cleric's obsidian long sword),
  a new warrior starting with a plain weapon of its type in a material it may
  use (new bone short swords and axes, obsidian ones for fire and earth
  clerics, as the game has only Kurzak's short sword and a metal axe; an
  obsidian mace pictured without Blackmace's glow; a plain great axe pictured
  without the Great Axe +3's gem; a two-handed weapon puts
  the starting shield in the backpack); a
  gladiator's 3rd and 4th (and any warrior's from before the rule) picked at
  a level gained, in the game's own pop-up for a psionicist's new power; the
  weapon types listed on the **Effects** screen and counted on the DAM lines and in
  the dice log. The Characters tab lists each character's weapon types
  (`Weapons: long sword (grand mastery)`) and gives the attacks a round with
  each weapon held (`Attacks: 3/2 a round with Long Sword, 1 with Axe`).
- **Class restrictions** (a new rule change, on by default): psionicists,
  multiclass thieves, preservers, druids and clerics held to their own limits
  on armour, shields and weapons whatever their other classes allow, the
  strictest winning; a multiclass preserver casts no spells in armour (its
  spell slots headed **NO SPELLS IN ARMOUR** on the USE screen, and
  "(no spells in armour)" on the Characters tab).
- **Multiclass hit points** (a new rule change, on by default): each level's
  die and CON's bonus divided between a character's classes, as in AD&D, at
  creation and at every level; the dice log shows the share. Meant for a new
  game: ticked during one, a character's next level shares CON's bonus for
  all its levels.
- **Hit dice: the better of two** (a new rule change, on by default): every
  character's hit die is rolled twice, at creation and at each level, and the
  better roll kept; the dice log shows both.

**Fixed**
- **The Characters tab read the game as if every rule were off** (its
  THAC0, attacks and specialization lines): it now uses the rules ticked.
- **Character creation in the dice log:** one click on the die rolls a whole
  character several times while it tumbles, and the log gave every one; when
  rolls came too fast to record, the hit point line took CON from an earlier
  one (37 logged where the game had 40). Now only the character the die stops
  on is logged, each ability and the hit points checked against what the
  screen shows (`DEX 19 (its rolls came too fast to record)`).
- **"No hit point roll" on a level gained:** the dice log said the game rolls
  hit points only when a character's highest class level rises. It rolls for
  every new class level; a level that leaves the most hit points unchanged
  only added a fraction (the game divides the whole total by the classes).

**Changed**
- **The Ledger's magic items are priced as the game's own:** the Rings and the
  Cloak of Protection +1 15,000 (were 5,000), Leather Chest Armor +1 6,000
  (was 3,000); ones already given are repriced. Kreenfang 20,800 (was
  18,000), as the game's Gythka +1.
- **The README is shorter** (2,974 lines to about 2,300): how each part works
  (the helper's interrupts, the game's offsets and flags), how the dice log
  works, what's known of the game's data and the development notes are in a
  new `obsidian-edition/DEVELOPMENT.md`, each README section linking to its
  part; "What it does" is a short overview; the thieves' skills and backstabs,
  and the saving throws, are each one section with their rule changes, and the
  two-weapon rule sits with the dice log's two weapons; the new items are one
  section with a table, Kalzith and Semyon one of new people told as a player
  meets them; and the helms' and boots' rules are one.

## Pull request #19 ([merged 2026-10-06](https://github.com/daaki85/darksun-companion-mod/pull/19))

**Added**
- **Which class levels up next, on View Character:** for a character of more
  than one class, the XP in brackets on the experience line now names the
  class that reaches its next level there: `EXP:87230 (90000 Pr)`. A letter
  for each class, but **Pr** and **Ps** for preserver and psionicist (both
  start with P); both named when two level up at the same XP
  (`(20000 Pr/T)`); a class already at the highest level never named. One
  class: as before. (The patched game's `INT D2h`, where the game adds the
  bracket.)

**Fixed**
- **Kalzith's prices:** Blur 6,000 (was 3,000) and Haste 9,000 (was 12,000).
  They were taken from the game's scrolls with the spell numbers read one off
  (Wall of Fog's and Flame Arrow's); the game has no scroll of either, so
  they're its price for the spell's level, 3,000 a level. His stock is
  repriced when the Ledger next sees the game.

**Changed**
- **Kalzith sells Shield and Burning Hands** in place of Magic Missile and
  Color Spray (3,000 each), so none of his scrolls is one the game has
  (Color Spray's is in the sewers). Magic Missile and Color Spray scrolls he
  stocked before become Shield and Burning Hands, wherever they are.

## Pull request #18 ([merged 2026-10-06](https://github.com/daaki85/darksun-companion-mod/pull/18))

- **Release 1.1.0:** the version, its notes, and pull request #17 marked
  merged in the READMEs.

## Pull request #17 ([merged 2026-10-06](https://github.com/daaki85/darksun-companion-mod/pull/17))

**Changed**
- **Kalzith's scrolls at the game's prices:** 3,000 to 12,000 ceramic: the
  game's own price for a scroll of the same spell, else its price for the
  spell's level.
- **A monster's alignment in the Look box:** `THAC0 17 AL TN`, the alignment
  in two letters; the description in the dialogue window and the dice log's
  `Look:` line name it in words.
- **The Options tab's sections open and close:** each group of switches is
  under a heading to click, so the tab is short; which are open is remembered.
- **The whole party walks as fast as the leader alone, at the fastest game
  speed:** the Ledger's shadows and dust are drawn much more cheaply, and look
  the same.
- **Cloaks and boots say what they do:** with the cloak and boots bonuses on,
  their item box says `Hide +10` or `Move +10` under the name.
- **Boots are named "Boots (Speed+1)"** for the boots rule, so their extra
  move in a fight isn't mistaken for the item box's `Move +10`.
- **Plain cloaks, boots and belts cost 24** (the Leather Cloak was 20); magic
  ones keep their prices.

**Added**
- **Searching junk, hay and wardrobes in the dice log:** each search's roll,
  what it found, and how far the count of finds has got; a rat's bite or a
  falling pot shows its damage roll.
- **More saves:** 40 instead of the game's 10, on four pages of ten in the
  save and load window: PAGE 1 to PAGE 4 buttons under EXIT, and PgDn and PgUp
  for the next page and the one before.
- **More characters:** 29 saved characters instead of the game's 19.
- **Rule change: items saving against acid:** a worn piece of armour or a
  held melee weapon the Rampager's acid or the Babau's corroding touch could
  destroy needs the easier of the game's number and AD&D's save against acid
  for its material, less its plus and 1 more for a magical power.
- **Rule change: rings and cloaks of protection as in AD&D:** of two rings
  only the better counts; a ring gives no AC with magical armour; a cloak of
  protection does nothing with magical armour, metal armour or a shield in
  either hand, natural armour being fine.
- **A worn belt helps a thief:** +5 to picking pockets and opening locks,
  counted by the game's own lock picking and by the Ledger; its item box says
  `Pick +5, Lock +5`.
- **Kreenfang and Shadowseeker:** the 2 handed Bone Gythka on the dead body
  by the stone arch in the arena is Kreenfang, a gythka +1, and Kurzak's short
  sword is Shadowseeker, a short sword +1 whose wielder sees the invisible.
- **Alagorn knows Kreenfang and Shadowseeker:** the Painted Badlands wizard
  who identifies magic items has each in his menus when the party carries it,
  with a story of its own.
- **200 XP for lifting Kurzak's sword:** the conversation says the thief lifts
  "a metal short sword" and receives 200 experience points, with the quest's
  sound, given by the game's own routine for a quest's XP.

**Fixed**
- A bug of the game's own: DELETE in the roster deleted the character in the
  row clicked counted from the top of the list, not of what was shown, so with
  the list scrolled down another character was deleted.
- **Kalzith's and Semyon's questions are asked once a talk:** a reply that
  doesn't end the talk leaves the list once chosen, as the game's own people's
  do, and is back the next time you talk to them.
- **The load window shows an empty page:** PAGE 2 to PAGE 4 did nothing in the
  load window when that page had no saves.
- **Gear on the figures:** walking side-on, a shield showed nowhere; now it is
  held forward of the chest, its near half showing.
- A character not yet played counted as not Okay: a New thief's skills all
  showed 0 on the inventory screen.
- The Look box no longer shows an AC the Ledger worked out for another
  creature: the arena's first fight comes too soon after the opening one to
  tell them apart by the game's time, and a Slig showed the opening fight's
  Defiler's AC -9.
- The Ledger's new item pictures no longer wipe an item's spell: changing an
  icon cleared four bytes of the item where the game's picture cache is two.

## Pull request #16 ([merged 2026-10-04](https://github.com/daaki85/darksun-companion-mod/pull/16))

**Added**
- **Semyon breaks out with Scar:** recruit Semyon before the fight with Scar,
  take up Scar's offer to break out, and Semyon comes along to the slave pens
  with Scar's men, fights the guards on the party's side, and has a line of
  his own for the breakout.

- **Game speed on the Options tab:** the launcher gives DOSBox 20,000 cycles
  by default; GOG's own speed and 30,000 can be chosen, with suggested system
  requirements for each in the companion's README.
- **Faster walking with gear shown:** the party's figure pictures keep only
  the room their gear needs while walking.
- **New content switches:** Kalzith, Semyon, the cooked vulture, the slave
  pens' gear, a worn cloak's and boots' bonuses to hiding, and the Effects
  screen's click keeping a spell can each be switched off on the Options tab.
- **Crash reports:** when DOSBox crashes or the game stops with an error, the
  game's message stays on screen and the Ledger saves a report in `crash-logs`
  with how it closed, what was on screen, the switches, and the end of the
  dice log and dialogue.
- **The Trustee knows Semyon got away:** if Semyon broke out with the party
  and lived, the Trustee says so after the escape, instead of "Every single
  one" for all the pens.

**Changed**
- **Kalzith and the alarm:** while the escape's alarm sounds he has a line for
  the party and no talk, as the pens' other slaves do.
- **A vanished bone scale piece is written up:** the set is still given once a
  game and never again; should the Bone Helm, or the arm or leg piece, vanish,
  the Ledger saves a report on what became of it in `crash-logs`, and the log
  says so.
- **Finding the Ring +1 is worth 50 XP** to whoever searches the Tied-up
  Prisoner's body, given as the game gives a quest's, once.
- **Picking pockets with the Thieves' Tools only, by default:** the Options
  tab's switch is now about the tools, and P in a conversation is a choice
  under it, off unless ticked.
- **The READMEs reorganised,** each with a table of contents: the guide's
  sections grouped as the Options tab is, the window's guide beside how to
  start it, the memory-mapping steps under Development; this changelog moved
  out of the main README into its own file.

**Fixed**
- **A crash in the opening fight:** when the game couldn't make the first of
  two drawing areas of the map's view, it freed the second one anyway with a
  number it had never set.
- **The bone scale set in a second new game:** the Ledger remembered it as
  given across games, so a later new game never had it; it is now kept for
  each game.
- **Thieves' Tools clicked between turns** (as an area changes) stopped the
  dice log with an error.
- **The game's flags** were read and written through a null pointer at times;
  the Ledger's guard stopped the writes.
- **Crash messages readable:** a game that stopped in graphics mode left its
  error message invisible; the screen goes back to text before the message.

**Fixed** (from a review of the code)
- **Clicks after Tab + Enter:** for a few seconds after Enter, anything the
  next character clicked could still count as the enemy chosen before.
- **Kalzith and Semyon in fights:** people past the map's 256th thing were
  missing from the Ledger's list of who is in a fight: no ring, no Tab, no HP
  lines, no "killed" line for them.
- **A thief who went last and is next** after someone first who can't act lost
  their turn line and hiding roll.
- **Two halved hits seen together** were put down to the first, and the second
  later logged as doing nothing.
- **The mouse wheel's watch** (Windows) was started again on every reconnect
  without stopping the last one.
- **Kalzith only with his object:** a copy of the game whose objects lack what
  he is made from no longer gets his scripts; a clash over his scrolls'
  pictures no longer loses every icon.
- **Speed:** the rings' and dust's colour tables are worked out once for a
  palette, not every 30 seconds.

## Pull request #15 ([merged 2026-10-04](https://github.com/daaki85/darksun-companion-mod/pull/15))

- **READMEs after pull request #14:** the changelog, the cooked vulture quest
  and its screenshot, and the new log lines.

## Pull request #14 ([merged 2026-10-04](https://github.com/daaki85/darksun-companion-mod/pull/14))

**Added**
- **What the party wears, on the map:** each character's figure shows their
  weapons and shields, bow and quiver on the back, armour, helms as circlets,
  cloaks, boots and belts, walking and fighting, and changes as soon as their
  gear does.
- **Kalzith, a defiler in the slave pens:** a slave the templars put in the
  arena now and then, kept in a pen of his own, with a face of his own.
- **Semyon in the slave pens,** once he has left the arena: in a pen of his
  own above Kalzith's, with his own conversation.
- **Dinos and the Trustee know about them:** their "who else is in here"
  questions also ask about Kalzith, and about Semyon once he is in the pens;
  if either is killed, they speak of him as of the game's dead.
- **Shadows under every figure on the map:** each living creature's outline,
  laid down toward the lower right, see-through and in the floor's own
  colours, drawn on the floor before the walls and figures, so everything in
  front stands on them.
- **Scrolling the map with the mouse:** pressing the wheel and moving drags
  the map with the pointer, in fights too, and in Windows turning the wheel
  scrolls it.
- **Dust behind walking feet:** puffs on sand and dirt behind anyone walking,
  spreading and fading in about a second, under the walls and figures.
- **Choosing an enemy with Tab, attacking it with Enter:** on a party member's
  turn in a fight, Tab picks an enemy, marked by a red ring, with the view
  scrolled to it; Enter attacks it as a click on it would, even when someone
  stands in front of it.
- **Hits that do less than rolled** in the dice log: a weapon hit that took
  part of its damage, or none, with what the monster's defences say.
- **The quest sound for the vulture:** giving Dinos the cooked vulture plays
  the sound the game plays when a quest is done.
- **Cloaks and boots help thieves and rangers hide:** with the stealth rule, a
  worn cloak adds 10 to hiding in shadows and worn boots 10 to moving
  silently, up to 95.
- **Regeneration in the dice log:** a hit point back by itself, which the game
  gives anyone with CON 20 or more, is logged as such.
- **A safety net against stray writes:** the Ledger never writes over the
  start of memory or the first bytes of the game's data; a write stopped there
  is named in the dice log.

**Changed**
- **The Effects screen no longer ends a spell's effect when its icon is
  clicked** .
- **Windows' security warning only once:** after the first `.bat` file is let
  through, the Ledger takes the download mark off the files in its own folder,
  so the others start without asking.
- **The vulture quest is part of Dinos's talk:** while the party carries the
  cooked vulture, his first menu has "We cooked the vulture from the arena."
  just before "Goodbye." His answer is in his own dialogue window, with his
  portrait, and the XP comes as the game's quests give it, in the game's own
  window; the vulture is no longer used on him from the inventory.
- **Cat's Grace's icon** is a cat's paw print instead of a cat's face.
- **Dinos's vulture lines** are his own words, without narration (the game's
  conversations are people speaking).

**Fixed**
- **DOSBox crashes, garbled figures, freezes and "Null pointer assignment":**
  the gear writer kept writing a party picture over memory the game had freed
  and given to something else.
- **Kalzith said he had nothing left to sell** after one purchase: while a
  save loaded, the Ledger could read the new game's flags with the last game's
  Kalzith and mark it sold out.
- **The vulture's reward in the dice log when a game was loaded,** and its XP
  and rest given then: the flag was read from memory still being loaded.
- **A thief first in a round didn't hide:** someone who had the last turn of
  one round and the first of the next got no new turn in the log, so no hide
  in shadows or move silently roll.
- **Tab + Enter froze the game:** after Enter, the walk to the chosen enemy
  stalled, sometimes until a mouse click.
- **The party's gear showed late after an area change:** the Ledger looked for
  the area's newly loaded pictures only every 10 seconds, and dressed the
  party with its slower checks; a party walking off as the area loaded stayed
  plain meanwhile.
- **Cat's Grace was missing from the Effects screen:** its effect had no icon
  in the game's table of effects, and the screen shows only effects with one.
- **Kalzith's scrolls cast their spell instead of teaching it:** the game
  teaches only from scroll objects numbered 1400 to 1499, and his were 1001 to
  1006.
- **Figures' shadows fell the wrong way:** they lay toward the lower left,
  while the walls', bones' and stones' shadows on the maps fall toward the
  lower right.
- **Kalzith's and Semyon's Look box** sometimes lacked the HP, AC and THAC0
  lines: the Ledger only looked among the map's first 256 things, and the game
  numbers them anew, sometimes past that.
- **The slave pens broken by Kalzith:** Kurzak vanished after leading the
  party in, people were missing, Merzol didn't stop the party, the doors'
  "pick the lock" and "knock" and the main door's "Summon Kurzak!" were gone
  and the water jug couldn't be filled.
- **Kalzith's scrolls taught the spell before their own** .
- **"Who are you?" hung the game** when asked of Kalzith.
- **Pickpocketing said "won't get another chance" to everyone** in a new game
  with the same party: the last game's tries were remembered.
- **Figures taking extra steps after their turn in a fight:** to have figures
  drawn again with their shadows, the Ledger marked them "changed", which in a
  fight could set one walking again after its turn.
- **"Killed" lines for everyone in an area the party left:** walking from the
  slave pens into the arena logged most of the pens as "is killed".

## Pull request #13 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/13))

**Added**
- **The Release workflow can be run by hand**, making the version's tag.

## Pull request #12 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/12))

**Added**
- **Release 1.0.0:** the version, its release notes, and a workflow that
  builds the release zip.

## Pull request #11 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/11))

**Added**
- **Cat's Grace looks like itself:** its own icon and its own description in
  the spell box, instead of Flaming Sphere's.

**Fixed**
- **The slave pens' gear given twice** to a game loaded after it was given:
  none of it is given where it is already in the game.
- **Prices:** Leather Chest Armor +1 is worth 3000, the Cloak of Protection +1
  5000 and the Rings of Protection +1 5000, as magic items; ones already in a
  game are repriced.
- **Dinos takes the vulture as soon as a fight is over:** the Ledger now
  reads the game's own combat flag.
- **Thieves' Tools can't be used in a fight**, only out of one.
- **The dice log and the Dialogue tab keep up with the newest lines** ;
  scrolling up to read back still holds the place.
- **The bone scale set added twice** to a game loaded after it was added: it
  is now added only where none of its pieces is.
- **No more log lines for the Ledger's items** handed out: they're there to be
  found.
- **The Bone Helm** can only be worn by those who can wear bone scale armour
  (not thieves).

**Changed**
- **Getting started:** open the Ledger first, pick the options, then **Start
  the game** from it.

## Pull request #10 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/10))

**Fixed**
- **Half-giants' two-handed weapons in one hand:** the rule didn't take
  effect.

## Pull request #9 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/9))

**Added**
- **Rule change: thief skills from AD&D's table.** A skill is AD&D's average
  for the thief level, plus the race's adjustment, plus Dark Sun's DEX
  adjustment.
- **The bone scale set:** where the Bone Scale Chest Armor is found, its arm
  and leg pieces and a new Bone Helm, coloured to match, are found with it.
- **Rule change: half-giants wield two-handed weapons in one hand,** with a
  shield or a light weapon in the other.
- **Names in colour in the dice log:** each party member's in a colour of
  their own, monsters' in red, bold, all at 4.5:1 contrast or more.

**Fixed**
- **A game that stops with an error** leaves its message on screen, and the
  dice log says how DOSBox closed, telling a crash of DOSBox's own apart.
- **Picking a pocket after loading a save:** a try made after the save is
  forgotten when it's loaded, so that person can be tried again.
- **XP taken away and given back between areas** is no longer logged as a loss
  and a gain; a loss that stays is logged after a minute.
- **A monster's AC in its Look box** could be an earlier fight's creature's: a
  slig in the first arena fight showed the opening fight's Defiler's AC −9.

**Changed**
- **The Options tab scrolls** when the window is too small to show it all.
- **Options:** the Ring +1, picking pockets and the thieving tools button sit
  under Rule changes, with the other changes to play.

## Pull request #8 ([merged 2026-10-02](https://github.com/daaki85/darksun-companion-mod/pull/8))

**Added**
- **Rule change: levels up to 10.** Every class can reach 10th level, at
  AD&D's XP.
- **Gear for the slave pens' bosses** (with the Ledger running, given once a
  game):
  - Kurzak: a metal Short Sword (1d6, a new item type; a thief can lift it)
    and a leather Helm;
  - Legcrusher: Leather Chest Armor +1;
  - Pehtucl: a Cloak of Protection +1 (a new item type: +1 AC and +1 on saves,
    as the ring) and a Ring of Protection +1 (a thief can lift it).
- **Rangers hide in shadows and move silently too** , with AD&D's ranger
  chances: the full chance outdoors and half indoors, the reverse of thieves.
- **Item icons of their own** for the Short Sword, Leather Chest Armor +1, the
  Cloak of Protection +1 and the two Rings of Protection +1, made from the
  game's plain ones.

**Changed**
- **Thief skills: no equipment penalty.** The game took 5 to 10 off some thief
  skills for anything in the legs slot, the quiver or either hand; it no
  longer does in games started with the dice log.
- **The inventory screen shows hide in shadows** in hear noise's place; the
  Ledger's own screens show both.
- **Pick pockets lifts a short sword** too, though it weighs more than other
  small things.

## Pull request #7 ([merged 2026-10-01](https://github.com/daaki85/darksun-companion-mod/pull/7))

**Added**
- **Rule change: AD&D's two-weapon penalties.** A non-ranger with a melee
  weapon in each hand attacks at −2 with the main hand and −4 with the off
  hand, offset by the DEX reaction adjustment.
- **Rule change: the spell save.** Spells are saved against with the spell save,
  not petrification/polymorph.
- **Rule change: DEX instead of a doubled d20.** On saves against fire, cold
  and electricity, the DEX defensive adjustment counts instead of a doubled
  d20.
- **Cat's Grace**, a new 2nd-level wizard spell in Flaming Sphere's place.
  - +1d6 DEX, at most 24, working exactly as Strength does for STR.
  - Untick the rule and Flaming Sphere is back.
- **REAC and DEF on the inventory screen.** REAC sits beside SP; DEF sits on
  the AC line.
- **Rule change: hiding in shadows to backstab.** A thief whose turn comes
  with no enemy beside them rolls hide in shadows, then move silently.
- **The cooked vulture quest.** Take the cooked vulture to Dinos in the slave
  pens: he cooks it for the party, who eat with him.
- **32 new entries in the game's item name table** , for the Ledger's own
  items.

**Changed**
- **Turn pop-ups in the game are off by default** , and have three levels: at
  the least, in short, or in detail.
- **Spell slots** only show the spell levels the character can cast.

**Fixed**
- Item names numbered past 255 were read wrongly by the Ledger (for example,
  Serpent Boots).

## Pull request #6 ([merged 2026-09-30](https://github.com/daaki85/darksun-companion-mod/pull/6))

**Fixed**
- **Boots gave no extra move.** The rule looked at the wrong equipment slot.

**Changed**
- README screenshots retaken (move silently, boots, Thieves' Tools, Options).

## Pull request #5 ([merged 2026-09-30](https://github.com/daaki85/darksun-companion-mod/pull/5))

**Added**
- A **Give thieving tools now** button on the Options tab.
- **Thieves' Tools** get a name of their own and a leather satchel's picture
  instead of a key's.

**Fixed**
- The arena ring, and the backpack cell the thieving tools went into.
- Only one set of tools per thief.
- Long lines on the Options tab wrap to the window.

## Pull request #4 ([merged 2026-09-30](https://github.com/daaki85/darksun-companion-mod/pull/4))

**Added**
- **Picking pockets:**
  - press P in a conversation, with a thief leading;
  - small things only;
  - a move silently roll decides whether a fumble is noticed;
  - a few coins when there's nothing else to take.
- **Thieving tools:** every thief starts a new game with a set.
- **Ring of Protection +1**, found on the Tied-up Prisoner in the arena.
- Items named for the rule changes ("Helm (AC 1)", "Boots (+1 Move)").
- **Thief skills as they stand:** equipment penalties and effects, in the game
  and in the Ledger.
- **Start the game** from the Ledger's window, and a triple-size game window.

**Fixed**
- Fights restarting or crashing after a pop-up's Continue.
- The arena's opening show.
- The Announcer's name being replaced by one learned mid-fight.

## Pull request #3 ([merged 2026-09-30](https://github.com/daaki85/darksun-companion-mod/pull/3))

**Added**
- **In the game:**
  - THAC0, saves and thief skills on the inventory and View Character screens;
  - spell slots on the USE screen;
  - each turn's rolls in the game's own window, with monsters' turns in a
    pop-up of their own;
  - monsters' defences in the Look box.
- **Spells tab:** what every spell and psionic power does.
- **Launchers:** one for the game alone with the in-game additions, and one
  for the game and the Ledger together.
- **Script decoder:** every thief and ability check in the game's scripts.
- **The first rule changes:** helms give AC 1; boots give a move more in a fight.
- **Saving throws** with each modifier named.
- **THAC0** shown with each weapon, fresh on every redraw.
- The Ring +1 (+1 AC and saves).

**Changed**
- No packaged .exe: the .bat files offer to install Python instead.

## Pull request #2 ([merged 2026-09-29](https://github.com/daaki85/darksun-companion-mod/pull/2))

**Added**
- The game's own **portraits and font**, read from your install at run time.
- **A Characters tab** laid out like the game's View Character screen.
  - Each character's equipment by slot.
  - Effects with rounds or charges left.
  - Spell slots.
- **Spell detail in the dice log:**
  - damage formulas, durations, and what a save does;
  - rules for 20 more effects;
  - healing, Magic Missile and Slay Living dice labelled;
  - Dispel Magic per effect.
- **Thief skill rolls**, with what each chance is made of.
- **Psionics:** powers named, PSP spent logged, magic resistance changes.
- **Saves:** the chance to save, and what the save left.
- **Dialogue:** the reply you picked, and named speakers.
- **The log at a glance:** round headers, hit chances, HP left, and a details
  switch.

## Pull request #1 ([merged 2026-09-28](https://github.com/daaki85/darksun-companion-mod/pull/1))

**Added**
- **The party viewer**, reading Shattered Lands' character records live.
- **The dice log:**
  - attack bonuses, weapons, saving throws, spells and buffs;
  - kills and XP, weapon breaks, level-up HP and AC make-up;
  - attacks from behind and backstabs (with the damage multiplier);
  - each round's initiative order and how each score was made up;
  - the two-weapon adjustment, and character creation rolls.
- **A dialogue tab.**
- **Accessibility** (AODA / WCAG 2.0 AA):
  - contrast checked in tests;
  - text size controls;
  - full keyboard access;
  - logs you can save.
- Double-click launchers and a step-by-step Windows guide.
- The name *Templar's Ledger*, and a window in the game's colours.
