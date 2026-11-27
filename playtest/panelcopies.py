"""panelcopies.py DIR: frames of framegrab.sh (320x240) with copies of the combat log's docked panel left on
the map: its stone and well colours counted left of it (x 0-133, rows 130-239) and above it (x 136-319,
rows 100-140), more than 20 such pixels a copy (a "Miss" label is 21-23). Prints the frames, those with
copies and their runs (first frame, length, most pixels): logs/2026-11-27-panel-scroll-autosave.md."""
import sys,glob
from PIL import Image
STONE={(113,113,138),(32,32,56),(101,101,125),(89,89,113)}
fs=sorted(glob.glob(sys.argv[1]+'/*.png')); bad=[]
for f in fs:
    px=Image.open(f).convert('RGB').load()
    n=sum(1 for x in range(0,134) for y in range(130,240) if px[x,y] in STONE)+sum(1 for x in range(136,320) for y in range(100,141) if px[x,y] in STONE)
    if n>20: bad.append((int(f[-9:-4]),n))
runs=[];
for i,n in bad:
    if runs and i-runs[-1][-1][0]<=2: runs[-1].append((i,n))
    else: runs.append([(i,n)])
print(sys.argv[1],len(fs),'frames',len(bad),'with copies, in',len(runs),'runs; longest',max((len(r) for r in runs),default=0))
print([(r[0][0],len(r),max(n for _,n in r)) for r in runs])
