# The callers of Wake of the Ravager routines at file offsets (argv, hex): far calls through the routine's overlay stub
# (by its segment or a selector naming it) and "push cs / call" inside its overlay. Reads $WORK/rav/DSUN.EXE
# and $WORK/ravimg/layout.json (RESEARCH.md, Wake of the Ravager).
import re,struct,json,sys
d=open('/tmp/playtest/rav/DSUN.EXE','rb').read()
j=json.load(open('/tmp/playtest/ravimg/layout.json'))
base=0x45E8*16+0x5200
def mod(x):
    for m in j['modules']:
      if m['file']<=x<m['file']+m['size']: return m['index']
    return 'res'
def callers(target):
    out=[]
    for m in j['modules']:
        for s in m['stubs']:
            if m['file']+s['entry']==target:
                seg=m['stub_seg']-418
                sels=[sel for sel in range(0,0x1000,8) if struct.unpack_from('<H',d,base+sel)[0]==seg]
                for v in [seg]+sels:
                    for h in re.finditer(re.escape(b'\x9a'+struct.pack('<HH',s['stub_off'],v)),d):
                        out.append((hex(h.start()),mod(h.start()),hex(v)))
                # internal
                lo,hi=m['file']-16,m['file']+m['size']
                for i in range(lo,hi):
                    if d[i]==0xE8 and d[i-1]==0x0e and i+3+struct.unpack_from('<h',d,i+1)[0]==target:
                        out.append((hex(i),'near'))
    return out
for t in sys.argv[1:]:
    print(t, callers(int(t,16)))
