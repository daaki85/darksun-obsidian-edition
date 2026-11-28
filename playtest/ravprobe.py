# ravprobe.py HEX: a script probe for a test in Wake of the Ravager: Reyhan's talk (GPL 140 from +45, ravjump.py's
# place, in the Loader's obsidian-edition/dos/GPLDAT2.GFF) replaced by the script commands HEX, then return and
# exit. After `sh ravload.sh ravager-roost`, the look pointer on Reyhan (two right-clicks, ravclick.py 150 128)
# and a left click run it; its prints land in the text buffer (ravtext.py). For a test of what a fixed script
# does in the game's own interpreter (2026-11-28: the ore voucher sale, logs/2026-11-28-ravager-script-fixes.md).
# Never save after: ravstart.sh writes the copy afresh at the next start.
import os, sys
import ravjump as rj
from dsloader import gpl
code = bytes.fromhex(sys.argv[1]) + rj.END
scripts, _ = gpl.load_scripts(open(os.path.join(rj.WORK, 'rav', 'GPLDATA.GFF'), 'rb').read())
talk = scripts[('GPL ', rj.TALK)]
copy = open(rj.COPY, 'rb').read()
at = rj.talk_at(copy, talk)
if len(code) >= len(talk) - rj.ENTRY - 10:
    sys.exit('the probe is longer than the talk it replaces')
out = bytearray(copy); out[at:at + len(code)] = code
open(rj.COPY, 'wb').write(out); print('Reyhan talk replaced:', len(code), 'bytes')
