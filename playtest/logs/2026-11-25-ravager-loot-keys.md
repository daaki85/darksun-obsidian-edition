# 2026-11-25: T, Shift+T, S, M, U and I in Wake of the Ravager; the quick page closed

**Under test:** branch `claude/ravager-loot-keys` (on `claude/ravager-join-blast-saves`). Row 10 of the port
list: SL's looting with T / Shift+T, selling with S and the M/U/I screen keys, on the sequel. DSCLOG2's
LOOT_KEY, SELL_KEY and MAP_KEY (in INT16's OUR_KEY, with MK_READ telling a peek from a read) and SHOP_LOOP
(site 82, the patch `shop_loop` at the shop's loop's test 88D99h, "cmp byte [143Dh],1"). The header's
fields are DSCLOG's, at its offsets (+1846 to +1859). The item moves are the Loader's (`loot.py`, `sell.py`
through `itemgate`) on the sequel's addresses (`ravlog.rav_items`). The dice log's view is read-only, so
for each pass `RavDiceLog._items_writable` opens the item and thing tables, the free lists, the money and
the header's words, and closes them after. The small fixes:

- the quick page put back (Q to E) by DSCLOG2 itself;
- the sequel's status names (`ravlog.ADDRESSES["STATUS_NAMES"]`, from the far pointers at DS:1463h);
- shorter autosave names ("Auto Day 1, 00:06 fight", "Auto Day 1, 09:05 Mines 1"; at most 28 letters).

DSCLOG2.EXE **42976 bytes** in the first runs. The final build, **42992**, has the page fix and T and S
left as the game's keys with no Loader.

The runs: [files/2026-11-25-ravager-loot-keys-start.sh](files/2026-11-25-ravager-loot-keys-start.sh). It
makes `ravLK`, a fresh copy of `rav` (thrown away after), loads `ravager-after-ambush` through the Loader's
start, then runs `ravdice.py` (none with `OFF`: the control). No memory edits. The looks were by
`ravloot.py` (new: the header's fields, the shop's passes, the container open, the shop, the member on
show, the money, the free lists walked; `thing T` a container's items).

## Looting (T, Shift+T)

The ambush's three Draxan bodies outside the start, things 209, 210 and 211. In the sequel the eye (the
pointer's mode 2, DS:1440h; right-click turns 1 → 4 → 2) on a body opens its container window. DS:05D6h
holds the container while it is open (SL's 05E6h), 9999 shut.

- **T on body 209** (six items; Ar'Anda had no backpack list). "Ar'Anda takes Bow, Stone Lotulis, Bone
  Brigandine Armor (3), Arrow". A pack list was made for her (thing 464), the body's list (469) was freed,
  the window shut. [img/2026-11-25-ravager-loot-t-pack.png](img/2026-11-25-ravager-loot-t-pack.png)
- **Shift+T on body 211.** "Ar'Anda takes Bone Ring Armor (3)" and "Plain weapons left: Bone Mace". The
  body opened again with the mace still in it. Then T: "Ar'Anda takes Bone Mace", and the list was freed.
- **T on body 210**, Ar'Anda's pack full. "Ar'Anda takes Bow, Stone Lotulis" and "Terrannus takes Bone
  Brigandine Armor (3), Arrow", with a new list for Terrannus.
- **Free lists**: 200 dynamic things (135 free + 65 out at the start: DS:56EFh the free list's head,
  DS:55C6h the count out); the free items' head DS:5AF3h, walked whole after each pass.
- **Control** (final build, the dice log stopped, more than 5 s): body 210 opened, T pressed. The window
  stayed open, LOOT_SEQ 0. [img/2026-11-25-ravager-loot-control-t.png](img/2026-11-25-ravager-loot-control-t.png)
  With the dice log started again, the same T: "Ar'Anda takes Bow, Stone Lotulis, Bone Brigandine Armor
  (3), Arrow", LOOT_SEQ 1, the window shut.

## Selling (S)

Notaku, south of Shadow Square. The route: y 1224, x 296, y 936; the eye on him; talk 3, 1, 3, 2 = "Show
me your goods". The shop's byte DS:143Dh is 1 while it is open (set at 7BCA6h); its merchant is DS:1A30h
(33). The member on show is at (load+3E71h):0B44h: 0 after a click on Ar'Anda's portrait. SHOP_AT was
stamped by site 82 each pass.

- **S**: "Ar'Anda sells 11 things for 204 ceramic pieces: ...". The party's money (2E8h:357h, the load +
  3C13h) went 5000 to 5204, the arrows were kept, the shop shut back to the talk, and 11 item records were
  freed. [img/2026-11-25-ravager-sell-s.png](img/2026-11-25-ravager-sell-s.png)
- After the sale "Show me your goods" was gone from Notaku's talk. This is the game's talk script; the sale
  writes nothing it reads. Not looked into further.
- No purse sound: DSCLOG2 has no SOUND_REQ (SL's sale plays one).
- **Control** for S: not played (the shop is a walk from the start). The emulated SELL_KEY covers it: with
  no Loader stamp, S is the game's key.

## Notaku's thank-you after S (fixed)

After S, Notaku said his no-sale line ("Sometimes the wisest purchase is none at all, yes?"), not "Thank you,
your business is appreciated." as after the game's own SELL (logs/2026-11-25-ravager-loot-tabs-join.md).

- **Why.** His script (GPL 153) keeps the party's money before the shop (3EFh: its 85h variable 0, the money
  at 2E8h:357h, into 89h 42), opens it, and as the shop returns tests the money against it (400h): moved, the
  thank-you (409h); not, the no-sale line (435h). The game's SELL pays while the shop is up. The Loader paid
  only after the shop had shut (it waits for SHOP_AT to go stale), so the test had already run.
- **The fix.** SELL_KEY sets SELL_WAIT as it counts S. SHOP_LOOP, at the loop's test with the shop shut (143Dh
  not 1) and SELL_WAIT set, holds there (STI, HLT) until the Loader's new SELL_DONE (header +1884, DSCLOG2's
  own) equals SELL_SEQ, or SELL_HOLD (55 ticks, 3 s) passes. `RavDiceLog._sell_pass` writes SELL_DONE for
  each S it has finished: sold, nothing to sell, or failed (not while the item gate makes it wait). The money
  is then in by the time the script tests it. An Escape out of the shop is never held.
- **Played** (a throwaway copy, `ravager-after-ambush`; Gerakis's armour moved into his pack on the inventory
  screen, the game's own move). DSCLOG2.EXE 43056 bytes, checked in memory against the build.
  - S with Gerakis on show: "Gerakis sells 1 things for 14 ceramic pieces: Bone Brigandine Armor 14", money
    5000 to 5014, then **"Thank you, your business is appreciated."**
    [img/2026-11-25-ravager-sell-s-thanks.png](img/2026-11-25-ravager-sell-s-thanks.png)
  - A new talk: his other armour piece sold by hand (SELL, "I'll give you 28", TAKE IT; 5014 to 5042), Escape:
    "Thank you, your business is appreciated."
  - A new talk: the shop opened, Escape with nothing sold: "Sometimes the wisest purchase is none at all, yes?"
  - In an earlier start, S with nothing plain in the pack ("Gerakis has no plain gear in the backpack to sell.")
    gave the no-sale line, as it should. The hold ended at once (SELL_DONE 1).
- **A mistake in that earlier start**: two right-clicks after closing the inventory gave the sword, not the
  eye, and a click on Notaku started a fight. Read the pointer's mode (DS:1440h, 2 the eye) before clicking
  on someone.

## M, U and I

U: USE. I: the inventory (the switch). I: shut. M: the overhead map (made O, the sequel's key). M: shut
(Escape). As in SL. A picture is in the project files (`2026-11-25-ravager-keys-umi.png`).

## The quick page (Part 1a), found wrong in play and fixed

The fix was meant to close the gap where F1 pressed just before the Loader put the page letter back from
Q to E would save into SAVQ. So DSCLOG2's SAVE_TICK now puts E back at the main loop's next pass, and the
Loader's own page-back (SL's `_page_back`) is off in the sequel.

- **First build.** F5, then F9: "Quick - Day 1, 00:08" listed. But the letters (DS:2088h, 20B9h) read EE
  with the window open.
- **Why.** The sequel's LOAD routine (4736h:0020h) **returns with the window up**: SAVE_REQ was 3 0.4 s
  after F9, and the window was still open. The map's main loop runs the window, and so does PROBE_SCROLL.
  Both page-backs (DSCLOG2's, then the Loader's after its 6 s wait) took Q off under the open window.
- **The fix.** SAVE_TICK puts E back only when the screen word DS:0DABh is 1 (the map). It is 2 with the
  window up, read in play. The Loader's page-back is off for the sequel (`QUICK_LAYOUT.page_back`).
- **Played.** F9: `EE req0 → QQ req2 → QQ req0 → QQ req3` (0.5 s) and QQ until Escape. EE 0.40 s after
  Escape, PAGES_BACK 1. [img/2026-11-25-ravager-quick-page-f9.png](img/2026-11-25-ravager-quick-page-f9.png)
- **F1 after it** opened the game's page ("AFTER AMBUSH").
- **A load from F9's window.** F5 at y 1304, a walk to y 1448, F9, then LOAD on the newest row ("Quick -
  Day 1, 00:05"). The party was back at 1304, so the file read was SAVQ02. SAVE01 is at 1544, by the
  locked gates.
- An F1 save typed into row 2 saved at once with an empty name (SAVE02.SAV, in the throwaway copy). It
  went to the E page as it should.

## Not played

- **Status names (Part 1b):** checked in the code only. The far pointers at DS:1463h give 0 New, 1 Okay,
  2 Stunned, 3 Out Cold, 4 Dying, 5 Animated, 6 Petrified, 7 Dead, 8 Gone. The blast log's dead member had
  7. A unit test covers it.
- **Autosave names (Part 1c):** unit tests only. Every area's name and the fight's, on day 1 and day 147,
  are at most 28 letters. The earlier play saw the window cut at 29.
- **S's control and `RAV_SKIP=shop_loop`:** emulated only.

Water: barrels and a jug by Notaku's stall, south of Shadow Square (Tyr, not a new area).
