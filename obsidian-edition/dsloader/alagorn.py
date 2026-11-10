"""Alagorn tells of the Loader's magic items: Kreenfang and Shadowseeker (arms.py), Gutterknot,
Deepbiter, Windlash, Greenbright and the Flame Blade, the axes, daggers, polearms, bow and
chatkcha, the Warden's Plate, Gutterward and Ironbulwark, the Cloak and Boots of
Elvenkind, the Bracers of Defense, Arrowbane and the Sunking Crown (worldgear.py), and the Tome of
Understanding (tome.py), Inixhide (npcitems.py), and the Rings and Cloak of Protection (ring.py,
npcitems.py): one story for each kind, whichever of it the party carries, as the game's own.

Alagorn, the wizard wandering the Painted Badlands, identifies magic items from menus by kind:
magic swords, magic weapons, fruit and wands (script 213); rings, armour, shields, necklaces,
clothes and other items (script 212). Each kind's part sees which of the items he knows the party
carries (a local for each, from a query on the item's picture: the Bloodwrath's is -1576), says
there are none, or shows a menu of those, one reply each; a reply's story clears its local, and
when none is left (a local of the script's: DONE) the menu's loop ends.

With the Loader, Shadowseeker, Greenbright and the Flame Blade join the swords, Kreenfang,
Gutterknot, Deepbiter and Windlash the weapons, Inixhide and the Warden's Plate's four pieces the
armour, Gutterward and Ironbulwark the shields, the Cloak and Boots of Elvenkind, the bracers, Arrowbane, the crown and the cloak of
protection the clothes (where the game has its Helm of Contemplation and Chameleon Gloves), the
rings of protection the rings, and the tome the other items, by their pictures of their own
(icons.py: without the icons' copy he doesn't know them; the tome's, its object's), each only
with its content switch on. As pensasks.py does, nothing
of the game's script moves: commands of it become jumps (64h) to code put after the script's end,
which jumps back:

- each kind's first test for none carried (the tests just before "none"): the new items' locals
  set too, then the game's tests again, the new items counted in the last: none carried goes on
  to "no magic swords" / "no magic weapons"..., any to where the game's test goes;
- the kind's menu: a copy with the new items' replies after the game's last;
- each of the kind's stories' test for none left: the new items counted too.

The new stories are subroutines, as the game's replies are. The weapons' copy (222) would be
longer than the scripts' buffer with its fourteen stories in it, so their lines are in a script of
their own (TOLD_IN: 224), one part each after a 19h, and each story subroutine calls its part
(14h, as his talk calls each of 212's and 213's parts; the 19h ending the part returns).
"""

import logging
from typing import Dict, List, Optional, Tuple

from . import gpl, icons
from .kalzith import _Script
from .pensasks import GOTO, LONGEST, MENU, TEST
from .tome import TOME_OBJECT

SCRIPT = 213  # Alagorn's
LOCAL_READ, LOCAL_SET = 0x8E, 14
QUERY, PARTY, HAS_PICTURE = 0x33, 32766, 72  # a query on the party's items: picture equal
DONE = 15  # the menu loop's local in script 213 (1: leave it; script 212's is 6)
LOCALS = 16  # (the script's locals)
SET, SAY = 0x16, 0x4F
NOTHING = "  Nothing"  # each menu's last reply, leaving it


class Kind:
    def __init__(self, first_reply: str, none_text: str, items: Tuple[Tuple[str, str], ...]):
        self.first_reply, self.none_text, self.items = first_reply, none_text, items


SWORDS, WEAPONS = ("  Darkflame", "It's too bad that you have no magic swords I know about. "), \
    ("  Balkazar's Staff", "I don't see any magic weapons that I know anything about. ")
ARMOUR, CLOTHES = ("  Tanelyv's Armor", "You have no magic armor that I know anything about. "), \
    ("  Belt of Might", "Unfortunately, you have no magic clothes that I know anything about. ")
RINGS, OTHER = ("  Light of Dawn", "However, you have no magic rings that I know anything about. "), \
    ("  Orb of Knowledge", "You have no other magic items that I know anything about. ")
SHIELDS = ("  El's Shield", "You have no magic shields that I know anything about. ")
OTHER_SCRIPT = 212  # (rings, armour, clothes and other items: Alagorn's other menus)
SCRIPT_OF = {SWORDS: SCRIPT, WEAPONS: SCRIPT, RINGS: OTHER_SCRIPT, ARMOUR: OTHER_SCRIPT, SHIELDS: OTHER_SCRIPT,
             CLOTHES: OTHER_SCRIPT, OTHER: OTHER_SCRIPT}
# Scripts 212 and 213 with every story would be longer than the scripts' buffer: 212's clothes, and
# its rings and other items, and 213's weapons are told by copies of them, each with only those
# (the Loader's scripts; Kalzith's 218, Semyon's 219). His talk (script 211) calls each part by its
# place in its script (14h): the call for those parts names the copy instead, its places the same.
TALK = 211
COPY_OF = {CLOTHES: 220, RINGS: 221, OTHER: 221, WEAPONS: 222}
CALL, START = 0x14, 0x19
# ... and the weapons' copy with all fourteen of its stories in it would still be (12,405 bytes, the
# buffer's LONGEST 11,376): their lines are in a script of their own, each story calling its part
TOLD_IN = {222: 224}
EXIT = 0x31
# What script_chunks left out, and why (a kind's part too long, or not as expected), for the
# Loader to tell: each run starts it afresh
LEFT_OUT: List[str] = []
_log = logging.getLogger(__name__)
# (item, story): the slave pens' two (arms.py)
ARMS = {
    SWORDS: (("Shadowseeker",
              "Shadowseeker! The head guards of the Draj slave pens have passed it down, one to the "
              "next. With it in hand, no slave could hide from them: not in the pens' shadows, not "
              "behind an illusion, not even made invisible by a friend's magic. Many an escape ended "
              "at its point. Better that it is in your hands now."),),
    WEAPONS: (("Kreenfang",
               "Kreenfang! The tohr-kreen say a gythka's blades are grown, not carved, and a clutch's "
               "elder blessed this one before the hunt. It strikes truer and deeper than any common "
               "gythka. A kreen does not part with such a weapon while it lives; whoever carried it "
               "into the arena died with it in hand."),),
}
# ... the slave pens' people's and the arena prisoner's (npcitems.py, ring.py): Inixhide, and the
# rings and cloak of protection, told of as a kind, as the bracers are (one story for all, as the
# game's own of a kind)
PENS = {
    RINGS: (("Ring of Protection",
             "A Ring of Protection! Every apprentice of the old schools made one as a first work, "
             "before the sorcerer-kings closed the schools; few are left now. It turns aside a blow "
             "that should have landed, and a curse that should have taken hold. The templars take "
             "them from those they arrest, and wear them themselves."),),
    ARMOUR: (("Inixhide",
              "Inixhide! The monster trainers of Draj have passed it down, one to the next, since "
              "the arena was young. It was cut from the first inix ever broken to the harness, and "
              "every trainer since has paid the templars to work a little more strength into it. "
              "Claws and teeth turn on it as on no common leather."),),
    CLOTHES: (("Cloak of Protection",
               "A Cloak of Protection! Its weave turns aside blades and spells alike: only a little, "
               "but a little is often enough. The tailors who know the craft sell to the templars by "
               "day and to the Veiled Alliance by night, and neither asks the other's business."),),
}
# ... and the world's (worldgear.py; the tome, tome.py)
MAGIC = {
    SWORDS: (("Greenbright",
              "Greenbright! True iron, forged in the Green Age, when Athas still had forests and "
              "smiths who knew more than how to knap stone. It was a long sword once; a thousand "
              "years of sharpening have worn it short, and the old enchantment only grew keener "
              "for it. Arant took it from a gladiator who would not kneel. He never fought fair "
              "again, and never needed to."),
             ("Flame Blade",
              "A Flame Blade! Its blade is no common obsidian, but glass from the heart of a "
              "fire-mountain, and the clerics of fire sang its flames into it. Whatever it cuts, "
              "it burns. The templars of Draj have tried to keep every one of them; the one at "
              "the Hot Springs wore his like a badge, though he never knew the prayers to wake it."),
             ("Mindshard",
              "Mindshard! A psionicist knapped its blade and would let no hand but hers shape it; "
              "she held the stone in her mind as she worked, and some of her will stayed in it. It "
              "answers a trained mind better than any sword of its kind, and strikes truer and "
              "deeper. Psionicists hand it down, master to pupil."),
             ("Stillwater",
              "Stillwater! Carved from the rib of a beast that drank at the last clear pool in the "
              "Tablelands, and bound by a mind and a water cleric together. It strikes truer than any "
              "common short sword, and its wielder's thoughts stay calm in the thick of a fight."),),
    WEAPONS: (("Gutterknot",
               "Gutterknot! A knot of agafari root, the hardest wood under the sun, with the stub "
               "of an iron spike driven through it. Every boss of the Draj low warrens has beaten "
               "his way up with it and held it until someone beat him down with it in turn. The "
               "warrens say whoever holds it can't be made to kneel. Churrr believed that."),
              ("Deepbiter",
               "Deepbiter! A dwarf of the Undermountain made it his focus: to dig to the root of "
               "the world. He cut its head from a vein of stone no other pick could mark and sang "
               "into it every day of his life. It breaks rock as other picks break earth, and "
               "bone more easily still. His kin kept it after he died, still digging."),
              ("Windlash",
               "Windlash! The desert elves make their staff slings to run and hunt with at once. "
               "This one was made for a chieftain's son, its cords braided with his own hair, and "
               "a wind spirit's blessing sung over it. Its stones fly farther and strike harder "
               "than any other's. How a village bowyer came by it, I'd rather not ask."),
              ("Drakejaw",
               "Drakejaw! Its head was cut from the jaw of a drake, teeth and all, and a druid of "
               "the wastes sang the drake's hunger back into it. It bites deeper than any common "
               "axe, and it never dulls. Whoever carried it last had no idea what he held."),
              ("Glasshewer",
               "Glasshewer! Its head was knapped from one flawless block of obsidian, black glass "
               "that holds an edge no stone can match. The templars gave it to their slavers to cut "
               "down any slave who ran. It strikes truer and deeper than any common axe; the elves "
               "it was used on would be glad to see it in other hands."),
              ("Headsman",
               "Headsman! The arenas once kept their own executioners, and this was the last of "
               "their axes: true iron, forged in the Green Age, heavy enough to end a fight in one "
               "stroke. It has passed from champion to champion since. It strikes truer and harder "
               "than any other great axe."),
              ("Galefang",
               "Galefang! The clerics of the air bless few blades; the wind, they say, needs no edge. "
               "This one they made for a cleric who guarded their high places, and the wind sharpens "
               "it still: it strikes truer and deeper than any common dagger. How a rogue shaman came "
               "by it, the clerics would dearly like to know."),
              ("Linebreaker",
               "Linebreaker! True iron on a long agafari haft, made in the Green Age for the soldiers "
               "who held a city's gates. A rank of them could stop a charge of inix. This one has "
               "outlived every army that carried it. It strikes truer and harder than any common "
               "polearm, and reaches over a shield."),
              ("Thornwall",
               "Thornwall! A thri-kreen's polearm, its blade a bone hook as long as a man's arm, bound "
               "in chitin. The kreen hold a line with them and drag riders from their kanks. It strikes "
               "truer than any common polearm."),
              ("Hayneedle",
               "Hayneedle! A slave of the Draj pens carved it from the shin of a mekillot, a little "
               "each night, and a cleric of water in the next cell prayed over it as he worked. He "
               "never got the chance to use it. It strikes truer than any common dagger, and it hides "
               "where nothing else would."),
              ("Nightsliver",
               "Nightsliver! Knapped from the black glass that wells up where the lava rifts open, "
               "and cooled in the dark of a moonless night so the fire stayed in it. The defiler who "
               "carried it thought it a pretty knife. It strikes truer and deeper than any common "
               "dagger."),
              ("Dunesong",
               "Dunesong! A desert elf made it from a horn of the wild kank and sinew of a crodlu, "
               "and its string sings when it looses, like wind over the dunes. Its arrows fly true. "
               "The Bowyer will tell you he bought it from a trader; the elves will tell you "
               "otherwise."),
              ("Skycutter",
               "Skycutter! A thri-kreen's chatkcha, its blades of obsidian set in a crystal no kreen "
               "will name, and blessed by the clerics of the air. It flies truer and cuts deeper "
               "than any common chatkcha. The packs of the Gemfields pass it to their best hunter; "
               "take it, and they will remember you."),),
    # the Warden's Plate, a piece of its story each
    ARMOUR: (("Warden's Helm",
              "The Warden's Helm! In the Green Age the Wardens kept the iron roads between the "
              "cities, in plate from head to foot. The last of them, Haldren, held the pass below "
              "Draj alone for a day and a night; that helm kept his courage when nothing else "
              "could. Dagolar robbed his tomb for it. A coward's trophy: put it on, and fear "
              "slides off you."),
             ("Warden's Arms",
              "The Warden's Arms! Haldren's plate was parted when he died, so that no one lord "
              "could own it whole. The arm pieces went west with a caravan the Wyvern Master's "
              "bandits robbed. He hid them with his finest treasure, behind a wall only the "
              "Serpent Boots can find. True iron, and no stronger arms on Athas."),
             ("Warden's Legs",
              "The Warden's Legs! Haldren's leg pieces went to his squire, who fled east with "
              "them and died on the plateaus where the wagon trains cross; his chest is there "
              "still, and the magera have walked past it for years. Plate fit to march a thousand "
              "miles in, as Haldren marched it."),
             ("Warden's Chest",
              "The Warden's Chest! Haldren's breastplate was quenched in the heart of a fire "
              "elemental, and fire still flinches from whoever wears it. Balkazar kept it in his "
              "school, a prize he could never wear: it would not sit easy on a defiler. Find the "
              "other three pieces, and the Warden's Plate is whole again for the first time in a "
              "thousand years.")),
    # the magic shields
    SHIELDS: (("Gutterward",
               "Gutterward! Agafari planks bound in sinew and sealed with sewer pitch. A boss of the "
               "Draj warrens carried it before Churrr's time, until the Tari dragged him down into the "
               "drains, and it was never seen again. It turns a blow better than any common shield, "
               "and smells no worse than its last owner did."),
              ("Ironbulwark",
               "Ironbulwark! True iron, a whole shield of it, forged in the Green Age for a city's "
               "champion: its weight in metal would buy a village today. Balkazar set a Guardian "
               "over his school and armed it with this, and the Guardian never once set it down. "
               "Blows that would fell a mul glance from it. Few shields on Athas are its equal.")),
    # the Cloak and Boots of Elvenkind
    CLOTHES: (("Cloak of Elvenkind",
               "A Cloak of Elvenkind! The elves weave them of spider silk and songs, a "
               "tribe's work of a whole year, and give them only to their best runners. Hood "
               "up, its wearer all but vanishes: in the open no eye finds them, and under a "
               "roof hardly more. The Elven Leader must think a great deal of you."),
              ("Boots of Elvenkind",
               "Boots of Elvenkind! Soft as a kank's belly and silent on any ground, dry "
               "leaves and old floors alike. An elf thief of the caravan buried them with his "
               "loot, meaning to come back; he never did. Their wearer can walk up behind anyone "
               "unheard."),
              ("Bracers of Defense",
               "Bracers of Defense! A wizard can't wear armour and cast, so the clever ones wear "
               "these: steel cuffs that ward the whole body as armour would. The better the pair, "
               "the older it is; the best were made before the sorcerer-kings, and the wizards who "
               "have them guard them jealously, as you must have found."),
              ("Arrowbane",
               "Arrowbane! A silver circlet made for a merchant house's caravan master, who had "
               "grown tired of raiders' arrows. While it sits on the brow, no common arrow, sling "
               "stone or chatkcha can harm its wearer. Kel parted with it? He must need the coin "
               "more than he lets on."),
              ("Sunking Crown",
               "The Sunking Crown! It was taken from the tomb of a king who ruled before Draj was "
               "a city, and who claimed the sun's own favour. Its gold still keeps evil from its "
               "wearer. Keldar wore it in the dark of Dagolar's "
               "tunnels; much good it did him."),
              ("Ashen Robe",
               "An Ashen Robe! A preserver of the Veiled Alliance wore this once, woven to turn "
               "a blade and a spell alike. The defiler Kalzith took it from her, and the ash of "
               "all he drained has greyed it since. It is a preserver's robe still: wear it with "
               "a clearer conscience than he did."),
              ("Veiled Robe",
               "A robe of the Veiled Alliance! The preservers who hide from the templars wear "
               "these under their plain clothes. It wards its wearer, steadies the mind against "
               "magic, and holds more of a wizard's spells ready than the wizard alone could. "
               "Kel sells it? Then someone in the Alliance has fallen on hard times.")),
    OTHER: (("Tome of Understanding",
             "The Tome of Understanding! Father Garyn gave you this? Then he trusts you more than "
             "most. The water clerics of the villages kept such books from before the sorcerer-kings, "
             "when learning was not yet a crime. Whoever reads it sees more clearly, for good; then "
             "its pages fall blank, and it is only a book."),),
}


def kinds(arms: bool = True, magic: bool = True, script: int = SCRIPT, pens: bool = True) -> Tuple[Kind, ...]:
    """Each kind of the script's with the new items of the switches on."""
    out = []
    for kind in (SWORDS, WEAPONS, RINGS, ARMOUR, SHIELDS, CLOTHES, OTHER):
        if SCRIPT_OF[kind] != script:
            continue
        items = (ARMS.get(kind, ()) if arms else ()) + (PENS.get(kind, ()) if pens else ()) \
            + (MAGIC.get(kind, ()) if magic else ())
        if items:
            out.append(Kind(kind[0], kind[1], items))
    return tuple(out)


KINDS = kinds()


# (a menu line for items of more than one picture: icons.py's names)
PICTURES_OF = {"Ring of Protection": ("Ring of Protection +1", "Pehtucl's Ring of Protection +1"),
               "Cloak of Protection": ("Cloak of Protection +1",)}


def _pictures(name: str) -> List[int]:
    """The item's pictures of its own, as an item has them (negative): icons.py's, or the tome's
    object's."""
    if name == "Tome of Understanding":
        return [-TOME_OBJECT]
    return [icons.PICTURES[n] - 0x10000 for n in PICTURES_OF.get(name, (name,))]


def _picture(name: str) -> int:
    return _pictures(name)[0]


def _carried(name: str) -> tuple:
    """The party carries an item of the name's pictures (as the game's queries; of more than one,
    any of them: "or", as the game's own tests join queries)."""
    queries = [("op", gpl.Op(0, QUERY, [("n", PARTY), 77, 80, [(HAS_PICTURE, 4, ("n", p))]])) for p in _pictures(name)]
    if len(queries) == 1:
        return queries[0]
    out: list = []
    for q in queries:
        out += (["or"] if out else []) + ["(", q, ")"]
    return ("expr", out)


# A menu with more items than the script's locals hold (the game's six weapons, the loop's own, and
# the new ones) keeps the rest in the Loader's flags from FLAGS on (the game's run to 755, the
# Loader's own 756-783, a save keeps 808), set afresh each time the part starts, as the locals are.
# A slot: a local's number, or a flag's negated.
FLAGS = 784
FLAG_SET, FLAG_READ = 13, 141


def _read(slot: int) -> tuple:
    return ("var", LOCAL_READ, slot) if slot >= 0 else ("var", FLAG_READ, -slot)


def _set(slot: int) -> tuple:
    return ("var", LOCAL_SET, slot) if slot >= 0 else ("var", FLAG_SET, -slot)


def _zero(slots: List[int]) -> tuple:
    out: list = []
    for n in slots:
        out += (["and"] if out else []) + ["(", _read(n), "==", ("n", 0), ")"]
    return ("expr", out)


def _locals(expr) -> Optional[List[int]]:
    """The locals an "all of these are 0" test names, or None for another test."""
    if not (isinstance(expr, tuple) and expr[0] == "expr"):
        return None
    parts, out = expr[1], []
    for i in range(0, len(parts), 6):
        group = parts[i:i + 5]
        if len(group) != 5 or group[0] != "(" or group[2] != "==" or group[3] != ("n", 0) \
                or not (isinstance(group[1], tuple) and group[1][:2] == ("var", LOCAL_READ)):
            return None
        out.append(group[1][2])
    return out


def _sets(op) -> Optional[Tuple[int, int]]:
    """(local, picture) for a "local = the party carries an item with this picture" command."""
    if op.code != SET or len(op.args) != 2 or op.args[1][:2] != ("var", LOCAL_SET):
        return None
    value = op.args[0]
    if not (isinstance(value, tuple) and value[0] == "op" and value[1].code == QUERY):
        return None
    tests = value[1].args[3]
    if len(tests) != 1 or tests[0][0] != HAS_PICTURE or not isinstance(tests[0][2], tuple):
        return None
    return op.args[1][2], tests[0][2][1]


def _story_end(ops, start: int) -> int:
    """The index of the return (15h) ending the story starting at ops[START]."""
    return next(i for i in range(start, len(ops)) if ops[i].code == 0x15)


def _nothing(reply) -> bool:
    return reply["text"][0] == "str" and reply["text"][1].strip() == NOTHING.strip()


def told(kinds) -> Tuple[bytes, Dict[str, int]]:
    """A script of the kinds' new stories' lines (TOLD_IN), and where each item's part starts: a
    19h, then each story's lines and a 19h ending it (a call's return, as each part of the
    game's 212 and 213), and an exit after the last."""
    out, places = bytearray(gpl.encode_op((START, []))), {}
    for kind in kinds:
        for item, text in kind.items:
            places[item] = len(out)
            s = _Script()
            s.say(text)
            out += s.bytes(end=False) + gpl.encode_op((START, []))
    return bytes(out + gpl.encode_op((EXIT, []))), places


def with_items(script: bytes, field_types: bytes, kinds=KINDS, told_in: Optional[Tuple[int, Dict[str, int]]] = None,
               why: Optional[List[str]] = None) -> bytes:
    """SCRIPT (the game's) with each kind's new item (unchanged if it isn't as expected, or would be
    too long: the reason in WHY). TOLD_IN: (a script, each item's place in it) whose parts say the
    stories (told()), called from each story instead of its lines here."""
    def unchanged(reason: str) -> bytes:
        if why is not None:
            why.append(reason)
        return script
    if any(gpl.encode_expr(("str", f"  {item}")) in script for kind in kinds for item, _ in kind.items):
        return script  # (done already: the commands made jumps no longer decode)
    ops = gpl.decode(script, field_types)
    at_index = {op.at: i for i, op in enumerate(ops)}
    s = _Script()
    jumps: List[Tuple[int, str]] = []
    for k, kind in enumerate(kinds):
        # the kind's part: its "none carried" line, the tests for none just before it
        none = next((i for i, o in enumerate(ops) if o.code == SAY and o.args[1] == ("str", kind.none_text)), None)
        menu_i = next((i for i, o in enumerate(ops) if o.code == MENU and o.args[0]["replies"]
                       and o.args[0]["replies"][0]["text"] == ("str", kind.first_reply)), None)
        if none is None or menu_i is None or menu_i < 2:
            return unchanged(f"{kind.first_reply.strip()}'s part not found")
        first_test, held, chain = none, [], []
        while first_test >= 2 and ops[first_test - 1].code == 0x3E and ops[first_test - 2].code == TEST \
                and _locals(ops[first_test - 2].args[0]) is not None:
            first_test -= 2
            held = _locals(ops[first_test].args[0]) + held
            chain.insert(0, (_locals(ops[first_test].args[0]), ops[first_test + 1].args[0]))
        done = _locals(ops[menu_i - 2].args[0]) if ops[menu_i - 2].code == TEST else None
        if not held or not done or len(done) != 1:
            return unchanged(f"{kind.first_reply.strip()}'s part not as expected")
        done = done[0]
        # the new items' locals: after the menu's, past the loop's own
        menu = ops[menu_i].args[0]
        used = [r["if"][2] for r in menu["replies"] if isinstance(r["if"], tuple) and r["if"][:2] == ("var", LOCAL_READ)]
        mine = [n for n in range(max(used + held) + 1, LOCALS) if n != done][:len(kind.items)]
        mine += [-(FLAGS + i) for i in range(len(kind.items) - len(mine))]  # (past the locals: flags)
        all_of = held + mine
        entry = f"entry {k}"
        s.label(entry)
        for (item, _), n in zip(kind.items, mine):
            s.op(SET, _carried(item), _set(n))
        # the game's tests again, each to its own place (the game keeps its ifs and elses
        # nested: skipping one, an else further on goes the wrong way), the new items in the last
        for t, (names, target) in enumerate(chain):
            s.op(TEST, _zero(names + (mine if t == len(chain) - 1 else [])))
            s.op(0x3E, target)
        s.op(GOTO, ("n", ops[none].at))
        jumps.append((ops[first_test].at, entry))

        # the menu: the game's replies, then the new ones
        replies = list(menu["replies"])
        # (before the game's "Nothing", which leaves: it stays last)
        at = next((r for r, reply in enumerate(replies) if _nothing(reply)), len(replies))
        # (the new stories' test for none left, the kind's every local: one subroutine they call)
        s.sub(f"left {k}", lambda all_of=all_of, done=done: s.when(_zero(all_of), lambda: s.set(done, 1)))
        for j, ((item, text), n) in enumerate(zip(kind.items, mine)):
            story = f"story {k} {j}"
            if told_in is not None and item in told_in[1]:
                say = lambda item=item: s.op(CALL, ("n", told_in[1][item]), ("n", told_in[0]))
            else:
                say = lambda text=text: s.say(text)
            s.sub(story, lambda say=say, n=n, k=k: (say(), s.op(SET, ("n", 0), _set(n)), s.call(f"left {k}")))
            replies.insert(at + j, {"text": ("str", f"  {item}"), "goto": ("label", story),
                                    "if": _read(n), "before": [], "after": []})
        copy = f"menu {k}"
        s.label(copy)
        s.op(MENU, dict(menu, replies=replies))
        s.op(GOTO, ("n", ops[menu_i + 1].at))
        jumps.append((ops[menu_i].at, copy))

        # the game's stories: their test for none left counts the new items too
        for r, reply in enumerate(menu["replies"]):
            if _nothing(reply):
                continue
            start = at_index.get(reply["goto"][1]) if reply["goto"][0] == "n" else None
            if start is None:
                return unchanged(f"{kind.first_reply.strip()}'s story {r} not found")
            end = _story_end(ops, start)
            for t in range(start, end - 2):
                names = _locals(ops[t].args[0]) if ops[t].code == TEST else None
                if names is None or ops[t + 1].code != 0x3E or ops[t + 2].args != [("n", 1), ("var", LOCAL_SET, done)]:
                    continue
                left = f"left {k} {r}"
                s.label(left)
                s.op(TEST, _zero(names + mine))
                s.op(0x3E, ops[t + 1].args[0])  # (some left: past the end of the loop's flag)
                s.op(GOTO, ("n", ops[t + 2].at))
                jumps.append((ops[t].at, left))
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    if len(out) > LONGEST:
        return unchanged(f"{', '.join(k.first_reply.strip() for k in kinds)}: {len(out)} bytes, past the "
                         f"scripts' buffer ({LONGEST})")
    gpl.put_jumps(out, script, field_types, [(at, s.at[label]) for at, label in jumps])
    return bytes(out)


def _entry(script: bytes, field_types: bytes, kind: Kind) -> Optional[int]:
    """Where the kind's part of SCRIPT starts (after its 19h), as script 211 calls it."""
    ops = gpl.decode(script, field_types)
    none = next((i for i, o in enumerate(ops) if o.code == SAY and o.args[1] == ("str", kind.none_text)), None)
    start = next((j for j in range(none or 0, -1, -1) if ops[j].code == START), None) if none else None
    return ops[start + 1].at if start is not None else None


def _called_from(talk: bytes, field_types: bytes, entry: int, number: int, source: int = OTHER_SCRIPT) -> Optional[bytes]:
    """TALK with its call of SOURCE's ENTRY calling NUMBER's (None: no such call)."""
    old = gpl.encode_op((CALL, [("n", entry), ("n", source)]))
    new = gpl.encode_op((CALL, [("n", entry), ("n", number)]))
    calls = [o.at for o in gpl.decode(talk, field_types)
             if o.code == CALL and o.args == [("n", entry), ("n", source)]]
    if len(calls) != 1 or len(new) != len(old):
        return None
    out = bytearray(talk)
    out[calls[0]:calls[0] + len(new)] = new
    return bytes(out)


def script_chunks(chunks, field_types: bytes, arms: bool = True, magic: bool = True,
                  pens: bool = True) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of GPLDATA: Alagorn's talks (his two scripts, and the copies of 212:
    COPY_OF) with the magic items of the switches on (ARMS: Kreenfang and Shadowseeker; PENS:
    Inixhide and the rings and cloak of protection; MAGIC: the world's and the tome). A kind left
    out (its script too long, or not as expected) is logged and in LEFT_OUT, with why."""
    out: Dict[Tuple[str, int], bytes] = {}
    del LEFT_OUT[:]

    def left_out(chosen, reason: str) -> None:
        line = f"Alagorn's {', '.join(k.first_reply.strip() for k in chosen)} menu ({reason})"
        LEFT_OUT.append(line)
        _log.warning("left out: %s", line)
    for number in (SCRIPT, OTHER_SCRIPT):
        key = ("GPL ", number)
        if key not in chunks:
            continue
        groups: Dict[int, List[Kind]] = {}
        for kind in kinds(arms, magic, number, pens):
            first = (kind.first_reply, kind.none_text)
            groups.setdefault(COPY_OF.get(first, number), []).append(kind)
        for target, chosen in groups.items():
            stories, told_in = None, None
            if target in TOLD_IN:
                if ("GPL ", TOLD_IN[target]) in chunks:
                    left_out(chosen, f"script {TOLD_IN[target]} is the game's")
                    continue
                stories, places = told(chosen)
                told_in = (TOLD_IN[target], places)
                if len(stories) > LONGEST:
                    left_out(chosen, f"its stories' script, {len(stories)} bytes, past the buffer ({LONGEST})")
                    continue
            why: List[str] = []
            changed = with_items(chunks[key], field_types, tuple(chosen), told_in, why)
            if changed == chunks[key]:
                if why:
                    left_out(chosen, "; ".join(why))
                continue
            if target != number:
                if ("GPL ", target) in chunks:
                    left_out(chosen, f"script {target} is the game's")
                    continue
                if ("GPL ", TALK) not in chunks:
                    continue  # (no talk to call it: nothing to tell from)
                talk = out.get(("GPL ", TALK), chunks[("GPL ", TALK)])
                for kind in chosen:
                    entry = _entry(chunks[key], field_types, kind)
                    talk = _called_from(talk, field_types, entry, target, number) if entry is not None and talk else None
                if not talk:
                    left_out(chosen, f"his talk ({TALK}) doesn't call the part as expected")
                    continue
                out[("GPL ", TALK)] = talk
            out[("GPL ", target)] = changed
            if stories is not None:
                out[("GPL ", TOLD_IN[target])] = stories
    return out


# What Alagorn says of two of the game's items, as they are (the user's decision, 2026-11-09): his
# story of the Quicksilver Glove (the game's name; his menus said "Quicksilver Gauntlets") had it
# graft a weapon to the hand, which nothing does: it casts Detonate on whoever it hits (its +0Fh,
# 139); the Helm of Contemplation's, a shield of thought against psionic attacks: it is Gaze
# Reflection (+0Fh 7). Each story's lines (SAY 4Fh, one a screen line) and each menu reply naming
# the glove are run from after the script's end, the old ones jumped over: script 212 and the
# copies of it Alagorn's parts run from (COPY_OF), the old bytes after the jump made exits (as
# scriptfixes' repairs, so the script still reads as commands). Always, as the Loader's other repairs of the
# game's scripts (scriptfixes.py).
MENU_OP, JUMP_OP, EXIT_OP = 0x48, 0x64, 0x31
STORIES = {
    "Wearing a Helm of Contemplation creates a shield of thought around you, ": (
        ("Wearing a Helm of Contemplation creates a shield of thought around you, ",
         "protecting you against all psionic attacks."),
        ("Wearing a Helm of Contemplation turns a creature's gaze back on itself.",)),
    "Quicksilver Gauntlets allow you to graft any one-handed melee weapon to ": (
        ("Quicksilver Gauntlets allow you to graft any one-handed melee weapon to ",
         "your body. The weapon becomes easier to use and does more damage ",
         "than normal."),
        ("The Quicksilver Glove holds a psionic charge. Whatever it strikes is ",
         "blasted from within, and the blast can shatter what the foe wears.")),
}
REPLIES = {"  Quicksilver Gauntlets": "  Quicksilver Glove"}


def retold(script: bytes, field_types: bytes) -> bytes:
    """SCRIPT with STORIES' lines and REPLIES' menu replies as they should read (as it is if it has
    none of them, or would be too long)."""
    import copy
    ops = gpl.decode(script, field_types)
    out, added = bytearray(script), bytearray()
    for i, o in enumerate(ops):
        detour, end = None, None
        if o.code == SAY and len(o.args) == 2 and o.args[1][0] == "str" and o.args[1][1] in STORIES:
            old, new = STORIES[o.args[1][1]]
            said = [ops[i + k] for k in range(len(old))] if i + len(old) < len(ops) else []
            if [p.code for p in said] != [SAY] * len(old) or [p.args[1] for p in said] != [("str", t) for t in old]:
                continue
            end = ops[i + len(old)].at
            detour = b"".join(gpl.encode_op((SAY, [o.args[0], ("str", t)])) for t in new)
        elif o.code == MENU_OP and any(r["text"] in (("str", t) for t in REPLIES) for r in o.args[0]["replies"]):
            menu = copy.deepcopy(o.args[0])
            for r in menu["replies"]:
                if r["text"][0] == "str" and r["text"][1] in REPLIES:
                    r["text"] = ("str", REPLIES[r["text"][1]])
            end = ops[i + 1].at if i + 1 < len(ops) else len(script)
            detour = gpl.encode_op((MENU_OP, [menu]))
        if detour is None or end - o.at < 3:
            continue
        if not added:
            added.append(EXIT_OP)  # (a script that ran off its end still stops there)
        start = len(script) + len(added)
        added += detour + bytes((JUMP_OP,)) + end.to_bytes(2, "big")
        out[o.at:end] = (bytes((JUMP_OP,)) + start.to_bytes(2, "big")).ljust(end - o.at, bytes((EXIT_OP,)))
    if not added or len(out) + len(added) > LONGEST:
        return script
    return bytes(out + added)


def retold_chunks(chunks, field_types: bytes, out: Dict[Tuple[str, int], bytes]) -> Dict[Tuple[str, int], bytes]:
    """Script 212 and its copies (from OUT, the Loader's changes so far, or else CHUNKS) retold."""
    changed: Dict[Tuple[str, int], bytes] = {}
    for number in sorted({OTHER_SCRIPT, *COPY_OF.values()}):
        key = ("GPL ", number)
        code = out.get(key, chunks.get(key))
        if code is not None:
            new = retold(code, field_types)
            if new != code:
                changed[key] = new
    return changed
