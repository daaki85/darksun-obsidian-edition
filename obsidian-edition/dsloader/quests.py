"""The game's quests, for the Journal tab: which are open and which are finished in the game
being played.

The game keeps no quest log. Its scripts keep a story's progress in global flags (a bit each at
the far pointer DS:1352h, SAVE chunk 29) and global numbers (words at DS:1356h, SAVE chunk 30),
and reward a deed through script 74's routines ("... receives N experience points!") or with an
award of their own. QUESTS is a table of those deeds, made by reading the scripts around each
reward (questdraft.py drafts it; DEVELOPMENT-SCREENS.md's The Journal tab tells how) and written
in the project's own words: nothing here is the game's text.

A quest is FINISHED when one of its `done` conditions holds, or when its `reward` (the area, the
amount and whose it was) is among the journal's own reward entries; OPEN when it isn't finished
and one of its `given` conditions holds; otherwise it isn't known to the player and isn't listed.
A quest with no `given` is seen only once finished. `told` is shown while it is open and says
only what the party was told when it was given; `ended` is shown once finished.

Each quest says how sure its conditions are:
  HIGH    its done flag (or number) is set within questdraft.NEAR commands of a reward in the
          script named, and no script clears it;
  MEDIUM  its done condition was read by hand to lie on the reward's way but further off, or it
          is finished by its reward's message alone (no flag kept: the area, amount and receiver
          are one no other reward of the game shares).
tests/test_quests.py holds the table to that with the game's GPLDATA.GFF (DSUN_GPLDATA).
"""

import json
import os
import re
import struct
from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple

from . import game

HIGH, MEDIUM = "high", "medium"
OPEN, FINISHED = "open", "finished"
FLAG_BYTES = (game.FLAG_COUNT + 7) // 8  # (SAVE chunk 29: 101 bytes)
NUMBER_COUNT = 200  # (SAVE chunk 30: 400 bytes)
SAVE_FLAGS, SAVE_NUMBERS = ("SAVE", 29), ("SAVE", 30)

Cond = Tuple  # ("flag", n) or ("number", n, at least)


def F(n: int) -> Cond:
    """Flag N is set."""
    return ("flag", n)


def N(n: int, least: int) -> Cond:
    """Global number N is LEAST or more."""
    return ("number", n, least)


class Reward(NamedTuple):
    """A reward message of script 74's routines, as the journal keeps it."""
    regions: Tuple[int, ...]  # where it is given (the journal entry's region)
    xp: int
    party: bool  # "Each party member receives ..." (else one person by name)


class Quest(NamedTuple):
    key: str
    name: str
    area: str
    ended: str  # shown once finished
    told: str = ""  # shown while open: what the party was told
    given: Tuple[Cond, ...] = ()  # any of them: the quest is known
    done: Tuple[Cond, ...] = ()  # any of them: it is finished
    steps: Tuple[Cond, ...] = ()  # an open quest's progress: how many of these hold
    reward: Optional[Reward] = None  # finished too when the journal holds this reward
    confidence: str = HIGH
    sites: Tuple[Tuple[int, int], ...] = ()  # the rewards it was read from: (GPL script, offset)
    ours: bool = False  # the Loader's own content (its flags: DEVELOPMENT.md's The Loader's game flags)


ARENA, PENS, SEWERS = "The arena", "The slave pens", "The sewers of Draj"
WAGONS, TEMPLE, NOTAKU, TEAQUETZL = "The wagon train", "The buried temple", "Notaku the trader", "Teaquetzl"
SPRINGS, CASTLE, DARKHOLD = "The hot springs", "Tara's castle", "Darkhold"

QUESTS: Tuple[Quest, ...] = (
    # ---- the arena and the slave pens (regions 42 and 41) ----
    Quest("bound-prisoner", "Water for the bound prisoner", ARENA,
          "The prisoner tied up in the arena was given water.",
          done=(F(26),), sites=((5, 408), (5, 649))),
    Quest("arena-ring", "The dead prisoner's ring", ARENA,
          "A ring was found on the body of the arena's prisoner.",
          done=(F(783),), ours=True),
    Quest("gilal", "Gilal's pain", PENS,
          "Dinos laid his hands on Gilal and the pain left her.",
          "Gilal is seized by a searing pain in her head whenever she tries to remember.",
          given=(F(527),), done=(F(528),), sites=((139, 331),)),
    Quest("pens-door-east", "A secret door in the pens (east)", PENS,
          "A hidden button opened a secret door in the east of the pens.",
          done=(F(517),), sites=((137, 6704),)),
    Quest("pens-door-west", "A secret door in the pens (west)", PENS,
          "A hidden button opened a secret door in the west of the pens.",
          done=(F(518),), sites=((137, 7051),)),
    Quest("water-pot", "Water to carry", PENS,
          "The party's water pot was filled.",
          done=(F(522),), sites=((137, 7885), (137, 8229))),
    Quest("shipment", "The guards' crate", PENS,
          "A party member carries the weapon that came in the guards' crate.",
          "Semyon saw the guards fuss over a crate; the weapon from it went to a rack in the pens.",
          given=(F(756),), done=(F(758),), ours=True),
    Quest("proper-meal", "A proper meal", PENS,
          "Dinos cooked the arena's vulture as it should be cooked and shared it with the party.",
          done=(F(781),), ours=True),
    Quest("champions", "King of the pens", ARENA,
          "The champions sent to test the new king of the pens were fought.",
          "A party member killed Scar and is king of the pens. The arena will not let that rest.",
          given=(F(759),), done=(F(807),), ours=True),
    # (503 is set 18 commands after the reward, in the same "into the sewers" branch)
    Quest("escape", "Out of the slave pens", PENS,
          "The party escaped from the slave pens of Draj.",
          done=(F(503),), confidence=MEDIUM, sites=((137, 1021), (137, 1034))),
    # ---- the sewers (region 40) ----
    # (449: she is untied, script 117; 464: her father's thanks, script 125's own award)
    Quest("chiefs-daughter", "The chief's daughter", SEWERS,
          "The chief of the Tari has his daughter back.",
          "The Tari chief's daughter is free of her bonds. Her father will want to hear of it.",
          given=(F(449),), done=(F(464),), sites=((117, 289), (125, 2796))),
    Quest("parted-water", "The staff and the water", SEWERS,
          "A staff parted the water and opened a way down.",
          done=(F(466),), sites=((124, 289),)),
    Quest("drain-lever", "A lever in a drain", SEWERS,
          "A lever hidden in a sewer drain was found and pulled.",
          reward=Reward((40,), 500, False), confidence=MEDIUM, sites=((124, 2202),)),
    # ---- the wagon train (region 8) ----
    Quest("rope", "A rope from a plant", WAGONS,
          "A rope-like plant gave the party a length of rope.",
          done=(F(724),), sites=((210, 54),)),
    Quest("captives", "The caravan's captives", WAGONS,
          "The captives were brought back to their wagons.",
          reward=Reward((8,), 3000, True), confidence=MEDIUM, sites=((210, 915),)),
    # (268 is set when he agrees and cleared by the last battle's script 62: the reward is kept too)
    Quest("kalinin", "Kalinin's warriors", WAGONS,
          "Kalinin agreed to stand with the alliance.",
          done=(F(268),), reward=Reward((8,), 1000, True), confidence=MEDIUM, sites=((208, 3066),)),
    # ---- the buried temple (region 45) ----
    # (616, 595, 596: each crystal's part done; 597: both set in the altar, 16 commands before the reward)
    Quest("temple", "The shades of the temple", TEMPLE,
          "Tynan and Tristram were freed and their temple made whole.",
          "The shades of Tynan and Tristram are bound to crystal hearts. Their temple may hold the way to free them.",
          given=(F(616), F(595), F(596)), done=(F(597),), steps=(F(616), F(595), F(596)),
          reward=Reward((45,), 6000, True), confidence=MEDIUM,
          sites=((170, 219), (163, 1943), (163, 2274), (163, 2383), (163, 2879))),
    # ---- Notaku's errands (region 7; number 96 is how far they have come) ----
    Quest("notaku-delivery", "A delivery for Notaku", NOTAKU,
          "The bag of pith reached Father Garyn and Notaku paid for the errand.",
          "Notaku asked the party to carry a bag of ranike tree pith to Father Garyn in Teaquetzl, and to come back for payment.",
          given=(F(581),), done=(N(96, 2),), sites=((156, 278),)),
    # (4 is set when the next errand is given, in the talk the reward opens)
    Quest("notaku-bloom", "Notaku's second errand", NOTAKU,
          "A terror bloom was found and brought to Notaku.",
          "Notaku has a second, more dangerous errand for the party.",
          given=(N(96, 2),), done=(N(96, 4),), confidence=MEDIUM, sites=((156, 636),)),
    # (5 or 6 is set at the end of the talk the reward opens)
    Quest("notaku-stinger", "Notaku's urgent errand", NOTAKU,
          "A mastyrial's stinger was brought to Notaku.",
          "Notaku urgently needs a rare spell component for a client of his.",
          given=(N(96, 4),), done=(N(96, 5),), confidence=MEDIUM, sites=((156, 1613),)),
    # ---- the sand oasis (region 18) ----
    Quest("oasis-seed", "A seed for the oasis", "The sand oasis",
          "A seed was planted where it can grow, to the joy of the oasis's keeper.",
          done=(F(413),), sites=((109, 2605), (109, 3144))),
    # ---- the elven caravan and the messenger route (regions 26 and 9) ----
    Quest("hesutu", "A purpose for Hesutu", "The elven caravan",
          "Hesutu found a purpose again and thanked the party for it.",
          reward=Reward((26,), 1000, True), confidence=MEDIUM, sites=((35, 77),)),
    Quest("dispatch", "A templar's dispatch", "The messenger route",
          "A dispatch meant for Draj's templars was read.",
          done=(F(247),), sites=((58, 2390),)),
    Quest("freed-slave", "The drugged slave", "The messenger route",
          "A noble-born slave bound for Draj was set free and left for home.",
          reward=Reward((9,), 3000, True), confidence=MEDIUM, sites=((134, 1651),)),
    # ---- the hot springs (region 35) ----
    Quest("hot-springs", "The hot springs", SPRINGS,
          "The templar's men no longer hold the hot springs.",
          done=(F(485),), sites=((148, 2264), (153, 2395))),
    Quest("freed-workers", "The freed workers", SPRINGS,
          "The workers freed at the hot springs left to join the alliance.",
          done=(F(484),), sites=((128, 2740),)),
    # ---- Gedron and Cedrilte (regions 3 and 31) ----
    Quest("safe", "The hidden safe", "Gedron",
          "A hidden safe was opened.",
          done=(F(310),), sites=((71, 6540),)),
    Quest("mountain-way", "The way into the mountain", "Cedrilte",
          "The hidden passage into the mountain was found.",
          done=(F(185),), sites=((38, 625),)),
    # (196 is set where the amount is, 47 commands before the routine is called)
    Quest("grain", "Grain for the hungry", "Cedrilte",
          "Grain was given to a village that had little to eat.",
          done=(F(196),), confidence=MEDIUM, sites=((39, 7273),)),
    # ---- the lines in the desert (region 34) and the gem fields (region 6) ----
    Quest("vision", "The ssurran's vision", "The lines in the desert",
          "A ssurran waiting for a vision told the party what he saw.",
          done=(F(753),), sites=((160, 5985),)),
    Quest("clarity", "A moment of clarity", "The lines in the desert",
          "One of the party came to a moment of enlightenment.",
          reward=Reward((34,), 500, False), confidence=MEDIUM, sites=((166, 3825),)),
    Quest("geysers", "The geysers", "The gem fields",
          "Every small geyser was stopped up, and the great one answered.",
          done=(F(605),), sites=((165, 1731),)),
    Quest("false-dome", "The false dome", "The gem fields",
          "A snare hidden among the lava domes was disarmed.",
          reward=Reward((6,), 500, False), confidence=MEDIUM, sites=((164, 1547),)),
    # ---- Tara's castle (regions 28 and 29) ----
    Quest("shimmering-wall", "The shimmering wall", CASTLE,
          "A wall that shimmered gave way to the right touch.",
          done=(F(110),), sites=((17, 347),)),
    Quest("tara", "Tara's end", CASTLE,
          "Tara was destroyed for good, to the thanks of the Druid of the Howling Wind.",
          done=(F(77),), sites=((17, 1493), (12, 428))),
    Quest("cleansing-wind", "The cleansing wind", CASTLE,
          "A wind swept the last of Tara's taint from her halls.",
          done=(F(88),), sites=((17, 1176),)),
    # ---- Teaquetzl (region 11) ----
    # (138: script 62, beside its own award after the last battle)
    Quest("alliance", "The alliance against Draj", TEAQUETZL,
          "The free villages stood together and the army of Draj was broken.",
          "Teaquetzl's council asked the party to bring the free villages together against the army of Draj.",
          given=(F(135),), done=(F(138),), sites=((183, 3233), (62, 5852))),
    Quest("chahl", "Chahl's story", TEAQUETZL,
          "Chahl was persuaded to tell of his past.",
          done=(F(645),), sites=((181, 5390),)),
    Quest("katti", "Counsel for Katti", TEAQUETZL,
          "Katti took the party's counsel about her gift to heart.",
          done=(N(37, 3),), sites=((180, 4459),)),
    Quest("leader", "Leader of Teaquetzl", TEAQUETZL,
          "The party accepted the leadership of Teaquetzl.",
          done=(F(648),), sites=((188, 5865),)),
    Quest("fine-shot", "A fine shot", TEAQUETZL,
          "A shot at the archery target won a prize.",
          reward=Reward((11,), 50, False), confidence=MEDIUM, sites=((178, 1978),)),
    # ---- Darkhold (region 30) ----
    Quest("grove", "The evil in the grove", DARKHOLD,
          "A pendant cast into the pit ended the evil in the fungus grove.",
          reward=Reward((30,), 3000, True), confidence=MEDIUM, sites=((198, 726),)),
    Quest("folk-peace", "The folk and the prince", DARKHOLD,
          "The folk of the Mindhome agreed to peace with Darkhold's prince.",
          done=(F(695),), sites=((204, 1486),)),
    # ---- awards the scripts give themselves ----
    Quest("balkazar", "Balkazar", "Balkazar's hall",
          "Balkazar was destroyed.",
          done=(F(34),), sites=((6, 3033),)),
    Quest("oasis-cleared", "The oasis cleared", "The oasis",
          "The oasis was cleared of those who held it.",
          done=(F(370),), sites=((91, 170), (92, 4358))),
)

# The rewards of script 74's routines the table leaves out, and why: (GPL script, offset).
LEFT_OUT: Dict[Tuple[int, int], str] = {
    (5, 3697): "a reward in Semyon's talk in the arena on a local the script alone keeps; no flag, and what earns it was not established",
    (8, 2494): "a find in a haystack (10 XP), one of its random finds and not a deed",
    (10, 528): "flags 64 and 65 are set beside it, but what the party did to earn it was not established",
    (33, 936): "alms to the refugees: the amount is what was given, and no flag is kept",
    (138, 1531): "a door of the pens: no flag, and the script's local decides it",
    (146, 226): "250 XP to one person in the pens, as the two secret doors give: its message can't be told from theirs, and no flag is kept",
    (152, 1550): "500 XP to each in the hot springs' region, as the freed workers give: its message can't be told from theirs, and no flag is kept",
    (202, 3217): "the reward for agreeing to the prince's plan (flag 685): the flag that ends that plan was not established, and a quest that never ends is worse than none",
}

# Where each script with a reward routine's call runs: the regions whose master script (MAS n is
# region n's) starts it, itself or through one other script. For telling rewards apart by region.
SCRIPT_REGIONS: Dict[int, Tuple[int, ...]] = {
    5: (42,), 8: (41, 45), 10: (28, 29), 12: (28,), 17: (28, 29), 33: (26,), 35: (26,), 38: (31,), 39: (31,),
    58: (9,), 71: (3,), 109: (18,), 117: (40,), 124: (40,), 128: (35,), 134: (9,), 137: (41,), 138: (41,),
    139: (41,), 146: (41,), 148: (35,), 152: (35,), 153: (35,), 156: (7,), 160: (34,), 163: (45,), 164: (6,),
    165: (6,), 166: (34,), 170: (45,), 178: (11,), 180: (11,), 181: (11,), 183: (11,), 188: (11,), 198: (30,),
    202: (30,), 204: (30,), 208: (8,), 210: (8,),
}

BY_KEY: Dict[str, Quest] = {quest.key: quest for quest in QUESTS}


class State:
    """A reading of the game's flags and numbers (from memory, or from a save)."""

    def __init__(self, flags: bytes, numbers: Optional[bytes] = None):
        self.flags = bytes(flags[:FLAG_BYTES]).ljust(FLAG_BYTES, b"\0")
        self.numbers = None if numbers is None else bytes(numbers[:NUMBER_COUNT * 2]).ljust(NUMBER_COUNT * 2, b"\0")

    def flag(self, n: int) -> bool:
        return 0 <= n < game.FLAG_COUNT and bool(self.flags[n // 8] >> (n % 8) & 1)

    def number(self, n: int) -> Optional[int]:
        if self.numbers is None or not 0 <= n < NUMBER_COUNT:
            return None
        return struct.unpack_from("<h", self.numbers, n * 2)[0]

    def holds(self, cond: Cond) -> bool:
        if cond[0] == "flag":
            return self.flag(cond[1])
        value = self.number(cond[1])
        return value is not None and value >= cond[2]

    def __eq__(self, other) -> bool:
        return isinstance(other, State) and (self.flags, self.numbers) == (other.flags, other.numbers)

    def __hash__(self) -> int:
        return hash((self.flags, self.numbers))


def read_state(gd) -> Optional[State]:
    """The flags and numbers in the game's memory now; None while the flags have no place there
    (their pointer is null at times: whoever asks keeps its last reading)."""
    flags = game.far_pointer(gd.guest, gd.ds, game.FLAGS_PTR)
    if not flags:
        return None
    numbers = game.far_pointer(gd.guest, gd.ds, game.NUMBERS_PTR)
    return State(gd.guest.read(flags, FLAG_BYTES), gd.guest.read(numbers, NUMBER_COUNT * 2) if numbers else None)


def save_state(chunks: Dict[Tuple[str, int], bytes]) -> Optional[State]:
    """The flags and numbers a saved game holds (CHUNKS: gff.read_gff of its SAVEnn.SAV)."""
    if SAVE_FLAGS not in chunks:
        return None
    return State(chunks[SAVE_FLAGS], chunks.get(SAVE_NUMBERS))


_REWARD = re.compile(r"^(.*?) receives? ([\d,]+) experience points?\b", re.I)
EACH = "each party member"


def reward_of(text: str, region: Optional[int]) -> Optional[Tuple[Optional[int], int, bool]]:
    """(region, amount, each party member?) of a reward message of script 74's routines, or None."""
    found = _REWARD.match(" ".join(text.split()))
    if not found:
        return None
    try:
        amount = int(found.group(2).replace(",", ""))
    except ValueError:
        return None
    return region, amount, found.group(1).strip().casefold() == EACH


def rewards_of(entries: Iterable) -> List[Tuple[Optional[int], int, bool]]:
    """The rewards among a journal's entries (journal.Entry: its reward kind)."""
    out = []
    for entry in entries:
        if entry.kind == "reward":
            reward = reward_of(entry.text, entry.region)
            if reward is not None:
                out.append(reward)
    return out


def _rewarded(quest: Quest, rewards: Sequence[Tuple[Optional[int], int, bool]]) -> bool:
    wanted = quest.reward
    return wanted is not None and any(region in wanted.regions and (xp, party) == (wanted.xp, wanted.party)
                                      for region, xp, party in rewards)


def status(quest: Quest, state: Optional[State], rewards: Sequence[Tuple[Optional[int], int, bool]] = ()) -> Optional[str]:
    """FINISHED, OPEN, or None for a quest the player doesn't know of. STATE None (no reading
    of the game): only what the journal's rewards say."""
    if _rewarded(quest, rewards) or (state is not None and any(state.holds(c) for c in quest.done)):
        return FINISHED
    if state is not None and any(state.holds(c) for c in quest.given):
        return OPEN
    return None


def progress(quest: Quest, state: Optional[State]) -> str:
    """An open quest's steps done, "2 of 3"; "" for a quest without steps."""
    if not quest.steps or state is None:
        return ""
    return f"{sum(state.holds(c) for c in quest.steps)} of {len(quest.steps)}"


def listing(state: Optional[State], rewards: Sequence[Tuple[Optional[int], int, bool]] = ()) -> Tuple[List[Quest], List[Quest]]:
    """(the open quests, the finished ones), each in the table's order."""
    found = [(quest, status(quest, state, rewards)) for quest in QUESTS]
    return [q for q, s in found if s == OPEN], [q for q, s in found if s == FINISHED]


def matches(quest: Quest, wanted: str, finished: bool) -> bool:
    """WANTED (any case) is in what is shown of the quest."""
    wanted = wanted.casefold()
    return any(wanted in part.casefold() for part in (quest.name, quest.area, quest.ended if finished else quest.told))


def rows(state: Optional[State], rewards: Sequence[Tuple[Optional[int], int, bool]] = (), wanted: str = "",
         note: str = "") -> Tuple[List[Tuple[str, str]], int, int]:
    """The quests as rows to show, each (what it is, its text): "note", "day" (a heading), "speaker"
    (a quest's name and area), "text" (an open quest's words), "reply" (its progress), "reward" (a
    finished one's words), "gap"; and how many are open and finished (of those holding WANTED)."""
    open_, finished = listing(state, rewards)
    open_ = [q for q in open_ if not wanted or matches(q, wanted, False)]
    finished = [q for q in finished if not wanted or matches(q, wanted, True)]
    out: List[Tuple[str, str]] = []
    if note:
        out += [("note", note), ("gap", "")]
    if open_:
        out += [("day", f"Open ({len(open_)})"), ("gap", "")]
        for quest in open_:
            out.append(("speaker", f"{quest.name} - {quest.area}"))
            out.append(("text", quest.told))
            steps = progress(quest, state)
            if steps:
                out.append(("reply", f"  Done so far: {steps}"))
            out.append(("gap", ""))
    if finished:
        out += [("day", f"Finished ({len(finished)})"), ("gap", "")]
        for quest in finished:
            out.append(("speaker", f"{quest.name} - {quest.area}"))
            out.append(("reward", quest.ended))
            out.append(("gap", ""))
    return out, len(open_), len(finished)


def count_text(open_: int, finished: int) -> str:
    return f"{open_} open, {finished} finished" if open_ or finished else "No quests yet"


# ---- the last reading, kept for when the game isn't running ----------------------------

def snapshot_path(journal_path: str) -> str:
    return os.path.join(os.path.dirname(journal_path), "quests.json")


def save_snapshot(path: str, head: int, state: State) -> bool:
    """The reading STATE, made while the journal's chain ended at entry HEAD (0: an empty
    journal), written to PATH; False if it couldn't be."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"head": head, "flags": state.flags.hex(),
                       "numbers": None if state.numbers is None else state.numbers.hex()}, f)
        return True
    except OSError:
        return False


def load_snapshot(path: str) -> Optional[Tuple[int, State]]:
    """(the head it was made at, the reading) from PATH, or None."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        head, numbers = d["head"], d.get("numbers")
        if not isinstance(head, int) or isinstance(head, bool) or head < 0:
            return None
        return head, State(bytes.fromhex(d["flags"]), None if numbers is None else bytes.fromhex(numbers))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
