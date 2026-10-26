"""The Bowyer's archery target in Teaquetzl (script 178, run when the target is shot at): the dice
log's line for each shot.

The script, as the game has it: the archer's distance from the target (its distance command, in
squares) under 5 is a bull's eye with no roll. Otherwise the shot needs a random 0-20 under
DEX - distance / 2 (2 if DEX is under the distance); 10 or more under it is the centre, the outer
ring under 5, the inner one under 10. The centre from more than 13 squares, with the Bowyer
within 25 of the archer, has him give 6 Arrows +2, once (flag 642).

The script counts the archer's bows in hand by their objects, the game's three (the bow, the Bow +2
and Phrain's Bow); the Loader's copy counts Dunesong (the Loader's bow +1, which the Bowyer sells)
with them (with_dunesong).

DSCLOG records the roll as any script's random command (PROBE_SCRIPT_RAND), its position past the
command (POSITION, in script 178 only); the distances are worked out as the game does (DISTANCE)
from the map's things where they stand.
"""

from typing import Dict, List, Optional, Tuple

from . import gpl

SCRIPT = 178
POSITION = 0x57F  # the random command's (57Ch) position past it, as DSCLOG records it
MOST = 20
TARGET, BOWYER = 1314, 283  # their objects
REWARD_FLAG = 642
NO_ROLL = 5  # closer: a bull's eye with no roll
FAR = 13  # the centre from farther gets the reward
BOWYER_NEAR = 25  # the Bowyer must be closer than this to the archer
CENTRE, INNER = 10, 5  # how far under what's needed the roll must be
FAR_AWAY = 999  # the game's distance when either side is more than 255 squares apart


def distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """The game's distance in squares (DSUN.EXE DD8Ch): the least n from its estimate with
    n * n + n at least dx * dx + dy * dy."""
    dx, dy = abs(x1 - x2), abs(y1 - y2)
    if dx > 255 or dy > 255 or dx * dx + dy * dy > 0xFFFF:
        return FAR_AWAY
    square = dx * dx + dy * dy
    most, least = max(dx, dy), min(dx, dy)
    guess = least + (least >> 1)
    add = least >> 2
    if guess <= most:
        add = add >> 1 if guess * 2 > most else 0
    n = most + add
    while n * n + n < square:
        n += 1
    return n


def need(dex: int, target: int) -> int:
    """What the roll must be under."""
    return 2 if dex < target else dex - target // 2


def describe(roll: int, dex: int, target: int, bowyer: Optional[int], given: bool, who: str) -> List[str]:
    """The dice log's line for a shot: the roll, what it needed, the distances and the result."""
    needed = need(dex, target)
    how = f"DEX {dex} under {target}: 2" if dex < target else f"DEX {dex} - {target} / 2"
    where = f"{target} squares from the target" + (f", {bowyer} from the Bowyer" if bowyer is not None else "")
    head = f"{who} shoots at the archery target ({where}): 0-{MOST} = {roll}, needs under {needed} ({how}), " \
           f"the centre {needed - CENTRE} or less"
    if roll >= needed:
        return [f"{head} -> miss"]
    under = needed - roll
    if under < INNER:
        return [f"{head} -> the outer ring"]
    if under < CENTRE:
        return [f"{head} -> the inner ring"]
    if target <= FAR:
        return [f"{head} -> the centre, no reward: {FAR} squares or closer"]
    if given:
        return [f"{head} -> the centre, no reward: the Bowyer gives his arrows once"]
    if bowyer is None or bowyer >= BOWYER_NEAR:
        return [f"{head} -> the centre, no reward: the Bowyer {BOWYER_NEAR} squares or more away"]
    return [f"{head} -> the centre: the Bowyer's reward, 6 Arrows +2"]


# Dunesong among the bows the script counts: at SUM (var 4 = var 1 + (var 2 + var 3), the three
# bows' counts) a jump to code added at the script's end, which counts Dunesong as PHRAIN (the
# count of Phrain's Bow) does into var 5 (set again before the roll's own use of it), adds the four
# and jumps back to SUM_NEXT: nothing in the script moves (POSITION stays where it is).
DUNESONG = 2594  # its object
PHRAIN, SUM, SUM_NEXT = 0x3FA, 0x40D, 0x41A
PHRAIN_COUNT = bytes.fromhex("168c3389254d5048049175375355048f028203")  # var 3 = Phrain's Bows in hand
SET, GOTO = 0x16, 0x64


# (never run, after the jump: a command, so the script still reads command by command)
FILLER = gpl.encode_op((SET, [("expr", ["(", ("var", 130, 6), ")", "+", ("n", 0)]), ("var", 2, 6)]))
SUM_THREE = gpl.encode_op((SET, [("expr", [("var", 130, 1), "+", "(", ("var", 130, 2), "+", ("var", 130, 3), ")"]),
                                 ("var", 2, 4)]))


def with_dunesong(script: bytes) -> bytes:
    """Script 178 (the game's) counting Dunesong among the bows; unchanged if it isn't as expected
    (or has it already)."""
    if script[PHRAIN:SUM] != PHRAIN_COUNT or script[SUM:SUM_NEXT] != SUM_THREE:
        return script
    count = PHRAIN_COUNT[:9] + bytes.fromhex("91") + DUNESONG.to_bytes(2, "big") + PHRAIN_COUNT[12:-1] + bytes((5,))
    four = gpl.encode_op((SET, [("expr", [("var", 130, 1), "+", "(", ("var", 130, 2), "+", "(", ("var", 130, 3), "+",
                                          ("var", 130, 5), ")", ")"]), ("var", 2, 4)]))
    added = count + four + gpl.encode_op((GOTO, [("n", SUM_NEXT)]))
    jump = gpl.encode_op((GOTO, [("n", len(script))])) + FILLER
    if len(jump) != SUM_NEXT - SUM:
        return script
    out = bytearray(script)
    out[SUM:SUM_NEXT] = jump
    return bytes(out) + added


def script_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    key = ("GPL ", SCRIPT)
    if key not in chunks:
        return {}
    changed = with_dunesong(chunks[key])
    return {key: changed} if changed != chunks[key] else {}
