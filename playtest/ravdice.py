# ravdice.py [--all] SECONDS [OUT]: the Loader's dice log for Wake of the Ravager (dsloader.ravlog.RavDiceLog: the
# sequel's layout, its memory read only) attached to the running sequel ($WORK/rav.pid), its lines printed
# (and appended to OUT) as they come, for SECONDS; then how many writes the read-only view dropped. --all: every roll, and each attack's AC
# worked out (base, armour, DEX, other). --numbers: each combatant's number after its name ("Draxan#26"), to
# tell apart foes of one name (as ravitems.py and ravfight.py number them). RAV_RULES_OFF=MASK (game.RULE_* bits, as 0x1000000): those rules off
# after the attach, in the Loader and DSCLOG2's header alike (a control run of a rule the Loader keeps).
# RAV_TAB_OFF=1: the red ring under the enemy chosen with Tab and the chances to hit (its line's, the pointer's) off.
# RAV_FRAMES=1: each THAC0 line followed by the attack set-up's locals it was read from (game.SETUP_*: the THAC0, the
# weapon's bonus, the from-behind and backstab flags, the weapons ready) and the type, range, skill and after-set-up parts.
# RAV_CHARGES_OFF=1: the charges' pass off (DiceLog.count_charges, as before its port: the charge routine's 2d4 behind the
# overlay manager's stub not known, its label "Armor: 7 left" with it), a control.
# RAV_STEALTH_ROLL=N: every hiding and moving silently roll N (stealth.py; 1 to hide every time, for a test).
# RAV_NO_PAN=1: the view not scrolled to an enemy chosen with Tab off the screen (targeting.Targeting._show a no-op: the
# Loader as it was before DSCLOG2's PAN, a control).
# RAV_FOES_SL=1: Tab's list by Shattered Lands' rule (another side than the leader's, not side 4), not the sequel's
# foes (rings.HOSTILE_SIDES: the sides 7-11): a control. With RAV_PREDICT, each change of the list is printed ("Tab
# list: N: Draxan#26 (side 7), ...").
# RAV_NO_SAVES=1: no quick saves (F5, F9) and no autosaves (for a run with memory edits). RAV_NO_SQUARES=1: the
# squares in reach off (R does nothing: the Options tab's switch), RAV_NO_MOVEBACK=1: F10 after the last step left
# the game's (moveback.py off), RAV_NO_USABLE=1: Alt marks nothing (usable.py off): controls.
# RAV_PREDICT=1: with each Tab line, what its chance to hit was made of ("  predict: ..."): the distance in squares,
# the target's facing and the way to the attacker, its AC from the front and behind (GameData.attack_ac), the AC gap
# kept from its last attack (ac_gap) and the game's last AC for it, the effects on it, each swing's THAC0 and AC.
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
if os.environ.get('RAV_NO_PAN'):  # (a control: DSCLOG2's PAN_X and PAN_Y never added to)
    from dsloader import targeting
    targeting.Targeting._show = staticmethod(lambda gd, tsr_hdr, thing: False)
    print('Tab: the view not scrolled to the chosen enemy', flush=True)
if os.environ.get('RAV_FOES_SL'):  # (a control: SL's rule for who is a foe)
    from dsloader import rings
    rings.HOSTILE_SIDES = None
    print('Tab: the list by Shattered Lands\' rule', flush=True)
if os.environ.get('RAV_PREDICT'):  # (Tab's list, printed as it changes)
    from dsloader import rings
    _enemies, _was = rings.enemies, [None]
    def _listed(gd):
        out = _enemies(gd)
        if out != _was[0]:
            _was[0] = out
            line = 'Tab list: %d: %s' % (len(out), ', '.join('%s (side %d)' % (gd.combatant_name(c), gd.creature(
                gd.combatant_creature(c))[game.CREATURE_SIDE]) for c in out))
            print(line, flush=True)
            if out_file_l: out_file_l.write(line + '\n'); out_file_l.flush()
        return out
    out_file_l = out
    rings.enemies = _listed
if os.environ.get('RAV_PREDICT'):  # (what each Tab line's chance was made of: hitchance.predict's inputs)
    from dsloader import hitchance
    _swings = log._swings
    def _detail(attacker, target):
        out = _swings(attacker, target)
        try:
            gd = log.game
            me, it = gd.combatant_creature(attacker), gd.combatant_creature(target)
            facing = gd.facing(it) if it is not None else None
            parts = ['%s THAC0 %d AC %d need %d%s' % (s.weapon, s.thac0, s.ac, s.need,
                     '' if s.behind is None else ' behind %d' % s.behind) for s in out]
            hits = ['%s %d %s' % (h.name, h.thac0, h.parts) for h in gd.weapon_hits(me, unarmed=True)]
            line = ('  predict: %s -> %s: squares %d, facing %s, way %s, AC front %s back %s, gap %s, '
                    'game AC %s, effects on it %s; %s; hits %s' % (
                        gd.combatant_name(attacker), gd.combatant_name(target), hitchance.squares(gd, attacker, target),
                        facing, hitchance.way(gd, target, attacker), gd.attack_ac(it, me, False),
                        gd.attack_ac(it, me, True), log.ac_gap.get(it), log.monster_ac(it),
                        sorted(e.id for e in gd.effects() if e.owner == target), '; '.join(parts), ' | '.join(hits)))
        except Exception as e:  # (a tool's line: never the log's end)
            line = '  predict: (%r)' % e
        if line == _last[0]:  # (the same again: the panel's header asks every few seconds)
            return out
        _last[0] = line
        print(line, flush=True)
        if out_file:
            out_file.write(line + '\n'); out_file.flush()
        return out
    out_file, _last = out, [None]
    log._swings = _detail
if os.environ.get('RAV_FRAMES'):  # (each THAC0 line's set-up locals, as the breakdown read them)
    _breakdown = log._thac0_breakdown
    def _framed(e, thac0, attacker, ac, tc, weapon, mode, item_type=None, skill=('', 0), kit=()):
        text = _breakdown(e, thac0, attacker, ac, tc, weapon, mode, item_type, skill, kit)
        return text + '  [set-up: THAC0 %s, bonus %s, rear %s, backstab %s, ready %s; type %s, mode %s, skill %s, after %s]' % (
            e.parent_local(game.SETUP_THAC0_LOCAL), e.parent_local(game.SETUP_BONUS_LOCAL),
            (e.parent_local(game.SETUP_REAR_LOCAL) or 0) & game.SETUP_FLAG_MASK,
            (e.parent_local(game.SETUP_BACKSTAB_LOCAL) or 0) & game.SETUP_FLAG_MASK,
            e.parent_local(game.SETUP_READY_LOCAL), item_type, mode, skill[1], list(kit))
    log._thac0_breakdown = _framed
if os.environ.get('RAV_NO_SAVES'):
    log.quicksave.keys = log.quicksave.auto = False
    print('quick saves and autosaves off', flush=True)
if os.environ.get('RAV_NO_SQUARES'):
    log.show_squares = False
    print('squares in reach off', flush=True)
if os.environ.get('RAV_NO_MOVEBACK'):
    log.move_back = False
    print('F10 after the last step: the game\'s', flush=True)
if os.environ.get('RAV_NO_USABLE'):
    log.show_usable = False
    print('Alt marks nothing', flush=True)
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
