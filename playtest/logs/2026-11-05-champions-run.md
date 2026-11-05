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
