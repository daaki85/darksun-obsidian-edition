# known.py MEMBER: the spells party member MEMBER knows (the known table, low four bits), by number and name
import os,sys;__file__=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'live.py');exec(open(__file__).read())
from dsloader import game, kits
m=int(sys.argv[1])
at=game.far_pointer(gd.guest, gd.ds, kits.KNOWN_SPELLS_PTR)+m*(game.SPELL_COUNT+1)
k=gd.guest.read(at, game.SPELL_COUNT+1)
print([ (s, gd.spell_name(s)) for s in range(len(k)) if k[s] & 0x0F])
