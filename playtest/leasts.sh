# leasts.sh (on the creation screen; ROWS="y ..." to pick rows): for each score's square, a right click (lower) then the least the game worked out, then a left click back
cd "$(dirname "$0")"
for y in ${ROWS:-140 146 154 161 167 174}; do
  timeout 15 python3 click.py 6 $y right >/dev/null; sleep 0.5
  timeout 20 python3 creationscores.py | sed "s/^/row $y: /"
  timeout 15 python3 click.py 6 $y left >/dev/null; sleep 0.5
done
