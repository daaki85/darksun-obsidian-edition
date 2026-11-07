# 2026-11-07: a check before the 2.14.0 release

Under test: branch obsidian-edition at f792171 (the fifth review's code: the item gate's cover for a
null table, the reserve of the game's free lists, the two-hander rule, the flag range; the Loader
window's labels and layout). DSCLOG and the scripts unchanged since #86 (comments only), so no
DSCLOG bytes to look for. In DOSBox, from `pens-after-scar` (region 29h, leader 1816,440).

1. **The game's people wear their gear** (`npcgear.py` after loading): all 21 people with items had
   them on: the Arena Guards' leather, arrows, obsidian long sword and bow; Legcrusher's Leather
   Inixhide +1 and two clubs; Kurzak's leather helm, chest and arm armour, his obsidian long sword
   and Shadowseeker +1; the Templars' leather shield and bone brigandine with a one-hander; Merzol's
   axe and long sword; Kalzith's cloak, Ashen Robe +1 and quarterstaff. Only keys, food and
   scrolls in packs. Pehtucl (thing 30) still wears his Cloak of Protection +1: the save is older
   than the chest change, as the patch notes say.
2. **Free things** (`thingsfree.py`): 143 of the 200 free after loading (the Loader keeps 20 back).
3. **A pocket picked**: walkto (1816,408), (1704,408), (1592,440), `viewto.py 1592 470`; U, Cilla
   (108,108), the purse (157,145, a slow press), the talk pointer on the figure south of the party
   (190,118), which was Kurzak (thing 47 at 1592,504). First try: d100 = 100, failed; moved
   silently, 44 under 57: "Cilla fumbles Kurzak's pockets, but slips away unnoticed." (free to try
   again, as DICE-LOG now says). Second try: d100 = 44 under 70: "Cilla lifts Metal Shadowseeker +1
   from Kurzak unnoticed. Cilla receives 200 experience points!" (the XP line: Cilla +66). After it:
   Kurzak holds only his long sword; Cilla's backpack (+0Ch) has item 41; 142 things free (one
   taken for her new backpack list).
4. No error, refused write or Traceback in the dice log; the watchdog reported nothing.

Not saved (nothing to keep: the pick changes the save).
