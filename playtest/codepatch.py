# codepatch.py [SECONDS] [game]: does a write to CODE in the game's memory take effect at once? (The
# DOSBox-X experiment, 2026-11-18: the Loader patches code while the game runs, and a write that
# doesn't go through DOSBox's own page handlers, as one through the memory file, could leave the
# dynamic core running its old translation.) DSCLOG's probe in the map's main loop has
# "inc word [cs:main_ticks]" (2E FF 06 lo hi, the header's +260; found in the helper's segment by
# those bytes): the five bytes are made NOPs, the count watched
# for SECONDS (default 2), and the bytes put back. With the write acted on, the count stands
# still while they are NOPs and runs again after. On the map, out of a fight; nothing is left
# changed (the count is DSCLOG's own, framerate.py reads), but as after any memory edit: no save.
# "game": the patch is made in the game's own code instead (conventional memory): the main loop's
# "INT VEC_SCROLL" (CD DC, then A9 and a segment: PROBE_SCROLL's site, where the game asked where
# the pointer is) made two NOPs, so the probe that counts isn't called for those seconds.
import os, sys, struct, time
PLAYTEST = os.path.dirname(os.path.abspath(__file__))
in_game = "game" in sys.argv[1:]
secs = next((float(a) for a in sys.argv[1:] if a != "game"), 2.0)
sys.argv = sys.argv[:1]
sys.path.insert(0, PLAYTEST); __file__ = os.path.join(PLAYTEST, "live.py"); exec(open(__file__).read())
MAIN_TICKS = 260
hdr = next(at for at in range(0xC0000, 0xF0000, 16) if g.read(at, 8) == b"DSCLOGvb")
image = g.read(hdr, 0x10000)
inc = b"\x2e\xff\x06" + struct.pack("<H", MAIN_TICKS)
assert image.count(inc) == 1, image.count(inc)
code, count = hdr + image.index(inc), hdr + MAIN_TICKS
was = g.read(code, 5)
if in_game:
    low = g.read(0, 0xA0000); site = b"\xcd\xdc\xa9"
    assert low.count(site) == 1, low.count(site)
    code = low.index(site); was = g.read(code, 2)
print(f"the patch at {code:#x}: {was.hex()}")
def flips(): return struct.unpack("<H", g.read(count, 2))[0]
def rate(label):
    a = flips(); t = time.time(); time.sleep(secs); b = flips()
    print(f"{label}: {((b - a) & 0xFFFF) / (time.time() - t):.1f} passes a second")
    return (b - a) & 0xFFFF
before = rate("as built")
g.write(code, b"\x90" * len(was))
try:
    first = flips(); time.sleep(0.05); soon = flips()
    patched = rate("made NOPs")
finally:
    g.write(code, was)
after = rate("put back")
print(f"passes counted in the first 50 ms after the write: {(soon - first) & 0xFFFF}")
print("RESULT:", "the write was acted on at once" if before and not patched and after
      else "STALE CODE: the game ran on with the old instruction" if before and patched
      else "the patch held after it was undone" if before and not after else "no passes to count (not on the map?)")
