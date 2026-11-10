# outfitcycle.py MEMBER SLOT N [SECONDS]: changes MEMBER's outfit N times, as fillcache.py does (the
# slot byte, +11h, of the item it has in SLOT set to 50, no place, and back), waiting each time for
# the Loader to dress the figure (its copy of SEGOBJEX.GFF written: obsidian-edition/dos/, beside
# this kit; at most SECONDS, default 4), then prints the game's picture slots taken (DS:1F84h), the
# STALE (FFFEh) ones, the store's end (the last slot's place + length, of 741,376), the member's
# walking and fighting pictures' slots (in memory or not) and whether its figure is drawn (map
# thing +0 bit 80h clear). Unlike fillcache.py it doesn't need the slots to grow: with the
# picture store's cells reused (2026-11-09, logs/2026-11-09-picture-store.md) they shouldn't. Ends
# with the slot byte as it was. Memory edit: never save after.
import os, sys, struct, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game, sprites
m, slot, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
wait = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
copy = os.path.join(PT, '..', 'obsidian-edition', 'dos', 'SEGOBJEX.GFF')
items = game.far_pointer(g, ds, game.ITEMS_PTR)
at = next(items + i * game.ITEM_SIZE for i, item, t in gd._worn(m) if item[game.ITEM_SLOT] == slot)
fig = struct.unpack_from('<H', gd.creature(m), sprites.CREATURE_FIGURE)[0] + 300


def table():
    count = struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
    tab = g.read((gd.load_seg + 0x3E60) * 16, min(count, 300) * 16)
    return count, [struct.unpack_from('<HIiIBB', tab, k * 16) for k in range(min(count, 300))]


def line(i):
    count, ents = table()
    stale = sum(1 for e in ents if e[0] == 0xFFFE)
    end = ents[-1][2] + ents[-1][1] if ents else 0
    walk, fight = sprites.picture_ids(fig)
    mine = [(k, 'mem' if e[4] & 2 else '-') for k, e in enumerate(ents) if e[0] in (walk, fight)]
    drawn = [not g.read(ds * 16 + sprites.MAP_ENTRIES + c * 32, 1)[0] & 0x80
             for c, cr in gd.combatants().items() if cr == m]
    print(i, 'slots', count, 'stale', stale, 'store end', end, 'its pictures', mine, 'drawn', drawn, flush=True)


line('start')
try:
    for i in range(1, n + 1):
        before = os.stat(copy).st_mtime_ns
        g.write(at + game.ITEM_SLOT, bytes([50 if i % 2 else slot]))
        t0 = time.time()
        while os.stat(copy).st_mtime_ns == before and time.time() - t0 < wait:
            time.sleep(0.05)
        time.sleep(0.4)  # (the game loads and draws it)
        line(i if os.stat(copy).st_mtime_ns != before else f'{i} (not dressed)')
finally:
    g.write(at + game.ITEM_SLOT, bytes([slot]))
