# acs.py: each combatant's AC as the game counts it (gd.counted_ac), to hold against the dice log's "target AC"
import os, sys
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
for n in range(4): print(n, gd.creature_name(n), gd.counted_ac(n))
for i in sorted(set(gd.combatants().values())):
    if i >= 4: print(i, gd.creature_name(i), gd.counted_ac(i))
