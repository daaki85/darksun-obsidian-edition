# hoverlabel.py [X Y | foe C] [watch SECONDS]: the chance to hit under the pointer (dsloader/hover.py) as the game has it: moves the pointer (no click) to game pixel X, Y, or onto enemy combatant C's figure (10 pixels above its feet), then prints the pointer, its mode, the thing the game has under it (DS:0BCBh) and each of DSCLOG's label slots in use with its text.
# The text is read back from the slot's own ink mask, matched against every text hover.py can
# make ("12+ (45%)", "Behind 10+ (55%)", "14+ (35%), behind 10+", "Hits") and "Miss", so it is
# what the session's Loader drew, not what this tool would work out ("?" for any other label, a
# spell's name). With "watch SECONDS" it prints the slots every 50 ms whenever they change, with
# the time: for a label going as the pointer leaves or the turn passes, and for flicker.
import os, re, struct, sys, time, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import art, dicelog, hitchance, hover, labels
low = g.read(0, dicelog.CONVENTIONAL_AND_UPPER)
hdr = next(m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), low) if m.start() % 16 == 0)
font = art.GameArt.of(GAME).font
def texts():
    yield labels.MISS
    yield "Hits"
    shorts = [hitchance._short(n) for n in range(2, 22)]
    for n in range(2, 22):
        for head in ("", "Backstab ", "Behind ", "Unseen "):
            plain = f"{head}{hitchance._short(n)} ({hitchance.chance(n)}%)"
            yield plain
            if not head:
                for word in ("behind", "backstab"):
                    for s in set(shorts):
                        yield f"{plain}, {word} {s}"
known = {}
def text_of(slot: bytes) -> str:
    if not known:
        for t in texts():
            w, h, ink, _ = labels.masks(font, t)
            known[(w, ink)] = t
    return known.get((slot[1], slot[8:8 + labels.MASK]), "?")
def name(thing: int) -> str:
    c = gd.combatant_creature(thing) if thing < 520 else None
    return gd.creature_name(c) if c is not None else "-"
def slots():
    at = labels.slots_at(g, hdr)
    out = []
    for n in range(labels.SLOTS):
        s = g.read(at + n * labels.SIZE, labels.SIZE)
        if s[0]:
            thing, = struct.unpack_from("<H", s, 6)
            out.append(f"slot {n}: thing {thing} {name(thing)} \"{text_of(s)}\"")
    return out
def pointer(): return struct.unpack('<HH', g.read(ds * 16 + POINTER, 4))
def move(x, y):
    for _ in range(12):
        px, py = pointer()
        if abs(px - x) <= 1 and abs(py - y) <= 1: break
        subprocess.run(['xdotool', 'mousemove_relative', '--', str(x - px), str(y - py)]); time.sleep(0.15)
watch = None
if 'watch' in args:
    watch = float(args[args.index('watch') + 1]); args = args[:args.index('watch')]
if args[:1] == ['foe']:
    c = int(args[1])
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + c * 32, 4))
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    move(x - cx, y - cy - 10)
elif len(args) >= 2:
    move(int(args[0]), int(args[1]))
if watch is None:
    time.sleep(0.5)
    seen = hover.look(gd)
    print(f"pointer {seen.pointer} mode {seen.mode} on the map {int(seen.on_map)} under it {seen.under} "
          f"{name(seen.under) if seen.under != hover.NONE else 'nothing'}; turn {gd.whose_turn()} fight {int(gd.in_combat())}")
    print("\n".join(slots()) or "no label")
else:
    start, last = time.time(), None
    while time.time() - start < watch:
        now = slots()
        if now != last:
            print(f"{time.time() - start:6.2f} turn {gd.whose_turn()} pointer {pointer()}: " + ("; ".join(now) or "no label"), flush=True)
            last = now
        time.sleep(0.05)
