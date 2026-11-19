# hitcheck.py [ATTACKER]: the chance to hit before the swing (dsloader/hitchance.py), read-only: for
# whoever's turn it is (or combatant ATTACKER) against every enemy, what the Loader would say on
# the "Chosen with Tab" line (without the dice log's AC gap: this isn't the session's Loader), with
# what it is made of: the squares between them, the target's facing (None: nowhere yet), the way
# from the target to the attacker, the AC the Loader counts from the front and from behind, THAC0
# and the need for each weapon. To hold against the dice log's "needs N+" for the attack after it.
# Not the session's Loader: no dance, no Wild Fighting, no AC gap (a Battle Dancer read 1 off here).
import os, re, struct, sys
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import dicelog, hitchance, launch, rings, stealth
gd.rules = rules = game.rules_from_settings(launch.load_settings())
low = g.read(0, dicelog.CONVENTIONAL_AND_UPPER)
hdr = next((m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), low) if m.start() % 16 == 0), None)
me = int(sys.argv[1]) if len(sys.argv) > 1 else gd.whose_turn()
hidden = bool(hdr is not None and me < 4 and struct.unpack('<H', g.read(hdr + stealth.TSR_STEALTH, 2))[0] >> me & 1)
mine = gd.combatant_creature(me)
print(f"attacker {me} {gd.creature_name(mine)} square {stealth.square(gd, me)} hidden {hidden} fight_on {int(gd.fight_on())}")
for h in gd.weapon_hits(mine, unarmed=True):
    print(f"  {h.name}: THAC0 {h.thac0} {h.parts} slot {h.slot} type {h.type} weight {h.weight} range {h.range}")
for foe in rings.enemies(gd):
    it = gd.combatant_creature(foe)
    swings = hitchance.predict(gd, me, foe, rules, hidden)
    print(f"{foe} {gd.creature_name(it)} square {stealth.square(gd, foe)} squares {hitchance.squares(gd, me, foe)} "
          f"facing {gd.facing(it)} way {hitchance.way(gd, foe, me)} AC {gd.attack_ac(it, mine, False)}/"
          f"{gd.attack_ac(it, mine, True)} from behind: {hitchance.line(swings)}")
    for s in swings:
        print(f"    {s.weapon}: THAC0 {s.thac0} AC {s.ac} need {s.need} {s.how} behind {s.behind} {s.behind_how} auto {s.auto}")
