# 2026-11-25: the Loader's Dialogue, Journal, Spells and Memory tabs on Wake of the Ravager

**Under test** (branch `claude/ravager-loader-tabs`, on `claude/ravager-join-blast-saves`): DSCLOG2's TEXT, Shattered
Lands' PROBE_TEXT and PROBE_MSG ported as sites **93** ("text", the dialogue window's input at 87BA0h, SL's 7CE83h)
and **94** ("message", the message box at 59A0Bh, SL's 5536Eh), each on the routine's `push bp / mov bp,sp`; the text
buffer (2048 bytes) in the far block (FAR_TBUF, after FAR_RED: FAR_TOP A0B8h, still in the HMA), the header's
SL places +126 TPOS, +128 TBUF_OFF, +130 TSIZE, +132/+134 the probes, +138 TBUF_SEG (no new header fields).
RavDiceLog runs SL's `_take_text` (the Dialogue tab, the journal, "Message:" lines); the sequel's reply addresses
(DS:25BAh the row clicked, 6321h the scroll, 6356h the texts) and who is talked to (load + 3C13h:365h) in ravlog's
layout; its portraits kept as 10000 + N (ravlog.RAV_PORTRAITS) so names given or learned stay apart from SL's; its
journal a chain of its own (no place found for the head's id in the sequel's numbers). DSCLOG2.EXE 42512 -> 42736
bytes (+224 resident; the buffer is in the far block).

The copy `ravTX` of `ravK`, `ravload.sh ravager-after-ambush` (the opening party in Tyr), the Loader's window
(`python3.12 -m dsloader view --pid`, Xvfb `:56` 1440x900). One test edit (the scroll, below); nothing saved.

## Run A (the build)

- **A conversation**: Uhubito's caravan office (the building east of the street: a click on its floor, game
  240,140, walks the party in; then 220,170 beside the counter). Two right-clicks for the look pointer, a click on
  him (210,165): his Look box ("Caravan Master, LEVEL: 3"); its first button (230,188) talks: "I don't want any
  trouble in here!", five replies; key 2 "Who are you?", then key 3 Goodbye, Return to close.
- The **Dialogue tab**: his lines, "(What do you say?)" and the numbered replies, "You chose: Who are you?",
  his answer ("I am Uhubito, the caravan master..."), "You chose: Goodbye.", "Goodbye.". Speaker "Portrait 18"
  until the window's CLOSE, then **"Caravan Master"** on every line (learned: one face, replies, started on him;
  settings.json `speakers_learned` `{"10018": "Caravan Master"}`)
  ([picture](img/2026-11-25-ravager-tabs-dialogue.png)).
- `ravtext.py`: the records as SL's: portrait 18 (kind 1), text (kind 2, word 115), "What do you say?" and the
  replies (kind 0, numbered by the word), kind 3, the answer in three pieces, "END" when a page is done and
  "CLOSE" only once the last page is clicked away.
- The **Journal tab**: "Day 1 - Tyr", the talk and the choices; later the message (4 entries)
  ([picture](img/2026-11-25-ravager-tabs-journal.png)). The journal keeps the speaker as it was when said
  ("Portrait 18"), as SL's does.
- **A message box**: Ar'Anda's left hand (item 1) made a spellbook of spell 0, which she knows (`ravshop.py
  scroll 0 1 0`, a test edit); I, her portrait (30,30), a right click on the left hand (173,92), the box's spell
  icon (267,78) pressed slowly: **YOU ALREADY KNOW THIS SPELL** on screen
  ([picture](img/2026-11-25-ravager-tabs-message-game.png)), a kind 16 record, the dice log's
  **"Message: YOU ALREADY KNOW THIS SPELL"** ([picture](img/2026-11-25-ravager-tabs-message.png)) and the journal's
  entry.
- The **Spells tab** (already working, the sequel's records from the Loader's RESOURCE.GFF copy): Acid Arrow,
  Anti Magic Shell, Armor, Blink, Blur..., each with its damage, save, effect, time and the party's caster level.
- The **Memory tools tab** (already working): "Gerakis" found at 72378h; the creature records at the sequel's
  stride 31h, "Record addresses in the party table" on.

## Control C (`RAV_SKIP=text,message`: the game's bytes at 87BA0h and 59A0Bh)

The same talk: the Dialogue tab holds only "You chose: Who are you?" (read from the game's reply row, the
sequel's DS:25BAh) ([picture](img/2026-11-25-ravager-tabs-control.png)); the same scroll: the message on screen
(DSCLOG2's MSG_SHOWN, sites 58/59, untouched), no "Message:" line, `ravtext.py`: TPOS 0.

No Illegal Op, DOSBox up throughout. Window the sequel's 640x480. Not run: the watchdog (each step watched by a
shot). No new area (Uhubito's office was noted by the shops run): no water to add.
