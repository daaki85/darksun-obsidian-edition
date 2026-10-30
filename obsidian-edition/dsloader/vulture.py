"""The cooked vulture: a meal at last.

Hitting the arena's vulture knocks its feathers off (a plucked vulture), and the slave pens'
campfire cooks it, but nothing in the game ever uses the cooked vulture. With the Loader, Dinos
(the pens' fine cook) is asked about it in his talk while the party carries it ("We cooked the
vulture from the arena.", pensasks.py): he takes it, shows them how to prepare it properly and
they eat it together, with the sound of a quest done. His script sets the Loader's flag MEAL, on
which the Loader gives each party member XP_REWARD XP and restores them as after a full rest (HP,
PSP and spell slots), once (EATEN).
"""

import struct
from typing import List

from . import game
from .game import GameData

COOKED = 0xA4C  # (its object, as the campfire's script makes it)
MEAL, EATEN = 780, 781  # (the Loader's flags) set by Dinos's script; the reward given
XP_REWARD = 100
PENS, DINOS = 0x29, "Dinos"  # where he is (RGN29), and his name
SHEET_MAX_PSP = 0x0C
STATUS_DEAD = 5
DOWN = (2, 3, 4)  # Stunned, Out Cold, Dying: up again after the meal

MEAL_TEXT = ("A vulture! Give it here. A pinch of salt, some agafari leaf, slow over the coals... "
             "Sit down and eat with me. A meal like this puts the strength back in you.")


def _party(gd: GameData) -> List[int]:
    """The party members there are, alive."""
    out = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) >= game.CREATURE_SIZE and rec[game.CREATURE_NAME] and rec[game.CREATURE_STATUS] != STATUS_DEAD:
            out.append(member)
    return out


def rest(gd: GameData, member: int) -> None:
    """As after a full rest: HP and PSP to their most, the spell slots full (as the game fills
    them), up again if down."""
    at = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + member * game.CREATURE_SIZE
    sheet = gd.sheet(member)
    hp, psp = struct.unpack_from("<hh", sheet, game.SHEET_MAX_HP)[0], struct.unpack_from("<h", sheet, SHEET_MAX_PSP)[0]
    gd.guest.write(at, struct.pack("<hh", hp, max(psp, 0)))
    if gd.creature(member)[game.CREATURE_STATUS] in DOWN:
        gd.guest.write(at + game.CREATURE_STATUS, bytes([game.STATUS_OKAY]))
    for kind_name, bit in game.MAGIC_KINDS:
        slots = bytes(min(255, gd.max_spell_slots(member, bit, level)) for level in range(1, game.SPELL_LEVELS + 1))
        gd.guest.write(gd.ds * 16 + game.SLOTS_LEFT[kind_name] + member * game.SLOTS_STRIDE + 1, slots)


def eat(gd: GameData) -> List[str]:
    """Each party member there is, alive: a full rest (the XP is given by the game). For the dice log."""
    party = _party(gd)
    for member in party:  # (the XP is the game's, given by Dinos's script)
        rest(gd, member)
    names = ", ".join(gd.creature_name(m) for m in party)
    return [f"Dinos cooks the vulture and the party eats with him: {names} restored as after a full "
            f"rest (HP, PSP and spell slots); the game gives each {XP_REWARD} XP (split among a "
            "multi-class character's classes)"]


def meal(gd: GameData) -> List[str]:
    """Once Dinos's script has set MEAL: the reward, once (EATEN). Only while the party is talking
    with him in the pens (where his script sets it): while a game is loading, the flags' memory
    can hold anything for a moment."""
    if not gd.flag(MEAL) or gd.flag(EATEN):
        return []
    if gd.region() != PENS or gd.talk_target() != DINOS:
        return []
    gd.set_flag(EATEN)
    return eat(gd)
