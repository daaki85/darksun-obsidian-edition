# rolog.py [--d20]: a read-only dice log beside the session's own Loader (2026-11-08): the Loader's
# describe() and hp_changes() on DSCLOG's entries, from this checkout's dsloader, writing nothing to
# the game (no attach(): it writes DSCLOG's seed, filters and switches; floating names off). For trying
# changed dice-log code on a DOSBox whose own Loader isn't yours to restart: two full Loaders would
# both answer the game. Run from anywhere, output to a file of your own:
#   setsid nohup python3 -u playtest/rolog.py > $PLAYTEST_WORK/rolog.txt 2>&1 < /dev/null &
# --d20: also each 1d20 of the dice routine with its caller's code, arguments and [BP-6] (how the Turn
# Undead roll was found behind the overlay manager's INT 3Fh stub).
import os, re, struct, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'obsidian-edition'))
from dsloader import dicelog, game
from dsloader.dicelog import DiceLog, HDR_SIG, CONVENTIONAL_AND_UPPER, RAND_IP
from dsloader.tracker import PartyTracker
from dsloader.__main__ import connect


class Args:
    pid = None
    host_base = None


log = DiceLog(connect(Args()))
log.floating_names = False
low = log.guest.read(0, CONVENTIONAL_AND_UPPER)
log.tsr_hdr = next(m.start() for m in re.finditer(re.escape(HDR_SIG), low) if m.start() % 16 == 0)
ds = game.find_data_segment(log.guest, low)
log.rand_addr = (ds - game.DGROUP) * 16 + RAND_IP
log.game = game.GameData(log.guest, ds)
log.tracker = PartyTracker(log.game)
log.last_seq = struct.unpack("<H", log.guest.read(log.tsr_hdr + 8, 2))[0]
d20 = '--d20' in sys.argv
print('read-only log attached', flush=True)
while True:
    now = time.monotonic()
    for e in log.poll():
        if d20 and e.code.startswith(dicelog.DICE_SITE) and (e.arg(6), e.arg(8)) == (1, 20):
            print('  [d20] caller code', e.parent_code.hex(), 'args', [e.parent_arg(o) for o in (6, 8, 0xA, 0xC)],
                  '[BP-6]', e.parent_local(-6), 'last cast', log._cast, flush=True)
        for line in log.describe(e, now=now):
            print(line, flush=True)
    for line in log.hp_changes(now) + log.flush(now):
        print(line, flush=True)
    time.sleep(0.05)
