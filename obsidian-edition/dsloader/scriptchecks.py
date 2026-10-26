"""The ability checks the game's scripts make with their random command rather than the ability
check command (gpl.ABILITY_CHECK): a condition comparing a random number with an ability of the
character acting, as Chahl's "random(19) <= CHA" when asked about his scars (script 181), the
chains a strong character breaks (76) or the secret door an intelligent one spots (69, INT - 10).

DSCLOG's PROBE_SCRIPT_RAND records each random command with the script's position past it
(searches.py); the conditions are found by that position in the scripts the game runs (the
Loader's copy of GPLDATA.GFF), and the dice log says what the roll needed and whether it did it.
"""

import os
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import gpl

ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
ABILITY_FIELDS = {23 + n: n for n in range(6)}  # an object's fields 23 to 28: STR to CHA
ACTING = 0x8025  # the object "the character acting" (gpl.FIELD_SPECIAL 25h)
RANDOM = 0x52  # the scripts' random command: 0 to its N, each as likely
PAST = 3  # the position DSCLOG records: the command, its N (the searches' too: searches.SEARCHES)
COMPARISONS = ("==", "!=", ">", "<", ">=", "<=")
_LEVELS = (("or",), ("and",), ("|", "^", "&"), COMPARISONS, ("+", "-"), ("*", "/"))


class Check(NamedTuple):
    script: str  # "GPL 181"
    most: int  # the random command's N
    ability: int  # 0 STR ... 5 CHA
    expr: list  # the condition's tokens (gpl's)


def _tokens(expr) -> Optional[list]:
    return expr[1] if isinstance(expr, tuple) and expr and expr[0] == "expr" else None


def _is_random(t) -> bool:
    return isinstance(t, tuple) and t[0] == "op" and t[1].code == RANDOM


def _ability_of(t) -> Optional[int]:
    if isinstance(t, tuple) and t[0] == "field" and t[1] == ACTING and len(t[2]) == 1:
        return ABILITY_FIELDS.get(t[2][0])
    return None


def find(scripts: Dict[Tuple[str, int], bytes], field_types: bytes) -> Dict[int, Check]:
    """Each condition with one random command and one ability of the character acting, by the
    position DSCLOG records for its random command. A position two scripts share is left out."""
    found: Dict[int, Check] = {}
    shared = set()
    for (ctype, cid), data in sorted(scripts.items()):
        try:
            ops = gpl.decode(data, field_types)
        except (gpl.ScriptError, ValueError, IndexError, KeyError):
            continue
        for op in gpl.walk(ops):
            for arg in op.args:
                tokens = _tokens(arg)
                if not tokens:
                    continue
                rolls = [t for t in tokens if _is_random(t)]
                abilities = {_ability_of(t) for t in tokens} - {None}
                if len(rolls) != 1 or len(abilities) != 1 or not any(t in COMPARISONS for t in tokens):
                    continue
                most = rolls[0][1].args[0]
                if most[0] != "n":
                    continue
                at = rolls[0][1].at + PAST
                if at in found or at in shared:
                    shared.add(at)
                    found.pop(at, None)
                    continue
                found[at] = Check(f"{ctype.strip()} {cid}", most[1], abilities.pop(), tokens)
    # (any other random command at the same position: the position alone tells them apart)
    for (ctype, cid), data in scripts.items():
        try:
            ops = gpl.decode(data, field_types)
        except (gpl.ScriptError, ValueError, IndexError, KeyError):
            continue
        for op in gpl.walk(ops):
            at = op.at + PAST
            if op.code == RANDOM and at in found and found[at].script != f"{ctype.strip()} {cid}":
                del found[at]
    return found


_cache: Dict[str, Dict[int, Check]] = {}


def load(path: str) -> Dict[int, Check]:
    """The checks in the GPLDATA.GFF at PATH (read once); none if it can't be read."""
    if path not in _cache:
        try:
            with open(path, "rb") as f:
                _cache[path] = find(*gpl.load_scripts(f.read()))
        except (OSError, ValueError, KeyError, gpl.ScriptError):
            _cache[path] = {}
    return _cache[path]


def evaluate(tokens: list, roll: int, ability: int) -> int:
    """The condition's value with the random command's ROLL and the ability ABILITY."""
    pos = 0

    def term() -> int:
        nonlocal pos
        t = tokens[pos]
        pos += 1
        if t == "(":
            v = level(0)
            pos += 1  # ")"
            return v
        if t == "-":
            return -term()
        if _is_random(t):
            return roll
        if _ability_of(t) is not None:
            return ability
        if isinstance(t, tuple) and t[0] == "n":
            return t[1]
        raise ValueError(f"not a number: {t!r}")

    def level(n: int) -> int:
        nonlocal pos
        if n == len(_LEVELS):
            return term()
        v = level(n + 1)
        while pos < len(tokens) and tokens[pos] in _LEVELS[n]:
            o = tokens[pos]
            pos += 1
            w = level(n + 1)
            v = {"or": lambda: int(bool(v or w)), "and": lambda: int(bool(v and w)), "|": lambda: v | w,
                 "^": lambda: v ^ w, "&": lambda: v & w, "==": lambda: int(v == w), "!=": lambda: int(v != w),
                 ">": lambda: int(v > w), "<": lambda: int(v < w), ">=": lambda: int(v >= w),
                 "<=": lambda: int(v <= w), "+": lambda: v + w, "-": lambda: v - w, "*": lambda: v * w,
                 "/": lambda: int(v / w) if w else 0}[o]()
        return v

    return level(0)


def _bare(tokens: list) -> list:
    while len(tokens) >= 2 and tokens[0] == "(" and tokens[-1] == ")":
        depth = 0
        for i, t in enumerate(tokens):
            depth += (t == "(") - (t == ")")
            if depth == 0 and i < len(tokens) - 1:
                return tokens
        tokens = tokens[1:-1]
    return tokens


def _sides(tokens: list) -> Tuple[list, list]:
    """The condition's two sides, split at its comparison outside brackets."""
    tokens = _bare(tokens)
    depth = 0
    for i, t in enumerate(tokens):
        depth += (t == "(") - (t == ")")
        if depth == 0 and t in COMPARISONS:
            return tokens[:i], tokens[i + 1:]
    return tokens, []


def _text(tokens: list, ability: int, value: int) -> str:
    out = []
    for t in _bare(tokens):
        if _ability_of(t) is not None:
            out.append(f"{ABILITIES[ability]} {value}")
        elif isinstance(t, tuple) and t[0] == "n":
            out.append(str(t[1]))
        elif isinstance(t, str):
            out.append(t)
    return " ".join(out).replace("( ", "(").replace(" )", ")")


def _shift(tokens: list) -> int:
    """What the roll's side adds to the random number ("(random(19)) + 1": 1), so the roll can
    be told as the die it is (1 to 20)."""
    side = _bare(next((s for s in _sides(tokens) if any(_is_random(t) for t in s)), []))
    try:
        return evaluate(side, 0, 0) if side else 0
    except (ValueError, IndexError):
        return 0


def describe(check: Check, roll: int, ability: int, who: str) -> List[str]:
    """The dice log's line: who checked what, the roll as its die, what it needed and the result."""
    shift = _shift(check.expr)
    low, high = shift, check.most + shift
    die = f"d{high}" if low == 1 else f"{low}-{high}"
    # the outcome the ability favours: the condition's value with the best score and the lowest roll
    try:
        good = evaluate(check.expr, 0, 25)
        made = [r + shift for r in range(check.most + 1) if evaluate(check.expr, r, ability) == good]
        success = evaluate(check.expr, roll, ability) == good
    except (ValueError, IndexError, ZeroDivisionError):
        return []
    if not made:
        need = "can't be made"
    elif len(made) == check.most + 1:
        need = "always made"
    elif made == list(range(low, made[-1] + 1)):
        need = f"needs {made[-1]} or less"
    elif made == list(range(made[0], high + 1)):
        need = f"needs {made[0]} or more"
    else:
        need = "needs " + ", ".join(map(str, made))
    side = next((s for s in _sides(check.expr) if any(_ability_of(t) is not None for t in s)), [])
    name = ABILITIES[check.ability]
    return [f"{who} {name} check: {die} = {roll + shift}, {need} "
            f"({_text(side, check.ability, ability)}) -> {'success' if success else 'failure'}"]


def default_path() -> str:
    from . import launch
    return os.path.join(launch.DOS_DIR, "GPLDATA.GFF")
