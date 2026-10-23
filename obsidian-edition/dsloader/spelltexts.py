"""Descriptions the game reads from RESOURCE.GFF (SPIN chunks) for what the mod adds: the new
spells' (SPIN the spell's number + 1, as the game's own: 197-202 the wizard spells', 203-211 the
6th-level priest spells') and, in Turn Undead's box (SPIN 1000),
the purse's and the spell arrows' (1001-1005: DSCLOG's PROBE_CHUNK_ID asks for 999 + TU_INFO in
1000's place). They were DSCLOG's own text once; in the Loader's copy of RESOURCE.GFF they take
no room in the helper. Each is under 195 bytes (the box reads it into 200, from its 5th byte)."""

from typing import Dict, Tuple

TU_SPIN = 1000  # Turn Undead's description (DSCLOG's TU_SPIN)
PICK_SPIN = TU_SPIN + 1  # the purse's (TU_INFO_PICK 2), then the four spell arrows' (3-6)

TEXTS: Dict[int, str] = {
    197: "CAT'S GRACE:  Raises the target's dexterity by 1 to 6 pts. Maximum dexterity is 24.",
    198: "ERDLU CLAW:  Erdlu talons: unarmed attacks do 1d6+1 (or +1 to Body Weaponry's or "
         "Animal Affinity's dice), +1 to hit, as a +1 weapon. Lasts 5 rounds per level.",
    199: "FOGBOLT:  A bolt of fog clings to one creature: -3 to hit and Armor Class 2 worse for "
         "2 to 8 rounds. A saving throw negates it.",
    200: "REFLECTED IMAGE:  An image of the caster moves with it: an attack may strike the "
         "image instead, which then vanishes. Mirror Image takes its place.",
    201: "SPOOK:  One creature flees in fear for 3 rounds. Its saving throw is 1 worse for each "
         "2 caster levels (up to 6). Undead are not affected.",
    202: "FRIENDS:  The caster's charisma rises by 2d4 (to 25 at most) for 1d4 rounds and 1 "
         "per level.",
    203: "HEAL:  A touch cures every wound. Cosmos, 6th level.",
    204: "HARM:  A touch leaves a creature 1d4 hit points, and diseased. No saving throw. Cosmos, 6th level.",
    205: "BLADE BARRIER:  A wall of whirling blades: 8d8 to any creature in it or passing through. "
         "Cosmos, 6th level.",
    206: "WALL OF THORNS:  A wall of tangled thorns: 1d10 + 8 to any creature in it or pushing "
         "through. Cosmos, 6th level.",
    207: "SUNSTROKE:  Beams of searing sunlight: each creature chosen that fails its saving throw "
         "collapses, helpless, for 2 rounds per level. Cosmos, 6th level.",
    208: "FIRE SEEDS:  Four seeds of fire hurled together: 8d8 where they burst, a saving throw for "
         "half. Fire, 6th level.",
    209: "HEARTSEEKER:  An arrow of living wood seeks the heart: the creature it strikes must save "
         "against death or die. Earth and water, 6th level.",
    210: "WATER OF LIFE:  A touch heals a creature's wounds by taking them onto the caster, who keeps "
         "5 hit points. Water, 6th level.",
    211: "WHIRLWIND:  A whirlwind tears through an area: 2d8, a saving throw for half. Air, 6th level.",
    PICK_SPIN: "PICK POCKETS:  The next person clicked on has their pockets tried by this thief. "
               "If it fails, the thief tries to slip away unseen. Not in a fight.",
    PICK_SPIN + 1: "BURNING ARROWS:  Weaves Burning Hands into 5 arrows per level, using a 1st-level slot. "
                   "Each casts it on what it hits. They fade at the next rest. Not in a fight.",
    PICK_SPIN + 2: "CHILL ARROWS:  Weaves Chill Touch into 5 arrows per level, using a 1st-level slot. "
                   "Each casts it on what it hits. They fade at the next rest. Not in a fight.",
    PICK_SPIN + 3: "SHOCKING ARROWS:  Weaves Shocking Grasp into 5 arrows per level, using a 1st-level slot. "
                   "Each casts it on what it hits. They fade at the next rest. Not in a fight.",
    PICK_SPIN + 4: "VAMPIRIC ARROWS:  Weaves Vampiric Touch into 5 arrows per level, using a 3rd-level slot. "
                   "Each casts it on what it hits. They fade at the next rest. Not in a fight.",
}


def chunks() -> Dict[Tuple[str, int], bytes]:
    """The SPIN chunks, in the game's form: the text and CR LF."""
    return {("SPIN", n): text.encode("ascii") + b"\r\n" for n, text in TEXTS.items()}
