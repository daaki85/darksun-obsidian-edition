# picstore.py [check|dump SLOT|stale]: the game's picture store (the 741,376 bytes behind memory
# handle DS:4C33h) as the Loader can reach it (2026-11-09, logs/2026-11-09-picture-store.md).
# The store is a handle of the game's paged memory manager: handle table DS:47FAh (14 bytes: +0
# its first page link, +2 its id = the handle's high word, +4 its size), its pages a chain of
# links through the page directory, cached in five 108h-byte blocks at DS:42D2h (+2 key A+1, +4
# key B, +8 sixty-four entries of (descriptor, next link); a link is A<<12 | B<<6 | entry); a
# descriptor is backend<<12 | page. Backend 0 (DS:4850h: read 1187:0491h, write 1187:04B0h, its
# word +0Ch the XMS handle) moves 16 KB pages to and from one XMS block with the XMS driver's
# function 0Bh. In DOSBox an XMS block is guest RAM above 1 MB, in one piece: found here by
# matching an in-memory picture's bytes (a slot's far pointer +0Ah) against guest RAM.
#   check  (default) the mapping, the XMS block's address, and every in-memory slot's buffer
#          compared with its bytes in the store (all should match)
#   dump SLOT  the slot's entry and its first bytes in the store
#   stale  the FFFEh slots: length, place, in memory or not
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
D = ds * 16
TABLE = (gd.load_seg + 0x3E60) * 16
PAGE = 0x4000


def w(o): return struct.unpack('<H', g.read(D + o, 2))[0]


def store_pages():
    """[(backend, page)] of the store handle's pages, in order; None if a link isn't cached."""
    handle = struct.unpack('<I', g.read(D + 0x4C33, 4))[0]
    idx, hid = handle & 0xFFFF, handle >> 16
    first, hid2, size = struct.unpack('<HHI', g.read(D + 0x47FA + idx * 14, 8))
    if hid2 != hid:
        return None, size
    blocks = {}
    for b in range(5):
        a, bb = struct.unpack('<HH', g.read(D + 0x42D2 + b * 0x108 + 2, 4))
        blocks[(a, bb)] = D + 0x42D2 + b * 0x108 + 8
    pages, link = [], first
    for _ in range((size + PAGE - 1) // PAGE):
        at = blocks.get(((link >> 12) + 1, (link & 0xFFF) >> 6))
        if at is None:
            return None, size
        desc, nxt = struct.unpack('<HH', g.read(at + (link & 0x3F) * 4, 4))
        pages.append((desc >> 12, desc & 0xFFF))
        link = nxt
    return pages, size


def slots():
    n = w(0x1F84)
    tab = g.read(TABLE, n * 16)
    out = []
    for k in range(n):
        num, ln, pl, off, seg, fl, age = struct.unpack_from('<HIiHHBB', tab, k * 16)
        out.append((k, num, ln, pl, seg * 16 + off, fl, age))
    return out


def xms_offset(pages, place):
    backend, page = pages[place // PAGE]
    return backend, page * PAGE + place % PAGE


def find_base(pages, ss):
    """The XMS block's guest address, from in-memory pictures' bytes; None if none matches."""
    mem = g.read(0x100000, g.size - 0x100000)
    cands = None
    for k, num, ln, pl, buf, fl, age in ss:
        if not fl & 2 or pl < 0 or ln < 64 or num == 0xFFFF:
            continue
        n = min(64, PAGE - pl % PAGE)
        if n < 32:
            continue
        probe = g.read(buf, n)
        _, x = xms_offset(pages, pl)
        hits, i = set(), mem.find(probe)
        while i >= 0:
            hits.add(0x100000 + i - x)
            i = mem.find(probe, i + 1)
        cands = hits if cands is None else cands & hits
        if cands is not None and len(cands) == 1:
            return cands.pop()
    return None


pages, size = store_pages()
ss = slots()
if pages is None:
    print('store pages not resolved (a directory block not cached)'); sys.exit(1)
arg = sys.argv[1:] or ['check']
backends = sorted({b for b, p in pages})
print(f'store {size} bytes, {len(pages)} pages, backends {backends}, XMS pages {pages[0][1]:#x}..{pages[-1][1]:#x}',
      'contiguous' if all(pages[i][1] == pages[0][1] + i for i in range(len(pages))) else 'scattered')
fn, xh = struct.unpack('<IH', g.read(D + 0x4854, 4) + g.read(D + 0x485C, 2))
print(f'backend 0 write {fn >> 16:04X}:{fn & 0xFFFF:04X} (load seg + {(fn >> 16) - gd.load_seg:04X}), XMS handle {xh}')
base = find_base(pages, ss)
print('XMS block at', hex(base) if base is not None else None)
if arg[0] == 'check' and base is not None:
    good = bad = 0
    for k, num, ln, pl, buf, fl, age in ss:
        if fl & 2 and pl >= 0:
            data, rest, p = b'', ln, pl
            while rest:
                n = min(rest, PAGE - p % PAGE)
                data += g.read(base + xms_offset(pages, p)[1], n)
                rest -= n; p += n
            if data == g.read(buf, ln):
                good += 1
            else:
                bad += 1; print('  differs: slot', k, 'picture', num)
    print(f'in-memory slots matching the store: {good}, differing: {bad}')
elif arg[0] == 'dump':
    k = int(arg[1]); e = ss[k]
    print(e)
    if base is not None and e[3] >= 0:
        print(g.read(base + xms_offset(pages, e[3])[1], 32).hex(' '))
elif arg[0] == 'stale':
    st = [e for e in ss if e[1] == 0xFFFE]
    print(len(st), 'stale:', [(k, ln, pl, 'mem' if fl & 2 else '-') for k, num, ln, pl, buf, fl, age in st])
