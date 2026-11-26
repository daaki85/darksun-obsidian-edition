# darkfix_apply.py GPLDATA_IN GPLDATA_OUT FIXES_DIR: put OpenDS darkfix-ds1 GPL repairs (every fix .py in
# FIXES_DIR, a checkout of their ds1-patch/fixes) into a copy of GPLDATA.GFF, with our own code: each
# fix's REPAIRS list is read by AST, never imported or run, and applied by their patcher's rules
# (same-length in place; a longer one a detour after the chunk, its labels rebased). For runtime QA of
# their betas in the stock game (start_stock.sh). Every fingerprint is checked first.
import ast, sys, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "obsidian-edition"))
from dsloader import gff, icons

def lit(n):
    if isinstance(n, ast.Constant): return n.value
    if isinstance(n, ast.List): return [lit(e) for e in n.elts]
    if isinstance(n, ast.Tuple): return tuple(lit(e) for e in n.elts)
    if isinstance(n, ast.Dict): return {lit(k): lit(v) for k, v in zip(n.keys, n.values)}
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add): return lit(n.left) + lit(n.right)
    raise ValueError(ast.dump(n))

def repairs_of(path):
    tree = ast.parse(open(path).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REPAIRS" for t in node.targets):
            return lit(node.value)
    return []

def patch_chunk(code, reps):
    out = bytearray(code); app = bytearray([0x00]); spans = []
    for r in reps:
        exp, rep, off = bytes.fromhex(r["expect"]), bytes.fromhex(r["replace"]), r["offset"]
        assert bytes(code[off:off+len(exp)]) == exp, ("fingerprint", r["chunk_id"], hex(off))
        assert all(off >= e or off + len(exp) <= s for s, e in spans); spans.append((off, off+len(exp)))
    for r in reps:
        exp, rep, off = bytes.fromhex(r["expect"]), bytes.fromhex(r["replace"]), r["offset"]
        if len(rep) == len(exp):
            out[off:off+len(rep)] = rep; continue
        at = len(code) + len(app)
        back = off + len(exp)
        body = bytearray(rep + bytes([0x12, back >> 8, back & 0xFF]))
        for i in r.get("relocate", ()):
            a = (body[i] << 8 | body[i+1]) + at; assert a < 0x8000
            body[i], body[i+1] = a >> 8, a & 0xFF
        app += body
        out[off:off+len(exp)] = b"\x00" * len(exp)
        out[off:off+3] = bytes([0x12, at >> 8, at & 0xFF])
    return bytes(out) + (bytes(app) if len(app) > 1 else b"")

src, dest, fixdir = sys.argv[1], sys.argv[2], sys.argv[3]
data = open(src, "rb").read(); chunks = gff.read_gff(data)
groups = {}
for f in sorted(glob.glob(os.path.join(fixdir, "0[0-9][0-9]-*.py"))):
    reps = repairs_of(f)
    print(os.path.basename(f), len(reps), "repairs")
    for r in reps: groups.setdefault((r["kind"].ljust(4), r["chunk_id"]), []).append(r)
added = {k: patch_chunk(chunks[k], v) for k, v in groups.items()}
open(dest, "wb").write(icons.with_chunks(data, added))
check = gff.read_gff(open(dest, "rb").read())
assert all(check[k] == v for k, v in added.items())
print("patched chunks:", sorted(added))
