# 2026-11-19 (5): "can't save" below 6th level, with and without the signed compare

**Under test:** the saving throw's signed compare (`save_signed`, found by hand at WotR 66EACh),
which only matters once Scare's record allows a save: a target below 6th level then gets -100
("can't save"), and the unsigned compare read that as a huge total, a save. Three games: as SSI
left it (`rav`), all the fixes (`ravfix`), all but the signed compare (`ravfix-ns`, from
`ravfixes.py --skip=save_signed`). Gerakis (a half-giant gladiator 7) was made 3rd level in memory
(`SCARE_LEVEL=3=3`, sheet +1Eh; a test edit, never saved).

1. **Which level the rule reads** (WotR 83606h, the save modifiers; Scare's part 83EA7h: "cmp
   [bp-6],6 / jl" then +100, the race part ending in -100 at 84284h): `[bp-6]` is the routine at
   1987:154 in the image (an overlay; its selector 98h in the file): for a human the sheet's first
   level (+1Eh), else the best of the class levels (+1Eh on, where the class at +1Bh on is set). So
   Gerakis's 3 is what it reads. (In the file an overlay's far call names a selector of the
   overlay manager's table, not a segment: follow it in build_image's image.)
2. **ravfix-ns, first try:** Scare cast, nobody scared, but whether it went off wasn't checked.
   **ravfix, first try:** Ar'anda's Move was 0 (the END menu up; Escape closed it) and the cast
   didn't go off: nothing changed.
3. **ravfix, second try** (her next turn): the cast went off (a blue sparkle over the group in the
   burst of grabs): **Gerakis +18h 60h, "Gerakis 165/165 Afraid"** on his turn, running up the
   street; Thy'rokh (6th) and Terrannus (7th) Okay.
4. **ravfix-ns, again**, with the cast checked: her 2nd-level casts left went from 2 to 1
   (DS:446Ah: 03 01 02): **Gerakis Okay** ("Gerakis 155/165 Okay" on his turn), and everyone else.
5. **So**, with Scare's reach over a 3rd-level and 6th- and 7th-level members:

   | | 3rd level (Gerakis, lowered) | 6th and 7th level |
   |---|---|---|
   | As SSI left it (no save allowed) | (scared: no save; seen for 6th) | Afraid (Thy'rokh) |
   | Scare's record fixed, the compare not | Okay: "can't save" saved | Okay |
   | Both fixed | **Afraid** | Okay |

   The signed compare is what makes "can't save" fail. No roll decides any of it.
6. **Found on the way:** the spell slots: DS:446Ah + 22h x member, wizard casts left by level (9
   bytes), the priest's 0Bh on (Terrannus 7 6 4 2 at 4497h, Thy'rokh 6 5 4 1 at 44B9h). The ring of
   dots shows when the aim is on bare floor or a foe, not on a party member's figure. The first C
   after the fight's keys is often lost: `ravscare.sh` now presses it until USE's red title pixel
   (window 314,48) is there.

**Stalls:** a C lost then a click meant for LEVEL walked Ar'anda; a cast with Move 0 went nowhere.

**Water:** none new.
