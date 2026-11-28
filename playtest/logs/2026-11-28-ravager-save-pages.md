# 2026-11-28: Wake of the Ravager, more saves (pages 2 to 4 and QUICK)

Under test: DSCLOG2's MORE SAVES, sites 216, 238 and 239 (branch `claude/ravager-save-pages`).

All from `ravload.sh ravager-after-ambush` (the game's SAVE01 "AFTER AMBUSH"; the folder already had the
QUICK page's SAVQ01 and SAVQ06 from earlier plays).

## First tries (fixed)

- **No label, and the game shut on PgDn.** The first DOSBox had started before the helper was rebuilt (check
  the start time against DSCLOG2.EXE's). With the new build, F2 then PgDn shut the game: PAGE_KEY's offsets
  were reckoned from the site + 2, but a 3-byte site returns to the site + 3 (7DABFh), so each of the window's
  routines was called a byte in. Fixed (PG_BACK).
- **The label from the main loop never came**: with F2's window up WIN_SHOWN (DS:1431h) is 0, and the window's
  routine gets no message but buttons and keys. The label is drawn from the opening routine now (site 216, the
  `add sp,4` after its window draw, 7D691h), after the window's own draw (drawn before it, the text was wiped).

## Play

- F2: LOAD, AFTER AMBUSH chosen, **PAGE 1** and **PGUP PGDN** under EXIT. F1: the same in the SAVE window.
- F1, PgDn: PAGE 2, empty rows. A click on a row, "PAGE TWO", Return: `SAVB02.SAV` written, and CHARSAVE.GFF's
  **GREQ 202** (`ravquick.py greq`).
- F2, PgDn: PAGE 2 with PAGE TWO chosen and named below. PgDn: pages 3 and 4 passed by (empty), **QUICK** with
  "Quick - Day 1, 00:05" chosen and the autosave in row 6. PgDn again: QUICK kept. PgUp: back to PAGE 2 (4 and 3
  passed by).
- LOAD on PAGE TWO: the game loaded. F2 again: PAGE 1. Before the page-back set the chosen row to 0, the row
  chosen on page 2 (row 2, empty on page 1) stayed chosen, with no name below; after it, AFTER AMBUSH chosen.
- F1, PgDn four times: PAGE 2, 3, 4, then 4 kept (no QUICK in the save window).

Not tried: a save of the sequel's started without the Loader on pages 2 to 4 (the game alone sees page 1 only,
as Shattered Lands'), the named saves' copies of pages 2 to 4 in play (unit tests only).

Water: none new.
