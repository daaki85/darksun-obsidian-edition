import sys, struct; sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader import gff, ravtransfer as rt
def member_items(s):
    cre, items, lists = rt._chunk(s,5), rt._chunk(s,7), rt._chunk(s,3)
    out = {}
    for m in range(4):
        rec = cre[m*0x3A:(m+1)*0x3A]; got=[]
        def walk(lst):
            if lst == rt.NONE: return
            n, = struct.unpack_from('<H', lists, lst*3+1)
            while n != rt.NONE:
                it = items[n*0x15:(n+1)*0x15]; got.append((n, it))
                c, = struct.unpack_from('<H', it, 8)
                if c != rt.NONE: walk(c)
                n, = struct.unpack_from('<H', it, 4)
        for at,_ in rt.SL_LISTS: walk(struct.unpack_from('<H', rec, at)[0])
        out[m] = (rec[0x28:0x3A].split(b'\0')[0].decode(), got)
    return out
if __name__ == '__main__':
    s = gff.read_gff(open(sys.argv[1],'rb').read())
    for m,(name,got) in member_items(s).items():
        print(name, [(n, -struct.unpack_from('<h',it,0)[0], struct.unpack_from('<H',it,0x0A)[0], it[0x11], it[0x14]) for n,it in got])
