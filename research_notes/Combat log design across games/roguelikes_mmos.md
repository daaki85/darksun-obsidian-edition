# Combat message design in roguelikes and MMOs

Scope: concrete techniques that roguelikes (DCSS, NetHack, Brogue, Cogmind, Caves of Qud, Dwarf Fortress) and MMOs (WoW and its add-ons, FFXIV, GW2) use to keep a fast stream of combat messages readable, and what carries over to a turn-based dice log (plain text widget) and a 320x200 in-game panel.

Source note: this session's network allowed only raw.githubusercontent.com plus web search. gridsagegames.com, indiedb.com, reddit mirrors, steamcommunity.com, dwarffortresswiki.org, warcraft.wiki.gg and wiki.cavesofqud.com could not be fetched. So the DCSS, NetHack and Brogue facts below come from their primary sources (options guide, default settings files, Guidebook, game source code), read in full. The Cogmind, DF, Qud, WoW, FFXIV and GW2 facts come from search-result snippets of the cited pages. Treat quotes from those snippets as close but unverified, and re-check them against the page before quoting them in a published report.

## 1. How does DCSS merge and colour messages, and which defaults do players change?

### Takeaway
DCSS combines several mechanisms. Identical messages in a turn are merged into "x5". Short messages on the same channel share a line. Every message belongs to one of about 35 channels, each with its own colour or mute. A regex layer (`message_colour`) recolours or mutes single messages. Another regex list (`force_more_message`) makes chosen messages stop the game. The shipped defaults already dim combat clutter: misses and no-damage hits are dark grey. Danger messages are light red, and only a short curated list forces --More--. Players mostly tune these regex lists rather than the merge logic.

### Cited findings
**Merging repeats**
- `msg_condense_repeats = true`: "If the same message is repeated multiple times during the same turn, then it will be output in a condensed format indicating how many times it was repeated. If the same output (including the counter) is repeated over several turns, the Show Previous Message command (Ctrl-P) will likewise condense them into one. For example: The killer bee misses you. x5" — [DCSS options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- `msg_condense_short = true`: "If set, short messages on the same channel don't all start a new line." — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- In the source, a merge happens only if the channel and parameter are the same. An exact text match bumps `repeats`, which is printed as `" x%d"` (a code comment reads "TODO: colour the repeats indicator?"). Otherwise messages from the same turn join with "; " only if the joined text fits the window's line length. A punctuation check was added as "a hack to avoid pickup messages merging with combat on the same turn - should find a nicer heuristic". — [crawl message.cc](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/message.cc)

**Channels**
- Syntax: `channel.CHANNEL_NAME = (COLOUR | mute | default | on | off | plain)`. "mute = show no messages from channel (dangerous, be careful!)". "alternative = turn channel on to its alternative 'colourful' scheme". "The only multi-colour channels currently are monster_damage and god. All other channels are defaulted to on." — [options_guide.txt §3-k](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- The channels relevant to combat are: plain, prompt, danger ("serious threats to the character's existence"), warning, recovery, talk, talk_visual, sound, intrinsic_gain, monster_spell, monster_enchant, monster_warning (monsters coming into view), friend_spell/friend_enchant/friend_action (the same for allies), monster_damage ("messages telling how damaged a monster is"), multiturn, examine and examine_filter (the boring examine messages), and others. — [options_guide.txt §3-k](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)

**Per-message colouring (`message_colour`)**
- "message_colour ^= <colour>:<channel>:<regex>, ..." "message_colour allows you to override colours for individual messages. For instance, if you find the low hp warning to be insufficiently attention grabbing, you could do something like `message_colour += yellow:LOW HITPOINT WARNING` ... `message_colour += lightred:god:xom` ... If you don't want to see a message at all, you can mute it: `message_colour += mute:You start resting`". It is an ordered list, and the first match wins: "message_colour = cyan:hits / ^= red:crimson / += yellow:killer → 'The crimson imp hits you!' will be displayed in red, while 'The killer bee hits you!' will be displayed in cyan." — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- The shipped default palette is three semantic names: `$danger := lightred`, `$warning := yellow`, `$boring := darkgrey`. — [dat/defaults/standard_colours.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/dat/defaults/standard_colours.txt)
- Shipped defaults, under a "Unimportant messages and combat clutter" heading:
  - `msc += $boring:plain:miss(es)? (the|you|it)` and `msc += $boring:but (do no|doesn't do any) damage` (misses and zero-damage hits are dark grey)
  - `$boring:You start (resting|waiting)`, and mutes for "spammy" god messages
  - Danger examples: `$danger:drains you`, `$danger:curare-tipped.*hits you`, `$danger:constricts you`, `$danger:goes berserk!`, `$danger:corrodes you`

  — [dat/defaults/messages.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/dat/defaults/messages.txt)

**Forced pauses and attention**
- `force_more_message`: "Any message that contains a regex specified here will enforce a --More-- prompt, so it can be used to highlight really important events. This option ignores the show_more option." `flash_screen_message`: "will flash the screen yellow, so it can be used to highlight very important events indeed." `monster_alert` (default `uniques`): a --More-- "whenever it is first encountered", with the groups nasty/tough/easy/trivial and uniques. — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- The default `force_more_message` list ("Messages so important to require a --more--") covers events, not ordinary hits:
  - level-up ("You have reached level")
  - falling into a shaft, water or lava
  - an ally breaking free of control
  - Zot clock warnings
  - "^Careful!" (flight or form running out)
  - portal vaults, religion changes, distortion weapons, banishment

  — [dat/defaults/messages.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/dat/defaults/messages.txt)
- `show_more = false` (the default): "Setting this option to true will cause the game to prompt if more than a window-full of messages are output at once." `clear_messages = false`: messages "cleared between player actions". `small_more = false` puts --more-- on its own line. — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- Low-HP handling: `hp_warning = 10` gives "* * * LOW HITPOINT WARNING * * *" on the danger channel "when the player takes damage and their hitpoints are less than this percentage". `hp_colour = 70:yellow, 40:red` colours the status HP. (The guide's prose says "red if at less than 25%, yellow if at less than 50%", which contradicts the listed default values.) — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)
- Window size: `msg_min_height = 7` (minimum 5), `msg_max_height = 10`, `msg_webtiles_height = -1`. — [options_guide.txt](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/docs/options_guide.txt)

### Inferences
- The default design ships *semantic* colour names ($danger/$warning/$boring) rather than per-event colours. It then maps hundreds of regexes onto those three, which keeps the palette small and learnable. (Inference from the defaults files.)
- Two levels of dimming are used: muting for truly spammy lines, and dark grey for combat outcomes that change nothing (miss, no damage). Misses stay in the log for completeness but read as background.
- The --More-- interrupt is kept for rare, run-changing events. Show_more for window overflow is off by default, so a hard-hitting turn scrolls rather than stops.
- What players change most, judging by the options' own examples: they add to `force_more_message` and `message_colour` (yellow LOW HITPOINT WARNING, muting rest messages) and resize the message window. I found no survey of player rc files, so this is inference from the guide's examples.

### Gaps
- No player survey or popular rc file (for example on Reddit or CAO) could be fetched to show which defaults players most often change.

## 2. NetHack: --More--, msg_window, MSGTYPE

### Takeaway
NetHack's single top line with --More-- forces every message to be acknowledged. Its fixes are a recall buffer (^P with msg_window modes) and the MSGTYPE regex rules (hide/norep/stop/show). Status highlighting (hilite_status thresholds) moves "you are low" out of the message stream and onto the status line.

### Cited findings
- "If you see a '--More--' on the top line, this means that NetHack has another message to display on the screen, but it wants to make certain that you've read the one that is there first. To read the next message, just press the space bar." — [NetHack 3.7 Guidebook](https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.7/doc/Guidebook.mn)
- `msghistory`: "The number of top line messages to keep (and be able to recall with ^P) (default 20)." `msg_window`: "s single message (default...); c combination, two messages as 'single', then as 'full'; f full window, oldest message first; r full window reversed, newest message first." Curses defaults to `r`. — [Guidebook](https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.7/doc/Guidebook.mn)
- `MSGTYPE=type "pattern"`: "show message normally; hide never show the message; stop wait for user with more-prompt; norep show the message once, but not again if no other message is shown in between." Example: `MSGTYPE=stop "You feel hungry."`, `MSGTYPE=hide "You displaced *."`. "the last matching rule is used. Put the general case first, exceptions below them." — [Guidebook](https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.7/doc/Guidebook.mn)
- `OPTION=hilite_status:hitpoints/<=30%/red/normal` "will cause the hitpoints field to display in the color red if your hitpoints drop to or below a threshold of 30%". Also `hilite_status:wisdom/down/red/up/green`, which colours a change by its direction. — [Guidebook](https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.7/doc/Guidebook.mn)

### Inferences
- `norep` is a simpler cousin of DCSS's "x5": it drops consecutive duplicates instead of counting them. It suits narrow displays where a count suffix costs space. (Inference.)
- `hilite_status` "down red / up green" is a cheap change cue that needs no log line at all.

### Gaps
- I did not research variants' improvements (for example, the curses interface and message-window changes in variants) with sources.

## 3. Brogue: folding, fading and victim-based colour (from the Brogue CE source)

### Takeaway
Brogue buffers a turn's combat messages and joins them with semicolons into one sentence-line. Identical messages collapse to "(x3)", and above a cap to "(many)". Each combat line is coloured by *who was hurt*: the player or an ally is bad, an enemy is good. Older lines fade toward black, and lines not yet read stay bright.

### Cited findings
- Combat messages are buffered "just for timing; otherwise player combat messages appear after monsters, rather than before". They are flushed as FOLDABLE messages: "These messages are 'foldable', meaning that if space permits they may be joined together by semi-colons." — [BrogueCE Combat.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/Combat.c)
- Repeat counting: `"%s (x%d)"`, or `"%s (many)"` once `count >= MAX_MESSAGE_REPEATS`. "FOLDABLE messages from the same turn are combined... Only fold messages from the same turn". Lines are joined with "; " while `lineLength + 3 + messageLength <= DCOLS`, otherwise wrapped. A sentence capitaliser and punctuator then runs over the result. — [BrogueCE IO.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/IO.c)
- Collapse rule: "An incoming message may 'collapse' into another (be dropped in favor of bumping a repetition count) if the two have identical content and one of two other conditions is met. First, if the two messages arrived on the same turn... Alternately... if the older message is the latest one in the archive and the new one is not semi-colon foldable." — [IO.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/IO.c)
- `messageColorFromVictim`:
  - player → `badMessageColor`
  - ally → `badMessageColor`
  - enemy → `goodMessageColor`
  - hallucinating → white

  Misses use white ("damage > 0 ? messageColorFromVictim(defender) : &white"). The palette is good (60,50,100) blue-ish, bad (100,50,60) red-ish, advancement (50,100,60) green, item (100,100,50) yellow, and flavor and background in purples. — [IO.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/IO.c), [Combat.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/Combat.c), [Globals.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/Globals.c)
- Fading: messages already confirmed are drawn at 50% and then darkened further by age, `applyColorAverage(&messageColor, &black, 75 * i / MESSAGE_LINES)`. A code comment reads "do a fade from bottom to top to make it clear that the bottom messages are the most recent". --MORE-- appears only for REQUIRE_ACKNOWLEDGMENT messages or in "cautiousMode". Distant fights become a single "you hear combat in the distance". — [IO.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/IO.c), [Combat.c](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/Combat.c)

### Inferences
- Colouring by victim allegiance answers "is this good or bad for me?" at a glance without reading names. It is a two-colour code that survives a tiny font and low resolution.
- Age-fading plus "unread stays bright" shows what is new without timestamps.

### Gaps
- I found no published designer commentary by Brian Walker on the message log. The search returned nothing; findings are from the code only.

## 4. What does Cogmind's developer (Josh Ge, "Kyzrati") recommend? (quotes)

### Takeaway
Ge treats the main log as a small, terse *secondary* channel. Attention belongs on the map, so animations and on-map cues carry combat, and the log keeps only high-importance events. A separate combat or calculation log with selectable detail (up to a full roll breakdown) serves experts.

### Cited findings (from search snippets; gridsagegames.com could not be fetched)
- "The ultimate goal is to make the log a secondary source of information while the player focuses attention on the map. This is part of the reason why the log is so tiny, showing only six lines at a time!" — [Grid Sage Games, "Message Log" (Feb 2014)](https://www.gridsagegames.com/blog/2014/02/message-log/) (repost: [IndieDB](https://www.indiedb.com/games/cogmind/news/message-log))
- Messages "are all very short, like 4-5 words" under the simplified log scheme (2014 blog comment). — [Grid Sage Games, "Message Log"](https://www.gridsagegames.com/blog/2014/02/message-log/)
- r/roguelikedev FAQ Friday #30 "Message Logs" (Jan 2016), summarised in search snippets:
  - Cogmind leans less on its log because combat animations draw the eye to the map.
  - The log mostly holds high-importance messages (part or robot destruction, status changes).
  - The developer moves important information onto the map and keeps messages "informative but terse".
  - There were 304 message types defined in data, each with a "knowledge" condition deciding whether the player would know of it, and messages aren't always full sentences.
  - Ideas floated there: highlight the actor or map spot a log entry refers to on hover, and filter by message category.

  — [FAQ Friday #30 thread](https://reddit.birdcat.cafe/r/roguelikedev/comments/4236j9/faq_friday_30_message_logs), [Kyzrati comment](https://reddit.birdcat.cafe/r/roguelikedev/comments/4236j9/faq_friday_30_message_logs/cz78rfe/?context=3), [FAQ Fridays Revisited #30 (2018)](https://redlib.ssps.io/r/roguelikedev/comments/7xui6b/faq_fridays_revisited_30_message_logs/duca5fs/?context=3)
- The combat log has detail levels. With it "set to full it shows the entire breakdown of every roll". Lines look like "Base Hit %: 60+0h+10m=69", showing each modifier summed. Hit chance is clamped between 10% and 95%. — [Steam: Non-damaging hits in the combat log](https://steamcommunity.com/app/722730/discussions/0/2290590708541447855/), [Cogmind manual](https://www.gridsagegames.com/blogs/files/Cogmind_Manual.pdf)
- Advanced options: `disableCombatLogTurnNumbers`. The on-map combat log's fade time and length are set by `mapCombatLogDuration` and `mapCombatLogMaxLength`. A single-line combat log entry option was added to the to-do list after player requests (2019). — [Steam: Combat log wish](https://steamcommunity.com/app/722730/discussions/0/1839063537796619488/)

### Inferences
- Ge's model has three tiers. The map shows the event (animation). A tiny main log names it in a few words. An opt-in calculation log explains it as "60+0h+10m=69". This maps directly onto a dice log: the panel shows the outcome and the text widget shows the arithmetic.

### Gaps
- I could not fetch his later combat log posts (for example, the combat log and readability posts on gridsagegames.com) for verbatim quotes. Re-check the snippet quotes above against the pages.

## 5. Caves of Qud

### Takeaway
Qud's log is a scrolling text log with a full history screen (Ctrl+M). Its readability options are layout options: a separator between combat rounds, docking, font size, and sending some popups to the log. Players have long asked for verbosity filters, which it lacks.

### Cited findings (search snippets)
- The official wiki's Options page lists:
  - message log font scaling from -12pt to +24pt (modern UI)
  - dock background opacity
  - an option that inserts a separator line in the log between combat rounds
  - options to show ability-on-cooldown messages and scavenged items as log entries instead of popups
  - verbose companion level-up messages

  — [Caves of Qud wiki: Options](https://wiki.cavesofqud.com/wiki/Options)
- Players asked "Any way to customise the combat log?", and wanted verbosity levels and to stop the log being spammed with things like passing a banana tree. The full log is Ctrl+M and "goes back much farther than the message bar". — [Steam: customise the combat log](https://steamcommunity.com/app/333640/discussions/0/3269057884702617381/), [Steam: message history](https://steamcommunity.com/app/333640/discussions/0/5671690972174994280/), [Steam: more text for battles](https://steamcommunity.com/app/333640/discussions/0/1738886352901678227/)

### Inferences
- A per-round separator is the cheapest form of "per-turn summary": it groups lines by round without any merging logic.

## 6. What do Dwarf Fortress players say about combat report verbosity, and how do they cope?

### Takeaway
DF splits *announcements* (short, configurable, can pause or recenter) from *combat reports* (blow-by-blow anatomical detail). Its problems are volume, since sparring and animal fights flood a capped buffer and push out other messages, and a lack of summary. Players cope with announcements.txt flags, DFHack's logcleaner, external regex-filtered windows, and the unit's wound screen in place of the log.

### Cited findings (search snippets)
- Reports are separate from announcements, which cover non-combat events. Each announcement type can be set in `data/init/announcements.txt` to pause, recenter or link to reports. `UCR_A` links an announcement to active reports only, for events "too chatty to always generate a combat report for". — [DF wiki: Announcements.txt](https://www.dwarffortresswiki.org/index.php/Announcements.txt), [DF wiki: Reports](https://dwarffortresswiki.org/Reports)
- Buffer flooding: a bug report says recent reports or announcements are cleared because "much more prolific messages like long sparring logs or announcement spam" fill the buffer (about 3,000 entries), including animals sparring. — [DF bug 10480](https://dwarffortressbugtracker.com/view.php?id=10480)
- Players have asked for identical announcements to collapse into one entry with a count, shown in the form "x2 Urist falls over." — [DF bug 12670](https://dwarffortressbugtracker.com/view.php?id=12670)
- Tools: DFHack's `logcleaner` periodically clears combat, sparring and hunting reports, with filters and an overlay UI ([DFHack release notes](https://newreleases.io/project/github/DFHack/dfhack/release/53.10-r2rc1)). Announcement Window+ splits announcements and combat into separate windows using regex filters on gamelog.txt ([GitHub NuAoA/AnnouncementWindow](https://github.com/NuAoA/AnnouncementWindow)).
- A player complained of having "a hard time keeping up with the log and chain of events... especially with a lot of combat messages being repeated" — [r/dwarffortress questions thread](https://redlib.hbubli.cc/r/dwarffortress/comments/1iwzi4p/dwarf_fortress_questions_thread/melwyf6/?context=3). Another said reading combat logs is often the only way to reconstruct a fight, and suggested the unit's description or health tab for current injuries — [Steam: details about injuries and combat](https://steamcommunity.com/app/975370/discussions/0/3727323721768168342/).
- The wording follows wound type and tissue layer (blunt weapons bruise or sprain, swords cut or gash, layers of skin, fat and muscle). The words do not give an exact health number. — [DF wiki: Wound](https://dwarffortresswiki.org/index.php/Wound)

### Inferences
- DF shows the cost of verbosity without a summary: the detail is loved as storytelling but unusable as tactical information. Players read *state* (the wound screen) instead of *events* (the log). A dice log benefits from a per-fight state summary for the same reason.

### Gaps
- I found no verbatim Bay12 forum or Toady One statement on combat log verbosity. The Hacker News and PC Gamer pieces were not checked.

## 7. How do WoW and its add-ons turn a raw combat log into readable information?

### Takeaway
WoW keeps a raw, filterable, colour-configurable combat log tab, but players mostly don't read it. Add-ons parse the event stream into aggregates: per-fight segments, per-source and per-ability breakdowns, death recaps, and floating combat text with merge and throttle spam control.

### Cited findings (search snippets)
- Since patch 2.4, the client fires `COMBAT_LOG_EVENT_UNFILTERED` with every event for add-ons, while `COMBAT_LOG_EVENT` passes only events that match the user's active filters. — [Warcraft Wiki: Guide to the New Combat Log](https://warcraft.wiki.gg/wiki/Patch_2.4.0/Consolidated_API_changes/Guide_to_the_New_Combat_Log)
- The built-in filter UI (2008 era) has these tabs:
  - "Message Sources": which units you receive messages from
  - "Colors": a colour for each part of a message (source, target, spell, damage), with a preview
  - "Formatting": timestamps and similar
  - "Settings": saved filters, optionally limited to solo, party or raid

  — [Engadget: combat log-o-rama (2008)](https://www.engadget.com/2008-06-28-the-creamy-gui-center-combat-log-o-rama.html)
- "A damage meter is a common name for an addon that parses the combat log to measure player performance during combat". Recount, Details! and Skada are the best known. — [Warcraft Wiki: Damage meter](https://warcraft.wiki.gg/wiki/Damage_meter)
- Skada is "a modular damage meter with various viewing modes, segmented fights and customizable windows". Skada times a fight from your entering combat to its end, while Recount pauses in inactivity, so the same log gives different DPS. — [WowAce: Skada](https://www.wowace.com/projects/skada?page=57), [Engadget: Skada versus Recount (2013)](https://www.engadget.com/2013-03-12-addon-spotlight-skada-versus-recount.html)
- Details! changelog (2026): "new segment selection menu; breakdown window upgrades; tooltip upgrades". Other meters list a "Death log" view (Numeration), killing blow and overkill (Peelometer) and a death recap (Tomo). Since patch 12.0, add-ons reportedly can't read the combat log and use Blizzard's built-in meter data (Peelometer page). — [CurseForge: Details!](https://www.curseforge.com/wow/addons/details/files/7800678), [Numeration](https://www.curseforge.com/wow/addons/numeration), [Peelometer](https://www.curseforge.com/wow/addons/peelometer-damage-meter)
- Floating combat text spam control: MSBT 5.x had "Merge AoE data into one event with cumulative damage/healing done with number of normal and crits specified". Forks have adjustable spam thresholds. ZSBT advertises "merge/throttle/thresholds". — [CurseForge: MSBT](https://www.curseforge.com/wow/addons/mik-scrolling-battle-text), [MSBT TBC Anniversary](https://www.curseforge.com/wow/addons/mikscrollingbattletext-tbc-anniversary), [ZSBT](https://www.curseforge.com/wow/addons/zores-scrolling-battle-text)

### Inferences
- The MMO lesson is to *aggregate* rather than display: totals per actor and per fight, a breakdown on demand, and a death recap (the last N events before a death). The raw log is kept for forensics. Merging, for example "Fireball hits 3 targets for 412 (1 crit)", is the floating-text version of DCSS's "x5".

### Gaps
- No current (retail 12.x) Blizzard documentation of the built-in damage meter or the combat log settings was fetched.

## 8. FFXIV and Guild Wars 2

### Cited findings (search snippets; old sources)
- FFXIV: the log filters are under Character Config → Log Window Settings → Log Filters, and colour can be set per filter. Common player schemes are blue for HP recovered, red for damage taken, yellow for enfeebles and white for damage done. Players hide "Player misses enemy" or damage taken to cut clutter. — [GameFAQs: Battle chat log filters](https://gamefaqs.gamespot.com/boards/678050-final-fantasy-xiv-online-a-realm-reborn/67218026), [ffxivpro forum](https://www.ffxivpro.com/forum/topic/2578/main-healing-text-color-choices-filter-settings)
- GW2: the combat log is checkbox-filtered in the chat window. Players found it too spammy in fights and wanted a separate window, available only through arcdps. GW2-SCT shows "incoming damage on the left side and outgoing damage on the right side". Players complain that floating numbers hide targets and that damage taken is hard to notice. — [GW2-SCT](https://github.com/Artenuvielle/GW2-SCT), [GW2 forum: floating combat text blocking vision](https://en-forum.guildwars2.com/topic/87512-floating-combat-text-is-blocking-vision/), [GW2 forum: hard to notice damage taken](https://en-forum.guildwars2.com/topic/138718-hard-to-notice-damage-taken/)

### Inferences
- Separating incoming from outgoing spatially (left and right) or by colour is a recurring answer to "did *I* get hurt?".

## 9. Which techniques transfer to a turn-based dice log (plain text widget) and a 320x200 in-game panel?

### Takeaway
For the tiny panel, follow the Brogue and Cogmind pattern: a few words per event, colour by whom it hurts, "(x3)" merging, misses dimmed, and older lines faded. For the text widget, follow the DCSS, Cogmind-calculation-log and WoW-meter pattern: full roll arithmetic, a turn or round separator, and a per-fight summary (totals, kills, damage taken, deaths). Anything run-changing gets a forced pause; HP state belongs on the status display, not in the log.

### Inferences (all inferences; each grounded in the findings above)
- **Brevity and grammar.** Keep panel lines to "Actor verb Target N" at 4-5 words ([Cogmind](https://www.gridsagegames.com/blog/2014/02/message-log/)). Put the arithmetic ("roll 14+2 vs AC 5 → hit, 7 dmg") only in the text widget, as Cogmind's full log does ("60+0h+10m=69").
- **Merging.** Collapse identical lines within one turn into "... x3", or "(many)" above a cap ([DCSS](https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/message.cc), [Brogue](https://raw.githubusercontent.com/tmewett/BrogueCE/master/src/brogue/IO.c)). On a 320x200 panel, also join short same-turn lines with "; " when they fit (Brogue's line-length check). Merge only within one turn and one category, as both games do, so "x3" never spans unrelated events.
- **Colour.** Use a 3-4 colour semantic palette, not per-event colours:
  - danger or harm to the party (Brogue's bad, DCSS's lightred)
  - harm to foes (good)
  - boring (misses, no damage: dark grey, as DCSS ships)
  - notable (level-up, item, kill: yellow or green)

  On a VGA palette, choose entries that stay distinct at small font sizes. The plain text widget may have no colour, so carry the same categories as a short prefix or marker (for example `!` for harm to the party, `·` for a miss) or as a filterable tag.
- **Highlight what matters.** Kills, damage to the party, a member's HP dropping below a threshold (DCSS hp_warning at 10%, NetHack's hilite_status <=30%), deaths and level-ups. Show HP state on the portraits or status display rather than as log lines.
- **Pausing.** A forced acknowledgement only for rare, run-changing events (DCSS's force_more list: level-up, death or knock-out, being drained, and so on). Never pause per hit. Don't pause on a window overflow by default (DCSS `show_more = false`).
- **Recency.** Fade older panel lines and keep unread ones bright (Brogue), or show the newest at the bottom with a round separator (Qud). A turn number is optional (Cogmind lets you turn it off).
- **Summaries.** A per-round separator or line, and a per-fight footer in the text widget: damage dealt and taken per member, hits and misses, kills, and the last few events before each knock-out (a WoW-style death recap). DF shows what happens without a summary: players stop reading the log and look at state screens.
- **Filters and scrollback.** In the text widget, tag each line with a channel (party-attack, foe-attack, miss, spell, status, system) so it can be filtered or grepped, the plain-text form of DCSS channels and WoW filters. Keep the full raw log, and filter the view, not the record (WoW's unfiltered and filtered events).
- **Failure modes to avoid.**
  - A shared buffer flooded by low-value lines (DF sparring)
  - Merges that hide which actor did what (DCSS's own "hacky" punctuation heuristic)
  - Floating or overlay text that covers the action (GW2 complaints)
  - Meters that disagree because of how they time a fight (Skada vs Recount): define "fight start and end" explicitly for any summary

### Gaps
- No source here tested readability with players (no studies or metrics); the recommendations are design-practice synthesis.
