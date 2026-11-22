# ravxfer_check.py SAVE.SAV [SAVE.SAV...]: the Loader's party transfer (dsloader/ravtransfer.py) set
# against SSI's own (CHARTRAN.EXE, through chartran.sh) on each Shattered Lands save: every roster
# chunk the two write (CHAR, CACT, SPST, PSST, PSIN) compared, the differing ones named. Needs
# setup_ravager.sh's $WORK/rav. CHARTRAN's stray 72nd spell bit (it sets it now and then for no spell
# the member knows) is shown apart, not counted as a difference.
import os, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader import gff, ravtransfer as rt
RAV = os.environ.get('RAV', os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav'))
sequel = rt.load_sequel(RAV); bad = 0
for save in sys.argv[1:]:
    out = tempfile.mkdtemp(prefix='ct-')
    subprocess.run(['sh', os.path.join(PT, 'chartran.sh'), save, out], capture_output=True, timeout=120)
    theirs = gff.read_gff(open(os.path.join(out, 'C', 'RAVAGER', 'CHARSAVE.GFF'), 'rb').read())
    mine, moved = rt.roster(gff.read_gff(open(save, 'rb').read()), sequel)
    diff, stray = [], []
    for k, v in sorted(mine.items()):
        t = theirs.get(k)
        if t == v: continue
        if k[0] == 'SPST' and t is not None and bytes(a ^ b for a, b in zip(v, t)) == bytes(8) + b'\x80':
            stray.append(k)
        else:
            diff.append(k)
    bad += len(diff)
    print('%s: %d members, %d chunks, %s%s' % (save, len(moved), len(mine), 'the same' if not diff else 'differ: %s' % diff,
                                             ', CHARTRAN\'s stray spell bit in %s' % stray if stray else ''))
sys.exit(1 if bad else 0)
