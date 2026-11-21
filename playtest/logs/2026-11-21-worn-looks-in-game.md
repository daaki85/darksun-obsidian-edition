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

## Round 4: the softer robe, a fight, chain and leather (same day)

**Changed first:** the robe's hem softer (feet showing, corners rounded, a broken hem line, folds on
its lower part only), from the side flaring in front and nearly straight at the back; the cloak
fuller behind the back from the side. The game's side frames all face right (it mirrors them), so
the back is to the left: reading it from the hair failed on the half-giant.

**How:** `fountain-user` (Pehtucl's ambush), every party object given a look
(`'300=worn:Chain,301=worn:Leather,...,312=worn:Robe'`: outfitgame.py prints which figure each
object is). **That save's party is not pens-after-arena's**: Seneca (a halfling man in leather),
a human man (chain), a human woman (leather) and a half-elf woman (robe).

**Seen:**
- Chain with its coif reads clearly as a mail-clad man; leather reads on the human woman; the
  half-elf woman's robe reads, slim on her.
- The fight: Seneca walked up to Pehtucl and was seen from behind (the back view) in his fight
  stance, in leather: readable, nothing misplaced.
- **With no Loader attached, Tab + Return does not attack**: Tab's nearest-enemy pick is the
  Loader's, so Return opens the game's menu (and fightout.sh's E then the Effects screen). Escape
  closes it (a screen is up). Attack by clicking the foe (click.py at the foe's screen point).

**Not seen:** a swing caught mid-frame (the grabs at 0.15 s showed the stance), the bone scale and
the cloak in this fight.
