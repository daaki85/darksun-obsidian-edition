# 2026-11-25: the Loader's tabs and the loot keys joined in one build of the sequel's helper; Notaku's goods and the empty save name

**Under test:** branch `claude/ravager-join-loot-tabs` (PR #177), the join of [the Loader's Dialogue and Journal
tabs](2026-11-25-ravager-loader-tabs.md) (sites 93-94) and [T / Shift+T, S, M/U/I and the quick page
fix](2026-11-25-ravager-loot-keys.md) (site 82). DSCLOG2.EXE built from the joined source: **43216 bytes**. A smoke
play (nothing new built), and two questions the loot-keys log left open. Play 15:03-15:26 UTC. Three throwaway copies
of `rav`, all deleted after. No memory edits; nothing kept.

The runs: [files/2026-11-25-ravager-loot-tabs-join-start.sh](files/2026-11-25-ravager-loot-tabs-join-start.sh)
(`ravJ5`, ravager-after-ambush through the Loader's start, then `ravdice.py`) and
[files/2026-11-25-ravager-loot-tabs-join-plain.sh](files/2026-11-25-ravager-loot-tabs-join-plain.sh) (`ravJ5p`, the
same save in the plain sequel: GOG's DSUN.EXE, no Loader, no DSCLOG2, no patches).

**The build in place.** DSCLOG2's segment in memory (CA1Bh, header `DSCLOGR1`) was compared with each file's load
image over 43000 bytes. The joined file matched **42153** bytes. The tabs branch's build (42736 bytes) matched 36181,
and the loot-keys branch's (42992) matched 12089. The same 42153 was read in copy B. The window was the sequel's
640x480.

## Copy A: the smoke play (mod, dice log)

- **Memory** (`dosmem.py`): DSCLOG2 takes **42688 bytes** in upper memory (MCB CA0Ah). After it, **112768** bytes
  are free in one piece (MCB D477h, the chain's Z: whole). The blast/saves join had 41984 and 113472, so this
  build uses 704 bytes more. DOS memory free after the game: 74432 bytes. The numbers were the same at the end.
- **T**: the party was walked south to y 1448. The eye on the top Draxan body (game 96,150) opened thing 209's
  window (DS:05D6h 209). T gave "Ar'Anda takes Bow, Stone Lotulis, Bone Brigandine Armor (3), Arrow", LOOT_SEQ 1,
  and the window shut ([picture](img/2026-11-25-ravager-jlt-loot-t.png)). Before that, a click with the eye on the
  loose pile at (111,121) picked it up (pointer mode 3), and the next click put it back down (thing 228). That was
  ordinary play, not an edit.
- **F5**: "Quick save" over the leader ([picture](img/2026-11-25-ravager-jlt-f5.png)). The dice log wrote `Quick save:
  "Quick - Day 1, 00:06" (the QUICK page, slot 1)`, SAVQ01.SAV was 51771 bytes, and GREQ 101 was written. Then the
  party walked to y 1384. **F9**: the LOAD window on "Quick - Day 1, 00:06", letters QQ
  ([picture](img/2026-11-25-ravager-jlt-f9.png)). **Return** loaded it: the leader was back at y 1448, GREQ read 1,
  and the letters were EE again.
- **Uhubito, the Dialogue tab.** `ravdice.py` was stopped by pid, then the Loader's window was started
  (`python3.12 -m dsloader view --pid`, Xvfb `:56`). A click on his office floor (240,140), then (220,170), opened
  the talk, and that second click chose "Who are you?". Key 3 gave Goodbye, and Return closed the talk. The
  **Dialogue tab** showed "I don't want any trouble in here!...", the five numbered replies, "You chose: Who are
  you?", "I am Uhubito, the caravan master...", the three replies, "You chose: Goodbye." and "Goodbye."
  ([picture](img/2026-11-25-ravager-jlt-dialogue.png)). The speaker stayed "Portrait 18" after CLOSE, and
  `ravtext.py`'s "talked to" was thing 16. The tabs log's talk, started on him through the Look box, learned
  "Caravan Master". Why this one didn't wasn't looked into. After this, the window and Xvfb `:56`
  were stopped by pid and the dice log was started again.
- **S at Notaku's.** The route was Up to y 1224, Left to x 296, Up to y 936. The eye on him (105,42), the Look box's
  first button (125,73), then talk 3, 1, 3 brought the menu, and 2 "Show me your goods." opened the shop. A click
  on Ar'Anda's portrait (30,25) showed her, then S: "Ar'Anda sells 5 things for 100 ceramic pieces: Bone Brigandine
  Armor x3 70, Stone Lotulis 12, Bow 18". The money went from 5000 to 5100, and the shop shut back to the talk
  ([picture](img/2026-11-25-ravager-jlt-sell-s.png)).
- **No Illegal Op, no quit**: STDOUT.TXT was 0 bytes, and DOSBox stayed up until it was stopped by pid.

## Investigation 1: "Show me your goods" gone after a sale. The game's own.

| Run | What was done in the shop | Notaku's line after it | "Show me your goods" |
|---|---|---|---|
| A, mod, talk 1 | S (the Loader's sale) | "Sometimes the wisest purchase is none at all, yes?" | gone |
| A, mod, talk 2 (a new talk) | (before the shop) | "Greetings once again, Thy'rokh..." | **back** ([picture](img/2026-11-25-ravager-jlt-talk-again.png)) |
| A, mod, talk 2 | arrows sold by hand (SELL, "I'll give you 12", TAKE IT; money 5100 to 5388), Escape | "Thank you, your business is appreciated." | gone ([picture](img/2026-11-25-ravager-jlt-hand-sale.png)) |
| A, mod, talk 3 | nothing, Escape | "Sometimes the wisest purchase is none at all, yes?" | gone |
| A, mod, talk 4 | Gerakis's Bone Brigandine Armor by hand (28) | "Thank you, your business is appreciated." | gone |
| P, **plain sequel** | Gerakis's Bone Brigandine Armor by hand (48: no `sell_price`) | "Thank you, your business is appreciated." | gone ([picture](img/2026-11-25-ravager-jlt-plain-sale.png)) |

- **The game's talk script drops the option for the rest of that conversation after any visit to the shop**: a
  sale, a sale by hand, or no trade at all. It does the same in the plain sequel. A new talk offers it again. Nothing
  to fix.
- **The one difference that comes from the mod:** after S, Notaku says the no-trade line ("none at all"), not "Thank
  you". The script tells a sale from no trade by something the shop's own SELL sets, and the Loader's sale
  (`sell.py`, the item moves and the money written directly) doesn't set it. A diff of the data segment around a sale
  by hand changed too much to point at the byte. It is cosmetic and was left open (RESEARCH.md).
- The control asked for (`RAV_SKIP=shop_loop`, no dice log) was replaced by the stricter plain sequel: no patch, no
  DSCLOG2 and no Loader at all. Upper memory there was 9FFFh SC and D000h free (65520), with no helper.

## Investigation 2: the F1 save with an empty name. The game's own.

- **Plain sequel**: F1, a click on row 2, "test" typed key by key, then Return saved SAVE02 "test". F1, a click on
  row 3, then **Return with the name box empty: SAVE03 was saved at once, its name ''** (`namedsaves.save_name`)
  ([picture](img/2026-11-25-ravager-jlt-plain-empty-save.png): the empty third row). Typing m u i t s M U I T S
  put all ten letters in the box.
- **Mod with the dice log (copies A and B):** F1, row 2, "test" and Return gave "test". Row 3 clicked twice saved
  nothing. Return with the box empty saved SAVE03 with an empty name ("Message: GAME SAVED"). In copy B, m u i t s
  M U I T S typed key by key, `xdotool type "Second save"`, and "abc" typed after F5, F9, Escape and F1 at once (the
  quick page back to E for F1) were all typed in, and nothing saved until asked. **SAVE (252,46) clicked with the
  box empty saved SAVE02 at once, named ''**.
- So an empty name comes from **SAVE or Return pressed while the box is empty**, in the plain game as in the mod. The
  loot-keys log's F1 picture has the pointer on SAVE: its letters most likely never reached the box, and the click
  saved. No key of the mod's (T, S, M/U/I, F5, F9) is taken in the name box. Nothing to fix.
- **Escape in the name box doesn't close the save window** (the box keeps the focus). EXIT is at (252,67).

## Not run

The watchdog (each step was watched by a shot). The Journal tab (the tabs log played it). No new area (Tyr's
streets, Uhubito's office and Notaku's stall are all known), so no water to add: the barrels by Notaku's stall are
already in ROUTE.md.

Pictures: `/mnt/project-files/ravager/2026-11-25-ravager-jlt-loot-t.png`, `-f5.png`, `-f9.png`, `-dialogue.png`,
`-sell-s.png`, `-talk-again.png`, `-hand-sale.png`, `-plain-sale.png`, `-plain-empty-save.png`.
