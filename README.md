# Obsidian Edition

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox: rules closer to AD&D, kits, new spells, items and people, the
party's gear drawn on the map, and every roll shown as it happens. You start
the game with the **Dark Sun Obsidian Edition Loader**, which loads the mod
with your options and keeps the full dice log while you play. (The Loader was
called Templar's Ledger up to 2.2.1, and up to 1.2.0 that was the whole mod's
name.)

![The arena in round 10 of a fight: Cermak's turn, with the combat log over the map's lower right showing a Slig's hits on Gerakis and the new round](obsidian-edition/docs/combat-log.png)

## Documentation

- [The player's guide](obsidian-edition/PLAYER-GUIDE.md): the rules, without spoilers, a section for each class (also as a web page, [`player-guide.html`](obsidian-edition/player-guide.html))
- [The full documentation](obsidian-edition/README.md): installing, running, the Loader's window and the dice log
- [Features and rules](obsidian-edition/FEATURES.md): every rule change and addition in detail, with its switch
- [Kits](obsidian-edition/KITS.md): every kit's gains, costs and starting gear
- [Patch notes](PATCH-NOTES.md): every change from the original game, in one page to share
- [Items](obsidian-edition/ITEMS.md): every magic item and every weapon, with its icon and where it is (spoilers)
- [How the game works](obsidian-edition/HOW-THE-GAME-WORKS.md): the original game's own rules, from its code
- [Changelog](CHANGELOG.md) and [development notes](obsidian-edition/DEVELOPMENT.md): for developers and testers

## What it does

It shows the rolls the game keeps hidden, brings its rules closer to AD&D 2nd
Edition, adds kits, weapon specialization, spells, items and people to Athas,
dresses the party in what they wear, and fixes the game's bugs. Every rule
change and addition has a switch. The full list is in
[What it does](obsidian-edition/README.md#what-it-does), and every change from
the original game in the [patch notes](PATCH-NOTES.md).

The game's own files are never modified: the Loader runs a patched copy of the
game from its own folder. It writes to the game folder only your saves (pages
2 to 4 as `SAVB`, `SAVC` and `SAVD` files) and your characters (20 to 29 in the
game's own `CHARSAVE.GFF`).

## Getting started

1. Download the latest release from the
   [Releases page](https://github.com/daaki85/darksun-obsidian-edition/releases)
   (`Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`) and unzip it
   anywhere. (Or this repository as it stands: **Code → Download ZIP**.)
2. In the unzipped folder
   (`Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>`, or
   `obsidian-edition` in a download of the repository), double-click
   **`Start Obsidian Edition.bat`**. The first time, it offers to install
   64-bit Python if you don't have it. If Windows shows "Open File - Security
   Warning" (it does for any `.bat` from a download), press **Run**: the
   Loader then unblocks its own files, so it asks only that once. (Or, before
   unzipping, tick **Unblock** in the zip's Properties.)
3. On the Loader's **Options** tab, pick the rule changes and additions you
   want (they're remembered).
4. Press **Start the game** at the top left. The game starts with your
   options, and the Loader shows the party and the dice log as you play.

(`Start Game with Dice Log.bat` starts the game and the Loader together in one
double-click, with the options as last set.)

## What's new

**Obsidian Edition 2.6.0** is out ([release notes](release-notes/v2.6.0.md)):
the Healer kit becomes the water cleric's healer, with Cure Serious and
Critical Wounds, Raise Dead and the other cures only druids had; much more
memory for the game in long sessions, and a warning before it runs low; the
combat log shows the party's count of arena fights; items can be swapped in a
pack again; and seven more of the original game's bugs are fixed, Negative Plane
Protection and Cloak of Bravery among them. 2.5.0 before it
([release notes](release-notes/v2.5.0.md)) brought a Pick Pockets button for
thieves, four more magic weapons, thri-kreen claws that cut, weapon specs
picked after DONE and item reports.

Every release has notes of its own: [2.6.0](release-notes/v2.6.0.md), [2.5.0](release-notes/v2.5.0.md), [2.4.0](release-notes/v2.4.0.md), [2.3.0](release-notes/v2.3.0.md), [2.2.1](release-notes/v2.2.1.md), [2.2.0](release-notes/v2.2.0.md), [2.1.1](release-notes/v2.1.1.md), [2.1.0](release-notes/v2.1.0.md), [2.0.0](release-notes/v2.0.0.md), [1.2.0](release-notes/v1.2.0.md), [1.1.0](release-notes/v1.1.0.md) and [1.0.0](release-notes/v1.0.0.md). The [patch notes](PATCH-NOTES.md)
have every change from the original game in one page, whatever the version.

## About

Obsidian Edition is a fan project, not affiliated with or endorsed by the
owners of Dark Sun or Dungeons & Dragons, whose names and trademarks are
theirs. It includes none of the game's files: you need your own copy of the
GOG release. Screenshots and item pictures in these pages are taken from the
game to show what the mod does.

Obsidian Edition's own code and documentation are free software
under the [GNU General Public License v3.0](LICENSE). That doesn't extend to
the game's own art shown in these pages, which isn't the project's to license.

Problems and ideas: [the project's Issues page](https://github.com/daaki85/darksun-obsidian-edition/issues).

## Credits

- **Code and documentation:** written by Claude, Anthropic's AI model, working
  in Claude Code: the patched game and its helper, the Loader, the tests and
  every page here. The project's commits name it as co-author.
- **Direction and testing:** daaki85, who asked for the features, chose
  between the options and played the game to find what was wrong.
- **The game:** Dark Sun: Shattered Lands (1993), by Strategic Simulations,
  Inc., under licence from TSR, Inc.; Dark Sun and Dungeons & Dragons are now
  Wizards of the Coast's. The Dark Sun setting was created by Troy Denning and
  Timothy B. Brown. GOG keeps the game on sale, and in DOSBox.
- **Research:** the notes of [yuan-ti](https://github.com/CalvinRodo/yuan-ti),
  CalvinRodo's new engine for the game, which pointed to several of the
  original game's bugs fixed here (facts only, each checked in the game's own
  code; none of its code is used), and through it the OpenDS project's fixes to
  the game's scripts.
- **Rules:** AD&D 2nd Edition's *Player's Handbook*, *Demihuman Deities* and
  *The Complete Ranger's Handbook*, where the mod's rule changes and the
  Seeker's and Justifier's tables come from; Baldur's Gate, for keeping a
  creation roll (STORE and RECALL) and Charisma's shop prices.
- **Tools:** [DOSBox](https://www.dosbox.com/), [NASM](https://www.nasm.us/),
  [Python](https://www.python.org/) and [Unicorn](https://www.unicorn-engine.org/)
  (the CPU emulator the helper's tests run in); the web pages' fonts, Marcellus
  SC, Alegreya Sans and IBM Plex Mono, from Google Fonts.
