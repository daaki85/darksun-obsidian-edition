# setitem.py ITEM TYPE: makes item ITEM (its number in the item table) a plain item of type TYPE in
# memory. It takes the game's first plain record of that type from SEGOBJEX.GFF, keeping the item's
# link (+4), flags (+10h) and slot (+11h); +08h 270Fh, +0Ch cleared. Memory only: never save after. Write it with
# the inventory closed (logs/2026-11-10-stinkpots.md: Lex's bow, item 36, made a staff sling, type 0).
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game, gff, champions
item, kind = int(sys.argv[1], 0), int(sys.argv[2], 0)
chunks = gff.read_gff(open(os.path.join(GAME, 'SEGOBJEX.GFF'), 'rb').read())
rec = champions.game_item(chunks, kind)
if rec is None:
    print('no plain item of type', kind, 'in SEGOBJEX.GFF'); sys.exit(1)
at = game.far_pointer(g, ds, game.ITEMS_PTR) + item * game.ITEM_SIZE
old = g.read(at, game.ITEM_SIZE)
new = bytearray(rec)
new[game.ITEM_NEXT:game.ITEM_NEXT + 2] = old[game.ITEM_NEXT:game.ITEM_NEXT + 2]
new[0x10:0x12] = old[0x10:0x12]                      # flags and slot
new[8:10] = struct.pack('<H', game.NO_ITEM)          # no contents (the file's 0 names item 0 in memory)
new[0x0C:0x0E] = bytes(2)                            # the icon the game last drew
g.write(at, bytes(new))
print(f'item {item} at {at:X}: type {struct.unpack_from("<H", old, game.ITEM_TYPE)[0]} -> {kind}')
print('was', old.hex(' '))
print('now', g.read(at, game.ITEM_SIZE).hex(' '))
