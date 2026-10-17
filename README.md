# Obsidian Edition

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox: rules closer to AD&D, kits, new spells, items and people, the
party's gear drawn on the map, and every roll shown as it happens. You start
the game with the **Dark Sun Obsidian Edition Loader**, which loads the mod
with your options and keeps the full dice log while you play. (The Loader was
called Templar's Ledger up to 2.2.1, and up to 1.2.0 that was the whole mod's
name.)

![The arena in round 10 of a fight: Cermak's turn, with the combat log over the map's lower right showing a Slig's hits on Gerakis and the new round](obsidian-edition/docs/combat-log.png)

## Contents

- [What it does](#what-it-does)
- [Getting started](#getting-started)
- [What's new](#whats-new)
- [Patch notes](PATCH-NOTES.md): every change from the original game, in one page to share
- [Changelog](CHANGELOG.md)
- [The player's guide](obsidian-edition/PLAYER-GUIDE.md): the rules and tables, without spoilers
- [The full documentation](obsidian-edition/README.md): everything in detail

## What it does

- **Shows what the game keeps hidden.** Every roll is logged as it happens,
  with what it needed and where each bonus came from
  ([the dice log](obsidian-edition/README.md#the-dice-log)). The game's own
  screens gain THAC0, saves, thief skills and spell slots, a combat log shows
  with **L**, and the Look box tells you what can hurt a monster
  ([In the game](obsidian-edition/README.md#in-the-game)).
- **Brings the rules closer to AD&D:** class restrictions, AD&D's class
  tables, INT's limits on learning spells, saving throws and multiclass hit
  points as the books have them
  ([Rule changes](obsidian-edition/README.md#rule-changes)).
- **More ways to build a character:** weapon specialization and mastery, kits
  (three for each class, and thirteen for races' pairs of classes), levels up to
  10, STORE and RECALL for a creation roll, and fuller starting gear
  ([More character customization](obsidian-edition/README.md#more-character-customization)).
- **Expanded play:** thieves hide in shadows to backstab and pick pockets, the
  leader's CHA lowers shop prices, and merchants sell back the magical items
  sold to them
  ([Expanded features](obsidian-edition/README.md#expanded-features)).
- **More of Athas:** new weapons, shields and magic items, six wizard spells,
  Kalzith (a defiler who sells scrolls), defilers who drop scrolls, more of
  Semyon's story and a use for the cooked vulture
  ([New content](obsidian-edition/README.md#new-content)); on the map, the
  party wears its gear, figures cast shadows and raise dust, and elves and
  half-elves look their own ([Graphics](obsidian-edition/README.md#graphics)).
- **Quality of life:** Tab and Enter to choose and attack an enemy, a view
  that stays put in fights, dragging the map with the mouse wheel held down
  ([Controls](obsidian-edition/README.md#controls)), 40 saves kept under their
  names too, 29 saved characters
  ([More saves and characters](obsidian-edition/README.md#more-saves-and-characters)),
  a game speed setting, crash reports, and no manual check
  ([No manual check](obsidian-edition/README.md#no-manual-check)).
- **Fixes the game's bugs:** Mirror Image stopping no blow, Armor wearing out
  twice as fast, Share Strength never ending, Dispel Magic silencing the party,
  Hold Undead holding the living, and more; and the rules it got wrong, from
  spell saves to warriors' attacks, put right
  ([The game's bugs, fixed](obsidian-edition/README.md#the-games-bugs-fixed)).

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

**Obsidian Edition 2.4.0** is out ([release notes](release-notes/v2.4.0.md)):
thirteen multiclass kits, features of their own for the game's own party,
thieves in light armour, the combat log shown with **L** and fixed (2.3.0's
could make fights quit or freeze), a steady view in fights, and crash and
freeze reports that say why. 2.3.0 before it
([release notes](release-notes/v2.3.0.md)) brought the combat log in the
game, three more wizard spells, two magic shields, defilers' scrolls, buying
back magical items, saves kept under their names and fuller starting gear.

Earlier changes, pull request by pull request, are in
[`CHANGELOG.md`](CHANGELOG.md). Releases have notes of their own:
[2.4.0](release-notes/v2.4.0.md) (pull requests #48 and #49),
[2.3.0](release-notes/v2.3.0.md) (#44 to #46),
[2.2.1](release-notes/v2.2.1.md) (#43), [2.2.0](release-notes/v2.2.0.md) (#39
to #42), [2.1.1](release-notes/v2.1.1.md) (#37),
[2.1.0](release-notes/v2.1.0.md) (#35), [2.0.0](release-notes/v2.0.0.md) (#31
and #32), [1.2.0](release-notes/v1.2.0.md) (#19 to #29),
[1.1.0](release-notes/v1.1.0.md) (#14 to #18) and
[1.0.0](release-notes/v1.0.0.md) (#1 to #13).
