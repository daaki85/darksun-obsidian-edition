# Kalzith's pictures with the outfits, and the sequel's items read (2026-11-27)

Under test: nothing new; the docs review's pictures that still showed the party before its class
outfits (reports/docs-review-full-2026-11-27.md, part 10), on `obsidian-edition` after #266 and #268.
Setup as the [startup procedure](../PLAYTESTING.md#startup-procedure): Xvfb :55, DOSBox 320x240, the
watchdog on; no memory edits (nothing to keep from saving), so autosave left on.

## Which pictures were out of date
Compared with today's game: only the map figures and the creation figure wear the outfits. The
inventory, Effects and USE screens' portraits are the game's own pictures, so `new-spells-effects.png`,
`effects-weapons.png`, `effects-charges.png` and `default-party-gerakis.png` were current. The figures in
`pens-asks.png`, `pens-asks-dead.png` (the Trustee, Dinos) and `semyon-escape.png` (Scar's gladiators)
aren't the party. Out of date: `kalzith.png`'s talk half and `kalzith-body.png`.

## Kalzith's talk (`docs/kalzith.png`)
`loadsave.sh selling-junk-user`, `openshop.sh`'s steps: the talk with "Show us what you have", the party
dressed (Cermak's plum mantle). The shop in that save holds the junk the user sold (1, 6,000 and 24
ceramic), not the six scrolls the caption names, and the shop screen has no map figures: the new talk
half beside the old shop half, 200%.

## Kalzith's body (`docs/kalzith-body.png`)
In `selling-junk-user` the attack pointer over Kalzith showed the barred sword and nothing happened
(his figure drawn as a shadow). From `pens-after-scar`: walkto (1816,408), (1704,408), (1592,440),
`viewto.py 1592 562`, three clicks at (184,138) through Kurzak's entryway, `route.py 1560 880`. From
(1496,840) the attack's click on him said NO PATH FROM HERE (twice); back by `route.py 1560 880`, the
attack at (262,126): Gerakis's Bone Gythka hit for 18, "Kalzith is killed", "Kalzith leaves: Scroll of
Burning Hands". Then `walkto.py 1544 856`, the look pointer, a slow press at (262,129): the body's box
(the scroll, the Quarterstaff, the Cloak, the Ashen Robe). 200%: 640x400. The fight's end autosaved into
the game folder (no edits in play).

## The sequel's items (no play)
For ITEMS.md's "Wake of the Ravager's items", the sequel's `OBJEX.GFF` read in the container
(`setup_ravager.sh`): its RDFF objects' item records (type +0Ah, name +14h, plus +16h, power +10h,
value +06h), the ALL 4 type table's material (+4), the holders' names (a person's record +21h) and the
regions' ETAB entries (positive object numbers in the sequel). Most people are only in Limbo (RGN0FF)
until a script brings them out. ITEMS.BIN's pairs mark the objects only a transfer gives. Icons: the
sequel's pictures are PLNR or PLAN (`docicons.decode_plan`); four items have no picture at all (objects
731, 745, 732, 735).

Water: no new area (the pens).
