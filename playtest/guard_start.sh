#!/bin/sh
# guard_start.sh: the watchdog. Every 20 s: GONE if DOSBox has quit; STUCK (and a screenshot,
# $WORK/guard-stuck-N.png) if the screen hasn't changed for 3 checks. Follow $WORK/guard.log with
# Monitor (grep STUCK|GONE) for the whole test; a STUCK while I'm deliberately idle isn't a fault.
# Stop it before reporting: kill $(cat $WORK/guard.pid)
. "$(dirname "$0")/env.sh"
[ -f "$WORK/guard.pid" ] && kill $(cat "$WORK/guard.pid") 2>/dev/null
(
  last=""; same=0; n=0
  while true; do
    W=$(timeout 5 xdotool search $WINQ | head -1)
    if [ -z "$W" ]; then echo "$(date +%T) GONE"; sleep 20; continue; fi
    h=$(timeout 10 import -window $W png:- 2>/dev/null | md5sum | cut -c1-8)
    if [ "$h" = "$last" ]; then same=$((same+1)); else same=0; fi; last=$h
    if [ $same -eq 3 ]; then n=$((n+1)); timeout 10 import -window $W "$WORK/guard-stuck-$n.png"; echo "$(date +%T) STUCK guard-stuck-$n.png"; fi
    sleep 20
  done
) >> "$WORK/guard.log" 2>&1 &
echo $! > "$WORK/guard.pid"; echo "guard $(cat "$WORK/guard.pid"), log $WORK/guard.log"
