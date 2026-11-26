"""outfitgame.py OBJECT=OUTFIT[,...]: the outfit prototype's pictures (prototypes/outfits.py) put
into the Loader's copy of SEGOBJEX.GFF, to look at them in the game. A test tool: nothing of the
Loader's is changed, and the copy is written afresh at the next start.

A party member's figure is object 300 + the figure picked at creation (the Loader's copy gives
each its own pair of pictures: sprites.picture_ids). OBJECT=OUTFIT replaces that object's walking
and fighting pictures with the outfit's (Warrior, Thief, Priest, Mage; `all=Mage` for every one;
`preset:Mage` for the gear-system preset of prototypes/presets.py instead; `worn:Bone scale` for
a look by what's worn, prototypes/wornlooks.py: Robe, Leather, Bone scale, Chain, Cloak and hood),
corrections by hand laid on, and the game's own pictures of that figure
with them (with no Loader attached the game draws those: everyone of that figure wears the outfit). Run it between the Loader writing its copies and DOSBox opening
them, and with no Loader attached (it would dress the figures again):

    PT_NO_LOADER=1 PT_AFTER_PREPARE="python3 outfitgame.py 300=Mage,305=Thief,308=Priest" sh loadsave.sh pens-after-arena

Each picture keeps the outfit's room round the figure's own (8 pixels each side and above; 4
above when walking), and nothing under its feet (the game stands a picture on its bottom edge).
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prototypes"))
sys.path.insert(0, os.path.join(HERE, "..", "obsidian-edition"))

import outfits as O  # noqa: E402
from dsloader import gff, halfelf, icons, launch, sprites  # noqa: E402
from paths import GAME  # noqa: E402


def key_of(game: O.Game, obj: int):
    """The figure an object is drawn as: one of the game's models, or a half-elf's."""
    if obj == halfelf.MAN:
        return O.HALF_ELF_MAN
    if obj == halfelf.WOMAN:
        return O.HALF_ELF_WOMAN
    rec = game.chunks.get(("OJFF", obj))
    model = struct.unpack_from("<H", rec, sprites.OJFF_PICTURE)[0] if rec else None
    return model if model in dict(O.FIGURES) else None


def main(argv):
    want = dict(a.split("=") for a in argv[0].split(","))
    if "all" in want:
        want = {str(o): want["all"] for o in sprites.PARTY_OBJECTS}
    game = O.Game(GAME)
    npcs = {o.name.lower(): n for n, o in O.OUTFITS.items()}
    dest = os.path.join(launch.DOS_DIR, "SEGOBJEX.GFF")
    with open(dest, "rb") as f:
        data = f.read()
    added, lost = {}, 0
    for obj, outfit in want.items():
        obj = int(obj)
        key = key_of(game, obj)
        if key is None:
            print(f"object {obj}: no figure to dress (a thri-kreen, or not in the game)")
            continue
        if outfit.lower().startswith("preset:"):  # (the gear's own drawing in a class's colours: prototypes/presets.py)
            import presets
            name = outfit.split(":")[1].lower()
            i = next(n for n, p in enumerate(presets.PRESETS) if p.name.lower() == name)
            pics = sprites.Pictures(game.chunks)
            for k, chunk in enumerate(presets.pictures(pics, obj, i)):
                added[("BMP ", sprites.picture_ids(obj)[k])] = chunk
                if isinstance(key, int):
                    added[("BMP ", key + k)] = chunk
            print(f"object {obj}: {dict(O.FIGURES)[key]} in the {name} preset")
            continue
        if outfit.lower().startswith("worn:"):  # (a look by what's worn: prototypes/wornlooks.py)
            import wornlooks
            name = outfit.split(":", 1)[1].lower()
            look = next(o for n, o in wornlooks.LOOKS.items() if n.lower() == name)
            worn = getattr(main, "worn", None) or wornlooks.WornGame(GAME)
            main.worn = worn
            walk, fight = worn.full(key, look.npc, fixed=False)
        else:
            walk, fight = game.full(key, npcs[outfit.lower()])
        for k, (pid, frames, top) in enumerate(zip(sprites.picture_ids(obj), (walk, fight), (4, 0))):
            out = []
            for rows, ox, oy, own in frames:
                lost += sum(c is not None for r in rows[len(own) - oy:] for c in r)
                out.append([list(r) for r in rows[top:len(own) - oy]])
            added[("BMP ", pid)] = sprites.encode_frames(out)
            if isinstance(key, int):  # (and the game's own picture of that figure, which a game
                added[("BMP ", key + k)] = added[("BMP ", pid)]  # with no Loader attached draws)
        print(f"object {obj}: {dict(O.FIGURES)[key]} as {outfit} (pictures {sprites.picture_ids(obj)})")
    gff.write_atomic(dest, icons.with_chunks(data, added))
    print(f"written to {dest}; {lost} pixels under the feet left off")


if __name__ == "__main__":
    main(sys.argv[1:])
