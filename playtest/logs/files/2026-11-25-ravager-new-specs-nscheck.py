# nscheck.py: the running sequel's helper (DSCLOG2, the INT F5h vector's segment) against dos/DSCLOG2.EXE: the first
# 40 bytes of the routines and tables this branch changed, and the rules words (+170, +270).
import os, sys, struct, subprocess, tempfile, argparse
sys.path.insert(0, '/home/claude/wt-ravager-new-specs/obsidian-edition')
from dsloader.__main__ import connect
DOS = '/home/claude/wt-ravager-new-specs/obsidian-edition/dos'
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
with tempfile.TemporaryDirectory() as t:
    src, mp = os.path.join(t, 'm.asm'), os.path.join(t, 'm.map')
    open(src, 'w').write(f"[map symbols {mp}]\n" + open(os.path.join(DOS, 'dsclog2.asm')).read())
    subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', os.path.join(t, 'm.exe'), src], check=True)
    listing = open(mp).read()
sym = {}
for line in listing.split('Section image')[1].split('---- Section')[0].splitlines():
    p = line.split()
    if len(p) == 3:
        try: sym[p[2]] = int(p[1], 16)
        except ValueError: pass
exe = open(os.path.join(DOS, 'DSCLOG2.EXE'), 'rb').read(); image = exe[struct.unpack_from('<H', exe, 8)[0] * 16:]
print('helper at segment %04X' % seg)
for name in ('spec_get', 'spec_kind', 'spec_kinds_own', 'missile_rate', 'missile_halves', 'kind_of_type', 'large_dice',
             'class_forbids_one', 'kit_to_hit', 'ef_kinds', 'ef_lines_of'):
    a = sym[name]; same = g.read(seg * 16 + a, 40) == image[a:a + 40]
    print('%-18s %04X %s' % (name, a, 'same' if same else 'DIFFERS'))
kt = g.read(seg * 16 + sym['kind_of_type'], 135)
print('kind_of_type 35 38 39 43 59 61 100 101:', [kt[t] for t in (35, 38, 39, 43, 59, 61, 100, 101)])
print('rules %#06x rules_hi %#06x' % struct.unpack('<HH', g.read(seg * 16 + sym['hdr'] + 170, 2) + g.read(seg * 16 + sym['hdr'] + 270, 2)))
