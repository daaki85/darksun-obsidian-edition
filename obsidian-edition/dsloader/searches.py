"""Searching junk piles, haystacks and wardrobes: the dice log's lines for the rolls.

All three are routines of the game's script 8. Each rolls the scripts' random command (0 to N,
each as likely) and finds nothing on a low roll; junk and hay find nothing either once the
party has found 6 things in them (the scripts' variables 135,21 and 135,22, counting finds
only), and wardrobes are empty after 6 searches (135,23, counting every search, before the
roll). Some outcomes roll damage the same way (a rat's bite 0-4, a falling pot 0-5).

DSCLOG's PROBE_SCRIPT_RAND records each random command: the result, N, the script's position
(past the command: what tells the searches apart) and the three counts at the time.
"""

from typing import Dict, List, NamedTuple, Optional, Tuple

COUNTS_AT = (2, 4, 6)  # the entry's frame: junk and hay finds, wardrobe searches
FINDS_MOST = 6


class Search(NamedTuple):
    name: str  # as the line starts
    most: int  # N: the roll is 0 to N
    nothing_below: int  # a roll under it finds nothing
    count: int  # which of COUNTS_AT
    counts_finds: bool  # junk and hay count finds (the roll's own not yet); wardrobes searches
    outcomes: Dict[int, str]


JUNK = Search("Junk pile searched", 14, 2, 0, True, {
    0: "a scorpion bite (0-4 damage)", 1: "a small rodent, narrowly escaped",
    2: "a scorpion bite, dodged", 3: "a scrap of paper: 'Watch out for the...'", 4: "a dead rat",
    5: "a piece of stale, moldy bread", 6: "a piece of a broken grainpot (left on the ground)",
    7: "a rat, which bites the searcher's hand (0-4 damage)",
    8: "a piece of magic fruit (left on the ground)",
    9: "a piece of wood that will do as a club (left on the ground)",
    10: "a drawing of a four-armed statue crushing adventurers",
    11: "a box of worthless trinkets with a gem at the bottom", 12: "a pile of dung",
    13: "some arrows", 14: "a piece of magic fruit"})
HAY = Search("Haystack searched", 10, 3, 1, True, {
    0: "a pile of dung", 1: "a human skull", 2: "a mummified rat", 3: "a crudely made bone needle",
    4: "a piece of a pot (left on the ground)", 5: "a rat, which bites the searcher (0-4 damage)",
    6: "an old table leg that will do as a club (left on the ground)", 7: "an old, soiled loincloth",
    8: "a handful of ceramic coins (+15)", 9: "a small bug, which crawls away", 10: "a small gem"})
WARDROBE = Search("Wardrobe searched", 10, 3, 2, False, {
    0: "a butterfly, which flies off", 1: "a little spider", 2: "a handful of ceramic coins (+15)",
    3: "a rat, which bites the searcher (0-4 damage)", 4: "a piece of a pot (left on the ground)",
    5: "a message carved in the wood: 'Gareth the scribe was here.'",
    6: "a piece of magic fruit (left on the ground)",
    7: "a pot leaning on the door, which falls on the searcher's head (0-5 damage)",
    8: "a small gem", 9: "a pot leaning on the door, which falls and misses",
    10: "a message carved in the wood: 'Don't trust Pehtucl.'"})

# Script 8's random commands, by the position past them: the searches, and their damage rolls
SEARCHES: Dict[int, Search] = {544: JUNK, 2116: HAY, 2946: WARDROBE}
DAMAGE: Dict[int, Tuple[str, int]] = {
    1098: ("The rat's bite", 4), 1575: ("The scorpion's bite", 4), 2452: ("The rat's bite", 4),
    3332: ("The rat's bite", 4), 3562: ("The pot", 5)}


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def describe(result: int, most: int, position: int, counts: Tuple[Optional[int], ...]) -> List[str]:
    """The dice log's lines for one random command (none if it isn't a search's)."""
    search = SEARCHES.get(position)
    if search is not None and most == search.most:
        roll = f"0-{most} = {result}"
        count = counts[search.count] if search.count < len(counts) else None
        if search.counts_finds and count is not None and count >= FINDS_MOST:
            kind = "junk" if search is JUNK else "hay"
            return [f"{search.name}: {roll}, nothing: the party has already found {FINDS_MOST} "
                    f"things in {kind} (after that, every search finds nothing)"]
        if result < search.nothing_below:
            return [f"{search.name}: {roll}, nothing (0-{search.nothing_below - 1} finds nothing)"]
        found = search.outcomes.get(result, "something")
        if count is None:
            note = ""
        elif search.counts_finds:
            note = f" (the party's {_ordinal(count + 1)} find of {FINDS_MOST} in {'junk' if search is JUNK else 'hay'})"
        else:
            note = f" (the {_ordinal(count)} wardrobe search of {FINDS_MOST}; after that they are empty)"
        return [f"{search.name}: {roll}, {found}{note}"]
    damage = DAMAGE.get(position)
    if damage is not None and most == damage[1]:
        return [f"  {damage[0]}: 0-{most} = {result} damage"]
    return []
