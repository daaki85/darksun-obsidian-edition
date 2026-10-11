# Obsidian Edition

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox, with its own companion window, **Templar's Ledger**, beside the
game. (Up to its 1.2.0 release, the whole mod was called Templar's Ledger.)

![Templar's Ledger during the arena's opening show: the party's character cards, and the dice log of the Defiler's Cone of Cold and the Rampager's acid](darksun-companion/docs/dicelog.png)

## Contents

- [What it does](#what-it-does)
- [Getting started](#getting-started)
- [What's new](#whats-new)
- [Patch notes](PATCH-NOTES.md): every change from the original game, in one page to share
- [Changelog](CHANGELOG.md)
- [The player's guide](darksun-companion/GUIDE.md): the rules and tables, without spoilers
- [The full documentation](darksun-companion/README.md): everything in detail

## What it does

It shows what the game keeps hidden. Every roll is logged as it happens:
attacks, damage, saving throws, thief skills, initiative, even the dice at
character creation. Each comes with what it needed and where every bonus came
from ([the dice log](darksun-companion/README.md#the-dice-log)). The game's own
screens gain THAC0, saves, thief skills and spell slots, and the Look box tells
you what can hurt a monster ([In the
game](darksun-companion/README.md#in-the-game)).

It brings the rules closer to AD&D: weapon specialization and mastery, kits
(three for each class), class restrictions, AD&D's class tables (experience,
priests' THAC0, spell slots), INT's limits on learning spells, thief skills
from the Player's Handbook, saving throws as the books have them, the party
leader's CHA at shops, scores and hit points kept as rolled, and levels up to
10 ([Rule
changes](darksun-companion/README.md#rule-changes)). Thieves can hide in
shadows to backstab, and pick pockets
([Picking pockets](darksun-companion/README.md#picking-pockets)).

It adds to Athas: new weapons in every material, magic items with stories of
their own (robes and bracers among them, for those who wear no armour), Kalzith
(a defiler who sells scrolls), more of Semyon's story, and a use for the cooked
vulture ([New content](darksun-companion/README.md#new-content)). Graphical
additions show the weapons and armour the party wears, have characters cast
shadows, and kick up dirt as they walk ([On the
screen](darksun-companion/README.md#on-the-screen)).

Quality of life changes: choosing an enemy with Tab and attacking it with Enter,
scrolling the map by dragging with the mouse wheel
([Controls](darksun-companion/README.md#controls)), 40 saves and 29 saved
characters ([More saves and
characters](darksun-companion/README.md#more-saves-and-characters)), a game
speed setting ([Game speed](darksun-companion/README.md#game-speed)), crash
reports, and no dragon asking for a word from the manual, the game's copy
protection ([No manual check](darksun-companion/README.md#no-manual-check)).

The game's own files are never modified: the Ledger runs a patched copy of the
game, and copies of its data files, from its own folder. Play writes to the game
folder only what you'd expect: your saves (pages 2 to 4 as files of their own,
`SAVB`, `SAVC` and `SAVD`) and your characters (20 to 29 in the game's own
`CHARSAVE.GFF`).

## Getting started

1. Download the latest release from the
   [Releases page](https://github.com/daaki85/darksun-obsidian-edition/releases)
   (`Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`) and unzip it
   anywhere. (Or this repository as it stands: **Code →
   Download ZIP**.)
2. In the unzipped folder (`Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>`, or `darksun-companion`
   in a download of the repository), double-click **`Start Obsidian Edition.bat`**.
   The first time, it offers to install 64-bit Python if you don't have it.
   If Windows shows "Open File - Security Warning" (it does for any `.bat`
   from a download), press **Run**: the Ledger then unblocks its own files, so
   it asks only that once. (Or, before unzipping, tick **Unblock** in the zip's
   Properties.)
3. On the Ledger's **Options** tab, pick the rule changes and additions you
   want (they're remembered).
4. Press **Start the game** at the top left. The game starts with your options,
   and the Ledger follows it.

(`Start Game with Dice Log.bat` starts the game and the Ledger together in one
double-click, with the options as last set.)

## What's new

**Obsidian Edition 2.1.1** is out ([release notes](release-notes/v2.1.1.md)),
with two fixes to character creation: the dice log no longer misses the
abilities' rolls while the die tumbles, and raising CON raises the hit points.
2.1.0 before it fixed a freeze on the creation screen in 2.0.0 and made
character creation keep what the die rolls: the scores can be moved around
but not raised past the die's total, shown under CHR, and the hit points stay
as rolled. It also stopped the turning mouse wheel scrolling the map, and
added [patch notes](PATCH-NOTES.md) for the whole project.

Earlier changes, pull request by pull request, are in
[`CHANGELOG.md`](CHANGELOG.md). Releases have notes of their own:
[2.1.1](release-notes/v2.1.1.md) (pull request #37),
[2.1.0](release-notes/v2.1.0.md) (#35),
[2.0.0](release-notes/v2.0.0.md) (#31 and #32),
[1.2.0](release-notes/v1.2.0.md) (#19 to #29),
[1.1.0](release-notes/v1.1.0.md) (#14 to #18) and
[1.0.0](release-notes/v1.0.0.md) (#1 to #13).
