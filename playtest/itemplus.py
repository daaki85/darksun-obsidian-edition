# itemplus.py ITEM PLUS: item ITEM's (its number in the item table, carried.py's second column) plus
# byte (+14h) set: a plain piece made magic for a picture (docs/magic-glint.gif: Gerakis's leather
# pieces +2, the Loader dressing them with sparks). Memory only: never save after
# (logs/2026-11-27-outfit-screenshots.md).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
item, plus = int(args[0]), int(args[1])
at = game.far_pointer(g, ds, game.ITEMS_PTR) + item * game.ITEM_SIZE
print('was', g.read(at, game.ITEM_SIZE).hex(' '))
g.write(at + 0x14, bytes([plus]))
print('now', g.read(at, game.ITEM_SIZE).hex(' '))
