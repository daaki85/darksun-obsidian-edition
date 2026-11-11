# Semyon's tip, and an empty weapon rack (2026-11-11)

The user's save ("Page 2 slot 08 - rest no call", the second one, `saves/semyon-rack-user`): Semyon
saved and asked about the shipment ("it couldn't have gone far"), but the pens' weapon rack was
empty. Flags: TOLD (756) 1, SHIPPED (757) 0. `rackcheck.py`: the rack, object 2599, map thing 243
at (779,550), item 229, type 108, its contents +08h 9999: no list at all (the party had taken what
was on it). `semyon.ship` only linked Thornwall into an existing list, so it gave up on every pass.

Fixed: an emptied rack gets a new list from the game's free things (`semyon._new_contents`, with
ring.RESERVE kept), and `ring.Items` is read again after (its table is read once: the first build
found the list "missing" and shipped only on the next pass). The save loaded with it: SHIPPED 1, the
rack's contents thing 453 holding Thornwall (item 271). (Walking over to open it, a fight began
with the save's guards; not saved.) Test: `test_rack_emptied`.
