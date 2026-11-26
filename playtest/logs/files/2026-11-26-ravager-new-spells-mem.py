# 2026-11-26-ravager-new-spells-mem.py [CLEAR_RULES_HEX]: DSCLOG2's NEW SPELLS counters in the running sequel; with an argument, those bits of
# its rules word (header +170) cleared (a test: RULE_RESTRICT 2000h)
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
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
base = seg * 16
w = lambda n: struct.unpack('<H', g.read(base + sym[n], 2))[0]
print('rules %04X rules_hi %04X' % (w('rules'), w('rules_hi')))
for n in ('ns_cmps', 'ns_lost', 'ns_knows_n', 'ns_listed', 'ns_casts', 'ns_abilities', 'ns_claws', 'ns_swings', 'ns_spooks', 'ns_reflects') + tuple(a for a in os.environ.get('NS_SYMS', '').split(',') if a):
    print(n, w(n))
if len(sys.argv) > 1:
    r = w('rules') & ~int(sys.argv[1], 16); g.write(base + sym['rules'], struct.pack('<H', r)); print('rules now %04X' % w('rules'))
