"""Wake of the Ravager's quests, for the Journal tab (quests.py's table for the sequel).

The sequel keeps a story's progress as Shattered Lands does: global flags (a bit each at the far
pointer DS:15F2h, SAVE chunk 30, 101 bytes) and global numbers (words at DS:15F6h, SAVE chunk 31),
and rewards a deed through script 27's routines (at 112 for each party member, at 148 for one
person, the amount in global number 3: questdraft.SEQUEL) or with an award of its own. This is the
sequel's table of those deeds, read from its scripts (`python -m dsloader.questdraft` on its
GPLDATA.GFF) and the walkthrough, and written in the project's own words: nothing here is the
game's text. quests.py's rules hold (a quest FINISHED by a `done` condition or its `reward`'s
message, OPEN by a `given` one); the Loader's layout for the sequel (ravlog.apply_layout) puts this
table in quests.QUESTS while the sequel runs.

Most of the sequel's quests are seen only once finished: their `given` conditions (what opens
them) are a later step (RAVAGER.md's "Not in the sequel yet"). tests/test_ravquests.py holds the
table to the game's scripts (DSUN_WOTR).
"""

from typing import Dict, Tuple

from .quests import F, HIGH, MEDIUM, N, Quest, Reward

SAVE_FLAGS, SAVE_NUMBERS = ("SAVE", 30), ("SAVE", 31)

# The sequel's regions a reward is told apart by (ravlog.REGIONS: the Veiled Alliance, the yuan-ti
# tunnels, the clouds)
ALLIANCE, TUNNELS, CLOUDS = 0x33, 0x36, 0x42

HUMBLETON, THE_JANN, ISLANDS = "Humbleton forest", "The jann tribe", "The silt sea islands"
UNDERDARK, VOLCANO = "The underdark", "The volcano"

QUESTS: Tuple[Quest, ...] = (
    # ---- Tyr (region 32h) ----
    Quest("arslan", "Arslan's errand", "Tyr",
          "Arslan read the proof the party brought him and took their side.",
          "Arslan offered his help in return for an errand.",
          given=(F(337),), done=(F(341),), sites=((131, 4900), (131, 3702))),
    Quest("fayina", "Fayina's debt", "Tyr",
          "Acar let Fayina off her debt once Boric agreed to his terms.",
          done=(F(324),), sites=((128, 7890),)),
    Quest("kalak-statue", "The way into Kalak's pyramid", "Tyr",
          "The stone medallion opened Kalak's statue and the stairs beneath it.",
          "A stone medallion turned up in a bookcase. It must fit something in the city.",
          given=(F(381),), done=(F(361),), sites=((146, 1935), (137, 1695))),
    Quest("elemental-wards", "The elemental wards", "Tyr",
          "The wards keyed to the elements were passed.",
          done=(F(360),), sites=((137, 319),)),
    Quest("tavern-chest", "The chest in Zhur's tavern", "Tyr",
          "A trap door was found inside the locked chest in Zhur's tavern.",
          done=(F(362),), sites=((137, 2535),)),
    # ---- the Veiled Alliance (region 33h) ----
    Quest("romila", "Romila's pursuers", "The Veiled Alliance",
          "The templars and Draxans hunting Romila through the headquarters were slain.",
          reward=Reward((ALLIANCE,), 10000, True), confidence=MEDIUM, sites=((162, 907),)),
    Quest("hidden-door", "A hidden door in the headquarters", "The Veiled Alliance",
          "A secret door was found in the Veiled Alliance's headquarters.",
          done=(F(393),), sites=((185, 1933),)),
    # ---- Kalak's pyramid (region 34h) ----
    Quest("garden-mistress", "The Mistress of the Garden", "Kalak's pyramid",
          "The Mistress of the Garden was slain and its magic broke loose.",
          done=(F(188),), sites=((322, 298), (322, 311))),
    # ---- under Tyr (region 45h) ----
    Quest("trapped-villager", "The villager in the rubble", "Under Tyr",
          "The villager trapped under the rubble was led back to safety.",
          "A villager was dug out of the rubble and asked to be led to safety.",
          given=(F(730),), done=(F(734),), sites=((324, 2605), (324, 3824))),
    # ---- the mosaic (region 3Ch) ----
    Quest("chandelier", "The Chandelier of Ancestry", "The mosaic",
          "The Chandelier of Ancestry was made whole again.",
          done=(F(279),), sites=((99, 2206),)),
    Quest("mosaic-puzzle", "A puzzle of the mosaic", "The mosaic",
          "A puzzle in the mosaic was solved.",
          done=(F(278),), sites=((98, 1632),)),
    Quest("quarrelling-wizards", "The quarrelling wizards", "The mosaic",
          "Quelles thanked the party for its help; her quarrel with Hiuwar is put off for now.",
          done=(F(285),), sites=((109, 379), (109, 384), (109, 389))),
    # ---- the jann (region 3Bh) ----
    Quest("sultans-cart", "The Sultan's cart", THE_JANN,
          "A tapestry was found among the goods in the Sultan's cart.",
          done=(F(180),), sites=((74, 2944), (74, 3006))),
    Quest("jann-saved", "The jann in peril", THE_JANN,
          "The jann were saved from the peril that threatened them for ever.",
          done=(F(178),), sites=((110, 1184), (110, 1189), (110, 1194), (110, 1199), (110, 1204),
                                 (110, 1209), (110, 1214))),
    # ---- Humbleton forest (region 1) ----
    Quest("dariya-root", "Hudgerun root for Dariya", HUMBLETON,
          "Dariya was brought the hudgerun root she asked for.",
          done=(F(94),), sites=((32, 1014),)),
    Quest("obelisk-tracks", "Tracks by the obelisk", HUMBLETON,
          "A ranger found tracks in the dirt by the ruined obelisk.",
          done=(F(92),), sites=((39, 100),)),
    Quest("ptar-key", "The sleeping giant's key", HUMBLETON,
          "The key to Magnolia's chains was taken from the giant Ptar.",
          done=(F(131),), sites=((47, 1155),)),
    Quest("yuanti-hunt", "The yuan-ti hunt", HUMBLETON,
          "A yuan-ti war party was hunted down in the forest with a halfling's help.",
          done=(F(109),), sites=((35, 4983),)),
    Quest("humbleton-hostages", "Humbleton's hostages", HUMBLETON,
          "The yuan-ti holding Humbleton's halflings were destroyed and the hostages set free.",
          done=(F(113),), sites=((37, 501), (37, 506), (37, 511))),
    Quest("dmitri", "Word for the Veiled Alliance", HUMBLETON,
          "Dariya's son Dmitri agreed to carry word to the Veiled Alliance in Tyr.",
          done=(F(104),), sites=((34, 1556),)),
    # ---- the yuan-ti tunnels (region 36h) ----
    Quest("wall-tracks", "Tracks under the wall", "The yuan-ti tunnels",
          "Halfling-sized tracks were found leading under the tunnels' north wall.",
          done=(F(530),), sites=((236, 2913),)),
    Quest("tunnel-halflings", "The halflings in the tunnels", "The yuan-ti tunnels",
          "The halflings held in the yuan-ti tunnels were led out to freedom.",
          reward=Reward((TUNNELS,), 30000, True), confidence=MEDIUM, sites=((238, 4126),)),
    # ---- El's temple (region 37h) ----
    # (126 is 2 once she agrees, set in the talk the reward ends)
    Quest("surrakina", "Surrakina's bargain", "El's temple",
          "Surrakina's warriors agreed to strike the yuan-ti beside the party, for their share of the plunder.",
          done=(N(126, 2),), confidence=MEDIUM, sites=((254, 3752),)),
    Quest("temple-prisoners", "The prisoners of El's temple", "El's temple",
          "The halfling prisoners slipped away from El's temple and went home to Humbleton.",
          done=(F(138),), sites=((245, 1579), (245, 2223))),
    # ---- the mines and the underdark (regions 38h-3Ah) ----
    Quest("flayer-prisoner", "The mind flayers' prisoner", UNDERDARK,
          "A prisoner was freed from the mind flayers' device.",
          done=(F(224),), sites=((86, 4270),)),
    Quest("flayer-lab", "The mind flayers' laboratory", UNDERDARK,
          "A chest in the mind flayers' laboratory gave up a key and a vial of gas.",
          done=(F(226),), sites=((87, 3768),)),
    Quest("flayer-chemicals", "A vial changed", UNDERDARK,
          "A vial on the mind flayers' racks was swapped for another.",
          done=(F(231),), sites=((87, 4498),)),
    Quest("gas-vial", "The gas vial", UNDERDARK,
          "The vial of gas was thrown into the mind flayers' doorway and they staggered out dazed.",
          done=(F(248),), sites=((91, 2995), (91, 3000))),
    Quest("yiss", "Gamemaster Yiss", UNDERDARK,
          "Gamemaster Yiss was killed in his arena.",
          done=(F(274),), sites=((95, 1200),)),
    Quest("elder-brain", "The Elder Brain", UNDERDARK,
          "The Elder Brain was destroyed and the last mind flayers fled into the deep, away from Tyr.",
          done=(F(253),), sites=((91, 5102), (91, 5115))),
    # ---- the silt sea islands (region 41h) ----
    Quest("giants-field", "The giants' field", ISLANDS,
          "The giants' field was sprayed and the crop saved.",
          done=(F(306),), sites=((119, 2352),)),
    Quest("drake-armour", "Armour of drake hide", ISLANDS,
          "Velden the smith made a suit of armour from an air drake's hide.",
          done=(F(312),), sites=((120, 673),)),
    Quest("generoe-treasure", "Generoe's treasure", ISLANDS,
          "Generoe's buried treasure was dug up.",
          done=(F(598),), sites=((264, 293),)),
    Quest("acolyte", "The captive acolyte", ISLANDS,
          "An acolyte held captive on the islands was set free.",
          done=(F(584),), sites=((264, 1545),)),
    Quest("beastheads", "The beasthead giants' thanks", ISLANDS,
          "The beasthead giants rewarded the party for its service to all of Athas.",
          done=(F(588),), sites=((260, 1999),)),
    # ---- the clouds (region 42h) ----
    Quest("cloud-plank", "A bridge of planks", "The clouds",
          "A plank was pried loose by Melanthea's hut to bridge the gap.",
          reward=Reward((CLOUDS,), 3000, True), confidence=MEDIUM, sites=((1, 1189),)),
    Quest("cloud-rod", "The rod and the switch", "The clouds",
          "A rod was set in its slot and the switch beside it thrown.",
          done=(F(6),), sites=((1, 1767),)),
    Quest("wind-flute", "The two halves of the flute", "The clouds",
          "The two halves of the flute were joined.",
          done=(F(2),), sites=((1, 4547),)),
    Quest("drake-flute", "The flute and the drakes", "The clouds",
          "The flute's shriek drove the air drakes from their nest, and the flute shattered.",
          reward=Reward((CLOUDS,), 30000, True), confidence=MEDIUM, sites=((1, 486),)),
    Quest("sunken-rocks", "The sinking rocks", "The clouds",
          "Something stepped on in the clouds sank great rocks into the ground.",
          reward=Reward((CLOUDS,), 15000, True), confidence=MEDIUM, sites=((1, 4145),)),
    Quest("helmine", "The drakes' nest", "The clouds",
          "Helmine was freed from the air drakes' nest.",
          done=(F(5),), sites=tuple((1, at) for at in range(1487, 1548, 5))),
    # ---- the volcano (regions 3Dh-3Fh) ----
    Quest("prosser", "Prosser and the elementals", VOLCANO,
          "Prosser was rescued from the elementals that had him cornered.",
          done=(F(483),), sites=((233, 334),)),
)

# The rewards of script 27's routines the table leaves out, and why: (GPL script, offset).
_SMALL_FIND = "a small find or skill check for one person, no deed of a quest, and no flag is kept"
_TALK_CHECK = "a Charisma check in talk, which can be tried again and again"
_UNKNOWN = "no flag beside it, and what earns it was not established"
_NO_AMOUNT = "no amount is set before the call, so the journal can't know its message, and no flag is kept"
LEFT_OUT: Dict[Tuple[int, int], str] = {
    (1, 639): "the flute played badly: it shatters for 5,000, the same deed as the drakes driven off (GPL 1 at 486)",
    (9, 4290): _SMALL_FIND, (9, 4586): _SMALL_FIND,
    (16, 1147): "a staff found in a sarcophagus (flag 53): a find, no deed of a quest",
    (18, 2712): "a trip wire disabled (Jumah's warning): a trap, not a quest's deed",
    (18, 2824): "a trip wire found in a niche: a trap, not a quest's deed",
    (18, 3046): _SMALL_FIND,
    (20, 618): "a rune lit by one of the four elements: a step of a puzzle whose end has no flag",
    (20, 1370): "a rune lit by one of the four elements: a step of a puzzle whose end has no flag",
    (30, 4020): _UNKNOWN, (31, 3821): "Cleave revived with the flask: 5,000 for the party in Humbleton, as freeing Magnolia gives, and no flag is kept",
    (33, 206): "Dariya's last word: 10,000 for the party in the forest, as the hostages' thanks gives, and no flag is kept",
    (35, 569): _UNKNOWN,
    (38, 1373): _SMALL_FIND, (38, 2385): _SMALL_FIND, (38, 3258): _SMALL_FIND, (38, 3920): _SMALL_FIND,
    (40, 97): "what was paid for Magnolia's release, the amount the money given (number 3 set beforehand)",
    (40, 981): "Magnolia freed: 5,000 for the party in the forest, as reviving Cleave gives, and no flag is kept",
    (40, 6823): "Magnolia freed, the leader's share: 2,000 for one person in the forest, as the giant's key gives",
    (45, 2451): _UNKNOWN, (46, 492): "a branch the script says it never reaches (no amount)",
    (49, 232): _UNKNOWN,
    (51, 6744): "Humbleton's thanks: told by its message alone it could be the payment for Magnolia (GPL 40 at 97, any amount)",
    (51, 6439): "the hostages' thanks: 10,000 for the party in the forest, as Dariya's last word gives, and no flag is kept",
    (54, 8127): _NO_AMOUNT, (56, 89): _NO_AMOUNT,
    (56, 2620): "the bell rung: 3,000 for the party with the jann, as the Sultan's cart gives, and no flag is kept",
    (63, 1371): _SMALL_FIND, (63, 1560): _SMALL_FIND,
    (63, 2271): "a merchant's pay for hides: the amount goes by how many were brought, and no flag is kept",
    (63, 2281): "a merchant's pay for hides: the amount goes by how many were brought, and no flag is kept",
    (63, 2291): "a merchant's pay for hides: the amount goes by how many were brought, and no flag is kept",
    (65, 4154): _TALK_CHECK, (65, 7010): _TALK_CHECK, (65, 7191): _TALK_CHECK, (68, 2917): _TALK_CHECK,
    (69, 134): _TALK_CHECK, (69, 1846): _TALK_CHECK, (69, 2470): _TALK_CHECK,
    (72, 3844): "the tapestry handed in for mending: its flags (31, 93) are cleared by other scripts",
    (72, 4864): "the mended tapestry: its flags (31, 93) are cleared by other scripts",
    (101, 914): "one of the museum's eight tasks: 3,000 each, no flag kept, so one can't be told from another",
    **{(101, at): "one of the museum's eight tasks: 3,000 each, no flag kept, so one can't be told from another"
       for at in (1238, 1374, 1472, 1562, 1652, 1728, 1881, 1984)},
    (104, 7328): _TALK_CHECK, (108, 4201): _TALK_CHECK,
    (118, 239): _UNKNOWN,
    (119, 3534): "a part added to the giants' skimmer: " + _NO_AMOUNT,
    (119, 3692): "a part added to the giants' skimmer: " + _NO_AMOUNT,
    (119, 3920): "a part added to the giants' skimmer: " + _NO_AMOUNT,
    (125, 1341): _SMALL_FIND,
    (128, 4273): "a report to Acar: 10,000 for the party in Tyr, as others there give, and no flag is kept",
    (128, 6606): "news sold to Acar: one of several, each 1,000",
    (133, 175): "a fight in the street: its flag (347) is cleared by another script",
    (133, 191): "a fight in the street: its flag (347) is cleared by another script",
    (133, 206): "a fight in the street: its flag (347) is cleared by another script",
    (133, 237): "a fight in the street: its flag (347) is cleared by another script",
    (138, 1508): _UNKNOWN, (146, 1259): "a tapestry pulled back from a door: a find, no deed of a quest",
    (150, 7470): _NO_AMOUNT, (159, 4876): "alms to the beggar: the amount goes by the money given, and no flag is kept",
    (162, 1577): "the headquarters cleared: its flag (392) is cleared by another script, and 25,000 is given there more than once",
    (172, 160): "a fight to clear the headquarters of Draxans: 25,000 each, and no flag is kept",
    (172, 197): "a fight to clear the headquarters of Draxans: 25,000 each, and no flag is kept",
    (172, 219): "a fight to clear the headquarters of Draxans: 25,000 each, and no flag is kept",
    (184, 5516): _NO_AMOUNT,
    (185, 360): _SMALL_FIND, (185, 575): _SMALL_FIND,
    (236, 3061): "one halfling more out of the tunnels: one of several, each 1,000",
    (236, 3231): _SMALL_FIND,
    (237, 1116): _UNKNOWN,
    (238, 769): _SMALL_FIND, (238, 968): "a patrol let pass from the alcove: a fight avoided, no deed of a quest",
    (238, 2297): _SMALL_FIND, (238, 4314): _SMALL_FIND,
    (241, 5589): "Donno revived with the flask: 5,000 for the party, as the giants' field gives (both scripts run from MAS 99 too)",
    (246, 2525): "the conch blown too early: a mistake, not a deed",
    (246, 2956): "a rock thrown at Tantris: a step of the temple's plan, no flag kept",
    (246, 3561): _UNKNOWN,
    (254, 304): _NO_AMOUNT, (255, 59): _NO_AMOUNT,
    (264, 681): "a bridge mended with vines: 5,000 for the party on the islands, as others there give, and no flag is kept",
    (264, 1241): "a lock picked on the way to the acolyte (flag 601): a step of that rescue",
    (297, 6807): "the way to Kalaobuta's meeting shown: 10,000 for the party in Tyr, as others there give, and no flag is kept",
    (299, 2789): _SMALL_FIND,
}

BY_KEY: Dict[str, Quest] = {quest.key: quest for quest in QUESTS}
