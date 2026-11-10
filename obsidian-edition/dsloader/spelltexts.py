"""Descriptions the game reads from RESOURCE.GFF (SPIN chunks) for what the mod adds: the new
spells' (SPIN the spell's number + 1, as the game's own: 197-202 the wizard spells', 203-212 the
6th-level priest spells') and, in Turn Undead's box (SPIN 1000),
the purse's and the spell arrows' (1001-1005: DSCLOG's PROBE_CHUNK_ID asks for 999 + TU_INFO in
1000's place), and Slay Living's (137) put right; with the spells as the manual has them
(MANUAL_TEXTS), those whose game text no longer says what they do (Fire Shield's, Strength's, Ironskin's...) and Cat's Grace's as they then work; with the creature size rule (SIZE_TEXTS), Hold and Charm Person's. They were DSCLOG's own text once; in the Loader's copy of RESOURCE.GFF they take
no room in the helper. Each is under 195 bytes (the box reads it into 200, from its 5th byte)."""

from typing import Dict, Tuple

TU_SPIN = 1000  # Turn Undead's description (DSCLOG's TU_SPIN)
PICK_SPIN = TU_SPIN + 1  # the purse's (TU_INFO_PICK 2), then the four spell arrows' (3-6)

TEXTS: Dict[int, str] = {
    197: "CAT'S GRACE:  Raises the target's dexterity by 1 to 6 pts. Maximum dexterity is 24.",
    # (seven lines fill the box: an eighth spills over its bottom edge)
    # (Body Weaponry's or Animal Affinity's dice: "a psionic power's")
    198: "ERDLU CLAW:  Erdlu talons: unarmed attacks (not a thri-kreen's bite) do 1d6+1 (or +1 to a psionic "
         "power's dice), +1 to hit, as a +1 weapon. Lasts 5 rounds per level.",
    199: "FOGBOLT:  A bolt of fog clings to one creature: -3 to hit and Armor Class 2 worse for "
         "2 to 8 rounds. A saving throw negates it.",
    200: "REFLECTED IMAGE:  An image of the caster moves with it: an attack may strike the "
         "image instead, which then vanishes. Mirror Image takes its place.",
    201: "SPOOK:  One creature flees in fear for 3 rounds. Its saving throw is 1 worse for each "
         "2 caster levels (up to 6). Undead are not affected.",
    202: "FRIENDS:  The caster's charisma rises by 2d4 (to 25 at most) for 1d4 rounds and 1 "
         "per level.",
    # Slay Living's own text says 3 to 17 (the book's 2d8+1): the game does half of 4d8
    137: "SLAY LIVING:  Kills one target. If the target makes its save it suffers 2 to 16 pts of "
         "damage.",
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
    209: "HEARTSEEKER:  Slays one target unless it saves versus death. If it saves, it suffers "
         "2 to 16 pts of damage.",
    210: "WATER OF LIFE:  Heals a target's wounds by passing them to the caster, who keeps at "
         "least 5 hit points.",
    211: "WHIRLWIND:  Inflicts 2 to 16 pts of damage a round on creatures in it, half on a save; "
         "those failing lose a turn. Lasts 1 round per level. Blocks missiles.",
    212: "RESTORE YOUTH:  Takes back 1 year of magical aging per level of caster, never below "
         "the target's true age. The target must survive a system shock.",
    PICK_SPIN: "PICK POCKETS:  The next person clicked on has their pockets tried by this thief. "
               "If it fails, the thief tries to slip away unseen. Not in a fight.",
    # (the arrows' too: seven lines fill the box)
    PICK_SPIN + 1: "BURNING ARROWS:  Weaves Burning Hands into 5 arrows a level in the empty quiver, for a 1st-level slot; each "
                   "casts it on what it hits. Gone at a rest. Not in a fight.",
    PICK_SPIN + 2: "CHILL ARROWS:  Weaves Chill Touch into 5 arrows a level in the empty quiver, for a 1st-level slot; each "
                   "casts it on what it hits. Gone at a rest. Not in a fight.",
    PICK_SPIN + 3: "SHOCKING ARROWS:  Weaves Shocking Grasp into 5 arrows a level in the empty quiver, for a 1st-level slot; each "
                   "casts it on what it hits. Gone at a rest. Not in a fight.",
    PICK_SPIN + 4: "VAMPIRIC ARROWS:  Weaves Vampiric Touch into 5 arrows a level in the empty quiver, for a 3rd-level slot; each "
                   "casts it on what it hits. Gone at a rest. Not in a fight.",
}


# With "Spells and psionics as the manual describes them" (gamepatch.SPELLS_MANUAL): Fire Shield's +2 on
# saves (DSCLOG's FSHIELD_SITE; the half damage and the returned blow are the game's), Cat's Grace's
# dice by class (STRENGTH_SITE)
MANUAL_TEXTS: Dict[int, str] = {
    # (seven lines fill the box: seen in the game, 2026-11-09)
    45: "FIRE SHIELD:  Attackers who hit the caster in melee take the same damage. The caster takes "
        "half damage from fire and cold spells and saves against them at +2.",
    197: "CAT'S GRACE:  Raises the target's dexterity: rogues 1 to 8 pts, warriors, wizards and "
         "psionicists 1 to 6, priests 1 to 4. Maximum dexterity is 24.",
    # the game's texts that no longer say what the spells do (2026-11-10: the rest already said what
    # the manual has, which the game's code didn't do: Stinking Cloud, Hold Undead, Minute Meteors...)
    24: "STRENGTH:  Raises the target's strength: warriors 1 to 8 pts, priests, rogues and "
        "psionicists 1 to 6, wizards 1 to 4. Maximum strength is 24.",
    134: "IRONSKIN:  The recipient's skin stops one blow of a weapon, fang, claw or hurled "
         "projectile for each level of the caster. Magic attacks have normal effects.",
    118: "FREE ACTION:  Frees the recipient from slow, hold person and paralysis, and from being "
         "held fast by web, solid fog, quicksand, entangle or grease.",
    52: "SOLID FOG:  A thick fog holds creatures caught in it fast for 1 to 3 rounds plus 1 per "
        "level of caster.",
    49: "MINOR SPELL TURNING:  For 3 rounds per level of caster, 1st, 2nd and 3rd level spells "
        "directed at the caster reflect back and affect the casting opponent.",
    105: "BESTOW CURSE:  Bestows a -4 penalty to attacks & saves on one creature unless it saves. "
         "Can be reversed with dispel magic or remove curse.",
    109: "BLOOD FLOW:  Heals 2 to 12 pts of damage. If used to injure, the target is stunned for "
         "up to 4 rounds unless it saves.",
    57: "CHAOS:  Affects 1 to 4 creatures plus 1 per caster level: only warriors and the very "
        "clever or very dull may save. They may stand confused, go berserk, or flee.",
    29: "FLAME ARROW:  One arrow for every 5 levels of caster, each aimed on its own: 1 to 6 pts "
        "of damage plus 4 to 24 pts of fire damage.",
    152: "CELL ADJUSTMENT:  Heals 1 to 4 pts of damage and cures diseases.",
}

# With "Creature size as in AD&D" (game.RULE_SIZE): the person spells don't take on a large target
SIZE_TEXTS: Dict[int, str] = {
    31: "HOLD PERSON:  May paralyze targets of character types (human, dwarf, etc.) no bigger than "
        "man-sized: not half-giants. You can aim at up to 4 targets.",
    87: "HOLD PERSON:  Holds human, demi-human or humanoid creatures no bigger than man-sized "
        "(not half-giants) unable to move. Lasts longer as the caster rises in level.",
    3: "CHARM PERSON:  Changes the target's allegiance in combat. Affects only character types "
       "(human, dwarf, etc.) no bigger than man-sized: not half-giants.",
    83: "CHARM PERSON OR MAMMAL:  Changes target's allegiance in combat. A person must be no "
        "bigger than man-sized (not a half-giant); any mammal may be charmed.",
}


def chunks(manual: bool = False, size: bool = False) -> Dict[Tuple[str, int], bytes]:
    """The SPIN chunks, in the game's form: the text and CR LF (MANUAL: with the spells as the manual
    has them, MANUAL_TEXTS' in their places; SIZE: with the creature size rule, SIZE_TEXTS')."""
    texts = {**TEXTS, **(MANUAL_TEXTS if manual else {}), **(SIZE_TEXTS if size else {})}
    return {("SPIN", n): text.encode("ascii") + b"\r\n" for n, text in texts.items()}
