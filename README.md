# Obsidian Edition

**[Read the Obsidian Edition manual](https://daaki85.github.io/darksun-obsidian-edition/)**

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox (DOSBox-X, which comes with the mod on Windows, or GOG's own): rules
closer to AD&D, kits, new spells, items and people, the party dressed for its classes and its gear
drawn on the map, and every roll shown as it happens. You start
the game with the **Dark Sun Obsidian Edition Loader**, which loads the mod
with your options and keeps the full dice log while you play. Most of it is
always on; the new content and a few rules have a switch on the Loader's Options
tab ([each one, its default and when it takes effect](obsidian-edition/PLAYER-GUIDE.md#the-options-tab-at-a-glance)).
If you have **Wake of the Ravager** too, the Loader starts the sequel with most of the mod, and
your party can go on into it ([Wake of the Ravager](obsidian-edition/FEATURES.md#wake-of-the-ravager)).

![Round 4 of Pehtucl's ambush at the slave pens' fountain, the party in its class outfits: Jenna's turn, with the combat log over the map's lower right, in short and its small font, seven lines: Seneca's miss, the Arena Guard's hit points after a blow, Ester's two misses, and Jenna unable to hide with the guard beside her](obsidian-edition/docs/combat-log.png)

## Getting started

1. Check the [requirements](obsidian-edition/README.md#requirements): Windows, the GOG release of
   the game, and a 64-bit Python, which the `.bat` files offer to install.
2. Download the latest release from the
   [Releases page](https://github.com/daaki85/darksun-obsidian-edition/releases) and unzip it
   anywhere.
3. Double-click **`Start Obsidian Edition.bat`**, pick your options and press **Play Shattered Lands**
   ([running it](obsidian-edition/README.md#running-it-windows), step by step).

## Documentation

- [The full documentation](obsidian-edition/README.md): installing, running, the Loader's window,
  troubleshooting, and [the full list of pages](obsidian-edition/README.md#contents) (features, kits,
  items, creatures, the dice log and more)
- [The player's guide](obsidian-edition/PLAYER-GUIDE.md), without spoilers, with a
  [glossary](obsidian-edition/PLAYER-GUIDE.md#glossary) of THAC0, AC, PSP and the rest
- [Class outfits on the map](obsidian-edition/docs/class-outfits/README.md), with animated galleries of the female and male figures
- [Features and rules](obsidian-edition/FEATURES.md): every switch of the Options tab and every
  change with none
- [The patch notes](PATCH-NOTES.md): what the mod adds and changes from the original game, in one
  page to share
- The manual: these pages as web pages, in the release's `manual` folder (open
  `manual/index.html`, or press the Loader's **Help** button)
- For developers, [the development notes](obsidian-edition/DEVELOPMENT.md) and the
  [changelog](CHANGELOG.md)

## What's new

**Obsidian Edition 2.19.2** is out: F10 does nothing for a held or stuck character
([release notes](release-notes/v2.19.2.md)). It follows 2.19.0: the chance to hit shown before the
swing, the squares a character can still walk to, quick saves and autosaves, a journal with the
quests, Alt to show what can be used, and fewer switches ([its notes](release-notes/v2.19.0.md);
earlier releases' in [`release-notes`](release-notes)).

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
  code; none of its code is used), and the
  [OpenDS](https://github.com/VirInvictus/opends) project's notes and fixes to
  the game's scripts.
- **Rules:** AD&D 2nd Edition's *Player's Handbook*, *Demihuman Deities*,
  *Player's Option: Combat & Tactics* and *Skills & Powers*, and the
  *Complete* handbooks (*Ranger's*, *Fighter's*, *Thief's* and *Barbarian's*,
  the *Book of Dwarves*), and *Dragon* #214's "The Complete Half-Elf" (the
  half-elves' Spellarcher, Shadowblade, Military Scout, Wilderness Avenger and Rescuer),
  where the mod's rule changes and its kits come from; Baldur's Gate, for keeping a
  creation roll (STORE and RECALL) and Charisma's shop prices.
- **Tools:** [DOSBox](https://www.dosbox.com/) and [DOSBox-X](https://dosbox-x.com) (which comes with the mod on
  Windows, under the GNU GPL, version 2), [NASM](https://www.nasm.us/),
  [Python](https://www.python.org/) and
  [Unicorn](https://www.unicorn-engine.org/) (the CPU emulator the helper's
  tests run in); the web pages' fonts, Marcellus SC, Alegreya Sans and IBM Plex
  Mono (SIL Open Font License), carried inside the pages.
