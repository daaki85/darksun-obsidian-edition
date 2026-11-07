# shut.py: Pehtucl's chest (object 1568) given the shut type (pehtuclchest.SHUT_TYPE, 67h) in memory,
# as a new game makes it: the pens-new-chest save's chest was made before the shut type. Prints its
# item record's place and the chest's flags (DISARMED, UNLOCKED). Memory only: never save after.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game, pehtuclchest as c
at = c._chest(gd)
g.write(at + game.ITEM_TYPE, struct.pack('<H', c.SHUT_TYPE))
print('chest at', hex(at), 'type', hex(struct.unpack('<H', g.read(at + game.ITEM_TYPE, 2))[0]),
      'disarmed', gd.flag(c.DISARMED), 'unlocked', gd.flag(c.UNLOCKED))
