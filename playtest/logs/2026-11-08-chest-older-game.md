# 2026-11-08: Pehtucl's chest in a game from before 2.14.0 (the user's "trap" save)

The user: "I got a notification that I needed to be closer to the chest in order to work it, and
the chest inventory just opened right after that"; and, bashing it open, "no indication about a trap".

1. `loadsave.sh trap-user`: flags 795 (disarmed) and 796 (unlocked) clear; the chest's record
   (picture -1568) had item type **31h, the plain chest**, not the shut type (67h) the mod's
   SEGOBJEX gives it since 2.14.0: the game came to the pens with an earlier version, while its
   USE command comes in all the same (the pens' master script).
2. From 4 squares off (leader 136,1400): the eye on the chest (200,95), its look box's third
   button (141,125): "You must be next to the chest in order to work on it." and then the chest's
   window opened with its things: reproduced.
3. Beside it (walkto 184,1400), Lex (a fighter/preserver): "The chest is locked. Lex doesn't know
   how to pick the lock. Bash it open?" Y: "smashes at the lock, making a lot of noise" (and the
   plain chest opened after each try). `bashloop.sh` repeated it: on a later try "Lex smashes at
   the lock, breaking it open, and a poisoned needle springs from it!", the narration on screen;
   then the game's trap roll for the party's best: "Seneca tries to find/remove traps: d100 = 21,
   needs 52 or less -> success" (the needle avoided: the game shows nothing on screen for that).
4. Fix: `pehtuclchest.watch` shuts a plain chest that isn't unlocked (67h), as it makes a shut one
   a chest once unlocked. Reloaded: within seconds the type read 67h; from afar the message, and
   the chest stayed shut.
