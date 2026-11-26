# kitset.py MEMBER CLASS LEVEL KITBYTE: the member made a single-class character of CLASS (the sheet's
# class number) at LEVEL with kit KITBYTE (0 none, 1-3 the class's kits in kitpages.KITS order). It sets a
# non-warrior's attack rate too (+2Ah 2: the game reads attacks a round from there, set at creation and
# level-up, so a warrior's 3 left in place keeps the old rate). Memory only: never save after.
import os,sys,struct;__file__=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'live.py');exec(open(__file__).read())
from dsloader import game, kitpages
m,c,l,k=map(int,sys.argv[1:5])
rec=gd.creature(m); idx=struct.unpack_from('<H',rec,game.CREATURE_SHEET_INDEX)[0]
a=game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)+idx*game.SHEET_SIZE
s=bytearray(gd.guest.read(a, game.SHEET_SIZE))
s[0x21:0x24]=bytes((c,0,0)); s[0x24:0x27]=bytes((l,0,0)); s[0x43]=k; s[0x2A]=2; gd.guest.write(a, bytes(s))
print('kits', kitpages.kits_of(bytes(s)), 'specs', list(game.spec_kinds(bytes(s))))
