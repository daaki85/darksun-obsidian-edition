"""The rest of the bone scale armour, in the chest with its chest piece.

The game has Bone Scale Chest Armor, Arm Armor and Leg Armor (objects 1033-1035, the arm and leg
pieces never placed anywhere in play) but no helm of bone. It puts the chest piece in a chest of
the slave pens (object 1564, with Arrows +3). In the Loader's copy of SEGOBJEX the arm and leg
pieces and a Bone Helm (an item type of the Loader's own: the Helm's, of bone, with an icon of
its own in the bone scale's colours, icons.py) are in that chest too (dataitems.py, worldgear.py's
data_chunks), so the game makes the set together.
"""

import struct
from typing import Optional

from . import game, npcitems

CHEST_OBJECT = 1564  # the slave pens' chest with the chest piece
CHEST_PICTURE, CHEST_TYPE = 0xFBF7, 15  # Bone Scale Chest Armor (object 1033)
HELM_NAME = 6  # "Helm" (the game shows the material before it: "Bone Helm")
# the game's own records (SEGOBJEX), in no list and no slot
ARM = npcitems._item("f6fb000000003000000037000000000005ff260100")  # Bone Scale Arm Armor
LEG = npcitems._item("f5fb000000003000000038000000000005ff270100")  # Bone Scale Leg Armor
# the leather Helm's, of the Loader's bone helm type (its picture the Helm's until icons.py
# gives it its own)
HELM = npcitems._item("03fc000000000500000005000000000004ff060000", type_=game.BONE_HELM_TYPE, name=HELM_NAME)
PIECES = (ARM, LEG, HELM)
NAMES = {ARM: "Bone Scale Arm Armor", LEG: "Bone Scale Leg Armor", HELM: "Bone Helm"}


def which_piece(rec: bytes) -> Optional[bytes]:
    """Which of the three REC is (ARM, LEG, HELM), or None."""
    if len(rec) < game.ITEM_SIZE:
        return None
    if struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == game.BONE_HELM_TYPE:
        return HELM
    return {0xFBF6: ARM, 0xFBF5: LEG}.get(struct.unpack_from("<H", rec, 0)[0])
