# figwatch.py SECONDS [EVERY] [TAG]: passive watch for the party's figures (no writes): every EVERY
# seconds a window grab, the camera, each member's screen place and whether its thing is in the
# draw list (its index, and OUTWIN when outside the last drawing's window, DS:57CAh-57C8h; inv: how
# often y falls along; stale: entries whose thing's +1 isn't their index; b0 the thing's +0, 80h not
# drawn; sN=P/F its picture slot (+0Fh), that cache entry's picture number and flags (+0Eh: 2 in
# memory), pP its picture (+18h); the list); the boxes round the four members (24 x 48 grab pixels) cut out and kept in a strip,
# $WORK/fw-TAG-N.png (N the sample), for a montage. One line a sample to stdout.
import os, sys, struct, subprocess, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from PIL import Image, ImageDraw
secs = float(sys.argv[1]); every = float(sys.argv[2]) if len(sys.argv) > 2 else 3
tag = sys.argv[3] if len(sys.argv) > 3 else 'w'
W = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
end = time.time() + secs; n = 0
while time.time() < end:
    p = f'{WORK}/fw-{tag}-full.png'
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    subprocess.run(['import', '-window', W, p], check=True)
    im = Image.open(p).convert('RGB')
    off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x6690, 4))
    cnt = struct.unpack('<H', g.read(ds * 16 + 0x1F72, 2))[0]
    raw = g.read(seg * 16 + off, 8 * min(cnt, 600))
    things = {struct.unpack('<H', raw[i + 6:i + 8])[0] for i in range(0, len(raw), 8)}
    ys = [struct.unpack('<h', raw[i + 2:i + 4])[0] for i in range(0, len(raw), 8)]
    inv = sum(1 for i in range(1, len(ys)) if ys[i] < ys[i - 1])
    w0, w1 = struct.unpack('<HH', g.read(ds * 16 + 0x57C8, 4))
    stale = 0
    for i in range(0, len(raw), 8):
        t = struct.unpack('<H', raw[i + 6:i + 8])[0]
        if t < 520 and struct.unpack('<H', g.read(ds * 16 + 0x6694 + t * 32 + 1, 2))[0] != i // 8: stale += 1
    idx = {struct.unpack('<H', raw[i + 6:i + 8])[0]: i // 8 for i in range(0, len(raw), 8)}
    strip = Image.new('RGB', (4 * 26, 50), (255, 0, 255)); parts = []
    for m in range(4):
        x, y = struct.unpack('<hh', g.read(ds * 16 + 0x669D + m * 32, 4))
        sx, sy = x - cx, y - cy
        box = (sx - 12, int((sy - 40) * 1.2), sx + 12, int((sy - 40) * 1.2) + 48)
        strip.paste(im.crop(box), (m * 26, 1))
        mt = g.read(ds * 16 + 0x6694 + m * 32, 32)
        bi = struct.unpack('<H', mt[1:3])[0]
        slot, pic = struct.unpack('<H', mt[0x0F:0x11]), struct.unpack('<H', mt[0x18:0x1A])[0]
        slot = slot[0]
        ce = g.read((gd.load_seg + 0x3E60) * 16 + slot * 16, 16) if slot < 300 else b''
        cs = f' s{slot}' + (f'={struct.unpack("<H", ce[0:2])[0]}/{ce[0x0E]:02X}' if ce else '') + f' p{pic}'
        parts.append(f'm{m} {sx},{sy} b0={mt[0]:02X}{cs}' + ('' if idx.get(m) == bi else f' +1={bi}!') + (f' #{idx[m]}' if m in idx else ' NOTLISTED') + (' OUTWIN' if m in idx and not w1 <= idx[m] < w0 else ''))
    strip.save(f'{WORK}/fw-{tag}-{n:03d}.png')
    st = subprocess.run(['python3', os.path.join(PT, 'state.py')], capture_output=True, text=True).stdout.strip()
    print(f'{time.strftime("%T")} {n} cam {cx},{cy} count {cnt} win {w1}-{w0} inv {inv} stale {stale} | ' + ' | '.join(parts) + ' | ' + st, flush=True)
    n += 1; time.sleep(every)
