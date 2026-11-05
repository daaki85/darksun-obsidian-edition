# 2026-11-05: the champion defiler's scrolls, read by a preserver and a Shinobi

**Under test:** the three scrolls the champions' defiler can carry (Fogbolt, Spook, Reflected Image,
with the new spells on): their price, and reading them as a preserver and as a Shinobi.

**In code:**
- `champions.SCROLL_SPELLS` = Fogbolt (198), Reflected Image (199), Spook (200). Each is level 1 in
  the game's spell table in play (`gd.spell_level`: 1, 1, 1).
- `defilerscrolls.scroll` prices a scroll at 3000 a spell level, so each is 3000.
- All three are on the Shinobi's list, in both `kits.SHINOBI_SPELLS` and DSCLOG's `SHINOBI_SPELLS`.

**Setup:**
- Loaded `pens-after-scar`.
- Gave the scrolls with `scrolltest.py shinobi give`, the same items `defilerscrolls.scroll` makes for the defiler:
  - Gerakis: the three, plus Magic Missile.
  - Cermak (preserver 3 / gladiator 3, INT 18): the three.
- Made Gerakis an 8th-level Shinobi in memory: class 17, level 8, kit byte 3, flags 0400h. Never saved.

**Seen:**
- **Item box** (right-click on the inventory): "3000 ceramic", "Scroll", with the spell's own icon.
  All three new-spell scrolls looked like this (`img/2026-11-05-scroll-box.png`).
- **Gerakis, as a Shinobi** (read languages 40, INT 13: 55%). The dice log said:
  - `Gerakis reads the scroll of Fogbolt: read languages d100 = 30, needs 40 or less -> read; d100 = 62, needs 55 or less (INT 13) -> not learnt (the scroll is used up)`. The screen said YOU FAIL TO LEARN THE SPELL.
  - Spook: read (37), not learnt (83). The scroll was used up.
  - `Gerakis reads the scroll of Reflected Image: read languages d100 = 45, needs 40 or less -> can't read it (the scroll is used up)`. The screen said YOU CAN NOT READ THE SCROLL.
  - Magic Missile: `can't learn Magic Missile from the scroll: not one of a Shinobi's spells (the scroll is kept)`. The screen said THAT IS NOT A SHINOBI SPELL.
- **Cermak, as a preserver** (INT 18: 85%):
  - Spook learnt (32).
  - Reflected Image learnt (64).
  - Fogbolt learnt (25).
  - His sheet's +45h went from 00h to C8h (Spook 80h, Fogbolt 40h, Reflected Image 08h).
  - The USE screen shows six 1st-level icons (`img/2026-11-05-cermak-spells.png`).

**Verdict:** the scrolls work and are priced right (3000 ceramic, 1st level). A Shinobi can learn
all three, after its read-languages roll and then its INT roll. It refuses a spell that isn't its own
and keeps the scroll. No bug found.

**Kit lessons (added to PLAYTESTING.md):**
- The backpack's rows are 18 pixels apart.
- An item box opens beside its row, so read the icon's place from a shot.
- A click on the icon needs a slow press: point first, then mousedown, 0.15 s, mouseup.
- The dice log doesn't repeat a Message line that is the same as the last one.
