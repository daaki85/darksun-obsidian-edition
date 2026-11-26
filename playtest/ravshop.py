# ravshop.py CMD ...: Wake of the Ravager's shops and scrolls for a test (run from playtest/; the running
# sequel, $WORK/rav.pid). CMD: `party` (each member's CHA, INT and items: number, entity, type, price,
# slot, power, plus, name word), `cha M N` (member M's CHA N: a test edit, never saved), `shop` (the
# shop's merchant thing DS:1A30h, the pointer's thing DS:1A32h and its slot DS:1A34h, the shop's own
# buy and sell adjustments 370h:36h/34h, the party's money; the merchant's items), `thing T` (a
# thing's kind and first item, and its list), `scroll M ITEM SPELL` (item record ITEM made a wizard
# scroll of SPELL, copied from a real scroll's record, item 58 in ravager-after-ambush: a test edit),
# `int M N` (member M's INT N), `known M` (member M's known wizard spells), `forget M SPELL`,
# `teach M SPELL`, `slot ITEM N` (its slot byte), `helper` (DSCLOG2's header: rules, rules_hi, the learn fields +272..+279).
# Records: creatures 31h bytes at the far DS:19C9h (CHA +1Eh, INT +1Ch, the item lists +08h/+0Ah/+0Ch),
# items 17h at DS:19C1h (+04h the next, +06h the price, +0Ah the type, +10h the power, +13h the slot,
# +14h the name, +16h the plus), things 3 bytes at (load + 3F49h):0C33h (a kind byte: 1 items, 2 a
# creature; then the first item or the creature).
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
load = ds - 0x47E0
w = lambda a: struct.unpack('<H', g.read(a, 2))[0]
far = lambda off: (lambda o, s: s * 16 + o)(*struct.unpack('<HH', g.read(ds * 16 + off, 4)))
CRE, ITM = far(0x19C9), far(0x19C1)
THINGS = (load + 0x3F49) * 16 + 0x0C33
KNOWN = (load + 0x3D62) * 16 + 0x39C
def creature(n): return CRE + n * 0x31
def item(n): return ITM + n * 0x17
def thing(t): return struct.unpack('<Bh', g.read(THINGS + t * 3, 3))
def chain(first, most=60):
    out = []
    while 0 <= first < 0x270F and len(out) < most and first not in out:
        out.append(first); first = struct.unpack('<h', g.read(item(first) + 4, 2))[0]
    return out
def show_item(n):
    r = g.read(item(n), 0x17)
    ent, price, typ = struct.unpack_from('<h', r, 0)[0], struct.unpack_from('<H', r, 6)[0], struct.unpack_from('<H', r, 0x0A)[0]
    return ('item %d: entity %d count %d price %d type %d charges %d power %d slot %d name %d plus %d next %d'
            % (n, ent, r[2], price, typ, r[0x0E], struct.unpack_from('<H', r, 0x10)[0], r[0x13],
               struct.unpack_from('<H', r, 0x14)[0], struct.unpack_from('b', r, 0x16)[0],
               struct.unpack_from('<h', r, 4)[0]))
def lists(cr):
    return [struct.unpack('<h', g.read(cr + o, 2))[0] for o in (8, 0x0A, 0x0C)]
def items_of(cr):
    for t in lists(cr):
        if 0 <= t < 0x270F:
            k, f = thing(t)
            print('  list thing %d kind %d' % (t, k))
            if k == 1:
                for i in chain(f): print('   ', show_item(i))
cmd = sys.argv[1]; a = [int(x, 0) for x in sys.argv[2:]]
if cmd == 'party':
    for m in range(4):
        cr = creature(m); r = g.read(cr, 0x31)
        print('member %d %s CHA %d INT %d lists %s' % (m, r[0x21:0x31].split(b'\0')[0].decode('latin1'), r[0x1E], r[0x1C], lists(cr)))
        items_of(cr)
    print('whose turn (leader)', w(ds * 16 + 0x426D))
elif cmd == 'cha':
    g.write(creature(a[0]) + 0x1E, bytes([a[1]])); print('CHA', g.read(creature(a[0]) + 0x1E, 1)[0])
elif cmd == 'int':
    g.write(creature(a[0]) + 0x1C, bytes([a[1]])); print('INT', g.read(creature(a[0]) + 0x1C, 1)[0])
elif cmd == 'shop':
    m, p, s = w(ds * 16 + 0x1A30), w(ds * 16 + 0x1A32), w(ds * 16 + 0x1A34)
    s370 = (load + 0x3E71) * 16
    print('merchant thing %d pointer thing %d pointer slot %d; adjust buy %d sell %d; money %d' % (
        m, p, s, struct.unpack('<h', g.read(s370 + 0x36, 2))[0], struct.unpack('<h', g.read(s370 + 0x34, 2))[0],
        struct.unpack('<I', g.read((load + 0x41C9) * 16 + 0x357, 4))[0] if False else -1))
    for t in (m, p):
        if 0 <= t < 0x270F:
            k, f = thing(t); print('thing %d kind %d first %d' % (t, k, f))
            if k == 2: items_of(creature(f))
            if k == 1:
                for i in chain(f): print('   ', show_item(i))
elif cmd == 'thing':
    k, f = thing(a[0]); print('thing %d kind %d first %d' % (a[0], k, f))
    if k == 1:
        for i in chain(f): print('   ', show_item(i))
    if k == 2: items_of(creature(f))
elif cmd == 'slot':   # item, slot
    g.write(item(a[0]) + 0x13, bytes([a[1]])); print(show_item(a[0]))
elif cmd == 'item':
    print(show_item(a[0]))
elif cmd == 'scroll':   # member, item, spell
    src = bytearray(g.read(item(58), 0x17)); dst = bytearray(g.read(item(a[1]), 0x17))
    dst[0:2] = src[0:2]; dst[0x0A:0x0C] = src[0x0A:0x0C]; dst[0x14:0x16] = src[0x14:0x16]; dst[0x0E] = src[0x0E]
    struct.pack_into('<H', dst, 0x10, a[2] + 1); struct.pack_into('<H', dst, 2, a[2] + 1) if False else None
    g.write(item(a[1]), bytes(dst)); print(show_item(a[1]))
elif cmd in ('known', 'forget', 'teach'):
    at = KNOWN + 15 * a[0]; b = bytearray(g.read(at, 15))
    if cmd == 'forget': b[a[1] // 8] &= ~(1 << a[1] % 8) & 0xFF; g.write(at, bytes(b))
    if cmd == 'teach': b[a[1] // 8] |= 1 << a[1] % 8; g.write(at, bytes(b))
    print('known', [i for i in range(120) if b[i // 8] >> (i % 8) & 1])
elif cmd == 'helper':   # DSCLOG2's rules words, the learn fields (+272) and the shops' and messages' counters
    import subprocess, tempfile
    DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
    base = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0] * 16
    with tempfile.TemporaryDirectory() as t:
        src, mp = os.path.join(t, 'm.asm'), os.path.join(t, 'm.map')
        open(src, 'w').write(f"[map symbols {mp}]\n" + open(os.path.join(DOS, 'dsclog2.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', os.path.join(t, 'm.exe'), src], check=True)
        sym = {}
        for line in open(mp).read().split('Section image')[1].split('---- Section')[0].splitlines():
            q = line.split()
            if len(q) == 3:
                try: sym[q[2]] = int(q[1], 16)
                except ValueError: pass
    hdr = base + sym['hdr']
    print('rules %#06x rules_hi %#06x learn %s' % (w(hdr + 170), w(hdr + 270), g.read(hdr + 272, 8).hex()))
    print(' '.join('%s=%d' % (n, w(base + sym[n])) for n in ('cha_prices', 'sold_kept', 'msg_windows', 'msg_waits', 'learnt_tries')))
