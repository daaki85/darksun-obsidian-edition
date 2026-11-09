# drawlist.py [all]: the game's draw list (far pointer DS:6690h, count DS:1F72h; 8 bytes an entry:
# x, y, height, flags, thing; kept in rising y: the drawing's and the clicks' window, DS:57CAh
# to 57C8h, is found by a scan that stops at the first y past the view) and whether each party member's thing (0-3) is in it, with its map
# place (DS:669Dh + 32n) and screen place. "all" prints every entry.
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x6690, 4))
n = struct.unpack('<H', g.read(ds * 16 + 0x1F72, 2))[0]
raw = g.read(seg * 16 + off, 8 * min(n, 600)) if n else b''
ents = [struct.unpack('<hhBBH', raw[i * 8:i * 8 + 8]) for i in range(len(raw) // 8)]
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
out = [f'list {seg:04X}:{off:04X} count {n} camera {cx},{cy}']
for m in range(4):
    x, y = struct.unpack('<hh', g.read(ds * 16 + 0x669D + m * 32, 4))
    e = [en for en in ents if en[4] == m]
    out.append(f'member {m} map {x},{y} screen {x - cx},{y - cy} in list: ' +
               (', '.join(f'({a},{b} h{c} f{d:02X})' for a, b, c, d, _ in e) if e else 'NO'))
inv = [(i, ents[i - 1], ents[i]) for i in range(1, len(ents)) if ents[i][1] < ents[i - 1][1]]
w0, w1 = struct.unpack('<HH', g.read(ds * 16 + 0x57C8, 4))
out.append(f'window: first {w1} end {w0}; out of order (y falls): {len(inv)}')
out += [f'  at {i}: {a} then {b}' for i, a, b in inv[:12]]
if sys.argv[1:] == ['all']:
    out += [f'  {i}: {e}' for i, e in enumerate(ents)]
print('\n'.join(out))
