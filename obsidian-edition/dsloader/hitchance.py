"""The chance to hit shown before the swing: what the d20 must show for the party member whose
turn it is to hit the enemy chosen with Tab (targeting.py), worked out as the game's attack does.

Nothing here writes to the game or asks DSCLOG for anything: predict() reads what the game's
attack set (58019h) reads, in the order it does.

- THAC0 with each ready weapon, before the target counts: GameData.weapon_hits (STR or DEX, the
  attacker's effects, the weapon, two weapons, kits, weapon specialization).
- The target's part of THAC0: its Blur (2 worse), its Fogbolt (2 better), its Golden Girdle of
  Urnst against a sword in melee (3 worse); from behind 2 better (a Rescuer's 1), a backstab 2 more.
- The target's AC against this attacker: GameData.attack_ac (the game's AC routine, 58DD3h and
  7C557h), and what the dice log saw the game add to that the last time the target was attacked
  (DSCLOG's part: a kit's, rings of protection, the Boots of Speed).
- Which weapon swings: the game's picker (5900Ah) takes the weapons in hand of range 1 for an
  attack at a distance of 1 or less, the missile weapon (range above 1) for one farther; Enter and
  a click walk a member up to fight hand to hand, the attack pointer shoots. So next to the
  target the melee weapons are given, farther off those and the shot.
- From behind: the target's facing (GameData.facing) is the way to its round's first attacker;
  an attacker in the square opposite is behind it. Facing nowhere yet, the first attacker is in
  front. Next to the target the answer is known; farther off (the member walks up, and where it
  ends isn't known) both numbers are given. A missile is never from behind by the facing
  (DSCLOG's MISSILE_REAR), a hidden thief's first attack always is (its backstab by the game's
  conditions, DSCLOG's PROBE_STEALTH), and a Girdle of Back Defense takes both back. A hidden
  one's later swings in the round are judged as anyone's (DSCLOG's REAR_FRESH, #116).
- A 20 always hits and a 1 always misses (dicelog.hit_chance); a held target is hit whatever the
  roll (AD&D's held target, RULE_HELD, always on).
"""

import struct
from typing import List, NamedTuple, Optional

from . import game, kits, specialize, stealth, worldgear

WAIST_SLOT = game.EQUIP_SLOTS.index("waist")
THIEF_FLAG = 0x400  # (the sheet's class flags, +12h: a thief)
STAB_WEIGHT = 40  # (a backstab's weapon weighs this or less: the type's word +4)
BLUR, BACKSTAB = 55, 2
# the game's eight directions (its routine 96C:009Bh, 0EB5Bh: the table at 3779:0000h), by the
# signs of the squares' difference (x, y): 0 north, then clockwise; a target faces its attacker,
# and one in the opposite direction is behind it
WAYS = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3, (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7, (0, 0): 0}
EIGHT_WAYS = 0x1F8  # DS word: 1 for the eight directions (as the game starts with), else only four


class Swing(NamedTuple):
    weapon: str  # the weapon's name ("unarmed" with none)
    missile: bool
    need: int  # what the d20 must show, as things stand (THAC0 less AC)
    how: str = ""  # "from behind", "a backstab" or "unseen" when NEED is such an attack's
    behind: Optional[int] = None  # the need from behind instead, where that depends on where the
    # attacker ends its walk (melee from farther off, the target facing a way already)
    behind_how: str = ""  # "from behind" or "a backstab", for BEHIND
    auto: Optional[str] = None  # why it hits whatever the roll (a held target: "Paralyzed", "Out Cold")
    thac0: int = 0  # (NEED's parts: THAC0 after the target's part, and the AC)
    ac: int = 0


def chance(need: int) -> int:
    """The chance (percent) of a d20 reaching NEED: a 20 always hits, a 1 always misses (the
    game's attack, 589E9h; as dicelog.hit_chance)."""
    return 5 * sum(1 for d in range(1, 21) if d == 20 or (d != 1 and d >= need))


def squares(gd, a: int, b: int) -> int:
    """The distance between combatants A and B as the game's routine (1A0A:2BA5h) counts it: the
    least between their footprints, in squares by 898:000Ch (the smallest s with s x s + s at least
    dx x dx + dy x dy: next to each other, diagonally too, 1)."""
    fa = stealth.footprint(gd, a, gd.combatant_creature(a))
    fb = stealth.footprint(gd, b, gd.combatant_creature(b))
    dx, dy = max(fb[0] - fa[2], fa[0] - fb[2], 0), max(fb[1] - fa[3], fa[1] - fb[3], 0)
    s = 0
    while s * s + s < dx * dx + dy * dy:
        s += 1
    return s


def way(gd, target: int, attacker: int) -> int:
    """The direction from combatant TARGET's square to ATTACKER's as the game's routine (0EB5Bh)
    gives it: by the signs of the difference alone (WAYS: straight north, east, south or west only
    with the other difference 0), whatever the distance; with the game's four directions
    (EIGHT_WAYS not 1) the nearer of north, east, south and west."""
    (tx, ty), (ax, ay) = stealth.square(gd, target), stealth.square(gd, attacker)
    dx, dy = ax - tx, ay - ty
    if struct.unpack("<H", gd.guest.read(gd.ds * 16 + EIGHT_WAYS, 2))[0] != 1:
        return (2 if dx >= 0 else 6) if abs(dx) >= abs(dy) else (4 if dy > 0 else 0)
    return WAYS[((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))]


def _on(effects, combatant: int, effect: int) -> bool:
    return any(e.owner == combatant and e.id == effect for e in effects)


def predict(gd, attacker: int, target: int, hidden: bool = False, ac_gap: int = 0) -> List[Swing]:
    """What combatant ATTACKER (a party member) needs to hit combatant TARGET with each weapon it
    would swing, as things stand, with the rules always on (game.RULES_ALWAYS: Thieves as in AD&D,
    the held target). HIDDEN the attacker hidden in shadows (its next attack from behind), AC_GAP what the game's AC for the target was above
    GameData.attack_ac's the last time it was attacked (0 for one not attacked yet). [] when
    either isn't a creature."""
    me, it = gd.combatant_creature(attacker), gd.combatant_creature(target)
    if me is None or it is None:
        return []
    front, back = gd.attack_ac(it, me, False), gd.attack_ac(it, me, True)
    if front is None or back is None:
        return []
    effects = gd.effects()
    far = squares(gd, attacker, target)
    near = far <= 1
    hits = gd.weapon_hits(me, unarmed=True)
    # (in the order the game's attack swings them: the creature's items' own, not right hand first)
    swings = sorted((h for h in hits if h.slot != game.MISSILE_SLOT), key=lambda h: h.order)
    if not near:
        swings += [h for h in hits if h.slot == game.MISSILE_SLOT and h.range >= far]
    sheet = gd.sheet(me)
    thief = len(sheet) >= game.SHEET_SIZE and struct.unpack_from("<H", sheet, game.SHEET_FLAGS)[0] & THIEF_FLAG
    kids = gd.kit_ids(me)
    rear_hit = min((kits.rear_to_hit(k) for k in kids), default=kits.REAR)
    guarded = gd.wears_type(it, game.BACK_GIRDLE_TYPE, WAIST_SLOT)  # (a Girdle of Back Defense)
    facing = gd.facing(it)
    held = gd.helpless(target)
    out = []
    for n, h in enumerate(swings):
        missile = h.slot == game.MISSILE_SLOT
        thac0 = h.thac0 + 2 * _on(effects, target, BLUR) - 2 * _on(effects, target, game.FOG_EFFECT)
        if not missile and h.type >= 0 and specialize.kind_of(h.type) in worldgear.SWORD_KINDS \
                and gd.wears_type(it, game.URNST_GIRDLE_TYPE, WAIST_SLOT):
            thac0 += worldgear.URNST_AC
        # a backstab by the game's conditions (58314h: a thief, in melee, the weapon's weight) and
        # DSCLOG's (THIEF_REAR: not in heavy armour; KIT_REAR: not a Military Scout; STAB_FIRST:
        # Thieves as in AD&D, always on, only the round's first attack)
        stab = bool(thief) and not missile and h.type >= 0 and h.weight <= STAB_WEIGHT \
            and not gd.thief_heavy(me) and all(kits.backstabs(k) for k in kids) and not n
        rear_thac0 = thac0 - rear_hit - (BACKSTAB if stab else 0)
        behind_how = "a backstab" if stab else "unseen" if missile else "from behind"
        behind = rear_thac0 - (back + ac_gap)
        plain = Swing(h.name, missile, thac0 - (front + ac_gap), auto=held, thac0=thac0, ac=front + ac_gap)
        rear = Swing(h.name, missile, behind, behind_how, auto=held, thac0=rear_thac0, ac=back + ac_gap)
        if guarded:
            out.append(plain)
        elif hidden and (not n or missile):
            # (hidden: the first swing, or the shot, from behind; a later melee swing in the round
            # as anyone's, by the facing: DSCLOG's REAR_FRESH, #116. Before it, Seneca's
            # Shadowseeker after her Hayneedle's backstab kept the first's flags: 2 worse to hit
            # than a plain swing, yet the AC from behind; 2026-11-17)
            out.append(rear)
        elif missile or facing is None:
            out.append(plain)
        elif near:
            out.append(rear if way(gd, target, attacker) == (facing + 4) % 8 else plain)
        else:
            out.append(plain._replace(behind=behind, behind_how=behind_how))
    return out


def _needs(need: int) -> str:
    return "hits on anything but a 1" if need <= 2 else "only a 20 hits" if need > 20 else f"needs {need}+"


def _short(need: int) -> str:
    return "20" if need > 20 else f"{max(need, 2)}+"


def _one(s: Swing) -> str:
    if s.auto:
        return f"hits whatever the roll ({s.auto})"
    text = f"{_needs(s.need)} ({chance(s.need)}%)" + (f" {s.how}" if s.how else "")
    if s.behind is not None:
        text += f", {s.behind_how} {_short(s.behind)} ({chance(s.behind)}%)"
    return text


def line(swings: List[Swing]) -> str:
    """For the dice log's "Chosen with Tab" line: "needs 14+ (35%)"; "needs 14+ (35%), from behind
    10+ (55%)" where the walk decides; each weapon named when they differ ("Bone Long Sword needs
    14+ (35%); Short Bow needs 12+ (45%)"). "" with nothing to say."""
    texts = [_one(s) for s in swings]
    if len(set(texts)) <= 1:
        return texts[0] if texts else ""
    named = []
    for s, text in zip(swings, texts):  # (two of the same weapon with the same numbers: once)
        if f"{s.weapon} {text}" not in named:
            named.append(f"{s.weapon} {text}")
    return "; ".join(named)


def brief(swings: List[Swing]) -> str:
    """For the panel's header while an enemy is chosen, in place of the round's line (the header
    is 103 pixels of the game's font: "Round 2: Gerakis" nearly fills it): the first swing's (the
    weapon Enter attacks with). "Needs 14+ (35%)"; from behind "Behind: 10+ (55%)" ("Backstab: 8+
    65%", "Unseen: ..."); where the walk decides "14+ 35%, behind 10+" (the header's fit drops the
    part after the comma if it must); a held target's "Hits (Paralyzed)"."""
    if not swings:
        return ""
    s = swings[0]
    if s.auto:
        return f"Hits ({s.auto})"
    if s.behind is not None:
        return f"{_short(s.need)} {chance(s.need)}%, behind {_short(s.behind)}"
    if s.how == "a backstab":
        return f"Backstab: {_short(s.need)} {chance(s.need)}%"
    head = {"from behind": "Behind:", "unseen": "Unseen:"}.get(s.how, "Needs")
    return f"{head} {_short(s.need)} ({chance(s.need)}%)"


def over(s: Swing) -> str:
    """For the label over the enemy under the pointer (hover.py), one swing's, within a label's
    128 pixels of the game's font: "12+ (45%)"; next to the enemy and behind it "Behind 10+
    (55%)" ("Backstab 8+ (65%)", "Unseen 10+ (55%)"); where the walk decides "14+ (35%), behind
    10+" (", backstab 8+"); a held target's, with the rule for it, "Hits"."""
    if s.auto:
        return "Hits"
    head = {"a backstab": "Backstab ", "from behind": "Behind ", "unseen": "Unseen "}.get(s.how, "")
    text = f"{head}{_short(s.need)} ({chance(s.need)}%)"
    if s.behind is not None:
        text += f", {'backstab' if s.behind_how == 'a backstab' else 'behind'} {_short(s.behind)}"
    return text
