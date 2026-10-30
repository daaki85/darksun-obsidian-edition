# Obsidian Edition

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox: rules closer to AD&D, kits, new spells, items and people, the
party's gear drawn on the map, and every roll shown as it happens. You start
the game with the **Dark Sun Obsidian Edition Loader**, which loads the mod
with your options and keeps the full dice log while you play.

![The arena in round 7 of a fight: K'ratchek's turn, with the combat log over the map's lower right showing a Slig's hits on Cermak and his hit points after each](obsidian-edition/docs/combat-log.png)

## Documentation

- [The player's guide](obsidian-edition/PLAYER-GUIDE.md): the rules, without
  spoilers, a section for each class (also as a web page,
  [`player-guide.html`](obsidian-edition/player-guide.html))
- [The full documentation](obsidian-edition/README.md): installing, running, the
  Loader's window and the dice log
- [Features and rules](obsidian-edition/FEATURES.md): every rule change and
  addition in detail, with its switch
- [Kits](obsidian-edition/KITS.md): every kit's gains, costs and starting gear
- [The dice log, line by line](obsidian-edition/DICE-LOG.md): every kind of line
  the Loader's dice log writes, and what it means
- [Patch notes](PATCH-NOTES.md): every change from the original game, in one
  page to share
- [Items](obsidian-edition/ITEMS.md): every magic item and every weapon, with
  its icon and where it is (spoilers)
- [How the game works](obsidian-edition/HOW-THE-GAME-WORKS.md): the original
  game's own rules, from its code
- [Changelog](CHANGELOG.md) and [development
  notes](obsidian-edition/DEVELOPMENT.md): for developers and testers

## What it does

The full list is in [What it does](obsidian-edition/README.md#what-it-does),
and every change from the original game in the [patch notes](PATCH-NOTES.md).
Nearly every rule change and addition has a switch on the Loader's Options tab.

The game's own files are never modified: the Loader runs a patched copy of the
game from its own folder. It writes to the game folder only your saves (page 1
in the game's own `SAVE` files, pages 2 to 4 as `SAVB`, `SAVC` and `SAVD`
files) and your characters (in the game's own `CHARSAVE.GFF`, up to 29). A save
made with the new items can hold items the original game doesn't have: load it
with the Loader.

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

**Obsidian Edition 2.13.2** is out ([release notes](release-notes/v2.13.2.md)):
the creation screen rolls a new character's age on Table 7's dice with each roll
of the die, and Restore Youth can take back any number of magical years. 2.13.1
made characters age with the game's clock and grey on the map, showed how long
you've played, and let Kurzak notice when Legcrusher is gone. 2.13.0 gave characters ages,
Haste's cost and Restore Youth; 2.12.4 let the Loader run the game as
[Dark Sun Recompiled](https://github.com/daaki85/darksun-recompiled).

Every release has notes of its own, in [`release-notes`](release-notes); the
[patch notes](PATCH-NOTES.md) have every change from the original game in one
page, whatever the version.

## About

Obsidian Edition is a fan project, not affiliated with or endorsed by the
owners of Dark Sun or Dungeons & Dragons, whose names and trademarks are
theirs. It includes none of the game's files: you need your own copy of the
GOG release. Screenshots and item pictures in these pages are taken from the
game to show what the mod does.

Obsidian Edition's own code and documentation are free software under the
[GNU General Public License v3.0](LICENSE). That doesn't extend to
the game's own art shown in these pages, which isn't the project's to license.

Problems and ideas: [the project's Issues
page](https://github.com/daaki85/darksun-obsidian-edition/issues).

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
  [Python](https://www.python.org/) and
  [Unicorn](https://www.unicorn-engine.org/) (the CPU emulator the helper's
  tests run in); the web pages' fonts, Marcellus SC, Alegreya Sans and IBM Plex
  Mono, from Google Fonts.
