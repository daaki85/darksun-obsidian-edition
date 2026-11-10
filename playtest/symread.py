"""Read DSCLOG variables by name in the running game: `python3 symread.py NAME [NAME...]` (each's first
4 bytes, hex), from a symbol map of obsidian-edition/dos/dsclog.asm as built (the tree's DSCLOG.EXE)."""
import os, struct, subprocess, sys, tempfile
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'obsidian-edition', 'dos')
with tempfile.TemporaryDirectory() as t:
    src, mp = os.path.join(t, 'm.asm'), os.path.join(t, 'm.map')
    with open(src, 'w') as f:
        f.write(f"[map symbols {mp}]\n" + open(os.path.join(DOS, 'dsclog.asm')).read())
    subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', os.path.join(t, 'm.exe'), src], check=True)
    listing = open(mp).read()
sym = {}
for line in listing.split('Section image')[1].split('---- Section')[0].splitlines():
    p = line.split()
    if len(p) == 3:
        try:
            sym[p[2]] = int(p[1], 16)
        except ValueError:
            pass
exe = open(os.path.join(DOS, 'DSCLOG.EXE'), 'rb').read()
image = exe[struct.unpack_from('<H', exe, 8)[0] * 16:]
mem = g.read(0, 0x110000)
base = mem.find(b'DSCLOGva') - image.find(b'DSCLOGva')
for name in sys.argv[1:]:
    print(name, mem[base + sym[name]:base + sym[name] + 4].hex())
