# Combat log and roll presentation in modern CRPGs and tactics games

Research conditions (read first): in this session only web *search* worked; every page fetch failed
because the hosts are outside the session's allowed network (forums.obsidian.net,
steamcommunity.com, forum.owlcatgames.com all returned ENOTFOUND). So the findings below rest on
search-result summaries and excerpts, not on full pages read end to end. Quotes are as given in those
excerpts; where a source is a forum post, it is one player's account, not a specification. Many of
the requested games (Wasteland 3, Tactics Ogre: Reborn, FFT, Tyranny, Expeditions, PoE2 turn-based
mode, Wrath's log filters) returned nothing usable and are listed under Gaps rather than filled from
memory.

## What is each game's line grammar and order (actor, action, target, outcome, numbers)?

### Takeaway
The pattern every well-documented game shares is a short summary line (actor, action, target, outcome
word, total) with the arithmetic kept in a second layer. Pillars of Eternity's math is
"Accuracy vs Defence, difference added to a d100 roll, band gives Miss/Graze/Hit/Crit". Owlcat's
Pathfinder log keeps one event per line and puts every bonus and its source in the tooltip. BG3 keeps
named sub-lines ("Resulting Attack Roll", "Resulting Defence", "Resulting Damage"), each with its own
hover breakdown.

### Cited Findings
- **Pathfinder: Kingmaker (Owlcat).** The developers' Kickstarter update #37 ("The Combat Log - It's
  how we roll!") says each log event has its own line, and the tooltip on a to-hit line shows "all of
  the bonuses and penalties for the to-hit roll and their sources" along with the roll itself, e.g.
  when "attacking a wolf" — [Kickstarter update #37](https://www.kickstarter.com/projects/owlcatgames/pathfinder-kingmaker/posts/1946988); mirrored at [Owlcat forum](https://forum.owlcatgames.com/t/update-37-the-combat-log-its-how-we-roll/12771) and discussed at [RPGWatch](https://rpgwatch.com/forum/threads/kingmaker-the-combat-log.37088/)
- **Kingmaker, unknown enemy AC.** The same update: the creature's AC in the tooltips "will be shown
  as ?19-34 – meaning, that your highest miss was against AC 18 and 19 could be hit, while your lowest
  hit was 34." (The log learns a bounded range of a hidden number from past rolls.) — [Kickstarter update #37](https://www.kickstarter.com/projects/owlcatgames/pathfinder-kingmaker/posts/1946988)
- **Pillars of Eternity II: Deadfire.** A Steam guide walks through a real log entry: "Accuracy of 86
  and the Deflection of the target is 66, which makes a bonus to the dice roll of 20 (=86 - 66)" and
  "25 + 20 = 45 which results in a Graze" — [Steam guide: Combat Basics](https://steamcommunity.com/sharedfiles/filedetails/?id=1393307492)
- **Pillars of Eternity (forum shorthand of the same math).** A player writes a log-style line as:
  "Accuracy 50, Deflection 60: -10. Hit Roll 70, -10: 60 *blabla Rogue Talent* -> Crit." —
  [Obsidian forum: Convert Graze > Hit > Crit?](https://forums.obsidian.net/topic/78020-convert-graze-hit-crit/)
- **Pillars outcome bands differ between games and sources.** The official wiki: PoE1 checks crit,
  then miss, then graze, else hit; Deadfire checks crit, then hit, then graze, else miss. A Steam guide
  gives Deadfire as "25 - 50 Graze, 50 - 99 Hit, 100 and beyond Crit"; Fextralife gives
  "≤30 Miss, 31-50 Graze, 51-100 Hit, >100 Crit" — [Attack Resolution wiki](https://pillarsofeternity.fandom.com/wiki/Attack_Resolution); [Steam guide](https://steamcommunity.com/sharedfiles/filedetails/?id=1393307492); contradicted by [Fextralife PoE2 Combat](https://pillarsofeternity2.wiki.fextralife.com/Combat)
- **Baldur's Gate 3.** Players describe the log entry as having named sub-parts you can hover:
  "Melee attack", "Resulting Attack Roll", "Resulting Defence", "Resulting Damage", each showing "the
  math behind this" — [Steam BG3 discussion](https://steamcommunity.com/app/1086940/discussions/0/4032473436330492524)
- **BG3 advantage.** A 2023 forum reply: with advantage two dice are rolled but "the combat log only
  displays the higher result"; the second die is shown on screen during the roll but not logged —
  [Steam BG3 discussion](https://steamcommunity.com/app/1086940/discussions/0/3802776599346312809) (search summary)
- **Disco Elysium (skill checks inside dialogue, not combat).** The check is a bracketed tag placed
  after the speaker's name and before the line, of the form `SKILL [Difficulty: Success/Failure]`
  (e.g. "[Easy: Success]"); a third-party engine author reproducing it asks how to make "the
  difficulty/success notice come after the 'speaker' name" as in the game — [Narrat forum](https://narrat.discourse.group/t/making-skillchecks-more-disco-like/313). The difficulty words map to numbers: Trivial 6-7, Easy 8-9 (and so on up) — [Disco Elysium wiki: Skills](https://breezewiki.discard.no/discoelysium/wiki/Skills). The developers' own post on active checks: [ZA/UM devblog 2016](https://discoelysium.com/devblog/2016/10/06/active-skill-checks)
- **Disco Elysium passive checks.** A player notes only *successful* passive checks appear in the
  dialogue, never failed ones or their dice — [Steam DE discussion](https://steamcommunity.com/app/632470/discussions/0/1755780148311380301) (search summary)

### Inferences
- The common grammar (inference from the above): `Actor` `action` `Target` : `outcome word`
  (`total` vs `defence`) → `damage`. The outcome word comes before the arithmetic in every example;
  the arithmetic, when inline at all, is a compact chain ("86 - 66 = 20; 25 + 20 = 45 → Graze").
- The forum shorthand "Accuracy 50, Deflection 60: -10. Hit Roll 70, -10: 60 -> Crit" is itself a
  workable plain-text format: one line, each step labelled, an arrow to the outcome. That a player
  wrote it unprompted suggests it reads naturally.
- Disco Elysium's `[Easy: Success]` tag shows the minimum disclosure that still feels honest: a named
  difficulty band and the outcome, with numbers only on hover. It works without interactivity.
- Kingmaker's `?19-34` is a plain-text technique worth copying: it shows what the player has
  *learned* about a hidden defence without revealing it.

### Gaps
- No verbatim BG3 log line (exact wording and order of the summary line) was retrieved; the bg3.wiki
  and Larian pages could not be fetched.
- No verbatim Wrath of the Righteous or Rogue Trader line was found.
- Solasta, DOS2, Wasteland 3, Tactics Ogre: Reborn, FFT, Tyranny, Expeditions: no quoted line
  formats were found in search results.

## How does progressive disclosure work (Owlcat's nested tooltips, Pillars' expandable entries, BG3's hover)? What do players say works or overwhelms?

### Takeaway
All the big games use a two-layer model: a terse line, and the full breakdown on hover. Owlcat adds
rule-driven extra blocks (crit confirmation, concealment) inside the same tooltip. Pillars puts it on
hover, with a Shift-hover extended tooltip in Deadfire. BG3 has hover per sub-line. Solasta has hover on any
roll plus a running log. The complaints are about the hover layer itself: tooltips that fail to appear,
cover other lines, need precise mouse work, or disagree with the real math. The usual proposal is a
clickable "audit trail" of how the roll was made.

### Cited Findings
- **Owlcat conditional blocks.** "Additional information will also appear in the tooltip if
  circumstances call for it. For example, on a critical threat roll, a confirmation roll will appear
  with same detailed information, or if a target has concealment there will be a mention of the miss
  chance." — [Kickstarter update #37](https://www.kickstarter.com/projects/owlcatgames/pathfinder-kingmaker/posts/1946988)
- **Pillars.** "You can also hover over attacks in the combat log to look over the modifiers." —
  [Quarter To Three forum](https://forum.quartertothree.com/t/the-spoiler-free-pillars-of-eternity-thread-about-managing-combat/76675)
- **Deadfire extended tooltip.** A forum post refers to an "extended tooltip in the combat log
  (shift+mouse over)" — [Obsidian forum: item bestowed effects in the combat log](https://forums.obsidian.net/topic/120212-item-bestowed-effects-and-how-they-show-up-in-the-combat-log) (search summary; page not read)
- **Pillars tooltip complaints and the hyperlink proposal.** Players argued tooltips cover other rows of
  the log and need extra mouse movement; one proposal was to make the roll breakdown a hyperlink that
  opens a table "showing how the roll was calculated, including all modifiers" — [Obsidian forum:
  Feature request: combat log audit trail](https://forums.obsidian.net/topic/93529-feature-request-combat-log-audit-trail) (search summary; page not read)
- **Deadfire tooltip positioning bug.** Combat log tooltips were misplaced: "As of patch 3.0 this has
  not been solved" — [Obsidian forum: UI combat log tooltips positioning bug](https://forums.obsidian.net/topic/105457-ui-combat-log-tooltips-positioning-bug/)
- **PoE1 had less than players wanted.** The "Extra Combat Details" mod "Added detailed breakdown of the
  accuracy, defense, damage, damage resistance and damage resistance bypass to the tooltip shown when
  hovering over combat log message." — [Nexus: Extra Combat Details (PoE1)](https://www.nexusmods.com/pillarsofeternity/mods/188). Related backer-era threads: [What does the combat log lack?](https://forums.obsidian.net/topic/69603-what-does-the-combat-log-lack), [Needed quality-of-life improvements: information and transparency](https://forums.obsidian.net/topic/78749-needed-qualyty-of-life-improvements-information-and-transparency), [Please give us in-game access to exhaustive combat mechanics info](https://forums.obsidian.net/topic/95636-please-obsidz-give-us-in-game-access-to-exhaustive-combat-mechanics-info)
- **Too much in the tooltip, too.** The Deadfire mod "Out With The Good" hides some defensive buffs
  from the combat tooltip: "This does not disable any buffs. It merely hides them from the combat
  tooltip." — [Nexus: Out With The Good](https://www.nexusmods.com/pillarsofeternity2/mods/370)
- **Wanting the hidden layer as text.** Deadfire's "Combat Log Exporter" writes the log to a file and
  can be configured for "whether tooltip information should be saved, whether auto-pause messages
  should be included", and keywords that exclude a line — [Nexus: Combat Log Exporter](https://www.nexusmods.com/pillarsofeternity2/mods/103?tab=docs). For BG3 a modder proposed an exportable, expanded log parser — [Nexus forums proposal](https://forums.nexusmods.com/topic/13513094-mod-proposal-exportable-combat-log-parser-for-bg3)
- **BG3 hover is unreliable.** "Sometimes when you mouse over it, it just doesn't display the roll
  window"; players ask for a way to show dice rolls and calculations, and note there is no dice-roll
  log as such — [Steam BG3 discussion](https://steamcommunity.com/app/1086940/discussions/0/4032473436330492524); [Steam BG3 discussion 2](https://steamcommunity.com/app/1086940/discussions/0/4204741588972273646) (search summaries)
- **BG3 tooltips that lied.** PC Gamer reported spell tooltips were "bugged—and may have even been
  this way for months", though the chance-to-hit figure was right — [PC Gamer](https://www.pcgamer.com/games/baldurs-gate/baldur-s-gate-3-s-spell-tooltips-have-been-lying-to-you-for-potentially-months-though-if-you-ve-been-running-off-the-chance-to-hit-you-re-just-fine); also [GamesRadar](https://gamesradar.com/games/baldur-s-gate/a-shrewd-baldurs-gate-3-fan-has-discovered-that-the-rpgs-dandd-spellcasting-system-might-have-been-bugged-for-months-which-could-explain-why-shadowheart-never-lands-sacred-flame)
- **BG3 dialogue roll UI.** Patch 5 revised the active roll UI in dialogue, with "improved displaying of
  bonuses and double dice for rolling with Advantage or Disadvantage" — [Larian: Patch 5](https://baldursgate3.game/news/patch-5-now-live_99); [Fextralife patch notes](https://baldursgate3.wiki.fextralife.com/Patch_Notes)
- **Solasta.** The Winter Update let players "hover any attack, damage, saving throw, ability check
  roll to see the details of the dice roll" — [Solasta Winter Update patch notes](https://www.solasta-game.com/solasta-crown-of-the-magister/news/110-solasta-winter-update-patch-notes). Reviewers praised seeing "the computations behind each roll" as a way to learn the rules — [Fextralife review](https://fextralife.com/solasta-crown-of-the-magister-review-impressions-a-faithful-dd-5e-adaptation/); [PCGamesN review](https://www.pcgamesn.com/solasta-crown-of-the-magister/review)
- **Rogue Trader.** Owlcat's survey summary said formulas in ability descriptions and combat logs were
  confusing and damage numbers were often "way off" the expected values; the beta known-issues page
  listed log errors (immunity shown as "damage reduced", true damage shown as "-1"); patch 1.2 listed
  combat log and tooltip improvements; a later review said "vital tooltips sometimes won't appear" —
  [Rogue Trader beta known issues](https://roguetrader.owlcat.games/beta_known_issues); [Steam RT discussion](https://steamcommunity.com/app/2186680/discussions/0/4027970229989565618); [RPGHQ thread](https://rpghq.org/forums/viewtopic.php?p=30369) (search summaries)

### Inferences
- What players praise is that the full math is *reachable* (Solasta reviews, the Owlcat design). What
  they criticise is the delivery: hover that fails, covers the log, or doesn't match the result. A
  plain text log that prints the math has none of those failure modes, but it also has no second
  layer, so the summary line has to stay short.
- The Pillars mods (exporter with tooltip text, "Out With The Good") show both demands at once: some
  players want *more* math in text form, others want *less* in the breakdown. That points to a
  verbosity switch rather than one fixed level.
- Owlcat's "extra block only when it matters" (crit confirmation, concealment) is a rule a text log
  can follow too: add an indented second line only when a special step happened.

### Gaps
- Owlcat's nested tooltips in Wrath (tooltip-inside-tooltip for terms) and player reaction to them:
  no source retrieved.
- Whether Pillars has an in-game verbosity setting for the log: not confirmed by any retrieved source.
  One search summary said none was found.

## How are colour and icons used (outcome colours, damage-type colours, actor colours), and are there colour-blind options?

### Takeaway
Little was retrievable. The only sourced colour-blind item is BG3 Patch 4's colour-blind feature. The
only grouping change found is BG3's round headings, also in Patch 4.

### Cited Findings
- BG3 Patch 4 added a colour-blind feature — [Dexerto: Patch 4 notes](https://dexerto.com/baldurs-gate/baldurs-gate-3-patch-4-notes-color-blind-feature-hireling-alterations-more-2364112)
- A search for BG3 colour-coded dice in the log found "no evidence of a colour-coded dice display in
  the combat log" — (negative search result; no source)
- Solasta lets players choose whether dice rolls are shown in dialogue, combat and exploration, and
  customise the dice's look in Dice Settings — [Solasta Winter Update patch notes](https://www.solasta-game.com/solasta-crown-of-the-magister/news/110-solasta-winter-update-patch-notes); [Fextralife Solasta New Player Help](https://solastacrownofthemagister.wiki.fextralife.com/New_Player_Help) (search summary)

### Inferences
- None that can be sourced. From general knowledge (unverified in this session, so treat as a lead
  only): Pillars and BG3 colour character names in the log and colour damage numbers by damage type;
  Owlcat colours the outcome words. These need checking against screenshots (e.g. gameuidatabase.com)
  before use.

### Gaps
- Outcome/damage-type colour schemes in any of the games: not retrieved.
- Colour-blind options specific to the combat log in any game: not retrieved.
- Typography and font size of logs: only the Wrath font-size reports below.

## What filters/verbosity levels exist, and what do players actually use?

### Takeaway
Retrieved sources show filters mainly as *mods* (Deadfire's exporter with keyword exclusion, the
tooltip-trimming mod) and as *requests* (filter toggles for BG3, a shorter feed-style Pillars log).
Solasta's per-context dice visibility is the one sourced first-party option. BG3's Patch 4 round
headings are the sourced example of grouping by turn.

### Cited Findings
- BG3 Patch 4: "the Combat Log now splits combat rounds into separate headings", making it easier to
  see when events happened — [Shacknews: Patch 4](https://shacknews.com/article/137645/baldurs-gate-3-patch-4?amphtml=1) (secondary coverage, not Larian's notes)
- Pillars players asked for a shorter, feed-style log; one said the log should show less, "especially
  regen"; another suggested shortening the strings to save horizontal space — Obsidian forum threads
  under the [Combat Log tag](https://forums.obsidian.net/tags/Combat%20Log/) and [What does the combat log lack?](https://forums.obsidian.net/topic/69603-what-does-the-combat-log-lack) (search summary; exact thread not confirmed)
- Deadfire Combat Log Exporter: keyword exclusions and an option to drop auto-pause messages —
  [Nexus](https://www.nexusmods.com/pillarsofeternity2/mods/103?tab=docs)
- BG3 log is short and lacks some modifier details; filter toggles requested — [Nexus forums proposal](https://forums.nexusmods.com/topic/13513094-mod-proposal-exportable-combat-log-parser-for-bg3)
- Solasta: per-context dice visibility (dialogue / combat / exploration) — [Solasta Winter Update](https://www.solasta-game.com/solasta-crown-of-the-magister/news/110-solasta-winter-update-patch-notes)
- XCOM 2 (no roll log): the displayed chance hides an aim assist that "isn't shown in the vanilla hit
  chance window" — [Steam Workshop discussion](https://steamcommunity.com/workshop/filedetails/discussion/625737801/412448158157445443); players' "missed a 95%" complaints, and a reply that players
  "remember the high % chances they miss easier but ignore all the ones they do hit" — [Steam XCOM discussion](https://steamcommunity.com/app/268500/discussions/0/412446292767037621); a mod aims to make the rolls "FEEL" more fair — [Nexus XCOM 2 mod](https://www.nexusmods.com/xcom2/mods/482?tab=docs)
- DOS2 (percentages, weak log): players call the displayed hit chance unreliable; others say it's
  accurate over enough attacks — [Steam DOS2: Hit Chance Bugged?](https://steamcommunity.com/app/435150/discussions/0/142261352654509760/); [chance to hit grossly exaggerated](https://steamcommunity.com/app/435150/discussions/0/1499000547493456330/)

### Inferences
- XCOM 2 and DOS2 show the cost of a percentage with no roll log: players can't check a surprising
  miss, so they suspect the dice. A visible log of the actual roll against the needed number answers
  that suspicion.
- Round headings (BG3 Patch 4) are a plain-text technique: a separator line per round costs nothing
  and was added in response to "when did this happen" confusion.
- What players *actually use* is not measured anywhere retrieved. The demand for exporters and
  trimmers suggests two groups: those who want everything, and those who want the noise (regen, buffs)
  gone.

### Gaps
- No usage data on which filter or verbosity level players choose, in any game.
- Wrath and Rogue Trader log tabs/filters, Pillars' native filter options, PoE2 turn-based mode's log:
  not retrieved.

## What common complaints exist (log too fast, too verbose, unreadable font size, math hidden, log desynced from animation)?

### Takeaway
The sourced complaints: rolls shown too briefly to read (Solasta), the roll far from the log and the
actor (Solasta), damage dice missing from the log (Solasta), hover that fails or covers the log (BG3,
Pillars), the log disagreeing with the real math (BG3 tooltips, Rogue Trader, DOS2), too much noise
(Pillars regen and buffs), the font size control not working (Wrath), and a log that doesn't
auto-scroll (DOS2).

### Cited Findings
- Solasta: the roll display is "gone so fast" and can't be paused — [Steam: can we pause on the dice result?](https://steamcommunity.com/app/1096530/discussions/0/4477100383818746284/)
- Solasta: the roll sits too far from the log and the character, a "scissor effect" of where to look —
  [Solasta forum: Die roll closer to log or character](https://forums.solasta-game.com/forum/gui-die-roll-closer-to-log-or-character)
- Solasta: players asked for the damage dice in the log, not just the total — [Steam Solasta discussion](https://steamcommunity.com/app/1096530/discussions/0/3784750917889482533) (search summary)
- Solasta: rolls sometimes don't appear on screen, but "a running log in the top right corner keeps
  track of all that as a backup" — [Gertlush Gaming review](https://gertlushgaming.co.uk/solasta-crown-of-the-magister-review-steam-updated/) (search summary)
- Wrath of the Righteous: the font size option "doesn't work for me"; a workaround of re-applying it
  each launch; the MoreFontSizes mod widens 0.8-1.2 to 0.1-5 but warns "not all text in the games is
  adjusted by this slider" — [Steam Wrath discussion](https://steamcommunity.com/app/1184370/discussions/0/4132682093267216698); [GitHub MoreFontSizes](https://github.com/cookEsandcream/MoreFontSizes). A ResetEra player found the log text too *large* — [ResetEra Wrath OT](https://www.resetera.com/threads/pathfinder-wrath-of-the-righteous-ot-crusader-kings-3-5.479329/page-17)
- DOS2: the log doesn't auto-scroll, its window position resets, it omits some events; one user calls
  it "broken and unusable"; another saw damage that didn't match their own sum — [Steam DOS2: Combat Log inconsistent?](https://steamcommunity.com/app/435150/discussions/6/1737715419897228300/); [Steam DOS2: Toggle log question](https://steamcommunity.com/app/435150/discussions/0/1678064284155441838/); critique of DOS2's UI generally at [Silver Rants](https://silverrants.wordpress.com/2017/10/10/the-flaws-of-divinity-original-sin-ii/)
- BG3: the log dropped the second advantage die; Patch 5 fixed Advantage/Disadvantage info not showing
  when targeting a body part of a larger creature — [Fextralife Patch 5 fixes](https://baldursgate3.wiki.fextralife.com/Patch_5_Fixes)
- BG3: a mod exists just to keep the log readable after a party wipe — [Nexus: Post-Mortem Combat Log](https://www.nexusmods.com/baldursgate3/mods/25355)

### Inferences
- "Too fast" is a complaint about transient roll displays, not about a scrolling log; the log is the
  fix players point to (Solasta's "backup"). A persistent text log should therefore carry everything
  the animation shows, including each die of an advantage pair and the damage dice.
- "Where to look" (Solasta) argues for keeping the roll text next to, or inside, the log rather than in
  a separate popup.
- Desync between log and animation: no source retrieved (see Gaps).

### Gaps
- Log desynced from animation: no source found for any game.
- Wasteland 3, Tactics Ogre: Reborn / FFT, Tyranny, Expeditions, Pathfinder turn-based modes, PoE2
  turn-based mode: searches returned nothing on their logs. Not filled from memory.
- Developer talks (Obsidian UI posts, Larian UI talks, GDC) on log design: none retrieved.
- To complete this file, a session with forums.obsidian.net, steamcommunity.com,
  forum.owlcatgames.com, bg3.wiki and gameuidatabase.com allowed could fetch the threads cited above
  and screenshots for verbatim lines and colours.
