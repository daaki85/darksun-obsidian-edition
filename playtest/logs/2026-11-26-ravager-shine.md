# Test log: the magic items' shine in Wake of the Ravager (2026-11-26)

Under test: the Loader's copy of OBJEX.GFF with the sequel's still magic items' icons shining (`dsloader/ravshine.py`,
`ravager.objects_fixed`'s step `item_shine`), and DSCLOG2's SHOP_SHINE (site 163 at 2F7BEh, the game's wait for an
event) with SHINE_TURN in SHOP_LOOP (site 82). The Loader's way (`ravload.sh ravager-after-ambush
/tmp/playtest/ravGX`, a throwaway copy), the dice log attached. No memory edit; nothing saved.

## Steps

1. **A survey** (scratch, on the player's OBJEX.GFF): every item record with a plus or a power, its object's icon
   decoded (`sequelicons.decode`) and its pixels in the cycled runs (1-31) counted. Most magic weapons have 2-8;
   twelve magic items have none or one or two: Dragonsbane +4 (675), Gloves +3 (680), Chatchka +1 (733), two
   leather armours +1 and +3 (833, 834) and a scale armour +3 (853), Boots (1603), Amulet (30010), Ioun Stone
   (30012), Toothed Club +2 (30014), Rod (31202), Necklace (31209). Each icon is its object's own. (Spellbooks,
   potions, fruits and doors have powers too, and no shine, as in Shattered Lands: left so.)
2. Each given every other pixel of its blade, metal, gem or brightest shades in a run (the weapons and the gold
   the fire's 16-23, the Chatchka the violet 6-10, the Boots the green 11-15, the rest the water's 24-31).
3. **The inventory** (the save's party already carries two of them: Gerakis Dragonsbane +4, Thy'rokh the
   Chatchka +1): a burst of grabs (`ravburst.sh`): the Dragonsbane's blade changed in 26 of 58 frames, fire
   running along it; the Chatchka's violet in 33 of 67. **Control** (`RAV_SKIP=item_shine`, the new `ravstart.sh`
   part): the same view, the blade grey and still (`img/2026-11-26-ravager-shine.png`).
4. **A shop** (Notaku, Shadow Square: the walk `ravgo.py x 1176 y 1224 x 520 y 1360 x 296 y 900`, the look
   pointer on him at game 80,20, the Look box's first button at 101,66, then the keys 3, 1, 3, 2: "Show me your
   goods."): with the build before SHOP_SHINE **no icon changed in 55 frames**, the inventory's nor the shop's
   (the sequel's colour cycles stand still on a shop's screen, as Shattered Lands' did). With it: the shop's
   column changed in 47 of 92 frames, `shine_turns` (header +1982) 118
   (`img/2026-11-26-ravager-shop-shine.png`).
5. Memory (`dosmem.py`): DSCLOG2.EXE 55,152 bytes, its upper memory block 54,624 bytes, 100,832 bytes of upper
   memory left.

## Found

- `ravgo.py`'s way to Notaku from the save in the 2026-11-25 log (x 1176, y 1224, x 296) sticks at x ~520 on
  y 1224 (a stall); go down to y 1360 there first.
- The leader differed between two runs from the same save (Thy'rokh, then Terrannus): not the load (three loads
  all gave Thy'rokh, 2026-11-26 see-through log) but the talk's keys: 1-4 on the map pick the leader, and when the
  talk came up late the last key, 2, made Terrannus leader. His CHA 18 is 5% off, so Notaku's top price was
  42,750, not 45,000 (the picture's crop cuts the first digit: "2750").

## Left

- See-through figures: not built. With 100,832 bytes of upper memory left, its 14,160-byte GHOST block and about
  1.8 KB of code would leave about 84,900 bytes (83 KB): under the 85 KB line, so asked before going on. The HMA's
  far block has about 9 KB free, not enough for the block either.
