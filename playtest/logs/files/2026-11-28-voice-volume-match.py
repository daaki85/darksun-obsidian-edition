# match.py RAW RATE T0 T1 'GLOB': the VOC files (GLOB) best matching a stretch of a raw 16-bit stereo recording, with the gain
import sys, glob, os, numpy as np
import importlib.util
_spec=importlib.util.spec_from_file_location('voc',os.path.join(os.path.dirname(os.path.abspath(__file__)),'2026-11-28-voice-volume-voc.py'))
_m=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m); voc=_m.voc
raw, rate, t0, t1 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
a=np.fromfile(raw,dtype='<i2').reshape(-1,2).astype(float).mean(1)/32768
seg=a[int(t0*rate):int(t1*rate)]
best=[]
for p in sorted(glob.glob(sys.argv[5])):
    v,r=voc(p); r=list(r)[0]
    if len(v)/r > (t1-t0): continue
    x=np.interp(np.arange(0,len(v)/r,1/rate), np.arange(len(v))/r, v)
    n=1<<int(np.ceil(np.log2(len(seg)+len(x))))
    c=np.fft.irfft(np.fft.rfft(seg,n)*np.conj(np.fft.rfft(x,n)),n)[:len(seg)-len(x)]
    k=int(np.argmax(np.abs(c))); y=seg[k:k+len(x)]
    g=np.dot(x,y)/np.dot(x,x); corr=np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)+1e-12)
    best.append((corr,os.path.basename(p),k/rate+t0,g,len(x)/rate))
best.sort(reverse=True)
for b in best[:4]: print('corr %.3f %s at %.2fs gain %.4f (%.1f dB) len %.1fs'%(b[0],b[1],b[2],b[3],20*np.log10(abs(b[3])+1e-9),b[4]))
