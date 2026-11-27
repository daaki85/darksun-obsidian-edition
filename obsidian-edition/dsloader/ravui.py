"""Shattered Lands' interface in Wake of the Ravager: the screens' pictures and the icons, taken from the
player's own Shattered Lands RESOURCE.GFF into the Loader's copy of the sequel's (RESOURC2.GFF:
ravager.resources_fixed), as darksun-recompiled's `tools/sl_figures.py build-ui` makes them (seen in the game
there 2026-11-20: docs/FIGURES.md, "The interface (phase 1)"; the owner's choice to have it in the mod,
2026-11-27).

  * PICTURES: 45 interface pictures (BMP) that are the same drawing, size and frame count in both games (the
    sequel's are Shattered Lands' art in fewer colours). Left out: 11000 and 20029 (Shattered Lands' are cut
    away on one side), 13005 (a second frame in the sequel), 20125 and 20126-20134 (other pictures), 12000
    and 20000-20013 (other sizes: the sequel's portrait frame and creation figures are larger).
  * ICONS: {the sequel's icon: Shattered Lands' icon of the same drawing}, 221 of them, 130 from another
    number (the sequel renumbered part of its spell list). Matched by look by sl_figures.py's icon_pairs on
    the GOG releases (the nearest of Shattered Lands' icons of the same size and frames, within a mean RGB
    distance of 36.5) and kept here as numbers, since matching takes seconds a start. The MORE and scroll
    buttons (12100-12102) stay the sequel's: they sit on its own talk boxes, where Shattered Lands' dimmed
    frame showed as a lavender ghost.
  * Colours: Shattered Lands' interface palette (its PAL 1000) into the nearest of the sequel's colours that
    every region's palette has as PAL 1000 does (ravitems.stable_colours: the interface is drawn over the map
    in the region's palette), but the cycled runs (1-31) and the system colours (240-248).

Run-length frames (Shattered Lands' kind) are drawn by the sequel among its own packed ones. A chunk the
Loader has already changed in the copy (the mod's own icons, the kit pages ...) is left as the mod has it, and
anything missing (no Shattered Lands folder, another release's files) leaves the sequel's own: `chunks` gives
none. SKIP ("sl_interface") leaves it all out: the Options tab's box (SETTING, on by default) and RAV_SKIP's control."""

import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, gff

SKIP = "sl_interface"  # (resources_fixed's name for it, a SKIP's to leave it out)
SETTING = "sl_interface"  # (the Options tab's box in its Wake of the Ravager section: ravager.skipped)
PALETTE = ("PAL ", 1000)  # (the interface's palette, in both games' RESOURCE.GFF)
KEPT = set(range(0, 32)) | set(range(240, 249))  # (cycled and system colours: never a target)

PICTURES = (10000, 10001, 10002, 10003, 10004, 13000, 13001, 13002, 13003, 13004, 13007, 13008, 14000,
            15000, 15001, 15002, 17000, 17001, 17002, 20028, 20047, *range(20048, 20059), 20075, 20079,
            20080, 20083, 20084, 20085, 20086, 20087, 20088, 20104, 20105, 20106, 20107)

_SAME = ((100, 100), (2002, 2009), (2038, 2047), (3044, 3045), (10100, 10102), (10105, 10105), (10107, 10108),
         (10113, 10113), (11100, 11111), (13006, 13006), (14101, 14103), (15101, 15109), (16100, 16105),
         (18100, 18100), (21000, 21000), (21003, 21005), (21007, 21009), (21011, 21011), (21013, 21013),
         (21015, 21020), (21022, 21024), (21026, 21026), (21029, 21031), (21052, 21053), (21055, 21055),
         (21057, 21060), (21063, 21064))  # (icons of the same number in both games)
_MOVED = {
    18101: 6030, 18102: 6031, 18103: 6036, 18104: 6037, 18105: 6038, 18106: 6039, 18107: 2056, 18108: 2057,
    18109: 2058, 18110: 2097, 19100: 2000, 19101: 6001, 19102: 6002, 19103: 6003, 19104: 6004, 19105: 6005,
    19106: 6006, 19107: 6007, 19108: 6008, 19109: 6009, 19110: 6010, 19111: 2048, 19112: 2049, 19113: 2050,
    19114: 2051, 19115: 3101, 19116: 3102, 19117: 3103, 19118: 3104, 19119: 3105, 19120: 3106, 19121: 3100,
    19122: 21037, 21035: 21036, 21036: 21037, 21037: 21038, 21038: 21039, 21042: 21044, 21043: 21045,
    21044: 21046, 21045: 21047, 21046: 21006, 21049: 21050, 21050: 21051, 21065: 21066, 21067: 21068,
    21072: 3001, 21115: 21069, 21116: 21070, 21117: 21071, 21118: 21072, 21119: 21073, 21120: 21074,
    21121: 21075, 21122: 21076, 21123: 21077, 21126: 21079, 21127: 21080, 21129: 21081, 21132: 21083,
    21133: 21084, 21136: 21030, 21138: 21087, 21139: 21088, 21141: 21089, 21146: 21094, 21147: 21095,
    21148: 21096, 21149: 21097, 21150: 21026, 21152: 21099, 21153: 21100, 21155: 21101, 21156: 21102,
    21157: 21103, 21158: 21104, 21159: 21105, 21164: 21106, 21165: 21060, 21166: 21108, 21167: 21109,
    21168: 21110, 21169: 21111, 21170: 21112, 21171: 21113, 21172: 21114, 21173: 21115, 21175: 21117,
    21178: 21118, 21179: 21119, 21182: 21076, 21183: 21122, 21189: 21123, 21191: 21125, 21194: 21127,
    21195: 21128, 21196: 21129, 21197: 21130, 21199: 21132, 21200: 21133, 21202: 21134, 21203: 21135,
    21204: 21136, 21224: 21135, 21235: 3000, 21236: 3001, 21237: 3002, 21238: 3003, 21240: 3005, 21241: 3006,
    21242: 3007, 21243: 3008, 21244: 3009, 21245: 3010, 21246: 3011, 21247: 3012, 21248: 3013, 21249: 3014,
    21250: 3015, 21251: 3016, 21252: 3017, 21253: 3018, 21254: 3019, 21258: 3023, 21259: 3024, 21262: 3027,
    21263: 3028, 21264: 3029, 21265: 3030, 21268: 3033}  # (the sequel's icon: Shattered Lands' of another number)
ICONS: Dict[int, int] = {**{i: i for a, b in _SAME for i in range(a, b + 1)}, **_MOVED}
ICON_KEEP = (12100, 12101, 12102)  # (never matched: the MORE and scroll buttons)
# (the inventory and shop screens' right-hand panel, Shattered Lands' smooth grey: mapped colour for colour
# its top came out lighter and its foot darker, 16 greys onto the sequel's 7, 2026-11-27's shop comparison;
# DITHERED's pictures mix the two kept colours either side of each of Shattered Lands' instead: `dithered`)
DITHERED = (13004,)
NEAR = 40  # (a mix only of colours within this of Shattered Lands' in each of red, green and blue)
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def colour_table(sl_palette: Sequence[Tuple[int, int, int]], stable: Sequence[Tuple[int, Tuple[int, int, int]]]) -> Dict[int, int]:
    """{Shattered Lands' palette number: the nearest of STABLE's (ravitems.stable_colours), but KEPT's}."""
    targets = [(c, rgb) for c, rgb in stable if c not in KEPT]
    if not targets:
        raise ValueError("no colour every region keeps")
    return {i: min(targets, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], rgb)))[0]
            for i, rgb in enumerate(sl_palette)}


def _mix(rgb: Tuple[int, int, int], targets: Sequence[Tuple[int, Tuple[int, int, int]]]) -> Tuple[int, int, float]:
    """(a, b, t): RGB as a + t (b - a), a and b of TARGETS within NEAR of it (the nearest alone if none)."""
    def far(e):
        return sum((u - v) ** 2 for u, v in zip(e[1], rgb))
    nearest = min(targets, key=far)
    best = (far(nearest), nearest[0], -1, 0.0)
    close = [e for e in targets if max(abs(u - v) for u, v in zip(e[1], rgb)) <= NEAR]
    for a, ra in close:
        for b, rb in close:
            d = [y - x for x, y in zip(ra, rb)]
            dd = sum(v * v for v in d)
            if not dd:
                continue
            t = max(0.0, min(1.0, sum((p - x) * v for p, x, v in zip(rgb, ra, d)) / dd))
            e = sum((p - (x + t * v)) ** 2 for p, x, v in zip(rgb, ra, d))
            if e < best[0] - 1e-9:
                best = (e, a, b, t)
    return best[1], best[2], best[3]


def dithered(chunk: bytes, sl_palette: Sequence[Tuple[int, int, int]],
             stable: Sequence[Tuple[int, Tuple[int, int, int]]]) -> bytes:
    """A one-frame Shattered Lands picture in the sequel's STABLE colours (but KEPT's), each pixel one of the
    two either side of its colour by a 4 by 4 ordered pattern, so a smooth shade keeps its tone."""
    from . import icons
    targets = [(c, rgb) for c, rgb in stable if c not in KEPT]
    if not targets:
        raise ValueError("no colour every region keeps")
    mixes: Dict[int, Tuple[int, int, float]] = {}
    out = []
    for y, row in enumerate(icons.decode(chunk)):
        line = []
        for x, p in enumerate(row):
            if not p:
                line.append(p)
                continue
            if p not in mixes:
                mixes[p] = _mix(sl_palette[p], targets)
            a, b, t = mixes[p]
            line.append(b if b >= 0 and t * 16 > BAYER[y % 4][x % 4] + 0.5 else a)
        out.append(line)
    return icons.encode(out)


def wanted() -> List[Tuple[Tuple[str, int], Tuple[str, int]]]:
    """[(the sequel's chunk, Shattered Lands' chunk drawn in its place)]."""
    return [(("BMP ", p), ("BMP ", p)) for p in PICTURES] + [(("ICON", w), ("ICON", s)) for w, s in sorted(ICONS.items())]


def made(sequel: gff.Chunks, sl: gff.Chunks, region_palettes: Sequence[bytes],
         stock: Optional[gff.Chunks] = None) -> gff.Chunks:
    """The chunks for the sequel's RESOURCE.GFF (SEQUEL, as the Loader's copy has it so far; STOCK the game's
    own, SEQUEL if none): Shattered Lands' (SL) pictures and icons, recoloured; each only where SEQUEL's chunk
    is still STOCK's and SL has its own."""
    from . import icons, ravitems
    stock = sequel if stock is None else stock
    sl_palette = art.palette_colours(sl[PALETTE])
    stable = ravitems.stable_colours(sequel, region_palettes)
    table = colour_table(sl_palette, stable)
    out = {}
    for ours, theirs in wanted():
        if ours[1] in ICON_KEEP or ours not in sequel or theirs not in sl or sequel[ours] != stock.get(ours):
            continue
        if ours[0] == "BMP " and ours[1] in DITHERED and struct.unpack_from("<H", sl[theirs], 4)[0] == 1:
            out[ours] = dithered(sl[theirs], sl_palette, stable)
        else:
            out[ours] = icons.recolour_frames(sl[theirs], table)
    return out


def region_palettes(game_dir: str) -> List[bytes]:
    """Every region's map palette in the sequel's folder (ravitems.region_palettes)."""
    from . import ravitems
    return ravitems.region_palettes(game_dir)


def chunks(sequel: gff.Chunks, sl_dir: Optional[str], game_dir: Optional[str],
           stock: Optional[gff.Chunks] = None) -> gff.Chunks:
    """`made` from the player's files: Shattered Lands' RESOURCE.GFF in SL_DIR, the regions in GAME_DIR (the
    sequel's folder). None without them, or with files `made` can't read."""
    path = sl_dir and art._find(sl_dir, "RESOURCE.GFF")
    if not path or not game_dir:
        return {}
    try:
        with open(path, "rb") as f:
            sl = gff.read_gff(f.read())
        palettes = region_palettes(game_dir)
        if not palettes or PALETTE not in sl or PALETTE not in sequel:
            return {}
        return made(sequel, sl, palettes, stock)
    except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
        return {}
