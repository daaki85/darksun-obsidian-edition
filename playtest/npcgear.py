# npcgear.py: every creature on the map now (the game's things that are creatures), with the items in
# its three lists: +08h worn, +0Ah held (what the Look box lists and the game fights with), +0Ch backpack.
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
held_any = []
seen = set()
for thing, creature in sorted(gd.combatants().items(), key=lambda kv: kv[1]):
    if creature in seen or creature < game.PARTY_SIZE:
        continue
    seen.add(creature)
    name = gd.creature_name(creature)
    lists = {}
    for off, label in zip(game.CREATURE_ITEM_LISTS, ('worn', 'held', 'pack')):
        items = []
        for _, item, typ in gd._worn(creature, (off,)):
            try:
                items.append(gd.item_label(item, typ))
            except Exception:
                items.append('?')
        lists[label] = items
    if any(lists.values()):
        print(f'{creature:3d} {name:18s} ' + '  '.join(f'{k}: {", ".join(v)}' for k, v in lists.items() if v))
    if lists['held']:
        held_any.append(name)
print(f'{len(seen)} creatures besides the party; holding something in hand: {held_any or "none"}')
