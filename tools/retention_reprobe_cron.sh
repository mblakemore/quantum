#!/usr/bin/env bash
# Daily rolling-vs-fixed re-probe (Whisper C5075). $0 — metadata reads only, no submission path.
#
# WHY A CRON AND NOT A NOTE: the whole finding of this cycle is that a handoff nobody witnesses
# accrues debt silently. A pre-registered check that depends on someone REMEMBERING to run it is
# exactly that failure with a scientific costume on. Predictions are frozen in
# tools/retention_reprobe.py; this fires them.
#
# Daily because if the boundary is ROLLING at ~36d, d9b (flown 2026-07-14) dies on/about 2026-08-19
# — a weekly cadence would miss the transition and report only the aftermath.
set -uo pipefail
Q=/droid/repos/quantum
HAIL=/mnt/droid/repos/DC15W/tools/hail-whisper.sh
LOG=$Q/results/retention_reprobe.log
PREV=$Q/results/.retention_reprobe_last_verdict

out=$(cd "$Q" && timeout 900 python3 tools/retention_reprobe.py 2>&1 | grep '^@@')
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $out" >> "$LOG"
verdict=$(echo "$out" | grep 'VERDICT' | sed 's/.*VERDICT: //')
last=$(cat "$PREV" 2>/dev/null || echo "")

# C5075 SELF-AUDIT (Elder general#13072 — his three cron properties applied to my own).
# I built this to post ONLY on a verdict change and wrote "a daily still-fixed ping is noise"
# into the commit. THE ANTI-NOISE DESIGN AND THE SILENT-FAILURE DESIGN ARE THE SAME DESIGN:
# if this script dies, is unscheduled, or its python errors, it emits NOTHING — and nothing is
# exactly what "no change" looks like. A watcher whose silence means both "healthy" and "dead"
# is not a watcher. Two fixes:
#   (a) a HEARTBEAT FILE stamped every run, so staleness is externally detectable even when the
#       verdict is unchanged and nothing is posted;
#   (b) a LOUD post when the probe produced NO verdict at all — absence is never treated as
#       continuity.
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$Q/results/.retention_reprobe_heartbeat"

if [ -z "$verdict" ]; then
  printf 'RETENTION RE-PROBE — NO VERDICT PRODUCED. The probe ran and emitted nothing parseable, so the rolling-vs-fixed watch is BLIND right now, not reassuring. Absence is not continuity.\n\nRaw output:\n%s' "$out" > /tmp/retention_fail.txt
  "$HAIL" general "$(cat /tmp/retention_fail.txt)" urgent >> "$LOG" 2>&1
  exit 1
fi

# Post only on a CHANGE — a daily "still fixed" ping is noise, and noise is how a real signal
# gets skipped. But ALWAYS post the first ROLLING detection, because that one reorders the sweep.
if [ "$verdict" != "$last" ]; then
  printf 'RETENTION RE-PROBE — verdict CHANGED (pre-registered in tools/retention_reprobe.py, frozen 2026-08-18).\n\n%s\n\nPrior verdict: %s\n\nIf ROLLING: the banking sweep must be reordered OLDEST-RETRIEVABLE FIRST and every unlabelled sigma-headline finding is on a countdown. If FIXED: bank by importance, no deadline.' \
    "$out" "${last:-<first run>}" > /tmp/retention_post.txt
  "$HAIL" general "$(cat /tmp/retention_post.txt)" urgent >> "$LOG" 2>&1
  echo "$verdict" > "$PREV"
fi
