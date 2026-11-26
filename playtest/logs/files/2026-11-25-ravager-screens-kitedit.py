# 2026-11-25-ravager-screens-kitedit.py set|restore: a test edit (never saved): Ester's (member 2) kit byte +3Dh 1 (Battle Dancer) and
# four specs (long sword, short sword, bow, mace, packed base 17 as SPEC_V2 keeps them at +42h..+44h), and RULE_HI_KITS (1) in DSCLOG2's rules_hi (header +270).
import sys, struct, argparse, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None)); ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C5, 4)); sheet = seg*16 + off + 2*0x48
mem = g.read(0, 0x110000); hdr = mem.find(b'DSCLOGR1')
while hdr % 16: hdr = mem.find(b'DSCLOGR1', hdr + 1)
keep = '/tmp/playtest/kitedit.json'
if sys.argv[1] == 'set':
    old = {'kit': g.read(sheet+0x3D,1).hex(), 'spec': g.read(sheet+0x42,4).hex(), 'hi': g.read(hdr+270,2).hex()}
    json.dump(old, open(keep,'w')); print('was', old)
    g.write(sheet+0x3D, b'\x01'); orig = int.from_bytes(bytes.fromhex(old['spec'])[:3], 'little'); new = (orig & ~0x1FFFF) | (1 + 4*17 + 14*289 + 5*4913); g.write(sheet+0x42, new.to_bytes(3, 'little'))
    hi, = struct.unpack('<H', g.read(hdr+270,2)); g.write(hdr+270, struct.pack('<H', hi | 1))
else:
    old = json.load(open(keep)); g.write(sheet+0x3D, bytes.fromhex(old['kit'])); g.write(sheet+0x42, bytes.fromhex(old['spec']))
    g.write(hdr+270, bytes.fromhex(old['hi'])); print('restored', old)
print('now', g.read(sheet+0x3D,1).hex(), g.read(sheet+0x42,4).hex(), g.read(hdr+270,2).hex())
