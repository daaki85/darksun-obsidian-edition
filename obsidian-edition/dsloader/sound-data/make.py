# The mod's sounds (dsloader/sounds.py), made at 32 kHz and brought down to the game's 8 kHz, 8-bit
# unsigned mono (its BVOC clips' form): `python3 make.py FOLDER` (numpy) writes the eight candidates
# the user chose from (2026-11-05); hide.wav is hide-1-fade-into-shadow.wav and pick.wav is
# pocket-2-purse-jingle.wav. A development tool only: the Loader reads the WAV files. Both made as loud
# as the game's typical clip on 2026-11-09 (full scale, the hide clip 3 dB more through a soft limiter:
# about -10.6 and -9.7 LUFS over their loudest 400 ms, the game's median -11.1), and denser on
# 2026-11-10 (still too quiet: DOSBox plays every clip at the same peak, so only a clip's average can
# rise): the hide clip through the limiter 12 dB harder, the pick 9 dB, each loudest 400 ms then
# 6-7 dB under its peak (11 and 12.5 before), as the game's loudest fight sounds (104: about 6).
import numpy as np, wave, sys
R = 32000; OUT = 8000
rng = np.random.default_rng(7)
def t(sec): return np.arange(int(sec * R)) / R
def env(n, a, d, shape=3.0):
    x = np.arange(n) / R
    e = np.minimum(1, x / max(a, 1e-4)) * np.exp(-np.maximum(0, x - a) * shape / max(d, 1e-4))
    return e
def onepole(x, fc):           # fc may be an array (a sweep)
    fc = np.broadcast_to(fc, x.shape); y = np.zeros_like(x); s = 0.0
    a = 1 - np.exp(-2 * np.pi * fc / R)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
def band(x, lo, hi): return onepole(x, hi) - onepole(onepole(x, hi), lo)
def clink(f, dur=0.22, amp=1.0):   # a small coin: inharmonic partials, fast decay
    tt = t(dur); s = 0
    for r, a, dk in ((1, 1, 18), (2.76, .6, 26), (5.4, .35, 40), (8.93, .2, 55)):
        s = s + a * np.sin(2 * np.pi * f * r * tt + rng.uniform(0, 6)) * np.exp(-dk * tt)
    return amp * s * np.minimum(1, tt / 0.0015)
def place(total, parts):
    out = np.zeros(int(total * R))
    for at, sig in parts:
        i = int(at * R); out[i:i + len(sig)] += sig[:len(out) - i]
    return out
def save(name, x, gain=0.8, drive=0):
    # to 8 kHz: lowpass under 3.6 kHz, then every 4th sample; DRIVE dB more through a soft limiter
    # (tanh, the peak kept at GAIN), for a clip whose average is low for its peak
    k = np.sinc(np.arange(-48, 49) * 3600 * 2 / R) * np.hamming(97); k /= k.sum()
    y = np.convolve(x, k, 'same')[::R // OUT]
    y = y / (np.abs(y).max() + 1e-9)
    if drive:
        g = 10 ** (drive / 20); y = np.tanh(y * g) / np.tanh(g)
    y = y * gain
    b = np.clip(np.round(y * 127 + 128), 0, 255).astype(np.uint8)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(OUT); w.writeframes(b.tobytes())
    print(name, round(len(b) / OUT, 2), 's')
d = sys.argv[1]
# --- hiding ---------------------------------------------------------------------------------
n = rng.standard_normal(int(.75 * R))
sweep = np.geomspace(2600, 220, len(n))                       # a breath that sinks into the dark
save(f'{d}/hide-1-fade-into-shadow.wav', onepole(n, sweep) * env(len(n), .12, .55, 2.2), 1.0, 12)  # (.55 and no drive till 2026-11-09, 3 till 2026-11-10: too quiet)
n = rng.standard_normal(int(.4 * R))
save(f'{d}/hide-2-cloak-swish.wav', band(n, 500, np.geomspace(3000, 900, len(n))) * env(len(n), .05, .3, 3), .6)
tt = t(.9); f = np.geomspace(330, 165, len(tt))
tone = np.sin(2 * np.pi * np.cumsum(f) / R) + .4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / R)
air = onepole(rng.standard_normal(len(tt)), 900) * 3
save(f'{d}/hide-3-shadow-hum.wav', (tone * .6 + air * .5) * env(len(tt), .15, .7, 2.5), .5)
tt = t(.7); s = 0
for f0, at in ((880, 0), (660, .09), (494, .18)):            # three soft notes stepping down
    x = np.zeros(len(tt)); i = int(at * R); m = len(tt) - i; u = tt[:m]
    x[i:] = (np.sin(2 * np.pi * f0 * u) + .3 * np.sin(2 * np.pi * f0 * 2 * u)) * np.exp(-6 * u) * np.minimum(1, u / .01)
    s = s + x
save(f'{d}/hide-4-falling-chime.wav', s * np.exp(-1.5 * tt), .5)
# --- pickpocket -----------------------------------------------------------------------------
save(f'{d}/pocket-1-two-coins.wav', place(.35, [(0, clink(2350)), (.07, clink(2900, amp=.7))]), .7)
parts = [(rng.uniform(0, .18), clink(rng.uniform(2000, 3400), .18, rng.uniform(.4, 1))) for _ in range(6)]
save(f'{d}/pocket-2-purse-jingle.wav', place(.4, parts), 1.0, 9)  # (.7 till 2026-11-09, no drive till 2026-11-10: too quiet)
n = rng.standard_normal(int(.12 * R))
snatch = band(n, 400, 2500) * env(len(n), .01, .1, 4)          # a quick tug of cloth, then a coin
save(f'{d}/pocket-3-snatch-and-clink.wav', place(.4, [(0, snatch * .8), (.09, clink(2600, .25))]), .7)
tt = t(.3)
pluck = np.sin(2 * np.pi * 1300 * tt) * np.exp(-30 * tt) + .5 * np.sin(2 * np.pi * 2600 * tt) * np.exp(-45 * tt)
save(f'{d}/pocket-4-soft-pluck.wav', pluck * np.minimum(1, tt / .002), .6)
