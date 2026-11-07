# thingsfree.py [LABEL]: the game's dynamic things (objects 320-519, handed out from a free list):
# how many are free (the free list walked), the game's count out (DS:4C48h), and how many item lists
# the people on the map hold (worn, held, backpack), for people.py's cost. One line.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game, ring
it = ring.Items(gd)
free, seen, at = 0, set(), it.word(ring.FREE_THINGS)
while 0 <= at < ring.THING_COUNT and at not in seen:
    seen.add(at); free += 1; at = it.thing(at)[1] & 0xFFFF
used = it.word(ring.THINGS_USED)
lists = {0: 0, 1: 0, 2: 0}
people = 0
on_map = set(gd.combatants().values())
for index in range(game.PARTY_SIZE, 128):
    if index not in on_map:
        continue
    rec = gd.creature(index)
    if len(rec) < game.CREATURE_SIZE:
        continue
    held = [struct.unpack_from('<h', rec, o)[0] for o in game.CREATURE_ITEM_LISTS]
    if any(0 <= t < ring.THING_COUNT for t in held):
        people += 1
    for n, t in enumerate(held):
        if 0 <= t < ring.THING_COUNT:
            lists[n] += 1
print('%s free %d out %d | people with items %d: worn lists %d, held %d, pack %d | region %02X fight %d'
      % (sys.argv[1] if len(sys.argv) > 1 else '', free, used, people, lists[0], lists[1], lists[2],
         gd.region(), gd.fight_on()))
