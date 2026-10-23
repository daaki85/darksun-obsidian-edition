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
    203: "HEAL:  Cures all damage, disease and blindness of one target.",
    204: "HARM:  Leaves one target with only 1 to 4 hit points. No saving throw.",
    205: "BLADE BARRIER:  Creates a wall of whirling blades. Inflicts 8 to 64 pts of damage on "
         "creatures in or passing through it, unless they save.",
    206: "WALL OF THORNS:  Creates a wall of thorns. Inflicts 8 pts plus the target's AC in damage "
         "on creatures in or passing through it.",
    207: "SUNSTROKE:  Paralyzes one target for 2 rounds per level of caster unless it saves, "
         "burning it for 1 to 4 pts of fire damage each round.",
    208: "FIRE SEEDS:  Inflicts 8 to 64 pts of fire damage on creatures within its area of effect. "
         "A successful save halves the damage.",
    209: "HEARTSEEKER:  Slays one target unless it saves versus death.",
    210: "WATER OF LIFE:  Heals a target's wounds by passing them to the caster, who keeps at "
         "least 5 hit points.",
    211: "WHIRLWIND:  Inflicts 2 to 16 pts of damage a round on creatures in it, half on a save; "
         "those failing lose a turn. Lasts 1 round per level. Blocks missiles.",
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
