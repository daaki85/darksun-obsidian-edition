# flagfoes.py PLAYTEST SECONDS: Alt's bit set in the BIOS flags during the foes' turns of a fight,
# clear in the party's (whose Tab and Enter the bit would turn into Alt+Tab and Alt+Enter)
import os, sys, time
PT = sys.argv[1]; secs = float(sys.argv[2]); sys.argv = sys.argv[:1]
sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py'); exec(open(__file__).read())
import subprocess
win = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
t0 = time.time(); n = 0; down = False
while time.time() - t0 < secs:
    try:
        turn = gd.whose_turn(); want = bool(gd.fight_on() and turn is not None and turn >= 4)
        if want != down:
            subprocess.run(['xdotool', 'keydown' if want else 'keyup', '--window', win, 'Alt_L']); down = want; n += 1
    except Exception:
        pass
    time.sleep(0.03)
subprocess.run(['xdotool', 'keyup', '--window', win, 'Alt_L']); print('key changes', n)
