# dec.py SCRIPT LO HI: decode GPL script SCRIPT (the game's own GPLDATA.GFF, $DS_GAME) from offset LO
# to HI (hex): each command's offset, number and arguments. For the Loader's built copy (what the
# game runs) set GPLDATA to obsidian-edition/dos/GPLDATA.GFF.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import REPO, GAME
sys.path.insert(0, os.path.join(REPO, 'obsidian-edition'))
from dsloader import gpl
data = open(os.environ.get('GPLDATA', os.path.join(GAME, 'GPLDATA.GFF')), 'rb').read()
scripts, ftypes = gpl.load_scripts(data)
kind = os.environ.get('KIND', 'GPL ')
s = int(sys.argv[1]); lo = int(sys.argv[2], 16); hi = int(sys.argv[3], 16)
for op in gpl.decode(scripts[(kind, s)], ftypes):
    if lo <= op.at <= hi: print(hex(op.at), op.code, str(op.args)[:200])
