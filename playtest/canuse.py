# canuse.py MEMBER TYPE...: whether the kit rules (restrict.kit_forbids) let party member MEMBER use each item type, and pick it as a weapon spec
import os,sys;__file__=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'live.py');exec(open(__file__).read())
from dsloader import game, restrict
game.RULES_IN_FORCE = game.RULE_KITS | game.RULE_RESTRICT | game.RULE_SPECIALIZE | game.RULE_HALF_GIANT
m=int(sys.argv[1]); s=gd.sheet(m)
types=game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
rd=lambda t: gd.guest.read(types+t*game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
for t in map(int, sys.argv[2:]):
    print(t, 'kit forbids' if restrict.kit_forbids(s, t, rd(t)) else 'allowed', '| as a spec pick:', 'forbidden' if restrict.kit_forbids(s, t, rd(t), spec=True) else 'allowed')
