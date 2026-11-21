"""F10 after the last step: the move taken back can be walked again (the game's own key, mended).

In a fight F10 takes a party member's move back (DSUN.EXE 1B83Ah, from the key table at 1BC5Bh):
with a fight on, a party member's turn and the member standing still (bit 20h of its map record
clear, 1BF9Dh), the member is put back on the square its turn began on (DS:4968h, 4966h) with the
movement points it had then (DS:4964h; all three kept by 1E4D6h as its turn comes up). That is all
it restores. The step that leaves fewer than 10 points zeroes them and clears bit 0 of the
member's turn flags, "can walk" (59106h: the word at 37BDh:01D5h + creature x 2), and F10 doesn't
set it again: after the last step the member stands where it began with all its points and no
click walks it.

The mend sets the bit again, and only that case's. The game clears the bit in two places: the last
step (591BCh, with the points zeroed), and an effect that pins a creature (786CBh, the points left
alone); and it zeroes the whole word when the turn is over or lost (1C090h, 78637h). So the Loader
mends only what it saw happen, in this order, in one turn of one party member:

1. the flags with bit 0 set (FULL);
2. then the same flags with bit 0 clear and the points 0: the last step (SPENT);
3. then, the flags still those, the points equal to the turn's own (DS:4964h, 10 or more), the
   member on the turn's first square and standing still: F10 has taken the move back.

And never for a member pinned at that moment: the game's pin (786A9h-786CBh) clears the bit when
effect 22h or 33h (Paralyzed or Stuck) lands, and does nothing else to the flags, so one landing
after the last step leaves them just as the last step did and the order alone can't tell. The
member's effects are read at F10 (the game's table, owner its combatant): with either one up,
nothing is written. (Seen in the game: Seneca made Paralyzed after her last step walked a step on
F10 before the game ended her turn, logs/2026-11-20-f10-after-spell.md in the playtest kit.) Since
DSCLOG's F10_PIN the game's F10 itself leaves such a member where it is, points and all, so this
never sees the points come back for one; the check stays as a second guard.

An attack made in the turn ends it: nothing is mended after one, before or after the walk, nor
once the flags have changed in any other way (a spell cast, an effect, the turn's end) or the turn
has passed. An attack is known by either of two bytes of the creature's: the swings made
(37BDh:0181h + creature, which is 0 again once the attack is over) and the attack commands given
this turn (37BDh:01ABh + creature, which stays). An attack ends the member's turn (the flags
zeroed) unless it kills: then the turn goes on, the game's F10 still puts the member back with its
points, and without the second byte the walk would be given too (seen in the game with the first
version of this: [the log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-modernisation-features.md)). With the bit the walk the points ran
out on is forgotten (its next step, 3972h:0377h + thing x 1Ch, and 3972h:08AAh + thing x 13h): the
game would go on with it from the square F10 put the member on.

What F10 does while some movement is left (the bit never cleared) is the game's and is untouched.
"""

import struct
from typing import Optional, Tuple

from . import game

POINTS_SEG, POINTS_OFF, FLAGS_OFF = 0x37BD, 0x22B, 0x1D5  # (a creature's: a word each)
ATTACKS_OFF, COMMANDS_OFF = 0x181, 0x1AB  # (a byte each: the swings made, the attack commands this turn)
CAN_WALK = 1  # the turn flags' bit 0
START_POINTS, START_Y, START_X = 0x4964, 0x4966, 0x4968  # DS words: the turn's own, as F10 gives them back
MAP_RECORD, WALKING = 0x6694, 0x20  # DS: a map thing's record (32 bytes each), its flags' bit while it walks
WALK_SEG, WALK_STEP, WALK_STEP_SIZE, WALK_LEFT, WALK_LEFT_SIZE = 0x3972, 0x377, 0x1C, 0x8AA, 0x13
STEP = 10  # a straight step's points: with fewer the game lets nobody walk
PINNING = (game.PARALYZED_EFFECT, 51)  # Paralyzed (22h) and Stuck (33h): the effects whose landing clears the bit (786A9h)


class MoveBack:
    def __init__(self):
        self._turn: Optional[Tuple[int, int]] = None  # (the combatant, its creature) whose turn was last seen
        self._full: Optional[int] = None  # its flags as last seen with "can walk"
        self._spent: Optional[int] = None  # ... as the last step left them

    def _forget(self) -> None:
        self._full = self._spent = None

    def update(self, gd, on: bool) -> Optional[str]:
        """One look. The dice log's line when a move taken back with F10 was given its walk."""
        if not on or not gd.in_combat():
            self._turn = None
            self._forget()
            return None
        turn = gd.whose_turn()
        creature = gd.combatant_creature(turn) if turn is not None and turn < game.PARTY_SIZE else None
        if creature is None:
            self._turn = None
            self._forget()
            return None
        if (turn, creature) != self._turn:
            self._turn = (turn, creature)
            self._forget()
        guest = gd.guest
        at = (gd.load_seg + POINTS_SEG) * 16
        points, = struct.unpack("<h", guest.read(at + POINTS_OFF + creature * 2, 2))
        flags, = struct.unpack("<H", guest.read(at + FLAGS_OFF + creature * 2, 2))
        if guest.read(at + ATTACKS_OFF + creature, 1)[0] or guest.read(at + COMMANDS_OFF + creature, 1)[0]:
            self._forget()  # (an attack made this turn: the game's alone from here)
            return None
        if flags & CAN_WALK:
            self._full, self._spent = flags, None
            return None
        if self._spent is None:
            if self._full is not None and flags == self._full & ~CAN_WALK and points == 0:
                self._spent = flags  # (the last step)
            else:
                self._full = None  # (cleared some other way: not ours to give back)
            return None
        if flags != self._spent:
            self._forget()
            return None
        ds = gd.ds * 16
        start, start_y, start_x = struct.unpack("<hHH", guest.read(ds + START_POINTS, 6))
        here = struct.unpack("<HH", guest.read(ds + game.POSITIONS + turn * 32, 4))
        walking = guest.read(ds + MAP_RECORD + turn * 32, 1)[0] & WALKING
        if points != start or points < STEP or here != (start_x, start_y) or walking:
            return None
        if any(e.owner == turn and e.id in PINNING for e in gd.effects()):
            self._forget()  # (pinned: no walk to give, now or later this turn)
            return None
        walk = (gd.load_seg + WALK_SEG) * 16
        guest.write(walk + WALK_STEP + turn * WALK_STEP_SIZE, b"\xff")  # (the walk the points ran out on)
        guest.write(walk + WALK_LEFT + turn * WALK_LEFT_SIZE, b"\0\0")
        guest.write(at + FLAGS_OFF + creature * 2, struct.pack("<H", flags | CAN_WALK))
        self._full, self._spent = flags | CAN_WALK, None
        return f"F10: {gd.creature_name(creature)}'s move taken back (can walk again)"
