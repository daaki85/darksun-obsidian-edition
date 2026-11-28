# voc.py 'GLOB': each Creative VOC file's rate, length, peak and RMS (dBFS); voc(path) its samples
import sys, struct, numpy as np, glob, os
def voc(path):
    d=open(path,'rb').read()
    off=struct.unpack('<H',d[20:22])[0]; i=off; out=[]; rates=set()
    while i<len(d):
        t=d[i]
        if t==0: break
        n=d[i+1]|d[i+2]<<8|d[i+3]<<16; b=d[i+4:i+4+n]
        if t==1:
            rates.add(1000000//(256-b[0])); assert b[1]==0, b[1]; out.append(np.frombuffer(b[2:],np.uint8))
        elif t==2: out.append(np.frombuffer(b,np.uint8))
        elif t==9:
            r,bits,ch,codec=struct.unpack('<IBBH',b[:8]); rates.add(r); out.append(np.frombuffer(b[12:],np.uint8))
        i+=4+n
    a=(np.concatenate(out).astype(float)-128)/128
    return a,rates
if __name__=='__main__':
    def stats(a):
        rms=np.sqrt(np.mean(a**2)); return 20*np.log10(np.max(np.abs(a))+1e-9),20*np.log10(rms+1e-9)
    rows=[]
    for p in sorted(glob.glob(sys.argv[1])):
        a,r=voc(p); pk,rm=stats(a); rows.append((os.path.basename(p),r,len(a),pk,rm))
    for r in rows: print(*r)
    pk=[r[3] for r in rows]; rm=[r[4] for r in rows]
    print('median peak',np.median(pk),'median rms',np.median(rm))
