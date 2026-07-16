#!/bin/bash
JID=d9c300k1osis73bjab80
cd /droid/repos/quantum
for i in $(seq 1 240); do   # up to ~4h at 60s
  ST=$(timeout 60 python3 -c "from qiskit_ibm_runtime import QiskitRuntimeService; print(QiskitRuntimeService().job('$JID').status())" 2>/dev/null | tail -1)
  echo "[poll $i] $JID status=$ST"
  case "$ST" in
    *DONE*) echo "=== JOB DONE — grading ==="; timeout 180 python3 scripts/grade_exp140.py $JID 2>&1 | grep -vE "Deprecat|warn"; exit 0;;
    *ERROR*|*CANCEL*) echo "=== JOB $ST — no grade ==="; exit 1;;
  esac
  sleep 60
done
echo "poll timed out after ~4h; job still not done"; exit 2
