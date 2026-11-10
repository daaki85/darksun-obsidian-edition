#!/bin/sh
# setup_guide.sh: kibbitz's GameFAQs walkthrough of Shattered Lands (2026-11-09), from the owner's
# Google Drive (the installers' folder; file id below): $WORK/guide/kibbitz.html, and its text,
# $WORK/guide/kibbitz.txt, to search (grep -n -i). Someone else's work: kept on the Drive, never
# committed (the repository is public).
. "$(dirname "$0")/env.sh"
mkdir -p "$WORK/guide"
[ -s "$WORK/guide/kibbitz.html" ] || curl -sSL -o "$WORK/guide/kibbitz.html" \
    "https://drive.usercontent.google.com/download?id=1eVBzh7u6rqvTGDcWnYfHEiAIgT61I0Zz&export=download&confirm=t"
python3 -I - "$WORK/guide/kibbitz.html" "$WORK/guide/kibbitz.txt" <<'PY'
import html, re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", t, re.S)
open(sys.argv[2], "w").write("\n".join(html.unescape(re.sub(r"<[^>]+>", "", b)) for b in blocks))
PY
wc -l "$WORK/guide/kibbitz.txt"
