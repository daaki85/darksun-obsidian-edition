# ravfixes.py [OUT]: a copy of Wake of the Ravager ($RAV, default $WORK/rav) in OUT (default $WORK/ravfix,
# hard links but for the two files changed and those the game writes) with the mod's bug fixes that carry over unchanged:
# five of DSUN.EXE's (gamepatch.py's own bytes, at their twins' offsets in the sequel's program: each
# checked to hold the patch's original bytes and no relocated word) and the spell records' (RESOURCE.GFF's
# DATA 0-319, 73 bytes a spell, whose first 32 are Shattered Lands' record: the same field fixed,
# only where the sequel's record still holds the original bytes). Prints what it did. Run from playtest/.
import os, sys, struct, shutil
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader import gamepatch as gp, game
from dsloader.gff import read_gff, index_places
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
RAV = os.environ.get('RAV', os.path.join(WORK, 'rav')); OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'ravfix')
SL = os.path.join(os.environ.get('DS_GAME', os.path.join(WORK, 'inst')), 'DSUN.EXE')
# the program's fixes: the patch, and its twin's offset in the sequel's DSUN.EXE (GOG 1.1, 634,416
# bytes), found by byte likeness and read side by side (reports/wake-of-the-ravager.md)
EXE_FIXES = {'party_best': 0x8C60E, 'monster_count': 0x8D3FB, 'thief_slots': 0x49C90,
             'dam_half': 0x7B1E8, 'page_free': 0x28412}
SPELL_TABLE = 0x41F70  # Shattered Lands' 32-byte spell records in its DSUN.EXE (Armor's)
P = {p.name: p for p in gp.PATCHES}
if os.path.exists(OUT): shutil.rmtree(OUT)
# hard links but for what the game writes (DOSBox writes a file in place: a link would change the original's too)
WRITTEN = ('DARKRUN.GFF', 'DARKSAVE.GFF', 'CHARSAVE.GFF')
def _copy(src, dst):
    b = os.path.basename(src).upper()
    (shutil.copy2 if b in WRITTEN or b.startswith('SAVE') else os.link)(src, dst)
shutil.copytree(RAV, OUT, copy_function=_copy)
exe = bytearray(open(os.path.join(RAV, 'DSUN.EXE'), 'rb').read())
assert len(exe) == 634416, 'not GOG 1.1 Wake of the Ravager'
rel = gp.relocated(bytes(exe))
for name, at in EXE_FIXES.items():
    p = P[name]
    assert exe[at:at + len(p.original)] == p.original, name
    assert not set(range(at, at + len(p.original))) & rel, name
    exe[at:at + len(p.original)] = p.replacement
    print('DSUN.EXE %05X %-14s %s -> %s' % (at, name, p.original.hex(), p.replacement.hex()))
# fixes found by hand, in the sequel's own bytes (its code differs from SL's round them)
OWN_FIXES = {
    # the saving throw's last compare unsigned, so "can't save" (-100) saved (SL's save_signed;
    # WotR 66EA6h "mov al,[bp-2] / cmp al,[bp-1] / jb fail / jmp saved"): jb made jl
    'save_signed': (0x66EAC, '7203', '7c03'),
}
for name, (at, old, new) in OWN_FIXES.items():
    old, new = bytes.fromhex(old), bytes.fromhex(new)
    assert exe[at:at + len(old)] == old and not set(range(at, at + len(old))) & rel, name
    exe[at:at + len(old)] = new
    print('DSUN.EXE %05X %-14s %s -> %s (by hand)' % (at, name, old.hex(), new.hex()))
os.unlink(os.path.join(OUT, 'DSUN.EXE')); open(os.path.join(OUT, 'DSUN.EXE'), 'wb').write(exe)
# the spell records: by name (Shattered Lands' names through its 7-byte info records, +5 the name's DS offset)
sl = open(SL, 'rb').read()
def sl_name(i):
    o = struct.unpack_from('<H', sl, 0x5400 + game.SPELL_INFO_OFF + (i - 1) * 7 + 5)[0]
    return sl[gp.DS_FILE + o:gp.DS_FILE + o + 40].split(b'\0')[0].decode('latin1').upper()
res = bytearray(open(os.path.join(RAV, 'RESOURCE.GFF'), 'rb').read())
chunks = read_gff(bytes(res)); places = index_places(bytes(res), 'DATA')
by_name = {}
for i in range(320):
    by_name.setdefault(chunks[('DATA', i)][32:63].split(b'\0')[0].decode('latin1').upper(), i)
ALIAS = {'IRONSKIN': 'IRON SKIN', 'TURN PEBBLE INTO BOULDER': 'PEBBLE TO BOULDER', 'FLAME ARROW': 'FLAMING ARROW'}
done = []
for p in gp.PATCHES:
    if not SPELL_TABLE <= p.offset < SPELL_TABLE + 138 * 32: continue
    idx, fld = divmod(p.offset - SPELL_TABLE, 32)
    n = sl_name(idx); w = by_name.get(ALIAS.get(n, n))
    if w is None: print('RESOURCE  %-24s %-24s no such spell' % (p.name, n)); continue
    at = places[w][1] + fld
    have = bytes(res[at:at + len(p.original)])
    if have != p.original:
        print('RESOURCE  %-24s %-24s DATA %3d: left (%s)' % (p.name, n, w, 'SSI fixed it' if have == p.replacement else 'other bytes ' + have.hex()))
        continue
    res[at:at + len(p.original)] = p.replacement; done.append((w, fld, p.replacement))
    print('RESOURCE  %-24s %-24s DATA %3d +%02Xh %s -> %s' % (p.name, n, w, fld, p.original.hex(), p.replacement.hex()))
os.unlink(os.path.join(OUT, 'RESOURCE.GFF')); open(os.path.join(OUT, 'RESOURCE.GFF'), 'wb').write(res)
assert read_gff(bytes(res)).keys() == chunks.keys()
print('%d program fixes, %d spell fixes, in %s' % (len(EXE_FIXES) + len(OWN_FIXES), len(done), OUT))
