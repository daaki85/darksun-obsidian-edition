# ravds.py [--fuzzy] HEX...: Shattered Lands data-segment offsets to Wake of the Ravager's: for each SL
# instruction using the offset (mov/cmp/les/lea... [disp16], with or without a base register), the 12 code
# bytes before it are looked for once in WotR's DSUN.EXE and the word after them read there; with
# --fuzzy, where that fails, SL's 48 bytes round the use are scored against every place in WotR's (bytes
# alike) and the word read at the best place, if it is clearly best and the opcode before it is the same.
# The commonest answers printed. Found so far: 4979h (whose turn) -> 426Dh, 6694h (map objects) -> 67BBh,
# 117Ch (region) -> 140Ch; the far pointers SL 1665h/1661h/165Dh are WotR 19C9h/19C5h/19C1h.
import os, re, sys, collections
sl = open(os.path.join(os.environ.get('DS_GAME', '/tmp/playtest/inst'), 'DSUN.EXE'), 'rb').read()
rv = open(os.path.join(os.environ.get('RAV', '/tmp/playtest/rav'), 'DSUN.EXE'), 'rb').read()
args = [a for a in sys.argv[1:] if a != '--fuzzy']; fuzzy = '--fuzzy' in sys.argv
if fuzzy:
    import numpy as np
    RV = np.frombuffer(rv, np.uint8); W = 48; N = len(RV) - W


def uses(v):
    for m in re.finditer(re.escape(v.to_bytes(2, 'little')), sl):
        i = m.start()
        if (sl[i-1] & 0xC7) in (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87) or sl[i-1] in (0xA1, 0xA3) or \
           (sl[i-2] in (0x8B, 0x89, 0x3B, 0x39, 0x83, 0xFF, 0xC7, 0x80, 0x8A, 0x88, 0xF6, 0xC4, 0xC5, 0x03, 0x2B, 0x8D)
                and sl[i-1] in (0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E)):
            yield i


for h in args:
    v = int(h, 16); c = collections.Counter(); f = collections.Counter()
    for i in uses(v):
        pre = sl[i-12:i]; j = rv.find(pre)
        if j > 0 and rv.find(pre, j + 1) < 0:
            c[int.from_bytes(rv[j+12:j+14], 'little')] += 1
        elif fuzzy:
            a = i - W // 2; win = np.frombuffer(sl[a:a+W], np.uint8)
            eq = np.zeros(N + 1, np.int16)
            for k in range(W):
                if k not in (W // 2, W // 2 + 1):      # (the operand itself left out of the score)
                    eq += (RV[k:k+N+1] == win[k])
            b = int(eq.argmax()); s = int(eq[b]); eq[max(0, b-8):b+8] = 0
            at = b + W // 2
            if s >= 0.6 * W and s - int(eq.max()) >= 5 and rv[at-2:at] == sl[i-2:i]:
                f[int.from_bytes(rv[at:at+2], 'little')] += 1
    print('SL DS:%04X -> WotR' % v, [('%04X' % k, n) for k, n in c.most_common(3)],
          ('fuzzy ' + str([('%04X' % k, n) for k, n in f.most_common(3)])) if fuzzy else '')
