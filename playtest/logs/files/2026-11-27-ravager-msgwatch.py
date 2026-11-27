import sys,os,subprocess,argparse,struct,time
sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition/tests')
sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition')
os.chdir('/home/claude/darksun-obsidian-edition/obsidian-edition')
import test_dsclog2_room as t
t.RoomTests.setUpClass(); img=t.RoomTests.sections['image']
from dsloader.__main__ import connect
pid=int(open('/tmp/playtest/rav.pid').read())
g=connect(argparse.Namespace(pid=pid,host_base=None))
mem=g.read(0,0x110000); base=mem.find(b'DSCLOGR1')-img.get('hdr',0)
A=base+img['msg_waiting']
mode=sys.argv[1]; dur=float(sys.argv[2])
W=subprocess.check_output(['xdotool','search','--class','dosbox']).split()[-1]
end=time.time()+dur; n=0
while time.time()<end:
    if g.read(A,1)[0]:
        t0=time.time(); n+=1
        time.sleep(0.3)
        subprocess.run(['import','-window',W,'/tmp/playtest/box%d.png'%n])
        t1=time.time()
        if mode=='click': subprocess.run(['xdotool','click','--window',W,'1'])
        elif mode=='key': subprocess.run(['xdotool','key','--window',W,'space'])
        while g.read(A,1)[0] and time.time()-t1<10: time.sleep(0.01)
        print('box %d: up %.2fs before %s, closed %.2fs after'%(n,t1-t0,mode,time.time()-t1),flush=True)
    time.sleep(0.01)
