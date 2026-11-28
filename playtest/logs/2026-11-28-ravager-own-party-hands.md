# 2026-11-28: Wake of the Ravager's own party, the weapon hand and the Effects panel

**Under test:** branch `claude/shield-hand-fix`: `startgear.weapon_hand`, `defaultparty.rav_hands_due` / `rav_hands`
(RavDiceLog's `_party_pass`), DSCLOG2's `EF_OWN_LINES` (DSCLOG2.EXE 75,728 bytes, rebuilt before DOSBox started).

**Why (the user, 2026-11-28):** the sequel's default party and new characters "often" start with a shield in the main
hand and a weapon in the off hand; Ar'Anda's panel where kit and specialization info appears is empty.

## What was found

- **The stock game's start, the Loader's copy without the fix** (`RAV_LOADER=1 ravstart.sh`, `ravitems.py`):
  Terrannus (member 1) had his Shield +1 (type 91) in slot 3, the right hand, and his Longsword +1 (97) in slot 10,
  the left. The other three: Ar'Anda a long sword +1 right and a club left, Thy'rokh his gythka right, Gerakis
  Dragonsbane right and a long sword +1 left. So only Terrannus.
- **New characters**: the sequel's gear routine 6EF49h is an if/else chain on the class flags (fighter, druid,
  gladiator, ranger, cleric, thief, psionicist, preserver; a thri-kreen first): a multiclass gets one class's set, all
  of them fixed by `gear_hands` since 2026-11-26. No case of a shield in the right hand left; `weapon_hand` runs on the
  starting gear anyway as a safety net (both games).
- **Shattered Lands** (`start.sh`, START GAME, `carried.py`): Gerakis long sword right, gythka left; K'ratchek her
  chatkcha; Cermak quarterstaff right; Cilla long sword right. Nothing to fix.
- **The empty panel**: DSCLOG2's `EF_LINES_OF` had no counterpart of DSCLOG's `OWN_LINES` (Shattered Lands' Cilla
  shows SHADOW-WALKER): Ar'Anda has no kit and no warrior class, so nothing.

## The play (the fix in)

`RAV_LOADER=1 ravstart.sh /tmp/playtest/rav`, `ravdice.py 2900` attached in Tyr. Its first lines:

```
Dice log attached.
Terrannus's Longsword goes to the right hand, the weapon hand, and the Shield to the left
Ar'Anda is an Elven Shadow-walker who casts in light armour.
...
```

`ravitems.py 1`: the Shield +1 in slot 10, the Longsword +1 in slot 3. The talk (40,160, then 100,171 three times)
went straight to the ambush. The top-left icon (22,17) opened USE for Ar'Anda; EFFECTS (120,171): **SHADOW-WALKER,
LIGHT ARMOUR CASTING** ([the picture](img/2026-11-28-ravager-arAnda-effects-panel.png)). Computer Control for all
four on the Effects screen's lower small icons (46,53 / 98,53 / 46,110 / 98,110). Terrannus's first turn:

```
Terrannus attacks Draxan with Longsword +1 (1d8+1): d20 = 16, needs 3+ (90%), hits AC -6, target AC 7 -> HIT
Terrannus attacks Draxan with Longsword +1 (1d8+1): d20 = 11, needs 3+ (90%), hits AC -1, target AC 7 -> HIT
```

Two swings with the long sword (a Crusader's warrior attacks), where the left hand gave him one.

## Part 2: games under way (branch `claude/shield-hand-fix-2`)

The swap now runs once a load (`_hands_at` against `_party_changed_at`, after LOAD_SETTLE, out of a fight), not only
before `rav_ready` marks the party. A restart with the party already marked (kit bytes 0x40/0x43 from the first
attach, Terrannus's shield still in slot 3: the first dice log of this run was cut short) then a dice log: at 3.1 s
after the attach "Terrannus's Longsword goes to the right hand, the weapon hand, and the Shield to the left", once.

**The Effects panels** in the ambush: on the Effects screen a portrait click shows that member's panel (USE says
ONLY ACTIVE CHAR CAN CAST). Thy'rokh: GROVE WARDEN AC, MASTER OF GYTHKA; Gerakis: WILD FIGHTING, SPECIALIZED IN LONG
SWORD, GYTHKA, TRIKAL; Terrannus: KIT: CRUSADER, EXPERT IN LONG SWORD
([the pictures](img/2026-11-28-ravager-own-party-effects-panels.png)).

**What a play needs to know:** `ravdice.py ... | head -N` kills the dice log at the Nth line (SIGPIPE): a pass that
waits for LOAD_SETTLE (3 s) never runs. Send it to a file and read that.
