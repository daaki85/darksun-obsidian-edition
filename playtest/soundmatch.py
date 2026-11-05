# soundmatch.py RAW START END WAV...: in DOSBox's recorded output (RAW: 16-bit stereo at 44100 Hz,
# from start.sh with PT_AUDIO set; START and END byte offsets, e.g. the file's size before and after
# the sound was asked for), the loudest sample and how well each 8000 Hz 8-bit WAV matches (the best
# normalised correlation: about 1.0 when it is the one played). Needs numpy (python3.13).
import sys, wave
import numpy as np
raw = np.memmap(sys.argv[1], dtype='<i2', mode='r')
start, end = int(sys.argv[2]), int(sys.argv[3])
x = np.asarray(raw[start // 2:end // 2], float).reshape(-1, 2).mean(1)
print('peak', int(np.abs(x).max()))
for path in sys.argv[4:]:
    with wave.open(path) as w:
        c = np.frombuffer(w.readframes(w.getnframes()), np.uint8).astype(float) - 128
    c = np.interp(np.arange(0, len(c), 8000 / 44100), np.arange(len(c)), c)
    if len(x) < len(c):
        print(path, 'window too short'); continue
    corr = np.correlate(x, c, 'valid')
    norms = np.sqrt(np.convolve(x ** 2, np.ones(len(c)), 'valid')) * np.sqrt((c ** 2).sum())
    r = corr / np.maximum(norms, 1e-9)
    print(path, 'r = %.3f at %.2f s' % (r.max(), r.argmax() / 44100))
