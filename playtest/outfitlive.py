# outfitlive.py MEMBER [classes=C1,C2,C3] [slot=SLOT]: checks the Loader's class outfit live: sets party member MEMBER's three class bytes (sheet +21h, the creation codes: 1 cleric, 6 druid, 9 fighter, 10 gladiator, 11 preserver, 12 psionicist, 13 ranger, 17 thief) and/or takes the item in SLOT off (slot byte 50) and puts it back,
# waits each time for the Loader to rewrite its copy of SEGOBJEX.GFF (obsidian-edition/dos/), and
# says whether that copy's walking and fighting pictures for the member's object are byte for byte
# what sprites.Pictures.build makes from the member's class outfit and worn gear. Memory edit:
# never save after; the class bytes are put back at the end unless KEEP=1.
# (logs/2026-11-23-elf-outfits-live.md)
import os, sys, struct, time
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import sprites, classoutfits, gff

m = int(sys.argv[1])
opts = dict(a.split('=', 1) for a in sys.argv[2:])
copy = os.path.join(REPO, 'obsidian-edition', 'dos', 'SEGOBJEX.GFF')
rec = gd.creature(m)
at = game.far_pointer(g, ds, 0x1661) + struct.unpack_from('<H', rec, 4)[0] * game.SHEET_SIZE
obj = struct.unpack_from('<H', rec, sprites.CREATURE_FIGURE)[0] + 300
src = gff.read_gff(open(os.path.join(GAME, 'SEGOBJEX.GFF'), 'rb').read())
# The Loader steadies outfit pixels against the portrait palette (spritegear.set_palette):
# without it the build here differs from the Loader's copy (2026-11-28, logs/2026-11-28-outfit-colours.md).
from dsloader import art, spritegear
spritegear.set_palette(list(art.palette_colours(
    gff.read_gff(open(os.path.join(GAME, 'GPLDATA.GFF'), 'rb').read())[('PAL ', 1)])))
pics = sprites.Pictures(src)


def written(before, wait=8.0):
    t0 = time.time()
    while os.stat(copy).st_mtime_ns == before and time.time() - t0 < wait:
        time.sleep(0.1)
    time.sleep(0.5)  # (the Loader writes both pictures)
    return os.stat(copy).st_mtime_ns != before


def check(tag, before):
    fresh = written(before)
    role = classoutfits.for_sheet(gd.sheet(m), pics.model(obj))
    chunks = gff.read_gff(open(copy, 'rb').read())
    gear = sprites.worn(gd, m, src)
    same = [chunks[('BMP ', pid)] == pics.build(obj, combat, gear[0], gear[1], pics.model(obj), obj, 0, role)
            for combat, pid in zip((False, True), sprites.picture_ids(obj))]
    print(f'{tag}: object {obj} role {role} gear {gear[0]} rewritten {fresh} walk/fight as built {same}',
          flush=True)


old = bytes(g.read(at + game.SHEET_CLASSES, 3))
try:
    if 'classes' in opts:
        before = os.stat(copy).st_mtime_ns
        g.write(at + game.SHEET_CLASSES, bytes(int(c) for c in opts['classes'].split(',')))
        check(f'classes {list(old)} -> {opts["classes"]}', before)
    if 'slot' in opts:
        slot = int(opts['slot'])
        items = game.far_pointer(g, ds, game.ITEMS_PTR)
        item = next(items + i * game.ITEM_SIZE for i, it, t in gd._worn(m) if it[game.ITEM_SLOT] == slot)
        for value, tag in ((50, f'slot {slot} off'), (slot, f'slot {slot} on')):
            before = os.stat(copy).st_mtime_ns
            g.write(item + game.ITEM_SLOT, bytes([value]))
            check(tag, before)
finally:
    if os.environ.get('KEEP') != '1' and bytes(g.read(at + game.SHEET_CLASSES, 3)) != old:
        before = os.stat(copy).st_mtime_ns
        g.write(at + game.SHEET_CLASSES, old)
        check('classes put back', before)
