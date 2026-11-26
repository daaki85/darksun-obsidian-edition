"""A draft of the quest table (quests.py), read from the game's scripts: for developers.

    python -m dsloader.questdraft GPLDATA.GFF [-o draft.txt] [--flag N ...] [--script N]

The game gives a quest's experience points in two ways. Most go through two routines of script
74: at 135 for each party member and at 171 for one person, the amount put in global number 16
just before (ring.py), and the routine says "... receives N experience points!". The rest are
given by the script itself (command 21h: who, how many) with words of its own ("Congratulations!
The party gains ..."). For each such place this prints the script, the amount, whose reward it
is, the flags and numbers set beside it (candidates for the quest's "done" flag), the flags the
script tests and sets before it (candidates for "given"), the other scripts that set or test
those flags, and the text nearest it, for a person to read and name the quest in the project's
own words.

The draft holds the game's text: it is printed, or written to a file of your choosing outside the
repository, and never kept in it. `--flag N` prints instead every place flag N is set or tested,
with the text near each; `--script N` the rewards of one script only.

The functions here are what tests/test_quests.py checks the table against (with DSUN_GPLDATA).
"""

import argparse
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import gpl

XP_SCRIPT = 74
XP_PARTY, XP_ONE = 135, 171  # script 74's routines: each party member, one person
XP_NUMBER = 16  # the global number the amount is put in
CALL, SET, GIVE_XP = 0x14, 0x16, 0x21
PARTY = 0x7FFE  # "who" of GIVE_XP for each party member
FLAG_READ, FLAG_SET, NUMBER_SET = 0x8D, 13, 7  # a flag read in a value; set as a destination; a number set
NEAR = 12  # commands either side of a reward a "done" flag is looked for in
# script 74 clears some flags at 251-361, a routine run as a region is entered: each region's own
# scratch flags, no use to a table (317 and 318 are set beside two rewards)
SCRATCH_AT = (251, 361)
TEXT_NEAR = 700  # bytes either side of a reward (or a flag's use) whose text is shown


class Use(NamedTuple):
    """A flag set (VALUE: the number it is set to, None when it isn't a plain number) or tested
    (SET False) by a script."""
    flag: int
    script: Tuple[str, int]
    at: int
    set: bool
    value: Optional[int]


class Site(NamedTuple):
    """One reward: a call of script 74's routine, or (DIRECT) a script's own award."""
    script: Tuple[str, int]  # ("GPL ", 5)
    at: int
    xp: Optional[int]  # the amount set last before it; None when that isn't a plain number
    amounts: Tuple[int, ...]  # every plain amount set within NEAR commands before it (an if and its else)
    party: bool  # each party member (else one person)
    near: List[Use]  # the flags set within NEAR commands of it
    before: List[Use]  # the script's flags set or tested before it
    numbers: List[Tuple[int, int, int]]  # global numbers set to a plain number within NEAR commands: (number, value, at)
    direct: bool = False


def _flag_uses(script: Tuple[str, int], ops) -> List[Use]:
    """Every flag SCRIPT sets or tests, in the script's order."""
    out: List[Use] = []

    def values(x, at):
        if isinstance(x, gpl.Op):
            look(x)
        elif isinstance(x, tuple) and len(x) == 3 and x[0] == "var" and x[1] == FLAG_READ:
            out.append(Use(x[2], script, at, False, None))
        elif isinstance(x, (list, tuple)):
            for y in x:
                values(y, at)
        elif isinstance(x, dict):
            for y in x.values():
                values(y, at)

    def look(op):
        if op.code == SET and op.args[1][0] == "var" and op.args[1][1] == FLAG_SET:
            values(op.args[0], op.at)
            out.append(Use(op.args[1][2], script, op.at, True, op.args[0][1] if op.args[0][0] == "n" else None))
        else:
            values(op.args, op.at)

    for op in ops:
        look(op)
    return out


class Flags:
    """The game's scripts' use of the flags: `uses[flag]` every place it is set or tested."""

    def __init__(self, scripts: Dict[Tuple[str, int], bytes], field_types: bytes):
        self.ops = {key: gpl.decode(data, field_types) for key, data in sorted(scripts.items())}
        self.uses: Dict[int, List[Use]] = {}
        self.by_script: Dict[Tuple[str, int], List[Use]] = {}
        for key, ops in self.ops.items():
            for use in _flag_uses(key, ops):
                self.uses.setdefault(use.flag, []).append(use)
                self.by_script.setdefault(key, []).append(use)

    def set_in(self, flag: int, on: bool = True) -> List[Use]:
        """Where FLAG is set (ON: to something other than a plain 0)."""
        return [u for u in self.uses.get(flag, []) if u.set and (not on or u.value != 0)]

    def cleared_in(self, flag: int) -> List[Use]:
        return [u for u in self.uses.get(flag, []) if u.set and u.value == 0]

    def tested_in(self, flag: int) -> List[Use]:
        return [u for u in self.uses.get(flag, []) if not u.set]

    def scratch(self) -> List[int]:
        """The regions' scratch flags (cleared by script 74 as a region is entered)."""
        return sorted({u.flag for u in self.by_script.get(("GPL ", XP_SCRIPT), [])
                       if u.set and SCRATCH_AT[0] <= u.at <= SCRATCH_AT[1]})

    def number_sets(self, number: int) -> List[Tuple[Tuple[str, int], int, Optional[int]]]:
        """Where global number NUMBER is set: (script, at, the plain number it is set to or None)."""
        out = []
        for key, ops in self.ops.items():
            for op in gpl.walk(ops):
                if op.code == SET and op.args[1] == ("var", NUMBER_SET, number):
                    out.append((key, op.at, op.args[0][1] if op.args[0][0] == "n" else None))
        return out

    def _site(self, key, ops, i: int, xp, amounts, party: bool, direct: bool) -> Site:
        uses = self.by_script.get(key, [])
        low, high = ops[max(0, i - NEAR)].at, ops[min(len(ops) - 1, i + NEAR)].at
        near = [u for u in uses if u.set and low <= u.at <= high]
        before = [u for u in uses if u.at < ops[i].at]
        numbers = [(op.args[1][2], op.args[0][1], op.at) for op in ops[max(0, i - NEAR):i + NEAR + 1]
                   if op.code == SET and op.args[1][:2] == ("var", NUMBER_SET) and op.args[0][0] == "n"
                   and op.args[1][2] != XP_NUMBER]
        return Site(key, ops[i].at, xp, amounts, party, near, before, numbers, direct)

    def sites(self) -> List[Site]:
        """Every call of script 74's reward routines, in the scripts' order."""
        out: List[Site] = []
        amount = ("var", NUMBER_SET, XP_NUMBER)
        for key, ops in self.ops.items():
            for i, op in enumerate(ops):
                if op.code != CALL or op.args[1] != ("n", XP_SCRIPT) or op.args[0] not in (("n", XP_PARTY), ("n", XP_ONE)):
                    continue
                sets = [o.args[0] for o in ops[max(0, i - NEAR):i] if o.code == SET and o.args[1] == amount]
                if not sets:  # (set further back: the last one before the call)
                    sets = [o.args[0] for o in ops[:i] if o.code == SET and o.args[1] == amount][-1:]
                xp = sets[-1][1] if sets and sets[-1][0] == "n" else None
                out.append(self._site(key, ops, i, xp, tuple(a[1] for a in sets if a[0] == "n"),
                                      op.args[0] == ("n", XP_PARTY), False))
        return out

    def direct_sites(self) -> List[Site]:
        """Every award a script gives by itself (command 21h), script 74's own aside."""
        out: List[Site] = []
        for key, ops in self.ops.items():
            if key == ("GPL ", XP_SCRIPT):
                continue
            for i, op in enumerate(ops):
                if op.code == GIVE_XP:
                    xp = op.args[1][1] if op.args[1][0] == "n" else None
                    out.append(self._site(key, ops, i, xp, () if xp is None else (xp,),
                                          op.args[0] == ("n", PARTY), True))
        return out

    def text_near(self, script: Tuple[str, int], at: int, reach: int = TEXT_NEAR) -> List[Tuple[int, str]]:
        """The script's text within REACH bytes of AT: (offset, text)."""
        return [(op.at, s) for op in self.ops[script] if abs(op.at - at) <= reach for s in gpl.strings(op.args)]


def load(path: str) -> Flags:
    with open(path, "rb") as f:
        return Flags(*gpl.load_scripts(f.read()))


def _name(script: Tuple[str, int]) -> str:
    return f"{script[0].strip()} {script[1]}"


def _others(flags: Flags, flag: int, home: Tuple[str, int]) -> str:
    sets = sorted({_name(u.script) for u in flags.set_in(flag) if u.script != home})
    clears = sorted({_name(u.script) for u in flags.cleared_in(flag)})
    tests = sorted({_name(u.script) for u in flags.tested_in(flag) if u.script != home})
    parts = [f"set in {', '.join(sets)}" if sets else "", f"cleared in {', '.join(clears)}" if clears else "",
             f"tested in {', '.join(tests)}" if tests else ""]
    return "; ".join(p for p in parts if p) or "this script only"


def draft(flags: Flags, only: Optional[int] = None) -> str:
    out: List[str] = []
    sites, direct = flags.sites(), flags.direct_sites()
    total = sum(s.xp or 0 for s in sites)
    out.append(f"{len(sites)} reward calls in {len({s.script for s in sites})} scripts, {total} XP in all; "
               f"{len(direct)} awards given by the scripts themselves")
    out.append(f"the regions' scratch flags (no use to the table): {flags.scratch()}")
    for site in sites + direct:
        if only is not None and site.script[1] != only:
            continue
        out.append("")
        amount = " or ".join(str(a) for a in site.amounts) if len(site.amounts) > 1 else str(site.xp)
        out.append(f"=== {_name(site.script)} at {site.at}: {amount} XP, "
                   f"{'each party member' if site.party else 'one person'}"
                   f"{' (the script itself gives it)' if site.direct else ''}")
        for use in site.near:
            out.append(f"  beside it: flag {use.flag} = {use.value} at {use.at} ({_others(flags, use.flag, site.script)})")
        if not site.near:
            out.append("  beside it: no flag set")
        for number, value, at in site.numbers:
            out.append(f"  beside it: number {number} = {value} at {at}")
        seen = set()
        for use in site.before:
            if (use.flag, use.set) in seen:
                continue
            seen.add((use.flag, use.set))
            what = f"set to {use.value}" if use.set else "tested"
            out.append(f"  before it: flag {use.flag} {what} at {use.at} ({_others(flags, use.flag, site.script)})")
        for at, text in flags.text_near(site.script, site.at):
            out.append(f"  {'>' if at > site.at else '<'} {at}: {text}")
    return "\n".join(out) + "\n"


def flag_report(flags: Flags, flag: int, reach: int = 250) -> str:
    out = [f"flag {flag}:"]
    for use in flags.uses.get(flag, []):
        out.append(f"  {_name(use.script)} at {use.at}: {'set to ' + str(use.value) if use.set else 'tested'}")
        out += [f"      {at}: {text}" for at, text in flags.text_near(use.script, use.at, reach)]
    return "\n".join(out) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m dsloader.questdraft", description=__doc__.split("\n\n")[0])
    parser.add_argument("gpldata", help="the game's GPLDATA.GFF")
    parser.add_argument("-o", "--out", help="write the draft here (outside the repository: it holds the game's text)")
    parser.add_argument("--flag", type=int, action="append", help="every use of this flag instead")
    parser.add_argument("--script", type=int, help="the rewards of this script only")
    args = parser.parse_args(argv)
    flags = load(args.gpldata)
    text = "".join(flag_report(flags, n) for n in args.flag) if args.flag else draft(flags, args.script)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
