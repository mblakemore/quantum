#!/usr/bin/env bash
# H15 epoch-quality survey DRIVER (Whisper C5075) — flies ONE un-flown epoch per invocation.
#
# Cronned so the 13 epochs land across TIMES AND DAYS. That spread is the scientific point, not a
# convenience: thirteen jobs back-to-back would characterise one weather system and call it a
# climate — the exact error that produced the retracted 0.875 reading this survey exists to replace.
#
# Idempotent + self-terminating by construction:
#   * the next epoch = lowest index with no manifest on disk, so a missed or failed fire simply
#     retries that epoch on the next tick rather than skipping it;
#   * it STOPS at N_EPOCHS and says so, so a forgotten cron cannot quietly keep spending tank;
#   * it refuses to fly if the ALT4 tank reads below MIN_TANK_S, so the survey cannot drain the
#     account other work depends on.
set -uo pipefail
Q=/droid/repos/quantum
N_EPOCHS=20
MIN_TANK_S=3
HAIL=/mnt/droid/repos/DC15W/tools/hail-whisper.sh
LOG=$Q/results/h15_survey_driver.log

ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

next_epoch=""
for e in $(seq 0 $((N_EPOCHS - 1))); do
  if [ ! -f "$Q/results/h15_survey_epoch${e}_manifest_c5075.json" ]; then next_epoch=$e; break; fi
done

if [ -z "$next_epoch" ]; then
  echo "[$(ts)] survey COMPLETE — all $N_EPOCHS epochs have manifests. Driver is a no-op; delete the cron." >> "$LOG"
  exit 0
fi

# Tank guard: never let a diagnostic drain the account other work needs.
tank=$(curl -s -H "Authorization: Bearer $(cat ~/.uhura-key)" \
  "http://127.0.0.1:8790/resources?kind=qpu_account" 2>/dev/null \
  | python3 -c "import json,sys
try:
    print(next(r['meta']['balance_s'] for r in json.load(sys.stdin)['resources'] if r['name']=='ALT4'))
except Exception: print(-1)" 2>/dev/null)

if [ "${tank:--1}" -lt "$MIN_TANK_S" ] 2>/dev/null; then
  echo "[$(ts)] epoch $next_epoch HELD — ALT4 tank reads ${tank}s < ${MIN_TANK_S}s (or unreadable). Not flying." >> "$LOG"
  exit 0
fi

# FREE WEATHER SCAN, recorded per epoch (C5075, Creator prompt "are you utilizing all our quantum
# weather work?" — the honest answer was no). tools/qpu_weather.py --scan is VENDOR-ONLY: zero
# qubits, zero QPU-seconds, no submission. Logging it beside every epoch turns a question we would
# otherwise have to assume into one the survey ANSWERS for free: does the campaign's existing
# population-based weather instrument forecast a PHASE-sensitive success rate?
# The prior says probably not — the U6 sentinel timeline spans 61 flights at 0.960 +/- 0.015 (~1.6%
# relative spread) while H15's ALT accept has swung 0.625-0.875 (~11.7%), i.e. SEVEN TIMES more.
# That is the currency map (population QUIET, phase TURBULENT) predicting its own limit. Either
# answer is worth having: a correlation would give a $0 pre-submit forecast and make the anchor arm
# redundant; no correlation bounds the weather service's reach and validates the map on a new axis.
wx=$(cd "$Q" && timeout 300 python3 tools/qpu_weather.py --scan --backend ibm_kingston 2>&1 | grep -viE "^qiskit_runtime|warning" | tr '\n' ' ')
echo "[$(ts)] epoch $next_epoch WEATHER(free): $wx" >> "$LOG"

out=$(cd "$Q" && timeout 600 python3 experiments/h15_survey_fly_whisper_c5075.py --epoch "$next_epoch" --fly 2>&1)
jid=$(echo "$out" | grep -oE 'JOB ID \(ANNOUNCED AT SUBMIT\): [a-z0-9]+' | awk '{print $NF}')
pend=$(echo "$out" | grep -oE "'pending_jobs_at_submit': [0-9]+" | awk '{print $NF}')

if [ -n "$jid" ]; then
  echo "[$(ts)] epoch $next_epoch FLOWN job=$jid queue=$pend tank_before=${tank}s" >> "$LOG"
  printf 'H15 epoch-quality survey — epoch %s/%s FLOWN: job %s on kingston/ALT4, queue-at-submit %s, ~1.4 QPU-s (unsealed, claim-free diagnostic). Announced at submit by the survey driver; epochs are deliberately spread across times and days.' \
    "$((next_epoch + 1))" "$N_EPOCHS" "$jid" "${pend:-?}" > /tmp/h15_survey_post.txt
  "$HAIL" general "$(cat /tmp/h15_survey_post.txt)" fyi >> "$LOG" 2>&1
else
  echo "[$(ts)] epoch $next_epoch SUBMIT FAILED — no job id. Output tail:" >> "$LOG"
  echo "$out" | tail -5 >> "$LOG"
fi

# BANK RAW ROWS for any flown-but-unbanked epoch. Retrieval is not custody: C5071 rescued 238 jobs
# whose shot records lived only at IBM, days from the retention edge. Idempotent; banks the PREVIOUS
# epoch on each tick (this one is still queued), and carries per-row A-weight for Declared Output 2.
(cd "$Q" && timeout 600 python3 experiments/h15_survey_collect_c5075.py 2>&1 | grep -v WARNING) >> "$LOG" 2>&1
