# gearpoll.py: watches the Loader's creation gear reach the roster, for 110 s. From DONE on the
# creation screen, each change of DSCLOG's GEAR_DUE (+1830) and lv_creating
# (+361, the weapon window up), the dice log's new lines, CHARSAVE.GFF written (the roster's copy) and
# the Loader's heartbeat age (+1865, over 20 ticks: Loader gone), for 110 s. Start it just before DONE:
# the gear lines must come before charsave_written (logs/2026-11-15-kit-rebalance-checks.md part 7).
import os,sys,time,struct;__file__=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'live.py');exec(open(__file__).read())
W = os.environ.get('PLAYTEST_WORK', '/tmp/playtest').rstrip('/') + '/'
hdr=next(i for i in range(0xA0000,0x100000,16) if g.read(i,8)==b'DSCLOGva')
last=None; t0=time.time(); n0=sum(1 for _ in open(''+W+'dice.txt')); m0=os.path.getmtime(''+W+'inst/CHARSAVE.GFF')
while time.time()-t0<110:
    bios=struct.unpack('<H',g.read(0x46C,2))[0]; beat=struct.unpack('<H',g.read(hdr+1865,2))[0]
    age=(bios-beat)&0xFFFF
    v=(g.read(hdr+1830,1)[0], g.read(hdr+361,1)[0], sum(1 for _ in open(''+W+'dice.txt'))-n0, os.path.getmtime(''+W+'inst/CHARSAVE.GFF')!=m0, age>20)
    if v!=last: print(f"{time.time()-t0:6.2f} gear_due={v[0]} creating={v[1]} dice_lines+{v[2]} charsave_written={v[3]} beat_age={age}", flush=True); last=v
    time.sleep(0.05)
