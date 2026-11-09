# slotcount.py [LABEL]: one line: the leader's place, the game's picture slots taken (of 300) and the
# store's end (of 741,376), for watching how a region fills the table (2026-11-09).
import sys, struct
PLAYTEST='/home/user/darksun-obsidian-edition/playtest'; sys.path.insert(0,PLAYTEST); __file__=PLAYTEST+'/live.py'
exec(open(PLAYTEST+'/live.py').read())
n = struct.unpack('<H', g.read(ds*16+0x1F84, 2))[0]
tab = g.read((gd.load_seg+0x3E60)*16, n*16)
ents = [struct.unpack_from('<HIiIBB', tab, k*16) for k in range(n)]
end = max(e[2]+e[1] for e in ents if e[2] >= 0)
x, y = struct.unpack('<hh', g.read(ds*16+0x669D, 4))
print(f'{sys.argv[1] if len(sys.argv)>1 else ""}: leader {x},{y} slots {n} store end {end} ({end*100//741376}%)')
