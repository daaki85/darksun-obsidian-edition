# buildcheck_syms.py: symbols() of obsidian-edition/dos/dsclog.asm as built: {label: image or tail offset} and
# {equ: value}, from nasm's symbol map (for scwatch.py and the like).
import os, sys
REPO_DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'obsidian-edition')


def symbols():
    sys.path.insert(0, os.path.join(REPO_DOS, 'tests'))
    from test_dsclog_room import build_map
    sections, equs = build_map('dsclog.asm')
    return dict(sections['image']), equs
