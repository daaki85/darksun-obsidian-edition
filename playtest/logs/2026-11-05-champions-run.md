# The champions' bout in a real run (2026-11-05)

Build: `obsidian-edition` at eb013d7 (every changed script decodes; the champions' hook on
script 3 at 3A7h). DOSBox, the ready-made party.

1. `loadsave.sh pens-after-arena`: the pens, arena count (the game's number 12) 1, flags 759
   and 807 clear.
2. The count set to 4 in memory (the pens hold the numbers), so the next trip is Scar's.
3. Followed Kurzak to his stop (follow.py 29), through his entryway and down the east passage;
   the fire room's door (115, 53), map (1848, 856), opened with the look pointer; the look
   pointer on the fire ring (map about 1931, 856) rests the party: "THE PARTY RESTS", hit points
   full. After a second rest and a few steps: "Gerakis! Get up here! It's your turn in the arena!"
4. Back at Kurzak's entryway (1592, 584): "Legcrusher! ... Legcrusher? Where has that lump got to?
   Gladiators! Get up here yourselves!" and "I sent Legcrusher after you, and he never came back..."
   **Suspect:** Legcrusher was never killed in this save; and the dice log said "Portrait 5 is
   Trustee" (portrait 5 is Kurzak's). Both to look into after the run.
5. Following Kurzak a second time (to square 115, 26, by the arena gate) took too long: "I saw them
   just a second ago. They must be trying to escape." / "Help! Somebody sound the alarm!", and a
   fight with the Arena Guards, Guards, Templars, **Legcrusher** and Kurzak. So Legcrusher was
   alive: Kurzak's "he never came back" lines in step 4 are a Loader bug (kurzak.py). Not fought:
   reloaded.
6. Saved by the fire with the count at 4 (`saves/pens-fire-count4`). Loaded, rested three times;
   the call came. Walked to Kurzak's stop (his lines again, the same Legcrusher ones), then
   toward the arena gate (1816, 408): "Give us a good show...", "I'm not standing around for my
   health. Get in there and fight!", then "That's it! Time's run out!". The way into the arena
   from the pens isn't known: asked the user.
7. Into the arena (the user's way, 2026-11-05): after the call, the party to Kurzak's entryway
   (route.py 1592 584: this time Legcrusher came, "Kurzak told me to bring you to the arena"),
   his stop (1592, 520), north to (1592, 440), east along the corridor at y 408 to (1816, 408)
   (walkto in two steps; y 376 further north counted as escaping), then a click into the gap
   in the brick wall just south of it (1816, 440): "Enter the arena?" Y. Region 2Ah.
   Kurzak still said "So Legcrusher found you. Then where's he got to? He never came back." with
   Legcrusher just there: the kurzak.py bug again.
8. In the arena the party walks south from the gate (488, 200), through the bone wall's gap
   (504, 360), and on south onto the stone platform until the bone gate closes behind it (the
   user): at (488, 424) the Announcer: "This day we have a surprise! The 'King of the Pens',
   Scar, ... has offered to kill them himself..." (the count at 4: Scar's visit).
9. Scar's talk ("Welcome, beetle-bait..."): "I'm breaking out. Get in my way and die!" (one line
   below the one aimed at; it still means a fight): "You've set yourself against me. To the
   death!". `fightout.sh`: Cilla killed Scar: "**This makes Cilla king of the pens!**". In memory
   afterwards: flag 19 set and **flag 759 set** (the champions' hook ran: before the fix it never
   did with Semyon on), 807 clear, the count still 4. Then "That was too easy. Perhaps these
   monsters would be more of a challenge!"
10. Saved after Scar (`saves/pens-after-scar`: count 5, flags 19 and 759). Loaded; Kurzak to his
    stop, the fire room (its door shut again: the look pointer from beside it, 1832, 840; the
    pointer cycle checked on screen: arrow, sword, eye), three rests, the call, the same way up,
    "Enter the arena?" Y, south through the bone wall to the platform (488, 408).
11. **The speech**: "Citizens of Draj! Scar is dead, and the pens have a new king. But word travels
    fast across the sands. From a distant arena come champions who have never known defeat, and
    they have come to see if the new king is worthy of the crown." / "Their leader, a Tohr-kreen,
    carries a gythka that has drunk the blood of a hundred gladiators."
12. **Six Champions** in round 1. Their lists in memory: the Tohr-kreen holds Bone Kreenfang +1;
    the half-giant wears a Bone Helm, the bone scale set and a Leather Shield, holds a Metal Great
    Axe; the mul the helm and scale set, two Bone Axes; the halfling a Leather Shield, Helm, Leg,
    Arm and Chest Armor, a Bone Short Sword and a Leather Sling; the elf the same leather, Wooden
    Arrows, an Obsidian Long Sword and a Wooden Bow; the defiler a Bone Dagger, a Scroll in its
    pack. Nothing left in a backpack but the scroll.
13. `fightout.sh` (a PICK A PSIONIC POWER screen for K'ratchek's level stopped it once: a red
    power's icon clicked, about 158, 62, closed it). The champions fought with their gear: the
    mul "with Bone Axe (1d8)", the elf "with Obsidian Long Sword (1d8)", the Tohr-kreen "with Bone
    Kreenfang +1 (2d4+1)" twice, then its bite. All six killed: 2000 XP each. **Flag 807 set**.
14. Then "That was too easy. Perhaps these monsters would be more of a challenge!" and a wave of
    the game's own (Renegades, Xorns, a Sand Howler): the same line and the same next wave as
    after Scar's fight. The champions are the visit's first wave only, as built. Fought; then
    "Yell something back at the Announcer?" N; "Go back to the pens...".
15. In memory: the Tohr-kreen's body is **object 2666** (map 388, 412) holding **Bone Kreenfang +1**;
    each other champion a Dead Body (1101) with all its gear (the defiler's: Scroll, Bone Dagger).
    Not done: looting it in the game (how a body is opened: asked the user), and the champions'
    Look boxes (to see on a second run from `pens-after-scar`).
