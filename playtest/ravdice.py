# ravdice.py [--all] SECONDS [OUT]: the Loader's dice log for Wake of the Ravager (dsloader.ravlog.RavDiceLog: the
# sequel's layout, its memory read only) attached to the running sequel ($WORK/rav.pid), its lines printed
# (and appended to OUT) as they come, for SECONDS; then how many writes the read-only view dropped. --all: every roll, and each attack's AC
# worked out (base, armour, DEX, other). --numbers: each combatant's number after its name ("Draxan#26"), to
# tell apart foes of one name (as ravitems.py and ravfight.py number them). RAV_RULES_OFF=MASK (game.RULE_* bits, as 0x1000000): those rules off
# after the attach, in the Loader and DSCLOG2's header alike (a control run of a rule the Loader keeps).
# RAV_TAB_OFF=1: the red ring under the enemy chosen with Tab and the chances to hit (its line's, the pointer's) off.
# RAV_CHARGES_OFF=1: the charges' pass off (DiceLog.count_charges, as before its port: the charge routine's 2d4 behind the
# overlay manager's stub not known, its label "Armor: 7 left" with it), a control.
# RAV_STEALTH_ROLL=N: every hiding and moving silently roll N (stealth.py; 1 to hide every time, for a test).
import sys, os, time, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, launch, ravlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
show_all = '--all' in sys.argv; numbers = '--numbers' in sys.argv
args = [a for a in sys.argv[1:] if a not in ('--all', '--numbers')]
secs = float(args[0]); out = open(args[1], 'a') if len(args) > 1 else None
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
log = ravlog.RavDiceLog(g)
log.game_dir = os.environ.get('RAV', os.path.join(WORK, 'rav'))  # (its font: the names over figures)
print(log.attach(), flush=True)
if numbers:
    name = log.game.combatant_name
    log.game.combatant_name = lambda n: '%s#%d' % (name(n), n)
# the rules as the Loader sets them (its settings, kits and the other switches with them: DSCLOG2's
# assembled word has only the always-on ones), then RAV_RULES_OFF's off
log.set_rules(game.rules_from_settings(launch.load_settings()) & ~int(os.environ.get('RAV_RULES_OFF') or '0', 0))
if os.environ.get('RAV_RULES_OFF'):
    print('rules off: %s, now %#x' % (os.environ['RAV_RULES_OFF'], log.game.rules), flush=True)
if os.environ.get('RAV_TAB_OFF'):  # (a control: no ring, no chance to hit on the Tab line or under the pointer)
    from dsloader import rings
    log.ring_mode, log.hit_chance, log.hit_hover = rings.OFF, False, False
    print('Tab: ring and chances off', flush=True)
if os.environ.get('RAV_STEALTH_ROLL'):
    log.stealth_roll = lambda n=int(os.environ['RAV_STEALTH_ROLL']): n
if os.environ.get('RAV_CHARGES_OFF'):
    log.count_charges = lambda entries: None
    print('charges pass off', flush=True)
end = time.time() + secs
while time.time() < end:
    for line in log.lines(show_all):
        print(line, flush=True)
        if out: out.write(line + '\n'); out.flush()
    time.sleep(0.05)
print('writes dropped:', log.guest.dropped)
