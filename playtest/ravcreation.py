# ravcreation.py [ROLLS] [RULES] [PID]: Wake of the Ravager's creation screen checked, the die pressed
# ROLLS times (default 20; game 145,92) on the screen as it stands (ravcreation.sh gets there). After
# each roll: the sheet's most hit points (+8, the line's right number) and the creature's (+0) agree,
# lie between the least and most the classes allow (DS:42D8h, 42D6h), and for one class equal the
# rolled dice (+0Ah) plus CON's bonus a level (the least less the levels): what DSCLOG2's ROLL_MAX_HP
# makes (the sequel alone kept the least the screen opened with: 7/7 for a 7th-level fighter). The
# rolls' mean too. RULES (default the ported ones, ravager.RULES_PORTED) are put in DSCLOG2's header
# first (0: the game's own rolls, to compare the better-of-two rule's mean). Exit 1 on any mismatch.
import sys, os, time, struct, argparse, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager, ravlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
rolls = int(sys.argv[1]) if len(sys.argv) > 1 else 20
rules = int(sys.argv[2], 0) if len(sys.argv) > 2 else ravager.RULES_PORTED
pid = int(sys.argv[3]) if len(sys.argv) > 3 else int(open(os.path.join(WORK, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
log = ravlog.RavDiceLog(g); log.attach(); log.set_rules(rules)   # (attaching writes the log's rules: set again)
def far(off):
    o, s = struct.unpack('<HH', g.read(ds*16 + off, 4)); return s*16 + o
def state():
    sheet, cr = g.read(far(0x1429), 0x42), g.read(far(0x142D), 0x31)
    most, least = struct.unpack('<HH', g.read(ds*16 + 0x42D6, 4))
    classes = [c for c in sheet[0x1B:0x1E] if c]
    return dict(hp=struct.unpack_from('<h', sheet, 8)[0], cur=struct.unpack_from('<h', cr, 0)[0],
                rolled=struct.unpack_from('<h', sheet, 0x0A)[0], least=least, most=most,
                classes=len(set(classes)) or 1, levels=sum(sheet[0x1E:0x21]))
bad, seen = 0, []
for n in range(rolls):
    subprocess.run(['python3', os.path.join(PT, 'ravclick.py'), '145', '92'], capture_output=True); time.sleep(2.5)
    s = state(); seen.append(s['hp'])
    why = []
    if s['hp'] != s['cur']: why.append('the line\'s two numbers differ')
    if not s['least'] <= s['hp'] <= s['most']: why.append('outside the least and most')
    if s['classes'] == 1 and s['hp'] != s['rolled'] + s['least'] - s['levels']: why.append('not the dice plus CON')
    bad += bool(why)
    print(f"roll {n+1}: HP {s['cur']}/{s['hp']} (dice {s['rolled']}, {s['least']}-{s['most']}, "
          f"{s['levels']} levels) {'; '.join(why) or 'ok'}", flush=True)
print(f"rules {rules:#x}: mean HP {sum(seen)/len(seen):.1f} over {len(seen)} rolls, {bad} wrong", flush=True)
sys.exit(1 if bad else 0)
