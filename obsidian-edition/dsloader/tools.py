"""Thieving tools: an item earlier versions of the Loader gave (Mirlon's set, Kel's pair), which
picked pockets when used on someone. A thief's Pick Pockets button does that now (pickpocket.py),
and no one is given the tools; a set already in a game keeps its name and picture, and does
nothing. The item is a small one of the game's "misc" type. Its name, "Thieves' Tools", is the
second of the entries DSCLOG adds after the game's own (names.py); the tools are told apart by
that name, their picture and their type together.
"""

import struct

from . import game, ring
from .game import GameData

NAME_ENTRY = 0x143
NAME = b"Thieves' Tools"
OLD_NAME_ENTRIES = (0xAD, 0x60)  # what earlier versions named them (the pickaxe's "pick", then the
# rest button's "Rest icon"): renamed
NEW_GAME = 3600  # game seconds: a game this young, in the arena, has just started
ARENA = 0x2A  # the region every game starts in
PICTURE, TYPE = 0xFBD4, 60  # the tools' picture (a leather satchel); small things carried (weight 1, worn nowhere)
OLD_PICTURES = (0x8AB0,)  # what earlier versions gave them (a Slavepen key's): changed to PICTURE
PICTURE_CACHE = 0x0C  # in an item: the game keeps the picture it loaded here (0: load it again)
# a Slavepen key's record, as the game has it, with that name and picture, not in a slot
ITEM = struct.pack("<HH", PICTURE, 0) + bytes.fromhex("0f27" "0100" "0f27") + struct.pack("<H", TYPE) + \
    bytes.fromhex("00000000" "05" "ff") + struct.pack("<Hb", NAME_ENTRY, 0)


def is_tools(rec: bytes) -> bool:
    return len(rec) == game.ITEM_SIZE \
        and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] in (NAME_ENTRY,) + OLD_NAME_ENTRIES \
        and struct.unpack_from("<H", rec, 0)[0] in (PICTURE,) + OLD_PICTURES \
        and struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == TYPE


def repaint(gd: GameData) -> None:
    """Tools an earlier version gave get today's name entry and picture (the game's cache of
    the picture it loaded cleared, so it loads the new one)."""
    it = ring.Items(gd)
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE:
            continue
        for offset in game.CREATURE_ITEM_LISTS:
            thing, = struct.unpack_from("<h", rec, offset)
            for item, data in it.chain(thing):
                if not is_tools(data):
                    continue
                at = it.items + item * game.ITEM_SIZE
                if struct.unpack_from("<H", data, game.ITEM_NAME)[0] != NAME_ENTRY:
                    gd.guest.write(at + game.ITEM_NAME, struct.pack("<H", NAME_ENTRY))
                if struct.unpack_from("<H", data, 0)[0] != PICTURE:
                    gd.guest.write(at, struct.pack("<H", PICTURE))
                    gd.guest.write(at + PICTURE_CACHE, bytes(2))


def new_game(gd: GameData) -> bool:
    now = gd.game_time()
    return gd.region() == ARENA and now is not None and now < NEW_GAME
