# T and Shift+T with Caps Lock on (2026-11-11)

DSCLOG 69,360 bytes (`LOOT_KEY` reading the Shift keys from the BIOS flags at 0:0417h);
`buildcheck.py` OK. From `fountain-user`: `dismiss.sh`, `fightout.sh` (4 rounds, 6 kills).

- The guards' bodies lay under the party's figures: look clicks there hit a member and opened the
  Effects screen. `walkto.py 1000 1490` moved the party west; the bodies then showed at about
  (230,138), (206,150), (226,158), Pehtucl's at (60,152) (camera 904,1368).
- `xdotool key --window <DOSBox> Caps_Lock`: the BIOS flags read 40h (Caps Lock on, no Shift).
- Body 146 (eye at 230,138), **Shift+T** (with Caps Lock a lower-case t, 1474h): "Lex takes
  Starfruit, Leather Arm Armor, Leather Chest Armor, Wooden Arrows" / "Plain weapons left: Wooden
  Bow, Obsidian Long Sword": Shift+T's mode, as it should be (before the fix this was T's).
- Opened again, **T** (with Caps Lock an upper-case T, 1454h): "Lex takes Wooden Bow, Obsidian Long
  Sword": T's mode (before the fix, Shift+T's).
- Caps Lock turned off again. Never saved.
