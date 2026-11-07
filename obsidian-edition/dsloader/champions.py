"""The champions' bout: once a party member has killed Scar, the arena's next bout is against
champions from a distant arena come to test the new king of the pens, led by a Tohr-kreen with
Kreenfang (the arena's gythka +1, no longer on the dead body by the stone arch).

- The team: six people of the arena's own kinds, each an object of its own (a copy of the kind's,
  OBJECTS, so the others of the kind stay as they are), named "Champion", with gear of its own in
  its record: the Tohr-kreen (the arena's, 292) with Kreenfang; a half-giant (the arena's Guard,
  293) with a metal great axe, a leather shield and full scale armour and a bone helm; a mul
  gladiator (the Wild Mul, 290) with two bone axes and the same armour; a halfling renegade (the
  Renegade, 289) with a sling, a bone short sword, full leather armour, a leather helm and a
  leather shield; an elven ranger (an elven caravan guard, 103) with a bow and arrows, an obsidian
  long sword and the same leather, helm and shield (the Tohr-kreen and the defiler wear none); a
  defiler (the arena's, 296) with a bone dagger and one scroll, chosen as it comes on, of
  Fogbolt, Spook or Reflected Image (the new spells; without them, of the game's own spells).
- Worn and wielded: the game makes a person's items in its backpack list (+0Ch), puts them on at
  its first action in a fight (people.py does it as it comes on the map), and fights with
  what is in its held list (+0Ah: seen, a Tohr-kreen given Headsman there attacked with it, 1d10+2,
  in place of its first two natural attacks) and counts the worn list's armour (+08h) for its AC,
  so the Loader moves each champion's gear to its place as it comes on (Gear.watch), as the
  inventory screen would. Their sheets keep their kinds' AC, the armour counting on top.
- Killed, the Tohr-kreen leaves a body of its own: the game makes a Dead Body (object 1101) for
  a creature that dies carrying something (DSUN.EXE 59412h, "push 0FFFF044Dh"); DSCLOG's
  PROBE_WORN takes that push (gamepatch's champion_body) and names BODY instead when the dying
  creature is the Tohr-kreen champion: a dead Tohr-kreen's picture (a copy of 1101's object and
  record, its own picture drawn from the Tohr-kreen's), Kreenfang and the rest in it as the
  game puts them.
- The bout (the arena's scripts, script_chunks): where the arena's death handler (script 3 at
  176h, hooked on Scar only in the arena: MAS 42, script 2, and script 154 for region 2Ah) says
  "This makes ... king of the pens!", KING is set too (Scar killed in the pens, script 144, sets
  the game's flag 19 alone: no bout); the arena's sixth visit (the visit count, the
  game's number 12, at 5: the one after Scar's), with KING set and FOUGHT not, has the
  Announcer's speech (SPEECH) and the six in place of the game's wave, and sets FOUGHT: once.
"""

import random
import struct
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import dataitems, game, gpl, itemgate, kalzith, npcitems, pickpocket, ring

# Objects of the Loader's own (2563 is never one: worldgear.NOT_AN_OBJECT)
TOHR_KREEN, HALF_GIANT, MUL, HALFLING, ELF, DEFILER = range(2660, 2666)
BODY = 2666  # the Tohr-kreen champion's body (its object, and its picture's number)
OBJECTS = (TOHR_KREEN, HALF_GIANT, MUL, HALFLING, ELF, DEFILER)
DEAD_BODY = 1101  # the game's Dead Body (an item, a container: what the game makes for the dead)
NAME = "Champion"
KING, FOUGHT = 759, 807  # flags: a party member killed Scar; the champions have been fought

# (the kind each is a copy of)
BASES = {TOHR_KREEN: 292, HALF_GIANT: 293, MUL: 290, HALFLING: 289, ELF: 103, DEFILER: 296}

# slots (game.EQUIP_SLOTS)
ARM, AMMO, MISSILE, RIGHT, LEGS, HEAD, CHEST, LEFT = 0, 1, 2, 3, 6, 7, 9, 10

# the game's item types used
SHIELD_TYPE, LEATHER_CHEST, SCALE_CHEST, SCALE_ARM, SCALE_LEGS = 0x04, 0x06, 0x0F, 0x37, 0x38
LEATHER_ARM, LEATHER_LEGS, LEATHER_HELM, BONE_HELM = 0x07, 0x08, 0x05, game.BONE_HELM_TYPE
# the game's plain leather Helm (its first of the type is Dapartea's Helm, named: not that)
HELM = npcitems._item("03fc000000000500000005000000000004ff060000")
BOW_TYPE, ARROWS_TYPE, SLING_TYPE, LONG_SWORD_TYPE = 0x01, 0x3E, 0x40, 0x2D
BONE_SHORT_SWORD_TYPE, BONE_DAGGER_TYPE = game.BONE_SHORT_SWORD_TYPE, game.BONE_DAGGER_TYPE

SCROLL_SPELLS = (game.FOG_SPELL, game.SPOOK_SPELL, game.REFLECT_SPELL)

SHEET_RECORD = 4  # (an RDFF's character sheet: its record of that type)
CREATURE_OBJECT = 0x06  # (a creature record's object, negated)
SEEN = 128  # creature records looked at (as defilerscrolls.SEEN)
DEAD_STATUS = kalzith.DEAD_STATUS


def game_item(chunks, kind: int) -> Optional[bytes]:
    """The first plain item of the game's of item type KIND (in its objects' records)."""
    for (ckind, _), data in sorted(chunks.items()):
        if ckind != "RDFF":
            continue
        try:
            items = dataitems.items_of(data)
        except ValueError:
            continue
        for rec in items:
            if len(rec) == game.ITEM_SIZE and struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == kind \
                    and rec[game.ITEM_PLUS] == 0 and rec[game.ITEM_POWER] == 0:
                return rec
    return None


def gear(chunks) -> Dict[int, List[Tuple[bytes, int]]]:
    """Each champion's items, as (item record, the slot it is worn or held in)."""
    from . import arms, bonescale, worldgear
    item = lambda kind: game_item(chunks, kind)
    gythka = item(game.GYTHKA_TYPE)
    out = {
        TOHR_KREEN: [(arms.magic(gythka, arms.GYTHKA_VALUE, arms.GYTHKA_NAME) if gythka else None, RIGHT)],
        HALF_GIANT: [(worldgear.weapon(worldgear.METAL_GREAT_AXE), RIGHT), (item(SHIELD_TYPE), LEFT),
                     (item(SCALE_CHEST), CHEST), (item(SCALE_ARM), ARM), (item(SCALE_LEGS), LEGS),
                     (bonescale.HELM, HEAD)],
        MUL: [(worldgear.weapon(worldgear.BONE_AXE), RIGHT), (worldgear.weapon(worldgear.BONE_AXE), LEFT),
              (item(SCALE_CHEST), CHEST), (item(SCALE_ARM), ARM), (item(SCALE_LEGS), LEGS),
              (bonescale.HELM, HEAD)],
        HALFLING: [(item(SLING_TYPE), MISSILE), (worldgear.weapon(worldgear.BONE_SHORT_SWORD), RIGHT),
                   (item(LEATHER_CHEST), CHEST), (item(LEATHER_ARM), ARM), (item(LEATHER_LEGS), LEGS),
                   (HELM, HEAD), (item(SHIELD_TYPE), LEFT)],
        ELF: [(item(BOW_TYPE), MISSILE), (item(ARROWS_TYPE), AMMO), (item(LONG_SWORD_TYPE), RIGHT),
              (item(LEATHER_CHEST), CHEST), (item(LEATHER_ARM), ARM), (item(LEATHER_LEGS), LEGS),
              (HELM, HEAD), (item(SHIELD_TYPE), LEFT)],
        DEFILER: [(worldgear.weapon(worldgear.BONE_DAGGER), RIGHT)],
    }
    missing = [obj for obj, items in out.items() if any(rec is None for rec, _ in items)]
    if missing:
        raise KeyError(f"no item of the game's for champions {missing}")
    return out


def _without_items(rdff: bytes) -> bytes:
    """An object's record with its own items (and theirs) taken out: the person alone."""
    recs, end = dataitems.records(rdff)
    first = next((i for i, r in enumerate(recs) if r.kind == dataitems.ITEM and r.level == dataitems.FIRST), len(recs))
    return dataitems.chunk(recs[:first], end)


DEX = {TOHR_KREEN: 18, HALF_GIANT: 15, ELF: 18, DEFILER: 18}  # (the mul and the halfling keep their kinds' 18)


def _with_dex(rdff: bytes, dex: int) -> bytes:
    """An object's record with its person's DEX made DEX: in its creature record (+22h on, the
    AC adjustment's) and its sheet (+1Bh on)."""
    recs, end = dataitems.records(rdff)
    recs = list(recs)
    for i, r in enumerate(recs):
        at = {2: game.CREATURE_ABILITIES, SHEET_RECORD: game.SHEET_ABILITIES}.get(r.kind)
        if at is not None and len(r.data) > at + 1 and r.level in (1, 3):
            data = bytearray(r.data)
            data[at + 1] = dex
            recs[i] = r._replace(data=bytes(data))
    return dataitems.chunk(recs, end)


def _named(rdff: bytes, name: str) -> bytes:
    out = bytearray(rdff)
    field = 16  # (the creature record's name: 15 letters and its end)
    at = kalzith.RDFF_NAME
    out[at:at + field] = name.encode("ascii")[:field - 1].ljust(field, b"\0")
    return bytes(out)


def body_picture(chunks) -> bytes:
    """The dead Tohr-kreen's picture (a BMP chunk of one frame): a frame of the Tohr-kreen's laid
    on its side, darkened, over the blood of the game's Dead Body (bodyart.py)."""
    from . import bodyart
    return bodyart.picture(chunks)


def object_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the six champions' objects and the Tohr-kreen's body
    (raises KeyError if a number is taken or an item of the game's is missing)."""
    for obj in OBJECTS + (BODY,):
        if any((kind, obj) in chunks for kind in ("OJFF", "RDFF", "BMP ")):
            raise KeyError(f"object {obj} taken")
    things = gear(chunks)
    numbers = dataitems.numbers(chunks)
    out: Dict[Tuple[str, int], bytes] = {}
    for obj in OBJECTS:
        base = BASES[obj]
        rdff = _named(dataitems.renumbered(_without_items(chunks[("RDFF", base)]), obj), NAME)
        if obj in DEX:
            rdff = _with_dex(rdff, DEX[obj])
        out[("RDFF", obj)] = dataitems.with_items(rdff, [rec for rec, _ in things[obj]], numbers)
        out[("OJFF", obj)] = chunks[("OJFF", base)]
    body = bytearray(chunks[("OJFF", DEAD_BODY)])
    struct.pack_into("<H", body, kalzith.OJFF_PICTURE, BODY)
    out[("OJFF", BODY)] = bytes(body)
    out[("RDFF", BODY)] = dataitems.renumbered(chunks[("RDFF", DEAD_BODY)], BODY)
    out[("BMP ", BODY)] = body_picture(chunks)
    return out


# ---------------------------------------------------------------------------------------------
# In the fight: each champion's gear to its place, and the defiler's scroll

# the slot each champion's item goes to, by item type (the two axes: the first the right hand)
SLOTS: Dict[int, Sequence[Tuple[int, int]]] = {
    TOHR_KREEN: ((game.GYTHKA_TYPE, RIGHT),),
    HALF_GIANT: ((game.METAL_GREAT_AXE_TYPE, RIGHT), (SHIELD_TYPE, LEFT), (SCALE_CHEST, CHEST),
                 (SCALE_ARM, ARM), (SCALE_LEGS, LEGS), (BONE_HELM, HEAD)),
    MUL: ((game.BONE_AXE_TYPE, RIGHT), (game.BONE_AXE_TYPE, LEFT), (SCALE_CHEST, CHEST), (SCALE_ARM, ARM),
          (SCALE_LEGS, LEGS), (BONE_HELM, HEAD)),
    HALFLING: ((SLING_TYPE, MISSILE), (BONE_SHORT_SWORD_TYPE, RIGHT), (LEATHER_CHEST, CHEST),
               (LEATHER_ARM, ARM), (LEATHER_LEGS, LEGS), (LEATHER_HELM, HEAD), (SHIELD_TYPE, LEFT)),
    ELF: ((BOW_TYPE, MISSILE), (ARROWS_TYPE, AMMO), (LONG_SWORD_TYPE, RIGHT), (LEATHER_CHEST, CHEST),
          (LEATHER_ARM, ARM), (LEATHER_LEGS, LEGS), (LEATHER_HELM, HEAD), (SHIELD_TYPE, LEFT)),
    DEFILER: ((BONE_DAGGER_TYPE, RIGHT),),
}


def champion_of(rec: bytes) -> Optional[int]:
    """The champion object of a creature record, or None."""
    if len(rec) < CREATURE_OBJECT + 2:
        return None
    obj = -struct.unpack_from("<h", rec, CREATURE_OBJECT)[0]
    return obj if obj in OBJECTS else None


class Gear:
    """Puts each champion's gear where it is worn or held as it comes on, once."""

    def __init__(self):
        self.done: set = set()  # (creature, name, object) equipped, while in the arena

    def reset(self) -> None:
        """Forget who was equipped (a game loaded: its champions are made again)."""
        self.done.clear()

    def watch(self, gd, new_spells: bool = True, choose: Optional[Callable[[Sequence[int]], int]] = None) -> List[str]:
        if gd.region() != ARENA:
            self.done.clear()
            return []
        choose = choose or random.choice
        table = gd.creatures(SEEN)
        size = game.CREATURE_SIZE
        for index in range(game.PARTY_SIZE, len(table) // size):
            rec = table[index * size:(index + 1) * size]
            obj = champion_of(rec)
            if obj is None:
                continue
            name = rec[game.CREATURE_NAME:game.CREATURE_NAME + 16].split(b"\0", 1)[0]
            key = (index, name, obj)
            if key in self.done and not self._unplaced(gd, index, obj):
                continue
            if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in DEAD_STATUS:
                continue
            itemgate.hold(gd)
            self.equip(gd, index, obj, new_spells, choose)
            self.done.add(key)
        return []

    @staticmethod
    def _unplaced(gd, index: int, obj: int) -> bool:
        """Something of champion INDEX's gear still in its backpack (a game loaded from before it
        was put on, under the same creature and name)."""
        kinds = {kind for kind, _ in SLOTS.get(obj, ())}
        pack, = struct.unpack_from("<h", gd.creature(index), game.CREATURE_ITEM_LISTS[2])
        return any(struct.unpack_from("<H", data, game.ITEM_TYPE)[0] in kinds
                   for _, data in ring.Items(gd).chain(pack, inside=False))

    @staticmethod
    def equip(gd, index: int, obj: int, new_spells: bool, choose) -> None:
        """Champion INDEX's items (in its backpack, as the game makes them) each to its slot; the
        defiler's scroll given first (into the backpack, while it has one), if it has none.
        Nothing moved that is in place already."""
        if obj == DEFILER:
            from . import defilerscrolls
            has = any(defilerscrolls.is_ours(data) for offset in game.CREATURE_ITEM_LISTS
                      for _, data in ring.Items(gd).chain(struct.unpack_from("<h", gd.creature(index), offset)[0]))
            if not has:
                pool = [s for s in SCROLL_SPELLS if 1 <= gd.spell_level(s) <= 5] if new_spells else []
                pool = pool or defilerscrolls.spells(gd.spell_level, False)
                if pool:
                    spell = choose(pool)
                    npcitems.add_to(gd, index, defilerscrolls.scroll(spell, gd.spell_level(spell)))
        it = ring.Items(gd)
        rec = gd.creature(index)
        pack, = struct.unpack_from("<h", rec, game.CREATURE_ITEM_LISTS[2])
        taken = {data[game.ITEM_SLOT] for offset in game.CREATURE_ITEM_LISTS[:2]
                 for _, data in it.chain(struct.unpack_from("<h", rec, offset)[0], inside=False)}
        wanted = [(kind, slot) for kind, slot in SLOTS.get(obj, ()) if slot not in taken]
        moves = []
        for item, data in it.chain(pack, inside=False):
            kind = struct.unpack_from("<H", data, game.ITEM_TYPE)[0]
            at = next((i for i, (k, _) in enumerate(wanted) if k == kind), None)
            if at is not None:
                moves.append((item, wanted.pop(at)[1]))
        for item, slot in moves:
            pickpocket.place(gd, index, item, slot)


ARENA = 0x2A


# ---------------------------------------------------------------------------------------------
# The arena's scripts

ARENA_SCRIPT, DEATHS_SCRIPT = 2, 3  # the arena's visits and waves; its creatures' deaths
INTRO_AT, INTRO_END = 0xAD4, 0xB50  # (script 2) a visit's opening, past the numbered visits: its
# first line ("Once again, expectant spectators..."), and where its part ends
WAVE_CALL, RANDOM_WAVES = 0x1581, 6320  # (script 2) the call to the wave maker of the visits past
# the fifth (the count over 4), and that wave maker
GROUP_SUB = 9301  # (script 2) puts a group in: object op 1Eh(LOCAL 12), LOCAL 13 of them, at LOCALS 9, 10
KING_AT = 0x3A7  # (script 3) "set flag 19", after "This makes ... king of the pens!"
VISITS, VISIT_PAST_SCAR = ("var", 0x87, 12), 5  # the game's visit count; the one after Scar's
GOTO, SAY, SET, INC, CALL, RETURN = 0x64, 0x4F, 0x16, 0x06, 0x13, 0x15
OBJ_OF = 0x1E  # (the expression op the game's waves name their kind with)

SPEECH = ("Citizens of Draj! Scar is dead, and the pens have a new king. But word travels fast "
          "across the sands. From a distant arena come champions who have never known defeat, and "
          "they have come to see if the new king is worthy of the crown. Their leader, a "
          "Tohr-kreen, carries a gythka that has drunk the blood of a hundred gladiators.")


def _flag(flag: int, value: int = 1) -> list:
    return ["(", ("var", 0x8D, flag), "==", ("n", value), ")"]


def _due() -> tuple:
    """The champions' bout is due: past Scar's visit, a party member killed him, not yet fought."""
    return ("expr", ["(", VISITS, ">=", ("n", VISIT_PAST_SCAR), ")", "and"] + _flag(KING) + ["and"]
            + _flag(FOUGHT, 0))


FILL = gpl.FILL  # (what is left of a command made a jump: never run, decoded)


def _put(out: bytearray, at: int, length: int, op) -> None:
    """OP over the command of LENGTH bytes at AT, the rest filled (so the script still decodes)."""
    code = gpl.encode_op(op)
    out[at:at + length] = code + bytes((FILL,)) * (length - len(code))


def _op_at(ops, at: int, code: int):
    op = next((o for o in ops if o.at == at), None)
    if op is None or op.code != code:
        return None, None
    after = next((o for o in ops if o.at > at), None)
    return op, after


def with_bout(script: bytes, field_types: bytes = b"") -> bytes:
    """The arena's script 2 with the champions' bout: the opening of a visit past the fifth says
    SPEECH while the bout is due (_due), else the game's; the call to that visit's wave maker
    goes to a part of ours that puts the six in (each a group of one, as the game's waves do) and
    sets FOUGHT while it is due, else calls the game's. Unchanged if either place isn't what it
    should be."""
    from .kalzith import _Script
    try:
        ops = gpl.decode(script, field_types)
    except gpl.ScriptError:
        return script
    intro, _ = _op_at(ops, INTRO_AT, SAY)
    call, after_call = _op_at(ops, WAVE_CALL, CALL)
    if intro is None or call is None or call.args != [("n", RANDOM_WAVES)]:
        return script
    first_lines = [o for o in ops if INTRO_AT <= o.at < INTRO_END]
    if not all(o.code == SAY for o in first_lines):
        return script

    s = _Script()
    s.label("intro")
    s.when(_due(), lambda: s.say(SPEECH), lambda: [s.op(o.code, *o.args) for o in first_lines])
    s.op(GOTO, ("n", INTRO_END))

    def champions():
        for obj in OBJECTS:
            s.op(SET, ("op", gpl.Op(0, OBJ_OF, [("n", -obj)])), ("var", 2, 12))
            s.op(SET, ("n", 1), ("var", 2, 13))
            s.op(INC, ("var", 0x82, 11))
            s.op(CALL, ("n", GROUP_SUB))
        s.flag(FOUGHT, 1)

    s.label("waves")
    s.when(_due(), champions, lambda: s.op(CALL, ("n", RANDOM_WAVES)))
    s.op(RETURN)
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    _put(out, INTRO_AT, INTRO_END - INTRO_AT, (GOTO, [("n", s.at["intro"])]))
    _put(out, WAVE_CALL, len(gpl.encode_op(call)), (CALL, [("n", s.at["waves"])]))
    return bytes(out) if len(out) <= _longest() else script


def with_king(script: bytes, field_types: bytes = b"") -> bytes:
    """The arena's deaths (script 3) with KING set where a party member's killing Scar sets the
    game's flag 19 ("This makes ... king of the pens!"): that command becomes a jump past the
    script's end, where it is done, then KING set, then a jump back. Unchanged if KING_AT isn't
    that command."""
    from .kalzith import _Script
    try:
        ops = gpl.decode(script, field_types)
    except gpl.ScriptError:
        return script
    op, after = _op_at(ops, KING_AT, SET)
    if op is None or after is None or op.args != [("n", 1), ("var", 13, 19)]:
        return script
    s = _Script()
    s.op(op.code, *op.args)
    s.flag(KING, 1)
    s.op(GOTO, ("n", after.at))
    out = bytearray(script) + s.bytes(base=len(script), end=False)
    _put(out, KING_AT, after.at - KING_AT, (GOTO, [("n", len(script))]))
    return bytes(out) if len(out) <= _longest() else script


def _longest() -> int:
    from .pensasks import LONGEST  # (the longest script the game's buffer takes, as the Loader has it)
    return LONGEST


def script_chunks(chunks, field_types: bytes, out) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of GPLDATA: the arena's scripts with the bout (on OUT's changes)."""
    new: Dict[Tuple[str, int], bytes] = {}
    for number, change in ((ARENA_SCRIPT, with_bout), (DEATHS_SCRIPT, with_king)):
        key = ("GPL ", number)
        if key in chunks:
            was = out.get(key, chunks[key])
            changed = change(was, field_types)
            if changed != was:
                new[key] = changed
    return new
