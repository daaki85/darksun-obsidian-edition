# ravjump.py REGION COL ROW: a jump for a test to any region of Wake of the Ravager, the way the game itself
# moves the party there: Reyhan's talk in the Harbinger's Roost (GPL 140, the part a talk runs, from +45) made
# the script command 5Eh (move: who, region, column, row) for the party, in the Loader's script copy
# (obsidian-edition/dos/GPLDAT2.GFF; ravstart.sh writes it afresh, so run this after the start). The game
# reads the talk from that file when it is run, takes the party there and loads the region whole: its own
# map objects and its scripts (MAS N is region N's), as an exit to it would (a save edited to another
# region number only redraws the map under the old region's objects: no use).
#
#   sh ravload.sh ravager-roost FOLDER; python3 ravjump.py 0x42 85 15
#   then the look pointer (two right clicks from the walk arrow) on Reyhan (ravclick.py 150 128 just after
#   the load) and a press: the region's picture, Space, and the party at square (COL, ROW): map pixel
#   16*COL, 16*ROW, a square GMAP has 0 for (open ground).
#
# Squares that worked (2026-11-27): 0x42 85 15 (the Cloud: the air drakes come at once, a fight), 0x3E 36 9
# (Volcano 1: the fire drakes), 0x44 33 43 (then Down x7 onto the Tarrasque's steps). Where no fight starts at
# once the view stays where the Roost's was: write the camera (DS:1408h) to the leader's foot less (152, 88) and
# open and close USE (game 24,20, then Escape) to redraw it; the party is still only half there (a fight there
# hangs: 0x43, the earth drake, logs/2026-11-27-ravager-encounters.md). Never save after a jump: the story's
# flags are where Tyr left them.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'obsidian-edition'))
from dsloader import gpl

WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
COPY = os.path.join(HERE, '..', 'obsidian-edition', 'dos', 'GPLDAT2.GFF')
TALK, ENTRY = 140, 45  # (Reyhan's script, where a talk with him starts: past the part a fight runs)
MOVE, PARTY, NUMBER, END = 0x5E, 0x7FFE, 0x8F, bytes([0x15, 0x31])  # (move; the party; a small number; return, end)


def move(region: int, col: int, row: int) -> bytes:
    """The command: move the party to REGION at (COL, ROW), each a 2-byte number (00h-7Fh big-endian)."""
    assert 0 <= region < 0x8000 and 0 <= col < 128 and 0 <= row < 98
    return (bytes([MOVE]) + PARTY.to_bytes(2, 'big') + region.to_bytes(2, 'big') + col.to_bytes(2, 'big')
            + row.to_bytes(2, 'big') + bytes([NUMBER, 0]) + END)


def patch(copy: bytes, talk: bytes, region: int, col: int, row: int) -> bytes:
    """COPY (the script file) with TALK (the game's own GPL 140) found by its body, its talk made the jump."""
    key = talk[ENTRY + 20:ENTRY + 300]
    at = copy.find(key)
    if at < 0 or copy.find(key, at + 1) >= 0:
        raise SystemExit("Reyhan's talk not found once in the script copy")
    out = bytearray(copy)
    out[at - 20:at - 7] = move(region, col, row)
    return bytes(out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('usage: ravjump.py REGION COL ROW')
    region, col, row = (int(v, 0) for v in sys.argv[1:])
    scripts, _ = gpl.load_scripts(open(os.path.join(WORK, 'rav', 'GPLDATA.GFF'), 'rb').read())
    data = patch(open(COPY, 'rb').read(), scripts[('GPL ', TALK)], region, col, row)
    open(COPY, 'wb').write(data)
    print(f"Reyhan's talk now moves the party to region {region:#x}, square ({col}, {row})")
