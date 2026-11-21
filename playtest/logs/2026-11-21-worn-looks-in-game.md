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
object is). **That save's party is not pens-after-arena's**: Lex (half-elf woman, 307: the robe), Jenna (human
woman, 301: leather), Ester (elf woman, 305: chain) and Seneca (halfling woman, 311: leather).
(Taken at first from the screen for a human man and others: `python3 -m dsloader save SAVE01.SAV`
lists a save's party.)

**Seen:**
- Chain with its coif reads clearly on Ester (elf woman); leather reads on Jenna; Lex's robe
  reads, slim on her.
- The fight: Seneca walked up to Pehtucl and was seen from behind (the back view) in her fight
  stance, in leather: readable, nothing misplaced.
- **With no Loader attached, Tab + Return does not attack**: Tab's nearest-enemy pick is the
  Loader's, so Return opens the game's menu (and fightout.sh's E then the Effects screen). Escape
  closes it (a screen is up). Attack by clicking the foe (click.py at the foe's screen point).

**Not seen:** a swing caught mid-frame (the grabs at 0.15 s showed the stance), the bone scale and
the cloak in this fight.

## Round 5: bone scale and the cloak in the fight (same day)

`'301=worn:Cloak and hood,307=worn:Bone scale'` (Ester and Seneca left in their own clothes).
Lex in bone scale walked up to Pehtucl: from the front the shoulder guards, the helm and the
scales read clearly next to him; Jenna's hooded cloak reads from the side, a little wide at the hem.
A mid-swing frame was not caught: ffmpeg's x11grab at 20-30 frames a second recorded the walks, but
the clicks on Pehtucl opened END <NAME>'S MOVE (a click on the member's own figure under him) or
walked without striking, and E then opened the Effects screen. The swing frames are the game's own
attack pictures dressed, as on the sheets; seeing one drawn needs the Loader's Tab targeting or a
foe clicked clear of the member.
