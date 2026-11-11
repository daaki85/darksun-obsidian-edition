"""Selling a party member's plain gear in one go (the user's ask, 2026-11-11, after looting: S).

On a shop's screen, S sells everything plain in the backpack of the party member on show: a
weapon (melee, missile or thrown), armour, a shield, or anything worn (a cloak, boots, a belt, a
helm), with no plus and no magical power. What is worn or held is never sold, nor ammunition or
anything of metal (the user's choices), anything magic, keys, scrolls, food, water, gems, or what the shop won't buy (a
price of 9999).

DSCLOG's SELL_KEY makes the key Escape, which shuts the shop (back to its merchant's talk), and
counts it (SELL_SEQ, header +1852) with the member on show (SELL_MEMBER, +1854: the game's
3931h:25Bh) and the merchant (+1856, DS:179Ch); SHOP_AT (+1858) is the BIOS tick of the shop's
loop's last pass. Once the shop is shut, the dice log calls sell(): each thing is paid for as the
game's shop pays (83CCAh on): its price (+06h), times its count (+02h) when its type stacks (the
type's +0Fh bit 2), 60% of the price with Shops as in AD&D (prices.sell_price, DSCLOG's
SELL_PRICE), added to the party's money; and freed, as the game frees what it buys (ring.unlink).
The dice log says what went and for how much, with the purse's sound."""

import struct
from typing import Dict, List, Tuple

from . import game, itemgate, pickpocket, prices, restrict, ring
from .game import GameData

TSR_SELL_SEQ, TSR_SELL_MEMBER, TSR_SELL_MERCHANT, TSR_SHOP_AT = 1852, 1854, 1856, 1858  # (DSCLOG's header)
BIOS_TICK = 0x46C
SHOP_FRESH = 2  # (DSCLOG's: the shop's screen up while its loop ran this recently)
NOT_FOR_SALE = 9999
STACKS = 0x02  # (a type's +0Fh: a stack, its count at the item's +02h)
COUNT = 0x02
VALUE = 0x06
GEAR = restrict.MELEE | restrict.MISSILE | restrict.SHIELD | restrict.THROWN
WORN_AT = 0x09
AMMUNITION = 11  # (a type's worn place, +09h: the quiver's; arrows, bolts, sling stones: never sold, the user's choice)


def bios_tick(gd: GameData) -> int:
    return struct.unpack("<H", gd.guest.read(BIOS_TICK, 2))[0]


def shop_up(gd: GameData, tsr_hdr: int) -> bool:
    at, = struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_SHOP_AT, 2))
    now = bios_tick(gd)
    return at != 0 and (now - at) & 0xFFFF <= SHOP_FRESH


def plain_gear(gd: GameData, rec: bytes) -> bool:
    """Gear (a weapon, armour, a shield, anything worn; not ammunition or metal) with no plus and no power,
    that the shop would buy; not a key."""
    if struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] >= game.NO_ITEM:
        return False
    typ = gd.item_type_record(rec)
    if len(typ) < game.ITEM_TYPE_SIZE:
        return False
    if typ[WORN_AT] == AMMUNITION or restrict.material(typ) == restrict.METAL:
        return False  # (ammunition, and metal, rare and dear on Athas: kept, the user's choices)
    gear = typ[restrict.TYPE_FLAGS] & GEAR or typ[restrict.TYPE_KIND_FLAGS] & restrict.ARMOUR or typ[WORN_AT]
    plus = struct.unpack_from("b", rec, game.ITEM_PLUS)[0]
    value = struct.unpack_from("<H", rec, VALUE)[0]
    name = gd.item_name(struct.unpack_from("<H", rec, game.ITEM_NAME)[0]).lower()
    return bool(gear) and plus == 0 and rec[game.ITEM_POWER] == 0 and 0 < value < NOT_FOR_SALE \
        and "key" not in name


def price(gd: GameData, rec: bytes) -> int:
    """What the shop pays for REC, as the game's (and DSCLOG's SELL_PRICE) works it out."""
    value = struct.unpack_from("<H", rec, VALUE)[0]
    if gd.rules & game.RULE_CHA_PRICES:  # (Shops as in AD&D)
        value = prices.sell_price(value)
    typ = gd.item_type_record(rec)
    if len(typ) > restrict.TYPE_KIND_FLAGS and typ[restrict.TYPE_KIND_FLAGS] & STACKS:
        value *= struct.unpack_from("<H", rec, COUNT)[0]  # (as stored, as the game's 83D6Bh)
    return value


def sell(gd: GameData, member: int) -> Tuple[List[str], int]:
    """Party member MEMBER's plain gear in its backpack sold: the dice log's lines and the money."""
    if not 0 <= member < game.PARTY_SIZE:
        return [], 0
    it = ring.Items(gd)
    thing, = struct.unpack_from("<h", gd.creature(member), pickpocket.PACK_LIST)
    goods = [(i, rec) for i, rec in it.chain(thing, inside=False)
             if rec[game.ITEM_SLOT] in pickpocket.BACKPACK and plain_gear(gd, rec)]
    if not goods:
        return [f"{gd.creature_name(member)} has no plain gear in the backpack to sell."], 0
    itemgate.hold(gd)  # (the game busy with its lists: ItemsBusy, in a later pass)
    sold: Dict[str, List[int]] = {}  # name: [how many, paid]
    total = 0
    for item, rec in goods:
        paid = price(gd, rec)
        name = gd.item_label(rec, gd.item_type_record(rec))
        if ring.unlink(gd, ring.Items(gd), item, f"sold: {name}", empty=True):
            entry = sold.setdefault(name, [0, 0])
            entry[0] += 1
            entry[1] += paid
            total += paid
    if total:
        gd.add_money(total)
    who, count = gd.creature_name(member), sum(n for n, _ in sold.values())
    listed = ", ".join(f"{name} x{n} {paid}" if n > 1 else f"{name} {paid}" for name, (n, paid) in sold.items())
    return [f"{who} sells {count} things for {total} ceramic pieces: {listed}"], total
