"""Worn equipment shown on a party member's map sprite, from where spriteparts finds the parts of
each frame (set by hand where finding them goes wrong). The artist's pixels are kept wherever they
can be: what is worn on the body recolours the character's own picture, what is carried is drawn
on it.

  * Weapons and shields: in a fight in the hands (each pose's grip set by hand); walking, a shield
    on the arm (from the side, on the far arm held forward of the chest) and a one-handed weapon
    worn at the belt like a scabbard; a bow and quiver on the back, a sling or chatkcha at the hip:
    drawn, in their material's colours (Kreenfang's and Shadowseeker's blades in their icons'; an
    axe's or mace's haft wood, its head solid; on a bigger figure only the haft is longer).
  * Body armour (chest, arms, legs), boots and belts: the character's own clothing, feet or waist
    recoloured toward the material, shade for shade.
  * Helms: a circlet at the brow, blended into the hair under it.
  * Cloaks: the human and half-elf woman's own cloak, frame by frame, fitted to the wearer.

The colours are muted ones from the parts of the palette no region changes (30-79 and 128-222), so
the gear sits in the picture the way the game's own colours do. A thri-kreen shows only weapons and
shields (all it can use). armed() makes one frame.
"""

import math
from bisect import bisect_right
from typing import Callable, Dict, FrozenSet, List, NamedTuple, Optional, Tuple

from . import classoutfits, game, halfelf, spritebelts, spritebracers, spritegreaves, spriteparts as sp

Rows = sp.Rows

# Materials (the item type's +8h, low nibble, as game.MATERIALS): (outline, body, light)
MATERIAL_COLOURS = {
    0: (207, 205, 206),  # wood: dark faded brown
    1: (206, 62, 63),  # bone: weathered ivory
    2: (210, 212, 213),  # stone: grey
    3: (24, 18, 26),  # obsidian: near-black, its edges a lighter grey (to show on dark clothes)
    4: (22, 25, 27),  # metal: dull blue-grey iron
    5: (207, 205, 194),  # leather
}
FLAME = (248, 241, 242)  # the Flame Blade: the fire colours the game cycles
# The Loader's named weapons (icons.which), their blades in their icons' colours: Kreenfang's two
# in the fire colours, Shadowseeker's in night steel (dark blue-greys no region changes)
BLADE_COLOURS: Dict[str, Tuple[int, int, int]] = {"Kreenfang": FLAME, "Shadowseeker": (17, 18, 21)}
# Any other magic weapon (a plus or a power: sprites.worn's MAGIC): its edge, the shape's lightest
# cells, in the fire colours the game cycles, stepping along them, so it shimmers as its icon does
MAGIC = "magic"
GLINT = tuple(range(240, 249))
# The colours the game cycles on the map (its colour cycler's four runs, the same in every area's
# palette but for a step or two): a magic item glows in the one nearest its icon's colour (GLOWS'
# index: worn's 4th element, or MAGIC_ARMOUR's GLOW_SHIFT bits for armour)
FIRE_GLOW, GREEN_GLOW, VIOLET_GLOW, BLUE_GLOW = range(4)
GLOWS = (GLINT, (1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 12, 13, 14, 15))
MAGIC_ARMOUR = 0x10000  # (with an armour's item type in armed's ARMOUR: it is magic, and glints)
VEILED_DYE = 1 << 20  # visual variant; the underlying chest item retains its game type
GLOW_SHIFT = 17  # (... in the colours GLOWS[type >> GLOW_SHIFT])
# The other weapons spells make: drawn whole in the colours the game cycles, as the Flame Blade in
# the fire's, in those their icons glow in: Shillelagh (28) the fire's, Spiritual Hammer (30) the blue
SPELL_WEAPONS = {28: FIRE_GLOW, 30: BLUE_GLOW}


def _magic(item: Tuple) -> bool:
    return len(item) > 2 and item[2] == MAGIC


def _glow(item: Tuple) -> Tuple[int, ...]:
    return GLOWS[item[3]] if len(item) > 3 and 0 <= item[3] < len(GLOWS) else GLINT


def glow_for(icon: Rows, colours: Optional[List[Tuple[int, int, int]]] = None) -> int:
    """Which of GLOWS suits an item's ICON: the cycled colours it shines in, as it does in the
    inventory (the Loader's icons: fire, or the water's blue on a tint the game doesn't cycle);
    else the hue its vivid pixels have, each by how vivid (red to yellow fire, green, blue,
    violet; wood's, leather's and bone's browns and tans left out), where they weigh a fifth of
    it or more (not a sword's hilt); else (greys, steel, plain browns) the blue."""
    import colorsys
    colours = colours or _RGB
    shine = [0] * len(GLOWS)
    votes = [0.0] * len(GLOWS)
    total = 0
    for row in icon:
        for p in row:
            if p is None:
                continue
            total += 1
            group = next((i for i, glow in enumerate(GLOWS) if p in glow), None)
            if group is not None:
                shine[group] += 1  # (a shine it already has)
                continue
            if p >= len(colours):
                continue
            r, g, b = colours[p]
            chroma = max(r, g, b) - min(r, g, b)
            if chroma < 60:
                continue  # (greys)
            h, _, _ = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            deg = h * 360
            if 12 <= deg <= 50 and max(r, g, b) < 200:
                continue  # (browns and tans: wood, leather, bone)
            votes[FIRE_GLOW if deg < 70 or deg >= 340 else GREEN_GLOW if deg < 170
                  else BLUE_GLOW if deg < 255 else VIOLET_GLOW] += chroma / 255
    best = max(range(len(GLOWS)), key=lambda i: shine[i])
    if shine[best] >= 3:
        return best
    best = max(range(len(GLOWS)), key=lambda i: votes[i])
    return best if votes[best] >= max(2.0, total / 5) else BLUE_GLOW


def sparkle(rows: Rows, before: Rows, colours: Tuple[int, ...] = GLINT, sparse: bool = False) -> None:
    """Magic worn gear: a scatter of the pixels a piece changed (ROWS against BEFORE) in COLOURS,
    ones the game cycles, on a diagonal (sparser on a piece as large as a cloak); a small piece
    (a circlet, boots) at least every other pixel of it, so it shows."""
    changed = [(x, y) for y, row in enumerate(rows) for x, p in enumerate(row)
               if p is not None and p != before[y][x]]
    sparkle_cells(rows, changed, colours, spacing=11 if sparse else None, sparse=sparse)


def sparkle_cells(rows, changed, colours, spacing=None, sparse=False):
    """Use the game's cycled palette on the visible surface of this item."""
    step = spacing or (5 if len(changed) < 150 else 9)
    picked = [(x, y) for x, y in changed if (x + 2 * y) % step == 0]
    if sparse and changed and not picked:
        # A sliver of fabric needs just one glint, on its lightest visible fold.
        picked = [max(changed, key=lambda xy: (_LIGHT.get(rows[xy[1]][xy[0]], 0), xy))]
    elif not sparse and len(picked) < 2:
        picked = changed[::2]
    for x, y in picked:
        rows[y][x] = colours[(x + y) % len(colours)]

# Shapes, by item type (the game's item type numbers)
DAGGER, SWORD, CLUB, MACE, AXE, GREAT_AXE, POLEARM, GYTHKA, CAHULAKS, STAFF, SHIELD, SLING, BOW, \
    CHATKCHA = ("dagger", "sword", "club", "mace", "axe", "great axe", "polearm", "gythka", "cahulaks",
                "staff", "shield", "sling", "bow", "chatkcha")
WEAPON_SHAPES: Dict[int, str] = {
    17: DAGGER, 33: DAGGER, 84: DAGGER, 94: DAGGER, 97: DAGGER,
    game.SHORT_SWORD_TYPE: SWORD, 45: SWORD, 63: SWORD, 81: SWORD, 85: SWORD, 98: SWORD, 41: SWORD, 50: SWORD, 29: SWORD,
    18: CLUB, 28: CLUB,
    20: MACE, 46: MACE, 30: MACE,
    22: AXE, 2: GREAT_AXE,
    19: POLEARM, 111: POLEARM, 112: POLEARM,
    44: GYTHKA, 21: CAHULAKS, game.METAL_CAHULAKS_TYPE: CAHULAKS, game.OBSIDIAN_CAHULAKS_TYPE: CAHULAKS,
    3: STAFF, 80: STAFF,
    4: SHIELD, 16: SHIELD, 34: SHIELD, 83: SHIELD, game.METAL_SHIELD_TYPE: SHIELD,  # (the last worldgear.py's Ironbulwark)
    0: SLING, 64: SLING, 1: BOW, 69: BOW, 48: CHATKCHA,
    47: SWORD,  # (Dragonsbane, El's Drinker)
    # the Loader's own weapons (game.py): a new warrior's (weaponchoice.py) and the world's
    game.BONE_SHORT_SWORD_TYPE: SWORD, game.OBSIDIAN_SHORT_SWORD_TYPE: SWORD, game.METAL_SHORT_SWORD_TYPE: SWORD,
    game.BONE_AXE_TYPE: AXE, game.OBSIDIAN_AXE_TYPE: AXE,
    game.METAL_DAGGER_TYPE: DAGGER, game.AIR_DAGGER_TYPE: DAGGER, game.BONE_DAGGER_TYPE: DAGGER,
    game.METAL_MACE_TYPE: MACE,
    game.METAL_GREAT_AXE_TYPE: GREAT_AXE, game.BONE_GREAT_AXE_TYPE: GREAT_AXE, game.OBSIDIAN_GREAT_AXE_TYPE: GREAT_AXE,
    game.METAL_PICK_TYPE: POLEARM, game.METAL_POLEARM_TYPE: POLEARM,
}
FLAME_BLADE = 29


def _whole(glow: int) -> Tuple[int, int, int]:
    """A spell weapon's colours (outline, body, light) from a run of cycled ones (GLOWS[GLOW])."""
    shine = GLOWS[glow]
    return FLAME if shine == GLINT else (shine[0], shine[len(shine) // 2], shine[-1])
# Which steps of a shape (_shape) are its blade
BLADE_STEPS = {GYTHKA: lambda step: abs(step) >= 6, SWORD: lambda step: step >= 1, DAGGER: lambda step: step >= 1}
TWO_HANDED = frozenset((GREAT_AXE, POLEARM, GYTHKA, STAFF, BOW))

# Each pose's grip, by hand: the angle the weapon points (degrees, 0 to the right of the picture,
# 90 straight down) and whether it is behind the body. Set by hand from the walking and combat
# frames (the same poses for every model); MODEL_GRIPS changes one for one model.
Grip = Tuple[float, bool]
WALK_GRIPS: List[Dict[str, Grip]] = [
    {"right": (112, False), "left": (68, False)},  # 0 front, standing: hanging down and outward
    {"right": (72, False), "left": (108, False)},  # 1 back
    {"right": (58, False), "left": (122, True)},  # 2 side: the near hand forward and down
] + [{"right": (112, False), "left": (68, False)}] * 4 \
  + [{"right": (72, False), "left": (108, False)}] * 4 \
  + [{"right": (58, False), "left": (122, True)}] * 4
# Walking, a one-handed weapon is not in the hand but worn at the belt by that hand's hip, the hilt
# above the belt and the rest hanging down and back, as a scabbard (and a club or an axe through a
# loop): its angle, by facing, for each side
SHEATHED: Dict[Optional[str], Dict[str, Grip]] = {
    sp.FRONT: {"right": (104, False), "left": (76, False)},  # (down the outside of the thigh)
    sp.BACK: {"right": (76, False), "left": (104, False)},
    sp.SIDE: {"right": (118, False), "left": (112, True)},  # (facing right: back is to the left)
}
HILT = 2  # (the grip and pommel above the belt)
SHEATHED_SCALE = 0.8  # (clear of the ground)
# Two-handed weapons (staffs, polearms, the gythka, the great axe) are carried upright in the right
# hand, the butt by the feet: their angle, by facing, in place of the hand's own
UPRIGHT: Dict[Optional[str], Grip] = {sp.FRONT: (262, False), sp.BACK: (278, False), sp.SIDE: (285, False)}
# The combat poses (the same for every model): which hand swings (the highest, lowest, leftmost or
# rightmost of the hands found) and at what angle, then the other hand's angle (a shield or a
# second weapon). Three frames each way: the wind-up, the strike, the follow-through; then the
# hit (12). Set by hand from the frames.
CombatGrip = Tuple[str, float, float]
COMBAT_POSES: List[Optional[CombatGrip]] = [
    ("highest", 285, 100),  # 0 toward the viewer: raised over the head
    ("highest", 200, 80),  # 1 the swing across
    ("highest", 215, 90),  # 2 followed through, low and out
    ("highest", 275, 100),  # 3 away: raised
    ("highest", 320, 100),  # 4 the swing
    ("lowest", 120, 80),  # 5 followed through
    ("highest", 250, 110),  # 6 to the side: raised behind
    ("rightmost", 10, 120),  # 7 thrust forward
    ("rightmost", 55, 120),  # 8 followed through, down and forward
    None, None, None,  # 9-11 the bow
    ("lowest", 100, 80),  # 12 hit
    None,  # 13 dead
]
COMBAT_GRIPS: List[Optional[Dict[str, Grip]]] = [None] * sp.COMBAT_FRAMES  # (by hand, per model, where needed)
MODEL_GRIPS: Dict[Tuple[int, bool, int], Dict[str, Grip]] = {}


# Weapons in proportion to the body: a half-giant's bigger, a halfling's and a dwarf's smaller
MODEL_SCALE = {2072: 1.35, 2074: 1.35, 2068: 0.85, 2070: 0.85, 2053: 0.9, 2055: 0.9}


def grip(model: int, frame: int, combat: bool, hand: str) -> Optional[Grip]:
    own = MODEL_GRIPS.get((model, combat, frame), {})
    if hand in own:
        return own[hand]
    table = COMBAT_GRIPS if combat else WALK_GRIPS
    poses = table[frame] if 0 <= frame < len(table) else None
    return poses.get(hand) if poses else None


def padded(rows: Rows, pad: int) -> Rows:
    """ROWS with PAD clear pixels on the left, right and top (room for what is drawn)."""
    width = len(rows[0]) if rows else 0
    return [[None] * (width + 2 * pad) for _ in range(pad)] + [[None] * pad + list(r) + [None] * pad for r in rows]


def _put(rows: Rows, x: float, y: float, colour: int, behind: bool, body: Rows) -> None:
    x, y = int(round(x)), int(round(y))
    if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
        if behind and body[y][x] is not None:
            return  # (the body is in front)
        rows[y][x] = colour


# Where a headed weapon's head starts (steps from the hand): drawn larger, only its haft is longer
HEADS = {AXE: 4, GREAT_AXE: 5, MACE: 4}

# Each shape along its line: (from, to) steps from the hand, and the half-width at each step, with
# which colour, as a list of (step, offsets across, colour index: 0 outline, 1 body, 2 light; WOOD +
# one of those, the wood's colour whatever the weapon's material: an axe's haft)
WOOD = 3
def _shape(shape: str) -> List[Tuple[int, List[Tuple[int, int]]]]:
    if shape == DAGGER:
        return [(0, [(-1, 0), (0, 0), (1, 0)])] + [(s, [(0, 2), (1, 0)]) for s in range(1, 4)] + [(4, [(0, 1)])]
    if shape == SWORD:
        return [(0, [(-1, 0), (0, 0), (1, 0), (2, 0)])] + [(s, [(0, 2), (1, 1)]) for s in range(1, 7)] \
            + [(7, [(0, 1), (1, 0)]), (8, [(0, 0)])]
    if shape == CLUB:
        return [(s, [(0, 1), (1, 0)]) for s in range(-1, 3)] + [(s, [(-1, 0), (0, 2), (1, 1), (2, 0)]) for s in range(3, 6)] \
            + [(6, [(0, 0), (1, 0)])]
    if shape == MACE:  # (a wooden haft, a solid round head)
        return [(s, [(0, WOOD + 1)]) for s in range(-1, 4)] + [
            (4, [(-1, 0), (0, 1), (1, 0)]), (5, [(-2, 0), (-1, 1), (0, 2), (1, 1), (2, 0)]),
            (6, [(-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)]), (7, [(-1, 0), (0, 0), (1, 0)])]
    if shape == AXE:  # (a wooden haft, the head a solid wedge on one side, as the game's own axemen's)
        return [(s, [(0, WOOD + 1)]) for s in range(-1, 5)] + [
            (4, [(-1, 0), (1, 0), (2, 0)]), (5, [(-1, 0), (0, 1), (1, 2), (2, 2), (3, 0)]),
            (6, [(-1, 0), (0, 1), (1, 1), (2, 1), (3, 0)]), (7, [(0, 0), (1, 0), (2, 0)])]
    if shape == GREAT_AXE:  # (a longer haft, a head each side)
        return [(s, [(0, WOOD + 1)]) for s in range(-4, 6)] + [
            (5, [(-2, 0), (-1, 0), (1, 0), (2, 0)]), (6, [(-3, 0), (-2, 2), (-1, 1), (0, 1), (1, 2), (2, 2), (3, 0)]),
            (7, [(-3, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 0)]), (8, [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0)])]
    if shape == POLEARM:
        return [(s, [(0, 1)]) for s in range(-5, 9)] + [(9, [(0, 2), (1, 0)]), (10, [(0, 2), (1, 0)]), (11, [(0, 0)])]
    if shape == GYTHKA:
        return [(s, [(0, 1)]) for s in range(-5, 6)] + [(6, [(0, 2), (1, 0)]), (7, [(0, 0)]),
                                                        (-6, [(0, 2), (-1, 0)]), (-7, [(0, 0)])]
    if shape == CAHULAKS:  # (a short haft, then a head of four blades, their tips hooked one way)
        return [(0, [(0, 1)]), (1, [(0, 1)]), (2, [(0, 1)]),
                (3, [(-2, 0), (0, 1), (2, 2)]),
                (4, [(-2, 2), (-1, 2), (0, 1), (1, 2), (2, 2)]),
                (5, [(-2, 2), (0, 2), (2, 0)]), (6, [(0, 0)])]
    if shape == STAFF:
        return [(s, [(0, 1)]) for s in range(-6, 9)] + [(9, [(0, 0)]), (-7, [(0, 0)])]
    return []


def draw_weapon(rows: Rows, body: Rows, hand: sp.Point, angle: float, shape: str, colours: Tuple[int, int, int],
                behind: bool, scale: float = 1.0, blade: Optional[Tuple[int, int, int]] = None,
                glint: bool = False, shine: Tuple[int, ...] = GLINT) -> None:
    """SHAPE drawn on ROWS (BODY: the picture without it, for what is in front) from HAND, pointing
    at ANGLE, SCALE times its length; its blade (BLADE_STEPS) in BLADE's colours, if given; with
    GLINT (a magic weapon) its lightest cells in the fire colours the game cycles (a shape with
    none, the staff, every third cell along it)."""
    on_blade = BLADE_STEPS.get(shape, lambda step: False)
    light = 2 if any(c == 2 for _, cells in _shape(shape) for _, c in cells) else None
    dx, dy = math.cos(math.radians(angle)) * scale, math.sin(math.radians(angle)) * scale
    across = (-dy, dx)
    hx, hy = hand
    across = (across[0] / scale, across[1] / scale)  # (only the length scales)
    steps = sorted(_shape(shape), key=lambda c: c[0])
    head = HEADS.get(shape)
    for step, cells in steps:
        for offset, colour in cells:
            if head is not None and step >= head:  # (a head keeps its size: only the haft is longer)
                spots = (step / scale + round(head * (scale - 1)) / scale,)
            else:
                spots = tuple(step + sub for sub in ((0.0, 0.5) if scale > 1 else (0.0,)))  # (no gaps in a longer one)
            for at in spots:
                x = hx + dx * at + across[0] * offset
                y = hy + dy * at + across[1] * offset
                ramp = MATERIAL_COLOURS[0] if colour >= WOOD else blade if blade and on_blade(step) else colours
                if glint and colour < WOOD and (colour == light or light is None and colour == 1 and step % 3 == 0):
                    _put(rows, x, y, shine[(step + offset) % len(shine)], behind, body)
                else:
                    _put(rows, x, y, ramp[colour % WOOD], behind, body)


def draw_hilt(rows: Rows, body: Rows, at: sp.Point, angle: float, colours: Tuple[int, int, int], behind: bool) -> None:
    """A sheathed weapon's grip above AT, opposite the way it hangs (ANGLE): dark, its end lighter."""
    dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for step in range(1, HILT + 1):
        _put(rows, at[0] - dx * step, at[1] - dy * step, colours[0] if step < HILT else colours[1], behind, body)


def _hip(rows: Rows, parts: sp.Parts, hx: int, pad: int) -> sp.Point:
    """Where a weapon is worn by the hand at HX: the side of the torso (not the arm) at the waist,
    on that hand's side; from the side, the middle of the body."""
    y = parts.waist
    if not parts.shoulders or not parts.head:
        return hx, y
    _, sa, sb = parts.shoulders
    middle = (parts.head.left + parts.head.right) / 2 if parts.facing != sp.SIDE else (sa + sb) / 2
    run = _torso_run(rows, y + pad, middle + pad, sa + pad, sb + pad)
    if not run:
        return hx, y
    a, b = run[0] - pad, run[1] - pad
    if parts.facing == sp.SIDE:
        return (a + b) // 2, y + 1
    return (a + 1 if hx < middle else b - 1), y + 1


# In a fight, where the shield is: (x, y, behind the body) on the frame (its forearm, as a hand is
# given: the shield's middle two rows above), by model and frame, set by hand where finding it goes
# wrong; None for none showing.
SHIELD_SPOTS: Dict[Tuple[int, int], Optional[Tuple[int, int, bool]]] = {
    # the human and half-elf man: on the forearm flung up, before the shoulder; from behind, its
    # rim past the body; edge on at the back; raised to the head when hit
    (2095, 2): (13, 10, False), (2095, 5): (22, 13, True), (2095, 7): (6, 12, False), (2095, 12): (16, 6, False),
    # the human and half-elf woman: up to the low hand; past her cloak from behind; before her
    # shoulder when hit
    (2099, 1): (19, 18, False), (2099, 2): (12, 15, False), (2099, 5): (23, 13, True), (2099, 7): (7, 12, False),
    (2099, 12): (14, 9, False),
    # the elves
    (2059, 1): (18, 18, False), (2059, 2): (13, 14, False), (2059, 5): (22, 12, True), (2059, 7): (8, 11, False),
    (2059, 12): (12, 10, False),
    (2061, 1): (18, 16, False), (2061, 2): (12, 15, False), (2061, 7): (7, 12, False),
    # the dwarves (the same fight)
    (2053, 2): (9, 10, False), (2053, 7): (5, 10, False), (2053, 12): (12, 7, False),
    (2055, 2): (9, 10, False), (2055, 7): (5, 10, False), (2055, 12): (12, 7, False),
    # the halflings
    (2068, 2): (9, 10, False), (2068, 7): (5, 10, False), (2068, 12): (12, 7, False),
    (2070, 2): (10, 10, False), (2070, 5): (14, 12, True), (2070, 7): (5, 11, False), (2070, 12): (12, 8, False),
    # the half-giants: from the side on the back, and on the arm flung back
    (2072, 7): (6, 16, False), (2072, 8): (7, 7, False),
    (2074, 7): (6, 16, False), (2074, 8): (7, 7, False),
    # the mul
    (2093, 2): (9, 11, False), (2093, 7): (5, 12, False), (2093, 12): (13, 7, False),
    # the thri-kreen: on an upper arm
    (2097, 0): (6, 14, False), (2097, 12): (16, 10, False),
}


def fight_shield(rows: Rows, model: int, frame: int, parts: sp.Parts,
                 swing: Optional[sp.Point]) -> Optional[Tuple[int, int, bool]]:
    """Where the shield is in a fight frame: on the forearm of the arm that isn't swinging (its
    wristband, the one farthest from the swinging hand's); where that arm is hidden, behind the
    body on that side, at the chest."""
    if (model, frame) in SHIELD_SPOTS:
        return SHIELD_SPOTS[(model, frame)]
    lowest = parts.bottom - 3  # (not a boot's band)
    arms = []
    if sp.MODELS[model][1] == sp.GREY_BANDS:  # (bands at the shoulders, elbows and knees too: the hands)
        arms = list(parts.hands.values())
    else:
        for group in sp._clusters(rows, sp.MODELS[model][1]):
            y = max(gy for _, gy in group)
            if y <= lowest:
                arms.append((round(sum(gx for gx, _ in group) / len(group)), y + 2))
    if swing is not None:
        arms = [a for a in arms if abs(a[0] - swing[0]) + abs(a[1] - swing[1]) > 4]
    if arms:
        far = max(arms, key=lambda a: abs(a[0] - swing[0]) + abs(a[1] - swing[1]) if swing else 0)
        return far[0], far[1], False
    if not parts.shoulders or parts.waist is None:
        return None
    sy, sa, sb = parts.shoulders
    middle = (sa + sb) / 2
    y = (sy + parts.waist) // 2
    run = _torso_run(rows, y, middle, sa, sb)
    if not run:
        return None
    left = swing is not None and swing[0] > middle  # (the other side from the swing)
    return (run[0] if left else run[1]), y + 2, True


SIDE_FAR = "side, far arm"  # (draw_shield: walking from the side, on the arm beyond the body)


def side_shield(rows: Rows, parts: sp.Parts) -> Optional[sp.Point]:
    """Walking from the side, where the shield is: on the far arm, which the body hides, so at the
    front of the chest (facing right: its right edge), where its near half shows past the body."""
    if not parts.shoulders or parts.waist is None:
        return None
    sy, sa, sb = parts.shoulders
    y = (sy + parts.waist) // 2 + 1
    run = _torso_run(rows, y, (sa + sb) / 2, sa, sb)
    if not run:
        return None
    return run[1] + 2, y + 2  # (held forward of the chest; as a hand is given: the shield's middle two rows above)


def draw_shield(rows: Rows, body: Rows, hand: sp.Point, facing: Optional[str], colours: Tuple[int, int, int],
                behind: bool, scale: float = 1.0, glint: bool = False, shine: Tuple[int, ...] = GLINT) -> None:
    """A round shield on the forearm (about 7 by 9 pixels on a human): its face, rim and boss from
    the front, its strapped back from behind, edge on from the side; on the far arm from the side
    (SIDE_FAR), turned partly toward us, behind the body with its front half showing. With GLINT
    (a magic shield) its light and every third pixel of its rim in the fire colours (GLINT)."""
    outline, fill, light = colours
    hx, hy = hand
    rx, ry = 3.4 * scale, 4.4 * scale
    cx, cy = hx, hy - 2 * scale  # (on the forearm, above the hand)
    if facing == sp.SIDE:
        rx = 1.2 * scale
    elif facing == SIDE_FAR:
        rx = 3.0 * scale
    for dy in range(-int(ry) - 1, int(ry) + 2):
        for dx in range(-int(rx) - 1, int(rx) + 2):
            d = (dx / rx) ** 2 + (dy / ry) ** 2
            if d > 1.0:
                continue
            edge = d > 0.6 if facing != sp.SIDE else abs(dx) >= rx - 0.6
            if facing == SIDE_FAR:
                edge = d > 0.55
            if edge:
                c = outline
            elif facing == sp.FRONT and abs(dx) <= 0 and abs(dy) <= 0:
                c = light  # the boss
            elif facing == sp.FRONT and dx < 0 and dy < 0 and d < 0.35:
                c = light  # light on the upper left, as the game's pictures have it
            elif facing == sp.BACK and dy in (-1, 1):
                c = outline  # the straps on its back
            else:
                c = fill
            if glint and (c == light or c == outline and edge and (dx + dy) % 3 == 0):
                c = shine[(dx + dy) % len(shine)]
            _put(rows, cx + dx, cy + dy, c, behind, body)


# On the back: the bow's stave and string, the quiver's leather and the arrows' fletching
STAVE, STRING = (207, 205), 213
QUIVER, FLETCHING = (207, 205, 194), (215, 196)


def _line(a: Tuple[float, float], b: Tuple[float, float]) -> List[Tuple[float, float]]:
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    return [(a[0] + (b[0] - a[0]) * i / max(1, n - 1), a[1] + (b[1] - a[1]) * i / max(1, n - 1)) for i in range(n)]


def draw_back_gear(rows: Rows, body: Rows, parts: sp.Parts, pad: int, bow: bool, quiver: bool,
                   at_hip: Optional[Tuple[int, int, int]] = None, missile_shape: Optional[str] = None) -> None:
    """A bow and a quiver on the back (across it from behind; their tops past the shoulders and a
    strap across the chest from the front; hanging behind the back from the side), and a sling or
    chatkcha at the hip (AT_HIP: its colours)."""
    if not parts.shoulders or parts.waist is None:
        return
    sy, sa, sb = parts.shoulders
    sy, sa, sb, waist = sy + pad, sa + pad, sb + pad, parts.waist + pad
    behind = parts.facing != sp.BACK
    if parts.facing == sp.SIDE:  # (facing right: the back is on the left)
        bow_line = _line((sa + 1, sy - 4), (sa - 1, waist + 4))
        quiver_at = (sa, sy - 3)
    else:
        bow_line = _line((sb - 1, sy - 4), (sa + 1, waist + 4)) if parts.facing == sp.BACK else             _line((sa + 1, sy - 4), (sb - 1, waist + 4))
        quiver_at = (sa + 2, sy - 3) if parts.facing == sp.BACK else (sb - 2, sy - 3)
    if bow:
        n = len(bow_line)
        for i, (x, y) in enumerate(bow_line):  # the stave bowed out, the string straight
            bulge = math.sin(math.pi * i / max(1, n - 1)) * 1.5
            _put(rows, x - bulge, y - bulge * 0.5, STAVE[i % 2], behind, body)
            _put(rows, x + 1, y, STRING, behind, body)
    if quiver:
        qx, qy = quiver_at
        for dy in range(0, 8):
            _put(rows, qx, qy + dy, QUIVER[0], behind, body)
            _put(rows, qx + 1, qy + dy, QUIVER[1 if dy % 3 else 2], behind, body)
        for dx in (0, 1):  # the fletching standing out of it
            _put(rows, qx + dx, qy - 1, FLETCHING[dx], behind, body)
            _put(rows, qx + dx, qy - 2, FLETCHING[0], behind, body)
    if (bow or quiver) and parts.facing == sp.FRONT:  # the strap across the chest
        for x, y in _line((sb - 1, sy), (sa + 1, waist)):
            _put(rows, x, y, QUIVER[0], False, body)
    if at_hip:
        side = sa if parts.facing != sp.BACK else sb
        # Fasten the pouch or throwing blade to the visible waist rather
        # than projecting the shoulder width down to belt height.
        belt = [x for x, p in enumerate(body[waist]) if p is not None]
        if belt:
            side = min(belt, key=lambda x: abs(x - side))
        hip_pixels = ((0, 0, 0), (0, 1, 1), (0, 2, 1), (-1, 2, 0), (1, 2, 0), (0, 3, 0))
        if missile_shape == CHATKCHA:
            hip_pixels = ((0, 0, 0), (0, 1, 1), (-1, 2, 2), (0, 2, 1), (1, 2, 0), (-2, 3, 0))
        for dx, dy, c in hip_pixels:
            _put(rows, side + dx, waist + dy, at_hip[c], False, body)
    # long hair falls over what is on the back
    for x, y in parts.hair:
        if 0 <= y + pad < len(rows) and 0 <= x + pad < len(rows[y + pad]):
            rows[y + pad][x + pad] = body[y + pad][x + pad]


# Helms, worn as circlets and headdresses (the hair and face showing): a band round the head at
# the brow, in the helm's material's faded colours, and its ornament. Item type: style.
FEATHER, STONE, SPIKES, CIRCLET, CROWN = "feather", "stone", "spikes", "circlet", "crown"
HELMS: Dict[int, str] = {5: FEATHER, 109: FEATHER, 89: STONE, game.BONE_HELM_TYPE: SPIKES,
                         game.CIRCLET_TYPE: CIRCLET, game.CROWN_TYPE: CROWN}  # (the last two worldgear.py's)
HELM_COLOURS = {  # dark to light, close in tone (the hair's own shading showing through them)
    FEATHER: (204, 207, 205, 194),  # faded leather
    STONE: (210, 211, 212, 24),  # dull iron
    SPIKES: (207, 194, 206, 213),  # weathered bone
    CIRCLET: (213, 214, 215, 216),  # silver (Arrowbane)
    CROWN: (64, 65, 65, 45),  # gold (the Sunking Crown)
}
CIRCLET_STONE = 243  # Arrowbane's stone: the fire colours' brightest
FEATHER_GREYS, STONE_RED = (210, 212, 211), 195

_LIGHT: Dict[int, float] = {}
_RGB: List[Tuple[int, int, int]] = []


def set_palette(colours: List[Tuple[int, int, int]]) -> None:
    """The palette (art.palette_colours): each colour's brightness, for blending a helm into the
    hair under it."""
    _LIGHT.clear()
    _RGB[:] = list(colours)
    _LIGHT.update({i: (0.3 * r + 0.59 * g + 0.11 * b) / 255 for i, (r, g, b) in enumerate(colours)})


# The circlet's half-width round each model's head (the head's own, not its hair's), by hand
CIRCLET_HALF = {2072: 4, 2074: 4}  # (3 for the rest)


def draw_helm(rows: Rows, parts: sp.Parts, item_type: int, pad: int, model: int = 0) -> None:
    """A circlet on the (padded) picture ROWS: a band round the head at the brow, as wide as the
    head itself, its ends curving round the temples (from the side, toward the back of the head),
    blended into what is under it: each pixel the helm's shade as light as the hair or skin it
    covers, no outline; and the helm's ornament: a short feather, a small stone at the front, or
    low spikes of bone over the hair."""
    style = HELMS.get(item_type)
    if style is None or not parts.head:
        return
    shades = HELM_COLOURS[style]
    h = parts.head
    half = CIRCLET_HALF.get(model, 3)
    y = h.brow + pad
    if parts.facing == sp.SIDE:  # (facing right: the forehead at the head's right)
        front = h.right + pad - 1
        a, b = front - 2 * half, front
    else:
        middle = (h.left + h.right) // 2 + pad
        a, b = middle - half, middle + half

    def blend(x, yy, lift=0.0):
        under = rows[yy][x]
        light = _LIGHT.get(under, 0.5) if under is not None else 0.5
        i = min(len(shades) - 1, max(0, int((light * 1.8 + lift) * (len(shades) - 1) + 0.5)))
        rows[yy][x] = shades[i]
    cells = []
    for x in range(a, b + 1):
        if parts.facing == sp.SIDE:
            dy = 1 if x < a + (b - a) // 3 else 0
        else:
            dy = 1 if x in (a, b) else 0
        if 0 <= y + dy < len(rows) and 0 <= x < len(rows[y + dy]) and rows[y + dy][x] is not None:
            cells.append((x, y + dy))
    if not cells:
        return
    for x, yy in cells:
        blend(x, yy, 0.1)
    xs = [x for x, _ in cells]
    first, last = min(xs), max(xs)
    centre = (first + last) // 2 if parts.facing != sp.SIDE else last - 1
    if style in (SPIKES, CROWN):
        for x in ([first + 1, centre, last - 1] if parts.facing != sp.SIDE else [centre - 2, centre]):
            tall = 2 if x == centre else 1
            for k in range(1, tall + 1):
                if rows[y - k][x] is None:
                    rows[y - k][x] = shades[1 if k == tall else 2]
                else:
                    blend(x, y - k, 0.15)
    elif style in (STONE, CIRCLET) and parts.facing in (sp.FRONT, sp.SIDE):
        rows[y][centre] = STONE_RED if style == STONE else CIRCLET_STONE
    elif style == FEATHER:
        x = centre - (2 if parts.facing == sp.SIDE else 0)
        for k, yy in enumerate(range(y - 1, y - 4, -1)):
            if rows[yy][x] is None:
                rows[yy][x] = FEATHER_GREYS[k % 2]
            else:
                blend(x, yy, 0.2)


# Cloaks: the human and half-elf woman's own cloak (the artist's, frame by frame: its folds and
# its swing as she walks and fights) fitted to the wearer's shoulders and height, in the cloak's
# colours: over the back from behind (the hair over it), behind the body from the front and side.
CLOAK_MODEL = 2099
CLOAK_GREENS = frozenset((53, 54, 55, 56, 188, 189, 190, 191, 69, 70))
CLOAK_COLOURS = {  # item type: shades, dark to light (None: her own green)
    65: (204, 207, 205, 194, 206, 60),  # Cloak, Koeatl's Cloak: faded dun
    game.CLOAK_TYPE: (17, 18, 20, 22, 24, 26),  # Cloak of Protection +1: dusk blue-grey
    38: None,  # Living Cloak
    game.ELVEN_CLOAK_TYPE: None,  # native forest greens
}


def _cloak_shade(p: int) -> float:
    return _LIGHT.get(p, 0.5)


# Row and span of the far shoulder in the frontal bow release. The bow tip
# sits well above the crown in this pose and defeats the usual row scan.
_BOW_SHOULDERS = {
    2099: (9, 4, 13), 2095: (9, 4, 14), 2053: (8, 3, 11), 2055: (8, 3, 11),
    2059: (9, 4, 12), 2061: (9, 4, 12), 2072: (13, 7, 23), 2074: (13, 7, 23),
    2068: (8, 3, 12), 2070: (8, 3, 12), 2093: (9, 4, 13),
}


def _cloak_bow_parts(parts, model):
    row, left, right = _BOW_SHOULDERS[model]
    head = sp.Head(row - 6, left + 1, right - 2, row - 4)
    return parts._replace(facing=sp.FRONT, shoulders=(row, left, right), head=head)


def cloak_template(rows: Rows, model: int, frame: int, combat: bool) -> Optional[Tuple[sp.Parts, Dict[sp.Point, int]]]:
    """Her cloak in one of her frames: (her parts, {pixel: colour}), its dark fold lines with it."""
    if combat and frame == sp.DEAD_FRAME:
        # The fallen cel is upside down. Register its own laid-out fabric
        # against the fallen wearer in the same orientation.
        rows = [row[::-1] for row in rows[::-1]]
        parts = sp.parts(rows, CLOAK_MODEL, 1, False)
    else:
        parts = sp.parts(rows, CLOAK_MODEL, frame, combat)
    if combat and frame == 11:
        parts = _cloak_bow_parts(parts, CLOAK_MODEL)
    elif combat and frame == 9:
        parts = parts._replace(facing=sp.SIDE)
    cloak = {}
    for y, row in enumerate(rows):
        for x, p in enumerate(row):
            if p in CLOAK_GREENS:
                cloak[(x, y)] = p
            elif combat and frame == 11 and 10 <= y <= 23 and x <= (4 if y < 13 else 5) and p in (250, 254):
                # On the bow release the black lining fills the strip between
                # the green rim and the hip. Lime highlights along this edge
                # share a palette entry with her wristbands.
                cloak[(x, y)] = 56 if p == 250 else p
            elif combat and frame == 12 and 4 <= y <= 11 and x > 8 and p == 254:
                # Her recoil tips the torso forwards. The upper-right flap
                # turns its lining to camera, behind the raised arm.
                cloak[(x, y)] = p
            elif p == 254:  # (a fold line or its edge: black between greens)
                near = sum(0 <= y + dy < len(rows) and 0 <= x + dx < len(rows[y + dy]) and rows[y + dy][x + dx] in CLOAK_GREENS
                           for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                if near >= 3:
                    cloak[(x, y)] = p
    return (parts, cloak) if cloak and parts.shoulders and parts.head else None


def draw_cloak(rows: Rows, body: Rows, model: int, parts: sp.Parts, item_type: int, pad: int,
               template: Tuple[sp.Parts, Dict[sp.Point, int]]) -> set:
    """The cloak of TEMPLATE (cloak_template, the same frame of hers) on the (padded) picture ROWS."""
    her, cloak = template
    shades = CLOAK_COLOURS.get(item_type, CLOAK_COLOURS[65])
    if not parts.shoulders or not parts.head or parts.waist is None:
        return set()
    # where her shoulders' middle is, and her body's size, to the wearer's
    hm = (her.head.left + her.head.right) / 2
    wm = (parts.head.left + parts.head.right) / 2
    her_h = max(1, her.bottom - her.shoulders[0])
    own_h = max(1, parts.bottom - parts.shoulders[0])
    sy_ = own_h / her_h
    her_w = max(1, her.shoulders[2] - her.shoulders[1])
    own_w = max(1, parts.shoulders[2] - parts.shoulders[1])
    sx_ = max(0.7, min(1.6, own_w / her_w))
    ramp = sorted(CLOAK_GREENS | {254}, key=_cloak_shade)
    keep = set(parts.hair)
    if parts.head:
        keep |= {(x, y) for y in range(parts.head.top, parts.shoulders[0]) for x in range(parts.head.left, parts.head.right + 1)}
    hands = list(parts.hands.values())
    if parts.facing == sp.SIDE:  # (facing right: the cloak hangs from the back, at the left)
        hm, wm = her.shoulders[1], parts.shoulders[1]
    # each pixel of the wearer's picture takes her cloak's pixel at the same place (no gaps when
    # it is fitted to a bigger body)
    xs = [x for x, _ in cloak]
    ys = [y for _, y in cloak]
    x0 = int(wm + (min(xs) - hm) * sx_) - 1
    x1 = int(wm + (max(xs) - hm) * sx_) + 2
    y0 = int(parts.shoulders[0] + (min(ys) - her.shoulders[0]) * sy_) - 1
    y1 = int(parts.shoulders[0] + (max(ys) - her.shoulders[0]) * sy_) + 2
    placed: Dict[sp.Point, int] = {}
    for y in range(y0, y1):
        # Trail the profile hem behind the hip instead of projecting it
        # inside the thigh. Keep the fabric attached at the shoulder.
        drop = min(1., max(0., (y - parts.shoulders[0]) / max(1, parts.waist - parts.shoulders[0])))
        swing = round(drop * max(3, own_w * .35)) if parts.facing == sp.SIDE else 0
        for x in range(x0, x1):
            src = (int(round(hm + (x - wm) / sx_)), int(round(her.shoulders[0] + (y - parts.shoulders[0]) / sy_)))
            if src in cloak:
                placed[(x - swing, y)] = cloak[src]
    # no wider than the wearer (a pixel or two each side), and only what hangs from the body (no
    # scraps where her cloak billows past an arm)
    filled = [(x - pad, y - pad) for y, row in enumerate(body) for x, q in enumerate(row) if q is not None]
    if filled:
        bx0, bx1 = min(x for x, _ in filled) - (5 if parts.facing == sp.SIDE else 2), max(x for x, _ in filled) + 2
        placed = {k: v for k, v in placed.items() if bx0 <= k[0] <= bx1}
    # it hangs from the shoulders (from behind, draped over their tops)
    shoulder_top = parts.shoulders[0] - 2
    placed = {k: v for k, v in placed.items() if k[1] >= shoulder_top}
    if parts.facing == sp.BACK:  # (from behind, no wider than the back: where hers swings out, not his)
        _, sa, sb = parts.shoulders
        centre, back = (sa + sb) / 2, (sb - sa) * 0.38  # (the shoulder line runs over the arms)
        placed = {k: v for k, v in placed.items() if abs(k[0] - centre) <= back}
    on_body = {(x, y) for x, y in filled}
    seen: set = set()
    kept: Dict[sp.Point, int] = {}
    for start in list(placed):
        if start in seen:
            continue
        group, stack = [], [start]
        seen.add(start)
        while stack:
            q = stack.pop()
            group.append(q)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (q[0] + dx, q[1] + dy)
                    if n in placed and n not in seen:
                        seen.add(n)
                        stack.append(n)
        if any((q[0] + dx, q[1] + dy) in on_body for q in group for dx in (-1, 0, 1) for dy in (-1, 0, 1)) \
                and len(group) >= 4:
            kept.update({q: placed[q] for q in group})
    placed = kept
    # no holes: a pixel with cloak on both sides (along its row or its column, within two) is cloak
    for _ in range(2):
        fill = {}
        for (x, y) in list(placed):
            for dx, dy in ((1, 0), (0, 1)):
                for gap in (1, 2):
                    a, b = (x + dx, y + dy), (x + dx * (gap + 1), y + dy * (gap + 1))
                    if a not in placed and b in placed:
                        for k in range(1, gap + 1):
                            fill.setdefault((x + dx * k, y + dy * k), placed[(x, y)])
                        break
        placed.update(fill)
    if parts.facing == sp.BACK and placed:  # (from behind, up the back to the hair, as hers is worn)
        for x in {x for x, _ in placed}:
            y = min(yy for xx, yy in placed if xx == x)
            colour = placed[(x, y)]
            for up in range(1, 5):
                q = (x, y - up)
                if q not in on_body or q in keep:
                    break
                placed[q] = colour
    # a dark edge where the cloak meets the ground, as hers has (not along its top, at the shoulders)
    edge = set()
    for (x, y) in placed:
        for dx, dy in ((1, 0), (-1, 0), (0, 1)):
            n = (x + dx, y + dy)
            if n not in placed and n not in on_body and n not in keep:
                edge.add(n)
    fabric = set()
    neck, sa, sb = parts.shoulders
    collar_bottom = neck + max(1, (parts.waist - neck) // 4)
    collar_right = sb if parts.facing == sp.FRONT else (sa + sb) // 2
    for (x, y), p in placed.items():
        X, Y = x + pad, y + pad
        if not (0 <= Y < len(rows) and 0 <= X < len(rows[Y])):
            continue
        if (x, y) in keep or any(abs(x - hx) <= 1 and abs(y - hy) <= 1 for hx, hy in hands):
            continue
        # The leading shoulder fold sits on the tunic just below the neck.
        # Arms and legs still pass in front of the hanging cloth.
        over = parts.facing == sp.BACK or (neck <= y <= collar_bottom and sa <= x <= collar_right and p != 254)
        if body[Y][X] is not None and not over:
            continue  # (behind the body)
        if shades is None or p == 254:
            colour = p if shades is None else shades[0]
        else:
            t = ramp.index(p) / max(1, len(ramp) - 1)
            colour = shades[min(len(shades) - 1, max(1, int(t * (len(shades) - 1) + 0.5)))]
        rows[Y][X] = colour
        fabric.add((X, Y))
    outline = 254 if shades is None else shades[0]
    for x, y in edge:
        X, Y = x + pad, y + pad
        if 0 <= Y < len(rows) and 0 <= X < len(rows[Y]) and rows[Y][X] is None:
            rows[Y][X] = outline
            fabric.add((X, Y))
    return fabric


# Boots and belts, recoloured like armour (the artist's pixels kept): boots the feet and lower
# shins, a belt a band at the waist across the body. Item type: shades, dark to light.
FOREST_CLOTH = (208, 69, 188, 189, 53, 70, 190, 54, 191, 192, 55, 193, 56, 57)
DUSK_CLOTH = (208, 17, 18, 19, 48, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27, 28, 29)
BOOT_LEATHER = (208, 16, 129, 204, 207, 195, 205, 194, 206, 60, 61, 199)
BOOT_RED = (208, 16, 129, 202, 195, 134, 135, 136, 132, 137, 196, 138, 76, 139,
            140, 77, 141, 78, 142, 143, 152, 79)
BOOTS = {68: BOOT_LEATHER, game.ELVEN_BOOTS_TYPE: FOREST_CLOTH, game.SPEED_BOOTS_TYPE: BOOT_RED}
BELT_LEATHER = (204, 207, 205, 194, 206, 61)
BELTS = {42: (204, 207, 205, 206), 35: (204, 207, 205, 206), game.BACK_GIRDLE_TYPE: BELT_LEATHER,
         game.URNST_GIRDLE_TYPE: (16, 202, 135, 136, 137, 32, 76, 77)}
MIGHT_BELT, BUCKLE = 35, 168


def _torso_run(rows: Rows, y: int, middle: float, sa: int, sb: int) -> Optional[Tuple[int, int]]:
    """The run of the picture's row Y through the body's middle, inside the shoulders."""
    x = int(round(middle))
    if not (0 <= y < len(rows)) or not (0 <= x < len(rows[y])) or rows[y][x] is None:
        near = [i for i in range(sa, sb + 1) if 0 <= i < len(rows[y]) and rows[y][i] is not None] if 0 <= y < len(rows) else []
        if not near:
            return None
        x = min(near, key=lambda i: abs(i - middle))
    a = b = x
    while a - 1 >= max(0, sa) and rows[y][a - 1] is not None:
        a -= 1
    while b + 1 <= min(len(rows[y]) - 1, sb) and rows[y][b + 1] is not None:
        b += 1
    return a, b


def _body_half_width(rows: Rows, parts: sp.Parts) -> float:
    """Half the body's own width (the run through its middle just above the waist, where the arms
    and hair seldom are), and a little for the shoulders' breadth."""
    if not parts.shoulders or parts.waist is None or not parts.head:
        return 3.0
    sy, sa, sb = parts.shoulders
    middle = (parts.head.left + parts.head.right) / 2 if parts.facing != sp.SIDE else (sa + sb) / 2
    widths = []
    for y in range(max(sy + 1, parts.waist - 3), parts.waist + 1):
        run = _torso_run(rows, y, middle, 0, len(rows[y]) - 1) if 0 <= y < len(rows) else None
        if run:
            widths.append(run[1] - run[0] + 1)
    width = sorted(widths)[len(widths) // 2] if widths else (sb - sa) * 0.6
    return width / 2 + 1.5


def _by_light(p: int, shades: Tuple[int, ...]) -> int:
    light = _LIGHT.get(p, 0.5)
    return shades[min(len(shades) - 1, max(0, int(light * 1.7 * (len(shades) - 1) + 0.5)))]


def _outline(rows: Rows, x: int, y: int) -> bool:
    return rows[y][x] == 254 and any(not (0 <= y + dy < len(rows) and 0 <= x + dx < len(rows[y + dy]))
                                     or rows[y + dy][x + dx] is None for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


# Native bounds of the two upturned feet in the fallen originals (x0, y0,
# x1, y1, inclusive). Her blue boots have their own pigment mask below.
FALLEN_BOOTS = {
    2095: ((4, 0, 7, 3), (11, 0, 15, 2)),
    2055: ((3, 0, 5, 2), (8, 0, 12, 2)), 2053: ((3, 0, 5, 2), (8, 0, 12, 2)),
    2061: ((3, 4, 5, 7), (12, 0, 14, 4)), 2059: ((6, 0, 9, 2), (11, 0, 14, 2)),
    2072: ((5, 0, 9, 4), (13, 0, 22, 5)), 2074: ((7, 0, 11, 4), (15, 0, 24, 5)),
    2068: ((3, 0, 5, 2), (8, 0, 12, 2)), 2070: ((3, 0, 5, 2), (8, 0, 12, 2)),
    2093: ((5, 0, 8, 3), (11, 0, 16, 3)),
}

# Two points on the retail woman's blue boots in each pose. They separate
# adjacent toes in the profile stride and follow the upturned soles in the fall.
WOMAN_BOOT_CENTRES = (
    ((4, 23), (12, 20)), ((4, 19), (13, 23)), ((1, 22), (6, 19)), ((4, 23), (9, 20)),
    ((7, 18), (12, 22)), ((6, 21), (11, 22)), ((4, 22), (9, 18)), ((5, 23), (10, 21)),
    ((7, 22), (11, 20)), ((7, 20), (12, 22)), ((7, 20), (11, 22)), ((6, 20), (9, 22)),
    ((6, 20), (14, 22)), ((9, 19), (13, 23)), ((4, 22), (12, 21)), ((3, 32), (11, 29)),
    ((7, 20), (14, 17)), ((12, 18), (20, 14)), ((2, 22), (9, 25)), ((4, 27), (13, 31)),
    ((13, 18), (22, 20)), ((14, 30), (18, 26)), ((7, 22), (12, 19)), ((7, 20), (12, 17)),
    ((2, 22), (9, 19)), ((4, 23), (10, 25)), ((8, 26), (12, 22)), ((13, 21), (17, 15)),
    ((6, 0), (12, 1)),
)


def _fallen_boot_cells(rows, own, model):
    """Visible upturned feet of an original figure, also used to clip its cloak."""
    feet = []
    for x0, y0, x1, y1 in FALLEN_BOOTS[model]:
        cells = []
        for y in range(y0, min(len(rows), y1 + 1)):
            for x in range(x0, x1 + 1):
                nx = own.at(x, y) if own else x
                if 0 <= nx < len(rows[y]) and rows[y][nx] is not None:
                    p = rows[y][nx]
                    # The giant's boot leather stops at the bare ankle.
                    if model not in (2072, 2074) or p in (48, 49, 50, 208, 209, 210, 211, 212):
                        cells.append((nx, y))
        feet.append(cells)
    return feet


def _woman_boot_cells(rows, own, pose):
    """Her blue shoe pixels and their grey glints, mapped through the half-elf cut."""
    source = own.source if own else rows
    blue = {(x, y) for y, row in enumerate(source) for x, p in enumerate(row) if p in halfelf.BOOTS}
    highlights = {(x, y) for x0, y0 in blue for y in range(max(0, y0-1), min(len(source), y0+2))
                  for x in range(max(0, x0-1), min(len(source[y]), x0+2)) if source[y][x] == 213}
    feet = ([], [])
    a, b = WOMAN_BOOT_CENTRES[pose]
    for x, y in blue | highlights:
        right = (x-b[0])**2 + (y-b[1])**2 < (x-a[0])**2 + (y-a[1])**2
        if own:
            # Only a source pixel still present after the narrower hip/leg cut.
            nx = own.at(x, y)
            if own.back is not None and own.back(nx, y) != x:
                continue
            x = nx
        feet[right].append((x, y))
    return feet


def _stock_boot_surface(rows, parts, pad):
    """Trace the two soles independently. The raised foot can clear the floor by several rows."""
    if parts.waist is None or not parts.feet:
        return []
    feet = [[] for foot in parts.feet]
    height = max(3, (parts.bottom - parts.waist) // 3)
    for y in range(max(parts.waist + 1, min(f[0] for f in parts.feet) - height), parts.bottom + 1):
        for X, p in enumerate(rows[y + pad]):
            x = X - pad
            if p is None or any(abs(x-hx) <= 2 and abs(y-hy) <= 2 for hx, hy in parts.hands.values()):
                continue
            distances = [(max(a - x, x - b, 0), i) for i, (sole, a, b) in enumerate(parts.feet)
                         if 0 <= sole - y <= height and a - 2 <= x <= b + 2]
            if distances:
                feet[min(distances)[1]].append((x, y))
    return feet


def draw_boots(rows: Rows, parts: sp.Parts, item_type: int, pad: int, feet=None,
               magic=()) -> None:
    """Dye each visible boot from its own shading and attach its glint to that foot."""
    shades = BOOTS.get(item_type)
    if shades is None:
        return
    if feet is None:
        feet = _stock_boot_surface(rows, parts, pad)
    for foot in feet:
        cells = [(x + pad, y + pad) for x, y in foot if rows[y + pad][x + pad] not in (None, 254)]
        dye_garment(rows, cells, shades, 0, rows)
        if magic:
            sparkle_cells(rows, cells, magic, spacing=11, sparse=True)


def paint_belt(rows, points, item_type, pad, face, glow=()):
    """Dye the visible waistband and attach its trim and glint to that same surface."""
    shades = BELTS.get(item_type)
    if not shades:
        return
    cells = sorted((x + pad, y + pad) for x, y in points if rows[y + pad][x + pad] not in (None, 254))
    if not cells:
        return
    for x, y in cells:
        rows[y][x] = _by_light(rows[y][x], shades)
    trim = None
    if item_type == game.BACK_GIRDLE_TYPE and len(cells) >= 3:
        trim = cells[len(cells) // 3]
        rows[trim[1]][trim[0]] = 37  # violet stitching in its inventory icon
    if item_type in (MIGHT_BELT, game.URNST_GIRDLE_TYPE) and face == sp.FRONT:
        trim = cells[len(cells) // 2]
        rows[trim[1]][trim[0]] = 183 if item_type == game.URNST_GIRDLE_TYPE else BUCKLE
    if glow:
        surface = [p for p in cells if p != trim] or cells
        sparkle_cells(rows, surface, glow, spacing=11, sparse=True)


def draw_belt(rows: Rows, parts: sp.Parts, item_type: int, pad: int, cloak: FrozenSet[int] = frozenset(),
              glow=()) -> None:
    """A belt: a row at the waist across the body (not the arms or hands, nor over the figure's own
    CLOAK's colours), a buckle at the front of the Belt of Might."""
    shades = BELTS.get(item_type)
    if shades is None or parts.waist is None or not parts.head:
        return
    unpadded = [r[pad:len(r) - pad] for r in rows[pad:]]
    middle = (parts.head.left + parts.head.right) / 2 if parts.facing != sp.SIDE else \
        (parts.shoulders[1] + parts.shoulders[2]) / 2 if parts.shoulders else parts.head.left
    half = _body_half_width(unpadded, parts) - 1.5
    hands = list(parts.hands.values())
    cells = []
    for y in (parts.waist,):
        run = _torso_run(unpadded, y, middle, 0, len(unpadded[0]) - 1) if 0 <= y < len(unpadded) else None
        if not run:
            continue
        for x in range(max(run[0], int(middle - half)), min(run[1], int(middle + half + 0.5)) + 1):
            if any(abs(x - hx) <= 1 and abs(y - hy) <= 1 for hx, hy in hands) or _outline(rows, x + pad, y + pad) \
                    or unpadded[y][x] in cloak:
                continue
            cells.append((x, y))
    if item_type in (42, MIGHT_BELT):
        for x, y in cells:
            rows[y + pad][x + pad] = _by_light(unpadded[y][x], shades)
        if item_type == MIGHT_BELT and parts.facing == sp.FRONT and cells:
            rows[parts.waist + pad][int(round(middle)) + pad] = BUCKLE
        if glow and cells:
            sparkle_cells(rows, [(x + pad, y + pad) for x, y in cells], glow, spacing=11, sparse=True)
    else:
        paint_belt(rows, cells, item_type, pad, parts.facing, glow)


class Own(NamedTuple):
    """A figure made from one of the game's frames in other colours and a little another shape
    (figures.py), whose parts and clothes can't be read from its own colours."""
    parts: sp.Parts  # where its parts are
    source: Rows  # the game's frame it was made from
    source_parts: sp.Parts
    at: Callable[[int, int], int]  # where a pixel (x, y) of the source is across it: its x
    clothes: Optional[Tuple[int, ...]] = None  # its clothing colours, dark to light (None: the model's)
    cloak: FrozenSet[int] = frozenset()  # its own cloak's colours (CLOAK_MODEL's figure)
    not_cloak: FrozenSet[sp.Point] = frozenset()  # pixels in them that aren't the cloak (wristbands)
    worn: Optional[FrozenSet[sp.Point]] = None  # the pixels that were clothing in the source (None: any)
    back: Optional[Callable[[int, int], int]] = None  # where a pixel (x, y) of it is across the source


def paint_region(rows, cells, shades, pad):
    """Shade the visible boot or glove pixels in native pose coordinates."""
    for x, y in cells:
        colour = rows[y + pad][x + pad]
        if colour is not None:
            rows[y + pad][x + pad] = _by_light(colour, shades)


# Palette from the inventory art: the Chameleon Gloves are blue-grey;
# the Quicksilver Glove has a silvery face over a leather palm.
GLOVE_SHADES = {37: (17, 19, 22, 24, 26, 29), 113: (204, 207, 210, 212, 214, 215)}


def _outfit_cloak(out, base_outfit, costume, kind, shades, pad):
    """Dress the saved pose mask; retain the native weave where there is existing cloth."""
    fabric = set()
    soft = FOREST_CLOTH if shades is None else DUSK_CLOTH if kind == game.CLOAK_TYPE else ()
    if costume.equipped_cape:
        material = soft or (LEATHER_SHADES if kind == 65 else shades)
        for x, y, source in costume.equipped_cape:
            X, Y = x + pad, y + pad
            out[Y][X] = garment_tone(source, material)
            fabric.add((X, Y))
        return fabric
    ranks = shades or (69, 188, 53, 54, 55, 56)
    limb = set(costume.regions.get(classoutfits.FOREARM, ()))
    for bit in (classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT, classoutfits.BOW):
        limb.update(costume.regions.get(bit, ()))
    detailed = []
    for x, y, rank in costume.cloak:
        X, Y = x + pad, y + pad
        p = base_outfit[Y][X]
        if (x, y) in limb and (p is None or 128 <= p <= 154):
            continue
        out[Y][X] = 254 if costume.native_cloak and soft and p == 254 else ranks[rank]
        fabric.add((X, Y))
        # A hood or mantle already carries the folds of this pose.
        # A separately fitted cape gets its folds from the registered ranks.
        if costume.native_cloak and soft and p is not None and p != 254 and not 128 <= p <= 154:
            detailed.append((X, Y))
    if detailed:
        dye_garment(out, detailed, soft, 0, base_outfit)
    return fabric


def _womans_cloak(out, rows, own, shades, pad):
    """Recover the retail green folds even beneath the half-elf’s purple recolor."""
    fabric = set()
    greens = own.cloak if own is not None and own.cloak else CLOAK_GREENS
    skip = own.not_cloak if own is not None else frozenset()
    ramp = sorted(greens, key=_cloak_shade)
    green = sorted(CLOAK_GREENS, key=_cloak_shade)
    for y, row in enumerate(rows):
        for x, p in enumerate(row):
            if p not in greens or (x, y) in skip:
                continue
            source = p
            if own is not None and own.back is not None:
                sx = own.back(x, y)
                if 0 <= sx < len(own.source[y]) and own.source[y][sx] in CLOAK_GREENS:
                    source = own.source[y][sx]
            X, Y = x + pad, y + pad
            fabric.add((X, Y))
            if shades is None:
                out[Y][X] = source if source in CLOAK_GREENS else green[ramp.index(p) * (len(green)-1) // max(1, len(ramp)-1)]
            else:
                ramp_at = green if source in CLOAK_GREENS else ramp
                fraction = ramp_at.index(source) / max(1, len(ramp_at) - 1)
                out[Y][X] = shades[round(fraction * (len(shades) - 1))]
    return fabric


def _project_cloak(out, rows, model, parts, frame, combat, kind, own, pad, cloak):
    """Place the matching retail cloak pose on an original figure and return visible fabric."""
    fabric = set()
    source = own.source if own else rows
    falling = combat and frame == sp.DEAD_FRAME
    cloth_parts = own.source_parts if own else parts
    if falling:
        source = [row[::-1] for row in source[::-1]]
        cloth_parts = sp.parts(source, model, 1, False)
    elif model in (2072, 2074) and combat and frame == 10:
        # Their raised rear bow hides both shoulders from the landmark finder.
        cloth_parts = cloth_parts._replace(shoulders=(14, 8, 17))
    elif combat and frame == 11 and model in _BOW_SHOULDERS:
        cloth_parts = _cloak_bow_parts(cloth_parts, model)
    elif combat and frame == 9:
        cloth_parts = cloth_parts._replace(facing=sp.SIDE)
    canvas = padded(source, pad)
    drawn = draw_cloak(canvas, [r[:] for r in canvas], model, cloth_parts, kind, pad, cloak)
    toes = set()
    if falling and model in FALLEN_BOOTS:
        toes = {point for foot in _fallen_boot_cells(rows, own, model) for point in foot}
    for X, Y in sorted(drawn):
        sx, sy = X - pad, Y - pad
        if falling:
            sx, sy = len(source[0]) - 1 - sx, len(source) - 1 - sy
        dest_y = sy + pad
        if not 0 <= dest_y < len(out):
            continue
        # The donor's standing width can differ from the half-elf's.
        xs = (sx,) if own is None else range(own.at(sx, sy), own.at(sx + 1, sy))
        for nx in xs:
            dest_x = nx + pad
            if (nx, sy) in toes or not 0 <= dest_x < len(out[dest_y]):
                continue
            if combat and frame in sp.BOW_FRAMES:
                p = rows[sy][nx] if 0 <= sy < len(rows) and 0 <= nx < len(rows[sy]) else None
                if p in (179, 180, 181, 182, 183) or (model == 2095 and p == 49) or (model == 2093 and p == 149):
                    continue
            out[dest_y][dest_x] = canvas[Y][X]
            fabric.add((dest_x, dest_y))
    return fabric


def armed(rows: Rows, model: int, frame: int, combat: bool, weapons: Dict[str, Tuple],
          pad: int = 10, armour: Tuple[int, ...] = (),
          cloak: Optional[Tuple[sp.Parts, Dict[sp.Point, int]]] = None,
          own: Optional[Own] = None, costume: Optional[classoutfits.Frame] = None, registered: bool = False) -> Rows:
    """One frame of MODEL with WEAPONS ({"right"/"left": (item type, material[, name in
    BLADE_COLOURS])}: in the hands in a
    fight, walking worn at the belt (two-handed ones carried upright);
    "missile": the bow, sling or chatkcha carried, "ammo": arrows, on the back or at the hip),
    padded by PAD, in ARMOUR (item types, MAGIC_ARMOUR added for a magic one: under all the rest). Nothing in the hands in the bow
    frames (the game draws the bow). OWN: a figure of its own made from MODEL's frame (Own)."""
    out = costume.canvas(rows, pad) if costume else padded(rows, pad)
    outfit_bow = {}
    if costume and (own is not None or model in classoutfits.FITTED_RACES) and combat and frame in sp.BOW_FRAMES:
        outfit_bow = {(x, y): out[y + pad][x + pad] for x, y in costume.regions[classoutfits.BOW]}
    parts = own.parts if own is not None else sp.parts(rows, model, frame, combat)
    if costume and costume.head:
        parts = parts._replace(hair=costume.head)
    if costume and model in classoutfits.DWARVES and parts.facing and costume.head:
        # In a bow or hit pose the raised hand can be higher than the crown.
        # Seat the circlet on the registered head, excluding those foreground pixels.
        top = min(y for x, y in costume.head)
        brow = top + 2
        temples = [x for x, y in costume.head if y == brow]
        if temples:
            facing = sp.FRONT if combat and frame == 11 else parts.facing
            parts = parts._replace(head=sp.Head(top, min(temples), max(temples), brow), facing=facing)
    if costume and model in classoutfits.ELVES and combat and frame in (10, 11):
        # The raised bow reaches higher than the crown. Locate the circlet and
        # quiver on the figure, including the turned-to-camera final bow frame.
        if frame == 10:
            parts = parts._replace(facing=sp.BACK, head=sp.Head(3, 3, 9, 5),
                                   shoulders=(10, 3, 10), waist=17)
        else:
            crown = 3 if model == 2059 else 4
            parts = parts._replace(facing=sp.FRONT, head=sp.Head(crown, 5, 10, crown+1),
                                   shoulders=(10, 4, 12), waist=18)
    if costume and model == 2099 and not combat and frame == 1:
        # The rear idle has a relaxed grip on each side of the hips.
        parts = parts._replace(hands={"left": (4, 15), "right": (15, 15)},
                               shoulders=(7, 5, 14))
    if costume and model == 2099 and not combat and frame == 6:
        # The raised wrist is outside the shoulder in the last front-walk pose.
        parts = parts._replace(shoulders=(7, 4, 11))
    if costume and model == 2099 and combat and frame == 7:
        # The thrusting arm and flying cloak span most of the frame. The quiver
        # stays at the shoulder, inside that span.
        parts = parts._replace(shoulders=(9, 11, 17), waist=15)
    if costume and model == 2099 and combat and frame in (10, 11):
        # Her vertical bow and raised hand both project above the face.
        if frame == 10:
            parts = parts._replace(facing=sp.SIDE, head=sp.Head(3, 4, 9, 5),
                                   shoulders=(10, 3, 10), waist=16)
        else:
            parts = parts._replace(facing=sp.FRONT, head=sp.Head(3, 5, 10, 5),
                                   shoulders=(10, 5, 13), waist=16)
    if costume and model == 2095 and parts.facing is not None and costume.cloak:
        k = frame + (sp.WALK_FRAMES if combat else 0)
        crown, left, right, brow, shoulder, sa, sb, waist = classoutfits.LANDMARKS[k]
        facing = sp.FRONT if combat and frame == 11 else parts.facing
        hair = {(x, y) for y in range(crown, shoulder) for x in range(left - 1, right + 2)
                if 0 <= x < len(rows[y]) and rows[y][x] in sp.MODELS[model][2]}
        parts = parts._replace(facing=facing, head=sp.Head(crown, left, right, brow),
                               shoulders=(shoulder, sa, sb), waist=waist, hair=hair)
    if costume:
        base_outfit = [r[:] for r in out] if armour or "cloak" in weapons else None
        # Chest first so a separately equipped pauldron takes precedence at the shoulder.
        armour = sorted(armour, key=lambda t: ARMOUR.get(t & (MAGIC_ARMOUR - 1), (None,))[0] != ARMOUR_CHEST)
    armor_parts, armor_canvas, armor_own = parts, out, own
    if armour and not costume and combat and frame == sp.DEAD_FRAME and model not in (CLOAK_MODEL, sp.KREEN):
        # The fallen drawing has the feet at the top. View its own pixels
        # feet-down while fitting the slots; the canvas rows still alias out.
        armor_parts = sp.find(rows[::-1], model, 0)
        armor_canvas = out[:pad] + list(reversed(out[pad:]))
        if own and own.worn is not None:
            armor_own = own._replace(worn=frozenset((x, len(rows)-1-y) for x, y in own.worn))
    # Slot ownership comes from the undyed drawing, including when multiple stock
    # pieces use a tone already present in the player's picture.
    stock_source = [r[:] for r in armor_canvas] if armour and not costume else None
    bow_keep = set()
    boot_keep = set()
    if stock_source and registered and model != sp.KREEN:
        if combat and frame in sp.BOW_FRAMES:
            layer = (halfelf.MAN if model == 2061 else halfelf.WOMAN) if own else model
            role = "Warrior" if layer in (2095, 2099) else "Fighter"
            bow_keep.update(classoutfits.frames(role, True, layer)[frame].regions[classoutfits.BOW])
        if any(ARMOUR.get(t & (MAGIC_ARMOUR - 1), (None,))[0] == ARMOUR_LEGS for t in armour):
            feet = _stock_boot_surface(stock_source, armor_parts, pad)
            boot_keep.update(p for foot in feet for p in foot)
            if model == CLOAK_MODEL:
                boots = _woman_boot_cells(rows, own, frame + sp.WALK_FRAMES * combat)
                boot_keep.update((x, y) for foot in boots for x, y in foot)
            if model == 2095:
                # His black high boots extend above the ordinary ankle cut. Their
                # teal stitching is specific to the boots below the waistband.
                clothed = [r[pad:len(r)-pad] for r in stock_source[pad:]]
                for y, row in enumerate(clothed):
                    if y <= (armor_parts.waist or 0) + 1:
                        continue
                    for x, colour in enumerate(row):
                        if colour == 69:
                            boot_keep.update((x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    if costume and armour:
        trim = set(costume.armor_trim)
        if costume.native_cloak:
            trim.update((x, y) for x, y, _ in costume.cloak)
    if model != sp.KREEN:
        for item_type in armour:
            kind = item_type & (MAGIC_ARMOUR - 1)
            if kind in ARMOUR and kind != game.BRACERS_TYPE:
                piece, shades, pattern = ARMOUR[kind]
                if costume:
                    bit = {ARMOUR_CHEST: classoutfits.CHEST, ARMOUR_ARMS: classoutfits.ARMS,
                           ARMOUR_LEGS: classoutfits.LEGS}[piece]
                    if item_type & VEILED_DYE and kind == game.ROBE_TYPE:
                        shades = VEILED_CLOTH
                    cells = costume.regions[bit]
                    leg_piece = kind == game.ROBE_TYPE and any(
                        ARMOUR.get(t & (MAGIC_ARMOUR - 1), (None,))[0] == ARMOUR_LEGS for t in armour)
                    if kind == game.ROBE_TYPE and not leg_piece:
                        # The robe falls over existing lower garment pixels. Preserve
                        # bare legs, boots and the class mantle above it.
                        protected = set(cells)
                        for owner in (classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT, classoutfits.BOW,
                                      classoutfits.FOREARM, classoutfits.ARMS):
                            protected.update(costume.regions[owner])
                        human = own is None and model in (2095, 2099)
                        if not human:
                            protected.update((x, y) for x, y, _ in costume.cloak)
                        skirt = [(x, y) for x, y in costume.regions[classoutfits.LEGS]
                                 if (x, y) not in protected and base_outfit[y + pad][x + pad] is not None
                                 and (human or not 128 <= base_outfit[y + pad][x + pad] <= 154)]
                        cells = [*cells, *skirt]
                    # Always take the dye value from the original cloth, even where
                    # two pieces overlap or the chest underneath already glints.
                    if (own is None and model == 2059 and piece == ARMOUR_CHEST and
                            pattern == PLATE and not combat and frame in (2, 11, 12, 13, 14)):
                        # The near arm and belt occlude this strip in the elf woman's stride.
                        cells = [(x, y) for x, y in cells if 6 <= y < 13]
                    cells = [(x, y) for x, y in cells if (x, y) not in trim
                             and base_outfit[y + pad][x + pad] not in (None, 254)]
                    dye_garment(out, cells, shades, pad, base_outfit)
                elif armor_parts.facing is not None:
                    cells = draw_armour(armor_canvas, model, armor_parts, kind, pad, armor_own,
                                        bool(item_type & VEILED_DYE), stock_source,
                                        bow_keep | boot_keep if piece == ARMOUR_LEGS else bow_keep)
                else:
                    cells = []
                if piece == ARMOUR_LEGS and registered and (costume or not cells):
                    surface = base_outfit if costume else padded(rows, pad)
                    exposed = spritegreaves.visible(rows, model, frame, combat, own, costume, surface, pad)
                    if not costume:
                        if armor_canvas is not out:
                            exposed = [(x, len(rows)-1-y) for x, y in exposed]
                        # The retail model has no visible lower garment in this
                        # pose. Require a continuous sliver of exposed calf above
                        # the shoes, so a lone shared skin tone cannot make a plate.
                        skin = set(exposed) - boot_keep - bow_keep
                        exposed = sorted((x, y) for x, y in skin if any(
                            (x+dx, y+dy) in skin for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy))
                    source = base_outfit if costume else stock_source
                    for x, y in exposed:
                        colour = garment_tone(source[y+pad][x+pad], shades)
                        value = shades.index(colour)
                        armor_canvas[y+pad][x+pad] = shades[_pattern(pattern, x, y, value, len(shades)-1)]
                    cells.extend(exposed)
                cuffs = []
                if piece == ARMOUR_ARMS:
                    surface = base_outfit if costume else padded(rows, pad)
                    band = spritebracers.visible(rows, model, frame, combat, own, costume, surface, pad)
                    if armor_canvas is not out:
                        band = [(x, len(rows)-1-y) for x, y in band]
                    blocked = trim if costume else bow_keep
                    cuffs = spritebracers.grouped(p for p in band if p not in blocked)
                    for cuff in cuffs:
                        if any(abs(x-u) <= 2 and abs(y-v) <= 2 for x, y in cuff for u, v in cells):
                            continue
                        dye_garment(armor_canvas, cuff, shades, pad, base_outfit if costume else stock_source)
                        cells.extend(cuff)
                if item_type & MAGIC_ARMOUR:
                    shine_armour(armor_canvas, cells, piece, armor_parts, pad,
                                 GLOWS[(item_type >> GLOW_SHIFT) % len(GLOWS)], cuffs)
    if model != sp.KREEN:
        for item in armour:
            if item & (MAGIC_ARMOUR - 1) == game.BRACERS_TYPE:
                surface = base_outfit if costume else out
                cuffs = spritebracers.visible(rows, model, frame, combat, own, costume, surface, pad)
                paint_region(out, cuffs, SHIMMER_SHADES, pad)
                if item & MAGIC_ARMOUR:
                    sparkle_cells(out, [(x + pad, y + pad) for x, y in cuffs],
                                  GLOWS[(item >> GLOW_SHIFT) % len(GLOWS)], spacing=11, sparse=True)
    if "boots" in weapons and model != sp.KREEN:
        item = weapons["boots"]
        if costume:
            feet = (costume.regions[classoutfits.LEFT_FOOT], costume.regions[classoutfits.RIGHT_FOOT])
        elif model == CLOAK_MODEL:
            feet = _woman_boot_cells(rows, own, frame + sp.WALK_FRAMES * combat)
        elif combat and frame == sp.DEAD_FRAME and model in FALLEN_BOOTS:
            feet = _fallen_boot_cells(rows, own, model)
        else:
            feet = None
        if feet is not None or parts.facing is not None:
            draw_boots(out, parts, item[0], pad, feet, _glow(item) if _magic(item) else ())
    if "belt" in weapons and model != sp.KREEN:
        item = weapons["belt"]
        layer = (halfelf.MAN if model == 2061 else halfelf.WOMAN) if own is not None else model
        covered = own.cloak if own else CLOAK_GREENS if model == CLOAK_MODEL else ()
        glow = _glow(item) if _magic(item) else ()
        if costume is not None or registered:
            belt = spritebelts.visible(layer, combat, frame, costume, rows, parts, covered)
            paint_belt(out, belt, item[0], pad, parts.facing, glow)
        else:
            draw_belt(out, parts, item[0], pad, covered, glow)
    if "cloak" in weapons and model != sp.KREEN:
        item = weapons["cloak"]
        kind = item[0]
        shades = CLOAK_COLOURS.get(kind, CLOAK_COLOURS[65])
        fabric = set()
        if costume:
            fabric = _outfit_cloak(out, base_outfit, costume, kind, shades, pad)
            if model == CLOAK_MODEL and cloak and (not combat and frame in (0, 3, 4, 5, 6)):
                # Her front mantle or hood owns only the upper folds. The
                # retail cloak also peeks around the legs, below the arms.
                # Reuse those exact side folds where the outfit leaves room.
                material = DUSK_CLOTH if kind == game.CLOAK_TYPE else shades
                for (x, y), source in cloak[1].items():
                    start, stop = (own.at(x, y), own.at(x+1, y)) if own else (x, x+1)
                    for X in range(start + pad, stop + pad):
                        Y = y + pad
                        if out[Y][X] is None:
                            out[Y][X] = source if material is None else garment_tone(source, material)
                            fabric.add((X, Y))
        elif model == CLOAK_MODEL:
            fabric = _womans_cloak(out, rows, own, shades, pad)
        elif cloak:
            fabric = _project_cloak(out, rows, model, parts, frame, combat, kind, own, pad, cloak)
        if _magic(item):
            visible = sorted((x, y) for x, y in fabric if out[y][x] != 254)
            sparkle_cells(out, visible, _glow(item), spacing=11, sparse=True)
    if "helm" in weapons and parts.facing is not None and model != sp.KREEN:
        before = [list(r) for r in out]
        draw_helm(out, parts, weapons["helm"][0], pad, model)
        if costume:
            for x, y in costume.regions.get(classoutfits.FOREARM, ()):
                out[y + pad][x + pad] = before[y + pad][x + pad]
        if _magic(weapons["helm"]):
            sparkle(out, before, _glow(weapons["helm"]))
    if costume and own is not None:
        k = frame + (sp.WALK_FRAMES if combat else 0)
        if k < len(classoutfits.HALF_ELF_SHOULDERS[model]):
            parts = parts._replace(shoulders=classoutfits.HALF_ELF_SHOULDERS[model][k])
        if model == 2099 and k in classoutfits.HALF_ELF_WOMAN_REAR_HAND:
            right = classoutfits.HALF_ELF_WOMAN_REAR_HAND[k]
            parts = parts._replace(hands={**parts.hands, "right": right})
    body = [list(r) for r in out]
    missile = weapons.get("missile")
    if missile or "ammo" in weapons:  # (the bow, quiver, sling or chatkcha carried)
        shape = WEAPON_SHAPES.get(missile[0]) if missile else None
        bow = shape == BOW and not (combat and frame in sp.BOW_FRAMES)
        hip = MATERIAL_COLOURS.get(missile[1], MATERIAL_COLOURS[5]) if shape in (SLING, CHATKCHA) else None
        draw_back_gear(out, body, parts, pad, bow, "ammo" in weapons or shape == BOW, hip, shape)
    if costume and (missile or "ammo" in weapons):
        for x, y in costume.regions.get(classoutfits.FOREARM, ()):
            out[y + pad][x + pad] = body[y + pad][x + pad]
    hands = dict(parts.hands)
    pose = COMBAT_POSES[frame] if combat and 0 <= frame < len(COMBAT_POSES) else None
    if pose and hands:  # (in a fight, the swinging hand is the pose's, not by side)
        pick, swing, other = pose
        points = list(hands.values())
        key = {"highest": lambda p: p[1], "lowest": lambda p: -p[1], "leftmost": lambda p: p[0],
               "rightmost": lambda p: -p[0]}[pick]
        points.sort(key=key)
        hands = {"right": points[0]}
        if len(points) > 1:
            hands["left"] = points[1]
    if model in classoutfits.DWARVES:
        grips = classoutfits.DWARF_FIGHT_GRIPS
        shields = classoutfits.DWARF_FIGHT_SHIELDS if combat else classoutfits.DWARF_WALK_SHIELDS
        if model == 2053 and combat and frame == 0:
            grips = ((1, 11),) + grips[1:]
            shields = (classoutfits.DWARF_WALK_SHIELDS[0],) + shields[1:]
    elif model == 2099:
        grips = classoutfits.WOMAN_FIGHT_GRIPS
        shields = classoutfits.WOMAN_FIGHT_SHIELDS if combat else classoutfits.WOMAN_WALK_SHIELDS
    else:
        grips = classoutfits.FIGHT_GRIPS
        shields = classoutfits.FIGHT_SHIELDS if combat else classoutfits.WALK_SHIELDS
    if costume and model in (*classoutfits.DWARVES, 2095, 2099) and combat and grips[frame]:
        hands["right"] = grips[frame]
        hands["left"] = shields[frame]
    if costume and model in classoutfits.ELVES:
        # Wristbands disappear behind the torso or share a cluster in these poses.
        # Coordinates follow each native picture, including the woman's raised off hand.
        if combat:
            corrections = classoutfits.ELF_MELEE_HANDS[model].get(frame)
            if corrections:
                hands["right"], hands["left"] = corrections
        elif parts.facing == sp.SIDE and "left" not in hands and "right" in hands:
            hx, hy = hands["right"]
            hands["left"] = (hx-2, hy-1)
    # The registered grips above are on the parent cel. The half-elf maker
    # widens or narrows individual rows; walk hands from own.parts already moved.
    if costume and own is not None and combat and pose:
        hands = {key: (own.at(x, y), y) for key, (x, y) in hands.items()}
    if costume:
        for hand, point in hands.items():
            item = weapons.get(hand)
            if item and item[0] in GLOVE_SHADES and point:
                hx, hy = point
                # The same owner mask that keeps swords and cloaks behind the arm.
                # A hidden hand has no visible pixels to dye.
                cells = [(x, y) for x, y in costume.regions[classoutfits.FOREARM]
                         if abs(x - hx) + abs(y - hy) <= 3
                         and out[y + pad][x + pad] == body[y + pad][x + pad]]
                paint_region(out, cells, GLOVE_SHADES[item[0]], pad)
                if cells and _magic(item):
                    x, y = min(cells, key=lambda p: (p[1], p[0]))
                    out[y + pad][x + pad] = _glow(item)[(x + y) % len(_glow(item))]
    if combat and frame in sp.BOW_FRAMES:
        if costume:
            for x, y in costume.regions[classoutfits.BOW]:
                out[y + pad][x + pad] = outfit_bow[x, y] if outfit_bow else rows[y][x]
        return out  # (the game draws the bow in the hands)
    if "left" not in weapons and WEAPON_SHAPES.get(weapons.get("right", (None,))[0]) == CAHULAKS:
        weapons = dict(weapons, left=weapons["right"])  # (a pair, one in each hand: one item)
    for hand in ("left", "right"):  # (the right drawn last, over the left)
        if hand not in weapons:
            continue
        item_type, material = weapons[hand][:2]
        blade = BLADE_COLOURS.get(weapons[hand][2]) if len(weapons[hand]) > 2 else None
        glint = _magic(weapons[hand]) or blade is not None  # (a named blade is magic too)
        shine = _glow(weapons[hand])
        shape = WEAPON_SHAPES.get(item_type)
        if costume and model not in classoutfits.FITTED_RACES and shape == SHIELD and hand == "left":
            centre = hands.get("left") if model in classoutfits.ELVES else shields[frame]
            if centre:
                x, y = centre
                if own is not None and model == 2099:
                    x = own.at(x, y)
                if model in classoutfits.ELVES and not combat:
                    y -= 2  # hand finder reports the fist, two rows below the band
                far = parts.facing == sp.SIDE and (not combat or frame == 7)
                facing = SIDE_FAR if far else parts.facing
                # In profile the far arm is behind the torso, but the swept
                # hem trails behind the shield. Use the native torso as its occluder.
                occluder = padded(rows, pad) if far and model == 2095 else body
                draw_shield(out, occluder, (x + pad, y + pad + 2), facing,
                            MATERIAL_COLOURS.get(material, MATERIAL_COLOURS[4]),
                            far or facing == sp.BACK, glint=glint, shine=shine)
            continue
        side = shape == SHIELD and not combat and parts.facing == sp.SIDE  # (placed by side_shield)
        if hand not in hands and not (shape == SHIELD and pose and hand == "left") and not side:
            continue
        g = grip(model, frame, combat, hand)
        if g is None and pose:
            g = (pose[1] if hand == "right" else pose[2], False)
        if shape == SHIELD and (pose and hand == "left" or side):
            g = g or (0, False)  # (placed by fight_shield, whichever hand was found)
        if costume and model in classoutfits.ELVES and g and shape != SHIELD:
            # The picture ends at the soles. Turn a long point or staff butt
            # away from that edge while keeping the grip on the registered hand.
            if not combat and hand == "left" and shape == POLEARM and frame in (6, 11):
                g = (55 if frame == 6 else 130, g[1])
            elif combat and frame == 1 and hand == "left":
                g = (70 if model == 2059 else 15, g[1])
            elif combat and model == 2059 and frame == 12 and hand == "right":
                g = (160, g[1])
            elif combat and model == 2061 and frame == 2 and hand == "right" and shape in (STAFF, GYTHKA):
                g = (200, g[1])
        if costume and model in classoutfits.DWARVES and combat and hand == "right":
            # The shorter figure's low recoil and follow-through expose the tip
            # below its soles. Keep the hand fixed and turn the shaft outward.
            if frame == 12:
                g = (150, False)
            elif frame == 8 and shape in (GREAT_AXE, POLEARM):
                g = (45, False)
            elif shape == GREAT_AXE and frame in (0, 1, 6):
                g = ({0: 280, 1: 205, 6: 245}[frame], g[1])
        if costume and model in (2095, 2099) and combat and frame == 12 and hand == "right" and shape != SHIELD:
            g = (155, False)  # Lowered across the body, clear of the baseline.
        if costume and model in (2095, 2099) and combat and frame == 1 and hand == "left" and shape != SHIELD:
            # Keep the off-hand head clear of the palm. The narrowed
            # half-elf grip falls a pixel farther in on this swing.
            g = (332 if own is not None and shape == CAHULAKS else 330, False)
        if costume and model == 2099 and combat and frame == 2 and hand == "right":
            g = (200, False)  # Keep the butt of a staff above the lower edge.
        if costume and model == 2099 and not combat and frame == 6 and hand == "left" and shape in TWO_HANDED:
            g = (52, False)
        if shape is None or g is None or shape in (SLING, BOW, CHATKCHA):
            continue
        colours = FLAME if item_type == FLAME_BLADE else _whole(SPELL_WEAPONS[item_type]) if item_type in SPELL_WEAPONS \
            else MATERIAL_COLOURS.get(material, MATERIAL_COLOURS[4])
        hx, hy = hands.get(hand, (0, 0))
        scale = MODEL_SCALE.get(model, 1.0)
        if shape in TWO_HANDED and not combat and hand == "right":
            g = UPRIGHT.get(parts.facing, g)
            if costume and model in classoutfits.DWARVES and frame == 11 and shape in (STAFF, GYTHKA):
                g = (315, False)
        elif not combat and shape != SHIELD and shape not in TWO_HANDED and parts.facing in SHEATHED:
            g = SHEATHED[parts.facing][hand]
            if costume and model in classoutfits.DWARVES and frame == 11 and shape == MACE:
                g = (130, g[1])
            hx, hy = _hip(out, parts, hx, pad)
            draw_hilt(out, body, (hx + pad, hy + pad), g[0], colours, g[1])
            scale = SHEATHED_SCALE * MODEL_SCALE.get(model, 1.0)
            blade = None  # (in its scabbard)
        if shape == SHIELD and not combat and parts.facing == sp.SIDE:
            spot = side_shield(rows, parts)
            if spot is not None:
                draw_shield(out, body, (spot[0] + pad, spot[1] + pad), SIDE_FAR, colours, True, MODEL_SCALE.get(model, 1.0), glint, shine)
        elif shape == SHIELD:
            behind = g[1] or parts.facing == sp.BACK  # (from behind: held in front of the body)
            if pose and hand == "left":
                if own is not None:  # (by the game's frame's wristbands)
                    spot = fight_shield(own.source, model, frame, own.source_parts, hands.get("right"))
                    spot = spot and (own.at(spot[0], spot[1]), spot[1], spot[2])
                else:
                    spot = fight_shield(rows, model, frame, parts, hands.get("right"))
                if spot is None:
                    continue
                hx, hy, hidden = spot
                behind = behind or hidden
            draw_shield(out, body, (hx + pad, hy + pad), parts.facing, colours, behind, MODEL_SCALE.get(model, 1.0), glint, shine)
        else:
            draw_weapon(out, body, (hx + pad, hy + pad), g[0], shape, colours, g[1], scale, blade,
                        glint and blade != FLAME and colours != FLAME and item_type not in SPELL_WEAPONS, shine)
    return out


# Body armour: not drawn on, but the character's own clothing recoloured toward the armour's
# material, every pixel of the artist's shading kept where it was: each clothing colour, by its
# place from dark to light, the material's shade at the same place. Each piece recolours its part
# of the outfit (the chest above the waist, the arms the bands and bracers by the hands, the legs
# below the waist); never the head or the hair.
ARMOUR_CHEST, ARMOUR_ARMS, ARMOUR_LEGS = "chest", "arms", "legs"
PLAIN, RINGS, STUDS, SCALES, CHAIN, PLATE = "plain", "rings", "studs", "scales", "chain", "plate"
# Material ramps use fixed retail palette entries. Class accents can still use
# their original regional colours. Adjacent folds often differ by only one shade.
LEATHER_SHADES = (208, 174, 204, 203, 207, 195, 134, 135, 205, 132, 196, 194, 59, 206,
                 144, 60, 197, 168, 65, 61, 169, 198, 199, 62, 155, 63)
BONE_SHADES = (208, 129, 204, 207, 205, 196, 194, 206, 212, 60, 213, 168, 214,
               61, 169, 198, 215, 31, 199, 66, 62, 216, 67, 217, 63, 156)
METAL_SHADES = (208, 17, 18, 19, 48, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27,
                213, 28, 214, 29, 30, 215, 31, 216, 52, 217, 46)
CHAIN_SHADES = (208, 17, 209, 19, 48, 20, 210, 21, 22, 49, 211, 24, 212, 50,
                26, 213, 28, 214, 29, 30, 215, 31, 216, 52, 217, 46)
VEILED_CLOTH = (208, 17, 18, 19, 48, 20, 21, 22, 49, 23, 211, 24, 25, 50, 26,
                27, 213, 28, 214, 29, 30, 215, 31, 216, 52, 217)
SILK_SHADES = (208, 17, 18, 209, 19, 48, 20, 58, 74, 194, 59, 206, 212, 60, 213,
               28, 214, 61, 198, 215, 199, 62, 216, 52, 217, 156)
DRAKE_SHADES = (208, 69, 188, 209, 189, 53, 70, 210, 190, 54, 191, 211, 71, 55,
                193, 56, 72, 214, 29, 57, 215, 73, 216, 52, 217, 46)
SHIMMER_SHADES = (17, 18, 19, 48, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27, 213,
                  28, 214, 29, 30, 215, 31, 216, 52, 67, 217, 46)

# Most cloth values lie below mid-grey. Give its close dark folds more steps,
# while retaining distinct entries for bright linen and bone.
GARMENT_TONE_BREAKS = (20, 27, 32, 37, 42, 47, 53, 60, 68, 74, 82, 90, 99, 109,
                       122, 140, 159, 162, 164, 172, 183, 195, 200.15, 205, 218)


def garment_tone(colour, shades):
    """Match an authored pixel's value in an equipped material's palette."""
    if colour == 254:
        return 254
    # Charcoal is the drawn outline, even beside equally dark brown leather.
    tone = 0 if colour == 208 else bisect_right(GARMENT_TONE_BREAKS, 255 * _LIGHT.get(colour, 0.5))
    return shades[round(tone * (len(shades) - 1) / len(GARMENT_TONE_BREAKS))]


def dye_garment(rows, cells, shades, pad, source):
    """Transfer the original seams and highlights into the equipped material's palette."""
    for x, y in cells:
        colour = source[y + pad][x + pad]
        if colour is not None and colour != 254:
            rows[y + pad][x + pad] = garment_tone(colour, shades)


# item type: (which piece, shades, pattern)
ARMOUR: Dict[int, Tuple[str, Tuple[int, ...], str]] = {
    6: (ARMOUR_CHEST, LEATHER_SHADES, PLAIN), 7: (ARMOUR_ARMS, LEATHER_SHADES, PLAIN), 8: (ARMOUR_LEGS, LEATHER_SHADES, PLAIN),
    9: (ARMOUR_CHEST, BONE_SHADES, RINGS), 10: (ARMOUR_ARMS, BONE_SHADES, RINGS), 11: (ARMOUR_LEGS, BONE_SHADES, RINGS),
    12: (ARMOUR_CHEST, BONE_SHADES, STUDS), 13: (ARMOUR_ARMS, BONE_SHADES, STUDS), 14: (ARMOUR_LEGS, BONE_SHADES, STUDS),
    15: (ARMOUR_CHEST, BONE_SHADES, SCALES), 55: (ARMOUR_ARMS, BONE_SHADES, SCALES), 56: (ARMOUR_LEGS, BONE_SHADES, SCALES),
    57: (ARMOUR_CHEST, CHAIN_SHADES, CHAIN), 58: (ARMOUR_ARMS, CHAIN_SHADES, CHAIN), 59: (ARMOUR_LEGS, CHAIN_SHADES, CHAIN),
    54: (ARMOUR_ARMS, METAL_SHADES, SCALES), 24: (ARMOUR_LEGS, METAL_SHADES, SCALES),  # Grey's Scale
    88: (ARMOUR_CHEST, METAL_SHADES, PLATE), 25: (ARMOUR_ARMS, METAL_SHADES, PLATE), 26: (ARMOUR_LEGS, METAL_SHADES, PLATE),
    79: (ARMOUR_CHEST, DRAKE_SHADES, SCALES), 82: (ARMOUR_CHEST, SHIMMER_SHADES, PLAIN), 90: (ARMOUR_CHEST, SILK_SHADES, PLAIN),
    game.PLATE_CHEST_TYPE: (ARMOUR_CHEST, METAL_SHADES, PLATE), game.PLATE_ARMS_TYPE: (ARMOUR_ARMS, METAL_SHADES, PLATE),
    game.PLATE_LEGS_TYPE: (ARMOUR_LEGS, METAL_SHADES, PLATE),  # the Warden's Plate (worldgear.py)
    game.BRACERS_TYPE: (ARMOUR_ARMS, SHIMMER_SHADES, PLAIN),  # bracers of defense: steel at the wrists
    game.ROBE_TYPE: (ARMOUR_CHEST, CHAIN_SHADES, PLAIN),  # the robes (robes.py): grey cloth
}
# Each model's clothing colours, dark to light (by hand: not its skin, hair, eyes or wristbands;
# black only inside the outline). The human and half-elf woman's green cloak stays as it is.
CLOTHES: Dict[int, Tuple[int, ...]] = {
    2053: (254, 208, 209, 210, 211, 212, 50),
    2055: (254, 208, 209, 210, 211, 212, 50),
    2059: (254, 16, 174, 69, 175, 210, 176, 58, 37, 177, 36, 24, 178),
    2061: (254, 158, 16, 69, 159, 175, 48, 38, 210, 160, 37, 49, 36, 24, 71, 39, 161),
    2068: (254, 17, 18, 209, 48, 179, 210, 22, 180, 64, 181, 182, 168, 183, 184),
    2070: (254, 208, 209, 210),
    2072: (254, 208, 209, 207, 19, 210, 205, 49, 211, 212),
    2074: (254, 208, 209, 210, 211),
    2093: (254, 208, 209, 48, 210, 23, 50),
    2095: (254, 48, 20, 210, 23, 212, 50, 213, 29),
    2099: (254,),
}

def _keep_out(rows: Rows, parts: sp.Parts) -> set:
    """What armour never recolours: the head (its box down to where the shoulders start), the
    hair, and any pixel among the hair (its dark strands, in the clothes' own colours)."""
    out = set(parts.hair)
    if parts.head and parts.shoulders:
        h, neck = parts.head, parts.shoulders[0]
        out |= {(x, y) for y in range(h.top, neck) for x in range(h.left, h.right + 1)}
    for _ in range(2):
        among = set()
        for y, row in enumerate(rows):
            for x, p in enumerate(row):
                if p is None or (x, y) in out:
                    continue
                if sum((x + dx, y + dy) in parts.hair for dx in (-1, 0, 1) for dy in (-1, 0, 1)) >= 2:
                    among.add((x, y))
        out |= among
    return out


def _pattern(pattern: str, x: int, y: int, shade: int, top: int) -> int:
    """The shade (0 the darkest) with a light touch of the armour's pattern, on its lighter shades."""
    if shade < 2:
        return shade
    if pattern == PLATE and shade >= top - 2 and (x + 2 * y) % 5 == 0:
        return min(top, shade + 1)  # short specular edges on the brightest planes
    if pattern == CHAIN and (x + y) % 2 == 0:
        return shade - 1  # (mail's fine weave)
    if pattern == SCALES and y % 2 == 1 and (x + (y // 2) % 2) % 2 == 0:
        return shade - 1  # (the scales' lower edges, offset row to row)
    if pattern in (RINGS, STUDS) and x % 3 == 1 and y % 3 == 1:
        return min(top, shade + 1)  # (a ring's or stud's glint)
    return shade


def shine_armour(rows, cells, piece, parts, pad, colours, cuffs=()):
    """Place cycling highlights on separated folds of *each* visible armour piece."""
    if not cells:
        return
    # The sleeve nearest each hand and the cloth above each sole can be a long
    # way apart in a strike. Give even the smaller exposed limb its own highlight.
    anchors = []
    if piece == ARMOUR_ARMS:
        anchors = [(sum(x for x, y in cuff)/len(cuff), sum(y for x, y in cuff)/len(cuff)) for cuff in cuffs]
        if len(anchors) < 2:
            anchors = list(parts.hands.values())
    elif piece == ARMOUR_LEGS:
        anchors = [((left + right) / 2, y) for y, left, right in parts.feet]
    groups = [[] for _ in anchors] or [[]]
    for x, y in cells:
        nearest = (min(range(len(anchors)), key=lambda i: (x-anchors[i][0])**2 + (y-anchors[i][1])**2)
                   if len(anchors) > 1 else 0)
        groups[nearest].append((x, y))

    chosen = []
    def highlights(points, count):
        # Bisect along the garment's longer extent to reach its upper and lower
        # folds, even on a narrow profile. Choose a lit material tone in each area.
        xs, ys = zip(*points)
        if count == 1:
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            def score(p):
                x, y = p
                value = _LIGHT.get(rows[y + pad][x + pad], 0.5)
                return value - 0.025*(abs(x-cx) + abs(y-cy)), -y, -x
            chosen.append(max(points, key=score))
            return
        axis = 0 if max(xs)-min(xs) >= max(ys)-min(ys) else 1
        ordered = sorted(points, key=lambda p: (p[axis], p[1-axis]))
        low, high = ordered[0][axis], ordered[-1][axis]
        if count == 2 and high-low >= 3:
            # A diagonal strap can be only one pixel wide. Light its two
            # ends in turn and retain the leather shadow between them.
            margin = (high-low-3)//2
            highlights([p for p in ordered if p[axis] <= low+margin], 1)
            highlights([p for p in ordered if p[axis] >= high-margin], 1)
            return
        half = count // 2
        cut = len(points)*half // count
        highlights(ordered[:cut], half)
        highlights(ordered[cut:], count-half)

    for region in groups:
        if region:
            count = max(1, (len(region)+4)//6)
            if count == 1 and len(region) >= 4:
                xs, ys = zip(*region)
                if max(max(xs)-min(xs), max(ys)-min(ys)) >= 3:
                    count = 2
            highlights(region, count)
    # Neighbouring highlights start at different points in the icon's DAC cycle,
    # so several parts of the worn piece can be read even on a stationary figure.
    phase = {ARMOUR_CHEST: 0, ARMOUR_ARMS: 2, ARMOUR_LEGS: 4}[piece]
    for i, (x, y) in enumerate(sorted(chosen, key=lambda p: (p[0]+2*p[1], p))):
        rows[y+pad][x+pad] = colours[(phase + 2*i) % len(colours)]


def draw_armour(rows: Rows, model: int, parts: sp.Parts, item_type: int, pad: int,
                own: Optional[Own] = None, veiled: bool = False, source: Optional[Rows] = None,
                covered=()) -> List[sp.Point]:
    """One piece of armour: the model's clothing (OWN's, a figure of its own) in its part of the
    (padded) picture ROWS recoloured into the armour's shades (never black within its own cloak)."""
    piece, shades, _ = ARMOUR[item_type]
    if veiled and item_type == game.ROBE_TYPE:
        shades = VEILED_CLOTH
    clothes = own.clothes if own is not None and own.clothes else CLOTHES.get(model, ())
    cloak = own.cloak if own is not None else CLOAK_GREENS if model == CLOAK_MODEL else frozenset()
    cells = []
    if not clothes or parts.waist is None:
        return cells
    rank = {c: i / max(1, len(clothes) - 1) for i, c in enumerate(clothes)}
    top = len(shades) - 1
    source = rows if source is None else source
    unpadded = [r[pad:len(r) - pad] for r in source[pad:]]
    keep_out = _keep_out(unpadded, parts)
    keep_out.update(covered)
    hands = list(parts.hands.values())
    for y, row in enumerate(unpadded):
        for x, p in enumerate(row):
            if p not in rank or (x, y) in keep_out or (own is not None and own.worn is not None and (x, y) not in own.worn):
                continue
            if p == 254 and any(not (0 <= y + dy < len(unpadded) and 0 <= x + dx < len(row))
                                or unpadded[y + dy][x + dx] is None
                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue  # (black at the edge is the outline, not clothing)
            if p == 254 and cloak and sum(0 <= y + dy < len(unpadded) and 0 <= x + dx < len(row)
                                          and unpadded[y + dy][x + dx] in cloak
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2:
                continue  # (a fold of the figure's own cloak)
            by_hand = any(abs(x - hx) <= 2 and hy - 4 <= y <= hy + 1 for hx, hy in hands)
            part = ARMOUR_ARMS if by_hand else (ARMOUR_CHEST if y <= parts.waist else ARMOUR_LEGS)
            if part != piece:
                continue
            shade = min(top, int(rank[p] * top + 0.5))
            rows[y + pad][x + pad] = shades[shade]
            cells.append((x, y))
    return cells
