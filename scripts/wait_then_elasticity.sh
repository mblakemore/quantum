#!/bin/bash
# C3867 (Ember): action-trigger for pred_c3841. Waits for Exp54 ArmA (the n=10
# anchor producer) to exit, verifies the checkpoint has all 10 seeds, then runs
# the shot-elasticity validate+elasticity stages. Output -> results/exp54_elasticity_auto.log
# Self-surfacing handoff: pred_c3841 grades next cycle from THIS output (conjunct-2),
# not from another time-estimate.
set -u
cd /droid/repos/quantum
LOG=results/exp54_elasticity_auto.log
PID=2132934   # Exp54 ArmA --full run
echo "=== wait_then_elasticity START $(date -Iseconds) waiting on PID $PID ===" > "$LOG"

# 1. Wait for Exp54 ArmA to exit (poll every 5 min, cap ~12h)
for i in $(seq 1 144); do
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "PID $PID exited at $(date -Iseconds) after ${i} polls" >> "$LOG"
    break
  fi
  sleep 300
done

# 2. Log checkpoint state for the record (the elasticity script is internally
#    GATED on the full 10-seed anchor set — it will refuse if incomplete, which
#    shows in the log below; no fragile pre-check needed here).
echo "checkpoint mtime: $(stat -c '%y' results/exp54_checkpoint.json 2>/dev/null)" >> "$LOG"

# 3. Run validate then elasticity (the P-C4209-a measurement)
echo "=== --validate $(date -Iseconds) ===" >> "$LOG"
python3 -u scripts/run_exp54_shot_elasticity.py --validate >> "$LOG" 2>&1
echo "=== --elasticity $(date -Iseconds) ===" >> "$LOG"
python3 -u scripts/run_exp54_shot_elasticity.py --elasticity >> "$LOG" 2>&1
echo "=== wait_then_elasticity DONE $(date -Iseconds) ===" >> "$LOG"
