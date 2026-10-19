"""Kalzith, a defiler in the slave pens who sells spell scrolls to a party that treats him well.

He is a slave the templars put in the arena now and then (the crowd loves to watch a defiler burn),
kept in a pen of his own the rest of the time; he has the look of the arena's Defiler, but the
party has never fought him. He secretly scribes spells on scraps of hide, to buy a guard's blind eye; a preserver can learn from them (the game's own scrolls: right-click one, click
its spell). Insult him or threaten to report him and he won't trade until the party makes amends:
50 ceramic pieces, or a Charisma check. Killed, he leaves one of his scrolls at random, a Cloak and
a Quarterstaff and his Ashen Robe (loot).

He is the game's own kind of person, added to the Loader's copies of three of its files (the game
folder is never changed; DSCLOG has the game open the copies):

  * SEGOBJEX.GFF: object OBJECT, his OJFF (a person's, with the arena Defiler's picture) and
    RDFF (a slave's record, Dinos's, with his name and a defiler's class);
  * RGN29.GFF, the slave pens: an entry in its entity table (ETAB) setting him in his pen (PEN);
  * GPLDATA.GFF: his conversation, script SCRIPT, and in the pens' master script (MAS 41) the
    command that runs it when the party talks to him (6Eh, as for Dinos and the rest), with its
    entry in the game's table of entry points (GPLI, which saves go by); and his
    portrait, PORTRAIT: the game's PORTRAIT_FROM with an X branded on the brow, so that no one
    else's face is his (the Loader's dialogue tab shows it too).

The game reads the pens' people from RGN29 only the first time the party goes there (a save keeps
them as they were), so he is in new games: those started after the Loader has these copies.
His stock, the six scrolls in SCROLLS, the Loader puts among his things once a game (stock), as it
does the slave-pen items (npcitems); the game's shop screen (24h) sells what he carries.
"""

import struct
from typing import Callable, Dict, List, Optional, Tuple

from . import game, gpl
from .gff import read_gff

OBJECT = 1000  # (no object of the game's has it. Past the game's object table, 520 long: the
# shop command takes a number below that as an object there, so 297 opened someone's item list)
SCRIPTS_FILE, REGION_FILE = "GPLDATA.GFF", "RGN29.GFF"  # (DSCLOG opens the copies for the game's)
NAME = "Kalzith"
DINOS, DEFILER = 183, 296  # whose records his are made from
REGION, ETAB_ID, MASTER = 0x29, 41, 41  # the slave pens, its entity table and master script
SCRIPT = 218  # his conversation (the game's run to 217)
BEGIN, START = 0x19, 1  # the byte every game script opens with, and where talking starts: after it
                         # (the game takes a talk command for offset 0 as none: clicking did nothing)
PORTRAIT = 101  # his own: the game's portrait 61 with a slave's brand (101 is free in the game's)
PORTRAIT_FROM = 61  # a gaunt, bald man (shown also for another of the game's people)
PEN = (1580, 880)  # by the straw in a free pen of the middle column (its door on the left)
ENTITY_FLAGS = 14  # as the pens' other people have
OJFF_PICTURE = 0x0C  # an object's picture
RDFF_SELF, RDFF_NAME, RDFF_NAME_SIZE = 0x10, 0x32, 8  # the record's own object number; its name
RDFF_CLASS, RDFF_LEVEL = 0x6F, 0x72  # (as the arena Defiler's: a defiler, of level 9)
DEFILER_CLASS, LEVEL = 18, 5

# his state, in four of the game's global flags (bits; it uses 1-755, a save keeps 808): met
# him, friendly, cold; his scrolls given
MET, FRIENDLY, COLD = 760, 761, 762
STOCKED = 763  # (set by the Loader: his scrolls and gear given)
DIED = 772  # (set by the Loader: seen dead; Dinos and the Trustee speak of him so, pensasks.py)

# The scrolls: (spell, its name, price in ceramic pieces). Cat's Grace is one of the new spells
# (game.NEW_SPELLS; once the game's Flaming Sphere, 14, under the rule), sold only while their rule
# is on; mend() makes an earlier build's scroll of it teach the new spell. The prices are the
# game's price for the spell's level (3000 a level, as most of its 19 scrolls, objects 1400-1418).
# None is a spell the game has a scroll of. Shield and Burning Hands took the places of Magic
# Missile and Color Spray (the game has a Color Spray scroll); mend() turns those into them
SCROLLS = ((9, "Shield", 3000), (1, "Burning Hands", 3000), (12, "Blur", 6000),
           (game.GRACE_SPELL, "Cat's Grace", 6000), (32, "Lightning Bolt", 9000), (29, "Haste", 9000))
SCROLL_TYPE = 0x60  # the game's spell scrolls (its objects 1400-1418)
SCROLL_TEMPLATE = "88fa01000f2700000f2760000000000105ff7f0000"  # its scroll of spell 1 (object 1400)
SCROLL_FROM = 1400  # the game's first scroll object, which his scrolls' objects copy
# His k-th scroll is object SCROLL_OBJECT + k: one each (the shop shows items of one object as one:
# six of 1400 showed as a single scroll), and among the numbers the game takes for scrolls: right-
# clicked, it teaches its spell only for an object from 1400 to 1499 (DSUN.EXE 8B6A3h), and
# casts it otherwise. The game's objects stop at 1432; from 1433 the numbers are pictures only,
# most of them other objects' icons: those of 1440-1445 move to pictures of their own
# (MOVED_ICONS: no chunk of the game's has those numbers, nor the Loader's other pictures), and
# the scrolls take theirs. Earlier builds' scrolls (OLD_SCROLL_OBJECT + k) are renumbered (mend).
SCROLL_OBJECT = 1440
SCROLL_LEARNED = range(1400, 1500)
OLD_SCROLL_OBJECT = OBJECT + 1
MOVED_ICONS = 2440
ITEM_OBJECT, ITEM_SPELL, ITEM_SPELL_AGAIN, ITEM_VALUE, ITEM_LINK = 0x00, 0x02, 0x0F, 0x06, 0x08


SCROLL_SPELL_FROM = 1  # a scroll names its spell one past the game's number for it (as the
# rest of the Loader numbers spells: 1 Burning Hands): one of 29, Haste's, taught Flame Arrow


def scroll(spell: int, price: int, k: int = 0) -> bytes:
    """A spell scroll item (the game's own kind) teaching SPELL, priced PRICE: his K-th."""
    rec = bytearray.fromhex(SCROLL_TEMPLATE)
    struct.pack_into("<h", rec, ITEM_OBJECT, -(SCROLL_OBJECT + k))
    struct.pack_into("<H", rec, ITEM_LINK, game.NO_ITEM)  # (as the game's items; 0 linked item 0 in)
    struct.pack_into("<H", rec, ITEM_SPELL, spell + SCROLL_SPELL_FROM)
    rec[ITEM_SPELL_AGAIN] = spell + SCROLL_SPELL_FROM
    struct.pack_into("<H", rec, ITEM_VALUE, price)
    struct.pack_into("<H", rec, game.ITEM_NEXT, game.NO_ITEM)
    rec[game.ITEM_SLOT] = 0xFF
    return bytes(rec)


# ---------------------------------------------------------------------------------------------
# The objects file: his OJFF, RDFF and picture

def object_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: Kalzith's object (the arena Defiler's look) and record
    (a peaceful slave's, Dinos's, named and classed as a defiler)."""
    if any(k not in chunks for k in (("RDFF", DINOS), ("OJFF", DINOS), ("OJFF", DEFILER))):
        return {}
    rec = bytearray(chunks[("RDFF", DINOS)])
    struct.pack_into("<h", rec, RDFF_SELF, -OBJECT)
    rec[RDFF_NAME:RDFF_NAME + RDFF_NAME_SIZE] = NAME.encode("ascii").ljust(RDFF_NAME_SIZE, b"\0")
    rec[RDFF_CLASS], rec[RDFF_LEVEL] = DEFILER_CLASS, LEVEL
    obj = bytearray(chunks[("OJFF", DINOS)])  # a person's object (not a fighter's), with his picture
    obj[OJFF_PICTURE:OJFF_PICTURE + 2] = chunks[("OJFF", DEFILER)][OJFF_PICTURE:OJFF_PICTURE + 2]
    out = {("OJFF", OBJECT): bytes(obj), ("RDFF", OBJECT): bytes(rec)}
    if ("OJFF", SCROLL_FROM) in chunks and ("BMP ", SCROLL_FROM) in chunks:
        owners: Dict[int, List[int]] = {}
        for (kind, number), data in chunks.items():
            if kind == "OJFF" and len(data) >= OJFF_PICTURE + 2:
                owners.setdefault(struct.unpack_from("<H", data, OJFF_PICTURE)[0], []).append(number)
        for k in range(len(SCROLLS)):
            number, moved = SCROLL_OBJECT + k, MOVED_ICONS + k
            if ("OJFF", number) in chunks or any(key[1] == moved for key in chunks):
                raise KeyError(f"object {number} or picture {moved} taken")  # (then none of his)
            if ("BMP ", number) in chunks:
                out[("BMP ", moved)] = chunks[("BMP ", number)]
                for owner in owners.get(number, ()):
                    rec_ = bytearray(out.get(("OJFF", owner), chunks[("OJFF", owner)]))
                    struct.pack_into("<H", rec_, OJFF_PICTURE, moved)
                    out[("OJFF", owner)] = bytes(rec_)
            out[("OJFF", number)] = chunks[("OJFF", SCROLL_FROM)]
            out[("BMP ", number)] = chunks[("BMP ", SCROLL_FROM)]  # (its picture on the map: a scroll's)
            out[("OJFF", OLD_SCROLL_OBJECT + k)] = chunks[("OJFF", SCROLL_FROM)]  # (until mended)
    return out


# ---------------------------------------------------------------------------------------------
# His portrait

BRAND = (  # an X burned into the brow: "#" the groove, "o" its raised rim (lit from the upper right)
    "#...#",
    "o#.#o",
    ".o#o.",
    ".#o#.",
    "#o.o#",
)
BRAND_AT = (12, 3)  # its top left, on the left of the brow's highlight
BRAND_GROOVE, BRAND_RIM = 133, 152  # (portrait palette: a dark red-brown, a pale skin highlight)


def portrait(rows):
    """Portrait PORTRAIT_FROM's pixels (rows of palette indexes) with the brand."""
    out = [list(r) for r in rows]
    x0, y0 = BRAND_AT
    for dy, line in enumerate(BRAND):
        for dx, c in enumerate(line):
            if c != ".":
                out[y0 + dy][x0 + dx] = BRAND_GROOVE if c == "#" else BRAND_RIM
    return out


def portrait_chunk(chunks) -> Optional[bytes]:
    """His portrait as a PORT chunk, from the game's own (None without it)."""
    from . import icons
    source = chunks.get(("PORT", PORTRAIT_FROM))
    return icons.encode(portrait(icons.decode(source))) if source else None


# ---------------------------------------------------------------------------------------------
# The slave pens: his place

ENTITY = struct.Struct("<HHBBh")  # x, y, height, flags, object (negative: one of SEGOBJEX's)


def with_entity(etab: bytes) -> bytes:
    """The pens' entity table with Kalzith in his pen (once), at its end: the game's scripts name
    the pens' people by their place in it, so every entry of the game's keeps its own (an entry
    put in among them moved everyone after it: Kurzak vanished, others went missing)."""
    entries = [ENTITY.unpack_from(etab, i) for i in range(0, len(etab) - ENTITY.size + 1, ENTITY.size)]
    if any(e[4] == -OBJECT for e in entries):
        return etab
    return etab[:len(entries) * ENTITY.size] + ENTITY.pack(PEN[0], PEN[1], 0, ENTITY_FLAGS, -OBJECT)


# ---------------------------------------------------------------------------------------------
# His conversation

SPEAKS = 115  # the dialogue window's lines: his words (no narration: the game's talks have little)
LINE = 60  # the game's lines are no longer than this
REPLY = 40  # nor its replies (the reply window cuts a longer one off)
TITLE = ("var", 0x86, 1)  # a reply menu's title, as the game's own (the speaker)
MORE, CLEAR = ("var", 0x86, 2), ("var", 0x86, 3)  # wait for a click, then clear the window
MONEY = ("var", 0x89, 42)  # the party's ceramic pieces
ACTOR = ("var", 0x89, 37)
SPEAKER = ("var", 0x89, 39)  # the person being talked to (as the game's scripts name him)  # the character talking (who rolls an ability check)
CHA = 5


def _lines(text: str, width: int = LINE) -> List[str]:
    """TEXT in the game's line lengths (each ending in a space, as the game's own)."""
    out, line = [], ""
    for word in text.split():
        if line and len(line) + len(word) + 1 > width:
            out.append(line + " ")
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        out.append(line + " ")
    return out


class _Script:
    """A script built the way the game's are: structured, with no jump of its own.

    18h tests, 3Eh goes on to the "else" (3Fh) or the end (67h) when the test fails, 3Fh at the
    end of the "then" part skips the "else" part, 67h ends the "if" (once on each way through:
    one too many or too few ends the script with "BAD GPL EXIT"); a 3Fh anywhere else does
    nothing. Shared parts are subroutines: 13h calls one, 15h returns.

    Menus are the game's: a loop showing the menu until a local flag (DONE) is set, each reply
    a subroutine returning to it, doing its own part (calling what comes next) and setting DONE
    to end the talk. (Branching after the menu on a "which way" local went wrong in the game.)
    A reply that stays in the menu is shown once a talk, as the game's: it sets a local of its
    own, cleared as the menu starts, and is shown only while that is 0 (but a body marked
    AGAIN, such as a shop, stays; one marked LEAVES, ending the menu, needs none)."""

    def __init__(self):
        self.items: List = []
        self.shown = 0  # lines in the window since it was last cleared (as laid out)
        self.subs: Dict[str, Callable[[], None]] = {}
        self._n = 0
        self._asked = DONE  # (the locals for replies asked: DONE + 1 on)

    def op(self, code: int, *args) -> None:
        self.items.append((code, list(args)))

    def label(self, name: str) -> None:
        self.items.append(name)

    def _new(self, what: str) -> str:
        self._n += 1
        return f"{what} {self._n}"

    def say(self, text: str, who: int = SPEAKS) -> None:
        """TEXT in the window, a new page whenever the window (WINDOW lines) would run over."""
        for line in _lines(text):
            if self.shown == WINDOW:
                self.page()
            self.op(0x4F, ("n", who), ("str", line))
            self.shown += 1

    def page(self) -> None:
        """Wait for a click, then clear the window."""
        self.op(0x4F, ("n", SPEAKS), MORE)
        self.clear()

    def clear(self) -> None:
        self.op(0x4F, ("n", SPEAKS), CLEAR)
        self.shown = 0

    def set(self, var: int, value: int) -> None:
        self.op(0x16, ("n", value), ("var", 14, var))

    def flag(self, flag: int, value: int) -> None:
        self.op(0x16, ("n", value), ("var", 13, flag))

    def when(self, test, then: Callable[[], None], otherwise: Optional[Callable[[], None]] = None) -> None:
        """If TEST: THEN, else OTHERWISE."""
        other, done = self._new("else"), self._new("end if")
        self.op(0x18, test)
        self.op(0x3E, ("label", other if otherwise else done))
        shown = self.shown
        then()
        if otherwise:
            self.label(other)
            self.op(0x3F, ("label", done))
            self.shown = shown
            otherwise()
        self.label(done)
        self.op(0x67)
        self.shown = 0  # (either way)

    def sub(self, name: str, body: Callable[[], None]) -> None:
        """A subroutine NAME (laid out at the end, after the script's end)."""
        self.subs[name] = body

    def call(self, name: str) -> None:
        self.op(0x13, ("label", name))
        self.shown = 0

    def menu(self, replies: List[Tuple[str, Callable[[], None], object]]) -> None:
        """A menu, shown again until a reply leaves it (leave()). Each reply (REPLIES: text, body,
        shown when) is a subroutine doing its own part (calling the rest of the talk, as the
        game's replies do), so nothing branches after the menu."""
        loop, out = self._new("menu"), self._new("menu out")
        names, conditions, asked = [], [], []
        for text, body, shown in replies:
            name = self._new("reply")
            names.append(name)
            if getattr(body, "leaves", False) or getattr(body, "again", False):
                self.sub(name, body)
                conditions.append(shown)
                continue
            self._asked += 1
            local = self._asked
            if local >= ASKED_LAST:
                raise gpl.ScriptError("too many replies to hide once asked")
            asked.append(local)
            self.sub(name, lambda body=body, local=local: (self.set(local, 1), body()))
            unasked = ["(", ("var", 0x8E, local), "==", ("n", 0), ")"]
            if shown == ALWAYS:
                conditions.append(("expr", unasked))
            else:
                inner = list(shown[1]) if shown[0] == "expr" else [shown]
                conditions.append(("expr", ["("] + inner + [")", "and"] + unasked))
        for local in asked:
            self.set(local, 0)
        self.set(DONE, 0)
        self.label(loop)
        self.op(0x18, ("expr", [("var", 0x8E, DONE), "==", ("n", 0)]))
        self.op(0x63, ("label", out))
        self.op(0x48, {"before": [], "title": TITLE, "replies": [
            {"text": ("str", f"  {text}"), "goto": ("label", name), "if": shown, "before": [], "after": []}
            for (text, _, _), shown, name in zip(replies, conditions, names)]})
        self.op(0x64, ("label", loop))
        self.label(out)

    def leave(self) -> None:
        """(In a reply:) leave the menu once the reply is done (and any menu it went through)."""
        self.set(DONE, 1)

    def bytes(self, base: int = 0, end: bool = True) -> bytes:
        """The script; BASE: where in its script it goes (a piece of another's), with END its own
        end (31h) and subroutines after it."""
        if end:
            self.op(0x31)  # the talk's end
        done = set()
        while len(done) < len(self.subs):  # (subroutines may add subroutines)
            for name, body in list(self.subs.items()):
                if name in done:
                    continue
                done.add(name)
                self.label(name)
                self.shown = 0
                if name.startswith("reply"):
                    self.clear()
                body()
                self.op(0x15)

        def fill(x, at):
            if isinstance(x, tuple) and x and x[0] == "label":
                return ("n", at[x[1]])
            if isinstance(x, gpl.Op):
                return gpl.Op(x.at, x.code, fill(x.args, at))
            if isinstance(x, list):
                return [fill(y, at) for y in x]
            if isinstance(x, tuple):
                return tuple(fill(y, at) for y in x)
            if isinstance(x, dict):
                return {k: fill(v, at) for k, v in x.items()}
            return x
        # (a jump's place is 2 bytes whatever it is, so the lengths are known before the places)
        labels = {i: 0 for i in self.items if isinstance(i, str)}
        at, pos = {}, base
        self.at = at  # (where each label went)
        for item in self.items:
            if isinstance(item, str):
                at[item] = pos
            else:
                pos += len(gpl.encode_op(fill(item, labels)))
        return b"".join(gpl.encode_op(fill(item, at)) for item in self.items if not isinstance(item, str))


ALWAYS = ("n", 1)
DONE = 1  # the script's local ending a menu (as the game's merchants use 1 for the menu loop)
ASKED_LAST = 15  # (the replies asked: locals 2 to 14)


def leaves(body: Callable[[], None]) -> Callable[[], None]:
    """BODY marked as a reply ending its menu (no local to hide it)."""
    body.leaves = True
    return body


def again(body: Callable[[], None]) -> Callable[[], None]:
    """BODY marked as a reply to stay in the menu once chosen (a shop)."""
    body.again = True
    return body
WINDOW = 4  # the lines the dialogue window shows


# The escape's alarm: the game's flag, set as the guards raise it (the arena's breakout, script 3)
# and tested by the pens' slaves to say so instead of their talk (scripts 142, 146)
ALARM = 20
ALARM_FRIENDLY = ("That's the alarm. So it's you breaking out. Go, and go quickly: if they find you "
                  "at my cell, I burn with you.")
ALARM_COLD = "The alarm's for you, isn't it? Good. Run, and let them chase you, not me."
ALARM_STRANGER = "That's the alarm. Whoever you are, this is no time to talk. Go!"


def _is(var, value) -> tuple:
    return ("expr", [var, "==", ("n", value)])


def conversation() -> bytes:
    """Kalzith's conversation (script SCRIPT)."""
    s = _Script()
    friendly, cold_, met, sold_out = (("var", 0x8D, f) for f in (FRIENDLY, COLD, MET, SOLD_OUT))

    def then_leave(*parts):
        def body():
            for part in parts:
                part()
            s.leave()
        return leaves(body)

    def go():
        s.say("Go, then.")
        s.page()

    # -- the first meeting
    def first():
        s.menu([("We mean no harm. We're slaves too.", then_leave(lambda: s.call("respect")), ALWAYS),
                ("You're a defiler. You kill the land.", then_leave(lambda: s.call("accused")), ALWAYS),
                ("Who are you?", who, ALWAYS),
                ("Farewell.", then_leave(go), ALWAYS)])

    def who():
        s.say("Kalzith. Once a sorcerer's apprentice in Draj, now Pehtucl's property. The templars "
              "put a defiler in the arena now and then: the crowd loves to watch one burn. The rest of "
              "the time they put me in here, where the ground's already dead.")

    def respect():
        s.clear()
        s.flag(FRIENDLY, 1)
        s.flag(COLD, 0)
        s.say("Hm. Slaves with manners. Rarer than water. Keep your voice down.")
        s.page()
        s.say("I have something you might want. I scribe spells on scraps of hide, at night. A "
              "preserver could learn from them: the magic on the page doesn't care how you draw your "
              "power.")
        s.page()
        s.say("And I need ceramic for a guard who can look the other way.")
        s.call("friend")

    # -- a friend: the shop
    def friend():
        s.menu([("Show us what you have.", again(shop), _is(sold_out, 0)),
                ("Anything left to sell?", nothing_left, _is(sold_out, 1)),
                ("Why would a defiler help a preserver?", why, ALWAYS),
                ("Isn't this dangerous for you?", danger, ALWAYS),
                ("Farewell.", then_leave(see_you), ALWAYS)])

    def shop():
        s.say("Quietly, now. One of each, and they're not cheap.")
        s.page()
        s.op(0x24, SPEAKER)  # (his own place in the game's object table: where its shops are)
        s.say("Learn them well, and burn the hide when you're done.")

    def nothing_left():
        s.say("Nothing. You've bought every scrap of hide I had, and the robe off my back. More "
              "takes time I don't have.")

    def why():
        s.say("Because a preserver's coin buys the same bribe. And because I'm tired of being the "
              "only one in the pens the others fear.")

    def danger():
        s.say("Everything is dangerous for me. Pehtucl would flay me for this. So keep it quiet.")

    def see_you():
        s.say("Come back when you've earned some coin.")
        s.page()

    # -- accused, and cold
    def accused():
        s.clear()
        s.say("And the templars kill slaves with every order. We do what Athas lets us.")
        s.menu([("Fair enough. I spoke too quickly.", then_leave(lambda: s.call("respect")), ALWAYS),
                ("We'll tell the templars about you.", then_leave(turn_cold), ALWAYS),
                ("Farewell.", then_leave(go), ALWAYS)])

    def turn_cold():
        s.flag(COLD, 1)
        s.say("Then go and tell them, and see whom they believe. I have nothing more to say to you.")
        s.page()

    def cold():
        s.say("I have nothing to say to you. Go and tell your templars.")
        s.menu([("Here's 50 ceramic, as an apology.", then_leave(paid), ("expr", [MONEY, ">=", ("n", 50)])),
                ("We're all slaves. Let's be friends.", then_leave(plead), ALWAYS),
                ("Farewell.", then_leave(lambda: None), ALWAYS)])

    def plead():
        s.when(("op", gpl.Op(0, gpl.ABILITY_CHECK, [ACTOR, ("n", 1), ("n", CHA)])), won_over, not_won)

    def paid():
        s.op(0x0C, ("n", -50))
        s.say("Coin that rings. That's an apology I'll take.")
        s.page()
        s.call("respect")

    def won_over():
        s.say("Hm. Fine. We're all slaves here.")
        s.page()
        s.call("respect")

    def not_won():
        s.say("Words are cheap in the pens.")
        s.page()

    # (every menu in a subroutine of its own: one laid out in the greeting's "if"s hung the game
    # when a reply went back to it, "Who are you?")
    for name, body in (("first", first), ("cold", cold), ("respect", respect), ("friend", friend),
                       ("accused", accused)):
        s.sub(name, body)

    def meeting():
        s.say("New faces in the pens. Mind the dust: nothing has grown in here since they put me in. "
              "What do you want?")
        s.flag(MET, 1)

    def greeting():
        s.when(_is(cold_, 1), lambda: s.call("cold"),
               lambda: s.when(_is(friendly, 1),
                              lambda: (s.say("Back again? Keep your voice down."), s.call("friend")),
                              lambda: (s.when(_is(met, 1), lambda: s.say("You again. Well?"), meeting),
                                       s.call("first"))))

    # the escape's alarm sounding (the game's flag ALARM), as the pens' other slaves have it: a
    # line for the party, by how he stands with them, and no talk
    def alarm():
        s.when(_is(friendly, 1),
               lambda: s.say(ALARM_FRIENDLY),
               lambda: s.when(_is(cold_, 1), lambda: s.say(ALARM_COLD), lambda: s.say(ALARM_STRANGER)))
        s.page()

    s.op(BEGIN)  # (every script of the game's opens so; its talk commands start after it)
    s.op(0x54, ("n", PORTRAIT))
    s.when(_is(("var", 0x8D, ALARM), 1), alarm, greeting)
    return s.bytes()


# ---------------------------------------------------------------------------------------------
# The scripts file: his conversation, and the command that runs it

TALK = 0x6E  # (place in a script, script, object): what talking to the object runs
END = 0x31


def with_talk(master: bytes, field_types: bytes = b"") -> bytes:
    """The pens' master script with Kalzith's talk command (once), last, just before its end: the
    script's "if" at 302 skips on to an offset in it, so nothing of the game's may move (his
    command put in after the other talk commands sent that skip into the middle of a command,
    and Merzol, the doors, the gate and the water were lost to whatever it read there)."""
    ops = gpl.decode(master, field_types)
    talk = gpl.encode_op((TALK, [("n", START), ("n", SCRIPT), ("n", -OBJECT)]))
    if talk in master:
        return master
    if ops[-1].code != END:
        raise gpl.ScriptError("the master script doesn't end as expected")
    end = ops[-1].at
    return master[:end] + talk + master[end:]


ENTRY = struct.Struct("<HHH")  # GPLI: (entry number, place in the script, script), numbered from 0
ENTRIES = ("GPLI", 1)


def with_entry(entries: bytes, script: int = SCRIPT) -> bytes:
    """The game's table of script entry points with his talk's (once). A save keeps each talk
    command as its entry's number, and loading turns the number back into place and script: one
    not in the table is saved as 0 and comes back as entry 0, a dead one."""
    table = [ENTRY.unpack_from(entries, i) for i in range(0, len(entries) - ENTRY.size + 1, ENTRY.size)]
    if any(e[1:] == (START, script) for e in table):
        return entries
    return entries + ENTRY.pack(max((e[0] for e in table), default=-1) + 1, START, script)


def script_chunks(gpldata: bytes, kalzith: bool = True, semyon: bool = True,
                  vulture: bool = True, ring: bool = True, arms: bool = True,
                  magic: bool = True, cloak: bool = False, tome: bool = False,
                  pens: bool = True, hay: bool = False) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of GPLDATA: his conversation, and the master script running it (and
    Semyon's, semyon.py; Dinos's and the Trustee's questions, pensasks.py; Alagorn on Kreenfang
    and Shadowseeker, alagorn.py), each part only if switched on (the Options tab's new content)."""
    chunks = read_gff(gpldata)
    if ("MAS ", MASTER) not in chunks:
        return {}
    field_types = next((v for k, v in chunks.items() if k[0] == "GPLX"), b"")[gpl.FIELD_TYPES_AT:]
    out: Dict[Tuple[str, int], bytes] = {}
    if kalzith:
        out[("GPL ", SCRIPT)] = conversation()
        out[("MAS ", MASTER)] = with_talk(chunks[("MAS ", MASTER)], field_types)
        if ENTRIES in chunks:
            out[ENTRIES] = with_entry(chunks[ENTRIES])
        face = portrait_chunk(chunks)
        if face and ("PORT", PORTRAIT) not in chunks:
            out[("PORT", PORTRAIT)] = face
    if semyon:  # Semyon, in the pens as he promises (semyon.py): his part after Kalzith's
        from . import semyon as sm
        out[("GPL ", sm.SCRIPT)] = sm.conversation()
        out[("MAS ", MASTER)] = sm.with_semyon(out.get(("MAS ", MASTER), chunks[("MAS ", MASTER)]), field_types)
        if ENTRIES in chunks:
            out[ENTRIES] = with_entry(out.get(ENTRIES, chunks[ENTRIES]), sm.SCRIPT)
        arena = ("GPL ", sm.ARENA_TALK)
        if arena in chunks:  # (his leaving after the fight marked)
            out[arena] = sm.with_exit(chunks[arena], field_types)
        escape = ("GPL ", sm.ESCAPE_SCRIPT)
        if escape in chunks:  # (taken along to the pens with Scar)
            out[escape] = sm.with_escape(chunks[escape], field_types)
    # Dinos and the Trustee asked about him and Semyon, and Dinos about the vulture (pensasks.py);
    # the questions about either show only once he is in the pens (their flags)
    from . import pensasks
    out.update(pensasks.script_chunks(chunks, field_types, vulture=vulture))
    if arms or magic or pens or ring:  # Alagorn tells of the new magic items (alagorn.py; the rings
        from . import alagorn  # and cloak of protection with the pens' people's or the arena's ring)
        out.update(alagorn.script_chunks(chunks, field_types, arms, magic, pens or ring))
    if cloak:  # the Elven Leader gives the Cloak of Elvenkind (elvenleader.py; its object in the
        from . import elvenleader  # objects' copy)
        out.update(elvenleader.script_chunks(chunks, field_types))
    if tome:  # Father Garyn gives the Tome of Understanding (garyn.py; its object in the objects' copy)
        from . import garyn
        out.update(garyn.script_chunks(chunks, field_types))
    if hay:  # Hayneedle in Merzol's hay stash (haystash.py; its object in the objects' copy)
        from . import haystash
        out.update(haystash.script_chunks(chunks, field_types))
    from . import manualcheck  # no manual check (the dragon's question): always
    out.update(manualcheck.script_chunks(chunks, field_types))
    if ring:  # the XP for finding the arena's ring (ring.py), in the same script as Semyon's exit
        from . import ring as rg
        body = ("GPL ", rg.BODY_SCRIPT)
        if body in chunks:
            changed = rg.with_xp(out.get(body, chunks[body]), field_types, chunks[body])
            if changed != out.get(body, chunks[body]):
                out[body] = changed
    return out


def region_chunks(rgn: bytes, gifts=()) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of RGN29.GFF: the pens' entity table with him in it (and with
    GIFTS' clones there, worldgear.py's: the pens' weapon rack's own object)."""
    from . import worldgear
    chunks = read_gff(rgn)
    if ("ETAB", ETAB_ID) not in chunks:
        return {}
    etab = worldgear.region_chunks(REGION, chunks, gifts).get(("ETAB", ETAB_ID), chunks[("ETAB", ETAB_ID)])
    return {("ETAB", ETAB_ID): with_entity(etab)}


# ---------------------------------------------------------------------------------------------
# His stock, given once a game

CREATURES_SEEN = 128  # creature records searched for him (the pens have 34)


DEAD_STATUS = (4, 5)  # a creature's status: dying, dead (as stealth.py)


def dead(gd, name: str, seen: int = CREATURES_SEEN) -> bool:
    """Whether a creature named NAME is among the first SEEN, dead (no hit points, or dying or
    dead)."""
    table = gd.creatures(seen)
    want = name.encode("ascii") + b"\0"
    size = game.CREATURE_SIZE
    for at in range(0, len(table) - size + 1, size):
        rec = table[at:at + size]
        if rec[game.CREATURE_NAME:game.CREATURE_NAME + len(want)] != want:
            continue
        if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in DEAD_STATUS:
            return True
    return False


def watch(gd) -> bool:
    """DIED set once Kalzith is seen dead. True when it was set now."""
    if gd.flag(DIED) or not dead(gd, NAME):
        return False
    gd.set_flag(DIED)
    return True


# What he wears: a plain Cloak and Quarterstaff (the game's own records, from SEGOBJEX) and his
# Ashen Robe (robes.py), given with his scrolls (stock). His shop offers all he has, worn or not,
# in any of his lists (the game has no mark for an item a merchant won't sell), so these are for
# sale too. What he leaves when killed: whatever he still carries, which the game puts in a pile
# where he fell (none if he has nothing); of the scrolls, the Loader leaves one, at random, and
# takes the others out of it (once: LOOTED).
LOOTED = 777
# Once he carries nothing (the Loader's flag SOLD_OUT), his shop is no longer offered ("Anything
# left to sell?" "Nothing."). DRESSED: his gear given (with his scrolls, when stocked).
DRESSED, SOLD_OUT = 776, 778
RIGHT_HAND = game.EQUIP_SLOTS.index("right hand")
CLOAK_TEMPLATE = "e3fb000000001400000041003500000003ff0e0000"  # the game's Cloak (as npcitems')
QUARTERSTAFF_TEMPLATE = "05fc0000000001000000030000000000" "04ff040000"  # the game's Quarterstaff


def _index(gd) -> Optional[int]:
    """His creature record (among the first CREATURES_SEEN), if he is alive."""
    table = gd.creatures(CREATURES_SEEN)
    want = NAME.encode("ascii") + b"\0"
    size = game.CREATURE_SIZE
    for index in range(game.PARTY_SIZE, len(table) // size):
        rec = table[index * size:(index + 1) * size]
        if rec[game.CREATURE_NAME:game.CREATURE_NAME + len(want)] == want:
            alive = struct.unpack_from("<h", rec, 0)[0] > 0 and rec[game.CREATURE_STATUS] not in DEAD_STATUS
            return index if alive else None
    return None


def sold_out(gd, quiet: bool) -> List[str]:
    """In the pens, with him alive and stocked: SOLD_OUT once he carries nothing (his scrolls and
    his gear all bought). SOLD_OUT while talking with him
    (the last one just bought) or when QUIET (the map's main loop running: no talk, menu or shop
    open), never while a game loads, when one game's flags can be read with another's people; his
    things only when QUIET (never into an open shop). His scrolls are counted by
    either number (an earlier build's, until mended), and a game marked sold out while he still
    has some has its shop back. What was given, by name."""
    from . import ring
    if gd.region() != REGION or not gd.flag(STOCKED) or gd.flag(DIED):
        return []
    index = _index(gd)
    if index is None:
        return []
    it = ring.Items(gd)
    rec = gd.creature(index)
    if any(True for o in game.CREATURE_ITEM_LISTS for _ in it.chain(struct.unpack_from("<h", rec, o)[0])):
        if gd.flag(SOLD_OUT) and quiet:
            gd.set_flag(SOLD_OUT, False)  # (marked by mistake: his shop back)
        return []
    talking = getattr(gd, "talk_target", lambda: None)() == NAME  # (the last one just bought)
    if (quiet or talking) and not gd.flag(SOLD_OUT):
        gd.set_flag(SOLD_OUT)
    return []


def gear() -> List[Tuple[bytes, Optional[int], str]]:
    """What he wears: (item record, slot, name)."""
    from . import npcitems, robes
    return [(npcitems._item(QUARTERSTAFF_TEMPLATE), RIGHT_HAND, "Quarterstaff"),
            (npcitems._item(CLOAK_TEMPLATE), game.CLOAK_SLOT, "Cloak"),
            (robes.item(robes.ASHEN), robes.CHEST_SLOT, "Ashen Robe")]


def _held_by_party(gd, it) -> set:
    held = set()
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        for offset in game.CREATURE_ITEM_LISTS:
            thing = struct.unpack_from("<h", rec, offset)[0]
            held.update(index for index, _ in it.chain(thing))
    return held


def loot(gd, choose: Callable = None) -> List[str]:
    """Once he is dead (DIED): of his scrolls the party doesn't hold, one kept (CHOOSE, random by
    default) and the others taken away (his gear the game leaves with him); once (LOOTED). The
    scroll left, by name."""
    import random
    from . import ring
    if not gd.flag(DIED) or gd.flag(LOOTED):
        return []
    it = ring.Items(gd)
    held = _held_by_party(gd, it)
    mine = {-(SCROLL_OBJECT + k): name for k, (_, name, _) in enumerate(SCROLLS)}
    left = {index: mine[struct.unpack_from("<h", rec, ITEM_OBJECT)[0]]
            for thing in range(ring.THING_COUNT) for index, rec in it.chain(thing)
            if struct.unpack_from("<h", rec, ITEM_OBJECT)[0] in mine and index not in held}
    gd.set_flag(LOOTED)
    if not left:
        return []  # (all bought)
    keep = (choose or random.choice)(sorted(left))
    for index in sorted(left):
        if index != keep:
            ring.unlink(gd, ring.Items(gd), index, "given back (Kalzith's)")
    return [f"Scroll of {left[keep]}"]


def stock(gd, new_spells: bool) -> List[str]:
    """In the pens, once a game, Kalzith gets his scrolls (Cat's Grace only with the new spells on) and
    his gear, worn (DRESSED); the game's flag STOCKED marks it done (a save keeps it, a new game
    starts without it). What was given, by name."""
    from . import npcitems
    if gd.region() != REGION or gd.flag(STOCKED):
        return []
    # (found by name among the region's creatures: not among the first 256 objects, where he
    # is not - the pens' last, past the 256th)
    table = gd.creatures(CREATURES_SEEN)
    name = NAME.encode("ascii") + b"\0"
    for index in range(game.PARTY_SIZE, len(table) // game.CREATURE_SIZE):
        at = index * game.CREATURE_SIZE
        if table[at + game.CREATURE_NAME:at + game.CREATURE_NAME + len(name)] != name:
            continue
        out = [name_ for rec, slot, name_ in gear() if npcitems.add_to(gd, index, rec, slot)]
        out += [name_ for k, (spell, name_, price) in enumerate(SCROLLS)
                if (new_spells or spell not in game.NEW_SPELLS)
                and npcitems.add_to(gd, index, scroll(spell, price, k))]
        gd.set_flag(DRESSED)
        gd.set_flag(STOCKED)
        return out
    return []


def mend(gd) -> int:
    """His scrolls of earlier builds, wherever they are now (his things, the party's, the ground:
    each scroll is its own object), made as they are now: each teaching its own spell (before
    SCROLL_SPELL_FROM, the one before it), with its object among those the game teaches from
    (before SCROLL_OBJECT, OLD_SCROLL_OBJECT + k, which it cast from), and at its price now
    (before, 100 to 500). How many were."""
    from . import ring
    it = ring.Items(gd)
    want = {}
    for k, (spell, _, price) in enumerate(SCROLLS):
        for number in (SCROLL_OBJECT + k, OLD_SCROLL_OBJECT + k):
            want[-number] = (-(SCROLL_OBJECT + k), spell + SCROLL_SPELL_FROM, price)
    done = set()
    for thing in range(ring.THING_COUNT):
        for index, rec in it.chain(thing):
            now = struct.unpack_from("<h", rec, ITEM_OBJECT)[0]
            if now not in want or index in done:
                continue
            obj, spell, price = want[now]
            if (now, struct.unpack_from("<H", rec, ITEM_SPELL)[0], rec[ITEM_SPELL_AGAIN],
                    struct.unpack_from("<H", rec, ITEM_VALUE)[0]) == (obj, spell, spell, price):
                continue
            done.add(index)
            at = it.items + index * game.ITEM_SIZE
            gd.guest.write(at + ITEM_OBJECT, struct.pack("<h", obj))
            gd.guest.write(at + ITEM_SPELL, struct.pack("<H", spell))
            gd.guest.write(at + ITEM_SPELL_AGAIN, bytes([spell]))
            gd.guest.write(at + ITEM_VALUE, struct.pack("<H", price))
    return len(done)


# ---------------------------------------------------------------------------------------------
# The copies

def _write(source: str, dest: str, added) -> None:
    import os
    from .icons import with_chunks
    with open(source, "rb") as f:
        data = f.read()
    out = with_chunks(data, added(data))
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, dest)


def write_scripts(source: str, dest: str, kalzith: bool = True, semyon: bool = True, vulture: bool = True,
                  ring: bool = True, arms: bool = True, magic: bool = True, cloak: bool = False,
                  tome: bool = False, pens: bool = True, hay: bool = False) -> None:
    """The game's GPLDATA.GFF (SOURCE, only read) with Kalzith's conversation (and the rest of
    the new content switched on), to DEST."""
    _write(source, dest, lambda data: script_chunks(data, kalzith, semyon, vulture, ring, arms, magic, cloak, tome, pens,
                                                             hay))


def write_region(source: str, dest: str, gifts=()) -> None:
    """The game's RGN29.GFF (SOURCE, only read) with Kalzith in his pen (and GIFTS' clones), to
    DEST."""
    _write(source, dest, lambda data: region_chunks(data, gifts))
