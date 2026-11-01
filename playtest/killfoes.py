# killfoes.py: kill every foe in memory (aging.kill), not the arena's prisoners. ONLY for fights no
# script waits on: the game's scripts never see these deaths (in the arena no Announcer, no flag 11,
# no way out). For a story fight use fightout.sh. The fight still needs its turn ended.
import os, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
from dsloader import aging
for i in range(game.PARTY_SIZE, 40):
    rec = gd.creature(i)
    if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or "Prisoner" in gd.creature_name(i): continue
    if struct.unpack_from('<h', rec, 0)[0] > 0:
        aging.kill(gd, i); print("killed", gd.creature_name(i))
