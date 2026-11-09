# restfixmem.py [check|fix|undo]: the rest routine's pass 2 (DSUN.EXE 8066Dh, overlay 5E8h) in the
# overlay buffer, if loaded: `check` says which version is there (the game's: the effects read
# before the free cures; the fix's: the cures first, logs/2026-11-09-rest-poison.md); `fix` and
# `undo` write one over the other in memory (the overlay must be loaded: rest once first; a reload
# of the overlay from the EXE puts the game's bytes back). Memory only: never save after.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
OLD = bytes.fromhex(
    "837ef0057c368a46f050ff76ea566a60900ee8280283c4088a46f050ff76ea566a67900ee8160283c4088a46f050"
    "ff76ea566a69900ee8040283c408837eee057c308a46ee5057566a60900ee8ee0183c4088a46ee5057566a67900e"
    "e8de0183c4088a46ee5057566a69900ee8ce0183c408837eee077c108a46ee5057566a76900ee8b80183c408")
NEW = bytes.fromhex(
    "e98500837ef0057c338a46f050ff76ea566a600ee8260283c4088a46f050ff76ea566a670ee8150283c4088a46f0"
    "50ff76ea566a690ee8040283c408837eee057c2d8a46ee5057566a600ee8ef0183c4088a46ee5057566a670ee8e0"
    "0183c4088a46ee5057566a690ee8d10183c408837eee077c0f8a46ee5057566a760ee8bc0183c408e96cff90")
LOOP = 0x80984 - 0x80765  # the loop's jmp, as far from the casts' start in the overlay as in the file
assert len(OLD) == len(NEW) == 0x88
mem = g.read(0, 0x110000)
hits = [(i, 'game') for i in range(len(mem)) if mem.startswith(OLD, i)] + \
       [(i, 'fix') for i in range(len(mem)) if mem.startswith(NEW, i)]
if not hits:
    print('not loaded'); sys.exit(1)
for at, kind in hits:
    print(f'{kind} at {at:X}h, loop jmp {mem[at + LOOP:at + LOOP + 3].hex()}')
    what = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if what == 'fix' and kind == 'game' and mem[at + LOOP:at + LOOP + 3] == bytes.fromhex('e9d1fd'):
        g.write(at, NEW); g.write(at + LOOP, bytes.fromhex('e9e1fd')); print('  fixed')
    if what == 'undo' and kind == 'fix' and mem[at + LOOP:at + LOOP + 3] == bytes.fromhex('e9e1fd'):
        g.write(at, OLD); g.write(at + LOOP, bytes.fromhex('e9d1fd')); print('  undone')
