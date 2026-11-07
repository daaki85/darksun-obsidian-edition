# 2026-11-06/07: Pehtucl's chest, locked and trapped (pehtuclchest.py)

**Setup:** a new game (`start.sh`, `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh`: about 30
minutes, all in the background), Kurzak answered Goodbye, saved as `saves/pens-new-chest`. A save
made before keeps the pens' commands and objects as they were: the chest's USE command and the
cloak in it come only with a new game. To reach the chest: things 0-3 to (200, 1432) and the camera
to (40, 1322) in memory, walkto (216, 1440), then walkto (120, 1470) so no one stands on it (later the same day the chest's script refuses
that as too far, "You must be next to the chest": walk to (184, 1400), a square west of it, as in
`2026-11-07-review-fixes.md`); the
look pointer on it (161, 72), its look box's third button (236, 101) uses it. Its type set shut in
memory for each try (the save's chest was made before the shut type: `shut.py` in the log's steps).

## Seen
1. **The script runs on USE** (MAS 41's 6Dh): "The chest is locked. Gerakis doesn't know how to pick
   the lock. Bash it open?" Answered No: **the game opened the chest anyway** as the script ended.
   Byte +0Eh of its record (0Bh on the locked cell doors) made no difference; emptied (+08h), an
   empty window opened. With the safe's item type (67h) it stayed shut, but the game hung on the
   window until the script ended with a click and the window cleared (the safe's ending).
2. **Bashing:** six tries at Gerakis's real odds: "making a lot of noise but little else". With the
   odds raised (a test build, put back): "breaking it open, and a poisoned needle springs from it!",
   the chest a chest again (31h) by the click, and opened after it.
3. **The needle:** first as copied (the spell byte set to 177): 1d6 to every party member and no
   save: the byte is the trap's descriptor (DSUN.EXE 80A11h: d6 count, reach, damage kind, Detect
   Traps bit; DS:251Ch the kinds: 1, 2, 10h, 80h). Set to 02h: Cilla spotted it four times (16, 37,
   6, 27 against 45); with her thief class taken away, "Dice: 2d6 = [1 + 5] = 6" on Gerakis alone.
4. **A thief** (Gerakis made a thief in memory, classes and the 400h flag): the safe's thief test
   reads the class flags (field 8025h[71,17] & 400h; the local 26 copied first was the safe's own and
   never set). Level 10: traps failed (77 against 65), the needle sprung and dodged, the lock opened
   (31 against 67), the chest opened after the click. Level 1: traps failed, the lock failed, and
   again and again ("works at the lock but it holds", the needle not looked for again).
5. **Unlocked** (flag 796 set): the Loader made it a chest within a second, and using it opened it at
   once, no text.
6. Not seen: a thief disarming the needle (the same check, the other way).

## Testing notes
- The chest is object 1568, item 162 in that save; Pehtucl (creature 30) wanders the room: a look
  click meant for the chest once opened his talk, and a later click chose "Templars are scum! Die!"
  (a fight). Check where he is before clicking.
- `L` only toggles the panel; after a load it can be up or down: look at a shot before clicking.
