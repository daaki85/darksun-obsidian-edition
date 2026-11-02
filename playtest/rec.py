# rec.py [FIRST LAST]: the combat records (58 bytes) of creatures FIRST to LAST (default the party,
# 0-3), hex from +10h, to find a field by comparing what the screen shows
import sys, os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 3)
print(' ' * 11 + ' '.join(f'{i:02x}' for i in range(0x10, 0x3a)))
for i in range(a, b + 1):
    r = gd.creature(i); print(gd.creature_name(i)[:10].ljust(10), ' '.join(f'{x:02x}' for x in r[0x10:0x3a]))
