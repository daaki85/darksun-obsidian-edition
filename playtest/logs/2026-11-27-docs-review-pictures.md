# Docs pictures retake 2026-11-27 (docs review)
Under test: docs/fogbolt.png and docs/show-usable.png retaken with the class outfits. Build: obsidian-edition at 19c6ebbb. Save: fountain-user.

- `fountain-user`, autosave and quick save off in settings.json (memory edit ahead), `dismiss.sh`: the ambush, Ester's turn.
- `sheetbyte.py 0 0x45 or0x40`: Lex knows Fogbolt (memory only; not saved after).
- `passto.sh 0`: Lex's turn. U: Lex's USE screen on MAGE, LEVEL 1, five icons; Fogbolt the third (212,59). The USE screen's portraits show the party in its outfits.
- A loop of 60 `import -window` grabs (about 0.1 s apart) started, then the click on the Templar (240,128): grab 21-23 show "Fogbolt" over Lex with the casting sparkle, grab 25 the grey bolt in flight to the Templar. Dice log: "Templar's saving throw vs Fogbolt from Lex (spell): ... -> saved". `import -window` catches the bolt where the earlier Ctrl+F5 loop missed it (each Ctrl+F5 takes about 2 s in shot.sh).
- docs/fogbolt.png: grab 25, 225x100 at (88,105) of the 320x240 window, 300% (675x300).
- show-usable.png: no party in it (guards and templars only): current, left.
- Still pre-outfit: the small party figures on the Effects and inventory screens of new-spells-effects.png, effects-weapons.png, effects-charges.png, default-party-gerakis.png, kalzith.png, and on the map in pens-asks*.png, semyon-escape.png, kalzith-body.png (all small; listed in the report).
Water: no new area.
