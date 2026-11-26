# ravstore.py [roll|gear]: STORE and RECALL and the fuller starting gear in the running sequel ($WORK/rav.pid).
#   roll: the roll on the creation screen (the sheet being made, far DS:1429h: race, sex, classes, kit, its hit
#         points, rolled and most PSP; the creature, far DS:142Dh: HP, PSP and the six scores; the hit points'
#         most and least, DS:42D6h/42D8h) and DSCLOG2's RL_POOL, RS_HAVE and its STORE/RECALL counts (RS_CLICK,
#         site 83). Compare two prints: after RECALL every number is the STOREd one.
#   gear: DSCLOG2's GEAR_DUE, GEAR_GIVEN (+1830, +1831), LOADER_BEAT (+1865, and the BIOS timer now), GEAR_WHO
#         (+1867), its DONEs held and timed out (GEAR_DONE, site 85), and each party sheet's race and classes.
# Run from playtest/; reads only.
import argparse, os, struct, sys
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
sys.argv, cmd = sys.argv[:1], (sys.argv[1] if len(sys.argv) > 1 else 'roll')
import ravkits  # (its helper(): DSCLOG2's base and symbols; it connects to the DOSBox)
from dsloader import game, ravager
g = ravkits.g
ds = game.find_data_segment(g)
far = lambda o: (lambda a: a[1] * 16 + a[0])(struct.unpack('<HH', g.read(ds * 16 + o, 4)))
base, sym = ravkits.helper()
word = lambda name: struct.unpack('<H', g.read(base + sym[name], 2))[0]
if cmd == 'roll':
    s, c = g.read(far(0x1429), 0x48), g.read(far(0x142D), 0x31)
    print('sheet: race', s[0x12], 'sex', s[0x13], 'classes', list(s[0x1B:0x1E]), 'kit %#04x' % s[0x3D],
          'hp/rolled/psp', list(struct.unpack('<HHH', s[8:14])))
    print('creature: hp', struct.unpack('<H', c[0:2])[0], 'psp', struct.unpack('<H', c[2:4])[0],
          'scores', list(c[0x19:0x1F]), '| most/least hp', list(struct.unpack('<HH', g.read(ds * 16 + 0x42D6, 4))))
    print('rl_pool', word('rl_pool'), 'rs_have', g.read(base + sym['rs_have'], 1)[0],
          'rs_stores', word('rs_stores'), 'rs_recalls', word('rs_recalls'))
else:
    hdr = base + sym['hdr']
    beat, now = struct.unpack('<H', g.read(hdr + 1865, 2))[0], struct.unpack('<H', g.read(0x46C, 2))[0]
    print('gear_due', g.read(hdr + 1830, 1)[0], 'gear_given %#04x' % g.read(hdr + 1831, 1)[0],
          'gear_who', g.read(hdr + 1867, 1)[0], 'loader_beat', beat, '(timer %d: %d ticks old)' % (now, (now - beat) & 0xFFFF),
          'gear_holds', word('gear_holds'), 'gear_timeouts', word('gear_timeouts'))
    at = ravkits.sheets_at()
    for m in range(4):
        sh = g.read(at + m * ravager.SHEET_SIZE, ravager.SHEET_SIZE)
        print(m, 'race', sh[0x12], 'classes', list(sh[0x1B:0x1E]), 'kit %#04x' % sh[0x3D])
