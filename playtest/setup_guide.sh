#!/bin/sh
# setup_guide.sh: the owner's walkthroughs made searchable. Shattered Lands': from
# $WORK/guide/kibbitz.html (the owner's saved copy of the page, from the private repository of installation
# files, $INSTALL, or put there by hand) to its text,
# $WORK/guide/kibbitz.txt (grep -n -i). Someone else's work: never committed, never shared from a
# public link (the repository is public). Wake of the Ravager's: $INSTALL/guide/wake-of-the-ravager-walkthrough.txt
# (the owner's copy, already text) to $WORK/guide/ravager.txt, when the private repository has it.
. "$(dirname "$0")/env.sh"
mkdir -p "$WORK/guide"
[ -s "$WORK/guide/kibbitz.html" ] || [ ! -s "$INSTALL/guide/kibbitz.html" ] || cp "$INSTALL/guide/kibbitz.html" "$WORK/guide/"
[ -s "$WORK/guide/kibbitz.html" ] || { echo "no walkthrough at $WORK/guide/kibbitz.html: put the owner's copy there"; exit 1; }
python3 -I - "$WORK/guide/kibbitz.html" "$WORK/guide/kibbitz.txt" <<'PY'
import html, re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", t, re.S)
open(sys.argv[2], "w").write("\n".join(html.unescape(re.sub(r"<[^>]+>", "", b)) for b in blocks))
PY
wc -l "$WORK/guide/kibbitz.txt"
R="$INSTALL/guide/wake-of-the-ravager-walkthrough.txt"
[ -s "$R" ] && cp "$R" "$WORK/guide/ravager.txt" && wc -l "$WORK/guide/ravager.txt"
exit 0
