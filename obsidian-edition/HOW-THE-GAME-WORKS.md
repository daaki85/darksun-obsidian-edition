# How the game works

*Part of Obsidian Edition's documentation: the original game's own rules, for
the curious, and the detail of one rule change ([Spells and psionics as the
manual describes them](#spells-and-psionics-as-the-manual-describes-them)).
[The README](README.md) is about the mod.*

What the game does that its manual doesn't say, from its code and checked in
play. The dice log shows each as it happens, and the [rule
changes](FEATURES.md#rule-changes) change some of it. Several findings were
first pointed out by the notes of
[yuan-ti](https://github.com/CalvinRodo/yuan-ti), CalvinRodo's new engine for
the game, and checked here in the game's own code. One section is the mod's own: the detail of
[Spells and psionics as the manual describes
them](#spells-and-psionics-as-the-manual-describes-them), beside the game's spells and powers.

## Contents

- [Character creation](#character-creation)
- [Initiative](#initiative)
- [No critical hits](#no-critical-hits)
- [Helpless targets take double](#helpless-targets-take-double)
- [The game's two weapons](#the-games-two-weapons)
- [Attacks from behind and backstabs](#attacks-from-behind-and-backstabs)
- [The game's saving throws](#the-games-saving-throws)
- [Monsters' defences](#monsters-defences)
- [Spells and effects](#spells-and-effects)
  - [Each cleric spell against the
    manual](#each-cleric-spell-against-the-manual)
  - [Turn Undead](#turn-undead)
    - [AD&D's turning table](#adds-turning-table)
- [Psionics](#psionics)
  - [Each power against the manual](#each-power-against-the-manual)
- [Spells and psionics as the manual describes them](#spells-and-psionics-as-the-manual-describes-them)
  (the mod's rule change)
  - [Each spell in more detail](#each-spell-in-more-detail)
  - [The monsters as the manual describes them](#the-monsters-as-the-manual-describes-them)
  - [Known differences left as they are](#known-differences-left-as-they-are)
- [How the game works out thief skills](#how-the-game-works-out-thief-skills)
- [Where the game rolls thief skills](#where-the-game-rolls-thief-skills)
- [Resting](#resting)
- [Searching junk, hay and wardrobes](#searching-junk-hay-and-wardrobes)
- [The Bowyer's archery target](#the-bowyers-archery-target)
- [The arena's count of fights](#the-arenas-count-of-fights)
- [How fast the party walks](#how-fast-the-party-walks)

## Character creation

Every click of the die on the creation screen (and every change of race or sex)
rolls a new character. From the game's code, and checked against the screen:

* **Abilities.** Each score is rolled four times as 4d4 + 4 (8 to 20), the
  best of the four kept, and the race's adjustment added. The game then
  raises the class's prime requisite to 17 and every other score to 9
  (clerics, fighters, preservers, thieves), 12 (druids, psionicists), 13
  (gladiators) or 14 (rangers), CHA included. (With the Loader: a score is
  raised only to the class's minimum in the manual: cleric WIS 9; druid WIS
  12, CHA 15; fighter STR 9; gladiator STR 13, DEX 12, CON 15; preserver INT 9;
  psionicist CON 11, INT 12, WIS 15; ranger STR 13, DEX 13, CON 14, WIS 14;
  thief DEX 9; a multiclass character the highest of its classes' minimums.)
* **Race adjustments** (STR, DEX, CON, INT, WIS, CHA): dwarf +1 −1 +2 0 0 −2;
  elf 0 +2 −2 +1 −1 0; half-elf 0 +1 −1 0 0 0; half-giant +4 −5 +2 −5 −3 −3;
  halfling −2 +2 −1 0 +2 −1; mul +2 0 +1 −1 0 −2; thri-kreen 0 +2 0 −1 +1 −2.
  Humans have none.
* **Hit points.** One die for every level of every class (d8 clerics and
  druids, d10 fighters, gladiators and rangers, d4 preservers, d6 psionicists
  and thieves), doubled for half-giants. The total is divided by the number of
  classes (rounded down), and then CON's bonus is added for every level: a
  warrior's full bonus (+1 at CON 15, +2 at 16, +3 at 17, +4 at 18, +5 at
  19-20, +6 at 21-23, +7 at 24-25; −1 at 4-6, −2 at 2-3, −3 at 0-1), and at
  most +2 for levels in the other classes. There is no automatic maximum at
  first level: the first level rolls like the rest.
* **Choices without dice.** Raising a score to a new class's minimum (adding
  Thief raises DEX to 9) and PSP aren't rolled, so they don't appear in the
  log. The creation screen's other random numbers only choose pictures.
* **The total.** After the six scores comes what they add up to, the most they
  may add up to with [Scores and hit points as
  rolled](FEATURES.md#scores-and-hit-points-as-rolled).

Changing sex or race can make the game roll hit points twice, once with the
old scores and once with the new: the last hit point line is the one that
counts.

## Initiative

From the game's code: at the start of every round each combatant's initiative
is 20 + a roll of 0-9 + a DEX adjustment + Hasted +2, Slowed −2 and Blind −2.
The DEX adjustment has its own table: −6 at DEX 1, −4 at 2, −3 at 3, −2 at 4,
−1 at 5, none for 6-15, +1 at 16, +2 at 17-18, +3 at 19-20, +4 at 21-23 and
+5 at 24-25. The weapon makes no difference (there are no weapon speeds). The
highest score acts first; a second roll, 0-199, decides between equal scores
(the log shows it only for those). Choosing Wait lowers the character's score
to 10 (or by one, if it's 10 or less already) so they act later in the round.

## No critical hits

A natural 20 on an attack always hits, and a natural 1 always misses, but
that is all the d20 does: the game has no critical hits or fumbles. Its attack
routine uses the d20 only for those two checks and the comparison with THAC0,
and never passes it to the damage routine, so a hit on a 20 rolls the same
damage as any other. Two things multiply a blow's damage by a whole number: a backstab, and a
[helpless target](#helpless-targets-take-double) (Enlarge scales it by 10% a caster level).

## Helpless targets take double

A creature that is **Paralyzed** (Hold Person, Hold Monster, a sand howler's gaze, Blood Flow...)
or **Out Cold** takes **double damage from every weapon blow** that hits it, and makes no saving
throw at all: it fails each one without a roll. The game's attack routine hands its damage
routine two numbers, the damage and twice the damage, and the damage routine takes the second
when its target is helpless; the save routine fails a helpless target before rolling. The x2
comes after a backstab's multiple (a backstab x3 on a held target is x6) and before Biofeedback's
2 off. The blow still has to hit: the d20 is rolled as ever (a held target is no easier to hit),
and the manual says nothing of any of it. A spell's damage comes with its own second number,
the most its dice can do, which a helpless target takes instead.

With [Held targets as in AD&D](FEATURES.md#held-targets) ticked (the default) the mod has such a
blow hit automatically for normal damage instead, as AD&D's 2nd edition does.

The dice log shows the blow's x2 (`x2 Paralyzed: a helpless target takes double`), and a
Poisoner's hit on a helpless target, whose poison has no save to show, as `is poisoned by the
hit: Poison (10 damage), no saving throw (Paralyzed)`, followed by the 10 when it lands.

## The game's two weapons

The manual says a character with two weapons ready uses the second "at a
disadvantage", unless a ranger or dextrous. The game's code does something
else: with two weapons ready (in melee), every attack, first hand and second
alike, is adjusted by the DEX table used for initiative with its sign flipped
and never below 0, and rangers are left out. That comes to a **bonus** of +6 at
DEX 1, +4 at 2, +3 at 3, +2 at 4 and +1 at 5, and nothing at DEX 6 and up, so
in practice there is no off-hand penalty at all: both weapons hit as well as a
single one would. The log names it, e.g. `+2 two weapons at DEX 4`. It looks
like a sign slip: AD&D uses the same DEX adjustment to make two-weapon
fighting *harder* at low DEX.

## Attacks from behind and backstabs

From the game's code:

- An attack is **from behind** when the attacker stands in the square directly
  behind the way the target is facing. A creature faces nowhere in particular
  at the start of each round; the first attack on it in the round turns it
  to face that attacker (one of eight directions), and it keeps facing that
  way for the rest of the round. So a second attacker on the far side, later
  in the same round, attacks from behind. (Its own attacks don't turn it.)
  It gets +2 to hit, and the target loses its DEX bonus and its shield. The
  game counted a missile from behind the same way, at any distance (an archer
  across the room); with the Loader a missile is never from behind by the
  target's facing, only as a hidden archer's shot, "unseen" (the stealth rule:
  [Hiding in shadows to backstab](FEATURES.md#hiding-in-shadows-to-backstab)).
- A **backstab** is an attack from behind by a thief, in melee, with a weapon
  that isn't too heavy (the game's weight value at most 40, a metal long
  sword's). It gets another +2 to hit (+4 in all), and on the thief's first
  two attacks of the round (an off-hand one too) the damage, STR bonus
  included, is multiplied: x2 at thief levels 1-4, x3 at 5-8, x4 at 9-12 and
  x5 from 13 (AD&D's table). (With the Loader: [the first attack's dice
  only](FEATURES.md#hiding-in-shadows-to-backstab).)

Which weapons can backstab, the game's and the [Loader's](FEATURES.md#new-items)
(magic ones included). Weight belongs to the weapon's type and material, in the
game's units, which look like tenths of a pound (a dagger is 10, a club 30, a
mace 100, as AD&D's 1, 3 and 10 lb), so the limit is 4 lb. Missile weapons
(slings, bows, a thrown chatkcha) never backstab: it has to be melee.

| Weapon | Material (weight) | Damage | Backstab |
|---|---|---|---|
| Dagger | bone, stone, obsidian, metal (10) | 1d4 | yes |
| Short sword | bone (15); obsidian, metal (30) | 1d6 | yes |
| Long sword | bone, obsidian, metal (10 to 40, metal at the limit) | 1d8 | yes |
| Club | wood (30) | 1d6 | yes |
| Quarterstaff | wood (40) | 1d6 | yes |
| Axe | bone, obsidian (30) | 1d8 | yes |
| Pick | stone, metal (40) | 1d6+1 (the game: 1d4+1) | yes |
| Shillelagh, Flame Blade, Spiritual Hammer (spells) | (10, 40, 40) | 2d4, 1d4+4, 1d4+1 | yes |
| Axe | metal (70) | 1d8 | no |
| Great axe | bone (50); obsidian, metal (70) | 1d10 | no |
| Mace | bone, obsidian, metal (100) | 1d6+1 | no |
| Cahulaks | bone, metal (120) | 1d6 | no |
| Gythka | bone (120) | 2d4 | no |
| Polearm | bone, metal (150) | 1d10 | no |

About a dozen more weapon types are in the game's tables with no item of
theirs in its data (monsters' own, made by scripts, or unused).

## The game's saving throws

From the game's saving throw routine. The spell names which of the character
sheet's five saves to use; a natural 1 always fails and a natural 20 always
saves (in the patched game, unless the save can't be made: below); otherwise the d20 and the modifiers below must reach the save's number.

**Petrification/polymorph for almost every spell.** The game's code maps the
spell's save kind 5 to the sheet's third save; kind 1 is
paralysis/poison/death, used by the clouds, Poison, Slay Living and the
psionic attacks. The spell save, the one AD&D uses for spells, is never used:
a 3rd-level warrior needs 13 against Psychic Crush (paralysis) and 14 against
Fireball (petrification), where the spell save would be 16.

**Fire, cold and electricity: the d20 counts double.** Each spell's record has
a word of flags saying what kind of damage it does, and the saving throw code
doubles the d20 whenever the kind is fire, cold or electricity. Nothing else
is doubled: not acid (Acid Arrow), crushing (Ice Storm, Magical Stone), poison
(Cloudkill), draining (Vampiric Touch, the Cause Wounds spells) or the psionic
attacks. The doubled spells are:
- fire: Burning Hands, Flaming Sphere, Fireball, Flame Arrow, Minute Meteors,
  Fire Shield, Wall of Fire (both), Focus Heat, Produce Fire, Flame Strike;
- cold: Chill Touch, Cone of Cold;
- electricity: Shocking Grasp, Lightning Bolt.

In between a 1 and a 20 the doubled roll makes saving far easier: needing 14,
a normal d20 saves 35% of the time and a doubled one 70%, which is why
Fireball's victims usually get away with half damage. It isn't AD&D, and the
game never explains it; it may have been meant as a dodge. The log says it on
each save: `d20 = 7, doubled against fire = 14`. The mod's
[**Saving throws against spells**](FEATURES.md#spells-saved-against-with-the-spell-save)
puts the spell save back and takes the doubled d20 away.

The target's spells and effects:
- Blessed +1, Barkskin +1, Spirit Armor +3 (but not on
  paralysis/poison/death saves), and the Save penalty effect −1.
- Prayer: +1 if its caster is on your side, −1 if not.
- Protection from Evil +2 against an evil caster (lawful, neutral or chaotic
  evil); Protection from Fire and from Cold +3 against fire and cold spells;
  Protection from Lightning +4 against electricity.
- +4 against a spell aimed at one target (not an area) when the caster can't
  see you: the caster is Blind, or you're Invisible (or Invisible to Undead,
  against an undead caster) and the caster can't detect invisibility.

Class, race and abilities:
- WIS, against mind-affecting spells, charms and holds, fear and illusions: −6
  at WIS 1, −4 at 2, −3 at 3, −2 at 4, −1 at 5-7, +1 at 15, +2 at 16, +3 at 17
  and +4 at 18 and up.
- CON, on paralysis/poison/death saves: −2 at CON 1, −1 at 2, +1 at 19-20, +2
  at 21-22, +3 at 23-24 and +4 at 25. Dwarves and halflings also add CON x 2 /
  7 (+1 for every 3.5 points); in AD&D that bonus replaces the adjustment
  (with the Loader: [CON as in AD&D](FEATURES.md#con-as-in-add)).
- Druids +2 against fire and electricity; psionicists +2 against
  mind-affecting spells and charms.
- Some spells carry a modifier of their own (a monster's poison at −4).

Spells with rules of their own: creatures of 6th level or lower can't save
against Cloudkill; against Chaos only warriors (fighters, gladiators and
rangers) can; against Dismissal the target adds its level and takes away the
caster's. But "can't save" is −100 on the save, and the game compares the total
with the number needed unsigned (79BBAh), so a total such as −85 reads as 171
and the creature **always saves** (seen in DOSBox: Arena Guards "unable to
save" took half Cloudkill's damage). The patched game's compare is signed, so
"can't save" fails, even on a natural 20 (which the game took as a save before
adding the −100), whatever the Options ([The game's bugs,
fixed](GAME-BUGS.md#spells-and-psionics)). Against Scare no one saves at all: its record allows no save, so the
saving throw ends at its first test and the rules the save code has for Scare
never run. Those rules: 6th level and up always save and everyone below can't,
but for some elf or half-elf priests (AD&D gives elves, half-elves and priests
a bonus), which it asks for as a creature that is both an elf and a half-elf,
so no one qualifies. The patched game allows the save, so the rules run (6th
level and up always save; below 6th, no save, the signed compare making the −100
fail), and lets an elf or half-elf priest save:
[The game's bugs, fixed](GAME-BUGS.md#spells-and-psionics).

Rules in the code that never come into play: Cloak of Bravery's +4 against
fear applies only to a kind of spell that no spell in the game is marked as
(the patched game marks the fear spells: see
[The game's bugs, fixed](GAME-BUGS.md#spells-and-psionics)), and so does
AD&D's DEX defensive adjustment for attacks that can be dodged (+5 at DEX 1 to
−6 at DEX 25 on AC, so −5 to +6 on the save), unless the
[rule change](FEATURES.md#rule-changes) puts it on the fire, cold and
electricity spells. And nothing in the game gives saves from items: there are
no rings or cloaks of protection, which is why the mod adds
[two rings and a cloak](FEATURES.md#new-items). Their +1 is in the log's
saving throws as `+1 Ring of Protection` and `+1 Cloak of Protection` (with
[AD&D's rules for them](FEATURES.md#rings-and-cloaks-of-protection) off, all
of it as `Ring of Protection`).

## Monsters' defences

From the game's damage and fighting code; none of this is in the manual:

- Every creature has a monster kind, and each kind a resistance class and a
  set of properties, in a table the game fills when it starts.
- Every hit has damage kinds: fire, cold, electricity, acid, poison, draining,
  psionic, death, and for weapons crushing, edged or pointed, from the item's
  type; a natural (unarmed) attack's is crushing, fists and monsters' claws
  alike (with the Loader, a party thri-kreen's claws and bite, and Erdlu
  Claw's talons, are edged: [Erdlu Claw](FEATURES.md#new-wizard-spells)).
  A weapon's hit also carries its magic: one bit for +1 or better, one
  for +2 or better and one for +3 or better (the weapon's plus, or its
  ammunition's if that's higher). A monster's own attacks count as magical by
  its level: (level - 2) / 2, so a 6th-level monster hits like a +2 weapon.
- A resistance class is up to four rules: "these kinds of damage: this
  percent of it". The largest percent that applies counts. So "crushing, edged
  and pointed: 0%; +1 or better: 100%" is a monster only magical weapons hurt.
  The game's 14 classes come to: only +1 (or +2) weapons hurt it, sometimes
  with immunity to poison and draining, or to fire; half damage from
  non-magical weapons and psionic attacks (the Rampager); immune to crushing
  weapons (the mastyrials); immune to crushing and pointed weapons, fire and
  acid, so that only edged weapons hurt it (the slimes); immune to fire and
  cold (and half from electricity); half from fire; immune to poison; immune
  to psionic attacks.
- Properties: can't be charmed or held; unaffected by spells left on the ground
  (fogs, clouds, walls, Web, Grease); not held by Grease, Web, Entangle, Solid
  Fog or Quicksand; and hits that also cast one of the monsters' powers on the
  target: 2d6 cold, 2d6 or 20 acid, paralysis, poison of 10 or 30 damage, a
  deadly Poison, disease on 1 hit in 10. The 20 acid (the Rampager's) and a
  corroding touch (the Babau's) can also destroy a worn item (see [Items saving
  against acid](FEATURES.md#items-saving-against-acid)). With the mod's monsters as the
  manual describes them, some of these differ ([which](#the-monsters-as-the-manual-describes-them)):
  the shadows drain STR in place of cold and paralysis, the Babau and the Blue Slaad
  carry the deadly Poison (which kills on a failed save, in a fight too) in place of the
  corroding touch and the disease.
- Undead (race 9 on the character sheet) take nothing from poison and
  draining, and mind-affecting spells, charms and holds don't work on them.
- The game makes the gear of the people the party fights (Kurzak's armour and
  sword, the Arena Guards' bows) in their backpacks, and puts it on only at
  each one's first action in a fight: weapons in hand, armour worn. Until then
  each is AC 10 with its armour unworn, so an opening blow (the game starts the
  fight after it), a backstab, or a first round's blow on one who hasn't acted
  meets no armour. Once on, a weapon in hand is fought with (in place of the
  first two natural attacks) and worn armour counts. The game never puts on
  rings, cloaks, belts, boots or amulets. (With the Loader: [worn from the
  start](GAME-BUGS.md#who-turns-up-and-how).)

The dice log notes a weapon hit that takes less than its roll, or nothing at
all, with what the monster's defences say about it
(`Mastyrial takes none of the 6 damage: crushing weapons can't hurt it`: the
game's mastyrials take nothing from clubs and maces, only from edged and
pointed weapons).

## Spells and effects

What the log says about spells comes from the game's own spell records and
code, checked by casting each spell in a fight. Where the game differs from the
AD&D rules, the log follows the game.

**Damage.** Each spell's record gives its dice: base dice plus dice (and a flat
bonus) for each step of caster level, counted up to level 10. So Fireball and
Lightning Bolt do at most 10d6, and Burning Hands 1d3 + 2 a level. A save halves
the damage, or stops it all for spells such as Chill Touch. A creature that is
Out Cold gets no save and takes the most the dice can do.

**No spell misses.** The game rolls no attack for a spell: Acid Arrow, Turn
Pebble to Boulder, Magical Stone, Condense and the touch spells (Chill Touch,
Shocking Grasp, Vampiric Touch, the Cause spells, Poison) always land, whatever
the target's AC. Its code has a place for a to-hit test (the routine applying a
spell to its target calls one for the missile spells, 78BA0h), but the routine
there always answers "hit". With the Options tab's [Spells roll to
hit](FEATURES.md#spells-roll-to-hit) ticked (the default) they roll against
the target's AC as a weapon does.

**Saves.** Almost every spell is saved against with petrification/polymorph,
and against fire, cold and electricity the save's d20 counts double: see
[The game's saving throws](#the-games-saving-throws).

**How long.** A duration is (caster level × so much + dice) × a unit of time.
A round is 60 game seconds. Some effects last a number of uses instead
(charges):
- Stoneskin: 1 a level + 1d4. Any damage uses a charge, even fire that gets
  through, but only blows are stopped.
- Ironskin: 1d6 blows stopped.
- Mirror Image: 1 a level + 1d4 images. They stop no weapon blow, and take a
  spell for one creature three times in four, whoever cast it, so Armor cast on
  oneself is lost, and an image with it. (With the Loader: [each hit and each foe's
  spell](GAME-BUGS.md#spells-and-psionics).)
- Invisibility: one attack or hostile spell ends it. Improved Invisibility is
  timed instead, so attacking doesn't end it.
- Minor Spell Turning: one spell turned back.
- Armor: a number of damaging hits, one charge each (with the Loader: see
  [The game's bugs, fixed](GAME-BUGS.md#spells-and-psionics)).

Charm, Feeblemind, Web and a few others last until removed.

**What effects do**, from the game's code:

| Effect | In the game |
|---|---|
| Blessed / Cursed | +1 / −1 to hit (Bless also +1 on saves); each one cancels the other instead of being added |
| Hasted / Slowed | Hasted: double movement and attacks, +2 initiative (the game keeps no ages: it costs nothing; with the Loader, [a year of age and a system shock roll](FEATURES.md#ages-and-magical-aging)). Slowed: half movement and attacks, loses every other turn, −4 to hit, AC 4 worse, −2 initiative. Each cancels the other; Free Action and Protection from Paralysis stop Slow |
| Paralyzed | Loses its turns, can't move, fails every saving throw. Free Action and Protection from Paralysis stop it |
| Stuck (Grease, Web, Entangle, Solid Fog, Quicksand) | Can't move; Free Action stops it; some creatures are immune |
| Afraid | The computer runs it; it can't attack or cast. Undead are immune, and Cloak of Bravery stops the next fear (and ends) |
| Charmed | Joins the caster's side, run by the computer |
| Confused | Each turn a d10: 1 runs off, 2–6 does nothing, 7–9 fights for a side picked with a d2, 10 acts normally (the log shows the rolls) |
| Berserk | Fights for a side picked at random each turn; can't cast. In the game a party member could be left on the monsters' side when this or Confused ended; the patched game puts it back ([bugs fixed](GAME-BUGS.md#sides-and-blows)) |
| Can't Attack (Stinking Cloud) | Can't attack or cast harmful spells |
| No spell use, Feeblemind | Can't cast spells. Feeblemind also makes INT and WIS 3 while it lasts (as they were after) and nothing ends it; with the manual's spells it stops psionic powers too, and the mod's Heal cures it |
| Blind | AC 4 worse, −2 initiative, can't cast spells that need sight |
| Acid (Acid Arrow) | 2d4 acid damage at the start of each round it lasts, a round for each started minute of its time. In the game it never burned after the hit; the patched game burns it ([bugs fixed](GAME-BUGS.md#spells-and-psionics)) |
| Poisoned | Fatal (1000 damage) if time passes out of combat, for instance resting, before it wears off or is cured |
| Cloak of Fear | Whoever hits the wearer has Cause Fear cast on them, once |

Other things the game does its own way:
- Strength adds 1d6 to STR while it lasts, up to 24 (with the manual's spells
  1d8, 1d6 or 1d4 by class, and not added to Adrenalin Control's: the bigger
  counts). The same goes for the psionic Adrenalin Control, and Weakened or
  lending strength takes it away (never below 3). A second Strength replaces
  the first.
- Chill Touch takes 1 STR (Weakened) from a creature that fails its save, but
  the spell's time is 0, so the effect ends at once (with the manual's spells,
  an hour).
- CON 20 or more gives a hit point back every 5 minutes of game time, at any
  such CON (AD&D: one an hour at 20 to one every 10 minutes at 25; with the
  Loader: [CON as in AD&D](FEATURES.md#con-as-in-add)). Every party member
  gets a psionic strength point back every 5 minutes.
- Enlarge adds 10% a level of its caster to the whole of a melee hit's
  damage, STR's bonus and the weapon's plus included, rounded down (with the
  Loader: [only the weapon's dice](FEATURES.md#enlarge-multiplies-the-weapons-dice-only)).
- Shillelagh, Flame Blade and Spiritual Hammer need an empty hand: with a
  weapon ready the game says "Failed, weapon in hand" and nothing happens.
- Death spells (Slay Living, Dismissal) do the target's HP + 10 on a failed
  save.
- In the arena, summonings fail ("Your summoning goes unanswered").
- A spell's caster level is the caster's highest level in a class that shares
  a sphere with the spell. Priests have one element each (cleric, druid and
  ranger classes come in air, earth, fire and water): Flame Blade, Focus Heat
  and Flame Strike are fire spells, Blood Flow and Dehydrate water, Deflection
  air, while spells such as Bless, Barkskin or Spiritual Hammer belong to
  every sphere. Cast by a priest of another element, an elemental spell counts
  caster level 0. The game shows each priest only their element's spells, so
  this only happens if a character somehow has the others.
- Clerics never have the common 4th and 5th-level priest spells: Cure Serious
  and Critical Wounds, Raise Dead, Neutralize Poison, Free Action and the rest
  are marked for druids alone (a cleric's 4th and 5th levels are its element's
  spells only). The mod's Healer kit gives them to a water cleric.

The spell's area catches its caster too. Cilla's Scare made her Afraid, and her
Fireball, cast at a Slig next to her, killed her.

### Each cleric spell against the manual

What the game's records and code do with each cleric spell, next to the manual
(pages 68–78). "Save" is the game's petrification/polymorph save unless named
(the spell save with the [rule
change](FEATURES.md#spells-saved-against-with-the-spell-save)); durations are in
rounds (a turn is ten). The log column is what the dice log shows for it; every
effect line also says what the effect does.

(The rows below are the game's own spells. Six of them, Bestow Curse, Blood Flow, Cause Fear,
Quicksand's save, Ironskin and Free Action, are set as the manual has them by the rule change [Spells
and psionics as the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them),
on by default, which changes wizard spells and psionic powers too: its table lists them all.)

| Spell | The manual | The game | The log |
|---|---|---|---|
| Bless | +1 to hit; not on anyone next to a monster; 6 rounds | +1 to hit and +1 on saves; not on anyone next to an enemy (the patched game measures that from where each stands); cancels Curse; 6 rounds | the effect |
| Cause Fear | flees 1d4 rounds; save | Afraid for 1 round a level on a failed save; undead immune; Cloak of Bravery +4 (with the patched game) | the save and the effect |
| Cause Light Wounds | 1d8 | 1d8, no save | the roll and the HP lost |
| Cure Light Wounds | heals 1d8 | heals 1d8 (Healer kit +1) | the roll and the HP regained |
| Curse | −1 to hit; not next to the party; 6 rounds | −1 to hit, no save; cancels Bless; 6 rounds | the effect |
| Entangle | moves very slowly; save for half; 1 turn a level | Stuck (can't move at all) on a failed save, for 1 round | the save and the effect |
| Invisibility to Undead | undead ignore the warded creature; 6 rounds | until it attacks or casts at an enemy; +4 on saves against an undead caster's spells aimed at it | the effect |
| Magical Stone | three stones, 1d4 each, 2d8 against undead | three stones, 1d4 crushing each (seen in DOSBox), no save; its record has nothing more against undead | the roll and the HP lost |
| Protection from Evil | AC and saves +2 against evil; 3 rounds a level | AC −2, +2 on saves against an evil caster; 3 rounds a level | the effect |
| Remove Fear | ends fear | ends Afraid | the effect ending |
| Shillelagh | a magical club in hand | a Shillelagh in an empty hand (a weapon held: "Failed, weapon in hand"); 4 + 1 a level rounds | the effect |
| Aid | as Bless, and 1d8 extra HP | Blessed and 1d8 extra HP; 1 + 1 a level rounds | the 1d8 and the effects |
| Barkskin | base AC 6, 1 better per 4 levels; +1 on saves | the same | the effect |
| Charm Person or Mammal | fights for the cleric; save; combat only | Charmed on a failed save | the save and the effect |
| Dust Devil | a dust devil fights for the cleric; 2 rounds a level | summons one, 2 rounds a level (none answers in the arena) | the summoning |
| Find Traps | traps found; 3 turns | Detect Traps: anyone finds traps for certain; 3 turns | the effect |
| Flame Blade | a blade of fire, 1d4+6; 4 rounds + 1 per 2 levels | a Flame Blade in an empty hand, as Shillelagh | the effect |
| Hold Person | rigid; 2 rounds a level; save | Paralyzed on a failed save, 2 rounds a level | the save and the effect |
| Resist Fire, Resist Cold | half damage, +3 on saves; 1 round a level | +3 on saves against fire (cold) spells, and half the damage of a spell that is all fire (cold) | the effect, and "(halved: ...)" on the damage |
| Spiritual Hammer | a hammer that hits +1 monsters | a Spiritual Hammer in an empty hand, as Shillelagh; 3 + 1 a level rounds | the effect |
| Bestow Curse | −4 on attacks and saves; save; permanent | Cursed: −1 to hit only, no save; its record gives no duration (it stays until dispelled); Remove Curse doesn't end it | the effect |
| Cause Blindness or Deafness | blind or deaf; save | Blind (AC 4 worse, −2 initiative, no spells needing sight) on a failed save, until cured | the save and the effect |
| Cause Disease | saps STR and HP; save | Diseased on a failed save: nothing is lowered; a STR something else lowered stays down until it is cured | the save and the effect |
| Conjure Lesser Elemental (four) | 1 turn + 1 round a level | summons one, 10 + 1 a level rounds | the summoning |
| Cure Blindness or Deafness, Cure Disease | cure them | end Blind, Diseased | the effect ending |
| Dispel Magic | removes spells | each effect separately, d100 at or under 50 + 5 x the dispeller's level − 5 x the effect's caster level (the levels of every effect of that kind on the target, usually one); can't touch Biofeedback, Diseased, Feeblemind, Synaptic Static, Mind Bar, Poisoned, Graft Weapon, No spell use, Stuck, nor any effect past 73 (it looks at 0 to 73 only: the mod's Friends, 74, and a stinkpot's Nauseated, 75) | each d100 |
| Magical Vestments | AC 5, 1 better per 3 levels above 5; 5 rounds a level | the same | the effect |
| Negative Plane Protection | stops one draining attack by undead | the game's own never worked; the patched game: a save against paralysis/poison/death stops one, and the undead takes 2d6 | the save and the effect |
| Prayer | +1 to hit and saves for friends, −1 for foes; 1 round a level | the same | the effect, and each save's ±1 |
| Protection from Fire | +3 on saves, half damage | as Resist Fire, lasting 1 turn a level | as Resist Fire |
| Remove Curse | ends Bestow Curse; unreadies cursed items | puts a lowered STR back to the score; ends no curse | the STR change |
| Remove Paralysis | ends paralysis and slow | ends Paralyzed and Slowed | the effects ending |
| Summon Insects | a cloud: 4 a round, AC 2 worse, −2 to hit | summons a creature for 1 round a level | the summoning |
| Abjure | sends extraplanar creatures home | d20 of 11 − caster level + the target's level or more, then a summoned creature is sent away (1000 damage) | the d20 and the result |
| Blood Flow | heals 2d6, or stuns an enemy up to 4 rounds; save | heals its own side 2d6; anyone else is Paralyzed for 1d4 rounds, no save, and takes no damage | the roll, or the effect |
| Cloak of Bravery | +4 on saves against fear, once | ends fear; the next fear fails and ends it; +4 against fear spells (with the patched game) | the effect |
| Cloak of Fear | the first who hits it must save or flee, once | the first who hits it has Cause Fear cast on them | the effect, then the Cause Fear |
| Condense | 3d6 | 3d6 crushing, no save | the roll and the HP lost |
| Cure Serious Wounds | heals 3–17 | heals 2d8+1 (Healer kit +1 a die) | the roll and the HP regained |
| Cause Serious Wounds | 3–17 | 2d9 in the game; 2d8+1 with the patched game | the roll and the HP lost |
| Dehydrate | 2d6 + 1 a level | the same, no save | the roll and the HP lost |
| Dust Cloud | blocks sight and missiles | a cloud on the ground; its record has no damage or effect | the cast |
| Focus Heat | 2d6 + 1 a level; save for half | the same, fire (the save's d20 doubled, or DEX with the rule change) | the save, roll and HP |
| Free Action | breaks slow, hold and webs | ends Paralyzed and Slowed when cast; then can't be Paralyzed, Slowed or Stuck, 1 turn a level | the effect |
| Neutralize Poison | ends poison | ends Poisoned | the effect ending |
| Poison | save or die | Poisoned on a failed save against paralysis/poison/death: no harm in a fight, but 1000 damage once time passes out of one (a rest) before it's cured | the save and the effect |
| Produce Fire | 2–5 in a 12' square | 1d6 fire, no save | the roll and the HP lost |
| Protection from Evil 10' Radius | +2 AC and saves for the target and friends beside it | each round, Protection from Evil for that round on its side close by; 1 turn a level | the effect |
| Protection from Lightning | +4 on saves, half damage | +4 on saves against lightning spells, and half a spell's damage that is all electricity | as Resist Fire |
| Cause Critical Wounds | 6–27 | 3d9 in the game; 3d8+3 with the patched game | the roll and the HP lost |
| Conjure Elemental (four) | 1 turn a level | summons one for 10 + 1 a level rounds | the summoning |
| Cure Critical Wounds | heals 6–27 | heals 3d8+3 (Healer kit +1 a die) | the roll and the HP regained |
| Deflection | small missiles miss | missile attacks miss it | the effect |
| Dispel Evil | AC −7 against summoned evil creatures, which save when hit | AC −7 against evil; no save for the creature | the effect |
| Flame Strike | 6d8; save for half | the same, fire | the save, roll and HP |
| Insect Plague | 1 a round, blocks sight, no spellcasting | Afraid on a failed save, 2 rounds a level, and no spells for a round; no damage | the save and the effects |
| Ironskin | immune to weapons | 1d6 blows stopped | the effect |
| Quicksand | sinks and is held; 1 turn + 1 round a level | Stuck on a failed save, for 1 round | the save and the effect |
| Raise Dead | by CON and how long dead; −1 CON; 1 HP | always works on someone dead who isn't an elf: −1 CON, 1 HP | the HP and the CON change |
| Slay Living | dies on a failed save, 3–17 if saved | HP + 10 damage on a failed save against paralysis/poison/death; half of 4d8 (2–16) if saved, as the Loader's description now says | the save and the damage |
| Wall of Fire | fire to those passing through | 4d4 + 1 a level fire, no save | the roll and the HP lost |

### Turn Undead

A cleric's Turn Undead is a button on the USE screen (the spell 190), not a spell: it takes no slot.
The button shows for a character whose sheet has a cleric's element (air, earth, fire or water); druids
have none, so they never get it. It tries each undead creature (race 9) in its area, one at a time, in
a fight or out of one (out of one, it starts a fight). For each the game rolls a d20 and needs
10 + 3 x (column - row) or more:

- the column from the creature's hit dice: 1 to 4 as they are, 5 and more one further (5 HD is column
  6), at most 13;
- the row from the priest level (the best of the cleric classes): 1 to 10 as they are, 11 counts as
  10, 12 as 11, 13 and more as 12;
- a 22 is made 20; anything over that can't be rolled, and 1 or less always works.

On the number or more the creature is **destroyed** (the game does it 1000 damage). Otherwise nothing
happens: no "turned" (fleeing) result, nothing remembered. The same cleric can try again on its next
turn, on the same creature too, in that fight and in later ones; the use ends the cleric's turn. Its
description says "May be used once per creature": the game doesn't keep to that. Magic resistance is
checked first; there is no saving throw.

Against AD&D's turning table (2nd edition), the steps of 3 are the same, but:

- AD&D has a row between 1 and 2 HD (zombies) and one between 5 and 6 HD (ghasts). The game's 2 HD uses
  the zombie row and its 3 HD AD&D's 2 HD row (both one easier than AD&D's 2 and 3-4 HD rows), and its
  5 HD the ghast row (one harder than AD&D's 5 HD row); 1, 4 and 6-11 HD are AD&D's rows.
- AD&D's T (turned: the undead flee) and D (destroyed) are all destroyed in the game, and D* (2d4 more
  of the kind destroyed) is one.
- AD&D's levels 12-13 share a column; the game gives level 13 the 14+ one (one easier).

The game's undead (their sheets in SEGOBJEX.GFF): Zombie, Convert and Tara's Follower 2 HD, Shadow 3 or
6, Skull Elder 4, Shadow Guard, Shadow King, Shadow Prince, Shadow Worker, Aposs, Cragg, Tanelyv,
Tristram and Tynan 6. A 3rd-level cleric needs 7 against a Zombie and a 20 against the 6 HD ones (a 1st or 2nd
level cleric can't turn those at all).

The dice log shows each try: `Seneca turns Zombie: d20 = 12, needs 7+ (priest level 3 vs 2 HD) ->
destroyed` (code: DSUN.EXE 7ADB7h, the number at 7AE01h-7AE48h, the d20 at 7AE4Dh).

**With "Spells and psionics as the manual describes them"** (the default) all of the above is the game's rule
only with the box unticked. Ticked, the mod takes over where the game works out its number
(7AE01h) and uses AD&D's turning table instead ([below](#adds-turning-table)). How it fits the game: a
turned undead is made Afraid with the effect Cause Fear gives (the game's own way of adding it
would refuse it to the undead, who are immune to fear spells); a priest who failed against an
undead and tries it again ends the try at once, the turn spent, with no roll; the failures are forgotten when the next fight's first
round starts, and by a turning out of a fight, which starts a new one (so a failure from out of a
fight is forgotten as that fight's first round starts). Magic resistance is still checked first, by
the game. The dice log says the number, the roll and the outcome (`... needs 10+ (priest level 3
vs 2 HD, AD&D's table) -> turned: flees 3d4 = 7 rounds (Afraid)`).

#### AD&D's turning table

With the box ticked (the default) the game's routine looks up AD&D's table (2nd edition) by the
undead's hit dice and the priest's level:

| Hit dice \ priest level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10-11 | 12-13 | 14+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 or less | 10 | 7 | 4 | T | T | D | D | D\* | D\* | D\* | D\* | D\* |
| 2 | 16 | 13 | 10 | 7 | 4 | T | T | D | D | D\* | D\* | D\* |
| 3-4 | 19 | 16 | 13 | 10 | 7 | 4 | T | T | D | D | D\* | D\* |
| 5 | 20 | 19 | 16 | 13 | 10 | 7 | 4 | T | T | D | D | D\* |
| 6 | --- | --- | 20 | 19 | 16 | 13 | 10 | 7 | 4 | T | T | D |
| 7 | --- | --- | --- | 20 | 19 | 16 | 13 | 10 | 7 | 4 | T | T |
| 8 | --- | --- | --- | --- | 20 | 19 | 16 | 13 | 10 | 7 | 4 | T |
| 9 | --- | --- | --- | --- | --- | 20 | 19 | 16 | 13 | 10 | 7 | 4 |
| 10 | --- | --- | --- | --- | --- | --- | 20 | 19 | 16 | 13 | 10 | 7 |
| 11 or more | --- | --- | --- | --- | --- | --- | --- | 20 | 19 | 16 | 13 | 10 |

- A number: a d20 of it or more **turns** the undead: it is Afraid (as Cause
  Fear makes a creature) and flees for 3d4 rounds. The Player's Handbook says
  turned undead flee or are kept at bay but gives no time; 3d4 rounds is the
  first edition's, used by the 2nd-edition-compatible rules too.
- **T** turns it with no roll; **D** destroys it with no roll (the game's own
  destruction); **D\*** destroys it, and up to 2d4 more of its kind (the same
  monster: one sheet) caught by the same turning are destroyed with no roll.
- **---**: no chance; nothing is rolled.
- A d20 under the number: not turned, and **that priest can't try again on that
  undead in this fight** (the button's own text: "May be used once per
  creature"); another priest still can. Forgotten when the next fight starts.
- The game has no kinds of undead, so its hit dice pick the row (AD&D's
  zombie, ghast and special rows aren't used: the game's 2 HD Zombie uses the
  2 HD row). Each use ends the priest's turn, as before; it tries each undead
  in its area, one at a time.

## Psionics

Psionic powers are numbered after the spells (Detonate 138 to Thought Shield
171) and go through the same code: the same records for damage, saves and
effects, so the log treats them like spells and names them. Some things are
their own:

- **Level.** A power works at the character's psionicist level; anyone else
  with psionic powers counts as level 1.
- **PSP.** A power costs its PSP to use. Kept-up powers (Inertial Barrier,
  Biofeedback, Graft Weapon...) cost more PSP at the start of each round, and
  the game puts them on again for another round; when the PSP runs short, the
  power drops. The log shows every change in a party member's PSP
  (` K'ratchek spends 18 PSP (52 -> 34)`).
- **The power check.** Each use rolls a d20 that must come up at or under the
  power's score: the ability the power uses (CON for most psychometabolism and
  psychokinesis, WIS for telepathy, Disintegrate and Enhanced Strength, INT for Superior
  Invisibility, Mind Bar and Synaptic Static) plus the power's adjustment, from
  −1 (Lend Health) to −7 (Mind Blank). A 1 always works and a 20 always fails;
  a failure says "psionic power check fails" and costs half the PSP. The game
  also keeps a number for each power a character knows, and adds anything
  above 1 to the score, but no code was found that raises it. Near someone
  else's **Synaptic Static**, the user first rolls a d20 against that number
  (the game reads the ability for it and drops it, so it's 1 for most
  characters): over it, "psionics disrupted by static". Otherwise the Static's
  keeper rolls a d20 at or under their own Synaptic Static score, and no lower
  than the user's, to disrupt it. The log shows each of these rolls.
- **Detonate** (the daggorans use it too): besides 1d10 from the blast, it
  picks the worn item that breaks most easily, the one with the lowest
  fragility number (under 6: a cloak 3, a bone helm or leather chest armour 4,
  bone scale arm and leg armour 5; a short sword's 6 is never picked; on a tie,
  the first), and destroys it outright on a d20 under 15 less its plus (70% for
  a plain item; one of a stack). The log shows the check.
- **Psionic defence.** Attacked by a psionic attack mode (Psychic Crush, Ego
  Whip, Id Insinuation, Psionic Blast), a character defends with WIS − 7, or
  with a defence mode already raised (used beforehand, it stays up at no cost
  each round) if that does better: the mode's rank plus half its cost, which
  the character pays again, if they can. A monster defends with its level where
  that's better. Two rolls of 1 to that number, both over the attacker's own
  roll for the power, resist it.
- **Mind Bar** adds 75% magic resistance against mind-affecting spells:
  charms, holds, Scare, Confusion, Chaos, Feeblemind, Minor Malison. The log's
  magic resistance line counts it, and Lower Resistance halving the result
  (with the manual's spells: 30% + 1% a caster level off instead).
- **Body Weaponry** makes unarmed attacks 2d4; **Animal Affinity** at least
  1d10. Only the first of a creature's natural attacks: a thri-kreen's four
  claws, not its bite.
- Monsters use them too: the Screamer Beetle's special attack is Psychic
  Crush (1d8, save vs paralysis/poison/death for half).

### Each power against the manual

What the game's code does with each power, next to the manual's text. Every use
also logs the power check and the PSP spent; a power with a save logs the save.

| Power | The manual | The game | The log |
|---|---|---|---|
| Detonate | 1d10 to everyone within 10'; may turn an item to ash | 1d10 to the target only, no save; then destroys its worn item that breaks most easily on a d20 under 15 less its plus (above) | the blast's damage and the item check |
| Disintegrate | save vs death or turned to ash | save vs paralysis/poison/death (the same save) or 10,000 damage | the save and the damage |
| Project Force | 1d6 plus the target's AC | 1d6 plus the target's AC (less against a good AC), no save | the 1d6 and the HP lost (with the AC in it) |
| Ballistic Attack | 1d6 on a successful hit | 1d6, no attack roll, no save | the damage |
| Control Body | the target fights for you at −6 to hit | Charmed for 5 rounds on a failed save vs paralysis/poison/death: it joins your side under the computer's control, with no −6 | the save and the charm |
| Inertial Barrier | halves damage from breath, missiles, gas, acid, ice storms | missile attacks miss its user outright; nothing else | "missile attacks miss it" |
| Animal Affinity | claws, 1d10 | unarmed attacks at least 1d10 | the effect |
| Energy Containment | no damage from electricity, cold, fire, heat, sound | no damage that is only fire, cold, electricity or magic | the effect |
| Life Draining | drains up to 6 HP as extra HP for an hour | 1d6 damage, the same as extra HP for the user | the drain roll and the HP |
| Absorb Disease | takes the target's disease to cure it | takes the disease (the mod's fix: the game also gave 1d6 STR) | the effect |
| Adrenalin Control | STR + 1 to 6 | STR + 1d6, at most 24 (with the manual's spells not added to Strength's: the bigger counts) | the 1d6 and the STR |
| Biofeedback | damage −2 and AC −1 | AC −1, and 2 off each blow and any other crushing, edged or pointed damage (79BF9h), leaving 0 of a blow of 2 or less (with the manual's spells at least 1) | "AC −1", and `-2 Biofeedback` on a hit's line |
| Body Weaponry | the arm as a wood or steel weapon | unarmed attacks 2d4 | the effect |
| Cell Adjustment | heals wounds, cures diseases | heals 2 HP (with the manual's spells 1d4); its record cures disease (Diseased removed) | the HP regained; with the manual's spells the 1d4 and the cure |
| Displacement | attacks miss the image; AC −2 | AC −2 | the effect |
| Enhanced Strength | STR up to 24, cost twice the points | STR 24 (a higher one kept), cost (24 − STR) × 2 | the effect and the PSP |
| Flesh Armor | armour by level, no penalties | AC 10 − level at best | the effect |
| Graft Weapon | +1 to hit, can't switch weapons | +1 to hit; stops picking pockets, locks and climbing | the effect |
| Lend Health | gives HP, within both maximums | gives the target's missing HP, keeping the user at 5 or more | the HP both ways |
| Share Strength | gives STR at 2 for 1 | target + a, user − 2a (a up to 24 − its STR and (the user's STR − 3) / 2) | the effects (not the amount) |
| Domination | controls the target; combat only | Charmed for 5 rounds on a failed spell save; combat only | the save and the charm |
| Mass Domination | up to 5 creatures | its record targets one creature, as Domination, for 10 rounds | the save and the charm |
| Psychic Crush | up to 6 damage | 1d8, half on a save vs paralysis/poison/death; psionic defence first | the defence, save and damage |
| Superior Invisibility | unseen; ends if it attacks | Invisible; attacking or casting at an enemy ends it | the effect |
| Ego Whip | stunned 1d4 rounds | can't attack or cast harmful spells for 1d4 rounds; psionic defence, no save | the defence and the effect |
| Id Insinuation | paralyzed 1d4 rounds; combat only | Paralyzed 1d4 rounds; psionic defence, no save; combat only | the defence and the effect |
| Psionic Blast | believes it has lost 80% of its HP | loses real HP down to a fifth of its maximum on a failed save vs paralysis/poison/death; psionic defence first; with the Loader, a party member gets the HP back at the fight's end (one knocked out wakes), and until then a blow that would kill it knocks it out | the defence, save, HP lost and given back |
| Mind Bar | 75% resistance to mind spells | the same | the resistance roll |
| Synaptic Static | no one nearby can use psionics | its keeper can't; anyone else must beat the static (above) | the contest |
| Tower of Iron Will, Intellect Fortress, Mental Barrier, Mind Blank, Thought Shield | defences against psionic attacks | defence modes (above) | the defence rolls |

What each power costs to use and to keep up is in the game's own table, given
in full in the [Player's Guide](PLAYER-GUIDE.md#psionics). Three are worked out
as they're used: Enhanced Strength (24 less the target's STR) × 2, and
Domination and Mass Domination 3, 8, 13 or 18 by the target's level (below 6,
below 11, below 16, and up). Defence modes cost nothing to keep up.

## Spells and psionics as the manual describes them

This section is the mod's, not the game's: the detail of the rule change [Spells and psionics as the manual describes
them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them), on by default, whose table there
lists each spell and power it changes. Its Turn Undead is [above](#adds-turning-table).
How it is done: [DEVELOPMENT-RULES.md](DEVELOPMENT-RULES.md#spells-and-psionics-as-the-manual-describes-them).

### Each spell in more detail

- **Fire Shield**: +2 on its caster's saves against spells of fire or cold
  (`+2 Fire Shield` in the log's save line); the half damage from them and the
  damage a melee attacker takes back are the game's own.
- **Blur**: +1 on its creature's saves against spells (`+1 Blur`), beside the
  game's −2 to attackers.
- **Chill Touch**: the game already takes 1 STR off a creature that fails its
  save (Weakened), but gave the effect no time, so it ended at once; it now
  lasts an hour (60 rounds), the STR coming back after (AD&D's lost Strength
  comes back a point an hour). Each touch takes 1 more. On an undead (which, in
  AD&D, takes no damage or STR loss and flees) it does nothing but make the
  undead Afraid for 1d4 rounds, no save:
  `Chill Touch on Zombie, undead: no damage, no STR lost; Afraid 1d4 = 3 rounds instead`.
  With [Spells roll to hit](FEATURES.md#spells-roll-to-hit) the touch rolls first.
- **Cloudkill** by the target's level for saves (a monster with no class: its
  hit dice): under 4, it dies with no saving throw; 4 or 5, it saves against
  poison (at the record's −2) or dies; 6 and up, the damage as before, a save
  halving it. The death is the cloud's own damage a thousand times over, each
  time the cloud strikes (as cast and at each round in it):
  `Cloudkill: Guard dies (under 4 HD: no save; its level for saves 3)`.
  AD&D's bands are by hit dice (4+1, 6); the game's levels are whole numbers.
- **Feeblemind**: the game already makes INT and WIS 3 while it lasts, and
  they come back as they were when it ends; it stops spells. With the box it
  stops psionic powers too (each fails its power
  check, costing half the PSP as any failed check does:
  `Seneca is feebleminded: Biofeedback can't be used (no psionics)`), and the
  mod's Heal (with [the new spells](FEATURES.md#6th-level-priest-spells)) cures it: `Heal cures Seneca's Feeblemind: INT and WIS as they were`.
  Dispel Magic still can't (the game's rule). The scores are worked out afresh
  from the character sheet's, which Feeblemind never changes.
- **Lower Resistance**: the creature's magic resistance 30% + 1% a level of the
  caster lower, at least 0 (`-40 Lower Resistance on it, level 10`), where the
  game halved it; the level is the cast's, kept with the effect. Cast at a
  creature already under one, the bigger of the two counts.
- **Strength** and **Cat's Grace** roll by the target's classes, the best die of
  a multiclass character's: `Strength: 1d8 = 6 (fighter) -> Ester's STR +6`.
  Adrenalin Control stays 1d6. Strength and Adrenalin Control on one creature
  don't add up: the bigger counts (Strength 1 and Adrenalin Control 4 make STR +4).
  A second Strength or Cat's Grace replaces the first (the game's own).
- **Rainbow Pattern** holds 1 round a caster level (its record's time), and a
  creature it holds is freed by any damage, a blow or a spell
  (`Guard takes 20 damage: Rainbow Pattern's hold on it ends`); Hold Person's
  and the others' Paralyzed aren't touched. The pattern itself stays on the
  ground for a few rounds (2d3, the game's), and anyone in it (the caster too)
  saves again each turn.
- **Cell Adjustment** heals 1d4 hit points (the game's 2), and its record already
  cures disease: `Cell Adjustment: 1d4 = 3 -> Seneca healed 3 HP, and Seneca is cured of disease`.
- **Biofeedback**: the game already takes 2 off each blow (melee or missile) and
  any other crushing, edged or pointed damage, but a blow of 2 or less did none;
  now at least 1. The log's hit line shows it (`-2 Biofeedback`).

### The monsters as the manual describes them

Where the manual (pp. 33-52) gives a monster a power its record hasn't, or the record
a power the manual hasn't:

| Monster | The game | As the manual |
|---|---|---|
| Shadow | 1d4+1, and 2d6 cold, each hit; cold hurts it | its chilling grasp's light 1d4+1, and **1 STR drained** each hit, no save (Weakened for 2d4 turns; each hit its own, so they add up, STR never below 3); unaffected by cold, +1 weapons to hurt it (as before) |
| Greater Shadow (the 6-HD Shadow, Shadow Guard, King, Prince and Worker, Cragg, Tanelyv, Tristram, Tynan) | 2 attacks of 2d6, each paralysing for 2d6 rounds (a save); any spell hurts it in full | 2 attacks of 2d6 and **1 STR drained** each hit, as the shadow's; "unaffected by cold-based attacks"; +1 weapons, AC 4, HD 6 and THAC0 15 as before |
| Babau | its claws a corroding touch (worn armour and the weapon held may be eaten) | its horn's **deadly poison** (the priests' Poison, AD&D's: a save against poison, else death, in a fight too) |
| Blue Slaad | disease, 1 rake in 10 | its bite's **deadly poison**, as the babau's |
| Tari | no disease; HD 2, THAC0 18, AC 10, a 1d2 bite | a bite of **1d3** that brings **disease 1 in 20** (a save against poison), HD 3, THAC0 17, AC 6 (better with the leather some wear) |
| Styr | no breath; any weapon hurts it; HD 10, THAC0 11 | **breathes fire for 3d6** one turn in four (a save halves), **+1 weapons** to hurt it, HD 14, THAC0 7; MR 30%, AC 0, 4 attacks of 2d10 as before |
| Djinn | a fighter | at its first turn of a fight it **turns invisible** (Improved Invisibility, 14 rounds) and makes **1d4+3 mirror images** of itself ("their ability to use illusions and become invisible") |

The Look box and its description say so (`1 STR drained (Weakened, 2d4 turns;
no save)`, `Breathes fire for 3d6 one turn in four`), and the dice log names
each: `Shadow drains 1 STR from Gerakis: Weakened for 2d4 = 5 turns (no save)`,
`Tari's bite on Seneca: 1 in 10, and a d2 for the manual's 1 in 20: 2 -> no
disease`, `Djinn turns invisible (14 rounds) and makes 6 mirror images of
itself`. The Styr, the Djinn and the Tari are made so in the Loader's copy of
the game's objects, and in a saved game too, as they come on the map with the
Loader running (and back as the game's with the box unticked).

### Known differences left as they are

The game has no way to do these as the
manual says, or the change would make a different spell rather than fix one:

| Spell | The manual | The game |
|---|---|---|
| Confusion, Chaos | a save each round | one save, as the spell lands |
| Mirror Image | images last 3 rounds a level | images last until struck (an effect lasts either uses or a time) |
| Shield | better saves against missiles | the game has no saves against missiles; Shield's AC 4 works, and it stops Magic Missile |
| Invisibility | ends when its creature casts any spell | ends on an attack, or a spell at an enemy |
| Protection from Normal Missiles, Deflection, Inertial Barrier | stop normal missiles (Inertial Barrier: halves breath, missiles, gas, acid) | one effect for all three: a missile weapon's hit does no damage, and breath weapons miss outright; no spell is stopped, Magic Missile included. They differ only in time (a turn a level; level + 5d3 rounds; while kept up), who can have them (anyone touched; the caster alone) and cost |
| Control Body | the controlled creature fights at -6 | Charmed 5 rounds, no -6 |
| Mass Domination | up to five creatures | one |
| Detonate | 1d10 to everyone within 10' | the target only |
| Quicksand | held 1 turn + 1 round a level | Stuck a round at a time, put on again each round while the quicksand lasts (5d3 rounds of its own); its record's time changes nothing |
| Feeblemind | INT and WIS drop "dramatically" | to 3 (the game's own choice, an idiot's in AD&D) |
| Chill Touch | Strength back a point an hour, repeated touches | each touch's point back after an hour |
| Rainbow Pattern | one save, as it is cast (a time of its own: "special") | the pattern stays on the ground for 2d3 rounds of its own and makes everyone in it, the caster too, save again each turn (a round a level and damage ending a hold are the manual's: above) |
| Biofeedback | damage −2 | −2 from blows and any crushing, edged or pointed damage, not from fire or other spells |

What else the manual and the game disagree on, and why the rest is left:
[spells against the manual](https://github.com/daaki85/darksun-obsidian-edition/blob/obsidian-edition/reports/spells-against-the-manual.md)
(a report in the repository).

## How the game works out thief skills

The game never shows thief skills, but it rolls them: for traps, and for the
locks, walls and so on its scripts ask for (see
[Where the game rolls thief skills](#where-the-game-rolls-thief-skills)). The
game gives the skills no names; its eight are AD&D's in AD&D's order (pick
pockets, open locks, find/remove traps, move silently, hide in shadows, hear
noise, climb walls, read languages), which the checks below fit. The roll is a
d100 that must come in under the skill's chance. The game's code works the
chance out as:
- a base for each skill, in that order (28, 18, 13, 28, 18, 23, 78, −4),
- plus 4 for each thief level,
- plus a racial adjustment. These are AD&D's, for example a dwarf gets +10 to
  open locks, +15 to find traps, −10 to climb walls and −5 to read languages.
- plus DEX: −5 for each point below 12, 11, 12, 13 or 11 (the first five
  skills); +5 for each point above 16, 15, 17, 16 or 16; and −3 for each point
  above 21, 20, 21, 19 or 19, so very high DEX gains less,
- minus an equipment penalty (5, 0, 0, 10, 5, 0, 10, 0) when the thief has
  anything at all in the leg armour slot, the quiver or either hand. That is
  the game's own check: it doesn't look at what the item is (leather or metal)
  and ignores chest and arm armour and helmets, so a thief holding any weapon
  pays it. (The manual's "anything other than leather-type armor" is AD&D's
  rule, not what the code does.) (With the Loader: [no equipment
  penalty](GAME-BUGS.md#thief-skills).)
- plus the situation's bonus or penalty (a hard lock, say).

With **Thieves as in AD&D** ticked (see
[Thief skills from AD&D's table](FEATURES.md#thief-skills-from-adds-table)),
the first two and the DEX part are AD&D's instead.

Only characters with thief levels have the skills; everyone else's chance is
0. The character's condition must be Okay (the status the character screen
shows under HP): a thief who is Stunned, Out Cold, Dying and so on can't use
the skills. A character not yet played (New, before the game starts) counts as
Okay with the mod, so a party's thief skills show while it is made (see
[More characters](FEATURES.md#more-characters)).

Some effects rule out a skill:
- Blind, Afraid, Confused, Berserk and Paralyzed stop them all, except that a
  blind thief can still hear noise.
- Slowed stops picking pockets only.
- Fire Shield stops picking pockets and hiding; Mirror Image stops hiding.
- Graft Weapon stops picking pockets, opening locks and climbing.
- Feeblemind stops reading languages.
- Enlarge scales the situation's bonus or penalty, not the skill: for hiding
  it's divided by (100 + 10 × Enlarge's level)%, for climbing multiplied by it.
  With no bonus or penalty it changes nothing; with a penalty, climbing gets
  harder.

Two effects make a skill certain instead: Detect Traps (anyone, thief or not,
finds traps) and Invisible (hiding in shadows).

These effects work on the situation's bonus: ruling a skill out takes 1000 off
it, so the roll can't succeed, and making it certain adds 1000. (One more rule
in the code would make move silently certain, and hearing noise impossible, for
someone wearing one particular item on their legs, but the game passes that
check its two lists the wrong way round, so it never applies.)

## Where the game rolls thief skills

There is no hide or sneak command, and nothing in the game's code rolls a thief
skill on its own: every roll comes from the game's scripts (conversations,
doors, walls...), which ask in two ways. These are all of them:
- **13 skill checks**: find/remove traps 4 times (a hidden passage, a secret
  door, a loose rug, a cord on a lava-dome egg; bonuses −10 to +3), open locks
  4 times (a safe, a grate and cell doors; −4 to +8), climb walls 3 times, and
  pick pockets and hear noise once each (a key in a trustee's pocket; two men
  arguing by a wagon, a check for the whole party). Most are made by the
  character who acted.
- **50 trap triggers, in 16 scripts.** A script sets off an object at a spot on
  the map (a trap, or a blast: the bound prisoners in the arena, a Drajian
  messenger's thrown sphere, a summoning circle, a breaking mirror...). First
  the party's best at find/remove traps rolls, with no bonus; success, or
  Detect Traps on the character who set it off, avoids it. This is the roll the
  arena prisoner makes.

A party check is meant to go to the member with the best chance, but the
game's pick compares the wrong way round, so the first party member always
rolls (with the Loader: [the best](GAME-BUGS.md#thief-skills)). (The game also has a script command that lets
each member try in turn, but no script uses it.)

**The game never rolls move silently, hide in shadows or read languages**, so on
their own they make no difference, nor does the equipment penalty on them. The
Loader rolls them: move silently when a pocket isn't picked ([Picking
pockets](FEATURES.md#picking-pockets)), hide in shadows and move silently in
fights ([backstabs](FEATURES.md#hiding-in-shadows-to-backstab)), and read
languages when a [Shinobi](KITS.md#thief-kits) reads a scroll. The scripts also
make 3 ability checks (a d20 under the ability): CHA twice and STR once.

`python -m dsloader checks` lists them all with the script's text around
each (spoilers).

(The Loader's [Characters tab](README.md#the-characters-tab) shows each
thief's chances as they stand.)

## Resting

A rest (at a fire ring, or one a script gives) passes 8 hours and fills hit
points, PSP and spell slots (the mod's [Resting as in AD&D](FEATURES.md#resting-as-in-add)
heals by the priests' spells and a night's natural healing instead), and the
party's priests tend everyone: if the best cleric among those
Okay is 5th level or more, it casts Cure Disease, Remove Curse and Remove
Paralysis on each party member, and so does the best druid; a druid of 7th
level or more casts Neutralize Poison on each too (found by CalvinRodo's
yuan-ti). Anyone still poisoned when the rest ends dies. The game looked at who
was poisoned before those cures, so a 7th-level druid's cure saved no one; the
mod casts the cures first ([the fix](GAME-BUGS.md#resting)).

## Searching junk, hay and wardrobes

Junk piles, haystacks and wardrobes are searched by one of the game's scripts,
each with a roll of its own: 0 to N, each number as likely. A low roll finds
nothing, and junk and hay stop giving anything once the party has found 6
things in them (each kind counts its own finds); wardrobes count every search,
and after 6 every wardrobe is empty.

| Search | Roll | Finds nothing on | What the rolls find |
|---|---|---|---|
| Junk pile | 0-14 | 0-1, or after 6 finds in junk | 2 a scorpion bite, dodged; 3 a scrap of paper ("Watch out for the..."); 4 a dead rat; 5 stale bread; 6 a piece of a grainpot; 7 a rat's bite (0-4 damage); 8 magic fruit; 9 wood for a club; 10 a drawing of a four-armed statue; 11 trinkets with a gem; 12 dung; 13 arrows; 14 magic fruit |
| Haystack | 0-10 | 0-2, or after 6 finds in hay | 3 a bone needle; 4 a piece of a pot; 5 a rat's bite (0-4 damage); 6 a table leg for a club; 7 a soiled loincloth; 8 15 ceramic coins; 9 a bug; 10 a small gem |
| Wardrobe | 0-10 | 0-2 (after 6 searches, empty) | 3 a rat's bite (0-4 damage); 4 a piece of a pot; 5 "Gareth the scribe was here."; 6 magic fruit; 7 a falling pot (0-5 damage); 8 a small gem; 9 a falling pot that misses; 10 "Don't trust Pehtucl." |

The script also has outcomes for the rolls that find nothing (a scorpion's bite
in junk, a skull in hay, coins in a wardrobe...), but its "nothing" check comes
first, so they never happen.

How it works: [DEVELOPMENT-SCREENS.md](DEVELOPMENT-SCREENS.md#searching-junk-hay-and-wardrobes).

## The Bowyer's archery target

In Teaquetzl, the Bowyer keeps an archery target, and his script decides each
shot at it. The distance is the game's, in squares from the archer to the
target, and the archer's DEX does the rest:

- From under 5 squares, every shot is a bull's eye ("could hardly miss at that
  range"), with no roll and no reward.
- Otherwise the shot rolls 0 to 20 and hits on a roll under **DEX − distance ÷
  2** (rounded down; 2 if DEX is under the distance). Under it by less than 5
  is the outer ring, by less than 10 the inner ring, by 10 or more the centre.
- The centre from **more than 13 squares**, with the Bowyer **within 25** of
  the archer, has him give **6 Arrows +2**, once a game. From 13 squares or
  closer, the centre is only "the bull's eye".
- The archer must have a bow in hand, one of the three the script names: the
  plain bow, the Bow +2 or Phrain's Bow (the mod adds its Dunesong, which the
  Bowyer sells). With anything else the Bowyer only tells you off.

So a centre from 14 squares needs DEX 17 or more: at DEX 21 a roll of 4 or
less (5 in 21), at DEX 18 a 1 or less (2 in 21), at DEX 17 a 0. Each shot is in
the dice log with the distances and what it needed.

How it works: [DEVELOPMENT-SCREENS.md](DEVELOPMENT-SCREENS.md#the-bowyers-archery-target).

## The arena's count of fights

The game counts the party's trips into Draj's arena (the Loader's [combat
log](FEATURES.md#the-combat-log-in-the-game) shows the count between fights in
the slave pens and the arena). It goes up by one each time the party walks out of the arena's gate
after being called, however many waves came that day; extra waves don't count.
Being called needs the game's clock to run: Kurzak's call comes once a little
over 8 hours of game time (8 h 05 min) have passed since the last trip, and the
clock stands still while the Look pointer is chosen, so a party resting by the
fire with it chosen is never called.

The announcer greets each trip by the count:

| Count | What happens |
|---|---|
| 0-3 | A speech of its own for each of the first four trips ("Before you is a handful of gladiators...", "Behold these gladiators as they fight in melee...", "These slaves have proven their worth...", "...Let the games begin!"), then the fight. |
| 4 | Scar's challenge: "The 'King of the Pens', Scar, has become so disgusted with the survival of these scum that he has offered to kill them himself", when a check the script makes on Scar passes; otherwise the everyday speech. |
| 1000 | "This day is very special. Let's have a round of applause for the one thousandth fight of our gladiators. King Tectuktitlay himself has sent gifts for these brave souls." Two weapons appear at the party's feet, with a sound: **El's Drinker +2** (a metal sword that carries a spell) and a **Bone Gythka +3**, each worth 65,000. The script then goes on as on any other day. |
| 5000 | "You win! Through fighting in the arena, you have completely depopulated Athas of all monsters." No monsters come: the announcer sends the party back to the pens to heal, the crowd throws money, and the script marks the war against Draj won. Reaching the final battlefield afterwards plays the game's victory: 20,000 XP, the allies' farewells, Dragonsbane, the genie's prophecy, and "Congratulations! You have defeated the Drajian army and completed Shattered Lands. Feel free to continue playing the game." |
| Any other | "Once again, expectant spectators, you see trained warriors pitted against the hordes of creatures which dwell beyond our walls." |

With the Loader's new items on, the first trip after a party member kills Scar
in the arena (the count at 5 or more) brings a speech of its own and six
champions instead ([the champions' bout](FEATURES.md#the-champions-bout)).

## How fast the party walks

Everything on the map moves a step at each tick of the game's own clock, 96 a
second: the game's timer sets a flag at each tick, and the map's main loop
moves everything a step when it finds the flag set, then draws what moved and
shows it at the screen's next refresh (70 a second), waiting for it. A tick
that passes while a picture is still being drawn and shown sets the flag that
is already set, so that step is lost, for every walker at once. Everything on
the screen adds to the drawing: four figures rather than the leader alone (the
manual's advice to collapse the party "speeds up the game" is this), the mod's
gear, shadows and dust, and how fast the computer runs DOSBox. Even the
unmodded game loses a step or so for each picture it shows.

The Loader's [steady pace](FEATURES.md#game-speed) keeps the walk near the
game's own by leaving out the pictures that would lose too many steps, rather
than waiting for them; its section has the pictures a second and the walking
speeds measured with it and without.
