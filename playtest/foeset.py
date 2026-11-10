# foeset.py [COMBATANT [race=R] [cls=A,B,C] [lv=A,B,C] [mr=N] [hp=N] [int=N] [eff=ID[:SPELL[:AMOUNT]]] ...]:
# memory only, never save after (2026-11-09, logs/2026-11-09-group-3.md). With no arguments, lists every
# combatant on the map: its creature, name, HP, sheet, race, classes, levels, magic resistance and
# the creature record's six scores (+22h: what the game works out from the sheet's +1Bh and the
# effects), then the table of active effects (owner, caster, spell, effect, handle, charges, amount).
# With a COMBATANT, writes its SHEET (race +18h, classes +21h, levels +24h, magic resistance +29h:
# creatures of one kind share a sheet, so all of them change), its creature's HP (+0) or INT score
# (+25h), and adds effects to the game's table of active effects in owner order (the place the game
# keeps them in: 598:B1h finds an owner's first entry and reads on while the owner is the same), with
# handles from 200 up (no timer: they last until removed, as Feeblemind's or Biofeedback's).
# e.g. python3 foeset.py 22 lv=3,0,0 eff=20 eff=55   (Fire Shield and Blur on combatant 22)
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
sheets = game.far_pointer(g, ds, game.SHEETS_PTR)
creatures = game.far_pointer(g, ds, game.CREATURES_PTR)
base = (gd.load_seg + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
combatants = gd.combatants()


def sheet_at(creature):
    return sheets + struct.unpack_from('<H', gd.creature(creature), 4)[0] * game.SHEET_SIZE


def table():
    n = gd._word(game.EFFECT_COUNT)
    return [g.read(base + i * 10, 10) for i in range(n)]


if len(sys.argv) > 1:
    c = int(sys.argv[1])
    creature = combatants[c]
    s = sheet_at(creature)
    rec = creatures + creature * game.CREATURE_SIZE
    for arg in sys.argv[2:]:
        key, value = arg.split('=')
        if key == 'race':
            g.write(s + game.SHEET_RACE, bytes([int(value)]))
        elif key in ('cls', 'lv'):
            g.write(s + (game.SHEET_CLASSES if key == 'cls' else game.SHEET_LEVELS), bytes(int(x) for x in value.split(',')))
        elif key == 'mr':
            g.write(s + game.SHEET_MAGIC_RESISTANCE, bytes([int(value)]))
        elif key == 'hp':
            g.write(rec, struct.pack('<h', int(value)))
        elif key == 'int':
            g.write(rec + game.CREATURE_ABILITIES + 3, bytes([int(value)]))
        elif key == 'eff':
            parts = [int(x) for x in value.split(':')]
            eid, spell, amount = parts[0], parts[1] if len(parts) > 1 else 0, parts[2] if len(parts) > 2 else 0
            entries = table()
            handles = {e[7] for e in entries if struct.unpack_from('<h', e)[0] == c}
            handle = next(h for h in range(200, 256) if h not in handles)
            at = next((i for i, e in enumerate(entries) if struct.unpack_from('<h', e)[0] > c), len(entries))
            new = struct.pack('<hhhBBBb', c, c, spell, eid, handle, 0, amount)
            entries.insert(at, new)
            g.write(base, b''.join(entries))
            g.write(ds * 16 + game.EFFECT_COUNT, struct.pack('<H', len(entries)))
            print(f'added effect {eid} ({game.EFFECT_NAMES.get(eid, "?")}) on {c}, handle {handle}, entry {at}')
for c, creature in sorted(combatants.items()):
    rec, sh = gd.creature(creature), g.read(sheet_at(creature), game.SHEET_SIZE)
    print(f'{c:3} creature {creature:3} {gd.creature_name(creature):18} HP {struct.unpack_from("<h", rec, 0)[0]:4} '
          f'sheet {struct.unpack_from("<H", rec, 4)[0]:3} race {sh[0x18]} cls {list(sh[0x21:0x24])} lv {list(sh[0x24:0x27])} '
          f'MR {sh[game.SHEET_MAGIC_RESISTANCE]} scores {list(rec[game.CREATURE_ABILITIES:game.CREATURE_ABILITIES + 6])}')
for e in table():
    owner, caster, spell = struct.unpack_from('<hhh', e)
    print(f'  effect: owner {owner} caster {caster} spell {spell} effect {e[6]} ({game.EFFECT_NAMES.get(e[6], "?")}) '
          f'handle {e[7]} charges {e[8]} amount {struct.unpack_from("b", e, 9)[0]}')
