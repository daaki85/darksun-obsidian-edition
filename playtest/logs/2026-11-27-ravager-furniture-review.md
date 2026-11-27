# Ravager furniture (#265) in game, against the stock pictures

Build: claude/ravager-all-area-furniture with obsidian-edition merged (3dbff4dc), DSCLOG2 rebuilt.
Follow-up: the [repair and live retest](2026-11-27-ravager-furniture-joins.md) identifies the red bed as 524 + 525. The original report below records the visible defect.

Save: ravager-roost, then ravjump.py to each region; the view moved onto changed placements by
writing the camera (DS:1408h). Control: the same jump with RAV_SKIP=figures (the stock pictures).

1. Veiled Alliance HQ (33h, jump to square 18, 25). Shelves, the potion table, couch, table and chair,
   broken crates and the vase on its crate all stand on the floor. **The torn beds break in two**: the
   head piece (object 9536, picture 2591 at 181,445 and 1205,445) came down and the foot piece (9537,
   picture 2704 at 160,447 and 1184,447) didn't, so floor shows across each bed. The storeroom's stacked
   barrels show a thin line of floor between upper and lower barrel. Codex notes written
   (codex-notes/2026-11-27-furniture-torn-beds.md in the project files); not merged.
2. Forest (01h, square 78, 10). The dining sets sit together; the green rug shows behind the lowered tables.
3. Mines 3 (3Ah, square 15, 46). The throne's back and seat meet. The other spots weren't reached: the
   jump lands in a fight.

Water: none seen in the three rooms looked at.
