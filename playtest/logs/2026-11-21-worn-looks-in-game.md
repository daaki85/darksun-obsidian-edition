# The worn looks in the game (2026-11-21)

**Under test:** `prototypes/wornlooks.py` (looks by what is worn: a robe, leather, bone scale,
chain, a cloak with its hood up), put into the game with `outfitgame.py`'s new `worn:LOOK` form.
Nothing of the Loader's changed; the game ran with no Loader attached.

**How:** `PT_NO_LOADER=1 PT_AFTER_PREPARE="python3 outfitgame.py '300=worn:Bone scale,305=worn:Cloak
and hood,308=worn:Robe'" sh loadsave.sh pens-after-arena` (the names have spaces: quote the list
inside the double quotes). Window 320x240. A grab standing, then two walks (to 70,130 and to
230,95) with grabs every 0.4 s.

**Seen:**
- Nothing broke: no clipping, misplacement or flicker; the pictures draw in the game's place.
- **Human man in bone scale**: the shoulder guards and the Bone Helm read at game size; he reads
  as armoured, the clearest change from his own look.
- **Half-giant in the robe**: unmistakably robed, but from the side the skirt is a stiff grey box
  with straight folds, and the feet are lost under it. It needs a softer hem (narrower at the back,
  the feet showing).
- **Elf woman in the hooded cloak**: the hood reads; from the side the cloak is thin.
- Kurzak (a half-giant with a picture of his own) is unchanged, as expected.
- The party reached each spot within the 0.4 s grabs' first second: most grabs show it standing.

**Not seen:** a fight's frames; the back view head-on; chain and leather in the game.

**Water:** no new area.
