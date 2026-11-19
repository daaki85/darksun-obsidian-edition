# ravds.py HEX...: Shattered Lands data-segment offsets to Wake of the Ravager's: for each SL instruction
# using the offset (mov/cmp/les... [disp16], with or without a base register), the 12 code bytes before it
# are looked for once in WotR's DSUN.EXE, and the word after them read there; the commonest answers
# printed. Found so far: 4979h (whose turn) -> 426Dh, 6694h (map objects) -> 67BBh. Misses where the
# code before differs (the far pointers: SL 1665h/1661h/165Dh are WotR 19C9h/19C5h/19C1h).
import os, re, sys, collections
sl=open(os.path.join(os.environ.get('DS_GAME', '/tmp/playtest/inst'), 'DSUN.EXE'),'rb').read(); rv=open(os.path.join(os.environ.get('RAV', '/tmp/playtest/rav'), 'DSUN.EXE'),'rb').read()
for h in sys.argv[1:]:
    v=int(h,16); c=collections.Counter()
    for m in re.finditer(re.escape(v.to_bytes(2,'little')), sl):
        i=m.start()
        if not ((sl[i-1] & 0xC7) in (0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87) or sl[i-1] in (0xA1,0xA3) or (sl[i-2] in (0x8B,0x89,0x3B,0x39,0x83,0xFF,0xC7,0x80,0x8A,0x88,0xF6,0xC4,0xC5,0x03,0x2B) and sl[i-1] in (0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E))): continue
        pre=sl[i-12:i]; j=rv.find(pre)
        if j>0 and rv.find(pre,j+1)<0: c[int.from_bytes(rv[j+12:j+14],'little')]+=1
    print('SL DS:%04X -> WotR' % v, [('%04X' % k, n) for k, n in c.most_common(3)])
