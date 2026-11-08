# Combat logs in classic dice-driven CRPGs (Gold Box, Infinity Engine, NWN 1/2, ToEE, KOTOR, Dark Sun)

**Method note (read first).** This session's network allowed web *search* but blocked page *fetches* for almost every relevant host: forums.beamdog.com, gog.com, steamcommunity.com, rpgcodex.net, *.fandom.com, beforeiplay.com, crpgaddict.blogspot.com and wish-goldbox.readthedocs.io all failed with "host not allowed". Only github.com could be fetched. So every finding below comes from search-engine snippets and summaries of the cited pages, not from reading the pages in full. Quotes are as the search tool returned them. Treat the exact wording as likely but not checked against the page. A follow-up pass with those hosts allowed should check the quotes and fill the gaps (especially the Gold Box message strings and the exact NWN line).

## 1. Line grammar: narrative vs math-first (quoted examples)

### Takeaway
Two families. The Gold Box (and, as far as anything is documented, SSI's Dark Sun) uses short narrative lines in one message area that overwrite each other, with no dice shown. The Infinity Engine, NWN and KOTOR use a math-first "Name - Attack Roll N +/- M = T : Hit/Miss" grammar in a scrolling log. They show the attacker's roll and total but not the target number (AC or THAC0) being compared against.

### Cited Findings
**Baldur's Gate / Icewind Dale (Infinity Engine, incl. EE)**
- Icewind Dale: Enhanced Edition line as quoted on the Beamdog forums: `Paladin - Attack Roll 16 - 1 = 15 : Hit the Fighter - Damage Taken (7)`. Grammar: actor, " - Attack Roll ", d20, signed modifier, "=", total, " : Hit/Miss", target, then damage in parentheses. — [Beamdog forum, "What does To-Hit roll calculate?"](https://forums.beamdog.com/discussion/comment/1183580)
- BG player's paraphrase of their log against a random enemy: "MC : atack roll 10 - 2 = 8 miss; 19 - 2 = 17 hit !" (player's typing, not the exact log text). The explanation given: "You rolled a 10 and then the game either adds or subtracts bonuses based on your stats and proficiencies". — [Beamdog forum results via search](https://forums.beamdog.com/discussion/68773/combat-log-information)
- The hit/miss label reflects a comparison with the target's AC/THAC0 that the log itself does not show (search summary of the BG threads). The BG fandom THAC0 talk page explains the attack report includes the attacker's THAC0 modifiers and that the defender's effective AC has its own modifiers. — [Baldur's Gate wiki, Talk:THAC0](https://baldursgate.fandom.com/wiki/Talk:THAC0); [Beamdog "Combat log information"](https://forums.beamdog.com/discussion/68773/combat-log-information)
- A complaint thread from the classic era: "Baldur's Gate 2 window log is not very detailed". — [Sorcerer's Place](https://sorcerers.net/community/threads/baldurs-gate-2-window-log-is-not-very-detailed.86150)

**Neverwinter Nights 1**
- A forum thread lists attack entries as `9+4=13 *Hit*` / `7+4=11 *Hit*` / `2+4=6 *Miss*`: d20 + attack bonus = total, with the result in asterisks. The search did not say which result held this quote. The likeliest source is the GameFAQs thread "How do I use multiple attacks?" — [GameFAQs NWN board](https://gamefaqs.gamespot.com/boards/188666-neverwinter-nights/44912633) (unconfirmed attribution)
- I could not confirm the full line with the actor prefix (the brief's `Attack Roll: 15 + 7 = 22 : *hit*` form) from a fetched source. **Inferred from memory, unverified:** NWN prints `Attacker attacks Target : *hit* : (15 + 7 = 22)`, then a separate `Attacker damages Target: 9 (9 Physical)` line. The bracketed roll is coloured.
- Scripted touch attacks (spells) also produce hit/miss feedback. The NWN wiki notes "the consequences for a miss, hit, and critical hit are completely determined by the script that invoked the touch attack". — [NWN wiki, Touch attack](https://nwn.fandom.com/wiki/Touch_attack)
- Players report spells "*miss* 70%+ of the time", which shows the `*miss*` token is what players see and quote. — [NWN PRC forum](https://nwnprc.com/index.php?topic=2364.0)

**Neverwinter Nights 2**
- I found no verbatim NWN2 line. A Nexus forum reply says "while fighting, there's also some details about the saves, etc...", and the thread calls the lack of info in the log "a common complaint". — [Nexus forums, "More detailed in game log?"](https://forums.nexusmods.com/topic/7544406-more-detailed-in-game-log/)
- An Obsidian bug report: with the game language set to Italian, "the lines with successful attack and damage are not shown ... They are replaced with empty lines". This shows hit and damage come from localised string templates. — [Obsidian forums, Combat Log tag](https://forums.obsidian.net/tags/Combat%20Log/)

**KOTOR 1/2 (Odyssey engine, NWN-derived)**
- The KOTOR II Messages/Feedback log gives a full Defense breakdown, quoted on Obsidian's forums as "base 10 + armor 7 + dex mod 1 + class 6 + feats and affects mod 3" ("base 10 is always given"). — [Obsidian forums, "kotor2/tsl combat mechanics questions"](https://forums.obsidian.net/topic/33665-kotor2tsl-combat-mechanics-questions)
- StrategyWiki: "the Attack Breakdown in the Messages Log displays Attack Modifier" accumulating with each attack in a round. Per Feedback, natural 1 always misses and natural 20 always hits (a critical threat). — [StrategyWiki KOTOR II Forms](https://strategywiki.org/wiki/Special:MobileDiff/907029); [StrategyWiki KOTOR Combat](https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Combat)
- Modders ask whether the combat-log messages can be edited beyond dialog.tlk, which suggests the strings live in the talk table. — [Deadly Stream](https://deadlystream.com/topic/12053-editing-combat-log-messages-is-anything-beyond-dialogtlk-editable/)

**Gold Box (Pool of Radiance etc.)**
- Combat screen layout: the battlefield view is on the left, "the right section displays all character and monster information", and the command list stays at the bottom. — [Retro Freak Reviews, Pool of Radiance DOS](https://retrofreakreviews.com/2025/03/17/pool-of-radiance-dos-review/)
- A reverse-engineering tool (the "wish" Gold Box project) documents the combat message window as **text columns 23-38, rows 1-22, with the top moved to row 10 for messages**. That is about 16 characters per line on a 40-column 320x200 screen. — [wish-goldbox docs, automap.combatlog](https://wish-goldbox.readthedocs.io/en/latest/api/generated/automap.combatlog.html) (search snippet only)
- I could not confirm the exact message strings (e.g. "HITS", "MISSES", "IS DYING") from any source. **Unverified, from memory:** lines were upper-case and terse, e.g. `NAME HITS ORC` / `FOR 5 POINTS OF DAMAGE`, with no dice shown.

### Inferences
- The IE/NWN/KOTOR family all print the **attacker's side** of the sum (d20 + modifier = total) and only a verdict for the defender's side. Not printing the target number (AC/THAC0) is the main thing players find hard to work out. The BG threads above show players reverse-engineering it.
- The Gold Box's 16-character column forces narrative two-liners with no maths.

### Gaps
- No fetched, verbatim NWN1 or NWN2 line with its actor prefix. No Gold Box string list. No BG2 "ExtraCombatInfo" output sample. All need the blocked hosts or an install.

## 2. How the roll breakdown is disclosed

### Takeaway
There is a spread of approaches. Gold Box: none. BG/IWD: inline but optional ("To Hit Rolls" feedback toggle), and original BG2 had an ini flag for the full THAC0/damage formula that EE dropped. NWN: always inline as a short sum, with more detail through a debug option. KOTOR: inline breakdown in the Messages log. ToEE: a separate "Rolls History" window where blue hypertext entries expand into the full modifier list. ToEE's on-click model is the most praised.

### Cited Findings
- **BG:EE toggle:** Options > Gameplay > Feedback > "To hit rolls". A user says enabling it also adds "additional info like stat changes". — [Beamdog thread 34487](https://forums.beamdog.com/discussion/34487/not-an-issue-no-to-hit-roll-information-even-when-enabled-in-gameplay-gt-feedback)
- Even with it on, some players saw "only an abbreviated version of attack rolls where some of them are missing" and "it still only shows me some of the hit rolls". One user's untested theory: rolls show only when the attacker's portrait has a weapon icon. Others say all rolls show. The thread was closed as [Not an Issue]. — [Beamdog thread 34487](https://forums.beamdog.com/discussion/34487/not-an-issue-no-to-hit-roll-information-even-when-enabled-in-gameplay-gt-feedback)
- **Original BG2 ini flag:** baldur.ini "ExtraCombatInfo" "would show you the THAC0 and Damage calculations (every single adjustment)". It does not work in BG:EE. A developer-side comment says "there are two pieces of code that are commented out for displaying that string/respecting that INI setting". — [Beamdog "Editing baldur.ini - Extra Combat Info"](https://forums.beamdog.com/discussion/7518/editing-baldur-ini-extra-combat-info); [Beamdog "Option to show damage calculations"](https://forums.beamdog.com/discussion/14041/option-to-show-damage-calculations)
- **NWN2 debug detail:** the console command `enablecombatdebugging 1` "causes a much more detailed combat log to appear in the feedback window". — [Lilura NWN2 mods guide](https://lilura1.blogspot.com/p/neverwinter-nights-2-mods.html?m=1) (via search summary)
- **NWN logging to file:** set `ClientEntireChatWindowLogging=1` in nwnplayer.ini to write the whole chat/combat window to a log file. — [Beamdog forum comment](https://forums.beamdog.com/discussion/comment/920290/). The NWN2 equivalent "also captures combat and system messages" (fetched page). — [RoleWeaver NWN2_LOGGING.md](https://github.com/RoleWeaver/roleweaver/blob/main/NWN2_LOGGING.md)
- **ToEE on-click history:** producer Tom Decker credits Sean Craig with adding "the die roll history system so players could monitor their every die roll", with hypertext clicks for a full explanation. The RPG Codex retrospective says "the help files and roll history weren't included in the original milestone schedule". — [RPG Codex ToEE retrospective](https://rpgcodex.net/article.php?id=9553)
- GOG player: "You can click on the blue messages in that window and then see a breakdown of the dieroll + modifiers". — [GOG ToEE forum, zombie/slime fight](https://gog.com/forum/temple_of_elemental_evil/need_advice_for_zombieslime_fight)
- Before I Play: the "Rolls History" window can be opened, and most of its numbers are hyperlinks that give "a step-by-step breakdown of the underlying rules and statistics". It recommends using it when attacks keep missing or doing little damage. — [Before I Play, ToEE](https://beforeiplay.com/index.php?title=The_Temple_of_Elemental_Evil)
- Octopus Overlords forum: the dice window shows every situational modifier, each linked to an explanation (e.g. why an attack got a flanking bonus). Critical threats show their confirmation roll. — [Octopus Overlords, ToEE restart](https://www.octopusoverlords.com/forum/viewtopic.php?t=14614)
- **Pillars (contrast, Obsidian):** a forum request asked for "detailed information about To Hit rolls inside the Combat Log, not just as a tooltip". Hover-only disclosure was criticised. — [Obsidian forums "what does the combat log lack"](https://forums.obsidian.net/topic/69603-what-does-the-combat-log-lack)

### Inferences
- The model players endorse is layered: a short verdict line always, and the full modifier list one click away (ToEE). An option that silently drops lines (BG:EE) erodes trust more than showing nothing.

### Gaps
- ToEE line wording (e.g. "X hits Y" in the floating text vs the history entry) was not quoted verbatim in any snippet.
- Whether Temple+ changes the history window: nothing found.

## 3. Player complaints, requests and mods

### Takeaway
The recurring complaints are missing information (the target number, absent rolls, damage formula), clutter from non-combat spam with no filters, too small or too large text, and messages vanishing too fast (Gold Box). The mods respond by enlarging the log, restoring detail, and exporting it to files for parsers.

### Cited Findings
- BG:EE 1.3 patch: "The combat log window has been widened and the text size has been increased for better readability". Some players then asked for a setting to restore the old size, or to set window and font size separately. — [Beamdog comment](https://forums.beamdog.com/discussion/comment/471542)
- "Jimfix is a great little mod that (among other things) improves significantly the combat log. Unfortunately, Jim has been offline for almost a year and his mod is no longer supported." — [Beamdog comment](https://forums.beamdog.com/discussion/comment/471785)
- Dragonspear UI++: "Combat statistics boxes area larger". I found no evidence it resizes the combat log itself. — [Beamdog forums](https://forums.beamdog.com/discussion/comment/878541)
- NWN:EE Steam thread "Game needs a better UI desperately": players want "filters or some way to seperate it", meaning combat, chat and system text share one stream. — [Steam NWN:EE discussion](https://steamcommunity.com/app/704450/discussions/0/3288067088108433442/)
- NWN2: lack of info in the log is "a common complaint". — [Nexus forums](https://forums.nexusmods.com/topic/7544406-more-detailed-in-game-log/). The NWN2 UI mods (Tchos HD UI, BlackUI) restyle the windows. — [Nexus NWN2 mod 1120](https://www.nexusmods.com/neverwinter2/mods/1120?tab=posts)
- External parsers exist: "NCLA - Neverwinter Combat Log Analyzer" reads the file log. — [SourceForge NCLA](https://sourceforge.net/projects/ncla/)
- KOTOR/Obsidian: a player asked for less regeneration noise, a smaller font and better colour coding. — [Obsidian forums, Combat Log tag](https://forums.obsidian.net/tags/Combat%20Log/)
- IWD2: a GOG thread titled "iwd2 attack roll modifier wrong" shows players auditing the printed modifier against the rules. — [GOG IWD forum](https://static.gog.com/forum/icewind_dale_series/iwd2_attack_roll_modifier_wrong)
- ToEE praise: the roll history is praised, while the help files were "not comprehensive" (RPG Codex retrospective, via search summary). — [RPG Codex](https://rpgcodex.net/article.php?id=9553)

### Inferences
- Showing the maths turns the log into an audit tool: players use it to check rules bugs (IWD2 modifier thread, NWN spells "missing" 70%). For a remaster, that argues for printing the target number as well as the roll.

### Gaps
- Specific Reddit threads were not reached (search returned none). LeUI's log features are unconfirmed.

## 4. Readability at small resolutions (Gold Box at 320x200, pacing)

### Takeaway
The Gold Box games had a narrow message column, about 16 characters wide (columns 23-38), shared with the character panel. They managed pacing with a player-set message delay (Speed: Faster/Slower) instead of scrollback: messages overwrite each other in one place. Reviewers and DOSBox players complain that messages flash past.

### Cited Findings
- Reference card: in combat, choose Done > Speed, then F to speed up or S to slow down. The card says the setting controls "the amount of time messages remain on the screen". — [SSI Pool of Radiance reference card (MOCAGH)](https://mocagh.org/ssi/pool-refcard.pdf)
- Manual: "If you are having trouble reading messages before they disappear, use the Slower command." — [Gold Box wiki, Pool of Radiance/Manual](https://goldbox.fandom.com/wiki/Pool_of_Radiance/Manual)
- Conflicting account: an Aminet doc file says the speed setting changes the wait between each word typed, not how long the message stays, and calls it a kludge (Amiga version). — [Aminet PoolOfRadiance.txt](https://sunsite2.icm.edu.pl/packages/aminet/docs/rview/PoolOfRadiance.txt)
- Reviewer complaint: output messages "all appear in the same space and always overwrite each other" (so there is no scrollback). — [math.uh.edu Pool of Radiance review text](https://www.math.uh.edu/~barrett/data/software/games/PoolOfRadiance)
- The wish tool documents a delay between a message and the clear that follows it, "in units of about a third of a second". — [wish-goldbox docs](https://wish-goldbox.readthedocs.io/en/latest/api/generated/automap.combatlog.html) (snippet)
- DOSBox: "the DOSBox cycle speed is way too high to see combat messages on the screen". A player suggests text "(usually) scrolls at an alright pace at 1000 cycles". — [Gold Box Games forums](https://forums.goldbox.games/index.php?topic=4431.0); [GOG "text scrolls too fast PoR"](https://gog.com/forum/forgotten_realms_collection/text_scrolls_too_fast_por)
- Krynn series players raise the same battle-speed issue. — [GOG "champions of krynn battle speed"](https://gog.com/forum/dungeons_dragons_krynn_series/champions_of_krynn_battle_speed)
- Weapon damage and similar numbers sat in a printed booklet, not on screen. — [Super Adventures in Gaming, PoR part 2](http://superadventuresingaming.blogspot.com/2025/12/dungeons-dragons-games-vol-5-gold-box.html)

**Dark Sun (SSI, 1993/94)**
- Reviews praise a "vastly improved interface" over earlier SSI products and a mouse-driven point-and-click feel that is "sometimes frustrating". Its combat is turn-based on the same overhead map, compared to the Gold Box. I found nothing documenting its combat message text, pacing or log. — [Wikipedia, Dark Sun: Shattered Lands](https://en.wikipedia.org/wiki/Dark_Sun:_Shattered_Lands); [CRPG Addict, game 434](https://crpgaddict.blogspot.com/2021/10/game-434-dark-sun-shattered-lands-1993.html)

### Inferences
- At 320x200 the workable pattern is: a fixed small text area; terse, abbreviated, upper-case lines; a timed hold per message under the player's control; and no scrollback. The cost is lost information, so a modern overlay or log file would fill a real gap rather than duplicate the screen.
- For a Dark Sun remaster, the closest precedent is a file or side log in the BG/NWN "Name - Attack Roll d20 +/- mod = total vs AC : Hit" form. That adds the target number the IE/NWN logs leave out, plus a ToEE-style expandable breakdown.

### Gaps
- No primary documentation of Dark Sun's on-screen combat messages. The game itself (this repo's dice log) is the best source.
- The exact Gold Box line strings and delay constants need the wish docs or a disassembly (host blocked here).
- Infinity Engine readability at 640x480 (font, colours: BG uses coloured actor names in the dialog window) was not sourced.
