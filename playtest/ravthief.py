# ravthief.py [MEMBER] [PID]: Wake of the Ravager's own thief-skill routine (its DSUN.EXE 8C647h, SL's
# 80240h) run in an emulator (unicorn) on the running game's memory, for party member MEMBER (default
# 0), once with the game's list of slots that bring the equipment penalty and once with the mod's fix
# (ravfixes.py's thief_slots: none), each skill's chance side by side. The routine and the overlays it
# calls are not in memory as a rule (swapped out to XMS), so the run is the live game's memory below
# A0000h with every overlay laid above from an image of ravfix's DSUN.EXE (Dark Sun Recompiled's
# tools/build_image.py, built once with the live PSP, 0192h, into $WORK/ravimg) and that image's stubs.
# Borland's model: SS is DS (buffers on the stack are read through DS). Needs: pip install unicorn.
# --helper: the Loader's game instead (class restrictions): the routine's end patched as the Loader
# patches it (INT F5h, site 20, DSCLOG2's BELT_SITE) and every INT dispatched through the live vector
# table, DSCLOG2's segment copied to A01Bh (its upper memory block is where the overlays are laid), so
# the helper's own code runs; one column, the game's slot list.
import sys, os, json, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UcError
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_AX, UC_X86_REG_IP
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
FIX = os.path.join(WORK, 'ravfix', 'DSUN.EXE'); IMG = os.path.join(WORK, 'ravimg')
RECOMP = os.environ.get('RECOMP', os.path.join(PT, '..', '..', 'darksun-recompiled'))
HELPER = '--helper' in sys.argv; args = [a for a in sys.argv[1:] if a != '--helper']
member = int(args[0]) if args else 0
pid = int(args[1]) if len(args) > 1 else int(open(os.path.join(WORK, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
live = g.read(0, 0xA0000)
psp = next(s for s in range(0x100, 0x400) if live[s*16:s*16+2] == b'\xcd\x20' and live[(s-1)*16] == 0x4D
           and live[(s-1)*16+8:(s-1)*16+12] == b'DSUN')
if not os.path.exists(os.path.join(IMG, 'layout.json')) or json.load(open(os.path.join(IMG, 'layout.json')))['psp_seg'] != psp:
    sys.path.insert(0, os.path.join(RECOMP, 'tools')); import build_image
    build_image.PSP_SEG = psp; build_image.build(FIX, IMG, '-W0 -L')
img = open(os.path.join(IMG, 'image.bin'), 'rb').read(); lay = json.load(open(os.path.join(IMG, 'layout.json')))
mem = bytearray(live) + bytearray(img[0xA0000:])
for r in lay['records']:
    if r['cls'] == 3: mem[r['seg']*16:r['seg']*16 + r['size']] = img[r['seg']*16:r['seg']*16 + r['size']]
fix = open(FIX, 'rb').read()
FN = 0x8C647  # the routine (its prologue; 8C716h the twin of SL's thief_skill site)
a = mem.find(fix[0x8C70D:0x8C71F]); assert a > 0 and mem.find(fix[0x8C70D:0x8C71F], a + 1) < 0, 'routine not found once'
L = a - (0x8C70D - FN); assert mem[L:L+3] == b'\x55\x8b\xec'
T = mem.find(fix[0x49C90-8:0x49C90+10]) + 8; assert T > 8, 'slot list not found'
FIXED, ORIG = bytes.fromhex('0d000d000d000d000d00'), bytes.fromhex('060001000a0003000d00')
def chance(skill, table):
    m = bytearray(mem); m[T:T+10] = table; m[0x500] = 0xF4            # HLT, the return address
    u = Uc(UC_ARCH_X86, UC_MODE_16); u.mem_map(0, 0x200000); u.mem_write(0, bytes(m))
    cs = (L - 0x100) >> 4; sp = 0xFE00 - 10
    u.mem_write(ds*16 + sp, struct.pack('<HHHI', 0x0500, 0, member, skill))  # far return, member, the skill (a long)
    for r, v in ((UC_X86_REG_CS, cs), (UC_X86_REG_DS, ds), (UC_X86_REG_ES, ds), (UC_X86_REG_SS, ds), (UC_X86_REG_SP, sp)): u.reg_write(r, v)
    stop = []
    if HELPER:
        u.hook_add(UC_HOOK_INTR, dispatch)
    else:
        u.hook_add(UC_HOOK_INTR, lambda uc, n, d: (stop.append(n), uc.emu_stop()))
    try: u.emu_start(L, 0x500, count=500000)
    except UcError as e: return 'error %s' % e
    if stop: return 'INT %Xh' % stop[0]
    ax = u.reg_read(UC_X86_REG_AX); return ax - 0x10000 if ax & 0x8000 else ax
def dispatch(uc, n, d):  # a real-mode INT: FLAGS, CS, IP pushed, CS:IP from the vector table
    from unicorn.x86_const import UC_X86_REG_EFLAGS
    ip, cs, ss, sp = (uc.reg_read(r) for r in (UC_X86_REG_IP, UC_X86_REG_CS, UC_X86_REG_SS, UC_X86_REG_SP))
    sp = (sp - 6) & 0xFFFF; uc.mem_write(ss*16 + sp, struct.pack('<HHH', ip, cs, uc.reg_read(UC_X86_REG_EFLAGS) & 0xFFFF))
    off, seg = struct.unpack('<HH', bytes(uc.mem_read(n*4, 4)))
    for r, v in ((UC_X86_REG_SP, sp), (UC_X86_REG_CS, seg), (UC_X86_REG_IP, off)): uc.reg_write(r, v)
if HELPER:
    full = g.read(0, 0x110000); hseg = struct.unpack_from('<H', full, 0xF5*4 + 2)[0]
    mem[0xA01B0:0xA01B0 + 0x8000] = full[hseg*16:hseg*16 + 0x8000]
    mem[0xF5*4:0xF5*4 + 4] = struct.pack('<HH', struct.unpack_from('<H', full, 0xF5*4)[0], 0xA01B)
    site = L + (0x8C7C5 - FN); assert mem[site:site+3] == b'\x8b\xc6\x5f'; mem[site:site+3] = b'\xcd\xf5\x14'
    NAMES = ('pick pockets', 'open locks', 'find/remove traps', 'move silently', 'hide in shadows', 'hear noise', 'climb walls', 'read languages')
    print('member %d through DSCLOG2 (its rules %04X)' % (member, struct.unpack_from('<H', full, hseg*16 + 170)[0]))
    for s, n in enumerate(NAMES):
        print('  %-18s %5s' % (n, chance(s, ORIG)))
    sys.exit()
NAMES = ('pick pockets', 'open locks', 'find/remove traps', 'move silently', 'hide in shadows', 'hear noise', 'climb walls', 'read languages')
print('member %d (DS %04X, PSP %04X): the game\'s slot list, the fix' % (member, ds, psp))
for s, n in enumerate(NAMES):
    print('  %-18s %5s %5s' % (n, chance(s, ORIG), chance(s, FIXED)))
